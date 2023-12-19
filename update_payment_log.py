
from time import sleep
from efipay import EfiPay
import requests
import credentials
import sys
import json
from client_redis import banco
import threading 
from service.send_email import request_send_email
import os
from dotenv import load_dotenv

load_dotenv()

def loop_all():
      
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
                            data =  {    
                                        "user_id": l["user_id"], 
                                        "total_price": l["total_price"],
                                        "check_in": l["check_in"],
                                        "check_out": l["check_out"],
                                        "room_option_id": l["room_option_id"],
                                        "children_quantity": l["children_quantity"],
                                        "adults_quantity": l["adults_quantity"],
                                        "user_email":l["user_email"],
                                        "hotel_name": l["hotel_name"],
                                        "key": os.getenv("key_api")
                                    }
                        
                            r = requests.post(os.getenv('endpoint_reservations'), json = data)
                                # status, email, nome_hotel, check_in, check_out
                            #request_send_email(detail["status"], l["user_email"], l["hotel_name"], l["check_in"], l["check_out"])

                            banco.lset(f"{key.decode()}", i, json.dumps([{ 
                                                                            "cobranca": { 
                                                                                            "pix_key": l["pix_key"], 
                                                                                            "user_id": l["user_id"],
                                                                                            "total_price": l["total_price"],
                                                                                            "cob_id": l["cob_id"],
                                                                                            "hotel_id": l["hotel_id"],
                                                                                            "check_in": l["check_in"],
                                                                                            "check_out": l["check_out"], 
                                                                                            "room_option_id": l["room_option_id"],
                                                                                            "status": detail["status"],
                                                                                            "children_quantity": l["children_quantity"],
                                                                                            "adults_quantity": l["adults_quantity"], 
                                                                                            "user_email": l["user_email"],
                                                                                            "hotel_name": l["hotel_name"] 
                                                                                        }
                                                                                    }
                                                                                ]
                                                                            )
                                                                        )
        except Exception as e:
            print(e, file=sys.stderr)
            sleep(5)

        
        banco.save()
        sleep(10)

thread_loop = threading.Thread(target=loop_all)
thread_loop.start()
thread_loop.join()

    