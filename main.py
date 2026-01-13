import argparse
from multiprocessing import freeze_support
import os

import matplotlib.pyplot as plt


def parse_distance_series(series: str):
    distances = [int(n) for n in series.split("-")]
    return list(range(distances[0], distances[1] + 1))


def parse_aspect_ratio(ar):
    w, h = ar.replace(" ", "").split(":")
    return float(w), float(h)


if __name__ == "__main__":
    freeze_support()

    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Generate throw distance drawings in feet."
    )
    parser.add_argument(
        "--surface_width",
        type=int,
        required=True,
        help="Width (ft) of the surface.",
    )
    parser.add_argument(
        "--surface_height",
        type=int,
        required=True,
        help="Height (ft) of the surface.",
    )
    parser.add_argument(
        "--throw_ratio",
        type=float,
        required=True,
        help="Throw ratio of projector/lens.",
    )
    parser.add_argument(
        "--distance",
        type=int,
        help="Distance (ft) from surface to lens.",
    )
    parser.add_argument(
        "--distance_series",
        type=str,
        help="Distance (ft) series from surface to lens.",
    )
    parser.add_argument(
        "--aspect_ratio",
        type=str,
        required=True,
        help="Aspect ratio of projector.",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        required=True,
        help="Output directory for generated drawings.",
    )

    args = parser.parse_args()

    if not args.distance and not args.distance_series:
        raise ValueError("Provide either --distance or --distance_series")

    if args.distance and args.distance_series:
        raise ValueError("Provide either --distance or --distance_series and not both")

    print()
    print(f"Processor Count: {os.cpu_count()}")
    print(f"Surface Width: {args.surface_width}")
    print(f"Surface Height: {args.surface_height}")
    print(f"Throw Ratio: {args.throw_ratio}")
    print(f"Distance: {args.distance}")
    print(f"Distance Series: {args.distance_series}")
    print(f"Aspect Ratio: {args.aspect_ratio}")
    print(f"Output Directory: {args.output_dir}")

    if not os.path.exists(args.output_dir):
        print(
            f"\nOutput directory does not exist: {args.output_dir}. Creating the directory... "
        )
        os.makedirs(args.output_dir)

    ar_w, ar_h = parse_aspect_ratio(args.aspect_ratio)

    if args.distance and args.distance_series:
        raise ValueError("Provide either distance or distance_series, but not both.")

    if args.distance_series:
        distances = parse_distance_series(args.distance_series)
    else:
        distances = [args.distance]

    for distance in distances:
        # Dimensions
        inner_width = distance / args.throw_ratio
        inner_height = inner_width * (ar_h / ar_w)

        # Create the figure and axis
        fig, ax = plt.subplots(figsize=(8, 5))

        # Outer rectangle (black outline)
        outer_rect = plt.Rectangle(
            (0, 0),
            args.surface_width,
            args.surface_height,
            fill=False,
            color="black",
            linewidth=2,
        )

        # Calculate inner rectangle's bottom-left coordinates to center it
        inner_x = (args.surface_width - inner_width) / 2
        inner_y = (args.surface_height - inner_height) / 2

        # Inner rectangle (blue outline)
        inner_rect = plt.Rectangle(
            (inner_x, inner_y),
            inner_width,
            inner_height,
            fill=False,
            color="blue",
            linewidth=2,
            linestyle="--",
        )

        # Add rectangles to the plot
        ax.add_patch(outer_rect)
        ax.add_patch(inner_rect)

        # Place labels for the outer rectangle
        y_outer = args.surface_height + 0.6
        x_outer = -0.7
        linewidth = 1.0
        fontsize = 9

        ax.annotate(
            "",
            xy=(0, y_outer),
            xytext=(args.surface_width, y_outer),
            arrowprops=dict(arrowstyle="<->", color="black", linewidth=linewidth),
        )
        ax.text(
            args.surface_width / 2,
            y_outer + 0.15,
            f"{args.surface_width} ft",
            ha="center",
            va="bottom",
            fontsize=fontsize,
            color="black",
        )

        ax.annotate(
            "",
            xy=(x_outer, 0),
            xytext=(x_outer, args.surface_height),
            arrowprops=dict(arrowstyle="<->", color="black", linewidth=linewidth),
        )
        ax.text(
            x_outer - 0.15,
            args.surface_height / 2,
            f"{args.surface_height} ft",
            ha="right",
            va="center",
            fontsize=fontsize,
            color="black",
            rotation=90,
        )

        # Place labels for the inner rectangle
        y_inner = inner_y + inner_height - 1.0
        x_inner = inner_x + 1.0
        linewidth = 0.8
        fontsize = 8

        ax.annotate(
            "",
            xy=(inner_x, y_inner),
            xytext=(inner_x + inner_width, y_inner),
            arrowprops=dict(arrowstyle="<->", color="blue", linewidth=linewidth),
        )
        ax.text(
            inner_x + inner_width / 2,
            y_inner - 0.15,
            f"{inner_width:.2f} ft",
            ha="center",
            va="top",  # ← was "bottom"
            fontsize=fontsize,
            color="blue",
        )

        ax.annotate(
            "",
            xy=(x_inner, inner_y),
            xytext=(x_inner, inner_y + inner_height),
            arrowprops=dict(arrowstyle="<->", color="blue", linewidth=linewidth),
        )
        ax.text(
            x_inner + 0.20,
            inner_y + inner_height / 2,
            f"{inner_height:.2f} ft",
            ha="left",
            va="center",
            fontsize=fontsize,
            color="blue",
            rotation=90,
        )

        # Adjust view and remove axes
        plt.title(
            f"Throw Distance = {distance} ft   |   Aspect Ratio = {args.aspect_ratio}"
        )
        ax.set_xlim(-1, args.surface_width + 2)
        ax.set_ylim(-1, args.surface_height + 2)
        ax.set_aspect("equal")
        ax.axis("off")

        # Save the figure
        file_path = os.path.join(args.output_dir, f"{distance}ft.png")
        plt.savefig(file_path, dpi=300, bbox_inches="tight")

        print(f"Image saved to: {file_path}")
