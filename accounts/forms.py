from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

    def clean_username(self):
        username = self.cleaned_data['username']
        if CustomUser.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('Пользователь с таким именем уже существует.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже зарегистрирован.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].lower()
        user.username = self.cleaned_data['username'].lower()
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number']
        labels = {
            'username': 'Имя пользователя',
            'email': 'Email',
            'phone_number': 'Номер телефона',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = user.email.lower()
        if commit:
            user.save()
        return user


class ConsolePasswordResetForm(PasswordResetForm):
    def save(self, *args, **kwargs):
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode
        from django.urls import reverse
        for user in self.get_users(self.cleaned_data['email']):
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            # Печатаем ссылку напрямую (для разработки без SMTP)
            print(f'\n{"="*60}')
            print(f'[MoneyFlow] Сброс пароля для {user.email}')
            print(f'Ссылка сброса (скопируйте и откройте в браузере):')
            print(f'  http://127.0.0.1:8000/accounts/reset/{uid}/{token}/')
            print(f'{"="*60}\n', flush=True)
        return super().save(*args, **kwargs)