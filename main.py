import sys
import os
import socket
import threading
import uuid
import asyncio

from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from uvicorn import Config, Server
import qrcode

# ---------------- CONFIG ----------------
PORT = 8000
QR_FILE = "qrcode.png"
# ----------------------------------------

# In-memory file registry: id -> absolute path
shared_files = {}


# Fix for PyInstaller --windowed + uvicorn
if getattr(sys, 'frozen', False):
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

# ---------------- Networking ----------------
def get_local_ip():
    """Return the local IP of the PC."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

# ---------------- FastAPI server ----------------
app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def index():
    links = "".join(
        f'<li><a href="/download/{fid}">{os.path.basename(path)}</a></li>'
        for fid, path in shared_files.items()
    )
    return f"<html><body><h1>📁 NeFiShare</h1><ul>{links}</ul></body></html>"

@app.get("/download/{file_id}")
def download(file_id: str):
    path = shared_files.get(file_id)
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, filename=os.path.basename(path))

def start_server():
    """Start uvicorn in a daemon thread."""
    config = Config(app, host="0.0.0.0", port=PORT, log_level="warning", loop="asyncio")
    server = Server(config)
    asyncio.run(server.serve())

# ---------------- GUI ----------------
class DropWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NeFiShare")
        self.setAcceptDrops(True)
        self.setMinimumSize(400, 500)

        self.label = QLabel("📂 Drag & Drop files here")
        self.label.setAlignment(Qt.AlignCenter)

        self.url_label = QLabel()
        self.url_label.setAlignment(Qt.AlignCenter)

        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.url_label)
        layout.addWidget(self.qr_label)
        self.setLayout(layout)

        self.init_network()

    def init_network(self):
        self.ip = get_local_ip()
        self.url = f"http://{self.ip}:{PORT}"
        self.url_label.setText(self.url)

        qr = qrcode.make(self.url)
        qr.save(QR_FILE)
        pixmap = QPixmap(QR_FILE)
        self.qr_label.setPixmap(pixmap.scaled(250, 250, Qt.KeepAspectRatio))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        added = 0
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isfile(path):
                file_id = str(uuid.uuid4())
                shared_files[file_id] = os.path.abspath(path)
                added += 1
        if added:
            self.label.setText(f"✅ {added} file(s) shared")

# ---------------- MAIN ----------------
if __name__ == "__main__":
    # Start FastAPI server in daemon thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Start GUI in main thread
    app = QApplication(sys.argv)
    window = DropWindow()
    window.show()
    sys.exit(app.exec())
