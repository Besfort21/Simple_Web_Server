from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import datetime
import urllib.parse

class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        with open("server.log", "a") as log_file:
            log_file.write("%s - - [%s] %s\n" % (self.client_address[0], self.log_date_time_string(), format % args))

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)
        self.log_message("GET request for %s with query parameters %s", parsed_path.path, query_params)
        
        if parsed_path.path == "/":
            now = datetime.datetime.now()
            content = f"<html><body><h1>Welcome to the Home Page!</h1><p>Current date and time: {now}</p></body></html>"
            self.send_response(200)
        elif parsed_path.path == "/greet" and 'name' in query_params:
            name = query_params['name'][0]
            content = f"<html><body><h1>Hello, {name}!</h1></body></html>"
            self.send_response(200)
        else:
            try:
                with open(parsed_path.path[1:], 'rb') as file:
                    content = file.read()
                self.send_response(200)
            except:
                content = f"<html><body><h1>404 Not Found</h1><p>The requested URL {parsed_path.path} was not found on this server.</p></body></html>"
                self.send_response(404)

        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(content if isinstance(content, bytes) else content.encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        parsed_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
        
        self.log_message("POST request received with data: %s", parsed_data)
        
        content = "<html><body><h1>POST Request Received</h1>"
        content += "<ul>"
        for key, value in parsed_data.items():
            content += f"<li>{key}: {value}</li>"
        content += "</ul></body></html>"

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))

def run(server_class=HTTPServer, handler_class=MyHTTPRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
