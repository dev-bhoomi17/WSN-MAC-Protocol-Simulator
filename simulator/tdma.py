from simulator.nodes import NodeState


class TDMAScheduler:
    def __init__(
        self,
        nodes,
        slot_duration=0.05,
        sleep_enabled=True
    ):
        if slot_duration <= 0:
            raise ValueError("Slot duration must be positive.")

        self.nodes = nodes
        self.slot_duration = slot_duration
        self.sleep_enabled = sleep_enabled
        self.frame_duration = len(nodes) * slot_duration

        self.slot_assignments = {
            node.node_id: index
            for index, node in enumerate(nodes)
        }

    def get_slot(self, node_id):
        if node_id not in self.slot_assignments:
            raise ValueError("Unknown node ID.")

        return self.slot_assignments[node_id]

    def get_transmission_time(self, node_id, frame_number):
        slot = self.get_slot(node_id)

        return (
            frame_number * self.frame_duration
            + slot * self.slot_duration
        )

    def update_node_states(self, current_time):
        if not self.nodes:
            return

        frame_position = current_time % self.frame_duration
        active_slot = int(frame_position // self.slot_duration)

        for node in self.nodes:
            assigned_slot = self.get_slot(node.node_id)

            if assigned_slot == active_slot:
                node.state = NodeState.ACTIVE
            elif self.sleep_enabled:
                node.state = NodeState.SLEEP
            else:
                node.state = NodeState.ACTIVE

    def get_active_node(self, current_time):
        if not self.nodes:
            return None

        frame_position = current_time % self.frame_duration
        active_slot = int(frame_position // self.slot_duration)

        for node in self.nodes:
            if self.get_slot(node.node_id) == active_slot:
                return node

        return None