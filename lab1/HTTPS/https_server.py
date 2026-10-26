from http.server import *
from urllib.parse import urlparse, parse_qs
import json
import ssl
import socketserver
import secrets
import threading

class RequestHandler(BaseHTTPRequestHandler):
    users = dict()

    def do_GET(self):

        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            with open('index.html', 'rb') as file:
                html_content = file.read()

            self.wfile.write(html_content)
            return
        
        elif self.path == '/me':
            cookie = self.headers.get('Cookie')

            if cookie is not None:
                get_session_id = cookie.split(';')[0].split('=')[1]
                print('session id received', get_session_id)

                if get_session_id in RequestHandler.users:
                    body = {'user': RequestHandler.users[get_session_id]}

                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()

                    self.wfile.write(json.dumps(body).encode('utf-8'))
                    return

            self.send_response(401)
            self.end_headers()
            return


        self.send_response(404)
        self.end_headers()
        return

    def do_POST(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/login':

            content_length = self.headers.get('Content-Length')
            if content_length is not None:
                post_body = self.rfile.read(int(content_length)).decode()
                print('post body:', post_body)
            else:
                self.send_response(400)
                self.end_headers()
                return

            try:
                py_dict = json.loads(post_body)
            except json.JSONDecodeError:
                self.send_response(400)
                self.end_headers()
                return
            
            username = py_dict.get('user')
            password = py_dict.get('password')

            if username is not None and password == 'netsec':
                # generate a secret session_id cookie
                session_id = secrets.token_hex(16)
                #set the cookie
                cookie = f'session_id={session_id}; Secure; HttpOnly'

                #save the cookie in the dictionary
                RequestHandler.users[session_id] = username

                self.send_response(200)
                self.send_header('Set-Cookie', cookie)
                self.end_headers()
                return
            else:
                self.send_response(401)
                self.end_headers()
                return
        
        self.send_response(404)
        self.end_headers()
        return

class ClientAuthenticator(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/whoami':
            certificate_dictionary = self.connection.getpeercert()
            # print(certificate_dictionary)
            subject = certificate_dictionary.get('subject')
            print(subject)

            element = subject[0]
            while(element[0] != 'commonName'):
                element = element[0]

            # print(element)
            common_name = element[1]
            # print(common_name)

            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()

            self.wfile.write(common_name.encode('utf-8'))
            return


        self.send_response(404)
        self.end_headers()
        return


def main():
    # Set the server address and port
    server_address = ('10.8.0.2', 8443) #application level server
    server2_address = ('10.8.0.2', 8444) #transport level server

    cert_path = '/home/alba-pellegrini/UNI/NetSec/lab1/HTTPS/cert.pem'
    key_path = '/home/alba-pellegrini/UNI/NetSec/lab1/HTTPS/key.pem'

    #SERVER
    #SSL
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=cert_path, keyfile=key_path)

    HTTPServer.allow_reuse_address = True
    # Create an instance of the HTTP server
    httpd = HTTPServer(server_address, RequestHandler)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)



    #SERVER2
    context2 = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context2.load_cert_chain(certfile=cert_path, keyfile=key_path)

    HTTPServer.allow_reuse_address = True
    httpd2 = HTTPServer(server2_address, ClientAuthenticator)
    context2.load_verify_locations("ca.crt")
    context2.verify_mode = ssl.CERT_REQUIRED
    httpd2.socket = context2.wrap_socket(httpd2.socket, server_side=True)

    t1 = threading.Thread(target=httpd.serve_forever)
    t2 = threading.Thread(target=httpd2.serve_forever)

    #threads need to be started
    t1.start()
    t2.start()


if __name__ == '__main__':
    main()