"""
             PI-TOP TOOLKIT         
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

import asyncio as aio
import time

# ===========================
# OBJECT DETECTION FUNCTIONS
# ===========================
async def run_color_isoc():
    """Object Detection - Color Isolation Controller (Computer side)"""
    from Tools.OBJDET.computer import main as isocmain
    await isocmain()

async def run_color_isos():
    """Object Detection - Color Isolation Server (Pi-Top side)"""
    try:
        from Tools.OBJDET.pt import start_client as isosmain
        return await isosmain()
    except ImportError:
        print("Pi-Top-specific dependencies missing. Run this on Pi-Top hardware.")
        time.sleep(2)
    except Exception as e:
        print(f"[run_color_isos] Error: {e}")
        return None

# ===========================
# ULTRASONIC FUNCTIONS
# ===========================
async def run_ultrasonic():
    """Ultrasonic Measurement (Pi-Top side)"""
    try:
        from Tools.USM.pt import main as ultrasonicmain
        await ultrasonicmain()
    except ImportError:
        print("Pi-Top ultrasonic module not found. Run on Pi-Top hardware.")
        time.sleep(2)
    except Exception as e:
        print(f"[run_ultrasonic] Error: {e}")

# ===========================
# REMOTE CONTROL FUNCTIONS
# ===========================
async def run_remote_control_client():
    """Remote Control - Client (Computer side)"""
    from Tools.RC.computer import main as rcmainc
    await rcmainc()

async def run_remote_control_server():
    """Remote Control - Server (Pi-Top side)"""
    try:
        from Tools.RC.pi_top import main as rcmains
        await rcmains()
    except ImportError:
        print("Pi-Top remote control module not found. Run on Pi-Top hardware.")
        time.sleep(2)
    except Exception as e:
        print(f"[run_remote_control_server] Error: {e}")
