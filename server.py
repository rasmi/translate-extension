import asyncio
import websockets
import requests
import json
import uuid

auth_token = None
translate_socket = None

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

@asyncio.coroutine
def server_handler(server, path):
    while True:
        message = yield from server.recv()
        if message is None:
            break
        elif message == 'START':
            print(message)
        elif message == 'STOP':
            print(message)
            translate_socket.send(bytearray(160000))
            while True:
                print('waiting for translation response')
                translation = yield from translate_socket.recv()
                if translation is None:
                    print('No response')
                    if not translate_socket.open:
                        print('translate_socket closed')
                        #translate_socket_init()
                    break
                print(translation)
        else:
            print(type(message))
            translate_socket.send(message)

@asyncio.coroutine
def translate_socket_init():
    ws_url = 'wss://dev.microsofttranslator.com/api/speech'
    params = {
        'from':'en-US',
        'to': 'it-IT',
        'features': 'texttospeech',
        'voice':'it-IT-Elsa'
    }
    paramsString = '?from=%s&to=%s&features=%s&voice=%s' % (params['from'], params['to'], params['features'], params['voice'])
    ws_url += paramsString
    headers = {'X-ClientAppId': str(uuid.uuid4()), 'Authorization': 'Bearer '+get_auth_token(), 'X-CorrelationId': str(uuid.uuid4())}
    print(headers)
    global translate_socket
    translate_socket = yield from websockets.connect(ws_url, extra_headers=headers)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(translate_socket_init())
    start_server = websockets.serve(server_handler, 'localhost', 9999)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()