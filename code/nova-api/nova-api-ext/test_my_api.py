from novaclient.v1_1 import client
from novaclient.v1_1.contrib import myapi

class ExtensionManager:
    def __init__(self, name, manager_class):
        self.name = name
        self.manager_class = manager_class

novaclient = client.Client(
                 'nova',
                 'keystone_nova_password',
                 'service',
                 auth_url='http://10.239.131.218:5000/v2.0/',
                 extensions = [ExtensionManager('myapiManager',
                                                myapi.MyAPIManager)],
                )

print(novaclient.myapiManager.is_ok())
