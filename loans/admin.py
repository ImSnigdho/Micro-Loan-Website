from django.contrib import admin
from .models import SiteSettings, UserProfile, LoanApplication, Transaction, InboxMessage


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('General', {'fields': ('site_name', 'logo_image', 'logo_url', 'youtube_url')}),
        ('Payment Numbers', {'fields': ('bkash_number', 'nagad_number', 'rocket_number')}),
        ('Loan Settings', {'fields': ('interest_rate_min', 'interest_rate_max', 'security_deposit_percent')}),
        ('Banner', {'fields': ('banner_tagline', 'banner_sub')}),
    )

    def has_add_permission(self, request):
        # Only one settings row allowed
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'occupation', 'balance', 'created_at')
    search_fields = ('user__username', 'phone')
    list_filter = ('occupation',)


@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'applicant_name', 'amount', 'duration_months', 'interest_rate', 'status', 'applied_at')
    list_filter = ('status', 'purpose', 'duration_months')
    search_fields = ('user__username', 'applicant_name')
    readonly_fields = ('applied_at', 'total_interest_display', 'total_payable_display', 'monthly_payment_display')
    fieldsets = (
        ('Applicant', {'fields': ('user', 'applicant_name', 'status', 'admin_note')}),
        ('Loan Details', {'fields': ('amount', 'duration_months', 'purpose', 'interest_rate', 'security_deposit')}),
        ('NID Documents', {'fields': ('nid_front', 'nid_back')}),
        ('Calculated', {'fields': ('total_interest_display', 'total_payable_display', 'monthly_payment_display', 'applied_at', 'approved_at')}),
    )

    def total_interest_display(self, obj):
        return f'৳{obj.total_interest}'
    total_interest_display.short_description = 'Total Interest'

    def total_payable_display(self, obj):
        return f'৳{obj.total_payable}'
    total_payable_display.short_description = 'Total Payable'

    def monthly_payment_display(self, obj):
        return f'৳{obj.monthly_payment}'
    monthly_payment_display.short_description = 'Monthly Payment'


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'amount', 'payment_method', 'status', 'created_at')
    list_filter = ('transaction_type', 'payment_method', 'status')
    search_fields = ('user__username', 'phone_number')


@admin.register(InboxMessage)
class InboxMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_read', 'created_at')
    list_filter = ('is_read',)
    search_fields = ('user__username', 'title')
