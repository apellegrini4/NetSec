from http.server import *
from urllib.parse import urlparse, parse_qs
import json

class RequestHandler(BaseHTTPRequestHandler):    
    latest_token = ''

    def do_GET(self):

        parsed_path = urlparse(self.path)
        # print('path parsato:', parsed_path)

        if self.path == '/':
            self.send_response(200)
            self.end_headers()
            return
        elif self.path == '/claim':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(RequestHandler.latest_token.encode('utf-8'))
            return

        self.send_response(404)
        self.end_headers()

        
    def do_POST(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/claim':
            content_length = self.headers.get('Content-Length')

            if content_length is not None:
                RequestHandler.latest_token = self.rfile.read(int(content_length)).decode()
                #print('post body:', post_body)
                self.send_response(200)
                self.end_headers()
                return
            else:
                self.send_response(400)
                self.end_headers()
                return


        self.send_response(404)
        self.end_headers()


        

def main():
    # Set the server address and port
    server_address = ('10.8.0.8', 8080)

    # Create an instance of the HTTP server
    httpd = HTTPServer(server_address, RequestHandler)

    # Start the server
    print('Starting server...')
    httpd.serve_forever()

if __name__ == '__main__':
    main()







#COMMANDS
# sudo systemctl start tor
# sudo systemctl stop tor
# systemctl status tor

#TOR SETUP
#HiddenServiceDir /var/lib/tor/hidden_service/
## Format: HiddenServicePort <onion_port> <local_address>:<local_port>
#HiddenServicePort 80 10.8.0.8:8080


#to RELOAD TOR
#sudo systemctl restart tor

#PRINT the onion address is in
#sudo cat /var/lib/tor/hidden_service/hostname

#cxdyaqdkhhy7y5bpyifwfx243vsagg74sqrhv5hkdhmp3g6cbtjdpryd.onion