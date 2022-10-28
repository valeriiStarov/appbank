from django.db import transaction

from .models import *


def make_interest():
    deposits = Deposit.objects.all()
    for deposit in deposits:
        with transaction.atomic():
            pr = 0.05 / 12
            amount = float(deposit.amount)
            interest = amount * pr
            amount += interest
            print('1', amount)
            deposit.amount = amount
            deposit.save()