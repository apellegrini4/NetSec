from http.server import *
from urllib.parse import urlparse, parse_qs
import json

class RequestHandler(BaseHTTPRequestHandler):
    notes = {}
    note_id = 0

    def unsupported_method(self):
        if self.path.startswith('/notes'):
            self.send_response(405)
            self.end_headers()
            return

    def do_GET(self):

        parsed_path = urlparse(self.path)
        # print('path parsato:', parsed_path)

        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            with open('index.html', 'rb') as file:
                html_content = file.read()

            self.wfile.write(html_content)
            return

        if parsed_path.path == '/echo':
            dictionary = parse_qs(parsed_path.query)
            print('dizionario', dictionary)

            if(len(dictionary) == 1 and dictionary.get('msg')):
                text = dictionary.get('msg')[0]
                # print('text', text)
                body = json.dumps({'msg': text}).encode('utf-8')
                # print('body in bytes', body)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()

                self.wfile.write(body)
                return

        if self.path.startswith('/notes/'):
            request_id = self.path.split('/notes/')[1]

            try:
                request_id = int(request_id)
            except ValueError:
                # the id is not numeric
                self.send_response(404)
                self.end_headers()
                return

            request_text = RequestHandler.notes.get(request_id)

            # if the note is missing
            if request_text is None:
                self.send_response(404)
                self.end_headers()
                return

            body = json.dumps({'id': request_id, 'text': request_text}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_response(404)
        self.end_headers()
        return

    def do_POST(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/notes':
            # content type different than application/json
            if self.headers.get('Content-type') != 'application/json':
                self.send_response(415)
                self.end_headers()
                return

            content_length = self.headers.get('Content-Length')
            if content_length is not None:
                post_body = self.rfile.read(int(content_length)).decode()
                print('post body:', post_body)
            else:
                self.send_response(400)
                self.end_headers()
                return

            # print('body', post_body)
            # print('python dictionary', json.loads(post_body))

            try:
                py_dict = json.loads(post_body)
            except json.JSONDecodeError:
                self.send_response(400)
                self.end_headers()
                return

            # missing note
            text = py_dict.get('text')
            if not(text):
                self.send_response(400)
                self.end_headers()
                return

            if not(isinstance(text, str)):
                self.send_response(400)
                self.end_headers()
                return

            RequestHandler.note_id += 1
            RequestHandler.notes[RequestHandler.note_id] = text
            
            body = json.dumps({'id': RequestHandler.note_id}).encode('utf-8')
            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(body)


    def do_DELETE(self):

        if self.path.startswith('/notes/'):
            request_id = self.path.split('/notes/')[1]

            try:
                request_id = int(request_id)
            except ValueError:
                # the id is not numeric
                self.send_response(404)
                self.end_headers()
                return

            if request_id in RequestHandler.notes:
                del RequestHandler.notes[request_id]
                self.send_response(204)
                self.end_headers()
                return
            else:
                self.send_response(404)
                self.end_headers()
                return


    def do_PUT(self):
        self.unsupported_method()

    def do_PATCH(self):
        self.unsupported_method()

    def do_HEAD(self):
        self.unsupported_method()

    def do_OPTIONS(self):
        self.unsupported_method()

        

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