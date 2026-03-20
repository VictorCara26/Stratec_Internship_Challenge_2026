import sys
import webbrowser

from PyQt5.QtCore import QTimer, QPointF, Qt
from PyQt5.QtGui import QPainter, QColor, QFont, QPen
from PyQt5.QtWidgets import (QWidget, QMainWindow, QApplication, QHBoxLayout,
                             QVBoxLayout, QComboBox, QSpinBox, QPushButton,
                             QTextEdit, QLabel, QStackedWidget, QFileDialog)
from SpaceApp import SpaceApp
from JourneyReport import JourneyReport


class SolarCanvas(QWidget):
    def __init__(self, planets):
        super().__init__()
        self.planets = planets
        self.rocket_pos = None
        self.current_day = 0
        self.current_speed = 0.0
        self.setMinimumSize(600, 600)
        self.scale = 15.0
        self.pan_offset = QPointF(0, 0)
        self.last_mouse_pos = QPointF(0, 0)

    def wheelEvent(self, event):
        zoom_factor = 1.25
        if event.angleDelta().y() > 0:
            self.scale *= zoom_factor
        else:
            self.scale /= zoom_factor
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            delta = event.pos() - self.last_mouse_pos
            self.pan_offset += delta
            self.last_mouse_pos = event.pos()
            self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor(5, 5, 15))

        center = self.rect().center() + self.pan_offset

        # 1.Sun
        p.setBrush(QColor(255, 220, 0))
        p.setPen(Qt.NoPen)
        p.drawEllipse(center, 10, 10)

        # 2.Planets and orbits
        for planet in self.planets:
            x, y = planet.get_coords(self.current_day, self.scale)

            p.setBrush(Qt.NoBrush)
            p.setPen(QColor(50, 50, 70))
            r_px = planet.orbital_radius_au * self.scale
            p.drawEllipse(center, int(r_px), int(r_px))

            p.setBrush(QColor(0, 150, 255))


            visual_boost = 1.2e-8
            radius_px = max(2, (planet.radius_m * visual_boost) * self.scale)
            p.drawEllipse(QPointF(center.x() + x, center.y() + y), radius_px, radius_px)

            p.setPen(Qt.white)
            p.drawText(int(center.x() + x + 8), int(center.y() + y + 8), planet.name)

        # 3.Rocket
        if self.rocket_pos and self.window().timer.isActive():
            rx, ry = self.rocket_pos
            p.setBrush(Qt.red)
            p.setPen(QPen(Qt.white, 1))
            p.drawEllipse(QPointF(center.x() + rx, center.y() + ry), 5, 5)

        # 4.Rest of HUD
        p.setPen(QColor(0, 255, 150))
        p.setFont(QFont("Consolas", 12, QFont.Bold))
        p.drawText(20, 30, f"MISSION TIME: Day {self.current_day:.2f}")
        p.drawText(20, 55, f"VELOCITY: {self.current_speed / 1000:.2f} km/s")

        p.setPen(QColor(200, 200, 200, 150))
        p.setFont(QFont("Arial", 10))

        author_text = "Developed by: Carabulea Victor"

        margin = 20
        text_width = p.fontMetrics().width(author_text)
        text_height = p.fontMetrics().height()

        p.drawText(self.width() - text_width - margin,
                   self.height() - margin,
                   author_text)

class SpaceGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.app = SpaceApp("Planetary_Data.txt", "Rocket_Data.txt", "Solar_System_Data.txt")
        self.timer = QTimer()
        # noinspection PyUnresolvedReferences
        self.timer.timeout.connect(self.update_anim)
        self.sim_time_s = 0
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("STRATEC Space App")
        main_widget = QWidget()
        layout = QHBoxLayout()
        controls = QVBoxLayout()

        self.stage_selector = QComboBox()
        self.stage_selector.addItems([
            "Stage 1: Escape Velocities",
            "Stage 2: Acceleration Stats",
            "Stage 3: Straight-Line Journey",
            "Stage 4: Orbital Simulation",
            "Stage 5: Static Transfer Window",
            "Stage 6: Dynamic Journey"
        ])
        self.stage_selector.currentIndexChanged.connect(self.update_ui_for_stage)

        self.planet_a = QComboBox()
        self.planet_b = QComboBox()
        for p in self.app.planets:
            self.planet_a.addItem(p.name)
            self.planet_b.addItem(p.name)

        self.day_input = QSpinBox()
        self.day_input.setRange(0, 100000)
        self.day_input.setValue(36500)  # Default to 100 years

        self.action_btn = QPushButton("🚀 Run Simulation")
        self.action_btn.clicked.connect(self.handle_action)

        self.output = QTextEdit()
        self.output.setReadOnly(True)

        controls.addWidget(QLabel("<b>Select Challenge Stage:</b>"))
        controls.addWidget(self.stage_selector)
        controls.addWidget(QLabel("Departure Planet:"))
        controls.addWidget(self.planet_a)
        controls.addWidget(QLabel("Destination Planet:"))
        controls.addWidget(self.planet_b)
        controls.addWidget(QLabel("Starting Day/Simulation Time:"))
        controls.addWidget(self.day_input)
        controls.addWidget(self.action_btn)
        controls.addWidget(self.output)

        # Create GitHub Button
        self.github_btn = QPushButton("📂 View Source on GitHub")
        self.github_btn.setStyleSheet("background-color: #24292e; color: white; font-weight: bold;")
        self.github_btn.clicked.connect(self.open_github)

        # Add it to the controls layout (above the output box)
        controls.addWidget(self.github_btn)


        self.canvas = SolarCanvas(self.app.planets)

        layout.addLayout(controls, 1)
        layout.addWidget(self.canvas, 2)
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)
        self.resize(1200, 800)
        self.update_ui_for_stage()

    def open_github(self):
        url = "https://github.com/VictorCara26/Stratec_Internship_Challenge_2026"
        webbrowser.open(url)

    def update_ui_for_stage(self):
        idx = self.stage_selector.currentIndex()
        is_journey = idx in [2, 4, 5]
        self.planet_b.setEnabled(is_journey)
        self.day_input.setEnabled(idx >= 3)

    def handle_action(self):
        idx = self.stage_selector.currentIndex()

        if idx in [2, 4, 5]:
            p1_name = self.planet_a.currentText()
            p2_name = self.planet_b.currentText()
            if p1_name == p2_name:
                self.output.setText(
                    f"<b style='color:red;'>Error:</b> Cannot compute a journey from {p1_name} to itself.")
                return

        self.output.clear()
        self.timer.stop()

        if idx == 0:  # Stage 1
            self.output.append("<b>Stage 1: Planetary Escape Velocities</b>")
            for p in self.app.planets:
                v = self.app.rocket.get_escape_velocity(p)
                self.output.append(f"{p.name}: {v / 1000:.2f} km/s")


        elif idx == 1:  # Stage 2
            self.output.append("<b>Stage 2: Launch Requirements</b>")

            for p in self.app.planets:
                v = self.app.rocket.get_escape_velocity(p)
                t, dist_km = self.app.rocket.get_burn_stats(v)
                self.output.append(f"{p.name}: {t:.1f}s to reach {v / 1000:.1f}km/s (Dist: {dist_km:.1f}km)")

        elif idx == 2:  # Stage 3
            p1 = self.app.planets[self.planet_a.currentIndex()]
            p2 = self.app.planets[self.planet_b.currentIndex()]
            stats = self.app.rocket.calculate_journey(p1, p2)
            summary = JourneyReport.generate_summary(stats)
            self.output.append("<b>Stage 3: Journey Parameters</b>")
            for key, val in summary.items():
                self.output.append(f"{key}: {val}")

        elif idx == 3:  # Stage 4
            day = self.day_input.value()
            self.canvas.current_day = day
            self.output.append(f"<b>Stage 4: Planet Positions (Day {day})</b>")
            for p in self.app.planets:
                self.output.append(f"{p.name}: {p.get_angle_at(day):.2f}°")
            self.canvas.update()

        elif idx >= 4:  # Stage 5 & 6
            is_dynamic = (idx == 5)
            self.p1 = self.app.planets[self.planet_a.currentIndex()]
            self.p2 = self.app.planets[self.planet_b.currentIndex()]
            start_day = self.day_input.value()

            offset = self.app.optimizer.find_window(self.app, self.p1, self.p2, start_day, is_dynamic)

            if offset is not None:
                self.start_day = start_day + offset
                self.stats = self.app.rocket.calculate_journey(self.p1, self.p2)
                self.sim_time_s = 0
                self.dynamic_flight = is_dynamic
                self.output.append(f"<b>Optimal Window Found:</b> Day {self.start_day}")
                self.timer.start(30)
            else:
                self.output.append("No suitable window found in 10 years.")

    def update_anim(self):
        """Stage 7: Animation logic."""
        self.sim_time_s += 100000

        reached_destination = False
        if self.sim_time_s >= self.stats['total_time']:
            self.sim_time_s = self.stats['total_time']
            reached_destination = True

        if getattr(self, 'dynamic_flight', False):
            self.canvas.current_day = self.start_day + (self.sim_time_s / 86400)
        else:
            self.canvas.current_day = self.start_day

        # Calculate rocket position
        rx, ry, v = self.app.get_rocket_position(
            self.p1, self.p2, self.sim_time_s, self.stats,
            self.canvas.scale, self.start_day, self.canvas.current_day,
            getattr(self, 'dynamic_flight', False)
        )

        self.canvas.rocket_pos = (rx, ry)
        self.canvas.current_speed = v

        if reached_destination:
            self.timer.stop()
            self.output.append("\n<b style='color:#00FF00;'>Touchdown confirmed!</b>")

        self.canvas.update()

if __name__ == "__main__":
    qt_app = QApplication(sys.argv)
    window = SpaceGUI()
    window.show()
    sys.exit(qt_app.exec_())