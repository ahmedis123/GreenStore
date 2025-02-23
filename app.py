from flask import Flask, render_template_string, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_reuploaded import UploadSet, configure_uploads, IMAGES
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///phone_store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOADED_PHOTOS_DEST'] = 'static/uploads'
app.config['SECRET_KEY'] = 'supersecretkey'

db = SQLAlchemy(app)

# إعداد Flask-Reuploaded
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

# تعريف نموذج الهاتف
class Phone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float), nullable=False)
    condition = db.Column(db.String(20), nullable=False)  # جديد أو مستعمل
    image = db.Column(db.String(200), nullable=False)

# تعريف نموذج الطلب
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_id = db.Column(db.Integer, db.ForeignKey('phone.id'), nullable=False)
    quantity = db.Column(db.Integer), nullable=False)

# إنشاء قاعدة البيانات
with app.app_context():
    db.create_all()

# الصفحة الرئيسية
@app.route('/')
def index():
    phones = Phone.query.all()
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>متجر الهواتف</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-dark bg-dark">
            <div class="container">
                <a class="navbar-brand" href="/">متجر الهواتف</a>
            </div>
        </nav>
        <div class="container mt-4">
            <div class="row">
                {% for phone in phones %}
                <div class="col-md-4 mb-4">
                    <div class="card">
                        <img src="{{ phone.image }}" class="card-img-top" alt="{{ phone.name }}">
                        <div class="card-body">
                            <h5 class="card-title">{{ phone.name }}</h5>
                            <p class="card-text">{{ phone.brand }} - {{ phone.condition }}</p>
                            <p class="card-text">السعر: {{ phone.price }} ريال</p>
                            <a href="{{ url_for('product', id=phone.id) }}" class="btn btn-primary">تفاصيل</a>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    ''', phones=phones)

# صفحة المنتج
@app.route('/product/<int:id>')
def product(id):
    phone = Phone.query.get_or_404(id)
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{ phone.name }}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-dark bg-dark">
            <div class="container">
                <a class="navbar-brand" href="/">متجر الهواتف</a>
            </div>
        </nav>
        <div class="container mt-4">
            <div class="row">
                <div class="col-md-6">
                    <img src="{{ phone.image }}" class="img-fluid" alt="{{ phone.name }}">
                </div>
                <div class="col-md-6">
                    <h1>{{ phone.name }}</h1>
                    <p>الماركة: {{ phone.brand }}</p>
                    <p>الحالة: {{ phone.condition }}</p>
                    <p>السعر: {{ phone.price }} ريال</p>
                    <form action="{{ url_for('add_to_cart', id=phone.id) }}" method="POST">
                        <label for="quantity">الكمية:</label>
                        <input type="number" id="quantity" name="quantity" min="1" value="1" class="form-control mb-3">
                        <button type="submit" class="btn btn-success">إضافة إلى السلة</button>
                    </form>
                </div>
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    ''', phone=phone)

# إضافة إلى سلة المشتريات
@app.route('/add_to_cart/<int:id>', methods=['POST'])
def add_to_cart(id):
    quantity = request.form.get('quantity', type=int)
    new_order = Order(phone_id=id, quantity=quantity)
    db.session.add(new_order)
    db.session.commit()
    flash('تمت إضافة المنتج إلى السلة بنجاح!', 'success')
    return redirect(url_for('cart'))

# سلة المشتريات
@app.route('/cart')
def cart():
    orders = Order.query.all()
    phones = [Phone.query.get(order.phone_id) for order in orders]
    total = sum(phone.price * order.quantity for phone, order in zip(phones, orders))
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>سلة المشتريات</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-dark bg-dark">
            <div class="container">
                <a class="navbar-brand" href="/">متجر الهواتف</a>
            </div>
        </nav>
        <div class="container mt-4">
            <h1>سلة المشتريات</h1>
            {% for order, phone in zip(orders, phones) %}
            <div class="card mb-3">
                <div class="row g-0">
                    <div class="col-md-4">
                        <img src="{{ phone.image }}" class="img-fluid" alt="{{ phone.name }}">
                    </div>
                    <div class="col-md-8">
                        <div class="card-body">
                            <h5 class="card-title">{{ phone.name }}</h5>
                            <p class="card-text">الكمية: {{ order.quantity }}</p>
                            <p class="card-text">السعر الإجمالي: {{ phone.price * order.quantity }} ريال</p>
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}
            <h3>المجموع: {{ total }} ريال</h3>
            <a href="{{ url_for('checkout') }}" class="btn btn-success">الدفع</a>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    ''', orders=orders, phones=phones, total=total)

# صفحة الدفع
@app.route('/checkout')
def checkout():
    orders = Order.query.all()
    for order in orders:
        db.session.delete(order)
    db.session.commit()
    flash('تمت عملية الدفع بنجاح! شكرًا لشرائك.', 'success')
    return redirect(url_for('index'))

# لوحة التحكم (إدارة المنتجات)
@app.route('/admin')
def admin():
    phones = Phone.query.all()
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>لوحة التحكم</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-dark bg-dark">
            <div class="container">
                <a class="navbar-brand" href="/">متجر الهواتف</a>
            </div>
        </nav>
        <div class="container mt-4">
            <h1>لوحة التحكم</h1>
            <h2>إضافة منتج جديد</h2>
            <form action="{{ url_for('add_product') }}" method="POST" enctype="multipart/form-data">
                <div class="mb-3">
                    <label for="name" class="form-label">اسم المنتج:</label>
                    <input type="text" id="name" name="name" class="form-control" required>
                </div>
                <div class="mb-3">
                    <label for="brand" class="form-label">الماركة:</label>
                    <input type="text" id="brand" name="brand" class="form-control" required>
                </div>
                <div class="mb-3">
                    <label for="price" class="form-label">السعر:</label>
                    <input type="number" id="price" name="price" step="0.01" class="form-control" required>
                </div>
                <div class="mb-3">
                    <label for="condition" class="form-label">الحالة:</label>
                    <select id="condition" name="condition" class="form-control" required>
                        <option value="جديد">جديد</option>
                        <option value="مستعمل">مستعمل</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label for="image" class="form-label">صورة المنتج:</label>
                    <input type="file" id="image" name="image" class="form-control" required>
                </div>
                <button type="submit" class="btn btn-primary">إضافة</button>
            </form>
            <h2 class="mt-4">المنتجات</h2>
            <div class="row">
                {% for phone in phones %}
                <div class="col-md-4 mb-4">
                    <div class="card">
                        <img src="{{ phone.image }}" class="card-img-top" alt="{{ phone.name }}">
                        <div class="card-body">
                            <h5 class="card-title">{{ phone.name }}</h5>
                            <p class="card-text">{{ phone.brand }} - {{ phone.condition }}</p>
                            <p class="card-text">السعر: {{ phone.price }} ريال</p>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    ''', phones=phones)

# إضافة منتج جديد (لوحة التحكم)
@app.route('/admin/add', methods=['POST'])
def add_product():
    name = request.form.get('name')
    brand = request.form.get('brand')
    price = request.form.get('price')
    condition = request.form.get('condition')
    image = request.files.get('image')

    if image and photos.file_allowed(image, image.filename):
        filename = photos.save(image)
        image_url = url_for('static', filename=f'uploads/{filename}')
    else:
        image_url = None

    new_phone = Phone(name=name, brand=brand, price=price, condition=condition, image=image_url)
    db.session.add(new_phone)
    db.session.commit()
    flash('تمت إضافة المنتج بنجاح!', 'success')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
