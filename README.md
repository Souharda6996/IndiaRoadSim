# TraffiSim AI: High-Fidelity Digital Twin for Indian Road Networks

[![SIH 2024](https://img.shields.io/badge/SIH-2024-blue.svg)](https://www.sih.gov.in/)
[![Next.js](https://img.shields.io/badge/Next.js-16.1-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**TraffiSim AI** is a cutting-edge Digital Twin platform designed to simulate and optimize complex Indian traffic conditions. Unlike traditional simulators, TraffiSim AI accounts for the "Weak Lane Discipline" and "Mixed Vehicle" realities of Indian urban environments, providing a high-fidelity visualization and analytics dashboard.

---

## 🚀 Key Features

### 1. Advanced Agent-Based Traffic Engine
- **Mixed Vehicle Interaction**: Modeled 7 distinct vehicle classes including Auto-rickshaws, Bikes, Buses, Trucks, and Emergency vehicles.
- **Weak Lane Discipline Simulation**: Specialized AI agents that utilize gap-seeking, lane-cutting, and side-by-side driving behaviors.
- **Curved Trajectory Math**: Vehicles follow real-world road geometries (OSM LineStrings) with precise interpolation.

### 2. Live Digital Twin Dashboard
- **Interactive Satellite Map**: Powered by **Leaflet.js** and **Esri World Imagery** for a "Google Maps" feel.
- **Real-Time Streaming**: High-speed WebSocket connection between the Python engine and the React frontend.
- **Congestion Analytics**: Live heatmaps and charts showing traffic density, average speed, and flow trends.

### 3. Real-World Data Integration
- **OSM Integration**: Automated extraction of road networks, junction layouts, and bridge geometries from **OpenStreetMap**.
- **City Hubs**: Ready-to-use models for major Indian hubs like Mumbai, Bangalore, and Delhi.

---

## 🛠️ Tech Stack

- **Frontend**: Next.js 16.1, TypeScript, Tailwind CSS, Lucide React.
- **Mapping**: Leaflet.js, React-Leaflet, Esri Satellite Tiles.
- **Backend API**: Python 3.12, FastAPI, Uvicorn, WebSockets.
- **Simulation Engine**: NetworkX, OSMnx, Custom Agent-Based Modeling.
- **Analytics**: Recharts, D3.js.

---

## 🏃 Getting Started

### Prerequisites
- **Python 3.12+**
- **Node.js 18+** & **npm**
- Internet connection (for fetching OSM data)

### Fast Launch (Windows)
Simply run the launcher script:
```powershell
./run_simulation.bat
```
Select **Option 4** to launch the full TraffiSim AI platform. This will automatically start the backend, frontend, and open the dashboard in your browser.

### Manual Setup

#### 1. Backend Setup
```powershell
pip install -r requirements.txt
py -3.12 -m uvicorn backend.main:app --port 8000
```
*The engine will download/load the Mumbai road network and start streaming traffic.*

#### 2. Frontend Setup
```powershell
cd frontend
npm install
npm run dev
```
*The dashboard will be available at [http://localhost:3000](http://localhost:3000).*

---

## 📊 Dashboard Overview

- **Primary Controls**: Toggle between Live Simulation, Map Modeler, and AI Optimizer.
- **Quick Events**: Simulate real-world disruptions like **Accidents**, **Protests**, **Road Work**, or **Potholes**.
- **Traffic Density**: Monitor flow patterns and potential bottle-necks in real-time.

---

## 🏆 SIH Context
This project was developed for the **Smart India Hackathon (SIH)** to address **Problem Statement ID 25100**: *Accelerating High-Fidelity Road Network Modeling for Indian Traffic Simulations.*

---

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

Developed with ❤️ for **Souharda6996/IndiaRoadSim**.
