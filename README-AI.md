# Long Slow Travel — AI Project Onboarding and Product Specification

> Canonical onboarding document for a new ChatGPT/Codex conversation.
>
> Last reconciled with the local repositories: **2026-09-02**.
>
> This file intentionally contains no passwords, tokens, SMTP credentials,
> database URLs containing credentials, tax identifiers, signing material, or
> private App Store values. Never add any of those here.

## 1. How a new chat must use this file

Read this entire file before changing the Long Slow Travel project. Then:

1. Inspect the Git status, current branch, recent history, and relevant source
   files in **all repositories affected by the request**. The branch snapshot in
   this document is historical context, not permission to assume the worktrees
   have not changed.
2. State which repository or repositories are in scope and what you believe the
   requested outcome is.
3. Preserve uncommitted user work. Never discard, reset, overwrite, or silently
   incorporate unrelated changes.
4. Work on a branch named `feature/...`, `fix/...`, `release/...`, or another
   conventional prefix appropriate to the task. The owner explicitly prefers
   these names over `codex/...`.
5. Diagnose before changing behavior. Prefer the smallest change that preserves
   the invariants in this document.
6. Add or update regression tests whenever behavior, persistence, sync, content,
   purchases, authentication, maps, localization, or calculations change.
7. Run proportionate tests and report exactly what ran. Do not describe a test
   as passed merely because an unrelated suite passed.
8. Do not deploy, merge, push, edit production data, or contact external parties
   unless the user asked for that action. Give commands when the user wants to
   perform the GitHub merge herself.
9. Update this file whenever a durable decision, invariant, workflow,
   architecture rule, production dependency, route product, known baseline, or
   active handoff state changes. Updating only a component repository's
   `README.md` is not sufficient; update this cross-repository handoff too.
10. Keep the current branch, uncommitted scope, completed validation, and
    remaining validation accurate during multi-step work so another chat can
    safely continue at any point, not only after a commit or release.

If this file conflicts with the current explicit user request, the current user
request wins. If it conflicts with current code or tests, investigate instead of
silently choosing one. Correct this file once the source of truth is established.

## 2. Project identity and repositories

Long Slow Travel is an offline-first travel-planning product family. The first
edition is the Camino de Santiago app. Future editions may cover hiking,
bikepacking, or overlanding, so Camino-specific behavior must remain behind the
active app/content configuration rather than becoming an assumption of every
future Long Slow Travel app.

Local project layout on the owner's Mac:

| Component | Local path | GitHub repository | Purpose |
| --- | --- | --- | --- |
| iOS app | `/Users/aureamoemke/Projects/LongSlowTravelProject/longslowtravel-ios/LongSlowTravel` | `aurea-moemke/longslowtravel-ios` | SwiftUI client, offline database, maps, purchases, and schedule sync |
| Backend | `/Users/aureamoemke/Projects/LongSlowTravelProject/longslowtravel_backend_starter` | `aurea-moemke/longslowtravel-backend` | Django API, PostgreSQL canonical data, authentication, content publishing, purchase verification, and sync |
| Public site | `/Users/aureamoemke/Projects/LongSlowTravelProject/longslowtravel-site` | `aurea-moemke/longslowtravel-site` | Static landing, Support, Privacy, and Imprint pages on GitHub Pages |

The repositories are separate; there is no monorepo transaction. A feature may
require coordinated backend and iOS branches and separate pull requests. Never
assume that a local `main`, GitHub `main`, Render deployment, checked-in content
snapshot, local PostgreSQL database, installed iOS SQLite database, or TestFlight
build contains the same version. Verify each boundary explicitly.

### Repository state at the last reconciliation

- Site: `main` at commit `df6432a`; `README-AI.md` is currently an untracked
  handoff document and must be intentionally added to the site repository when
  the owner is ready to publish it.
- iOS: active branch `feature/declutter-itinerary-tabs`, based at commit
  `59e5117` (`Fix reversed Finisterre template schedules`), with uncommitted
  itinerary UI, accommodation presentation, localization, map/elevation, cache,
  tests, and `README.md` changes. Do not discard or split these changes without
  reviewing the complete diff. `tools/testflight_preflight.sh` is intentionally
  unchanged and must remain preserved.
- Backend: active branch `feature/accommodation-opening-information`, based at
  commit `9ffaceb`, with uncommitted accommodation import/model/admin/serializer,
  snapshot/export, test, and migration `0053_accommodation_open_all_year.py`
  changes.
- The owner last confirmed that Render was live and iOS build 15 was uploaded
  to TestFlight Internal Testing. Later local/merged commits may not be in that
  build or deployment; verify the exact production and TestFlight SHAs before
  calling current branch behavior shipped.

Do not keep this snapshot stale: update or remove it after the corresponding
branches are merged or abandoned.

## 3. Product principles and non-negotiable invariants

### 3.1 Offline first

- Platform content and user schedules live in the iOS GRDB/SQLite database.
- App screens read local data. The network refreshes local data; it must not be
  a prerequisite for opening already-installed routes or schedules.
- A server outage must not erase the signed-in presentation or make cached
  schedules, routes, places, accommodations, geometry, or entitlements appear
  lost.
- Previously installed paid content remains usable offline even if account or
  catalog refresh fails. A fresh purchase, restore, or download still requires
  the applicable Long Slow Travel account, Apple service, and backend.
- Never replace valid local content with an empty or failed response.

### 3.2 Backend-owned, data-driven content

- Journeys, routes, variants, places, accommodations, services, itinerary
  templates, template days, ordering, access metadata, and geometry are data.
  Do not hardcode route content in Swift.
- Django/PostgreSQL and reviewed checked-in bundle snapshots are the canonical
  publishing system. The iOS database is a cache plus the local source of
  unsynced user edits.
- Legacy Camino SQLite data is provenance/import history only. It must never be
  blindly re-imported over the evolved canonical database.
- UUIDs of released records are stable public identities. Never regenerate or
  swap them casually.

### 3.3 Guest use is a first-class mode

- A traveler may use the free Sarria-to-Santiago route and create schedules
  without an account.
- An account is required for paid-route purchase/restore and multi-device
  schedule sync.
- After registration or sign-in, if guest schedules exist, ask whether to add
  and sync them to the authenticated account. If the traveler declines, delete
  those guest schedules so mixed ownership is not confusing.
- Guest schedules for paid content may only be adopted when that authenticated
  account has access to the route.

### 3.4 Purchases are permanent route-pack access

- iOS route products are non-consumable, one-time purchases.
- Apple processes payment; the backend verifies Apple's signed transaction and
  grants a server-side entitlement.
- Purchase and restore require sign-in. StoreKit receives the authenticated
  user's stable `app_account_token`.
- A transaction/original transaction and its app-account token cannot silently
  migrate between Long Slow Travel accounts or unrelated routes. A 403
  `app_account_mismatch` and a 409 `transaction_already_linked` are deliberate
  safety checks. Do not weaken them as a quick fix; first determine which Apple
  Account, sandbox history, Long Slow Travel account, and entitlement own the
  transaction.
- The same sandbox Apple Account can naturally surface the same non-consumable
  history after reinstall. Clearing the app or creating another Long Slow
  Travel login does not create a new Apple purchase identity.

### 3.5 Foreground location only

- Trail Mode tracks location only while the app is open. There is no background
  trail recording requirement.
- The actual GPS position remains visible even when the user is far from the
  route. Never substitute a default Cupertino marker as if it were current
  device location.
- Current live location is not sent to the Long Slow Travel backend.

### 3.6 Performance is product behavior

- Opening an elevation profile or map must not block navigation or freeze the
  app.
- iOS builds 13 and 15 were reported as responsive references for itinerary and
  schedule elevation handling. Several intervening attempts to unify or
  recompute schedule elevation caused long hangs; compare representative routes
  against these builds when changing the pipeline.
- Do not rewrite elevation loading, add broad concurrency, refetch geometry, or
  recompute full routes on the main actor without profiling the baseline first.
  Make a surgical change, retain cached geometry behavior, and test both a long
  Camino Francés template and a schedule on a real device.
- The active iOS branch introduces bounded in-memory route preparation caches:
  decoded main geometry, elevation samples, and all active variants are warmed
  once per selected route; template and schedule consumers join the same
  in-flight preparation. Composed route paths and completed template/schedule
  presentations are cached separately. All caches are process-local, bounded,
  and invalidated after installed-content changes.
- Primary itinerary/schedule content must remain interactive while elevation
  enrichment runs. Publish a usable base profile first, then add variant
  overlays and derived summaries without replacing or hiding the base result.

### 3.7 Privacy, legal text, and secrets

- Do not introduce analytics, advertising, cross-app tracking, or server-side
  live-location collection without an explicit product decision and a privacy,
  App Store disclosure, and legal review.
- Never commit credentials, database passwords, signing keys, SMTP keys,
  private certificates, `.env` files, or personal tax identifiers.
- Public legal pages reflect a Germany-based independent operator serving users
  who may be in the EU. They are implementation-aligned disclosure text, not a
  substitute for legal advice. Re-review them whenever data flows or vendors
  change.
- Apply data minimization, purpose limitation, access control, deletion, backup
  retention, processor/DPA, breach-response, and data-subject-request procedures
  to production operations. Privacy requests go through the public support
  address and must be authenticated before account data is disclosed.

## 4. System architecture

```text
Reviewed CSV/GPX/OSM-derived sources
               |
               v
Django import/validation -> PostgreSQL canonical content
               |                    |
               |                    +-> Django admin/operations
               v
checked-in JSON snapshots -> content catalog + bundle/geometry APIs
                                      |
                                      v
                             iOS GRDB/SQLite cache
                                      |
                    +-----------------+-----------------+
                    |                                   |
             offline UI/maps                    local schedule edits
                                                        |
                                                        v
                                              revision-based sync API
```

### iOS technology and configuration

- SwiftUI app with GRDB 7.x, Mapbox Maps 11.x, Mapbox Common/Core Maps, Turf,
  Core Location, and StoreKit 2.
- Xcode project remains `LongSlowTravel.xcodeproj`; the Camino app target,
  unit-test target, UI-test target, and shared scheme are `LSTCamino`,
  `LSTCaminoTests`, `LSTCaminoUITests`, and `LSTCamino`.
- Product bundle identifier: `com.longslowtravel.ios.camino`.
- Home-screen display name: `LSTCamino` in the current project settings. Confirm
  the desired spaced marketing name before changing it; the project name itself
  should remain LongSlowTravel to support future editions.
- Minimum deployment target: iOS 17.0, intentionally supporting devices such as
  iPhone 11 that can run iOS 17.
- Current active config is
  `LongSlowTravel/AppVariants/Camino/ActiveAppConfig.swift`; the default offline
  bundle/route is `camino-frances-last-100km`, and the database file is
  `longslowtravel-camino.sqlite`.
- Debug scheme: `LSTCamino`; it may override `LST_API_BASE_URL` with the Mac's
  LAN API URL. Release/TestFlight scheme: `LSTCamino Production`; Release uses
  `https://api.longslowtravel.com/api/` and rejects non-HTTPS API URLs.
- Public Mapbox tokens are app configuration, but secret Mapbox download tokens
  or other private credentials must never be documented or committed.

### Backend technology and configuration

- Django 5.x, Django REST Framework, SimpleJWT, PostgreSQL, psycopg, Gunicorn,
  WhiteNoise, SRTM processing, and Apple's App Store Server library.
- Render production runtime uses Python 3.12.13 and PostgreSQL 17. Local Python
  may differ, but production compatibility must be tested against Python 3.12.
- API health endpoint: `https://api.longslowtravel.com/health/`.
- Admin endpoint: `/admin/`; staff access is a Django user, not a PostgreSQL
  username/password.
- Production runs migrations in Render's pre-deploy command and starts Gunicorn;
  never use Django's development `runserver` in production.

### Website technology and configuration

- Plain HTML, CSS, and small JavaScript; no build step, external font request,
  analytics script, or cookie dependency.
- GitHub Pages publishes `main` from the repository root.
- Canonical domain: `https://longslowtravel.com`; `www` points to the GitHub
  Pages host and HTTPS must be enforced.
- Public pages: `/`, `/support/`, `/privacy/`, `/imprint/`.
- The landing-page product screenshot is
  `assets/camino-planner-journeys.png`. It must be an actual current app screen,
  not a fabricated UI that differs from the shipping Journeys screen.

## 5. Domain model and ownership boundaries

### Platform content

- `Journey`: a travel family shown at the top level, currently Camino walking
  and cycling journeys.
- `Route`: one complete route belonging to a journey. A derived free sample is
  a distinct route with its own UUID, not a partial view using the paid route's
  identity.
- `RouteVariant`: an alternate path or transport choice. It has ordered geometry
  and may replace a portion of the main route.
- `Place`: an ordered place on one or more routes, with type, country,
  coordinates, elevation, descriptions, services, and provenance.
- `Accommodation`: a place-linked stay with tri-state facilities, contacts,
  direct booking links, and review/provenance metadata.
- `ItineraryTemplate` and `ItineraryTemplateDay`: backend-provided suggested
  stages. Templates have explicit sort order; days have stable UUIDs, contiguous
  numbering, optional default variants, and start/end place identities.
- `ContentBundle`: a published offline route pack with dataset/schema versions,
  access policy, product metadata, ordering, and optional purchase-family
  parent.

### User data

- `UserItinerary`: a personal schedule, optionally created from a template,
  with name/start date/route and sync metadata.
- `UserItineraryDay`: an editable day with date, endpoints, rest-day state,
  distance, elevation, notes, selected route variants, deletion state, and
  revision metadata.
- Server records belong to an authenticated user. Local records also carry an
  owner identifier or explicit guest ownership.
- User records are never included in platform-content snapshots or overwritten
  by a content bootstrap.

### Unknown is not false

Accommodation facilities and service facts are tri-state: confirmed available,
confirmed unavailable, or unknown. Missing source data must remain unknown; it
must not become a negative claim. UI legends should explain the states without
cluttering every row.

## 6. Current route-pack and purchase specification

The route catalog must list all published routes, including locked routes. A
lock opens the relevant Content entry; purchase controls live in Content rather
than being duplicated unpredictably throughout route navigation.

| Parent pack | Bundle/product | Access granted |
| --- | --- | --- |
| Free sample | `camino-frances-last-100km`; no product | Camino Francés — Sarria to Santiago, approximately 115 km, permanently available without purchase |
| Camino Francés | `com.longslowtravel.camino.frances` | Full walking route plus `camino-frances-bike` |
| Camino Finisterre | `com.longslowtravel.camino.finisterre` | Walking route plus `camino-finisterre-bike` |
| Camino Português | `com.longslowtravel.camino.portugues` on parent bundle `camino-portugues-central` | Central walking, Coastal walking, Central bike, and Coastal bike bundles |

There must be no separate active Central or Coastal Portuguese product IDs.
Included bundles have an empty product ID and point directly to the paid parent
using `included_with_bundle`. Old Central/Coastal product references and legacy
entitlements were intentionally discarded while the app was still in testing.

### Catalog order

Walking:

1. Camino Francés — Sarria to Santiago (free)
2. Camino Francés
3. Camino Finisterre
4. Camino Português Central, presented under the Camino Português family
5. Camino Português Coastal, presented under the same family

Cycling:

1. Camino Francés by Bike
2. Camino Finisterre by Bike
3. Camino Português Central by Bike
4. Camino Português Coastal by Bike

Ordering is data (`ContentBundle.sort_order` and itinerary-template
`sort_order`), not a display-name switch in Swift. The iOS catalog merges
installed data with catalog projections so uninstalled/locked routes remain
discoverable.

### Route-card presentation

- Camino route cards use the Camino shell, including cycling routes; walking vs
  cycling is shown by the travel-mode chip.
- Status icons use a consistent size and alignment: gift for free/included,
  lock for locked, green seal/check for purchased. Do not add redundant `Free`,
  `Owned`, or duplicate lock/download words beside an already clear icon.
- Round displayed route totals to whole kilometres on route cards.
- Long route names wrap so Central and Coastal remain distinguishable.
- The Camino Português family card shows Central and Coastal choices. The child
  page explains that walking routes are part of the Camino Português route pack
  and bike routes are included with that pack.

## 7. Itinerary-template catalog

The backend branch `feature/itinerary-template-catalog` defines this desired
catalog and ordering. Verify that it is merged, deployed, bootstrapped, and
downloaded before treating it as production content.

### Camino Francés

1. Cam Frances Pinay Pilgrim — 31 days
2. Cam Frances Classic — 31 days
3. Cam Frances Medium — 32 days
4. Cam Frances Slow — 34 days
5. Cam Frances Relaxed with 6 rest days — 40 days

The Relaxed template has rest days on day 1 at Saint-Jean-Pied-de-Port, day 5
Pamplona, day 15 Burgos, day 24 León, day 34 Sarria, and day 40 Santiago de
Compostela. Each rest day has the same start/end place, zero distance, and must
survive schedule creation even at the first or last day. Days are continuous
1...40. Default variant days are preserved where the reviewed route requires
them.

### Camino Finisterre

1. Cam Fisterra Classic — 3 days, direct Olveiroa-to-Fisterra route
2. Cam Fisterra via Muxia ending at Fisterra — 4 days
3. Cam Fisterra ending at Muxia — 4 days, Fisterra before Muxia

The names describe route order and are not interchangeable. Finisterre template
geometry must follow the reviewed direct/alternate route rather than drawing a
straight line or routing through the wrong destination.

### Camino Português Central

1. Central from Lisbon — 24 days
2. Central from Porto no variants — 10 days
3. Central from Porto via Spiritual — 11 days
4. Central from Tui — 5 days

### Camino Português Coastal

1. Coastal from Porto no variants — 12 days
2. Coastal from Porto via Senda Litoral — 14 days
3. Coastal from Porto via Spiritual — 13 days
4. Coastal from Porto via Senda Litoral and Spiritual — 15 days

The old standalone three-day Spiritual sample templates are not published.
Variant-enabled templates explicitly constrain which reviewed variants may be
selected.

## 8. Schedule behavior

- Default schedule names may be prefixed by the local Settings `Pilgrim Name`;
  the traveler can still edit the name before saving.
- Builder fields include name, start date, template metadata, route, start/end
  places, and valid route variants. Split-place choices show distance from the
  day's start and useful amenity icons without introducing network queries.
- A schedule is fully usable offline immediately after creation.
- After creation, show the schedule-editing tip explaining that a long press on
  a day offers rest, split, and combine actions. Respect the persisted “show
  again” preference.
- Long-press actions include adding a rest day, splitting a stage, combining
  with the previous/next stage where valid, and deleting a rest day. First and
  last rest days must remain deletable through a valid action; no edge-day may
  become trapped.
- A rest-day row displays `Rest Day` and the single place name, not `Place–Place`.
- Stage edits preserve route continuity, selected compatible variants, dates,
  day numbering, dirty flags, and soft-deletion records required for sync.
- A day map displays the whole route as context but initially focuses the
  selected day. The day's elevation profile is sliced only between that day's
  start and end.

## 9. Maps, variants, elevation, and location

### Route rendering

- Main route: red.
- Unselected alternatives: blue.
- Selected alternative: red.
- Replaced main section: orange/ochre for contrast.
- Never synthesize straight connector lines as a substitute for missing variant
  geometry. Investigate UUID, sequence, import, and cache consistency instead.
- Template variant selection is preview-only. Schedule variant selection is
  persistent user data and synchronizes across devices.
- A day map retains the complete route for zooming out while fitting/focusing
  the selected stage initially.
- Route maps and accommodation/place maps provide a full-screen option,
  especially for iPad.

### Elevation

- Elevation is plotted against route distance, supports horizontal scrolling on
  long profiles, includes useful place/day markers, and displays gain/loss with
  localized units.
- Day elevation is restricted to the day's endpoints even though its map shows
  whole-route context.
- Route-variant elevation must follow the variant path; the Valcarlos,
  Finisterre, and Portuguese Spiritual/Senda variants are regression cases.
- SRTM attribution and the approximate-data notice remain visible in
  Attributions.
- Do not restore the former inspect/zoom-in/zoom-out controls; they were removed
  because they were unnecessary and caused slow reactions. Horizontal panning
  is the intended interaction.
- Builds 13 and 15 are the performance references. Reuse already-imported/cached
  route geometry across templates and schedules; do not perform a duplicate
  full-route database/geometry build when opening another tab.
- The current cache implementation starts route warm-up from the template list,
  reuses decoded geometry for builder distance calculations and schedule
  creation, and keys composed paths by their ordered legs/variants. The latter
  is required so opposite-direction Camino Finisterre templates never share an
  incorrect cached path.
- Current memory budgets are deliberately bounded: four recently used decoded
  routes (approximately 24 MiB), twelve composed paths (approximately 12 MiB),
  twelve template presentations (approximately 12 MiB), and eight schedule
  presentations (approximately 8 MiB). These are performance caches, not a new
  persistence layer; installed SQLite/JSON content remains the offline source
  of truth.

### Trail Mode and offline basemaps

- Trail Mode uses `When In Use` Core Location, best accuracy, a 5 m distance
  filter, and foreground-only updates.
- A location older than 120 seconds is not considered current. Accuracy worse
  than 100 m is flagged as weak. The user is considered off-route beyond about
  250 m plus reported horizontal accuracy.
- The blue marker always represents the actual current/simulated GPS point. The
  app explains simulator location and weak/off-route conditions.
- GPS works offline; first fix may be slow indoors.
- Route geometry and content are installed with a content bundle. Mapbox base
  tiles are **not automatically downloaded for every route**. The traveler
  explicitly downloads a Trail Mode stage region.
- Current offline region behavior uses a roughly 1.5 km route buffer, Mapbox
  Standard style, and zoom levels 6...16. It exposes progress, cancel, retry,
  ready, and refresh states.
- Preserve Mapbox's required attribution and telemetry/privacy controls.

## 10. Places, accommodations, and corrections

- Place metadata icons must include their value: country code, one-line place
  type (`Town`, `Village`, `City`, etc.), and elevation with localized units.
  Values may stack as rows on narrow screens, but an icon label must not wrap
  into unreadable vertical letters.
- Important service icons include cafés, restaurants, pharmacies, and
  albergues. Pilgrim credential service uses a stamp/stamp-pad metaphor rather
  than a generic person icon.
- Accommodation facilities expose an info button explaining confirmed
  available/unavailable/unknown; the word `Legend` is unnecessary.
- Accommodation opening information is structured content. The active backend
  branch adds an `open_all_year` field through migration `0053` and carries it
  through imports, snapshots, exports, serializers, and admin. The active iOS
  branch imports/stores it, offers an `Open all year` accommodation filter, and
  shows opening dates/hours in the appropriate route-card and detail sections.
  Preserve unknown as unknown; do not infer year-round opening from missing
  dates or hours.
- Production hides source/debug metadata such as OSM ID, coordinates, source,
  source notes, catalog diagnostics, local content counts/hashes, and imported
  source commentary. Visible debug labels and console messages start with
  `DEBUG:`. Debug-only English does not need localization.
- Address can be copied and opened in Apple Maps or Google Maps. Phone opens the
  dialer; WhatsApp opens WhatsApp when available; email opens the default mail
  client and can be copied.
- Both Place and Accommodation pages offer `Suggest a correction` to
  `support@longslowtravel.com`. If no mail client exists, show/copy the prepared
  fallback and visibly state the support address.
- Subjects are `Long Slow Travel Camino - Accommodation Correction: <name>` or
  `Long Slow Travel Camino - Place Correction: <name>`.
- The localized message includes journey, route, itinerary template, place
  where found, current public fields, `Correct information`, and `Evidence if
  available`. It does **not** include the current source record. Reporter name
  and email remain optional.
- Booking links must identify a direct property page. Do not publish generic
  search-result links or infer identity from a matching name alone. Verify
  address/coordinates and record evidence in the reviewed ledger.

## 11. Authentication, offline identity, and account deletion

- Register is the first account-mode tab for first-time users. Sign-in accepts
  username or verified email.
- Production requires email verification. Registration returns
  `verification_required`, sends a six-digit code through Brevo, and does not
  authenticate the user until verification succeeds. Regression tests must
  protect this contract.
- Password reset also uses a time-limited emailed code.
- JWT access and rotating refresh tokens are the production mechanism; legacy
  token auth is disabled in production.
- Credentials and the cached current-user snapshot live in Keychain. On offline
  launch or transient server failure, a cached authenticated user remains shown
  as signed in and can use offline data. A confirmed 401/403 or expired session
  clears authentication.
- Auth requests time out rather than spinning forever; current client timeout is
  12 seconds and errors distinguish no internet, unreachable server, and TLS
  failures.
- Logging out resets navigation to the initial Journeys state and clears
  account-bound local access/sync state so a protected detail screen is not left
  open. Data belonging to different account IDs must remain isolated.
- `Delete Account` belongs in Settings. It requires the password, deletes the
  backend account and account-owned data, clears local account ownership, and
  returns to guest mode while preserving legitimate guest schedules.

## 12. Multi-device schedule sync

### User-facing model

- `Sync` means push local dirty schedules/days and then pull server changes.
- Content `Refresh` means check the backend catalog and install/update route
  data. It is not schedule sync.
- Schedule lists support both a clearly labeled Sync control and pull-to-refresh
  where appropriate. Foregrounding the app also triggers authenticated sync.

### Protocol invariants

- Client UUIDs identify records across devices.
- Push itineraries before their days.
- Updates carry `base_revision`; the backend accepts them only when it matches
  the server `sync_revision`. A mismatch returns 409 conflict with the server
  record; do not silently overwrite either side.
- Soft deletes synchronize. After another device deletes a schedule, the local
  list and any open detail view must dismiss/remove it instead of showing an
  empty orphan page.
- Pull checkpoints use the backend response `server_time`, never the phone's
  wall clock. Timestamps are UTC/ISO-8601 and are not a substitute for revision
  conflict control.
- Separate itinerary and day pull checkpoints are scoped per authenticated user.
- Local changes made during an in-flight sync queue a follow-up pass so they are
  not stranded as dirty.
- Sync runs after authentication/guest transfer, verified purchase access
  changes, return to foreground, explicit Sync, and appropriate refresh actions.
- A local edit should appear on another signed-in device after the first device
  syncs and the second device syncs/foregrounds. This and remote deletion are
  mandatory regression tests.

## 13. Localization and presentation

- Supported app choices: System Default, English, German, Spanish, French,
  Italian, and Portuguese.
- User-facing SwiftUI text belongs in `Localizable.xcstrings`; Info.plist privacy
  strings belong in `InfoPlist.xcstrings`.
- Use `LocalizedStringKey` in views and `String(localized:locale:)` where a plain
  `String` is required. Interpolated correction-email templates require the
  requested locale's localization bundle, not only the process language.
- Proper place names, route names, database keys, slugs, UUIDs, product IDs, and
  debug-only diagnostics are not translated unless there is an explicit
  localized content field.
- Localize navigation, route/access messages, Content purchase/restore/status
  text, schedule creation/editing, day actions, details, place types, dates,
  units, and accessibility labels. Do not limit localization to tab titles.
- Dates use the selected/system locale; measurements use the Settings metric or
  imperial choice. Avoid hard-coded `YYYY-MM-DD` in user-facing UI.
- Layout must tolerate longer German and Romance-language strings. Prefer
  wrapping, vertical stacks, `ViewThatFits`, and Dynamic Type over shrinking text
  into unreadable vertical fragments.
- The app intentionally uses a light visual theme. Keep form fields and tab bars
  high-contrast and predictable regardless of device dark-mode settings.

### Brand system

- Brand: `LONG SLOW TRAVEL`; tagline: `JOURNEYS WORTH TAKING`.
- Camino edition uses the Long Slow Travel mountain/path mark plus a gold Camino
  scallop shell. The same updated mark is used for the app icon and Journeys
  header.
- Core palette is centralized in `LSTDesign.swift`: pine, sage, gold/ochre,
  terracotta, sea, sand, stone, cream, charcoal, and semantic success.
- Reuse `LSTFont`, `LSTSpacing`, `LSTRadius`, card styles, buttons, hierarchy
  headers, and edition badges. Route content must not carry UI color decisions.

## 14. Content creation and publishing rules

### Geometry and distance

- Canonical GPX is full-resolution route geometry. The backend imports and
  validates GPX; iOS does not parse GPX.
- Route distance is measured along the ordered geometry. Project places onto
  segments, not merely the nearest stored vertex.
- Alternate geometry must be ordered and connected. Missing geometry is an
  import defect; do not invent straight lines between endpoints.
- Recalculate route-place and template distances from reviewed canonical
  geometry, and keep elevation/source metadata consistent.

### Route packages and snapshots

- Create/import route packages atomically. Dry-run first, review counts and
  geometry, then apply.
- Checked-in snapshots under backend `exports/` make production content
  reproducible. `travel/data/bootstrap/platform-content.json` lists the required
  platform release.
- `bootstrap_platform_content` is dry-run unless `--apply` is supplied. It
  reconciles canonical UUIDs and must protect user schedules/entitlements.
- `prepare_platform_content_release` validates the database and checked-in
  snapshots. Use `--write` only after reviewed source changes and a passing dry
  run.
- Increment dataset versions when published bundle content changes. Do not bump
  versions for unrelated code-only changes.
- Deactivate released content rather than physically deleting records referenced
  by schedules or entitlements.
- Purchase-family children may point only to a direct paid parent, never a child
  of another child, themselves, or a free bundle. Included children must have no
  store product ID.

### Accommodation/source maintenance

- Keep OSM/manual override/suppression/exclusion and booking-link evidence
  ledgers reviewable and reproducible.
- Record evidence, date, and reason for manual corrections.
- Never turn unknown facility data into a negative claim.

## 15. Production topology and operational invariants

### Current services

- Domain registration remains with the owner's registrar.
- Static website: GitHub Pages at `longslowtravel.com`.
- API: Render web service in Frankfurt at `api.longslowtravel.com`.
- Database: managed Render PostgreSQL 17 in Frankfurt; it is private to Render.
- Transactional account mail: Brevo SMTP using the verified
  `noreply@longslowtravel.com` sender.
- Support mailbox: Proton Mail at `support@longslowtravel.com`.
- iOS distribution and purchases: App Store Connect/TestFlight and StoreKit 2.

DNS website records must coexist with the `api` record, Proton MX records, and
Proton/Brevo verification, SPF, DKIM, and DMARC records. Never replace all DNS
records when changing one service.

### Production configuration classes

Values live in Render/App Store/GitHub configuration, not this file. Required
classes include database URL, separate long Django and JWT signing secrets,
allowed hosts/CSRF origins, HTTPS redirect, SMTP host/user/key, default/support
addresses, verification and legacy-auth flags, StoreKit bundle/environment/Apple
ID/online-verification settings, Apple public root certificate path, and demo
account password.

- `DJANGO_DEBUG=false`, HTTPS redirect on, only production hosts/origins allowed.
- `ACCOUNT_EMAIL_VERIFICATION_REQUIRED=true`.
- `ENABLE_LEGACY_TOKEN_AUTH=false`.
- The public Apple root certificate may be checked into the backend repository;
  private keys and credentials may not.
- Demo credentials are operational secrets. `provision_demo_account` may create
  or refresh the demo account, but never publish its password.

### Deployment safety

- Normal deployment path is reviewed branch -> GitHub merge to `main` -> CI on
  `main` -> Render automatic deployment after checks pass.
- Both iOS and backend GitHub workflows currently run on pushes to `main` or
  manual dispatch, not on every pull request, to conserve GitHub Actions minutes.
- Before backend deployment: tests, missing-migration check, system/deploy
  checks, and platform-content validation where content changed.
- After deployment: verify Render completed migration/startup, health endpoint,
  logs, content catalog, email registration/reset, purchase verification when
  applicable, and `check_production_readiness` in the Render shell.
- Take a PostgreSQL backup before high-risk data/content operations. Test restore
  into a separate database; never overwrite production as the first restore
  attempt.
- Prefer a forward fix and additive migration. Never use `git reset --hard`,
  manually delete migration history, fake production migrations casually, or
  run `reset_development_users` in production.

## 16. Development workflow and useful commands

Run Git commands from the intended repository, never from the project parent by
accident. If the worktree is dirty, inspect first and preserve the owner's files.

### Create a branch

```bash
git switch main
git pull --ff-only origin main
git switch -c feature/descriptive-name
```

For a bug use `fix/descriptive-name`. Do not switch branches with uncommitted
overlapping work until it is committed, stashed with the owner's approval, or
otherwise safely handled.

### iOS local backend

The local backend uses PostgreSQL. A typical no-password local socket URL used
in this project is:

```bash
export DATABASE_URL="postgres://localhost:5432/longslowtravel"
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver 0.0.0.0:8000
```

On a physical iPhone, set the Debug scheme `LST_API_BASE_URL` to
`http://<Mac-LAN-IP>:8000/api/`, run Django on `0.0.0.0:8000`, and include that
LAN IP in local `DJANGO_ALLOWED_HOSTS`. Browse `http://localhost:8000/health/`,
not `/`; the backend intentionally has no root webpage.

Never point routine local development at the production Render database. Local
and production databases are not meant to be live replicas; canonical snapshots
and migrations keep platform content reproducible while user production data
remains protected.

### iOS tests

Preferred interactive check:

1. Open `LongSlowTravel.xcodeproj`.
2. Select scheme `LSTCamino` and an installed iOS 17+ simulator/device.
3. Choose **Product -> Test**.

Do not hardcode an unavailable simulator OS. Inspect destinations first:

```bash
xcodebuild -project LongSlowTravel.xcodeproj -scheme LSTCamino -showdestinations
```

Run the release gate before archiving:

```bash
bash tools/testflight_preflight.sh
```

Mapbox binary-framework dSYM upload warnings can occur after a successful
archive. Confirm they refer only to vendor frameworks and monitor crash
symbolication; do not block a valid TestFlight upload without evidence the app's
own symbols are missing.

### Backend tests and checks

Use the local PostgreSQL URL unless a test explicitly needs an isolated SQLite
fixture. The production-like full checks are:

```bash
export DATABASE_URL="postgres://localhost:5432/longslowtravel"
.venv/bin/python manage.py makemigrations --check --dry-run
.venv/bin/python manage.py check
.venv/bin/python manage.py test config accounts travel
.venv/bin/python manage.py prepare_platform_content_release
```

Expected tests may deliberately print handled 400/401/409 responses, a
`Production readiness failed: [test.issue] Not ready.` fixture message, or GPX
query-splitting diagnostics. They are not failures when the test process ends
`OK`; investigate only unexpected traceback/failure/error output.

Bootstrap reviewed snapshots:

```bash
.venv/bin/python manage.py bootstrap_platform_content \
  travel/data/bootstrap/platform-content.json

.venv/bin/python manage.py bootstrap_platform_content \
  travel/data/bootstrap/platform-content.json --apply
```

Run the first command as a dry run. In Render, long content imports can consume
CPU for several minutes; use another shell and `ps` to verify progress rather
than launching duplicate `--apply` jobs.

### Website preview

```bash
python3 -m http.server 8000
```

Open `http://localhost:8000/` and manually verify desktop/mobile landing,
Support, Privacy, Imprint, navigation, current app imagery, mail links, and no
external tracking requests.

## 17. Test and release matrix

### iOS regression areas

- First launch with bundled free content and airplane mode.
- Locked catalog routes visible in the correct order; lock opens Content.
- Free Sarria route available without account.
- Registration requires and sends verification; resend and password reset.
- Offline signed-in state remains signed in; logout resets protected navigation.
- Guest schedule add-and-sync/delete decision after register and after sign-in.
- Same-account two-device create/edit/delete sync, including foreground refresh,
  UTC checkpoints, conflicts, and open-detail deletion.
- Purchase/restore with StoreKit local config and TestFlight sandbox; parent
  purchase unlocks included bike/Portuguese bundles.
- Content install/update and offline restart.
- Main/selected/replaced/alternate geometry for Valcarlos, Finisterre, Spiritual,
  Senda Litoral, and Portuguese overland/boat alternatives.
- Build 13 elevation responsiveness for a long Camino Francés template and
  schedule; tab changes remain responsive.
- First/last rest days survive template-to-schedule creation and are editable.
- Whole-route context on day map but day-only elevation slice.
- Foreground GPS permission, stale/weak/off-route states, and offline stage map.
- Full-screen route and accommodation maps; Apple/Google Maps and contact links.
- Long German/localized text, Dynamic Type, narrow iPhone 11, and iPad layouts.
- Account deletion and correction-email fallback.

### Backend regression areas

- Production-required email verification and throttles.
- JWT refresh/logout/account deletion.
- Catalog ordering, locked/owned/download states, parent included bundles, and
  the single Portuguese product policy.
- StoreKit certificate/signature/product/environment/app-account/transaction
  validation and idempotent restore.
- User-itinerary creation preserves zero-distance edge rest days and default
  variants.
- Revision conflicts, per-user delta checkpoints, UTC server time, and soft
  deletes.
- Canonical UUID reconciliation, migration compatibility, snapshot round trips,
  content integrity, OSM identity audit, and no user-data overwrite.

### TestFlight smoke test

Use a Release/TestFlight build so it reaches production, not the Debug LAN API.
Check guest/free use, account email flows, catalog/order, purchase and restore,
included routes, content downloads, offline relaunch, maps/elevation/location,
schedule edit/sync across two devices, correction mail, Settings, Privacy and
Support URLs, and account deletion. Increment build number before every upload.

## 18. Known state, deferred work, and cautions

### Release and performance baseline

Builds 13 and 15 are the owner's responsive elevation references. Build 15 was
the last TestFlight upload explicitly confirmed in this conversation, but it
does not automatically contain later merged Finisterre fixes or the active
uncommitted branches. Before any new iOS work, confirm:

```bash
git status --short
git diff
git diff --staged
```

Do not reintroduce abandoned changes from shell history or an old patch.

### Active handoff: iOS itinerary/accommodation/performance branch

As of 2026-09-02, `feature/declutter-itinerary-tabs` is intentionally dirty and
not ready to merge merely because individual screens look correct. Its current
scope includes:

- less cluttered itinerary/schedule map and elevation presentation, with full
  route/elevation source details centralized in Attributions;
- accommodation-map/card consistency, accommodation filters, opening dates,
  opening hours, and year-round-opening presentation;
- localized production notes and user-facing labels while keeping provenance
  diagnostics debug-only;
- asynchronous route/elevation warm-up plus bounded decoded, processed-path,
  template-presentation, and schedule-presentation caches;
- preservation of corrected bidirectional Camino Finisterre schedule paths;
- regression tests and matching `README.md` changes.

Recent compiler repairs make the variant-geometry `compactMap` result explicitly
`[LSTRouteGeometry]` in `RouteGeometryRepository.swift`; without it, Swift
reports that generic parameter `ElementOfResult` cannot be inferred. The
template and schedule presentation cache-key builders now also construct their
geometry arrays and signature fields as explicitly typed intermediate values;
the previous chained optional-array/map expressions exceeded Swift's reasonable
type-checking time.
Swift parsing, localization-catalog compilation, and `git diff --check` passed
during the cache work. A full Xcode build/test is still required on the owner's
Mac because this Codex sandbox cannot load Apple's CoreSimulator framework.
After any further compile fixes, rerun the focused tests plus the complete
`LSTCamino` test action and manually time long Camino Francés templates and
schedules on a simulator/device.

### Active handoff: backend accommodation-opening branch

As of 2026-09-02, `feature/accommodation-opening-information` contains
uncommitted `open_all_year` model/import/export/snapshot/serializer/admin work
and migration `0053_accommodation_open_all_year.py`. Verify the migration,
focused import/snapshot tests, full backend suite, missing-migration check, and
platform release validation before commit. If content snapshots change, follow
the normal dry-run/apply and dataset-version rules rather than expecting a code
deployment alone to update installed iOS content.

### Documentation drift already observed

- Older iOS README text may still call the app `Camino Planner`, mention the old
  scheme `LongSlowTravel`, or list fewer languages. Current project/config files
  take precedence until those docs are corrected.
- The public Privacy page text says Render “will host” production even though
  production hosting is active. Review wording before App Store release.
- The public landing/support wording may still use `Camino Planner` while the
  installed app is branded `LSTCamino`. Treat naming consistency as an explicit
  marketing decision, not an incidental code replacement.
- Booking.com/affiliate monetization has been discussed but is not documented as
  live production behavior. If activated, retain direct-property identity
  checks, add clear affiliate disclosure, update Privacy/Imprint/App Store
  disclosures as applicable, and review whether any tracking or cookies require
  consent before deployment.

## 19. How an AI assistant should handle common requests

### “Fix this error”

Inspect the exact file and surrounding data flow, reproduce or compile, make the
smallest fix, add a regression test if behavior can recur, and run the narrow
test plus an appropriate broader suite. Do not use a reported compile error as
permission to redesign the feature.

### “It is slow” or “it hangs”

Do not guess. Compare against build 13, measure main-thread/database/network
work, identify duplicate loads and cache misses, inspect actor boundaries, and
verify on representative long routes. Preserve UI responsiveness and allow
navigation/cancellation while loading.

### “Routes/content differ locally and in TestFlight”

Trace all versions separately: source CSV/GPX, checked-in JSON snapshot,
backend migration/bootstrap, production database bundle dataset version and
hash, API catalog response, installed iOS bundle, geometry cache, and app build.
Do not assume Debug and Release share SQLite or backend databases.

### “Purchase belongs to another account”

Collect only safe identifiers/status codes; never request passwords or full
receipts. Check Apple Account/sandbox account, Long Slow Travel user,
`app_account_token` ownership, product ID, original transaction linkage,
backend entitlement, and whether the build uses local StoreKit or TestFlight.
Do not delete production entitlements until exact rows and recovery are known.

### “Change content”

Use backend data/import/snapshot workflows, preserve released UUIDs, increment
appropriate dataset versions, run content integrity tests, and deploy/bootstrap
before expecting iOS to see it. Do not patch a Swift display switch to mask bad
canonical data.

### “Commit and merge”

Show status/diff first. Stage only scoped files, use a descriptive conventional
commit, push the feature branch, and give the user the PR/merge steps. The owner
normally merges in GitHub's browser. After she says “merged,” update local main
with a fast-forward before creating the next branch.

## 20. Keeping this README-AI.md current

This file is part of the definition of done for all durable project changes,
including single-repository changes already documented in that repository's
`README.md`. A component README explains that component; this file preserves the
cross-repository state and continuation instructions for the next chat.

Update it when any of the following changes:

- repository layout, scheme/target/bundle/display names, deployment target, or
  core dependency;
- domain, hosting, database, email, App Store, privacy, or support architecture;
- authentication, guest-transfer, sync, purchase, account-deletion, offline,
  map, variant, or elevation behavior;
- route packs, product IDs, inclusion families, route order, template catalog,
  content publishing commands, or data ownership;
- supported languages, measurement/date rules, brand system, or production/debug
  visibility;
- known-good release baseline, active in-progress branch, release checklist, or
  recurring regression test.

Maintenance procedure:

1. Re-read the affected code, tests, migrations, source data, and operational
   docs; do not update this file from memory alone.
2. Change the `Last reconciled` date and repository-state snapshot.
3. Move completed work out of `Known state/deferred work`; document the final
   invariant in the appropriate main section.
4. Mark abandoned ideas as abandoned or remove them. Do not present a requested
   idea as shipped behavior.
5. Check every command, scheme, endpoint, slug, product ID, and filename.
6. Scan the diff for secrets and personal identifiers. Values may be named as
   environment-variable keys, never included.
7. Commit this file in the same branch as the durable change when feasible.
8. During unfinished work, record the active branch, dirty-file scope, completed
   checks, blocked checks, and next required verification before ending a chat.
   Reconcile that temporary handoff after the work is committed, merged, or
   abandoned.

## 21. Primary source map

Start with these files when verifying this specification.

### iOS

- `README.md`, `docs/LOCALIZATION.md`, `docs/TESTFLIGHT.md`
- `LongSlowTravel/AppVariants/Camino/ActiveAppConfig.swift`
- `LongSlowTravel/Core/AppConfig/LSTAppConfig.swift`
- `LongSlowTravel/App/RootView.swift`
- `LongSlowTravel/Core/Networking/APIEndpoints.swift`
- `LongSlowTravel/Core/Networking/AuthTokenProvider.swift`
- `LongSlowTravel/Core/StoreKit/RoutePurchaseStore.swift`
- `LongSlowTravel/Core/Sync/`
- `LongSlowTravel/Core/Content/`, `LongSlowTravel/Core/Import/`
- `LongSlowTravel/Features/Route/RouteListView.swift`
- `LongSlowTravel/Features/Route/RouteGeometryRepository.swift`
- `LongSlowTravel/Features/Route/RouteDistanceCalculator.swift`
- `LongSlowTravel/Features/Itinerary/`
- `LongSlowTravel/Features/Map/`
- `LongSlowTravel/Features/Place/`, `LongSlowTravel/Features/Accomodation/`
- `LongSlowTravel/Core/Settings/AppPreferences.swift`
- `LongSlowTravel/Localizable.xcstrings`
- `LongSlowTravel.xcodeproj/project.pbxproj`
- `LongSlowTravel.xcodeproj/xcshareddata/xcschemes/`
- `LongSlowTravelTests/`

### Backend

- `README.md`, `docs/mobile_sync_api.md`, `docs/route-packs.md`
- `docs/content-maintenance.md`, `docs/gpx-route-distances.md`
- `docs/production-deployment.md`, `docs/operations-runbook.md`
- `config/settings.py`, `render.yaml`, `build.sh`
- `accounts/`
- `travel/models.py`, `travel/content_catalog.py`, `travel/content_access.py`
- `travel/storekit_route_purchases.py`, `travel/storekit_views.py`
- `travel/services/itinerary_builder.py`
- `travel/canonical_bundle_snapshot.py`, `travel/platform_content_release.py`
- `travel/management/commands/`
- `travel/data/`, `exports/`, `travel/tests/`

### Website

- `README.md`, `CNAME`
- `index.html`, `styles.css`, `script.js`
- `support/index.html`, `privacy/index.html`, `imprint/index.html`

When a new chat has read this file and verified the current Git state, it should
be able to continue without relying on memory from any previous conversation.
