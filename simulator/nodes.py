
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class NodeState(Enum):
    ACTIVE = "active"
    SLEEP = "sleep"
    TRANSMITTING = "transmitting"
    RECEIVING = "receiving"


@dataclass
class Packet:
    packet_id: int
    source_id: int
    destination_id: int
    size_bits: int
    generated_at: float
    attempts: int = 0
    delivered_at: Optional[float] = None

    @property
    def latency(self) -> Optional[float]:
        if self.delivered_at is None:
            return None
        return self.delivered_at - self.generated_at


@dataclass
class EnergyModel:
    tx_j_per_bit: float = 50e-9
    rx_j_per_bit: float = 50e-9
    idle_j_per_second: float = 1e-3
    sleep_j_per_second: float = 1e-5
    receive_j_per_second: float = 1e-3


@dataclass
class SensorNode:
    node_id: int
    initial_energy: float = 10.0
    energy_model: EnergyModel = field(default_factory=EnergyModel)
    state: NodeState = NodeState.ACTIVE
    packet_queue: list[Packet] = field(default_factory=list)
    energy_consumed: float = 0.0
    packets_generated: int = 0
    packets_delivered: int = 0
    last_state_change: float = 0.0

    @property
    def remaining_energy(self) -> float:
        return max(0.0, self.initial_energy - self.energy_consumed)

    @property
    def is_alive(self) -> bool:
        return self.remaining_energy > 0

    def consume_energy(self, amount: float) -> None:
        if amount < 0:
            raise ValueError("Energy consumption cannot be negative.")

        self.energy_consumed += min(amount, self.remaining_energy)

    def update_state(self, new_state: NodeState, current_time: float) -> None:
        if current_time < self.last_state_change:
            raise ValueError("State update time cannot move backwards.")

        elapsed = current_time - self.last_state_change

        power_rates = {
            NodeState.ACTIVE: self.energy_model.idle_j_per_second,
            NodeState.SLEEP: self.energy_model.sleep_j_per_second,
            NodeState.TRANSMITTING: 0.0,
            NodeState.RECEIVING: self.energy_model.receive_j_per_second,
        }

        self.consume_energy(elapsed * power_rates[self.state])

        self.state = new_state
        self.last_state_change = current_time

    def finish_energy_accounting(self, simulation_end: float) -> None:
        if simulation_end < self.last_state_change:
            raise ValueError("Simulation end cannot precede the last state change.")

        elapsed = simulation_end - self.last_state_change

        power_rates = {
            NodeState.ACTIVE: self.energy_model.idle_j_per_second,
            NodeState.SLEEP: self.energy_model.sleep_j_per_second,
            NodeState.TRANSMITTING: 0.0,
            NodeState.RECEIVING: self.energy_model.receive_j_per_second,
        }

        self.consume_energy(elapsed * power_rates[self.state])
        self.last_state_change = simulation_end

    def generate_packet(self, packet: Packet) -> None:
        if not self.is_alive:
            return

        if packet.source_id != self.node_id:
            raise ValueError("Packet source does not match this node.")

        self.packet_queue.append(packet)
        self.packets_generated += 1

    def get_next_packet(self) -> Optional[Packet]:
        if not self.packet_queue:
            return None

        return self.packet_queue.pop(0)
