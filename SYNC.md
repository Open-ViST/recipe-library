# Published recipe synchronization

GitHub Actions checks the public OpenViST catalogue hourly, at minute 17 UTC.
GitHub can delay scheduled runs. The Actions page also offers **Run workflow**.

Only recipes already published at https://openvist.com/recipes/ are imported.
Drafts, VPS queues, API keys and private infrastructure are never read. No OpenAI
or WordPress credentials are needed. The workflow uses GitHub's temporary token
to commit to this repository only; it never executes recipe code.

Code hashes and MIT notices are checked before writing. Existing published
versions cannot be silently replaced. A changed version, unsupported license,
empty catalogue, hash mismatch or conflicting file stops the run for review.
Published files are retained even if a recipe later disappears from the site;
removal from a public Git history requires a separate decision.

Failures appear in GitHub Actions. A concurrent manual commit can reject the
push safely; the next scheduled run starts from the new head. There is no force
push or automatic retry with weakened checks. This sync does not publish posts
on OpenViST and does not change the VPS generation or review schedule.

If Actions is disabled, enable it in this repository's Actions tab. Repository
rules that prohibit bot pushes to main must be resolved by the owner before
automatic commits can succeed. Forks do not run the synchronization job.
