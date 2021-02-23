from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from rest_framework.authtoken.models import Token


admin.site.unregister(Group)
admin.site.unregister(Token)
admin.site.site_header = 'Hyposoft Administration'
admin.site.site_title = "Hyposoft Administration"
admin.site.index_title = "Hyposoft Administration"


class MyUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_admin')
    list_filter = ()
    fieldsets = (
        ('Account', {
            'fields': ('username', 'password', 'is_staff')
        }),

        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        })
    )

    def is_admin(self, obj):
        return obj.is_staff

    is_admin.boolean = True
    is_admin.short_description = "Admin Status"

    def get_form(self, request, obj=None, **kwargs):
        form = super(MyUserAdmin, self).get_form(request, obj, **kwargs)
        # base_fields don't have the field is_staff
        print(form.base_fields)
        if 'is_staff' in form.base_fields:
            form.base_fields['is_staff'].label = 'Is Admin'
            form.base_fields['is_staff'].help_text = 'Allows this user to modify objects on the site and in the admin page.'
        return form


admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
