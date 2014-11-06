from nova.api.openstack import wsgi
from nova.api.openstack import extensions

class Controller(wsgi.Controller):
    def is_ok(self, req):
        return {'key':'ok'}

class MyAPI(extensions.ExtensionDescriptor):
    """self-defined Nova-api"""
    name = "myapi"
    alias = "myapi"
    
    def get_resources(self):
        resources = [extensions.ResourceExtension('myapi',
                     Controller(),
                     collection_actions = {
                     'is_ok':'GET',
                     })]
        return resources

