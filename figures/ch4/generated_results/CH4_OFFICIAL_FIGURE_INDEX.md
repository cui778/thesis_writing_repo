# CH4 official figure chain

This index separates the new numbered CH4 figure chain from legacy scripts and historical protocol outputs.

## Official numbered scripts

| No. | Script | Source data | Output folder | Status |
|---|---|---|---|---|
| 01 | `figures/scripts/ch4/draw_01_ch4_main_model_multiseed.py` | `CH4-F06_main_model_multiseed.csv` | `01_CH4_main_model_multiseed` | Formal, keep |
| 02 | `figures/scripts/ch4/draw_02_ch4_task_level_summary.py` | `CH4-F07_task_level_results_summary.csv` | `02_CH4_task_level_summary` | Formal mainline row only, keep |
| 03 | `figures/scripts/ch4/draw_03_ch4_formal_model_comparison.py` | `CH4-F08_formal_model_comparison_multiseed_summary.csv` | `03_CH4_formal_model_comparison` | Formal, keep |
| 04 | `figures/scripts/ch4/draw_04_ch4_window_length_tradeoff.py` | `CH4-F09b_formal_time_window_length_eval_summary.csv` | `04_CH4_window_length_tradeoff` | Formal trend, keep |
| 05 | `figures/scripts/ch4/draw_05_ch4_ie_type_analysis.py` | `CH4-F10a_formal_ie_type_group_multiseed_summary.csv` | `05_CH4_ie_type_analysis` | Formal, keep |
| 06 | `figures/scripts/ch4/draw_06_ch4_observability_generalization.py` | `CH4-F10b_candidate_observability_counts.csv`; `CH4-F10b_nodehold_observability_summary.csv` | `06_CH4_observability_generalization` | Backup/appendix candidate |
| 07 | `figures/scripts/ch4/draw_07_ch4_main_result_fingerprint.py` | `CH4-F06_main_model_multiseed.csv`; `CH4-F07_task_level_results_summary.csv` | `07_CH4_main_result_fingerprint` | Official main-result figure; preferred over 01/02 ordinary bars |
| 08 | `figures/scripts/ch4/draw_08_ch4_model_gain_forest.py` | `CH4-F08_formal_model_comparison_multiseed_summary.csv` | `08_CH4_model_gain_forest` | Official model-comparison core figure |
| 09 | `figures/scripts/ch4/draw_09_ch4_window_pareto_tradeoff.py` | `CH4-F09b_formal_time_window_length_eval_summary.csv` | `09_CH4_window_pareto_tradeoff` | Mechanism-analysis figure; preferred over ordinary trend lines |
| 10 | `figures/scripts/ch4/draw_10_ch4_ie_observability_mechanism.py` | `CH4-F10a_formal_ie_type_group_multiseed_summary.csv`; `CH4-F10b_candidate_observability_counts.csv`; `CH4-F10b_nodehold_observability_summary.csv` | `10_CH4_ie_observability_mechanism` | Mechanism-explanation figure for thesis and defense |
| 11 | `figures/scripts/ch4/draw_11_ch4_model_progression_hybrid.py` | `CH4-F08_formal_model_comparison_multiseed_summary.csv` | `11_CH4_model_progression_hybrid` | Hybrid bar-line model progression figure |
| 12 | `figures/scripts/ch4/draw_12_ch4_window_hybrid_dual_axis.py` | `CH4-F09b_formal_time_window_length_eval_summary.csv` | `12_CH4_window_hybrid_dual_axis` | Hybrid bar-line dual-axis window tradeoff figure |
| 13 | `figures/scripts/ch4/draw_13_ch4_single_scenario_diagnosis_profile.py` | `formal_window_length/ch4_formal_window_3h_s42_window_predictions.csv`; `formal_window_length/ch4_formal_window_3h_s42_event_predictions.csv` | `13_CH4_single_scenario_diagnosis_profile` | Process-evidence figure: window probability to scene interval and node localization |
| 14 | `figures/scripts/ch4/draw_14_ch4_spatial_diagnosis_evidence_chain.py` | `formal_window_length/ch4_formal_window_3h_s42_window_predictions.csv`; `formal_window_length/ch4_formal_window_3h_s42_event_predictions.csv`; `parsed_inp_data.json` | `14_CH4_spatial_diagnosis_evidence_chain` | Spatial process-evidence figure: window-level top candidates on topology |
| 16 | `figures/scripts/ch4/draw_16_ch4_grouped_model_comparison.py` | `CH4-F11_method_ablation_summary.csv` | `16_CH4_grouped_model_comparison` | Formal grouped model-comparison figure; preferred model comparison |
| 17 | `figures/scripts/ch4/draw_17_ch4_deepattn_depth_ablation.py` | `CH4-F11_method_ablation_summary.csv` | `17_CH4_deepattn_depth_ablation` | Formal depth-ablation figure |
| 18 | `figures/scripts/ch4/draw_18_ch4_path_prior_ablation.py` | `CH4-F11_method_ablation_summary.csv`; `CH4-F11_method_ablation_by_seed.csv` | `18_CH4_path_prior_ablation` | Formal path-prior mechanism figure |

## New thickening figures

| No. | Scientific question | Thesis/PPT section | Role | Relation to existing figures |
|---|---|---|---|---|
| 07 | Does fixed `degree_N25` achieve low false alarms, reliable scene alarms, and usable candidate localization at the same time? | 4.4.1, 4.4.2 | Official main figure | Replaces `01/02` ordinary bar snapshots as the preferred thesis/PPT figure |
| 08 | Where does `hydraulic_inverse_deepattn` gain over sequence-only and simpler graph baselines? | 4.4.3 | Official model comparison | Complements `03`; adds gain-over-baseline CSV |
| 09 | How does window length trade spatial localization, temporal boundary recovery, and false-alarm control? | 4.4.5 | Mechanism analysis | Preferred over `04` if only one window-length figure can be used |
| 10 | Do I/E type gaps and direct/near/far observability jointly explain localization difficulty and node-holdout limits? | 4.4.6, 4.5.1, 4.5.2 | Mechanism explanation | Upgrades `05/06` into one narrative mechanism figure |
| 11 | As models become more graph-aware and hydraulically informed, do localization quality and false-alarm control improve together? | 4.4.3 | PPT/thesis hybrid result figure | Alternative to `08` when a heatmap feels too forced |
| 12 | Which window length best balances localization strength, temporal boundary error, and false-alarm control? | 4.4.5 | PPT/thesis hybrid mechanism figure | Alternative to `09` when a direct dual-axis story is clearer |
| 13 | For a representative formal defect scene, how does the model turn window-level `p_active` and top candidates into a scene-level interval and localized defect node? | 4.4.1, 4.4.2 | Process-evidence figure | Fills the missing evidence chain between aggregate metrics and actual diagnosis behavior |
| 14 | Where do window-level top candidates appear on the network, and how do success, temporal under-coverage, and spatial offset cases differ? | 4.4.1, 4.4.2, 4.5.1 | Spatial process-evidence figure | Complements `13`; uses available top-candidate trajectories rather than unavailable full node-score logits |
| 16 | Does the proposed model improve localization because of generic graph modeling, a recurrent encoder change, or multi-layer path-guided aggregation? | 4.3.1 | Formal core result | Reorganizes sequence, graph, single-layer path, and proposed models by evidence role |
| 17 | How many path-attention layers are needed before localization performance saturates? | 4.3.2 | Formal method ablation | Establishes L3 as the accuracy-complexity-error-control operating point |
| 18 | Does the complete hydraulic path prior contribute beyond content attention or distance alone? | 4.3.3 | Formal mechanism ablation | Shows gains in front-rank localization, event Top-1, and false-alarm control |

## Current thesis priority

1. `16_CH4_grouped_model_comparison`: primary evidence for the proposed model.
2. `17_CH4_deepattn_depth_ablation`: primary evidence for the multi-layer design.
3. `18_CH4_path_prior_ablation`: primary evidence for the hydraulic path prior.
4. `12_CH4_window_hybrid_dual_axis`: parameter sensitivity.
5. `13_CH4_single_scenario_diagnosis_profile`: process evidence.
6. `15_CH4_defect_monitor_distance_performance`: spatial-condition analysis, if retained.

Figures `05`, `06`, `10`, and `14` are supplementary or defense candidates. I/E differences and adverse cases do not carry the main method-validity argument.

## Legacy retained

The previous `plot_*.py` scripts and existing unnumbered figures are intentionally retained for traceability. Do not use `figures/ch4/source_data/legacy_old_protocol` for official CH4 figures.

`CH4-F08_feature_set_comparison.csv` is historical and is not part of the official normal20 protocol.
