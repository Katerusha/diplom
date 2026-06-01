from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal


class Account(models.Model):
    class AccountType(models.TextChoices):
        CASH = 'cash', 'Наличные'
        CARD = 'card', 'Банковская карта'
        DEPOSIT = 'deposit', 'Вклад'
        CREDIT = 'credit', 'Кредитная карта'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='accounts')
    name = models.CharField('Название', max_length=100)
    balance = models.DecimalField('Баланс', max_digits=12, decimal_places=2, default=Decimal('0.00'))
    type = models.CharField('Тип', max_length=10, choices=AccountType.choices, default=AccountType.CARD)
    currency = models.CharField('Валюта', max_length=3, default='RUB')
    is_favorite = models.BooleanField('Избранный', default=False)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Счёт'
        verbose_name_plural = 'Счета'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.get_type_display()})'


class Category(models.Model):
    class CategoryType(models.TextChoices):
        INCOME = 'income', 'Доход'
        EXPENSE = 'expense', 'Расход'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField('Название', max_length=100)
    type = models.CharField('Тип', max_length=7, choices=CategoryType.choices)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories', verbose_name='Родительская категория')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['type', 'name']

    def __str__(self):
        if self.parent:
            return f'{self.parent.name} → {self.name}'
        return f'{self.name} ({self.get_type_display()})'


class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        INCOME = 'income', 'Доход'
        EXPENSE = 'expense', 'Расход'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions', verbose_name='Счёт')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions', verbose_name='Категория')
    type = models.CharField('Тип', max_length=7, choices=TransactionType.choices)
    amount = models.DecimalField('Сумма', max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    date = models.DateField('Дата')
    description = models.CharField('Описание', max_length=255, blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'
        ordering = ['-date', '-created_at']

    def __str__(self):
        prefix = '+' if self.type == self.TransactionType.INCOME else '-'
        return f'{prefix}{self.amount} ({self.account.name})'


class RecurringPayment(models.Model):
    class Frequency(models.TextChoices):
        WEEKLY = 'weekly', 'Еженедельно'
        MONTHLY = 'monthly', 'Ежемесячно'
        QUARTERLY = 'quarterly', 'Ежеквартально'
        YEARLY = 'yearly', 'Ежегодно'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recurring_payments')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='recurring_payments', verbose_name='Счёт')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='recurring_payments', verbose_name='Категория')
    name = models.CharField('Название', max_length=200)
    amount = models.DecimalField('Сумма', max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    type = models.CharField('Тип', max_length=7, choices=Transaction.TransactionType.choices)
    frequency = models.CharField('Периодичность', max_length=10, choices=Frequency.choices, default=Frequency.MONTHLY)
    next_date = models.DateField('Следующий платёж')
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        verbose_name = 'Регулярный платёж'
        verbose_name_plural = 'Регулярные платежи'
        ordering = ['next_date']

    def __str__(self):
        return f'{self.name} ({self.amount} р.)'


class Debt(models.Model):
    class DebtType(models.TextChoices):
        OWED_TO_ME = 'owed_to_me', 'Мне должны'
        I_OWE = 'i_owe', 'Я должен'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Активен'
        PAID = 'paid', 'Погашен'
        OVERDUE = 'overdue', 'Просрочен'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='debts')
    creditor_name = models.CharField('Кредитор / должник', max_length=200)
    amount = models.DecimalField('Сумма', max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    type = models.CharField('Тип', max_length=10, choices=DebtType.choices)
    due_date = models.DateField('Дата возврата')
    status = models.CharField('Статус', max_length=10, choices=Status.choices, default=Status.ACTIVE)
    description = models.CharField('Описание', max_length=255, blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Долг'
        verbose_name_plural = 'Долги'
        ordering = ['status', 'due_date']

    def __str__(self):
        return f'{self.creditor_name}: {self.amount} р.'


class Reminder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reminders')
    title = models.CharField('Заголовок', max_length=200)
    message = models.TextField('Сообщение', blank=True)
    remind_date = models.DateField('Дата напоминания')
    is_completed = models.BooleanField('Выполнено', default=False)
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True, related_name='reminders', verbose_name='Связанная транзакция')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Напоминание'
        verbose_name_plural = 'Напоминания'
        ordering = ['is_completed', 'remind_date']

    def __str__(self):
        return self.title
