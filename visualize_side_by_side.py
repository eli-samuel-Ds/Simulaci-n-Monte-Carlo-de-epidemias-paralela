import numpy as np
import matplotlib.pyplot as plt
import imageio
import os
import argparse

def load_snapshots(folder):
    files = sorted([f for f in os.listdir(folder) if f.endswith(".npy")])
    snaps = [np.load(os.path.join(folder, f)) for f in files]
    return snaps

def downsample(img, max_side=400):
    H, W = img.shape
    scale = max(1, max(H, W) // max_side)
    if scale == 1:
        return img
    return img[::scale, ::scale]

def make_animation(seq_folder, par_folder, out_file="animations/side_by_side.gif", fps=5):
    seq_snaps = load_snapshots(seq_folder)
    par_snaps = load_snapshots(par_folder)
    n = min(len(seq_snaps), len(par_snaps))
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    frames = []
    for i in range(n):
        s = downsample(seq_snaps[i])
        p = downsample(par_snaps[i])
        H, W = s.shape
        canvas = np.zeros((H, W*2, 3), dtype=np.uint8) + 255
        def to_rgb(mat):
            rgb = np.zeros((mat.shape[0], mat.shape[1], 3), dtype=np.uint8) + 255
            rgb[mat==1] = [255,0,0]   # infected red
            rgb[mat==2] = [0,180,0]   # recovered green
            rgb[mat==3] = [0,0,0]     # dead black
            return rgb
        canvas[:, :W, :] = to_rgb(s)
        canvas[:, W:, :] = to_rgb(p)
        frames.append(canvas)
    imageio.mimsave(out_file, frames, fps=fps)
    out_mp4 = out_file.replace(".gif", ".mp4")
    imageio.mimsave(out_mp4, frames, fps=fps, codec="libx264")
    print(f"Saved {out_file} and {out_mp4}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--seq", default="snapshots_seq")
    p.add_argument("--par", default="snapshots_par_w4")
    p.add_argument("--out", default="animations/side_by_side.gif")
    args = p.parse_args()
    make_animation(args.seq, args.par, out_file=args.out, fps=6)
