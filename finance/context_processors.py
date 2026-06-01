from django.db.models import Sum
from .models import Account


def total_balance(request):
    if request.user.is_authenticated:
        balance = Account.objects.filter(user=request.user).aggregate(
            total=Sum('balance')
        )['total'] or 0
        return {'sidebar_balance': balance}
    return {'sidebar_balance': 0}
