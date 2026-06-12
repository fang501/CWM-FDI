#!/usr/bin/env python3
"""
net_energy.py — power & energy readings from nethogs traffic,
using the assignment's energy model:

    "A 1 Gb/s Ethernet port draws roughly 0.3 W to 1.0 W of active power."

Two equivalent views of that model:
  1. Per-byte:  E/B = P / link_rate
                upper bound: 1.0 W / 125e6 B/s = 8e-9 J/B  (8 nJ/byte)
                lower bound: 0.3 W / 125e6 B/s = 2.4e-9 J/B
  2. Active-power: the port draws ACTIVE_POWER_W whenever traffic flows,
                regardless of speed. Energy = P x active time.

This script reports BOTH:
  - per-byte model  -> power proportional to byte rate
  - active model    -> constant power while rate > threshold

Usage:
    sudo nethogs -t | python3 net_energy.py firefox
    (argument = substring filter on the program name, like grep)

nethogs -t (default -v 0) lines end with two numbers: SENT RECEIVED in KB/s.
"""

import sys
import time

# ---- Energy model parameters (from the assignment) ---------------------------
LINK_RATE_BPS   = 125e6    # 1 Gb/s = 125,000,000 bytes/s
ACTIVE_POWER_W  = 1.0      # active power draw of the port (use 0.3 for lower bound)
JOULES_PER_BYTE = ACTIVE_POWER_W / LINK_RATE_BPS   # = 8e-9 J/B at 1.0 W

ACTIVE_THRESHOLD_BPS = 1.0  # rate above this counts the port as "active"
KB = 1024                   # nethogs KB/s -> bytes/s


def parse_line(line: str):
    """Return (sent_KBps, recv_KBps) or None for non-data lines."""
    parts = line.split()
    if len(parts) < 3:
        return None
    try:
        return float(parts[-2]), float(parts[-1])   # SENT, RECEIVED
    except ValueError:
        return None


def main():
    name_filter = sys.argv[1] if len(sys.argv) > 1 else ""

    total_bytes   = 0.0   # cumulative data
    energy_pb_J   = 0.0   # cumulative energy, per-byte model
    energy_act_J  = 0.0   # cumulative energy, active-power model
    active_time_s = 0.0
    last_t = time.time()

    print(f"{'rate B/s':>12} {'P(per-byte) W':>14} {'P(active) W':>12} "
          f"{'data MB':>10} {'E(per-byte) J':>14} {'E(active) J':>12}")

    try:
        for line in sys.stdin:
            if name_filter and name_filter not in line:
                continue
            parsed = parse_line(line)
            if parsed is None:
                continue
            sent, recv = parsed

            rate_Bps = (sent + recv) * KB

            # --- instantaneous power readings ---
            p_perbyte = rate_Bps * JOULES_PER_BYTE          # scales with rate
            p_active  = ACTIVE_POWER_W if rate_Bps > ACTIVE_THRESHOLD_BPS else 0.0

            # --- integrate over elapsed time (E = P x dt) ---
            now = time.time()
            dt = now - last_t
            last_t = now

            total_bytes  += rate_Bps * dt
            energy_pb_J  += p_perbyte * dt
            energy_act_J += p_active * dt
            if p_active > 0:
                active_time_s += dt

            print(f"{rate_Bps:12.1f} {p_perbyte:14.3e} {p_active:12.2f} "
                  f"{total_bytes/KB/KB:10.3f} {energy_pb_J:14.3e} {energy_act_J:12.3f}")
    except KeyboardInterrupt:
        pass

    print("\n--- session summary ---")
    print(f"total data            : {total_bytes/KB/KB:.2f} MB")
    print(f"active time           : {active_time_s:.1f} s")
    print(f"energy (per-byte)     : {energy_pb_J:.4e} J  "
          f"(at {JOULES_PER_BYTE:.1e} J/B)")
    print(f"energy (active-power) : {energy_act_J:.2f} J  "
          f"(at {ACTIVE_POWER_W} W while active)")
    # sanity check vs the assignment: 1 GB at full 1 Gb/s for 8 s at 1 W -> 8 J


if __name__ == "__main__":
    main()
