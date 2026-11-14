
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import heapq
import itertools


class EventType(Enum):
    PACKET_GENERATION = "packet_generation"
    TRANSMISSION_START = "transmission_start"
    TRANSMISSION_END = "transmission_end"
    ACK = "ack"
    TIMEOUT = "timeout"
    SLOT_START = "slot_start"
    SLOT_END = "slot_end"


EVENT_PRIORITIES = {
    EventType.SLOT_END: 0,
    EventType.SLOT_START: 1,
    EventType.TRANSMISSION_END: 2,
    EventType.ACK: 3,
    EventType.PACKET_GENERATION: 4,
    EventType.TRANSMISSION_START: 5,
    EventType.TIMEOUT: 6,
}


@dataclass(order=True)
class Event:
    time: float
    priority: int
    sequence: int
    event_type: EventType = field(compare=False)
    node_id: int = field(compare=False, default=-1)
    data: Any = field(compare=False, default=None)


class EventQueue:
    def __init__(self):
        self._events = []
        self._counter = itertools.count()

    def schedule(
        self,
        time: float,
        event_type: EventType,
        node_id: int = -1,
        data: Any = None,
        priority: int = None
    ) -> None:
        if time < 0:
            raise ValueError("Event time cannot be negative.")

        if priority is None:
            priority = EVENT_PRIORITIES.get(event_type, 10)

        event = Event(
            time=time,
            priority=priority,
            sequence=next(self._counter),
            event_type=event_type,
            node_id=node_id,
            data=data
        )

        heapq.heappush(self._events, event)

    def pop(self) -> Event:
        if not self._events:
            raise IndexError("Cannot pop from an empty event queue.")

        return heapq.heappop(self._events)

    def is_empty(self) -> bool:
        return len(self._events) == 0

    def __len__(self) -> int:
        return len(self._events)
    
def test_event_queue_priority_order():
    from simulator.events import EventQueue, EventType

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

