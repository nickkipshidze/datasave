import os
import json
import datetime
import cloudflare
import http.server
import urllib.parse
import settings

STARTED = datetime.datetime.now()

class HTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)
    
    def log_message(self, format, *args):
        now = datetime.datetime.now().strftime("%I:%M:%S %p")
        print(f"* {now} - {self.client_address[0]} - \"{self.command} {self.path}\" {args[1]}")

    def quickres(self, status_code, headers, buffer=None):
        self.send_response(status_code)
        for keyword, value in headers.items():
            self.send_header(keyword, value)
        self.end_headers()
        if buffer:
            self.wfile.write(buffer)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/":
            self.quickres(
                status_code=200,
                headers={"Content-Type": "text/plain"},
                buffer="\n".join([
                    f"> Server running\n",
                    f"- Server Uptime: {datetime.datetime.now() - STARTED}",
                    f"- Cloudflare tunnel: {settings.CLOUDFLARE_TUNNEL}"
                ]).encode()
            )

        elif path == "/up":
            self.quickres(
                status_code=200,
                headers={"Content-Type": "text/html"},
                buffer=open("form.html", "rb").read()
            )

        elif path == "/down":
            if settings.ALLOW_DOWNLOAD == False:
                self.quickres(
                    status_code=403,
                    headers={"Content-Type": "text/plain"},
                    buffer="403 Forbidden".encode()
                )
                return

            if "f" not in query:
                self.quickres(
                    status_code=400,
                    headers={"Content-Type": "text/plain"},
                    buffer=b"No file specified"
                )
                return

            filename = os.path.basename(query["f"][0])
            filepath = os.path.join(settings.UPLOAD_DIR, filename)

            if not os.path.exists(filepath):
                self.quickres(
                    status_code=404,
                    headers={"Content-Type": "text/plain"},
                    buffer=b"File not found"
                )
                return

            self.quickres(
                status_code=200,
                headers={
                    "Content-Type": "text/plain",
                    "Content-Disposition": f"attachment; filename=\"{filename}\""
                }
            )

            with open(filepath, "rb") as f:
                while chunk := f.read(8192):
                    self.wfile.write(chunk)

        elif path == "/list":
            if settings.ALLOW_LISTING == False:
                self.quickres(
                    status_code=403,
                    headers={"Content-Type": "text/plain"},
                    buffer="403 Forbidden".encode()
                )
                return
        
            self.quickres(
                status_code=200,
                headers={"Content-Type": "application/json"},
                buffer=json.dumps(os.listdir(settings.UPLOAD_DIR)).encode()
            )

        else:
            self.quickres(
                status_code=404,
                headers={"Content-Type": "text/plain"},
                buffer="404 Not Found".encode()
            )

    # These can get messy huh?
    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/up":
            content_length = int(self.headers.get("Content-Length", 0))
            content_type = self.headers.get("Content-Type", "")

            if "multipart/form-data" not in content_type:
                self.quickres(400, {"Content-Type": "text/plain"}, b"Content-Type must be multipart/form-data")
                return

            boundary = content_type.split("boundary=")[1].encode()
            body = self.rfile.read(content_length)

            parts = body.split(b"--" + boundary)

            saved_files = []

            for part in parts:
                if b"Content-Disposition" not in part:
                    continue

                try:
                    header, file_data = part.split(b"\r\n\r\n", 1)
                except ValueError:
                    continue

                file_data = file_data.rstrip(b"\r\n--")
                header_str = header.decode(errors="ignore")

                if "filename=\"" not in header_str:
                    continue

                filename = header_str.split("filename=\"")[1].split("\"")[0]
                filename = os.path.basename(filename)
                filepath = os.path.join(settings.UPLOAD_DIR, filename)

                if os.path.exists(filepath):
                    print(f"* \"{filepath}\" already exists. Overwriting...")

                with open(filepath, "wb") as f:
                    f.write(file_data)

                print(f"* Saved \"{filepath}\" {os.stat(filepath).st_size} bytes")
                saved_files.append(filename)

            if not saved_files:
                self.quickres(400, {"Content-Type": "text/plain"},
                            b"No file found in request")
                return

            response = f"Uploaded {len(saved_files)} file(s):\n" + "\n".join(saved_files)

            self.quickres(
                200,
                {"Content-Type": "text/plain"},
                response.encode()
            )

        else:
            self.quickres(
                status_code=404,
                headers={"Content-Type": "text/plain"},
                buffer="404 Not Found".encode()
            )

def main():
    if settings.CLOUDFLARE_TUNNEL == True:
        print("* Starting cloudflare tunnel...")
        cf_proc, cf_addr = cloudflare.start(
            url=f"http://{settings.HOST}:{settings.PORT}/"
        )
        print(f"* Cloudflare tunnel started: {cf_addr}")
    else:
        print("* Skip starting cloudflare tunnel (local only)")

    httpd = http.server.HTTPServer(
        server_address=(settings.HOST, settings.PORT),
        RequestHandlerClass=HTTPRequestHandler
    )

    try:
        print(f"* HTTP server started: http://{settings.HOST}:{settings.PORT}/")
        httpd.serve_forever()
    except KeyboardInterrupt:
        cf_proc.kill()
        httpd.server_close()
        exit(0)

if __name__ == "__main__":
    main()
