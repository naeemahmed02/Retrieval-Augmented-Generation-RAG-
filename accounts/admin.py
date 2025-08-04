from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account

# @admin.register(Account)
# class AccountAdmin(UserAdmin):
#     list_display = ('email', 'first_name', 'last_name', 'username', 'is_active')
#     ordering = ('-date_joined',)
#     readonly_fields = ('date_joined', 'last_login')
#     list_filter = ('is_staff', 'is_superuser', 'is_active',)
#     filter_horizontal = ()
#     fieldsets = UserAdmin.fieldsets + (
#         (),
#     )






@admin.register(Account)
class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username', 'is_active')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    filter_horizontal = ()

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone_number',)}),
    )
