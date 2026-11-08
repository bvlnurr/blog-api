from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    list_display = (
        "id",
        "email",
        "first_name",
        "last_name",
        "user_role",
        "account_status",
    )
    ordering = ("email",)
    search_fields = ("email", "first_name", "last_name")

    fieldsets = (
        ("Account", {"fields": ("email", "password")}),
        (
            "Personal information",
            {"fields": ("first_name", "last_name")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (
            "Created user",
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )

    list_filter = ("is_staff", "is_superuser", "is_active")
    list_per_page = 20

    readonly_fields = ("last_login",)

    @admin.display(description="Status")
    def account_status(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="color: green;font-weight: bold;">Active</span.'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">Inactive</span>'
        )
    @admin.display(description="Role")
    def user_role(self, obj):
        if obj.is_superuser:
            return "Superuser"
        if obj.is_staff:
            return "Staff"
        return "User"
    
    actions = ["activate_users", "deactivate_users"]

    @admin.action(description="Activate selected users")
    def activate_users(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(
            request,
            f"{count} users activated.",
            messages.SUCCESS,
        )

    @admin.action(description="Deactivate selected users")
    def deactivate_users(self, request, queryset):
        queryset = queryset.exclude(is_superuser=True)
        count = queryset.update(is_active=False)
        self.message_user(
            request,
            f"{count} users deactivated.",
            messages.SUCCESS,
        )

    tabs = [
        ("Account", ["email", "password"]),
        ("Personal", ["first_name", "last_name"]),
        ("Permissions", ["is_active", "is_staff", "is_superuser"]),
    ]
                