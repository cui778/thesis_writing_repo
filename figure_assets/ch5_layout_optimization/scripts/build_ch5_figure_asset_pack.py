from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np
import pandas as pd


ROOT = Path(r"E:\11.16")
PACK_ROOT = ROOT / "thesis_writing_repo" / "figure_assets" / "ch5_layout_optimization"
DATA_DIR = PACK_ROOT / "data"
FIG_DATA = PACK_ROOT / "figures" / "data_redraw"
FIG_SCHEMATIC = PACK_ROOT / "figures" / "generated_schematic"
FIG_SCREENSHOT = PACK_ROOT / "figures" / "screenshot_needed"
FIG_IMAGEGEN = PACK_ROOT / "figures" / "imagegen_prompted"

CH5 = ROOT / "script2_new" / "chapter5_layout_optimization"
CH4 = ROOT / "script2_new" / "chapter4_diagnosis_model"
RAW_REPORTS = CH5 / "outputs" / "raw_metrics_from_main_reports_20260413"
LIVE_REPORTS = ROOT / "script2_new" / "outputs" / "reports"
THESIS_TABLES = CH5 / "outputs" / "thesis_tables"

DEFECT_MATRIX = ROOT / "script2_new" / "input_1" / "defect_matrix_diverse_ie_v4_formal_conservative420_seed42.csv"
CANDIDATE_TIERS = CH4 / "outputs" / "candidate_observability_tiers.csv"
MAIN_WITH_EVENT = THESIS_TABLES / "table_5_2_main_scenario_seed_summary_with_event_topk.csv"
BUDGET_SUMMARY = THESIS_TABLES / "table_5_6_budget_observability_summary.csv"
JACCARD = THESIS_TABLES / "table_5_7_layout_jaccard_similarity.csv"
NODE_HOLDOUT = THESIS_TABLES / "table_5_4_node_holdout_boundary_seed42.csv"


plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


METHODS = [
    {
        "method_short": "Degree",
        "method": "degree",
        "json": RAW_REPORTS / "last_run_metrics_ch5_firstcmp_degree_N25_s42.json",
        "color": "#69757f",
    },
    {
        "method_short": "Cand-Obs",
        "method": "candidate_observability",
        "json": RAW_REPORTS / "last_run_metrics_ch5_firstcmp_candidate_observability_N25_s42.json",
        "color": "#27786b",
    },
    {
        "method_short": "Two-stage v1",
        "method": "two_stage_balanced_layout_v1",
        "json": RAW_REPORTS / "last_run_metrics_ch5_tsbal25_s42.json",
        "color": "#4c6fb2",
    },
    {
        "method_short": "v0_2 clean",
        "method": "learnable_layout_network_v0_2_clean_scenario",
        "json": LIVE_REPORTS / "last_run_metrics_ch5_llnv02clean_scen_N25_s42.json",
        "color": "#b66a2a",
    },
    {
        "method_short": "v2_2 clean",
        "method": "learnable_layout_network_v2_2_clean_generalization",
        "json": RAW_REPORTS / "last_run_metrics_ch5_llnv22clean_gen_scen_N25_s42.json",
        "color": "#7b4ba0",
    },
]

COLOR = {m["method_short"]: m["color"] for m in METHODS}
ORDER = [m["method_short"] for m in METHODS]


def ensure_dirs() -> None:
    for path in [DATA_DIR, FIG_DATA, FIG_SCHEMATIC, FIG_SCREENSHOT, FIG_IMAGEGEN]:
        path.mkdir(parents=True, exist_ok=True)


def load_by_scenario() -> pd.DataFrame:
    defects = pd.read_csv(DEFECT_MATRIX)
    tiers = pd.read_csv(CANDIDATE_TIERS)
    rows = []
    for spec in METHODS:
        report = json.loads(Path(spec["json"]).read_text(encoding="utf-8"))
        for scenario_id, metrics in report["by_scenario"].items():
            rows.append(
                {
                    "method_short": spec["method_short"],
                    "method": spec["method"],
                    "scenario_id": int(scenario_id),
                    "n_windows": metrics.get("n_windows"),
                    "mrr": metrics.get("mrr"),
                    "top1": metrics.get("top1"),
                    "top3": metrics.get("top3"),
                    "top5": metrics.get("top5"),
                    "source_json": str(spec["json"]),
                }
            )
    raw = pd.DataFrame(rows)
    merged = raw.merge(defects, left_on="scenario_id", right_on="defect_id", how="left")
    merged = merged.merge(
        tiers[["node_id", "observability_tier", "min_monitor_hop", "nearest_monitors"]],
        on="node_id",
        how="left",
    )
    merged["is_hard_candidate"] = merged["observability_tier"].eq("far")
    merged.to_csv(DATA_DIR / "ch5_seed42_by_scenario_raw_metrics.csv", index=False, encoding="utf-8-sig")
    return merged


def plot_main_dot_error() -> None:
    df = pd.read_csv(MAIN_WITH_EVENT)
    df["method_short"] = pd.Categorical(df["method_short"], ORDER, ordered=True)
    df = df.sort_values("method_short")
    metrics = [("mrr", "MRR"), ("top1", "Top-1"), ("event_level_top1", "Event Top-1")]
    y = np.arange(len(df))
    offsets = [-0.18, 0, 0.18]
    markers = ["o", "s", "D"]

    fig, ax = plt.subplots(figsize=(8.5, 5.2), dpi=240)
    for (metric, label), off, marker in zip(metrics, offsets, markers):
        ax.errorbar(
            df[f"{metric}_mean"],
            y + off,
            xerr=df[f"{metric}_std"],
            fmt=marker,
            markersize=7,
            capsize=3,
            linewidth=1.4,
            label=label,
            color="#222222" if metric == "mrr" else ("#3d7fa6" if metric == "top1" else "#c46b37"),
        )
    ax.set_yticks(y)
    ax.set_yticklabels(df["method_short"])
    ax.set_xlim(0.58, 0.93)
    ax.set_xlabel("Score (mean ± std, seed 7/42/123)")
    ax.set_title("主协议空间定位表现：从人工规则到诊断反馈布局", fontsize=13, fontweight="bold")
    ax.grid(axis="x", linestyle="--", alpha=0.25)
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(FIG_DATA / "F5_D01_main_performance_dot_error.png", bbox_inches="tight")
    plt.close(fig)


def plot_scenario_distribution(raw: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(9.2, 5.4), dpi=240)
    data = [raw[raw["method_short"] == method]["mrr"].dropna().to_numpy() for method in ORDER]
    parts = ax.violinplot(data, showmeans=False, showmedians=False, showextrema=False)
    for body, method in zip(parts["bodies"], ORDER):
        body.set_facecolor(COLOR[method])
        body.set_edgecolor("none")
        body.set_alpha(0.28)
    bp = ax.boxplot(
        data,
        widths=0.18,
        patch_artist=True,
        showfliers=False,
        medianprops={"color": "#111111", "linewidth": 1.3},
        boxprops={"facecolor": "white", "edgecolor": "#333333", "linewidth": 1},
        whiskerprops={"color": "#555555"},
        capprops={"color": "#555555"},
    )
    ax.set_xticks(np.arange(1, len(ORDER) + 1))
    ax.set_xticklabels(ORDER, rotation=12, ha="right")
    ax.set_ylim(0, 1.03)
    ax.set_ylabel("Scenario-level MRR")
    ax.set_title("场景级定位表现分布（seed 42, raw by_scenario）", fontsize=13, fontweight="bold")
    ax.grid(axis="y", linestyle="--", alpha=0.22)
    fig.tight_layout()
    fig.savefig(FIG_DATA / "F5_D02_scenario_mrr_distribution_seed42.png", bbox_inches="tight")
    plt.close(fig)


def plot_observability_group_performance(raw: pd.DataFrame) -> None:
    grouped = (
        raw.groupby(["method_short", "observability_tier"], as_index=False)
        .agg(mrr_mean=("mrr", "mean"), top1_mean=("top1", "mean"), scenario_count=("scenario_id", "nunique"))
    )
    grouped.to_csv(DATA_DIR / "ch5_seed42_observability_group_performance.csv", index=False, encoding="utf-8-sig")

    tiers = ["direct", "near", "far"]
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.2), dpi=240, sharey=True)
    for ax, metric, title in [(axes[0], "mrr_mean", "MRR"), (axes[1], "top1_mean", "Top-1")]:
        x = np.arange(len(tiers))
        width = 0.14
        for idx, method in enumerate(ORDER):
            sub = grouped[grouped["method_short"] == method].set_index("observability_tier").reindex(tiers)
            ax.bar(
                x + (idx - 2) * width,
                sub[metric],
                width=width,
                color=COLOR[method],
                alpha=0.9,
                label=method if ax is axes[0] else None,
            )
        ax.set_xticks(x)
        ax.set_xticklabels(tiers)
        ax.set_ylim(0, 1.05)
        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.grid(axis="y", linestyle="--", alpha=0.22)
    axes[0].set_ylabel("Score")
    fig.legend(frameon=False, ncol=5, loc="upper center", bbox_to_anchor=(0.5, 1.04))
    fig.suptitle("direct / near / far 候选分组下的定位表现（seed 42）", fontsize=13, fontweight="bold", y=1.11)
    fig.tight_layout()
    fig.savefig(FIG_DATA / "F5_D03_observability_group_performance_seed42.png", bbox_inches="tight")
    plt.close(fig)


def plot_hard_candidate_performance(raw: pd.DataFrame) -> None:
    grouped = (
        raw.groupby(["method_short", "is_hard_candidate"], as_index=False)
        .agg(mrr_mean=("mrr", "mean"), top1_mean=("top1", "mean"), scenario_count=("scenario_id", "nunique"))
    )
    grouped["group"] = grouped["is_hard_candidate"].map({True: "hard: far under Degree", False: "other"})
    grouped.to_csv(DATA_DIR / "ch5_seed42_hard_candidate_performance.csv", index=False, encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(8.6, 5.0), dpi=240)
    y = np.arange(len(ORDER))
    width = 0.32
    for offset, group, color in [(-width / 2, "other", "#b9c1c8"), (width / 2, "hard: far under Degree", "#b84b3a")]:
        sub = grouped[grouped["group"] == group].set_index("method_short").reindex(ORDER)
        ax.barh(y + offset, sub["mrr_mean"], height=width, color=color, label=group, alpha=0.9)
        for yi, value in zip(y + offset, sub["mrr_mean"]):
            ax.text(value + 0.01, yi, f"{value:.2f}", va="center", fontsize=8)
    ax.set_yticks(y)
    ax.set_yticklabels(ORDER)
    ax.set_xlim(0, 1.05)
    ax.set_xlabel("Scenario-level MRR")
    ax.set_title("hard candidates 与其他场景的定位表现对比（seed 42）", fontsize=13, fontweight="bold")
    ax.grid(axis="x", linestyle="--", alpha=0.22)
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(FIG_DATA / "F5_D04_hard_candidate_performance_seed42.png", bbox_inches="tight")
    plt.close(fig)


def plot_budget_structure() -> None:
    df = pd.read_csv(BUDGET_SUMMARY)
    fig, axes = plt.subplots(1, 2, figsize=(11.8, 5.0), dpi=240)
    colors = {"Degree": "#69757f", "Cand-Obs": "#27786b"}
    for method, sub in df.groupby("method_short"):
        sub = sub.sort_values("n")
        axes[0].plot(sub["n"], sub["direct"], marker="o", color=colors[method], label=f"{method} direct")
        axes[0].plot(sub["n"], sub["far"], marker="s", linestyle="--", color=colors[method], label=f"{method} far")
        axes[1].plot(sub["n"], sub["mean_hop"], marker="o", color=colors[method], label=method)
    axes[0].set_title("direct / far count")
    axes[1].set_title("mean hop")
    for ax in axes:
        ax.set_xlabel("Monitor budget N")
        ax.set_xticks([5, 10, 15, 20, 25])
        ax.grid(axis="y", linestyle="--", alpha=0.22)
        ax.legend(frameon=False, fontsize=8)
    axes[0].set_ylabel("Candidate count")
    axes[1].set_ylabel("Hop")
    fig.suptitle("预算变化下的候选可观测性结构（无重训）", fontsize=13, fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DATA / "F5_D05_budget_observability_structure.png", bbox_inches="tight")
    plt.close(fig)


def plot_jaccard_clean() -> None:
    df = pd.read_csv(JACCARD)
    labels = df["method_short"].tolist()
    mat = df[labels].to_numpy(float)
    fig, ax = plt.subplots(figsize=(6.6, 5.7), dpi=240)
    im = ax.imshow(mat, cmap="Greens", vmin=0, vmax=1)
    ax.set_xticks(np.arange(len(labels)))
    ax.set_yticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.set_yticklabels(labels)
    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(j, i, f"{mat[i, j]:.2f}", ha="center", va="center", fontsize=8)
    ax.set_title("监测节点集合相似度（Jaccard）", fontsize=13, fontweight="bold")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(FIG_DATA / "F5_D06_layout_jaccard_heatmap.png", bbox_inches="tight")
    plt.close(fig)


def plot_generated_protocol_loop() -> None:
    fig, ax = plt.subplots(figsize=(10.5, 5.6), dpi=240)
    ax.axis("off")
    boxes = [
        (0.08, 0.58, "第3章母数据\nIE420 场景"),
        (0.32, 0.58, "第4章诊断协议\n任务 / 模型 / 指标固定"),
        (0.56, 0.58, "改变监测节点集合 S\n生成 observed mask"),
        (0.80, 0.58, "空间定位评价\nMRR / Top-K"),
        (0.44, 0.18, "诊断反馈\n指导下一轮布点"),
    ]
    for x, y, text in boxes:
        ax.add_patch(plt.Rectangle((x, y), 0.16, 0.18, facecolor="#f3f6f4", edgecolor="#2f6f61", linewidth=1.5))
        ax.text(x + 0.08, y + 0.09, text, ha="center", va="center", fontsize=11)
    arrows = [
        ((0.24, 0.67), (0.32, 0.67)),
        ((0.48, 0.67), (0.56, 0.67)),
        ((0.72, 0.67), (0.80, 0.67)),
        ((0.88, 0.58), (0.56, 0.30)),
        ((0.44, 0.27), (0.64, 0.58)),
    ]
    for start, end in arrows:
        ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="->", lw=1.6, color="#2f4f4f"))
    ax.text(0.5, 0.92, "固定诊断协议下的监测布局评价闭环", ha="center", fontsize=16, fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_SCHEMATIC / "F5_G01_fixed_protocol_layout_loop.png", bbox_inches="tight")
    plt.close(fig)


def plot_generated_learning_levels() -> None:
    fig, ax = plt.subplots(figsize=(10.5, 5.6), dpi=240)
    ax.axis("off")
    ax.text(0.5, 0.92, "从人工规则选点到诊断反馈学习布点", ha="center", fontsize=16, fontweight="bold")
    xs = [0.08, 0.30, 0.52, 0.74]
    texts = [
        "Degree\n拓扑规则",
        "Cand-Obs / Two-stage\n任务驱动规则",
        "v0_2 clean\n节点级反馈学习",
        "v2_2 clean\n布局级代理搜索",
    ]
    colors = ["#e7ecef", "#dcefe7", "#f1e2ce", "#e8ddf0"]
    for x, text, color in zip(xs, texts, colors):
        ax.add_patch(FancyBboxPatch((x, 0.42), 0.17, 0.24, boxstyle="round,pad=0.02,rounding_size=0.02", facecolor=color, edgecolor="#333333", linewidth=1.2))
        ax.text(x + 0.085, 0.54, text, ha="center", va="center", fontsize=11)
    for i in range(3):
        ax.annotate("", xy=(xs[i + 1] - 0.015, 0.54), xytext=(xs[i] + 0.185, 0.54), arrowprops=dict(arrowstyle="->", lw=1.6, color="#333333"))
    ax.text(0.605, 0.28, "学习型变化：不是只找高中心性节点，而是让诊断结果反过来指导布点", ha="center", fontsize=11, color="#333333")
    fig.tight_layout()
    fig.savefig(FIG_SCHEMATIC / "F5_G02_learning_layout_two_level.png", bbox_inches="tight")
    plt.close(fig)


def write_indexes() -> None:
    rows = [
        {
            "fig_id": "F5-D01",
            "category": "data_redraw",
            "ppt_slide": "Slide 5-6",
            "thesis_section": "5.5.2",
            "title": "主协议空间定位表现点图",
            "output_file": "figures/data_redraw/F5_D01_main_performance_dot_error.png",
            "source_data": "table_5_2_main_scenario_seed_summary_with_event_topk.csv",
            "who_handles": "Codex",
            "status": "done",
            "claim": "学习型布局与任务驱动布局优于 Degree，v2_2 clean 的 Top-1 更高但波动更大",
        },
        {
            "fig_id": "F5-D02",
            "category": "data_redraw",
            "ppt_slide": "Slide 5-6 / backup",
            "thesis_section": "5.5.2",
            "title": "场景级 MRR 分布",
            "output_file": "figures/data_redraw/F5_D02_scenario_mrr_distribution_seed42.png",
            "source_data": "data/ch5_seed42_by_scenario_raw_metrics.csv",
            "who_handles": "Codex",
            "status": "done",
            "claim": "均值之外，场景级分布显示不同布局的低性能尾部差异",
        },
        {
            "fig_id": "F5-D03",
            "category": "data_redraw",
            "ppt_slide": "Slide 5-7",
            "thesis_section": "5.6.2",
            "title": "direct / near / far 分组性能",
            "output_file": "figures/data_redraw/F5_D03_observability_group_performance_seed42.png",
            "source_data": "data/ch5_seed42_observability_group_performance.csv",
            "who_handles": "Codex",
            "status": "done",
            "claim": "结构可观测性分组可以连接布局结构与定位表现",
        },
        {
            "fig_id": "F5-D04",
            "category": "data_redraw",
            "ppt_slide": "Slide 5-7 / backup",
            "thesis_section": "5.6.3",
            "title": "hard candidates 场景性能",
            "output_file": "figures/data_redraw/F5_D04_hard_candidate_performance_seed42.png",
            "source_data": "data/ch5_seed42_hard_candidate_performance.csv",
            "who_handles": "Codex",
            "status": "done",
            "claim": "Degree 下 far 候选形成难点场景，可用于检验学习型布局是否改善尾部",
        },
        {
            "fig_id": "F5-D05",
            "category": "data_redraw",
            "ppt_slide": "Slide 5-7",
            "thesis_section": "5.6.1",
            "title": "预算变化下可观测性结构",
            "output_file": "figures/data_redraw/F5_D05_budget_observability_structure.png",
            "source_data": "table_5_6_budget_observability_summary.csv",
            "who_handles": "Codex",
            "status": "done",
            "claim": "预算变化会改变 direct/far 与 mean_hop，但不代表多预算性能结论",
        },
        {
            "fig_id": "F5-D06",
            "category": "data_redraw",
            "ppt_slide": "Slide 5-7 / backup",
            "thesis_section": "5.6.4",
            "title": "布局节点集合 Jaccard 相似度",
            "output_file": "figures/data_redraw/F5_D06_layout_jaccard_heatmap.png",
            "source_data": "table_5_7_layout_jaccard_similarity.csv",
            "who_handles": "Codex",
            "status": "done",
            "claim": "学习型布局不是简单复制人工规则布局",
        },
        {
            "fig_id": "F5-G01",
            "category": "generated_schematic",
            "ppt_slide": "Slide 5-1",
            "thesis_section": "5.2",
            "title": "固定诊断协议下的布局评价闭环",
            "output_file": "figures/generated_schematic/F5_G01_fixed_protocol_layout_loop.png",
            "source_data": "chapter protocol",
            "who_handles": "Codex",
            "status": "done",
            "claim": "固定数据和诊断协议，只改变监测节点集合 S",
        },
        {
            "fig_id": "F5-G02",
            "category": "generated_schematic",
            "ppt_slide": "Slide 5-2",
            "thesis_section": "5.4",
            "title": "从人工规则到双层学习型布局",
            "output_file": "figures/generated_schematic/F5_G02_learning_layout_two_level.png",
            "source_data": "chapter mainline",
            "who_handles": "Codex",
            "status": "done",
            "claim": "v0_2 clean 与 v2_2 clean 分别对应节点级和布局级学习",
        },
        {
            "fig_id": "F5-S01",
            "category": "screenshot_needed",
            "ppt_slide": "Slide 5-3 / Slide 5-7",
            "thesis_section": "5.3 / 5.6",
            "title": "管网软件或 GIS 中的监测节点布局截图",
            "output_file": "figures/screenshot_needed/F5_S01_network_layout_screenshot.png",
            "source_data": "user screenshot from SWMM/GIS/script viewer",
            "who_handles": "User",
            "status": "todo_user",
            "claim": "真实管网背景中展示不同布局的监测点位置",
        },
        {
            "fig_id": "F5-I01",
            "category": "imagegen_prompted",
            "ppt_slide": "Slide 5-0 cover",
            "thesis_section": "chapter opener",
            "title": "第五章概念封面图",
            "output_file": "figures/imagegen_prompted/F5_I01_ch5_cover_concept.png",
            "source_data": "prompt in imagegen_prompts.md",
            "who_handles": "Codex imagegen after style confirmation",
            "status": "prompt_ready",
            "claim": "监测节点布局优化的主题视觉，不作为实验数据证据",
        },
    ]
    index = pd.DataFrame(rows)
    index.to_csv(PACK_ROOT / "figure_index.csv", index=False, encoding="utf-8-sig")

    ppt_lines = [
        "# 第5章 PPT 插图索引",
        "",
        "| PPT页 | 推荐图号 | 文件 | 用途 | 状态 |",
        "|---|---|---|---|---|",
    ]
    for _, row in index.iterrows():
        ppt_lines.append(
            f"| {row['ppt_slide']} | {row['fig_id']} | `{row['output_file']}` | {row['claim']} | {row['status']} |"
        )
    (PACK_ROOT / "ppt_insert_index.md").write_text("\n".join(ppt_lines) + "\n", encoding="utf-8")

    raw_lines = [
        "# 第5章图件原始数据说明",
        "",
        "本文件说明图件资产包中每类图的证据来源。数据图优先使用 raw metrics JSON、defect matrix 和候选可观测性分层表，不使用旧探索版本作为正式主线。",
        "",
        "## 原始来源",
        "",
        f"- raw metrics JSON: `{RAW_REPORTS}`",
        f"- live clean v0_2 metrics: `{LIVE_REPORTS}`",
        f"- defect matrix: `{DEFECT_MATRIX}`",
        f"- candidate observability tiers: `{CANDIDATE_TIERS}`",
        f"- thesis tables: `{THESIS_TABLES}`",
        "",
        "## 生成数据",
        "",
        "- `data/ch5_seed42_by_scenario_raw_metrics.csv`: seed42 下正式方法逐场景定位结果，已合并缺陷类型和 direct/near/far 分组。",
        "- `data/ch5_seed42_observability_group_performance.csv`: direct/near/far 分组后的 MRR 与 Top-1。",
        "- `data/ch5_seed42_hard_candidate_performance.csv`: Degree N25 下 far 候选定义的 hard group 与其他场景对比。",
    ]
    (PACK_ROOT / "raw_data_catalog.md").write_text("\n".join(raw_lines) + "\n", encoding="utf-8")

    imagegen_lines = [
        "# ImageGen 备选提示词",
        "",
        "这些图只用于 PPT 氛围页或章节封面，不作为实验数据证据。若后续正式生成，应保存到 `figures/imagegen_prompted/` 并更新 `figure_index.csv`。",
        "",
        "## F5-I01 第五章概念封面图",
        "",
        "Use case: scientific-educational",
        "Asset type: thesis defense slide cover visual",
        "Primary request: an abstract but realistic drainage network monitoring layout optimization visual, showing a simplified urban pipe network map with glowing sensor nodes and diagnostic feedback arrows",
        "Style/medium: polished scientific illustration, modern academic presentation style",
        "Composition/framing: wide 16:9, left side network topology, right side subtle feedback loop, enough negative space for a Chinese chapter title",
        "Color palette: restrained teal, graphite, muted amber highlights",
        "Constraints: no readable text, no logos, no watermarks, no people, no decorative fantasy elements",
    ]
    (FIG_IMAGEGEN / "imagegen_prompts.md").write_text("\n".join(imagegen_lines) + "\n", encoding="utf-8")

    screenshot_lines = [
        "# 需要用户截图的图件",
        "",
        "## F5-S01 管网软件或 GIS 中的监测节点布局截图",
        "",
        "建议你自己截取：",
        "- 底图：SWMM / GIS / 你当前可视化脚本中的真实管网拓扑；",
        "- 叠加：Degree、Cand-Obs、v2_2 clean 中至少一种监测节点布局；",
        "- 用途：PPT 的 Slide 5-3 或 Slide 5-7，用真实工程画面增强可信度；",
        "- 保存文件名：`F5_S01_network_layout_screenshot.png`；",
        "- 保存位置：`figures/screenshot_needed/`。",
        "",
        "注意：这类截图不作为定量实验图，正文中需要配合数据图使用。",
    ]
    (FIG_SCREENSHOT / "README.md").write_text("\n".join(screenshot_lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    raw = load_by_scenario()
    plot_main_dot_error()
    plot_scenario_distribution(raw)
    plot_observability_group_performance(raw)
    plot_hard_candidate_performance(raw)
    plot_budget_structure()
    plot_jaccard_clean()
    plot_generated_protocol_loop()
    plot_generated_learning_levels()
    write_indexes()
    print(f"Figure asset pack updated: {PACK_ROOT}")


if __name__ == "__main__":
    main()
