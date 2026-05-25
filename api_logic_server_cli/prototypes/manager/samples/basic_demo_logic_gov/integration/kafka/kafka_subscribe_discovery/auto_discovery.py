"""
Kafka Topic Handler Discovery
==============================
Mirrors the logic_discovery pattern for Kafka consumers.

Scans this directory for *.py files (excluding auto_discovery.py and __init__.py),
imports each one, and calls module.register(bus) to wire up @bus.handle decorators.

Usage (in kafka_consumer.py — called before bus.run()):

    from integration.kafka.kafka_subscribe_discovery.auto_discovery import discover_topic_handlers
    discover_topic_handlers(bus)

Each topic file must expose a single function:

    def register(bus):
        @bus.handle('my_topic')
        def my_topic(msg, safrs_api):
            ...

Drop a new file here to add a Kafka consumer — no edits to kafka_consumer.py required.
"""

import importlib.util
import logging
import os
from pathlib import Path

logger = logging.getLogger('integration.kafka')


def discover_topic_handlers(bus) -> list:
    """
    Discover and register all topic handlers in this directory.

    Args:
        bus: FlaskKafka instance — passed to each module's register(bus) function.

    Returns:
        List of discovered module filenames (for logging).
    """
    discovered = []
    discovery_path = Path(__file__).parent

    for root, dirs, files in os.walk(discovery_path):
        root_path = Path(root)
        for file in sorted(files):      # sorted for deterministic load order
            if not file.endswith('.py'):
                continue
            if file in ('auto_discovery.py', '__init__.py'):
                continue
            file_path = root_path / file
            spec = importlib.util.spec_from_file_location('kafka_topic.' + file[:-3], file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, 'register'):
                module.register(bus)
                discovered.append(file)
                logger.debug(f'kafka_subscribe_discovery: registered {file}')
            else:
                logger.warning(f'kafka_subscribe_discovery: {file} has no register(bus) function — skipped')

    logger.info(f'kafka_subscribe_discovery: discovered topic handlers: {discovered}')
    return discovered
