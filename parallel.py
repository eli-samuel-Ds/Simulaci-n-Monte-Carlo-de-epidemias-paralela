import numpy as np
import time
import argparse
import os
from multiprocessing import Pool, cpu_count

SUS = np.uint8(0)
INF = np.uint8(1)
REC = np.uint8(2)
DEAD = np.uint8(3)

def get_block_indices(H, W, n_blocks_y, n_blocks_x):

    ys = np.linspace(0, H, n_blocks_y+1, dtype=int)
    xs = np.linspace(0, W, n_blocks_x+1, dtype=int)
    blocks = []
    for by in range(n_blocks_y):
        for bx in range(n_blocks_x):
            i0, i1 = ys[by], ys[by+1]
            j0, j1 = xs[bx], xs[bx+1]
            blocks.append((i0, i1, j0, j1))
    return blocks

def extract_block_with_ghosts(grid, i0, i1, j0, j1):
    H, W = grid.shape
    row_idx = np.arange(i0 - 1, i1 + 1, dtype=int)
    col_idx = np.arange(j0 - 1, j1 + 1, dtype=int)
    row_idx_mod = row_idx % H
    col_idx_mod = col_idx % W
    block = grid[np.ix_(row_idx_mod, col_idx_mod)]
    return block

def worker_update(args):

    (i0,i1,j0,j1, block, rand_inf_block, rand_rec_block, rand_dead_block, beta, gamma, mu) = args
    # interior coords in block
    Hb, Wb = block.shape
    interior = block[1: Hb-1, 1: Wb-1].copy()
    infected_mask = (block == INF)

    b_inf_bool = (block == INF).astype(np.uint8)
    up    = b_inf_bool[:-2, 1:-1]
    down  = b_inf_bool[2:, 1:-1]
    left  = b_inf_bool[1:-1, :-2]
    right = b_inf_bool[1:-1, 2:]
    ul = b_inf_bool[:-2, :-2]
    ur = b_inf_bool[:-2, 2:]
    dl = b_inf_bool[2:, :-2]
    dr = b_inf_bool[2:, 2:]
    neigh_inf = up + down + left + right + ul + ur + dl + dr

    sus_mask = (interior == SUS)
    p_inf = 1.0 - np.power(1.0 - beta, neigh_inf)
    new_infections = sus_mask & (rand_inf_block < p_inf)
    new_inf_count = int(np.count_nonzero(new_infections))
    interior[new_infections] = INF

    inf_cells = (interior == INF)
    deaths = inf_cells & (rand_dead_block < mu)
    interior[deaths] = DEAD

    inf_after_death = (interior == INF)
    recov = inf_after_death & (rand_rec_block < gamma)
    interior[recov] = REC

    local_infected = int(np.count_nonzero(interior == INF))
    local_stats = {"new_inf": new_inf_count, "infected": local_infected}
    return (i0, i1, j0, j1, interior, local_stats)

def run_parallel(H=200, W=200, days=60,
                 beta=0.3, gamma=0.05, mu=0.005,
                 init_infected_frac=0.001, base_seed=42,
                 n_workers=4, blocks_y=2, blocks_x=2,
                 save_snapshots=True, snapshot_dir="snapshots_par",
                 snapshot_every=1, verbose=True):

    np.random.seed(base_seed)
    grid = np.full((H, W), SUS, dtype=np.uint8)
    init_mask = np.random.rand(H, W) < init_infected_frac
    grid[init_mask] = INF

    blocks = get_block_indices(H, W, blocks_y, blocks_x)

    stats = {"daily_new_infections": [], "daily_infected": [], "daily_Rt": []}
    snapshots = []

    pool = Pool(processes=n_workers)
    t0 = time.perf_counter()
    for day in range(days):
        rng = np.random.RandomState(base_seed + day)
        rand_inf = rng.rand(H, W).astype(np.float32)
        rand_rec = rng.rand(H, W).astype(np.float32)
        rand_dead = rng.rand(H, W).astype(np.float32)

        tasks = []
        for (i0,i1,j0,j1) in blocks:
            block = extract_block_with_ghosts(grid, i0, i1, j0, j1)
            rand_inf_block = rand_inf[i0:i1, j0:j1]
            rand_rec_block = rand_rec[i0:i1, j0:j1]
            rand_dead_block = rand_dead[i0:i1, j0:j1]
            tasks.append((i0,i1,j0,j1, block, rand_inf_block, rand_rec_block, rand_dead_block, beta, gamma, mu))

        results = pool.map(worker_update, tasks)

        total_new_inf = 0
        for (i0,i1,j0,j1, interior, local_stats) in results:
            grid[i0:i1, j0:j1] = interior
            total_new_inf += local_stats["new_inf"]

        current_infected = int(np.count_nonzero(grid == INF))
        stats["daily_new_infections"].append(total_new_inf)
        stats["daily_infected"].append(current_infected)
        prev_infected = stats["daily_infected"][-2] if day > 0 else max(1, current_infected)
        Rt = total_new_inf / max(1, prev_infected)
        stats["daily_Rt"].append(Rt)

        if save_snapshots and (day % snapshot_every == 0):
            snapshots.append(grid.copy())

        if verbose and (day % max(1, days // 10) == 0):
            print(f"[PAR] day {day:3d}/{days} new_inf={total_new_inf} I={current_infected} Rt={Rt:.3f}")

    total_time = time.perf_counter() - t0
    pool.close()
    pool.join()

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
        print(f"[PAR] finished in {total_time:.3f} s with {n_workers} workers")
    return result

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--H", type=int, default=200)
    p.add_argument("--W", type=int, default=200)
    p.add_argument("--days", type=int, default=60)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--by", type=int, default=2)
    p.add_argument("--bx", type=int, default=2)
    p.add_argument("--out", default="snapshots_par")
    p.add_argument("--beta", type=float, default=0.3)
    p.add_argument("--gamma", type=float, default=0.05)
    p.add_argument("--mu", type=float, default=0.005)
    args = p.parse_args()

    run_parallel(H=args.H, W=args.W, days=args.days, base_seed=args.seed,
                 n_workers=args.workers, blocks_y=args.by, blocks_x=args.bx,
                 beta=args.beta, gamma=args.gamma, mu=args.mu,
                 save_snapshots=True, snapshot_dir=args.out, snapshot_every=1)
