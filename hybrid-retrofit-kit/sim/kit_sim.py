#!/usr/bin/env python3
"""
First-order (backward-facing) energy model for the bolt-on P4 hybrid retrofit kit.

Purpose: sanity-check sizing and the fuel-economy story BEFORE building hardware.
It is deliberately simple and every assumption is a named constant you can change.
It is NOT a substitute for a calibrated forward model (GT-Suite / AVL Cruise /
MATLAB-Simulink) or for chassis-dyno testing.

Run:  python3 kit_sim.py
"""
import math
import numpy as np

G = 9.81
RHO_AIR = 1.18
PETROL_KWH_PER_L = 8.9          # lower heating value ~32 MJ/L
PETROL_DENSITY = 0.745          # kg/L

# ---------------------------------------------------------------- vehicle
M_STOCK = 1500.0                # test mass incl. driver + 1 passenger [kg]
KIT_MASS = 105.0                # see BOM mass budget in the design doc [kg]
CDA = 0.72                      # Cd * frontal area [m^2] (compact SUV / sedan)
CRR = 0.011
R_WHEEL = 0.305                 # rolling radius, 195/60 R16 class [m]
ROT_INERTIA_FACTOR = 1.06       # equivalent mass factor (wheels, driveline)

# ---------------------------------------------------------------- engine (1.5 L NA petrol, ~100 bhp)
DISP = 1.462e-3                 # m^3
P_ENG_MAX = 75e3                # W
N_IDLE = 800.0
ETA_IND = 0.37                  # Willans slope: indicated efficiency
IDLE_PENALTY = 1.05             # idle speed control / spark reserve

def fmep_bar(n_rpm):
    """Friction + pumping mean effective pressure (Willans offset), bar."""
    k = n_rpm / 1000.0
    return 1.15 + 0.18 * k + 0.04 * k * k

def p_friction(n_rpm):
    return fmep_bar(n_rpm) * 1e5 * DISP * n_rpm / 120.0   # W, 4-stroke

def t_eng_max(n_rpm):
    """Full-load torque curve, Nm (peak ~138 Nm @ 4400 rpm, ~75 kW @ 6000)."""
    t = 138.0 * (1.0 - ((n_rpm - 4400.0) / 7000.0) ** 2)
    t = min(t, P_ENG_MAX / (max(n_rpm, 500.0) * 2 * math.pi / 60.0))
    return max(t, 60.0)

def fuel_power(p_brake, n_rpm, idle=False):
    """Fuel chemical power [W] for given brake power and speed (Willans line)."""
    p = (max(p_brake, 0.0) + p_friction(n_rpm)) / ETA_IND
    return p * (IDLE_PENALTY if idle else 1.0)

# ---------------------------------------------------------------- manual gearbox (K15-class 5MT)
GEARS = [3.545, 1.904, 1.233, 0.885, 0.690]
FINAL = 4.10
ETA_MT = 0.92

def engine_rpm(v, g):
    return v / R_WHEEL * GEARS[g] * FINAL * 60.0 / (2 * math.pi)

def pick_gear(v, accel, p_wheel_req):
    """Rough model of a typical Indian city driver (early upshifts)."""
    rpm_floor = 1900.0 if accel > 0.3 else 1350.0
    best = 0
    for g in range(len(GEARS)):
        n = engine_rpm(v, g)
        if n < rpm_floor:
            break
        p_avail = t_eng_max(n) * n * 2 * math.pi / 60.0 * ETA_MT
        if p_avail * 0.9 >= p_wheel_req:
            best = g
    return best

# ---------------------------------------------------------------- kit electric drive (48 V, P4 rear)
MOT_T_MAX = 70.0                # Nm peak
MOT_P_MAX = 18e3                # W peak (30 s)
MOT_P_CONT = 10e3               # W continuous
MOT_N_MAX = 8000.0              # rpm
RATIO_REAR = 8.5                # 2-stage reduction incl. diff
ETA_REAR_GEAR = 0.96
BATT_KWH = 5.12                 # 16S 100 Ah LFP, 51.2 V nominal
ETA_BATT = 0.96                 # one-way (charge or discharge)
REGEN_MAX_G = 0.12              # rear-only regen limit for stability
DISCONNECT_KMH = 100.0          # dog clutch opens above this

def eta_motor_inv(p_abs):
    """Combined motor + inverter efficiency, crude map vs load."""
    return 0.91 - 0.12 * math.exp(-p_abs / 1500.0)

def motor_rpm(v):
    return v / R_WHEEL * RATIO_REAR * 60.0 / (2 * math.pi)

def motor_wheel_force_max(v):
    n = max(motor_rpm(v), 1.0)
    if n > MOT_N_MAX or v * 3.6 > DISCONNECT_KMH:
        return 0.0
    t = min(MOT_T_MAX, MOT_P_MAX / (n * 2 * math.pi / 60.0))
    return t * RATIO_REAR * ETA_REAR_GEAR / R_WHEEL

# ---------------------------------------------------------------- accessories
AC_ON = True                    # Indian summer city driving
AC_MECH_SHAFT_W = 1300.0        # stock belt compressor, avg incl. clutch cycling
AC_ELEC_W = 1000.0              # 48 V variable-speed e-compressor, same cabin duty
LV_LOAD_W = 300.0               # 12 V loads (EPS, fans, ECU, lights avg)
EVP_W = 30.0                    # electric vacuum pump average
ALT_ETA = 0.60
DCDC_ETA = 0.92
START_FUEL_G = 1.0              # warm restart fuel penalty per engine start

# ---------------------------------------------------------------- drive cycles (1 Hz speed traces, m/s)
def ece15():
    pts = [(0, 0), (11, 0), (15, 15), (23, 15), (28, 0), (49, 0), (61, 32), (85, 32),
           (96, 0), (117, 0), (143, 50), (155, 50), (163, 35), (176, 35), (188, 0), (195, 0)]
    t = np.arange(0, 196)
    return np.interp(t, [p[0] for p in pts], [p[1] for p in pts]) / 3.6

def midc_urban():
    return np.concatenate([ece15()[:-1]] * 4)

def indian_heavy_traffic(seed=7, duration=3600):
    """Synthetic stop-go metro traffic: ~35% idle, peaks 8-45 km/h."""
    rng = np.random.default_rng(seed)
    v = []
    while len(v) < duration:
        v += [0.0] * int(rng.integers(8, 75))                 # idle
        vpk = rng.uniform(8, 45) / 3.6
        a = rng.uniform(0.6, 1.2)
        d = rng.uniform(0.8, 1.4)
        v += list(np.arange(0, vpk, a))                        # accelerate
        v += [vpk] * int(rng.integers(3, 35))                  # cruise
        if rng.random() < 0.35:                                # slow-down & re-accelerate
            vlow = vpk * rng.uniform(0.3, 0.6)
            v += list(np.arange(vpk, vlow, -d)) + list(np.arange(vlow, vpk, a))
            v += [vpk] * int(rng.integers(3, 20))
        v += list(np.arange(vpk, 0, -d))                       # stop
    return np.clip(np.array(v[:duration]), 0, None)

def highway(seed=3, duration=2400):
    """Indian 4-lane highway: 70-95 km/h cruise, overtakes to ~105, truck slowdowns."""
    rng = np.random.default_rng(seed)
    v = list(np.arange(0, 80 / 3.6, 0.8))
    while len(v) < duration:
        cur = v[-1]
        r = rng.random()
        if r < 0.25:   # overtake
            tgt = min(cur + rng.uniform(15, 25) / 3.6, 105 / 3.6)
            v += list(np.arange(cur, tgt, 0.9)) + [tgt] * 8
        elif r < 0.45: # slow down behind truck
            tgt = max(cur - rng.uniform(15, 35) / 3.6, 45 / 3.6)
            v += list(np.arange(cur, tgt, -0.7)) + [tgt] * int(rng.integers(10, 40))
        else:          # cruise
            tgt = rng.uniform(72, 95) / 3.6
            step = 0.5 if tgt > cur else -0.5
            v += list(np.arange(cur, tgt, step)) + [tgt] * int(rng.integers(30, 120))
    return np.array(v[:duration])

# ---------------------------------------------------------------- simulation core
def road_force(v, m):
    return CRR * m * G * (1 if v > 0.05 else 0) + 0.5 * RHO_AIR * CDA * v * v

def simulate(cycle, kit=False, soc0=0.55, mode="CS", soc_target=0.55):
    """
    Returns dict with fuel [L], distance [km], battery energy change [kWh], starts, etc.
    mode: "CS" charge-sustaining (no plug), "CD" charge-depleting (plug-in day).
    """
    m = M_STOCK + (KIT_MASS if kit else 0.0)
    me = m * (ROT_INERTIA_FACTOR + (0.005 if kit else 0.0))
    soc = soc0
    e_batt = BATT_KWH * 3600e3
    fuel_J = 0.0
    dist = 0.0
    starts = 0
    eng_on = not kit
    eng_on_timer = 0
    ev_s = 0
    regen_J = 0.0
    depleted_km = None
    soc_low = 0.20 if mode == "CS" else 0.15
    v_ev_max = 40 / 3.6

    for i in range(1, len(cycle)):
        v0, v1 = cycle[i - 1], cycle[i]
        v = 0.5 * (v0 + v1)
        a = v1 - v0
        dist += v
        f_wheel = me * a + road_force(v, m)
        p_wheel = f_wheel * v

        # ------------------------------------------------ accessory demand
        if kit:
            p_elec_acc = (AC_ELEC_W if AC_ON else 0) + LV_LOAD_W / DCDC_ETA + EVP_W
            p_shaft_acc = 80.0   # unloaded alternator drag
        else:
            p_elec_acc = 0.0
            p_shaft_acc = (AC_MECH_SHAFT_W if AC_ON else 0) + LV_LOAD_W / ALT_ETA

        p_motor_wheel = 0.0      # +drive / -regen at the wheel, rear axle
        p_eng_wheel = 0.0        # engine contribution at the wheel

        if not kit:
            p_eng_wheel = p_wheel
        else:
            fmax = motor_wheel_force_max(v)
            # ---------- state machine (mimics prompted driver hand-over)
            ev_ok = soc > soc_low and v < v_ev_max and (f_wheel <= fmax or f_wheel <= 0)
            if eng_on:
                eng_on_timer += 1
                if v < 10 / 3.6 and soc > soc_low + 0.05 and eng_on_timer > 20 and ev_ok:
                    eng_on = False          # driver slots neutral at a stop/crawl
            else:
                if not ev_ok:
                    eng_on = True
                    eng_on_timer = 0
                    starts += 1
                    fuel_J += START_FUEL_G / 1000 / PETROL_DENSITY * PETROL_KWH_PER_L * 3600e3

            if p_wheel < 0:   # braking: rear regen up to stability limit, rest friction
                f_regen = min(-f_wheel, REGEN_MAX_G * m * G, fmax) if v > 5 / 3.6 else 0.0
                p_motor_wheel = -f_regen * v
            elif not eng_on:
                p_motor_wheel = p_wheel
                ev_s += 1 if v > 0.05 else 0
            else:
                g = pick_gear(v, a, p_wheel)
                n = engine_rpm(v, g)
                p_eng_cap = t_eng_max(n) * n * 2 * math.pi / 60 * ETA_MT
                # boost: motor covers what engine can't, plus heavy-pedal assist
                assist = max(0.0, p_wheel - 0.85 * p_eng_cap)
                if mode == "CD" and soc > soc_target:
                    assist = max(assist, min(0.5 * p_wheel, 8e3))   # spend grid energy
                assist = min(assist, fmax * v)
                charge = 0.0
                if mode == "CS" and soc < soc_target and fmax > 0:
                    # through-the-road load-point shifting (rear motor generates)
                    charge = min(4e3, fmax * v * 0.5, max(0.0, 0.8 * p_eng_cap - p_wheel))
                p_motor_wheel = assist - charge
                p_eng_wheel = p_wheel - p_motor_wheel

        # ------------------------------------------------ electrical bookkeeping
        if kit:
            if p_motor_wheel >= 0:
                p_mech = p_motor_wheel / ETA_REAR_GEAR
                p_dc = p_mech / eta_motor_inv(p_mech) if p_mech > 0 else 0.0
            else:
                p_mech = -p_motor_wheel * ETA_REAR_GEAR
                p_dc = -p_mech * eta_motor_inv(p_mech)
                regen_J += -p_dc
            p_dc += p_elec_acc
            # standstill with exhausted battery: engine idles, alternator->DCDC trickle
            if v < 0.05 and soc <= soc_low and not eng_on:
                eng_on = True; starts += 1; eng_on_timer = 0
            if v < 0.05 and eng_on and soc <= soc_low + 0.03:
                trickle = 1000.0
                p_dc -= trickle
                p_shaft_acc += trickle / (ALT_ETA * DCDC_ETA)
            e_term = p_dc / ETA_BATT if p_dc > 0 else p_dc * ETA_BATT
            soc -= e_term / e_batt
            if depleted_km is None and soc <= soc_low + 0.005:
                depleted_km = dist / 1000

        # ------------------------------------------------ engine fuel
        if eng_on:
            if v < 0.05 or (p_eng_wheel <= 0 and v < 15 / 3.6):
                fuel_J += fuel_power(p_shaft_acc, N_IDLE, idle=True)       # idle / declutched
            elif p_eng_wheel <= 0:
                pass                                                         # DFCO overrun
            else:
                g = pick_gear(v, a, p_eng_wheel)
                n = max(engine_rpm(v, g), 1100.0)                            # clutch slip at launch
                fuel_J += fuel_power(p_eng_wheel / ETA_MT + p_shaft_acc, n)

    fuel_L = fuel_J / (PETROL_KWH_PER_L * 3600e3)
    d_batt_kwh = (soc0 - soc) * BATT_KWH          # +ve = energy taken from battery
    return dict(fuel_L=fuel_L, km=dist / 1000, d_batt_kwh=d_batt_kwh, soc_end=soc,
                starts=starts, ev_frac=ev_s / max(1, np.count_nonzero(cycle > 0.05)),
                regen_kwh=regen_J / 3.6e6, depleted_km=depleted_km)

def cs_corrected_kmpl(res):
    """Correct residual SoC swing to fuel using marginal engine->battery path (~27%)."""
    marg = 0.33 * 0.86 * ETA_REAR_GEAR * ETA_BATT
    fuel = res["fuel_L"] + res["d_batt_kwh"] / marg / PETROL_KWH_PER_L
    return res["km"] / fuel

# ---------------------------------------------------------------- performance checks
def accel_time(v_from, v_to, gear, boost, m):
    me = m * ROT_INERTIA_FACTOR
    v, t = v_from / 3.6, 0.0
    while v < v_to / 3.6:
        n = engine_rpm(v, gear)
        f = t_eng_max(n) * GEARS[gear] * FINAL * ETA_MT / R_WHEEL
        if boost:
            f += motor_wheel_force_max(v)
        a = (f - road_force(v, m)) / me
        v += a * 0.05
        t += 0.05
        if t > 60:
            return float("nan")
    return t

def main():
    print("=" * 78)
    print("ROAD LOAD (stock mass %.0f kg) & EV CAPABILITY (kit mass %.0f kg)" % (M_STOCK, M_STOCK + KIT_MASS))
    print("-" * 78)
    for kmh in (20, 30, 40, 50, 60, 80, 100, 120):
        v = kmh / 3.6
        print(f"  {kmh:4d} km/h : road load {road_force(v, M_STOCK):6.0f} N  ->  {road_force(v, M_STOCK)*v/1e3:5.1f} kW at wheels"
              f"   | motor rpm {motor_rpm(v):6.0f}")
    mk = M_STOCK + KIT_MASS
    f0 = motor_wheel_force_max(1.0)
    print(f"\n  Rear wheel force at launch       : {f0:6.0f} N  ({f0*R_WHEEL:.0f} Nm at axle)")
    print(f"  EV launch acceleration (flat)     : {(f0 - road_force(1, mk)) / (mk*ROT_INERTIA_FACTOR):.2f} m/s^2")
    print(f"  EV gradeability (standing start)  : {100*math.tan(math.asin((f0 - CRR*mk*G)/(mk*G))):.1f} %")
    t = 0.0; v = 0.0
    while v < 40 / 3.6:
        v += (motor_wheel_force_max(v) - road_force(v, mk)) / (mk * ROT_INERTIA_FACTOR) * 0.05; t += 0.05
    print(f"  EV 0-40 km/h (full pedal)         : {t:.1f} s")
    print(f"  Rear-axle traction limit (mu 0.7) : {0.7*0.42*mk*G:6.0f} N  (static rear load ~42%)")

    print("\n" + "=" * 78)
    print("OVERTAKING (engine full load, 4th gear)")
    print("-" * 78)
    for (a_, b_) in ((40, 80), (60, 100)):
        ts = accel_time(a_, b_, 3, False, M_STOCK)
        tk = accel_time(a_, b_, 3, True, mk)
        print(f"  {a_}-{b_} km/h : stock {ts:5.1f} s   kit+boost {tk:5.1f} s   ({100*(ts-tk)/ts:4.0f}% quicker)")
    for (a_, b_) in ((60, 100),):
        ts = accel_time(a_, b_, 4, False, M_STOCK)
        tk = accel_time(a_, b_, 4, True, mk)
        print(f"  {a_}-{b_} km/h in 5th : stock {ts:5.1f} s   kit+boost {tk:5.1f} s")

    print("\n" + "=" * 78)
    print("FUEL ECONOMY  (AC ON, petrol)   CS = charge-sustaining, no plug-in")
    print("-" * 78)
    cycles = {"MIDC urban (4x ECE-15)": midc_urban(),
              "Indian heavy traffic (synthetic)": indian_heavy_traffic(),
              "Highway 70-105 km/h (synthetic)": highway()}
    for name, cyc in cycles.items():
        s = simulate(cyc, kit=False)
        k = simulate(cyc, kit=True, mode="CS")
        kmpl_s = s["km"] / s["fuel_L"]
        kmpl_k = cs_corrected_kmpl(k)
        avg = s["km"] / (len(cyc) / 3600)
        print(f"  {name:34s} avg {avg:4.1f} km/h | stock {kmpl_s:5.1f} kmpl | kit CS {kmpl_k:5.1f} kmpl"
              f" | {100*(kmpl_k/kmpl_s-1):+4.0f}% | EV {100*k['ev_frac']:3.0f}% of moving time | starts {k['starts']}")

    print("\n" + "=" * 78)
    print("PLUG-IN DAY: heavy traffic, start at 95% SoC, run until 15% then CS")
    print("-" * 78)
    cyc = indian_heavy_traffic(seed=11, duration=3600 * 3)
    k = simulate(cyc, kit=True, mode="CD", soc0=0.95, soc_target=0.15)
    s = simulate(cyc, kit=False)
    print(f"  battery reached 15% SoC after      : {k['depleted_km']:.1f} km (engine-assisted CD driving)")
    print(f"  distance {k['km']:.1f} km | stock fuel {s['fuel_L']:.2f} L | kit fuel {k['fuel_L']:.2f} L"
          f" + {k['d_batt_kwh']:.2f} kWh from battery (plug-in)")
    e_per_km = k["d_batt_kwh"] / max(k["km"], 1e-6)
    print(f"  battery energy use incl. AC        : {1000*e_per_km:.0f} Wh/km over the run")

def extra():
    global AC_ON
    print("\n" + "=" * 78)
    print("SENSITIVITY")
    print("-" * 78)
    hw = highway()
    s = simulate(hw, kit=False)
    k = simulate(hw, kit=True, mode="CD", soc0=0.60, soc_target=0.25)
    print(f"  Highway using leftover plug-in energy (60->25% SoC): fuel {s['fuel_L']:.2f} -> {k['fuel_L']:.2f} L"
          f" ({100*(1-k['fuel_L']/s['fuel_L']):.0f}% less) + {k['d_batt_kwh']:.2f} kWh")
    AC_ON = False
    for name, cyc in (("MIDC urban, AC OFF", midc_urban()), ("Heavy traffic, AC OFF", indian_heavy_traffic())):
        s = simulate(cyc, kit=False); k = simulate(cyc, kit=True, mode="CS")
        a, b = s["km"] / s["fuel_L"], cs_corrected_kmpl(k)
        print(f"  {name:34s} stock {a:5.1f} kmpl | kit CS {b:5.1f} kmpl | {100*(b/a-1):+4.0f}%")
    AC_ON = True

if __name__ == "__main__":
    main()
    extra()
