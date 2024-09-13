from datetime import datetime, timedelta

import firebase_admin
from firebase_admin import credentials, db


class FirebaseConnection:

    def __init__(self, service_key, db_url, app_name):
        self.app_name = app_name
        self.db_url = db_url
        self.service_key = service_key
        self.app = self.initialize_connection()

    def getOnlineValues(self):
        if self.is_connected():
            try:
                ref = db.reference("/configs/", app=self.app)
                return {
                    'termos'        : str(ref.child('termos').get()).split(','),
                    'minimoDiario'  : ref.child('minimoDiario').get(),
                    'qtyPorTermo'   : ref.child('qtyPorTermo').get(),
                    'maxTentativas' : ref.child('maxTentativas').get(),
                    'sites':{
                        'xvideos'   : bool(ref.child('sites/xvideos').get()),
                        'xnxx'      : bool(ref.child('sites/xnxx').get()),
                        'pornhub'   : bool(ref.child('sites/pornhub').get()),
                        'spankbang' : bool(ref.child('sites/spankbang').get()),
                        'eporner'   : bool(ref.child('sites/eporner').get()),
                        'sex'       : bool(ref.child('sites/sex').get()),
                        'hqporner'  : bool(ref.child('sites/hqporner').get()),
                    }
                }
            except:
                return None
        else:
            return None

    def initialize_connection(self):
        try:
            cred = credentials.Certificate(self.service_key)
            return firebase_admin.initialize_app(cred,
                                                 {'databaseURL': self.db_url},
                                                 self.app_name)
        except Exception as e:
            try:
                if firebase_admin.get_app(self.app_name):
                    return firebase_admin.get_app(self.app_name)
            except Exception as e:
                print(f"Falha ao conectar ao Firebase: {e}")
                return None

    def is_connected(self):
        return self.app is not None

    def report(self, data):
        if self.is_connected():
            try:
                now = datetime.now()
                timezone_offset = -3
                adjusted_now = now + timedelta(hours=timezone_offset)
                current_date = adjusted_now.strftime('%d-%m-%Y')
                timestamp = adjusted_now.strftime('%d-%m-%Y %H:%M:%S')
                report_ref = db.reference(f"/relatorios/{current_date}/",
                                          app=self.app)
                data['timestamp'] = timestamp
                report_ref.push(data)
            except Exception as e:
                print(f"Falha ao registrar relatório no Firebase: {e}")
