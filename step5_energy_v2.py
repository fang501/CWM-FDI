#!/usr/bin/env python3
"""
step5_energy_v2.py — CUMULATIVE ENERGY, improved model, with static/dynamic split.

Energy = STATIC part  (P_IDLE x elapsed time)          <- cost of being on
       + DYNAMIC part (K x total bytes)                <- marginal cost of data
       + NIC part     (NIC_POWER x elapsed time)       <- datasheet, RAPL-invisible

Run with nethogs TOTAL mode (-v 3, cumulative MB):

    sudo nethogs -v 3 -t | python3 step5_energy_v2.py firefox
"""

import sys
import time

# ---------- fitted model parameters: PASTE YOUR VALUES FROM STEP 2 & 4 ----------
P_IDLE_W     = 7.19     # measured idle baseline, W   (step2_idle_baseline.py)
K_J_PER_BYTE = 8e-9     # fitted marginal cost, J/B   (step4_fit_model.py)
NIC_POWER_W  = 0      # datasheet NIC power (0.3 .. 1.0 W)

MB = 1024 * 1024        # nethogs -v 3 reports MB


def main():
    name_filter = sys.argv[1] if len(sys.argv) > 1 else ""

    t_start = time.time()
    total_MB = 0.0      # latest cumulative reading from nethogs

    print(f"{'data MB':>10} {'E_static J':>12} {'E_dynamic J':>12} {'E_total J':>11}")

    for line in sys.stdin:
        if name_filter and name_filter not in line:
            continue
        parts = line.split()
        if len(parts) < 3:
            continue
        try:
            sent_MB, recv_MB = float(parts[-2]), float(parts[-1])  # cumulative MB
        except ValueError:
            continue

        total_MB = sent_MB + recv_MB
        elapsed = time.time() - t_start

        # the three components of the improved model
        e_static  = P_IDLE_W * elapsed                 # idle floor x time
        e_dynamic = K_J_PER_BYTE * total_MB * MB       # marginal x bytes
        e_nic     = NIC_POWER_W * elapsed              # datasheet NIC x time
        e_total   = e_static + e_dynamic + e_nic

        print(f"{total_MB:10.3f} {e_static:12.2f} {e_dynamic:12.4e} {e_total:11.2f}")

    # ---------- session summary ----------
    elapsed = time.time() - t_start
    e_static  = P_IDLE_W * elapsed
    e_dynamic = K_J_PER_BYTE * total_MB * MB
    e_nic     = NIC_POWER_W * elapsed
    print("\n--- session summary ---")
    print(f"elapsed        : {elapsed:.1f} s")
    print(f"data           : {total_MB:.2f} MB")
    print(f"E static (CPU idle floor) : {e_static:10.2f} J")
    print(f"E dynamic (per-byte cost) : {e_dynamic:10.4e} J")
    print(f"E NIC (datasheet)         : {e_nic:10.2f} J")
    print(f"E TOTAL                   : {e_static + e_dynamic + e_nic:10.2f} J")
    print("\nnote how static+NIC (time-based) usually dwarfs dynamic (byte-based):")
    print("this is the energy-proportionality gap / 'race to idle' result.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
