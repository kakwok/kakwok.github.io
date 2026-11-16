# CV + Personal Site Pipeline

Single-source-of-truth CV system for a CMS particle physicist. Structured YAML data is the
source; PDF and HTML are build targets.

**This repo is PUBLIC.** It is the GitHub Pages user site. See "Privacy constraints"
before adding anything — git history here is permanent and world-readable.

---

## Core principle: the publication list is HAND-CURATED

INSPIRE-HEP is **not** the source of truth for publications. The author is on hundreds of
CMS collaboration papers they did not personally work on. Listing those hides actual
contributions and makes the CV unreadable.

- `_data/publications.yml` is written by hand and is authoritative. ~15 entries, ever.
- INSPIRE is a **metadata assistant** (autofill on entry) and a **linter** (catch stale
  refs). It never generates or expands the list.
- The full list is a **single link** to the INSPIRE author profile, plus two integers
  (paper count, citation count) fetched at build time.

There is no BibTeX anywhere in this system. No `.bib` files, no jekyll-scholar, no
bibliography tooling. BibTeX manages large machine-generated corpora; this is a small
curated set with rich annotations, and YAML serves it better.

**If a task seems to call for auto-populating publications from INSPIRE, that is a
misunderstanding of this project. Stop and ask.**

---

## Repo topology

**One repo.** This one. It is both the CV source and the website.

```
kakwok.github.io/  PUBLIC  (this repo)
  _data/*.yml  ─┬─►  Jekyll + Liquid  ─►  the website
                └─►  build.py (filter by variant) ─► rendercv ─► assets/cv.pdf
```

`_data/` is read directly by Jekyll AND by `build.py`. It is hand-edited source, not
generated output — one set of files, two renderers, so the PDF and the site cannot drift.

This replaces an earlier two-repo design (a private `cv` repo pushing four files into this
one via a fine-grained PAT). It was dropped because almost nothing in `_data/` is actually
private: seven of the eight files are CV content that already appears on the public site.
The cross-repo copy, the `SITE_PAT` secret, and the drift risk all bought very little.

Do not reintroduce a second repo or git submodules. The one thing that genuinely must not
be public is handled by `.gitignore` — see "Privacy constraints" below.

---

## Privacy constraints — read before committing

Everything committed here is world-readable, forever. Git history is permanent; a later
commit cannot scrub a leak. There is no private tier — the guard is what you don't commit.

1. **Never commit a personal phone number or home address**, in `_data/`, in an example,
   a fixture, or a test. `basics.yml` carries work email and work mailing address only;
   `phone` stays `null`. A CV that needs a phone number gets it added at print time.
2. **Variants are named by FLAVOR, never by employer.** `academic`, `computing-staff`,
   `industry-ml` are fine and committed — nobody learns anything from their existence.
   A file named for where you are applying publishes your job search, with a timestamp.
   Anything targeted stays local and must match a `.gitignore` pattern:
   `variants/*-application.yml`, `variants/private-*.yml`, `variants/local-*.yml`.
3. Only the `academic` variant is committed as `assets/cv.pdf`. Other flavors are CI
   artifacts, downloadable from the Actions run, not committed.
4. Strip PDF metadata (`/Author`, `/Creator`, producer strings) before committing a PDF
   if it leaks a variant name or a local filesystem path.
5. `narrative:` in `research.yml` and every `role`-adjacent free-text field is read by
   strangers. Write it for a general physics audience.

---

## Layout

```
kakwok.github.io/
├── _data/                   SOURCE OF TRUTH — read by Jekyll and by build.py
│   ├── basics.yml           name, work contact, links (ORCID, INSPIRE, GitHub)
│   ├── education.yml
│   ├── experience.yml       work + professional service appointments
│   ├── publications.yml     HAND-CURATED — see schema below
│   ├── talks.yml
│   ├── awards.yml
│   ├── teaching.yml         teaching, outreach, mentoring
│   └── research.yml         research themes — feeds CV highlights AND site Research page
├── schemas/
│   ├── publications.schema.json   editor autocomplete + validation
│   └── talks.schema.json
├── variants/                flavors only, never employer names (privacy #2)
│   ├── academic.yml         THE ONE COMMITTED AS assets/cv.pdf
│   ├── computing-staff.yml
│   └── industry-ml.yml
├── scripts/
│   └── inspire.py           add | check | stats
├── build.py
├── legacy/                  the pre-pipeline CV, kept for reference
│   ├── CV.tex
│   └── CV_UNL.pdf
├── _layouts/ _includes/ _sass/ assets/    Jekyll site
├── index.md about.md publications.md talks.md
├── _config.yml
└── .github/workflows/cv.yml
```

---

## publications.yml schema

```yaml
- date: 2024-07
  authors: CMS Collaboration
  title: >-
    Search for long-lived heavy neutral leptons decaying in the CMS muon
    detectors in proton-proton collisions at $\sqrt{s}=13$ TeV
  ref: Phys. Rev. D 110 (2024) 012004
  arxiv: "2402.18658"
  doi: 10.1103/PhysRevD.110.012004
  inspire: 2762588
  domain: physics            # physics | computing  — ONLY these two
  tags: [llp, hnl, trigger]
```

**`domain`** has exactly two values, matching the existing CV's section split. Detector and
electronics work (HGCAL ASIC, MAIA muon collider concept) is `domain: physics` carrying an
`instrumentation` tag — NOT a third domain. The tag keeps that work selectable by variants
without a schema split, and preserves information that would be expensive to reconstruct
by hand later.

**There is no `contribution` field and no `role` field.** Curation itself is the signal:
an entry is in this file because it belongs on the CV, and nothing else needs saying. The
publication list is not where expertise gets argued — research highlights, talks, service
appointments and teaching carry that, and a reader weighs them against the paper list.

Do not reintroduce per-paper contribution or role annotations. Stating your own role inside
a publication list is not convention in this field, and a curated ~15-entry list already
excludes the hundreds of author-list-only CMS papers that the annotation existed to mark.

`talks.yml` uses the same `domain` axis plus
`kind: [plenary, parallel, poster, seminar, lecture]`.

### Rendered output

- "Selected publications — Physics" → `domain: physics`
- "Selected publications — Computing" → `domain: computing`
- One line: `Full publication list (N papers, M citations): inspirehep.net/authors/XXXXXXX`

N and M are the only values fetched from INSPIRE at build time. Two integers, no records.

---

## research.yml schema — two verbosity levels, one source

Feeds both the CV's "Research highlights" (terse bullets) and the website's Research page
(prose). Same entry, different fields, so they cannot drift apart.

```yaml
- title: Long-lived particle searches with Muon Detector Showers
  start: 2020
  end: null                  # null = ongoing
  domain: physics
  tags: [llp, trigger, detector]
  highlights:                # → CV bullets, terse, imperative
    - Coordinating multiple LLP search efforts using the novel MDS signature
    - Set world-best limits on low-mass long-lived HNLs; published in PRD
  narrative: >               # → website Research page, prose, 1-2 paragraphs
    Long-lived particles decaying inside the CMS muon detectors leave a distinctive
    shower signature that conventional reconstruction discards...
  figure: assets/mds-shower.png   # optional, website only
```

- The CV uses `title`, dates, and `highlights`. It ignores `narrative` and `figure`.
- The website uses `title`, dates, and `narrative`, falling back to `highlights` if
  `narrative` is absent — so a new entry is useful on the CV before the prose is written.
- `narrative` is public. Write it for a general physics audience, not for a grant panel.

---

## scripts/inspire.py

Three commands. This is where implementation effort should go — ease of entry is a primary
requirement.

**`add <arxiv-id | doi | recid>`** — fetch record, append a stub to `publications.yml` with
everything machine-knowable filled in and `domain` and `tags` left as `TODO`.

Endpoints: `https://inspirehep.net/api/arxiv/{id}`, `/api/doi/{doi}`, `/api/literature/{recid}`.
Relevant metadata fields: `titles[0].title`, `publication_info[0]` (journal_title,
journal_volume, year, artid/page_start), `arxiv_eprints[0].value`, `dois[0].value`,
`control_number`, `collaborations[0].value`, `earliest_date`.

**`check`** — re-query each entry by its `inspire` recid. Report: preprints now published,
missing DOIs, journal refs changed during proofs. Run monthly in CI, open a PR with the
diff. This is the ONLY automated write path and it only corrects metadata on entries the
author already chose to include. Never adds entries.

**`stats`** — refresh N (paper count) and M (citation count) for the full-list line.

Add JSON Schema so the editor autocompletes `domain` and the closed `tags` vocabulary, and
flags entries still carrying a `TODO`.
Combined with `add`, entering a new paper should take ~20 seconds.

---

## Data conventions

Every entry carries `tags`. Variants are filters over tags, never copies of content.

Tag vocabulary (keep closed; add deliberately):
`hep`, `computing`, `ml`, `llp`, `hnl`, `trigger`, `detector`, `instrumentation`, `gpu`,
`portability`, `leadership`, `outreach`, `carve`

The vocabulary is enforced by `schemas/*.schema.json`. Adding a tag means editing the enum
in both schemas — that friction is deliberate, it is what keeps the list closed.

A variant is a section list with filters:

```yaml
# variants/industry-ml.yml
theme: classic
max_pages: 2
sections:
  - {from: experience,   tags_any: [ml, computing], limit: 4}
  - {from: publications, domain_any: [computing], tags_any: [ml, instrumentation], limit: 5}
  - {from: talks,        domain_any: [computing], limit: 4}
```

Adding a new tailored CV should be a ~15-line YAML file and nothing else. If a change
requires editing `_data/`, the abstraction is wrong — fix the filter layer instead.

---

## Rendering

**RenderCV** (YAML → Typst → PDF, plus HTML output; ships a JSON Schema). Needs Python
≥ 3.12 — the default `python3` here is MacPorts 3.8, so build the venv against
`/usr/local/bin/python3.13`. The tag-filter layer sits upstream:

    _data/*.yml →  build.py (filter by variant)  →  rendercv YAML  →  rendercv render

The HTML output feeds the website's `/cv/` page, so PDF and web CV never diverge.

Two things `build.py` does that are easy to undo by accident:

- **`detex()`** converts the LaTeX in `_data/` to Unicode on the PDF path only (`√s = 13
  TeV`). Typst does not read LaTeX math. The source keeps LaTeX because Jekyll renders it
  with KaTeX — do not "clean up" `_data/` by pre-converting it.
- **Publications, talks, awards and teaching render as one-line text entries**, not
  RenderCV's structured entry types. A `PublicationEntry` spreads title, authors, journal
  and date over four lines at 1.2em spacing; with ~50 of them that alone cost two pages.
  Text entries pack at 0.25em and read like the old LaTeX CV. This is why the CV fits in
  three pages instead of five.

Fallback if RenderCV's layout proves too constraining: Jinja2 → `moderncv`/`altacv` →
`latexmk`. Do not switch without a concrete blocker.

Overleaf is a **preview target only**. Never edit there — it reintroduces the copy-paste
divergence this system exists to eliminate.

---

## KNOWN BUG to fix during migration

The current CV's header block reads *"Research Associate, Fermi National Accelerator
Laboratory, MS 205, PO Box 500, Batavia, IL"* while Work Experience correctly says
*"2025 – Now  Research Assistant Professor, University of Nebraska-Lincoln, NE."*
The personal website also still says "research associate at Fermilab."

Fix: `basics.yml` must **derive** the header title/affiliation/address from the first entry
in `experience.yml` rather than storing them separately. This class of error is the reason
the pipeline exists.

---

## Verify before writing dependent code

- ~~INSPIRE **author recid**~~ — confirmed: `1380817` (ORCID on the profile matches).
- ~~INSPIRE **BAI**~~ — confirmed: `Ka.Hei.Martin.Kwok.1`. Used by `stats`.
- Contact email is `kkwok@fnal.gov` **on purpose** — the author kept the Fermilab address and it is
  the primary contact. It is not stale; do not "fix" it. (Same logic as the Batavia location on the
  UNL entry in `experience.yml`.)

---

## CI

Triggers: push to `_data/`, `variants/`, `build.py`; monthly cron; `workflow_dispatch`.

Everything runs in this repo. There is no cross-repo push and no PAT — the site rebuilds
from `_data/` on its own when Pages sees the commit.

- Build all variants → `out/*.pdf` → `actions/upload-artifact`. Flavors other than
  `academic` stay artifacts and are never committed (privacy #3).
- Commit `out/academic.pdf` → `assets/cv.pdf` using the built-in `GITHUB_TOKEN` with
  `contents: write`. No secret to manage.
- Guard against loops: the commit step must skip when `assets/cv.pdf` is byte-identical,
  and the workflow must ignore pushes it made itself (`[skip ci]` or a paths filter).
- Monthly `inspire.py check` opens a PR if metadata drifted. Never auto-merge.
- `inspirehep.net` must be added to the allowed network domains.
- CI must fail if a tracked file matches a `.gitignore` privacy pattern from privacy #2 —
  the pattern only helps if nothing slipped in before it existed.

---

## Website (kakwok.github.io)

Current state: minimal Jekyll, four pages (Home / About / Publications / Talks),
hand-maintained publication list, footer stuck at `© 2023`, stale Fermilab affiliation.
Clean and fast, but thin and reads as frozen.

Migration to **al-folio** planned — but note the publications page now comes from
`_data/publications.yml`, NOT from jekyll-scholar. Do not enable the theme's bibliography
machinery.

Backlog, roughly in priority order:

- [ ] Fix stale affiliation (UNL, not Fermilab) sitewide
- [ ] `/cv/` page — embedded PDF + HTML version
- [ ] Publications page rendered from `_data/`, grouped by domain
- [ ] Identity links: ORCID, INSPIRE, Google Scholar, GitHub, LinkedIn, arXiv —
      footer *and* JSON-LD `Person` schema in `<head>`
- [ ] Research page — its own top-level page, rendered from `_data/research.yml` using
      each entry's `narrative`. Themes: LLP/MDS searches, boosted H→bb̄, GPU portability,
      DQM+VLM. Do not duplicate this content on About or Home.
- [ ] Projects page: dqm-vision-bench, CARVE, SonicTriton, IFSC results viewer
- [ ] News / "Now" feed — dated one-liners, top 3 on homepage
- [ ] **Verify math rendering** — publications contain `$\sqrt{s}=13$ TeV`. Confirm
      KaTeX/MathJax is loaded; raw LaTeX may be showing to visitors.
- [ ] Typography: ~18px body, line-height 1.6, ~68ch measure, `prefers-color-scheme` toggle
- [ ] Auto-year footer: `{{ site.time | date: '%Y' }}`
- [ ] Meta: OpenGraph card image, favicon, sitemap.xml, RSS, image alt text, 404 page
- [ ] Custom domain

---

## Build order

1. `_data/` transcribed from the existing `CV_UNL.pdf`, with `domain` and `tags` added to
   every publication and talk. Hand work, unavoidable, do it first.
2. `schemas/` + `scripts/inspire.py add` — makes step 1 faster partway through.
3. RenderCV + the `academic` variant — prove the pipeline end to end against the existing PDF.
4. Remaining variants, then CI.
5. Website migration last.

## Working agreements

- Never auto-generate publication entries. Curation is the point.
- Prefer fixing the filter layer over touching `_data/`.
- Never commit a real phone number or address in an example, fixture, or test.
- When adding a variant, confirm it is not the one published to the public site.
