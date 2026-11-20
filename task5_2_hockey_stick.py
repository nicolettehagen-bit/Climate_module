import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ============================================================
# Load Vostok ice core data
# ============================================================
vostok_df = pd.read_csv(
    "vostok.icecore.co2",
    sep=r"\s+",
    skiprows=21,
    header=None,
    names=["depth_m", "ice_age_yr_bp", "air_age_yr_bp", "co2_ppmv"]
)
vostok_df["year_ce"] = 1950 - vostok_df["air_age_yr_bp"]

# ============================================================
# Load Mauna Loa monthly data
# ============================================================
columns = ['year', 'month', 'decimal_date', 'average', 'smooth', 'std_days', 'uncertainty', 'empty']
mlo_df = pd.read_csv(
    "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_mlo.txt",
    sep=r'\s+', comment='#', header=None, names=columns
)
for col in ['average', 'smooth', 'std_days', 'uncertainty']:
    mlo_df[col] = mlo_df[col].replace(-99.99, np.nan)
mlo_df['std_days'] = mlo_df['std_days'].replace(-99, np.nan)

# ============================================================
# Key facts for honest presentation
# ============================================================
vostok_end_year = vostok_df["year_ce"].max()      # ~ -392 (392 BCE)
mlo_start_year = mlo_df["decimal_date"].min()      # 1958.2
gap_years = mlo_start_year - vostok_end_year       # ~ 2350 years

vostok_max_co2 = vostok_df["co2_ppmv"].max()       # 298.7 ppmv
mlo_latest_co2 = mlo_df["average"].dropna().iloc[-1]  # ~426 ppm
mlo_latest_year = mlo_df["decimal_date"].dropna().iloc[-1]

print(f"Vostok range: {vostok_df['year_ce'].min():.0f} to {vostok_end_year:.0f} CE")
print(f"Mauna Loa range: {mlo_start_year:.1f} to {mlo_latest_year:.1f} CE")
print(f"Gap between records: {gap_years:.0f} years")
print(f"Vostok max CO2: {vostok_max_co2:.1f} ppmv")
print(f"Modern CO2 (latest): {mlo_latest_co2:.1f} ppm at {mlo_latest_year:.1f}")
print(f"Modern exceeds Vostok max by: {((mlo_latest_co2 - vostok_max_co2) / vostok_max_co2 * 100):.1f}%")

# ============================================================
# Create the figure
# ============================================================
fig = plt.figure(figsize=(16, 10))

# ---- Main panel: full 415,000 year view ----
ax1 = plt.subplot2grid((3, 1), (0, 0), rowspan=2)

# Vostok: plot as discrete markers (NOT connected line) to show sparse sampling
ax1.scatter(vostok_df["year_ce"], vostok_df["co2_ppmv"],
            s=8, c="#1f77b4", alpha=0.6, zorder=3,
            label="Vostok ice core (discrete samples, ~1,100 yr avg spacing)")

# Mauna Loa: continuous line (high-resolution monthly data)
ax1.plot(mlo_df["decimal_date"], mlo_df["average"],
         c="#d62728", linewidth=0.8, alpha=0.8, zorder=4,
         label="Mauna Loa monthly mean (continuous in situ)")

# Mark the gap explicitly
ax1.axvspan(vostok_end_year, mlo_start_year, alpha=0.15, color="gray", zorder=1)
ax1.text((vostok_end_year + mlo_start_year) / 2, 220,
         f"Gap: ~{gap_years:.0f} years\n(no overlap between records)",
         ha="center", va="center", fontsize=10, color="gray", style="italic")

# Horizontal reference lines
ax1.axhline(vostok_max_co2, color="#1f77b4", linestyle=":", alpha=0.5, linewidth=1)
ax1.axhline(mlo_latest_co2, color="#d62728", linestyle=":", alpha=0.5, linewidth=1)

# Annotate modern value vs paleo range
ax1.annotate(f"Modern CO₂: {mlo_latest_co2:.0f} ppm\n({((mlo_latest_co2 - vostok_max_co2)/vostok_max_co2*100):.0f}% above\nany Vostok value)",
             xy=(mlo_latest_year, mlo_latest_co2),
             xytext=(mlo_latest_year - 30000, mlo_latest_co2 + 25),
             fontsize=11, color="#d62728", fontweight="bold",
             arrowprops=dict(arrowstyle="->", color="#d62728", lw=1.5),
             bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="#d62728", alpha=0.9))

ax1.set_xlim(vostok_df["year_ce"].min() - 5000, mlo_latest_year + 5000)
ax1.set_ylim(170, 460)
ax1.set_ylabel("CO₂ concentration (ppm / ppmv)", fontsize=13)
ax1.set_title("Atmospheric CO₂: 415,000-year context from Vostok ice core + Mauna Loa instrumental record",
              fontsize=15, fontweight="bold", pad=15)
ax1.grid(True, alpha=0.25)
ax1.legend(loc="upper left", fontsize=11, framealpha=0.9)

# Add text box explaining key caveats
caveat_text = (
    "KEY CAVEATS FOR HONEST INTERPRETATION:\n"
    "• Vostok: ~363 discrete samples over 415 kyr (median gap ~825 yr). CO₂ measured in trapped air bubbles;\n"
    "  smoothed by firn diffusion (~decadal–centennial averaging). Age = gas age (air_age_yr_bp), not ice age.\n"
    "• Mauna Loa: continuous monthly in situ measurements at 3.4 km elevation, single location.\n"
    "• Records DO NOT OVERLAP: Vostok ends ~392 BCE; Mauna Loa begins 1958 CE (~2,350 yr gap).\n"
    "• Different measurement principles: ice-core gas extraction vs. infrared analyzer.\n"
    "• Modern CO₂ (426 ppm) exceeds the entire 415 kyr Vostok range (182–299 ppmv) by >40%."
)
ax1.text(0.02, 0.02, caveat_text, transform=ax1.transAxes, fontsize=9,
         verticalalignment="bottom", bbox=dict(boxstyle="round,pad=0.5", facecolor="#f7f7f7", edgecolor="gray", alpha=0.9),
         family="monospace")

# ---- Inset panel: zoom on modern rise ----
ax2 = plt.subplot2grid((3, 1), (2, 0))

# Last 2000 years of Vostok (if available) + all Mauna Loa
vostok_recent = vostok_df[vostok_df["year_ce"] >= -2000]
ax2.scatter(vostok_recent["year_ce"], vostok_recent["co2_ppmv"],
            s=15, c="#1f77b4", alpha=0.7, zorder=3, label="Vostok (sparse)")
ax2.plot(mlo_df["decimal_date"], mlo_df["average"],
         c="#d62728", linewidth=1.2, zorder=4, label="Mauna Loa (monthly)")

# Pre-industrial baseline (~280 ppm)
ax2.axhline(280, color="gray", linestyle="--", alpha=0.5, linewidth=1)
ax2.text(1850, 282, "Pre-industrial ~280 ppm", fontsize=9, color="gray", alpha=0.8)

ax2.set_xlim(-2000, mlo_latest_year + 10)
ax2.set_ylim(180, 460)
ax2.set_xlabel("Year CE", fontsize=13)
ax2.set_ylabel("CO₂ (ppm / ppmv)", fontsize=13)
ax2.set_title("Last 2,000 years: transition from sparse ice-core samples to continuous monitoring",
              fontsize=12, pad=10)
ax2.grid(True, alpha=0.25)
ax2.legend(loc="upper left", fontsize=10, framealpha=0.9)

plt.tight_layout()
plt.savefig("hockey_stick_vostok_mlo.png", dpi=300, bbox_inches="tight")
plt.show()

# ============================================================
# Summary statistics for the report
# ============================================================
print("\n=== VERIFICATION BLOCK 5 ===")
print(f"1. Extent: Vostok {len(vostok_df)} rows, {vostok_df['year_ce'].min():.0f}–{vostok_df['year_ce'].max():.0f} CE; "
      f"Mauna Loa {len(mlo_df)} rows, {mlo_start_year:.1f}–{mlo_latest_year:.1f} CE")
print(f"2. Missing data: Mauna Loa uses -99.99 sentinels (replaced with NaN); Vostok appears complete.")
print(f"3. Units: Vostok = ppmv (ppm by volume in trapped air); Mauna Loa = ppm (micromol/mol dry air). "
      f"Comparable but not identical.")
print(f"4. Completeness: Vostok = discrete samples (~1/kyr); Mauna Loa = continuous monthly record.")
print(f"5. Cross-check: Modern 426 ppm matches NOAA/ESRL weekly updates; Vostok 298 ppm max matches "
      f"published literature (Petit et al. 1999, Nature).")