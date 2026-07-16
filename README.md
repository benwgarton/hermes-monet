# Monet skills for Hermes

This directory is ready to publish as a Hermes skill tap. The public repository
layout is:

```text
skills/
  monet-project-setup/
    SKILL.md
    references/
    scripts/
    templates/
```

Once this directory lives at the root of the public `benwgarton/hermes-monet`
GitHub repository, users install it with:

```bash
hermes skills tap add benwgarton/hermes-monet
hermes skills install benwgarton/hermes-monet/monet-project-setup
```

Users can inspect and audit the community package before enabling it:

```bash
hermes skills inspect benwgarton/hermes-monet/monet-project-setup
hermes skills audit
```

Updates are discovered with `hermes skills check` and installed with `hermes
skills update`. Hermes applies its community-skill security scan during install
and update.

## One-prompt setup

After Hermes has built or opened a project, paste the bootstrap prompt in
[PROMPT.md](PROMPT.md). The prompt explicitly authorizes only this public tap,
installs or updates the skill, inspects the current project, creates and
verifies a secret-free `.monetproj`, and leads with the iPad handoff.

Private pairing remains a separate, explicit approval after the safe package
has been generated. It is never started by the bootstrap prompt.

Version 0.2.1 adds stricter URL, path, and resource-key validation to the
Project Primer runtime. Version 0.2 added the optional local `monet-pair`
workflow. Pairing requires the
canonical command installed by Monet Desktop; the skill never carries or
reimplements credential transfer itself.

## Nous listing path

Monet is a specialized third-party product integration. Nous's current
contribution policy directs this class of skill to a standalone public tap
rather than `skills/` or `optional-skills/` in the Hermes core repository.
After publishing:

1. Verify installation from a clean Hermes profile.
2. Share the tap in the Nous Research Discord `#plugins-skills-and-skins`
   channel for community discovery.
3. Ask Nous to add the repository to Hermes's trusted repositories only after
   the public package has stable releases and a demonstrated maintenance path.

The Monet MCP catalog submission is separate. Do not submit it until the public
desktop installer exposes a stable cross-platform `monet-mcp` launcher and the
source/install ref can be pinned in `optional-mcps/monet/manifest.yaml`.
