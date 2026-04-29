from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import sqlite3
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from functools import wraps
from PIL import Image
from waitress import serve
import socket

try:
    from flask_compress import Compress
except ImportError:
    Compress = None

app = Flask(__name__)
app.secret_key = 'super_maxfiy_kalit_777'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=12)

if Compress: Compress(app)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# --- SOZLAMALAR ---
ADMIN_LOGIN = "BEK SANTEXNIKA"  # <-- LOGIN
ADMIN_PAROL = "BEK1987"         # <-- PAROL


# --- BAZA ---
def get_db():
    conn = sqlite3.connect('database.db', timeout=30)
    try:
        conn.execute('PRAGMA journal_mode=WAL;')
        conn.execute('PRAGMA synchronous=NORMAL;')
    except:
        pass
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    # 1. Mahsulotlar
    conn.execute('''CREATE TABLE IF NOT EXISTS products
                    (
                        id
                        INTEGER
                        PRIMARY
                        KEY
                        AUTOINCREMENT,
                        name
                        TEXT,
                        category
                        TEXT,
                        buy_price
                        REAL,
                        sell_price
                        REAL,
                        currency
                        TEXT
                        DEFAULT
                        'UZS',
                        quantity
                        INTEGER,
                        image
                        TEXT,
                        date_added
                        TEXT
                    )''')
    # 2. Savdolar
    conn.execute('''CREATE TABLE IF NOT EXISTS sales
                    (
                        id
                        INTEGER
                        PRIMARY
                        KEY
                        AUTOINCREMENT,
                        product_id
                        INTEGER,
                        quantity
                        INTEGER,
                        total_price
                        REAL,
                        currency
                        TEXT,
                        profit
                        REAL,
                        date_sold
                        TEXT
                    )''')
    # 3. Mijozlar qarzi (Nasiya)
    conn.execute('''CREATE TABLE IF NOT EXISTS debts
                    (
                        id
                        INTEGER
                        PRIMARY
                        KEY
                        AUTOINCREMENT,
                        customer
                        TEXT,
                        phone
                        TEXT,
                        amount
                        REAL,
                        currency
                        TEXT
                        DEFAULT
                        'UZS',
                        note
                        TEXT,
                        due_date
                        TEXT,
                        date_added
                        TEXT,
                        status
                        TEXT
                        DEFAULT
                        'active'
                    )''')
    # 4. MENING QARZLARIM (YANGI JADVAL)
    conn.execute('''CREATE TABLE IF NOT EXISTS my_debts
                    (
                        id
                        INTEGER
                        PRIMARY
                        KEY
                        AUTOINCREMENT,
                        supplier
                        TEXT, -- Korxona nomi
                        phone
                        TEXT,
                        amount
                        REAL,
                        currency
                        TEXT
                        DEFAULT
                        'UZS',
                        note
                        TEXT,
                        due_date
                        TEXT,
                        date_added
                        TEXT,
                        status
                        TEXT
                        DEFAULT
                        'active'
                    )''')
    # 5. Tarix
    conn.execute('''CREATE TABLE IF NOT EXISTS logs
                    (
                        id
                        INTEGER
                        PRIMARY
                        KEY
                        AUTOINCREMENT,
                        action
                        TEXT,
                        details
                        TEXT,
                        date_time
                        TEXT
                    )''')
    conn.commit()
    conn.close()


init_db()


# --- FILTR ---
@app.template_filter('date_color')
def date_color_filter(date_str):
    try:
        due_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        today = datetime.now().date()
        days_left = (due_date - today).days
        if days_left < 0:
            return "bg-danger text-white"
        elif days_left == 0:
            return "bg-danger text-white border border-dark"
        elif days_left <= 3:
            return "bg-warning text-dark fw-bold"
        else:
            return "bg-primary bg-opacity-10 text-primary border border-primary"
    except:
        return "bg-secondary text-white"


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'): return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


def log_activity(action_text, details_text=None):
    try:
        with sqlite3.connect('database.db', timeout=10) as conn:
            conn.execute('PRAGMA journal_mode=WAL;')
            now = datetime.now().strftime('%d-%m-%Y %H:%M')
            conn.execute("INSERT INTO logs (action, details, date_time) VALUES (?, ?, ?)",
                         (action_text, details_text, now))
            conn.commit()
    except:
        pass


@app.after_request
def add_header(response):
    if 'static' in request.path:
        response.cache_control.max_age = 31536000
        response.cache_control.public = True
    return response


# --- ROUTES ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # TEKSHIRUV: Login va Parol ikkalasi ham to'g'ri bo'lishi shart
        if username == ADMIN_LOGIN and password == ADMIN_PAROL:
            session.permanent = True
            session['logged_in'] = True
            # Ekranda chiroyli ko'rinishi uchun katta harflarda saqlaymiz
            session['username'] = username.upper()
            session['login_time'] = datetime.now().strftime("%d-%m-%Y %H:%M")
            return redirect(url_for('dashboard'))
        else:
            error = "Login yoki Parol xato! (Diqqat: Katta-kichik harflarga e'tibor bering)"

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/')
@login_required
def dashboard():
    conn = get_db()
    stats = {
        'sales_uzs': conn.execute("SELECT SUM(total_price) FROM sales WHERE currency != 'USD'").fetchone()[0] or 0,
        'sales_usd': conn.execute("SELECT SUM(total_price) FROM sales WHERE currency = 'USD'").fetchone()[0] or 0,
        'profit_uzs': conn.execute("SELECT SUM(profit) FROM sales WHERE currency != 'USD'").fetchone()[0] or 0,
        'profit_usd': conn.execute("SELECT SUM(profit) FROM sales WHERE currency = 'USD'").fetchone()[0] or 0,
        'debts_uzs':
            conn.execute("SELECT SUM(amount) FROM debts WHERE status='active' AND currency != 'USD'").fetchone()[
                0] or 0,
        'debts_usd':
            conn.execute("SELECT SUM(amount) FROM debts WHERE status='active' AND currency = 'USD'").fetchone()[0] or 0,
        'products': conn.execute("SELECT COUNT(*) FROM products").fetchone()[0] or 0
    }
    chart = conn.execute(
        'SELECT substr(date_sold, 1, 10) as date, SUM(total_price) as total FROM sales GROUP BY date ORDER BY date DESC LIMIT 7').fetchall()
    recent = conn.execute(
        'SELECT s.*, p.name FROM sales s LEFT JOIN products p ON s.product_id = p.id ORDER BY s.id DESC LIMIT 5').fetchall()
    conn.close()
    return render_template('dashboard.html', stats=stats, recent_sales=recent,
                           chart_labels=[r['date'] for r in chart][::-1],
                           chart_values=[r['total'] for r in chart][::-1])


@app.route('/inventory', methods=['GET', 'POST'])
@login_required
def inventory():
    conn = get_db()
    if request.method == 'POST':
        if 'add_stock' in request.form:
            conn.execute("UPDATE products SET quantity = quantity + ? WHERE id=?",
                         (int(request.form['added_qty']), request.form['id']))
            conn.commit()
            log_activity(f"Kirim: {request.form['product_name']} (+{request.form['added_qty']})")
            return redirect(url_for('inventory'))
        elif 'delete_product' in request.form:
            conn.execute("DELETE FROM products WHERE id=?", (request.form['id'],))
            conn.commit()
            log_activity(f"O'chirildi: {request.form['product_name']}")
            return redirect(url_for('inventory'))
        else:
            file = request.files['image']
            fname = secure_filename(file.filename) if file else ''
            if fname:
                try:
                    img = Image.open(file)
                    img.thumbnail((400, 400))
                    img.save(os.path.join(app.config['UPLOAD_FOLDER'], fname), quality=85, optimize=True)
                except:
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
            conn.execute(
                "INSERT INTO products (name, category, buy_price, sell_price, currency, quantity, image, date_added) VALUES (?,?,?,?,?,?,?,?)",
                (request.form['name'], request.form['category'], float(request.form['buy_price']),
                 float(request.form['sell_price']), request.form['currency'], int(request.form['quantity']), fname,
                 datetime.now().strftime('%Y-%m-%d')))
            conn.commit()
            log_activity(f"Yangi: {request.form['name']} ({request.form['currency']})")
            return redirect(url_for('inventory'))
    products = conn.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('inventory.html', products=products)


@app.route('/pos')
@login_required
def pos():
    conn = get_db()
    products = conn.execute("SELECT * FROM products WHERE quantity > 0").fetchall()
    conn.close()
    return render_template('pos.html', products=products)


@app.route('/api/sell', methods=['POST'])
@login_required
def sell_api():
    data = request.json['cart']
    conn = get_db()
    try:
        # 1. HAMMA TOVAR YETARLIMI? (Tekshirish)
        for item in data:
            p = conn.execute("SELECT name, quantity FROM products WHERE id=?", (item['id'],)).fetchone()
            if not p:
                return jsonify({'success': False, 'message': f"Mahsulot topilmadi (ID: {item['id']})"})
            if p['quantity'] < item['qty']:
                return jsonify(
                    {'success': False, 'message': f"'{p['name']}' yetarli emas! Omborda: {p['quantity']} dona."})

        # 2. SOTISH VA CHEK YASASH
        total_sum_uzs = 0
        total_sum_usd = 0

        details_html = "<table class='table table-bordered table-sm mb-0'><thead><tr><th>Nomi</th><th>Soni</th><th>Narx</th><th>Jami</th></tr></thead><tbody>"

        for item in data:
            p = conn.execute("SELECT * FROM products WHERE id=?", (item['id'],)).fetchone()

            # Summalarni hisoblash
            item_total = p['sell_price'] * item['qty']

            if p['currency'] == 'USD':
                # DOLLAR (2 xona qoldiramiz .00)
                total_sum_usd += item_total
                price_fmt = f"$ {p['sell_price']:,.2f}"
                total_fmt = f"$ {item_total:,.2f}"
            else:
                # SO'M (O'ZGARTIRILDI: .0f qildik, ya'ni butun son)
                total_sum_uzs += item_total
                price_fmt = f"{p['sell_price']:,.0f} so'm"
                total_fmt = f"{item_total:,.0f} so'm"

            profit = (p['sell_price'] - p['buy_price']) * item['qty']

            # Bazadan ayirish
            conn.execute("UPDATE products SET quantity = quantity - ? WHERE id=?", (item['qty'], item['id']))
            conn.execute(
                "INSERT INTO sales (product_id, quantity, total_price, currency, profit, date_sold) VALUES (?,?,?,?,?,?)",
                (item['id'], item['qty'], item_total, p['currency'], profit,
                 datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

            # Jadval qatori
            details_html += f"<tr><td>{p['name']}</td><td>{item['qty']}</td><td>{price_fmt}</td><td>{total_fmt}</td></tr>"

        details_html += "</tbody>"

        # --- JAMI SUMMA QISMI (O'zgartirildi) ---
        details_html += "<tfoot class='bg-light'>"

        if total_sum_uzs > 0:
            # So'm uchun .0f (butun)
            details_html += f"<tr><th colspan='3' class='text-end'>Jami (SO'M):</th><th class='text-dark fw-bold'>{total_sum_uzs:,.0f} so'm</th></tr>"

        if total_sum_usd > 0:
            # Dollar uchun .2f (sentlar bilan)
            details_html += f"<tr><th colspan='3' class='text-end'>Jami (USD):</th><th class='text-success fw-bold'>$ {total_sum_usd:,.2f}</th></tr>"

        details_html += "</tfoot></table>"
        # --------------------------------------------------

        conn.commit()

        # Log uchun qisqa matn
        log_text = "Sotuv: "
        parts = []
        if total_sum_uzs > 0: parts.append(f"{total_sum_uzs:,.0f} so'm")  # Logda ham 00 siz
        if total_sum_usd > 0: parts.append(f"${total_sum_usd:,.2f}")
        log_text += " & ".join(parts)

        log_activity(log_text, details_html)
        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()



# --- 1. NASIYALAR (Mijozlar) ---
@app.route('/debts', methods=['GET', 'POST'])
@login_required
def debts():
    conn = get_db()
    if request.method == 'POST':
        if 'pay' in request.form:
            conn.execute("UPDATE debts SET status='paid' WHERE id=?", (request.form['id'],))
            log_activity(f"Qarz to'landi: ID {request.form['id']}")
        elif 'delete' in request.form:
            conn.execute("UPDATE debts SET status='deleted' WHERE id=?", (request.form['id'],))
            log_activity(f"Qarz o'chirildi: ID {request.form['id']}")
        else:
            conn.execute(
                "INSERT INTO debts (customer, phone, amount, currency, note, due_date, date_added) VALUES (?,?,?,?,?,?,?)",
                (request.form['customer'], request.form['phone'], request.form['amount'],
                 request.form['currency'], request.form['note'], request.form['date'],
                 datetime.now().strftime("%Y-%m-%d %H:%M")))
            log_activity(f"Nasiya: {request.form['customer']}")
        conn.commit()
        return redirect(url_for('debts'))

    debts = conn.execute("SELECT * FROM debts WHERE status='active' ORDER BY due_date ASC").fetchall()
    conn.close()
    return render_template('debts.html', debts=debts)


# --- 2. MENING QARZLARIM (Taminotchilar) - YANGI ---
@app.route('/my_debts', methods=['GET', 'POST'])
@login_required
def my_debts():
    conn = get_db()
    if request.method == 'POST':
        # To'landi
        if 'pay' in request.form:
            conn.execute("UPDATE my_debts SET status='paid' WHERE id=?", (request.form['id'],))
            log_activity(f"Korxona qarzi to'landi (ID: {request.form['id']})")
        # O'chirildi
        elif 'delete' in request.form:
            conn.execute("UPDATE my_debts SET status='deleted' WHERE id=?", (request.form['id'],))
            log_activity(f"Korxona qarzi o'chirildi (ID: {request.form['id']})")
        # Yangi qo'shish
        else:
            conn.execute(
                "INSERT INTO my_debts (supplier, phone, amount, currency, note, due_date, date_added) VALUES (?,?,?,?,?,?,?)",
                (request.form['supplier'], request.form['phone'], request.form['amount'],
                 request.form['currency'], request.form['note'], request.form['date'],
                 datetime.now().strftime("%Y-%m-%d %H:%M")))
            log_activity(f"Bizning qarz (Kirim): {request.form['supplier']}")
        conn.commit()
        return redirect(url_for('my_debts'))

    my_debts = conn.execute("SELECT * FROM my_debts WHERE status='active' ORDER BY due_date ASC").fetchall()
    conn.close()
    return render_template('my_debts.html', my_debts=my_debts)


@app.route('/archive', methods=['GET', 'POST'])
@login_required
def archive():
    conn = get_db()

    # 1. TIKLASH (RESTORE)
    if request.method == 'POST' and 'restore' in request.form:
        debt_id = request.form['id']
        debt_type = request.form['type']

        if debt_type == 'supplier':
            conn.execute("UPDATE my_debts SET status='active' WHERE id=?", (debt_id,))
            log_activity(f"Tiklandi (Bizning qarz): ID {debt_id}")
        else:
            conn.execute("UPDATE debts SET status='active' WHERE id=?", (debt_id,))
            log_activity(f"Tiklandi (Mijoz): ID {debt_id}")

        conn.commit()
        return redirect(url_for('archive'))

    # 2. LOGLAR (Tarix)
    logs = conn.execute("SELECT * FROM logs ORDER BY id DESC LIMIT 100").fetchall()

    # 3. NASIYALARNI OLISH VA BIRLASHTIRISH
    # A) Mijozlarning o'chirilgan/to'langan qarzlari
    cust_rows = conn.execute("SELECT * FROM debts WHERE status != 'active' ORDER BY id DESC").fetchall()
    # B) Bizning o'chirilgan/to'langan qarzlar
    supp_rows = conn.execute("SELECT * FROM my_debts WHERE status != 'active' ORDER BY id DESC").fetchall()

    all_archived = []

    # Mijozlarni ro'yxatga qo'shamiz (Formatlaymiz)
    for row in cust_rows:
        item = dict(row)  # Bazadagi qatorni oddiy lug'atga aylantiramiz
        item['type'] = 'customer'
        item['display_name'] = item['customer']  # Ekranda ko'rinadigan ism
        all_archived.append(item)

    # Bizning qarzlarni ro'yxatga qo'shamiz
    for row in supp_rows:
        item = dict(row)
        item['type'] = 'supplier'
        item['display_name'] = item['supplier']  # Ekranda ko'rinadigan ism (Korxona)
        all_archived.append(item)

    # ID bo'yicha saralaymiz (Yangi o'chirilganlar tepada turadi)
    all_archived.sort(key=lambda x: x['id'], reverse=True)

    conn.close()
    return render_template('archive.html', logs=logs, all_archived=all_archived)




if __name__ == '__main__':
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = "127.0.0.1"
    print(f"\n✅ DASTUR ISHGA TUSHDI!\n👉 http://{local_ip}:5000\n")
    serve(app, host='0.0.0.0', port=5000, threads=6)