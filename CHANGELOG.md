# Changelog

## [1.0.1] - 2026-10-21

### Added
- **Vanilla Time-Scale Preservation (`vanilla_vitals_alife_scale`, enabled by default)**:
  - **Hunger (`db.actor.satiety`)**: Compensates C++ engine `satiety_v` drain for `time_factor = 1.0` so hunger drains at the exact same real-world rate as vanilla Anomaly (`time_factor = 6.0`).
  - **Thirst & Sleep (`actor_status_thirst` & `actor_status_sleep`)**: Dynamically scales `drink_chk` and `sleep_chk` check intervals via Lua upvalues (`300 * (cur_tf / 6.0)` in-game seconds = `50` real seconds per tick) so thirst and sleep deprivation progress at the exact vanilla `6.0x` real-time pace.
  - **A-Life Squad Movement & Stay Timers (`sim_squad_scripted`, `mod_system_rtz_alife.ltx`)**: Scales squad smart-terrain `idle_time` via `squad_on_update` and compensates offline squad `going_speed` / `current_level_going_speed` via DLTX so A-Life squads travel and rotate between smart terrains at vanilla real-world speed.
  - **Smart Terrain Respawns (`smart_terrain` & ZCP `smr_pop`)**: Hooks `on_try_respawn` and `smr_pop.smart_can_respawn` so stalker and mutant respawn cooldowns match vanilla real-world intervals.
  - **Surge & Psi-Storm Pacing (`surge_manager` & `psi_storm_manager`)**: Scales emission and psi-storm `_delta` intervals to match vanilla real-world frequency.
- **Full Rest Duration Balance (`rtz_mcm.script`, `rtz_rest.script`)**:
  - Updated **Full Rest Duration** in MCM to **Minutes** with a default of **5 minutes** and a maximum of **10 minutes** (`1–10 min`).

### Fixed
- **Strict Vitals Guard on Clock Sync & Rest (`rtz_clock.script`, `rtz_rest.script`)**:
  - Replaced clamped vitals restoration with `change_game_time_guarded`, which snapshots and restores the **exact** pre-jump values of Hunger (`satiety`), Thirst (`last_drink` + sub-tick `last_drink_chk` offset), Sleep (`last_sleep` + sub-tick `last_sleep_chk` offset), Health, Stamina, Bleeding, and Surge/Psi-Storm progress on both initial sync and periodic drift checks.
  - Guarded `satiety` and `last_drink` around `actor_on_sleep` in `rtz_rest.script` so waking from real-time rest never triggers third-party hunger/thirst penalties.
- **X-Ray Engine `get_game_hms` Compatibility (`rtz_clock.script`)**:
  - Replaced non-existent `level.get_time_seconds()` call with `game.get_game_time():get(Y, M, D, gh, gm, gs, ms)`.

---

## [1.0.0] - 2026-10-20

### Added
- **1:1 Real-Time Clock Synchronization (`rtz_clock.script`)**:
  - Enforces a 1:1 real-time `time_factor` (`1.0` default, configurable `1.0–10.0` in MCM).
  - Synchronizes the in-game clock (`HH:MM`) with the host OS wall clock on game load and level transition, with circular sub-minute wrap protection.
  - Added post-jump vitals and surge/psi-storm safeguards so syncing the clock after hours offline never causes starvation, dehydration, exhaustion blackouts, or immediate overdue emissions.
- **Live Real-World Weather Engine (`rtz_weather.script`, `_tools/fetch_rtz_hourly.py`, `setup_rtz.bat`)**:
  - Reads hour-by-hour Open-Meteo weather forecasts (`rtz_weather.ltx`) and *Seasons of the Zone*'s `season_weather.ltx` (with built-in diurnal fallback) to drive in-game weather cycles (`clear`, `partly`, `cloudy`, `foggy`, `rain`, `storm`, `snow`).
  - Syncs `WeatherManager.day_plan` so *Seasons of the Zone*'s in-game PDA Forecast tab displays the real-world schedule.
  - Non-destructively hooks both **Atmospherics** (`WeatherManager.get_next_weather_cycle`) and **W.P.W.M.** (`WeatherManager.check_day_plan`).
  - Included one-click `setup_rtz.bat` installer inside the mod folder so any user can install `_tools/fetch_rtz_hourly.py` into `GAMMA\_tools` and hook `play.bat` automatically.
- **Real-Time Bed & Campfire Resting (`rtz_rest.script`, `ui_rtz_rest.xml`)**:
  - Replaces multi-hour time-skip sleeping with the interactive `UIRtzRest` screen (progress bar, real-time clock, comfort bonus, `SPACE`/`ESC` or button wake-up, danger/damage interrupt, and autosave on wake).
  - Added passive fatigue recovery when resting near lit campfires (`bind_campfire.campfires_all`).
- **MCM Configuration & Localization (`rtz_mcm.script`, `ui_mcm_rtz.xml`)**:
  - Full MCM menu (`rtz`) with English and Russian (`windows-1251`) localizations.
