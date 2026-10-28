"""Docker execution with no application mounts, secrets or network access.

This module deliberately has no dependency on the web app's configuration or DB.
It is also used by the standalone authenticated runner on a Docker-capable host.
"""
import json
import os
import selectors
import signal
import subprocess
import tempfile
import time
from uuid import uuid4

MAX_RESPONSE_BYTES = 2_000_000


class ContainerUnavailable(Exception):
    pass


# Runs inside the disposable container. Source enters through stdin, never a host mount.
BOOTSTRAP = r'''
import base64, json, pathlib, stat, subprocess, sys
job = json.load(sys.stdin)
root = pathlib.Path('/work')
(root / 'solution.py').write_text(job['code'], encoding='utf-8')
timed_out = False
with open('/work/stdout', 'w+b') as out, open('/work/stderr', 'w+b') as err:
    try:
        result = subprocess.run([sys.executable, '-I', '-B', '/work/solution.py'],
            input=job['stdin'].encode(), stdout=out, stderr=err, timeout=job['timeout'])
        error = result.returncode != 0
    except subprocess.TimeoutExpired:
        timed_out, error = True, False
    def read_output(file):
        file.seek(0)
        value = file.read(80001).decode('utf-8', errors='replace')
        return value[:20000] + ('\n... output truncated ...' if len(value) > 20000 else '')
    stdout, stderr = read_output(out), read_output(err)
images = []
for path in sorted(root.glob('*.png')):
    if len(images) == 3:
        break
    try:
        info = path.lstat()
        if stat.S_ISREG(info.st_mode) and info.st_size <= 400000:
            images.append('data:image/png;base64,' + base64.b64encode(path.read_bytes()).decode())
    except OSError:
        pass
print(json.dumps(dict(stdout=stdout, stderr=stderr, timed_out=timed_out, error=error, images=images)))
'''


def _remove_container(name):
    try:
        subprocess.run(["docker", "rm", "-f", name], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        pass


def execute_in_container(code, stdin, *, image, timeout):
    name = "pylearn-job-" + uuid4().hex
    command = [
        "docker", "run", "--pull=never", "--rm", "--name", name, "--init", "-i",
        "--network=none", "--ipc=none", "--read-only",
        "--cap-drop=ALL", "--security-opt=no-new-privileges", "--user=65534:65534",
        "--memory=256m", "--memory-swap=256m", "--cpus=0.5", "--pids-limit=32",
        "--ulimit", "nofile=64:64", "--ulimit", "fsize=2097152:2097152",
        "--ulimit", f"cpu={timeout + 2}:{timeout + 2}",
        "--tmpfs", "/work:rw,nosuid,nodev,noexec,size=16m,mode=1777",
        "--tmpfs", "/tmp:rw,nosuid,nodev,noexec,size=16m,mode=1777", "--workdir=/work",
        "--env=HOME=/tmp", "--env=MPLCONFIGDIR=/tmp/matplotlib", "--env=MPLBACKEND=Agg",
        "--env=OPENBLAS_NUM_THREADS=1", "--env=OMP_NUM_THREADS=1",
        image, "python", "-I", "-B", "-c", BOOTSTRAP,
    ]
    process = None
    try:
        with tempfile.TemporaryFile() as input_file:
            input_file.write(json.dumps({"code": code, "stdin": stdin, "timeout": timeout}).encode())
            input_file.seek(0)
            process = subprocess.Popen(command, stdin=input_file, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, start_new_session=True)
            output = bytearray()
            deadline = time.monotonic() + timeout + 8
            with selectors.DefaultSelector() as selector:
                selector.register(process.stdout, selectors.EVENT_READ)
                while True:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        return {"stdout": "", "stderr": "", "timed_out": True, "error": False, "images": []}
                    if not selector.select(remaining):
                        continue
                    chunk = os.read(process.stdout.fileno(), 65536)
                    if not chunk:
                        break
                    output.extend(chunk)
                    if len(output) > MAX_RESPONSE_BYTES:
                        return {"stdout": "", "stderr": "Execution output exceeded the limit.",
                                "timed_out": False, "error": True, "images": []}
            process.wait(timeout=max(0.1, deadline - time.monotonic()))
            if process.returncode:
                raise ContainerUnavailable("The isolated runner could not start. Check Docker and the sandbox image.")
            return json.loads(output)
    except (OSError, ValueError, RecursionError, subprocess.TimeoutExpired):
        raise ContainerUnavailable("The isolated runner is unavailable.") from None
    finally:
        # Killing the CLI alone leaves Docker workloads running. Always remove by name.
        _remove_container(name)
        if process is not None:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            process.stdout.close()
