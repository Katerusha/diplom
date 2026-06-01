from django.contrib import admin
from .models import Account, Category, Transaction, RecurringPayment, Debt, Reminder


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'balance', 'currency', 'user', 'created_at')
    list_filter = ('type', 'currency')
    search_fields = ('name', 'user__username')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'parent', 'user')
    list_filter = ('type',)
    search_fields = ('name', 'user__username')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'account', 'category', 'type', 'amount', 'date', 'created_at')
    list_filter = ('type', 'date')
    search_fields = ('description', 'user__username')


@admin.register(RecurringPayment)
class RecurringPaymentAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'amount', 'type', 'frequency', 'next_date', 'is_active')
    list_filter = ('type', 'frequency', 'is_active')


@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ('creditor_name', 'user', 'amount', 'type', 'status', 'due_date')
    list_filter = ('type', 'status')


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'remind_date', 'is_completed')
    list_filter = ('is_completed',)
