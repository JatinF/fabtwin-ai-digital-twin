# Data sources

## Synthetic equipment

`datasets/synthetic_equipment/episodes.json` and `documents.json` are EXAMPLE records. `real_equipment` is 0 and `live_control` is false. Identifiers start with `SYN-`. The `fault` field is the plant injection used by the simulator. The HTTP body does not accept it.

| Episode | Tenant | Injection | Image | Question focus |
| --- | --- | --- | --- | --- |
| `SYN-EP-001` | `tenant-a` | `cooling_flow_low` | `SYN-IMG-COOLING` | Abnormal chamber temperature |
| `SYN-EP-002` | `tenant-a` | `pressure_leak` | `SYN-IMG-PRESSURE` | Vacuum pressure drop |
| `SYN-EP-003` | `tenant-a` | `sensor_drift` | `SYN-IMG-DRIFT` | Readings climb while the twin stays flat |
| `SYN-EP-004` | `tenant-a` | `normal` | `SYN-IMG-NORMAL` | Operating window |
| `SYN-EP-005` | `tenant-a` | `cooling_flow_low` | `SYN-IMG-NORMAL` | Conflict between plant and image |
| `SYN-EP-B01` | `tenant-b` | `cooling_flow_low` | `SYN-IMG-COOLING` | Isolation |

`SYN-DOC-OTHER` belongs to `tenant-b` and mentions abnormal chamber temperature. Retrieval drops it before scoring a `tenant-a` question.

The inspection arrays are generated in `src/fabtwin/diagnostics/images.py`. They are not photographs and they are not a neural-net embedding.

## NIST SEM metrics

Citation: Bajcsy, Peter, Sathe, Pushkar, Vladar, Andras (2025), Detection Limits for SEM Image Segmentation, Version 1.0.0, National Institute of Standards and Technology, https://doi.org/10.18434/mds2-3838 (Accessed: 2026-10-21).

Bundled, unmodified:

| File | Role |
| --- | --- |
| `datasets/public_nist/README.txt` | NIST publication readme. SHA-256 is in the benchmark report |
| `datasets/public_nist/metrics_sets.zip` | CSV metrics, including `dice-coef-global.csv` |

Fetched on 2026-10-21 from the NIST OAR cache prefix `https://nist-oar-cache.s3.amazonaws.com/prd/fst4/mds2-3838/`. `intensity_sets.zip` and `AImodel_sets.zip` were not downloaded. The landing record is https://data.nist.gov/od/id/mds2-3838.

The readme states that the data are publicly available under the NIST copyright, fair use, and licensing statements: https://www.nist.gov/director/copyright-fair-use-and-licensing-statements-srd-data-and-software

The readme also states that the images were generated with ARTIMAGEN SEM simulation software. Those images are public research simulations. They are not live production-fab data. FabTwin's fault label does not read them. The global Dice arithmetic means are copied into the report with evidence class SPEC, and `unet_executed_by_fabtwin` is false.

`datasets/public_nist/NOTICE.md` is this repository's attribution note.

## NIST digital-twin program

The manufacturing program page describes digital twins as synchronized virtual models that help manufacturers represent, diagnose, predict, and optimize their operations: https://www.nist.gov/programs-projects/digital-twins-advanced-manufacturing (accessed 2026-10-21).

That page is a SPEC reference for the monitoring, diagnosis, prediction, and optimization vocabulary. FabTwin is a separate simulation-only codebase. It does not implement the NIST Digital Twin Testbed, ISO 23247, or MTConnect.
