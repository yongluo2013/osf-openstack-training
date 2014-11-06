from novaclient import base

class MyAPIManager(base.ManagerWithFind):
    """Manager to send myapi url request"""

    def is_ok(self):
        resp, body = self.api.client.get('/myapi/is_ok')
        return body
