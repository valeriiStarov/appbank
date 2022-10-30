from rest_framework import serializers

from .models import *


class AccountSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Account
        fields = ('id', 'balance')
        read_only_fields = ('id', 'balance')


class ProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Profile
        fields = ('id', 'first_name', 'last_name', 'image')
        read_only_fields = ('id',)


class ActionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Action
        fields = ('id', 'account', 'amount', 'date')
        read_only_fields = ('id', 'date')


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = ('id', 'account', 'merchant', 'amount', 'date')
        read_only_fields = ('id', 'date', 'account')


class TransferSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transfer
        fields = ('id', 'from_account', 'to_account', 'amount', 'date')
        read_only_fields = ('id', 'date', 'from_account')

    
class DepositSerializer(serializers.ModelSerializer):

    class Meta:
        model = Deposit
        fields = ('id', 'date', 'amount', 'account')
        read_only_fields = ('id', 'date', 'account')


class CreditSerializer(serializers.ModelSerializer):

    class Meta:
        model = Credit
        fields = ('id', 'date', 'total_amount', 'amount', 'account')
        read_only_fields = ('id', 'date', 'account', 'total_amount')