# Published recipe synchronization

GitHub-hosted downloads were tested on 15 October 2026. SiteGround returned
its CAPTCHA HTML rather than the public JSON catalogue. Site protection was
not changed. GitHub Actions therefore validates the exporter only; the hourly
synchronization must run from the existing authorized VPS.

## One-repository credential

On the VPS, create a dedicated SSH deploy key (never paste the private key):

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
ssh-keygen -t ed25519 -f ~/.ssh/openvist_recipe_library -C openvist-public-library -N ''
cat ~/.ssh/openvist_recipe_library.pub
```

If that filename exists, keep it and inspect its public key instead of replacing
it. Add the public key under this repository's **Settings → Deploy keys → Add
deploy key**, with **Allow write access**. It grants access to this repository
only. Do not reuse a personal token or the private VPS repository credential.

Establish GitHub's SSH host key with `ssh -T git@github.com`; compare the displayed
fingerprint to https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/githubs-ssh-key-fingerprints
before accepting it. Authentication can fail without the deploy key; that step
is for host identity verification. The sync worker subsequently requires the
verified known host entry and never accepts new host keys automatically.

## Install on the VPS

```bash
git clone --depth 1 https://github.com/Open-ViST/recipe-library.git ~/openvist/public-recipe-library
python3 ~/openvist/public-recipe-library/tools/sync_from_vps.py
```

If the checkout already exists, do not overwrite it: inspect local changes and
update it with a fast-forward pull. A successful worker prints either
`PUBLIC LIBRARY UP TO DATE` or `PUBLIC RECIPES SYNCHRONIZED`.

After the first successful run, create these user service files, adapting paths
if the VPS account differs from `johnny`:

`~/.config/systemd/user/openvist-recipes-github.service`:

```ini
[Unit]
Description=Sync published OpenViST Recipes to public GitHub library

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /home/johnny/openvist/public-recipe-library/tools/sync_from_vps.py
Environment=PYTHONUNBUFFERED=1
UMask=0077
TimeoutStartSec=600
```

`~/.config/systemd/user/openvist-recipes-github.timer`:

```ini
[Unit]
Description=Sync published OpenViST Recipes hourly

[Timer]
OnBootSec=5min
OnUnitInactiveSec=1h
Unit=openvist-recipes-github.service

[Install]
WantedBy=timers.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now openvist-recipes-github.timer
systemctl --user start openvist-recipes-github.service
journalctl --user -u openvist-recipes-github.service -n 20 --no-pager
```

## Guarantees and limits

Only the public OpenViST catalogue is imported: no drafts, API keys or private
infrastructure are read. No OpenAI calls are made and recipe code is never
executed. The worker executes the trusted exporter from this repository, whose
updates are controlled by repository maintainers. It preserves code hashes,
MIT licenses and upstream notices. Existing versions cannot silently change.
A changed version, unsupported license, empty catalogue, hash mismatch or file
conflict stops the run. Exporting is not independent validation of the recipes.

Public files remain in history if later removed from the site. Only public
catalogue metadata is used to rebuild the current index. There is no force
push. A dirty checkout or non-fast-forward update stops for inspection. If a
push fails after a local commit, the local commit remains for reconciliation;
there is no paid API retry. SiteGround access from the VPS must still be
verified during the first installation run. Repository rules can prohibit bot
pushes and must be addressed by the owner before unattended operation.

The timer is not installed by adding these files to GitHub. It becomes active
only when the VPS installation above is completed. Existing generation,
editorial review and WordPress draft delivery schedules are unaffected.
