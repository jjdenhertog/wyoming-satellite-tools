from setuptools import find_packages, setup

setup(
    name="wyoming-satellite-tools",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "wyoming>=1.5.2",
        "pixel-ring",
        "paho-mqtt",
    ],
    entry_points={
        "console_scripts": [
            "wyoming-satellite-tools-mqtt=wyoming_satellite_tools.mqtt:main",
            "wyoming-satellite-tools-control=wyoming_satellite_tools.usb_led:main",
        ],
    },
    author="Your Name",
    description="Wyoming Satellite Tools",
    keywords="wyoming,respeaker,led,mqtt",
    python_requires=">=3.7",
)
