from flask import Flask
from flask_restful import Api
from resources.payment_log import PaymentsLogResource, PaymentLogResource
from client_redis import banco
from flask_cors import CORS
app = Flask(__name__)

CORS(app)

api = Api(app)

api.add_resource(PaymentsLogResource, '/consultaPagamentos')
api.add_resource(PaymentLogResource, '/consultaPagamento')

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)