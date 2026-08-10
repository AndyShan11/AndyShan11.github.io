from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle


OUT = Path(__file__).resolve().parents[1] / "assets" / "papers"
OUT.mkdir(parents=True, exist_ok=True)

NAVY = "#102A43"
INK = "#243B53"
MUTED = "#627D98"
LINE = "#C9D8E6"
PAPER = "#F8FBFD"
WHITE = "#FFFFFF"
BLUE = "#5B8FF9"
TEAL = "#45B8AC"
GREEN = "#67C587"
AMBER = "#F3B562"
CORAL = "#E97979"
PURPLE = "#8E7DBE"


def canvas(title, kicker, accent=TEAL):
    fig, ax = plt.subplots(figsize=(12, 7.2), dpi=200)
    fig.patch.set_facecolor(WHITE)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 1, facecolor=WHITE, edgecolor="none"))
    ax.add_patch(Rectangle((0.035, 0.925), 0.045, 0.006, facecolor=accent, edgecolor="none"))
    ax.text(0.035, 0.89, kicker.upper(), fontsize=8.2, color=accent, weight="bold", family="DejaVu Sans")
    ax.text(0.035, 0.835, title, fontsize=16.2, color=NAVY, weight="bold", family="DejaVu Sans")
    ax.plot([0.035, 0.965], [0.80, 0.80], color=LINE, lw=0.8)
    return fig, ax


def card(ax, x, y, w, h, title, subtitle="", color=BLUE, fill=WHITE, lw=1.0, title_size=8.7, align="left"):
    shadow = FancyBboxPatch((x + 0.004, y - 0.006), w, h, boxstyle="round,pad=0.008,rounding_size=0.014",
                            facecolor="#DCE7EF", edgecolor="none", alpha=0.55, zorder=1)
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.008,rounding_size=0.014",
                         facecolor=fill, edgecolor=color, linewidth=lw, zorder=2)
    ax.add_patch(shadow)
    ax.add_patch(box)
    tx = x + (w / 2 if align == "center" else 0.016)
    ha = "center" if align == "center" else "left"
    title_color = WHITE if fill == NAVY else NAVY
    subtitle_color = "#D9E6EF" if fill == NAVY else MUTED
    compact = h < 0.105
    title_y = y + h * 0.64 if compact else y + h - 0.032
    ax.text(tx, title_y, title, fontsize=min(title_size, 7.8) if compact else title_size,
            color=title_color, weight="bold", ha=ha, va="center" if compact else "top", zorder=3)
    if subtitle:
        subtitle_y = y + h * 0.24 if compact else y + 0.025
        ax.text(tx, subtitle_y, subtitle, fontsize=6.2 if compact else 6.6, color=subtitle_color,
                ha=ha, va="center" if compact else "bottom", zorder=3, linespacing=1.25)
    return box


def pill(ax, x, y, text, color=TEAL, width=None, fill=None, fontsize=6.8):
    width = width or max(0.075, 0.012 + 0.0092 * len(text))
    fill = fill or color + "18"
    p = FancyBboxPatch((x, y), width, 0.042, boxstyle="round,pad=0.004,rounding_size=0.018",
                       facecolor=fill, edgecolor=color, linewidth=0.8, zorder=4)
    ax.add_patch(p)
    ax.text(x + width / 2, y + 0.021, text, ha="center", va="center", fontsize=fontsize, color=INK, weight="bold", zorder=5)
    return p


def arrow(ax, start, end, color=MUTED, lw=1.25, rad=0.0, dashed=False):
    a = FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=10, linewidth=lw,
                        color=color, connectionstyle=f"arc3,rad={rad}", linestyle="--" if dashed else "-", zorder=6)
    ax.add_patch(a)
    return a


def phase(ax, x, number, title, color=TEAL):
    ax.add_patch(Circle((x, 0.76), 0.018, facecolor=color, edgecolor="none", zorder=5))
    ax.text(x, 0.76, str(number), ha="center", va="center", fontsize=7.2, color=WHITE, weight="bold", zorder=6)
    ax.text(x + 0.027, 0.76, title, va="center", fontsize=7.4, color=MUTED, weight="bold")


def tiny_graph(ax, x, y, w, h, nodes, edges, colors=None, dashed=None):
    colors = colors or [BLUE] * len(nodes)
    dashed = dashed or set()
    pts = [(x + px * w, y + py * h) for px, py in nodes]
    for idx, (i, j) in enumerate(edges):
        arrow(ax, pts[i], pts[j], color=CORAL if idx in dashed else "#8CA6B8", lw=0.85,
              dashed=idx in dashed)
    for (px, py), c in zip(pts, colors):
        ax.add_patch(Circle((px, py), 0.010, facecolor=WHITE, edgecolor=c, linewidth=1.5, zorder=8))
        ax.add_patch(Circle((px, py), 0.004, facecolor=c, edgecolor="none", zorder=9))


def save(fig, name):
    fig.savefig(OUT / name, dpi=200, bbox_inches="tight", pad_inches=0.02, facecolor=WHITE)
    plt.close(fig)


def prcd():
    fig, ax = canvas("Learning how much to trust an imperfect prior", "PRCD-MAP · METHOD OVERVIEW", TEAL)
    for x, n, t in [(0.055, 1, "Evidence"), (0.34, 2, "Edge-wise calibration"), (0.69, 3, "Trust-aware discovery")]:
        phase(ax, x, n, t, TEAL)

    card(ax, 0.035, 0.47, 0.22, 0.22, "Observational time series", "local fit · residual dependence", BLUE, PAPER)
    for i, c in enumerate([BLUE, TEAL, PURPLE]):
        xs = [0.055 + k * 0.016 for k in range(10)]
        ys = [0.555 + i * 0.028 + 0.012 * ((k + i) % 4 - 1.5) for k in range(10)]
        ax.plot(xs, ys, color=c, lw=1.25, zorder=5)
    card(ax, 0.035, 0.18, 0.22, 0.20, "Imperfect structural prior", "helpful and contradictory edges", CORAL, PAPER)
    tiny_graph(ax, 0.07, 0.235, 0.15, 0.10,
               [(0.05, .5), (.32, .9), (.52, .2), (.73, .72), (.95, .42)],
               [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4)], [BLUE, BLUE, TEAL, PURPLE, GREEN], {3})

    card(ax, 0.31, 0.18, 0.31, 0.51, "Edge-wise Trust Calibrator", "posterior trust  τᵢⱼ ∈ [0,1]", TEAL, "#F0FBF8", 1.3, 10)
    pill(ax, 0.335, 0.55, "data fit", BLUE, 0.075)
    pill(ax, 0.425, 0.55, "topology", PURPLE, 0.083)
    pill(ax, 0.522, 0.55, "agreement", CORAL, 0.083)
    arrow(ax, (0.373, 0.545), (0.41, 0.47), BLUE)
    arrow(ax, (0.467, 0.545), (0.467, 0.47), PURPLE)
    arrow(ax, (0.563, 0.545), (0.525, 0.47), CORAL)
    card(ax, 0.36, 0.38, 0.215, 0.085, "Empirical Bayes  +  topology MLP", "shrink noisy edge evidence", TEAL, WHITE, 1, 8.1, "center")
    arrow(ax, (0.468, 0.375), (0.468, 0.30), TEAL, 1.6)
    ax.add_patch(FancyBboxPatch((0.36, 0.235), 0.215, 0.065, boxstyle="round,pad=0.006,rounding_size=0.015",
                                facecolor=NAVY, edgecolor=NAVY, zorder=4))
    ax.text(0.468, 0.268, "τᵢⱼ   edge-specific confidence", color=WHITE, ha="center", va="center", fontsize=8, weight="bold", zorder=5)

    card(ax, 0.675, 0.39, 0.29, 0.30, "Prior-aware MAP objective", "data likelihood + adaptive regularization", AMBER, "#FFF9EF", 1.2, 10)
    ax.text(0.70, 0.53, "ℒ(A) + λ₁(τ)‖A‖₁ + λ₂(τ)‖A − A⁰‖²", fontsize=7.2, color=NAVY, weight="bold", zorder=5)
    pill(ax, 0.70, 0.445, "low τ → data only", CORAL, 0.112, "#FFF0F0")
    pill(ax, 0.83, 0.445, "high τ → retain", GREEN, 0.108, "#EFFAF2")
    arrow(ax, (0.62, 0.435), (0.675, 0.50), TEAL, 1.6)
    card(ax, 0.675, 0.18, 0.29, 0.14, "Calibrated causal graph", "", GREEN, "#F1FAF4", 1.2, 9.5)
    tiny_graph(ax, 0.73, 0.220, 0.18, 0.048, [(0, .45), (.26, .85), (.48, .2), (.72, .72), (1, .4)],
               [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4)], [BLUE, BLUE, TEAL, PURPLE, GREEN], {1})
    ax.text(.70,.195,"retain · attenuate · reject",fontsize=6.2,color=MUTED,zorder=5)
    arrow(ax, (0.82, 0.39), (0.82, 0.32), GREEN, 1.6)
    save(fig, "prcd-map.png")


def cdv():
    fig, ax = canvas("Testing causal assumptions before they steer decisions", "CAUSAL-SKEPTIC BANDITS · ONLINE LOOP", BLUE)
    for x, n, t in [(0.055, 1, "Initialize worlds"), (0.34, 2, "Probe and update"), (0.69, 3, "Rescue or veto")]:
        phase(ax, x, n, t, BLUE)
    card(ax, 0.035, 0.45, 0.22, 0.24, "Historical evidence", "logged actions · outcomes · context", BLUE, PAPER)
    for i in range(5):
        ax.add_patch(Rectangle((0.057, 0.505 + i * 0.025), 0.14 + (i % 3) * 0.018, 0.010,
                               facecolor=[BLUE, TEAL, PURPLE][i % 3], edgecolor="none", alpha=.75, zorder=5))
    card(ax, 0.035, 0.18, 0.22, 0.18, "Unreliable causal graph", "treated as a hypothesis—not truth", CORAL, "#FFF4F4")
    tiny_graph(ax, .073, .213, .145, .09, [(0,.5),(.3,.9),(.52,.2),(.78,.72),(1,.42)], [(0,1),(0,2),(1,3),(2,3),(3,4)], dashed={2})

    card(ax, 0.305, 0.18, 0.315, 0.51, "Competing causal worlds", "posterior weight is updated after every action", PURPLE, "#F7F4FC", 1.2, 10)
    worlds = [("Naive", "history predicts directly", BLUE), ("Causal", "graph transports effects", TEAL), ("Cold", "ignore historical claims", AMBER)]
    for i, (name, sub, col) in enumerate(worlds):
        y = 0.55 - i * 0.105
        card(ax, 0.335, y, 0.255, 0.074, name, sub, col, WHITE, .9, 8.2)
        ax.add_patch(Rectangle((0.51, y + .017), 0.06, .008, facecolor=LINE, edgecolor="none", zorder=5))
        ax.add_patch(Rectangle((0.51, y + .017), [0.032, 0.047, 0.021][i], .008, facecolor=col, edgecolor="none", zorder=6))
    pill(ax, .36, .225, "diagnostic action  aᵗ", CORAL, .205, "#FFF0F0", 7.4)
    arrow(ax, (.257, .49), (.305, .49), BLUE, 1.5)
    arrow(ax, (.257, .27), (.305, .31), CORAL, 1.5)

    card(ax, .675, .51, .29, .18, "Interventional feedback", "reward + prediction error by world", BLUE, "#F2F7FF", 1.1, 9.5)
    ax.plot([.70,.75,.80,.85,.90,.94], [.57,.595,.555,.62,.58,.635], color=BLUE, lw=1.6, zorder=5)
    for x,y in zip([.70,.75,.80,.85,.90,.94], [.57,.595,.555,.62,.58,.635]): ax.add_patch(Circle((x,y),.006,facecolor=WHITE,edgecolor=BLUE,lw=1,zorder=6))
    card(ax, .675, .30, .29, .15, "Sequential trust update", "", PURPLE, "#F7F4FC", 1.1, 9.2)
    pill(ax, .715, .335, "world posterior  wᵗ", PURPLE, .21, "#EEE9F8", 7.2)
    arrow(ax, (.82,.51), (.82,.45), BLUE, 1.5)
    card(ax, .675, .12, .29, .12, "Causal rescue  /  causal veto", "act only when evidence supports transport", GREEN, "#F0FAF3", 1.3, 9.2)
    arrow(ax, (.82,.30), (.82,.24), GREEN, 1.6)
    arrow(ax, (.675,.36), (.62,.31), PURPLE, 1.1, rad=-.18)
    ax.text(.615,.285,"next round",fontsize=6.8,color=MUTED,ha="right")
    save(fig, "testing-before-trusting.png")


def delta():
    fig, ax = canvas("Incremental reasoning by selective reuse and repair", "DELTANAR · EDIT-AWARE NEURAL ALGORITHMS", PURPLE)
    for x, n, t in [(0.055, 1, "Read the edit"), (0.34, 2, "Gate state reuse"), (0.72, 3, "Merge the solution")]:
        phase(ax, x, n, t, PURPLE)
    card(ax,.035,.43,.21,.26,"Post-edit graph  Gᵗ","added / deleted edge",CORAL,PAPER)
    tiny_graph(ax,.07,.49,.14,.13,[(0,.5),(.25,.85),(.48,.15),(.7,.73),(1,.42)],[(0,1),(0,2),(1,3),(2,3),(3,4)],dashed={3})
    card(ax,.035,.18,.21,.17,"Previous solution  Hᵗ⁻¹","distance · parent · witness",BLUE,"#F2F7FF")
    for i,t in enumerate(["d(v)","π(v)","w(v)"]): pill(ax,.055+i*.06,.22,t,BLUE,.052,"#EAF2FF",6.6)

    card(ax,.29,.18,.31,.51,"Edit encoder + semiring messages","localize influence before recomputation",PURPLE,"#F7F4FC",1.3,10)
    pill(ax,.32,.565,"ΔG",CORAL,.055,"#FFF0F0")
    arrow(ax,(.375,.586),(.41,.54),CORAL)
    card(ax,.40,.48,.16,.09,"Affected-region gate","could this state change?",PURPLE,WHITE,.9,7.8,"center")
    arrow(ax,(.48,.475),(.48,.405),PURPLE,1.5)
    card(ax,.40,.32,.16,.08,"Copy-safety gate","is old witness valid?",BLUE,WHITE,.9,7.8,"center")
    arrow(ax,(.40,.355),(.345,.285),GREEN,1.4)
    arrow(ax,(.56,.355),(.615,.285),CORAL,1.4)
    pill(ax,.305,.235,"SAFE  →  COPY",GREEN,.13,"#EDF9F0",7)
    pill(ax,.535,.235,"UNSAFE  →  RECOMPUTE",CORAL,.19,"#FFF0F0",7)
    arrow(ax,(.245,.52),(.29,.52),CORAL,1.5)
    arrow(ax,(.245,.25),(.29,.27),BLUE,1.5)

    card(ax,.755,.47,.21,.22,"Reused states","unchanged region",GREEN,"#F0FAF3")
    tiny_graph(ax,.80,.505,.12,.09,[(0,.45),(.33,.82),(.6,.2),(1,.52)],[(0,1),(0,2),(1,3),(2,3)],[GREEN]*4)
    card(ax,.755,.20,.21,.18,"Recomputed states","edited dependency cone",CORAL,"#FFF4F4")
    tiny_graph(ax,.80,.235,.12,.075,[(0,.45),(.33,.82),(.6,.2),(1,.52)],[(0,1),(0,2),(1,3),(2,3)],[CORAL]*4)
    arrow(ax,(.725,.275),(.755,.29),CORAL,1.4)
    arrow(ax,(.725,.275),(.755,.56),GREEN,1.4,rad=-.14)
    card(ax,.65,.075,.315,.10,"Updated solution  Hᵗ","copied safe state  ⊕  locally repaired state",NAVY,NAVY,1,8.4,"center")
    save(fig,"deltanar.png")


def claim():
    fig, ax = canvas("Claim-matched controls for learning from failure", "FAILURE LEARNING · EVALUATION DESIGN", CORAL)
    for x,n,t in [(0.055,1,"Specify the claim"),(.31,2,"Freeze agent outputs"),(.65,3,"Apply matched controls")]: phase(ax,x,n,t,CORAL)
    card(ax,.035,.44,.205,.25,"Failure memory","source plan · trace · error",CORAL,"#FFF4F4")
    ax.text(.065,.57,"✕",fontsize=28,color=CORAL,weight="bold",zorder=5)
    ax.plot([.105,.135,.165,.205],[.56,.61,.52,.59],color="#9FB3C8",lw=1.3,zorder=5)
    card(ax,.035,.18,.205,.17,"Target families","",PURPLE,"#F7F4FC")
    pill(ax,.058,.215,"near",GREEN,.065,"#EDF9F0")
    pill(ax,.13,.215,"far",AMBER,.065,"#FFF7E8")
    ax.text(.058,.195,"near transfer  /  contrastive target",fontsize=6.0,color=MUTED,zorder=5)

    card(ax,.285,.18,.29,.51,"Probe battery","same model · fixed decoding · frozen outputs",BLUE,"#F2F7FF",1.2,10)
    probes=[("TRACE","repair the failed step",CORAL),("REFLECT","name the invariant",PURPLE),("TRANSFER","solve changed targets",TEAL),("EXECUTE","validate the artifact",GREEN)]
    for i,(a,b,c) in enumerate(probes):
        y=.56-i*.09
        card(ax,.31,y,.24,.062,a,b,c,WHITE,.8,7.5)
    arrow(ax,(.24,.52),(.285,.52),CORAL,1.5)
    arrow(ax,(.24,.25),(.285,.29),PURPLE,1.5)

    card(ax,.625,.42,.34,.27,"Control matrix","",TEAL,"#F0FBF8",1.2,10)
    cols=["Exact","Core","Transfer","Exec."]
    rows=["baseline","failure mem.","scrambled","oracle"]
    for j,c in enumerate(cols): ax.text(.72+j*.056,.61,c,fontsize=5.8,color=MUTED,ha="center",weight="bold")
    for i,r in enumerate(rows):
        ax.text(.652,.572-i*.038,r,fontsize=5.8,color=MUTED,va="center")
        for j in range(4):
            col=[BLUE,TEAL,AMBER,CORAL][j]
            alpha=.18+.16*((i+j)%4)
            ax.add_patch(Rectangle((.702+j*.056,.556-i*.038),.037,.026,facecolor=col,edgecolor=WHITE,lw=.7,alpha=alpha+.3,zorder=5))
    ax.text(.65,.432,"each comparison isolates one scientific claim",fontsize=6.2,color=MUTED,zorder=5)
    card(ax,.625,.20,.34,.15,"Auditable claim report","",NAVY,NAVY,1.2,9.3)
    ax.text(.65,.273,"repair  ≠  transfer  ≠  task success  ≠  execution",fontsize=6.4,color="#D9E6EF",zorder=5)
    ax.text(.65,.238,"✓ matched baselines    ✓ contrastive targets    ✓ boundary stated",fontsize=6.4,color=WHITE,zorder=5)
    arrow(ax,(.575,.45),(.625,.54),BLUE,1.5)
    arrow(ax,(.795,.42),(.795,.35),TEAL,1.5)
    save(fig,"failure-learning.png")


def bpc():
    fig, ax = canvas("Bounded language context with exact symbolic memory", "BOUNDED PATH CONTEXT · KGQA", AMBER)
    for x,n,t in [(0.055,1,"Ground the question"),(.30,2,"Expose a bounded suffix"),(.69,3,"Route and expand")]: phase(ax,x,n,t,AMBER)
    card(ax,.035,.18,.22,.51,"Question-grounded KG","entities and relations stay symbolic",BLUE,"#F2F7FF",1.1,10)
    tiny_graph(ax,.07,.37,.15,.22,[(0,.5),(.2,.85),(.35,.2),(.55,.68),(.72,.35),(.9,.82),(1,.12)],[(0,1),(0,2),(1,3),(2,4),(3,4),(3,5),(4,6)],[BLUE,TEAL,PURPLE,BLUE,AMBER,GREEN,CORAL])
    pill(ax,.067,.245,"question q",NAVY,.085,"#E8EEF3")
    pill(ax,.16,.245,"start entity",TEAL,.075,"#EAF8F6",6.2)

    card(ax,.30,.18,.29,.51,"Dual-memory interface","full paths outside; bounded text inside",PURPLE,"#F7F4FC",1.2,10)
    card(ax,.325,.45,.24,.145,"Symbolic beam memory  Bᵗ","",BLUE,WHITE,.9,8.2)
    ax.text(.345,.505,"(e₀, r₁, e₁, …, rₜ, eₜ)",fontsize=7.2,color=NAVY,weight="bold",zorder=5)
    ax.text(.345,.475,"complete path tuples + scores",fontsize=6.2,color=MUTED,zorder=5)
    arrow(ax,(.445,.445),(.445,.39),PURPLE,1.5)
    card(ax,.325,.25,.24,.13,"Context lens  hK(Bᵗ)","",AMBER,"#FFF8EA",1,8.5)
    for i in range(4):
        col=LINE if i<2 else AMBER
        ax.plot([.35+i*.045,.38+i*.045],[.29,.29],color=col,lw=3,zorder=5,solid_capstyle="round")
    ax.text(.345,.268,"only the last K hops are verbalized",fontsize=6.0,color=MUTED,zorder=5)
    arrow(ax,(.255,.44),(.30,.44),BLUE,1.5)

    card(ax,.64,.46,.325,.23,"LLM relation router","rank candidate relations from bounded context",TEAL,"#F0FBF8",1.2,10)
    rels=[("r₃",.88,GREEN),("r₇",.63,BLUE),("r₂",.37,AMBER)]
    for i,(r,s,c) in enumerate(rels):
        y=.57-i*.045
        ax.text(.675,y,r,fontsize=7,color=NAVY,weight="bold")
        ax.add_patch(Rectangle((.71,y-.006),.17,.012,facecolor=LINE,edgecolor="none",zorder=5))
        ax.add_patch(Rectangle((.71,y-.006),.17*s,.012,facecolor=c,edgecolor="none",zorder=6))
    arrow(ax,(.59,.315),(.64,.54),AMBER,1.6)
    card(ax,.64,.24,.155,.13,"Expand + prune","beam search",BLUE,"#F2F7FF",1,8.5,"center")
    card(ax,.81,.24,.155,.13,"Answer + evidence","full path",GREEN,"#F0FAF3",1,8.5,"center")
    arrow(ax,(.717,.46),(.717,.37),TEAL,1.5)
    arrow(ax,(.795,.305),(.81,.305),GREEN,1.5)
    arrow(ax,(.64,.285),(.59,.35),BLUE,1.1,rad=-.25)
    ax.text(.598,.245,"repeat",fontsize=6.4,color=MUTED,ha="right")
    save(fig,"bounded-path-context.png")


def rcda():
    fig, ax = canvas("A controlled factorial audit of structural KGC", "RECIPE-CONTROLLED DECODER AUDIT", GREEN)
    for x,n,t in [(0.055,1,"Freeze the recipe"),(.33,2,"Cross architecture factors"),(.72,3,"Attribute conclusions")]: phase(ax,x,n,t,GREEN)
    card(ax,.035,.48,.23,.21,"Datasets + descriptors","entities/relations · symmetry · provenance",BLUE,"#F2F7FF")
    for i,t in enumerate(["WN18RR","FB15k-237","CoDEx"]): pill(ax,.055+i*.065,.535,t,[BLUE,TEAL,PURPLE][i],.06,fontsize=5.9)
    card(ax,.035,.22,.23,.17,"One fixed training recipe","optimizer · negatives · budget · seeds",GREEN,"#F0FAF3")
    ax.text(.06,.27,"θtrain  fixed across every cell",fontsize=7.4,color=NAVY,weight="bold",zorder=5)
    arrow(ax,(.265,.55),(.31,.55),BLUE,1.4)
    arrow(ax,(.265,.29),(.31,.35),GREEN,1.4)

    card(ax,.31,.18,.34,.51,"Matched factorial grid","decoder × encoder depth × dataset",PURPLE,"#F7F4FC",1.2,10)
    dec=["TransE","DistMult","ComplEx","RotatE"]
    dep=["0-hop","1-layer","2-layer"]
    for j,d in enumerate(dep): ax.text(.445+j*.065,.60,d,ha="center",fontsize=6.3,color=MUTED,weight="bold")
    for i,d in enumerate(dec):
        ax.text(.335,.548-i*.07,d,va="center",fontsize=6.2,color=MUTED,weight="bold")
        for j in range(3):
            col=[BLUE,TEAL,PURPLE][j]
            ax.add_patch(FancyBboxPatch((.415+j*.065,.525-i*.07),.052,.045,boxstyle="round,pad=.002,rounding_size=.006",
                                        facecolor=col+"35",edgecolor=col,lw=.7,zorder=5))
            ax.text(.441+j*.065,.548-i*.07,f"s1–s5",ha="center",va="center",fontsize=5.4,color=INK,zorder=6)
    ax.text(.48,.225,"same checkpoints · same evaluation · multiple seeds",ha="center",fontsize=6.5,color=MUTED)

    card(ax,.70,.48,.265,.21,"Metric panel","MRR · Hits@1/3/10 · uncertainty",AMBER,"#FFF8EA",1.1,9.4)
    for i,h in enumerate([.05,.10,.075,.13,.09]):
        ax.add_patch(Rectangle((.735+i*.038,.525),.022,h,facecolor=[BLUE,TEAL,PURPLE,AMBER,GREEN][i],edgecolor="none",zorder=5))
        ax.plot([.746+i*.038,.746+i*.038],[.525+h-.012,.525+h+.012],color=NAVY,lw=.7,zorder=6)
    card(ax,.70,.23,.265,.18,"Factor attribution","",TEAL,"#F0FBF8",1.1,9.2)
    pill(ax,.725,.275,"Δ decoder",BLUE,.067,"#EAF2FF",6.2)
    pill(ax,.80,.275,"Δ depth",PURPLE,.06,"#F1ECFA",6.2)
    pill(ax,.868,.275,"interaction",CORAL,.075,"#FFF0F0",6.0)
    card(ax,.70,.11,.265,.07,"Controlled reporting checklist","state what is held fixed",NAVY,NAVY,1,8.2,"center")
    arrow(ax,(.65,.53),(.70,.56),PURPLE,1.5)
    arrow(ax,(.833,.48),(.833,.41),AMBER,1.5)
    arrow(ax,(.833,.23),(.833,.18),TEAL,1.5)
    save(fig,"decoder-audit.png")


if __name__ == "__main__":
    prcd()
    cdv()
    delta()
    claim()
    bpc()
    rcda()
    print(f"Generated six figures in {OUT}")
