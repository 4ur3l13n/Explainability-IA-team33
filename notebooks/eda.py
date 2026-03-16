"""
eda.py
Exploratory Data Analysis for the HR Attrition dataset.
Run this script standalone to generate EDA insights and plots.
Outputs saved to docs/eda_output/

Usage:
    python eda.py
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from sklearn.preprocessing import LabelEncoder


DATA_PATH = "../data/HRDataset_v14.csv"
OUT_DIR = "../docs/eda_output"
os.makedirs(OUT_DIR, exist_ok=True)

sns.set_style("whitegrid")
PALETTE = {"Active": "#6366f1", "Voluntarily Terminated": "#ef4444"}


df = pd.read_csv(DATA_PATH)
print(f"Dataset: {df .shape [0 ]} rows × {df .shape [1 ]} columns")
print(f"\nTarget distribution:\n{df ['Termd'].value_counts ()}")


fig, axes = plt.subplots(1, 2, figsize=(12, 4))


counts = df["Termd"].value_counts()
axes[0].pie(
    counts,
    labels=["Active", "Terminated"],
    colors=["#6366f1", "#ef4444"],
    autopct="%1.1f%%",
    startangle=90,
)
axes[0].set_title("Overall Attrition Rate", fontweight="bold")


dept_attrition = df.groupby("Department")["Termd"].mean().sort_values(ascending=False)
dept_attrition.plot(kind="bar", ax=axes[1], color="#6366f1", edgecolor="white")
axes[1].set_title("Attrition Rate by Department", fontweight="bold")
axes[1].set_ylabel("Attrition Rate")
axes[1].set_xticklabels(axes[1].get_xticklabels(), rotation=30, ha="right")
axes[1].yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y :.0%}"))

plt.tight_layout()
plt.savefig(f"{OUT_DIR }/01_attrition_overview.png", dpi=150)
plt.close()
print("[EDA] Saved: 01_attrition_overview.png")


numeric_features = [
    "EngagementSurvey",
    "EmpSatisfaction",
    "Absences",
    "Salary",
    "DaysLateLast30",
    "SpecialProjectsCount",
]

fig, axes = plt.subplots(2, 3, figsize=(15, 8))
axes = axes.flatten()

for i, feat in enumerate(numeric_features):
    for termd_val, label, color in [
        (0, "Active", "#6366f1"),
        (1, "Terminated", "#ef4444"),
    ]:
        subset = df[df["Termd"] == termd_val][feat].dropna()
        axes[i].hist(subset, bins=20, alpha=0.6, label=label, color=color)
    axes[i].set_title(feat, fontweight="bold")
    axes[i].legend(fontsize=8)

plt.suptitle(
    "Feature Distributions: Active vs Terminated", fontsize=14, fontweight="bold"
)
plt.tight_layout()
plt.savefig(f"{OUT_DIR }/02_feature_distributions.png", dpi=150)
plt.close()
print("[EDA] Saved: 02_feature_distributions.png")


numeric_df = df[numeric_features + ["Termd"]].copy()
corr = numeric_df.corr()

fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(
    corr, annot=True, fmt=".2f", cmap="RdYlGn_r", center=0, ax=ax, linewidths=0.5
)
ax.set_title("Feature Correlation with Attrition", fontweight="bold")
plt.tight_layout()
plt.savefig(f"{OUT_DIR }/03_correlation_heatmap.png", dpi=150)
plt.close()
print("[EDA] Saved: 03_correlation_heatmap.png")


fig, axes = plt.subplots(1, 2, figsize=(10, 5))

for ax, feat, title in [
    (axes[0], "EngagementSurvey", "Engagement Score"),
    (axes[1], "EmpSatisfaction", "Employee Satisfaction"),
]:
    data_active = df[df["Termd"] == 0][feat]
    data_left = df[df["Termd"] == 1][feat]
    ax.boxplot(
        [data_active, data_left],
        labels=["Active", "Terminated"],
        patch_artist=True,
        boxprops=dict(facecolor="#6366f1", alpha=0.6),
    )
    ax.set_title(f"{title } by Attrition Status", fontweight="bold")

plt.tight_layout()
plt.savefig(f"{OUT_DIR }/04_engagement_satisfaction_boxplot.png", dpi=150)
plt.close()
print("[EDA] Saved: 04_engagement_satisfaction_boxplot.png")


recruit_attrition = (
    df.groupby("RecruitmentSource")["Termd"]
    .agg(["mean", "count"])
    .rename(columns={"mean": "attrition_rate", "count": "n"})
    .sort_values("attrition_rate", ascending=False)
)

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(
    recruit_attrition.index,
    recruit_attrition["attrition_rate"],
    color="#6366f1",
    edgecolor="white",
)
ax.set_title("Attrition Rate by Recruitment Source", fontweight="bold")
ax.set_ylabel("Attrition Rate")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y :.0%}"))
ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right")


for bar, (_, row) in zip(bars, recruit_attrition.iterrows()):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.005,
        f"n={int (row ['n'])}",
        ha="center",
        va="bottom",
        fontsize=8,
    )

plt.tight_layout()
plt.savefig(f"{OUT_DIR }/05_recruitment_source_attrition.png", dpi=150)
plt.close()
print("[EDA] Saved: 05_recruitment_source_attrition.png")


print("\n" + "=" * 60)
print("EDA SUMMARY")
print("=" * 60)
print(f"\nTotal employees: {len (df )}")
print(f"Overall attrition rate: {df ['Termd'].mean ():.1%}")
print(f"\nHighest attrition departments:")
print(dept_attrition.head(3).to_string())
print(f"\nCorrelation with Termd (top features):")
print(
    corr["Termd"]
    .drop("Termd")
    .sort_values(key=abs, ascending=False)
    .head(5)
    .to_string()
)
print(f"\nAll EDA plots saved to: {OUT_DIR }/")
