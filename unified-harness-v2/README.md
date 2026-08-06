# DIAZAI Unified Harness v2.0.0

This integration extends the existing enterprise DIAZAI scaffold with the production-oriented dual-runtime harness built from the Synaptic PC Harness feature set.

## Unified architecture

- **Python substrate:** FastAPI REST/OpenAPI, stateless HTTP MCP, stdio MCP, WebSocket events, workflows, sessions, approvals, policies, plugins, AI providers, virtualization, knowledge workspaces, API synapses, governed remote agents, PARAVOX, DR TENSOR, OPUS databases, y/s/n masks, and CINDERS receipts.
- **Node.js control plane:** Python supervision, same-origin HTTP and WebSocket gateway, Node-native MCP, DR TENSOR parity tools, explicit-seed API discovery, point-and-connect bindings, ESM plugins, independent audit ledger, SDK, CLI, and governed remote agent.
- **Unified HTML:** a dependency-free operator console covering health, DR TENSOR, both MCP surfaces, synapses, bindings, models, knowledge, remote control, plugins, audit, events, and the embedded PARAVOX cockpit.

## Validated release

The complete source-and-release ZIP contains 163 files and has SHA-256:

`cf34e6197ade6b4572991d592395bcd89d9dc8f42ecea623a6bca9992b2ca181`

Validation completed before publication:

- Python tests: 17/17
- DR TENSOR and source checks: 14/14
- Node tests: 11/11
- Node self-tests: 5/5
- End-to-end dual-runtime integration checks: 11/11
- ZIP integrity and required-artifact verification: passed

## Runtime surfaces

- Unified console: `http://127.0.0.1:8790/`
- PARAVOX: `http://127.0.0.1:8790/paravox`
- Python MCP: `http://127.0.0.1:8790/mcp`
- Node MCP: `http://127.0.0.1:8790/mcp-node`
- OpenAPI UI: `http://127.0.0.1:8790/docs`

## Security boundary

Authentication is enabled by default. Python remains loopback-bound behind Node. Remote execution is disabled by default and uses exact command bindings, HMAC envelopes, nonces, expiry checks, bounded output, `shell:false`, and optional single-use approvals. Endpoint discovery is restricted to explicit seeds and configured outbound host allowlists; it is not a subnet scanner.

This branch is a review/staging integration. The downloadable ZIP is the canonical complete repository snapshot for v2.0.0; this directory surfaces the publication scaffold and core Node/HTML integration for review before merge.