import json
from flask import jsonify
from flask_restful import Resource, reqparse
import requests
from sqlalchemy import Date
from client_redis import banco

class PaymentLogResource(Resource):
    attrs = reqparse.RequestParser()
    attrs.add_argument('id_user', type=int, required=True, help="The field 'id' cannot be left blank.")
    attrs.add_argument('id_cob', type=int, required=True, help="The field 'id_cob' cannot be left blank.")
    

    def get(self):
        dados = PaymentLogResource.attrs.parse_args()
        logs = banco.lrange(f"paymentLog:{dados.id_user}", 0, -1)
        log = None
        for log_entry in logs:
            log_json = json.loads(log_entry)
            id_cobranca =  log_json[0]["cobranca"]["id_cob"]
            if dados.id_cob == id_cobranca:
                log = log_json[0]
                break
        return {"logs":log}, 200

class PaymentsLogResource(Resource):
    
    atributos = reqparse.RequestParser()
    atributos.add_argument('id_user', type=int, required=True, help="The field 'id' cannot be left blank.")
    atributos.add_argument('id_cob', type=str, required=True)
    atributos.add_argument('qnt_cob', type=str, required=True)
    atributos.add_argument('id_hotel', type=int, required=True)
    atributos.add_argument('status', type=str, required=False)
    atributos.add_argument('check_in', type=str, required=False)
    
    atributos.add_argument('id_room_option', type=int, required=False)
    atributos.add_argument('check_out', type=str, required=False)
    atributos.add_argument('pix_key', type=str, required=False)

    def get(self):
        
        dados = PaymentsLogResource.atributos.parse_args()

                
        logs = banco.lrange(f"paymentLog:{dados.id_user}", 0, -1)
        
        paymentlogs = { "logs": [] }
        for log in logs:
             l = json.loads(log)
             paymentlogs["logs"].append(l[0])

        return paymentlogs, 200


    def post(self):
        dados = PaymentsLogResource.atributos.parse_args()
        banco.rpush(f"paymentLog:{dados.id_user}", json.dumps([{ "cobranca": {"pix_key": dados.pix_key, "user_id" : dados.id_user, "qnt_cob": dados.qnt_cob, 
                                                                               "id_cob": dados.id_cob, "hotel_id": dados.id_hotel, "check_in": dados.check_in, "check_out": dados.check_out, "room_option_id": dados.id_room_option, "status": dados.status} }]))
        banco.save()
        return "bomDeu", 201