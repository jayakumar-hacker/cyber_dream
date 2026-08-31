# CyberDream

**A Graph‑RSSM World Model for Predictive Cyber Defense.**

> One‑liner: CyberDream learns a compressed, dynamic "world model" of an
> enterprise network — as a graph — and imagines how an attack will unfold
> *before* it fully unfolds, so defenders can act on the predicted future
> instead of reacting to the past.

## Vision & UVP

Most cyber‑defense tooling is fundamentally retrospective: it detects and
classifies events that have already happened. CyberDream takes a
model‑based reinforcement‑learning approach (inspired by world models like
RSSM/Dreamer) but replaces flat sensor vectors with a **graph** representing
hosts, users, processes, and domains and how they relate to one another at
each point in time.

The unique value proposition is threefold:

1. **Structural awareness** — a Graph Neural Network encoder captures
   relational context (lateral movement, privilege escalation paths) that
   flat feature vectors discard.
2. **Temporal imagination** — a Recurrent State‑Space Model (RSSM) core
   learns network dynamics and can "roll forward" in latent space for *K*
   steps, producing a distribution over plausible near‑future states without
   needing to simulate the real network.
3. **Actionable explainability** — every prediction is paired with an
   attention/SHAP attribution trace and a latent trajectory visualization,
   so analysts get a ranked, human‑readable rationale instead of an opaque
   score.

This repository is a **research prototype / scaffold**. It defines the
architecture, interfaces, and configuration surface for an 8‑stage
pipeline. Model internals (layers, training loops, forward passes) are
intentionally left as docstring‑only stubs for the research team to fill
in during the sprint.

## The 8‑Stage Architecture (conceptual overview)

| # | Stage | Module(s) | Purpose |
|---|-------|-----------|---------|
| 1 | Feature Pipeline | `src/pipeline/feature_fusion.py` | Ingests raw flow/event records from CIC‑IDS‑2018 and CTU‑13, cleans and normalizes them, and fuses multiple sources into windowed feature tables (Parquet, in `data/processed/`). |
| 2 | Graph Builder | `src/pipeline/graph_constructor.py` | Converts each windowed feature table into a typed, attributed graph snapshot (nodes = hosts/users/processes/domains) and caches it as a PyG object in `data/graphs/`. |
| 3 | GNN Encoder | `src/core/spatial_encoder.py` | Compresses each graph snapshot into a fixed‑size latent embedding (GAT/GraphSAGE‑style). |
| 4 | RSSM World Model | `src/core/world_model.py` | Fuses the sequence of graph embeddings into a recurrent latent belief state describing the network's evolving condition over time. |
| 5 | Prediction Heads | `src/heads/prediction_heads.py` | Reads the belief state to produce a continuous risk score and a MITRE ATT&CK‑aligned stage classification. |
| 6 | Imagination Rollout | `src/simulator/rollout_engine.py` | Recursively advances the world model's prior dynamics *K* steps into the future ("dreaming"), and supports counterfactual ("what‑if") rollouts. |
| 7 | Explainability | `src/explainability/{attention,shap_wrapper,trajectory_viz}.py` | Attributes predictions back to contributing graph structure via attention weights and SHAP, and visualizes latent trajectories (UMAP). |
| 8 | Evaluation & Demo | `src/evaluation/{baselines,benchmark_runner}.py`, `app/` | Benchmarks the full model against non‑graph baselines (logistic regression, LSTM‑only), and exposes everything through a Streamlit demo. |

```
1. Feature Pipeline → 2. Graph Builder → 3. GNN Encoder → 4. RSSM World Model
                                                                     │
                        ┌────────────────────────────────────────────┘
                        ▼
              5. Prediction Heads ──► 6. Imagination Rollout
                        │                       │
                        └──────────┬────────────┘
                                   ▼
                    7. Explainability ──► 8. Evaluation / Demo UI
```

## Repository Layout

```
cyber_dream/
├── .gitignore                    # standard Python + PyTorch + Streamlit ignores
├── README.md                     # this file
├── requirements.txt
├── setup.py
├── bootstrap.py                  # scaffolding script (creates dirs/placeholders)
├── configs/
│   └── default.yaml              # all hyperparameters
├── data/
│   ├── raw/                      # CIC-IDS-2018/ and CTU-13/ placeholders — see below
│   ├── processed/                # WS1 output: windowed feature Parquet files
│   └── graphs/                   # WS2 output: cached PyG graph objects
├── src/
│   ├── __init__.py
│   ├── pipeline/                 # Stages 1-2: data ingestion & graph building
│   │   ├── __init__.py
│   │   ├── feature_fusion.py     # docstring-only method stubs
│   │   └── graph_constructor.py  # docstring-only method stubs
│   ├── core/                     # Stages 3-4: GNN encoder & RSSM world model
│   │   ├── __init__.py
│   │   ├── spatial_encoder.py    # interface for GAT/GraphSAGE
│   │   └── world_model.py        # interface for RSSM
│   ├── heads/                    # Stage 5: Prediction heads
│   │   ├── __init__.py
│   │   └── prediction_heads.py   # risk score + MITRE stage classifier interfaces
│   ├── simulator/                # Stage 6: Imagination rollout & counterfactuals
│   │   ├── __init__.py
│   │   └── rollout_engine.py     # K-step prior rollout interface
│   ├── explainability/           # Stage 7: Attention, SHAP, UMAP
│   │   ├── __init__.py
│   │   ├── attention.py
│   │   ├── shap_wrapper.py
│   │   └── trajectory_viz.py
│   ├── evaluation/                # Stage 8: benchmarking & baselines
│   │   ├── __init__.py
│   │   ├── baselines.py          # logistic regression / LSTM-only interfaces
│   │   └── benchmark_runner.py   # ablation table orchestration
│   └── utils/
│       ├── __init__.py
│       ├── config_loader.py      # loads default.yaml (fully implemented)
│       └── logger.py             # shared logging setup (fully implemented)
├── app/                           # Streamlit Demo Interface
│   ├── app.py                     # main entry point (skeleton)
│   ├── pages/
│   │   ├── 1_Upload.py
│   │   ├── 2_Risk_Timeline.py
│   │   ├── 3_Rollout.py
│   │   └── 4_Explain.py
│   └── utils/
│       ├── __init__.py
│       └── session_state.py      # placeholder for Streamlit caching
├── experiments/                   # logs, checkpoints, results (.gitkeep only)
└── tests/                         # unit test stubs
    ├── test_pipeline.py
    ├── test_core.py
    └── test_simulator.py
```

### About `data/raw/`

`data/raw/CIC-IDS-2018/` and `data/raw/CTU-13/` are placeholder
directories (each holding a `.gitkeep`) for the two datasets this
prototype targets:

- **CIC-IDS-2018** — Canadian Institute for Cybersecurity Intrusion
  Detection Evaluation Dataset. Download separately from the CIC website
  and place the extracted CSVs/PCAPs into `data/raw/CIC-IDS-2018/`.
- **CTU-13** — the CTU University botnet traffic capture dataset.
  Download separately and place the extracted NetFlow/PCAP files into
  `data/raw/CTU-13/`.

Neither dataset is bundled with this repository; both must be obtained
under their respective licenses/terms.

## Setup Instructions

```bash
# 1. Clone
git clone https://jayakumar-hacker_cyber_dream
cd cyber_dream

# 2. Create an environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the bootstrap script (creates the folder tree + placeholder files)
python bootstrap.py
# add --force to overwrite existing stub files
# add --dry-run to preview without writing anything

# 5. Install the package itself in editable mode
pip install -e .

# 6. Review & adjust configuration
$EDITOR configs/default.yaml

# 7. Place raw datasets
#    data/raw/CIC-IDS-2018/  <- CIC-IDS-2018 files
#    data/raw/CTU-13/        <- CTU-13 files

# 8. Launch the demo UI shell (skeleton only, until stages are implemented)
streamlit run app/app.py
```

## Team Responsibility Map (1‑Week Sprint)

| Folder | Owner | Sprint Focus |
|---|---|---|
| `src/pipeline/` (`feature_fusion.py`) | **WS1 — Data Engineer** | Implement ingestion, cleaning, normalization, windowing for CIC‑IDS‑2018 / CTU‑13 → `data/processed/`. |
| `src/pipeline/` (`graph_constructor.py`) | **WS2 — Data Engineer / Graph Specialist** | Implement node/edge extraction and PyG snapshot caching → `data/graphs/`. |
| `src/core/spatial_encoder.py` | **ML Engineer A** | Implement the GAT/GraphSAGE encoder per `configs/default.yaml -> spatial_encoder`. |
| `src/core/world_model.py` | **ML Engineer B (Research Lead)** | Implement the RSSM recurrent/stochastic state transition logic. |
| `src/heads/prediction_heads.py` | **ML Engineer A** | Implement `RiskScoreHead` and `MitreStageClassifierHead`. |
| `src/simulator/rollout_engine.py` | **ML Engineer B (Research Lead)** | Implement K‑step latent rollout and counterfactual intervention logic. |
| `src/explainability/` | **ML Engineer C / Security SME** | Implement attention extraction, SHAP wrapping, and UMAP trajectory projection; validate against SME intuition. |
| `src/evaluation/` | **ML Engineer C + Data Engineer** | Implement `LogisticRegressionBaseline`, `LstmOnlyBaseline`, and the ablation `BenchmarkRunner`. |
| `app/` | **Full‑Stack / Front‑End Engineer** | Wire the Streamlit pages to the real pipeline/model outputs. |
| `tests/` | **All engineers** (owner: **QA / ML Engineer C**) | Replace interface smoke tests with real unit + integration tests per stage. |
| `configs/`, `bootstrap.py`, `README.md` | **Tech Lead / Architect** | Own config schema and scaffolding tooling (this repo). |

## Explicit Non‑Goals of This Scaffold

This repository intentionally contains **no model implementation code**:
no `forward()` methods, no layer definitions, no training loops.
`src/pipeline/`, `src/core/`, `src/heads/`, `src/simulator/`, and
`src/explainability/` are docstring‑only interface stubs whose methods
raise `NotImplementedError`. Only `src/utils/` (config loading, logging)
and the Streamlit page skeletons under `app/` contain working code, since
neither is a model component. The goal of this scaffold is to lock in
the *architecture, interfaces, and configuration surface* so the team can
parallelize implementation immediately.
