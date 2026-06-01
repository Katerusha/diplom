from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.db.models import Sum
from django.core.mail import send_mail
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
from datetime import date
from .forms import CustomUserCreationForm, UserProfileForm
from .models import CustomUser
from finance.models import Account, Transaction

signer = TimestampSigner()


def _send_verification_email(request, user):
    token = signer.sign(f'{user.pk}:{user.email}')
    verify_url = request.build_absolute_uri(
        reverse('accounts:verify_email', args=[token])
    )
    subject = 'Подтверждение почты — MoneyFlow'
    message = render_to_string('accounts/email/verify_email.txt', {
        'user': user,
        'verify_url': verify_url,
    })
    # Вывод ссылки напрямую в терминал (для разработки без SMTP)
    print(f'\n{"="*60}')
    print(f'[MoneyFlow] Письмо для {user.email}')
    print(f'Тема: {subject}')
    print(f'Ссылка подтверждения: {verify_url}')
    print(f'{"="*60}\n', flush=True)
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=True,
    )


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_email_verified = False
            user.save()
            _send_verification_email(request, user)
            messages.info(
                request,
                'На вашу почту отправлено письмо. Подтвердите email, чтобы войти.'
            )
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def verify_email(request, token):
    try:
        data = signer.unsign(token, max_age=86400)
        user_id, email = data.split(':', 1)
        user = CustomUser.objects.get(pk=user_id, email=email)
        if not user.is_email_verified:
            user.is_email_verified = True
            user.save(update_fields=['is_email_verified'])
            messages.success(request, 'Email подтверждён! Теперь вы можете войти.')
        else:
            messages.info(request, 'Email уже подтверждён.')
    except (SignatureExpired, BadSignature, CustomUser.DoesNotExist):
        messages.error(request, 'Ссылка недействительна или истекла. Запросите новое подтверждение.')
    return redirect('login')


def resend_verification(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        try:
            user = CustomUser.objects.get(email=email, is_email_verified=False)
            _send_verification_email(request, user)
            messages.success(request, 'Письмо отправлено повторно. Проверьте почту.')
        except CustomUser.DoesNotExist:
            messages.warning(request, 'Пользователь с такой почтой не найден или уже подтверждён.')
    return redirect('login')


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_email_verified:
            return render(self.request, self.template_name, {
                'form': form,
                'unverified_email': user.email,
            })
        remember_me = self.request.POST.get('remember_me')
        if remember_me:
            self.request.session.set_expiry(60 * 60 * 24 * 30)
        return super().form_valid(form)


@login_required
def home(request):
    today = date.today()
    first_day_of_month = today.replace(day=1)

    total_balance = Account.objects.filter(user=request.user).aggregate(
        total=Sum('balance')
    )['total'] or 0

    monthly_income = Transaction.objects.filter(
        user=request.user,
        type=Transaction.TransactionType.INCOME,
        date__gte=first_day_of_month,
    ).aggregate(total=Sum('amount'))['total'] or 0

    monthly_expense = Transaction.objects.filter(
        user=request.user,
        type=Transaction.TransactionType.EXPENSE,
        date__gte=first_day_of_month,
    ).aggregate(total=Sum('amount'))['total'] or 0

    recent_transactions = Transaction.objects.filter(
        user=request.user
    ).select_related('account', 'category').order_by('-date', '-created_at')[:5]

    context = {
        'total_balance': total_balance,
        'monthly_income': monthly_income,
        'monthly_expense': monthly_expense,
        'recent_transactions': recent_transactions,
        'account_count': Account.objects.filter(user=request.user).count(),
    }
    return render(request, 'accounts/home.html', context)


@login_required
def settings_view(request):
    profile_form = UserProfileForm(instance=request.user)
    password_form = PasswordChangeForm(user=request.user)
    for field in password_form.fields.values():
        field.widget.attrs['class'] = 'form-control'

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = UserProfileForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Профиль обновлён.')
                return redirect('settings')
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            for field in password_form.fields.values():
                field.widget.attrs['class'] = 'form-control'
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Пароль изменён.')
                return redirect('settings')

    return render(request, 'accounts/settings.html', {
        'profile_form': profile_form,
        'password_form': password_form,
    })