from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from webscraper import db_file

port = 8000
hostname = 'localhost'

class HTTPRequestHandler(SimpleHTTPRequestHandler):

  def do_GET(self) -> None:
    if self.path == '/':
      self.send_response(200)
      self.send_header('Content-Type', 'application/octet-stream')
      self.send_header('Content-Disposition', f'attachement; filename="{db_file}"');
      self.end_headers()
      with open(db_file, 'rb') as db:
        self.wfile.write(db.read())
    else:
      self.do_GET()

handler = HTTPRequestHandler

server = ThreadingHTTPServer((hostname, port), handler)
print(f'Web server started at http://{hostname}:{port}/')

try:
  server.serve_forever()
except KeyboardInterrupt:
  pass
server.server_close()
print("Server Stopped.")