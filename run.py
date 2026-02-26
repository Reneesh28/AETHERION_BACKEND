import subprocess
import sys
import os
import signal

processes = []


def start_service(command, cwd):
    return subprocess.Popen(command, cwd=cwd)


def shutdown_all(signum, frame):
    print("\nShutting down all services...")
    for p in processes:
        p.terminate()
    sys.exit(0)


if __name__ == "__main__":

    signal.signal(signal.SIGINT, shutdown_all)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    python_executable = sys.executable  # 🔥 THIS FORCES VENV PYTHON

    django_dir = os.path.join(base_dir, "django_core")
    flask_dir = os.path.join(base_dir, "flask_regime")

    print("Starting Django on 8000...")
    processes.append(
        start_service(
            [python_executable, "manage.py", "runserver", "8000"],
            django_dir,
        )
    )

    print("Starting FastAPI on 8001...")
    processes.append(
        start_service(
            [
                python_executable,
                "-m",
                "uvicorn",
                "fastapi_market.main:app",
                "--reload",
                "--port",
                "8001",
            ],
            base_dir,
        )
    )

    print("Starting Flask Regime Engine on 8002...")
    processes.append(
        start_service(
            [python_executable, "app.py"],
            flask_dir,
        )
    )

    print("\nAll services started.")
    print("Press CTRL+C to stop all.\n")

    for p in processes:
        p.wait()