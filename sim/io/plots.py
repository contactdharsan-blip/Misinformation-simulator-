from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_adoption_curves(metrics: pd.DataFrame, out_dir: str | Path, strain_names: list | None = None, max_day: int | None = None) -> None:
    out_dir = Path(out_dir)
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Filter to max_day if specified
    if max_day is not None:
        metrics = metrics[metrics["day"] <= max_day].copy()
    
    for claim in sorted(metrics["claim"].unique()):
        subset = metrics[metrics["claim"] == claim]
        if strain_names and claim < len(strain_names):
            label = strain_names[claim]
            # Highlight mutations with different style
            if "_m" in label:
                ax.plot(subset["day"], subset["adoption_fraction"], label=label, linestyle="--", alpha=0.7)
            else:
                ax.plot(subset["day"], subset["adoption_fraction"], label=label, linewidth=2)
        else:
            ax.plot(subset["day"], subset["adoption_fraction"], label=f"claim {claim}")
    ax.set_title(f"Adoption Curves{' (up to day ' + str(max_day) + ')' if max_day else ''}")
    ax.set_xlabel("Day")
    ax.set_ylabel("Adoption Fraction")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / f"adoption_curves_day_{max_day if max_day else 'all'}.png", dpi=150)
    plt.close(fig)


def plot_polarization(metrics: pd.DataFrame, out_dir: str | Path, strain_names: list | None = None, max_day: int | None = None) -> None:
    out_dir = Path(out_dir)
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Filter to max_day if specified
    if max_day is not None:
        metrics = metrics[metrics["day"] <= max_day].copy()
    
    for claim in sorted(metrics["claim"].unique()):
        subset = metrics[metrics["claim"] == claim]
        if strain_names and claim < len(strain_names):
            label = strain_names[claim]
            if "_m" in label:
                ax.plot(subset["day"], subset["polarization"], label=label, linestyle="--", alpha=0.7)
            else:
                ax.plot(subset["day"], subset["polarization"], label=label, linewidth=2)
        else:
            ax.plot(subset["day"], subset["polarization"], label=f"claim {claim}")
    ax.set_title(f"Polarization Over Time{' (up to day ' + str(max_day) + ')' if max_day else ''}")
    ax.set_xlabel("Day")
    ax.set_ylabel("Polarization")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / f"polarization_day_{max_day if max_day else 'all'}.png", dpi=150)
    plt.close(fig)


def plot_belief_histogram(beliefs: pd.DataFrame, out_dir: str | Path, day: int) -> None:
    out_dir = Path(out_dir)
    fig, ax = plt.subplots(figsize=(8, 4))
    claim_cols = [c for c in beliefs.columns if c.startswith("claim_")]
    for col in claim_cols:
        ax.hist(beliefs[col], bins=20, alpha=0.4, label=col)
    ax.set_title(f"Belief Distributions (Day {day})")
    ax.set_xlabel("Belief")
    ax.set_ylabel("Count")
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / f"belief_hist_day_{day}.png", dpi=150)
    plt.close(fig)


def plot_adoption_by_ethnicity(
    snapshots: pd.DataFrame,
    ethnicity: pd.Series,
    adoption_threshold: float,
    out_dir: str | Path,
    target_day: int,
    strain_names: list | None = None,
) -> None:
    """Plot adoption rates by ethnicity group over time (line graph)."""
    out_dir = Path(out_dir)
    
    if snapshots.empty:
        return
    
    # Create ethnicity Series indexed by agent_id
    ethnicity_df = pd.DataFrame({
        "agent_id": range(len(ethnicity)),
        "ethnicity": ethnicity.values
    })
    
    # Merge ethnicity with snapshots
    snapshots = snapshots.copy()
    snapshots = snapshots.merge(ethnicity_df, on="agent_id", how="left")
    
    # Filter to target_day
    snapshots = snapshots[snapshots["day"] <= target_day].copy()
    
    # Calculate adoption by ethnicity over time for each claim
    claim_cols = [c for c in snapshots.columns if c.startswith("claim_")]
    ethnicity_groups = sorted(snapshots["ethnicity"].dropna().unique())
    days = sorted(snapshots["day"].unique())
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for claim_col in claim_cols:
        claim_num = int(claim_col.split("_")[1])
        label = strain_names[claim_num] if strain_names and claim_num < len(strain_names) else claim_col
        
        for eth in ethnicity_groups:
            eth_mask = snapshots["ethnicity"] == eth
            eth_data = snapshots[eth_mask]
            
            adoption_over_time = []
            for day in days:
                day_data = eth_data[eth_data["day"] == day]
                if len(day_data) > 0:
                    adoptions = (day_data[claim_col] >= adoption_threshold).sum()
                    total = len(day_data)
                    adoption_over_time.append(adoptions / total if total > 0 else 0.0)
                else:
                    adoption_over_time.append(0.0)
            
            # Plot line for this ethnicity and claim combination
            eth_label = f"{label} - {eth}"
            ax.plot(days, adoption_over_time, label=eth_label, alpha=0.7, linewidth=1.5)
    
    ax.set_xlabel("Day")
    ax.set_ylabel("Adoption Rate")
    ax.set_title(f"Adoption Rates by Ethnicity Over Time (up to day {target_day})")
    ax.legend(loc="upper left", fontsize=7, ncol=2)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1)
    fig.tight_layout()
    fig.savefig(out_dir / f"adoption_by_ethnicity_day_{target_day}.png", dpi=150)
    plt.close(fig)


def plot_adoption_by_age(
    snapshots: pd.DataFrame,
    ages: pd.Series,
    adoption_threshold: float,
    out_dir: str | Path,
    target_day: int,
    strain_names: list | None = None,
) -> None:
    """Plot adoption rates by age group over time (line graph)."""
    out_dir = Path(out_dir)
    
    if snapshots.empty:
        return
    
    # Create age DataFrame indexed by agent_id
    age_df = pd.DataFrame({
        "agent_id": range(len(ages)),
        "age": ages.values
    })
    
    # Define age groups
    def age_group(age):
        if age < 18:
            return "0-17"
        elif age < 35:
            return "18-34"
        elif age < 55:
            return "35-54"
        elif age < 75:
            return "55-74"
        else:
            return "75+"
    
    age_df["age_group"] = age_df["age"].apply(age_group)
    
    # Merge age with snapshots
    snapshots = snapshots.copy()
    snapshots = snapshots.merge(age_df, on="agent_id", how="left")
    
    # Filter to target_day
    snapshots = snapshots[snapshots["day"] <= target_day].copy()
    
    age_groups = ["0-17", "18-34", "35-54", "55-74", "75+"]
    
    # Calculate adoption by age group over time for each claim
    claim_cols = [c for c in snapshots.columns if c.startswith("claim_")]
    days = sorted(snapshots["day"].unique())
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for claim_col in claim_cols:
        claim_num = int(claim_col.split("_")[1])
        label = strain_names[claim_num] if strain_names and claim_num < len(strain_names) else claim_col
        
        for age_grp in age_groups:
            age_mask = snapshots["age_group"] == age_grp
            age_data = snapshots[age_mask]
            
            adoption_over_time = []
            for day in days:
                day_data = age_data[age_data["day"] == day]
                if len(day_data) > 0:
                    adoptions = (day_data[claim_col] >= adoption_threshold).sum()
                    total = len(day_data)
                    adoption_over_time.append(adoptions / total if total > 0 else 0.0)
                else:
                    adoption_over_time.append(0.0)
            
            # Plot line for this age group and claim combination
            age_label = f"{label} - {age_grp}"
            ax.plot(days, adoption_over_time, label=age_label, alpha=0.7, linewidth=1.5)
    
    ax.set_xlabel("Day")
    ax.set_ylabel("Adoption Rate")
    ax.set_title(f"Adoption Rates by Age Group Over Time (up to day {target_day})")
    ax.legend(loc="upper left", fontsize=7, ncol=2)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1)
    fig.tight_layout()
    fig.savefig(out_dir / f"adoption_by_age_day_{target_day}.png", dpi=150)
    plt.close(fig)
