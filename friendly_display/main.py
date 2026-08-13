"""
Entry point. DashboardEngine reads config.json, builds one TransitPanel
per transit group, and runs the refresh/print loop.

Nothing here mentions Harvard, Watertown, 71, or 73 -- that all lives in
config.json.
"""

import json
import os
import time
from datetime import datetime

from .mbta_client import MBTAClient
from .queriers import TransitGroupQuerier
from .panels import TransitPanel


class DashboardEngine:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')
        with open(config_path) as f:
            config = json.load(f)

        settings = config["mbta_settings"]
        self.client = MBTAClient(base_url=settings["base_url"], api_key=settings.get("api_key"))

        self.panels = []
        for group_name, rules in config["transit_groups"].items():
            querier = TransitGroupQuerier(self.client, rules["stops"], rules.get("routes"))
            self.panels.append(TransitPanel(group_name, querier))

    def run_forever(self, interval_seconds=30):
        print("Starting dashboard...")
        try:
            while True:
                print("\033[H\033[J", end="")  # clear screen
                print(f"MBTA DASHBOARD | {datetime.now().strftime('%I:%M:%S %p')}\n")
                for panel in self.panels:
                    panel.refresh()
                    print(panel.render())
                    print()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\nExiting.")


if __name__ == "__main__":
    engine = DashboardEngine()
    engine.run_forever(interval_seconds=15)
