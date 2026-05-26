# CH5 P2 embedding-guided clean

This batch records the embedding-guided clean layout and its diagnosis-seed
evaluation results.

Method role:
- This is a diagnosis-representation-guided layout probe.
- It reuses the trained diagnosis encoder checkpoint and does not learn from
  historical layout scores.
- The layout is generated once from the seed42 encoder and then evaluated under
  diagnosis seeds 7, 42, and 123. These seeds are diagnosis evaluation seeds,
  not layout-generation seeds.

Key protocol:
- Checkpoint: `E:\11.16\script2_new\outputs\model_checkpoints\best_model_ch4_timewin_seq24_s42.pth`
- Resolved encoder type: `hydraulic_inverse_deepattn`
- Train windows used for embedding extraction: `12980`
- Embedding shape: `[128, 256]`
- Selection rule: max-min diversity on L2-normalized node embeddings.
- Evaluation: Chapter-5 sparse-observation scenario split, seeds [7, 42, 123], 25 epochs.

Layout structure:
- overlap_count: 7
- direct / near / far: 7 / 22 / 21

Multi-seed result:
- MRR mean/std: 0.832548 / 0.066489
- Top-1 mean/std: 0.737893 / 0.081333
- Top-3 mean/std: 0.906945 / 0.068862
- Top-5 mean/std: 0.959640 / 0.053257

Outputs:
- `CH5-P2_embedding_guided_clean_layout_structure_seed42.csv`
- `CH5-P2_embedding_guided_clean_selection_trace_seed42.csv`
- `CH5-P2_embedding_guided_clean_evaluation_seed42.csv`
- `CH5-P2_embedding_guided_clean_evaluation_all_seeds.csv`
- `CH5-P2_embedding_guided_clean_seed_summary.csv`
- `CH5-P2_embedding_guided_clean_by_scenario_seed42.csv`
- `CH5-P2_embedding_guided_clean_by_scenario_all_seeds.csv`
- `CH5-P2_embedding_guided_clean_seed42_comparison.csv`
- `CH5-P2_embedding_guided_clean_all_seed_comparison.csv`
- `CH5-P2_embedding_guided_clean_comparison_seed_summary.csv`
- `CH5-P2_monitor_nodes_embedding_guided_clean_N25.json`
