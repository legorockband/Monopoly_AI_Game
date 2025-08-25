#!/usr/bin/env python3
import argparse
import glob
import os
import math
from typing import Dict, List, Tuple

import pandas as pd
import matplotlib.pyplot as plt

# --- Utilities --------------------------------------------------------------
def ensure_dir(p: str):
    os.makedirs(p, exist_ok=True)

def normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    # Lowercase + strip
    mapping = {c: c.strip().lower() for c in df.columns}
    return df.rename(columns=mapping)

def has_cols(df: pd.DataFrame, cols: List[str]) -> bool:
    return all(c in df.columns for c in cols)

def wilson_ci(k: int, n: int, z: float = 1.96) -> Tuple[float, float]:
    """Wilson 95% CI for binomial proportion."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z**2 / n
    center = (p + z*z/(2*n)) / denom
    half = (z * math.sqrt((p*(1-p) + z*z/(4*n)) / n)) / denom
    return (max(0.0, center - half), min(1.0, center + half))

def save_txt(path: str, text: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

# --- Plotters ---------------------------------------------------------------
def plot_win_counts(df: pd.DataFrame, out_png: str, title: str):
    winner_col = "winner"
    if winner_col not in df.columns:
        return False
    counts = df[winner_col].value_counts().sort_index()
    plt.figure(figsize=(8,5))
    counts.plot(kind="bar")
    plt.title(title)
    plt.xlabel("Winner")
    plt.ylabel("Number of Wins")
    plt.tight_layout()
    plt.savefig(out_png, dpi=150)
    plt.close()
    return True

def plot_seat_winrate(df: pd.DataFrame, out_png: str, title: str):
    if not has_cols(df, ["seat", "winner"]):
        return False
    # Seat should be 0-based seat index; convert to int safely
    seat_series = pd.to_numeric(df["seat"], errors="coerce").dropna().astype(int)
    df2 = df.loc[seat_series.index].copy()
    df2["seat"] = seat_series.values

    # Compute total games by seat and wins by seat (where winner's seat matches)
    # If df records only winner row once per game, we use seat of winner directly.
    seat_counts = df2["seat"].value_counts().sort_index()
    # Estimate wins by seat = count of rows where seat equals winner seat
    wins_by_seat = seat_counts  # same as counts because each row is the winner
    total_by_seat = seat_counts.sum() / max(len(seat_counts), 1)  # Not quite right without per-game seat rotation
    # More directly: winrate per seat is wins_by_seat / total games if seat is uniformly rotated.
    total_games = len(df2)
    rates = {s: wins_by_seat.get(s, 0) / total_games for s in seat_counts.index}

    # Plot
    xs = list(rates.keys())
    ys = [rates[s] for s in xs]
    plt.figure(figsize=(8,5))
    plt.bar([str(x) for x in xs], ys)
    plt.ylim(0, 1)
    plt.title(title)
    plt.xlabel("Seat index")
    plt.ylabel("Win rate")
    # Annotate with Wilson CI
    for i, s in enumerate(xs):
        lo, hi = wilson_ci(wins_by_seat.get(s, 0), total_games)
        plt.text(i, ys[i] + 0.01, f"{ys[i]*100:.1f}%\n[{lo*100:.1f},{hi*100:.1f}]%", ha="center", va="bottom", fontsize=8)
    plt.tight_layout()
    plt.savefig(out_png, dpi=150)
    plt.close()
    return True

def plot_turns_hist(df: pd.DataFrame, out_png: str, title: str):
    if "turns" not in df.columns:
        return False
    turns = pd.to_numeric(df["turns"], errors="coerce").dropna()
    if turns.empty:
        return False
    plt.figure(figsize=(8,5))
    plt.hist(turns, bins=20)
    plt.title(title)
    plt.xlabel("Turns to win (or end)")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(out_png, dpi=150)
    plt.close()
    return True

# --- Per-file processing ----------------------------------------------------
def summarize_file(df: pd.DataFrame) -> Dict[str, str]:
    out = {}
    n = len(df)
    out["n_rows"] = str(n)
    if "winner" in df.columns:
        counts = df["winner"].value_counts()
        lines = []
        for k, v in counts.items():
            lo, hi = wilson_ci(v, n)
            lines.append(f"{k}: {v} / {n}  ({v/n:.1%})  95% CI [{lo:.1%}, {hi:.1%}]")
        out["winners"] = "\n".join(lines)
    if "turns" in df.columns:
        turns = pd.to_numeric(df["turns"], errors="coerce").dropna()
        if not turns.empty:
            out["turns"] = f"Median {turns.median():.1f}, IQR [{turns.quantile(0.25):.1f}, {turns.quantile(0.75):.1f}]"
    return out

def process_file(csv_path: str, out_dir: str):
    base = os.path.splitext(os.path.basename(csv_path))[0]
    file_out = os.path.join(out_dir, base)
    ensure_dir(file_out)

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        save_txt(os.path.join(file_out, "ERROR.txt"), f"Failed to read CSV: {e}")
        return

    df = normalize_cols(df)

    # Plots
    any_plot = False
    if plot_win_counts(df, os.path.join(file_out, "win_counts.png"), f"Win Counts – {base}"):
        any_plot = True
    if plot_seat_winrate(df, os.path.join(file_out, "seat_winrate.png"), f"Win Rate by Seat – {base}"):
        any_plot = True
    if plot_turns_hist(df, os.path.join(file_out, "turns_hist.png"), f"Turns Distribution – {base}"):
        any_plot = True

    # Summary
    summ = summarize_file(df)
    lines = [f"File: {csv_path}"]
    for k in ["n_rows", "winners", "turns"]:
        if k in summ:
            lines.append(f"{k}:")
            lines.append(summ[k])
            lines.append("")
    if not any_plot:
        lines.append("No applicable columns found for plotting. Expected at least one of: winner, seat, turns.")
    save_txt(os.path.join(file_out, "summary.txt"), "\n".join(lines))

# --- Aggregate (optional) ---------------------------------------------------
def aggregate(files: List[str], out_dir: str):
    frames = []
    for f in files:
        try:
            df = pd.read_csv(f)
            df = normalize_cols(df)
            frames.append(df)
        except Exception:
            pass
    if not frames:
        return
    all_df = pd.concat(frames, ignore_index=True)
    agg_dir = os.path.join(out_dir, "_aggregate_all")
    ensure_dir(agg_dir)

    # Reuse plots
    plot_win_counts(all_df, os.path.join(agg_dir, "win_counts.png"), "Win Counts – ALL FILES")
    plot_seat_winrate(all_df, os.path.join(agg_dir, "seat_winrate.png"), "Win Rate by Seat – ALL FILES")
    plot_turns_hist(all_df, os.path.join(agg_dir, "turns_hist.png"), "Turns Distribution – ALL FILES")

    summ = summarize_file(all_df)
    lines = ["Aggregate of all input CSVs:"]
    for k in ["n_rows", "winners", "turns"]:
        if k in summ:
            lines.append(f"{k}:")
            lines.append(summ[k])
            lines.append("")
    save_txt(os.path.join(agg_dir, "summary.txt"), "\n".join(lines))

# --- Main -------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Make graphs from Monopoly AI simulation CSVs.")
    ap.add_argument("--inputs", nargs="+", required=True, help="CSV file paths or globs. Example: results_*.csv")
    ap.add_argument("--out", default="graphs_out", help="Output directory")
    ap.add_argument("--no-aggregate", action="store_true", help="Skip aggregate ALL FILES report")
    args = ap.parse_args()

    # Expand globs
    files = []
    for pat in args.inputs:
        matched = glob.glob(pat)
        if matched:
            files.extend(matched)
        else:
            # If it's a direct path (maybe no wildcard) include it
            if os.path.exists(pat):
                files.append(pat)

    if not files:
        print("No input CSV files found for the given patterns.")
        return

    ensure_dir(args.out)

    for f in files:
        print(f"Processing {f} ...")
        process_file(f, args.out)

    if not args.no_aggregate:
        aggregate(files, args.out)

    print(f"Done. Outputs in: {args.out}")

if __name__ == "__main__":
    main()
