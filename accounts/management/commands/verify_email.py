from django.core.management.base import BaseCommand
from accounts.models import CustomUser


class Command(BaseCommand):
    help = 'Подтверждает email пользователя (is_email_verified = True)'

    def add_arguments(self, parser):
        parser.add_argument(
            'identifier',
            help='Имя пользователя (username) или email для подтверждения',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            dest='verify_all',
            help='Подтвердить email всем неподтверждённым пользователям',
        )

    def handle(self, *args, **options):
        if options['verify_all']:
            count = CustomUser.objects.filter(is_email_verified=False).update(is_email_verified=True)
            self.stdout.write(self.style.SUCCESS(f'Подтверждено пользователей: {count}'))
            return

        identifier = options['identifier']
        try:
            if '@' in identifier:
                user = CustomUser.objects.get(email=identifier)
            else:
                user = CustomUser.objects.get(username=identifier)
        except CustomUser.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Пользователь «{identifier}» не найден'))
            return

        if user.is_email_verified:
            self.stdout.write(self.style.WARNING(f'Email пользователя «{user.username}» уже подтверждён'))
        else:
            user.is_email_verified = True
            user.save(update_fields=['is_email_verified'])
            self.stdout.write(self.style.SUCCESS(f'Email пользователя «{user.username}» подтверждён'))
