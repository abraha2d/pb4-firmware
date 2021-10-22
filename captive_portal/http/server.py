print("===IMPORTING captive_portal/http/server.py===")
from socket import socket, SOL_SOCKET, SO_REUSEADDR

from .utils import url_decode
from .views import template


class HTTPServer:
    def __init__(self, ip_addr, urlconf, bind_addr=("0.0.0.0", 80)):
        print("===INITIALIZING HTTP server===")
        self.ip_addr = ip_addr
        self.urlconf = urlconf

        self.socket = socket()
        self.socket.setblocking(False)
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.socket.bind(bind_addr)
        self.socket.listen(1)

    def process(self):
        try:
            conn, addr = self.socket.accept()
        except OSError:
            return

        print()
        print(f"===PROCESSING HTTP request from {addr}===")

        request = bytearray()
        while True:
            try:
                chunk = conn.recv(512)
                if chunk == b"":
                    break
                request.extend(chunk)
                if b"\r\n\r\n" in request:
                    break
            except OSError:
                print("===DONE: aborted===")
                return
        request = request.decode("ISO-8859-1")

        print("=====DEBUG REQUEST=====")
        print(request)
        print("===END DEBUG REQUEST===")

        req_lines = request.split("\r\n")

        if " " not in req_lines[0]:
            print("===DONE: malformed===")
            return
        method, uri, version = req_lines[0].split(" ")
        uri, qs = uri.split("?") if "?" in uri else (uri, "")
        qps = dict(
            url_decode(qp) if "=" in qp else [url_decode(qp), True]
            for qp in qs.split("&") if qp != ""
        )

        headers = dict(line.split(": ", 1) for line in req_lines[1:] if ": " in line)

        try:
            status, out_headers, response = getattr(self, method)(uri, qps, headers)
        except Exception as e:
            status, out_headers, response = 500, {}, f"{type(e)}: {str(e)}"

        header_str = "".join(f"{k}: {v}\r\n" for k, v in out_headers.items())
        response_headers = f"HTTP/1.1 {status}\r\n{header_str}\r\n"

        print("=====DEBUG RESPONSE=====")
        print(response_headers)
        print("===END DEBUG RESPONSE===")

        if type(response) != bytes:
            if type(response) != str:
                response = str(response)
            response = response.encode("ISO-8859-1")

        conn.send(response_headers.encode() + response)
        conn.close()
        print(f"===DONE: status {status}===")

    def GET(self, uri, qps, headers):
        if headers.get("Host", self.ip_addr) != self.ip_addr:
            return 303, {"Location": f"http://{self.ip_addr}"}, ""

        uri = uri.rstrip("/")
        if uri == "":
            uri = "/"

        view = self.urlconf.get(uri, template)
        return view(uri, qps, headers)


# if __name__ == "__main__":
#     from urlconf import urlconf
#     http_server = HTTPServer(urlconf, ("0.0.0.0", 8080))
#     while True:
#         http_server.process()
