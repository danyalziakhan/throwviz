import argparse
from multiprocessing import freeze_support
import os
from dearpygui import dearpygui as dpg
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def parse_distance_series(series: str):
    distances = [int(n) for n in series.split("-")]
    return list(range(distances[0], distances[1] + 1))


def parse_aspect_ratio(ar):
    w, h = ar.replace(" ", "").split(":")
    return float(w), float(h)


def fmt_num(x, decimals=3):
    if float(x).is_integer():
        return str(int(x))
    return f"{x:.{decimals}f}".rstrip("0").rstrip(".")


def fmt_ar(x):
    return fmt_num(x, 3)


def launch_gui(args):
    def generate_callback():
        surface_w = dpg.get_value("surface_w")
        surface_h = dpg.get_value("surface_h")
        throw = dpg.get_value("throw")
        dist = dpg.get_value("distance")
        ar = dpg.get_value("aspect")
        out = dpg.get_value("out")

        ar_w, ar_h = parse_aspect_ratio(ar)

        print()
        print(f"Surface Width: {fmt_num(surface_w)}")
        print(f"Surface Height: {fmt_num(surface_h)}")
        print(f"Throw Ratio: {fmt_num(throw)}")
        print(f"Distance: {fmt_num(dist)}")
        print(f"Aspect Ratio: {ar}")
        print(f"Output Directory: {out}")

        os.makedirs(out, exist_ok=True)
        generate_images(surface_w, surface_h, throw, [dist], ar_w, ar_h, out)

    dpg.create_context()

    with dpg.window(
        label="ThrowViz",
        tag="main",
        no_title_bar=True,
        no_move=True,
        no_resize=True,
        no_collapse=True,
    ):
        dpg.add_input_float(
            label="Surface Width (ft)",
            tag="surface_w",
            default_value=args.surface_width,
        )
        dpg.add_input_float(
            label="Surface Height (ft)",
            tag="surface_h",
            default_value=args.surface_height,
        )
        dpg.add_input_float(
            label="Throw Ratio", tag="throw", default_value=args.throw_ratio
        )
        dpg.add_input_float(
            label="Distance (ft)", tag="distance", default_value=args.distance
        )
        dpg.add_input_text(
            label="Aspect Ratio", tag="aspect", default_value=args.aspect_ratio
        )
        dpg.add_input_text(label="Output Dir", tag="out", default_value=args.output_dir)
        dpg.add_button(label="Generate", callback=generate_callback)

    dpg.create_viewport(
        title="ThrowViz",
        width=450,
        height=450,
        small_icon="icon.ico",
        large_icon="icon.ico",
    )
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("main", True)
    dpg.start_dearpygui()
    dpg.destroy_context()


def generate_images(
    surface_width: int,
    surface_height: int,
    throw_ratio: float,
    distances: list[int],
    ar_w: int,
    ar_h: int,
    output_dir: str,
):
    for distance in distances:
        # Dimensions
        inner_width = distance / throw_ratio
        inner_height = inner_width * (ar_h / ar_w)

        # Create the figure and axis
        fig, ax = plt.subplots(figsize=(8, 5))

        # Outer rectangle (black outline)
        outer_rect = plt.Rectangle(
            (0, 0),
            surface_width,
            surface_height,
            fill=False,
            color="black",
            linewidth=2,
        )

        # Calculate inner rectangle's bottom-left coordinates to center it
        inner_x = (surface_width - inner_width) / 2
        inner_y = (surface_height - inner_height) / 2

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
        y_outer = surface_height + 0.6
        x_outer = -0.7
        linewidth = 1.0
        fontsize = 9

        ax.annotate(
            "",
            xy=(0, y_outer),
            xytext=(surface_width, y_outer),
            arrowprops=dict(arrowstyle="<->", color="black", linewidth=linewidth),
        )
        ax.text(
            surface_width / 2,
            y_outer + 0.15,
            f"{fmt_num(surface_width)} ft",
            ha="center",
            va="bottom",
            fontsize=fontsize,
            color="black",
        )

        ax.annotate(
            "",
            xy=(x_outer, 0),
            xytext=(x_outer, surface_height),
            arrowprops=dict(arrowstyle="<->", color="black", linewidth=linewidth),
        )
        ax.text(
            x_outer - 0.15,
            surface_height / 2,
            f"{fmt_num(surface_height)} ft",
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
            f"{fmt_num(inner_width)} ft",
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
            f"{fmt_num(inner_height)} ft",
            ha="left",
            va="center",
            fontsize=fontsize,
            color="blue",
            rotation=90,
        )

        # Adjust view and remove axes
        plt.title(
            f"Throw Distance = {fmt_num(distance)} ft   |   Aspect Ratio = {fmt_ar(ar_w)}:{fmt_ar(ar_h)}"
        )
        ax.set_xlim(-1, surface_width + 2)
        ax.set_ylim(-1, surface_height + 2)
        ax.set_aspect("equal")
        ax.axis("off")

        # Save the figure
        file_path = os.path.join(output_dir, f"{fmt_num(distance)}ft.png")
        plt.savefig(file_path, dpi=300, bbox_inches="tight")

        print(f"Image saved to: {file_path}")


if __name__ == "__main__":
    freeze_support()

    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Generate throw distance drawings in feet."
    )
    parser.add_argument(
        "--surface_width",
        type=int,
        default=31,
        help="Width (ft) of the surface.",
    )
    parser.add_argument(
        "--surface_height",
        type=int,
        default=16,
        help="Height (ft) of the surface.",
    )
    parser.add_argument(
        "--throw_ratio",
        type=float,
        default=0.8,
        help="Throw ratio of projector/lens.",
    )
    parser.add_argument(
        "--distance",
        type=int,
        default=20,
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
        default="16:10",
        help="Aspect ratio of projector.",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="output",
        help="Output directory for generated drawings.",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch GUI instead of CLI mode",
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

    if args.gui:
        launch_gui(args)
    else:
        generate_images(
            args.surface_width,
            args.surface_height,
            args.throw_ratio,
            distances,
            ar_w,
            ar_h,
            args.output_dir,
        )
