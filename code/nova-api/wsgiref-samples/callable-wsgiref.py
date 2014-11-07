'''
Created on 2014-11-1

@author: eluoyng
'''

from wsgiref.simple_server import make_server

def simple_app(environ, start_response):
    '''
        wsgiref 需要定义一个callable 对象就可以用于APP 调用
    '''
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return [u"This is hello wsgi app".encode('utf8')]


if __name__ == '__main__':
    httpd = make_server('', 8000, simple_app)
    print "Serving on port 8000..."
    httpd.serve_forever()