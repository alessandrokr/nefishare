import sys
import os
import socket
import threading
import uuid

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
import qrcode
import asyncio
from uvicorn import Config, Server


# ---------------- CONFIG ----------------
PORT = 8000
QR_FILE = "qrcode.png"
# ----------------------------------------


# In-memory file registry
shared_files = {}  # id -> absolute file path


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def start_server():
    app = FastAPI()

    # --- your routes here ---
    @app.get("/", response_class=HTMLResponse)
    def index():
        links = ""
        for file_id, path in shared_files.items():
            name = os.path.basename(path)
            links += f'<li><a href="/download/{file_id}">{name}</a></li>'
        return f"<html><body><h1>📁 NeFiShare</h1><ul>{links}</ul></body></html>"

    @app.get("/download/{file_id}")
    def download(file_id: str):
        if file_id not in shared_files:
            raise HTTPException(status_code=404)
        path = shared_files[file_id]
        if not os.path.exists(path):
            raise HTTPException(status_code=410)
        return FileResponse(path, filename=os.path.basename(path))

    # Use uvicorn.Server instead of uvicorn.run
    config = Config(app=app, host="0.0.0.0", port=PORT, log_level="warning", loop="asyncio")
    server = Server(config)

    asyncio.run(server.serve())


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


if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    app = QApplication(sys.argv)
    window = DropWindow()
    window.show()
    sys.exit(app.exec())
