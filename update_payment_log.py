import os
from time import sleep
from efipay import EfiPay
import requests
import credentials
import sys
import json
from client_redis import banco



def update_payment_logs():
    efi = EfiPay(credentials.CREDENTIALS)

    
    while True:

        try:

            keys = banco.scan_iter("paymentLog:*")
            
            for key in keys:
            
                logs = banco.lrange(f"{key.decode()}", 0, -1)
            
                for i, log in enumerate(logs):
                    l = json.loads(log)
                    l = l[0]["cobranca"]
                    params_detail = {
                        'txid': l['cob_id']
                    }
                    detail = efi.pix_detail_charge(params=params_detail)
                    print(l["status"] == "ATIVA", file=sys.stderr)
                    print(detail["status"] == "CONCLUIDA", file=sys.stderr)
                    if (detail["status"] == "CONCLUIDA" and l["status"] == "ATIVA"):
                        try:
                            data = { "user_id": l["user_id"], "total_price": l["total_price"], "check_in": l["check_in"], "check_out": l["check_out"], "room_option_id": l["room_option_id"],
                                     "children_quantity": l["children_quantity"], "adults_quantity": l["adults_quantity"] }
                        
                            requests.post("http://192.168.0.191:3000/hotel_reservations", json = data)

                            banco.lset(f"{key.decode()}", i, json.dumps([{ "cobranca": { "pix_key": l["pix_key"], "user_id": l["user_id"], "total_price": l["total_price"],
                                                                            "cob_id": l["cob_id"], "hotel_id": l["hotel_id"], "check_in": l["check_in"], "check_out": l["check_out"], "room_option_id": l["room_option_id"], "status": detail["status"],
                                                                            "children_quantity": l["children_quantity"], "adults_quantity": l["adults_quantity"] }}]))
                        except Exception as e:
                            print(e, sys.stderr)
                        
        except Exception as e:
            print(e)
            sleep(5)

        
        banco.save()
        sleep(10)
