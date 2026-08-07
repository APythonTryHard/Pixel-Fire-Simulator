import numpy as np
import tkinter as tk
from tkinter import ttk, Scale, Frame, Label, Button, HORIZONTAL
import cv2
from PIL import Image, ImageTk
import random
import time


class FirePropagationModel:
    def __init__(self, size=(100, 100)):
        self.size = size
        self.grid = np.zeros(self.size)  # 0: empty, 1: tree, 2: burning, 3: burnt
        self.wind_direction = 0  # in degrees (0: north, 90: east, 180: south, 270: west)
        self.wind_speed = 0  # 0-10
        self.dryness = 5  # 0-10
        self.terrain = np.zeros(self.size)  # 0: flat, 1: uphill, -1: downhill
        self.initialize_forest()

    def initialize_forest(self, density=0.6):
        # Create forest with random tree density
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                if random.random() < density:
                    self.grid[i, j] = 1  # Place tree

        # Create some random terrain features
        for _ in range(10):
            x, y = random.randint(0, self.size[0] - 20), random.randint(0, self.size[1] - 20)
            radius = random.randint(5, 15)
            height = random.choice([-1, 1])

            for i in range(max(0, x - radius), min(self.size[0], x + radius)):
                for j in range(max(0, y - radius), min(self.size[1], y + radius)):
                    dist = np.sqrt((i - x) ** 2 + (j - y) ** 2)
                    if dist < radius:
                        self.terrain[i, j] = height * (1 - dist / radius)

    def start_fire(self, positions=None):
        if positions is None:
            # Start fire at random positions
            for _ in range(3):
                i, j = random.randint(0, self.size[0] - 1), random.randint(0, self.size[1] - 1)
                if self.grid[i, j] == 1:  # Only start fire on trees
                    self.grid[i, j] = 2
        else:
            for pos in positions:
                i, j = pos
                if 0 <= i < self.size[0] and 0 <= j < self.size[1] and self.grid[i, j] == 1:
                    self.grid[i, j] = 2

    def update(self):
        new_grid = self.grid.copy()
        burning_cells = np.where(self.grid == 2)
        burning_count = len(burning_cells[0])

        if burning_count == 0:
            return False  # No more fire

        for idx in range(burning_count):
            i, j = burning_cells[0][idx], burning_cells[1][idx]
            new_grid[i, j] = 3  # Current burning cell becomes burnt

            # Calculate wind influence direction
            wind_rad = np.radians(self.wind_direction)
            wind_influence_x = -np.sin(wind_rad) * self.wind_speed / 10
            wind_influence_y = -np.cos(wind_rad) * self.wind_speed / 10

            # Check neighboring cells for potential spread
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di == 0 and dj == 0:
                        continue

                    ni, nj = i + di, j + dj
                    if 0 <= ni < self.size[0] and 0 <= nj < self.size[1] and self.grid[ni, nj] == 1:
                        # Base spread probability
                        spread_prob = 0.2 + (self.dryness / 20)

                        # Wind influence
                        direction_match = wind_influence_x * di + wind_influence_y * dj
                        wind_factor = 1 + direction_match

                        # Terrain influence
                        terrain_diff = self.terrain[ni, nj] - self.terrain[i, j]
                        # Fire spreads more easily uphill
                        terrain_factor = 1 + (terrain_diff * 0.5)

                        # Combine factors
                        total_prob = spread_prob * wind_factor * terrain_factor

                        # Ensure probability bounds
                        total_prob = max(0.01, min(0.95, total_prob))

                        if random.random() < total_prob:
                            new_grid[ni, nj] = 2  # Spread fire

        self.grid = new_grid
        return True  # Fire still burning

    def get_display_grid(self):
        # Create RGB representation
        display = np.zeros((self.size[0], self.size[1], 3), dtype=np.uint8)

        # Color mapping: green for trees, red for burning, dark gray for burnt, light brown for empty
        display[self.grid == 0] = [210, 180, 140]  # Empty (light brown)
        display[self.grid == 1] = [34, 139, 34]  # Trees (forest green)
        display[self.grid == 2] = [0, 0, 255]  # Burning (red)
        display[self.grid == 3] = [105, 105, 105]  # Burnt (dark gray# )

        # Add terrain visualization (lighter for higher elevation)
        terrain_vis = ((self.terrain + 1) / 2 * 30).astype(np.uint8)

        # Only adjust empty and tree cells for terrain visibility
        for i in range(3):
            mask_empty = (self.grid == 0)
            mask_trees = (self.grid == 1)

            display[mask_empty, i] = np.clip(display[mask_empty, i] + terrain_vis[mask_empty], 0, 255)
            display[mask_trees, i] = np.clip(display[mask_trees, i] + terrain_vis[mask_trees], 0, 255)

        return cv2.resize(display, (500, 500), interpolation=cv2.INTER_NEAREST)


class FireSimulationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Wildfire Propagation Simulator")
        self.root.geometry("900x700")
        self.root.resizable(False, False)

        self.sim_size = (100, 100)
        self.model = FirePropagationModel(self.sim_size)
        self.is_running = False
        self.animation_speed = 100  # ms delay between frames

        self.create_widgets()

    def create_widgets(self):
        # Main frame
        main_frame = Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Left panel (controls)
        control_frame = Frame(main_frame, width=300, bg="#000000", padx=10, pady=10, relief="ridge", bd=2)
        control_frame.pack(side="left", fill="y", padx=(0, 10))

        # Title
        title_label = Label(control_frame, text="WILDFIRE SIMULATOR", font=("Arial", 16, "bold"), bg="#000000")
        title_label.pack(pady=(0, 20))

        # Wind direction control
        wind_dir_frame = Frame(control_frame, bg="#000000")
        wind_dir_frame.pack(fill="x", pady=5)

        Label(wind_dir_frame, text="Wind Direction:", bg="#000000").pack(anchor="w")
        self.wind_dir_slider = Scale(wind_dir_frame, from_=0, to=359, orient=HORIZONTAL,
                                     command=self.update_wind_direction)
        self.wind_dir_slider.set(self.model.wind_direction)
        self.wind_dir_slider.pack(fill="x")

        # Wind speed control
        wind_speed_frame = Frame(control_frame, bg="#000000")
        wind_speed_frame.pack(fill="x", pady=5)

        Label(wind_speed_frame, text="Wind Speed:", bg="#000000").pack(anchor="w")
        self.wind_speed_slider = Scale(wind_speed_frame, from_=0, to=10, orient=HORIZONTAL,
                                       command=self.update_wind_speed)
        self.wind_speed_slider.set(self.model.wind_speed)
        self.wind_speed_slider.pack(fill="x")

        # Dryness control
        dryness_frame = Frame(control_frame, bg="#000000")
        dryness_frame.pack(fill="x", pady=5)

        Label(dryness_frame, text="Dryness Level:", bg="#000000").pack(anchor="w")
        self.dryness_slider = Scale(dryness_frame, from_=0, to=10, orient=HORIZONTAL,
                                    command=self.update_dryness)
        self.dryness_slider.set(self.model.dryness)
        self.dryness_slider.pack(fill="x")

        # Forest density control
        density_frame = Frame(control_frame, bg="#000000")
        density_frame.pack(fill="x", pady=5)

        Label(density_frame, text="Forest Density:", bg="#000000").pack(anchor="w")
        self.density_slider = Scale(density_frame, from_=0.1, to=0.9, resolution=0.1, orient=HORIZONTAL)
        self.density_slider.set(0.6)
        self.density_slider.pack(fill="x")

        # Animation speed control
        speed_frame = Frame(control_frame, bg="#000000")
        speed_frame.pack(fill="x", pady=5)

        Label(speed_frame, text="Simulation Speed:", bg="#000000").pack(anchor="w")
        self.speed_slider = Scale(speed_frame, from_=10, to=500, orient=HORIZONTAL,
                                  command=self.update_animation_speed)
        self.speed_slider.set(self.animation_speed)
        self.speed_slider.pack(fill="x")

        # Action buttons
        btn_frame = Frame(control_frame, bg="#000000")
        btn_frame.pack(fill="x", pady=20)

        self.reset_btn = ttk.Button(btn_frame, text="Reset Simulation", command=self.reset_simulation)
        self.reset_btn.pack(fill="x", pady=5)

        self.start_btn = ttk.Button(btn_frame, text="Start Fire", command=self.start_fire)
        self.start_btn.pack(fill="x", pady=5)

        self.pause_btn = ttk.Button(btn_frame, text="Pause", command=self.toggle_simulation)
        self.pause_btn.pack(fill="x", pady=5)

        # Statistics frame
        stats_frame = Frame(control_frame, bg="#000000", relief="ridge", bd=1)
        stats_frame.pack(fill="x", pady=10)

        Label(stats_frame, text="Statistics", font=("Arial", 12, "bold"), bg="#000000").pack(pady=(5, 0))

        self.stats_text = Label(stats_frame, text="", justify="left", bg="#000000")
        self.stats_text.pack(fill="x", padx=5, pady=5)

        # Legend
        legend_frame = Frame(control_frame, bg="#000000", relief="ridge", bd=1)
        legend_frame.pack(fill="x", pady=10)

        Label(legend_frame, text="Legend", font=("Arial", 12, "bold"), bg="#000000").pack(pady=(5, 0))

        legend_items = [
            ("Trees", "green"),
            ("Burning", "red"),
            ("Burnt", "gray"),
            ("Empty", "brown")
        ]

        for text, color in legend_items:
            item_frame = Frame(legend_frame, bg="#000000")
            item_frame.pack(anchor="w", padx=10, pady=2)

            color_box = Frame(item_frame, width=15, height=15, bg=color)
            color_box.pack(side="left", padx=(0, 5))

            Label(item_frame, text=text, bg="#000000").pack(side="left")

        # Right panel (visualization)
        visual_frame = Frame(main_frame)
        visual_frame.pack(side="right", fill="both", expand=True)

        self.canvas = tk.Canvas(visual_frame, width=500, height=500, bg="white", highlightthickness=0)
        self.canvas.pack(pady=10)

        # Canvas click event
        self.canvas.bind("<Button-1>", self.canvas_click)

        # Initial display
        self.update_display()

    def update_wind_direction(self, value):
        self.model.wind_direction = float(value)

    def update_wind_speed(self, value):
        self.model.wind_speed = float(value)

    def update_dryness(self, value):
        self.model.dryness = float(value)

    def update_animation_speed(self, value):
        self.animation_speed = int(value)

    def reset_simulation(self):
        self.is_running = False
        self.model = FirePropagationModel(self.sim_size)
        self.model.initialize_forest(density=self.density_slider.get())
        self.model.wind_direction = self.wind_dir_slider.get()
        self.model.wind_speed = self.wind_speed_slider.get()
        self.model.dryness = self.dryness_slider.get()
        self.update_display()
        self.pause_btn.config(text="Start")

    def start_fire(self):
        if not self.is_running:
            self.model.start_fire()
            self.is_running = True
            self.pause_btn.config(text="Pause")
            self.run_simulation()

    def toggle_simulation(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.pause_btn.config(text="Pause")
            self.run_simulation()
        else:
            self.pause_btn.config(text="Resume")

    def canvas_click(self, event):
        # Convert canvas coordinates to grid coordinates
        grid_size = self.sim_size
        canvas_size = (500, 500)

        grid_x = int(event.y / canvas_size[0] * grid_size[0])
        grid_y = int(event.x / canvas_size[1] * grid_size[1])

        # Start fire at clicked position and neighbors
        positions = [(grid_x, grid_y)]
        self.model.start_fire(positions)
        self.update_display()

        if not self.is_running:
            self.is_running = True
            self.pause_btn.config(text="Pause")
            self.run_simulation()

    def run_simulation(self):
        if not self.is_running:
            return

        still_burning = self.model.update()
        self.update_display()

        if still_burning:
            self.root.after(self.animation_speed, self.run_simulation)
        else:
            self.is_running = False
            self.pause_btn.config(text="Start")

    def update_display(self):
        # Get visual representation
        display_img = self.model.get_display_grid()

        # Convert to format compatible with tkinter
        img = cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img_tk = ImageTk.PhotoImage(image=img)

        # Update canvas
        self.canvas.create_image(0, 0, anchor="nw", image=img_tk)
        self.canvas.image = img_tk  # Keep reference to prevent garbage collection

        # Update statistics
        tree_count = np.sum(self.model.grid == 1)
        burning_count = np.sum(self.model.grid == 2)
        burnt_count = np.sum(self.model.grid == 3)
        total_cells = self.sim_size[0] * self.sim_size[1]

        stats_text = f"Trees: {tree_count} ({tree_count / total_cells * 100:.1f}%)\n"
        stats_text += f"Burning: {burning_count} ({burning_count / total_cells * 100:.1f}%)\n"
        stats_text += f"Burnt: {burnt_count} ({burnt_count / total_cells * 100:.1f}%)\n"

        if burning_count > 0:
            stats_text += f"\nFire is spreading!"
        elif burnt_count > 0:
            stats_text += f"\nFire has stopped."

        self.stats_text.config(text=stats_text)


if __name__ == "__main__":
    root = tk.Tk()
    app = FireSimulationApp(root)
    root.mainloop()
