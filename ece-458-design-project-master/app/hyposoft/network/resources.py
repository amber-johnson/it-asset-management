from django.core.exceptions import ValidationError
from import_export import fields
from rest_framework import serializers

from equipment.models import Asset
from changeplan.models import ChangePlan
from hypo_auth.handlers import check_asset_perm
from network.models import NetworkPortLabel, NetworkPort
from import_export.widgets import ForeignKeyWidget

from equipment.resources import VersionedResource
from hyposoft.utils import versioned_queryset, versioned_object, add_network_conn, add_asset, newest_object


class NetworkPortResource(VersionedResource):
    class SrcAssetForeignKeyWidget(ForeignKeyWidget):
        def clean(self, value, row=None, *args, **kwargs):
            version = ChangePlan.objects.get(id=row['version'])
            asset = newest_object(Asset, version, hostname=row['src_hostname'])
            return add_asset(asset, version, ['hostname'])

    class SrcLabelForeignKeyWidget(ForeignKeyWidget):
        def clean(self, value, row=None, *args, **kwargs):
            my_asset = newest_object(Asset, ChangePlan.objects.get(id=row['version']), hostname=row['src_hostname'])
            return NetworkPortLabel.objects.get(
                name__iexact=row['src_port'],
                itmodel__vendor__iexact=my_asset.itmodel.vendor,
                itmodel__model_number__iexact=my_asset.itmodel.model_number
            )

    class VersionWidget(ForeignKeyWidget):
        def clean(self, value, row=None, *args, **kwargs):
            if value is not None:
                return self.get_queryset(value, row, *args, **kwargs).get(**{self.field: value})
            else:
                return None

    src_hostname = fields.Field(
        column_name='src_hostname',
        attribute='asset',
        widget=SrcAssetForeignKeyWidget(Asset, 'hostname')
    )
    src_port = fields.Field(
        column_name='src_port',
        attribute='label',
        widget=SrcLabelForeignKeyWidget(NetworkPortLabel, 'name')
    )
    src_mac = fields.Field(
        column_name='src_mac',
        attribute='mac_address'
    )
    dest_hostname = fields.Field(attribute="dest_hostname")
    dest_port = fields.Field(attribute="dest_port")
    version = fields.Field(
        attribute='version',
        widget=VersionWidget(ChangePlan, 'id')
    )

    def dehydrate_dest_hostname(self, networkport):
        try:
            if networkport.connection:
                return networkport.connection.asset.hostname
            else:
                return ''
        except:
            return ''

    def dehydrate_dest_port(self, networkport):
        try:
            if networkport.connection:
                return networkport.connection.label.name
            else:
                return ''
        except:
            return ''

    class Meta:
        model = NetworkPort
        exclude = ('id', 'asset', 'label', 'connection')
        import_id_fields = ('src_hostname', 'src_port', 'version')
        export_order = ('src_hostname', 'src_port', 'src_mac', 'dest_hostname', 'dest_port')
        skip_unchanged = True
        report_skipped = True
        clean_model_instances = True

    def skip_row(self, instance, original):
        check_asset_perm(self.owner.username, instance.asset.site.abbr)
        if instance.asset.site.offline and getattr(instance, 'dest_hostname'):
            raise serializers.ValidationError(
                "Cannot set network connections in offline storage."
            )
        dest = newest_object(NetworkPort, self.version,
                             asset__hostname=getattr(instance, 'dest_hostname'),
                             label__name=getattr(instance, 'dest_port'))
        if dest:
            check_asset_perm(self.owner.username, dest.asset.site.abbr)
            if dest.asset.site.offline and getattr(instance, 'dest_hostname'):
                raise serializers.ValidationError(
                    "Cannot set network connections in offline storage."
                )

        if original.mac_address != instance.mac_address:
            return False

        if not dest and not original.connection:
            return True

        if dest and original.connection:
            return dest.connection.asset.hostname == instance.asset.hostname

        return False

    def before_import_row(self, row, **kwargs):
        row['version'] = self.version.id
        if len(row['src_mac']) == 0:
            row['src_mac'] = None

        if row['src_mac']:
            mac = row['src_mac'].lower().replace('-', '').replace('_', '').replace(':', '')
            row['src_mac'] = ':'.join([mac[b:b + 2] for b in range(0, 12, 2)])

        if Asset.objects.filter(hostname=row['src_hostname']).count() == 0:
            raise ValidationError("Asset with hostname {} not found.".format(row['src_hostname']))

        if len(row['dest_hostname']) > 0 and Asset.objects.filter(hostname=row['dest_hostname']).count() == 0:
            raise ValidationError("Asset with hostname {} not found.".format(row['dest_hostname']))

    def after_save_instance(self, instance, using_transactions, dry_run):
        if self.version.parent:
            asset = versioned_object(instance.asset, self.version.parent, ['hostname'])
            for port in asset.networkport_set.all():
                add_network_conn(port, self.version)

    def after_import_row(self, row, row_result, **kwargs):
        if row_result.import_type == 'skip':
            return
        try:
            port = NetworkPort.objects.get(id=row_result.object_id)
        except:
            return
    
        if (row['dest_hostname'] == '' and row['dest_port'] != '') or (
                row['dest_hostname'] != '' and row['dest_port'] == ''):
            raise ValidationError(
                "These fields must both be empty or set")

        if row['dest_hostname'] != '' and row['dest_port'] != '':
            dest_conn = newest_object(NetworkPort, self.version,
                                      asset__hostname=row['dest_hostname'], label__name=row['dest_port'])

            dest_conn = add_network_conn(dest_conn, self.version)
            port.connection = dest_conn
            port.save()
        else:
            port.connection = None
            port.save()

    def export(self, queryset=None, version_id=0, *args, **kwargs):
        if queryset is None:
            queryset = self.get_queryset()
        for network_connection in queryset:
            src = network_connection
            dest = network_connection.connection
            if dest:
                if src.asset.itmodel.network_ports > dest.asset.itmodel.network_ports:
                    queryset = queryset.exclude(id=src.id)
                elif src.asset.itmodel.network_ports == dest.asset.itmodel.network_ports:
                    if src.asset.asset_number > dest.asset.asset_number:
                        queryset = queryset.exclude(id=src.id)

        queryset = queryset.exclude(mac_address__isnull=True, connection__isnull=True)

        version = ChangePlan.objects.get(id=version_id)
        versioned = versioned_queryset(queryset, version, NetworkPort.IDENTITY_FIELDS)
        versioned = versioned.order_by('asset__hostname', 'label__name')
        return super(NetworkPortResource, self).export(versioned, *args, **kwargs)

    def after_export(self, queryset, data, *args, **kwargs):
        del data['version']
        del data['mac_address']
