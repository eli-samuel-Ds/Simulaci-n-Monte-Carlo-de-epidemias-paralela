import time
import argparse
import csv
import numpy as np
import matplotlib.pyplot as plt
from sequential import run_sequential
from parallel import run_parallel
import os

def run_and_time(H, W, days, seed, beta, gamma, mu, n_workers, blocks_y, blocks_x, quick=False):
    print(f"Running parallel (workers={n_workers}) ...")
    par_res = run_parallel(H=H, W=W, days=days, beta=beta, gamma=gamma, mu=mu,
                           init_infected_frac=0.001, base_seed=seed,
                           n_workers=n_workers, blocks_y=blocks_y, blocks_x=blocks_x,
                           save_snapshots=not quick, snapshot_dir=f"snapshots_par_w{n_workers}", snapshot_every=1, verbose=False)
    t_par = par_res["time_sec"]
    print(f"Parallel time (w={n_workers}): {t_par:.3f}s")

    print("Running sequential ...")
    seq_res = run_sequential(H=H, W=W, days=days, beta=beta, gamma=gamma, mu=mu,
                             init_infected_frac=0.001, base_seed=seed,
                             save_snapshots=not quick, snapshot_dir="snapshots_seq", snapshot_every=1, verbose=False)
    t_seq = seq_res["time_sec"]
    print(f"Sequential time: {t_seq:.3f}s")
    return t_seq, t_par

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--H", type=int, default=200)
    p.add_argument("--W", type=int, default=200)
    p.add_argument("--days", type=int, default=60)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", default="speedup.csv")
    p.add_argument("--workers", nargs="+", type=int, default=[1,2,4,8])
    p.add_argument("--beta", type=float, default=0.3)
    p.add_argument("--gamma", type=float, default=0.05)
    p.add_argument("--mu", type=float, default=0.005)
    p.add_argument("--quick", action="store_true", help="No save snapshots (faster, less IO)")
    args = p.parse_args()

    rows = []
    print("Measuring baseline sequential time...")
    t_seq_baseline, _ = run_and_time(H=args.H, W=args.W, days=args.days, seed=args.seed,
                                     beta=args.beta, gamma=args.gamma, mu=args.mu,
                                     n_workers=1, blocks_y=1, blocks_x=1, quick=args.quick)

    for w in args.workers:
        by = min(w, int(np.sqrt(w)) if w>1 else 1)
        bx = max(1, w // by)
        t_seq, t_par = run_and_time(H=args.H, W=args.W, days=args.days, seed=args.seed,
                                    beta=args.beta, gamma=args.gamma, mu=args.mu,
                                    n_workers=w, blocks_y=by, blocks_x=bx, quick=args.quick)
        speedup = t_seq / t_par if t_par > 0 else np.nan
        rows.append({"workers": w, "time_sec": t_par, "seq_time_sec": t_seq, "speedup": speedup})

    os.makedirs("results", exist_ok=True)
    out_csv = os.path.join("results", args.out)
    with open(out_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["workers", "seq_time_sec", "time_sec", "speedup"])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print(f"Wrote {out_csv}")

    # plot speedup
    ws = [r["workers"] for r in rows]
    sp = [r["speedup"] for r in rows]
    seqs = [r["seq_time_sec"] for r in rows]
    pars = [r["time_sec"] for r in rows]

    plt.figure(figsize=(8,5))
    plt.plot(ws, sp, marker="o")
    plt.xlabel("Workers / Cores")
    plt.ylabel("Speed-up (seq_time / par_time)")
    plt.title("Strong scaling")
    plt.grid(True)
    plt.savefig("results/speedup.png", dpi=150)
    print("Saved results/speedup.png")

if __name__ == "__main__":
    main()
