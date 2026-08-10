#!/usr/bin/env python3
"""INSPIRE-HEP helper for the hand-curated publication list.

Three commands:

    add <arxiv-id | doi | recid>   fetch metadata, append a stub to publications.yml
    check [--fix]                  re-query existing entries, report drifted metadata
    stats [--write]                refresh paper and citation counts

INSPIRE is a metadata assistant and a linter here, never a source of entries.
`add` requires an identifier you chose; `check` only corrects entries already in the
file and never appends. See CLAUDE.md, "Core principle: the publication list is
HAND-CURATED".

The file is edited as TEXT, not round-tripped through a YAML dumper. publications.yml
carries a header comment, section dividers and VERIFY notes that a dump would silently
destroy, so every write here is a targeted line edit.

Depends only on the standard library plus PyYAML (for reading).
"""

from __future__ import annotations

import argparse
import json
import re
import ssl
import sys
import textwrap
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PUBLICATIONS = ROOT / "_data" / "publications.yml"
BASICS = ROOT / "_data" / "basics.yml"

API = "https://inspirehep.net/api"
UA = "kakwok.github.io-cv-pipeline (+https://github.com/kakwok/kakwok.github.io)"
TIMEOUT = 30

ARXIV_RE = re.compile(r"^\d{4}\.\d{4,5}(v\d+)?$|^[a-z-]+(\.[A-Z]{2})?/\d{7}$")
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")
RECID_RE = re.compile(r"^\d+$")


# --------------------------------------------------------------------------- fetch


def _ssl_context() -> ssl.SSLContext:
    """Some Python builds (MacPorts, python.org) ship no CA bundle, so every HTTPS
    request fails CERTIFICATE_VERIFY_FAILED. Fall back to certifi's bundle when the
    interpreter has none of its own. Never disables verification."""
    context = ssl.create_default_context()
    if ssl.get_default_verify_paths().cafile is None:
        try:
            import certifi
        except ImportError:
            raise SystemExit(
                "This Python has no CA certificate bundle, so HTTPS cannot be verified.\n"
                "Install one:  pip install certifi     (see scripts/requirements.txt)"
            )
        context.load_verify_locations(certifi.where())
    return context


def _get(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT, context=_ssl_context()) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            raise SystemExit(f"not found on INSPIRE: {url}")
        raise SystemExit(f"INSPIRE returned HTTP {error.code} for {url}")
    except urllib.error.URLError as error:
        raise SystemExit(f"could not reach INSPIRE ({error.reason}). Network allowed?")


def fetch_record(identifier: str) -> dict:
    """Resolve an arXiv id, DOI or recid to one INSPIRE literature record."""
    identifier = identifier.strip()
    if identifier.startswith("arXiv:"):
        identifier = identifier[len("arXiv:") :]
    if identifier.startswith("https://doi.org/"):
        identifier = identifier[len("https://doi.org/") :]

    if RECID_RE.match(identifier):
        endpoint = f"{API}/literature/{identifier}"
    elif ARXIV_RE.match(identifier):
        endpoint = f"{API}/arxiv/{identifier}"
    elif DOI_RE.match(identifier):
        endpoint = f"{API}/doi/{urllib.parse.quote(identifier, safe='')}"
    else:
        raise SystemExit(
            f"unrecognised identifier: {identifier!r}\n"
            "expected an arXiv id (2402.18658), a bare DOI (10.1103/...) or a recid."
        )

    payload = _get(endpoint)
    # /arxiv and /doi return a search-style envelope; /literature returns the record.
    if "hits" in payload.get("metadata", {}):
        hits = payload["metadata"]["hits"]["hits"]
        if not hits:
            raise SystemExit(f"no INSPIRE record for {identifier}")
        return hits[0]["metadata"]
    return payload["metadata"]


# --------------------------------------------------------------- metadata shaping


def pick_date(metadata: dict) -> str:
    """First-public date as YYYY-MM.

    `earliest_date` is a computed field INSPIRE returns on search results but NOT on the
    /literature, /arxiv or /doi record endpoints — and passing ?fields= does not bring it
    back. Fall through to the raw dates that are always present.
    """
    for key in ("earliest_date", "preprint_date", "legacy_creation_date"):
        value = metadata.get(key)
        if value:
            return str(value)[:7]
    for info in metadata.get("publication_info", []):
        if info.get("year"):
            return f"{info['year']}-01"  # month unknown; correct it by hand
    return ""


def space_journal(ref: str) -> str:
    """INSPIRE writes 'Phys.Rev.D 99'; this file uses the spaced form a reader expects."""
    return re.sub(r"\.(?=\S)", ". ", ref)


def format_ref(metadata: dict) -> str:
    """Build 'Phys. Rev. D 110 (2024) 012004', falling back to 'arXiv:xxxx.xxxxx'."""
    for info in metadata.get("publication_info", []):
        journal = space_journal(info.get("journal_title") or "")
        if not journal:
            continue
        volume = info.get("journal_volume", "")
        year = info.get("year", "")
        # page_start wins over artid: journals that paginate (Phys.Rept., Phys.Lett.B)
        # also carry the publisher's internal article number, and the page is what a
        # reader cites. Article-number journals (PRD, JHEP) supply artid only.
        page = info.get("page_start") or info.get("artid", "")
        ref = journal
        if volume:
            ref += f" {volume}"
        if year:
            ref += f" ({year})"
        if page:
            ref += f" {page}"
        return ref

    eprints = metadata.get("arxiv_eprints", [])
    if eprints:
        return f"arXiv:{eprints[0]['value']}"
    return ""


def format_authors(metadata: dict) -> str:
    collaborations = metadata.get("collaborations", [])
    if collaborations:
        return f"{collaborations[0]['value']} Collaboration"

    authors = metadata.get("authors", [])
    if not authors:
        return "TODO"
    # INSPIRE gives "Kwok, Ka Hei Martin"; the file uses "M. Kwok" / "M. Atif et al."
    surname, _, forenames = authors[0]["full_name"].partition(", ")
    initials = " ".join(f"{part[0]}." for part in forenames.split() if part)
    lead = f"{initials} {surname}".strip()
    return f"{lead} et al." if len(authors) > 1 else lead


def ref_changed(old: str | None, new: str) -> bool:
    """Has the citation really changed, or only INSPIRE's house style?

    INSPIRE writes 'Phys.Rev.D 99 (2019) 012005'; this file uses the spaced form a CV
    reader expects. Those are the same reference, and a linter that nags about it every
    month trains you to ignore it. Author annotations on preprint refs — 'arXiv:2203.09945
    (Snowmass 2021 contribution)' — are kept for the same reason.
    """
    if old is None:
        return True
    squashed = lambda text: re.sub(r"[\s.]", "", text).lower()
    if squashed(old) == squashed(new):
        return False
    if new.startswith("arXiv:") and old.startswith(new):
        return False
    return True


def shape(metadata: dict) -> dict:
    eprints = metadata.get("arxiv_eprints", [])
    dois = metadata.get("dois", [])
    return {
        "date": pick_date(metadata),
        "authors": format_authors(metadata),
        "title": metadata["titles"][0]["title"],
        "ref": format_ref(metadata),
        "arxiv": eprints[0]["value"] if eprints else None,
        "doi": dois[0]["value"] if dois else None,
        "inspire": metadata.get("control_number"),
    }


# ------------------------------------------------------------------ file handling


def load_entries() -> list[dict]:
    return yaml.safe_load(PUBLICATIONS.read_text()) or []


def entry_blocks(text: str) -> list[tuple[int, int]]:
    """Return (start, end) line spans for each top-level '- ' entry, comments included."""
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith("- ")]
    spans = []
    for position, start in enumerate(starts):
        end = starts[position + 1] if position + 1 < len(starts) else len(lines)
        # Trailing blank lines and any '# ---' divider belong to the next block.
        while end > start + 1 and (
            not lines[end - 1].strip() or lines[end - 1].startswith("#")
        ):
            end -= 1
        spans.append((start, end))
    return spans


def _render(value) -> str:
    """One-line YAML scalar. safe_dump emits a trailing '...' document-end marker for
    bare scalars, which must not land in the file as a second line."""
    if value is None:
        return "null"
    dumped = yaml.safe_dump(value, default_flow_style=True, width=10**6).strip()
    if dumped.endswith("\n..."):
        dumped = dumped[: -len("\n...")].strip()
    return dumped


def set_field(lines: list[str], span: tuple[int, int], field: str, value) -> bool:
    """Set `field:` inside one entry, in place.

    Replaces the value if the key exists, dropping any stale trailing comment on that
    line. If the key is absent — `inspire:` usually is, since entries are typed by hand —
    it is inserted just before `domain:`, which every entry has.
    """
    start, end = span
    pattern = re.compile(rf"^(\s*){field}:(?:\s.*)?$")
    for index in range(start, end):
        match = pattern.match(lines[index])
        if match:
            lines[index] = f"{match.group(1)}{field}: {_render(value)}"
            return True

    anchor = re.compile(r"^(\s*)domain:")
    for index in range(start, end):
        match = anchor.match(lines[index])
        if match:
            lines.insert(index, f"{match.group(1)}{field}: {_render(value)}")
            return True
    return False


# ----------------------------------------------------------------------- commands


def cmd_add(args: argparse.Namespace) -> int:
    record = shape(fetch_record(args.identifier))

    existing = load_entries()
    for entry in existing:
        same = (
            (record["inspire"] and entry.get("inspire") == record["inspire"])
            or (record["arxiv"] and entry.get("arxiv") == record["arxiv"])
            or (record["doi"] and entry.get("doi") == record["doi"])
        )
        if same:
            print(f"already in publications.yml: {entry['ref']}")
            return 1

    title = "\n".join(
        "    " + line for line in textwrap.wrap(record["title"], width=84)
    )
    arxiv = f'"{record["arxiv"]}"' if record["arxiv"] else "null"
    stub = f"""
- date: {record['date']}
  authors: {record['authors']}
  title: >-
{title}
  ref: {record['ref']}
  arxiv: {arxiv}
  doi: {record['doi'] or 'null'}
  inspire: {record['inspire']}
  domain: TODO               # physics | computing
  tags: [TODO]               # closed vocabulary — see schemas/publications.schema.json
"""

    with PUBLICATIONS.open("a") as handle:
        handle.write(stub)

    print(f"appended to {PUBLICATIONS.relative_to(ROOT)}:\n{stub}")
    print("Set `domain` and `tags`, then move it into the right section in date order.")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    text = PUBLICATIONS.read_text()
    lines = text.splitlines()
    spans = entry_blocks(text)
    entries = load_entries()

    if len(spans) != len(entries):
        raise SystemExit(
            f"parsed {len(entries)} entries but found {len(spans)} text blocks — "
            "publications.yml formatting is unusual; fix by hand."
        )

    problems = 0
    fixes = 0
    pending: list[tuple[tuple[int, int], str, object]] = []
    for entry, span in zip(entries, spans):
        identifier = entry.get("inspire") or entry.get("arxiv") or entry.get("doi")
        if not identifier:
            print(f"SKIP  {entry['ref']}\n      no arxiv, doi or inspire id to query")
            problems += 1
            continue

        try:
            current = shape(fetch_record(str(identifier)))
        except SystemExit as error:
            print(f"ERROR {entry['ref']}\n      {error}")
            problems += 1
            continue

        for field in ("ref", "doi", "inspire"):
            new = current[field]
            old = entry.get(field)
            if new in (None, ""):
                continue
            if field == "ref":
                if not ref_changed(old, new):
                    continue
            elif new == old:
                continue

            became_published = (
                field == "ref"
                and str(old).startswith("arXiv:")
                and not new.startswith("arXiv:")
            )
            label = "PUBLISHED" if became_published else "DRIFT"
            print(f"{label:9} {entry['title'][:60]}...")
            print(f"          {field}: {old!r} -> {new!r}")
            problems += 1

            if args.fix:
                pending.append((span, field, new))

    # Applied bottom-up: inserting a missing key shifts every line below it, which would
    # invalidate the spans of entries not yet patched.
    for span, field, value in sorted(pending, key=lambda item: item[0][0], reverse=True):
        if set_field(lines, span, field, value):
            fixes += 1
        else:
            print(f"could not locate or insert `{field}:` near line {span[0] + 1}")

    if args.fix and fixes:
        PUBLICATIONS.write_text("\n".join(lines) + "\n")
        print(f"\napplied {fixes} correction(s) to {PUBLICATIONS.relative_to(ROOT)}")
    elif problems and not args.fix:
        print("\nre-run with --fix to apply. `check` never adds or removes entries.")

    if not problems:
        print(f"all {len(entries)} entries match INSPIRE")
    return 1 if problems and not args.fix else 0


def cmd_stats(args: argparse.Namespace) -> int:
    basics = yaml.safe_load(BASICS.read_text())
    bai = (basics.get("links") or {}).get("inspire_bai")
    if not bai or bai == "TODO":
        raise SystemExit("set links.inspire_bai in _data/basics.yml first")

    papers = 0
    citations = 0
    page = 1
    while True:
        query = urllib.parse.urlencode(
            {
                "q": f"a {bai}",
                "fields": "citation_count",
                "size": 250,
                "page": page,
            }
        )
        payload = _get(f"{API}/literature?{query}")
        hits = payload["hits"]["hits"]
        papers = payload["hits"]["total"]
        citations += sum(h["metadata"].get("citation_count", 0) for h in hits)
        if page * 250 >= papers or not hits:
            break
        page += 1

    print(f"papers:    {papers}")
    print(f"citations: {citations}")
    # The profile link is keyed by recid; the BAI is a search handle, not a URL path.
    print(f"profile:   {(basics.get('links') or {}).get('inspire_author', '(set links.inspire_author)')}")

    if args.write:
        target = ROOT / "_data" / "inspire_stats.yml"
        target.write_text(
            "# GENERATED by scripts/inspire.py stats — do not edit by hand.\n"
            f"papers: {papers}\ncitations: {citations}\n"
        )
        print(f"\nwrote {target.relative_to(ROOT)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="inspire.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add = subparsers.add_parser("add", help="append a stub for one paper you chose")
    add.add_argument("identifier", help="arXiv id, bare DOI, or INSPIRE recid")
    add.set_defaults(func=cmd_add)

    check = subparsers.add_parser("check", help="report metadata that drifted")
    check.add_argument("--fix", action="store_true", help="apply the corrections")
    check.set_defaults(func=cmd_check)

    stats = subparsers.add_parser("stats", help="refresh paper and citation counts")
    stats.add_argument("--write", action="store_true", help="write _data/inspire_stats.yml")
    stats.set_defaults(func=cmd_stats)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
