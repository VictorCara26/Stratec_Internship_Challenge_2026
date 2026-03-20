from PyQt5.QtCore import QCoreApplication


class TransferOptimizer:
    def find_window(self, app, start_p, dest_p, initial_day, dynamic=False):
        max_search_days = 3650  # 10 years
        best_day = None
        min_distance = float('inf')

        stats = app.rocket.calculate_journey(start_p, dest_p)

        for d in range(max_search_days):
            # --- PREVENT CRASH: Keep GUI alive ---
            if d % 100 == 0:
                QCoreApplication.processEvents()

            current_day = initial_day + d

            # Check for 0-degree alignment [cite: 124, 139]
            ang1 = start_p.get_angle_at(current_day)
            if abs(ang1 - 0) < 1.0:
                ang2 = dest_p.get_angle_at(current_day)
                diff = abs(ang2 - 0)

                # Perform collision check [cite: 139, 140]
                blocked, _ = app.collision_mgr.is_path_blocked(
                    start_p, dest_p, current_day, stats, dynamic
                )

                if not blocked and diff < min_distance:
                    min_distance = diff
                    best_day = d
                    if diff < 0.1: break  # Perfect alignment found

        return best_day