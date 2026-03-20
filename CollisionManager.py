import math


class CollisionManager:
    def __init__(self, all_planets):
        self.all_planets = all_planets

    def is_path_blocked(self, start_p, dest_p, current_day, travel_stats, dynamic=False):
        # Only check planets physically between the two orbits
        inner_r = min(start_p.orbital_radius_au, dest_p.orbital_radius_au)
        outer_r = max(start_p.orbital_radius_au, dest_p.orbital_radius_au)
        potential_obstacles = [p for p in self.all_planets if inner_r < p.orbital_radius_au < outer_r]

        for obs in potential_obstacles:
            check_day = current_day
            rocket_angle_at_intercept = 0.0

            if dynamic:
                # 1. Rocket interception time
                dist_to_obs = abs(obs.orbital_radius_m - start_p.orbital_radius_m)
                days_to_intercept = (dist_to_obs / travel_stats['v_cruise']) / 86400
                check_day += days_to_intercept

                # 2. Rocket angle at the moment
                total_travel_days = travel_stats['total_time'] / 86400
                arrival_angle = dest_p.get_angle_at(current_day + total_travel_days)

                # Rocket starts at 0° and ends at arrival_angle
                total_dist = abs(dest_p.orbital_radius_m - start_p.orbital_radius_m)
                progress_fraction = dist_to_obs / total_dist
                rocket_angle_at_intercept = progress_fraction * arrival_angle

            # 3. Obstacle planet location at specific time
            obs_angle = obs.get_angle_at(check_day)

            # 4. Collision Check using angular width
            angle_diff = abs(obs_angle - rocket_angle_at_intercept) % 360
            if angle_diff > 180: angle_diff = 360 - angle_diff
            angular_radius = math.degrees(obs.radius_m / obs.orbital_radius_m)

            if angle_diff < angular_radius:
                return True, obs.name
        return False, None