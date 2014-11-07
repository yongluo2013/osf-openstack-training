'''
Created on 2014-11-1

@author: eluoyng
'''
from wsgiref.simple_server import make_server

class AppClass:

    def __call__(self,environ, start_response):
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return ["hello world!"]


if __name__ == '__main__':
    app = AppClass()
    httpd = make_server('', 8000, app)
    print "Serving on port 8000..."
    httpd.serve_forever()