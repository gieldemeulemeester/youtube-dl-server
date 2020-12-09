import os

class ContainerClient:
    def __init__(self):
        self.container_id = os.environ['HOSTNAME']
        self.memory_limit = self.serialize_bytes(int(open("/sys/fs/cgroup/memory/memory.limit_in_bytes", "r").read()))

    def get_memory_used(self) -> str:
        return self.serialize_bytes(int(open("/sys/fs/cgroup/memory/memory.usage_in_bytes", "r").read()))

    def serialize_bytes(self, value_in_bytes: int) -> str:
        return "{:.1f}".format(value_in_bytes/1048576).rstrip('0').rstrip('.') + " MiB"
