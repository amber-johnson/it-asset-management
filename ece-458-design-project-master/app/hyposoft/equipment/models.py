from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

from changeplan.models import ChangePlan


class Site(models.Model):
    abbr = models.CharField(
        max_length=6,
        unique=True
    )
    name = models.CharField(
        max_length=64
    )
    offline = models.BooleanField(
        default=False
    )

    def __str__(self):
        return str(self.abbr).upper()


class ITModel(models.Model):
    vendor = models.CharField(
        max_length=64
    )
    model_number = models.CharField(
        max_length=64,
    )
    height = models.IntegerField(
        validators=[
            MinValueValidator(1,
                              message="Height must be at least 1.")
        ]
    )
    display_color = models.CharField(
        max_length=10,
        blank=True,
        validators=[
            RegexValidator("^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                           message="Please enter a valid color code.")  # Color code
        ],
        default="#ddd"
    )
    power_ports = models.IntegerField(
        blank=True,
        default=0,
        validators=[
            MinValueValidator(0,
                              message="Number of power ports must be at least 0.")
        ]
    )
    network_ports = models.IntegerField(
        blank=True,
        default=0,
        validators=[
            MinValueValidator(0,
                              message="Number of network ports must be at least 0.")
        ]
    )
    cpu = models.CharField(
        max_length=64,
        blank=True
    )
    memory = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Memory (GB)",
        validators=[
            MinValueValidator(0,
                              message="Number of GB of memory must be at least 0.")
        ]
    )
    storage = models.CharField(
        max_length=128,
        blank=True
    )
    comment = models.TextField(
        blank=True,
        validators=[
            RegexValidator("(?m)""(?![ \t]*(,|$))",
                           message="Comments must be enclosed by double quotes if comment contains line breaks.")
        ]
    )

    class Type(models.TextChoices):
        REGULAR = ('regular', 'regular')
        CHASSIS = ('chassis', 'chassis')
        BLADE = ('blade', 'blade')

    type = models.CharField(
        max_length=16,
        choices=Type.choices
    )

    class Meta:
        unique_together = ('vendor', 'model_number')
        verbose_name = "Model"
        verbose_name_plural = "Models"
        ordering = ['vendor', 'model_number']

    def __str__(self):
        return '{} by {}'.format(self.model_number, self.vendor)


class Rack(models.Model):
    rack = models.CharField(
        max_length=4,
        validators=[
            RegexValidator("^[A-Z]{1,2}[0-9]{2}$",
                           message="Row number must be specified by one or two capital letters.")
        ],
    )
    site = models.ForeignKey(
        Site,
        on_delete=models.PROTECT,
    )
    version = models.ForeignKey(
        ChangePlan,
        on_delete=models.CASCADE
    )
    decommissioned = models.BooleanField(
        # Used to show deleted racks with decommissioned assets on them
        default=False
    )

    def __str__(self):
        return "Rack {} Site {}".format(self.rack, self.site)

    class Meta:
        unique_together = ['rack', 'site', 'version']
        ordering = 'rack',

    IDENTITY_FIELDS = ['rack', 'site']


class Asset(models.Model):
    asset_number = models.IntegerField(
        null=True,
        blank=True
    )
    hostname = models.CharField(
        blank=True,
        null=True,
        max_length=64,
        validators=[
            RegexValidator(r"^&|([a-zA-Z0-9](?:(?:[a-zA-Z0-9-]*|(?<!-)\.(?![-.]))*[a-zA-Z0-9]+)?)$",
                           message="Hostname must be compliant with RFC 1034.")
        ]
    )
    site = models.ForeignKey(
        Site,
        on_delete=models.PROTECT,
    )
    rack = models.ForeignKey(
        Rack,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    rack_position = models.IntegerField(
        validators=[
            MinValueValidator(1,
                              message="Rack position must be at least 1.")
        ],
        null=True,
        blank=True
    )
    itmodel = models.ForeignKey(
        ITModel,
        on_delete=models.PROTECT,
        verbose_name="Model"
    )
    owner = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET(None),
        related_name='owned_assets'
    )
    display_color = models.CharField(
        max_length=10,
        blank=True, 
        validators=[
            RegexValidator("^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                           message="Please enter a valid color code.")  # Color code
        ],
        default="#ddd",
        null=True, # Thought these were nullable???
    )
    cpu = models.CharField(
        max_length=64,
        blank=True,
        null=True, # Thought these were nullable???
    )
    memory = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Memory (GB)",
        validators=[
            MinValueValidator(0,
                              message="Number of GB of memory must be at least 0.")
        ]
    )
    storage = models.CharField(
        max_length=128,
        blank=True,
        null=True, # Thought these were nullable???
    )
    comment = models.TextField(
        blank=True,
        validators=[
            RegexValidator("(?m)""(?![ \t]*(,|$))",
                           message="Comments must be enclosed by double quotes if value contains line breaks.")
        ]
    )
    version = models.ForeignKey(
        ChangePlan,
        on_delete=models.CASCADE
    )

    class Decommissioned(models.TextChoices):
        COMMISSIONED = 'C'
        # DECOMMISSIONED = None

    commissioned = models.CharField(
        max_length=1,
        null=True,
        choices=Decommissioned.choices,
        default=Decommissioned.COMMISSIONED
    )
    decommissioned_timestamp = models.DateTimeField(
        null=True,
        blank=True
    )
    decommissioned_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='decommissioned_assets'
    )
    blade_chassis = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        default=None,
        on_delete=models.PROTECT,
        related_name="blade_set"
    )
    slot = models.IntegerField(
        null=True,
        blank=True,
        default=None,
        validators=[
            MinValueValidator(1,
                              message="Chassis slot position must be at least 1."),
            MaxValueValidator(14,
                              message="Chassis slot position must be at most 14."),
        ]
    )

    class Meta:
        unique_together = [
            # Allow decommissioned assets to have conflicting hostnames
            ['hostname', 'version', 'commissioned'],
            ['asset_number', 'version']
        ]
        ordering = 'hostname', 'asset_number'

    def __str__(self):
        if self.hostname is not None and len(self.hostname) > 0:
            return self.hostname
        # return "#{}: Rack {} U{} in {}".format(self.asset_number, self.rack.rack, self.rack_position, self.site)
        return str(self.asset_number)

    IDENTITY_FIELDS = ['asset_number']
