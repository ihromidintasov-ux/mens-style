from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Product, Cart
from datetime import datetime
import os

app = Flask(__name__)

app.config["SECRET_KEY"] = "mens-style-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mens_style.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Загрузка фотографий
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# Главная страница
@app.route("/")
def index():
    products = Product.query.order_by(Product.id.desc()).all()
    return render_template("index.html", products=products)


# Регистрация
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        if len(username) < 2 or len(password) < 8:
            flash("Имя должно быть от 2 символов, пароль — от 8.")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("Этот email уже зарегистрирован.")
            return redirect(url_for("register"))

        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password)
        )

        db.session.add(user)
        db.session.commit()

        flash("Регистрация успешна!")
        return redirect(url_for("login"))

    return render_template("register.html")


# Вход
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("index"))

        flash("Неверный email или пароль.")

    return render_template("login.html")


# Выход
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


# Каталог
@app.route("/catalog")
def catalog():
    category = request.args.get("category", "")
    search = request.args.get("search", "").strip()

    query = Product.query

    if category:
        query = query.filter_by(category=category)

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    products = query.order_by(Product.id.desc()).all()

    return render_template("catalog.html", products=products)


# Страница товара
@app.route("/product/<int:product_id>")
def product(product_id):
    product = db.get_or_404(Product, product_id)
    return render_template("product.html", product=product)


# Корзина
@app.route("/cart")
@login_required
def cart():
    items = Cart.query.filter_by(user_id=current_user.id).all()
    return render_template("cart.html", items=items, db=db, Product=Product)


# Добавление в корзину
@app.route("/cart/add/<int:product_id>", methods=["POST"])
@login_required
def add_to_cart(product_id):
    product = db.get_or_404(Product, product_id)

    item = Cart.query.filter_by(
        user_id=current_user.id,
        product_id=product.id
    ).first()

    if item:
        item.quantity += 1
    else:
        item = Cart(user_id=current_user.id, product_id=product.id)
        db.session.add(item)

    db.session.commit()
    flash("Товар добавлен в корзину!")
    return redirect(url_for("cart"))


# Удаление из корзины
@app.route("/cart/delete/<int:item_id>", methods=["POST"])
@login_required
def delete_from_cart(item_id):
    item = Cart.query.filter_by(
        id=item_id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(item)
    db.session.commit()

    flash("Товар удалён из корзины.")
    return redirect(url_for("cart"))


# Админ-панель
@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    if not current_user.is_admin:
        return "Доступ запрещён", 403

    if request.method == "POST":
        try:
            price = float(request.form["price"])
            if price <= 0:
                flash("Цена должна быть больше нуля.")
                return redirect(url_for("admin"))
        except ValueError:
            flash("Укажи правильную цену.")
            return redirect(url_for("admin"))

        image = ""
        file = request.files.get("image")

        if file and file.filename:
            if not allowed_file(file.filename):
                flash("Разрешены JPG, JPEG, PNG и WEBP.")
                return redirect(url_for("admin"))

            filename = secure_filename(file.filename)
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{filename}"

            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            image = filename

        product = Product(
            name=request.form["name"],
            description=request.form["description"],
            price=price,
            category=request.form["category"],
            size=request.form.get("size", ""),
            image=image
        )

        db.session.add(product)
        db.session.commit()

        flash("Товар успешно добавлен!")
        return redirect(url_for("admin"))

    products = Product.query.order_by(Product.id.desc()).all()
    return render_template("admin.html", products=products)


# Удаление товара
@app.route("/admin/delete/<int:product_id>", methods=["POST"])
@login_required
def delete_product(product_id):
    if not current_user.is_admin:
        return "Доступ запрещён", 403

    product = db.get_or_404(Product, product_id)

    Cart.query.filter_by(product_id=product.id).delete()

    db.session.delete(product)
    db.session.commit()

    flash("Товар удалён!")
    return redirect(url_for("admin"))


# Создание базы данных
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)