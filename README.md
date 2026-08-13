# mybus

A modular MBTA departure board, built for a Harvard Square / Mt Auburn St /
Belmont St 71+73 setup -- but nothing about that lives in code. It's all
in `config.json`.

## How it fits together

```
MBTAClient          -- raw HTTP calls to the MBTA API, plus a cache of
                        stop_id -> name (a stop-name lookup is just
                        another kind of query, so it lives here rather
                        than off in its own file). Knows nothing about
                        panels or directions.

TransitGroupQuerier  -- the "querying" half of the split. Given a list of
                        stop_ids and route_ids for one named group, it
                        fetches predictions for all of them in a single
                        API call (the MBTA API itself filters and sorts
                        across multiple stops, so there's no need to
                        query each stop separately and merge results in
                        Python) and returns a sorted list of Departures.

TransitPanel          -- the "display" half. Owns a querier, turns its
                        Departures into text. Doesn't know what the
                        group's name means or how predictions are
                        fetched -- rename a group in config.json and
                        this class doesn't change.

DashboardEngine       -- in main.py. Reads config.json, builds one
                        TransitGroupQuerier + TransitPanel per transit
                        group, and runs the refresh/print loop.
```

Both `TransitGroupQuerier` and `TransitPanel` just expose `refresh()` /
`get_items()` (or `render()`) -- that's a convention, not an enforced
interface, so a future querier for weather or trash pickup can follow the
same shape without inheriting from anything.

## Setup

```bash
pip install -r requirements.txt
cp config.example.json config.json
# edit config.json with your real stop_ids and API key
python main.py
```

Get a free API key at https://api-v3.mbta.com (used for higher rate
limits -- the app runs without one, just more conservatively rate-limited).

To change the refresh interval, edit the `run_forever(interval_seconds=30)`
call at the bottom of `main.py`.

## Finding your stop_ids

```
GET https://api-v3.mbta.com/stops?filter[route]=71,73
```

or browse https://www.mbta.com/schedules/71/line and
https://www.mbta.com/schedules/73/line and read the ID out of each stop's
URL. You need the IDs for whichever stop(s) sit on each side of your
fork -- list the "toward Harvard" ones under one group and the "toward
Watertown/Belmont" ones under the other, same as `config.example.json`.

## Extending with a new kind of panel (weather, trash day, etc.)

1. Write a querier class with `refresh()` / `get_items()` -- it can talk
   to any API you want; `TransitGroupQuerier` is just one example of the
   shape.
2. Write a panel class with `refresh()` / `render()`, following
   `TransitPanel`.
3. Build and refresh it in `DashboardEngine.__init__` / `run_forever`
   alongside the transit panels.

Keep it all in `main.py` while there are only a couple of panel types,
and only split into more files once that actually gets unwieldy.
