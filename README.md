# Wyoming Satellite Tools

A collection of tools for Wyoming satellites that provides:
1. A Wyoming event to MQTT bridge - publishes satellite events to MQTT
2. An LED controller for ReSpeaker Mic Array v2.0 that responds to MQTT messages

## Use Cases

- Monitor Wyoming satellite events for home automation (via MQTT)
- Synchronize LED behavior across multiple satellites (e.g., all satellites in a room light up when any one detects a wake word)

## Installation

```bash
./script/setup
```

## Usage

### 1. Start the MQTT Publisher

This service listens for Wyoming events and publishes them as MQTT messages. When starting the wyoming-satellite you can add the event-uri using `--event-uri 'tcp://127.0.0.1:10800'`. 

```bash
script/run_mqtt \
    --uri 'tcp://127.0.0.1:10800' \
    --name 'living_room' \
    --mqtt_host 'ip-to-your-mqtt-broker' \
    --mqtt_username 'username (optional)' \
    --mqtt_password 'password (optional)' \
    --debug
```

### 2. Start the LED Controller

This service listens for MQTT messages and controls the ReSpeaker LEDs. The `--name` is used to filter out any events that are not belonging to the satellite. 

```bash
script/run_led \
    --mqtt_host 'ip-to-your-mqtt-broker' \
    --mqtt_username 'username (optional)' \
    --mqtt_password 'password (optional)' \
    --name 'living_room' \
    --debug
```

## MQTT Messages

The service publishes to `wyoming-satellite/event` with JSON payloads containing:
```json
{
    "name": "living_room",
    "event": "event_type",
    "data": {}
}
```

Supported events:
- `connected` - Satellite connected
- `disconnected` - Satellite disconnected
- `detection` - Wake word detected
- `voice-started` - Voice activity started
- `voice-stopped` - Voice activity stopped
- `streaming-started` - Audio streaming started
- `streaming-stopped` - Audio streaming stopped
- `audio-start` - Audio playback started
- `audio-stop` - Audio playback stopped
- `played` - Audio playback completed

## Command Line Options

### MQTT Publisher (wyoming-satellite-tools-mqtt)
- `--uri` - Wyoming server URI (required)
- `--mqtt_host` - MQTT broker address (required)
- `--mqtt_port` - MQTT broker port (default: 1883)
- `--mqtt_username` - MQTT username
- `--mqtt_password` - MQTT password
- `--name` - Satellite name (required)
- `--debug` - Enable debug logging

### LED Controller (wyoming-satellite-tools-led)
- `--mqtt_host` - MQTT broker address (required)
- `--mqtt_port` - MQTT broker port (default: 1883)
- `--mqtt_username` - MQTT username
- `--mqtt_password` - MQTT password
- `--name` - Satellite name to respond to (required)
- `--debug` - Enable debug logging

## LED Behaviors (ReSpeaker Mic Array v2.0)

The LED ring responds to events as follows:
- Satellite connected: Think pattern (turns off after 2 seconds)
- Satellite disconnected: LEDs off
- Wake word detection: Think pattern
- Voice activity started: Status update only
- Voice activity stopped: Status update only
- Streaming started: Status update only
- Streaming stopped: LEDs off
- Audio start: Wakeup pattern
- Audio stop: LEDs off
- Audio played: LEDs off

## Requirements

- Python 3.7 or later
- ReSpeaker Mic Array v2.0 (for LED control)
- MQTT broker
- Wyoming satellite service
