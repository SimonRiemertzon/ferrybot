#!/usr/bin/env python3
import json, os, sys
from datetime import datetime
from urllib.request import urlopen, Request

API_URL = "https://api.trafikinfo.trafikverket.se/v2/data.json"
# weekday() returns 0=Mon..6=Sun; Trafikverket IDs: Mon=2..Fri=6, Sat=7, Sun=1
_WEEKDAY_ID = {0: 2, 1: 3, 2: 4, 3: 5, 4: 6, 5: 7, 6: 1}

QUERY = """<REQUEST>
  <LOGIN authenticationkey="{key}"/>
  <QUERY objecttype="FerryRoute" namespace="ferry.trafficinfo" schemaversion="1.2">
    <FILTER><EQ name="Name" value="Svanesundsleden"/></FILTER>
  </QUERY>
</REQUEST>"""


def fetch_route():
    key = os.environ.get("TRAFIKVERKET_KEY", "demokey")
    body = QUERY.format(key=key).encode()
    req = Request(API_URL, data=body, headers={"Content-Type": "text/xml"})
    with urlopen(req) as r:
        return json.load(r)["RESPONSE"]["RESULT"][0]["FerryRoute"][0]


def next_departures(schedule, harbor_name, now_hm, n=3):
    times = sorted(
        e["Time"] for e in schedule if e["Harbor"]["Name"].lower() == harbor_name.lower()
    )
    upcoming = [t for t in times if t > now_hm]
    if len(upcoming) >= n:
        return upcoming[:n], False
    # wrap around to start of next day
    return (upcoming + times)[:n], len(upcoming) < n


def active_period(timetable):
    today_id = _WEEKDAY_ID[datetime.today().weekday()]
    for tt in timetable:
        for period in tt["Period"]:
            if any(w["Id"] == today_id for w in period["Weekday"]):
                return period
    return timetable[0]["Period"][0]


def main():
    harbors = {"svanesund": "Kolhättan", "kolhättan": "Svanesund"}
    args = sys.argv[1:]

    harbor_arg = next((a.lower() for a in args if a.lower() in harbors), None)
    count_arg = next((int(a) for a in args if a.isdigit()), 3)

    invalid = [a for a in args if a.lower() not in harbors and not a.isdigit()]
    if invalid:
        print("Usage: ferry [svanesund|kolhättan] [count]")
        sys.exit(1)

    route = fetch_route()
    period = active_period(route["Timetable"])
    now_hm = datetime.now().strftime("%H:%M")

    show = [harbor_arg] if harbor_arg else list(harbors)
    for from_harbor in show:
        to_harbor = harbors[from_harbor]
        times, wrapped = next_departures(period["Schedule"], from_harbor, now_hm, count_arg)
        label = f"{from_harbor.capitalize()} → {to_harbor}  ({period['Name']})"
        suffix = "  (wraps to tomorrow)" if wrapped else ""
        print(f"{label}\n  Next: {', '.join(times)}{suffix}\n")


if __name__ == "__main__":
    main()
