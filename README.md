# linxRTC — Secure Real-Time Chat System

A high-performance, multi-client real-time messaging application featuring an end-to-end encrypted protocol layer built with Python sockets, CustomTkinter modern UI, and asymmetric/symmetric hybrid cryptography (RSA + AES-GCM).

---

## Architecture Overview

```text
  [ Client A: CustomTkinter GUI ]  <--- AES-GCM Encrypted Payload --->  [ Client B: CustomTkinter GUI ]
              |                                                                     |
       RSA Public Key                                                        RSA Public Key
          Exchange                                                              Exchange
              \                                                                 /
               \---> [ Central linxRTC Socket Server / Router ] <--------------/
                     - Packet Routing & Framing (struct)
                     - Session Lifecycle (Login, Ping/Pong, Exit)
                     - Group Key Distribution (Encrypted Broadcast)

```

### Core Technologies & Libraries

* **GUI Interface:** `customtkinter` / `tkinter` via custom theme engine (`src.themeClass.Theme`)
* **Cryptography:**
* **Asymmetric (RSA):** Key-pair generation, PKCS#1 v1.5 / OAEP padding, public key export/import via `cryptography.hazmat.primitives.asymmetric.rsa` and `serialization`
* **Symmetric (AES-GCM):** Authenticated encryption for zero-leakage peer/group communication via `cryptography.hazmat.primitives.ciphers.aead.AESGCM`


* **Transport & Protocol:** Low-level TCP sockets framed with Python `struct` and serialized via `json`
* **Concurrency:** `threading` for non-blocking packet ingestion, GUI dispatch, and background heartbeat keep-alives

---

## Protocol & Packet Engine

The communication protocol utilizes internal operational packet codes defined in `libs.middleware` and routed through `libs.route.routeR`:

| Opcode / Constant | Description |
| --- | --- |
| `TYPE_LOGIN` / `TYPE_LOGIN_OK` | Initial handshake, client identity authentication, and connection approval |
| `I_KEYS` | Initial public key advertisement on channel join |
| `SHARE_GROUP_KEY` / `RECV_GROUP_KEY` | Distribution and ingestion of session group keys encrypted with target peer public keys |
| `TYPE_GMSG` | AES-GCM encrypted group payload transit |
| `U_JOIN` | Broadcast notification when a new peer joins the network |
| `COUNT_CONN` | Dynamic sync of total connected active peers |
| `PONG` | Heartbeat keep-alive verification |
| `EXIT` / `EXIT_MSG` | Graceful peer teardown, socket closure, and key discard |

---

## Project Structure

```text
linxRTC/
├── src/
│   ├── themeClass.py          # CustomTkinter styling and UI theming
│   ├── client_ui.py           # Main chat interface and rendering
│   └── ...
├── libs/
│   ├── middleware.py          # Packet framing, protocol opcodes, network handlers
│   ├── route.py               # Inbound/outbound message dispatch router (routeR)
│   └── crypto_utils.py        # Key generation, AES-GCM and RSA wrappers
├── captures/                  # Shared storage / export directory (if applicable)
├── server.py                  # Multi-threaded socket relay server
├── client.py                  # Client entrypoint
├── requirements.txt           # Python package dependencies
└── README.md                  # Project documentation

```

---

## Installation & Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/linxRTC.git
cd linxRTC

```

### 2. Create and Activate a Virtual Environment

```bash
python3 -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows (Command Prompt)
# venv\Scripts\activate.bat

# Windows (PowerShell)
# .\venv\Scripts\Activate.ps1

```

### 3. Install System & Python Dependencies

#### Linux Systems (Ubuntu/Debian)

Ensure Tkinter system bindings are installed:

```bash
sudo apt update
sudo apt install -y python3-tk python3-dev

```

#### Python Packages

Install the required dependencies:

```bash
pip install --upgrade pip
pip install cryptography customtkinter

```


---

## Usage & Execution


###  Launch Client Node(s)

Open separate terminal instances for each chat participant:

```bash
# Terminal 1 - First Client
python3 chatapp.py

```

```bash
# Terminal 2 - Second Client
python3 chatapp.py

```

1. Enter your display handle and target server IP (e.g., `127.0.0.1` for local loopback or local LAN IP).
2. The client will initialize its local RSA keypair, transmit `I_KEYS` to the server, and negotiate `SHARE_GROUP_KEY` via `libs.middleware`.
3. All outgoing messages under `TYPE_GMSG` are signed, encrypted with AES-GCM, packed using `struct`, and dispatched through `routeR`.

---

## Security Pipeline

1. **Identity & Discovery:** When a client connects, an ephemeral RSA 2048/4096-bit keypair is generated. The public key is serialized via `cryptography.hazmat.primitives.serialization` and published via `I_KEYS`.
2. **Key Exchange:** Symmetric AES-GCM session keys (`peer_group_key`, `my_sender_key`) are encrypted using the recipient's RSA public key using OAEP padding (`hashes.SHA256`) and distributed via `SHARE_GROUP_KEY`.
3. **Payload Encryption:** Chat messages are converted to JSON, encrypted using `AESGCM` with a unique 96-bit nonce, packed with length headers via Python's `struct`, and relayed through the server.
4. **Zero-Knowledge Relay:** The relay server routes framed raw payloads (`TYPE_GMSG`) without access to private keys or decryption secrets.