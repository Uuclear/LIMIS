from django.contrib import admin

from .models import Consumable, ConsumableIn, ConsumableOut, Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'contact_person', 'phone',
        'evaluation_score', 'is_qualified',
    ]
    list_filter = ['is_qualified']
    search_fields = ['name', 'contact_person']


@admin.register(Consumable)
class ConsumableAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'name', 'specification', 'unit',
        'stock_quantity', 'safety_stock', 'expiry_date',
    ]
    list_filter = ['category']
    search_fields = ['code', 'name']
    raw_id_fields = ['supplier']


@admin.register(ConsumableIn)
class ConsumableInAdmin(admin.ModelAdmin):
    list_display = [
        'consumable', 'quantity', 'batch_no',
        'purchase_date', 'operator',
    ]
    raw_id_fields = ['consumable', 'operator']


@admin.register(ConsumableOut)
class ConsumableOutAdmin(admin.ModelAdmin):
    list_display = [
        'consumable', 'quantity', 'purpose',
        'recipient', 'out_date',
    ]
    raw_id_fields = ['consumable', 'recipient']
