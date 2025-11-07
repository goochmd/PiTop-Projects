"""             PI-TOP TOOLKIT         
Contains multiple tools used for Pi-Top, such as:

OBJDET - Object Detection: Basic object detection
using color isolation, with main processing and 
viewing via network.

RC - Remote Control: Control your Pi-Top remotely 
via network.

USM - Ultrasonic Measurement: Basic object avoidance
using Pi-Top's ultrasonic sensor.

Each tool can be run asynchronously using the provided 
functions.
"""

# This module provides asynchronous functions to run various Pi-Top tools.
import asyncio as aio

# Used to give time to read errors or messages
import time

# Object Detection - Controller, No Pi-Top dependence
from OBJDET.cisoc import main as isocmain

# Remote Control - Controller, No Pi-Top dependence
from RC.controller import main as rcmainc

# Attempts to import Pi-Top dependent modules, handles ImportError gracefully for non-Pi-Top devices.
try:
    # Object Detection - Server, Pi-Top dependent
    from OBJDET.cisos import main as isosmain
    # Remote Control - Server, Pi-Top dependent
    from RC.server import main as rcmains
    # Ultrasonic Measurement - Pi-Top dependent
    from USM.ultrasonic import main as ultrasonicmain
except ImportError:
    # Error message, mainly for non-Pi-Top devices
    print("Errors importing Pi-Top modules.\nIf you're running this on a non-Pi-Top device, please ignore this message.\nOtherwise, ensure all dependencies are installed.")
    time.sleep(2)

# Asynchronous functions to run each tool

# Object Detection - Color Isolation Controller
async def run_color_isoc():
    await isocmain()

# Object Detection - Color Isolation Server
async def run_color_isos():
    # Returns list, indices: 0 = frame, 1 = object locations
    return await isosmain()

# Ultrasonic Measurement
async def run_ultrasonic():
    await ultrasonicmain()

# Remote Control - Client
async def run_remote_control_client():
    await rcmainc()

# Remote Control - Server
async def run_remote_control_server():
    await rcmains()

