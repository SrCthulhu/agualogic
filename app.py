from flask import Flask, render_template, redirect
from mongokit import Connection, Document, ObjectId

app = Flask(__name__)


class Masvendidos(Document):
    __database__ = 'agualogic'
    __collection__ = 'masvendidos'
    structure = {
        'img': str,
        'price': str,
        'parrafo': str,
    }


class Productsfiltros(Document):
    __database__ = 'agualogic'
    __collection__ = 'productsfiltros'
    structure = {
        'img': str,
        'price': str,
        'parrafo': str,
    }


class Filtros(Document):
    __database__ = 'agualogic'
    __collection__ = 'categoryfiltros'
    structure = {
        'img': str,
        'price': str,
        'parrafo': str,
    }


class Accesorios(Document):
    __database__ = 'agualogic'
    __collection__ = 'categoryaccesorios'
    structure = {
        'img': str,
        'price': str,
        'parrafo': str,
    }


class Termos(Document):
    __database__ = 'agualogic'
    __collection__ = 'categorytermos'
    structure = {
        'img': str,
        'price': str,
        'parrafo': str,
    }


class Cart(Document):
    __database__ = 'agualogic'
    # La coleccion se crea automaticamente, si ya hay un registro de datos como en este caso
    __collection__ = 'cart'
    structure = {
        'img': str,
        'price': str,
        'parrafo': str,
    }


db = Connection(host="localhost", port=27017)
db.register([Masvendidos, Productsfiltros, Filtros, Accesorios, Termos, Cart])


@app.route("/")
def home_view():

    masvendidos = list(db.Productsfiltros.find({'top': "1"}))
    return render_template("agualogic_home.html", masvendidos=masvendidos)


@app.route("/products")
def products_view():

    productsfiltros = list(db.Productsfiltros.find())
    return render_template("agualogic_detalle.html", productsfiltros=productsfiltros)


@app.route("/category/<category>")
def catfiltros_view(category):
    productsfiltros = list(db.Productsfiltros.find({'category': category}))
    return render_template("agualogic_detalle.html", productsfiltros=productsfiltros)


@app.route("/producto/detalle/<id>")
def producto_view(id):
    masvendidos = list(db.Productsfiltros.find({'top': "1"}))
    # Estructura para Redireccionar por categoria de un elemento con id.
    productsfiltros = list(db.Productsfiltros.find({'_id': ObjectId(id)}))
    return render_template("carrito.html", productsfiltros=productsfiltros, masvendidos=masvendidos)


@app.route("/add/<id>")
def add_product_to_cart(id):
    # Las variables de ruta como id siempre son un string inclusive los numeros
    product = db.Productsfiltros.find_one({'_id': ObjectId(id)})

    """
    La funcion ObjectId() convierte un string en un ObjectId -El ObjectID
    es un tipo de dato como un string, un entero o un booleano-
    """

    newProduct = db.Cart()
    newProduct['parrafo'] = product['parrafo']
    newProduct['img'] = product['img']
    newProduct['price'] = product['price']
    newProduct.save()

    return redirect('/cart')  # redirect me envia a la ruta de cart_view:


@app.route("/cart")
def cart_view():
    productsfiltros = list(db.Cart.find())
    masvendidos = list(db.Productsfiltros.find({'top': "1"}))
    return render_template(
        "cart_detalle.html", productsfiltros=productsfiltros, masvendidos=masvendidos)


@app.route("/checkout")
def check_view():
    cartproducts = list(db.Cart.find())
    # operación para calcular subtotales, sumar distintos valores.
    subtotal = 0
    for p in cartproducts:
        # este codigo de .replace sirve para remplazar el string $ por un espacio en blanco '' y se pueda hacer la suma y tambien la , y el . al final.
        price = p['price'].replace('$', '').replace(',', '').replace('.00', '')
        subtotal = subtotal + int(price)
    # operación para sumar iva al total en este caso 19% de iva.
    total = subtotal * 1.19

    return render_template("checkout.html",
                           cartproducts=cartproducts,
                           subtotal=subtotal,
                           total=total,
                           )
