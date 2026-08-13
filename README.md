# Long Slow Travel site

The static GitHub Pages site for **Long Slow Travel** and its first app,
**Camino Planner**.

## Pages

- `/` — branded Camino Planner landing page
- `/support/` — public support, troubleshooting, and account-deletion guidance
- `/privacy/` — privacy policy aligned with the app's current TestFlight privacy
  manifest and production behavior

The site is plain HTML, CSS, and JavaScript. It has no build step, external font
request, analytics script, or cookie dependency.

## Preview locally

From the repository root:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000/`.

## Publish with GitHub Pages

After merging to `main`, open the repository's **Settings → Pages** and choose:

- **Source:** Deploy from a branch
- **Branch:** `main`
- **Folder:** `/ (root)`

The expected public URLs are:

- Landing: `https://aurea-moemke.github.io/longslowtravel-site/`
- Support: `https://aurea-moemke.github.io/longslowtravel-site/support/`
- Privacy: `https://aurea-moemke.github.io/longslowtravel-site/privacy/`

Use the Support and Privacy URLs in App Store Connect unless a custom domain is
configured later.

## Before public release

- Have the privacy policy reviewed for the operator's applicable legal and
  infrastructure requirements.
- Re-audit the policy and App Store privacy answers when analytics, crash
  reporting, advertising, uploads, new SDKs, or server-side location features
  are added.
- Update route availability or App Store calls to action only after those
  products are publicly available.
