#!/usr/bin/env python3
"""Controls the LEDs on the ReSpeaker Mic Array v2.0 (USB) using MQTT."""
import argparse
import asyncio
import json
import logging

import paho.mqtt.client as mqtt
from pixel_ring import pixel_ring

_LOGGER = logging.getLogger()


def on_connect(client, userdata, flags, reason_code, properties):
    """MQTT on_connect callback."""
    if reason_code == 0:
        _LOGGER.info("Connected to MQTT broker")

        client.subscribe("wyoming-satellite/event")
        _LOGGER.debug("Subscribed to topic: wyoming-satellite/event")
    else:
        _LOGGER.error("Failed to connect to MQTT broker with code: %d", rc)


def on_message(client, userdata, msg):
    """MQTT on_message callback."""
    try:
        payload = json.loads(msg.payload.decode())
        name = payload.get("name")
        event = payload.get("event")
        data = payload.get("data")

        if name != userdata["satellite_name"]:
            return

        # _LOGGER.debug("Received message: %s -> %s", msg.topic, payload)

        if event == "connected":
            pixel_ring.think()
            asyncio.get_event_loop().create_task(turn_off_after_delay(2))
        elif event == "disconnected":
            pixel_ring.off()
        elif event == "detection":
            logging.debug("Wake-word detected")
            # pixel_ring.wakeup()
            pixel_ring.think()
            asyncio.get_event_loop().create_task(turn_off_after_delay(2))
        elif event == "voice-started":
            # Recording stopped
            logging.debug("Speech detection: started")
        elif event == "voice-stopped":
            # Recording stopped
            logging.debug("Speech detection: stopped")
        elif event == "streaming-started":
            # Recording stopped
            logging.debug("Streaming audio: started")
        elif event == "streaming-stopped":
            # Recording stopped
            logging.debug("Streaming audio: stopped")
            pixel_ring.off()
        elif event == "transcript":
            # STT completed
            logging.debug("STT completed")
        elif event == "audio-start":
            pixel_ring.off()
        elif event == "audio-stop":
            pixel_ring.off()
        elif event == "played":
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

    parser.add_argument("--mqtt_host", required=True, help="MQTT broker address")
    parser.add_argument("--mqtt_port", type=int, default=1883, help="MQTT broker port")
    parser.add_argument("--mqtt_username", default="", help="MQTT username")
    parser.add_argument("--mqtt_password", default="", help="MQTT password")
    parser.add_argument("--name", required=True, help="Satellite Name")
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
    mqtt_broker = args.mqtt_host
    mqtt_port = args.mqtt_port
    mqtt_username = args.mqtt_username
    mqtt_password = args.mqtt_password

    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqtt_client.username_pw_set(mqtt_username, mqtt_password)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.user_data_set({"satellite_name": args.name})

    try:
        mqtt_client.connect(mqtt_broker, mqtt_port, 60)
        mqtt_client.loop_start()

        # Keep script running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        _LOGGER.info("Shutting down")
    finally:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        pixel_ring.off()


def main() -> None:
    """Entry point for console script."""
    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
