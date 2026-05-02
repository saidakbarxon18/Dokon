from django.contrib import admin
from .models import Product, Sale, Debt, MyDebt, ActivityLog


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'quantity', 'sell_price', 'currency', 'date_added')
    list_filter = ('category', 'currency', 'date_added')
    search_fields = ('name', 'category')
    readonly_fields = ('date_added',)
    fieldsets = (
        ('Mahsulot Ma\'lumotlari', {'fields': ('name', 'category', 'image')}),
        ('Narxlar', {'fields': ('buy_price', 'sell_price', 'currency')}),
        ('Kirim', {'fields': ('quantity', 'date_added')}),
    )


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'quantity', 'total_price', 'profit', 'currency', 'date_sold')
    list_filter = ('currency', 'date_sold')
    search_fields = ('product__name',)
    readonly_fields = ('date_sold', 'profit')
    fieldsets = (
        ('Savdo Ma\'lumotlari', {'fields': ('product', 'quantity')}),
        ('Narx', {'fields': ('total_price', 'profit', 'currency')}),
        ('Sana', {'fields': ('date_sold',)}),
    )


@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ('customer', 'phone', 'amount', 'currency', 'due_date', 'status', 'date_added')
    list_filter = ('status', 'currency', 'due_date')
    search_fields = ('customer', 'phone')
    readonly_fields = ('date_added',)
    fieldsets = (
        ('Mijoz Ma\'lumotlari', {'fields': ('customer', 'phone')}),
        ('Qarz', {'fields': ('amount', 'currency', 'note')}),
        ('Sana', {'fields': ('due_date', 'date_added', 'status')}),
    )


@admin.register(MyDebt)
class MyDebtAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'phone', 'amount', 'currency', 'due_date', 'status', 'date_added')
    list_filter = ('status', 'currency', 'due_date')
    search_fields = ('supplier', 'phone')
    readonly_fields = ('date_added',)
    fieldsets = (
        ('Taminotchi Ma\'lumotlari', {'fields': ('supplier', 'phone')}),
        ('Qarz', {'fields': ('amount', 'currency', 'note')}),
        ('Sana', {'fields': ('due_date', 'date_added', 'status')}),
    )


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'details', 'date_time')
    list_filter = ('date_time',)
    search_fields = ('action', 'details')
    readonly_fields = ('date_time',)
    fieldsets = (
        ('Faoliyat', {'fields': ('action', 'details', 'date_time')}),
    )
