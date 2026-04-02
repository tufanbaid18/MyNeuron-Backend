from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Event, Member, Program, EventCategoryPricing, ManualPayment, Registration



@admin.register(User)
class UserAdmin(BaseUserAdmin):

    list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff', 'is_verified', 'is_verified_lite')
    ordering = ('email',)
    search_fields = ('email', 'first_name')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {
            'fields': (
                'first_name',
                'middle_name',
                'last_name',
                'profile_image',
                'profile_title',
            )
        }),
        ('Role info', {'fields': ('role','is_verified', 'is_verified_lite')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role'),
        }),
    )


class EventCategoryPricingInline(admin.TabularInline):
    model = EventCategoryPricing
    extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    inlines = [EventCategoryPricingInline]

admin.site.register(Member)

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("id", "event", "speaker", "venue", "topic", "date", "start_time", "end_time")
    list_filter = ("event", "date")
    search_fields = ("topic", "speaker__email", "event__name")


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "event",
        "pricing",
        "amount",
        "status",
        "created_at",
    )

    list_filter = ("status", "event")
    search_fields = ("email", "user__email")

@admin.register(ManualPayment)
class ManualPaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "registration",
        "transaction_id",
        "status",
        "created_at",
        "screenshot_preview",
    )

    list_filter = ("status", "created_at")
    search_fields = ("transaction_id", "registration__email")

    actions = ["approve_payments", "reject_payments"]

    def screenshot_preview(self, obj):
        if obj.screenshot:
            return format_html(
                '<img src="{}" width="100" />',
                obj.screenshot.url
            )
        return "No Image"

    screenshot_preview.short_description = "Screenshot"

    # ✅ APPROVE
    def approve_payments(self, request, queryset):
        for payment in queryset:
            if payment.status != "VERIFIED":
                payment.status = "VERIFIED"
                payment.save()  # 🔥 This handles everything

        self.message_user(request, "Selected payments approved")

    # ❌ REJECT
    def reject_payments(self, request, queryset):
        for payment in queryset:
            if payment.status != "REJECTED":
                payment.status = "REJECTED"
                payment.save()  # 🔥 This handles everything

        self.message_user(request, "Selected payments rejected")