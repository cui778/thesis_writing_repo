# CH5 official figure chain

This index records the numbered CH5 figures under the fixed DeepAttn-L3 diagnosis protocol.

| No. | Script | Scientific question | Role | Main source |
|---|---|---|---|---|
| 01 | `draw_01_ch5_expt_n25_main_table.py` | Does changing the monitoring layout improve localization at N=25? | Formal main result | `CH5-EXPT_fixed_protocol_N25_main_table.csv` |
| 02 | `draw_02_ch5_budget_sweep_seed42.py` | How do layout rankings change with monitoring budget? | Budget trend; seed42 only | `CH5-budget_sweep_seed42.csv` |
| 03 | `draw_03_ch5_layout_structure.py` | How are defect-space coverage and localization performance coupled? | Formal mechanism result | `CH5-N25_layout_structure.csv` |
| 04 | `draw_04_ch5_hard_candidate_analysis.py` | Which defect locations show the largest layout-dependent observability changes? | Boundary/mechanism analysis | `CH5-N25_hard_candidate_analysis.csv` |
| 05 | `draw_05_ch5_defect_type_analysis.py` | Are I/E group results visibly different? | Supplementary grouping result | `CH5-N25_by_defect_type_analysis.csv` |
| 06 | `draw_06_ch5_pairwise_jaccard.py` | Do different methods select the same monitoring nodes? | Formal structural-independence evidence | `CH5-N25_pairwise_jaccard.csv` |
| 07 | `draw_07_ch5_coverage_rate_response.py` | Does localization improve monotonically with defect-space coverage? | Seed42 mechanism probe | `CH5-coverage_rate_controlled_eval_seed42.csv` |
| 08 | `draw_08_ch5_layout_spatial_distribution.py` | Where do different methods place sensors across budgets and the network? | Spatial presentation figure | layout JSON/summary files |
| 09 | `draw_09_ch5_embedding_guided_mechanism.py` | How does diagnosis embedding guide diverse node selection? | Method illustration | trained diagnosis embedding and topology |
| 10 | `draw_10_ch5_embedding_source_ablation.py` | Is E-G effective because of diagnosis embeddings or merely max-min dispersion? | Formal source-ablation figure | `CH5-targeted_supplements_summary.csv` |

## Thesis priority

1. `01_CH5_EXPT_N25`: N=25 main comparison.
2. `03_CH5_layout_structure`: effectiveness and insufficiency of defect-space proximity.
3. `10_CH5_embedding_source_ablation`: direct evidence for the proposed diagnosis representation.
4. `06_CH5_pairwise_jaccard`: structural independence of E-G layouts.
5. `02_CH5_budget_sweep_seed42` plus the N=5 multi-seed table: budget boundary.
6. `08_CH5_layout_spatial_distribution`: intuitive network-space presentation.

`05_CH5_defect_type_analysis` is supplementary only. The I/E gap is not used as a core method claim because group sizes are not fully balanced and absolute gap differences are small.

`07_CH5_coverage_rate_response` is a mechanism probe rather than a strict causal experiment: some low-coverage settings correspond to identical node sets, and the response is non-monotonic.

## Main conclusions supported by figures

- Task-informed layouts improve MRR from Degree's 0.825 to 0.878-0.905 at N=25.
- Two-stage v1 obtains the highest MRR (0.905); Embedding-Guided obtains competitive MRR (0.897), the highest Top-3 (0.981), and the smallest MRR standard deviation (0.017).
- Defect-space proximity is effective but insufficient: Cand-Obs and Two-stage both leave one far defect node, yet their MRR differs by 0.027.
- Under the same max-min selector, diagnosis embeddings outperform topology and coordinate representations by 0.089 and 0.067 MRR, respectively.
- N=5 is an applicability boundary: Degree and E-G have similar MRR, while Two-stage v1 degrades consistently across seeds.
