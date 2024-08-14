import http.server
import socketserver

PORT = 8080
DIRECTORY = "C:\\Users\\Desktop\\Desktop\\lukilme\\personal-projects\\chess-logger\\src\\data\\template\\"  # Nome da pasta onde estão os arquivos HTML

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        print(args)
        print(kwargs)
        super().__init__(*args, directory=DIRECTORY, **kwargs)

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Servidor rodando na porta {PORT}")
    httpd.serve_forever()