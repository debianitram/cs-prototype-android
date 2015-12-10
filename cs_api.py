import requests

from config import *


class CSApi(object):
    def __init__(self):
        self.auth = None
        self.headers = {
            'content-type': "multipart/form-data;",
            'cache-control': "no-cache",
        }

    def setAuth(self, username, password):
        self.auth = requests.auth.HTTPBasicAuth(username, password)

    def sendSignal(self, data):
        return requests.post(URL_SERVICE, data=data, auth=self.auth)

    def check_user(self):
        try:
            r = requests.post(URL_SERVICE + 'ping/', auth=self.auth)
            r.raise_for_status()
            return (True, '')

        except requests.exceptions.HTTPError:
            return (False, 'Controle User/Pass')
            
        except requests.exceptions.ConnectionError:
            return (False, 'Problemas con la conexión')

