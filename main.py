
from simulator.engine import SimulationEngine


def print_results(results):
    print("\n" + "=" * 55)
    print(f"PROTOCOL: {results['protocol']}")
    print("=" * 55)

    print(f"Number of nodes: {results['node_count']}")
    print(f"Simulation duration: {results['simulation_duration']} seconds")
    print(f"Packets generated: {results['total_generated']}")
    print(f"Packets delivered: {results['total_delivered']}")

    print(f"Throughput: {results['throughput_bps']:.2f} bps")
    print(
        f"Average latency: "
        f"{results['average_latency_seconds']:.6f} seconds"
    )
    print(
        f"Packet delivery ratio: "
        f"{results['packet_delivery_ratio'] * 100:.2f}%"
    )
    print(
        f"Average energy per node: "
        f"{results['average_energy_per_node_joules']:.6f} J"
    )

    print(f"Total collisions: {results['total_collisions']}")

    print("\nEnergy consumed per node:")
    for node_id, energy in results["energy_per_node_joules"].items():
        print(f"Node {node_id}: {energy:.6f} J")


def main():
    print("\nWIRELESS SENSOR NETWORK MAC PROTOCOL SIMULATOR")
    print("-" * 55)

    tdma_engine = SimulationEngine(
        protocol="tdma",
        num_nodes=20,
        duration=100,
        packet_interval=1.0,
        packet_size=512,
        seed=42
    )

    csma_engine = SimulationEngine(
        protocol="csma",
        num_nodes=20,
        duration=100,
        packet_interval=1.0,
        packet_size=512,
        seed=42
    )

    tdma_results = tdma_engine.run()
    csma_results = csma_engine.run()

    print_results(tdma_results)
    print_results(csma_results)

    print("\nSIMULATION COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    main()
