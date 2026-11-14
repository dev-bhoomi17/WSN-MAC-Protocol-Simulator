from statistics import mean


class NetworkMetrics:
    def __init__(self):
        self.total_generated = 0
        self.total_delivered = 0
        self.total_bits_delivered = 0
        self.latencies = []
        self.node_energy = {}

    def record_generated(self):
        self.total_generated += 1

    def record_delivered(self, packet):
        self.total_delivered += 1
        self.total_bits_delivered += packet.size_bits

        if packet.latency is not None:
            self.latencies.append(packet.latency)

    def record_node_energy(self, nodes):
        self.node_energy = {
            node.node_id: node.energy_consumed
            for node in nodes
        }

    def calculate(self, simulation_duration):
        if simulation_duration <= 0:
            raise ValueError("Simulation duration must be positive.")

        throughput = (
            self.total_bits_delivered / simulation_duration
        )

        pdr = (
            self.total_delivered / self.total_generated
            if self.total_generated else 0.0
        )

        average_latency = (
            mean(self.latencies)
            if self.latencies else 0.0
        )

        average_energy = (
            mean(self.node_energy.values())
            if self.node_energy else 0.0
        )

        return {
            "throughput_bps": throughput,
            "average_latency_seconds": average_latency,
            "packet_delivery_ratio": pdr,
            "energy_per_node_joules": self.node_energy.copy(),
            "average_energy_per_node_joules": average_energy,
            "total_generated": self.total_generated,
            "total_delivered": self.total_delivered
        }