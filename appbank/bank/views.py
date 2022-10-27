
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from .serializers import *
from .models import *


class AccountViewSet(viewsets.GenericViewSet,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin):
    serializer_class = AccountSerializer
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        """User gets only his account"""
        if self.action == 'retrieve':
            return Account.objects.filter(user=self.request.user)
        else:
            return Account.objects.all()

    def get_permissions(self):
        """Admin can get list accounts, but not specific user"""
        if self.action == 'list':
            permission_classes = (IsAdminUser,)
        else:
            permission_classes = (IsAuthenticated,)

        return (permission() for permission in permission_classes)


class ProfileViewSet(
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        """User gets only his account"""
        if self.action == 'retrieve':
            return self.queryset.filter(user=self.request.user)
        else:
            return self.queryset

    def get_permissions(self):
        """Admin can get list accounts, but not specific user"""
        if self.action == 'list':
            permission_classes = (IsAdminUser,)
        else:
            permission_classes = (IsAuthenticated,)

        return (permission() for permission in permission_classes)


class ActionViewSetPagination(PageNumberPagination):
    page_size = 3


class ActionViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = Action.objects.all().order_by('-id')
    serializer_class = ActionSerializer
    permission_classes = (IsAdminUser,)
    authentication_classes = (TokenAuthentication,)
    pagination_class = ActionViewSetPagination

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            Action.make_action(**serializer.validated_data)
        except Exception as e:
            content = {"error": str(e)}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data, 
            status=status.HTTP_201_CREATED, 
            headers=headers)


class TransactionViewSetPagination(PageNumberPagination):
    page_size = 3           


class TransactionViewSet(mixins.CreateModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    pagination_class = TransactionViewSetPagination

    def get_queryset(self):
        return self.queryset.filter(account=Account.objects.get(user=self.request.user)).order_by('-id')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            Transaction.make_transaction(**serializer.validated_data, account=Account.objects.get(user=self.request.user))  
        except Exception as e:
            content = {"error": str(e)}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data, 
            status=status.HTTP_201_CREATED, 
            headers=headers)


class TransferViewSetPagination(PageNumberPagination):
    page_size = 3           


class TransferViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    queryset = Transfer.objects.all()
    serializer_class = TransferSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    pagination_class = TransferViewSetPagination

    def get_queryset(self):
        return self.queryset.filter(from_account=Account.objects.get(user=self.request.user)).order_by('-id')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            Account.objects.get(pk=self.request.data['to_account'])
        except Exception as e:
            content = {'error': 'No such account'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        try:
            Transfer.make_transfer(**serializer.validated_data, from_account=Account.objects.get(user=self.request.user))  
        except Exception as e:
            content = {"error": str(e)}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data, 
            status=status.HTTP_201_CREATED, 
            headers=headers)


class DepositViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    queryset = Deposit.objects.all()
    serializer_class = DepositSerializer
    permission_classes = (IsAuthenticated, )
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        return self.queryset.filter(account=Account.objects.get(user=self.request.user)).order_by('-id')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            Deposit.make_deposit(**serializer.validated_data, account=Account.objects.get(user=self.request.user))
        except Exception as e:
            content = {"error": str(e)}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        """Making withdraw from deposit"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            Deposit.update_deposit(instance=instance, **serializer.validated_data, account=Account.objects.get(user=self.request.user))
        except Exception as e:
            content = {"error": str(e)}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        
        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
            headers=headers
        )

    def destroy(self, request, *args, **kwargs):
        """Destroy deposit and transfer of balance to account"""
        instance = self.get_object()
        account = Account.objects.get(user=self.request.user)

        if instance.amount > 0:
            account.balance += instance.amount
            account.save()
        
        self.perform_destroy(instance)
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )