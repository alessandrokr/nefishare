# 🚀 NeFiShare

**NeFiShare** is a lightweight desktop file-sharing tool that allows you to share files in your **local network** via **HTTP** using simple **drag & drop** — no cloud, no accounts, no installation required on the receiving device.

Perfect for quickly transferring files from your PC to **smartphones, tablets, or other computers** on the same network.

---

## ✨ Features

- 📂 **Drag & Drop** – simply drop files into the window
- 🌐 **Local HTTP sharing** – accessible from any web browser
- ⛶  **QR-Code** - scan a qr code on your phone for fast access
- 📱 **Mobile-friendly** – works on iOS & Android
- ⚡ **Fast & simple** – no pairing, no login
- 🖥️ **Cross-platform** – Windows, macOS, Linux
- 🔒 **Offline & local** – files never leave your network

---

## 🧠 How It Works

1. Start NeFiShare
2. Drag & drop files into the window
3. NeFiShare automatically starts a local HTTP server
4. Open the displayed URL (e.g. `http://192.168.1.42:8000`)  
   on any device in the same network to download the files

Optionally, the URL can be shared via **QR code**.

---

## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **GUI:** PySide6 (Qt)
- **HTTP Server:** FastAPI
- **Server:** Uvicorn
- **Frontend:** HTML / CSS (minimal)

---

## 📦 Installation (Development)

### Requirements
- Python 3.10 or higher
- pip

### Clone the repository
```bash
git clone https://github.com/yourusername/NeFiShare.git
cd NeFiShare
