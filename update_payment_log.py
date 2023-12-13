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
                    params_detail = {
                        'txid': l[0]["cobranca"]['id_cob']
                    }
                    detail = efi.pix_detail_charge(params=params_detail)
                    print(l[0]["cobranca"]["status"] == "ATIVA", file=sys.stderr)
                    print(detail["status"] == "CONCLUIDA", file=sys.stderr)
                    if (detail["status"] == "CONCLUIDA" and l[0]["cobranca"]["status"] == "ATIVA"):
                        try:
                            data = { "user_id": l[0]["cobranca"]["id_user"], "qnt_cob": l[0]["cobranca"]["qnt_cob"], "check_in": l[0]["cobranca"]["check_in"], "check_out": l[0]["cobranca"]["check_in"], "room_option_id": l[0]["cobranca"]["id_room_option"] }
                        
                            requests.post("http://192.168.0.191:3000/hotel_reservations", json = data)

                            banco.lset(f"{key.decode()}", i, json.dumps([{ "cobranca": { "id_user": l[0]["cobranca"]["id_user"], "qnt_cob": l[0]["cobranca"]["qnt_cob"],
                                                                               "id_cob": l[0]["cobranca"]["id_cob"], "id_hotel": l[0]["cobranca"]["id_hotel"], "check_in": l[0]["cobranca"]["check_in"], "check_out": l[0]["cobranca"]["check_in"], "id_room_option": l[0]["cobranca"]["id_room_option"], "status": detail["status"] }}]))
                        except Exception as e:
                            print(e, sys.stderr)
                        


            banco.save()
            sleep(10)

        except Exception as e:
            print(e)
            sleep(5)