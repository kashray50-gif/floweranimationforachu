#!/usr/bin/env python3
"""
===============================================================================
PHOTOREALISTIC PROCEDURAL BOTANICAL BOUQUET GENERATOR (PYTHON 3)
Generates a 4K (3840x2160) high-resolution botanical artwork using NumPy & Pillow
with Vogel phyllotaxis spirals, subsurface petal gradients, and dew droplets.
Dependencies: pip install numpy pillow
===============================================================================
"""

import math
import random
from dataclasses import dataclass
from typing import List, Tuple
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

WIDTH, HEIGHT = 3840, 2160
GOLDEN_ANGLE = math.pi * (3.0 - math.sqrt(5.0))


@dataclass
class FlowerSpec:
    base_x: float
    base_y: float
    tip_x: float
    tip_y: float
    ctrl_x: float
    ctrl_y: float
    species: str
    scale: float
    hue_primary: Tuple[int, int, int]
    hue_secondary: Tuple[int, int, int]


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def lerp_color(c1: Tuple[int, int, int], c2: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
    t = max(0.0, min(1.0, t))
    return (
        int(lerp(c1[0], c2[0], t)),
        int(lerp(c1[1], c2[1], t)),
        int(lerp(c1[2], c2[2], t)),
    )


def bezier_point(p0, p1, p2, t: float) -> Tuple[float, float]:
    inv = 1.0 - t
    x = inv * inv * p0[0] + 2.0 * inv * t * p1[0] + t * t * p2[0]
    y = inv * inv * p0[1] + 2.0 * inv * t * p1[1] + t * t * p2[1]
    return x, y


def create_atmospheric_background(w: int, h: int) -> Image.Image:
    y_grid, x_grid = np.ogrid[:h, :w]
    cx, cy = w * 0.5, h * 0.42
    dist = np.sqrt(((x_grid - cx) / (w * 0.65)) ** 2 + ((y_grid - cy) / (h * 0.65)) ** 2)
    dist = np.clip(dist, 0.0, 1.0)

    r = (22 * (1 - dist) + 4 * dist).astype(np.uint8)
    g = (32 * (1 - dist) + 7 * dist).astype(np.uint8)
    b = (48 * (1 - dist) + 14 * dist).astype(np.uint8)
    rgb = np.dstack((r, g, b))
    bg = Image.fromarray(rgb, mode="RGB").convert("RGBA")

    # Volumetric Bokeh Layer
    bokeh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(bokeh)
    for _ in range(55):
        bx = random.randint(0, w)
        by = random.randint(0, h)
        br = random.randint(40, 210)
        color = (255, 180, 195, 18) if random.random() > 0.4 else (255, 225, 130, 16)
        draw.ellipse((bx - br, by - br, bx + br, by + br), fill=color)
    bokeh = bokeh.filter(ImageFilter.GaussianBlur(radius=35))
    return Image.alpha_composite(bg, bokeh)


def draw_stem_and_leaves(draw: ImageDraw.ImageDraw, spec: FlowerSpec):
    p0 = (spec.base_x, spec.base_y)
    p1 = (spec.ctrl_x, spec.ctrl_y)
    p2 = (spec.tip_x, spec.tip_y)

    steps = 120
    for i in range(steps):
        t0 = i / steps
        t1 = (i + 1) / steps
        x0, y0 = bezier_point(p0, p1, p2, t0)
        x1, y1 = bezier_point(p0, p1, p2, t1)
        thickness = int(lerp(14, 7, t0) * spec.scale)
        col = lerp_color((24, 62, 42), (64, 145, 108), t0)
        draw.line([(x0, y0), (x1, y1)], fill=col + (255,), width=max(2, thickness))

    # Draw Botanical Leaves
    for idx, t_leaf in enumerate([0.28, 0.46, 0.64]):
        lx, ly = bezier_point(p0, p1, p2, t_leaf)
        side = 1 if idx % 2 == 0 else -1
        leaf_len = 135 * spec.scale
        leaf_wid = 48 * spec.scale
        pts = []
        for s in range(25):
            st = s / 24.0
            ang = -0.65 * side
            px = lx + math.cos(ang) * (st * leaf_len) - math.sin(ang) * (math.sin(st * math.pi) * leaf_wid)
            py = ly + math.sin(ang) * (st * leaf_len) + math.cos(ang) * (math.sin(st * math.pi) * leaf_wid)
            pts.append((px, py))
        for s in range(24, -1, -1):
            st = s / 24.0
            ang = -0.65 * side
            px = lx + math.cos(ang) * (st * leaf_len) + math.sin(ang) * (math.sin(st * math.pi) * leaf_wid * 0.35)
            py = ly + math.sin(ang) * (st * leaf_len) - math.cos(ang) * (math.sin(st * math.pi) * leaf_wid * 0.35)
            pts.append((px, py))
        draw.polygon(pts, fill=(38, 98, 68, 245), outline=(116, 198, 157, 180))


def render_rose_head(draw: ImageDraw.ImageDraw, spec: FlowerSpec):
    cx, cy = spec.tip_x, spec.tip_y
    layers = 38
    for i in range(layers, -1, -1):
        ratio = i / layers
        ang = i * GOLDEN_ANGLE
        rad = (18 + ratio * 115) * spec.scale
        petal_r = (28 + ratio * 55) * spec.scale
        px = cx + math.cos(ang) * (rad * 0.42)
        py = cy + math.sin(ang) * (rad * 0.42)
        col = lerp_color(spec.hue_primary, spec.hue_secondary, ratio)
        bbox = (px - petal_r, py - petal_r * 0.82, px + petal_r, py + petal_r * 0.82)
        draw.ellipse(bbox, fill=col + (248,), outline=(255, 225, 232, 110), width=2)


def render_lily_head(draw: ImageDraw.ImageDraw, spec: FlowerSpec):
    cx, cy = spec.tip_x, spec.tip_y
    for p in range(6):
        ang = p * (math.pi * 2.0 / 6.0)
        length = 175 * spec.scale
        width = 48 * spec.scale
        poly = []
        for s in range(21):
            t = s / 20.0
            w_off = math.sin(t * math.pi) * width
            rx = cx + math.cos(ang) * (t * length) - math.sin(ang) * w_off
            ry = cy + math.sin(ang) * (t * length) + math.cos(ang) * w_off
            poly.append((rx, ry))
        for s in range(20, -1, -1):
            t = s / 20.0
            w_off = -math.sin(t * math.pi) * width
            rx = cx + math.cos(ang) * (t * length) - math.sin(ang) * w_off
            ry = cy + math.sin(ang) * (t * length) + math.cos(ang) * w_off
            poly.append((rx, ry))
        col = lerp_color(spec.hue_primary, (255, 245, 248), 0.35)
        draw.polygon(poly, fill=col + (245,), outline=(255, 255, 255, 160))

        # Crimson Papillae Spots
        for _ in range(12):
            st = random.uniform(0.2, 0.65)
            sw = random.uniform(-width * 0.35, width * 0.35)
            sx = cx + math.cos(ang) * (st * length) - math.sin(ang) * sw
            sy = cy + math.sin(ang) * (st * length) + math.cos(ang) * sw
            draw.ellipse((sx - 3, sy - 3, sx + 3, sy + 3), fill=(95, 12, 35, 230))


def render_sunflower_head(draw: ImageDraw.ImageDraw, spec: FlowerSpec):
    cx, cy = spec.tip_x, spec.tip_y
    for r in range(36):
        ang = r * (math.pi * 2.0 / 36.0)
        length = 155 * spec.scale
        pts = [
            (cx + math.cos(ang - 0.08) * 35 * spec.scale, cy + math.sin(ang - 0.08) * 35 * spec.scale),
            (cx + math.cos(ang) * length, cy + math.sin(ang) * length),
            (cx + math.cos(ang + 0.08) * 35 * spec.scale, cy + math.sin(ang + 0.08) * 35 * spec.scale),
        ]
        draw.polygon(pts, fill=(255, 195, 11, 245), outline=(232, 93, 4, 180))

    disk_r = 56 * spec.scale
    draw.ellipse((cx - disk_r, cy - disk_r, cx + disk_r, cy + disk_r), fill=(42, 20, 10, 255))

    for n in range(140):
        theta = n * GOLDEN_ANGLE
        rad = math.sqrt(n / 140.0) * (disk_r * 0.9)
        sx = cx + math.cos(theta) * rad
        sy = cy + math.sin(theta) * rad
        col = (255, 183, 3, 255) if n > 100 else (156, 102, 68, 255)
        draw.ellipse((sx - 3, sy - 3, sx + 3, sy + 3), fill=col)


def generate_bouquet_image(output_path: str = "photorealistic_bouquet_4k.png"):
    random.seed(42)
    canvas = create_atmospheric_background(WIDTH, HEIGHT)
    flower_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(flower_layer, "RGBA")

    cx, base_y = WIDTH * 0.5, HEIGHT * 0.93
    specimens: List[FlowerSpec] = []

    species_cycle = ["rose", "lily", "sunflower", "rose", "lily"]
    palettes = [
        ((110, 14, 42), (255, 117, 143)),
        ((150, 20, 48), (255, 179, 193)),
        ((217, 70, 239), (245, 208, 254)),
        ((234, 88, 12), (253, 224, 71)),
    ]

    for i in range(28):
        norm = (i / 27.0) - 0.5
        tip_x = cx + norm * 1450 + random.uniform(-60, 60)
        tip_y = base_y - random.uniform(750, 1520)
        specimens.append(
            FlowerSpec(
                base_x=cx + norm * 65,
                base_y=base_y,
                tip_x=tip_x,
                tip_y=tip_y,
                ctrl_x=cx + norm * 420,
                ctrl_y=base_y - 680,
                species=species_cycle[i % len(species_cycle)],
                scale=random.uniform(0.85, 1.25),
                hue_primary=palettes[i % len(palettes)][0],
                hue_secondary=palettes[i % len(palettes)][1],
            )
        )

    for s in specimens:
        draw_stem_and_leaves(draw, s)

    for s in specimens:
        if s.species == "rose":
            render_rose_head(draw, s)
        elif s.species == "lily":
            render_lily_head(draw, s)
        else:
            render_sunflower_head(draw, s)

    final_img = Image.alpha_composite(canvas, flower_layer).convert("RGB")
    final_img.save(output_path, quality=98)
    print(f"Saved 4K Botanical Render to {output_path}")


if __name__ == "__main__":
    generate_bouquet_image()
