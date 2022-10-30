from celery import shared_task
from bank.services import make_interest, credit_payment


@shared_task
def call_make_interest():
    make_interest()

@shared_task
def call_credit_payment():
    credit_payment()