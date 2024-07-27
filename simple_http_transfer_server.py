import http.server
import socketserver
import cgi
import os
import socket
import argparse

UPLOAD_DIRECTORY = "uploads"

class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/upload':
            self.upload_file()
        else:
            self.send_error(404, "File not found")

    def upload_file(self):
        content_type, pdict = cgi.parse_header(self.headers['Content-Type'])
        if content_type == 'multipart/form-data':
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'})
            if 'file' in form:
                file_field = form['file']
                if file_field.filename:
                    filename = os.path.basename(file_field.filename)
                    with open(os.path.join(UPLOAD_DIRECTORY, filename), 'wb') as output_file:
                        output_file.write(file_field.file.read())
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'File uploaded successfully')
                else:
                    self.send_error(400, "No file uploaded")
            else:
                self.send_error(400, "No file field in form")
        else:
            self.send_error(400, "Invalid content type")

    def do_GET(self):
        if self.path == '/uploads' or self.path == '/uploads/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <body>
                    <form enctype="multipart/form-data" method="post" action="/upload">
                        <input type="file" name="file" />
                        <input type="submit" value="Upload" />
                    </form>
                </body>
                </html>
            """)
        else:
            super().do_GET()

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't need to be reachable
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def main():
    parser = argparse.ArgumentParser(description='Simple file upload server.')
    parser.add_argument('--port', type=int, default=8000, help='Port to listen on (default: 8000)')
    args = parser.parse_args()
    
    port = args.port

    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)

    with socketserver.TCPServer(("", port), SimpleHTTPRequestHandler) as httpd:
        local_ip = get_local_ip()
        print(f"Serving at http://{local_ip}:{port}")
        httpd.serve_forever()

if __name__ == "__main__":
    main()
