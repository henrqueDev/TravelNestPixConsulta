from email.mime.image import MIMEImage
import pika
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
load_dotenv()
#21312
# Função que será chamada quando uma mensagem for recebida
def callback(ch, method, properties, body):
    print(f" [x] Recebido: {body}")
    
# Configurações do servidor SMTP do Gmail
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587  # Porta de comunicação TLS

    # Suas credenciais de e-mail
    sender_email = 'travelnest2023ifpb@gmail.com'
    password = os.getenv('travelnest_email_secret')

    message = body.decode('utf-8').split(' ')
    # Detalhes do e-mail
    receiver_email = message[1]
    subject = 'Pagamento da Reserva confirmado!' if message[0] == 'CONCLUIDA'  else 'Prazo de Pagamento da Reserva expirado!'

    html = f"""
    <html>
    <body>
        <img src="cid:imagem_embedded">

        <h1> { 'OBRIGADOOOOO  :) ! ' if message[0] == 'CONCLUIDA'  else 'Prazo de Pagamento da Reserva expirado!' }</h1>
        <h2> { f'Check-in: {message[3]}   Check-out: {message[4]}'  if message[0] == 'CONCLUIDA' else '' }</h2>
        <h3>JUNTOS DERROTAREMOS A TRIVAGO!</h3>
    </body>
    </html>
    """

    # Criando o e-mail
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    #msg.attach(MIMEText(message, 'plain', 'utf-8'))

    body = MIMEText(html, 'html')
    msg.attach(body)

    with open('./travelNestLogo.png', 'rb') as img_file:
        img = MIMEImage(img_file.read())
        img.add_header('Content-Disposition', 'inline', filename='imagem_embedded')
        img.add_header('Content-ID', '<imagem_embedded>')
        msg.attach(img)
    # Conectando-se ao servidor SMTP do Gmail
    try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()  # Habilita a criptografia TLS
            server.login(sender_email, password)
            text = msg.as_string()
            server.sendmail(sender_email, receiver_email, text)
            print('E-mail enviado com sucesso!')
            
            server.quit()
    except Exception as e:
            print(f'Erro ao enviar o e-mail: {e}')

        # Fechando a conexão com o servidor
    # Aqui você pode adicionar a lógica para processar a reserva
    # Por exemplo, atualizar o banco de dados, enviar e-mails, etc.

# Conectando-se ao RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declarando a fila 'reservas' novamente para garantir que ela exista
channel.queue_declare(queue='reservas')

# Consumindo mensagens da fila 'reservas' e chamando a função callback
channel.basic_consume(queue='reservas',
                      on_message_callback=callback,
                      auto_ack=True)  # Confirma automaticamente o recebimento da mensagem

print(' [*] Aguardando mensagens. Para sair, pressione CTRL+C')
channel.start_consuming()