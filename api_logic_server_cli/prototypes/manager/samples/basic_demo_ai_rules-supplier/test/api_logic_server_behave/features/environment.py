"""
Behave hooks, shared by every project.

* times each scenario -> logs/scenario_times.json (seconds), which the Requirements Traceability Report shows
  next to each scenario (the whole run's time is written into behave.log by behave_run.py)
* forgets the previous run's records, so the report reads only this run:
    logs/scenario_times.json
    logs/delivery_modes.json   (how Kafka messages were delivered, 'live' or 'simulated': written by the steps of
                                projects with a Kafka subscribe pipeline; see docs/training/testing.md, Step 1d)
"""
import json
import time
from pathlib import Path

LOGS = Path(__file__).resolve().parent.parent / 'logs'
TIMES_FILE = LOGS / 'scenario_times.json'
RECORD_FILES = (TIMES_FILE, LOGS / 'delivery_modes.json')

_times = {}


def before_all(context):
    _times.clear()
    for each in RECORD_FILES:
        if each.is_file():
            each.unlink()


def before_scenario(context, scenario):
    context.scenario_started = time.perf_counter()


def after_scenario(context, scenario):
    started = getattr(context, 'scenario_started', None)
    if started is None:
        return
    _times[f'{scenario.feature.name} / {scenario.name}'] = round(time.perf_counter() - started, 3)
    LOGS.mkdir(parents=True, exist_ok=True)
    TIMES_FILE.write_text(json.dumps(_times, indent=2))
