"""
Talks to the MBTA v3 API. Owns two things: raw HTTP calls, and a cache of
stop_id -> name, since looking up a name is just another kind of query.
Nothing in this file knows about "eastbound" or panels.
"""

import requests


class MBTAClient:
    def __init__(self, base_url="https://api-v3.mbta.com", api_key=None):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.headers = {"Accept": "application/vnd.api+json"}
        if api_key and api_key != "YOUR_FREE_MBTA_API_KEY":
            self.headers["x-api-key"] = api_key
        self._stop_name_cache = {}

    def get_stop_name(self, stop_id):
        """Cached lookup -- each stop_id triggers at most one real
        request, no matter how many times or from where it's called."""
        if stop_id in self._stop_name_cache:
            return self._stop_name_cache[stop_id]
        try:
            resp = self.session.get(
                f"{self.base_url}/stops/{stop_id}", headers=self.headers, timeout=10
            )
            resp.raise_for_status()
            name = resp.json()["data"]["attributes"]["name"]
        except Exception:
            name = f"Stop #{stop_id}"
        self._stop_name_cache[stop_id] = name
        return name

    def fetch_predictions(self, stop_ids, route_ids=None):
        """Raw predictions response for one or more stops in a single
        call, optionally restricted to specific routes. The API filters
        and sorts across all the stops itself -- no need to fetch each
        stop separately and merge client-side."""
        params = {
            "filter[stop]": ",".join(str(s) for s in stop_ids),
            "include": "route",
            "sort": "arrival_time",
        }
        if route_ids:
            params["filter[route]"] = ",".join(str(r) for r in route_ids)
        resp = self.session.get(
            f"{self.base_url}/predictions", params=params, headers=self.headers, timeout=10
        )
        resp.raise_for_status()
        return resp.json()
