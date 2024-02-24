import socket
import ssl
import enum
import sys


class ResourceInterface:
    def read(self):
        pass
        # raise AttributeError("read function must be implemented")
    def write(self):
        pass
        # raise AttributeError("write function must be implemented")


@enum.unique
class Scheme(enum.Enum):
    HTTP = "http",
    HTTPS = "https"
    FILE = "file"
    DATA = "data"

class URL:
    def __init__(self, url):
        if "://" in url:
            self.scheme, url = url.split("://", 1)
            assert self.scheme in [Scheme.HTTP.value, Scheme.HTTPS.value, Scheme.FILE.value]
            if self.scheme in [Scheme.HTTP.value, Scheme.HTTPS.value]:
                if "/" not in url:
                    url = url + "/"
                self.host, url = url.split("/", 1)
                self.path = "/" + url

                # parse port
                if self.scheme == "http":
                    self.port = 80
                elif self.scheme == "https":
                    self.port = 443
                if ":" in self.host:
                    self.host, port = self.host.split(":", 1)
                    self.port = int(port)
            elif self.scheme == Scheme.FILE.value:
                self.path = url
        elif ":" in url:
            self.scheme, url = url.split(":", 1)
            if self.scheme == Scheme.DATA.value:
                def parse_data(text):
                    """
                    :param text: 不要附带`data:`，合法例子`text/html,Hello world!`
                    :return:
                    """
                    res_type, content = text.split(",", 1)
                    assert res_type in ["text/html"]
                    return content
                self.request = lambda: parse_data(url)


    def request(self, method="GET"):
        if self.scheme == Scheme.FILE.value:
            with open(f"{self.path}", mode="rb") as f:
                return f.read()
        elif self.scheme in [Scheme.HTTP.value, Scheme.HTTPS.value]:
            s = socket.socket(
                family=socket.AF_INET,
                type=socket.SOCK_STREAM,
                proto=socket.IPPROTO_TCP,
            )
            s.connect((self.host, self.port))
            if self.scheme == "https":
                ctx = ssl.create_default_context()
                s = ctx.wrap_socket(s, server_hostname=self.host)
            if method == "GET":
                s.send(((f"GET {self.path} HTTP/1.1\r\n" +
                         f"Host: {self.host}\r\n" +
                         f"Connection:close\r\n" +
                         f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246\r\n" +
                         "\r\n"
                         ).encode("utf8")))
            response = s.makefile("r", encoding="utf8", newline="\r\n")
            # parse the response
            statusline = response.readline()
            version, statue, explanation = statusline.split(" ", 2)

            response_headers = {}
            while True:
                line = response.readline()
                if line == "\r\n": break
                header, value = line.split(":", 1)
                response_headers[header.casefold()] = value.strip()
            # 确保我们试图访问的数据并非以不寻常的方式发送
            assert "transfer-encoding" not in response_headers
            assert "content-encoding" not in response_headers

            body = response.read()
            s.close()

            return body
def lex(body):
    res = ""
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            res += c
    return res

def load(url):
    body = url.request()
    print(body)
    print("-" * 40)


if __name__ == "__main__":
    '''import sys
    load(URL(sys.argv[1]))'''

    # http/s
    load(URL("https://browser.engineering/examples/example1-simple.html"))
    # data
    load(URL("data:text/html,Hello world!"))
    # file
    load(URL("file://C:/Temp/test.html"))