from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import datetime
import urllib.parse
import cgi

UPLOAD_DIRECTORY = "uploads"

class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        with open("server.log", "a") as log_file:
            log_file.write("%s - - [%s] %s\n" % (self.client_address[0], self.log_date_time_string(), format % args))

    def list_uploads(self):
        files = os.listdir(UPLOAD_DIRECTORY)
        file_list_html = "<ul>"
        for file in files:
            file_list_html += f"<li><a href='/uploads/{file}'>{file}</a></li>"
        file_list_html += "</ul>"
        return file_list_html

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)
        self.log_message("GET request for %s with query parameters %s", parsed_path.path, query_params)
        
        if parsed_path.path == "/":
            uploads_list = self.list_uploads()
            content = f"""
                <html>
                    <body>
                        <h1>Welcome to the Home Page!</h1>
                        <p>Current date and time: {datetime.datetime.now()}</p>
                        <h2>Upload a File</h2>
                        <form enctype="multipart/form-data" method="post" action="/upload">
                            <input type="file" name="file"><br>
                            <input type="submit" value="Upload">
                        </form>
                        <h2>Uploaded Files</h2>
                        {uploads_list}
                    </body>
                </html>
            """
            self.send_response(200)
        elif parsed_path.path.startswith("/uploads/"):
            try:
                file_path = parsed_path.path[1:]  # Remove leading slash
                with open(file_path, 'rb') as file:
                    content = file.read()
                self.send_response(200)
                self.send_header('Content-type', 'application/octet-stream')
                self.send_header('Content-Disposition', f'attachment; filename="{os.path.basename(file_path)}"')
                self.end_headers()
                self.wfile.write(content)
                return
            except Exception as e:
                print(e)
                content = f"<html><body><h1>404 Not Found</h1><p>The requested URL {parsed_path.path} was not found on this server.</p></body></html>"
                self.send_response(404)
        elif parsed_path.path == "/greet" and 'name' in query_params:
            name = query_params['name'][0]
            content = f"<html><body><h1>Hello, {name}!</h1></body></html>"
            self.send_response(200)
        else:
            content = f"<html><body><h1>404 Not Found</h1><p>The requested URL {parsed_path.path} was not found on this server.</p></body></html>"
            self.send_response(404)

        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))

    def do_POST(self):
        if self.path == "/upload":
            content_type = self.headers['Content-Type']
            if not content_type.startswith('multipart/form-data'):
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Only multipart/form-data content is supported.")
                return

            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'})
            if 'file' not in form:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"No file field in form.")
                return

            file_item = form['file']
            if file_item.filename:
                filename = os.path.basename(file_item.filename)
                filepath = os.path.join(UPLOAD_DIRECTORY, filename)
                with open(filepath, 'wb') as output_file:
                    output_file.write(file_item.file.read())
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f"<html><body><h1>File {filename} uploaded successfully.</h1></body></html>".encode('utf-8'))
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"File upload failed.")

def run(server_class=HTTPServer, handler_class=MyHTTPRequestHandler, port=8000):
    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)
    
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
