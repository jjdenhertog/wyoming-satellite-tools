#!/usr/bin/env python3
"""Controls the LEDs on the ReSpeaker Mic Array v2.0 (USB) using MQTT."""
import argparse
import asyncio
import json
import logging

import paho.mqtt.client as mqtt
from pixel_ring import pixel_ring

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


def on_connect(client, userdata, flags, rc):
    """MQTT on_connect callback."""
    if rc == 0:
        _LOGGER.info("Connected to MQTT broker")
        # Subscribe to all topics
        for topic in MQTT_TOPICS.values():
            client.subscribe(topic)
            _LOGGER.debug("Subscribed to topic: %s", topic)
    else:
        _LOGGER.error("Failed to connect to MQTT broker with code: %d", rc)


def on_message(client, userdata, msg):
    """MQTT on_message callback."""
    try:
        payload = json.loads(msg.payload.decode())
        satellite_id = payload.get("satelliteId")

        # Only process messages for our satellite ID
        if satellite_id != userdata["satellite_id"]:
            return

        _LOGGER.debug("Received message: %s -> %s", msg.topic, payload)

        if msg.topic == MQTT_TOPICS["detection"]:
            pixel_ring.wakeup()
        elif msg.topic == MQTT_TOPICS["voice_started"]:
            pixel_ring.speak()
        elif msg.topic == MQTT_TOPICS["voice_stopped"]:
            pixel_ring.spin()
        elif msg.topic == MQTT_TOPICS["streaming_stopped"]:
            pixel_ring.off()
        elif msg.topic == MQTT_TOPICS["connected"]:
            pixel_ring.think()
            asyncio.get_event_loop().create_task(turn_off_after_delay(2))
        elif msg.topic == MQTT_TOPICS["disconnected"]:
            pixel_ring.off()
        elif msg.topic == MQTT_TOPICS["played"]:
            pixel_ring.off()

    except json.JSONDecodeError:
        _LOGGER.error("Failed to decode JSON payload")
    except Exception as e:
        _LOGGER.error("Error processing message: %s", str(e))


async def turn_off_after_delay(delay):
    """Turn off LEDs after delay."""
    await asyncio.sleep(delay)
    pixel_ring.off()


async def _main() -> None:
    """Internal async main entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--broker", required=True, help="MQTT broker address")
    parser.add_argument("--port", type=int, default=1883, help="MQTT broker port")
    parser.add_argument(
        "--satellite-id", default="living_room", help="Satellite ID to respond to"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    _LOGGER.debug(args)

    # Initialize LED ring
    pixel_ring.set_vad_led(0)
    pixel_ring.set_brightness(0x0A)
    pixel_ring.set_color_palette(0xFF1493, 0xC71585)
    pixel_ring.think()
    await asyncio.sleep(3)
    pixel_ring.off()

    # Configure MQTT client
    client = mqtt.Client(userdata={"satellite_id": args.satellite_id})
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(args.broker, args.port, 60)
        client.loop_start()

        # Keep script running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        _LOGGER.info("Shutting down")
    finally:
        client.loop_stop()
        client.disconnect()
        pixel_ring.off()


def main() -> None:
    """Entry point for console script."""
    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
