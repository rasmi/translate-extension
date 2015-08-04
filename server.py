import threading
import requests
import json
import uuid
import time
from ws4py.client.threadedclient import WebSocketClient
from wsgiref.simple_server import make_server
from ws4py.websocket import WebSocket
from ws4py.server.wsgirefserver import WSGIServer, WebSocketWSGIRequestHandler
from ws4py.server.wsgiutils import WebSocketWSGIApplication

auth_token = None
translate_socket = None
server = None

class TranslateSocket(WebSocketClient):
    def opened(self):
        print 'TRANSLATE SOCKET OPENED'

    def closed(self, code, reason=None):
        print 'TRANSLATE SOCKET CLOSED', code, reason

    def received_message(self, message):
        print 'RECEIVED MESSAGE FROM TRANSLATOR'
        if message.is_binary:
            print 'GOT TRANSLATED AUDIO'
        elif message.is_text:
            print 'GOT TRANSLATED TEXT'
            print message

def get_auth_token():
    global auth_token
    if not auth_token:
        client_id = 'civic-translator-test'
        client_secret = 'civic-translator-test-secret'
        ADMurl = 'https://datamarket.accesscontrol.windows.net/v2/OAuth2-13'
        postData = {
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'http://api.microsofttranslator.com',
            'grant_type': 'client_credentials'
        }
        authrequest = requests.post(ADMurl, data=postData)
        auth_token = json.loads(authrequest.text)['access_token']

    return auth_token

def translate_socket_init():
    print 'STARTING TRANSLATE SOCKET'
    ws_url = 'wss://dev.microsofttranslator.com/api/speech'
    params = {
        'from':'en-US',
        'to': 'it-IT',
        'features': 'texttospeech',
        'voice':'it-IT-Elsa'
    }
    paramsString = '?from=%s&to=%s&features=%s&voice=%s' % (params['from'], params['to'], params['features'], params['voice'])
    ws_url += paramsString
    headers = [('X-ClientAppId', str(uuid.uuid4())), ('Authorization', 'Bearer '+get_auth_token()), ('X-CorrelationId', str(uuid.uuid4()))]
    print(headers)
    global translate_socket
    translate_socket = TranslateSocket(ws_url, headers=headers)
    translate_socket.connect()
    translate_socket.run_forever()

class ServerSocket(WebSocket):
    def opened(self):
        print 'SERVER SOCKET OPENED'

    def closed(self, code, reason=None):
        print 'SERVER SOCKET CLOSED', code, reason

    def received_message(self, message):
        print 'RECEIVED MESSAGE FROM CLIENT'
        if message.is_binary:
            translate_socket.send(message, binary=True)
        elif message.is_text:
            print message

def server_init():
    print 'STARTING SERVER SOCKET'
    global server
    server = make_server('', 9999, server_class=WSGIServer,
                     handler_class=WebSocketWSGIRequestHandler,
                     app=WebSocketWSGIApplication(handler_cls=ServerSocket))
    server.initialize_websockets_manager()
    server.serve_forever()
    
if __name__ == '__main__':
    translator_thread = threading.Thread(target=translate_socket_init)
    translator_thread.daemon = True
    server_thread = threading.Thread(target=server_init)
    server_thread.daemon = True
    translator_thread.start()
    server_thread.start()
    while True:
        time.sleep(1)