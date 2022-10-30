from django.db import models, transaction
from django.conf import settings
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class Account(models.Model):
    balance = models.DecimalField(
        default=0,
        max_digits=12,
        decimal_places=2
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return f'{self.user.username} id - {self.id}'

@receiver(post_save, sender=User)
def create_user_account(sender, instance, created, **kwargs):
    """Create account after registration"""
    if created:
        Account.objects.create(user=instance)

class Profile(models.Model):
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to = 'photos/%Y/%m/%d', null=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.user.username} id - {self.id}'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create profile after registration"""
    if created:
        Profile.objects.create(user=instance)


class Action(models.Model):
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'[{self.pk}] Account id {self.account.pk} ' +\
            f'was changed on {str(self.amount)}'

    @classmethod
    def make_action(cls, amount, account):
        """Making action logic"""
        if account.balance + amount < 0:
            raise(ValueError('Not enough money'))

        account.balance += amount
        account.save()
        action = cls.objects.create(amount=amount, account=account)

        return account, action


class Transaction(models.Model):
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    merchant = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f'[{self.pk}] Account number {self.account.pk} ' +\
            f'sent {str(self.amount)} to {self.merchant}'

    @classmethod
    def make_transaction(cls, amount, account, merchant):
        """Making transaction logic"""
        if amount < 0:
            raise(ValueError("Amount can't be negative"))

        if account.balance < amount:
            raise(ValueError("Not enough money"))

        account.balance -= amount
        account.save()
        tran = cls.objects.create(amount=amount, account=account, merchant=merchant)

        return tran

class Transfer(models.Model):
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    from_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='from_account')
    to_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='to_account')

    def __str__(self) -> str:
        return f'[{self.pk}] Account number {self.from_account.pk} ' +\
            f'sent {str(self.amount)} to {self.to_account.pk}'

    
    @classmethod
    def make_transfer(cls, amount, from_account, to_account):
        """Making transfer logic"""
        if amount < 0:
            raise(ValueError("Amount can't be negative"))

        if from_account == to_account:
            raise(ValueError('Chose another account'))

        if from_account.balance < amount:
            raise(ValueError("Not enough money"))

        with transaction.atomic():
            from_account.balance -= amount
            to_account.balance += amount
            from_account.save()
            to_account.save()
            transf = cls.objects.create(amount=amount, from_account=from_account, to_account=to_account)

        return transf


class Deposit(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'[{self.pk}] Account number {self.account.pk} put {str(self.amount)} on a deposit'

    @classmethod
    def make_deposit(cls, amount, account):
        """Making deposit logic"""
        if amount < 0:
            raise(ValueError("Amount can't be negative"))
        if amount > account.balance:
            raise(ValueError("Not enough money"))
        
        with transaction.atomic():
            account.balance -= amount
            account.save()
            dep = cls.objects.create(amount=amount, account=account)

        return dep

    @staticmethod
    def update_deposit(instance, amount, account):
        """Making withdraw from deposit logic"""
        if amount < 0:
            raise(ValueError("Amount can't be negative"))
        if amount > instance.amount:
            raise(ValueError("Not enough money"))

        with transaction.atomic():
            account.balance += amount
            instance.amount -= amount

            account.save()
            instance.save()


class Credit(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'[{self.pk}] Account number {self.account.pk} borrow {str(self.amount)}'

    @classmethod
    def make_credit(cls, amount, account):
        """Making credit logic"""
        if amount < 0:
            raise(ValueError("Amount can't be negative"))
        if amount > account.balance * 100:
            raise(ValueError("Reduce your credit amount"))
        
        credit_amount = amount + amount/10

        with transaction.atomic():
            account.balance += amount
            account.save()
            cre = cls.objects.create(amount=credit_amount,total_amount=credit_amount, account=account)

        return cre

    @staticmethod
    def update_credit(instance, amount, account):
        """Partial repayment of a credit"""
        if amount < 0:
            raise(ValueError("Amount can't be negative"))
        if amount > instance.amount:
            raise(ValueError("The amount entered is greater than the credit amount"))

        with transaction.atomic():
            account.balance -= amount
            instance.amount -= amount

            account.save()
            instance.save()

    
