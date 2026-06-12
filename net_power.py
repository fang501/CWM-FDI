#!/usr/bin/env python3
"""
net_power.py — INSTANTANEOUS POWER reading.

Run with nethogs in DEFAULT mode (-v 0), where the two numbers
on each line are SENT and RECEIVED *speeds* in KB/s:

    sudo nethogs -t | python3 net_power.py firefox
"""

import sys

# ---------- model parameters (from the assignment) ----------
LINK_RATE_BPS  = 125e6                          # 1 Gb/s link = 125e6 bytes/s
ACTIVE_POWER_W = 1.0                            # port draws 1.0 W when active (0.3 W lower bound)
JOULES_PER_BYTE = ACTIVE_POWER_W / LINK_RATE_BPS  # 8e-9 J per byte (8 nJ/B)

KB = 1024                                       # nethogs reports KB/s


def main():
    # optional command-line argument: filter lines by program name (like grep)
    name_filter = sys.argv[1] if len(sys.argv) > 1 else ""

    # header for the output table
    print(f"{'sent KB/s':>10} {'recv KB/s':>10} {'rate B/s':>12} {'power W':>12}")

    # read nethogs output line by line as it streams in
    for line in sys.stdin:
        # skip lines that don't mention the app we care about
        if name_filter and name_filter not in line:
            continue

        parts = line.split()
        if len(parts) < 3:
            continue                      # not a data line (header, blank, etc.)

        try:
            sent = float(parts[-2])       # second-to-last field = SENT  (KB/s)
            recv = float(parts[-1])       # last field           = RECEIVED (KB/s)
        except ValueError:
            continue                      # fields weren't numbers -> skip

        # total instantaneous byte rate, converted KB/s -> bytes/s
        rate_Bps = (sent + recv) * KB

        # POWER = byte rate x energy-per-byte   (analogous to W = J/s)
        power_W = rate_Bps * JOULES_PER_BYTE

        print(f"{sent:10.3f} {recv:10.3f} {rate_Bps:12.1f} {power_W:12.3e}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass                              # clean exit on Ctrl-C
