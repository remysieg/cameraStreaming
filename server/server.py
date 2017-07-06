#!/usr/bin/python3

# to open server: url -> localhost:8888/index.py
# for raspi -> 192.168.0.XX:8888/index.py

import http.server
import signal
import sys

# "Proper" way to exit the server (press Ctrl-C)
def signal_handler(signal, frame):
        print('Exit server')
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

# Server parameters
PORT = 8888
server_address = ("", PORT)

server = http.server.HTTPServer
handler = http.server.CGIHTTPRequestHandler
#handler.cgi_directories = ["/"] # for windows
handler.cgi_directories = ["/home/pi/hopiro"] # for raspi
print("Activ server on port :", PORT)

httpd = server(server_address, handler)
httpd.serve_forever()
