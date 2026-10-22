"""Real Time Zone (RTZ) - Companion Hourly Weather Fetcher & Installer

Fetches live hour-by-hour weather from Open-Meteo for the location configured in
Seasons of the Zone (or Chornobyl by default), maps each forecast hour to the
PC's local wall-clock hour (0..23) so the sky matches what is happening at the
configured location at that exact moment, and writes gamedata\\configs\\rtz_weather.ltx.

Note: Seasons of the Zone 2.11.0+ natively writes an [hourly] section mapped to
the PC's clock in season_weather.ltx, which RTZ reads first. This script serves
as an optional standalone fallback for older Seasons versions.
"""

from datetime import datetime, timezone
import json
import os
import shutil
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
    """Fetches hourly forecast in UTC (GMT) so timestamps map cleanly to PC local clock hours."""
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&hourly=weather_code,temperature_2m,precipitation"
        f"&timezone=GMT&forecast_days=2"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "RTZ-WeatherFetcher/1.0.2"})
    with urllib.request.urlopen(req, timeout=12) as response:
        return json.loads(response.read().decode("utf-8"))


def install_hook():
    """Copies fetch_rtz_hourly.py to GAMMA\\_tools and hooks GAMMA\\play.bat."""
    tools_dir = os.path.join(GAMMA, "_tools")
    os.makedirs(tools_dir, exist_ok=True)
    dst_script = os.path.join(tools_dir, "fetch_rtz_hourly.py")
    src_script = os.path.abspath(__file__)
    if os.path.normcase(src_script) != os.path.normcase(dst_script):
        shutil.copy2(src_script, dst_script)
        print(f"  + Installed {dst_script}")

    play_bat = os.path.join(GAMMA, "play.bat")
    if os.path.isfile(play_bat):
        with open(play_bat, "rb") as f:
            raw = f.read()
        hook_line = b'if exist "_tools\\fetch_rtz_hourly.py" %PY% "_tools\\fetch_rtz_hourly.py"'
        if b"fetch_rtz_hourly.py" not in raw:
            target = b'%PY% "_tools\\fetch_weather.py"'
            if target in raw:
                nl = b"\r\n" if b"\r\n" in raw else b"\n"
                raw = raw.replace(target, target + nl + hook_line, 1)
                with open(play_bat, "wb") as f:
                    f.write(raw)
                print(f"  + Added hourly weather hook to {play_bat}")
        else:
            print(f"  + {play_bat} already has the RTZ hourly weather hook")


def main():
    if "--install" in sys.argv:
        install_hook()

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

    now_local = datetime.now()
    today_str = now_local.strftime("%Y-%m-%d")
    now_utc_ts = datetime.now(timezone.utc).timestamp()

    # Map the next 24 hours from now to the PC's local wall-clock hours (0..23)
    mapped_hours = {}
    for i, t_str in enumerate(times):
        try:
            dt_utc = datetime.strptime(t_str, "%Y-%m-%dT%H:%M").replace(tzinfo=timezone.utc)
            ts = dt_utc.timestamp()
        except ValueError:
            continue
        # Pick the 24 hourly slots covering [now - 1h, now + 23h]
        if -3600 <= (ts - now_utc_ts) < 23 * 3600:
            pc_hour = datetime.fromtimestamp(ts).hour
            if pc_hour not in mapped_hours:
                code = codes[i] if i < len(codes) else 3
                temp = temps[i] if i < len(temps) else "?"
                mapped_hours[pc_hour] = (code_to_cycle(code), temp)

    lines = [
        "; Real Time Zone (RTZ) - Live Hourly Weather Data (Mapped to PC Clock)",
        "; Generated automatically from Open-Meteo",
        "",
        "[place]",
        f"name = {place['name']}",
        f"lat  = {place['lat']}",
        f"lon  = {place['lon']}",
        f"date = {today_str}",
        "",
        "[hourly]",
    ]

    for h in range(24):
        if h in mapped_hours:
            cycle, temp = mapped_hours[h]
        else:
            idx = min(h, len(codes) - 1)
            cycle = code_to_cycle(codes[idx])
            temp = temps[idx] if idx < len(temps) else "?"
        lines.append(f"{h} = {cycle} ; {temp}C")

    content = "\n".join(lines) + "\n"

    # Write strictly to RTZ mod configs (self-contained)
    rtz_dir = find_mod_folder(RTZ_MARKER, "Seasons of the Zone - Real Time Zone (RTZ)")
    rtz_cfg_dir = os.path.join(rtz_dir, "gamedata", "configs")
    os.makedirs(rtz_cfg_dir, exist_ok=True)
    out_file = os.path.join(rtz_cfg_dir, "rtz_weather.ltx")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  RTZ: Updated 24-hour live weather forecast ({place['name']}) mapped to PC clock.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
