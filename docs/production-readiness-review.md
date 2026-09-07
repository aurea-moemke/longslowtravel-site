# Website production-readiness review

Reviewed: 7 September 2026. Scope: the local site release branch, relevant iOS
source, and official German/EU guidance. This is an implementation and legal-gap
review, **not a lawyer’s opinion or legal sign-off**. No lawyer has been
instructed, and nothing has been pushed, merged, or published.

## Decision

The requested product-copy corrections are implemented and regression-tested.
**Do not treat the website as legally cleared for public launch yet.** Resolve
the operator confirmations and qualified legal-review items below. Passing tests
does not establish legal compliance.

## Requested checks

| Check | Result on this branch |
| --- | --- |
| Public identity | Public product: LST Camino Planner. Installed iPhone app: LST Camino. Publisher: Long Slow Travel. Historical Camino Pilgrim references preserved. |
| Render | Privacy describes active API and Frankfurt PostgreSQL hosting in the present tense, matching recorded deployment history. Live configuration was not independently inspected. |
| Stage claims | Homepage now says “curated itinerary,” not “proven stage pattern.” |
| Offline behavior | Home/Support distinguish installed route content and schedules from separately downloaded basemap tiles. Support explains per-stage downloads, coverage limits, airplane mode with Wi-Fi off, and network-dependent features. |
| iPhone Settings | Location instructions use LST Camino, matching the configured installed name. Account deletion now includes Account → Settings → Delete Account. |
| Trail Mode | Support/Privacy describe location only while the app is open, without background tracking or emergency monitoring. |
| Safety | Planning-aid/not-emergency-or-navigation-service warning and 112 link preserved on Support, including translations. |
| Privacy/Imprint review | Source-based gap review completed below; external qualified legal review remains outstanding. |

Home/Support changes cover English, German, Spanish, French, Italian, and
Portuguese. Privacy remains English and Imprint German. Language notices now
describe availability, not legal approval; HTML attributes preserve the actual
language of each legal body.

Additional corrections: Privacy covers synced accommodation favourites and
language-preference local storage, identifies the controller with a link to the
existing postal address in Imprint, and links to BayLDA’s complaint service.
The contact callout still does not repeat the personal address. Broad
“No tracking” badges were removed; Mapbox telemetry remains disclosed.

## Resolve before legal approval

### Imprint: contact and business particulars

The existing provider identity, physical address, freelance status, registration
and VAT statements were not re-confirmed with the operator. Confirm that these
also describe the paid app business and whether a Wirtschafts-Identifikationsnummer
has been issued. Disclose applicable business identifiers, not a private tax
number. [DDG §5](https://www.gesetze-im-internet.de/ddg/__5.html)

Only email is currently offered. Have the reviewer approve an additional rapid,
direct contact channel. A telephone number is not the only possible solution;
an effectively operated enquiry form can qualify. Do not invent a phone number
or response-time promise. [CJEU C-298/07, paragraphs 25–40](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:62007CJ0298)

### Privacy: actual processing, retention, and transfers

The existing retention section uses broad criteria for support/security records
and says backups rotate without specifying when. The transfer paragraph lists
several possible safeguards without establishing which applies to each provider.
Obtain actual settings and agreements; replace generic statements with verified
periods or meaningful criteria and specific transfer information. Privacy notices
must clearly cover purposes, legal bases, recipients, retention, transfers, and
rights. [European Commission: GDPR principles and disclosure obligations](https://commission.europa.eu/law/law-topic/data-protection/information-business-and-organisations/principles-gdpr_en)

Prepare a private provider record for Render, Mapbox, Brevo, Proton, Apple and
GitHub: contracted entity, processor/independent-controller role, data categories,
locations/remote access, retention, agreement and applicable transfer basis.
Confirm processor agreements where required. Frankfurt database hosting alone
does not establish EU-only handling by every provider. No private dashboard,
agreement, retention schedule or transfer safeguard was verified in this review.
[European Commission: controller obligations](https://commission.europa.eu/law/law-topic/data-protection/information-business-and-organisations/obligations_en)

### Mapbox and local storage

Mapbox documents the telemetry opt-out provided through its attribution control.
That alone does not establish that the complete EU consent/legal-basis setup is
sufficient. Have the reviewer assess actual SDK events, defaults, purposes,
provider roles and any consent needed before optional processing. iOS location
permission and telemetry preferences are separate. Align the approved outcome
with app behavior and App Store privacy declarations.
[Mapbox SDK documentation](https://docs.mapbox.com/ios/maps/guides/)

The website’s local storage remembers a language explicitly selected by the
visitor. Confirm the necessary/requested-service exception for that purpose.
A cosmetic cookie banner would not solve app telemetry. Future analytics,
embeds or affiliate tracking require a fresh assessment.
[TDDDG §25](https://www.gesetze-im-internet.de/ttdsg/BJNR198210021.html)

### Understandable legal language

German visitors can select German marketing/support but still receive English
Privacy text. A notice is not a substitute for understandable information.
Have a qualified reviewer approve a German privacy version and decide which
other launch languages need reviewed versions. Do not describe machine
translations as legally approved. This is an audience-specific release-risk
assessment, not a claim that every site needs every EU language.
[European Commission: transparent privacy information](https://commission.europa.eu/law/law-topic/data-protection/information-business-and-organisations/principles-gdpr_en)

### Children and consent

The existing under-13 paragraph is not a complete Germany/EU age-policy analysis.
Confirm audience, registration/purchase rules, any relevant parental-consent
process and store age rating. For consent-based online services offered directly
to children, national thresholds range from 13 to 16. Do not blindly substitute
16 for 13 and assume all questions are resolved.
[European Commission: safeguards for children](https://commission.europa.eu/law/law-topic/data-protection/information-business-and-organisations/legal-grounds-processing-data/are-there-any-specific-safeguards-data-about-children_en)

### Consumer dispute information

Confirm employee count at the previous year-end and any duty or commitment to
participate in consumer dispute resolution. The ten-or-fewer-person exception
concerns §36(1)(1), not every dispute obligation. Do not invent a participation
or refusal statement. [VSBG §36](https://www.gesetze-im-internet.de/vsbg/__36.html)

There is no obsolete EU ODR-platform link in the current Imprint; do not add one.
Its governing regulation was repealed from 20 July 2025.
[Regulation (EU) 2024/3228](https://eur-lex.europa.eu/eli/reg/2024/3228/oj)

## Evidence and verification

- Reviewed all four HTML pages, script, styles, translations, site README, and
  canonical backend README-AI.
- iOS source: project configuration sets the installed name; SettingsView contains
  account deletion; LSTTrailModeView contains stage downloads and foreground
  location copy; TrailLocationMonitor requests when-in-use authorization and
  stops updates on dismissal; TrailOfflineMapStore implements bounded downloads.
  The Download/readiness labels were also checked against Localizable.xcstrings.
  This was not a new physical-device/background-behavior test.
- Website suite: `python3 -B -m unittest discover -s tests -v` — 18 tests passed.
  Checks cover translation catalogues, names, critical copy, safety, hosting,
  privacy disclosures, legal-content language, internal links/fragments, assets
  and screenshot references.
- **Visual/mobile browser verification remains outstanding.** The environment
  rejected a localhost server even after an approval attempt; the browser runtime
  also failed to start. No browser preview is claimed.
- No production deploy, signed-agreement review, App Store submission or complete
  accessibility/consumer-contract audit was done. Ask the legal reviewer to scope
  paid digital-content terms/withdrawal information and applicable accessibility
  obligations or exemptions for the actual business.

## Release sequence

1. Provide the confirmed operator/provider facts privately to a German/EU legal
   reviewer; obtain approval of Privacy and Imprint and required translations.
2. Implement any legal/app changes and update policy dates on publication.
   Re-run website tests.
3. Preview home, support, privacy and imprint at iPhone and desktop widths.
   Check all languages, expanded offline FAQ, keyboard navigation, email/112
   links and legal-language notices.
4. Verify the release app matches the promises; perform the documented offline
   preparation and airplane-mode test on a physical iPhone.
5. Push this release branch and open a GitHub PR. Merge when approved; confirm
   the configured GitHub Pages deployment from main and check public pages.
6. Add a real public App Store link only when it exists. The site intentionally
   has no fabricated download link. Website-only changes need no database
   migration, content bootstrap or Render deployment.
