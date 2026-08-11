"""Create compact, silent method animations for the publication cards.

The high-resolution PNG figures remain the canonical poster/fallback.  This
script turns each overview into a short visual trace: the active module is
spotlit, the method path fills from left to right, and particles carry state
between modules.  MP4/H.264 keeps the result broadly compatible with browsers.
"""

from __future__ import annotations

import math
import subprocess
from dataclasses import dataclass
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = ROOT / "assets" / "papers"
OUT_DIR = PAPER_DIR / "animations"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SIZE = (960, 576)
FPS = 18
DURATION = 6
FRAMES = FPS * DURATION

NAVY = (16, 42, 67)
MUTED = (98, 125, 152)
WHITE = (255, 255, 255)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    windows = Path("C:/Windows/Fonts")
    names = ["arialbd.ttf", "segoeuib.ttf"] if bold else ["arial.ttf", "segoeui.ttf"]
    for name in names:
        path = windows / name
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


FONT_MICRO = font(12, True)
FONT_STAGE = font(15, True)
FONT_VALUE = font(11, False)


@dataclass(frozen=True)
class Scene:
    file: str
    accent: tuple[int, int, int]
    labels: tuple[str, ...]
    boxes: tuple[tuple[float, float, float, float], ...]
    path: tuple[tuple[float, float], ...]
    value_label: str
    value_range: tuple[float, float]


SCENES = (
    Scene(
        "prcd-map", (52, 181, 170),
        ("OBSERVATIONAL EVIDENCE", "EDGE-WISE TRUST  τᵢⱼ", "TRUST-AWARE MAP", "CALIBRATED GRAPH"),
        ((.03, .31, .27, .58), (.30, .31, .64, .90), (.66, .31, .98, .67), (.66, .70, .98, .91)),
        ((.14, .45), (.46, .49), (.81, .49), (.81, .80)), "posterior trust", (.18, .87),
    ),
    Scene(
        "testing-before-trusting", (76, 132, 232),
        ("HISTORICAL EVIDENCE", "COMPETING WORLDS", "DIAGNOSTIC ACTION", "RESCUE / VETO"),
        ((.03, .31, .27, .67), (.30, .31, .64, .88), (.66, .31, .98, .69), (.66, .69, .98, .91)),
        ((.15, .47), (.46, .47), (.81, .48), (.81, .80)), "causal-world weight", (.22, .78),
    ),
    Scene(
        "deltanar", (125, 104, 190),
        ("EDIT EVENT", "AFFECTED-REGION GATE", "COPY-SAFETY GATE", "MERGED SOLUTION"),
        ((.03, .31, .27, .64), (.29, .31, .64, .59), (.29, .55, .73, .88), (.64, .68, .98, .92)),
        ((.15, .47), (.47, .46), (.47, .69), (.81, .79)), "recompute mass", (.10, .72),
    ),
    Scene(
        "failure-learning", (225, 105, 105),
        ("FAILURE MEMORY", "FROZEN PROBES", "MATCHED CONTROLS", "AUDITABLE CLAIM"),
        ((.03, .31, .26, .67), (.29, .31, .61, .90), (.63, .31, .98, .67), (.63, .68, .98, .91)),
        ((.14, .46), (.45, .48), (.80, .49), (.80, .80)), "claim support", (.16, .83),
    ),
    Scene(
        "bounded-path-context", (232, 169, 76),
        ("QUESTION-GROUNDED KG", "EXACT BEAM MEMORY", "BOUNDED CONTEXT LENS", "FULL-PATH ANSWER"),
        ((.03, .31, .27, .91), (.30, .31, .62, .65), (.30, .56, .62, .90), (.65, .68, .98, .91)),
        ((.15, .48), (.46, .45), (.46, .71), (.82, .80)), "visible context", (.82, .27),
    ),
    Scene(
        "decoder-audit", (61, 154, 123),
        ("FIXED RECIPE", "FACTORIAL GRID", "UNCERTAINTY", "FACTOR ATTRIBUTION"),
        ((.03, .31, .27, .89), (.30, .31, .62, .89), (.65, .31, .98, .64), (.65, .61, .98, .90)),
        ((.15, .48), (.46, .48), (.81, .47), (.81, .77)), "identified effect", (.12, .88),
    ),
)


def xy(point: tuple[float, float]) -> tuple[int, int]:
    return int(point[0] * SIZE[0]), int(point[1] * SIZE[1])


def rect(box: tuple[float, float, float, float]) -> tuple[int, int, int, int]:
    return (
        int(box[0] * SIZE[0]), int(box[1] * SIZE[1]),
        int(box[2] * SIZE[0]), int(box[3] * SIZE[1]),
    )


def ease(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


def point_on_polyline(points: tuple[tuple[float, float], ...], progress: float) -> tuple[int, int]:
    progress %= 1.0
    segments = []
    total = 0.0
    for start, end in zip(points, points[1:]):
        length = math.dist(start, end)
        segments.append((start, end, length))
        total += length
    target = progress * total
    covered = 0.0
    for start, end, length in segments:
        if covered + length >= target:
            local = (target - covered) / max(length, 1e-6)
            return xy((start[0] + (end[0] - start[0]) * local, start[1] + (end[1] - start[1]) * local))
        covered += length
    return xy(points[-1])


def rounded_mask(box: tuple[int, int, int, int], radius: int = 18) -> Image.Image:
    width, height = box[2] - box[0], box[3] - box[1]
    mask = Image.new("L", (width, height), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, width, height), radius=radius, fill=255)
    return mask


def make_frame(base: Image.Image, scene: Scene, index: int) -> Image.Image:
    cycle = index / FRAMES
    phase_float = cycle * len(scene.boxes)
    phase = min(len(scene.boxes) - 1, int(phase_float))
    local = phase_float - phase
    pulse = .5 + .5 * math.sin(local * math.tau)

    # A light veil makes the active computation read as a spotlight without
    # sacrificing the white paper background or the labels in inactive panels.
    dim = Image.blend(base, Image.new("RGB", SIZE, WHITE), 0.14)
    active_box = rect(scene.boxes[phase])
    dim.paste(base.crop(active_box), active_box, rounded_mask(active_box))
    frame = dim.convert("RGBA")

    glow = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    accent = scene.accent
    width = 5 + int(2 * pulse)
    gd.rounded_rectangle(active_box, radius=18, outline=(*accent, 175), width=width)
    blurred = glow.filter(ImageFilter.GaussianBlur(11))
    frame = Image.alpha_composite(frame, blurred)
    frame = Image.alpha_composite(frame, glow)

    overlay = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Paper-like progress rule, kept compact enough not to compete with the
    # scientific figure itself.
    x0, x1, y = 36, SIZE[0] - 36, 126
    draw.line((x0, y, x1, y), fill=(201, 216, 230, 180), width=2)
    draw.line((x0, y, int(x0 + (x1 - x0) * cycle), y), fill=(*accent, 245), width=4)
    for step in range(len(scene.labels)):
        sx = int(x0 + (x1 - x0) * step / (len(scene.labels) - 1))
        fill = (*accent, 255) if step <= phase else (255, 255, 255, 255)
        outline = (*accent, 255) if step <= phase else (164, 184, 202, 255)
        draw.ellipse((sx - 6, y - 6, sx + 6, y + 6), fill=fill, outline=outline, width=2)

    # Current-stage capsule and a small quantitative trace make the animation
    # behave like a method execution rather than a slideshow.
    label = f"{phase + 1:02d}  {scene.labels[phase]}"
    label_width = draw.textlength(label, font=FONT_STAGE)
    lx = SIZE[0] - int(label_width) - 64
    draw.rounded_rectangle((lx, 25, SIZE[0] - 26, 65), radius=18, fill=(255, 255, 255, 238), outline=(*accent, 145), width=2)
    draw.ellipse((lx + 14, 41, lx + 22, 49), fill=(*accent, 255))
    draw.text((lx + 31, 36), label, font=FONT_STAGE, fill=NAVY)

    v0, v1 = scene.value_range
    value = v0 + (v1 - v0) * ease(cycle)
    value_text = f"{scene.value_label}  {value:.2f}"
    draw.rounded_rectangle((36, SIZE[1] - 44, 232, SIZE[1] - 17), radius=12, fill=(255, 255, 255, 232), outline=(201, 216, 230, 210), width=1)
    draw.text((49, SIZE[1] - 38), value_text, font=FONT_VALUE, fill=MUTED)
    meter_x = 169
    draw.rounded_rectangle((meter_x, SIZE[1] - 34, 220, SIZE[1] - 27), radius=3, fill=(226, 235, 242, 255))
    draw.rounded_rectangle((meter_x, SIZE[1] - 34, meter_x + int(51 * max(0, min(1, value))), SIZE[1] - 27), radius=3, fill=(*accent, 255))

    # State particles move continuously through the method path.  A soft halo
    # plus a sharp core remains legible even after H.264 compression.
    for offset, radius in ((0.0, 7), (.075, 5), (.15, 4)):
        px, py = point_on_polyline(scene.path, cycle * 1.08 + offset)
        draw.ellipse((px - radius * 2, py - radius * 2, px + radius * 2, py + radius * 2), fill=(*accent, 35))
        draw.ellipse((px - radius, py - radius, px + radius, py + radius), fill=(255, 255, 255, 255), outline=(*accent, 255), width=2)
        draw.ellipse((px - 2, py - 2, px + 2, py + 2), fill=(*accent, 255))

    # A short scanning sheen crosses the active module once per stage.
    left, top, right, bottom = active_box
    scan_x = int(left + (right - left) * ease(local))
    draw.line((scan_x, top + 10, scan_x, bottom - 10), fill=(*accent, int(35 + 45 * pulse)), width=3)

    return Image.alpha_composite(frame, overlay).convert("RGB")


def encode(scene: Scene) -> None:
    source = PAPER_DIR / f"{scene.file}.png"
    output = OUT_DIR / f"{scene.file}.mp4"
    base = Image.open(source).convert("RGB").resize(SIZE, Image.Resampling.LANCZOS)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    command = [
        ffmpeg, "-y", "-loglevel", "error",
        "-f", "rawvideo", "-vcodec", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{SIZE[0]}x{SIZE[1]}", "-r", str(FPS), "-i", "-",
        "-an", "-vcodec", "libx264", "-preset", "slow", "-crf", "24",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(output),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    assert process.stdin is not None
    try:
        for index in range(FRAMES):
            process.stdin.write(make_frame(base, scene, index).tobytes())
    finally:
        process.stdin.close()
    if process.wait() != 0:
        raise RuntimeError(f"ffmpeg failed while encoding {scene.file}")
    print(f"{output.name}: {output.stat().st_size / 1024:.0f} KiB")


if __name__ == "__main__":
    for item in SCENES:
        encode(item)
