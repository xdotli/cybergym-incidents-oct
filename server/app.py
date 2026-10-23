# SPDX-License-Identifier: BSD-3-Clause
"""FastAPI app for cybergym_crash_poc."""

try:
    from openenv.core.env_server.http_server import create_app
except Exception as e:  # pragma: no cover
    raise ImportError("openenv is required; install dependencies first") from e

try:
    from ..models import CybergymIncidentsOctAction, CybergymIncidentsOctObservation
    from .cybergym_incidents_oct_environment import CybergymIncidentsOctEnvironment
except ImportError:
    from models import CybergymIncidentsOctAction, CybergymIncidentsOctObservation
    from server.cybergym_incidents_oct_environment import CybergymIncidentsOctEnvironment

app = create_app(
    CybergymIncidentsOctEnvironment,
    CybergymIncidentsOctAction,
    CybergymIncidentsOctObservation,
    env_name="cybergym_incidents_oct",
    max_concurrent_envs=8,
)

def main(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn

    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()
