'''
Created on 2014-11-1

@author: eluoyng
'''
import wsgi

class ControllerTest(object):
    def __init__(self):
        print "ControllerTest!!!!"
    def test(self, req):
          print "req", req
          return {
            'name': "test",
            'properties': "test"
        }

class MyControllerTest(object):
    def __init__(self):
        print "MyControllerTest!!!!"
        
    def my_test(self, req):
          print "req", req
          return {
            'name': "my_test",
            'properties': "my_test"
        }

class MyRouterApp(wsgi.Router):
      '''
      app
      '''
      def __init__(self, mapper):
          controller = ControllerTest()
          mapper.connect('/test',
                       controller=wsgi.Resource(controller),
                       action='test',
                       conditions={'method': ['GET']})

          mapper.connect('/mytest',
                       controller=wsgi.Resource(MyControllerTest()),
                       action='my_test',
                       conditions={'method': ['GET']})   
                 
          super(MyRouterApp, self).__init__(mapper)
          
