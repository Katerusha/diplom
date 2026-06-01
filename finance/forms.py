from django import forms
from django.utils.safestring import mark_safe
from .models import Account, Category, Transaction, RecurringPayment, Debt, Reminder

CURRENCY_CHOICES = [
    ('RUB', 'RUB — Российский рубль'),
    ('USD', 'USD — Доллар США'),
    ('EUR', 'EUR — Евро'),
    ('GBP', 'GBP — Фунт стерлингов'),
    ('CNY', 'CNY — Китайский юань'),
    ('JPY', 'JPY — Японская иена'),
    ('KZT', 'KZT — Казахстанский тенге'),
    ('BYN', 'BYN — Белорусский рубль'),
    ('TRY', 'TRY — Турецкая лира'),
    ('CHF', 'CHF — Швейцарский франк'),
]


class DatalistInput(forms.TextInput):
    def __init__(self, choices=None, datalist_id='currency-list', **kwargs):
        self.choices = choices or []
        self.datalist_id = datalist_id
        super().__init__(**kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        attrs['list'] = self.datalist_id
        attrs['autocomplete'] = 'off'
        html = super().render(name, value, attrs, renderer)
        options = ''.join(
            f'<option value="{code}" data-label="{label}">{code}</option>'
            for code, label in self.choices
        )
        datalist = f'<datalist id="{self.datalist_id}">{options}</datalist>'
        return mark_safe(html + datalist)


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['name', 'balance', 'type', 'currency']
        labels = {
            'name': 'Название',
            'balance': 'Начальный баланс',
            'type': 'Тип счёта',
            'currency': 'Валюта',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'balance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'currency': DatalistInput(choices=CURRENCY_CHOICES, attrs={'class': 'form-control'}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'type', 'parent']
        labels = {
            'name': 'Название',
            'type': 'Тип',
            'parent': 'Родительская категория',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['parent'].required = False
        self.fields['parent'].empty_label = '— Нет (верхний уровень) —'
        if user:
            self.fields['parent'].queryset = Category.objects.filter(user=user)


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['account', 'type', 'category', 'amount', 'date', 'description']
        labels = {
            'account': 'Счёт',
            'type': 'Тип',
            'category': 'Категория',
            'amount': 'Сумма',
            'date': 'Дата',
            'description': 'Описание',
        }
        widgets = {
            'account': forms.Select(attrs={'class': 'form-select'}),
            'type': forms.RadioSelect(attrs={'class': 'btn-check'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['category'].required = False
        self.fields['category'].empty_label = '— Выберите категорию —'
        if user:
            self.fields['account'].queryset = Account.objects.filter(user=user)
            self.fields['category'].queryset = Category.objects.filter(user=user)
            if not self.initial.get('account'):
                fav = Account.objects.filter(user=user, is_favorite=True).first()
                if fav:
                    self.initial['account'] = fav.pk

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        txn_type = cleaned_data.get('type')
        if category and txn_type and category.type != txn_type:
            self.add_error('category', 'Тип категории не соответствует типу транзакции')
        return cleaned_data


class RecurringPaymentForm(forms.ModelForm):
    class Meta:
        model = RecurringPayment
        fields = ['name', 'amount', 'account', 'type', 'category', 'frequency', 'next_date', 'is_active']
        labels = {
            'name': 'Название',
            'amount': 'Сумма',
            'account': 'Счёт',
            'type': 'Тип',
            'category': 'Категория',
            'frequency': 'Периодичность',
            'next_date': 'Следующий платёж',
            'is_active': 'Активен',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'account': forms.Select(attrs={'class': 'form-select'}),
            'type': forms.RadioSelect(attrs={'class': 'btn-check'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'frequency': forms.Select(attrs={'class': 'form-select'}),
            'next_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['category'].required = False
        self.fields['category'].empty_label = '— Выберите категорию —'
        if user:
            self.fields['account'].queryset = Account.objects.filter(user=user)
            self.fields['category'].queryset = Category.objects.filter(user=user)
            if not self.initial.get('account'):
                fav = Account.objects.filter(user=user, is_favorite=True).first()
                if fav:
                    self.initial['account'] = fav.pk


class DebtForm(forms.ModelForm):
    adjustment = forms.DecimalField(
        label='Сумма', max_digits=12, decimal_places=2, required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'})
    )
    adjustment_mode = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Debt
        fields = ['creditor_name', 'amount', 'type', 'due_date', 'status', 'description']
        labels = {
            'creditor_name': 'Кредитор / должник',
            'amount': 'Сумма',
            'type': 'Тип',
            'due_date': 'Дата возврата',
            'status': 'Статус',
            'description': 'Описание',
        }
        widgets = {
            'creditor_name': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        hide_type = kwargs.pop('hide_type', False)
        super().__init__(*args, **kwargs)
        is_update = self.instance and self.instance.pk is not None
        if hide_type:
            self.fields['type'].widget = forms.HiddenInput()
            self.fields['type'].label = ''
        if is_update:
            self.fields['amount'].widget = forms.HiddenInput()
            self.fields['adjustment'].initial = 0
        else:
            self.fields['adjustment'].widget = forms.HiddenInput()
            self.fields['adjustment_mode'].widget = forms.HiddenInput()

    def clean(self):
        cleaned = super().clean()
        if self.instance and self.instance.pk:
            mode = cleaned.get('adjustment_mode', '')
            adj = cleaned.get('adjustment') or 0
            old_amount = self.instance.amount
            if mode == 'add':
                cleaned['amount'] = old_amount + adj
            elif mode == 'subtract':
                cleaned['amount'] = max(old_amount - adj, 0)
            elif mode == 'manual':
                if adj and adj > 0:
                    cleaned['amount'] = adj
                else:
                    self.add_error('adjustment', 'Укажите сумму для ручного режима')
            elif not mode:
                cleaned['amount'] = old_amount
        return cleaned


class ReminderForm(forms.ModelForm):
    class Meta:
        model = Reminder
        fields = ['title', 'message', 'remind_date', 'is_completed', 'transaction']
        labels = {
            'title': 'Заголовок',
            'message': 'Сообщение',
            'remind_date': 'Дата напоминания',
            'is_completed': 'Выполнено',
            'transaction': 'Связанная транзакция',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'remind_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'is_completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'transaction': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['transaction'].required = False
        self.fields['transaction'].empty_label = '— Нет —'
        if user:
            self.fields['transaction'].queryset = Transaction.objects.filter(user=user).select_related('account')
