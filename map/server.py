import http.server
import socketserver
import os
import threading
import json
import map # Import your map formatting script!

# Configuration
PORT = 8080
DIRECTORY = "."

is_downloading = True

class MapHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    # Add custom API to check if downloading
    def do_GET(self):
        if self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            self.end_headers()
            self.wfile.write(json.dumps({"downloading": is_downloading}).encode())
        else:
            # Let the browser cache the map tiles to prevent lag/reloading!
            super().do_GET()

def background_download():
    global is_downloading
    print("Checking for missing map tiles...")
    map.download_all_tiles("tiles/minecraft_overworld/")
    is_downloading = False
    print("All downloads complete! Web map is fully ready.")

# Start downloading in the background
threading.Thread(target=background_download, daemon=True).start()

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

ThreadedTCPServer.allow_reuse_address = True
with ThreadedTCPServer(("", PORT), MapHTTPRequestHandler) as httpd:
    print(f"\nServer Online")
    print(f"http://localhost:{PORT}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()