import asyncio
import os
import sys

sys.path.insert(0, os.getcwd())
from models import CybergymIncidentsOctAction, CybergymIncidentsOctObservation  # noqa: E402

from client import CybergymIncidentsOctEnv  # noqa: E402

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
INDEX = int(sys.argv[2]) if len(sys.argv) > 2 else 0
POC = os.environ.get("SMOKE_POC", "A" * 64)
HARD_ANSWER = sys.argv[3] if len(sys.argv) > 3 else None


async def main():
    client = CybergymIncidentsOctEnv(base_url=URL)
    await client.connect()
    result = await client.reset(seed=1, split="train", index=INDEX)
    task = result.observation.task_id
    assert task, "no task after reset"
    result = await client.step(CybergymIncidentsOctAction(cmd="ls -la"))
    assert result.observation.output, "no output from ls"
    result = await client.step(CybergymIncidentsOctAction(cmd="cat challenge.txt"))
    assert "submit" in result.observation.output.lower(), "challenge text missing"
    if HARD_ANSWER:
        result = await client.reset(seed=2, split="train", index=5)
        print("hard task:", result.observation.task_id)
        php = ("nohup php -S 127.0.0.1:8099 -t www >/dev/null 2>&1 & sleep 1.5; "
                "curl -s --get --data-urlencode 'render=file_get_contents(" + chr(34) + "secret.php" + chr(34) + ")' "
                "http://127.0.0.1:8099/index.php")
        result = await client.step(CybergymIncidentsOctAction(cmd=php))
        print("php-solve output:", (result.observation.output or "")[:200])
        result = await client.step(CybergymIncidentsOctAction(answer=HARD_ANSWER))
        print(f"hard task={task} reward={result.reward}")
        await client.close()
        sys.exit(0 if result.reward == 1.0 else 1)
    result = await client.step(CybergymIncidentsOctAction(answer=POC))
    print(f"task={task} reward={result.reward} done={result.done}")
    print((result.observation.output or "")[:300])
    await client.close()
    sys.exit(0 if result.done else 1)


asyncio.run(main())
