#!/usr/bin/python3
from http.server import BaseHTTPRequestHandler, HTTPServer

class githubHandler(BaseHTTPRequestHandler):
    def make_url(self):
        self.target_url = "http://www.github.com"
        if self.path != '/':
            self.target_url += self.path
            
    def get_page(self):
        import urllib.request
        req = urllib.request.Request(self.target_url)
        self.resp = urllib.request.urlopen(req)
        
        
    def do_GET(self):
        self.make_url(); self.get_page()
        self.send_response(self.resp.getcode())
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(self.resp.read())
        
try:
    server = HTTPServer(('0.0.0.0', 80), githubHandler)
    server.serve_forever()
except KeyboardInterrupt:
    print('^C received, shutting down the server')
    server.socket.close()