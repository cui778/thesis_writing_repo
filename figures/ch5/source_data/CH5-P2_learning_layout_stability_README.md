# CH5 P2 learning layout stability tables

This batch summarizes layout-generation stability only. It does not train or
evaluate diagnosis models.

Scope:

- methods: v0_2 clean, v2_2 clean
- budget for stability: N=25
- layout seeds: 1..10

Data scale:

- layout instances: 20
- Jaccard pairs: 90

Important boundary:

- `layout_seed` is not diagnosis seed.
- These tables support generation stability, not diagnostic performance.

Outputs:

- `CH5-P2_learning_layout_stability_instances.csv`
- `CH5-P2_learning_layout_jaccard_pairs.csv`
- `CH5-P2_learning_layout_node_frequency.csv`
- `CH5-P2_learning_layout_structure_summary.csv`
