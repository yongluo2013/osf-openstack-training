'''
Created on 2014-11-1

@author: eluoyng
'''
import os  
import webob  
from webob import Request  
from webob import Response  
from paste.deploy import loadapp  
from wsgiref.simple_server import make_server  
# Filter  
class LogFilter():  
    def __init__(self, app):  
        self.app = app  
        pass  
    def __call__(self, environ, start_response):  
        print "filter:LogFilter is called."  
        return self.app(environ, start_response)  
    @classmethod  
    def factory(cls, global_conf, **kwargs):  
        print "in LogFilter.factory", global_conf, kwargs  
        return LogFilter  
    
class ShowVersion():  
    def __init__(self):  
        pass  
    def __call__(self, environ, start_response):  
        start_response("200 OK", [("Content-type", "text/plain")])  
        return ["Paste Deploy LAB: Version = 1.0.0", ]  
    @classmethod  
    def factory(cls, global_conf, **kwargs):  
        print "in ShowVersion.factory", global_conf, kwargs  
        return ShowVersion()  
    
class Calculator():  
    def __init__(self):  
        pass  
      
    def __call__(self, environ, start_response):  
        req = Request(environ)  
        res = Response()  
        res.status = "200 OK"  
        res.content_type = "text/plain"  
        # get operands  
        operator = req.GET.get("operator", None)  
        operand1 = req.GET.get("operand1", None)  
        operand2 = req.GET.get("operand2", None)  
        print req.GET  
        opnd1 = int(operand1)  
        opnd2 = int(operand2)  
        if operator == u'plus':  
            opnd1 = opnd1 + opnd2  
        elif operator == u'minus':  
            opnd1 = opnd1 - opnd2  
        elif operator == u'star':  
            opnd1 = opnd1 * opnd2  
        elif operator == u'slash':  
            opnd1 = opnd1 / opnd2  
        res.body = "%s /nRESULT= %d" % (str(req.GET) , opnd1)  
        return res(environ, start_response)  
    @classmethod  
    def factory(cls, global_conf, **kwargs):  
        print "in Calculator.factory", global_conf, kwargs  
        return Calculator() 
     
if __name__ == '__main__':  
    configfile = "pastedeploylab.ini"  
    appname = "pdl"  
    wsgi_app = loadapp("config:%s" % os.path.abspath(configfile), appname)  
    server = make_server('localhost', 8080, wsgi_app)  
    server.serve_forever()  
