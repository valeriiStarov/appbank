from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from bank.models import Transaction, Account
from bank.views import TransactionViewSet

TRANSACTION_URL = reverse('bank:transaction-list')


class PublicBankApiTest(TestCase):
    """Test unauthenticated recipe API request"""

    def setUp(self):
        self.client = APIClient()

    def test_account_auth_required(self):
        res = self.client.get(TRANSACTION_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateBankApiTest(TestCase):
    def setUp(self) -> None:
        TransactionViewSet.pagination_class = None

        self.user = get_user_model().objects.create_user(
            username='test',
            password='ghbrjkmxbr',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.account = Account.objects.get(user=self.user)
        self.account.balance = 1000
        self.account.save()

    def test_create_transaction(self):
        payload = {
            'merchant': 'KFC',
            'amount': 100
        }
        res = self.client.post(TRANSACTION_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_list_transactions_for_request_user(self):
        user2 = get_user_model().objects.create_user(
            username = 'test2',
            password = 'ghbrjkmxbr2'
        )
        account2 = Account.objects.get(user=user2)
        Transaction.objects.create(account=self.account, merchant='kfc', amount=100)
        Transaction.objects.create(account=account2, merchant='kfc', amount=200)
        res = self.client.get(TRANSACTION_URL)
        self.assertEqual(len(res.data), 1)

    def test_make_transaction(self):
        payload = {
            'merchant': 'KFC',
            'amount': 100
        }
        balance_before = self.account.balance
        res = self.client.post(TRANSACTION_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.account.refresh_from_db()
        balance_after = self.account.balance

        self.assertEqual(payload['amount'], balance_before - balance_after)

    def test_make_transaction_with_negative_amount(self):
        payload = {
            'merchant': 'KFC',
            'amount': -100
        }
        res = self.client.post(TRANSACTION_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_make_transaction_with_not_enough_money(self):
        payload = {
            'merchant': 'KFC',
            'amount': 100
        }
        self.account.balance = 0
        self.account.save()

        res = self.client.post(TRANSACTION_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        

