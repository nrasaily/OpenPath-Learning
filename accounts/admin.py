from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("email",)
    list_display = ("email", "first_name", "last_name", "is_staff", "is_active")
    search_fields = ("email", "first_name", "last_name")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal information", {
            "fields": ("first_name", "last_name", "preferred_language")
        }),
        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "is_staff", "is_superuser"),
        }),
    )


from django import forms
from django.contrib.auth.models import Group
from django.utils import timezone

from .models import TeacherApplication


class TeacherApplicationAdminForm(forms.ModelForm):
    class Meta:
        model = TeacherApplication
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        if (
            cleaned_data.get("status") == TeacherApplication.Status.APPROVED
            and not (
                cleaned_data.get("identity_verified")
                and cleaned_data.get("qualifications_verified")
            )
        ):
            raise forms.ValidationError(
                "Verify identity and qualifications before approving."
            )
        return cleaned_data


@admin.register(TeacherApplication)
class TeacherApplicationAdmin(admin.ModelAdmin):
    form = TeacherApplicationAdminForm
    list_display = (
        "user",
        "country",
        "status",
        "identity_verified",
        "qualifications_verified",
        "submitted_at",
    )
    list_filter = ("status", "country", "identity_verified", "qualifications_verified")
    search_fields = ("user__email", "user__first_name", "user__last_name")
    readonly_fields = ("user", "submitted_at", "reviewed_by", "reviewed_at")
    fields = (
        "user",
        "country",
        "subject_areas",
        "teaching_languages",
        "years_experience",
        "qualifications",
        "identity_verified",
        "qualifications_verified",
        "status",
        "review_notes",
        "reviewed_by",
        "reviewed_at",
        "submitted_at",
    )

    def can_review(self, request):
        return request.user.is_superuser or request.user.groups.filter(
            name="management"
        ).exists()

    def has_module_permission(self, request):
        return self.can_review(request)

    def has_view_permission(self, request, obj=None):
        return self.can_review(request)

    def has_change_permission(self, request, obj=None):
        return self.can_review(request)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        old_status = None
        if change:
            old_status = TeacherApplication.objects.get(pk=obj.pk).status

        if change and obj.status != old_status:
            obj.reviewed_by = request.user
            obj.reviewed_at = timezone.now()

        super().save_model(request, obj, form, change)

        teacher_group, _ = Group.objects.get_or_create(name="teacher")
        if obj.status == TeacherApplication.Status.APPROVED:
            obj.user.groups.add(teacher_group)
        else:
            obj.user.groups.remove(teacher_group)
