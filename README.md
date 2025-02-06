# Wyoming LED Service

Control ReSpeaker Mic Array v2.0 LEDs using Wyoming events via MQTT. This package provides two services:
1. A Wyoming event to MQTT bridge
2. An LED controller that responds to MQTT messages

## Installation

```bash
./script/setup
```

## Usage

### 1. Start the MQTT Publisher

This service listens for Wyoming events and publishes them as MQTT messages:

```bash
script/run_mqtt \
    --uri 'tcp://127.0.0.1:10800' \
    --broker 'mqtt://mqtt:mqtt@192.168.50.174:1883)' \
    --satellite-id 'living_room'
```

### 2. Start the LED Controller

This service listens for MQTT messages and controls the ReSpeaker LEDs:

```bash
wyoming-satellite-tools-control \
    --broker localhost \
    --satellite-id living_room
```

## MQTT Topics

The service publishes to the following topics under `wyoming-satellite/`:
- `detection` - Wake word detected
- `voice_started` - Voice activity started
- `voice_stopped` - Voice activity stopped
- `streaming_started` - Audio streaming started
- `streaming_stopped` - Audio streaming stopped
- `connected` - Satellite connected
- `disconnected` - Satellite disconnected
- `played` - Audio playback completed

Each message contains a JSON payload with the satellite ID:
```json
{
    "satelliteId": "living_room"
}
```

## Command Line Options

### MQTT Publisher (wyoming-satellite-tools-mqtt)
- `--uri` - Wyoming server URI (required, e.g., unix:///path/to/socket)
- `--broker` - MQTT broker address (required)
- `--port` - MQTT broker port (default: 1883)
- `--satellite-id` - Satellite ID (default: living_room)
- `--debug` - Enable debug logging

### LED Controller (wyoming-satellite-tools-control)
- `--broker` - MQTT broker address (required)
- `--port` - MQTT broker port (default: 1883)
- `--satellite-id` - Satellite ID to respond to (default: living_room)
- `--debug` - Enable debug logging

## LED Behaviors

The ReSpeaker LED ring responds to events as follows:
- Wake word detection: Wakeup pattern
- Voice activity: Speaking pattern
- Voice stopped: Spin pattern
- Satellite connected: Think pattern (turns off after 2 seconds)
- Streaming stopped: LEDs off
- Satellite disconnected: LEDs off
- Audio played: LEDs off

## Requirements

- Python 3.7 or later
- ReSpeaker Mic Array v2.0
- MQTT broker (e.g., Mosquitto)
- Wyoming satellite service

## License

This project is licensed under the MIT License.
