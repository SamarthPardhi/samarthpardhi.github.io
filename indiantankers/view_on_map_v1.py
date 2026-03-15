import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import geopandas as gpd
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.collections import PatchCollection
from danger_area import quad_coords
# quad_coords = [
#     (54.8555946, 18.9434720),
#     (64.7010612, 26.1051959),
#     (49.6103096, 32.5929613),
#     (44.6657753, 29.6698575)
# ]

try:
    from adjustText import adjust_text
except ImportError:
    print("Error: The 'adjustText' library is missing.")
    print("Please install it by running: pip install adjustText")
    exit()

# ── Colour palette ──────────────────────────────────────────────────────────
OCEAN_COLOR   = "#D6EAF8"   # soft nautical blue
LAND_COLOR    = "#EAE0D5"   # warm parchment
BORDER_COLOR  = "#A0917A"   # muted brown for coastlines
GRID_COLOR    = "#AECCD8"   # subtle gridlines
ZONE_FILL     = "#E74C3C"   # danger zone fill
ZONE_EDGE     = "#C0392B"   # danger zone border
SHIP_FACE     = "#1A5276"   # deep navy ship dot
SHIP_EDGE     = "#FDFEFE"   # white outline for contrast
LABEL_COLOR   = "#1A2960"   # near-black navy for text
LABEL_BG      = "#FDFEFE"   # white label background
# ────────────────────────────────────────────────────────────────────────────


def plot_ships(csv_filepath: str, output_image: str) -> None:

    # 1 ── Bounding box from quad + padding ──────────────────────────────────
    lons = [c[0] for c in quad_coords]
    lats = [c[1] for c in quad_coords]
    pad  = 5
    min_lon, max_lon = min(lons) - pad, max(lons) + pad
    min_lat, max_lat = min(lats) - pad, max(lats) + pad

    # 2 ── World basemap ──────────────────────────────────────────────────────
    print("Downloading basemap…")
    url = "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"
    world = gpd.read_file(url)

    # 3 ── Ship data ──────────────────────────────────────────────────────────
    try:
        df = pd.read_csv(csv_filepath)
        df["LON"] = pd.to_numeric(df["LON"], errors="coerce")
        df["LAT"] = pd.to_numeric(df["LAT"], errors="coerce")
        df = df.dropna(subset=["LON", "LAT", "SHIPNAME"])
    except FileNotFoundError:
        print(f"Error: '{csv_filepath}' not found.")
        return

    # 4 ── Figure setup ───────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(15, 12))
    fig.patch.set_facecolor("#F4F6F7")

    # Ocean background (set before anything is drawn)
    ax.set_facecolor(OCEAN_COLOR)

    # Basemap: land
    world.plot(ax=ax, color=LAND_COLOR, edgecolor=BORDER_COLOR, linewidth=0.6, zorder=1)

    # 5 ── Danger zone ────────────────────────────────────────────────────────
    poly_lons = lons + [lons[0]]
    poly_lats = lats + [lats[0]]

    ax.fill(poly_lons, poly_lats,
            color=ZONE_FILL, alpha=0.18, zorder=2, label="_nolegend_")
    ax.plot(poly_lons, poly_lats,
            color=ZONE_EDGE, linewidth=2.2, linestyle="--",
            dash_capstyle="round", zorder=3, label="_nolegend_")

    # Corner markers
    ax.scatter(lons, lats,
               color=ZONE_EDGE, s=55, zorder=4,
               marker="D", edgecolors="white", linewidths=0.8)

    # 6 ── Ships ──────────────────────────────────────────────────────────────
    ax.scatter(df["LON"], df["LAT"],
               color=SHIP_FACE, s=55, zorder=5,
               marker="o", edgecolors=SHIP_EDGE, linewidths=0.9)

    # 7 ── Smart labelling: isolated = direct offset, congested = adjust_text ──
    print("Optimising label placement…")

    # Set axis limits FIRST so adjust_text respects the viewport
    ax.set_xlim(min_lon, max_lon)
    ax.set_ylim(min_lat, max_lat)

    # How close two ships must be (degrees) to be considered congested
    CONGESTION_RADIUS = 1.5

    coords = df[["LON", "LAT"]].values
    n = len(coords)
    is_congested = [False] * n
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            dist = ((coords[i][0] - coords[j][0]) ** 2 +
                    (coords[i][1] - coords[j][1]) ** 2) ** 0.5
            if dist < CONGESTION_RADIUS:
                is_congested[i] = True
                break

    bbox_plain = dict(
        boxstyle="round,pad=0.22", facecolor=LABEL_BG,
        edgecolor="#CCCCCC", linewidth=0.4, alpha=0.85,
    )
    # Slightly more prominent box for arrow-linked labels
    bbox_arrow = dict(
        boxstyle="round,pad=0.22", facecolor=LABEL_BG,
        edgecolor="#AAAAAA", linewidth=0.6, alpha=0.90,
    )

    # Small fixed offset for isolated ships (degrees)
    OFFSET_LON, OFFSET_LAT = 0.18, 0.18

    congested_texts  = []   # will go through adjust_text
    congested_points = []   # x, y of the actual ship dot

    for idx, (_, row) in enumerate(df.iterrows()):
        lon, lat, name = row["LON"], row["LAT"], row["SHIPNAME"]
        if not is_congested[idx]:
            # Place label directly — no arrow needed
            ax.text(
                lon + OFFSET_LON, lat + OFFSET_LAT, name,
                fontsize=7.5, color=LABEL_COLOR,
                fontweight="semibold", fontfamily="DejaVu Sans",
                bbox=bbox_plain, zorder=6,
                ha="left", va="bottom",
            )
        else:
            t = ax.text(
                lon + OFFSET_LON, lat + OFFSET_LAT, name,
                fontsize=7.5, color=LABEL_COLOR,
                fontweight="semibold", fontfamily="DejaVu Sans",
                bbox=bbox_arrow, zorder=6,
            )
            congested_texts.append(t)
            congested_points.append((lon, lat))

    if congested_texts:
        adjust_text(
            congested_texts,
            x=[p[0] for p in congested_points],
            y=[p[1] for p in congested_points],
            ax=ax,
            arrowprops=dict(arrowstyle="-", color="#999999", lw=0.65),
            expand_points=(1.4, 1.4),
            expand_text=(1.2, 1.2),
            force_text=(0.4, 0.6),
            force_points=(0.3, 0.4),
            lim=150,                  # cap iterations → prevents runaway placement
            only_move={"text": "xy", "points": "xy"},
        )

    # 8 ── Gridlines ──────────────────────────────────────────────────────────
    # (limits already set above)
    ax.grid(True, color=GRID_COLOR, linestyle="--", linewidth=0.6, alpha=0.8, zorder=0)

    # Degree symbols on tick labels
    ax.xaxis.set_major_formatter(
        plt.FuncFormatter(lambda v, _: f"{abs(v):.1f}°{'E' if v >= 0 else 'W'}")
    )
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda v, _: f"{abs(v):.1f}°{'N' if v >= 0 else 'S'}")
    )
    ax.tick_params(labelsize=9, colors="#444444")

    # 9 ── Spines ─────────────────────────────────────────────────────────────
    for spine in ax.spines.values():
        spine.set_edgecolor("#AAAAAA")
        spine.set_linewidth(0.8)

    # 10 ── Title block ───────────────────────────────────────────────────────
    ax.set_title(
        "Vessel Traffic — Target Zone",
        fontsize=17, fontweight="bold", color="#1A2960",
        pad=14, loc="left",
    )
    ax.text(
        0.0, 1.025,
        f"{len(df)} vessels detected within or near the search area",
        transform=ax.transAxes,
        fontsize=10, color="#555555",
    )

    ax.set_xlabel("Longitude", fontsize=10, color="#444444", labelpad=8)
    ax.set_ylabel("Latitude",  fontsize=10, color="#444444", labelpad=8)

    # 11 ── Legend ────────────────────────────────────────────────────────────
    ship_handle  = mlines.Line2D([], [], marker="o", color="w",
                                  markerfacecolor=SHIP_FACE,
                                  markeredgecolor=SHIP_EDGE,
                                  markersize=8, label="Vessel")
    zone_patch   = mpatches.Patch(facecolor=ZONE_FILL, edgecolor=ZONE_EDGE,
                                   linestyle="--", linewidth=1.5,
                                   alpha=0.7, label="Danger zone")
    corner_handle = mlines.Line2D([], [], marker="D", color="w",
                                   markerfacecolor=ZONE_EDGE,
                                   markeredgecolor="white",
                                   markersize=7, label="Zone vertex")

    legend = ax.legend(
        handles=[ship_handle, zone_patch, corner_handle],
        loc="lower right",
        frameon=True,
        framealpha=0.92,
        edgecolor="#CCCCCC",
        fontsize=9,
        title="Legend",
        title_fontsize=9.5,
    )
    legend.get_title().set_fontweight("bold")

    # 12 ── Save ───────────────────────────────────────────────────────────────
    plt.tight_layout()
    plt.savefig(output_image, bbox_inches="tight", dpi=300, facecolor=fig.get_facecolor())
    print(f"Saved → {output_image}")


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    plot_ships("ship_details.csv", "smart_labeled_ship_map.png")