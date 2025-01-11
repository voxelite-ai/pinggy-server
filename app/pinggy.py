import subprocess
import threading
import re
from typing import Tuple

from app.settings import settings

def create_tunnel(url: str) -> Tuple[int, str]:
    pinggy_location = ""
    if settings.PINGGY_TOKEN:
        pinggy_location += "{}@".format(settings.PINGGY_TOKEN)
    pinggy_location += "a.pinggy.io"
    command = "ssh -t -p 443 -R0:{} {}".format(url, pinggy_location)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def read_output(pipe, output_list):
        for line in iter(pipe.readline, ''):
            output_list.append(line)
        pipe.close()

    stdout_lines = []
    stderr_lines = []

    stdout_thread = threading.Thread(target=read_output, args=(process.stdout, stdout_lines))
    stderr_thread = threading.Thread(target=read_output, args=(process.stderr, stderr_lines))

    stdout_thread.start()
    stderr_thread.start()

    while not any("pinggy.link" in line for line in stdout_lines):
        if not stdout_thread.is_alive():
            raise RuntimeError("Tunnel creation failed: {}".format(''.join(stderr_lines)))
        stdout_thread.join(timeout=0.1)

    public_url = extract_public_url(''.join(stdout_lines))
    return process.pid, public_url

def extract_public_url(output: str) -> str:
    match = re.search(r'http://\S*pinggy\.link', output)
    if match:
        return match.group(0)
    raise RuntimeError("Public URL not found in the output")

def terminate_tunnel(pid: int):
    process = subprocess.Popen(['kill', str(pid)])
    process.wait()