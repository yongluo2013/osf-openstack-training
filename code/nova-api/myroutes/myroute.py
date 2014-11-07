'''' 
Created on 2013-6-1 
 
@author: spch2008 
'''  
  
from wsgiref.simple_server import make_server  
  
import routes.middleware  
import webob.dec  
import webob.exc  
  
class Controller:  
    @webob.dec.wsgify  
    def __call__(self, req):  
        return webob.Response("Hello World!")  
  
  
   
class Router(object):  
    def __init__(self):  
        self._mapper = routes.Mapper()  
        self._mapper.connect('/hello',
                        controller=Controller(),
                        action='index',
                        conditions={'method': ['GET']})    
          
        self._router = routes.middleware.RoutesMiddleware(self._dispatch, self._mapper)  
 
    @webob.dec.wsgify  
    def __call__(self, req):  
          
        return self._router  
 
    @staticmethod  
    @webob.dec.wsgify  
    def _dispatch(req):  
        match = req.environ['wsgiorg.routing_args'][1]  
                  
        if not match:  
            return webob.exc.HTTPNotFound()  
          
        app = match['controller']    
        return app  
          
        
  
app = Router()  
httpd = make_server('localhost', 8282, app)    
httpd.serve_forever()   
