"""Real Time Zone (RTZ) - Real-Time Emission Sky Builder

Anomaly plays emissions and psi-storms with the clock at 10x, and their sky effects
(configs\\environment\\weather_effects\\fx_blowout_*.ltx, fx_psi_storm_*.ltx) are timed
for that: about 50 game minutes, which pass in 5 real minutes. RTZ's Real-Time Emissions
keep the clock at 1x, so at the effects' own timing the sky would barely start to change.

This writes a copy of each effect, from whichever mod wins it in the MO2 profile's load
order, with its keyframe times divided by 10, as <name>_rtz.ltx in RTZ's own folder.
RTZ plays those copies during real-time emissions, so the engine blends the sky exactly as
it does in vanilla. Everything else in the file is copied unchanged.

play.bat runs this on every launch through fetch_rtz_hourly.py, so the copies follow
whichever weather mod is installed. Run it by hand with:  py _tools\\rtz_build_fx.py
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

FX_NAMES = ("fx_blowout_day", "fx_blowout_night", "fx_psi_storm_day", "fx_psi_storm_night")
FX_REL = ("gamedata", "configs", "environment", "weather_effects")
SUFFIX = "_rtz"
# The surge and psi-storm managers' `surge_time_factor`: the clock speed the effects were made for
SPEEDUP = 10

RTZ_MARKER = ("gamedata", "scripts", "rtz_main.script")
KEY_RE = re.compile(rb"^(\s*)\[(\d+):(\d+):(\d+)\]")


def find_gamma_root():
    """The MO2 folder: the one holding ModOrganizer.ini, this script's folder or above it."""
    for rel in (".", "..", os.path.join("..", ".."), os.path.join("..", "..", "..")):
        cand = os.path.abspath(os.path.join(HERE, rel))
        if os.path.isfile(os.path.join(cand, "ModOrganizer.ini")):
            return cand
    return None


def profile_name(gamma):
    """The profile MO2 opens, from ModOrganizer.ini's selected_profile."""
    try:
        with open(os.path.join(gamma, "ModOrganizer.ini"), encoding="utf-8", errors="replace") as f:
            for line in f:
                if line.startswith("selected_profile="):
                    val = line.split("=", 1)[1].strip()
                    m = re.match(r"@ByteArray\((.*)\)$", val)
                    return m.group(1) if m else val
    except OSError:
        pass
    return None


def enabled_mods(gamma):
    """The profile's enabled mods, highest priority first (the top of modlist.txt wins)."""
    profile = profile_name(gamma)
    if not profile:
        return []
    path = os.path.join(gamma, "profiles", profile, "modlist.txt")
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return [l[1:].rstrip("\r\n") for l in f if l.startswith("+")]
    except OSError:
        return []


def find_rtz_folder(gamma):
    """RTZ's folder: the enabled mod holding rtz_main.script, or failing that any mod that does."""
    mods = os.path.join(gamma, "mods")
    for name in enabled_mods(gamma):
        if os.path.isfile(os.path.join(mods, name, *RTZ_MARKER)):
            return os.path.join(mods, name)
    try:
        for name in sorted(os.listdir(mods)):
            if os.path.isfile(os.path.join(mods, name, *RTZ_MARKER)):
                return os.path.join(mods, name)
    except OSError:
        pass
    return None


def find_winner(gamma, fx_name, skip):
    """The file the game loads for an effect: overwrite first, then enabled mods by priority."""
    rel = FX_REL + (fx_name + ".ltx",)
    over = os.path.join(gamma, "overwrite", *rel[1:])
    if os.path.isfile(over):
        return over, "overwrite"
    for name in enabled_mods(gamma):
        folder = os.path.join(gamma, "mods", name)
        if skip and os.path.normcase(os.path.abspath(folder)) == os.path.normcase(os.path.abspath(skip)):
            continue
        path = os.path.join(folder, *rel)
        if os.path.isfile(path):
            return path, name
    return None, None


def compress(raw, speedup=SPEEDUP):
    """The effect with each [HH:MM:SS] keyframe time divided by `speedup`, everything else as it was."""
    nl = b"\r\n" if b"\r\n" in raw else b"\n"
    out, last = [], -1
    for line in raw.split(nl):
        m = KEY_RE.match(line)
        if m:
            secs = int(m.group(2)) * 3600 + int(m.group(3)) * 60 + int(m.group(4))
            new = int(round(secs / float(speedup)))
            if new <= last:                      # keep keyframes in order after rounding
                new = last + 1
            last = new
            stamp = b"[%02d:%02d:%02d]" % (new // 3600, (new // 60) % 60, new % 60)
            line = m.group(1) + stamp + line[m.end():]
        out.append(line)
    return nl.join(out)


def build(gamma=None, quiet=False):
    """Writes the compressed copies; returns how many were written."""
    gamma = gamma or find_gamma_root()
    say = (lambda *a: None) if quiet else print
    if not gamma:
        say("  RTZ: ModOrganizer.ini not found; real-time emission skies not built.")
        return 0
    rtz = find_rtz_folder(gamma)
    if not rtz:
        say("  RTZ: RTZ's mod folder not found; real-time emission skies not built.")
        return 0
    out_dir = os.path.join(rtz, *FX_REL)
    os.makedirs(out_dir, exist_ok=True)
    written = 0
    for fx in FX_NAMES:
        out = os.path.join(out_dir, fx + SUFFIX + ".ltx")
        src, owner = find_winner(gamma, fx, rtz)
        if not src:
            # Only the base game has it (packed in .db archives): RTZ falls back to pacing the original
            if os.path.isfile(out):
                os.remove(out)
            continue
        with open(src, "rb") as f:
            raw = f.read()
        header = (b"; Real Time Zone (RTZ): " + fx.encode() + b" from \"" + owner.encode("utf-8", "replace")
                  + b"\", keyframe times divided by " + str(SPEEDUP).encode()
                  + b" for real-time emissions. Rebuilt by _tools\\rtz_build_fx.py on every play.bat launch.")
        nl = b"\r\n" if b"\r\n" in raw else b"\n"
        data = header + nl + compress(raw)
        try:
            with open(out, "rb") as f:
                if f.read() == data:
                    written += 1
                    continue
        except OSError:
            pass
        with open(out, "wb") as f:
            f.write(data)
        written += 1
    say("  RTZ: Real-time emission skies ready (%d of %d effects)." % (written, len(FX_NAMES)))
    return written


if __name__ == "__main__":
    sys.exit(0 if build() else 1)
