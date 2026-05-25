from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle


ROOT = Path(r"E:\11.16\thesis_writing_repo\figures")
OUT = ROOT / "ch4" / "diagrams"


def setup(figsize=(12, 6)):
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    fig, ax = plt.subplots(figsize=figsize, dpi=180)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return fig, ax


def box(ax, xy, wh, text, fc="#F4F8FB", ec="#315B7C", fontsize=13, lw=1.6):
    x, y = xy
    w, h = wh
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.012,rounding_size=0.02",
        linewidth=lw,
        edgecolor=ec,
        facecolor=fc,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize, color="#1F2D3A")
    return patch


def arrow(ax, p1, p2, color="#315B7C", lw=1.8):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=16, linewidth=lw, color=color))


def save(fig, filename):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / filename, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def workflow():
    fig, ax = setup((14, 4.8))
    labels = [
        "IE420\n连续缺陷场景",
        "滑动窗口\n样本构建",
        "窗口级\n诊断证据",
        "场景级\n活跃期定位",
        "场景级\n空间定位",
        "综合诊断\n时间段 + Top-K",
    ]
    xs = [0.03, 0.19, 0.35, 0.51, 0.67, 0.83]
    for x, lab in zip(xs, labels):
        box(ax, (x, 0.38), (0.12, 0.24), lab, fc="#EFF6FA")
    for i in range(len(xs) - 1):
        arrow(ax, (xs[i] + 0.12, 0.50), (xs[i + 1], 0.50))
    ax.text(0.5, 0.76, "固定稀疏监测布局下的全过程缺陷诊断主线", ha="center", fontsize=16, weight="bold")
    ax.text(0.5, 0.20, "第4章固定诊断协议，第5章在同一协议下优化监测节点集合 S", ha="center", fontsize=12, color="#52616B")
    save(fig, "CH4-F00_diagnosis_workflow.png")


def window_scene_aggregation():
    fig, ax = setup((13, 5.4))
    ax.plot([0.08, 0.92], [0.34, 0.34], color="#2F4F68", lw=2)
    for i in range(9):
        x = 0.10 + i * 0.09
        fc = "#DCEEF8" if 3 <= i <= 6 else "#F6F8FA"
        rect = Rectangle((x, 0.39), 0.17, 0.13, facecolor=fc, edgecolor="#47708E", linewidth=1.2)
        ax.add_patch(rect)
        ax.text(x + 0.085, 0.455, f"W{i+1}", ha="center", va="center", fontsize=10)
        ax.plot([x, x], [0.30, 0.36], color="#91A3B0", lw=1)
    ax.add_patch(Rectangle((0.37, 0.25), 0.35, 0.18, facecolor="#FCE8D7", edgecolor="#C46B28", alpha=0.8))
    ax.text(0.545, 0.235, "真实 active 时段", ha="center", fontsize=12, color="#8A4215")
    box(ax, (0.10, 0.68), (0.22, 0.16), "每个窗口输出\np_active(t), node_scores(t)", fc="#EFF6FA")
    box(ax, (0.40, 0.68), (0.22, 0.16), "按 scenario_id\n恢复时间线", fc="#EFF6FA")
    box(ax, (0.70, 0.68), (0.20, 0.16), "聚合预测 active 窗口\n形成节点 Top-K", fc="#EFF6FA")
    arrow(ax, (0.32, 0.76), (0.40, 0.76))
    arrow(ax, (0.62, 0.76), (0.70, 0.76))
    ax.text(0.5, 0.08, "窗口级证据不是终点；同一场景内按时间排序后形成场景级诊断结果", ha="center", fontsize=12, color="#52616B")
    save(fig, "CH4-F01_window_scene_aggregation.png")


def vscd_sets():
    fig, ax = setup((10, 6))
    ax.add_patch(Circle((0.47, 0.50), 0.40, facecolor="#F6F8FA", edgecolor="#2F4F68", lw=2))
    ax.text(0.47, 0.90, "V = 128 全图拓扑节点", ha="center", fontsize=15, weight="bold", color="#1F2D3A")
    ax.add_patch(Circle((0.36, 0.50), 0.18, facecolor="#CFE8F3", edgecolor="#2C7DA0", lw=1.8, alpha=0.85))
    ax.add_patch(Circle((0.58, 0.50), 0.24, facecolor="#F8D7C2", edgecolor="#C46B28", lw=1.8, alpha=0.78))
    ax.add_patch(Circle((0.66, 0.42), 0.09, facecolor="#D7EAD2", edgecolor="#4D8B42", lw=1.6, alpha=0.95))
    ax.text(0.31, 0.51, "S = 25\n监测节点", ha="center", va="center", fontsize=13, color="#1F2D3A")
    ax.text(0.59, 0.58, "C = 50\n候选定位空间", ha="center", va="center", fontsize=13, color="#1F2D3A")
    ax.text(0.66, 0.42, "D\n实际缺陷", ha="center", va="center", fontsize=11, color="#1F2D3A")
    box(ax, (0.08, 0.08), (0.30, 0.13), "输入保留全图结构 V\n动态观测来自 S", fc="#EFF6FA", fontsize=12)
    box(ax, (0.58, 0.08), (0.34, 0.13), "输出在候选集合 C 内排序\nD 为评价目标", fc="#FFF4EC", fontsize=12)
    save(fig, "CH4-F02_vscd_node_sets.png")


def time_gated_window_label():
    fig, ax = setup((13, 5))
    ax.plot([0.08, 0.92], [0.50, 0.50], color="#2F4F68", lw=2)
    ax.add_patch(Rectangle((0.40, 0.43), 0.32, 0.14, facecolor="#F8D7C2", edgecolor="#C46B28", lw=1.8))
    ax.text(0.56, 0.62, "缺陷活跃时段：start_hour 到 start_hour + duration_h", ha="center", fontsize=13, color="#8A4215")
    for i, x in enumerate([0.17, 0.28, 0.39, 0.50, 0.61, 0.72]):
        rect = Rectangle((x, 0.24), 0.22, 0.16, facecolor="#F6F8FA", edgecolor="#47708E", lw=1.2)
        ax.add_patch(rect)
        ax.text(x + 0.11, 0.32, f"窗口 {i+1}", ha="center", va="center", fontsize=11)
        arrow(ax, (x + 0.11, 0.40), (x + 0.11, 0.48), lw=1.2)
    box(ax, (0.12, 0.73), (0.22, 0.13), "采样间隔 10 min", fc="#EFF6FA", fontsize=12)
    box(ax, (0.40, 0.73), (0.22, 0.13), "sequence_length=36\n约 6 h", fc="#EFF6FA", fontsize=12)
    box(ax, (0.68, 0.73), (0.22, 0.13), "window_stride=6\n约 1 h 判断步长", fc="#EFF6FA", fontsize=12)
    ax.text(0.5, 0.10, "active_label 由窗口与真实活跃时段的重叠比例计算", ha="center", fontsize=12, color="#52616B")
    save(fig, "CH4-F03_time_gated_window_label.png")


def output_heads_to_metrics():
    fig, ax = setup((13, 6.2))
    box(ax, (0.05, 0.42), (0.18, 0.16), "模型窗口输入\nX(t), A, mask", fc="#F6F8FA")
    box(ax, (0.31, 0.42), (0.18, 0.16), "时空图诊断模型\nhydraulic_inverse_deepattn", fc="#EFF6FA")
    arrow(ax, (0.23, 0.50), (0.31, 0.50))
    heads = [
        ("logits_has_defect\n→ p_active(t)", "Active Recall\nOnset Error\nInterval IoU"),
        ("logits_node\n→ node_scores(t)", "MRR / Top-K\nEvent Top-K"),
        ("logits_defect_type", "仅保留输出头\n不作为正式分类指标"),
    ]
    ys = [0.72, 0.42, 0.12]
    for (h, m), y in zip(heads, ys):
        box(ax, (0.58, y), (0.17, 0.13), h, fc="#FFF4EC", fontsize=11)
        box(ax, (0.81, y), (0.15, 0.13), m, fc="#F4F8FB", fontsize=10)
        arrow(ax, (0.49, 0.50), (0.58, y + 0.065))
        arrow(ax, (0.75, y + 0.065), (0.81, y + 0.065))
    ax.text(0.50, 0.93, "模型输出头到评价指标的计算链条", ha="center", fontsize=16, weight="bold")
    save(fig, "CH4-F04_output_heads_to_metrics.png")


def model_architecture():
    fig, ax = setup((13, 5.5))
    labels = [
        "稀疏观测\n窗口序列",
        "时间特征\n编码",
        "图结构\n传播",
        "水力响应\n注意力融合",
        "active 输出\nnode 输出",
    ]
    xs = [0.05, 0.25, 0.45, 0.65, 0.84]
    colors = ["#F6F8FA", "#EFF6FA", "#EFF6FA", "#FFF4EC", "#F4F8FB"]
    for x, lab, fc in zip(xs, labels, colors):
        box(ax, (x, 0.44), (0.14, 0.18), lab, fc=fc)
    for i in range(len(xs) - 1):
        arrow(ax, (xs[i] + 0.14, 0.53), (xs[i + 1], 0.53))
    box(ax, (0.08, 0.16), (0.25, 0.13), "全图拓扑 V=128\n动态观测来自 S=25", fc="#F6F8FA", fontsize=12)
    box(ax, (0.38, 0.16), (0.25, 0.13), "候选空间 C=50\n用于节点排序评价", fc="#F6F8FA", fontsize=12)
    box(ax, (0.68, 0.16), (0.24, 0.13), "场景聚合形成\n时间段 + Top-K", fc="#F6F8FA", fontsize=12)
    ax.text(0.5, 0.83, "hydraulic_inverse_deepattn 模型结构示意", ha="center", fontsize=16, weight="bold")
    save(fig, "CH4-F05_model_architecture.png")


def ch4_to_ch5_bridge():
    fig, ax = setup((12, 5))
    box(ax, (0.08, 0.45), (0.28, 0.20), "第4章\n固定 S 的诊断模型\n评价诊断能力", fc="#EFF6FA", fontsize=14)
    box(ax, (0.64, 0.45), (0.28, 0.20), "第5章\n固定 V/C/诊断协议\n优化监测节点 S", fc="#FFF4EC", fontsize=14)
    arrow(ax, (0.36, 0.55), (0.64, 0.55))
    box(ax, (0.22, 0.17), (0.56, 0.15), "继承：IE420 数据、候选空间 C=50、模型结构、训练评价协议、空间定位指标", fc="#F6F8FA", fontsize=12)
    ax.text(0.5, 0.80, "从诊断模型到监测布局优化的章节衔接", ha="center", fontsize=16, weight="bold")
    save(fig, "CH4-F11_ch4_to_ch5_bridge.png")


def main():
    workflow()
    window_scene_aggregation()
    vscd_sets()
    time_gated_window_label()
    output_heads_to_metrics()
    model_architecture()
    ch4_to_ch5_bridge()


if __name__ == "__main__":
    main()
