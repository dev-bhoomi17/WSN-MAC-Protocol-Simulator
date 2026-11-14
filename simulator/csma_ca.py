import random


class CSMA_CA:
    def __init__(
        self,
        channel,
        min_backoff=0.001,
        max_backoff=0.01,
        max_retries=4,
        seed=42
    ):
        if min_backoff < 0 or max_backoff < min_backoff:
            raise ValueError("Invalid backoff interval.")

        if max_retries < 0:
            raise ValueError("Maximum retries cannot be negative.")

        self.channel = channel
        self.min_backoff = min_backoff
        self.max_backoff = max_backoff
        self.max_retries = max_retries
        self.random = random.Random(seed)

        self.successful_transmissions = 0
        self.failed_transmissions = 0

    def get_backoff_time(self):
        return self.random.uniform(
            self.min_backoff,
            self.max_backoff
        )

    def can_transmit(self, current_time):
        return not self.channel.is_busy(current_time)

    def transmit(self, node_id, packet_id, current_time, duration):
        for attempt in range(self.max_retries + 1):
            backoff = self.get_backoff_time()
            transmission_time = current_time + backoff

            if self.channel.is_busy(transmission_time):
                current_time = transmission_time
                continue

            transmission = self.channel.start_transmission(
                node_id=node_id,
                packet_id=packet_id,
                start_time=transmission_time,
                duration=duration
            )

            if transmission.collided:
                current_time = transmission.end_time
                continue

            self.successful_transmissions += 1
            return transmission

        self.failed_transmissions += 1
        return None