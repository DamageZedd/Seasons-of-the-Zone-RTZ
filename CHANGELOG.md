# Changelog

## [1.0.2] - 2026-10-22

### 1. W.P.W.M. (`UmYeahNo`) `check_day_plan` Delegation & Credit
- **`rtz_weather.script`**: Updated the `WeatherManager.check_day_plan` hook so that whenever `self.pre_blowout_period or self.weather_fx` is set, it calls `return org_check_day_plan(self)` directly instead of duplicating the emission block—automatically inheriting any future W.P.W.M. fixes.
- **`README.md` & `CHANGELOG.md`**: Added **W.P.W.M. (Weighted Probability Weather Manager) by `UmYeahNo`** to the Credits.

### 2. Hunger & Thirst Mode MCM Selector (`vitals_mode`)
- **`rtz_mcm.script` & `rtz_clock.script`**: Added a 3-way **Hunger & Thirst Mode** dropdown in MCM (`ui_mcm_rtz_vitals_mode` in `ui_mcm_rtz.xml`):
  - **`Vanilla Speed (6x)`** *(Default)*: Hunger and Thirst drain at vanilla Anomaly real-time speed.
  - **`Real-Time Speed (1:1)`**: Hunger and Thirst drain 6x slower in real time, matching the 1:1 clock (`drink_chk = 300` in-game seconds = 5 real minutes per tick, and C++ `satiety_v` runs unscaled at `1:1`).
  - **`Disabled (No Eat / Drink)`**: Locks `db.actor.satiety = 1.0` and keeps `actor_status_thirst` `last_drink = 0` so the protagonist never needs to eat or drink.

### 3. 1:1 Medkit / Booster Healing & Passive Recovery Fix (`fix_boosters_and_effects`)
- **Root Cause**: In X-Ray Engine C++ (`CActorCondition::UpdateCondition()`), consumable boosters (`boost_time`) count down in **real seconds** (`Device.fTimeDelta`), while `boost_health_restore`, `boost_power_restore`, `boost_radiation_restore`, and `boost_bleeding_restore` are multiplied by `Device.fTimeDelta * level.get_time_factor()`—causing medkits and drugs to only heal **1/6th** of their intended amount at `time_factor = 1.0`.
- **Fix (`rtz_clock.script`)**: Tracks active consumable boosters on `actor_on_item_use` over their exact `boost_time` window and applies the missing `(6.0 - cur_tf) * dt_real` restoration every `100ms` (along with passive C++ `psy_health_v`, `alcohol_v`, and `wound_incarnation_v` recovery).

### 4. Anomaly Camera Shake & Psy Recovery Duration Fix
- **Root Cause**: Demonized's **Dynamic Anomalies Overhaul (DAO) / Arrival** (`drx_da_main.script`) hardcodes `local time_factor = 6` inside its local `get_time_elapsed()` function (`get_game_time():diffSec(get_start_time()) / time_factor`). At `time_factor = 1.0`, `get_time_elapsed()` advances 6x slower than real time, causing the 1-second gravitational anomaly camera shake (`earthquake_40.anm`) to last 6x too long.
- **Fix (`rtz_clock.script`)**: Non-destructively patches the `get_time_elapsed` upvalue in `drx_da_main` and `perk_based_artefacts` with a monotonic real-time clock (advancing `1.0s` per real second and immune to clock sync jumps), clamps any stale `timed_effects` timers, and scales `arszi_psy.get_psy_health_regeneration` so psy recovery runs at vanilla real-time speed.

---

## [1.0.1] - 2026-10-21

### Added
- **Vanilla Time-Scale Preservation (`vanilla_vitals_alife_scale`, enabled by default)**:
  - **Hunger (`db.actor.satiety`)**: Compensates C++ engine `satiety_v` drain for `time_factor = 1.0` so hunger drains at the exact same real-world rate as vanilla Anomaly (`time_factor = 6.0`).
  - **Thirst & Sleep (`actor_status_thirst` & `actor_status_sleep`)**: Dynamically scales `drink_chk` and `sleep_chk` check intervals via Lua upvalues (`300 * (cur_tf / 6.0)` in-game seconds = `50` real seconds per tick) so thirst and sleep deprivation progress at the exact vanilla `6.0x` real-time pace.
  - **A-Life Squad Movement & Stay Timers (`sim_squad_scripted`, `mod_system_rtz_alife.ltx`)**: Scales squad smart-terrain `idle_time` via `squad_on_update` and compensates offline squad `going_speed` / `current_level_going_speed` via DLTX so A-Life squads travel and rotate between smart terrains at vanilla real-world speed.
  - **Smart Terrain Respawns (`smart_terrain` & ZCP `smr_pop`)**: Hooks `on_try_respawn` and `smr_pop.smart_can_respawn` so stalker and mutant respawn cooldowns match vanilla real-world intervals.
  - **Surge & Psi-Storm Pacing (`surge_manager` & `psi_storm_manager`)**: Scales emission and psi-storm `_delta` intervals to match vanilla real-world frequency.
- **Full Rest Duration & Campfire Speed Balance (`rtz_mcm.script`, `rtz_rest.script`)**:
  - Updated **Full Rest Duration** in MCM to **Minutes** with a default of **5 minutes** and a maximum of **10 minutes** (`1–10 min`).
  - Reduced **Campfire Rest Speed** default to **`6 / sec`** (`1–12 / sec` in MCM) and dynamically capped it below sleeping bag and bed recovery rates so campfire resting is always slower than a sleeping bag or bed.

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
