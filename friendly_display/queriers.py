"""
TransitGroupQuerier is the "querying" half of the split: it fetches and
parses predictions for one named group of stops (e.g. "Eastbound (To
Harvard Sq)") and hands back a sorted list of Departures. TransitPanel,
in panels.py, is the "display" half, and only ever talks to this class
through refresh()/get_items() -- it never touches the API or the parsing.
"""
import abc
from datetime import datetime

from .models import Departure

class DataQuerier(abc.ABC):
    """Abstract base class handling external API requests and caching."""
    def __init__(self, client=None):
        self.client = client

    @abc.abstractmethod
    def refresh(self, **kwargs):
        pass

    @abc.abstractmethod
    def get_items(self, **kwargs):
        pass

class TransitGroupQuerier(DataQuerier):
    def __init__(self, client, stop_ids, route_ids=None):
        super().__init__(client)
        self.stop_ids = [str(s) for s in stop_ids]
        self.route_ids = [str(r) for r in route_ids] if route_ids else None
        self.departures = []

    def refresh(self):
        payload = self.client.fetch_predictions(self.stop_ids, self.route_ids)
        self.departures = self._parse(payload)

    def get_items(self):
        return self.departures

    def _parse(self, payload):
        routes_by_id = {
            item["id"]: item for item in payload.get("included", []) if item["type"] == "route"
        }
        departures = []

        for pred in payload.get("data", []):
            attrs = pred["attributes"]
            rels = pred["relationships"]

            when_str = attrs.get("arrival_time") or attrs.get("departure_time")
            if not when_str:
                continue
            when = datetime.fromisoformat(when_str)

            route_id = rels["route"]["data"]["id"]
            stop_id = rels["stop"]["data"]["id"]

            # Route resources carry direction_destinations, a 2-item list
            # of display names indexed by direction_id -- this gets us a
            # destination without a separate trip lookup.
            destination = ""
            route = routes_by_id.get(route_id)
            direction_id = attrs.get("direction_id")
            if route and direction_id is not None:
                try:
                    destination = route["attributes"]["direction_destinations"][direction_id]
                except (IndexError, KeyError, TypeError):
                    pass

            departures.append(Departure(
                route=route_id,
                destination=destination,
                when=when,
                stop_name=self.client.get_stop_name(stop_id),
            ))

        departures.sort(key=lambda d: d.when)
        return departures
