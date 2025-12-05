import numpy as np
import time
import argparse
import os

SUS = np.uint8(0)
INF = np.uint8(1)
REC = np.uint8(2)
DEAD = np.uint8(3)

def neighbor_infected_count(grid):
    g = grid.astype(np.uint8)
    up    = np.roll(g, -1, axis=0)
    down  = np.roll(g, 1, axis=0)
    left  = np.roll(g, -1, axis=1)
    right = np.roll(g, 1, axis=1)
    ul = np.roll(up, -1, axis=1)
    ur = np.roll(up, 1, axis=1)
    dl = np.roll(down, -1, axis=1)
    dr = np.roll(down, 1, axis=1)
    return up + down + left + right + ul + ur + dl + dr

def run_sequential(H=200, W=200, days=60,
                   beta=0.3, gamma=0.05, mu=0.005,
                   init_infected_frac=0.001,
                   base_seed=42,
                   save_snapshots=True, snapshot_dir="snapshots_seq",
                   snapshot_every=1, verbose=True):
    np.random.seed(base_seed)
    grid = np.full((H, W), SUS, dtype=np.uint8)
    init_mask = np.random.rand(H, W) < init_infected_frac
    grid[init_mask] = INF

    stats = {"daily_new_infections": [], "daily_infected": [], "daily_Rt": []}
    snapshots = []

    t0 = time.perf_counter()
    for day in range(days):
        rng = np.random.RandomState(base_seed + day)
        rand_inf = rng.rand(H, W).astype(np.float32)
        rand_rec = rng.rand(H, W).astype(np.float32)
        rand_dead = rng.rand(H, W).astype(np.float32)

        infected_mask = (grid == INF)
        sus_mask = (grid == SUS)

        neigh_inf = neighbor_infected_count(infected_mask)
        p_inf = 1.0 - np.power(1.0 - beta, neigh_inf)

        new_infections = (sus_mask) & (rand_inf < p_inf)
        new_inf_count = int(np.count_nonzero(new_infections))
        grid[new_infections] = INF

        deaths = infected_mask & (rand_dead < mu)
        grid[deaths] = DEAD

        infected_mask_after_death = (grid == INF)
        recov = infected_mask_after_death & (rand_rec < gamma)
        grid[recov] = REC

        current_infected = int(np.count_nonzero(grid == INF))
        stats["daily_new_infections"].append(new_inf_count)
        stats["daily_infected"].append(current_infected)
        prev_infected = stats["daily_infected"][-2] if day > 0 else max(1, current_infected)
        Rt = new_inf_count / max(1, prev_infected)
        stats["daily_Rt"].append(Rt)

        if save_snapshots and (day % snapshot_every == 0):
            snapshots.append(grid.copy())

        if verbose and (day % max(1, days // 10) == 0):
            print(f"[SEQ] day {day:3d}/{days} new_inf={new_inf_count} I={current_infected} Rt={Rt:.3f}")

    total_time = time.perf_counter() - t0
    if save_snapshots:
        os.makedirs(snapshot_dir, exist_ok=True)
        for i, snap in enumerate(snapshots):
            np.save(os.path.join(snapshot_dir, f"snap_{i:04d}.npy"), snap)

    result = {
        "grid_final": grid,
        "stats": stats,
        "time_sec": total_time,
        "snapshots": snapshots
    }
    if verbose:
        print(f"[SEQ] finished in {total_time:.3f} s")
    return result

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--H", type=int, default=200)
    p.add_argument("--W", type=int, default=200)
    p.add_argument("--days", type=int, default=60)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", default="snapshots_seq")
    p.add_argument("--beta", type=float, default=0.3)
    p.add_argument("--gamma", type=float, default=0.05)
    p.add_argument("--mu", type=float, default=0.005)
    args = p.parse_args()
    run_sequential(H=args.H, W=args.W, days=args.days, base_seed=args.seed,
                   beta=args.beta, gamma=args.gamma, mu=args.mu,
                   save_snapshots=True, snapshot_dir=args.out, snapshot_every=1)
