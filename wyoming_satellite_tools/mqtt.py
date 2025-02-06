#!/usr/bin/env python3
"""Publishes Wyoming events as MQTT messages."""
import argparse
import asyncio
import json
import logging
import socket
import time
from functools import partial

import paho.mqtt.client as mqtt
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

MQTT_TOPIC_PREFIX = "wyoming-satellite"
MQTT_TOPICS = {
    "detection": f"{MQTT_TOPIC_PREFIX}/detection",
    "voice_started": f"{MQTT_TOPIC_PREFIX}/voice_started",
    "voice_stopped": f"{MQTT_TOPIC_PREFIX}/voice_stopped",
    "streaming_started": f"{MQTT_TOPIC_PREFIX}/streaming_started",
    "streaming_stopped": f"{MQTT_TOPIC_PREFIX}/streaming_stopped",
    "connected": f"{MQTT_TOPIC_PREFIX}/connected",
    "disconnected": f"{MQTT_TOPIC_PREFIX}/disconnected",
    "played": f"{MQTT_TOPIC_PREFIX}/played",
}


class MQTTEventHandler(AsyncEventHandler):
    """Event handler for publishing Wyoming events to MQTT."""

    def __init__(
        self,
        mqtt_client: mqtt.Client,
        satellite_id: str,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.mqtt_client = mqtt_client
        self.satellite_id = satellite_id
        self.client_id = str(time.monotonic_ns())
        _LOGGER.debug("Client connected: %s", self.client_id)

    async def handle_event(self, event: Event) -> bool:
        _LOGGER.debug(event)
        payload = json.dumps({"satelliteId": self.satellite_id})

        if Detection.is_type(event.type):
            self.mqtt_client.publish(MQTT_TOPICS["detection"], payload)
        elif VoiceStarted.is_type(event.type):
            self.mqtt_client.publish(MQTT_TOPICS["voice_started"], payload)
        elif VoiceStopped.is_type(event.type):
            self.mqtt_client.publish(MQTT_TOPICS["voice_stopped"], payload)
        elif StreamingStarted.is_type(event.type):
            self.mqtt_client.publish(MQTT_TOPICS["streaming_started"], payload)
        elif StreamingStopped.is_type(event.type):
            self.mqtt_client.publish(MQTT_TOPICS["streaming_stopped"], payload)
        elif SatelliteConnected.is_type(event.type):
            self.mqtt_client.publish(MQTT_TOPICS["connected"], payload)
        elif Played.is_type(event.type):
            self.mqtt_client.publish(MQTT_TOPICS["played"], payload)
        elif SatelliteDisconnected.is_type(event.type):
            self.mqtt_client.publish(MQTT_TOPICS["disconnected"], payload)

        return True


async def _main() -> None:
    """Internal async main entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--uri", required=True, help="unix:// or tcp://")
    parser.add_argument("--broker", required=True, help="MQTT broker address")
    parser.add_argument("--port", type=int, default=1883, help="MQTT broker port")
    parser.add_argument("--satellite-id", default="living_room", help="Satellite ID")
    parser.add_argument("--debug", action="store_true", help="Log DEBUG messages")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    _LOGGER.debug(args)

    # Configure MQTT client
    mqtt_client = mqtt.Client(protocol=mqtt.MQTTv5)  # Use MQTT v5 protocol

    try:
        mqtt_client.connect(args.broker, args.port, 60)
    except (ConnectionRefusedError, socket.gaierror) as err:
        _LOGGER.error(
            "Failed to connect to MQTT broker at %s:%d - %s",
            args.broker,
            args.port,
            str(err),
        )
        return
    except Exception as err:
        _LOGGER.error("Unexpected error connecting to MQTT broker: %s", str(err))
        return

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
