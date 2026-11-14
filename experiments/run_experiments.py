
import csv
from pathlib import Path

import matplotlib.pyplot as plt

from simulator.engine import SimulationEngine


def run_experiments():
    results = {}

    for protocol in ("tdma", "csma"):
        results[protocol.upper()] = SimulationEngine(
            protocol=protocol,
            num_nodes=20,
            duration=20,
            packet_interval=1.0,
            packet_size=512,
            seed=42
        ).run()

    return results


def save_summary(results, output_dir):
    fields = [
        "protocol",
        "total_generated",
        "total_delivered",
        "packet_delivery_ratio",
        "throughput_bps",
        "average_latency_seconds",
        "total_collisions",
        "average_energy_per_node_joules"
    ]

    with open(
        output_dir / "comparison.csv",
        "w",
        newline=""
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        for protocol, data in results.items():
            writer.writerow({
                "protocol": protocol,
                **{field: data[field] for field in fields if field != "protocol"}
            })

    with open(
        output_dir / "node_energy.csv",
        "w",
        newline=""
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["Node ID", "TDMA Energy (J)", "CSMA Energy (J)"])

        for node_id in results["TDMA"]["energy_per_node_joules"]:
            writer.writerow([
                node_id,
                results["TDMA"]["energy_per_node_joules"][node_id],
                results["CSMA"]["energy_per_node_joules"][node_id]
            ])


def create_comparison_graph(results, output_dir, key, title, ylabel, filename):
    protocols = ["TDMA", "CSMA"]
    values = [results[p][key] for p in protocols]

    plt.figure(figsize=(8, 5))
    plt.bar(protocols, values)

    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel("MAC Protocol")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    plt.savefig(output_dir / filename, dpi=300)
    plt.close()


def create_energy_graph(results, output_dir):
    node_ids = list(results["TDMA"]["energy_per_node_joules"].keys())

    tdma_energy = [
        results["TDMA"]["energy_per_node_joules"][node]
        for node in node_ids
    ]

    csma_energy = [
        results["CSMA"]["energy_per_node_joules"][node]
        for node in node_ids
    ]

    plt.figure(figsize=(10, 5))

    plt.plot(node_ids, tdma_energy, marker="o", label="TDMA")
    plt.plot(node_ids, csma_energy, marker="s", label="CSMA")

    plt.title("Energy Consumption Per Sensor Node")
    plt.xlabel("Sensor Node ID")
    plt.ylabel("Energy Consumed (Joules)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    plt.savefig(output_dir / "energy_per_node.png", dpi=300)
    plt.close()


def main():
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)

    results = run_experiments()

    print("\nMAC PROTOCOL COMPARISON")
    print("=" * 45)

    for protocol, data in results.items():
        print(f"\n{protocol}")
        print("-" * 30)
        print("Generated:", data["total_generated"])
        print("Delivered:", data["total_delivered"])
        print(f"PDR: {data['packet_delivery_ratio'] * 100:.2f}%")
        print(f"Throughput: {data['throughput_bps']:.2f} bps")
        print(
            f"Average latency: "
            f"{data['average_latency_seconds']:.4f} seconds"
        )
        print("Collisions:", data["total_collisions"])
        print(
            f"Average energy: "
            f"{data['average_energy_per_node_joules']:.6f} J"
        )

    save_summary(results, output_dir)

    create_comparison_graph(
        results, output_dir,
        "packet_delivery_ratio",
        "Packet Delivery Ratio Comparison",
        "PDR",
        "pdr_comparison.png"
    )

    create_comparison_graph(
        results, output_dir,
        "throughput_bps",
        "Throughput Comparison",
        "Throughput (bps)",
        "throughput_comparison.png"
    )

    create_comparison_graph(
        results, output_dir,
        "average_latency_seconds",
        "Average Latency Comparison",
        "Latency (seconds)",
        "latency_comparison.png"
    )

    create_comparison_graph(
        results, output_dir,
        "average_energy_per_node_joules",
        "Average Energy Consumption Comparison",
        "Energy (Joules)",
        "energy_comparison.png"
    )

    create_energy_graph(results, output_dir)

    print("\n" + "=" * 45)
    print("EXPERIMENTS COMPLETED")
    print("Generated files in:", output_dir.resolve())

    for file in sorted(output_dir.iterdir()):
        if file.is_file():
            print(" -", file.name)


if __name__ == "__main__":
    main()
