# CH5 fixed-protocol N25 main manifest

This manifest lists the first strict fixed-protocol runs needed for the Chapter 5 optimization-method main table.

Fixed protocol:

```text
teacher_subdir = ie420_plus_normal20_v1
feature_set = raw_plus_residual
lambda_loc = 0.5
model = hydraulic_inverse_deepattn
split = scenario
diagnosis_seed = 42
budget = N25
```

Methods:

```text
Cand-Obs
Two-stage v1
Node-Feedback
Surrogate-Search
Embedding-Guided
```

Boundary:

- `degree_N25` is already available as the Chapter 4 fixed-protocol reference.
- These five runs are the missing strict fixed-protocol runs for the Chapter 5 optimization-method main table.
- Because the machine has reported memory problems, run one command at a time and validate the expected metrics JSON immediately after each run.
- Do not batch-run these commands until hardware stability is fixed.
