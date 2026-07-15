# Security

The Monet Project Primer is configuration-only. It must never contain API
keys, passwords, cookies, authorization headers, private keys, or executable
setup hooks. The included builder and verifier reject credential-looking
material and unsafe package members before handoff.

Private pairing is optional and local to a user-approved macOS or Windows
session. See
[`skills/monet-project-setup/references/security.md`](skills/monet-project-setup/references/security.md)
and
[`skills/monet-project-setup/references/pairing.md`](skills/monet-project-setup/references/pairing.md)
for the protocol boundaries.

Please report vulnerabilities privately to `support@iammonet.com`. Do not open
a public issue containing credentials, private project data, or exploit details.
