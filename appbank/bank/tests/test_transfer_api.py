from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from bank.models import Transfer, Account
from bank.views import TransferViewSet

TRANSFER_URL = reverse('bank:transfer-list')


class PublicBankApiTest(TestCase):
    """Test unauthenticated recipe API request"""

    def setUp(self):
        self.client = APIClient()

    def test_account_auth_required(self):
        res = self.client.get(TRANSFER_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateBankApiTest(TestCase):
    def setUp(self) -> None:
        TransferViewSet.pagination_class = None

        self.user = get_user_model().objects.create_user(
            username='test',
            password='ghbrjkmxbr',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.account = Account.objects.get(user=self.user)
        self.account.balance = 1000
        self.account.save()

        self.user2 = get_user_model().objects.create_user(
            username = 'test2',
            password = 'ghbrjkmxbr2'
        )
        self.account2 = Account.objects.get(user=self.user2)
        self.account2.balance = 1000
        self.account2.save()

    def test_create_transaction(self):
        payload = {
            'to_account': self.account2.id,
            'amount': 100
        }
        res = self.client.post(TRANSFER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_list_transfer_for_request_user(self):

        Transfer.objects.create(from_account=self.account, to_account=self.account2, amount=100)
        Transfer.objects.create(from_account=self.account2, to_account=self.account, amount=200)
        res = self.client.get(TRANSFER_URL)
        self.assertEqual(len(res.data), 1)

    def test_make_transfer(self):
        payload = {
            'to_account': self.account2.id,
            'amount': 100
        }
        balance_before_account = self.account.balance
        balance_before_account2 = self.account2.balance

        res = self.client.post(TRANSFER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.account.refresh_from_db()
        self.account2.refresh_from_db()

        balance_after_account = self.account.balance
        balance_after_account2 = self.account2.balance

        self.assertEqual(payload['amount'], balance_before_account - balance_after_account)
        self.assertEqual(payload['amount'], balance_after_account2 - balance_before_account2)

    def test_make_transfer_with_negative_amount(self):
        payload = {
            'to_account': self.account2.id,
            'amount': -100
        }

        res = self.client.post(TRANSFER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_make_transfer_with_not_enough_money(self):
        payload = {
            'to_account': self.account2.id,
            'amount': 100
        }
        self.account.balance = 0
        self.account.save()

        res = self.client.post(TRANSFER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_make_transfer_on_own_account(self):
        payload = {
            'to_account': self.account.id,
            'amount': 100
        }
        res = self.client.post(TRANSFER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    