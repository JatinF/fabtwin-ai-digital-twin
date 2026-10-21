# FabTwin benchmark report

This file records one workstation run of the in-process twin. Kafka, PostgreSQL, Grafana, a vision-language model, the NIST U-Net, a GPU, and the IntelliForge gateway were not executed.

| Item | Value | Class |
| --- | --- | --- |
| Deployment decision | NO-GO | GATE |
| Real equipment records | 0 | SPEC |
| Live equipment control | False | SPEC |
| Mode | simulation-only | SPEC |
| Machine | Windows-11-10.0.26200-SP0 | SPEC |
| Processor | Intel64 Family 6 Model 140 Stepping 1, GenuineIntel | SPEC |
| CPU count | 8 | SPEC |
| Python | 3.12.10 | SPEC |
| NumPy | 2.5.4 | SPEC |
| SciPy | 1.18.1 | SPEC |
| Nominal recommended flow | 0.549999 | MEASURED |
| Nominal steady temperature C | 70.000063 | MEASURED |
| Cooling-fault recommended flow | 0.999995 | MEASURED |
| Cooling-fault steady temperature C | 130.000563 | MEASURED |
| Cooling bound restores 70 C | False | MEASURED |
| Noise trials | 30 | MEASURED |
| Noise seed | 7 | SPEC |
| Normal-trace false positives | 0 | MEASURED |
| Qualification episodes | 4 | MEASURED |
| Qualification passes | 4 | MEASURED |
| Qualification pass rate | 1.0 | MEASURED |
| Gateway calls | 0 | MEASURED |
| Diagnose iterations | 40 | MEASURED |
| Diagnose P50 | 2.777 ms | MEASURED |
| Diagnose P95 | 5.296 ms | MEASURED |
| Tokens | 0 | MEASURED |
| Cost | no price applied | SPEC |
| README sha256 | d696d68841090b87b6e565c5f6415321ef9e45b0803360640e31cd30530d7b6f | MEASURED |
| Metrics zip sha256 | a2b89522c6d8d3fae6afefa97dd99932b564d6455beb96ae0c69083622cffa36 | MEASURED |
| Metrics zip bytes | 787689 | MEASURED |
| U-Net executed by FabTwin | False | GATE |

## Residual classes

Command flow 0.55. The twin uses the nominal EXAMPLE parameters. The plant uses the injected fault. Residual is observed minus predicted.

| Fault | Label | Final temperature residual C | Final pressure residual kPa | Temperature slope | Class |
| --- | --- | --- | --- | --- | --- |
| normal | normal | 0.0 | 0.0 | 0.0 | MEASURED |
| cooling_flow_low | cooling_flow_low | 148.158359 | 0.0 | 0.22659 | MEASURED |
| pressure_leak | pressure_leak | 0.0 | -5.333332 | 0.0 | MEASURED |
| sensor_drift | sensor_drift | 20.0 | 0.0 | 0.5 | MEASURED |

## NIST global Dice

These means are copied from `dice-coef-global.csv` inside the NIST archive. FabTwin did not run the U-Net.

| Path | Arithmetic mean | Standard deviation | Class |
| --- | --- | --- | --- |
| CsvCollection-UNet-SEM-sim-eval31-compare-output/evaluated_set6/dice-coef-global.csv | 0.7888469074374048 | 0.12499149367925828 | SPEC |
| CsvCollection-UNet-SEM-sim-eval51-compare-output/evaluated_set6/dice-coef-global.csv | 0.8466672651576093 | 0.14565108325109172 | SPEC |
| CsvCollection-UNet-SEM-sim-eval71-compare-output/evaluated_set6/dice-coef-global.csv | 0.8162391854030813 | 0.19252440423731895 | SPEC |

## Gates

| Gate | Status | Class |
| --- | --- | --- |
| kafka | not-run | GATE |
| postgres | not-run | GATE |
| grafana | not-run | GATE |
| live-equipment | not-run | GATE |
| vision-language-model | not-run | GATE |
| unet-inference | not-run | GATE |
| intelliforge-gateway-call | not-run | GATE |
| gpu | not-run | GATE |

Plant constants in `src/fabtwin/simulation/plant.py` are EXAMPLE values. The optimizer loss is the squared gap from 70 C plus `0.01 * flow^2`, bounded to the interval [0.2, 1.0], on the diagnosed fault's EXAMPLE parameters. Latency is `diagnose` on `SYN-EP-001`, including `solve_ivp`, image features, manual retrieval, and `minimize_scalar`. The percentile is nearest-rank. Tokens on this path are 0, so no token price is applied.
