from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from webscraper import db_file
import sqlite3

port = 8000
hostname = 'localhost'

class HTTPRequestHandler(SimpleHTTPRequestHandler):

  def do_GET(self) -> None:
    self.send_response(200)
    with open(db_file, 'rb') as file_handle:
      db_data = file_handle.read()
    self.log_message(f'%d bytes.', len(db_data))
    self.send_header('Content-Disposition', f'attachment; filename={db_file}')
    self.send_header('Content-Type', 'application/octet-stream')
    self.send_header('Content-Length', f'{len(db_data)}')
    self.end_headers()
    self.wfile.write(db_data)


handler = HTTPRequestHandler

server = ThreadingHTTPServer((hostname, port), handler)
print(f'Web server started at http://{hostname}:{port}/')

try:
  server.serve_forever()
except KeyboardInterrupt:
  pass
server.server_close()
print("Server Stopped.")