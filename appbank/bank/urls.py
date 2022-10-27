from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import *

app_name='bank'

router = DefaultRouter()
router.register(r'account', AccountViewSet, basename='account')
router.register(r'profile', ProfileViewSet)
router.register(r'action', ActionViewSet)
router.register(r'transaction', TransactionViewSet)
router.register(r'transfer', TransferViewSet)
router.register(r'deposit', DepositViewSet)
urlpatterns = [
    path('', include(router.urls)),
]