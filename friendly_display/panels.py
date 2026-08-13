"""
TransitPanel is the display half: it owns a querier and knows how to turn
its Departures into text. It has no idea what "eastbound" means or how
predictions get fetched -- rename a group in config.json and this class
doesn't change at all.
"""
import abc

class DataPanel(abc.ABC):
    def __init__(self, name, querier=None):
        self.name = name
        self.querier = querier

    @abc.abstractmethod
    def refresh(self, **kwargs):
        pass

    @abc.abstractmethod
    def render(self, **kwargs):
        pass

class TransitPanel(DataPanel):
    def __init__(self, name, querier, max_departures=5):
        super().__init__(name, querier)
        self.max_departures = max_departures

    def refresh(self):
        self.querier.refresh()

    def render(self):
        lines = [f"=== {self.name.upper()} ==="]
        departures = self.querier.get_items()[: self.max_departures]

        if not departures:
            lines.append(" No upcoming arrivals scheduled.")
            return "\n".join(lines)

        for dep in departures:
            alert = ""
            #alert = " *" if dep.minutes_away <= 5 else ""
            lines.append(
                f" Route {dep.route:<2} to {dep.destination:<20} | "
                f"{dep.minutes_away:>2} min{alert}  ({dep.stop_name})"
            )
        return "\n".join(lines)
