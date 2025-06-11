import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.patches import Patch

legend_handles = [
    Patch(facecolor='skyblue', label='ObjectType'),
    Patch(facecolor='orchid', label='Unique Element')
]
plt.legend(handles=legend_handles, loc='upper right', fontsize=7, frameon=False)


def plot_indicators(csv_path, output_dir, database_config):

    # Set indicator list based on database
    if database_config.lower() == "kbob":
        indicators = [
            "Global Warming Potential Total [kgCO2-eqv]",
            "Biogenic Carbon [kg C]",
            "UBP (Total)",
            "Total Renewable Primary Energy [kWh oil-eq]",
            "Total Non-Renewable Primary Energy [kWh oil-eq]",
        ]
    else:
        indicators = [
            "GWPbiogenic",
            "GWPfossil",
            "GWPtotal",
            "GWPtotal (A1-A3)",
            "GWPtotal (A4)",
            "GWPtotal (A5)",
            "GWPtotal (C1)",
            "GWPtotal (C2)",
            "GWPtotal (C3)",
            "GWPtotal (C4)"
        ]

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(csv_path)

    df = pd.read_csv(csv_path, na_values=["not matched", "not available", ""])

    for indicator in indicators:
        min_col = f"{indicator} (min)"
        mean_col = f"{indicator} (mean)"
        max_col = f"{indicator} (max)"

        if not all(col in df.columns for col in [min_col, mean_col, max_col]):
            print(f"Skipping {indicator}: columns missing.")
            continue

        # Convert to numeric safely
        for col in [min_col, mean_col, max_col]:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Filter rows where both min and max are missing or zero
        mask = ~((df[min_col].fillna(0) == 0) & (df[max_col].fillna(0) == 0))
        if "Compiled" in df.columns:    
            temp_df = df.loc[mask, ["Name", "Compiled", min_col, mean_col, max_col]].copy()
        else:
            temp_df = df.loc[mask, ["Name", min_col, mean_col, max_col]].copy()

        if temp_df.empty:
            print(f"Skipping {indicator}: no valid data after filtering.")
            continue

        # Error
        temp_df["error"] = (temp_df[[max_col, min_col]].max(axis=1) - temp_df[[max_col, min_col]].min(axis=1)) / 2

        # Sort
        temp_df = temp_df.sort_values(by=mean_col, ascending=False).reset_index(drop=True)
        x = range(len(temp_df))

        # Colors
        if "Compiled" in df.columns:
            bar_colors = ["skyblue" if compiled else "orchid" for compiled in temp_df["Compiled"]]
        else:
            bar_colors = ["orchid" for _ in temp_df["Name"]]

        # Plot
        plt.figure(figsize=(14, 6))
        for i in x:
            plt.bar(i, temp_df[mean_col].iloc[i], color=bar_colors[i], edgecolor="none")

        plt.xlim(-1.5, len(temp_df))

        err = plt.errorbar(
            x=x,
            y=temp_df[mean_col],
            yerr=temp_df["error"],
            fmt='none',
            ecolor='black',
            capsize=3.5,
            linewidth=0.7
        )
        for cap in err[1]:
            cap.set_linewidth(0.3)

        # X-ticks
        plt.xticks(ticks=x, labels=temp_df["Name"], rotation=90, ha='right', fontsize=5)
        plt.yticks(fontsize=6)
        plt.ylabel(indicator, fontsize=8)

        # Tick label colors
        ax = plt.gca()
        xtick_labels = ax.get_xticklabels()

        if "Compiled" in df.columns:
            for i, label in enumerate(xtick_labels):
                label.set_color('skyblue' if temp_df["Compiled"].iloc[i] else 'orchid')

            # Legend
            legend_handles = [
                Patch(facecolor='skyblue', label='ObjectType'),
                Patch(facecolor='orchid', label='Unique Element')
            ]
            plt.legend(handles=legend_handles, loc='upper right', fontsize=7, frameon=False)

        plt.title(indicator, fontsize=10)
        plt.tight_layout()

        # Save
        safe_name = indicator.split("[")[0].strip().replace(" ", "_").replace("(", "").replace(")", "").lower()
        output_file = output_dir / f"{safe_name}_plot.png"
        plt.savefig(output_file, dpi=300)
        plt.close()