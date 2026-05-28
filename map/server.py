import http.server
import socketserver
import os
import threading
import json

if __name__ == "__main__":
    import map
else:
    import map.map as map

# Configuration
PORT = 8080
DIRECTORY = "."

current_status = "Checking images..."

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
            self.wfile.write(json.dumps({"status": current_status}).encode())
        else:
            # Let the browser cache the map tiles to prevent lag/reloading!
            super().do_GET()

def update_status(msg):
    global current_status
    current_status = msg

def background_download():
    global current_status
    print("Checking for missing map tiles...")
    update_status("Checking for missing map tiles...")
    
    map.download_all_tiles("tiles/minecraft_overworld/", status_callback=update_status)
    
    current_status = "idle"
    print("All downloads complete! Web map is fully ready.")

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def start_server():
    ThreadedTCPServer.allow_reuse_address = True
    with ThreadedTCPServer(("", PORT), MapHTTPRequestHandler) as httpd:
        print(f"\nServer Online")
        print(f"http://localhost:{PORT}")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping server...")
            httpd.server_close()

if __name__ == "__main__":
    # Start downloading in the background
    threading.Thread(target=background_download, daemon=True).start()
    start_server()