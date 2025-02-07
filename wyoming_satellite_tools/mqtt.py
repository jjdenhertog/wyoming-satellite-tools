#!/usr/bin/env python3
"""Publishes Wyoming events as MQTT messages."""
import argparse
import asyncio
import json
import logging
import random
import socket
import time
from functools import partial

import paho.mqtt.client as mqtt
from paho.mqtt.packettypes import PacketTypes
from paho.mqtt.properties import Properties
from wyoming.event import Event
from wyoming.satellite import (
    SatelliteConnected,
    SatelliteDisconnected,
    StreamingStarted,
    StreamingStopped,
)
from wyoming.server import AsyncEventHandler, AsyncServer
from wyoming.snd import Played
from wyoming.vad import VoiceStarted, VoiceStopped
from wyoming.wake import Detection

_LOGGER = logging.getLogger()


class MQTTEventHandler(AsyncEventHandler):
    """Event handler for publishing Wyoming events to MQTT."""

    def __init__(
        self, mqtt_client: mqtt.Client, satellite_id: str, *args, **kwargs
    ) -> None:

        super().__init__(*args, **kwargs)
        self.mqtt_client = mqtt_client
        self.satellite_id = satellite_id
        self.client_id = str(time.monotonic_ns())

        _LOGGER.debug("Client connected: %s", self.client_id)

    async def handle_event(self, event: Event) -> bool:
        _LOGGER.debug(event)
        payload = json.dumps(
            {"satelliteId": self.satellite_id, "event": event.type, "data": event.data}
        )
        self.mqtt_client.publish("wyoming-satellite/event", payload)

        return True


async def _main() -> None:
    """Internal async main entry point."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--uri", required=True, help="unix:// or tcp://")
    parser.add_argument("--mqtt_host", required=True, help="MQTT broker address")
    parser.add_argument("--mqtt_port", type=int, default=1883, help="MQTT broker port")
    parser.add_argument("--mqtt_username", default="", help="MQTT username")
    parser.add_argument("--mqtt_password", default="", help="MQTT password")
    parser.add_argument("--name", required=True, help="Satellite Name")
    parser.add_argument("--debug", action="store_true", help="Log DEBUG messages")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    _LOGGER.debug(args)

    mqtt_broker = args.mqtt_host
    mqtt_port = args.mqtt_port
    mqtt_username = args.mqtt_username
    mqtt_password = args.mqtt_password

    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqtt_client.username_pw_set(mqtt_username, mqtt_password)
    mqtt_client.connect(mqtt_broker, mqtt_port, 60)
    mqtt_client.loop_start()

    # Start server
    server = AsyncServer.from_uri(args.uri)
    try:
        await server.run(partial(MQTTEventHandler, mqtt_client, args.satellite_id))
    except KeyboardInterrupt:
        pass
    finally:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()


def main() -> None:
    """Entry point for console script."""
    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
