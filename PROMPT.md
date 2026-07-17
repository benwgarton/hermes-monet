# Set up this project for Monet on iPad

Copy and paste the prompt below into Hermes after Hermes has built or opened
the project you want to review.

```text
Set up the project in this workspace for design review in Monet on iPad.

I authorize you to add the public skill tap benwgarton/hermes-monet and install
or update benwgarton/hermes-monet/monet-project-setup. Use that installed skill
for the rest of this task. Do not install software from any other source. If
your runtime cannot load a newly installed skill until a new session starts,
finish the installation and give me the exact continuation prompt to paste
into the new session.

Inspect the actual repository and a reachable live or preview deployment. Find
DESIGN.md, design.md, or equivalent design guidance. Identify the framework,
hosting provider, repository and branch, routes, web fonts, delayed rendering,
protected pages, representative pages, and paths that should be captured or
excluded.

Choose conservative capture settings for this project. Add connector
requirements only when they provide useful source, capture, handoff, or
verification context. Include GitHub and Vercel when applicable, but request
the least privilege needed.

If the chosen deployment is reachable and its rendered pages are safe for me
to receive in chat, create an ordered Agent Preview Pack. Capture full-page PNG
screenshots after fonts and the page settle. Put home first, then primary
navigation and the high-value routes I should review. Exclude duplicate
templates, auth/account/admin routes, generated brochure fluff, and pages
outside the project scope. Preserve that exact order in preview.json. Do not
include raw HTML, browser storage, cookies, request headers, source maps, or
private customer data. If safe rendering is unavailable, create the
configuration-only package and say why.

Generate and verify a secret-free .monetproj Project Primer. Never put
passwords, tokens, API keys, cookies, private keys, authorization headers, or
secret-bearing URLs into the package, setup link, chat, or logs. Describe
required private values only as connector slots that Monet will ask me to
configure securely on the destination device.

Send the completed .monetproj as one document attachment so I can open it in
Monet on iPad; do not send its screenshots as separate chat photos. It is okay
if the chat client names it .monetproj.zip because current Monet accepts that
exact double suffix. Also provide an https://iammonet.com/setup link when the
validated configuration fits. Run the package verifier and report valid: true,
containsSecrets: false, the project slug, selected URLs in review order, Agent
Preview page count, capture profile, connector checklist, package path, and
setup link when available.

Recommend the iPad handoff first and explain exactly what to open in Monet and
which destination-side setup steps remain. Explain that imported screenshots
are ready for annotation but should be refreshed from the website before Reply
+ Verify. Do not install or open Monet Desktop unless I explicitly choose the
macOS or Windows alternative. There is no Linux desktop build.

Finish private connector setup inside Monet by default. Do not mention or start
private transfer during the normal handoff. Only if I explicitly ask to move
private values from this nearby computer may you offer the optional local
encrypted transfer. It requires canonical monet-pair, a separate approval, a
matching four-digit code on both devices, and my selection of every value.
```
