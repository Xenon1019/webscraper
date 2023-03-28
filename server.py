from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from webscraper import db_file

port = 8000
hostname = 'localhost'

class HTTPRequestHandler(SimpleHTTPRequestHandler):

  def do_GET(self) -> None:
    self.path = f'/{db_file}'
    super().do_GET()

handler = HTTPRequestHandler

server = ThreadingHTTPServer((hostname, port), handler)
print(f'Web server started at http://{hostname}:{port}/')

try:
  server.serve_forever()
except KeyboardInterrupt:
  pass
server.server_close()
print("Server Stopped.")