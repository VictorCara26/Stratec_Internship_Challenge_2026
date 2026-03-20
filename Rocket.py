import math


class Rocket:
    G = 6.67e-11

    def __init__(self, engine_count, accel_per_engine):
        self.a_total = engine_count * accel_per_engine  # [cite: 49, 53]

    def get_escape_velocity(self, planet):
        return math.sqrt((2 * self.G * planet.mass_kg) / planet.radius_m)

    def get_burn_stats(self, target_v):
        time = target_v / self.a_total
        dist_m = 0.5 * self.a_total * (time ** 2)
        dist_km = dist_m / 1000.0

        return time, dist_km

    def calculate_journey(self, start_p, dest_p):
        v_cruise = max(self.get_escape_velocity(start_p), self.get_escape_velocity(dest_p))

        t_burn, d_burn = self.get_burn_stats(v_cruise)

        dist_centers = abs(start_p.orbital_radius_m - dest_p.orbital_radius_m)
        dist_surf = dist_centers - start_p.radius_m - dest_p.radius_m

        d_cruise = dist_surf - (2 * d_burn)
        t_cruise = d_cruise / v_cruise

        return {
            "v_cruise": v_cruise,
            "t_burn": t_burn,
            "d_burn": d_burn,
            "d_cruise": d_cruise,
            "t_cruise": t_cruise,
            "total_time": (2 * t_burn) + t_cruise
        }