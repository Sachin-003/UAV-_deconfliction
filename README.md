# Drone Conflict Detection and Visualization

This project simulates drone flight paths and detects conflicts between them, including both spatial and temporal conflicts. It visualizes these conflicts in a 3D animation and generates a detailed conflict report.

## Features
- **Spatial Conflict Detection**: Detects when drones are too close to each other during their flight paths.
- **Temporal Conflict Detection**: Identifies when drones occupy the same position at the same time step.
- **3D Animation Visualization**: Visualizes the flight paths of drones and conflicts in real-time using `matplotlib`.
- **Conflict Reporting**: Generates a PDF report summarizing the detected conflicts, including their time steps and drone positions.
- **Bézier Curves**: Generates smooth drone flight paths using Bézier curves, ensuring realistic movements.

## Requirements

To run this project, the following Python libraries are required:

```bash
pip install numpy matplotlib fpdf bezier
```

## Project Structure
```bash
├── README.md                # Project documentation
├── waypoints.json           # JSON file containing drone waypoints data
├── waypoints_temporal_vis.json # JSON file for temporal conflict visualization
├── drone_sim.py             # Main script for detecting and visualizing conflicts
```

## Usage

### 1. Prepare the Waypoints JSON File
The waypoints for the primary drone and other drones should be specified in a JSON file (`waypoints.json`). The file should follow this structure:

```json
{
    "primary": {
        "id": "Primary_Drone",
        "waypoints": [[5, 5, 0], [12, 18, 22], [18, 8, 45]]
    },
    "drones": [
        {
            "id": "Drone_1",
            "waypoints": [[-40, 0, 0], [6, 12, 25], [2, 2, 45]]
        },
        {
            "id": "Drone_2",
            "waypoints": [[10, 10, 0], [8, 6, 22], [6, 12, 45]]
        }
    ]
}
```

### 2. Adjust Safety Distance and Time Steps

To customize the **safety distance** (for spatial conflicts) and **time step resolution**, modify the following variables in `drone_sim.py`:

```python
SAFETY_DISTANCE = 5  # Minimum distance (in meters) between drones to avoid spatial conflicts
TIME_STEP_RESOLUTION = 1  # Time granularity for conflict detection
```

### 3. Run the Script

Once the JSON file is prepared, you can run the script to generate the 3D visualization and detect conflicts:

```bash
python3 drone_sim.py
```

## Conflict Visualization

During the 3D visualization:
- **Yellow Points**: Indicate spatial conflicts (when drones are too close to each other)
- **Violet Points**: Represent temporal conflicts (when drones reach the same position at the same time)
- **Primary Drone (Highlighted Path)**: The main drone's flight path is emphasized for clarity

## Video Demonstration


https://github.com/user-attachments/assets/f5e7da67-d25c-4c63-a5a1-fdcf717449a7

---

Let me know if you need any further modifications! 🚀
