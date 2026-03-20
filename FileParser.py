import os


class FileParser:

    @staticmethod
    def parse_planetary_data(filepath):
        planets = []
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Missing file: {filepath}")

        with open(filepath, 'r') as f:
            for line in f:
                try:
                    name, data = line.strip().split(':')
                    diam, mass = data.split(',')
                    clean_diam = float(''.join(c for c in diam if c.isdigit() or c == '.'))
                    clean_mass = float(''.join(c for c in mass if c.isdigit() or c == '.'))
                    planets.append({"name": name, "diam_km": clean_diam, "mass_rel": clean_mass})
                except (ValueError, IndexError):
                    print(f"Warning: Skipping malformed line in {filepath}")
        return planets

    @staticmethod
    def parse_system_data(filepath):
        system_info = {}
        with open(filepath, 'r') as f:
            for line in f:
                try:
                    name, data = line.strip().split(':')
                    period, orbit = data.split(',')
                    p_val = float(''.join(c for c in period if c.isdigit() or c == '.'))
                    o_val = float(''.join(c for c in orbit if c.isdigit() or c == '.'))
                    system_info[name] = {"period": p_val, "orbit_au": o_val}
                except ValueError:
                    continue
        return system_info  