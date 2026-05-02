from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Sum, Q
from .models import Product, Sale, Debt, MyDebt, ActivityLog
from datetime import datetime, timedelta
import json

ADMIN_LOGIN = "BEK SANTEXNIKA"
ADMIN_PAROL = "BEK1987"


def login_view(request):
    """Login sahifasi"""
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        
        if username == ADMIN_LOGIN and password == ADMIN_PAROL:
            request.session['logged_in'] = True
            request.session['username'] = username.upper()
            request.session.set_expiry(12 * 60 * 60)
            ActivityLog.objects.create(action=f"Login: {username}")
            return redirect('store:dashboard')
        else:
            error = "❌ Login yoki Parol xato!"
    
    return render(request, 'store/login.html', {'error': error})


def logout_view(request):
    """Logout"""
    username = request.session.get('username', 'Unknown')
    ActivityLog.objects.create(action=f"Logout: {username}")
    request.session.clear()
    return redirect('store:login')


def check_login(view_func):
    """Login tekshirish decorator"""
    def wrapper(request, *args, **kwargs):
        if not request.session.get('logged_in'):
            return redirect('store:login')
        return view_func(request, *args, **kwargs)
    return wrapper


@check_login
def dashboard(request):
    """Bosh sahifa - Statistika va Grafiklar"""
    # Sotish statistikasi
    sales_uzs = Sale.objects.filter(currency='UZS').aggregate(Sum('total_price'))['total_price__sum'] or 0
    sales_usd = Sale.objects.filter(currency='USD').aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    # Foyda statistikasi
    profit_uzs = Sale.objects.filter(currency='UZS').aggregate(Sum('profit'))['profit__sum'] or 0
    profit_usd = Sale.objects.filter(currency='USD').aggregate(Sum('profit'))['profit__sum'] or 0
    
    # Qarz statistikasi
    debts_uzs = Debt.objects.filter(status='active', currency='UZS').aggregate(Sum('amount'))['amount__sum'] or 0
    debts_usd = Debt.objects.filter(status='active', currency='USD').aggregate(Sum('amount'))['amount__sum'] or 0
    
    my_debts_uzs = MyDebt.objects.filter(status='active', currency='UZS').aggregate(Sum('amount'))['amount__sum'] or 0
    my_debts_usd = MyDebt.objects.filter(status='active', currency='USD').aggregate(Sum('amount'))['amount__sum'] or 0
    
    products_count = Product.objects.count()
    low_stock = Product.objects.filter(quantity__lt=10).count()
    
    recent_sales = Sale.objects.select_related('product').order_by('-date_sold')[:10]
    recent_activities = ActivityLog.objects.all().order_by('-date_time')[:5]
    
    context = {
        'sales_uzs': int(sales_uzs),
        'sales_usd': int(sales_usd),
        'profit_uzs': int(profit_uzs),
        'profit_usd': int(profit_usd),
        'debts_uzs': int(debts_uzs),
        'debts_usd': int(debts_usd),
        'my_debts_uzs': int(my_debts_uzs),
        'my_debts_usd': int(my_debts_usd),
        'products_count': products_count,
        'low_stock': low_stock,
        'recent_sales': recent_sales,
        'recent_activities': recent_activities,
    }
    
    return render(request, 'store/dashboard.html', context)


@check_login
def inventory(request):
    """Inventar boshqaruvi"""
    if request.method == 'POST':
        if 'add_stock' in request.POST:
            product_id = request.POST.get('id')
            added_qty = int(request.POST.get('added_qty', 0))
            product = Product.objects.get(id=product_id)
            old_qty = product.quantity
            product.quantity += added_qty
            product.save()
            ActivityLog.objects.create(
                action=f"Kirim: {product.name}",
                details=f"{old_qty} → {product.quantity} (qo'shildi: +{added_qty})"
            )
            return redirect('store:inventory')
        
        elif 'delete_product' in request.POST:
            product_id = request.POST.get('id')
            product = Product.objects.get(id=product_id)
            product_name = product.name
            product.delete()
            ActivityLog.objects.create(action=f"Mahsulot o'chirildi: {product_name}")
            return redirect('store:inventory')
        
        elif 'update_price' in request.POST:
            product_id = request.POST.get('id')
            sell_price = request.POST.get('sell_price')
            product = Product.objects.get(id=product_id)
            old_price = product.sell_price
            product.sell_price = sell_price
            product.save()
            ActivityLog.objects.create(
                action=f"Narx o'zgartirildi: {product.name}",
                details=f"{old_price} → {sell_price}"
            )
            return redirect('store:inventory')
        
        else:
            Product.objects.create(
                name=request.POST.get('name', 'Unnamed'),
                category=request.POST.get('category', 'Other'),
                buy_price=request.POST.get('buy_price', 0),
                sell_price=request.POST.get('sell_price', 0),
                currency=request.POST.get('currency', 'UZS'),
                quantity=request.POST.get('quantity', 0),
                image=request.FILES.get('image')
            )
            ActivityLog.objects.create(
                action=f"Yangi mahsulot qo'shildi: {request.POST.get('name')}"
            )
            return redirect('store:inventory')
    
    products = Product.objects.all().order_by('-date_added')
    return render(request, 'store/inventory.html', {'products': products})


@check_login
def pos(request):
    """POS Savdo Sistemasi"""
    products = Product.objects.filter(quantity__gt=0)
    return render(request, 'store/pos.html', {'products': products})


@check_login
def sell_api(request):
    """API: Savdo qilish"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart = data.get('cart', [])
            
            if not cart:
                return JsonResponse({'success': False, 'message': 'Savat bo\'sh!'})
            
            total_profit = 0
            for item in cart:
                product = Product.objects.get(id=item['id'])
                if product.quantity < item['qty']:
                    return JsonResponse({
                        'success': False,
                        'message': f"'{product.name}' yetarli emas! Mavjud: {product.quantity}"
                    })
                
                qty = item['qty']
                total = product.sell_price * qty
                profit = (product.sell_price - product.buy_price) * qty
                
                Sale.objects.create(
                    product=product,
                    quantity=qty,
                    total_price=total,
                    currency=product.currency,
                    profit=profit
                )
                
                product.quantity -= qty
                product.save()
                total_profit += profit
            
            ActivityLog.objects.create(
                action="Savdo yakunlandi",
                details=f"{len(cart)} mahsulot sotildi, Foyda: {total_profit}"
            )
            
            return JsonResponse({
                'success': True,
                'message': f'✅ {len(cart)} mahsulot sotildi!',
                'profit': float(total_profit)
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Xato: {str(e)}'
            })


@check_login
def debts(request):
    """Mijozlar Qarzlari"""
    if request.method == 'POST':
        if 'pay' in request.POST:
            debt_id = request.POST.get('id')
            debt = Debt.objects.get(id=debt_id)
            debt.status = 'paid'
            debt.save()
            ActivityLog.objects.create(
                action=f"Qarz to'landi",
                details=f"{debt.customer} - {debt.amount} {debt.currency}"
            )
        
        elif 'delete' in request.POST:
            debt_id = request.POST.get('id')
            debt = Debt.objects.get(id=debt_id)
            debt.status = 'deleted'
            debt.save()
            ActivityLog.objects.create(
                action=f"Qarz o'chirildi",
                details=f"{debt.customer} - {debt.amount} {debt.currency}"
            )
        
        else:
            Debt.objects.create(
                customer=request.POST.get('customer', 'Unknown'),
                phone=request.POST.get('phone', ''),
                amount=request.POST.get('amount', 0),
                currency=request.POST.get('currency', 'UZS'),
                note=request.POST.get('note', ''),
                due_date=request.POST.get('date', '2026-06-02')
            )
            ActivityLog.objects.create(
                action=f"Nasiya qo'shildi",
                details=f"{request.POST.get('customer')} - {request.POST.get('amount')} {request.POST.get('currency')}"
            )
        
        return redirect('store:debts')
    
    debts = Debt.objects.filter(status='active').order_by('due_date')
    return render(request, 'store/debts.html', {'debts': debts})


@check_login
def my_debts(request):
    """Taminotchi Qarzlari"""
    if request.method == 'POST':
        if 'pay' in request.POST:
            debt_id = request.POST.get('id')
            debt = MyDebt.objects.get(id=debt_id)
            debt.status = 'paid'
            debt.save()
            ActivityLog.objects.create(
                action=f"Taminotchi qarzi to'landi",
                details=f"{debt.supplier} - {debt.amount} {debt.currency}"
            )
        
        elif 'delete' in request.POST:
            debt_id = request.POST.get('id')
            debt = MyDebt.objects.get(id=debt_id)
            debt.status = 'deleted'
            debt.save()
            ActivityLog.objects.create(
                action=f"Taminotchi qarzi o'chirildi",
                details=f"{debt.supplier} - {debt.amount} {debt.currency}"
            )
        
        else:
            MyDebt.objects.create(
                supplier=request.POST.get('supplier', 'Unknown'),
                phone=request.POST.get('phone', ''),
                amount=request.POST.get('amount', 0),
                currency=request.POST.get('currency', 'UZS'),
                note=request.POST.get('note', ''),
                due_date=request.POST.get('date', '2026-06-02')
            )
            ActivityLog.objects.create(
                action=f"Taminotchi qarzi qo'shildi",
                details=f"{request.POST.get('supplier')} - {request.POST.get('amount')} {request.POST.get('currency')}"
            )
        
        return redirect('store:my_debts')
    
    my_debts = MyDebt.objects.filter(status='active').order_by('due_date')
    return render(request, 'store/my_debts.html', {'my_debts': my_debts})


@check_login
def archive(request):
    """Arxiv va Faoliyat Tarix"""
    if request.method == 'POST':
        if 'restore_customer' in request.POST:
            debt_id = request.POST.get('id')
            debt = Debt.objects.get(id=debt_id)
            debt.status = 'active'
            debt.save()
            ActivityLog.objects.create(
                action=f"Mijoz qarzi tiklandi",
                details=f"{debt.customer} - {debt.amount}"
            )
        
        elif 'restore_supplier' in request.POST:
            debt_id = request.POST.get('id')
            debt = MyDebt.objects.get(id=debt_id)
            debt.status = 'active'
            debt.save()
            ActivityLog.objects.create(
                action=f"Taminotchi qarzi tiklandi",
                details=f"{debt.supplier} - {debt.amount}"
            )
        
        return redirect('store:archive')
    
    logs = ActivityLog.objects.all().order_by('-date_time')[:200]
    archived_debts_customer = Debt.objects.filter(status__in=['paid', 'deleted'])
    archived_debts_supplier = MyDebt.objects.filter(status__in=['paid', 'deleted'])
    
    context = {
        'logs': logs,
        'archived_debts_customer': archived_debts_customer,
        'archived_debts_supplier': archived_debts_supplier,
    }
    
    return render(request, 'store/archive.html', context)
