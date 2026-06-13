#!/usr/bin/env python3
"""
net_energy.py — CUMULATIVE ENERGY reading.

Run with nethogs in TOTAL mode (-v 3), where the two numbers
on each line are SENT and RECEIVED *cumulative totals* in MB:

    sudo nethogs -v 3 -t | python3 net_energy.py firefox

Because nethogs already integrates the traffic for us in -v 3 mode,
no time integration is needed here: energy is simply

    E [J] = total bytes x energy-per-byte [J/B]
"""

import sys

# ---------- model parameters (from the assignment) ----------
LINK_RATE_BPS  = 125e6                          # 1 Gb/s link = 125e6 bytes/s
ACTIVE_POWER_W = 1.0                            # port draws 1.0 W when active (0.3 W lower bound)
JOULES_PER_BYTE = ACTIVE_POWER_W / LINK_RATE_BPS  # 8e-9 J per byte (8 nJ/B)

MB = 1024 * 1024                                # nethogs -v 3 reports MB


def main():
    # optional command-line argument: filter lines by program name (like grep)
    name_filter = sys.argv[1] if len(sys.argv) > 1 else ""

    # remember the latest reading so we can print a summary at the end
    last_sent_MB = last_recv_MB = 0.0

    # header for the output table
    print(f"{'sent MB':>10} {'recv MB':>10} {'total MB':>10} {'energy J':>12}")

    # read nethogs output line by line as it streams in
    for line in sys.stdin:
        # skip lines that don't mention the app we care about
        if name_filter and name_filter not in line:
            continue

        parts = line.split()
        if len(parts) < 3:
            continue                      # not a data line

        try:
            sent_MB = float(parts[-2])    # second-to-last field = SENT total (MB)
            recv_MB = float(parts[-1])    # last field           = RECEIVED total (MB)
        except ValueError:
            continue                      # fields weren't numbers -> skip

        last_sent_MB, last_recv_MB = sent_MB, recv_MB

        # total cumulative bytes (both directions)
        total_bytes = (sent_MB + recv_MB) * MB

        # ENERGY = cumulative bytes x energy-per-byte   (analogous to J = W x s)
        energy_J = total_bytes * JOULES_PER_BYTE

        print(f"{sent_MB:10.3f} {recv_MB:10.3f} "
              f"{sent_MB + recv_MB:10.3f} {energy_J:12.4e}")

    # ---------- session summary (printed after the stream ends) ----------
    total_MB = last_sent_MB + last_recv_MB
    print("\n--- session summary ---")
    print(f"total data   : {total_MB:.2f} MB")
    print(f"total energy : {total_MB * MB * JOULES_PER_BYTE:.4e} J "
          f"(at {JOULES_PER_BYTE:.1e} J/B)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass                              # Ctrl-C ends nethogs and the pipe
