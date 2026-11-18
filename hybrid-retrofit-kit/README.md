# Bolt-On Strong-Hybrid Retrofit Kit for Manual Cars: Design Study and Startup Plan

**Working name:** *e-Beam Hybrid Kit*
**Target vehicles:** front-wheel-drive manual cars around 1,500 kg and about 100 bhp (petrol or diesel), with Indian city use as the main design case
**Kit concept:** about 5 kWh of 48 V LFP battery plus a rear-axle motor rated about 10 kW continuous and 18 kW peak, with an electric AC compressor
**Cost target:** hardware under ₹2 lakh, retail around ₹3 lakh installed

> Method: (1) review how production strong hybrids work, (2) size the kit from first principles like a powertrain engineer, backed by the energy model in [`sim/kit_sim.py`](sim/kit_sim.py), (3) pick the design apart like a workshop mechanic who has to fit it, (4) revise the design, then (5) turn it into a startup plan.
>
> Production-car specifications below are recalled from public material and rounded. They are good enough for concept work. **Check every figure against current OEM data before using it in a pitch or a homologation file.** Kit numbers are model estimates, not test results.

---

## 0. Summary

| Question | Answer |
|---|---|
| Best architecture for a retrofit? | **Approach 1, "through-the-road" (P4), done as a bolt-in replacement rear axle module ("e-Beam")** with a 48 V system. The car's own engine, clutch and gearbox stay untouched. |
| Is the e-CVT swap (Approach 2) viable? | **Not as a retrofit.** It needs control of the engine ECU, a high-voltage (200–650 V) system, a different gearbox for every engine and bell-housing combination, and re-certification of emissions. Under ₹2 lakh it cannot be done. It is an OEM or Tier-1 licensing business, not a kit. |
| How does it "drive like an automatic"? | **Clutch-free EV mode from 0 to about 40 km/h** with the lever in **neutral**: engine off, accelerator drives the rear motor, with creep, hill-hold and regen. Above that speed (or when the battery is low) the driver is prompted to select a gear and drives a normal manual, now with boost, regen and smoother shifts because the rear motor fills the torque gap during gear changes (the Renault E-Tech idea, applied through the road). A later add-on (an iMT-style clutch actuator) removes the clutch pedal completely. |
| City fuel economy gain (model) | **+28% (MIDC urban) to +42% (heavy stop-go)** with AC on and no plug-in charging. **+47% to +77% with AC off.** On a plug-in day in heavy traffic, fuel use falls by about **55%**, plus about 4.4 kWh of grid energy. |
| Highway | Overtaking 60–100 km/h in 4th: **17.3 s → 10.6 s** (about 39% quicker). Fuel economy change is about 0% when charge-sustaining and **about 19% better when leftover plug-in energy is spent** on the highway. |
| Why 48 V? | It stays below the 60 V DC "high-voltage" threshold, so installers need no HV training, cables need no orange HV insulation or isolation monitoring, and the parts come from India's very large 48 V e-3W/e-2W supply chain. This one decision does more for the cost target than any other. |
| AC | **Required.** Replace the belt-driven compressor with a 48 V electric scroll compressor in the same mounting position, reusing the existing hoses through adapters. Without it, EV mode is unusable in an Indian summer. |
| Cost | Hardware cost about **₹1.9 lakh at 10k units a year** (about ₹2.3 lakh at pilot volume). MRP about **₹3.25 lakh including GST, installed**. A roadmap brings cost to about ₹1.6 lakh. |
| Weak spot | **Customer payback is about 3–5.5 years** for typical commuters. The case is strongest for heavy city users and for people who want an automatic without selling their car. The pitch has to sell convenience plus savings, with financing; savings alone will not carry it. |
| Biggest technical risks | (1) Stopping and restarting the engine **without touching the emission-certified ECU** (use the OEM start-stop function where it exists). (2) Fitting the rear package around the fuel tank, spare well and exhaust. (3) Rear-only regen and stability. (4) Getting AIS-123 type approval for each model. |

---

# PART A: How production strong hybrids work

## A1. Taxonomy

**Power-flow types**

| Type | Engine drives wheels? | Examples | Notes |
|---|---|---|---|
| Series | Never, the engine only generates | Nissan e-POWER, BMW i3 REx | Simple; double energy conversion hurts at highway speed |
| Parallel | Yes, through a gearbox | Hyundai/Kia HEV (P2 with 6AT), Mercedes 48 V, Maruti SHVS (mild) | Needs a clutch or gearbox; efficient at cruise |
| Series-parallel (power split) | Partly mechanical, partly electrical, continuously | Toyota THS / e-CVT, Ford, Lexus | Most refined; needs 2 motors plus a planetary gearset |
| Series-parallel (switched) | Series at low speed, direct drive at cruise | Honda e:HEV / i-MMD, BYD DM-i, Renault E-Tech | The industry is converging here |
| Through-the-road (TTR) | Engine drives one axle, a motor drives the other; the road couples them | Peugeot 3008 HYbrid4, Volvo V60 D6/T8, BMW 225xe, Toyota E-Four (rear unit) | **The only type you can add without opening the powertrain** |

**Motor position (P-codes)**

```
         P0                 P1         P2          P3            P4
  [belt on engine]--[ENGINE]--[crank]--[clutch]--[GEARBOX]--[diff out]   [other axle]
  BSG / ISG                 ISG        between     on gearbox    separate e-axle
  (Maruti SHVS,             (Honda     engine &    output        (rear motor on a
   48V BSG)                  IMA)      gearbox                    FWD car)
```

For a retrofit, **P0 (belt) and P4 (other axle) are the only positions you can reach without changing the engine-to-gearbox stack.** P1, P2 and P3 all need the bell housing or gearbox redesigned.

---

## A2. Toyota THS-II "e-CVT" (power-split device)

### Hardware
```
                 ENGINE (Atkinson cycle, ~40% peak BTE)
                    |
                [carrier]  (planet carrier)
             /     |      \
        [sun]---planets---[ring]------> counter gear -> final drive -> wheels
          |                  |
        MG1                 MG2 (via reduction gear: planetary in Gen 3, parallel axis in Gen 4)
   (generator/starter,   (traction motor,
    sets engine speed)    regen, reverse)
          \_____ inverter / boost converter (~200 V battery -> up to ~650 V) _____/
                              |
                        HV battery ~0.7–1.3 kWh (NiMH or Li-ion)
```
* No clutch, no torque converter, no gear-change steps. "CVT" refers to the electrically controlled speed ratio; there are no belts.
* **Reverse:** MG2 runs backward. There is no reverse gear.
* **Engine start:** MG1 spins the engine through the planetary set. There is no 12 V starter.
* **AC:** a **high-voltage electric compressor**, so the cabin stays cool with the engine off. Every Toyota hybrid does this, and it is why our kit needs an e-compressor too.

### The equation that makes it work (Willis equation for a simple planetary)
With sun teeth Zs, ring teeth Zr (Prius Gen 2/3: Zs = 30, Zr = 78):

```
(Zs + Zr)·ω_carrier = Zs·ω_sun + Zr·ω_ring
=>  ω_MG1 = ω_sun = 3.6·ω_engine − 2.6·ω_ring
Torque split (steady state):  T_ring = 0.722·T_engine (mechanical path to wheels)
                              T_sun  = 0.278·T_engine (reacted by MG1)
```
**Worked example:** 60 km/h, ring at about 1,733 rpm (ring-to-wheel ratio about 3.27, wheel radius 0.30 m). The engine runs at 1,800 rpm and 70 Nm (13.2 kW).
* MG1 speed = 3.6×1800 − 2.6×1733 ≈ **1,974 rpm**, with MG1 torque 0.278×70 ≈ 19.5 Nm, so MG1 **generates about 4.0 kW**.
* The ring receives 0.722×70 ≈ 50.5 Nm at 1,733 rpm, about **9.2 kW mechanical**.
* The 4.0 kW of electricity goes to MG2 (or to the battery). About 30% of engine power takes the electrical path at this operating point.
* By changing MG1 speed, the controller **chooses engine speed independently of road speed**. That lets the engine stay on its best-efficiency line (high-load, low-rpm, Atkinson operation).

### Operating modes
| Mode | Engine | MG1 | MG2 |
|---|---|---|---|
| EV launch / crawl | off (carrier stationary) | freewheels backward | drives |
| Engine start | cranked by MG1 | motor | holds traction |
| Power split cruise | on, at its efficient point | generator (controls rpm) | motor |
| Hard acceleration | high load | generator | motor plus battery power |
| Regen braking | off | - | generator |
| High-speed cruise | on | may motor (negative split, power circulation, which costs efficiency) | may generate |

### Indian-market reference (public specs, check before use)
* **Toyota Urban Cruiser Hyryder / Maruti Grand Vitara strong hybrid:** 1.5 L 3-cylinder Atkinson engine (M15D-FXE) about 92 PS / 122 Nm, motor about 80 PS / 141 Nm, about 116 PS system output, Li-ion battery around 177 V, claimed about 28 km/l.
* **Innova Hycross:** 2.0 L hybrid on the same principle.

### Strengths and weaknesses
* ✔ Smoothest drive, best city economy, no clutch wear, few moving parts.
* ✘ Needs two motors, HV power electronics, an engine designed for it (Atkinson cycle, no belt accessories), and full engine-ECU integration. **None of this is possible as a bolt-on.**

---

## A3. Renault E-Tech "multi-mode dog-clutch" hybrid (Clio, Captur, Arkana, Dacia Jogger/Duster Hybrid 140, newer 1.8 E-Tech 155/160)

### Hardware (E-Tech 140/145, public figures)
* 1.6 L naturally aspirated 4-cylinder, about 90–94 PS / about 148 Nm.
* **Main e-motor** about 36 kW (49 PS), about 205 Nm.
* **HSG (high-voltage starter-generator)** about 15 kW (20 PS), about 50 Nm, on the engine side.
* Battery about 1.2 kWh, about 230 V Li-ion (the newer 1.8 version uses about 1.4 kWh).
* **Multi-mode gearbox with no clutch and no synchronizers:** dog clutches only. **4 ratios for the engine and 2 for the e-motor**, which Renault says gives roughly 14–15 combinations (counting neutral).

```
   ENGINE --(4 ratios via dog clutches)--\
                                           >==== output shaft ==== diff ==== wheels
   E-MOTOR --(2 ratios via dog clutch)---/
   HSG ---- engine side: starts the engine, synchronizes dog engagement, generates (series mode)
```

### How it works
1. **The car always moves off electrically.** There is no launch clutch at all.
2. **Engine gear engagement:** the HSG spins the engine to exactly the speed the target gear requires, so dog teeth and slots match, and a fork pushes the dog clutch in. Synchronizer cones are not needed because **the e-machines synchronize electronically**.
3. **Torque fill:** while the engine path is in neutral during a ratio change, the **main e-motor keeps driving the wheels**, so the driver feels no interruption. When the e-motor path changes ratio, the engine carries the load.
4. **Series mode:** the engine is disconnected from the wheels and drives the HSG as a generator while the main motor propels the car (low-speed city driving).
5. **Parallel mode:** engine plus e-motor both drive (overtaking), or the engine alone drives at cruise.
6. Origin story: the first prototype is said to have been built from Lego Technic. Around 150 patents surround the system.

### Lessons for us
* **Dog clutches plus electronic synchronization are cheap, compact and efficient.** We use the same idea for the rear motor's **disconnect clutch** (spin the motor up to wheel speed, then engage the dog, so no synchronizer is needed).
* **Electric torque fill during engine shifts is what makes a stepped-gear hybrid feel seamless.** In our kit, the rear motor fills the gap when the driver presses the clutch.

---

## A4. Honda e:HEV (i-MMD) and Nissan e-POWER (series-dominant)
* **Honda City e:HEV (India):** 1.5 L Atkinson engine about 98 PS, traction motor about 109 PS / 253 Nm, plus a generator motor. **Series mode** at low and medium speed. **One lock-up clutch** connects the engine directly to the wheels at a fixed ratio for highway cruise. Claimed about 27 km/l.
* **Nissan e-POWER:** pure series. The engine never drives the wheels and runs at a few efficient points.
* **BYD DM-i** and many Chinese DHTs follow the Honda pattern (series plus 1–2 direct gears) with larger batteries.
* **Lesson:** in the city, the winning recipe is to **keep the engine off, or at an efficient load, and let an electric motor do the stop-and-go driving.** Our EV mode in neutral does exactly that. When the battery is low, the engine charges it "through the road" at better efficiency than first-gear crawling.

---

## A5. Engine-front, motor-rear (through-the-road) hybrids
| Car | Front | Rear | Battery | Notes |
|---|---|---|---|---|
| Peugeot 3008 / 508 RXH HYbrid4 (2011) | 2.0 HDi diesel about 163 PS + **6-speed automated manual** + reinforced stop-start starter-alternator | about 27 kW e-motor | about 1.1 kWh NiMH, about 200 V | **Closest production precedent for our kit.** The rear motor fills the shift gaps of the robotized manual, gives EV crawl and electric AWD. |
| Volvo V60 D6 PHEV (2012) | 2.4 D5 diesel | about 50 kW ERAD | about 11 kWh | Plug-in TTR |
| Volvo T8 Twin Engine | 2.0 turbo+supercharged + crank ISG | about 65 kW ERAD | about 10–18 kWh | P1 + P4 |
| BMW 225xe Active Tourer | 1.5 T 3-cylinder FWD | about 65 kW rear motor | about 7.6 kWh | FWD car with rear e-axle |
| Toyota E-Four (RAV4/NX hybrid) | THS e-CVT | about 40–50 kW rear MGR | shared | No propeller shaft; rear motor for traction and stability |
| Mitsubishi Outlander PHEV | Front motor + engine with clutch | Rear motor | 12–20 kWh | Twin-motor series/parallel |

**Problems these OEMs had to solve (and so will we):**
1. **Two drivelines that know nothing about each other.** You need a supervisory controller that coordinates torque.
2. **Regen on one axle only.** The brake balance shifts, and rear-axle regen can destabilize the car (lift-off oversteer) at the limit, so regen must be limited and coordinated with ABS/ESC.
3. **Charging while driving.** The engine drives the front wheels harder while the rear motor generates, so energy passes through the tyres and road (lossy, but workable).
4. **Charging at standstill is impossible without a generator on the engine.** PSA added a starter-alternator for this reason. We handle it with plug-in charging, sizing the battery reserve, and a 12 V → 48 V trickle path as a fallback (see E2).

## A6. Mild hybrids and "clutchless manuals" (relevant building blocks)
* **Maruti SHVS / Smart Hybrid:** 12 V ISG (integrated starter generator, belt-driven) plus a second battery, idle start-stop, mild assist and regen. **Many K15 cars already have OEM start-stop (ISS) in the engine ECU**, which matters for our engine-off strategy (see D/E).
* **48 V BSG (belt starter generator, e.g. Hyundai/Kia, Mercedes EQ Boost):** about 10–15 kW at the crank, quick quiet restarts, about 8–15% city benefit.
* **Hyundai/Kia iMT:** a manual gearbox with **clutch-by-wire** (intention sensor on the gear lever plus hydraulic actuator, no clutch pedal). It shows that Indian buyers accept a two-pedal manual, and it is the model for our Phase-3 add-on.

## A7. Retrofit precedents and what they teach
| Attempt | What it was | What happened / lesson |
|---|---|---|
| **KPIT Revolo** (India, around 2010) | Plug-in parallel hybrid retrofit kit, motor coupled to the driveline, claims of very large fuel savings | Widely publicized, never reached scale. **Lessons:** homologation per model, installer quality, battery cost (pre-LFP era), and over-promised savings. KPIT pivoted to OEM software. *(Details from press coverage at the time; verify.)* |
| **Altigreen** (India, around 2013–15) | Hybrid retrofit kit | Pivoted to electric three-wheelers. Retrofit car volumes were too small to fund per-model engineering. |
| **XL Fleet** (USA) | Bolt-on hybrid for fleet trucks (motor on the propeller shaft) | Fleet B2B worked better than retail. Modest real savings, about 10–20%. |
| **HySolarKit / eProInn** (Italy) | Rear **in-wheel** motors + battery + solar film for FWD cars | Shows that "convert FWD to through-the-road hybrid" is a recognized concept. In-wheel motors add unsprung mass and complicate brakes and sealing. |
| **ZF eTB "electric twist beam"** (concept around 2012) | Twist-beam rear axle with integrated e-motors | **Direct inspiration for our e-Beam module:** a rear axle with drive built in, bolted to the original hard points. |
| **CNG retrofit industry (India)** | Model-specific kits, type approval, authorized fitment centres, RC endorsement | **The business template:** per-model kits plus certified installers plus RTO endorsement already works at scale in India. |

## A8. What we borrow
| From | Idea used in the kit |
|---|---|
| Toyota THS | Electric AC compressor; EV crawl with the engine off; keep the engine on its efficient line or off |
| Renault E-Tech | Dog-clutch disconnect synchronized by the motor; **torque fill during shifts** |
| Honda/Nissan | City = electric traction; engine as energy source only when needed |
| Peugeot HYbrid4 | P4 rear axle on a front-engine car with stepped gears; rear motor masks shift gaps |
| ZF eTB | Rear axle module that bolts to existing hard points |
| Hyundai iMT | Clutch-by-wire add-on for a true two-pedal experience |
| CNG kit industry | Per-model approval, installer network, RC endorsement, financing |

---

# PART B: Engineer's pass, first-principles sizing

## B1. Requirements
| # | Requirement | Target |
|---|---|---|
| R1 | Vehicle | FWD manual, about 1,500 kg test mass, about 75 kW (100 bhp) petrol or diesel |
| R2 | City "automatic" behaviour | Clutch-free driving from 0 to 40 km/h, creep, hill-hold, smooth |
| R3 | City economy | ≥ +25% charge-sustaining, ≥ +50% on plug-in days |
| R4 | Highway | Noticeable overtaking boost; no economy penalty |
| R5 | Reversibility | Car can be returned to stock in under one working day |
| R6 | Kit cost | < ₹2 lakh hardware; ≈ ₹3 lakh retail installed |
| R7 | Safety | If the kit fails, the car becomes a normal manual car |
| R8 | Climate | 45 °C ambient, monsoon water wading about 300 mm, dust, Indian road shocks |

## B2. Road load (from `sim/kit_sim.py`, CdA 0.72 m², Crr 0.011, 1,500 kg)
| Speed | Road load force | Power at the wheel |
|---|---|---|
| 20 km/h | 175 N | 1.0 kW |
| 40 km/h | 214 N | 2.4 kW |
| 60 km/h | 280 N | 4.7 kW |
| 80 km/h | 372 N | 8.3 kW |
| 100 km/h | 490 N | 13.6 kW |
| 120 km/h | 634 N | 21.1 kW |

**Reading:** steady city cruising takes only 1–3 kW. A **10 kW continuous** motor can cruise electrically to about 80 km/h on the flat. What a 10 kW motor **cannot** deliver is brisk acceleration: that depends on **peak torque**, which is cheap to add at 48 V because it means more phase current at low speed, not more battery power.

## B3. Motor and gearing
Chosen: **48 V IPMSM (interior permanent-magnet synchronous motor), 10 kW continuous / 18 kW peak (30 s), 70 Nm peak, 8,000 rpm max, single 8.5:1 reduction with open differential, dog-clutch disconnect above about 100 km/h.**

| Check | Result |
|---|---|
| Wheel force at launch | 70 × 8.5 × 0.96 / 0.305 ≈ **1,870 N (571 Nm at the axle)** |
| EV launch acceleration (1,605 kg with kit) | **≈ 1.0 m/s²**, similar to a gentle AT launch in traffic |
| EV 0–40 km/h at full pedal | **≈ 11.5 s.** Adequate for jams; heavier pedal prompts engine engagement |
| EV standing-start gradeability | **≈ 11%.** Covers flyovers and most ramps; steep basement ramps (>11%) need the engine |
| Rear traction limit (μ 0.7, 42% rear load) | ≈ 4,600 N, so the motor will not spin the tyres on dry roads; wet and gravel need slip control |
| Motor speed at 100 km/h | 7,390 rpm (inside the 8,000 limit) → **disconnect at 100 km/h**, which also removes magnet drag losses at cruise and the risk of high back-EMF at overspeed |

Why not use a bigger motor? Battery current at 48 V (18 kW ≈ 375 A) is already the practical ceiling for low-cost cables, contactors and LFP cells. More power means moving to 96 V or more, which crosses into "high voltage" and costs more in safety and certification than it returns.

## B4. Battery: voltage and size
**Voltage: 48 V class (16S LFP, 51.2 V nominal, 58.4 V max, so < 60 V DC).**
* Under AIS-038 / ECE R100 style rules, most HV construction requirements (orange cables, IP2X touch protection, isolation monitoring, HV-trained technicians) apply **above 60 V DC**. Staying below this is what makes a neighbourhood installer network practical.
* Components (motors, inverters, BMS, DC-DC converters, chargers) come from India's very large **48–51.2 V e-3W/e-2W ecosystem**.

**Size: 5.12 kWh (16S, 100 Ah, high-rate LFP rated ≥ 3C continuous and ≥ 5C for 30 s).**
* Charge-sustaining operation needs only about 1.5–2 kWh. The 5 kWh size **only pays off with plug-in charging**, so the kit is positioned as a **"plug-in city hybrid"** that charges from a 15 A home socket (2 kW onboard charger, 0–100% in about 2.5–3 h).
* Usable 15–95% SoC is about 4.1 kWh. In heavy traffic with AC on, the model uses **about 136 Wh/km** (AC alone is about 90 Wh/km at 11 km/h average), so roughly **20 km of engine-off city driving per charge** (EV-dominant, with engine help on surges), more with AC off.
* A modular design (2 × 2.56 kWh bricks) allows a cheaper **2.5 kWh "Lite" SKU** for owners who will never plug in. A single brick limits peak power to about 10 kW.
* **LFP, not NMC:** the battery sits in the boot or spare well of a car parked in 45 °C sun, with a fuel tank nearby. LFP's thermal stability matters more than its weight penalty.

## B5. Energy model results (`python3 sim/kit_sim.py`, full output in [`sim/results.txt`](sim/results.txt))
Model: backward-facing, 1 Hz time step. Engine modelled with a Willans line (η_ind 0.37 plus an rpm-dependent friction/pumping term), a typical Indian driver's early-upshift gear choice, AC load, 12 V loads, rear-only regen limited to 0.12 g, prompted EV↔engine hand-over with a minimum engine-on time, and a restart fuel penalty. **The stock model is somewhat pessimistic** compared with ARAI figures (stock MIDC urban without AC = 12.3 km/l), so read the **percentage gains** rather than the absolute km/l.

| Cycle (AC ON, petrol) | Avg speed | Stock | Kit, charge-sustaining | Gain |
|---|---|---|---|---|
| MIDC urban (4×ECE-15) | 18 km/h | 9.9 km/l | 12.7 km/l | **+28%** |
| Indian heavy traffic (synthetic, about 35% idle) | 11 km/h | 6.9 km/l | 9.8 km/l | **+42%** |
| Highway 70–105 km/h | 82 km/h | 16.0 km/l | 16.1 km/l | ±0% |
| *AC OFF: MIDC urban* | | 12.3 | 18.2 | **+47%** |
| *AC OFF: heavy traffic* | | 9.1 | 16.1 | **+77%** |

| Plug-in day (heavy traffic, 32 km, starting at 95% SoC) | Stock | Kit |
|---|---|---|
| Fuel | 4.76 L | **2.12 L (−55%)** |
| Grid energy | - | 4.4 kWh (≈ ₹35–40) |
| Battery reaches 15% after | - | about 21 km |

| Highway with leftover plug-in energy (60→25% SoC) | 3.42 L → 2.76 L (**−19%**) |
|---|---|

**Where the savings come from (heavy traffic, roughly in order):**
1. **No idling.** The stock engine burns about 0.9–1.0 L/h at idle with AC; the kit engine is off and AC runs from the battery.
2. **No first- and second-gear crawling** at 8–12% engine efficiency; the motor does this at about 85%.
3. **Regen** from the rear axle (limited to 0.12 g for stability).
4. **Load-point shifting:** when the engine does run, generating through the rear axle moves it into a better BSFC region (marginal efficiency about 33%).
5. **Mechanical AC load removed** from the engine belt (a variable-speed e-compressor is also more efficient).

**Why the highway gain is small:** at a steady 80–100 km/h the engine already runs efficiently, and through-the-road charging costs about 30% round trip. Highway benefits are **performance** (boost) plus the option of **spending grid energy**.

## B6. Highway boost
| Overtake (full load) | Stock | Kit + boost | Improvement |
|---|---|---|---|
| 40–80 km/h, 4th gear | 17.2 s | 9.1 s | 47% quicker |
| 60–100 km/h, 4th gear | 17.3 s | 10.6 s | 39% quicker |
| 60–100 km/h, 5th gear | 27.0 s | 13.3 s | about 2× quicker |

An 18 kW, 10 s boost uses only about 50 Wh, so it is nearly always available. Roughly, a 100 bhp car feels like a 125 bhp car during overtakes (a 75 kW engine plus about 17 kW at the wheels).

---

# PART C: Comparing the architectures

| Criterion (1 = poor, 5 = good) | **A1: P4 rear (body-mounted e-axle)** | **A1b: P4 "e-Beam" module (recommended)** | A1c: P4 in-wheel motors | **A2: e-CVT swap** | P0 48 V BSG only | P0 + P4 (Pro) |
|---|---|---|---|---|---|---|
| Fitment invasiveness | 2 (cut spare well, new hubs) | **4** (swap the axle at existing hard points) | 4 | 1 | 5 | 3 |
| Reversible to stock | 3 | **5** | 4 | 1 | 5 | 4 |
| Calibration difficulty | 3 | 3 | 2 (two motors, wheel-level slip control) | 2 (needs engine ECU) | 4 | 2 |
| Cost under ₹2 lakh | 4 | **4** | 3 | 1 | 5 | 2 |
| City economy gain | 4 | 4 | 4 | 5 | 2 | 5 |
| "Automatic" feel | 4 (EV in neutral) | 4 | 4 | 5 | 1 | 4 |
| Regulatory effort | 3 | 3 | 2 (wheel/track changes) | 1 (emissions re-certification) | 4 | 2 |
| Scalable across models | 3 | **4** (one module per platform family) | 4 | 1 | 4 | 3 |
| Ride / unsprung mass | 5 | 3 | **1** | 5 | 5 | 3 |
| **Total** | 31 | **34** | 28 | 22 | 35 (but fails R2/R3) | 28 |

**Why the e-CVT swap fails as a retrofit** (even though it sounds easier to calibrate):
1. **The engine ECU has to take torque and speed commands.** OEM BS-VI ECUs are locked. A standalone or reflashed ECU means **emissions and OBD re-certification for every engine variant**, a cost of crores and many months each.
2. **Mechanical variety:** every engine family (Maruti K-series, Hyundai Kappa/Gamma, Honda L/E, Tata Revotron, Mahindra mFalcon, Renault HR, diesels) has a different bell-housing pattern, starter position, mounts, driveshaft splines and differential offset. That means one transaxle design per engine.
3. **Power needs:** for a 75 kW engine, MG1 must be about 25–30 kW and MG2 about 40–50 kW, which requires **HV (200–650 V)** and an HV-certified installation.
4. **Cost:** the transaxle, two motors, power control unit and HV battery cost well above ₹2.5 lakh in materials even at volume, before custom tooling.
5. **The efficiency case is weak** without an Atkinson-cycle engine designed for it.
→ Treat it as a separate **B2B licensing opportunity** (a dedicated hybrid transmission for Indian OEMs). It is a different company.

**Why P0 BSG alone is not enough:** it cannot drive the car with the engine off, so it fails "drives like an automatic". Gains are about 10%. It makes a good **Pro add-on** (standstill charging, quiet restarts), not the core product.

**Rejected "innovative" ideas (and why):**
* *Motor driving one front half-shaft:* through an open differential, torque on one side cannot react, so you get torque steer and yaw.
* *Motor at the gearbox output/diff (P3):* it sits inside the transaxle housing and cannot be reached.
* *Hub motors at the front:* conflicts with steering and brakes, and adds unsprung mass.

---

# PART D: Mechanic's pass, what goes wrong when fitting it

Each issue is listed as **Problem → Consequence → Fix in the revised design**, with severity H/M/L.

### Rear axle and chassis
1. **(H) The rear hubs on a FWD car are not driven.** They are non-splined stub axles or Gen-3 hubs, often with integrated drums. → You cannot just bolt a motor on. → **Supply the whole rear axle as a module (e-Beam)** with driven Gen-3 hubs (splined), CV half-shafts, matching brakes, and the **ABS tone rings at the same tooth count** so the ABS ECU sees identical wheel-speed signals.
2. **(H) Packaging around the twist beam.** The fuel tank sits ahead of the beam, the spare well behind it, and the exhaust muffler often runs transversely between them. → A conventional parallel-axis e-axle with a drop gear does not fit on most cars. → **Coaxial drive unit** (hollow-rotor motor around the half-shaft, two-stage planetary reduction, compact differential) on the **wheel-axis line**, about Ø210 × 380 mm, in the gap between the beam cross-member and the spare-well front wall. Muffler hangers and heat shields are relocated per model.
3. **(H) Ground clearance on Indian speed breakers.** → The lowest point of the drive unit must stay **above the beam's own lowest point and above the fuel tank skin**. Add a **skid plate**. Clearance is checked against the full bump-travel envelope for each model.
4. **(M) Twist-beam roll stiffness.** A housing bolted rigidly across the beam stiffens it in torsion and changes handling. → Mount the drive unit to the beam **at one rigid point and one compliant point** near the shear centre. Validate roll stiffness against OEM values.
5. **(M) Unsprung mass.** The drive unit moves with the beam. → The beam pivots at the front bushings, so mass at the cross-member contributes only about (x/L)² ≈ 0.5 of its weight as effective unsprung mass. That is about **+6 to 7 kg per wheel** on a corner of about 35–40 kg, so roughly +17%. Retune dampers. This is far better than in-wheel motors (+12–15 kg per wheel).
6. **(M) Rear sag from about 60 kg of extra rear mass (battery, drive unit).** → About 20 mm of sag with stock springs. → **Uprated rear springs** in the kit. Check rear **axle load rating (GAWR)**, **tyre load index**, and **GVW / payload** (passenger capacity must not fall).
7. **(M) Brake balance.** More rear mass plus rear regen. → Keep **identical drum or disc torque capacity** to the OEM part, limit rear regen to 0.12 g, and check against IS/AIS braking requirements (R13H-type) with the kit fitted.
8. **(M) Handbrake.** Integrated drums carry the park-brake mechanism. → The e-Beam reuses the OEM drum and shoe park-brake hardware on the driven-hub drum.

### Water, heat, dust (Indian specifics)
9. **(H) Monsoon flooding.** Rear underbody parts go under water at 300 mm. → **IP67/IP6K9K** motor, inverter and connectors; gearbox breather **routed high** into the boot cavity; battery raised on standoffs with **sealed spare-well drain plugs**.
10. **(M) Heat.** The battery is in the boot in 45 °C sun; the motor sees little airflow at crawl speed. → **Cabin-air ducted battery cooling** (as Toyota does, from under the rear seat). The motor is oil-spray cooled from the reducer and has a finned housing. Crawl duty is only 2–4 kW average, while the 10 kW continuous rating is for highway assist.
11. **(L) Dust.** Use sealed bearings and breather filters.

### Engine-off side effects (what most people forget)
12. **(H) Brake vacuum disappears with the engine off.** Petrol engines take it from the intake manifold; diesels use a cam-driven vacuum pump. → After a few brake applications, the pedal goes hard. **This is a safety issue.** → **Electric vacuum pump (EVP)** with a pressure sensor and check valve. If vacuum is low, the kit **refuses EV mode and prompts the driver to start the engine**.
13. **(H) Electric power steering with the engine off.** Many EPS units reduce or remove assist when engine rpm = 0 (to protect the battery), and some start-stop cars restart the engine when the steering wheel is turned. → For each model, a **CAN gateway** on the EPS branch supplies an "engine running" status to the EPS module **only while kit EV mode is active and the 48→12 V DC-DC is supplying power**. Validated per model.
14. **(H) AC stops with the engine off.** In India this alone decides whether EV mode is usable. → A **48 V electric scroll compressor mounted on the original compressor bracket** with an adapter plate, the original hoses re-used through adapter fittings, a shorter accessory belt or idler, and a refrigerant recharge. The **condenser fan** is driven by the kit (wired in parallel with the ECU's fan control), and the **ECU's AC request input is fed by the kit** so the ECU does not raise idle for a compressor that is no longer there. Bonus: removing the belt compressor takes about 1–3 kW of parasitic load off the engine.
15. **(M) The 12 V system drains in EV mode** (EPS, fans, ECU, ABS, wipers). → A **48→12 V DC-DC (2 kW)** at the front, fed by one 16 mm² 48 V cable from the rear pack (2 kW at 48 V is about 42 A; doing the same at 12 V would need about 170 A and a 35 mm² cable). An **EFB 12 V battery** replaces the original.
16. **(M) Dashboard warnings.** With the key on and the engine off, the oil and charge lamps light. → **Do not spoof them** (hiding the oil lamp is unsafe). The kit display shows "EV mode, normal".
17. **(H) How do we stop and restart the engine without tampering with an emission-certified ECU?**
    * ❌ Cutting fuel-pump, injector or coil power sets DTCs, causes emission spikes and is legally treated as tampering.
    * ❌ Switching the ignition key off kills ABS, EPS and airbags. Never do this.
    * ✔ **Tier 1 platforms: use the OEM idle start-stop (ISS/ISG) function** that the ECU already has. Many 2020+ 1.5 L Indian cars (for example the K15 Smart Hybrid models) ship with it. The kit only **creates the conditions** (neutral, clutch released, vacuum OK, battery OK) and **holds the accelerator signal at zero** while in EV mode. Check for each ECU how it behaves with the engine stopped while rolling.
    * ✔ **Tier 2 (no ISS):** the engine **keeps idling** in EV mode (gear in neutral, motor drives). Idle savings are lost but regen, clutch-free driving and the end of low-gear crawling remain (about half the benefit). A later OEM or authorized calibration partnership can enable stop/start.
    * ✔ **Restart:** OEM ISS restart on clutch press, **or a rolling restart**: above about 12 km/h the driver presses the clutch, selects 2nd or 3rd and releases, the car's momentum spins the engine, and **the rear motor adds torque to cancel the jolt**. This causes no starter wear and is smooth when calibrated.
18. **(M) Catalyst cooling during long engine-off periods**, leading to emission spikes on restart. → Model catalyst temperature from engine-off time and keep the engine running during cold start until the catalyst lights off. Prove compliance on the chassis dynamometer as part of type approval.
19. **(M) Diesel DPF regeneration** needs long engine-on periods. → Read DPF regeneration status (OBD/CAN) and **block EV mode during a regeneration**. Do the same for turbo cool-down.

### Driveline
20. **(H) If the motor drives while a gear is engaged and the engine is off, it will back-drive a stopped engine through the gearbox.** → **EV propulsion is allowed only when a neutral sensor (Hall sensor on the shift shaft) confirms neutral and the clutch is released**, or when the clutch is fully depressed. Two independent signals are required.
21. **(M) Gearbox lubrication while rolling in neutral with the engine off.** The output shaft and differential spin while the input shaft is stationary. Manual transaxles splash-lubricate from the final-drive ring gear, and many FWD manuals allow flat towing, but **confirm per gearbox with a 20,000 km endurance test**.
22. **(M) Driver habits.** Rolling in neutral, then selecting a low gear at speed, risks over-revving. → A "Shift to 3" prompt shows the right gear for the current speed, with an over-rev warning chime. Phase-2 rev-matching (see E4) reduces this further.
23. **(M) Parking.** A manual car has no P position. → In EV mode the motor does hill-hold, and a **chime sounds if the door opens with the handbrake off**.

### Electrical and electronics
24. **(H) Intercepting the accelerator (APP) signal is safety-critical.** → Dual-track plausibility as the OEM ECU expects, **a fail-safe relay that defaults to direct pass-through**, independent monitoring, and **pass-through without modification whenever the engine is driving** (no emission-relevant change).
25. **(M) ABS/ESC interaction.** → Read wheel speeds and ESC/ABS active flags from CAN. **Cut rear torque and regen when ABS/ESC intervenes.** The VCU's own IMU acts as an independent check.
26. **(M) EMC from a 400 A, 48 V inverter near radio and CAN.** → AIS-004 EMC testing, twisted shielded phase leads, inverter inside the battery enclosure.
27. **(L) Phase cables flex with suspension travel.** → Use **high-flex cables** with strain relief. The inverter is body-mounted (inside the pack enclosure), not on the beam.

### Business-side "mechanic" realities
28. **(H) OEM warranty is void after the fit.** → Target **cars out of warranty (3–8 years old)**. Over time, approach dealer groups for co-warranty.
29. **(H) Indian buyers expect a full-size spare tyre.** → Battery in the spare well with a **T-type space-saver spare on top** (the boot floor rises about 30–40 mm). A full-size spare option raises the floor about 100 mm.
30. **(M) Rear impact.** The battery sits in the rear crush zone. → A pack cage tied to the **rear longitudinal rails**, the pack pushed to the front of the well, and crash simulation (plus a sled or physical test if the type-approval agency requires it). 48 V LFP has much lower electrical and thermal risk than HV NMC.
31. **(M) CNG cars carry the cylinder in the boot**, which conflicts with the battery location. → Offer slim side-cavity battery modules as a "CNG pack" variant later.
32. **(L) Theft of a valuable battery.** → Security-Torx fasteners and a BMS that pairs to the VCU and refuses to run if moved to another car.

---

# PART E: Revised design, the e-Beam Hybrid Kit

## E1. System layout
```
 FRONT (stock powertrain untouched)                              REAR (kit)
 ┌───────────────────────────────┐                   ┌──────────────────────────────────────┐
 │ ENGINE ─ clutch ─ 5MT ─ diff  │                   │  SPARE WELL: 5.12 kWh 48V LFP pack   │
 │   │                           │                   │  (+ inverter + BMS + 2 kW OBC inside)│
 │ belt: alternator (kept)       │                   │  T-type spare tyre on top            │
 │ AC: 48V e-compressor on the   │   48V feeder      │        │ 3-phase (high-flex)         │
 │     ORIGINAL bracket          │◄══ 16 mm² ═══════►│        ▼                             │
 │ 48V distribution/fuse box     │   (along fuel/    │  e-BEAM (bolts to OEM hard points):  │
 │ DC-DC 48→12V 2 kW             │    brake lines)   │   new twist beam + coaxial e-drive   │
 │ Electric vacuum pump          │                   │   (IPMSM 10/18 kW, 8.5:1, open diff, │
 │ VCU + CAN gateway + IMU       │                   │   dog-clutch disconnect)             │
 │ APP interceptor (fail-safe)   │                   │   driven hubs, CV shafts, OEM-spec   │
 │ Neutral + clutch sensors      │                   │   brakes & ABS rings, uprated springs│
 │ HMI: display / LED + app      │                   │   skid plate                         │
 └───────────────────────────────┘                   └──────────────────────────────────────┘
          CAN: OBD-II (read), chassis CAN (wheel speeds, ESC flags, steering angle), kit CAN
```

## E2. Subsystem specifications
| Subsystem | Specification | Notes |
|---|---|---|
| Battery | 16S LFP, 51.2 V, 100 Ah (5.12 kWh), ≥3C continuous / ≥5C 30 s, IP67, cabin-air ducted cooling, BMS with contactor, pyro-fuse, manual service disconnect | Modular 2 × 2.56 kWh; Lite SKU = one module |
| Motor | 48 V IPMSM, hollow rotor (coaxial), 10 kW continuous / 18 kW peak / 70 Nm, 8,000 rpm, oil-spray cooled | Back-EMF designed to stay below bus voltage up to the disconnect speed |
| Inverter | 48 V, 500 A peak MOSFET, AEC-Q grade, resolver input, CAN, safe state = active short or freewheel by speed | Inside the battery enclosure (EMC, sealing, short DC link) |
| Reducer | 2-stage planetary 8.5:1, compact open differential, **electrically actuated dog-clutch disconnect (spring-open = fail-safe)**, motor speed-synchronized | Renault-style synchronization by the motor |
| e-Beam | New twist beam with OEM hard points (pivot bushings, spring seats, damper mounts), driven-hub end plates, Gen-3 driven hubs, CV shafts, OEM-equivalent drums or discs with park brake, ABS rings, uprated springs, skid plate | One design per platform family; validated for fatigue and roll stiffness |
| AC | 48 V electric scroll compressor (about 14–18 cc, variable speed), adapter bracket on the OEM compressor mounting bolts, hose adapter blocks, new belt or idler | The kit controls the condenser fan and the ECU's AC request |
| Brake vacuum | Electric vacuum pump with pressure sensor and check valve (teed into the booster line) | Blocks EV mode if vacuum is low |
| 12 V | 48→12 V DC-DC 2 kW at the front; alternator retained; EFB 12 V battery | Bidirectional 12→48 V 1 kW trickle (optional) for standstill AC when the pack is empty |
| Charging | 2 kW OBC, inlet behind the fuel flap or bumper, 15 A home socket | 0–100% in about 2.5–3 h |
| VCU | Dual-core lockstep or main+monitor MCU, 6-axis IMU, 3 × CAN, APP in/out with fail-safe relay, GPS/BLE/4G (telematics + OTA) | Supervisory controller |
| Sensors | Neutral position (Hall on shift shaft), clutch pedal position (analog), brake switch tap, vacuum | Plug-in harness adapters with OEM connectors |
| HMI | Small display or cluster-side LEDs (EV / SHIFT n / BOOST / REGEN), chime, phone app | Shows mode, SoC, savings |

**Mass budget:** battery 42 kg, motor 13, inverter 4, reducer + differential 14, e-Beam net of removed parts 14, e-compressor (net) 4, EVP 2, DC-DC 2, OBC 3, cables and harness 6, misc 1 → **about 105 kg** (used in the model).

## E3. Operating modes (what the driver experiences)
```
            key ON, neutral, SoC ok, vacuum ok
   OFF ─────────────────────────────────────► READY (EV)
                                                 │ accelerator → rear motor torque
                                                 │ creep 4 km/h on brake release, hill-hold
                                                 ▼
                              ┌──────────── EV DRIVE (lever in N, engine OFF, clutch untouched) ◄──┐
                              │  exit if: v > 40 km/h, pedal > 85% for 1.5 s, SoC < 20%,           │
                              │           vacuum low, DPF regen, grade > 11%, AC max-cool demand   │
                              ▼                                                                     │
                       HAND-OVER prompt "SHIFT 3"                                                   │
                     driver presses clutch → (a) OEM-ISS restart, or (b) rolling restart:           │
                     select gear, release clutch, rear motor torque-fills the jolt                  │
                              ▼                                                                     │
                       HYBRID (manual driving)                                                      │
                         • ASSIST/BOOST: pedal > 80% → up to 18 kW rear                             │
                         • SHIFT FILL: clutch pressed → rear torque holds acceleration              │
                         • REGEN: lift-off 0.03–0.06 g (B-mode button), brake switch → up to 0.12 g │
                         • CHARGE: SoC < target → rear generates 2–4 kW (load-point shift)          │
                         • DISCONNECT: v > 100 km/h → dog clutch open, zero drag                    │
                              │  driver slows below ~10 km/h and slots N, engine stops (ISS) ───────┘
                              ▼
                       LIMP / FAULT → kit torque = 0, APP pass-through, EVP and DC-DC stay on
                                       = a normal manual car
```

**Typical commute:** leave home on electric power with the lever in neutral, crawl through traffic clutch-free with AC on, take a flyover in EV (or get a "Shift 3" prompt and drive normally), then return to EV at the next signal. Plug in at night.

## E4. How we make a P4 hybrid smooth (the calibration plan)
The reason Approach 1 is "harder to calibrate" is that the kit has **no authority over the engine or the clutch**. The design works around that:

1. **In EV mode the kit has full authority** (engine off, gearbox in neutral). It behaves like an EV: a pedal-to-wheel-torque map, jerk limiting (axle torque rate about 2–4 kNm/s), **gear-lash management** (slow ramp through ±20 Nm when switching between drive and regen), creep, and hill-hold using IMU pitch.
2. **The driver is the shift actuator, and the kit coaches.** HMI prompts are based on speed, pedal and grade, and the driver chooses when to shift.
3. **Shift torque fill (the Renault idea, through the road):** a clutch pedal position sensor anticipates the clutch. As the clutch opens, rear torque rises to match the acceleration before the shift (up to its limit), then fades as the clutch re-engages. Manual shifts feel like a fast AT.
4. **Rolling restart torque fill:** estimate the engine's spin-up drag (compression plus inertia) from speed and gear, and add matching rear torque during clutch release.
5. **Phase 2, rev-matching:** with the clutch down and the engine unloaded, the APP interceptor "blips" the engine to the target-gear rpm (the same thing a driver does by heel-and-toe). Released only if the type-approval agency accepts it.
6. **Regen blending without brake-by-wire:** coast regen (adjustable), plus *additive* regen on the brake switch, plus proportional regen from the ESC brake-pressure signal where that is on CAN. Regen is off during ABS, at lateral acceleration above 0.3 g, with wipers on (reduced), and when rear wheel slip exceeds front by more than 5%.
7. **Stability:** rear slip control (rear vs front wheel speeds), yaw-rate plausibility (IMU vs steering angle from CAN), torque cut on any ESC flag, and **regen limited in corners** to avoid lift-off oversteer.
8. **Self-learning to reduce per-model calibration:** gear ratios identified from OBD rpm vs wheel speed, clutch bite point learned from the clutch sensor plus engine rpm drop, pedal maps by driver profile.
9. **Energy management:** SoC windows; **blended plug-in mode** (learns the commute and home-charging pattern by GPS and time, aims to arrive home at 15–20%); boost reserve always held back.
10. **Effort estimate:** about 300–500 vehicle-calibration hours for the first platform and about 120–200 for each derivative.

## E5. Safety concept (ISO 26262 approach)
| Hazard | Mitigation | Target |
|---|---|---|
| Unintended acceleration (rear motor) | Dual-track pedal plausibility, brake-overrides-accelerator, independent torque monitor (2nd MCU), inverter torque plausibility, contactor-off path | ASIL-B-like |
| Unintended or excess regen (rear lock, oversteer) | Regen ≤ 0.12 g, ABS/ESC flag cut, IMU yaw check, slip control | ASIL-B-like |
| Motor drives against a stopped engine in gear | Two-signal neutral/clutch interlock | ASIL-B-like |
| Loss of brake assist in EV | EVP + vacuum sensor, EV inhibited if vacuum is low, engine-start prompt | ASIL-C-like (brakes) |
| Loss of steering assist in EV | EPS status supplied only while DC-DC is healthy; on fault, request engine start | ASIL-B-like |
| Motor overspeed / uncontrolled generation | Spring-open dog clutch above 100 km/h, back-EMF below bus voltage, active short circuit | QM-B |
| Battery thermal event | LFP, BMS with cell-level monitoring, fuse, IP67, cabin-air isolation damper, crash cage | AIS-038 R2 / AIS-156-style tests |
| APP interceptor fault | Fail-safe relay → direct OEM pass-through (de-energized = stock) | ASIL-B-like |
| **Kit total failure** | **Car reverts to a normal manual car.** EVP and DC-DC stay powered from the 12 V side. | Design principle |

The last line is the strongest safety argument for P4. **The original drivetrain is never broken into**, so a kit fault never strands the car.

## E6. Installation (one and a half days at a certified centre, about 10–11 labour hours)
1. Lift the car; remove rear wheels, brake lines, ABS sensors, handbrake cables, lower damper bolts and beam pivot bolts; drop the OEM beam (1.5 h). **The customer keeps the OEM beam** (or uses a core-exchange discount).
2. Fit the pre-assembled, pre-tested e-Beam and uprated springs; connect and bleed brakes, ABS sensors and handbrake (2 h).
3. Battery cage in the spare well, using existing tie-downs plus 2 rivet-nut points (1 h).
4. 48 V feeder along the existing underbody line clips (1 h).
5. Recover refrigerant, swap the compressor for the e-compressor on the OEM bracket, fit the new belt, recharge (1.5 h).
6. EVP, DC-DC and 48 V distribution box at the front (1 h).
7. Plug-in harness: OBD/CAN gateway, APP interceptor with OEM connectors, neutral and clutch sensors, brake switch tap, HMI (1.5 h).
8. Flash the platform calibration, end-of-line test (automated via the app), road test, RTO paperwork (1 h).

**Returning to stock** is the reverse procedure, about 6 h. The kit can be **re-fitted to the owner's next car** of the same platform family (the battery, motor and electronics move; only the e-Beam is platform-specific).

## E7. Platform roadmap (start where the parc is large and the ECU already supports start-stop)
| Wave | Platform / engine | Example models | Why |
|---|---|---|---|
| 1 | Suzuki Heartect + K15 1.5 L NA (Smart Hybrid ISS) | Brezza, Ertiga, XL6, Ciaz, S-Cross | Matches the 100 bhp / 1,150–1,250 kg kerb target; **OEM ISS already in the ECU**; huge parc; Ertiga is used heavily by fleets |
| 2 | Hyundai–Kia 1.5 MPi / 1.5 CRDi | Creta, Seltos, Verna | Large 2015–2024 manual parc; diesel option |
| 3 | Honda 1.5 i-VTEC | City (4th/5th gen), WR-V | Loyal owners, many manual cars in metros |
| 4 | Tata 1.2 T / 1.5 D, Mahindra 1.2 T / 1.5 D | Nexon, XUV300 | Turbo engines (verify ISS behaviour) |

---

# PART F: Cost, price and customer economics

## F1. Bill of materials (₹, ex-GST, at about 10k kits a year; pilot volumes are about 20% higher)
| # | Item | ₹ |
|---|---|---|
| 1 | Battery 5.12 kWh LFP high-rate + BMS + IP67 enclosure + contactor/fuse/MSD + cooling | 54,000 |
| 2 | Motor 48 V IPMSM 10/18 kW (hollow rotor) | 16,000 |
| 3 | Inverter 48 V 500 A peak | 13,000 |
| 4 | Reducer (2-stage planetary, differential, dog-clutch disconnect + actuator) | 18,000 |
| 5 | e-Beam structure + driven hubs ×2 + CV shafts ×2 + brakes/ABS rings + uprated springs | 26,000 |
| 6 | 48 V e-AC compressor + adapter bracket + hose adapters + belt/idler | 19,000 |
| 7 | Electric vacuum pump + sensor + check valve | 4,000 |
| 8 | DC-DC 48→12 V 2 kW | 6,500 |
| 9 | 2 kW OBC + inlet + portable cable | 8,500 |
| 10 | VCU (main+monitor MCU, IMU, 3×CAN, APP interceptor, telematics) | 8,000 |
| 11 | Sensors (neutral, clutch, brake) + plug-in harness adapters | 3,000 |
| 12 | HMI (LED/display + app) | 3,000 |
| 13 | 48 V cables, distribution/fuse box, connectors, harness | 7,000 |
| 14 | Heat shields, skid plate, exhaust hangers, fasteners | 3,500 |
| | **Kit hardware total** | **≈ ₹1,89,500** (meets the < ₹2 lakh target at volume; about ₹2.3 lakh at pilot volume) |

**Cost-down roadmap to about ₹1.6 lakh:** a 4 kWh default pack (−₹10k), inverter merged into the VCU (−₹5k), localized e-compressor (−₹5k), LFP price trend (−₹6–8k), localized reducer (−₹4k).

**SKUs:**
* **Lite:** 2.56 kWh, no OBC, charge-sustaining only. Cost about ₹1.6 lakh, MRP about ₹2.6 lakh.
* **Core:** the 5.12 kWh plug-in kit above. MRP about ₹3.25 lakh.
* **Auto add-on:** iMT-style clutch actuator for a two-pedal drive. Adds about ₹45k.
* **Pro add-on:** P0 48 V BSG for standstill charging and quiet restarts. Adds about ₹30k.

## F2. Unit economics (Core, at volume)
| Line | ₹ |
|---|---|
| MRP incl. GST (assumed 18% on parts after the 2025 rationalization; verify HSN codes) | 3,25,000 |
| Net of GST | 2,75,400 |
| − Installer fee (about 11 h labour + margin) | 15,000 |
| − Warranty reserve (about 4%, 3 yr / 60,000 km; battery 5 yr) | 11,000 |
| − Sales, marketing, logistics | 15,000 |
| − Kit hardware | 1,89,500 |
| **Contribution per kit** | **≈ ₹45,000 (16%)**, rising to about ₹75k (27%) after cost-down |

## F3. Customer payback (petrol ₹100/L, electricity ₹8/kWh, AC on; percentages from the model)
| User | Use pattern | Stock fuel cost a year | With kit (fuel + electricity) | Saving a year | Simple payback on ₹3.25 lakh |
|---|---|---|---|---|---|
| City commuter | 40 km/day × 300 days, one charge a day | ₹1.20 lakh | ₹0.65 lakh | **≈ ₹55–60k** (+ about ₹4k clutch/brake wear) | about 5–5.5 years |
| Heavy city user (sales/fleet) | 100 km/day × 300 days, one charge a day | ₹3.0 lakh | ₹2.05 lakh | **≈ ₹95k** | about 3.4 years |
| Heavy user, two charges a day | 100 km/day, midday top-up | ₹3.0 lakh | ₹1.89 lakh | **≈ ₹1.1 lakh** | about 2.9 years |

**Being honest about the pitch:** at 5-year payback, **savings alone will not sell the kit to light commuters**. The real value proposition is this:
> *"Your manual car becomes a clutch-free plug-in hybrid in city traffic, with about 1.4–2× city mileage and an overtaking boost, for less than the loss you take selling it to buy a new automatic or hybrid (₹2–6 lakh+)."*

* A 5-year loan at 12% on ₹3.25 lakh is an EMI of **about ₹7.2k a month**. For heavy users, the fuel saving covers the EMI.
* Target buyers: (1) owners of 3–8-year-old manual cars in traffic-heavy metros (Bengaluru, Mumbai, Pune, Delhi-NCR, Hyderabad, Chennai) who want an automatic; (2) high-mileage city users; (3) corporate employee-transport and rental fleets (B2B, data-friendly, centralized charging).

---

# PART G: The startup plan

## G1. Regulatory path (India), to confirm with ARAI / ICAT / GARC early
* **CMVR retrofit route for hybrid electric system kits: AIS-123 (Part 1), conversion of M and N vehicles under 3.5 t GVW to hybrid.** Kit type approval is **per make/model (variant family)** by a test agency. Installation only through **kit-manufacturer-authorized installers**. **RTO endorsement** on the RC. Insurance endorsement.
* Supporting standards: **AIS-038 Rev 2** (electric powertrain and REESS safety; most clauses relaxed below 60 V), battery safety tests (AIS-156-style), **AIS-004 EMC**, braking tests with the kit fitted, **emissions on MIDC with the kit fitted** (show no deterioration), and BS-VI **OBD functions must stay intact** (which is why we never modify the engine ECU).
* Also check: suspension component approval (the e-Beam is a replacement axle), the rear-impact test requirement, and whether wiring the APP interceptor counts as modifying an emission-related control. **Get written guidance from the test agency in Phase 0.**

## G2. Go-to-market
* **Channel:** use the **CNG-kit playbook**. Certified fitment centres (multi-brand workshop chains, CNG installers wanting to diversify, dealer groups' used-car arms), with a factory-trained technician at each and installs booked through the app.
* **Beachhead:** 1–2 cities and 1 platform (Brezza/Ertiga K15), B2B fleet pilots first (they measure fuel, are tolerant of iteration, and give testimonials), then retail.
* **Financing:** NBFC partnerships with EMIs marketed against fuel savings shown in the app (telematics proves the savings).
* **Retention and moat:** kit re-fit to the next car, OTA updates, a battery health certificate for resale value.

## G3. Roadmap and capital
| Phase | Time | Budget | Milestones |
|---|---|---|---|
| 0: Proof | 0–4 months | ₹40–60 lakh | Teardown of platform 1; mule car using an off-the-shelf 48 V e-3W motor and inverter, a Chinese 48 V e-compressor, and a crude rear sub-frame; prove **EV crawl in neutral, OEM-ISS engine-off behaviour, rolling restart and shift fill**; test-agency pre-consultation |
| 1: Engineering prototype | 4–12 months | ₹3–4 Cr | e-Beam v1 + coaxial drive unit (Indian gear supplier), pack v1 (cell supplier + pack partner), VCU v1 with safety concept; 5 cars; 50,000 km durability; chassis-dyno MIDC; water wading and 45 °C hot tests |
| 2: Approval + pilot | 12–24 months | ₹10–15 Cr | AIS-123 approval for platform 1 (2–3 variants); 200–500 kits through 5 centres in 2 cities; fleet data |
| 3: Scale | 24–48 months | ₹40–60 Cr | Platforms 2–4, 10k kits a year, localized pack/motor/reducer, cost-down to about ₹1.6 lakh, 50+ centres |

**Core team:** powertrain controls/calibration lead, chassis and suspension engineer (e-Beam), power electronics engineer, battery engineer, functional-safety engineer, homologation specialist, service-network operations lead.

## G4. Market size (rough)
* India's in-use passenger-car parc is several tens of millions and still mostly manual.
* Serviceable segment: **manual 1.2–1.5 L cars, 2016–2024 models, on the top 4–6 platforms, in the top 15 cities**, roughly **4–6 million vehicles**.
* 1% penetration over 5 years is about 50k kits, roughly **₹1,500 Cr in revenue**. *(Refine with VAHAN registration data.)*

## G5. Key risks and mitigations
| Risk | Mitigation |
|---|---|
| Approval time and cost per model | Platform families sharing one e-Beam; start with the largest parc; engage the agency in Phase 0 |
| ECU will not cooperate with engine-off (no ISS) | Tier-2 "engine idles" mode; long term, an OEM partnership (offer the kit as dealer-fitted accessory) |
| Long payback | Convenience-led pitch, financing, fleet focus, Lite SKU |
| Competition from new affordable strong hybrids (including OEM in-house series hybrids) and EVs | We target the **existing parc**, which new launches do not serve; our price undercuts any trade-in loss |
| Installer quality and liability | Pre-assembled modules, plug-in harnesses, app-guided end-of-line test, telematics monitoring, product liability insurance |
| Battery price and supply | LFP multi-sourcing; modular pack |
| Safety incident damaging the brand | ISO 26262-style process from day one; fail-to-stock architecture; conservative regen |

## G6. Patentable ideas to file early
1. **Rolling engine restart with clutch-anticipated rear-axle torque fill** for manual-gearbox through-the-road hybrids.
2. **Neutral-state EV propulsion with two-signal interlock and driver hand-over prompts** for retrofitted manual vehicles.
3. **Shift torque fill for manual gearboxes** using a secondary-axle motor driven by a clutch pedal position sensor.
4. **Bolt-in rear axle module (e-Beam)** with a coaxial e-drive that reuses OEM suspension hard points.
5. **Start-stop condition emulation** to use an OEM ECU's idle-stop function for rolling EV operation without modifying the ECU.

---

# PART H: Next steps and open questions
1. **Pick platform 1 and tear one down.** Measure the space between beam, tank, spare well and exhaust; ECU ISS behaviour while rolling; EPS behaviour with the engine stopped; how the hub bolts on; ABS ring tooth count.
2. **Build the mule (Phase 0)** within about 3 months using off-the-shelf 48 V parts. Measure fuel on a fixed city route against an identical stock car (back-to-back, same driver, same day).
3. **Replace the synthetic cycle** with logged real traffic data (OBD + GPS from 20 cars over 2 weeks) and re-run `sim/kit_sim.py`, then move to a forward model (Simulink or similar) for drivability.
4. **Test-agency pre-consultation** on AIS-123 scope, APP interception and the e-Beam (suspension part) approval route.
5. **Supplier RFQs:** LFP high-rate cells/pack, 48 V coaxial motor, inverter, 48 V e-compressor, twist-beam fabrication, gear sets.
6. **Customer discovery:** 100 interviews (commuters, fleet managers, workshop owners) to test the ₹3.25 lakh price and the "automatic in traffic" pitch, and a Lite vs Core preference.

---

### Appendix: model assumptions (`sim/kit_sim.py`)
* 1,500 kg stock test mass, +105 kg kit; CdA 0.72 m²; Crr 0.011; rolling radius 0.305 m; rotational mass factor 1.06.
* Engine: 1.46 L, 75 kW, Willans line η_ind = 0.37, FMEP = 1.15 + 0.18·k + 0.04·k² bar (k = rpm/1000), idle 800 rpm, 1 g of fuel per restart.
* 5MT ratios 3.545/1.904/1.233/0.885/0.690, final drive 4.10, driveline efficiency 0.92; driver upshifts early (about 1,350–1,900 rpm).
* AC: stock belt compressor 1.3 kW average shaft load; kit e-compressor 1.0 kW electrical. 12 V loads 300 W (alternator efficiency 0.60, DC-DC 0.92).
* Kit: motor+inverter efficiency 0.79–0.91 depending on load; reducer 0.96; battery 0.96 one way; regen ≤ 0.12 g and above 5 km/h; EV below 40 km/h; engine stops only below 10 km/h after at least 20 s on; charge-sustaining mode generates up to 4 kW through the road.
* Charge-sustaining results are corrected for the remaining SoC difference using a marginal engine-to-battery efficiency of about 27%.
* **Limitations:** no thermal model, no cold start, synthetic cycles, a simplified driver, and no diesel map. Use the trends; do not treat the absolute numbers as results.
