# Wildfire Propagation Simulator

Python-based wildfire simulation that models fire spread using **wind direction, wind speed, dryness, terrain, and forest density**.

Built with **Python, NumPy, Tkinter, OpenCV, and Pillow**. The application uses a 100 × 100 grid and provides an interactive GUI for changing environmental conditions and observing how they affect wildfire propagation.

## Demo

### Simulation 1

[Watch the demo](Examples/demo.mp4)

### Simulation 2

[Watch the demo](Examples/demo2.mp4)

## Features

* Interactive wildfire simulation
* Adjustable wind speed and direction
* Adjustable dryness and forest density
* Randomized terrain generation
* Click-to-start fire locations
* Pause, resume, and reset controls
* Real-time fire statistics
* Probability-based fire spread model

## Technologies

* Python
* NumPy
* Tkinter
* OpenCV
* Pillow

## Installation

```bash
pip install numpy opencv-python pillow
```

Run the program:

```bash
python wildfire_simulator.py
```

## How It Works

Each grid cell represents:

* Tree
* Burning tree
* Burned area
* Empty terrain

Fire spread probability is calculated using environmental factors including **dryness, wind influence, and terrain elevation**. Higher dryness and favorable wind or terrain conditions increase the likelihood that nearby trees ignite.

## Project Files

```text
main.py
Fire1.mp4
Fire2.mp4
README.md
```

## Purpose

Developed as an interactive demonstration of **probabilistic modeling, cellular simulation, GUI development, and environmental modeling in Python**.

> This project is an educational simulation and is not intended for real-world wildfire prediction.
