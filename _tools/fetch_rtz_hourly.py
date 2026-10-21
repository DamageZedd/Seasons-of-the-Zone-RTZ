"""Real Time Zone (RTZ) - Companion Hourly Weather Fetcher

Fetches live hour-by-hour weather from Open-Meteo for the location configured in
Seasons of the Zone (or Chornobyl by default), and writes gamedata\\configs\\rtz_weather.ltx
inside the RTZ addon folder.
"""

import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))


def find_gamma_root():
    """Finds the MO2 / GAMMA root folder containing ModOrganizer.ini."""
    for rel in ("..", os.path.join("..", ".."), os.path.join("..", "..", "..")):
        cand = os.path.abspath(os.path.join(HERE, rel))
        if os.path.isfile(os.path.join(cand, "ModOrganizer.ini")):
            return cand
    return r"C:\GAMMA"


GAMMA = find_gamma_root()
MODS = os.path.join(GAMMA, "mods")

SOTZ_MARKER = ("gamedata", "scripts", "zzz_seasons_of_the_zone.script")
RTZ_MARKER = ("gamedata", "scripts", "rtz_main.script")

WMO = [
    ({0}, "clear"),
    ({1, 2}, "partly"),
    ({3}, "cloudy"),
    ({45, 48}, "foggy"),
    ({51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82}, "rain"),
    ({71, 73, 75, 77, 85, 86}, "snow"),
    ({95, 96, 99}, "storm"),
]


def code_to_cycle(code):
    for codes, name in WMO:
        if code in codes:
            return name
    return "cloudy"


def find_mod_folder(marker, fallback_name):
    """Finds a mod folder in mods/ by its marker script, regardless of what MO2 named the folder."""
    try:
        for name in os.listdir(MODS):
            folder = os.path.join(MODS, name)
            if os.path.isfile(os.path.join(folder, *marker)):
                return folder
    except OSError:
        pass
    return os.path.join(MODS, fallback_name)


def get_place():
    """Reads configured place from Seasons of the Zone's season_weather.ltx."""
    default = {"name": "Chornobyl", "lat": 51.2763, "lon": 30.2219}
    sotz_dir = find_mod_folder(SOTZ_MARKER, "SeasonsOfTheZone")
    sotz_path = os.path.join(sotz_dir, "gamedata", "configs", "season_weather.ltx")
    if not os.path.isfile(sotz_path):
        return default

    name, lat, lon = None, None, None
    in_place = False
    try:
        with open(sotz_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if line.startswith("["):
                    in_place = (line.lower() == "[place]")
                    continue
                if not in_place or "=" not in line:
                    continue
                k, v = [x.strip() for x in line.split("=", 1)]
                if k == "name":
                    name = v
                elif k == "lat":
                    lat = float(v)
                elif k == "lon":
                    lon = float(v)
        if lat is not None and lon is not None:
            return {"name": name or "Configured Place", "lat": lat, "lon": lon}
    except Exception as e:
        print(f"Error reading place: {e}")
    return default


def fetch_hourly(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&hourly=weather_code,temperature_2m,precipitation"
        f"&timezone=auto&forecast_days=2"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "RTZ-WeatherFetcher/1.0"})
    with urllib.request.urlopen(req, timeout=12) as response:
        return json.loads(response.read().decode("utf-8"))


def main():
    place = get_place()
    print(f"  RTZ: Fetching hourly weather for {place['name']} ({place['lat']:.4f}, {place['lon']:.4f})...")
    try:
        data = fetch_hourly(place["lat"], place["lon"])
    except Exception as e:
        print(f"  RTZ: Could not fetch weather: {e}")
        return 1

    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    codes = hourly.get("weather_code", [])
    temps = hourly.get("temperature_2m", [])

    if not times or not codes:
        print("  RTZ: No hourly data in response.")
        return 1

    lines = [
        "; Real Time Zone (RTZ) - Live Hourly Weather Data",
        "; Generated automatically from Open-Meteo",
        "",
        "[place]",
        f"name = {place['name']}",
        f"lat  = {place['lat']}",
        f"lon  = {place['lon']}",
        "",
        "[hourly]",
    ]

    for i in range(min(24, len(times))):
        h = int(times[i].split("T")[1].split(":")[0])
        code = codes[i]
        cycle = code_to_cycle(code)
        temp = temps[i] if i < len(temps) else "?"
        lines.append(f"{h} = {cycle} ; {temp}C")

    content = "\n".join(lines) + "\n"

    # Write strictly to RTZ mod configs (self-contained)
    rtz_dir = find_mod_folder(RTZ_MARKER, "Seasons of the Zone - Real Time Zone (RTZ)")
    rtz_cfg_dir = os.path.join(rtz_dir, "gamedata", "configs")
    os.makedirs(rtz_cfg_dir, exist_ok=True)
    out_file = os.path.join(rtz_cfg_dir, "rtz_weather.ltx")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  RTZ: Updated 24-hour live weather forecast ({place['name']}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
