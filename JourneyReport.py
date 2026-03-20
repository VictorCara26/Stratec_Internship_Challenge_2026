class JourneyReport:

    @staticmethod
    def format_time(seconds):
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        sec = int(seconds % 60)
        return f"{days}d {hours}h {minutes}m {sec}s"

    @classmethod
    def generate_summary(cls, stats):
        return {
            "Time to Cruising": f"{stats['t_burn']:.1f} s", # [cite: 105]
            "Dist from Start Surface": f"{stats['d_burn']/1000:.1f} km", # [cite: 106]
            "Cruise Duration": cls.format_time(stats['t_cruise']), # [cite: 107]
            "Decel Start Distance": f"{stats['d_burn']/1000:.1f} km", # [cite: 108]
            "Decel Time": f"{stats['t_burn']:.1f} s", # [cite: 110]
            "Total Journey": cls.format_time(stats['total_time']) # [cite: 111]
        }