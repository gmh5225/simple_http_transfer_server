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
            self.upload_files()
        else:
            self.send_error(404, "File not found")

    def upload_files(self):
        content_type, pdict = cgi.parse_header(self.headers['Content-Type'])
        if content_type == 'multipart/form-data':
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'})
            if 'file' in form:
                if isinstance(form['file'], list):
                    files = form['file']
                else:
                    files = [form['file']]
                
                for file_field in files:
                    if file_field.filename:
                        filepath = file_field.filename
                        # 创建文件夹
                        full_path = os.path.join(UPLOAD_DIRECTORY, filepath)
                        directory = os.path.dirname(full_path)
                        if not os.path.exists(directory):
                            os.makedirs(directory)
                        
                        with open(full_path, 'wb') as output_file:
                            while True:
                                chunk = file_field.file.read(8192)
                                if not chunk:
                                    break
                                output_file.write(chunk)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'Files uploaded successfully')
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
                    <h2>Upload Files</h2>
                    <form id="uploadForm" enctype="multipart/form-data" method="post" action="/upload">
                        <input type="file" name="file" id="fileInput" multiple />
                        <input type="submit" value="Upload" />
                    </form>
                    <progress id="progressBar" value="0" max="100"></progress>
                    <h2>Upload Folder</h2>
                    <form id="folderUploadForm" enctype="multipart/form-data" method="post" action="/upload">
                        <input type="file" id="folderInput" webkitdirectory multiple />
                        <input type="submit" value="Upload Folder" />
                    </form>
                    <progress id="folderProgressBar" value="0" max="100"></progress>
                    <script>
                        document.getElementById('uploadForm').onsubmit = function(event) {
                            event.preventDefault();
                            var formData = new FormData();
                            var fileInput = document.getElementById('fileInput');
                            var files = fileInput.files;
                            for (var i = 0; i < files.length; i++) {
                                formData.append('file', files[i]);
                            }
                            
                            var xhr = new XMLHttpRequest();
                            xhr.open('POST', '/upload', true);
                            
                            xhr.upload.onprogress = function(event) {
                                if (event.lengthComputable) {
                                    var percentComplete = (event.loaded / event.total) * 100;
                                    document.getElementById('progressBar').value = percentComplete;
                                }
                            };
                            
                            xhr.onload = function() {
                                if (xhr.status == 200) {
                                    alert('Files uploaded successfully');
                                    document.getElementById('progressBar').value = 0;
                                } else {
                                    alert('File upload failed');
                                }
                            };
                            
                            xhr.send(formData);
                        };

                        document.getElementById('folderUploadForm').onsubmit = function(event) {
                            event.preventDefault();
                            var formData = new FormData();
                            var folderInput = document.getElementById('folderInput');
                            var files = folderInput.files;
                            for (var i = 0; i < files.length; i++) {
                                formData.append('file', files[i]);
                            }
                            
                            var xhr = new XMLHttpRequest();
                            xhr.open('POST', '/upload', true);
                            
                            xhr.upload.onprogress = function(event) {
                                if (event.lengthComputable) {
                                    var percentComplete = (event.loaded / event.total) * 100;
                                    document.getElementById('folderProgressBar').value = percentComplete;
                                }
                            };
                            
                            xhr.onload = function() {
                                if (xhr.status == 200) {
                                    alert('Folder uploaded successfully');
                                    document.getElementById('folderProgressBar').value = 0;
                                } else {
                                    alert('Folder upload failed');
                                }
                            };
                            
                            xhr.send(formData);
                        };
                    </script>
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
