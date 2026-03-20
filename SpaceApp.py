import math

from CollisionManager import CollisionManager
from FileParser import FileParser
from Planet import Planet
from Rocket import Rocket
from TransferOptimizer import TransferOptimizer


class SpaceApp:
    def __init__(self, p_path, r_path, s_path):
        p_data = FileParser.parse_planetary_data(p_path)
        s_data = FileParser.parse_system_data(s_path)

        self.planets = []
        for p in p_data:
            name = p['name']
            if name in s_data:
                self.planets.append(Planet(
                    name, p['diam_km'], p['mass_rel'],
                    s_data[name]['period'], s_data[name]['orbit_au']
                ))

        self.rocket = Rocket(4, 10)  # 4 engines, 10 m/s^2 acceleration
        self.collision_mgr = CollisionManager(self.planets)
        self.optimizer = TransferOptimizer()

    def get_rocket_position(self, start_p, dest_p, time_elapsed_s, stats, scale, start_day, current_day, dynamic):
        try:
            t = time_elapsed_s
            accel = self.rocket.a_total
            v_cruise = stats.get('v_cruise', 0)
            t_burn = stats.get('t_burn', 0)
            t_cruise = stats.get('t_cruise', 0)
            total_time = stats.get('total_time', 1)  # Prevent division by zero

            if t <= t_burn:
                current_d_m = 0.5 * accel * (t ** 2)
                current_v = accel * t
            elif t <= (t_burn + t_cruise):
                current_d_m = stats.get('d_burn', 0) + (v_cruise * (t - t_burn))
                current_v = v_cruise
            else:
                decel_t = max(0, t - t_burn - t_cruise)
                current_d_m = stats.get('d_burn', 0) + stats.get('d_cruise', 0) + \
                              (v_cruise * decel_t - 0.5 * accel * (decel_t ** 2))
                current_v = max(0.0, v_cruise - (accel * decel_t))
        except (KeyError, TypeError):
            return 0, 0, 0

        x1, y1 = start_p.get_coords(start_day, scale)

        if dynamic:
            arrival_day = start_day + (total_time / 86400.0)
            x2, y2 = dest_p.get_coords(arrival_day, scale)
        else:
            x2, y2 = dest_p.get_coords(start_day, scale)

        dx = x2 - x1
        dy = y2 - y1
        dist_px = math.sqrt(dx ** 2 + dy ** 2)

        if dist_px == 0: return x1, y1, current_v

        ux, uy = dx / dist_px, dy / dist_px

        visual_boost = 1.5e-8
        r1_px = max(2.0, (start_p.radius_m * visual_boost) * scale)
        r2_px = max(2.0, (dest_p.radius_m * visual_boost) * scale)

        start_surf_x = x1 + ux * r1_px
        start_surf_y = y1 + uy * r1_px
        end_surf_x = x2 - ux * r2_px
        end_surf_y = y2 - uy * r2_px

        dist_centers_m = abs(dest_p.orbital_radius_m - start_p.orbital_radius_m)
        dist_surf_m = dist_centers_m - start_p.radius_m - dest_p.radius_m

        fraction = min(1.0, current_d_m / dist_surf_m) if dist_surf_m > 0 else 1.0

        rx = start_surf_x + (end_surf_x - start_surf_x) * fraction
        ry = start_surf_y + (end_surf_y - start_surf_y) * fraction

        return rx, ry, current_v