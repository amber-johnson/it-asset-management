from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Permission
from django.contrib.auth.models import User


@receiver(pre_save, sender=Permission)
def add_perms(sender, instance, *args, **kwargs):
    user = User.objects.get(username=instance.user)
    if instance.admin_perm:
        instance.model_perm = True
        instance.asset_perm = True
        instance.power_perm = True
        instance.audit_perm = True
        instance.site_perm = 'Global'
        user.is_staff = True
        user.is_admin = True
        user.is_superuser = True
        user.save()
    else:
        user.is_staff = False
        user.is_admin = False
        user.is_superuser = False
        user.save()


@receiver(post_save, sender=User)
def add_user_perm(instance, created, *args, **kwargs):
    if created and not Permission.objects.filter(user=instance).exists():
        perm = Permission(site_perm="", user=instance)
        if instance.is_superuser:
            perm.admin_perm = True
            perm.site_perm = 'Global'
        perm.save()
