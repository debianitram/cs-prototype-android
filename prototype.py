#-*- encoding: utf-8 -*-

import sl4a
import time
import threading

from cs_api import CSApi


FOLLOW_END = False


class CSPrototype(sl4a.Android):
    POLICE = 'PO'
    EMERGENCY = 'EM'
    FIREFIGHTER = 'BM'
    TEST = 'TT'
    
    def __init__(self):
        super(CSPrototype, self).__init__()
        
        self.choices = (
            (CSPrototype.POLICE, 'Police'),
            (CSPrototype.FIREFIGHTER, 'Firefighter'),
            (CSPrototype.EMERGENCY, 'Emergency'),
            (CSPrototype.TEST, 'Follow up')
        )
        

        self.loop_end = False
        self.api = CSApi()

    def run(self):
        self.welcome()
        self.activate_gps()
        self.login()

        while not self.loop_end:

            type_alert = self.select_type_alert()

            if type_alert:
                if type_alert != CSPrototype.TEST:
                    payload = self.get_data_location()
                    payload.update(type_alert=type_alert)

                    self.api.sendSignal(payload)

                else:
                    # type_alert = CSPrototype.TEST
                    threading.Thread(
                        target=init_follow,
                        args=(self, )
                    ).start()

                    self.display_exit_mode_follow()

            else:
                self.loop_end = True

        self.stopLocating()

    
    def progressbar(self, time_=.1):
        title = 'Activando GPS'
        message = 'Buscando Señal...'
        self.dialogCreateHorizontalProgress(title, message, 100)
        self.dialogShow()

        for t in range(0, 50):
            time.sleep(time_)
            self.dialogSetCurrentProgress(t)
        self.dialogDismiss()

    def welcome(self):
        title = 'Prototype CS v0.1'
        message = '''
            Prototipo Aplicación Android
            Proyecto: Catamarca Segura
        '''

        self.dialogCreateAlert(title, message)
        self.dialogSetPositiveButtonText('Ingresar')
        self.dialogShow()
        response = self.dialogGetResponse().result

    def login(self):

        pass_user_end = False

        while not pass_user_end:

            username = self.dialogGetInput(
                'Username',
                'Username:'
            ).result

            password = self.dialogGetPassword(
                'Password', 
                'for: {}'.format(username)
            ).result

            self.api.setAuth(username, password)
            check_user = self.api.check_user()

            if check_user[0]:
                pass_user_end = True

            else:
                self.dialogCreateAlert('Error!', check_user[1])
                self.dialogSetPositiveButtonText('Ok')
                self.dialogSetNegativeButtonText('Exit')
                self.dialogShow()

                response = self.dialogGetResponse().result

                if response['which'] == 'negative':
                    pass_user_end = True
                    self.loop_end = True
        
    def select_type_alert(self):
        title = 'Select the type of alert'

        self.dialogCreateAlert(title)
        self.dialogSetSingleChoiceItems([i[1] for i in self.choices])
        self.dialogSetPositiveButtonText('Send alert!')
        self.dialogSetNegativeButtonText('Exit')
        self.dialogShow()

        response = self.dialogGetResponse().result

        if response['which'] == 'positive':
            selected = self.dialogGetSelectedItems().result[0]
            return [i[0] for i in self.choices][selected]

        else:
            return False
    
    def activate_gps(self):
        self.startLocating()
        self.progressbar()

    def get_data_location(self):
        result = self.readLocation().result
        point_format = 'POINT ({0} {1})'

        if not result:
            result = self.getLastKnowLocation().result

        if 'gps' in result.keys():
            device = result.get('gps')
        else:
            device = result.get('network')
            
        location = point_format.format(device['longitude'], device['latitude'])

        result = {
            'location': location,
            'bearing': device.get('bearing'),
            'provider': device.get('provider'),
            'accuracy': device.get('accuracy'),
        }

        print(result)
        
        return result


    def display_exit_mode_follow(self):
        global FOLLOW_END

        title = 'Mode: Test Follow'
        message = '''Init Mode Follow - Press End for terminate mode'''

        self.dialogCreateAlert(title, message)
        self.dialogSetPositiveButtonText('End')
        self.dialogShow()
        
        response = self.dialogGetResponse().result

        if response['which'] == 'positive':
            FOLLOW_END = True


def init_follow(csproto):
    global FOLLOW_END
    
    FOLLOW_END = False

    while not FOLLOW_END:
        payload = csproto.get_data_location()
        payload.update(type_alert=CSPrototype.TEST)
        
        csproto.api.sendSignal(payload)

        time.sleep(10)
    
if __name__ == '__main__':
    cs = CSPrototype()
    cs.run()

