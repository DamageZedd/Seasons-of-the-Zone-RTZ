# Changelog

## [1.0.0] - 2026-10-20

### Added
- **1:1 Real-Time Clock Synchronization (`rtz_clock.script`)**:
  - Enforces a 1:1 real-time `time_factor` (`1.0` default, configurable `1.0–10.0` in MCM).
  - Synchronizes the in-game clock (`HH:MM`) with the host OS wall clock on game load and level transition, with circular sub-minute wrap protection.
  - Strictly guards Hunger (`satiety`), Thirst (`actor_status_thirst`), Sleep (`actor_status_sleep`), Health, Stamina, Bleeding, and Surge/Psi-Storm timers on all clock sync jumps and rest wake-ups so player vitals are left 100% untouched.
  - **Vanilla Time-Scale Preservation (`vanilla_vitals_alife_scale`)**: Ensures Hunger (`satiety_v`), Thirst (`drink_chk`), Sleep (`sleep_chk`), A-Life squad stay/idle timers (`sim_squad_scripted`), offline squad travel speed (`mod_system_rtz_alife.ltx`), Smart Terrain respawns (`smart_terrain` & ZCP `smr_pop`), and Emission/Psi-Storm intervals continue to progress at the exact same real-world pace as vanilla Anomaly (`time_factor = 6.0`) while the world clock runs at 1:1 real time.
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
