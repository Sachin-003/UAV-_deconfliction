import numpy as np
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import bezier

# Constants
SAFETY_DISTANCE = 2  # meters
TIME_STEPS = 100  # Number of animation frames
MAX_DEGREE = 5  # Bézier max degree limit

# Load waypoints from JSON file
def load_waypoints(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data["primary"].get("waypoints", []), data["drones"]

# Generate Bézier curve
def generate_curve(waypoints, num_points=50):
    waypoints = np.array(waypoints)
    if waypoints.shape[0] < 2 or waypoints.shape[1] != 3:
        raise ValueError(f"Invalid waypoints shape: {waypoints.shape}, must be (N,3)")
    degree = min(waypoints.shape[0] - 1, MAX_DEGREE)
    curve = bezier.Curve(waypoints.T, degree=degree)
    return curve.evaluate_multi(np.linspace(0, 1, num_points)).T

# Check conflicts
def check_conflicts(primary_curve, drones):
    spatial_conflicts, temporal_conflicts = [], []
    for drone in drones:
        for t in range(len(primary_curve)):
            dist = np.linalg.norm(primary_curve[t] - drone['curve'][t])
            if dist < SAFETY_DISTANCE:
                spatial_conflicts.append((drone['id'], t, primary_curve[t].tolist()))
            if np.allclose(primary_curve[t], drone['curve'][t], atol=1e-2):
                temporal_conflicts.append((drone['id'], t, primary_curve[t].tolist()))
    return spatial_conflicts, temporal_conflicts

# Generate conflict report
def generate_conflict_report(spatial_conflicts, temporal_conflicts, filename="conflict_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    pdf.cell(200, 10, "Drone Conflict Report", align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(10)
    
    if spatial_conflicts:
        pdf.cell(200, 10, "Spatial Conflicts:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        for drone_id, t, pos in spatial_conflicts:
            pdf.cell(200, 10, f"Time: {t}, Drone: {drone_id}, Position: {pos}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    if temporal_conflicts:
        pdf.ln(10)
        pdf.cell(200, 10, "Temporal Conflicts:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        for drone_id, t, pos in temporal_conflicts:
            pdf.cell(200, 10, f"Time: {t}, Drone: {drone_id}, Position: {pos}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.output(filename)
    print(f"Report saved as {filename}")

# Load data
primary_waypoints, drones = load_waypoints("waypoints.json")
primary_curve = generate_curve(primary_waypoints, TIME_STEPS)

for drone in drones:
    drone["curve"] = generate_curve(drone["waypoints"], TIME_STEPS)

# Detect conflicts
spatial_conflicts, temporal_conflicts = check_conflicts(primary_curve, drones)

# Generate report
generate_conflict_report(spatial_conflicts, temporal_conflicts)

# 3D Animation Setup
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_xlim([-50, 50])
ax.set_ylim([-50, 50])
ax.set_zlim([0, 50])
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

# Plot primary drone path
(primary_line,) = ax.plot([], [], [], 'b-', label="Primary Drone")
(primary_dot,) = ax.plot([], [], [], 'bo', markersize=5)

drone_lines, drone_dots, drone_labels = [], [], []
for drone in drones:
    line, = ax.plot([], [], [], 'r-', alpha=0.6, label=f"Drone {drone['id']}")
    dot, = ax.plot([], [], [], 'ro', markersize=5)
    label = ax.text(0, 0, 0, f"{drone['id']}", color='red')
    drone_lines.append(line)
    drone_dots.append(dot)
    drone_labels.append(label)

# Initialize animation
def init():
    primary_line.set_data([], [])
    primary_line.set_3d_properties([])
    primary_dot.set_data([], [])
    primary_dot.set_3d_properties([])
    for line, dot, label in zip(drone_lines, drone_dots, drone_labels):
        line.set_data([], [])
        line.set_3d_properties([])
        dot.set_data([], [])
        dot.set_3d_properties([])
        label.set_position((0, 0))
        label.set_3d_properties(0)
    return [primary_line, primary_dot] + drone_lines + drone_dots + drone_labels

# Update animation frames
# Update animation frames with conflict visualization
# Store original colors for drones
drone_original_color = ['r'] * len(drones)

def update(frame):
    primary_line.set_data(primary_curve[:frame, 0], primary_curve[:frame, 1])
    primary_line.set_3d_properties(primary_curve[:frame, 2])
    primary_dot.set_data([primary_curve[frame, 0]], [primary_curve[frame, 1]])
    primary_dot.set_3d_properties([primary_curve[frame, 2]])

    for i, drone in enumerate(drones):
        drone_lines[i].set_data(drone["curve"][:frame, 0], drone["curve"][:frame, 1])
        drone_lines[i].set_3d_properties(drone["curve"][:frame, 2])

        drone_dots[i].set_data([drone["curve"][frame, 0]], [drone["curve"][frame, 1]])
        drone_dots[i].set_3d_properties([drone["curve"][frame, 2]])

        drone_labels[i].set_position((drone["curve"][frame, 0], drone["curve"][frame, 1]))
        drone_labels[i].set_3d_properties(drone["curve"][frame, 2])

        # Reset color to default
        drone_dots[i].set_color(drone_original_color[i])

        # Check for spatial conflicts at this frame
        for drone_id, t, pos in spatial_conflicts:
            if t == frame and drone_id == drone["id"]:
                drone_dots[i].set_color('yellow')  # Change color during conflict
                break  # No need to check further

        # Check for temporal conflicts at this frame
        for drone_id, t, pos in temporal_conflicts:
            if t == frame and drone_id == drone["id"]:
                drone_dots[i].set_color('purple')  # Change color during conflict
                break  # No need to check further

    return [primary_line, primary_dot] + drone_lines + drone_dots + drone_labels



ani = animation.FuncAnimation(fig, update, frames=TIME_STEPS, init_func=init, blit=False, interval=100)
plt.legend()
plt.show()
