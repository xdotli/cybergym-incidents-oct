# SPDX-License-Identifier: BSD-3-Clause
"""Client for the cybergym_crash_poc environment (WebSocket session)."""

from typing import Dict

from openenv.core import EnvClient
from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State

try:
    from .models import CybergymIncidentsOctAction, CybergymIncidentsOctObservation
except ImportError:
    from models import CybergymIncidentsOctAction, CybergymIncidentsOctObservation


class CybergymIncidentsOctEnv(EnvClient[CybergymIncidentsOctAction, CybergymIncidentsOctObservation, State]):
    """Persistent WebSocket client; one instance is one dedicated episode session."""

    def _step_payload(self, action: CybergymIncidentsOctAction) -> Dict:
        payload: Dict = {}
        if action.cmd:
            payload["cmd"] = action.cmd
        if action.answer:
            payload["answer"] = action.answer
        return payload

    def _parse_result(self, payload: Dict) -> StepResult[CybergymIncidentsOctObservation]:
        obs_data = payload.get("observation", {})
        observation = CybergymIncidentsOctObservation(
            task_id=obs_data.get("task_id", ""),
            challenge=obs_data.get("challenge", ""),
            output=obs_data.get("output", ""),
            message=obs_data.get("message", ""),
            steps_left=obs_data.get("steps_left", 0),
            done=payload.get("done", False),
            reward=payload.get("reward") or 0.0,
        )
        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", False),
            metadata=payload.get("metadata"),
        )

    def _parse_state(self, payload: Dict) -> State:
        return State(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
        )
