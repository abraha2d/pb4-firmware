from _thread import start_new_thread, allocate_lock
from errno import EAGAIN
from socket import AF_INET, SO_REUSEADDR, SOCK_STREAM, SOL_SOCKET, getaddrinfo, socket
# from sys import print_exception

from .utils import url_decode
from .views import file_view


class HTTPServer:
    def __init__(self, ip_addr, urlconf, bind_addr=getaddrinfo("0.0.0.0", 80, AF_INET, SOCK_STREAM)[0][-1]):
        self.ip_addr = ip_addr
        self.urlconf = urlconf
        self.bind_addr = bind_addr
        self.run_lock = allocate_lock()
        self.should_run = False
        self.num_threads = 0

    def start(self):
        self.should_run = True
        start_new_thread(self.run, ())

    def run(self):
        with self.run_lock:
            try:
                sock = socket(AF_INET, SOCK_STREAM)
                sock.setblocking(False)
                sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
                sock.bind(self.bind_addr)
                sock.listen(5)

                while self.should_run:
                    if self.num_threads >= 4:
                        continue

                    try:
                        conn, addr = sock.accept()
                    except OSError as e:
                        if e.errno == EAGAIN:
                            continue
                        raise

                    start_new_thread(self.process, (conn,))
            finally:
                sock.close()

    def stop(self):
        self.should_run = False
        while self.run_lock.locked():
            pass

    def process(self, conn):
        self.num_threads += 1

        request = bytearray()
        while True:
            try:
                chunk = conn.recv(4096)
            except OSError:
                return
            if chunk == b"":
                break
            request += chunk
            if b"\r\n\r\n" in request:
                break
        request = request.decode("ISO-8859-1")

        try:
            status, headers, data = self.get_response(request)
        except Exception as e:
            # get_response includes a try/except to catch view exceptions (status 500)
            # If it throws an exception, that means the request is malformed (status 400)
            status, headers, data = 400, {}, f"{type(e)}: {str(e)}"

        headers = "".join(f"{k}: {v}\r\n" for k, v in headers.items())
        response = f"HTTP/1.1 {status} \r\n{headers}\r\n"

        if type(data) != bytes:
            if type(data) != str:
                data = str(data)
            data = data.encode("ISO-8859-1")

        conn.send(response.encode() + data)
        conn.close()

        self.num_threads -= 1

    def get_response(self, request):
        request_lines = request.split("\r\n")

        method, uri, _ = request_lines[0].split(" ")
        if method != "GET":
            return 501, {}, ""

        headers = dict(line.split(": ", 1) for line in request_lines[1:] if ": " in line)
        if headers.get("Host", self.ip_addr) != self.ip_addr:
            return 303, {"Location": f"http://{self.ip_addr}"}, ""

        path, query = uri.split("?", 1) if "?" in uri else (uri, "")
        query_dict = dict(
            url_decode(qp) if "=" in qp else (url_decode(qp), True)
            for qp in query.split("&") if qp != ""
        )

        path = path.rstrip("/")
        if path == "":
            path = "/"

        view = self.urlconf.get(path, file_view)

        try:
            return view(path, query_dict, headers)
        except Exception as e:
            # print_exception(e)
            return 500, {}, f"{type(e)}: {str(e)}"
