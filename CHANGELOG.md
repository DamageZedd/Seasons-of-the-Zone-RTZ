# Changelog

## [1.0.7] - 2026-10-27

### Clock & Weather Follow Your Seasons of the Zone Location
- **Problem**: RTZ set the game clock to your PC's clock, and the hour-by-hour sky was keyed to your PC's hours. With a place in Seasons of the Zone's `configure.bat` in another time zone (say Chornobyl while you play in Canada), the in-game time and the sky were for your PC's time zone, not the place's.
- **Fix**: `_tools\fetch_rtz_hourly.py` now asks Open-Meteo for the place's time zone and writes it (`timezone`, `utc_offset`) to `rtz_weather.ltx` on every `play.bat` launch, with the hourly sky keyed by the place's own hours. RTZ syncs the game clock to the place's local time, reads Seasons' `[hourly]` (keyed by the PC's hours) shifted to the place's hours, and keys the daily `[forecast]` by the place's date. The rest screen's clock shows the place's time too.
- New MCM option **Use Seasons of the Zone Location Time** (on by default). Turn it off to follow your PC's clock. If the place's time zone isn't known yet (before the first launch through `play.bat`), RTZ uses your PC's clock.
- **Changing the place to another time zone** moves the game clock once on the next load: forward to the new time, or, if the new place is up to 4 hours behind, the clock is slowed until it matches.
- **After updating, run `setup_rtz.bat` once more** so `play.bat` uses the new fetcher.

### Medication Dizziness Wears Off at Vanilla Speed
- **Problem**: GAMMA's Yadulin, Akvatab and tetanus shot add alcohol, which the engine shows as the drunk sway, and alcohol wears off per game second. At 1:1 time a Yadulin's sway lasted ~14 real minutes instead of vanilla's ~2.4. RTZ's compensation never ran: it read `db.actor.alcohol`, which this engine doesn't have.
- **Fix**: RTZ now applies the missing decay through the actor's condition (`ChangeAlcohol`), which the engine clamps at zero, so alcohol clears at vanilla's real-time speed (part of **1:1 Medkit Healing & Anomaly Shake Fix** in MCM).

---

## [1.0.6] - 2026-10-27

### Real-Time Emissions (`rtz_clock.script`, new MCM option, on by default)
- **Problem**: Anomaly's surge and psi-storm managers switch the clock to 10x for the whole event (~4.6 real minutes), so every emission left the game clock ~40 minutes ahead of the wall clock and RTZ then had to crawl at 0.1x for ~45 real minutes to catch up.
- **Fix**: The clock now stays at RTZ's factor during emissions and psi-storms. While the surge script updates, its timers see the elapsed time a 10x clock would give, so sirens, rumble, waves, damage and the end land at the same real moments as vanilla, and the emission lasts as long as vanilla's (3m42s with GAMMA's surge manager). Works across save/load mid-emission. Turn off **Real-Time Emissions** in MCM for the vanilla sped-up emission.
- **Smooth emission sky**: the blowout and psi-storm skies are timed for a 10x clock. New `_toolstz_build_fx.py` writes a copy of each (`fx_blowout_day_rtz.ltx` and so on) from whichever mod wins it in your MO2 profile, with its keyframe times divided by 10, and RTZ plays those copies during real-time emissions. The engine blends them exactly as it blends vanilla's, and they fade out on their own after the emission as vanilla's do. `play.bat` rebuilds them on every launch, so they follow your weather mod. Without the copies, RTZ restarts the original effect ahead every 100 ms instead.
- **After updating, run `setup_rtz.bat` once more** so `play.bat`'s RTZ step gets the new sky builder.

### Pre-Emission Crows at Vanilla Pacing
- Pre-emission sounds keyed to game seconds (e.g. Preblowout Murder's crows, 360 game-seconds out) played over 6 real minutes at 1:1. The time-to-emission they see is now scaled, so they play over the last real minute, as in vanilla.

### Hourly Weather Written to the Enabled Copy
- With more than one copy of RTZ in `mods`, the hourly fetcher wrote `rtz_weather.ltx` into the first one alphabetically, even a disabled one. It now writes into the copy your MO2 profile has enabled.

### Readable Logs
- RTZ log lines printed `%d` / `%02d` literally because the engine's `printf` only substitutes `%s`. All RTZ modules now format their messages first.

---

## [1.0.5] - 2026-10-26

Fixes the eleven items reported in Issue #3. (Supersedes the v1.0.4 tag, which was published with files missing; use v1.0.5.)

- **PBA/DAO clock persists across loads**: the monotonic elapsed clock is saved with the game and re-anchored to the larger of the raw and saved values (`rtz_clock.script`, `rtz_main.script`).
- **Next emission uses the configured time factor**: the interval is rolled with the target factor instead of the emission's own factor, so emissions no longer land far too late until a reload.
- **Pre-emission lead scaled**: W.P.W.M.'s `check_pre_blowout` lead is now scaled by the time ratio, so the default 2 game-hour lead is no longer a real-time 2 hours at 1:1.
- **Rest window closes on load/death**: `actor_on_net_destroy` tears down the rest dialog, effects and volume (`rtz_rest.script`).
- **Pause catch-up skipped while hurt**: the clock drift correction no longer runs while bleeding or irradiated.
- **Weather planner no longer freezes**: `check_day_plan` falls back to the original when no real-world cycle is available.
- **Booster/wound/alcohol compensation works**: uses the `bleeding` setter and `ChangeAlcohol` instead of the non-existent `heal_wounds` and `alcohol`.
- **24-hour forecast** looks up each planned hour by its own timestamp.
- **Time-factor sawtooth removed**: GAMMA's surge `main_loop` stored factor is pointed at RTZ's desired factor so it stops resetting to 6 every second.
- **Rest autosave** now runs after the sleep handlers so it includes the rest's healing.
- **`gigant_jumper`** `current_level_going_speed` set to 6 (`mod_system_rtz_alife.ltx`).

---

## [1.0.3] - 2026-10-22

### 1. Fix Lingering Post-Blowout Weather FX & Immediate Clock Realignment (`rtz_clock.script`)
- **Root Cause (Weather lasting 6x too long after blowout)**:
  - In vanilla Anomaly, `CSurgeManager:end_surge()` and `CPsiStormManager:finish()` do not stop the weather effect (`level.stop_weather_fx()` is commented out or gated behind `manual/time_forwarded`). The blowout weather effect (`fx_blowout_day.ltx`) spans 50 in-game minutes. In vanilla Anomaly at 6x speed, the remaining 13 in-game minutes take only ~2 real minutes to dissipate. In RTZ at 1:1 speed (and during ahead-of-wall-clock catch-up holds), those remaining minutes took **13 to 30+ real minutes**, leaving the sky dark, stormy, and red long after the sirens and blowout wave had already finished.
- **Fix**: Wrapped `CSurgeManager.end_surge` and `CPsiStormManager.finish` to immediately call `level.stop_weather_fx()`, trigger `level_weathers:forced_weather_change()` to restore live real-world weather, lock `time_factor` back to `1.0`, and realign the clock with real wall-clock time via `sync_to_real_time(true)` (with vitals safeguarded).

### 2. Complete & Verified Russian Localization (`gamedata/configs/text/rus/ui_mcm_rtz.xml`)
- Fixed character encoding corruption in `ui_mcm_rtz.xml` where newly added MCM strings appeared as question marks (`????`) or fallback English.
- Fully translated and verified all 77 MCM string entries in `windows-1251` (headers, options, descriptions, comfort indicators, rest notifications, and weather cycle names).

### 3. Perk-Based Artefacts (PBA) Monotonic Clock Upvalue Swap (`rtz_clock.script`)
- **Root Cause**: PBA (G.A.M.M.A. Artefacts Reinvention) counts elapsed time as game seconds divided by its `time_factor` local. RTZ previously updated that local to the live time factor, which caused PBA's clock to jump tenfold or more each time `time_factor` changed (e.g. 10 during emissions, 0.1 during catch-up). Because the Lucifer artefact degrades by `rate * time_factor * (time_elapsed - saved_time_elapsed)`, a single jump cost Lucifer most or all of its condition, while cooldowns and timed effects set during catch-up landed 10x further out and stuck.
- **Fix**: Replaced mutating PBA's `time_factor` upvalue with the monotonic real-time clock `rtz_pba_get_time_elapsed` (swapping `get_time_elapsed` in `perk_based_artefacts.actor_on_update`). Time elapsed now advances strictly 1.0s per real second and is immune to time factor changes (Issue #2).

### 4. Seasons 2.11.0 `[hourly]` 24-Hour Freshness Check (`rtz_weather.script`)
- Added `hourly_fresh(ini)` verifying that `season_weather.ltx`'s `[hourly]` section is within 24 hours of its `start` timestamp. If the hourly data is older than 24 hours (e.g. launching from MO2 without `play.bat` or during offline play), RTZ cleanly falls back to the date-keyed daily `[forecast]` instead of displaying yesterday's sky for the current hour (Issue #2).

### 5. Offline A-Life Speed Overrides for 7 Standalone Creature Sections (`mod_system_rtz_alife.ltx`)
- Applied 6x DLTX overrides to `m_rat_e`, `m_tushkano_e`, `m_borya_e` (`18.0`), `rotan` (`15.0`), `gigant_jumper` (`12.0`), `m_bibliotekar_e` (`51.0`), and `poltergeist_build` (`27.0`), which define their own `going_speed` and did not inherit the `[monster_base]` override, ensuring their offline squads travel at full vanilla real-world speed (Issue #2).

### 6. Early Emission Radio Warnings Compatibility (e.g., EnVy's Radio Warning)
- Documented and verified early radio emission warning behavior: mods such as **EnVy's Emission Radio Warning** trigger advance announcements 5-8 in-game minutes ahead of an emission. At vanilla 6x speed, this is 50-80 real seconds, whereas at RTZ's 1:1 real-time flow, the arrival window spans a full **5 to 8 real minutes**.
- Maintained all engine and manager safeguards introduced in `rtz_clock.script` so the 5-8 minute advance window is never prematurely cancelled by `time_forwarded`, drift checks, or `diff_sec > surge_time` skips.

---

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

### 5. Emission Radio Announcement False-Alarm Fix & Custom Real-Time Frequency MCM Selector (`emission_frequency_mode`)
- **Root Cause ("Emission incoming" radio announcement with no emission)**:
  1. On save load (`load_state` -> `initialize()`), `CSurgeManager` and `CPsiStormManager` initialized `self.inited_time` to the pre-sync save timestamp. When RTZ synced the clock forward on `actor_on_first_update`, `last_surge_time` was shifted forward, but `inited_time` remained at the old pre-sync time. On `CSurgeManager:update()`'s `first_update`, `diff_sec = game.get_game_time():diffSec(self.inited_time) / level.get_time_factor()` exceeded `self.surge_time` (`222`s) even when `started == false`, triggering `self:skip_surge()` which overwrote `last_surge_time` back to the old pre-sync `inited_time + 222`—causing radio announcement mods ("Emission Announcements via Radio") and pre-blowout crows to fire immediately and then get silently cancelled by `start()`'s `diff_sec + 6 > self.surge_time` check or `time_forwarded` (`diff < 3600` pushing `_delta` back by 3 hours).
- **Fix (`rtz_clock.script`)**:
  - Aligns `inited_time` to `game.get_game_time()` and clears `time_forwarded = false` whenever `not started`, wraps `CSurgeManager.start` and `CPsiStormManager.start` so naturally triggered emissions at `1:1` time factor start cleanly at `diff_sec = 0` without falsely skipping, and sanitizes any pre-existing corrupted `last_surge_time` on load.
- **New MCM Setting — Emission & Psi-Storm Frequency (`emission_frequency_mode` in `rtz_mcm.script` & `ui_mcm_rtz.xml`)**:
  - **`Vanilla Scaled (2-4 Hours)`** *(Default)*: Scales Anomaly's emission frequency setting to real time.
  - **`6-12 Hours (Real Time)`**: Rolls emissions and psi-storms every 6 to 12 real hours.
  - **`12-24 Hours (Real Time)`**: Rolls emissions and psi-storms every 12 to 24 real hours.
  - **`1-2 Days (24-48 Hours)`**: Rolls emissions and psi-storms every 1 to 2 real days.
  - **`2-4 Days (48-96 Hours)`**: Rolls emissions and psi-storms every 2 to 4 real days.

### 6. *Seasons of the Zone 2.11.0* Integration & `xray-monolith` Engine Fixes (Issue #1 by `@devinhorowitz` / `WindWalker`)
- **Removed Shipped `rtz_weather.ltx` & Prioritized Seasons 2.11.0 `[hourly]` (`rtz_weather.script`)**:
  - Removed the static sample `gamedata/configs/rtz_weather.ltx` from the repository and release package so weather is never stuck on a static sample out of the box.
  - `get_real_cycle()` now reads *Seasons of the Zone 2.11.0+*'s `[hourly]` section in `season_weather.ltx` first (which maps the next 24 hours to the PC's wall clock), respects `sotz_api.weather_hold()` on remembrance days/anniversaries, and verifies `date == today` if an optional `rtz_weather.ltx` is present.
- **Mapped `_tools/fetch_rtz_hourly.py` to PC Wall-Clock Hours**:
  - Updated `_tools/fetch_rtz_hourly.py` to fetch UTC timestamps and map the next 24 hours to the PC's local wall-clock hours (`0..23`) so remote locations (e.g. Chornobyl while playing in US Eastern) match the weather happening at that exact moment.
- **Ahead-of-Wall-Clock Catch-Up Hold (`rtz_clock.script`)**:
  - When the in-game clock gets ahead of the PC's wall clock by up to 4 hours (e.g. after an emission running at `time_factor = 10` or Fair Fast Travel), `sync_to_real_time` no longer wraps around and jumps `+23` hours forward; instead, `enforce_time_factor` slows the game clock to `0.1x` until the wall clock catches up.
- **Fixed `db.actor.bleeding` Setter Healing Wounds on Sync (`rtz_clock.script`)**:
  - Removed `db.actor.bleeding = snap.bleeding` from `restore_vitals_exact()` (`script_game_object_script2.cpp` binds `.property("bleeding", GetBleeding, ChangeBleeding)` where `ChangeBleeding` shrinks wounds rather than assigning).
- **Protected Active Emissions & Psi-Storms from Clock Sync (`rtz_clock.script`)**:
  - `sync_to_real_time()` and the periodic drift check now skip syncing while `level.is_wfx_playing()`, `surge_manager.is_started()`, or `psi_storm_manager.is_started()` is true, and `restore_vitals_exact()` no longer forces `started = false` / `finished = true` directly on either manager.
- **Once-Per-Roll Emission & Psi-Storm `_delta` Scaling (`rtz_clock.script`)**:
  - Replaced per-second `_delta` rescaling with wrappers around `CSurgeManager.new_surge_time` and `CPsiStormManager.new_psi_storm_time` that preserve their 1-hour mutual spacing check in unscaled vanilla seconds and scale `_delta` once per roll.
- **Offline Squad `going_speed` on Creature Sections (`mod_system_rtz_alife.ltx`)**:
  - Applied 6x `going_speed` and `current_level_going_speed` DLTX overrides directly to `[stalker]`, `[monster_base]`, and stock monster sections (`alife_online_offline_group.cpp` copies `m_fGoingSpeed` from squad members' creature sections rather than `[online_offline_group]`).
- **GAMMA `UISleep:TestAndShow` Rules, `actor_on_sleep(equiv_hours)`, & Forced Blackout Lock (`rtz_rest.script`)**:
  - `start_resting` now enforces GAMMA's `5000` sleep threshold, bleeding/radiation checks, and safe cover / tent shelter checks (`GetEvent("current_safe_cover")` or `item_tent.get_nearby_tent(1.5)`).
  - `stop_resting` computes the equivalent hours rested (`math.floor((recovered / 8000) * 8 + 0.5)`) and passes them to `actor_on_sleep(equiv_hours)` while guarding `forced_weather_change`, `time_forwarded`, hunger, thirst, and fatigue—allowing Body Health System limb healing and `arszi_psy` regeneration to scale properly with rest.
  - Exhaustion blackouts (`sleep_forced`) now enforce a 30-second unskippable penalty window before wake controls unlock.
- **Restored `snd_volume_music` on `actor_on_net_destroy` and Quit (`rtz_rest.script`)**:
  - Registered `actor_on_net_destroy`, `on_before_level_changing`, and `main_menu.OnButton_quit_clicked` hooks to restore `snd_volume_music` and `snd_volume_eff` so quitting mid-rest never saves `0` into `user.ltx`.
- **Added MIT `LICENSE`**:
  - Added the MIT `LICENSE` file to the repository root.

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
