import threading
import sys
import os

# Import main components
import api
from map import server as map_server

print("Starting Project Samaritan...")

def run_api_server():
    print("Starting Flask API Server on http://127.0.0.1:5000 ...")
    # Using use_reloader=False so it doesn't cause issues in a thread
    api.app.run(host="127.0.0.1", port=5000, use_reloader=False)

if __name__ == "__main__":
    print("Starting Central Server...")
    
    # Start the background map tile download thread
    download_thread = threading.Thread(target=map_server.background_download, daemon=True)
    download_thread.start()

    # The old map viewer on :8080 isn't started any more. The API serves the map and tiles itself,
    # and the viewer shared the whole project folder (database included) with the network.
    # Run map/server.py directly if you still want it.

    # Start the Flask API server in the main thread
    try:
        run_api_server()
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        sys.exit(0)

