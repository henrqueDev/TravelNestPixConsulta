import json
import sys
from flask import jsonify, request
from flask_restful import Resource, reqparse
import requests
from sqlalchemy import Date
from client_redis import banco

class PaymentLogResource(Resource):
    #attrs = reqparse.RequestParser()
    
    
    def get(self):
        user_id = request.args.get('user_id')
        cob_id = request.args.get('cob_id')
        
        logs = banco.lrange(f"paymentLog:{user_id}", 0, -1)
        log = None
        for log_entry in logs:
            log_json = json.loads(log_entry)
            id_cobranca =  log_json[0]["cobranca"]["cob_id"]
            if cob_id == id_cobranca:
                log = log_json[0]
                break
        return {"logs":log}, 200

class PaymentsLogResource(Resource):
    
    atributos = reqparse.RequestParser()
    atributos.add_argument('user_id', type=int, required=True, help="The field 'id' cannot be left blank.")
    atributos.add_argument('cob_id', type=str, required=False)
    atributos.add_argument('total_price', type=str, required=False)
    atributos.add_argument('hotel_id', type=int, required=False)
    atributos.add_argument('status', type=str, required=False)
    atributos.add_argument('check_in', type=str, required=False)
    
    atributos.add_argument('room_option_id', type=int, required=False)
    atributos.add_argument('check_out', type=str, required=False)
    atributos.add_argument('pix_key', type=str, required=False)
    atributos.add_argument('children_quantity', type=int, required=False)
    atributos.add_argument('adults_quantity', type=int, required=False)

    def get(self):
        
        user_id = request.args.get('user_id')
                
        logs = banco.lrange(f"paymentLog:{user_id}", 0, -1)
        
        paymentlogs = { "logs": [] }
        for log in logs:
             l = json.loads(log)
             paymentlogs["logs"].append(l[0])

        return paymentlogs, 200


    def post(self):
        dados = PaymentsLogResource.atributos.parse_args()
        banco.rpush(f"paymentLog:{dados.user_id}", json.dumps([{ "cobranca": {"pix_key": dados.pix_key, "user_id" : dados.user_id, "total_price": dados.total_price, 
                                                                               "cob_id": dados.cob_id, "hotel_id": dados.hotel_id, "check_in": dados.check_in, "check_out": dados.check_out, "room_option_id": dados.room_option_id, "status": dados.status, 
                                                                               "children_quantity": dados.children_quantity, "adults_quantity": dados.adults_quantity} }]))
        banco.save()
        return "bomDeu", 201