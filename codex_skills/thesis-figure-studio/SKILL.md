---
name: thesis-figure-studio
description: Use when drawing, auditing, selecting, or polishing thesis/PPT figures for this project, especially Chapter 3-5 data figures. Enforces formal data protocols, numbered scripts/outputs, Chapter 5 visual style, scientific-question-first figure selection, and PNG+editable-SVG export.
---

# Thesis Figure Studio

Use this skill whenever the user asks to create, revise, audit, or plan thesis/PPT figures for `E:/11.16/thesis_writing_repo`.

The core rule is: draw from the formal data first, and only after the figure has a clear scientific role. Do not create decorative mechanism diagrams before exhausting the real-data evidence.

## Figure Gate

Before writing or running a figure script, explicitly answer these checks:

1. Scientific question: what question does this figure answer?
2. Thesis/PPT section: which chapter section or slide does it support?
3. Figure identity: formal main figure, mechanism analysis figure, PPT figure, or backup/defense figure?
4. Data source: exact file path(s), and whether the source belongs to the current formal protocol.
5. Redundancy: whether it duplicates an existing figure and should replace, supplement, or be demoted.
6. Composition: whether it should stand alone or be combined with another table/figure.

Prefer keeping and normalizing useful existing figures over redrawing for its own sake. Preserve old scripts and old-protocol outputs unless the user explicitly asks to delete them.

## Formal Data Protocols

### Chapter 3

Official dataset and matrix:

- Dataset: `E:/11.16/script2_new/training_data_new/ie420_plus_normal20_v1`
- Defect matrix: `E:/11.16/script2_new/input_1/defect_matrix_diverse_ie_v4_formal_conservative420_seed42.csv`
- Residual parquet: `E:/11.16/script2_new/training_data_new/ie420_plus_normal20_v1/node_timeseries_with_residuals.parquet`
- Scenario summary: `E:/11.16/script2_new/training_data_new/ie420_plus_normal20_v1/scenario_summary.csv`
- Manifest: `E:/11.16/script2_new/training_data_new/ie420_plus_normal20_v1/dataset_manifest.json`
- Topology candidates: `E:/11.16/script2_new/input_1/node_list.json`, `candidate_nodes_new.json`, `monitor_nodes_degree_N25.json`
- INP/topology: `E:/11.16/input_data/2_tuned_v3_merged1.inp`, `E:/11.16/script2_new/input_1/parsed_inp_data.json`

Before drawing Chapter 3 figures, confirm the manifest contains:

- `dataset_type = ie420_plus_normal20`
- `defect_csv_path` points to `defect_matrix_diverse_ie_v4_formal_conservative420_seed42.csv`
- `scenario_count = 441`
- `time_gated_count = 421`
- `persistent_count = 0`
- `normal_count = 20`
- formal defect type counts: `I = 250`, `E = 170`

Never auto-select or use these for official Chapter 3 figures:

- `persistent_ie_fullwindow_v1_seed42`
- `ie420_plus_persistent84_plus_normal20_v1`
- `normal_multibaseline_v1_seedset10`
- `ie420_plus_normal_multibaseline_v1_seedset10`
- `fulltime_full_ie_v4_formal_conservative420_seed42`
- `chapter3_data_generation/legacy_exploration`
- any `persistent`, `fulltime`, `legacy`, or `seedset10` data discovered by broad search

The residual parquet is large. Do not load the full file unless absolutely necessary. Prefer column filters, scenario filters, node filters, `pyarrow.dataset`, or `polars.scan_parquet`.

### Chapter 4

Use `E:/11.16/thesis_writing_repo/figures/ch4/source_data` for official summary figures. Keep old scripts and old口径 under their existing folders. New scripts must be numbered after the existing sequence.

Chapter 4 should not only add summary performance plots. Prioritize real model-process evidence when local prediction details exist:

- single-scenario diagnosis profile: true active, `p_active`, Top-1 trajectory, true-node rank
- normal vs active `p_active` distribution
- window-length Pareto tradeoff
- model comparison and I/E observability summaries only when they add a distinct argument

### Chapter 5

Chapter 5 is already comparatively mature. Avoid unlimited expansion. Keep the six formal figure/table designs and only add a spatial layout map when it improves PPT interpretability.

## Naming And Outputs

Scripts must be numbered:

- `E:/11.16/thesis_writing_repo/figures/scripts/ch3/draw_01_ch3_*.py`
- `E:/11.16/thesis_writing_repo/figures/scripts/ch4/draw_01_ch4_*.py`
- `E:/11.16/thesis_writing_repo/figures/scripts/ch5/draw_01_ch5_*.py`

Outputs must be numbered and placed in generated-result subdirectories:

- Chapter 3: `E:/11.16/thesis_writing_repo/figures/ch3/generated_results/NN_CH3_*`
- Chapter 4: `E:/11.16/thesis_writing_repo/figures/ch4/generated_results/NN_CH4_*`
- Chapter 5: `E:/11.16/thesis_writing_repo/figures/ch5/generated_results/NN_CH5_*`

Only export:

- `.png`
- `.svg`
- necessary cleaned or summary `.csv`

Never export `.pdf`.

Every Matplotlib script must set:

```python
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["savefig.dpi"] = 300
```

## Visual System

Use Chapter 5 as the visual baseline. Do not mechanically turn every CSV into a bar chart or every matrix into a heatmap. Choose the figure type from the data argument.

Good choices:

- parameter matrix
- normal envelope plus defect residual curve
- node-time residual energy heatmap
- topology residual spatial map
- dumbbell plot for paired gaps
- forest plot for model gains
- Pareto scatter for tradeoffs
- performance fingerprint when it truly summarizes a model profile
- clustered or Jaccard matrix for overlap/stability
- hybrid bar+line or dual-axis plot when it clarifies coupled performance and error trends
- compact multi-panel only when panels form an evidence chain

Avoid:

- ordinary bar charts without a thesis-level comparison
- ordinary line charts without a diagnostic story
- thin lollipop charts
- ranking plots with no mechanism
- colorful network diagrams with weak interpretability
- heatmaps or group figures created only because the checklist mentions them

### Fixed Colors

Use these method colors:

```python
METHOD_COLORS = {
    "Degree": "#4E79A7",
    "Betweenness": "#59A14F",
    "Cand-Obs": "#F28E2B",
    "Two-stage v1": "#E15759",
    "Node-Feedback": "#B07AA1",
    "Embedding-Guided": "#76B7B2",
}
```

Use these metric colors:

```python
METRIC_COLORS = {
    "mrr": "#4E79A7",
    "top1": "#F28E2B",
    "top3": "#59A14F",
    "top5": "#E15759",
    "event_top1": "#B07AA1",
    "event_top3": "#76B7B2",
    "event_top5": "#EDC948",
    "scene_f1": "#9C755F",
}
```

If Top-5 or Scene F1 is saturated, weaken or omit it. Prefer highlighting:

- MRR
- Top-1
- Top-3
- Event Top-1
- Event Top-3
- Normal FPR
- I/E gap
- `mean_hop`
- far candidate
- Jaccard

### Heatmaps

Heatmap rules:

- use `imshow`, not `pcolormesh`
- prefer `cmap="YlGnBu"`
- keep the map square or close to square
- do not add white grid borders between cells
- do not show axis tick marks
- keep x/y labels and colorbar
- do not stretch with `aspect="auto"` unless the data shape demands it

### Non-Heatmap Axes

Axes should read as finite line segments, not infinite rays.

For ordinary Matplotlib axes, use a shared helper such as `style_axes_as_segments(ax)`:

- left spine from lower to upper y limit
- bottom spine from lower to upper x limit
- hide top and right spines unless explicitly needed
- use `spines.set_bounds(...)` after limits are fixed

## Current Priority Order

Chapter 3 first, because it lacks formal data-evidence figures:

1. `draw_01_ch3_ie420_parameter_matrix.py`
2. `draw_02_ch3_normal_envelope_defect_residual.py`
3. `draw_03_ch3_node_time_residual_energy.py`
4. `draw_04_ch3_topology_residual_spatial_map.py`

Then Chapter 4 process evidence:

1. single-scenario diagnosis profile
2. normal vs active `p_active` distribution
3. window-length Pareto tradeoff

Then Chapter 5 only if needed:

1. multi-layout sewer-network selected-node map

## Validation Checklist

For every new figure script:

1. Run `python -m py_compile`.
2. Run the script and confirm no `.pdf` appears.
3. Confirm outputs are PNG + SVG plus necessary CSV only.
4. Confirm SVG text is editable by checking `svg.fonttype = "none"` in the script.
5. Confirm output directory and filenames have the correct numeric prefix.
6. Visually inspect PNG for text overlap, legend occlusion, stretched heatmaps, and axis segment styling.
7. Confirm no forbidden Chapter 3 protocol paths were read.
8. Confirm old scripts, old figures, and old-protocol data were not modified.
