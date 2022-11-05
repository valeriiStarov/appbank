from django.contrib import admin

from .models import *

admin.site.register(Account)
admin.site.register(Profile)
admin.site.register(Action)
admin.site.register(Transaction)
admin.site.register(Transfer)
admin.site.register(Deposit)
admin.site.register(Credit)
