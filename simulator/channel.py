from dataclasses import dataclass


@dataclass
class Transmission:
    node_id: int
    start_time: float
    end_time: float
    packet_id: int
    collided: bool = False


class WirelessChannel:
    def __init__(self):
        self.active_transmissions: list[Transmission] = []
        self.total_transmissions = 0
        self.total_collisions = 0

    def start_transmission(
        self,
        node_id: int,
        packet_id: int,
        start_time: float,
        duration: float
    ) -> Transmission:
        if duration <= 0:
            raise ValueError("Transmission duration must be positive.")

        self.remove_finished(start_time)

        transmission = Transmission(
            node_id=node_id,
            start_time=start_time,
            end_time=start_time + duration,
            packet_id=packet_id
        )

        # Any overlapping transmission causes a collision.
        for active in self.active_transmissions:
            active.collided = True
            transmission.collided = True

        if transmission.collided:
            self.total_collisions += 1

        self.active_transmissions.append(transmission)
        self.total_transmissions += 1

        return transmission

    def remove_finished(self, current_time: float) -> None:
        self.active_transmissions = [
            tx for tx in self.active_transmissions
            if tx.end_time > current_time
        ]

    def is_busy(self, current_time: float) -> bool:
        self.remove_finished(current_time)
        return bool(self.active_transmissions)

    def get_collision_rate(self) -> float:
        if self.total_transmissions == 0:
            return 0.0

        return self.total_collisions / self.total_transmissions