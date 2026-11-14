
import random

from simulator.nodes import SensorNode, Packet, NodeState
from simulator.events import EventQueue, EventType
from simulator.channel import WirelessChannel
from simulator.tdma import TDMAScheduler
from simulator.csma_ca import CSMA_CA
from simulator.metrics import NetworkMetrics


class SimulationEngine:
    def __init__(
        self,
        protocol,
        num_nodes=20,
        duration=100,
        packet_interval=1.0,
        packet_size=512,
        seed=42
    ):
        if num_nodes < 1:
            raise ValueError("At least one sensor node is required.")

        if duration <= 0 or packet_interval <= 0 or packet_size <= 0:
            raise ValueError("Simulation parameters must be positive.")

        self.protocol = protocol.lower()

        if self.protocol not in ("tdma", "csma"):
            raise ValueError("Protocol must be 'tdma' or 'csma'.")

        self.num_nodes = num_nodes
        self.duration = duration
        self.packet_interval = packet_interval
        self.packet_size = packet_size

        self.random = random.Random(seed)

        self.nodes = [
            SensorNode(node_id=i)
            for i in range(num_nodes)
        ]

        self.event_queue = EventQueue()
        self.channel = WirelessChannel()
        self.metrics = NetworkMetrics()

        self.tdma = (
            TDMAScheduler(self.nodes, slot_duration=0.05)
            if self.protocol == "tdma" else None
        )

        self.csma = (
            CSMA_CA(self.channel, seed=seed)
            if self.protocol == "csma" else None
        )

        self.next_packet_id = 0
        self.transmission_duration = 0.01
        self.ack_delay = 0.001

        self.completed_packets = set()

        self.pending_packets = {
            node.node_id: []
            for node in self.nodes
        }

        self.tdma_scheduled = set()
        self.results = None

    def schedule_packet_generation(self):
        for node in self.nodes:
            generation_time = 0.1

            while generation_time < self.duration:
                self.event_queue.schedule(
                    generation_time,
                    EventType.PACKET_GENERATION,
                    node_id=node.node_id
                )
                generation_time += self.packet_interval

    def generate_packet(self, node_id, current_time):
        node = self.nodes[node_id]

        if not node.is_alive:
            return None

        packet = Packet(
            packet_id=self.next_packet_id,
            source_id=node_id,
            destination_id=-1,
            size_bits=self.packet_size * 8,
            generated_at=current_time
        )

        self.next_packet_id += 1

        node.generate_packet(packet)
        node.get_next_packet()

        self.metrics.record_generated()
        self.pending_packets[node_id].append(packet)

        return packet

    def get_next_tdma_slot(self, node_id, current_time):
        frame_duration = self.tdma.frame_duration
        slot_offset = (
            self.tdma.get_slot(node_id) * self.tdma.slot_duration
        )

        tolerance = 1e-12
        frame_number = int(
            (current_time + tolerance) // frame_duration
        )

        transmission_time = (
            frame_number * frame_duration + slot_offset
        )

        if transmission_time < current_time - tolerance:
            transmission_time += frame_duration

        return transmission_time

    def schedule_tdma_transmission(self, node_id, current_time):
        queue = self.pending_packets[node_id]

        if not queue or node_id in self.tdma_scheduled:
            return

        transmission_time = self.get_next_tdma_slot(
            node_id,
            current_time
        )

        if transmission_time >= self.duration:
            return

        self.tdma_scheduled.add(node_id)

        self.event_queue.schedule(
            transmission_time,
            EventType.TRANSMISSION_START,
            node_id=node_id
        )

    def schedule_csma_transmission(self, node_id, packet, current_time):
        backoff = self.csma.get_backoff_time()

        self.event_queue.schedule(
            current_time + backoff,
            EventType.TRANSMISSION_START,
            node_id=node_id,
            data=packet
        )

    def schedule_tdma_state_events(self):
        if self.protocol != "tdma":
            return

        for frame_start in self._frame_starts():
            for node in self.nodes:
                slot_start = (
                    frame_start
                    + self.tdma.get_slot(node.node_id)
                    * self.tdma.slot_duration
                )

                slot_end = slot_start + self.tdma.slot_duration

                if slot_start < self.duration:
                    self.event_queue.schedule(
                        slot_start,
                        EventType.SLOT_START,
                        node_id=node.node_id
                    )

                if slot_end < self.duration:
                    self.event_queue.schedule(
                        slot_end,
                        EventType.SLOT_END,
                        node_id=node.node_id
                    )

    def _frame_starts(self):
        frame_start = 0.0

        while frame_start < self.duration:
            yield frame_start
            frame_start += self.tdma.frame_duration

    def start_transmission(self, node_id, packet, current_time):
        node = self.nodes[node_id]

        if not node.is_alive:
            return

        if packet.packet_id in self.completed_packets:
            return

        if self.protocol == "tdma":
            frame_duration = self.tdma.frame_duration
            slot_duration = self.tdma.slot_duration

            slot_offset = (
                self.tdma.get_slot(node_id) * slot_duration
            )

            frame_number = int(
                (current_time + 1e-12) // frame_duration
            )

            frame_start = frame_number * frame_duration
            slot_start = frame_start + slot_offset
            slot_end = slot_start + slot_duration

            if (
                current_time < slot_start - 1e-12
                or current_time + self.transmission_duration
                > slot_end + 1e-12
            ):
                next_frame_time = (
                    frame_start + frame_duration + slot_offset
                )

                if next_frame_time < self.duration:
                    self.tdma_scheduled.add(node_id)

                    self.event_queue.schedule(
                        next_frame_time,
                        EventType.TRANSMISSION_START,
                        node_id=node_id
                    )

                return

        if (
            self.protocol == "csma"
            and self.channel.is_busy(current_time)
        ):
            active_end = max(
                tx.end_time
                for tx in self.channel.active_transmissions
            )

            self.schedule_csma_transmission(
                node_id,
                packet,
                active_end
            )
            return

        transmission = self.channel.start_transmission(
            node_id=node_id,
            packet_id=packet.packet_id,
            start_time=current_time,
            duration=self.transmission_duration
        )

        node.update_state(
            NodeState.TRANSMITTING,
            current_time
        )

        self.event_queue.schedule(
            transmission.end_time,
            EventType.TRANSMISSION_END,
            node_id=node_id,
            data={
                "packet": packet,
                "transmission": transmission
            }
        )

    def handle_event(self, event):
        current_time = event.time
        node_id = event.node_id

        if event.event_type == EventType.PACKET_GENERATION:
            packet = self.generate_packet(node_id, current_time)

            if packet is None:
                return

            if self.protocol == "tdma":
                self.schedule_tdma_transmission(
                    node_id,
                    current_time
                )

            elif len(self.pending_packets[node_id]) == 1:
                self.schedule_csma_transmission(
                    node_id,
                    packet,
                    current_time
                )

        elif event.event_type == EventType.SLOT_START:
            node = self.nodes[node_id]

            if node.state != NodeState.TRANSMITTING:
                node.update_state(
                    NodeState.ACTIVE,
                    current_time
                )

        elif event.event_type == EventType.SLOT_END:
            node = self.nodes[node_id]

            if node.state != NodeState.TRANSMITTING:
                node.update_state(
                    NodeState.SLEEP,
                    current_time
                )

        elif event.event_type == EventType.TRANSMISSION_START:
            if self.protocol == "tdma":
                self.tdma_scheduled.discard(node_id)

                queue = self.pending_packets[node_id]

                if not queue:
                    return

                packet = queue[0]

            else:
                packet = event.data

            self.start_transmission(
                node_id,
                packet,
                current_time
            )

        elif event.event_type == EventType.TRANSMISSION_END:
            packet = event.data["packet"]
            transmission = event.data["transmission"]

            node = self.nodes[node_id]

            node.consume_energy(
                packet.size_bits * node.energy_model.tx_j_per_bit
            )

            if self.protocol == "tdma":
                frame_position = (
                    current_time % self.tdma.frame_duration
                )

                slot_number = int(
                    frame_position // self.tdma.slot_duration
                )

                assigned_slot = self.tdma.get_slot(node_id)

                next_state = (
                    NodeState.ACTIVE
                    if slot_number == assigned_slot
                    else NodeState.SLEEP
                )

            else:
                next_state = NodeState.ACTIVE

            node.update_state(next_state, current_time)

            self.channel.remove_finished(current_time)

            if transmission.collided:
                packet.attempts += 1

                if (
                    self.protocol == "csma"
                    and packet.attempts <= self.csma.max_retries
                ):
                    self.schedule_csma_transmission(
                        node_id,
                        packet,
                        current_time
                    )

            else:
                self.event_queue.schedule(
                    current_time + self.ack_delay,
                    EventType.ACK,
                    node_id=node_id,
                    data=packet
                )

        elif event.event_type == EventType.ACK:
            packet = event.data

            if packet.packet_id in self.completed_packets:
                return

            packet.delivered_at = current_time

            node = self.nodes[node_id]
            node.packets_delivered += 1

            self.completed_packets.add(packet.packet_id)
            self.metrics.record_delivered(packet)

            queue = self.pending_packets[node_id]

            if queue and queue[0].packet_id == packet.packet_id:
                queue.pop(0)

            if self.protocol == "tdma":
                self.schedule_tdma_transmission(
                    node_id,
                    current_time
                )

            elif queue:
                self.schedule_csma_transmission(
                    node_id,
                    queue[0],
                    current_time
                )

    def configure_tdma_sleep_states(self):
        if self.protocol != "tdma":
            return

        for node in self.nodes:
            node.update_state(NodeState.SLEEP, 0.0)

    def finish_energy_accounting(self):
        for node in self.nodes:
            node.finish_energy_accounting(self.duration)

    def run(self):
        self.schedule_packet_generation()
        self.configure_tdma_sleep_states()
        self.schedule_tdma_state_events()

        while not self.event_queue.is_empty():
            event = self.event_queue.pop()

            if event.time > self.duration:
                break

            self.handle_event(event)

        if self.protocol == "tdma":
            for node in self.nodes:
                if node.state != NodeState.TRANSMITTING:
                    node.update_state(
                        NodeState.SLEEP,
                        self.duration
                    )

        self.finish_energy_accounting()

        self.metrics.record_node_energy(self.nodes)

        self.results = self.metrics.calculate(self.duration)

        self.results["protocol"] = self.protocol.upper()
        self.results["node_count"] = self.num_nodes
        self.results["simulation_duration"] = self.duration
        self.results["total_collisions"] = self.channel.total_collisions
        self.results["total_transmissions"] = self.channel.total_transmissions

        return self.results
