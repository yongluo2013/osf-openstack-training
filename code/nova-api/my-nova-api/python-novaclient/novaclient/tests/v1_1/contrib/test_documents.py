from novaclient.v1_1 import client
from novaclient.v1_1.contrib import documents

class ExtensionManager:
    def __init__(self, name, manager_class):
        self.name = name
        self.manager_class = manager_class

novaclient = client.Client(
                 'admin',
                 'quiet',
                 'admin',
                 auth_url='http://10.20.0.210:35357/v2.0/',
                 extensions = [ExtensionManager('documentManager',
                                                documents.DocumentManager)],
                )

print(novaclient.documentManager.list())
