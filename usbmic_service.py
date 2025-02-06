#!/usr/bin/env python3
"""Controls the LEDs on the ReSpeaker Mic Array v2.0 (USB) using MQTT."""
import argparse
import asyncio
import logging

import paho.mqtt.client as mqtt
from pixel_ring import pixel_ring

# Setup logging
_LOGGER = logging.getLogger()

# MQTT Topics with "leds" prefix before the area
AREA_PREFIX = "living_room"
MQTT_TOPICS = {
    "detection": f"leds/{AREA_PREFIX}/detection",
    "voice_start": f"leds/{AREA_PREFIX}/voice/start",
    "voice_stop": f"leds/{AREA_PREFIX}/voice/stop",
    "streaming_stop": f"leds/{AREA_PREFIX}/streaming/stop",
    "satellite_connected": f"leds/{AREA_PREFIX}/satellite/connected",
    "satellite_disconnected": f"leds/{AREA_PREFIX}/satellite/disconnected",
    "played": f"leds/{AREA_PREFIX}/played",
    "error": f"leds/{AREA_PREFIX}/error",
    "transcript": f"leds/{AREA_PREFIX}/transcript",
}


# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    """MQTT on_connect callback."""
    if rc == 0:
        _LOGGER.info("Connected to MQTT broker.")
        # Subscribe to all topics for the area
        for topic in MQTT_TOPICS.values():
            client.subscribe(topic)
            _LOGGER.debug(f"Subscribed to topic: {topic}")
    else:
        _LOGGER.error(f"Failed to connect to MQTT broker. Return code: {rc}")


def on_message(client, userdata, msg):
    """MQTT on_message callback."""
    _LOGGER.info(f"Received message: {msg.topic} -> {msg.payload.decode()}")

    # LED Control based on the received topic
    if msg.topic == MQTT_TOPICS["detection"]:
        pixel_ring.wakeup()
    elif msg.topic == MQTT_TOPICS["voice_start"]:
        pixel_ring.speak()
    elif msg.topic == MQTT_TOPICS["voice_stop"]:
        pixel_ring.spin()
    elif msg.topic == MQTT_TOPICS["streaming_stop"]:
        pixel_ring.off()
    elif msg.topic == MQTT_TOPICS["satellite_connected"]:
        pixel_ring.off()
    elif msg.topic == MQTT_TOPICS["satellite_disconnected"]:
        pixel_ring.off()
    elif msg.topic == MQTT_TOPICS["played"]:
        pixel_ring.off()
    elif msg.topic == MQTT_TOPICS["error"]:
        pixel_ring.off()
    elif msg.topic == MQTT_TOPICS["transcript"]:
        pixel_ring.off()


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--broker", required=True, help="MQTT broker address")
    parser.add_argument("--port", type=int, default=1883, help="MQTT broker port")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    _LOGGER.debug(args)

    _LOGGER.info("Initializing LED control")

    # Initialize Pixel Ring
    pixel_ring.set_vad_led(0)
    pixel_ring.set_brightness(0x0A)
    pixel_ring.set_color_palette(0xFF1493, 0xC71585)
    pixel_ring.think()
    await asyncio.sleep(3)
    pixel_ring.off()

    # Configure MQTT client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        # Connect to MQTT broker
        client.connect(args.broker, args.port, 60)

        # Start MQTT client loop in a separate thread
        client.loop_start()

        # Keep script running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        _LOGGER.info("Shutting down.")
    finally:
        client.loop_stop()
        pixel_ring.off()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
