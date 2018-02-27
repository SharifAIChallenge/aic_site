from django.contrib import admin

from .models import Transaction


class TransactionAdmin(admin.ModelAdmin):
    readonly_fields = ['team', 'amount', 'status', 'order_id', 'reference_id', 'created', 'updated']
    list_display = ['team', 'amount', 'status', 'reference_id', 'updated']

admin.site.register(Transaction, TransactionAdmin)