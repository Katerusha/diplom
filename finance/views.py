from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Sum, F
from django.db import transaction
from datetime import date, timedelta
from .models import Account, Category, Transaction, RecurringPayment, Debt, Reminder
from .forms import AccountForm, CategoryForm, TransactionForm, RecurringPaymentForm, DebtForm, ReminderForm


class AccountListView(LoginRequiredMixin, ListView):
    model = Account
    template_name = 'finance/account_list.html'
    context_object_name = 'accounts'

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)


class AccountCreateView(LoginRequiredMixin, CreateView):
    model = Account
    form_class = AccountForm
    template_name = 'finance/account_form.html'
    success_url = reverse_lazy('finance:account_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class AccountUpdateView(LoginRequiredMixin, UpdateView):
    model = Account
    form_class = AccountForm
    template_name = 'finance/account_form.html'
    success_url = reverse_lazy('finance:account_list')

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)


class AccountDeleteView(LoginRequiredMixin, DeleteView):
    model = Account
    template_name = 'finance/account_confirm_delete.html'
    success_url = reverse_lazy('finance:account_list')
    context_object_name = 'account'

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)


@login_required
def account_toggle_favorite(request, pk):
    account = get_object_or_404(Account, pk=pk, user=request.user)
    # Снять избранное у всех других счетов, если этот становится избранным
    if not account.is_favorite:
        Account.objects.filter(user=request.user, is_favorite=True).update(is_favorite=False)
    account.is_favorite = not account.is_favorite
    account.save(update_fields=['is_favorite'])
    return redirect('finance:account_list')


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'finance/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user).select_related('parent')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['income_categories'] = self.get_queryset().filter(type=Category.CategoryType.INCOME)
        ctx['expense_categories'] = self.get_queryset().filter(type=Category.CategoryType.EXPENSE)
        return ctx


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'finance/category_form.html'
    success_url = reverse_lazy('finance:category_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'finance/category_form.html'
    success_url = reverse_lazy('finance:category_list')

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'finance/category_confirm_delete.html'
    success_url = reverse_lazy('finance:category_list')
    context_object_name = 'category'

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


def _adjust_balance(account, amount, txn_type, sign=1):
    delta = amount if txn_type == Transaction.TransactionType.INCOME else -amount
    Account.objects.filter(pk=account.pk).update(balance=F('balance') + (sign * delta))


class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'finance/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 20

    def get_queryset(self):
        qs = Transaction.objects.filter(user=self.request.user).select_related('account', 'category')
        txn_type = self.request.GET.get('type', '')
        account_id = self.request.GET.get('account', '')
        if txn_type:
            qs = qs.filter(type=txn_type)
        if account_id:
            qs = qs.filter(account_id=account_id)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['accounts'] = Account.objects.filter(user=self.request.user)
        ctx['selected_type'] = self.request.GET.get('type', '')
        ctx['selected_account'] = self.request.GET.get('account', '')
        return ctx


class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'finance/transaction_form.html'
    success_url = reverse_lazy('finance:transaction_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        with transaction.atomic():
            response = super().form_valid(form)
            _adjust_balance(self.object.account, self.object.amount, self.object.type, sign=1)
        return response


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'finance/transaction_form.html'
    success_url = reverse_lazy('finance:transaction_list')

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).select_related('account')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        old = self.get_object()
        old_account = old.account
        old_amount = old.amount
        old_type = old.type
        with transaction.atomic():
            response = super().form_valid(form)
            _adjust_balance(old_account, old_amount, old_type, sign=-1)
            _adjust_balance(self.object.account, self.object.amount, self.object.type, sign=1)
        return response


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = Transaction
    template_name = 'finance/transaction_confirm_delete.html'
    success_url = reverse_lazy('finance:transaction_list')
    context_object_name = 'transaction'

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def form_valid(self, form):
        with transaction.atomic():
            _adjust_balance(self.object.account, self.object.amount, self.object.type, sign=-1)
            return super().form_valid(form)


@login_required
def charts_view(request):
    import pandas as pd
    import plotly.graph_objects as go
    import plotly.express as px

    user = request.user
    today = date.today()
    first_day_of_month = today.replace(day=1)
    six_months_ago = (today.replace(day=1) - timedelta(days=180)).replace(day=1)

    transactions = Transaction.objects.filter(
        user=user, date__gte=six_months_ago
    ).values('date', 'type', 'amount', 'category__name').order_by('date')

    df = pd.DataFrame(list(transactions))
    charts = {}

    if not df.empty:
        df['amount'] = df['amount'].astype(float)
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.to_period('M').astype(str)

        # Bar chart: monthly income vs expense
        monthly = df.pivot_table(
            index='month', columns='type', values='amount',
            aggfunc='sum', fill_value=0
        )
        for col in ['income', 'expense']:
            if col not in monthly.columns:
                monthly[col] = 0

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=monthly.index, y=monthly['income'],
            name='Доходы', marker_color='#198754'
        ))
        fig_bar.add_trace(go.Bar(
            x=monthly.index, y=monthly['expense'],
            name='Расходы', marker_color='#dc3545'
        ))
        fig_bar.update_layout(
            barmode='group',
            template='plotly_white',
            margin=dict(l=10, r=10, t=30, b=10),
            height=350,
            legend=dict(orientation='h', y=1.1),
        )
        charts['bar'] = fig_bar.to_html(full_html=False, config={'displayModeBar': False})

        # Pie chart: expenses by category for current month
        expenses_this_month = df[
            (df['date'] >= pd.Timestamp(first_day_of_month)) &
            (df['type'] == 'expense')
        ]
        if not expenses_this_month.empty:
            pie_data = expenses_this_month.groupby('category__name')['amount'].sum().sort_values(ascending=False)
            fig_pie = px.pie(
                values=pie_data.values, names=pie_data.index,
                hole=0.4, template='plotly_white'
            )
            fig_pie.update_layout(
                margin=dict(l=10, r=10, t=30, b=10),
                height=350,
            )
            charts['pie'] = fig_pie.to_html(full_html=False, config={'displayModeBar': False})

        # Line chart: cumulative balance over time
        df_sorted = df.sort_values('date')
        df_sorted['delta'] = df_sorted.apply(
            lambda r: r['amount'] if r['type'] == 'income' else -r['amount'], axis=1
        )
        df_sorted['cumulative'] = df_sorted['delta'].cumsum()
        daily = df_sorted.groupby('date')['cumulative'].last().reset_index()

        starting_balance = Account.objects.filter(user=user).aggregate(
            total=Sum('balance')
        )['total'] or 0
        initial_balance = float(starting_balance) - float(df_sorted['delta'].sum())
        daily['cumulative'] += initial_balance

        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=daily['date'], y=daily['cumulative'],
            mode='lines+markers', name='Баланс',
            line=dict(color='#0d6efd', width=2),
            marker=dict(size=4),
        ))
        fig_line.update_layout(
            template='plotly_white',
            margin=dict(l=10, r=10, t=30, b=10),
            height=300,
        )
        charts['line'] = fig_line.to_html(full_html=False, config={'displayModeBar': False})

    return render(request, 'finance/charts.html', {'charts': charts})


class RecurringPaymentListView(LoginRequiredMixin, ListView):
    model = RecurringPayment
    template_name = 'finance/recurring_list.html'
    context_object_name = 'payments'

    def get_queryset(self):
        return RecurringPayment.objects.filter(user=self.request.user).select_related('account', 'category')


class RecurringPaymentCreateView(LoginRequiredMixin, CreateView):
    model = RecurringPayment
    form_class = RecurringPaymentForm
    template_name = 'finance/recurring_form.html'
    success_url = reverse_lazy('finance:recurring_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class RecurringPaymentUpdateView(LoginRequiredMixin, UpdateView):
    model = RecurringPayment
    form_class = RecurringPaymentForm
    template_name = 'finance/recurring_form.html'
    success_url = reverse_lazy('finance:recurring_list')

    def get_queryset(self):
        return RecurringPayment.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class RecurringPaymentDeleteView(LoginRequiredMixin, DeleteView):
    model = RecurringPayment
    template_name = 'finance/recurring_confirm_delete.html'
    success_url = reverse_lazy('finance:recurring_list')
    context_object_name = 'payment'

    def get_queryset(self):
        return RecurringPayment.objects.filter(user=self.request.user)


class DebtListView(LoginRequiredMixin, ListView):
    model = Debt
    template_name = 'finance/debt_list.html'
    context_object_name = 'debts'

    def get_queryset(self):
        qs = Debt.objects.filter(user=self.request.user)
        tab = self.request.GET.get('tab', '')
        if tab in ('owed_to_me', 'i_owe'):
            qs = qs.filter(type=tab)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_tab'] = self.request.GET.get('tab', 'all')
        return ctx


class DebtCreateView(LoginRequiredMixin, CreateView):
    model = Debt
    form_class = DebtForm
    template_name = 'finance/debt_form.html'
    success_url = reverse_lazy('finance:debt_list')

    def get_initial(self):
        initial = super().get_initial()
        debt_type = self.request.GET.get('type', '')
        if debt_type in ('owed_to_me', 'i_owe'):
            initial['type'] = debt_type
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['hide_type'] = bool(self.request.GET.get('type', ''))
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class DebtUpdateView(LoginRequiredMixin, UpdateView):
    model = Debt
    form_class = DebtForm
    template_name = 'finance/debt_form.html'
    success_url = reverse_lazy('finance:debt_list')

    def get_queryset(self):
        return Debt.objects.filter(user=self.request.user)


class DebtDeleteView(LoginRequiredMixin, DeleteView):
    model = Debt
    template_name = 'finance/debt_confirm_delete.html'
    success_url = reverse_lazy('finance:debt_list')
    context_object_name = 'debt'

    def get_queryset(self):
        return Debt.objects.filter(user=self.request.user)


class ReminderListView(LoginRequiredMixin, ListView):
    model = Reminder
    template_name = 'finance/reminder_list.html'
    context_object_name = 'reminders'

    def get_queryset(self):
        return Reminder.objects.filter(user=self.request.user).select_related('transaction')


class ReminderCreateView(LoginRequiredMixin, CreateView):
    model = Reminder
    form_class = ReminderForm
    template_name = 'finance/reminder_form.html'
    success_url = reverse_lazy('finance:reminder_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ReminderUpdateView(LoginRequiredMixin, UpdateView):
    model = Reminder
    form_class = ReminderForm
    template_name = 'finance/reminder_form.html'
    success_url = reverse_lazy('finance:reminder_list')

    def get_queryset(self):
        return Reminder.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class ReminderDeleteView(LoginRequiredMixin, DeleteView):
    model = Reminder
    template_name = 'finance/reminder_confirm_delete.html'
    success_url = reverse_lazy('finance:reminder_list')
    context_object_name = 'reminder'

    def get_queryset(self):
        return Reminder.objects.filter(user=self.request.user)
