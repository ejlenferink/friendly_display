"""Simple data container passed from the querier layer to the display layer."""

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class Departure:
    route: str          # MBTA bus route IDs are just the route number, e.g. "71"
    destination: str    # e.g. "Watertown Square"
    when: datetime
    stop_name: str = ""

    @property
    def minutes_away(self):
        now = datetime.now(self.when.tzinfo or timezone.utc)
        return max(0, int((self.when - now).total_seconds() // 60))
