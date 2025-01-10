# Adaptive Traffic Signal Control System 🚦

An innovative and intelligent system for managing urban traffic using real-time data, machine learning, and dynamic traffic flow optimization.

---

## 📌 Overview

The **Adaptive Traffic Signal Control System** is designed to reduce congestion, enhance traffic flow, and improve overall commuter experience. It incorporates sensor feedback, dynamic vehicle prioritization, and predictive algorithms to adapt to real-time traffic conditions.

---

## 🏷️ **Title**: Tackling Urban Traffic Challenges  
## 💡 **Problem Statement**

**Traffic congestion** is a growing issue in urban areas, leading to increased travel time, fuel consumption, and pollution.  
**How can technology help optimize traffic flow, reduce congestion, and improve the overall transportation experience for commuters?**

---

## 🛠 Features

- **Dynamic Signal Control**: Adjusts traffic light timings based on real-time vehicle density and road conditions.
- **Feedback Loop Mechanism**: Utilizes sensor data to measure congestion and optimize signal timings.
- **Vehicle Categorization**: Prioritizes emergency vehicles, public transport, and high-priority sectors like "office commuters" or "students."
- **80% Flow Restriction**: Ensures smooth traffic by limiting vehicle flow to prevent downstream congestion.
- **Peak Time Optimization**: Focuses on high-traffic hours (8–10 AM and 4–7 PM) for efficient traffic management.
- **Scalable Design**: Can be extended to manage complex intersections and multi-lane networks.

---

## 📊 Workflow

1. **Linearization and Vehicle Segmentation**:
   - Represent the road network as a linear graph.
   - Group vehicles by type (e.g., buses, private cars, taxis) and priority.

2. **Road Segmentation**:
   - Segment roads based on width, length, and traffic density.
   - Consider distance between signals for smooth vehicle flow.

3. **Adaptive Vehicle Restriction**:
   - Restrict flow to 80% of road capacity to prevent bottlenecks.
   - Dynamically adjust based on vehicle dimensions and congestion.

4. **Feedback Mechanism**:
   - Use sensors at intersections to collect real-time data.
   - Adjust signal timings dynamically using congestion factors.

---

## 🖥 Tech Stack

- **Programming Language**: Python
- **Data Collection**: IoT Sensors
- **Simulation**: SUMO (Simulation of Urban Mobility)
- **Machine Learning**: TensorFlow, Scikit-learn
- **Visualization**: Matplotlib


---

## 🚀 Installation and Usage

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/adaptive-traffic-signal-system.git
   cd adaptive-traffic-signal-system
