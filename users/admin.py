# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User, ServiceCart, ServicePayment

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'iin', 'phone', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'iin', 'phone', 'first_name', 'last_name')
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('phone', 'iin')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Личная информация', {'fields': ('first_name', 'last_name', 'phone', 'iin')}),
    )

admin.site.register(User, CustomUserAdmin)


@admin.register(ServiceCart)
class ServiceCartAdmin(admin.ModelAdmin):
    list_display = ['user', 'service', 'service_price', 'added_at']
    list_filter = ['added_at', 'service__category']
    search_fields = ['user__username', 'service__name']
    raw_id_fields = ['user', 'service']
    
    def service_price(self, obj):
        return f"{obj.service.price:,} ₸"
    service_price.short_description = 'Цена услуги'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'service')


@admin.register(ServicePayment)
class ServicePaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'get_services_list', 'total_amount_display', 'status', 'created_at', 'receipt_file', 'act_file']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['services']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'services', 'total_amount', 'status')
        }),
        ('Оплата', {
            'fields': ('receipt_file', 'act_file')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_amount_display(self, obj):
        return f"{obj.total_amount:,} ₸"
    total_amount_display.short_description = 'Сумма'
    
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').prefetch_related('services')
    
    actions = ['approve_payments', 'reject_payments']
    
    def approve_payments(self, request, queryset):
        count = queryset.update(status='approved')
        self.message_user(request, f'Одобрено {count} платежей')
    approve_payments.short_description = 'Одобрить выбранные платежи'
    
    def reject_payments(self, request, queryset):
        count = queryset.update(status='rejected')
        self.message_user(request, f'Отклонено {count} платежей')
    reject_payments.short_description = 'Отклонить выбранные платежи'