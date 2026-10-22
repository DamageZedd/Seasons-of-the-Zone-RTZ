# Real Time Zone (RTZ) — Addon for Seasons of the Zone

**Real Time Zone (RTZ)** is a standalone, non-destructive gameplay addon for [**Seasons of the Zone**](https://github.com/devinhorowitz/seasonsofthezone) (S.T.A.L.K.E.R. Anomaly / G.A.M.M.A.) that synchronizes the Zone with real life:

1. **1:1 Real-Time Clock & Speed (`time_factor = 1.0`)**:
   - Locks the engine `time_factor` to `1.0` (1 real second = 1 in-game second; vanilla Anomaly is `6.0`).
   - Synchronizes the in-game clock (`hours:minutes`) directly with your computer's OS wall clock (`os.date("*t")`) when loading a save or changing levels.
   - **Strict Vitals & Emission Guard**: Whenever the clock synchronizes or adjusts, Hunger (`satiety`), Thirst (`actor_status_thirst`), Sleep (`actor_status_sleep`), Health, Stamina, Bleeding, and Emission timers are snapshotted and restored to their exact pre-jump values so vitals are left 100% untouched.
   - **Vanilla 6x Vitals & A-Life Pacing + Configurable Hunger & Thirst Mode**: Keeps A-Life squad movement/idle timers, Smart Terrain respawns (Vanilla & ZCP), Emission intervals, and Sleep progressing at vanilla Anomaly speed (`time_factor = 6.0`), while giving you a 3-way **Hunger & Thirst Mode** selector in MCM:
     - **Vanilla Speed (6x)** *(Default)*: Hunger and Thirst drain at vanilla Anomaly real-time speed.
     - **Real-Time Speed (1:1)**: Hunger and Thirst drain 6x slower in real time, matching the 1:1 clock.
     - **Disabled (No Eat / Drink)**: Locks hunger and thirst at 100% full so the protagonist never needs to eat or drink.
   - **1:1 Medkit Healing & Anomaly Camera Shake Fix**: Compensates the X-Ray Engine C++ quirk where consumable boosters (`boost_time`) expire in real seconds while multiplying `boost_health_restore`, `boost_power_restore`, `boost_radiation_restore`, and `boost_bleeding_restore` by `time_factor` (which otherwise caused medkits to only heal 1/6th of their value at `1:1` speed), and patches Demonized's **Dynamic Anomalies Overhaul (DAO) / Arrival**, **Perk-Based Artefacts**, and **Arszi Psy** so gravitational anomaly camera shakes (`earthquake_40.anm`) and psy/alcohol recovery finish at the normal vanilla real-time speed.
2. **Live Real-World Weather (Open-Meteo)**:
   - Drives in-game weather cycles (`clear`, `partly`, `cloudy`, `foggy`, `rain`, `storm`, `snow`) directly from the real-world meteorological observations at your configured *Seasons of the Zone* location instead of random probability, and updates `WeatherManager.day_plan` so *Seasons of the Zone*'s in-game PDA Forecast tab displays your real-world schedule.
   - Works out-of-the-box with both **Atmospherics** and **W.P.W.M. (Weighted Probability Weather Manager)**.
3. **Real-Time Bed & Campfire Resting System**:
   - Replaces multi-hour time-skip sleeping (which would desynchronize the real-time clock) with an atmospheric **Real-Time Rest Screen** (`UIRtzRest`).
   - Using a bed or sleeping bag fades the screen dark with a live clock, comfort bonus indicator (`+30%` for beds, `+15%` for sleeping bags), and fatigue recovery progress bar—restoring full stamina and sleep deprivation over **5 real minutes** (configurable `1–10 mins` in MCM).
   - Press **`SPACE`** or **`ESC`** (or click **Wake Up**) at any time to end your rest early. Automatically wakes you up if attacked or taking damage.
   - **Campfire Passive Rest**: Sitting or idling near any lit campfire passively recharges your fatigue in real time alongside campfire health regeneration.
4. **Full MCM Menu & Localization**:
   - Complete Mod Configuration Menu (`MCM -> Real Time Zone (RTZ)`) with English and Russian (`windows-1251`) translations.

---

## 📦 Installation Instructions

### Requirements
- **S.T.A.L.K.E.R. Anomaly 1.5.2 / 1.5.3** (or **G.A.M.M.A.**)
- [**Seasons of the Zone**](https://github.com/devinhorowitz/seasonsofthezone) (v2.10+)
- **Mod Configuration Menu (MCM)** (optional, recommended for customizing settings)

### Step 1: Install in Mod Organizer 2 (MO2)
1. Download **`Seasons.of.the.Zone.-.Real.Time.Zone.RTZ.v1.0.3.zip`** from the [Releases](../../releases) page.
2. In **Mod Organizer 2**, click **Install a new mod from an archive** and select the downloaded `.zip`.
3. Place **`Seasons of the Zone - Real Time Zone (RTZ)`** anywhere **below** `Seasons of the Zone` in your MO2 left pane (so it loads after *Seasons of the Zone*) and check the box to enable it.

### Step 2: Hour-by-Hour Live Weather (Automatic with Seasons 2.11.0+)
- **Seasons of the Zone v2.11.0+** natively writes an `[hourly]` section mapped to your PC's clock inside `season_weather.ltx`, and `play.bat` already includes the RTZ hook—so hour-by-hour live weather works **100% out of the box** with no extra setup!
- *(Optional fallback for older Seasons versions)*: Right-click **`Seasons of the Zone - Real Time Zone (RTZ)`** in MO2, select **Open in Explorer**, and run **`setup_rtz.bat`** once.

### Step 3: Launch the Game
- Start the game using **`play.bat`** inside your GAMMA / MO2 folder as usual!

---

## ⚙️ MCM Settings (`Real Time Zone (RTZ)`)

| Option | Default | Description |
| :--- | :---: | :--- |
| **Enable Real Time Zone** | `On` | Master toggle for all RTZ systems. |
| **Sync In-Game Clock with Real Time** | `On` | Aligns the in-game clock (`HH:MM`) to your PC's wall clock on load. |
| **Enforce 1:1 Real-Time Speed** | `On` | Locks `time_factor` to the target value (`1.0` default). |
| **Custom Time Factor** | `1.0` | Adjustable from `1.0` (true 1:1 real time) to `10.0` (vanilla is `6.0`). |
| **Safeguard Vitals on Time Jump** | `On` | Strictly preserves exact hunger, thirst, sleep, health, and emission progress across clock sync jumps. |
| **Preserve Vanilla Vitals & A-Life Pacing (6x)** | `On` | Keeps Sleep, A-Life squad movement/respawns, and Emissions running at vanilla `6.0x` real-time speed. |
| **Hunger & Thirst Mode** | `Vanilla (6x)` | Choose between **Vanilla Speed (6x)**, **Real-Time Speed (1:1)**, or **Disabled (No Eat / Drink)**. |
| **Emission & Psi-Storm Frequency** | `Vanilla (2-4h)` | Choose between **Vanilla Scaled (2-4 Hours)**, **6-12 Hours**, **12-24 Hours**, **1-2 Days (24-48h)**, or **2-4 Days (48-96h)** in real time. |
| **1:1 Medkit Healing & Anomaly Shake Fix** | `On` | Fixes medkits/boosters only healing 1/6th at 1:1 time factor and fixes DAO/Arrival anomaly camera shake & psy recovery lasting 6x too long. |
| **Sync Weather with Real Location** | `On` | Drives weather transitions from Open-Meteo for your *Seasons of the Zone* location. |
| **Weather Check Interval** | `5 min` | How often to check for hourly real-world weather transitions (`1–30 min`). |
| **Enable Real-Time Resting** | `On` | Replaces multi-hour sleep time-skips with the real-time rest screen. |
| **Full Rest Duration** | `5 min` | Real minutes required to recover from 100% exhaustion to 0% at a bed (`1–10 min`). |
| **Campfire Passive Rest** | `On` | Passively recovers sleep deprivation while sitting near a lit campfire. |
| **Campfire Rest Speed** | `6 / sec` | Fatigue recovery rate near lit campfires (`1–12 / sec`, always slower than a sleeping bag or bed). |
| **Interrupt Rest on Danger / Damage** | `On` | Instantly wakes the player if taking damage or bleeding. |
| **Autosave Upon Waking** | `On` | Creates a `<name> - rest` save upon completing a rest session. |

---

## 🤝 Credits & License
- **Author**: `Denis_Zedd` (`DamageZedd`)
- **Concept & Design Discussion**: `Denis_Zedd` & `WindWalker`
- **Built for**: [*Seasons of the Zone*](https://github.com/devinhorowitz/seasonsofthezone) by Devin Horowitz (`WindWalker`) — special thanks for the comprehensive `xray-monolith` engine & *Seasons 2.11.0* audit ([Issue #1](../../issues/1))
- **W.P.W.M. (Weighted Probability Weather Manager)**: `UmYeahNo` (`check_day_plan` emission guard & restore architecture)
- **Community Feedback & Testing**: `LittleMorty`
- **Weather Data**: [Open-Meteo](https://open-meteo.com/) (CC BY 4.0)
- **License**: [MIT License](LICENSE)
