from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse
from user import User

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager


app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = 'cainhogostoso'
api = Api(app)
jwt = JWTManager(app)

users = [
    User(1, 'caio', 'caminha123')
]

username_mapping = {u.username: u for u in users}
userid_mapping = {u.id : u for u in users}

items = []


class Security(Resource):
    def post(self):
        username = request.json.get("username", None)
        password = request.json.get("password", None)
        user = username_mapping.get(username)

        if username != user.username or password != user.password:
            return {"msg": "Bad username or password"}, 401
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token)
class Store(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
                        type=float,
                        required=True,
                        help='this field cannot be blank'
                        )


    #herda a classe Resource e sobrescreve o metodo get
    #funciona como um JpaRepository
    @jwt_required()
    def get(self, name):
        item = next(filter(lambda x : x['name'] == name, items), None)
        return {'item': item}, 200 if item else 404

    def post(self, name):
        if next(filter(lambda x : x['name'] == name, items), None):
            return {'message': "An item with the name {} alredy exists.".format(name)}, 400
        data = Store.parser.parse_args()
        item = {
            'name': name,
            'price': data['price']
        }
        items.append(item)
        return item

    def delete(self, name):
        #forces python to use the global variable 'itens'
        global items
        items = list(filter(lambda x : x['name'] != name, items))
        return {'message': 'Item was deleted successfully'}, 200

    def put(self, name):
        data = Store.parser.parse_args()
        item = next(filter(lambda x : x['name'] == name, items), None)
        if item is None:
            item = {'name': name, 'price': data['price']}
            items.append(item)
            return {'message': 'Item was created'}
        else:
            item.update(data)
            return {'message': 'Item was successfully updated'}

class ItemList(Resource):
    def get(self):
        return {'itens': items}

api.add_resource(Store, '/store/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(Security, '/login')

app.run(port=5001, debug=True)
