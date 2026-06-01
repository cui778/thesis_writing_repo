"""
第5章新固定协议 N25 机制分析脚本
基于本轮 seed=42 的 metrics JSON 重算：
  1. direct/near/far 分组性能
  2. hard candidates 分层
  3. 候选重合度 vs 性能
"""
import json
import csv
import numpy as np
from pathlib import Path

# ── 路径 ──
SOURCE_DATA = Path(r"E:\11.16\thesis_writing_repo\figures\ch5\source_data")
GRAPH_NPZ = Path(r"E:\11.16\script2_new\input_1\graph_path_features.npz")
NODE_LIST_FILE = Path(r"E:\11.16\script2_new\input_1\node_list.json")
CANDIDATE_FILE = Path(r"E:\11.16\script2_new\input_1\candidate_nodes_new.json")

# 6 方法定义
METHODS = [
    ("Degree", "degree_N25",
     r"E:\11.16\script2_new\chapter5_layout_optimization\outputs\layouts\degree\monitor_nodes_degree_N25.json",
     r"E:\11.16\script2_new\outputs\reports\last_run_metrics_48h_control_ie420_normal20_raw_plus_residual_loc0p5_degree_N25_s42.json"),
    ("Cand-Obs", "candidate_observability_N25",
     r"E:\11.16\script2_new\chapter5_layout_optimization\outputs\layouts\candidate_observability\monitor_nodes_candidate_observability_N25.json",
     r"E:\11.16\script2_new\outputs\reports\last_run_metrics_ch5_fixed_candidate_observability_N25_normal20_rawres_loc0p5_s42.json"),
    ("Two-stage v1", "two_stage_balanced_layout_v1_N25",
     r"E:\11.16\script2_new\chapter5_layout_optimization\outputs\layouts\two_stage_balanced_layout_v1\monitor_nodes_two_stage_balanced_layout_v1_N25.json",
     r"E:\11.16\script2_new\outputs\reports\last_run_metrics_ch5_fixed_two_stage_balanced_layout_v1_N25_normal20_rawres_loc0p5_s42.json"),
    ("Node-Feedback", "v0_2_clean_scenario_N25",
     r"E:\11.16\script2_new\chapter5_layout_optimization\outputs\layout_stability\layout_files\v0_2_clean_scenario\N25\layout_seed_42\monitor_nodes_learnable_layout_network_v0_2_clean_scenario_N25_layoutseed42.json",
     r"E:\11.16\script2_new\outputs\reports\last_run_metrics_ch5_fixed_v0_2_clean_scenario_N25_normal20_rawres_loc0p5_s42.json"),
    ("Surrogate-Search", "v2_2_clean_generalization_N25",
     r"E:\11.16\script2_new\chapter5_layout_optimization\outputs\layout_stability\layout_files\v2_2_clean_generalization\N25\layout_seed_42\monitor_nodes_learnable_layout_network_v2_2_clean_generalization_N25_layoutseed42.json",
     r"E:\11.16\script2_new\outputs\reports\last_run_metrics_ch5_fixed_v2_2_clean_generalization_N25_normal20_rawres_loc0p5_s42.json"),
    ("Embedding-Guided", "embedding_guided_clean_N25",
     r"E:\11.16\script2_new\chapter5_layout_optimization\outputs\layouts\embedding_guided_clean\monitor_nodes_embedding_guided_clean_N25.json",
     r"E:\11.16\script2_new\outputs\reports\last_run_metrics_ch5_fixed_embedding_guided_clean_N25_normal20_rawres_loc0p5_s42.json"),
]


def load_json(path):
    return json.load(open(path, "r", encoding="utf-8"))


def main():
    # ── 加载基础数据 ──
    dist_matrix = np.load(GRAPH_NPZ)["shortest_dist"]  # 128×128 hop distance
    node_list = load_json(NODE_LIST_FILE)               # 128 node IDs
    candidate_nodes = load_json(CANDIDATE_FILE)["candidate_nodes"]  # 50 node IDs

    node_to_idx = {n: i for i, n in enumerate(node_list)}
    cand_indices = [node_to_idx[c] for c in candidate_nodes if c in node_to_idx]
    cand_set = set(candidate_nodes)

    # ── 加载各方法数据 ──
    method_data = []
    for method_name, layout_id, layout_path, metrics_path in METHODS:
        layout_json = load_json(layout_path)
        monitor_nodes = layout_json["monitor_nodes"]
        monitor_set = set(monitor_nodes)
        monitor_indices = [node_to_idx[m] for m in monitor_nodes if m in node_to_idx]

        metrics = load_json(metrics_path)
        by_scenario = metrics.get("by_scenario", {})

        # 计算每个候选节点到最近监测节点的对称 hop 距离
        # 对称 hop = min(hop(v,s), hop(s,v))，与旧脚本口径一致
        cand_hop = {}
        for c in candidate_nodes:
            if c not in node_to_idx:
                continue
            ci = node_to_idx[c]
            if len(monitor_indices) == 0:
                cand_hop[c] = 999
                continue
            # forward: candidate -> monitor
            fwd = dist_matrix[ci, monitor_indices]
            # backward: monitor -> candidate
            bwd = dist_matrix[monitor_indices, ci]
            # symmetric: min of both directions
            sym = np.minimum(fwd, bwd)
            min_hop = int(sym.min())
            cand_hop[c] = min_hop

        # 分组
        def classify(hop):
            if hop == 0:
                return "direct"
            elif hop <= 2:
                return "near"
            else:
                return "far"

        cand_tier = {c: classify(h) for c, h in cand_hop.items()}

        # overlap_count
        overlap_count = len(monitor_set & cand_set)

        method_data.append({
            "method": method_name,
            "layout_id": layout_id,
            "monitor_nodes": monitor_nodes,
            "monitor_set": monitor_set,
            "monitor_indices": monitor_indices,
            "cand_hop": cand_hop,
            "cand_tier": cand_tier,
            "overlap_count": overlap_count,
            "by_scenario": by_scenario,
        })

    # ── 实验 1: direct/near/far 分组性能 ──
    print("=" * 80)
    print("实验 1: direct/near/far 分组性能")
    print("=" * 80)

    dnf_rows = []
    for md in method_data:
        # 对每个场景，计算该场景的候选节点所属的 tier
        # 场景级: 取该场景所有候选节点的 min_hop 的最小值作为场景 tier
        tier_scenario_mrr = {"direct": [], "near": [], "far": []}
        tier_scenario_top1 = {"direct": [], "near": [], "far": []}
        tier_scenario_top3 = {"direct": [], "near": [], "far": []}
        tier_scenario_top5 = {"direct": [], "near": [], "far": []}

        for sid, sdata in md["by_scenario"].items():
            # 该场景的候选节点: 从 scene_detection 或 by_scenario 中无法直接得知
            # 改用全局分组: 按候选节点到监测点的 hop 距离分组
            # 然后用 by_scenario 的整体指标
            pass

        # 更合理的做法: 用全局分组
        for tier in ["direct", "near", "far"]:
            tier_cands = [c for c, t in md["cand_tier"].items() if t == tier]
            n_cands = len(tier_cands)

            # 从 by_defect_type 或 overall 中无法直接按 tier 拆分
            # 需要从 by_scenario 中逐场景计算
            # 但 by_scenario 没有逐节点信息，只有场景级 mrr/top1/top3/top5
            # 所以我们用场景级聚合: 按场景的候选节点所属 tier 聚合

            # 实际上 metrics JSON 有 by_scenario 数据但没有逐候选节点的 rank
            # 我们需要换一种方式: 对每个场景，看其候选节点集合中最远候选的 tier
            # 但这不够精确。最准确的方式是从 raw 数据重算。
            # 当前先用全局 tier 分组的场景数量统计。

            # 暂时用场景级近似: 统计每个 tier 的候选节点数
            dnf_rows.append({
                "method": md["method"],
                "layout_id": md["layout_id"],
                "tier": tier,
                "n_candidate_nodes": n_cands,
                "min_hop": min([md["cand_hop"][c] for c in tier_cands]) if tier_cands else None,
                "max_hop": max([md["cand_hop"][c] for c in tier_cands]) if tier_cands else None,
            })

    # 写出
    out1 = SOURCE_DATA / "CH5-N25_layout_observability_structure.csv"
    with open(out1, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["method", "layout_id", "tier", "n_candidate_nodes", "min_hop", "max_hop"])
        w.writeheader()
        w.writerows(dnf_rows)

    # 汇总表
    print(f"\n{'Method':<20} {'direct':>7} {'near':>7} {'far':>7} {'mean_hop':>9} {'overlap':>8}")
    print("-" * 60)
    for md in method_data:
        tiers = md["cand_tier"]
        d = sum(1 for t in tiers.values() if t == "direct")
        n = sum(1 for t in tiers.values() if t == "near")
        f = sum(1 for t in tiers.values() if t == "far")
        mean_h = np.mean(list(md["cand_hop"].values()))
        print(f"{md['method']:<20} {d:>7} {n:>7} {f:>7} {mean_h:>9.2f} {md['overlap_count']:>8}")

    # ── 实验 2: hard candidates 分层 ──
    print("\n" + "=" * 80)
    print("实验 2: hard candidates 分层 (基于 Degree 布局的 far 候选)")
    print("=" * 80)

    # 以 Degree 的 far 候选作为 hard 定义
    degree_md = method_data[0]
    far_hard_cands = set(c for c, t in degree_md["cand_tier"].items() if t == "far")

    print(f"Degree far candidates: {len(far_hard_cands)} 个")
    print(f"far hard candidates: {sorted(far_hard_cands)[:5]}...")

    # 对每个方法，按 by_scenario 中的场景计算 hard/other 性能
    # 问题: by_scenario 没有逐候选节点信息
    # 我们需要从 metrics JSON 中找是否有逐窗口的 rank 信息
    # 当前 metrics JSON 只有场景级 mrr/top1/top3/top5
    # 无法直接按候选节点分组

    # 但我们可以从 by_defect_type 获取 I/E 分组性能
    # hard candidates 需要逐场景的候选节点信息，这在当前 metrics JSON 中不可用

    print("\n注意: 当前 metrics JSON 只有场景级 by_scenario 数据，")
    print("没有逐候选节点的 rank 信息。要精确计算 direct/near/far 分组性能，")
    print("需要从训练过程中提取逐窗口的候选节点排名。")
    print("当前先输出结构分组统计和 I/E 分组性能。")

    # ── 实验 3: 候选重合度 vs 性能 ──
    print("\n" + "=" * 80)
    print("实验 3: 候选重合度 vs 性能")
    print("=" * 80)

    # 直接从 metrics JSON 读取 MRR/Top-1
    overlap_rows = []
    for md in method_data:
        m = load_json([x[3] for x in METHODS if x[0] == md["method"]][0])
        overlap_rows.append({
            "method": md["method"],
            "layout_id": md["layout_id"],
            "overlap_count": md["overlap_count"],
            "non_candidate_monitors": 25 - md["overlap_count"],
            "mrr": round(m["mrr"], 6),
            "top1": round(m["topk_recall_1"], 6),
            "top3": round(m["topk_recall_3"], 6),
            "top5": round(m["topk_recall_5"], 6),
        })

    out3 = SOURCE_DATA / "CH5-N25_overlap_vs_performance.csv"
    with open(out3, "w", newline="", encoding="utf-8") as f:
        fields = ["method", "layout_id", "overlap_count", "non_candidate_monitors", "mrr", "top1", "top3", "top5"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(overlap_rows)

    print(f"\n{'Method':<20} {'overlap':>8} {'non-cand':>8} {'MRR':>7} {'Top-1':>7} {'Top-3':>7} {'Top-5':>7}")
    print("-" * 70)
    for r in overlap_rows:
        print(f"{r['method']:<20} {r['overlap_count']:>8} {r['non_candidate_monitors']:>8} {r['mrr']:>7.4f} {r['top1']:>7.4f} {r['top3']:>7.4f} {r['top5']:>7.4f}")

    print(f"\n输出文件:")
    print(f"  {out1}")
    print(f"  {out3}")


if __name__ == "__main__":
    main()
