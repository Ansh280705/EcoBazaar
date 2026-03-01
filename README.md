<div align="center">


# ⚡ Eco Bazzar

**Decentralized Peer-to-Peer Energy Trading on the Algorand Blockchain**

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/release/python-3120/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Algorand](https://img.shields.io/badge/Algorand-000000?style=for-the-badge&logo=algorand&logoColor=white)](#)
[![PostgreSQL](https://img.shields.io/badge/Neon_Postgres-00e599?style=for-the-badge&logo=postgresql&logoColor=white)](#)
[![Clerk](https://img.shields.io/badge/Clerk_Auth-6C47FF?style=for-the-badge&logo=clerk&logoColor=white)](#)
[![License: MIT](https://img.shields.io/badge/MIT-yellow?style=for-the-badge&logo=opensourceinitiative&logoColor=white)](https://opensource.org/licenses/MIT)

Eco Bazzar empowers individuals and businesses to **harness, track, and trade** surplus renewable energy directly with peers — secured by blockchain smart contracts. No middlemen. No hidden fees. Just clean energy, fairly traded.

</div>

---

## 📖 Table of Contents

- [Problem Statement](#-problem-statement)
- [Solution Overview](#-solution-overview)
- [System Architecture](#-system-architecture)
- [Core Features](#-core-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation & Setup](#-installation--setup)
- [API Flow](#-api-flow)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🔍 Problem Statement

The traditional energy grid is **centralized, inefficient, and monopolized**. Small-scale renewable energy producers (solar panel owners, micro-wind farms) have no transparent, profitable, or direct way to sell excess capacity to nearby consumers. The current system suffers from:

- High transmission losses across long-distance grids
- Opaque pricing with hidden markups
- Single points of failure and zero consumer choice

```mermaid
graph TD
    A["🏠 Energy Producers"] -->|Forced to sell at deficit| B["⚡ Centralized Grid"]
    B -->|30% Transmission Loss| C["🔄 Inefficient Routing"]
    C -->|Hidden Markups| D["🏢 Energy Consumers"]

    style A fill:#052e16,stroke:#22c55e,color:#fff
    style B fill:#3f1414,stroke:#ef4444,color:#fff
    style C fill:#3f1414,stroke:#ef4444,color:#fff
    style D fill:#1e1b4b,stroke:#6366f1,color:#fff
```

---

## 💡 Solution Overview

**Eco Bazzar** eliminates the middleman entirely. Using the carbon-negative **Algorand Blockchain** for trustless settlement and a responsive **Flask** backend for real-time operations, we connect local energy producers directly with consumers in their vicinity.

```mermaid
graph LR
    A["🏠 Solar Producer"] -->|Lists Excess kWh| B["🌐 Eco Bazzar Platform"]
    C["🏢 Local Buyer"] -->|Purchases Energy| B
    B -->|Executes Smart Contract| D["🔗 Algorand AVM"]
    D -->|Settles Payment & Ownership| E["📒 Immutable Ledger"]

    style A fill:#052e16,stroke:#22c55e,color:#fff
    style B fill:#111827,stroke:#9FC0C1,color:#fff
    style C fill:#1e1b4b,stroke:#6366f1,color:#fff
    style D fill:#312e81,stroke:#6366f1,color:#fff
    style E fill:#1e293b,stroke:#475569,color:#fff
```

---

## 🏗 System Architecture

### High-Level Platform Architecture

```mermaid
graph TB
    subgraph Users
        Seller["🏠 Energy Seller"]
        Buyer["🏢 Energy Buyer"]
    end

    subgraph Platform ["Eco Bazzar Core"]
        UI["Web UI - Jinja2 / HTML / CSS / JS"]
        API["Flask API Server - Python 3.12"]
        DB[("Neon PostgreSQL")]
    end

    subgraph External ["External Services"]
        Clerk["Clerk Auth - JWT / RBAC"]
        Algo["Algorand Network - Smart Contracts"]
    end

    Seller -->|Lists Energy, Updates Location| UI
    Buyer -->|Browses Map, Purchases Energy| UI
    UI -->|REST API Calls| API
    UI -->|Authenticates| Clerk
    API -->|Reads/Writes| DB
    API -->|Triggers Smart Contracts| Algo

    style Seller fill:#052e16,stroke:#22c55e,color:#fff
    style Buyer fill:#1e1b4b,stroke:#6366f1,color:#fff
    style UI fill:#111827,stroke:#9FC0C1,color:#fff
    style API fill:#111827,stroke:#9FC0C1,color:#fff
    style DB fill:#064e3b,stroke:#10b981,color:#fff
    style Clerk fill:#312e81,stroke:#6366f1,color:#fff
    style Algo fill:#312e81,stroke:#6366f1,color:#fff
```

### AI Price Prediction Flow

```mermaid
sequenceDiagram
    participant UI as Dashboard
    participant API as Flask Backend
    participant DB as Neon PostgreSQL

    UI->>API: GET /api/prediction
    API->>DB: Fetch 30-day transaction history
    DB-->>API: Returns supply/demand data
    API->>API: Execute weighted pricing algorithm
    API-->>UI: Return predicted_price, trend, change_pct
```

---

## ✨ Core Features

| Feature | Description | Status |
| :--- | :--- | :---: |
| **Live Energy Map** | Interactive Leaflet.js map with real-time geolocation connecting buyers directly to nearby active sellers. | ✅ Live |
| **Smart Contract Settlement** | Secure, trustless energy exchange via Algorand Virtual Machine (AVM) smart contracts. | ✅ Live |
| **AI Price Prediction** | Dynamic pricing suggestions powered by real-time supply/demand analysis from the transaction database. | ✅ Live |
| **Clerk Identity + RBAC** | Enterprise-grade JWT authentication with strict role separation between buyers and sellers. | ✅ Live |
| **Gamification Engine** | Engagement loops rewarding carbon footprint reduction with on-platform points and badges. | 🔄 Beta |
| **Seller Dashboard** | Full energy control panel with charts, production history, location tracking, and quick actions. | ✅ Live |
| **Real-time Marketplace** | Browse, filter, and purchase energy listings with live availability updates. | ✅ Live |

---

## 🛠 Tech Stack

### Layered Architecture

```mermaid
graph TD
    subgraph Frontend ["Frontend Layer"]
        A1["Jinja2 Templates"]
        A2["Vanilla CSS"]
        A3["Leaflet.js - Maps"]
        A4["Chart.js - Analytics"]
    end

    subgraph Backend ["Backend Layer"]
        B1["Flask - API Server"]
        B2["Prisma ORM"]
        B3["Clerk SDK - Auth"]
    end

    subgraph Data ["Data & Blockchain Layer"]
        C1[("Neon PostgreSQL")]
        C2["Algorand - PyTeal"]
        C3["Docker - LocalNet"]
    end

    Frontend -->|REST / JSON| Backend
    Backend -->|SQL / ORM| Data

    style Frontend fill:#111827,stroke:#9FC0C1,color:#D4E3E3
    style Backend fill:#111827,stroke:#f59e0b,color:#D4E3E3
    style Data fill:#111827,stroke:#22c55e,color:#D4E3E3
```

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | HTML5, CSS3, JavaScript, Jinja2, Leaflet.js, Chart.js |
| **Backend** | Python 3.12, Flask, Prisma ORM, Clerk SDK |
| **Blockchain** | Algorand, PyTeal, AlgoKit CLI, AlgoKit Utils |
| **Database** | Neon PostgreSQL (Cloud) |
| **DevOps** | Docker, Git, GitHub Actions |

---

## 📂 Project Structure

```
EcoBazzar/
├── Eco Bazzar/                     # AlgoKit Smart Contract Project
│   └── projects/
│       └── Eco Bazzar/
│           └── smart_contracts/
│               └── unit_transfer/  # Core trading contract (PyTeal)
├── doc/                            # Architecture documentation
├── instance/                       # Local database & secrets
├── main/
│   ├── routes.py                   # Flask API endpoints & view routing
│   ├── models.py                   # SQLAlchemy / Prisma models
│   ├── auth.py                     # Clerk JWT middleware
│   ├── services/
│   │   ├── ledger_service.py       # Blockchain interaction layer
│   │   ├── prediction_service.py   # AI dynamic pricing engine
│   │   └── gamification.py         # Points & badges system
│   ├── static/                     # CSS, JS, images, videos
│   └── templates/                  # Jinja2 HTML templates
│       ├── dashboard.html          # Buyer dashboard
│       ├── seller_dashboard.html   # Seller energy control panel
│       ├── marketplace.html        # Energy marketplace
│       ├── energy_map.html         # Live geolocation map
│       └── layout.html             # Base template
├── playground/                     # Standalone AVM testing scripts
├── prisma/                         # Database schema & migrations
├── main.py                         # Application entry point
└── requirements.txt                # Python dependencies
```

---

## 🚀 Installation & Setup

### Prerequisites

| Tool | Version | Purpose |
| :--- | :--- | :--- |
| Python | >= 3.12 | Runtime |
| Docker | Latest | Algorand LocalNet |
| AlgoKit CLI | >= 2.5.0 | Smart contract tooling |

### Step 1 — Clone & Install

```bash
git clone https://github.com/Ansh280705/EcoBazaar.git
cd EcoBazaar

python -m venv venv
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

pip install -r requirements.txt
```

### Step 2 — Environment Configuration

Create a `.env` file in the project root:

```env
FLASK_APP=main.py
FLASK_DEBUG=1
DATABASE_URL="postgresql://user:password@your-neon-host.neon.tech/neondb"
CLERK_SECRET_KEY="sk_test_..."
CLERK_FRONTEND_API="pk_test_..."
```

### Step 3 — Start Algorand LocalNet

```bash
# Ensure Docker Desktop is running
algokit localnet start
```

### Step 4 — Launch

```bash
python main.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

> **Note:** Smart contract compilation is only needed if you modify the PyTeal source:
> ```bash
> algokit compile py <CONTRACT_FILE> --output-arc32 --no-output-teal
> ```

---

## 🔄 API Flow

### Energy Purchase Lifecycle

```mermaid
sequenceDiagram
    participant Buyer as Buyer Browser
    participant API as Flask API
    participant DB as Neon PostgreSQL
    participant Chain as Algorand AVM

    Buyer->>API: POST /buy-energy (listing_id, units)
    API->>DB: Validate listing availability
    DB-->>API: Listing data
    API->>Chain: Execute transfer smart contract
    Chain-->>API: Transaction confirmed
    API->>DB: Update balances & record transaction
    API-->>Buyer: Return success + transaction hash
```

### Key Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/seller-dashboard` | Seller energy control panel |
| `GET` | `/marketplace` | Browse active energy listings |
| `GET` | `/api/map-data` | Fetch seller locations for the map |
| `GET` | `/api/prediction` | AI price prediction data |
| `POST` | `/api/seller/update-location` | Update seller GPS coordinates |
| `POST` | `/sell` | Create a new energy listing |
| `POST` | `/buy-energy` | Purchase energy from a listing |

---

## 🗺 Roadmap

```mermaid
gantt
    title Eco Bazzar Development Roadmap
    dateFormat YYYY-MM-DD

    section Foundation
    Auth and RBAC System         :done, a1, 2026-01-01, 2026-01-15
    Neon DB Architecture         :done, a2, 2026-01-15, 2026-01-30

    section Marketplace
    Algorand Smart Contracts     :done, b1, 2026-02-01, 2026-02-28
    Live Map and Geotagging      :done, b2, 2026-02-15, 2026-02-28

    section Advanced
    AI Price Prediction          :active, c1, 2026-03-01, 2026-03-15
    Gamification v2              :c2, 2026-03-15, 2026-04-01
    IoT Hardware Integration     :c3, 2026-04-01, 2026-05-01
    Mobile App                   :c4, 2026-05-01, 2026-06-01
```

---

## 🛑 Troubleshooting

<details>
<summary><strong>Docker "unauthorized" error when starting LocalNet</strong></summary>

If you see `unauthorized: incorrect username or password`:
1. Sign out from the Docker Desktop system tray icon.
2. Log back in using your **Docker Hub username** (not email):
   ```bash
   docker login --username your_username
   ```
3. Verify at [hub.docker.com](https://hub.docker.com) — your username is shown in the top-right menu.

</details>

<details>
<summary><strong>LocalNet account/asset setup</strong></summary>

If using LocalNet, you need fresh accounts and assets:
1. Create new accounts and note their mnemonics in `playground/account_constants.py` under `ACCOUNTS_LOCAL`.
2. Create a new asset using `playground/asset_creation.py`.
3. Update `ASSET_ID_LOCAL_NET` with the new asset ID.

For **TestNet**, set `LOCAL_NET = False` in the test files.

</details>

---




<div align="center">

**Eco Bazzar** — Built to revolutionize planetary energy flow.


</div>
