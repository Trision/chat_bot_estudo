from flask import Flask, request, render_template
import json
import logging
import os
import requests

app             = Flask(__name__)
app.debug       = True

#-------------VARs Z-API ---------------- INICIO
instancia           = 'ID_da_INSTANCIA'
token               = 'TOKEN_DA_INSTANCIA'
sc_token            = {'client-token':'TOKEN_DE_SEGURANCA'}
#-------------VARs Z-API ---------------- FIM

#-------------------MSGs PADRÃO---------------------- INICIO
greeting            = """Olá, tudo bem com você?\n\nEu me chamo Dentin e sou o atendente virtual da Est-estica Odonto, como eu posso te ajudar hoje?\n\n1 - Reabilitação\n2 - Ortodontia\n\nPor favor responda com o número da opção desejada."""
passo_pos_gree      = 'Perfeito, nós temos as seguintes opções para você.\n\n1 - Como funciona?\n2 - Agendar'
agendamento         = 'Perfeito, nós iremos entrar em contato daqui a pouco.\n\nAgradecemos o seu contato.'
#-------------------MSGs PADRÃO---------------------- FIM

#Opções de reabilitação ---------- INICIO ------------
reab_info           = 'O procedimento funciona da seguinte forma:\nNós iremos começar fazendo um pré-avaliação da sua situação como um todo e então nós iremos criar um procedimento personalizado só para você.\n\n1 - Agendar\n2 - Sair'
opcoes_1_reab       = ['1','Reabilitação', 'reabilitação', 'reabilitacao', 'Reabilitacao', '1 - Reabilitação'] ##list of possibles responses for greet message
#Opções de reabilitação ---------- FIM ------------

#Opções de odonto ----------------- INICIO -----------------
odo_info            = 'O procedimento funciona da seguinte forma:\nNós iremos começar fazendo um pré-avaliação da sua boca e dentes e então nós iremos criar um procedimento personalizado só para você.\n\n1 - Agendar\n2 - Sair'
opcoes_odonto       = ['2', 'Ortodontia', 'ortodontia', 'odonto', 'dente', 'boca'] #list of possibles responses for greet message
#Opções de odonto ----------------- FIM -----------------


def envia_mensagem(telefone, mensagem):#Envia a mensagem utilizando a API do Z-API 
    # -------------------- Url da API ----------------------
    url = f'https://api.z-api.io/instances/{instancia}/token/{token}/send-text'
    # -------------------- Url da API ----------------------
    dados = {"phone":telefone, "message":mensagem}
    envio = requests.post(url, data=dados, headers=sc_token).text
    envio_json = json.loads(envio)
    json_retorno = {'message':mensagem, 'tel':telefone, 'enviada':'True'}
    return json_retorno

@app.post('/webhook')#This function will trigger with each new messagem from webhook
def webhook():#This chat_bot works with a API from Z-API 
    if request.method   == 'POST':
            retorno     = request.get_json()
            #Ignores message from groups, because we just need talk with a single person
            if retorno['isGroup']:
                  return '<p>Group</p>'
            #----------------- Vars from WEBHOOK ----------------  START
            tel         = retorno['phone']
            msg_rcb     = retorno['text']['message']
            #----------------- Vars from WEBHOOK ---------------- END
            path_log    = os.path.exists(f'./logs/{tel}.log') #CHECK IF WE ALREADY TALK WITH THE PERSON
            stopper_1   = 'msg de reab 1 enviada' #VAR FOR MARKS THE SENDING OF FIRST MESSAGE
            op_envia    = 'ops enviada' #VAR TO MARK THE SEND OF OPTION LIST
            log_path    = f'./logs/{tel}.log' 
            logger      = logging.getLogger(f'logger_{tel}') #GET LOG FOR THIS NUMBER/PERSON
            if not logger.handlers: #IF THERE'S NO LOG CREATE A NEW ONE
                file_handler = logging.FileHandler(log_path, encoding='UTF-8')
                logger.addHandler(file_handler)
                logger.setLevel(logging.INFO)
            with open(f'./logs/{tel}.log', 'r') as enviados: #OPEN LOG
                enviado     = enviados.read()
            while True: #AND HERE IS THE BEGGINING OF OUR CODE
                if 'Contato finalizado' not in enviado: #IF THE END MESSAGE IS IN LOG WE ALREADY TALKED WITH PERSON IN QUESTION
                        if 'True' in enviado: #IF 'TRUE' IN LOG WE JUST SENDED THE FIRST MESSAGE
                            if op_envia not in enviado: #SEND THE OPTION LIST FOR THE PERSON
                                    if msg_rcb in opcoes_1_reab:
                                        opcoes = envia_mensagem(tel, passo_pos_gree)
                                        logger.info(op_envia)
                                        logger.info('reab') #IT'S SHOW ON THE LOG IF THE PERSON HAVE CHOSEN THE OPTION 1
                                        break
                                    elif msg_rcb in opcoes_odonto:
                                        opcoes = envia_mensagem(tel, passo_pos_gree) #CALL THE FUNCTION TO SEND DESIRED MESSAGE
                                        logger.info(op_envia)
                                        logger.info('odon') #IT'S SHOW ON THE LOG IF THE PERSON HAVE CHOSEN THE OPTION 2
                                        break
                            elif op_envia in enviado:
                                    if 'odon' in enviado: #IF THE PERSON HAVE CHOSE THE OPTION 1 IT WILL FOLLOW THIS PATH
                                        if stopper_1 not in enviado: 
                                            if msg_rcb == '2':
                                                    agend_reab = envia_mensagem(tel, agendamento)
                                                    logger.info('Contato finalizado')
                                                    break                       
                                            if msg_rcb == '1':
                                                    reab_inf = envia_mensagem(tel, odo_info)
                                                    logger.info(stopper_1)
                                                    break
                                        elif stopper_1 in enviado:
                                                if msg_rcb      == '1':
                                                        agend_reab = envia_mensagem(tel, agendamento)
                                                        logger.info('Contato finalizado')
                                                        break
                                                elif msg_rcb    == '2':
                                                        logger.info('Contato finalizado')
                                                        break
                                    elif 'reab' in enviado: #IF THE PERSON HAVE CHOSEN OPTION 2 IT WILL FOLLOW THIS PATH
                                        if stopper_1 not in enviado:    
                                            if msg_rcb      == '2':
                                                    agend_reab = envia_mensagem(tel, agendamento)
                                                    logger.info('Contato finalizado')
                                                    break                       
                                            elif msg_rcb    == '1':
                                                        reab_inf = envia_mensagem(tel, reab_info)
                                                        logger.info(stopper_1)
                                                        break
                                        elif stopper_1 in enviado:
                                                if msg_rcb      == '1':
                                                        agend_reab = envia_mensagem(tel, agendamento)
                                                        logger.info('Contato finalizado')
                                                        break
                                                elif msg_rcb    == '2':
                                                        logger.info('Contato finalizado')
                                                        break
                        else:
                            logger.info(f'Conversa com o número {tel} iniciada', stack_info=False)# SHOWS IN THE LOG THE BEGGINING OF CHAT
                            greet_msg = envia_mensagem(tel, greeting)
                            logger.info(greet_msg, stack_info=False) #WE JUST NEED ONE INFO OF START
                            break #and breaks the WHILE statement
                else:
                    break
    else:
          return '<p>Método inválido</p>'   
    return '<p>Método inválido</p>'

if __name__ == "__main__":
    app.run(port=5000)