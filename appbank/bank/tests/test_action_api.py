
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from bank.models import Action, Account
from bank.views import ActionViewSet
from bank.serializers import ActionSerializer

ACTION_URL = reverse('bank:action-list')

class PublicBankApiTest(TestCase):
    """Test unauthenticated recipe API request"""

    def setUp(self):
        self.client = APIClient()

    def test_account_auth_required(self):
        res = self.client.get(ACTION_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AdminActionApiTests(TestCase):
    """Test Admin API access"""

    def setUp(self):
        ActionViewSet.pagination_class = None

        self.user = get_user_model().objects.create_user(
            username='test',
            password='ghbrjkmxbr',
            is_staff=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.account = Account.objects.get(user=self.user)
        self.account.balance = 1000
        self.account.save()

    def test_create_action(self):
        payload = {
            'account': self.account.id,
            'amount': 100.00
        }
        res = self.client.post(ACTION_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_list_actions(self):

        Action.objects.create(account = self.account, amount = 1000)
        Action.objects.create(account = self.account, amount = 100)

        actions = Action.objects.all().order_by('-id')

        res = self.client.get(ACTION_URL)
        serializer = ActionSerializer(actions, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_make_deposit(self):
        payload = {
            'account': self.account.id,
            'amount': 100.00
        }
        balance_before = self.account.balance

        res = self.client.post(ACTION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.account.refresh_from_db()

        balance_after = self.account.balance

        self.assertEqual(payload['amount'], balance_after - balance_before)
        self.assertEqual(payload['account'], res.data['account'])

        #hardcode
        self.assertEqual(f"{payload['amount']:.2f}", res.data['amount'])

    def test_make_withdraw(self):
        payload = {
            'account': self.account.id,
            'amount': -100.00
        }
        balance_before = self.account.balance

        res = self.client.post(ACTION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.account.refresh_from_db()

        balance_after = self.account.balance

        self.assertEqual(payload['amount'], balance_after - balance_before)
        self.assertEqual(payload['account'], res.data['account'])
        
        #hardcode
        self.assertEqual(f"{payload['amount']:.2f}", res.data['amount'])

    def test_make_withdraw_with_not_enough_money(self):
        payload = {'account': self.account.id,
                   'amount': -100}

        self.account.balance = 0
        self.account.save()

        res = self.client.post(ACTION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        