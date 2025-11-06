# Pi Top Projects
This repository collects small robotics projects and competition helpers built around the pi-top platform and Pi-Top hardware components. The code is organized under the `Tools` folder and grouped by project type — Object Detection (color isolation), Ultrasonic Movement, and Remote Control — plus a small utilities module used across projects.

Contents
 - `Tools/` — main project folder with subprojects and helpers
	 - `tools.py` — shared utilities and helper functions used by the projects
	 - `OBJDET/` — object-detection-by-color projects
		 - `cisoc.py` — color isolation & object detection helpers (single-file detector)
		 - `cisos.py` — secondary or alternate color-isolation implementation
		 - `testc.py` — quick test harness for `OBJDET` code
	 - `USM/` — Ultrasonic Movement project(s)
		 - `ultrasonic.py` — ultrasonic sensor control, distance measurement and movement coordination
	 - `RC/` — Remote Control related code
		 - `controller.py` — code to drive the robot from a controller or input device
		 - `server.py` — optional network server for remote control or telemetry

Why this structure
- Grouping by capability keeps hardware and algorithm code together (e.g., all object-detection helpers in `OBJDET`).
- `tools.py` holds commonly reused code (initialization, helpers for Pi-Top sensors, GPIO wrappers, logging helpers, config parsing). Importing `tools` from each subproject avoids duplication and keeps small example files easy to read.

##Project summaries

###1) Object Detection — Color Isolation (`Tools/OBJDET`)
 - Goal: detect objects using basic color isolation rather than heavy ML models. These scripts show how to capture frames, apply color thresholding, find contours, and compute object centroids for simple navigation or pick-up tasks.
 - Files: `cisoc.py`, `cisos.py` (two complementary implementations), `testc.py` (runtime/test harness).

###2) Ultrasonic Movement (`Tools/USM`)
 - Goal: use ultrasonic distance data to drive movement decisions (stop, avoid, or follow). The `ultrasonic.py` file contains sensor read loops, smoothing/filtering and basic movement commands you can hook into your motor controller.

###3) Remote Control (`Tools/RC`)
 - Goal: provide manual control interfaces and a lightweight server for remote commands. `controller.py` is the main control client; `server.py` can accept network commands or serve as a telemetry endpoint.

##tools.py
 - Purpose: centralized helper utilities that multiple projects use. Examples that belong here: Pi-Top SDK initialization, unified logging setup, common PWM/motor abstractions, safe shutdown sequences, and short helper functions for sensor calibration. Keeping these helpers in `tools.py` keeps the example project files concise and focused on the core algorithm for each demo.

##Competition / challenge files
 - When preparing for a competition or a specific challenge, place the challenge-specific Python files (the solutions and entry scripts) in the repository root (the main repository folder). This makes it easy to find the primary challenge entrypoint and package or copy just the files needed for submission.
 - Example convention: `challenge_<name>.py` or `run_challenge.py` at the repo root. Keep helper modules under `Tools/` and import them from the root script.

##Notes and tips
- Keep `tools.py` small and hardware-agnostic where possible; if a function is only used by one project, prefer keeping it in that project's folder.
- Use virtual environments and pin dependencies in a `requirements.txt` when you prepare a challenge submission.
- If you'd like, I can add a tiny example `challenge_template.py` at the repo root that shows how to import from `Tools/` and initialize sensors safely.

##Links
- Pi-Top SDK: https://github.com/pi-top/pi-top-Python-SDK

