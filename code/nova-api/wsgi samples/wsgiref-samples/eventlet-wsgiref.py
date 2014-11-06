from eventlet import wsgi  
import eventlet  
  
def hello_world(env, start_response):  
    start_response('200 OK', [('Content-Type', 'text/plain')])  
    return ['Hello, World!\r\n']  
  
wsgi.server(eventlet.listen(('', 8090)), hello_world)  