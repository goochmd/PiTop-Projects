# Ultrasonic Movement (USM)

This folder contains code for reading ultrasonic distance sensors and converting measurements into movement decisions. The scripts are intended to help the robot maintain safe distances, avoid obstacles, or follow objects at a set distance.

## Files
### - `ultrasonic.py` — ultrasonic sensor read and movement helper
  - Purpose: read raw trigger/echo timing, compute distance (usually in cm), smooth readings, and provide a clean interface for other modules to query the robot's current distance and state.

## Troubleshooting
- Interference: nearby ultrasonic sensors or reflective surfaces can cause false readings.
- Temperature and humidity: speed-of-sound varies slightly with conditions; for most use-cases, a fixed constant is fine.
- No echo: ensure wiring and trigger pulses are correct. Add debug logging to timestamp trigger and echo events.
