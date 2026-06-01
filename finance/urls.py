from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('accounts/', views.AccountListView.as_view(), name='account_list'),
    path('accounts/new/', views.AccountCreateView.as_view(), name='account_create'),
    path('accounts/<int:pk>/edit/', views.AccountUpdateView.as_view(), name='account_update'),
    path('accounts/<int:pk>/delete/', views.AccountDeleteView.as_view(), name='account_delete'),
    path('accounts/<int:pk>/toggle-favorite/', views.account_toggle_favorite, name='account_toggle_favorite'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/new/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    path('transactions/', views.TransactionListView.as_view(), name='transaction_list'),
    path('transactions/new/', views.TransactionCreateView.as_view(), name='transaction_create'),
    path('transactions/<int:pk>/edit/', views.TransactionUpdateView.as_view(), name='transaction_update'),
    path('transactions/<int:pk>/delete/', views.TransactionDeleteView.as_view(), name='transaction_delete'),
    path('charts/', views.charts_view, name='charts'),
    path('recurring/', views.RecurringPaymentListView.as_view(), name='recurring_list'),
    path('recurring/new/', views.RecurringPaymentCreateView.as_view(), name='recurring_create'),
    path('recurring/<int:pk>/edit/', views.RecurringPaymentUpdateView.as_view(), name='recurring_update'),
    path('recurring/<int:pk>/delete/', views.RecurringPaymentDeleteView.as_view(), name='recurring_delete'),
    path('debts/', views.DebtListView.as_view(), name='debt_list'),
    path('debts/new/', views.DebtCreateView.as_view(), name='debt_create'),
    path('debts/<int:pk>/edit/', views.DebtUpdateView.as_view(), name='debt_update'),
    path('debts/<int:pk>/delete/', views.DebtDeleteView.as_view(), name='debt_delete'),
    path('reminders/', views.ReminderListView.as_view(), name='reminder_list'),
    path('reminders/new/', views.ReminderCreateView.as_view(), name='reminder_create'),
    path('reminders/<int:pk>/edit/', views.ReminderUpdateView.as_view(), name='reminder_update'),
    path('reminders/<int:pk>/delete/', views.ReminderDeleteView.as_view(), name='reminder_delete'),
]
