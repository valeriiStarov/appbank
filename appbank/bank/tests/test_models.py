from django.test import TestCase
from django.contrib.auth import get_user_model

from bank.models import *


def sample_user(username='test', password='ghbrjkmxbr'):
    """Create a sample account"""

    return get_user_model().objects.create_user(username, password)


class ModelTest(TestCase):

    def test_account_str(self):
        """Test the account string representation"""

        user = sample_user()
        account = Account.objects.get(user=user)

        self.assertEqual(str(account), f'{user.username} id - {user.id}')

    def test_signal_create_account(self):
        user = sample_user()
        self.assertTrue(Account.objects.get(user=user))
        
    def test_profile_str(self):
        """Test the profile string representation"""

        user = sample_user()
        profile = Profile.objects.get(user=user)

        self.assertEqual(str(profile), f'{user.username} id - {user.id}')

    def test_signal_create_profile(self):
        user = sample_user()
        self.assertTrue(Profile.objects.get(user=user))

    def test_action_str(self):
        """Test the action string representation"""

        user = sample_user()
        account = Account.objects.get(user=user)
        action = Action.objects.create(account=account, amount=100)

        self.assertEqual(str(action), f'[{action.pk}] Account id {account.pk} was changed on {str(action.amount)}')

    def test_transaction_str(self):
        """Test the transaction string representation"""

        user = sample_user()
        account = Account.objects.get(user=user)
        transaction = Transaction.objects.create(account=account, amount=100, merchant='kfc')

        self.assertEqual(str(transaction), f'[{transaction.pk}] Account number {account.pk} sent {str(transaction.amount)} to {transaction.merchant}')

    def test_transfer_str(self):
        """Test the transfer string representation"""

        user = sample_user()
        user2 = sample_user(username='test2')

        account = Account.objects.get(user=user)
        account2 = Account.objects.get(user=user2)

        transfer = Transfer.objects.create(from_account=account,to_account=account2, amount=100)

        self.assertEqual(str(transfer), f'[{transfer.pk}] Account number {transfer.from_account.pk} sent {str(transfer.amount)} to {transfer.to_account.pk}')
    

    