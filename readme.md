# Coreloom

> **Distributed Compute Virtualization and Resource Provisioning Framework**  
> Developed by HJKEnsignElectronics

Coreloom is an architectural framework designed for decentralized resource allocation and distributed hardware virtualization. By abstracting local resource constraints, Coreloom aggregates computational metrics across disjoint local network nodes, algorithmically mapping combined multi-system CPU capacity into isolated, threaded virtual "Cores." This design enables parallel execution environments that mimic GPU-like processing capabilities using a unified network-to-container pipeline.

## 🌟 Core Architecture & Mechanics

- **CPU-to-GPU Aggregation:** Collects computing density across network connections (e.g., pooling physical processors) and unifies processing density into cohesive parallel logical modules.
- **Dynamic Thread Structuring:** Leverages multi-threading maps over cluster nodes to create dense, parallel computing slots optimized for heavy simulation workloads.
- **Decoupled Backend Engine:** Utilizes a strict 6-module Python framework prioritizing isolation of duties, performance stability, and low latency.
- **Independent Asset Handling:** Frontend dependencies (`hjk.html`, `hjk.css`, `hjk.js`) and OS configuration layers (Docker structures) are entirely separate from execution components.

---

## 🛠️ The 6-File Python Architecture

The processing ecosystem is strictly segmented into exactly six operational Python source modules:

1. **`main.py`** – The high-performance entry point initializing the FastAPI app context, enabling CORS structures, and mounting routes.
2. **+--------------+        +------------+        +-------------------+
| hjk.html/.js | -----> |   api.py   | -----> |    hardware.py    |
|  (Frontend)  |        |  (FastAPI) |        | (Virtual Cluster) |
+--------------+        +------------+        +-------------------+
^                      |                         |
|                      v                         v
+--------------+        +------------+        +-------------------+
|   hjk.css    |        |   auth.py  |        |   Docker Engine   |
| (Design Mod) |        |   (JWT)    |        | (Node Containers) |
+--------------+        +------------+        +-------------------+`auth.py`** – Account security controller managing secure storage hashes, user session tokens (JWT), and authorization barriers.
3. **`models.py`** – Pydantic schema validator enforcing interface consistency for provisioning requests, data flows, and registration properties.
4. **`api.py`** – Master router managing system routing maps, endpoint tracking (`/login`, `/allocate-resources`), and server hooks.
5. **`hardware.py`** – Hardware virtualization mechanism running the container scheduling, node coordination, and resource calculation engine.
6. **`utils.py`** – Telemetry collector, configuration environment parser, certificate generator, and underlying system logger.

---

