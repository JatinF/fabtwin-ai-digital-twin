# Benchmark methodology

The committed numbers come from one workstation run of `python benchmarks/run_benchmark.py`. That script writes `benchmarks/results/benchmark_report.json` and `benchmarks/results/benchmark_report.md`. Pytest checks labels, ranges, archive hashes, and gates against a fresh in-process rerun. It does not require the latency sample to match across machines.

## Machine line

The report records `platform.platform()`, `platform.processor()`, `platform.machine()`, `os.cpu_count()`, and the Python, NumPy, and SciPy versions of the interpreter that ran the script. The hostname is not recorded.

## Physics

Each noiseless case calls `solve_ivp` twice at command flow 0.55: once with `NOMINAL` and once with `parameters_for(fault)`. The observation adds `drift_c_per_s * t` and, when a generator is passed, normal noise. Qualification episodes pass no generator. The residual is observed minus twin. The reported label is `classify_residual` of that pair.

The noise study draws 30 normal traces with `numpy.random.default_rng(7)`, temperature sigma 0.05 C, and pressure sigma 0.02 kPa. A false positive is a label other than `normal`. The report stores the count from that run.

## Optimizer

`minimize_scalar` uses method `bounded` and bounds `(0.2, 1.0)`. The loss is the squared gap from 70 C plus `0.01 * flow^2`. The flow and the steady temperature in the report are the values returned for the nominal map and for the `cooling_flow_low` map. `restores_target` is true when the steady temperature is within 1 C of 70. The cooling map is saturated at the upper bound, so that flag is false on this plant.

## Diagnostics and score

Image labels come from `classify_image(render(image_id))`. Retrieval rank is token overlap after the tenant filter. Qualification episodes are `SYN-EP-001` through `SYN-EP-004`. `score_episode` requires the injected fault, both evidence ids, `setpoint_applied` false, the sentence `The setpoint was not applied.`, status `COMPLETED`, `completion_claimed` true, `gateway.called` false, and `live_control` false. `SYN-EP-005` and `SYN-EP-B01` are outside that rate. The conflict episode is recorded separately.

## Latency

Forty calls of `diagnose` on `SYN-EP-001` with the engineer fixture. Each sample is the `latency_ms` field, which times the ODE pair, the image features, retrieval, the optimizer, and the audit append. The percentile is nearest-rank: sort ascending and take index `ceil(p/100 * n) - 1`. P50 and P95 are rounded to 6 decimal places by the renderer helper. This is an in-process figure.

## NIST archive

`archive_manifest` hashes `datasets/public_nist/README.txt` and `metrics_sets.zip` with SHA-256 and parses every `dice-coef-global.csv` in the zip. Those means are SPEC. `unet_executed_by_fabtwin` is false. The intensity zip and the model zip stay `not-downloaded`.

## What this run does not measure

Gateway call count on the default path is 0. Token count is 0. No USD price is applied. The gates `kafka`, `postgres`, `grafana`, `live-equipment`, `vision-language-model`, `unet-inference`, `intelliforge-gateway-call`, and `gpu` are `not-run`. Deployment decision is `NO-GO`.

Commands recorded with the run:

```bash
python -m pip install -e ".[dev]"
python benchmarks/run_benchmark.py
python -m pytest
```
