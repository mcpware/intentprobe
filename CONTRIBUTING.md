# Contributing to IntentProbe

Contributions are welcome. Here is what helps most:

## Report missed detections

If IntentProbe misses a poisoned tool you found in the wild, open a [Missed detection](https://github.com/mcpware/IntentProbe/issues/new?template=missed-detection.yml) issue. Every missed sample directly improves the next probe version.

## Report false positives

If a benign tool gets warned or blocked, open a [False positive](https://github.com/mcpware/IntentProbe/issues/new?template=false-positive.yml) issue.

## Redact secrets

Do not paste live credentials, API keys, private URLs, customer names, or personal data into issues or pull requests. Replace real values with placeholders.

## Pull requests

Before submitting a PR:

1. Read the [CLA](CLA.md). By submitting, you agree to its terms.
2. Add `Signed-off-by: Your Name <email>` to your commit message.
3. Run the regression suites:

```bash
python -m research.activation_scanner_regression --no-build --pretty
python -m research.activation_scanner_cli_regression --pretty
python -m research.activation_scanner_hook_regression --pretty
```

## What is not accepted

- Dependencies that add network calls or telemetry.
- Changes that upload scan targets or results to external services.
- Probe weight changes without a reproducible training command and benchmark comparison.
