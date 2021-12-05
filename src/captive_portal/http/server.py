from io import StringIO
from sys import print_exception
from time import time_ns

from uasyncio import start_server

from .utils import url_decode
from .views import file_view


class HTTPServer:
    def __init__(self, ip_addr, urlconf):
        self.ip_addr = ip_addr
        self.urlconf = urlconf

    async def serve(self):
        server = await start_server(self.callback, '0.0.0.0', 80)
        await server.wait_closed()

    async def callback(self, reader, writer):
        request = bytearray()
        while True:
            chunk = await reader.read(4096)
            if len(chunk) == 0:
                break
            request.extend(chunk)
            if b"\r\n\r\n" in request:
                break
        request = request.decode("ISO-8859-1")
        request_lines = request.split("\r\n")

        try:
            status, headers, data = await self.get_response(request_lines)
        except Exception as e:
            # get_response includes a try/except to catch view exceptions (status 500)
            # If it throws an exception, that means the request is malformed (status 400)
            sio = StringIO()
            print_exception(e, sio)
            status, headers, data = 400, {}, f"400 Bad Request\r\n{sio.getvalue()}"

        print(f'[{time_ns() / 1000000000:14.3f}] "{request_lines[0]}" {status}')

        headers = "".join(f"{k}: {v}\r\n" for k, v in headers.items())
        response = f"HTTP/1.1 {status} \r\n{headers}\r\n"

        if type(data) != bytes:
            if type(data) != str:
                data = str(data)
            data = data.encode("ISO-8859-1")

        writer.write(response.encode("ISO-8859-1") + data)
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    async def get_response(self, request_lines):
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
            status, headers, data = await view(path, query_dict, headers)
            return status, headers, data
        except Exception as e:
            sio = StringIO()
            print_exception(e, sio)
            return 500, {}, f"500 Internal Server Error\r\n{sio.getvalue()}"
