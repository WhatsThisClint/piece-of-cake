# Publishing To PyPI

Piece of Cake uses PyPI Trusted Publishing through GitHub Actions. This avoids
storing a PyPI password or long-lived API token in GitHub.

## One-Time PyPI Setup

On PyPI, add a pending publisher from the `PyPiClint` account:

- PyPI project name: `piece-of-cake`
- Owner: `WhatsThisClint`
- Repository name: `piece-of-cake`
- Workflow name: `publish.yml`
- Environment name: `pypi`

PyPI will create the project the first time this publisher successfully uploads
a release. Until that first upload happens, the pending publisher does not
reserve the package name.

## Publish

After the pending publisher exists, run the GitHub workflow:

```bash
gh workflow run publish.yml --repo WhatsThisClint/piece-of-cake --ref main -f ref=v0.1.0
```

For future versions:

1. Update the version in `pyproject.toml` and `src/piece_of_cake/__init__.py`.
2. Add a changelog entry.
3. Commit and tag the version, for example `v0.1.1`.
4. Create a GitHub Release.
5. Run the publish workflow, or let it run from the published release event.

The workflow builds the wheel/source distribution, checks package metadata with
Twine, then publishes to PyPI through OIDC.
