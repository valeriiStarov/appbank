from django.db import transaction

from .models import *


def make_interest():
    deposits = Deposit.objects.all()
    for deposit in deposits:
        pr = 0.05 / 12
        amount = float(deposit.amount)
        interest = amount * pr
        amount += interest
        deposit.amount = amount
        deposit.save()


def credit_payment():
    credits = Credit.objects.all()
    for credit in credits:
        payment = float(credit.total_amount)/10
        account = credit.account

        if credit.amount > 0:
            with transaction.atomic():

                amount = float(credit.amount) - payment
                if amount <= 0:
                    credit.account.balance = float(account.balance) - float(credit.amount)

                    credit.amount = 0
                    account.save()
                    credit.delete()
                else:
                    credit.account.balance = float(account.balance) - payment
                    account.save()
                    credit.amount = amount
                    credit.save()
