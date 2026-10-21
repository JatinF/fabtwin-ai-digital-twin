# Threat model

This is a local reference. The trust boundary is the process that holds the fixture tokens and the in-memory store.

| Boundary | Control in this repository |
| --- | --- |
| Live equipment | `live_control` is false on health, diagnosis, and decision records. The API has no tool driver |
| Tenant | Episode lookup, manual retrieval, approval lookup, and audit reads filter on the token's tenant. A miss is 404 |
| Role | Diagnose allows reader, engineer, and approver. Parameter changes allow engineer. Decisions allow a different approver |
| Approval | Expiry is 3600 seconds. Reject and expiry leave the command in place. Approve recomputes the flow and refuses a mismatch as `UNVERIFIED` |
| Rollback | The previous simulated fraction is stored on apply and written back only after a second approval |
| Client body | Episode and decision models set `extra=forbid`. The client cannot submit `expected_fault` |
| Model gateway | An empty base URL does not open a socket. A set URL posts the chat-completions body and does not treat the response as the fault label |
| Secrets | Tokens `dev-reader-a`, `dev-engineer-a`, `dev-approver-a`, and `dev-engineer-b` are fixtures. The compose password `local-demo-only` is a fixture |
| Public imagery | The bundled NIST files are research artifacts. They are not production-fab telemetry |
| Cloud sketch | `infrastructure/terraform` pins account `000000000000` and declares no applied resources |

A failed policy check, a rejected or expired approval, an unverified reread, or disagreed evidence leaves `setpoint_applied` false. The answer then contains `The setpoint was not applied.`

The benchmark did not start Kafka, PostgreSQL, Grafana, or a remote model. Those slots are untested as deployed systems. Decision: **NO-GO**.
