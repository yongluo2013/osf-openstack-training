'''
Created on 2014-11-1

@author: eluoyng
'''
from wsgiref.simple_server import make_server

URL_PATTERNS = (
    ('hi/', 'say_hi'),
    ('hello/', 'say_hello'),
    )

class Dispatcher(object):

    def _match(self, path):
        path = path.split('/')[1]
        for url, app in URL_PATTERNS:
            if path in url:
                return app

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '/')
        app = self._match(path)
        if app :
            app = globals()[app]
            return app(environ, start_response)
        else:
            start_response("404 NOT FOUND", [('Content-type', 'text/plain')])
            return ["Page dose not exists!"]

def say_hi(environ, start_response):
    start_response("200 OK", [('Content-type', 'text/html')])
    return ["wsgiref say hi to you!"]

def say_hello(environ, start_response):
    start_response("200 OK", [('Content-type', 'text/html')])
    return ["wsgiref say hello to you!"]


if __name__ == '__main__':
    app = Dispatcher()
    httpd = make_server('', 8000, app)
    print "Serving on port 8000..."
    httpd.serve_forever()