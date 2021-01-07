from django.contrib import admin
from django.contrib.auth.forms import UsernameField, UserChangeForm, UserCreationForm
from .models import UserProfile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth.models import Group

# Register your models here.


class UserCreateForm(UserCreationForm):

    class Meta:
        model = UserProfile
        fields = ('username', 'sex', 'style')


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreateForm

    list_display = ('username', 'email' 'sex', 'style', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'sex', 'style')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'sex', 'style', 'password1', 'password2'),
        }),
    )

    list_display = ('username', 'email', 'first_name', 'last_name', 'sex', 'style', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'sex', 'style')
    ordering = ('username',)
    filter_horizontal = ()


admin.site.register(UserProfile, UserAdmin)
admin.site.unregister(Group)