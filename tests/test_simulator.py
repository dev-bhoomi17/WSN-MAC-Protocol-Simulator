
import pytest

from simulator.engine import SimulationEngine
from simulator.nodes import SensorNode, Packet
from simulator.events import EventQueue, EventType
from simulator.channel import WirelessChannel


def test_sensor_node_creation():
    node = SensorNode(node_id=1)

    assert node.node_id == 1
    assert node.is_alive
    assert node.remaining_energy == 10.0


def test_packet_generation():
    node = SensorNode(node_id=1)

    packet = Packet(
        packet_id=1,
        source_id=1,
        destination_id=-1,
        size_bits=4096,
        generated_at=0.5
    )

    node.generate_packet(packet)

    assert node.packets_generated == 1
    assert len(node.packet_queue) == 1


def test_event_queue_order():
    queue = EventQueue()

    queue.schedule(3.0, EventType.PACKET_GENERATION)
    queue.schedule(1.0, EventType.PACKET_GENERATION)
    queue.schedule(2.0, EventType.PACKET_GENERATION)

    assert queue.pop().time == 1.0
    assert queue.pop().time == 2.0
    assert queue.pop().time == 3.0


def test_event_queue_empty():
    queue = EventQueue()

    assert queue.is_empty()


def test_channel_transmission():
    channel = WirelessChannel()

    transmission = channel.start_transmission(
        node_id=1,
        packet_id=1,
        start_time=1.0,
        duration=0.01
    )

    assert not transmission.collided
    assert channel.total_transmissions == 1


def test_channel_collision():
    channel = WirelessChannel()

    channel.start_transmission(1, 1, 1.0, 0.05)

    second = channel.start_transmission(
        2, 2, 1.02, 0.05
    )

    assert second.collided
    assert channel.total_collisions == 1


@pytest.mark.parametrize("protocol", ["tdma", "csma"])
def test_simulation_runs(protocol):
    engine = SimulationEngine(
        protocol=protocol,
        num_nodes=20,
        duration=5,
        packet_interval=1,
        seed=42
    )

    results = engine.run()

    assert results["node_count"] == 20
    assert results["total_generated"] > 0
    assert results["total_delivered"] >= 0
    assert results["throughput_bps"] >= 0


def test_invalid_protocol():
    with pytest.raises(ValueError):
        SimulationEngine(protocol="invalid")


def test_invalid_node_count():
    with pytest.raises(ValueError):
        SimulationEngine(protocol="tdma", num_nodes=0)


def test_idle_energy_accounting():
    node = SensorNode(node_id=1)

    node.finish_energy_accounting(10.0)

    assert node.energy_consumed == pytest.approx(0.01)


def test_sleep_energy_accounting():
    from simulator.nodes import NodeState

    node = SensorNode(node_id=1)

    node.update_state(NodeState.SLEEP, 0.0)
    node.finish_energy_accounting(10.0)

    assert node.energy_consumed == pytest.approx(0.0001)


def test_transmission_energy_accounting():
    from simulator.nodes import NodeState

    node = SensorNode(node_id=1)

    node.update_state(NodeState.TRANSMITTING, 0.0)
    node.consume_energy(4096 * node.energy_model.tx_j_per_bit)
    node.update_state(NodeState.ACTIVE, 1.0)

    assert node.energy_consumed == pytest.approx(0.0002048)

def test_tdma_node_returns_to_sleep_after_transmission():
    from simulator.engine import SimulationEngine
    from simulator.nodes import NodeState

    engine = SimulationEngine(
        protocol="tdma",
        num_nodes=20,
        duration=2,
        packet_interval=1.0,
        packet_size=512,
        seed=42
    )

    engine.run()

    for node in engine.nodes:
        assert node.state == NodeState.SLEEP

def test_event_queue_priority_order():
    queue = EventQueue()

    queue.schedule(1.0, EventType.TRANSMISSION_START)
    queue.schedule(1.0, EventType.SLOT_START)
    queue.schedule(1.0, EventType.SLOT_END)
    queue.schedule(1.0, EventType.TRANSMISSION_END)

    events = [queue.pop() for _ in range(4)]

    assert [event.event_type for event in events] == [
        EventType.SLOT_END,
        EventType.SLOT_START,
        EventType.TRANSMISSION_END,
        EventType.TRANSMISSION_START,
    ]

