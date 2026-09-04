# Long Slow Travel site

The static GitHub Pages site for publisher and product-family brand
**Long Slow Travel** and its first app, **LST Camino Planner**. The installed
iOS home-screen name is **LST Camino**.

AI-assisted work must begin with the canonical cross-repository
[README-AI.md](https://github.com/aurea-moemke/longslowtravel-backend/blob/main/README-AI.md)
in the backend repository.

## Pages

- `/` — branded LST Camino Planner landing page
- `/support/` — public support, troubleshooting, and account-deletion guidance
- `/privacy/` — privacy policy aligned with the app's current TestFlight privacy
  manifest and production behavior
- `/imprint/` — German provider identification for the independent operator

The site is plain HTML, CSS, and JavaScript. It has no build step, external font
request, analytics script, or cookie dependency.

## Preview locally

From the repository root:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000/`.

## Tests

Run the public-identity regression checks from the repository root:

```bash
python3 -m unittest discover -s tests -v
```

## Publish with GitHub Pages

After merging to `main`, open the repository's **Settings → Pages** and choose:

- **Source:** Deploy from a branch
- **Branch:** `main`
- **Folder:** `/ (root)`

The production URLs are:

- Landing: `https://longslowtravel.com/`
- Support: `https://longslowtravel.com/support/`
- Privacy: `https://longslowtravel.com/privacy/`
- Imprint: `https://longslowtravel.com/imprint/`

Use these Support and Privacy URLs in App Store Connect.

## Custom domain

The root-level `CNAME` file declares `longslowtravel.com` as the GitHub Pages
domain. In **Settings → Pages**, set **Custom domain** to
`longslowtravel.com`. At the DNS provider, use these website records:

| Type | Host | Value |
| --- | --- | --- |
| A | `@` | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |
| CNAME | `www` | `aurea-moemke.github.io` |

Do not add the repository name to the `www` CNAME target. After GitHub finishes
issuing the certificate, enable **Enforce HTTPS** in the Pages settings.

These website records can coexist with the `api` CNAME, Proton MX records, and
Proton/Brevo verification or authentication TXT/CNAME records. Do not replace
those email or API records during the website cutover.

## Before public release

- Have the privacy policy reviewed for the operator's applicable legal and
  infrastructure requirements.
- Re-audit the policy and App Store privacy answers when analytics, crash
  reporting, advertising, uploads, new SDKs, or server-side location features
  are added.
- Update route availability or App Store calls to action only after those
  products are publicly available.
