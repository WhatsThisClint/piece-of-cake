# Publishing To PyPI

Piece of Cake uses PyPI Trusted Publishing through GitHub Actions. This avoids
storing a PyPI password or long-lived API token in GitHub.

Current package:

- PyPI: https://pypi.org/project/piece-of-cake-terrain/
- GitHub release: https://github.com/WhatsThisClint/piece-of-cake/releases/tag/v0.1.2

## Trusted Publisher

The PyPI trusted publisher is configured with:

- Project name: `piece-of-cake-terrain`
- Owner: `WhatsThisClint`
- Repository name: `piece-of-cake`
- Workflow name: `publish.yml`
- Environment name: `pypi`

## Publish

Run the GitHub workflow for the version tag:

```bash
gh workflow run publish.yml --repo WhatsThisClint/piece-of-cake --ref main -f ref=v0.1.2
```

For future versions:

1. Update the version in `pyproject.toml` and `src/piece_of_cake/__init__.py`.
2. Add a changelog entry.
3. Commit and tag the version, for example `v0.1.2`.
4. Create a GitHub Release.
5. Run the publish workflow, or let it run from the published release event.

The workflow builds the wheel/source distribution, checks package metadata with
Twine, then publishes to PyPI through OIDC.
