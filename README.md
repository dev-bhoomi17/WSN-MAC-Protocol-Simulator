# Wireless Sensor Network MAC Protocol Simulator

A Python-based discrete-event simulator for evaluating and comparing two Medium Access Control (MAC) protocols in Wireless Sensor Networks (WSNs): **TDMA** and **CSMA/CA**.

The project evaluates network performance using packet delivery ratio, throughput, average latency, collision count, and energy consumption.

## Features

- Discrete-event simulation using a priority-based event queue.
- Simulation of multiple sensor nodes.
- TDMA-based transmission scheduling with sleep and active states.
- CSMA/CA-based channel sensing and random backoff.
- Packet generation, transmission, collision tracking, and delivery.
- Energy consumption tracking for sensor nodes.
- Automated protocol comparison.
- Performance graphs and CSV result generation.
- Automated tests using pytest.

## Technologies Used

- Python 3
- NumPy
- Matplotlib
- Pytest
- Python Heap Queue (`heapq`)

## MAC Protocols

### 1. TDMA (Time Division Multiple Access)

TDMA assigns a dedicated time slot to each sensor node.

Features:
- Scheduled transmission slots.
- Nodes switch between active and sleep states.
- Reduced idle energy consumption through duty cycling.

### 2. CSMA/CA (Carrier Sense Multiple Access with Collision Avoidance)

CSMA/CA checks channel availability before transmission.

Features:
- Channel-busy detection.
- Random backoff intervals.
- Collision detection.
- Transmission retries.

## Performance Metrics

| Metric | Description |
|---|---|
| Throughput | Successfully delivered bits per second |
| Packet Delivery Ratio | Ratio of delivered packets to generated packets |
| Average Latency | Average time taken for successful packet delivery |
| Collision Count | Number of recorded transmission collisions |
| Energy Consumption | Estimated energy consumed by each sensor node |

## Project Structure

```text
WSN-MAC-Protocol-Simulator/
│
├── simulator/
│   ├── __init__.py
│   ├── nodes.py
│   ├── events.py
│   ├── channel.py
│   ├── tdma.py
│   ├── csma_ca.py
│   ├── metrics.py
│   └── engine.py
│
├── experiments/
│   └── run_experiments.py
│
├── results/
│   ├── comparison.csv
│   ├── node_energy.csv
│   ├── pdr_comparison.png
│   ├── throughput_comparison.png
│   ├── latency_comparison.png
│   ├── energy_comparison.png
│   └── energy_per_node.png
│
├── tests/
│   └── test_simulator.py
│
├── main.py
├── requirements.txt
├── pytest.ini
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/dev-bhoomi17/WSN-MAC-Protocol-Simulator.git
cd WSN-MAC-Protocol-Simulator
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the simulator

```bash
python main.py
```

### 6. Run experiments

```bash
python -m experiments.run_experiments
```

### 7. Run tests

```bash
python -m pytest -q
```

## Experimental Configuration

The comparison experiments use identical simulation settings for both protocols.

| Parameter | Value |
|---|---:|
| Number of sensor nodes | 20 |
| Simulation duration | 20 seconds |
| Packet generation interval | 1 second |
| Packet size | 512 bytes |
| Random seed | 42 |
| TDMA slot duration | 0.05 seconds |
| Transmission duration | 0.01 seconds |

## Experimental Results

The following results were obtained from the simulation.

| Metric | TDMA | CSMA/CA |
|---|---:|---:|
| Packets Generated | 400 | 400 |
| Packets Delivered | 398 | 400 |
| Packet Delivery Ratio | 99.50% | 100.00% |
| Throughput | 81,510.40 bps | 81,920.00 bps |
| Average Latency | 0.4837 s | 0.1243 s |
| Collisions | 0 | 0 |
| Average Energy per Node | 0.005067 J | 0.023896 J |

### Result Analysis

- CSMA/CA achieved a slightly higher packet delivery ratio and throughput in the tested workload.
- CSMA/CA also recorded lower average latency.
- TDMA consumed approximately 78.8% less estimated energy per node.
- Neither protocol recorded collisions under the selected simulation configuration.

These observations apply to this particular simulation configuration and should not be generalized to all network conditions.

## Generated Graphs

The experiment script automatically generates:

1. Packet Delivery Ratio Comparison
2. Throughput Comparison
3. Average Latency Comparison
4. Average Energy Consumption Comparison
5. Energy Consumption Per Sensor Node

All graphs and CSV files are saved in the `results/` directory.

## Testing

The project includes automated tests covering:

- Sensor node creation.
- Packet generation.
- Event queue ordering and priorities.
- Wireless channel transmission.
- Collision detection.
- TDMA and CSMA simulation execution.
- Input validation.
- Energy accounting.
- TDMA sleep-state handling.

**Latest test result: 15 passed.**

## Limitations

- The simulator uses a simplified wireless channel model.
- Receiver-side and ACK energy consumption are not fully represented.
- A complete physical-layer propagation and interference model is not implemented.
- Results are software simulation estimates, not measurements from physical sensor hardware.

## Future Improvements

- Implement more detailed wireless channel and propagation models.
- Add receiver-side and acknowledgment energy accounting.
- Introduce configurable network topologies.
- Add larger-scale network simulations.
- Evaluate protocol performance under varying traffic loads.
- Add more MAC protocols for comparison.

## Conclusion

This project demonstrates how TDMA and CSMA/CA can be evaluated using a discrete-event Wireless Sensor Network simulator.

The experimental results highlight the trade-offs between latency, throughput, packet delivery, and estimated energy consumption.

The simulator provides a foundation for further research and experimentation with energy-efficient MAC protocols in wireless sensor networks.

---

**Project:** Wireless Sensor Network MAC Protocol Simulator  
**Language:** Python  
**Domain:** Wireless Sensor Networks, Computer Networks, Network Simulation
