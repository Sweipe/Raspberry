# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import ssl
import secrets

def get_ssl_context(certfile, keyfile):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    #context.load_cert_chain(certfile, keyfile)
    context.set_ciphers("@SECLEVEL=1:ALL")
    return context

#hostName = "0.0.0.0"
hostName = 192.168.1.211
#hostName = "localhost"
#serverPort = 443
serverPort = 8000

class MyServer(BaseHTTPRequestHandler):
    #def log_message(self, format, *args):
        #pass
    
    def do_GET(self):
        #print(self.headers["Cookie"])
        if self.path == '/quit':
            raise KeyboardInterrupt('')
        if self.path == '/ignore':
            self.send_response(308)
            self.send_header('Location', 'http://192.168.1.1')
            self.end_headers()
        if self.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
            self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
            self.wfile.write(bytes("<body>", "utf-8"))
            self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
            self.wfile.write(bytes("</body></html>", "utf-8"))
                

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    
    print("Server started http://%s:%s" % (hostName, serverPort))

    context = get_ssl_context("certificate/myserver.crt", "certificate/myserver.key")
    
    #webServer.socket = context.wrap_socket(webServer.socket, server_side=True)

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")