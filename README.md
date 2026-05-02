# 🏪 Dokon - Django 5.0 Do'kon Boshqaruv Sistemasi

**Flask'dan Django 5.0'ga to'liq konvertatsiya!** ✨

## 📋 Haqida

**Dokon** - kichik va o'rta bizneslar uchun to'liq do'kon boshqaruv tizimi. Inventar, savdo, qarzlarni boshqarish va statistika bir joyda!

### ✨ Asosiy Xususiyatlar:

- 📊 **Dashboard** - Statistika va Grafiklar
- 📦 **Inventar Boshqaruvi** - Mahsulotlar, Kategoriyalar
- 💳 **POS Sistema** - Tezkor Savdo
- 💰 **Qarz Boshqaruvi** - Mijozlar va Taminotchilar
- 📈 **Tarix va Logi** - Barcha amallar yoziladi
- 🔐 **Login Sistema** - Xavfsiz kirishlar
- 🎨 **Bootstrap 5** - Zamonaviy interfeys

---

## 🚀 Tez Ishga Tushirish

### Talablar:
- Python 3.9+
- pip (paket menejeri)

### 1️⃣ O'rnatish:

```bash
# Virtual environment yaratish
python -m venv venv

# Virtual environment'ni aktivlashtirish
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Dependencies o'rnatish
pip install -r requirements.txt
```

### 2️⃣ Database Tayyorlash:

```bash
# Migration'larni qo'llash
python manage.py migrate

# Superuser (admin) yaratish
python manage.py createsuperuser
```

### 3️⃣ Server Ishga Tushirish:

```bash
python manage.py runserver
```

**Brauzerda oching:** `http://127.0.0.1:8000`

---

## 🔐 Login Ma'lumotlari:

**Default Login:**
- **Login:** `BEK SANTEXNIKA`
- **Parol:** `BEK1987`

**Django Admin:**
- URL: `http://127.0.0.1:8000/admin/`
- Superuser bilan kiring (createsuperuser orqali yaratilgan)

---

## 📁 Loyihaning Strukturasi:

```
Dokon/
├── config/                 # Django settings
│   ├── settings.py        # Asosiy sozlamalar
│   ├── urls.py            # URL yo'naltirlari
│   ├── wsgi.py            # Production WSGI
│   └── asgi.py            # Async support
├── store/                 # Asosiy App
│   ├── models.py          # Database modellari
│   ├── views.py           # View functions
│   ├── urls.py            # App URL'lari
│   ├── admin.py           # Admin panel
│   └── apps.py            # App konfiguratsiyasi
├── templates/store/       # HTML fayllar
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── inventory.html
│   ├── pos.html
│   ├── debts.html
│   ├── my_debts.html
│   └── archive.html
├── static/                # CSS, JS, Images
├── media/                 # Uploaded files
├── db.sqlite3            # SQLite database
├── manage.py             # Django management
└── requirements.txt      # Dependencies
```

---

## 🗄️ Database Modellari:

### 📦 **Product** (Mahsulot)
- Nomi, Kategoriya
- Sotib olish va sotish narxi
- Miqdori, Rasm
- Valyuta (UZS/USD)

### 💳 **Sale** (Savdo)
- Mahsulot, Miqdori
- Umumiy narx, Foyda
- Sotilgan sana

### 💰 **Debt** (Mijoz Qarzi)
- Mijoz ismi, Telefon
- Summa, Qaytarish sanasi
- Holati (Faol/To'langan/O'chirilgan)

### 🏭 **MyDebt** (Taminotchi Qarzi)
- Taminotchi ismi, Telefon
- Summa, Qaytarish sanasi
- Holati (Faol/To'langan/O'chirilgan)

### 📝 **ActivityLog** (Faoliyat Tarix)
- Amal, Batafsil
- Sana va vaqt

---

## 🛠️ Django Commands:

```bash
# Server ishga tushirish
python manage.py runserver

# Migration'larni yaratish
python manage.py makemigrations

# Migration'larni qo'llash
python manage.py migrate

# Admin foydalanuvchi yaratish
python manage.py createsuperuser

# Shell'ni ochish
python manage.py shell

# Static fayllarni to'plash (Production uchun)
python manage.py collectstatic
```

---

## 🌐 Production'ga Deployment:

### Gunicorn bilan:

```bash
# Gunicorn o'rnatish
pip install gunicorn

# Server ishga tushirish
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Nginx konfiguratsiyasi:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/Dokon/staticfiles/;
    }

    location /media/ {
        alias /path/to/Dokon/media/;
    }
}
```

---

## 📊 Statistika:

**Dashboard'da ko'rsatiladi:**
- 📈 Umumiy Sotish (UZS/USD)
- 💹 Umumiy Foyda
- 💳 Faol Qarzlar
- 📦 Mahsulotlar Soni
- ⚠️ Kam Miqdordagi Mahsulotlar
- 📝 So'nggi Savdolar
- 🕐 So'nggi Amallar

---

## 🔒 Security:

- ✅ Django built-in security middleware
- ✅ CSRF protection
- ✅ XSS protection
- ✅ SQL injection protection (ORM)
- ✅ Session-based authentication
- ✅ Password hashing

---

## 📞 Muammolar va Surotlar:

Agar qandaydir muammo bo'lsa:

1. **Terminal'da error ko'rsatilishi**
   - Errorni o'qib chiqing
   - Google'da qidiring
   - Stack Overflow'da yozing

2. **Database muammolari**
   ```bash
   python manage.py migrate --run-syncdb
   ```

3. **Static files muammolari**
   ```bash
   python manage.py collectstatic --clear --no-input
   ```

---

## 📚 O'quv Manbalari:

- [Django Official Documentation](https://docs.djangoproject.com/)
- [Django for Beginners](https://djangoforbeginners.com/)
- [Real Python Django](https://realpython.com/django/)

---

## 📄 Litsenziya:

MIT License - Ishlating va tahrir qilib taqsimlang!

---

**✨ Django 5.0 bilan yaratilgan!** 🚀
