import math

class Planet:
    AU_TO_M = 149597870700.0

    def __init__(self, name, diam_km, mass_rel, period=0, orbit_au=0):
        self.name = name
        self.diameter_km = diam_km
        self.radius_m = (diam_km / 2) * 1000
        self.period = period
        self.orbital_radius_au = orbit_au
        self.orbital_radius_m = orbit_au * self.AU_TO_M
        self.current_angle = 0.0

        if self.name == 'Earth':
            self.mass_kg = 6e24
        else:
            self.mass_kg = mass_rel * 6e24

    def update_position(self, days):
        if self.period > 0:
            self.current_angle = (360.0 / self.period * (days % self.period)) % 360
        return self.current_angle

    def get_angle_at(self, days):
        if self.period == 0: return 0
        return (360.0 / self.period * (days % self.period)) % 360

    def get_coords(self, days, scale):
        angle = self.get_angle_at(days)
        rad = math.radians(angle - 90)
        dist = self.orbital_radius_au * scale
        return dist * math.cos(rad), dist * math.sin(rad)