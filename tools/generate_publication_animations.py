"""Generate semantic, paper-style method animations for the publication cards.

Every animation changes an actual model state: trust, posterior world weights,
affected regions, control outcomes, the visible context window, or the
factorial audit grid.  There are deliberately no decorative particles or
scanning overlays.  The final frame is also exported as the static poster.
"""

from __future__ import annotations

import math
import subprocess
from pathlib import Path
from typing import Callable

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = ROOT / "assets" / "papers"
OUT_DIR = PAPER_DIR / "animations"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SIZE = (1280, 768)
FPS = 20
DURATION = 8
FRAMES = FPS * DURATION

BG = "#FCFDFE"
WHITE = "#FFFFFF"
INK = "#102D2B"
NAVY = "#17324D"
MUTED = "#647789"
LINE = "#D8E3EA"
PANEL = "#F5F8FB"
TEAL = "#2AA79A"
BLUE = "#5B82E5"
PURPLE = "#8169C7"
CORAL = "#E47878"
GOLD = "#E6A83D"
GREEN = "#4DAA78"
PALE_TEAL = "#EAF8F5"
PALE_BLUE = "#EDF3FE"
PALE_PURPLE = "#F1EEFB"
PALE_CORAL = "#FDEEEE"
PALE_GOLD = "#FFF6E5"


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    fonts = Path("C:/Windows/Fonts")
    candidates = ["segoeuib.ttf", "arialbd.ttf"] if bold else ["segoeui.ttf", "arial.ttf"]
    for candidate in candidates:
        path = fonts / candidate
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


F_MICRO = _font(13, True)
F_SMALL = _font(15)
F_SMALL_B = _font(15, True)
F_BODY = _font(17)
F_BODY_B = _font(17, True)
F_H3 = _font(20, True)
F_H2 = _font(26, True)
F_TITLE = _font(34, True)
F_NUM = _font(24, True)


def clamp(x: float) -> float:
    return max(0.0, min(1.0, x))


def smooth(x: float) -> float:
    x = clamp(x)
    return x * x * (3 - 2 * x)


def prog(t: float, start: float, end: float) -> float:
    return smooth((t - start) / max(end - start, 1e-9))


def mix(a: float, b: float, p: float) -> float:
    return a + (b - a) * clamp(p)


def hex_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def blend(a: str, b: str, p: float) -> str:
    ca, cb = hex_rgb(a), hex_rgb(b)
    vals = [round(mix(x, y, p)) for x, y in zip(ca, cb)]
    return "#" + "".join(f"{v:02x}" for v in vals)


def phase(t: float) -> int:
    if t < .23:
        return 0
    if t < .47:
        return 1
    if t < .71:
        return 2
    return 3


def canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", SIZE, BG)
    draw = ImageDraw.Draw(image)
    return image, draw


def rounded(draw: ImageDraw.ImageDraw, box, fill=WHITE, outline=LINE, radius=18, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def pill(draw: ImageDraw.ImageDraw, xy, text: str, fill=WHITE, color=NAVY, outline=LINE, font=F_MICRO):
    x, y = xy
    tw = draw.textlength(text, font=font)
    rounded(draw, (x, y, x + tw + 24, y + 29), fill, outline, 14, 1)
    draw.text((x + 12, y + 6), text, font=font, fill=color)
    return x + tw + 24


def arrow(draw: ImageDraw.ImageDraw, start, end, color=TEAL, width=3, alpha=1.0, dashed=False):
    x1, y1 = start
    x2, y2 = end
    c = blend(BG, color, alpha)
    if dashed:
        length = math.dist(start, end)
        for i in range(0, int(length), 13):
            a = i / max(length, 1)
            b = min(1, (i + 7) / max(length, 1))
            draw.line((mix(x1, x2, a), mix(y1, y2, a), mix(x1, x2, b), mix(y1, y2, b)), fill=c, width=width)
    else:
        draw.line((x1, y1, x2, y2), fill=c, width=width)
    ang = math.atan2(y2 - y1, x2 - x1)
    d = 11
    pts = [
        (x2, y2),
        (x2 - d * math.cos(ang - .45), y2 - d * math.sin(ang - .45)),
        (x2 - d * math.cos(ang + .45), y2 - d * math.sin(ang + .45)),
    ]
    draw.polygon(pts, fill=c)


def header(draw: ImageDraw.ImageDraw, tag: str, title: str, subtitle: str, stages: tuple[str, ...], t: float, accent=TEAL):
    draw.text((42, 22), tag.upper(), font=F_MICRO, fill=accent)
    draw.text((42, 47), title, font=F_TITLE, fill=NAVY)
    draw.text((42, 91), subtitle, font=F_SMALL, fill=MUTED)
    active = phase(t)
    # Keep the execution trace clear of long paper titles.  It is a compact
    # state legend, not a second headline.
    x0, gap, y = 875, 100, 52
    draw.line((x0, y + 20, x0 + gap * 3, y + 20), fill=LINE, width=2)
    for i, label in enumerate(stages):
        x = x0 + i * gap
        done = i <= active
        draw.ellipse((x - 7, y + 13, x + 7, y + 27), fill=accent if done else WHITE, outline=accent if done else "#AEBECB", width=2)
        draw.text((x - 26, y + 33), label, font=F_MICRO, fill=NAVY if i == active else MUTED, anchor="ma")


def section_title(draw: ImageDraw.ImageDraw, x: int, y: int, title: str, subtitle: str | None = None, color=NAVY):
    draw.text((x, y), title, font=F_H3, fill=color)
    if subtitle:
        draw.text((x, y + 28), subtitle, font=F_SMALL, fill=MUTED)


def bar(draw: ImageDraw.ImageDraw, box, value: float, color=TEAL, bg="#E6EDF2", label: str | None = None, number: str | None = None):
    x1, y1, x2, y2 = box
    if label:
        draw.text((x1, y1 - 21), label, font=F_SMALL, fill=MUTED)
    rounded(draw, (x1, y1, x2, y2), bg, bg, 7, 1)
    if value > .01:
        rounded(draw, (x1, y1, x1 + (x2 - x1) * clamp(value), y2), color, color, 7, 1)
    if number:
        draw.text((x2, (y1 + y2) / 2), number, font=F_SMALL_B, fill=NAVY, anchor="rm")


def node(draw: ImageDraw.ImageDraw, pos, label: str, fill=WHITE, outline=BLUE, radius=18, text=NAVY, width=3):
    x, y = pos
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=fill, outline=outline, width=width)
    draw.text((x, y + 1), label, font=F_SMALL_B, fill=text, anchor="mm")


def edge(draw: ImageDraw.ImageDraw, a, b, color="#9AB0C4", width=3, p=1.0, dashed=False):
    x1, y1 = a
    x2, y2 = b
    x2, y2 = mix(x1, x2, p), mix(y1, y2, p)
    arrow(draw, (x1, y1), (x2, y2), color=color, width=width, alpha=1, dashed=dashed)


def token(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, fill=PALE_BLUE, outline=BLUE, color=NAVY, active=True):
    w = draw.textlength(text, font=F_SMALL_B) + 22
    rounded(draw, (x, y, x + w, y + 31), fill if active else WHITE, outline if active else LINE, 8, 1)
    draw.text((x + 11, y + 7), text, font=F_SMALL_B, fill=color if active else MUTED)
    return x + w + 8


def prcd(t: float) -> Image.Image:
    image, d = canvas()
    p_data = prog(t, .05, .22)
    p_trust = prog(t, .24, .48)
    p_map = prog(t, .49, .72)
    p_out = prog(t, .70, .88)
    header(d, "PRCD-MAP / CAUSAL DISCOVERY", "Learning when an imperfect prior deserves trust",
           "Data evidence calibrates every prior edge before it shapes the MAP graph.",
           ("evidence", "calibrate", "optimize", "graph"), t, TEAL)

    rounded(d, (40, 143, 310, 714), WHITE)
    section_title(d, 64, 166, "Two imperfect views", "observations + external prior")
    d.text((64, 223), "OBSERVATIONAL EVIDENCE", font=F_MICRO, fill=TEAL)
    pts = {"A": (91, 317), "B": (186, 273), "C": (249, 348), "D": (141, 390)}
    for a, b, strength in [("A", "B", .88), ("B", "C", .76), ("A", "D", .65), ("D", "C", .18)]:
        edge(d, pts[a], pts[b], TEAL if strength > .5 else CORAL, 4 if strength > .5 else 2, p_data)
        d.text(((pts[a][0] + pts[b][0]) / 2, (pts[a][1] + pts[b][1]) / 2 - 12), f"{strength:.2f}", font=F_MICRO, fill=MUTED, anchor="mm")
    for k, pos in pts.items():
        node(d, pos, k, PALE_TEAL, TEAL, 16)
    d.line((64, 438, 286, 438), fill=LINE, width=1)
    d.text((64, 464), "EXTERNAL PRIOR", font=F_MICRO, fill=PURPLE)
    priors = [("A -> B", .91, GREEN), ("B -> C", .79, GREEN), ("D -> C", .76, CORAL), ("C -> A", .68, CORAL)]
    for i, (name, value, color) in enumerate(priors):
        y = 510 + i * 43
        d.text((68, y), name, font=F_SMALL_B, fill=NAVY)
        bar(d, (145, y + 3, 278, y + 15), value, color)

    arrow(d, (311, 410), (348, 410), TEAL, 4, p_trust)
    rounded(d, (348, 143, 818, 714), WHITE, outline=blend(LINE, TEAL, .22))
    section_title(d, 374, 166, "Per-edge trust calibration", "agreement features -> temperature tau_ij")
    d.text((374, 232), "EDGE", font=F_MICRO, fill=MUTED)
    d.text((481, 232), "DATA AGREEMENT", font=F_MICRO, fill=MUTED)
    d.text((650, 232), "LEARNED TRUST", font=F_MICRO, fill=MUTED)
    agreements = [.89, .82, .21, .13]
    targets = [.88, .79, .17, .09]
    starts = [.50, .50, .50, .50]
    for i, ((name, prior, _), agree, target, start) in enumerate(zip(priors, agreements, targets, starts)):
        y = 271 + i * 94
        fill = PALE_TEAL if agree > .5 else PALE_CORAL
        outline = TEAL if agree > .5 else CORAL
        rounded(d, (372, y - 15, 795, y + 62), fill=blend(WHITE, fill, .58), outline=blend(LINE, outline, .35), radius=13, width=1)
        d.text((390, y + 3), name, font=F_BODY_B, fill=NAVY)
        bar(d, (493, y + 8, 612, y + 21), agree * p_data, TEAL if agree > .5 else CORAL)
        trust = mix(start, target, p_trust)
        bar(d, (655, y + 8, 770, y + 21), trust, TEAL if target > .5 else CORAL)
        d.text((714, y + 40), f"tau={trust:.2f}", font=F_MICRO, fill=MUTED, anchor="mm")
    rounded(d, (384, 652, 555, 690), PALE_BLUE if phase(t) == 2 else WHITE, BLUE, 11, 2)
    d.text((469, 671), "update graph W", font=F_SMALL_B, fill=BLUE, anchor="mm")
    arrow(d, (559, 671), (607, 671), PURPLE, 2, p_map)
    rounded(d, (612, 652, 783, 690), PALE_PURPLE if phase(t) == 1 else WHITE, PURPLE, 11, 2)
    d.text((697, 671), "update trust tau", font=F_SMALL_B, fill=PURPLE, anchor="mm")

    arrow(d, (818, 410), (855, 410), TEAL, 4, p_map)
    rounded(d, (855, 143, 1240, 714), WHITE)
    section_title(d, 881, 166, "Trust-aware MAP", "prior influence is edge-specific")
    d.text((881, 233), "ADAPTIVE PENALTY", font=F_MICRO, fill=TEAL)
    for i, (name, _, _) in enumerate(priors):
        y = 268 + i * 44
        target = targets[i]
        keep = target > .5
        d.text((885, y), name, font=F_SMALL_B, fill=NAVY)
        d.text((1095, y), "retain" if keep else "attenuate", font=F_SMALL_B, fill=GREEN if keep else CORAL)
        d.text((1203, y), f"{mix(.50, target, p_map):.2f}", font=F_SMALL_B, fill=MUTED, anchor="ra")
    d.line((881, 449, 1214, 449), fill=LINE, width=1)
    d.text((881, 474), "CALIBRATED DAG", font=F_MICRO, fill=TEAL)
    out = {"A": (928, 592), "B": (1039, 528), "C": (1165, 586), "D": (1043, 657)}
    for a, b, trust in [("A", "B", .88), ("B", "C", .79), ("A", "D", .61)]:
        edge(d, out[a], out[b], GREEN, 5, p_out * trust / .88)
    for k, pos in out.items():
        node(d, pos, k, blend(WHITE, PALE_TEAL, p_out), blend(LINE, TEAL, p_out), 18)
    pill(d, (1090, 673), "low-trust edges removed", PALE_CORAL, CORAL, "#F3C8C8")
    return image


def cdv(t: float) -> Image.Image:
    image, d = canvas()
    p_world = prog(t, .05, .22)
    p_probe = prog(t, .25, .47)
    p_update = prog(t, .48, .70)
    p_policy = prog(t, .70, .88)
    header(d, "CDV / DYNAMIC DECISION-MAKING", "Test a causal story before trusting it",
           "A diagnostic action exposes disagreement, updates candidate worlds, and can veto unsafe transfer.",
           ("worlds", "diagnose", "update", "decide"), t, BLUE)

    rounded(d, (40, 143, 286, 714), WHITE)
    section_title(d, 63, 166, "Historical evidence", "one log, three interpretations")
    d.text((63, 231), "OBSERVED LOG", font=F_MICRO, fill=BLUE)
    for i, (a, r) in enumerate([("arm A", "+0.8"), ("arm B", "+0.5"), ("probe P", "unseen")]):
        y = 269 + i * 48
        rounded(d, (64, y, 261, y + 35), PANEL, LINE, 9, 1)
        d.text((78, y + 9), a, font=F_SMALL_B, fill=NAVY)
        d.text((244, y + 9), r, font=F_SMALL, fill=MUTED, anchor="ra")
    d.line((63, 431, 262, 431), fill=LINE, width=1)
    d.text((63, 458), "CAUSAL ASSUMPTION", font=F_MICRO, fill=PURPLE)
    pts = {"X": (93, 553), "A": (181, 507), "R": (222, 594)}
    edge(d, pts["X"], pts["A"], PURPLE, 3, p_world)
    edge(d, pts["X"], pts["R"], PURPLE, 3, p_world)
    edge(d, pts["A"], pts["R"], PURPLE, 3, p_world)
    for k, pos in pts.items():
        node(d, pos, k, PALE_PURPLE, PURPLE, 16)
    pill(d, (66, 651), "transfer is only a hypothesis", PALE_GOLD, GOLD, "#F1D9A8")

    arrow(d, (286, 410), (322, 410), BLUE, 4, p_world)
    rounded(d, (322, 143, 876, 714), WHITE)
    section_title(d, 348, 166, "Online-testable candidate worlds", "all worlds see the same intervention")
    worlds = [
        ("NAIVE", "reuse association", CORAL, .58, .18),
        ("ADJUSTED", "causal transfer", BLUE, .72, .22),
        ("COLD", "ignore history", TEAL, .12, .60),
    ]
    for i, (name, desc, color, pred, target_w) in enumerate(worlds):
        y = 238 + i * 128
        active = i == 2 and p_update > .35
        rounded(d, (348, y, 850, y + 105), blend(WHITE, PALE_TEAL if active else PANEL, .65), blend(LINE, color, .35), 14, 2 if active else 1)
        d.text((370, y + 17), name, font=F_BODY_B, fill=color)
        d.text((370, y + 45), desc, font=F_SMALL, fill=MUTED)
        pred_now = pred
        d.text((572, y + 17), "probe prediction", font=F_MICRO, fill=MUTED)
        bar(d, (572, y + 48, 716, y + 62), pred_now * p_world, color)
        d.text((730, y + 46), f"{pred_now:.2f}", font=F_SMALL_B, fill=NAVY)
        start_w = [.34, .51, .15][i]
        weight = mix(start_w, target_w, p_update)
        d.text((780, y + 16), "trust", font=F_MICRO, fill=MUTED, anchor="ma")
        d.text((780, y + 50), f"{weight:.2f}", font=F_NUM, fill=color, anchor="mm")
        d.text((780, y + 78), "posterior", font=F_MICRO, fill=MUTED, anchor="ma")
    y_obs = 639
    d.text((366, y_obs), "DIAGNOSTIC OBSERVATION", font=F_MICRO, fill=BLUE)
    rounded(d, (555, y_obs - 8, 844, y_obs + 31), PALE_BLUE if p_probe > .7 else WHITE, BLUE, 10, 2)
    d.text((574, y_obs + 2), "pull probe P", font=F_SMALL_B, fill=NAVY)
    reveal = "reward = 0.14" if p_probe > .72 else "reward = ?"
    d.text((819, y_obs + 2), reveal, font=F_SMALL_B, fill=CORAL if p_probe > .72 else MUTED, anchor="ra")
    if p_probe > .72:
        arrow(d, (698, 631), (698, 607), CORAL, 2, p_update)

    arrow(d, (876, 410), (912, 410), BLUE, 4, p_policy)
    rounded(d, (912, 143, 1240, 714), WHITE)
    section_title(d, 938, 166, "Policy consequence", "evidence changes deployment")
    d.text((938, 238), "WORLD LOSSES", font=F_MICRO, fill=MUTED)
    losses = [(.64, CORAL), (.58, BLUE), (.11, TEAL)]
    for i, ((name, _, _, _, _), (loss, color)) in enumerate(zip(worlds, losses)):
        y = 276 + i * 52
        d.text((940, y), name.lower(), font=F_SMALL_B, fill=NAVY)
        bar(d, (1025, y + 3, 1197, y + 17), loss * p_update, color)
    d.line((938, 438, 1214, 438), fill=LINE, width=1)
    d.text((938, 468), "TRANSFER GATE", font=F_MICRO, fill=MUTED)
    rescue_fill = blend(PALE_BLUE, WHITE, p_policy)
    veto_fill = blend(WHITE, PALE_CORAL, p_policy)
    rounded(d, (939, 509, 1213, 563), rescue_fill, blend(BLUE, LINE, p_policy), 14, 2)
    d.text((1076, 536), "CAUSAL RESCUE", font=F_BODY_B, fill=blend(BLUE, MUTED, p_policy), anchor="mm")
    rounded(d, (939, 580, 1213, 650), veto_fill, blend(LINE, CORAL, p_policy), 14, 3)
    d.text((1076, 603), "VETO UNSAFE TRANSFER", font=F_BODY_B, fill=CORAL, anchor="mm")
    d.text((1076, 628), "blend toward cold start", font=F_SMALL, fill=MUTED, anchor="mm")
    return image


def deltanar(t: float) -> Image.Image:
    image, d = canvas()
    p_edit = prog(t, .06, .23)
    p_aff = prog(t, .24, .48)
    p_gate = prog(t, .49, .71)
    p_merge = prog(t, .70, .89)
    header(d, "DELTANAR / NEURAL ALGORITHMIC REASONING", "Repair only what a graph edit invalidates",
           "Local edit awareness separates safe copying from targeted recomputation.",
           ("edit", "localize", "gate", "repair"), t, PURPLE)

    rounded(d, (40, 143, 570, 714), WHITE)
    section_title(d, 64, 166, "Previous solution + graph edit", "the old witness is still useful")
    pts = {"s": (104, 384), "a": (213, 276), "b": (226, 500), "c": (356, 291), "d": (367, 486), "t": (495, 383)}
    all_edges = [("s", "a"), ("s", "b"), ("a", "c"), ("b", "d"), ("c", "t"), ("d", "t"), ("a", "d")]
    for a, b in all_edges:
        old_path = (a, b) in [("s", "a"), ("a", "c"), ("c", "t")]
        color = BLUE if old_path else "#B9C7D3"
        width = 5 if old_path else 2
        if (a, b) == ("a", "c") and p_edit > .08:
            edge(d, pts[a], pts[b], CORAL, 4, 1, dashed=True)
            x = mix(pts[a][0], pts[b][0], .5)
            y = mix(pts[a][1], pts[b][1], .5)
            d.line((x - 10, y - 10, x + 10, y + 10), fill=CORAL, width=4)
            d.line((x - 10, y + 10, x + 10, y - 10), fill=CORAL, width=4)
        else:
            edge(d, pts[a], pts[b], color, width, 1)
    affected = {"c": p_aff, "t": p_aff, "d": prog(t, .35, .53)}
    for k, pos in pts.items():
        q = affected.get(k, 0)
        fill = blend(PALE_BLUE, PALE_CORAL, q) if k in ("c", "t") else blend(WHITE, PALE_PURPLE, q)
        outline = blend(PURPLE, CORAL, q) if q else PURPLE
        node(d, pos, k, fill, outline, 20)
    d.text((65, 607), "OLD WITNESS", font=F_MICRO, fill=BLUE)
    x = 65
    for name in ["s", "a", "c", "t"]:
        x = token(d, x, 635, name, PALE_BLUE, BLUE)
    pill(d, (366, 628), "edge a->c deleted", PALE_CORAL if p_edit > .1 else WHITE, CORAL, "#F0C0C0")

    arrow(d, (570, 410), (607, 410), PURPLE, 4, p_aff)
    rounded(d, (607, 143, 925, 714), WHITE)
    section_title(d, 632, 166, "Two learned gates", "node-level update policy")
    rounded(d, (633, 239, 899, 386), blend(WHITE, PALE_CORAL, .45 * p_aff), CORAL, 14, 2)
    d.text((655, 258), "AFFECTED-REGION GATE", font=F_MICRO, fill=CORAL)
    d.text((655, 291), "Where can the edit matter?", font=F_BODY_B, fill=NAVY)
    for i, (name, target) in enumerate([("c", .96), ("t", .91), ("d", .48), ("s", .04)]):
        y = 329 + (i % 2) * 36
        x = 655 + (i // 2) * 122
        d.text((x, y), name, font=F_SMALL_B, fill=NAVY)
        bar(d, (x + 23, y + 3, x + 97, y + 15), target * p_aff, CORAL)
    rounded(d, (633, 417, 899, 585), blend(WHITE, PALE_TEAL, .45 * p_gate), TEAL, 14, 2)
    d.text((655, 438), "COPY-SAFETY GATE", font=F_MICRO, fill=TEAL)
    d.text((655, 471), "Can the old witness be reused?", font=F_BODY_B, fill=NAVY)
    for i, (name, target) in enumerate([("s", .98), ("a", .95), ("c", .06), ("t", .08)]):
        y = 511 + (i % 2) * 36
        x = 655 + (i // 2) * 122
        d.text((x, y), name, font=F_SMALL_B, fill=NAVY)
        bar(d, (x + 23, y + 3, x + 97, y + 15), target * p_gate, TEAL)
    rounded(d, (644, 622, 888, 680), PANEL, LINE, 12, 1)
    d.text((766, 641), "safe -> COPY", font=F_SMALL_B, fill=TEAL, anchor="mm")
    d.text((766, 663), "unsafe -> RECOMPUTE", font=F_SMALL_B, fill=CORAL, anchor="mm")

    arrow(d, (925, 410), (962, 410), PURPLE, 4, p_gate)
    rounded(d, (962, 143, 1240, 714), WHITE)
    section_title(d, 987, 166, "Merged solution", "copy stable; repair local")
    out = {"s": (1015, 372), "a": (1081, 284), "b": (1081, 491), "d": (1160, 470), "t": (1201, 367)}
    for a, b, active, color in [
        ("s", "a", 1, TEAL), ("a", "d", p_merge, CORAL), ("d", "t", p_merge, CORAL),
        ("s", "b", 1, "#B9C7D3"), ("b", "d", 1, "#B9C7D3")]:
        edge(d, out[a], out[b], color, 5 if color in (TEAL, CORAL) else 2, active)
    for k, pos in out.items():
        changed = k in ("d", "t")
        node(d, pos, k, blend(WHITE, PALE_CORAL if changed else PALE_TEAL, p_merge if changed else 1), CORAL if changed else TEAL, 18)
    d.text((988, 584), "UPDATED WITNESS", font=F_MICRO, fill=PURPLE)
    x = 989
    for i, name in enumerate(["s", "a", "d", "t"]):
        x = token(d, x, 612, name, PALE_CORAL if i >= 2 else PALE_TEAL, CORAL if i >= 2 else TEAL, active=p_merge > .15 or i < 2)
    d.text((1100, 673), "global consistency, local work", font=F_SMALL_B, fill=NAVY, anchor="mm")
    return image


def failure_learning(t: float) -> Image.Image:
    image, d = canvas()
    p_claim = prog(t, .05, .22)
    p_freeze = prog(t, .24, .45)
    p_controls = prog(t, .46, .73)
    p_report = prog(t, .72, .89)
    header(d, "CONTROLLED EVALUATION / RESEARCH AGENTS", "Failure-learning claims need matched controls",
           "Freeze the agent output, vary the control lens, and report only what the evidence supports.",
           ("claim", "freeze", "control", "report"), t, CORAL)

    rounded(d, (40, 143, 328, 714), WHITE)
    section_title(d, 64, 166, "Failure memory", "same source; matched targets")
    d.text((64, 231), "SOURCE FAILURE", font=F_MICRO, fill=CORAL)
    rounded(d, (65, 263, 303, 370), PALE_CORAL, "#F0CACA", 13, 2)
    x = 82
    for name, ok in [("inspect", True), ("edit", True), ("verify", False)]:
        x = token(d, x, 286, name, PALE_CORAL if not ok else PANEL, CORAL if not ok else LINE, active=True)
    d.text((184, 345), "failure: skipped validation", font=F_SMALL_B, fill=CORAL, anchor="mm")
    d.text((64, 411), "TARGET FAMILIES", font=F_MICRO, fill=MUTED)
    rounded(d, (65, 445, 303, 505), PALE_TEAL, "#BFE3DB", 12, 1)
    d.text((85, 461), "NEAR", font=F_SMALL_B, fill=TEAL)
    d.text((85, 482), "same invariant", font=F_SMALL, fill=MUTED)
    rounded(d, (65, 520, 303, 580), PALE_GOLD, "#EDD49D", 12, 1)
    d.text((85, 536), "CONTRASTIVE", font=F_SMALL_B, fill=GOLD)
    d.text((85, 557), "different invariant", font=F_SMALL, fill=MUTED)
    pill(d, (67, 626), "claim: learns from failure", PALE_CORAL if p_claim else WHITE, CORAL, "#F0CACA")

    arrow(d, (328, 410), (365, 410), CORAL, 4, p_freeze)
    rounded(d, (365, 143, 744, 714), WHITE)
    section_title(d, 390, 166, "Frozen probe battery", "outputs never change across controls")
    probes = [
        ("TRACE", "repair the failed step", BLUE),
        ("REFLECT", "name the invariant", PURPLE),
        ("TRANSFER", "solve a changed target", TEAL),
        ("EXECUTE", "validate the artifact", GREEN),
    ]
    for i, (name, desc, color) in enumerate(probes):
        y = 240 + i * 96
        rounded(d, (392, y, 716, y + 70), blend(WHITE, PANEL, p_freeze), blend(LINE, color, .45 * p_freeze), 12, 2 if p_freeze > .7 else 1)
        d.text((412, y + 14), name, font=F_BODY_B, fill=color)
        d.text((412, y + 42), desc, font=F_SMALL, fill=MUTED)
        if p_freeze > .75:
            pill(d, (624, y + 21), "FROZEN", WHITE, MUTED, LINE)
    rounded(d, (395, 642, 711, 682), PALE_BLUE, "#C4D4F5", 10, 1)
    d.text((553, 662), "same model / fixed decoding / fixed outputs", font=F_SMALL_B, fill=BLUE, anchor="mm")

    arrow(d, (744, 410), (780, 410), CORAL, 4, p_controls)
    rounded(d, (780, 143, 1240, 714), WHITE)
    section_title(d, 805, 166, "Claim-matched control matrix", "one score cannot support every claim")
    cols = ["exact", "core", "transfer", "exec"]
    rows = ["TRACE", "REFLECT", "TRANSFER", "EXECUTE"]
    x0, y0, cw, rh = 914, 252, 72, 54
    for j, name in enumerate(cols):
        d.text((x0 + j * cw + cw / 2, 222), name, font=F_MICRO, fill=MUTED, anchor="mm")
    support = [
        [1, 1, 0, 0],
        [0, 1, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 0, 1],
    ]
    outcomes = [
        [1, 1, 0, 0],
        [0, 1, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1],
    ]
    for i, row in enumerate(rows):
        d.text((890, y0 + i * rh + 19), row, font=F_SMALL_B, fill=NAVY, anchor="ra")
        for j in range(4):
            reveal = prog(t, .47 + (i * 4 + j) * .012, .58 + (i * 4 + j) * .012)
            relevant = support[i][j]
            passed = outcomes[i][j]
            fill = WHITE
            outline = LINE
            mark = ""
            color = MUTED
            if reveal > .5 and relevant:
                fill = PALE_TEAL if passed else PALE_CORAL
                outline = GREEN if passed else CORAL
                mark = "OK" if passed else "MISS"
                color = GREEN if passed else CORAL
            elif reveal > .5:
                fill = PANEL
                mark = "--"
            box = (x0 + j * cw, y0 + i * rh, x0 + j * cw + 58, y0 + i * rh + 38)
            rounded(d, box, fill, outline, 9, 1)
            d.text(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2), mark, font=F_MICRO, fill=color, anchor="mm")
    rounded(d, (806, 493, 1214, 676), blend(WHITE, "#EEF3F8", p_report), blend(LINE, NAVY, .3 * p_report), 15, 2)
    d.text((830, 516), "AUDITABLE CLAIM REPORT", font=F_MICRO, fill=NAVY)
    report = [
        ("repairs the local failure", True),
        ("identifies the invariant", True),
        ("transfers to changed targets", False),
        ("produces an executable artifact", True),
    ]
    for i, (text, ok) in enumerate(report):
        y = 550 + i * 29
        color = GREEN if ok else CORAL
        symbol = "YES" if ok else "NOT SHOWN"
        d.text((833, y), symbol, font=F_MICRO, fill=color)
        d.text((921, y), text, font=F_SMALL, fill=NAVY if p_report > .4 else MUTED)
    return image


def bounded_context(t: float) -> Image.Image:
    image, d = canvas()
    p_ground = prog(t, .04, .20)
    p_memory = prog(t, .20, .48)
    p_route = prog(t, .48, .72)
    p_answer = prog(t, .71, .89)
    header(d, "BOUNDED PATH CONTEXT / KGQA", "Exact symbolic memory, bounded language context",
           "The controller keeps the full path while the LLM sees only the last K hops.",
           ("ground", "remember", "route", "answer"), t, GOLD)

    rounded(d, (40, 143, 430, 714), WHITE)
    section_title(d, 64, 166, "Question-grounded KG", "symbolic beam expansion")
    pill(d, (64, 220), "Who directed the film starring Ada?", PALE_GOLD, NAVY, "#E9D49F")
    pts = {"Ada": (99, 373), "Film": (205, 294), "Book": (208, 480), "Dir": (337, 270), "Actor": (337, 393), "City": (337, 526)}
    edges = [
        ("Ada", "Film", "starred_in", GOLD, .24),
        ("Ada", "Book", "wrote", "#B9C7D3", .30),
        ("Film", "Dir", "directed_by", TEAL, .52),
        ("Film", "Actor", "cast", "#B9C7D3", .60),
        ("Book", "City", "published_in", "#B9C7D3", .60),
    ]
    for a, b, rel, color, start in edges:
        active = prog(t, start, start + .14) if color in (GOLD, TEAL) else .35 * p_memory
        edge(d, pts[a], pts[b], color, 5 if color in (GOLD, TEAL) else 2, active)
        if active > .5:
            d.text(((pts[a][0] + pts[b][0]) / 2, (pts[a][1] + pts[b][1]) / 2 - 12), rel, font=F_MICRO, fill=color, anchor="mm")
    for k, pos in pts.items():
        active = k in ("Ada", "Film", "Dir")
        node(d, pos, k, PALE_GOLD if k == "Ada" else (PALE_TEAL if active else WHITE), GOLD if k == "Ada" else (TEAL if active else LINE), 19 if len(k) < 5 else 25)
    pill(d, (67, 635), f"beam width B = 2", PALE_BLUE, BLUE, "#CAD8F3")

    arrow(d, (430, 410), (466, 410), GOLD, 4, p_memory)
    rounded(d, (466, 143, 887, 714), WHITE)
    section_title(d, 492, 166, "Dual-memory interface", "complete state outside; suffix inside")
    d.text((492, 232), "EXACT SYMBOLIC MEMORY  B^t", font=F_MICRO, fill=TEAL)
    rounded(d, (492, 260, 860, 385), PALE_TEAL, "#BFE2DA", 13, 2)
    mem_tokens = ["Ada", "starred_in", "Film", "directed_by", "Dir"]
    reveal_count = 1 + int(p_memory * 4.99)
    memory_positions = [(510, 282), (568, 282), (670, 282), (510, 322), (626, 322)]
    for name, (x, y) in zip(mem_tokens[:reveal_count], memory_positions):
        token(d, x, y, name, PALE_TEAL, TEAL, active=True)
    d.text((509, 359), "full paths + scores remain exact", font=F_SMALL, fill=MUTED)
    d.text((492, 414), "BOUNDED LANGUAGE VIEW  h_K(B^t)", font=F_MICRO, fill=GOLD)
    rounded(d, (492, 442, 860, 579), PALE_GOLD, "#EAD39A", 13, 2)
    k = 2
    visible = mem_tokens[max(0, reveal_count - (2 * k + 1)):reveal_count]
    visible_positions = [(510, 466), (568, 466), (670, 466), (510, 506), (626, 506)]
    for name, (x, y) in zip(visible, visible_positions):
        token(d, x, y, name, PALE_GOLD, GOLD, active=True)
    d.text((509, 552), "only the last K hops are verbalized", font=F_SMALL, fill=MUTED)
    pill(d, (492, 620), "outside prompt: complete path", PALE_TEAL, TEAL, "#C2E2DB")
    pill(d, (682, 620), "inside prompt: suffix", PALE_GOLD, GOLD, "#E9D39D")

    arrow(d, (887, 410), (923, 410), GOLD, 4, p_route)
    rounded(d, (923, 143, 1240, 714), WHITE)
    section_title(d, 948, 166, "LLM relation router", "route; controller expands")
    d.text((949, 234), "CANDIDATE RELATIONS", font=F_MICRO, fill=MUTED)
    rels = [("directed_by", .91, TEAL), ("cast", .34, BLUE), ("genre", .18, PURPLE)]
    for i, (name, target, color) in enumerate(rels):
        y = 274 + i * 63
        d.text((950, y), name, font=F_SMALL_B, fill=NAVY)
        bar(d, (1058, y + 5, 1206, y + 19), target * p_route, color)
    rounded(d, (949, 471, 1214, 528), PALE_BLUE, "#C7D6F2", 13, 2)
    d.text((1081, 499), "expand top-w -> prune to B", font=F_BODY_B, fill=BLUE, anchor="mm")
    arrow(d, (1081, 531), (1081, 564), TEAL, 3, p_answer)
    rounded(d, (949, 567, 1214, 677), blend(WHITE, PALE_TEAL, p_answer), blend(LINE, TEAL, p_answer), 14, 3)
    d.text((974, 588), "ANSWER + EVIDENCE", font=F_MICRO, fill=TEAL)
    d.text((1081, 622), "Dir", font=F_H2, fill=NAVY, anchor="mm")
    d.text((1081, 653), "Ada -> Film -> Dir", font=F_SMALL_B, fill=TEAL, anchor="mm")
    return image


def decoder_audit(t: float) -> Image.Image:
    image, d = canvas()
    p_fix = prog(t, .04, .22)
    p_grid = prog(t, .22, .52)
    p_flip = prog(t, .52, .73)
    p_effect = prog(t, .71, .89)
    header(d, "RECIPE-CONTROLLED KGC AUDIT", "Separate decoder, encoder depth, and recipe",
           "A fixed training recipe turns architectural folklore into an identifiable factorial comparison.",
           ("freeze", "factorial", "compare", "attribute"), t, GREEN)

    rounded(d, (40, 143, 317, 714), WHITE)
    section_title(d, 64, 166, "Freeze the recipe", "same data and optimization")
    items = [
        ("loss", "1-vs-all CE"),
        ("regularize", "label smoothing"),
        ("optimize", "AdamW + schedule"),
        ("evaluate", "filtered MRR"),
    ]
    for i, (key, value) in enumerate(items):
        y = 243 + i * 77
        rounded(d, (65, y, 291, y + 57), blend(WHITE, PALE_TEAL, .5 * p_fix), blend(LINE, GREEN, .35 * p_fix), 11, 1)
        d.text((82, y + 11), key.upper(), font=F_MICRO, fill=GREEN)
        d.text((82, y + 31), value, font=F_SMALL_B, fill=NAVY)
    pill(d, (66, 590), "one controlled recipe", PALE_TEAL, GREEN, "#C4E1D4")
    pill(d, (66, 634), "same seeds + protocol", PANEL, MUTED, LINE)

    arrow(d, (317, 410), (353, 410), GREEN, 4, p_grid)
    rounded(d, (353, 143, 893, 714), WHITE)
    section_title(d, 378, 166, "Decoder x depth grid", "populate every cell, not one selected row")
    datasets = ["WN18RR", "UMLS"]
    active_dataset = 1 if p_flip > .58 else 0
    x = 378
    for i, name in enumerate(datasets):
        fill = PALE_BLUE if i == active_dataset else WHITE
        x = pill(d, (x, 218), name, fill, BLUE if i == active_dataset else MUTED, BLUE if i == active_dataset else LINE) + 8
    depths = ["L=0", "L=1", "L=2", "L=3"]
    rows = ["ComplEx", "DistMult"]
    wn = [[.4849, .4533, .4810, .4775], [.4731, .4410, .4670, .4743]]
    # UMLS was measured at the paper's fixed L=2 recipe.  The other cells are
    # intentionally blank; inventing a full depth sweep would misstate evidence.
    umls = [[None, None, .8302, None], [None, None, .8748, None]]
    values = umls if active_dataset else wn
    x0, y0, cw, rh = 483, 299, 93, 94
    for j, dep in enumerate(depths):
        d.text((x0 + j * cw + 39, 273), dep, font=F_SMALL_B, fill=NAVY, anchor="mm")
    for i, row in enumerate(rows):
        d.text((460, y0 + i * rh + 39), row, font=F_SMALL_B, fill=PURPLE if i == 0 else TEAL, anchor="ra")
        for j, value in enumerate(values[i]):
            idx = i * 4 + j
            reveal = prog(t, .22 + idx * .025, .39 + idx * .025)
            measured = [v for row_values in values for v in row_values if v is not None]
            winner = value is not None and value == max(measured)
            fill = blend(WHITE, PALE_TEAL if winner else PALE_BLUE, reveal * (.85 if winner else .42))
            outline = blend(LINE, GREEN if winner else BLUE, reveal * (.7 if winner else .22))
            box = (x0 + j * cw, y0 + i * rh, x0 + j * cw + 78, y0 + i * rh + 72)
            rounded(d, box, fill, outline, 12, 2 if winner else 1)
            shown = value if reveal > .4 else None
            display = f"{shown:.4f}" if shown is not None else ("--" if value is None and reveal > .4 else "...")
            d.text(((box[0] + box[2]) / 2, box[1] + 27), display, font=F_BODY_B, fill=NAVY if shown is not None else MUTED, anchor="mm")
            d.text(((box[0] + box[2]) / 2, box[1] + 51), "MRR" if shown is not None else "not swept", font=F_MICRO, fill=MUTED, anchor="mm")
    rounded(d, (379, 515, 867, 676), PANEL, LINE, 14, 1)
    d.text((402, 536), "CONTROLLED READOUT", font=F_MICRO, fill=GREEN)
    if active_dataset:
        headline = "DistMult wins on low edges / relation"
        detail = "UMLS: 0.8748 vs 0.8302  |  reversal"
        color = TEAL
    else:
        headline = "Depth ranking depends on decoder"
        detail = "ComplEx peaks at L=0; DistMult at L=3"
        color = BLUE
    d.text((402, 575), headline, font=F_H3, fill=color)
    d.text((402, 612), detail, font=F_BODY, fill=NAVY)
    bar(d, (402, 641, 842, 654), p_flip if not active_dataset else 1, color)

    arrow(d, (893, 410), (929, 410), GREEN, 4, p_effect)
    rounded(d, (929, 143, 1240, 714), WHITE)
    section_title(d, 954, 166, "Factor attribution", "compare effect ranges")
    effects = [
        ("decoder x dataset", .134, PURPLE),
        ("encoder x dataset", .075, BLUE),
        ("recipe controls", .041, GREEN),
    ]
    for i, (name, value, color) in enumerate(effects):
        y = 264 + i * 94
        d.text((955, y), name, font=F_SMALL_B, fill=NAVY)
        bar(d, (955, y + 31, 1207, y + 48), value / .15 * p_effect, color)
        d.text((1207, y + 1), f"range {value:.3f}", font=F_SMALL_B, fill=color, anchor="ra")
    rounded(d, (955, 560, 1214, 665), blend(WHITE, PALE_PURPLE, p_effect), blend(LINE, PURPLE, .6 * p_effect), 14, 2)
    d.text((1084, 590), "HIGHER-LEVERAGE AXIS", font=F_MICRO, fill=PURPLE, anchor="mm")
    d.text((1084, 625), "decoder choice", font=F_H2, fill=NAVY, anchor="mm")
    return image


SCENES: tuple[tuple[str, Callable[[float], Image.Image]], ...] = (
    ("prcd-map", prcd),
    ("testing-before-trusting", cdv),
    ("deltanar", deltanar),
    ("failure-learning", failure_learning),
    ("bounded-path-context", bounded_context),
    ("decoder-audit", decoder_audit),
)


def encode(name: str, renderer: Callable[[float], Image.Image]) -> None:
    output = OUT_DIR / f"{name}.mp4"
    poster = PAPER_DIR / f"{name}.png"
    renderer(.90).save(poster, optimize=True)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    command = [
        ffmpeg, "-y", "-loglevel", "error",
        "-f", "rawvideo", "-vcodec", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{SIZE[0]}x{SIZE[1]}", "-r", str(FPS), "-i", "-",
        "-an", "-vcodec", "libx264", "-preset", "slow", "-crf", "21",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(output),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    assert process.stdin is not None
    try:
        for index in range(FRAMES):
            t = index / FRAMES
            process.stdin.write(renderer(t).tobytes())
    finally:
        process.stdin.close()
    if process.wait() != 0:
        raise RuntimeError(f"ffmpeg failed while encoding {name}")
    print(f"{name}: poster {poster.stat().st_size / 1024:.0f} KiB, video {output.stat().st_size / 1024:.0f} KiB")


def main() -> None:
    for name, renderer in SCENES:
        encode(name, renderer)


if __name__ == "__main__":
    main()
