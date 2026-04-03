from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/versions"):
            response = {
                "versions": {
                    "default": "http://localhost:8000/index.html",
                    "dyslexia": "http://localhost:8000/index_dyslexia.html",
                    "captioned": "http://localhost:8000/index_captioned.html"
                }
            }

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

server = HTTPServer(("localhost", 5000), Handler)
print("Server running on http://localhost:5000")
server.serve_forever()