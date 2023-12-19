import pika

import os
from dotenv import load_dotenv

load_dotenv()

def request_send_email(status, email, nome_hotel, check_in, check_out):
    if status=="CONCLUIDA":
        #[0] to [4]
        msg = f'${status} ${email} ${nome_hotel} ${check_in} ${check_out}'
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()

        channel.queue_declare(queue='reservas')

        channel.basic_publish(exchange='',
                            routing_key='reservas',
                            body=msg)

        # Fechando a conexão
        connection.close()