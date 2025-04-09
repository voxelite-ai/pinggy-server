import subprocess
import threading
import re
from typing import Tuple, Pattern
from os import kill
from signal import SIGTERM

from src.app.core.settings import settings
from src.app.core.log import logger

HTTP_URL_RE = re.compile(r"http://\S*pinggy\.link")
HTTPS_URL_RE = re.compile(r"https://\S*pinggy\.link")


def create_tunnel(url: str) -> Tuple[int, str, str]:
    logger.debug(f"Creating tunnel for {url}")
    pinggy_location = ""
    if settings.PINGGY_TOKEN:
        pinggy_location += "{}@".format(settings.PINGGY_TOKEN)
    pinggy_location += "a.pinggy.io"
    command = "ssh -t -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -p 443 -R0:{} {}".format(
        url, pinggy_location
    )
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    def read_output(pipe, output_list):
        for line in iter(pipe.readline, ""):
            output_list.append(line)
        pipe.close()

    stdout_lines = []
    stderr_lines = []

    stdout_thread = threading.Thread(
        target=read_output, args=(process.stdout, stdout_lines)
    )
    stderr_thread = threading.Thread(
        target=read_output, args=(process.stderr, stderr_lines)
    )

    stdout_thread.start()
    stderr_thread.start()

    while not any("pinggy.link" in line for line in stdout_lines):
        if not stdout_thread.is_alive():
            raise RuntimeError(
                "Tunnel creation failed: {}".format("".join(stderr_lines))
            )
        stdout_thread.join(timeout=0.1)

    http_url = extract_url("".join(stdout_lines), HTTP_URL_RE)
    https_url = extract_url("".join(stdout_lines), HTTPS_URL_RE)
    return process.pid, http_url, https_url


def extract_url(output: str, pattern: Pattern) -> str:
    match = re.search(pattern, output)
    if match:
        return match.group(0)
    raise RuntimeError("URL not found in output: {}".format(output))


def terminate_tunnel(pid: int):
    try:
        kill(pid, SIGTERM)
    except ProcessLookupError as e:
        if e.errno == 3:
            logger.warning(f"Process with PID {pid} does not exist.")
        else:
            raise
