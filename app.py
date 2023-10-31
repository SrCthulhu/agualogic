from flask import Flask, render_template, redirect, session, request, send_from_directory
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
print(uri)
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
    return render_template("inner_product_detail.html", productsfiltros=productsfiltros, masvendidos=masvendidos)

#@app.route("/update-counter", methods=["POST"])
### update_counter():
 #   data = request.get_json()
   # new_count = data.get("count")

    # Realiza las operaciones necesarias para actualizar el contador en el servidor

   # return "Contador actualizado", 200

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
 # paso 1 (agregar productos al carrito sin que se repitan) buscar en el carrito mismo nombre 'parrafo' de la colección pasada.
    cartproduct = db.cart.find_one(
        {'parrafo': product['parrafo'], 'user_id': user})  # busca por el filtro parrafo y tambien que sea el usuario que corresponde con 'user_id': user
#################################################
    if cartproduct:  # paso 2  #si el find_one consiguio devuelve un diccionario y es true, entonces si no consiguio nada lo devuelve como vacio y el if es false
        db.cart.update_one(
            # forma alternativa {'_id': ObjectId(cartproduct['_id'])} 👇 aqui estamos actualizando el mismo id del producto del carrito.
            {'parrafo': product['parrafo'], 'user_id': user},
            {'$set':
                # el producto que ya existe en el carrito nos devuelve la cantidad y le suma uno
                {'cantidad': cartproduct['cantidad'] + 1}
             }
        )
        return redirect('/cart')
        ####################################
    nuevo = {}
    nuevo['parrafo'] = product['parrafo']
    nuevo['img'] = product['img']
    nuevo['price'] = product['price']
    nuevo['cantidad'] = 1  # paso 3

    # ponemos el id al usuario con sus productos elegidos.
    nuevo['user_id'] = user

    db.cart.insert_one(nuevo)  # creamos documentos en la base de datos.

    return redirect('/cart')  # redirect me envia a la ruta de cart_view:


@app.route("/cart")
def cart_view():
    if not session.get('id'):
        return redirect('/')

    # llamamos la variable global. paso 1 necesitas user con el id
    user = session.get('id')
    # con el user_id:user filtramos por el id de usuario los productos cuando son agregados al carrito.
    productsfiltros = list(db.cart.find({'user_id': user}))  # paso 2
    masvendidos = list(db.productsfiltros.find({'top': "1"}))
    return render_template(
        "cart_detalle.html", productsfiltros=productsfiltros, masvendidos=masvendidos)


@app.route("/checkout")
def check_view():
    user = session.get('id')
    cartproducts = list(db.cart.find({'user_id': user}))
    # operación para calcular subtotales, sumar distintos valores.
    subtotal = 0
    for p in cartproducts:
        # este codigo de .replace sirve para remplazar el string $ por un espacio en blanco '' y se pueda hacer la suma y tambien la , y el . al final.
        price = p['price'].replace('$', '').replace(',', '').replace('.00', '')
        subtotal = subtotal + (int(price) * p['cantidad'])
    # operación para sumar iva al total en este caso 19% de iva.
    total = subtotal * 1.19

    # creacion de mensaje de error paso 1
    mensaje = request.args.get('mensaje')

    return render_template("checkout.html",
                           cartproducts=cartproducts,
                           subtotal=subtotal,
                           total=total,
                           mensaje=mensaje
                           )


@app.route("/remove/<id>")
def remove_to_cart(id):
    # borra de la colección del carrito.
    db.cart.delete_one({'_id': ObjectId(id)})
    return redirect('/cart')


@app.route("/order/create")
def order_created_view():
    # nombre del input documento del checkout.html
    document = request.args.get('document')
    firstName = request.args.get('first_name')
    lastName = request.args.get('last_name')
    companyName = request.args.get('company_name')
    address = request.args.get('address')
    state = request.args.get('state')
    country = request.args.get('country')
    phone = request.args.get('phone')
    email = request.args.get('email')
    total = request.args.get('total')
   #### #paso 2 creacion mensaje de error#####
    if document == "" or firstName == "" or lastName == "" or companyName == "" or address == "" or state == "" or country == "" or phone == "" or email == "" or total == "":
        return redirect('/checkout?mensaje=tienes campos vacios')
###################################################
     # paso 1 error emai l#
    emailSplitted = email.split('@')
    #email = 'hola@gmail.com'
    # emailSplitted = email.split('@') --> ['hola', 'gmail.com']

    # emailSplitted[0] --> 'hola'
    # emailSplitted[1] --> 'gmail.com'
    # paso 2 error email #
    if len(emailSplitted) != 2 or emailSplitted[1] != 'gmail.com':

        return redirect('/checkout?mensaje=la direccion de correo no es valida')

    userId = session.get('user_id')
    cartproducts = list(db.cart.find({'user_id': userId}))

    # pedido es un diccionario que tiene el diccionario client dentro.
    pedido = {}
    pedido['client'] = {
        'document': document,
        'first_name': firstName,
        'last_name': lastName,
        'company_name': companyName,
        'address': address,
        'state': state,
        'country': country,
        'phone': phone,
        'email': email
    }
    pedido['user_id'] = userId
    pedido['cart'] = cartproducts
    pedido['total'] = total
    orderCreated = db.orders.insert_one(pedido)
    orderId = orderCreated.inserted_id

    # borrar todos los productos del carrito DEL USUARIO
    db.cart.delete_many({'user_id': userId})

    return redirect('/order/' + str(orderId))


@app.route("/order/<id>")
def order_view(id):
    pedido = db.orders.find_one({'_id': ObjectId(id)})

    return render_template("order_created.html", pedido=pedido)
