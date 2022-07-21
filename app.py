from flask import Flask, render_template, redirect, session
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import random

#############################
# APP FLASK CONFIGURATION
app = Flask(__name__)
app.secret_key = ".."
# DATABASE CONFIGURATION
uri = os.environ.get('MONGO_DB_URI', "mongodb://127.0.0.1")
client = MongoClient(uri)
db = client.agualogic
#############################


@app.route("/")
def home_view():

    if not session.get('id'):
        session['id'] = random.randint(12345, 99999)
    masvendidos = list(db.productsfiltros.find({'top': "1"}))
    return render_template("agualogic_home.html", masvendidos=masvendidos, id=session.get('id'))


@app.route("/products")
def products_view():

    productsfiltros = list(db.productsfiltros.find())
    return render_template("agualogic_detalle.html", productsfiltros=productsfiltros)


@app.route("/category/<category>")
def catfiltros_view(category):
    productsfiltros = list(db.productsfiltros.find({'category': category}))
    return render_template("agualogic_detalle.html", productsfiltros=productsfiltros)


@app.route("/producto/detalle/<id>")
def producto_view(id):
    masvendidos = list(db.productsfiltros.find({'top': "1"}))
    # Estructura para Redireccionar por categoria de un elemento con id.
    productsfiltros = list(db.productsfiltros.find({'_id': ObjectId(id)}))
    return render_template("carrito.html", productsfiltros=productsfiltros, masvendidos=masvendidos)


@app.route("/add/<id>")
def add_product_to_cart(id):
    # Las variables de ruta como id siempre son un string inclusive los numeros
    product = db.productsfiltros.find_one({'_id': ObjectId(id)})

    """
    La funcion ObjectId() convierte un string en un ObjectId -El ObjectID
    es un tipo de dato como un string, un entero o un booleano-
    """
    if not session.get('id'):
        return redirect('/')

    user = session.get('id')

    nuevo = db.cart()
    nuevo['parrafo'] = product['parrafo']
    nuevo['img'] = product['img']
    nuevo['price'] = product['price']

    nuevo['user_id'] = user

    db.cart.insert_one(nuevo)

    return redirect('/cart')  # redirect me envia a la ruta de cart_view:


@app.route("/cart")
def cart_view():
    if not session.get('id'):
        return redirect('/')

    productsfiltros = list(db.cart.find())
    masvendidos = list(db.productsfiltros.find({'top': "1"}))
    return render_template(
        "cart_detalle.html", productsfiltros=productsfiltros, masvendidos=masvendidos)


@app.route("/checkout")
def check_view():
    cartproducts = list(db.cart.find())
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
