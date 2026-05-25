# CH5 candidate-overlap evidence

This table supports the Chapter-5 claim that monitor layout optimization is not
equivalent to maximizing candidate-node overlap.

Two evidence groups are included:

1. `formal_clean_mainline`: formal five-method comparison averaged over
   diagnosis evaluation seeds 7, 42, and 123.
2. `overlap_controlled_probe_seed42`: existing seed-42 probe layouts with the
   same overlap count as Degree / v2_2 clean, used only as supplementary
   mechanism evidence.

Important boundary:

- The probe rows are not part of the formal main ranking.
- The table does not claim that candidate-only layouts have been fully trained
  and evaluated. It demonstrates that higher overlap_count is not sufficient to
  explain the best mainline performance, and that equal overlap_count can still
  produce different diagnostic performance.
