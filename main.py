import cloudflare
import http.server

class HTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write("Server up and running!".encode())

def main():
    cf_proc, cf_addr = cloudflare.start()

    address = ("0.0.0.0", 16461)
    print(address, cf_addr)

    httpd = http.server.HTTPServer(
        server_address=address,
        RequestHandlerClass=HTTPRequestHandler
    )
    httpd.serve_forever()

if __name__ == "__main__":
    main()
