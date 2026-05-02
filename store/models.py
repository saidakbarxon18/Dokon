from django.db import models
from django.utils import timezone


class Product(models.Model):
    CURRENCY_CHOICES = [('UZS', 'So\'m'), ('USD', 'Dollar')]
    
    name = models.CharField(max_length=200, verbose_name='Mahsulot Nomi')
    category = models.CharField(max_length=100, verbose_name='Kategoriya')
    buy_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Sotib Olish Narxi')
    sell_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Sotish Narxi')
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='UZS', verbose_name='Valyuta')
    quantity = models.IntegerField(default=0, verbose_name='Miqdori')
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name='Rasm')
    date_added = models.DateField(auto_now_add=True, verbose_name='Qo\'shilgan Sana')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-date_added']
        verbose_name = 'Mahsulot'
        verbose_name_plural = 'Mahsulotlar'


class Sale(models.Model):
    CURRENCY_CHOICES = [('UZS', 'So\'m'), ('USD', 'Dollar')]
    
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Mahsulot')
    quantity = models.IntegerField(verbose_name='Miqdori')
    total_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Umumiy Narxi')
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, verbose_name='Valyuta')
    profit = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Foyda')
    date_sold = models.DateTimeField(auto_now_add=True, verbose_name='Sotilgan Sana')

    def __str__(self):
        return f"Sale {self.id} - {self.product.name}"

    class Meta:
        ordering = ['-date_sold']
        verbose_name = 'Savdo'
        verbose_name_plural = 'Savdolar'


class Debt(models.Model):
    STATUS_CHOICES = [('active', 'Faol'), ('paid', 'To\'langan'), ('deleted', 'O\'chirilgan')]
    CURRENCY_CHOICES = [('UZS', 'So\'m'), ('USD', 'Dollar')]
    
    customer = models.CharField(max_length=200, verbose_name='Mijoz Ismi')
    phone = models.CharField(max_length=20, verbose_name='Telefon')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Summa')
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='UZS', verbose_name='Valyuta')
    note = models.TextField(blank=True, verbose_name='Izoh')
    due_date = models.DateField(verbose_name='Qaytarish Sanasi')
    date_added = models.DateTimeField(auto_now_add=True, verbose_name='Qo\'shilgan Sana')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='Holati')

    def __str__(self):
        return f"{self.customer} - {self.amount}"

    class Meta:
        ordering = ['due_date']
        verbose_name = 'Mijoz Qarzi'
        verbose_name_plural = 'Mijoz Qarzlari'


class MyDebt(models.Model):
    STATUS_CHOICES = [('active', 'Faol'), ('paid', 'To\'langan'), ('deleted', 'O\'chirilgan')]
    CURRENCY_CHOICES = [('UZS', 'So\'m'), ('USD', 'Dollar')]
    
    supplier = models.CharField(max_length=200, verbose_name='Taminotchi Ismi')
    phone = models.CharField(max_length=20, verbose_name='Telefon')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Summa')
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='UZS', verbose_name='Valyuta')
    note = models.TextField(blank=True, verbose_name='Izoh')
    due_date = models.DateField(verbose_name='Qaytarish Sanasi')
    date_added = models.DateTimeField(auto_now_add=True, verbose_name='Qo\'shilgan Sana')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='Holati')

    def __str__(self):
        return f"{self.supplier} - {self.amount}"

    class Meta:
        ordering = ['due_date']
        verbose_name = 'Taminotchi Qarzi'
        verbose_name_plural = 'Taminotchi Qarzlari'


class ActivityLog(models.Model):
    action = models.CharField(max_length=255, verbose_name='Amal')
    details = models.TextField(blank=True, verbose_name='Batafsil')
    date_time = models.DateTimeField(auto_now_add=True, verbose_name='Sana va Vaqt')

    def __str__(self):
        return f"{self.action} - {self.date_time}"

    class Meta:
        ordering = ['-date_time']
        verbose_name = 'Faoliyat Logi'
        verbose_name_plural = 'Faoliyat Loglari'
