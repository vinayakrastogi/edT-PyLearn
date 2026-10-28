import importlib
import os
import subprocess

from fastapi.testclient import TestClient
import pytest


@pytest.fixture
def runner(monkeypatch):
    monkeypatch.setenv("SANDBOX_RUNNER_KEY", "test-runner-key-" + "x" * 32)
    from runner import app
    return importlib.reload(app)


def test_runner_requires_key_and_bounds_job_input(runner, monkeypatch):
    monkeypatch.setattr(runner, "execute_in_container", lambda *args, **kwargs: {
        "stdout": "2\n", "stderr": "", "error": False, "timed_out": False, "images": []})
    with TestClient(runner.app) as client:
        assert client.post("/execute", json={"code": "print(2)"}).status_code == 401
        headers = {"X-Runner-Key": runner.KEY}
        assert client.post("/execute", headers=headers, json={"code": "print(2)"}).json()["stdout"] == "2\n"
        assert client.post("/execute", headers=headers, json={"code": "", "timeout": 100}).status_code == 422
        assert client.post("/execute", headers=headers, json={"code": "x" * 40001}).status_code == 422


@pytest.mark.skipif(os.environ.get("RUN_SANDBOX_INTEGRATION") != "1", reason="Needs local Docker and sandbox image")
def test_real_runner_isolates_network_files_secrets_and_cleans_timeouts(runner):
    with TestClient(runner.app) as client:
        headers = {"X-Runner-Key": runner.KEY}
        def run(code, stdin="", timeout=5):
            response = client.post("/execute", headers=headers,
                                   json={"code": code, "stdin": stdin, "timeout": timeout})
            assert response.status_code == 200, response.text
            return response.json()
        assert run("print('Hello', input())", "Ada\n")["stdout"].strip() == "Hello Ada"
        result = run("import numpy as np\nimport pandas as pd\nimport matplotlib.pyplot as plt\n"
                     "print(int(np.array([1,2,3]).sum()))\nplt.plot([1,2]);plt.savefig('chart.png')")
        assert result["stdout"].strip() == "6" and result["images"][0].startswith("data:image/png;base64,")
        result = run("import os, socket\nprint(os.getuid())\nprint(os.getenv('SANDBOX_RUNNER_KEY'))\n"
                     "print(os.path.exists('/app/backend/.env'))\n"
                     "try:\n open('/etc/forbidden', 'w')\nexcept OSError:\n print('read-only')\n"
                     "try:\n socket.create_connection(('1.1.1.1',443), timeout=1)\n"
                     "except OSError:\n print('network-blocked')")
        assert result["stdout"].splitlines() == ["65534", "None", "False", "read-only", "network-blocked"]
        assert run("while True: pass", timeout=1)["timed_out"]
    remaining = subprocess.check_output(["docker", "ps", "-aq", "--filter", "name=pylearn-job-"]).strip()
    assert remaining == b""
