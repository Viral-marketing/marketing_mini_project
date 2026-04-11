# Register your models here.
from django.contrib import admin

from apps.transactions.models import Transaction

admin.site.register(Transaction)
