# main.py — ejecuta parallel.py, sequential.py y run_experiments.py
import sys
import subprocess
from pathlib import Path
import numpy as np

here = Path(__file__).resolve().parent

# ==========================
#   DEMO PEQUEÑO 200x200
# ==========================

parallel_script = here / "parallel.py"
sequential_script = here / "sequential.py"
experiments_script = here / "run_experiments.py"

# ----- Ejecutar parallel.py -----
cmd_parallel = [
    sys.executable,
    str(parallel_script),
    "--H", "200", "--W", "200",
    "--days", "60",
    "--seed", "42",
    "--workers", "4",
    "--by", "2", "--bx", "2",
    "--out", "snapshots_par_w4"
]

print("Ejecutando PAR:", " ".join(cmd_parallel))
subprocess.run(cmd_parallel, check=True)

# ----- Ejecutar sequential.py -----
cmd_seq = [
    sys.executable,
    str(sequential_script),
    "--H", "200", "--W", "200",
    "--days", "60",
    "--seed", "42",
    "--out", "snapshots_seq"
]

print("Ejecutando SEQ:", " ".join(cmd_seq))
subprocess.run(cmd_seq, check=True)

# ----- Comparación de un snapshot -----
print("Comparando snapshots...")
seq = np.load("snapshots_seq/snap_0000.npy")
par = np.load("snapshots_par_w4/snap_0000.npy")
print("¿Son iguales?:", (seq == par).all())

# ==========================
#   SIMULACIONES GRANDES
# ==========================

# --- Secuencial 1000×1000 ---
cmd_seq_big = [
    sys.executable,
    str(sequential_script),
    "--H", "1000", "--W", "1000",
    "--days", "365",
    "--seed", "42",
    "--out", "snapshots_seq_big"
]

print("Ejecutando SEQ GRANDE:", " ".join(cmd_seq_big))
subprocess.run(cmd_seq_big, check=True)

# --- Paralelo 1000×1000 con 8 workers ---
cmd_par_big = [
    sys.executable,
    str(parallel_script),
    "--H", "1000", "--W", "1000",
    "--days", "365",
    "--seed", "42",
    "--workers", "8",
    "--by", "4",
    "--bx", "2",
    "--out", "snapshots_par_w8"
]

print("Ejecutando PAR GRANDE:", " ".join(cmd_par_big))
subprocess.run(cmd_par_big, check=True)

# ==========================
#   EXPERIMENTOS AUTOMÁTICOS
# ==========================

# --- Experimentos pequeños ---
cmd_exp_small = [
    sys.executable,
    str(experiments_script),
    "--H", "200", "--W", "200",
    "--days", "60",
    "--seed", "42",
    "--workers", "1", "2", "4", "8",
    "--quick"
]

print("Ejecutando EXP SMALL:", " ".join(cmd_exp_small))
subprocess.run(cmd_exp_small, check=True)

# --- Experimentos grandes ---
cmd_exp_big = [
    sys.executable,
    str(experiments_script),
    "--H", "1000", "--W", "1000",
    "--days", "365",
    "--seed", "42",
    "--workers", "1", "2", "4", "8"
]

print("Ejecutando EXP BIG:", " ".join(cmd_exp_big))
subprocess.run(cmd_exp_big, check=True)