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
from Tools.OBJDET.computer import main as isocmain

# Remote Control - Controller, No Pi-Top dependence
from Tools.RC.computer import main as rcmainc

# Attempts to import Pi-Top dependent modules, handles ImportError gracefully for non-Pi-Top devices.
try:
    # Object Detection - Server, Pi-Top dependent
    from Tools.OBJDET.pi-top import start_client as isosmain
    # Remote Control - Server, Pi-Top dependent
    from Tools.RC.pi-top import main as rcmains
    # Ultrasonic Measurement - Pi-Top dependent
    from Tools.USM.pi-top import main as ultrasonicmain
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
    try:
        return await isosmain()
    except Exception as e:
        print(f"Error in run_color_isos. Ensure this is Pi-Top hardware.\nError details: {e}")
        return None

# Ultrasonic Measurement
async def run_ultrasonic():
    try:
        await ultrasonicmain()
    except Exception as e:
        print(f"Error in run_ultrasonic. Ensure this is Pi-Top hardware.\nError details: {e}")

# Remote Control - Client
async def run_remote_control_client():
    await rcmainc()

# Remote Control - Server
async def run_remote_control_server():
    try:
        await rcmains()
    except Exception as e:
        print(f"Error in Remote Control Server. Ensure this is Pi-Top hardware.\nError details: {e}")

