from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///phone_store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# تعريف نموذج الهاتف
class Phone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    condition = db.Column(db.String(20), nullable=False)  # جديد أو مستعمل
    image = db.Column(db.String(200), nullable=False)

# تعريف نموذج الطلب
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_id = db.Column(db.Integer, db.ForeignKey('phone.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

# إنشاء قاعدة البيانات
with app.app_context():
    db.create_all()

# الصفحة الرئيسية
@app.route('/')
def index():
    phones = Phone.query.all()
    return '''
    <!DOCTYPE html>
    <html lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>متجر الهواتف</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0; }
            header { background-color: #333; color: #fff; padding: 10px 0; text-align: center; }
            .products { display: flex; flex-wrap: wrap; justify-content: space-around; padding: 20px; }
            .product { background-color: #fff; border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin: 10px; width: 200px; text-align: center; }
            .product img { max-width: 100%; height: auto; }
        </style>
    </head>
    <body>
        <header>
            <h1>متجر الهواتف</h1>
        </header>
        <main>
            <section class="products">
                {% for phone in phones %}
                <div class="product">
                    <img src="{{ phone.image }}" alt="{{ phone.name }}">
                    <h2>{{ phone.name }}</h2>
                    <p>{{ phone.brand }} - {{ phone.condition }}</p>
                    <p>السعر: {{ phone.price }} ريال</p>
                    <a href="/product/{{ phone.id }}">تفاصيل</a>
                </div>
                {% endfor %}
            </section>
        </main>
    </body>
    </html>
    '''

# صفحة المنتج
@app.route('/product/<int:id>')
def product(id):
    phone = Phone.query.get_or_404(id)
    return f'''
    <!DOCTYPE html>
    <html lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{phone.name}</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0; }
            header { background-color: #333; color: #fff; padding: 10px 0; text-align: center; }
            .product-details { padding: 20px; text-align: center; }
            .product-details img { max-width: 100%; height: auto; }
        </style>
    </head>
    <body>
        <header>
            <h1>{phone.name}</h1>
        </header>
        <main>
            <section class="product-details">
                <img src="{phone.image}" alt="{phone.name}">
                <p>الماركة: {phone.brand}</p>
                <p>الحالة: {phone.condition}</p>
                <p>السعر: {phone.price} ريال</p>
                <form action="/add_to_cart/{phone.id}" method="POST">
                    <label for="quantity">الكمية:</label>
                    <input type="number" id="quantity" name="quantity" min="1" value="1">
                    <button type="submit">إضافة إلى السلة</button>
                </form>
            </section>
        </main>
    </body>
    </html>
    '''

# إضافة إلى سلة المشتريات
@app.route('/add_to_cart/<int:id>', methods=['POST'])
def add_to_cart(id):
    quantity = request.form.get('quantity', type=int)
    new_order = Order(phone_id=id, quantity=quantity)
    db.session.add(new_order)
    db.session.commit()
    return redirect('/cart')

# سلة المشتريات
@app.route('/cart')
def cart():
    orders = Order.query.all()
    phones = [Phone.query.get(order.phone_id) for order in orders]
    return '''
    <!DOCTYPE html>
    <html lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>سلة المشتريات</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0; }
            header { background-color: #333; color: #fff; padding: 10px 0; text-align: center; }
            .cart { padding: 20px; }
            .cart-item { background-color: #fff; border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin: 10px; }
        </style>
    </head>
    <body>
        <header>
            <h1>سلة المشتريات</h1>
        </header>
        <main>
            <section class="cart">
                {% for order, phone in zip(orders, phones) %}
                <div class="cart-item">
                    <img src="{{ phone.image }}" alt="{{ phone.name }}">
                    <h2>{{ phone.name }}</h2>
                    <p>الكمية: {{ order.quantity }}</p>
                    <p>السعر: {{ phone.price * order.quantity }} ريال</p>
                </div>
                {% endfor %}
                <a href="/checkout">الدفع</a>
            </section>
        </main>
    </body>
    </html>
    '''

# صفحة الدفع
@app.route('/checkout')
def checkout():
    return '''
    <!DOCTYPE html>
    <html lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>الدفع</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0; }
            header { background-color: #333; color: #fff; padding: 10px 0; text-align: center; }
            .checkout { padding: 20px; text-align: center; }
        </style>
    </head>
    <body>
        <header>
            <h1>الدفع</h1>
        </header>
        <main>
            <section class="checkout">
                <p>شكرًا لشرائك!</p>
            </section>
        </main>
    </body>
    </html>
    '''

# لوحة التحكم (إدارة المنتجات)
@app.route('/admin')
def admin():
    phones = Phone.query.all()
    return '''
    <!DOCTYPE html>
    <html lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>لوحة التحكم</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0; }
            header { background-color: #333; color: #fff; padding: 10px 0; text-align: center; }
            .admin { padding: 20px; }
            .admin form { margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <header>
            <h1>لوحة التحكم</h1>
        </header>
        <main>
            <section class="admin">
                <h2>إضافة منتج جديد</h2>
                <form action="/admin/add" method="POST">
                    <label for="name">اسم المنتج:</label>
                    <input type="text" id="name" name="name" required>
                    <label for="brand">الماركة:</label>
                    <input type="text" id="brand" name="brand" required>
                    <label for="price">السعر:</label>
                    <input type="number" id="price" name="price" step="0.01" required>
                    <label for="condition">الحالة:</label>
                    <select id="condition" name="condition" required>
                        <option value="جديد">جديد</option>
                        <option value="مستعمل">مستعمل</option>
                    </select>
                    <label for="image">رابط الصورة:</label>
                    <input type="url" id="image" name="image" required>
                    <button type="submit">إضافة</button>
                </form>
                <h2>المنتجات</h2>
                {% for phone in phones %}
                <div class="product">
                    <img src="{{ phone.image }}" alt="{{ phone.name }}">
                    <h2>{{ phone.name }}</h2>
                    <p>{{ phone.brand }} - {{ phone.condition }}</p>
                    <p>السعر: {{ phone.price }} ريال</p>
                </div>
                {% endfor %}
            </section>
        </main>
    </body>
    </html>
    '''

# إضافة منتج جديد (لوحة التحكم)
@app.route('/admin/add', methods=['POST'])
def add_product():
    name = request.form.get('name')
    brand = request.form.get('brand')
    price = request.form.get('price')
    condition = request.form.get('condition')
    image = request.form.get('image')
    new_phone = Phone(name=name, brand=brand, price=price, condition=condition, image=image)
    db.session.add(new_phone)
    db.session.commit()
    return redirect('/admin')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
