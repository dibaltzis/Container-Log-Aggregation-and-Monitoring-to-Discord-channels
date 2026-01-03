import docker
import threading
from datetime import datetime

class LogEntry:
    """Represents one log line with timestamp + message."""
    def __init__(self, raw_line: str):
        self.message = raw_line.strip()

    def __repr__(self):
        return f"{self.message}"


class ContainerLogs:
    def __init__(self, container, callback=None):
        self.container = container
        self.name = container.name
        self.callback = callback
        self._stop_flag = False
        self._thread = None

    def start_stream(self):
        """Start streaming logs from the container in a background thread."""
        def stream():
            try:
                for line in self.container.logs(
                    stream=True, follow=True, timestamps=True, since=int(datetime.now().timestamp())
                ):
                    if self._stop_flag:
                        break
                    entry = LogEntry(line.decode("utf-8", errors="replace").strip())
                    if self.callback:
                        self.callback(entry)
            except Exception as e:
                print(f"[ERROR] {self.name}: {e}")

        self._stop_flag = False
        self._thread = threading.Thread(target=stream, daemon=True)
        self._thread.start()

    def stop_stream(self):
        """Stop streaming logs and join the thread."""
        self._stop_flag = True
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)

class DockerMonitor:
    def __init__(self, base_url):
        self.client = docker.DockerClient(base_url=base_url)
        self.containers = {}  # name -> ContainerLogs

    def add_container(self, name_or_id, callback=None):
        """Start monitoring a container's logs, restart if needed."""
        try:
            container = self.client.containers.get(name_or_id)
        except docker.errors.NotFound:
            print(f"[WARN] Container not found: {name_or_id}")
            return

        existing_log = self.containers.get(container.name)
        if existing_log:
            if existing_log.container.id != container.id:
                # Container restarted: stop old stream and replace it
                existing_log.stop_stream()
            else:
                # Already monitoring the same container
                return

        # Create new log stream
        log_obj = ContainerLogs(container, callback=callback)
        self.containers[container.name] = log_obj
        log_obj.start_stream()


