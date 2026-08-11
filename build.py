#!/usr/bin/env python3
"""Render a CV variant from _data/ via RenderCV.

    ./build.py                     build every variant in variants/
    ./build.py academic            build one
    ./build.py academic --no-pdf   emit the RenderCV YAML only, skip rendering

    _data/*.yml  →  filter by variant  →  out/<variant>.rendercv.yaml  →  out/<variant>.pdf

_data/ is the single source of truth, read by Jekyll for the website and by this script
for the PDF, so the two cannot drift. A variant (variants/*.yml) is a section list with
tag filters — never content. See CLAUDE.md.

The CV header is DERIVED from the first `type: work` entry of experience.yml. It is not
stored anywhere else. The old hand-maintained CV kept the header affiliation separately
and it drifted a whole institution out of date; that bug is why this pipeline exists.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "_data"
VARIANTS = ROOT / "variants"
OUT = ROOT / "out"


def load(name: str) -> list | dict:
    path = DATA / f"{name}.yml"
    if not path.exists():
        return []
    return yaml.safe_load(path.read_text()) or []


# ------------------------------------------------------------------- filtering


def matches(entry: dict, spec: dict) -> bool:
    """AND over every *_any filter present in the section spec."""
    for key, field in (
        ("type_any", "type"),
        ("domain_any", "domain"),
        ("kind_any", "kind"),
    ):
        allowed = spec.get(key)
        if allowed and entry.get(field) not in allowed:
            return False

    allowed = spec.get("tags_any")
    if allowed and not set(entry.get("tags") or []) & set(allowed):
        return False
    return True


def sort_key(entry: dict):
    """Newest first. Entries use either `date` (YYYY-MM) or `start`/`end` (YYYY)."""
    if "date" in entry:
        return str(entry["date"])
    # Ongoing work sorts above finished work that started the same year.
    end = entry.get("end")
    return f"{entry.get('start', 0)}-{'9999' if end is None else end}"


def select(entries: list[dict], spec: dict) -> list[dict]:
    kept = [entry for entry in entries if matches(entry, spec)]
    kept.sort(key=sort_key, reverse=True)
    limit = spec.get("limit")
    return kept[:limit] if limit else kept


# ------------------------------------------------------- _data → RenderCV entries


GREEK = {
    "alpha": "α", "beta": "β", "gamma": "γ", "mu": "μ", "nu": "ν", "tau": "τ",
    "ell": "ℓ", "pi": "π", "sigma": "σ", "Lambda": "Λ", "Delta": "Δ",
}


def detex(text: str) -> str:
    """Turn the LaTeX fragments in _data/ into Unicode.

    RenderCV renders through Typst, which does not read LaTeX math, so `$\\sqrt{s}=13$`
    reaches the page verbatim. The same strings are read by Jekyll, where KaTeX handles
    them properly — so the source keeps LaTeX and only the PDF path converts.
    """
    if not isinstance(text, str) or "\\" not in text and "$" not in text:
        return text
    out = text
    out = re.sub(r"\\sqrt\{([^}]*)\}", r"√\1", out)
    out = re.sub(r"\\bar\{([^}]*)\}", lambda m: m.group(1) + "\u0304", out)
    out = re.sub(r"\\text(?:rm)?\{([^}]*)\}", r"\1", out)
    out = out.replace("\\to", "→").replace("\\rightarrow", "→")
    out = re.sub(r"\\(" + "|".join(GREEK) + r")\b", lambda m: GREEK[m.group(1)], out)
    out = out.replace("$", "")
    out = re.sub(r"\s*=\s*", " = ", out)
    out = re.sub(r"\s*→\s*", " → ", out)
    return re.sub(r"\s{2,}", " ", out).strip()


def years(entry: dict) -> dict:
    """A literal date string, not start_date/end_date.

    Our data has year precision only. RenderCV reads '2025' as January 2025 and prints
    'Jan 2025 – present', which asserts a month the source never claimed.
    """
    end = entry.get("end")
    return {"date": f"{entry['start']} – {'present' if end is None else end}"}


def as_education(entry: dict) -> dict:
    highlights = []
    if entry.get("advisor"):
        highlights.append(f"Advisor: {entry['advisor']}")
    if entry.get("thesis"):
        highlights.append(f"Thesis: {detex(entry['thesis'])}")
    return {
        "institution": entry["institution"],
        "area": entry["degree"],
        "degree": "",
        "location": entry.get("location"),
        "highlights": highlights,
        **years(entry),
    }


def as_experience(entry: dict) -> dict:
    company = entry["institution"]
    if entry.get("url"):
        company = f"[{company}]({entry['url']})"
    return {
        "company": company,
        "position": entry["position"],
        "location": entry.get("location"),
        **years(entry),
    }


def as_research(entry: dict) -> dict:
    return {
        "name": detex(entry["title"]),
        "highlights": [detex(h) for h in (entry.get("highlights") or [])],
        **years(entry),
    }


def as_award(entry: dict) -> dict:
    return {
        "name": entry["title"],
        "date": str(entry["date"]),
        "summary": entry.get("institution"),
    }


def as_teaching(entry: dict) -> dict:
    summary = entry.get("institution") or ""
    if entry.get("note"):
        summary = f"{summary}. {entry['note']}" if summary else entry["note"]
    name = entry["title"]
    if entry.get("url"):
        name = f"[{name}]({entry['url']})"
    return {"name": name, "summary": summary, **years(entry)}


def as_talk(entry: dict) -> dict:
    """Talks carry no `end`, so they use `date`, and the event goes in the summary."""
    name = detex(entry["title"])
    if entry.get("url"):
        name = f"[{name}]({entry['url']})"
    event = entry["event"]
    if entry.get("kind") in ("plenary", "poster", "seminar", "lecture"):
        event = f"{event} ({entry['kind']})"
    return {
        "name": name,
        "date": str(entry["date"]),
        "location": entry.get("location"),
        "summary": event,
    }


def as_publication(entry: dict) -> dict:
    url = None
    if entry.get("arxiv"):
        url = f"https://arxiv.org/abs/{entry['arxiv']}"
    return {
        "title": detex(entry["title"]),
        "authors": [entry["authors"]],
        "journal": entry["ref"],
        "doi": entry.get("doi"),
        "url": None if entry.get("doi") else url,
        "date": str(entry["date"]),
    }


BUILDERS = {
    "education": as_education,
    "experience": as_experience,
    "research": as_research,
    "awards": as_award,
    "teaching": as_teaching,
    "talks": as_talk,
    "publications": as_publication,
}


def publication_count_line() -> list[str]:
    """One line standing in for the hundreds of author-list papers this CV omits."""
    stats = load("inspire_stats") or {}
    basics = load("basics")
    profile = (basics.get("links") or {}).get("inspire_author")
    if not stats or not profile or profile == "TODO":
        return []
    return [
        f"Full publication list ({stats['papers']} papers, {stats['citations']} "
        f"citations): [INSPIRE-HEP]({profile})"
    ]


# ------------------------------------------------------------------ header block


def header(basics: dict, experience: list[dict]) -> dict:
    """Derive name/headline/location from experience — never from stored duplicates."""
    current = next((e for e in experience if e.get("type") == "work"), None)
    if current is None:
        raise SystemExit("experience.yml has no `type: work` entry to derive the header")

    contact = {
        "name": basics["name"],
        "headline": f"{current['position']}, {current['institution']}",
        "location": current.get("address") or current.get("location"),
    }

    email = basics.get("email")
    if email and email != "TODO" and "@" in str(email):
        contact["email"] = email
    if basics.get("phone"):
        contact["phone"] = basics["phone"]

    links = basics.get("links") or {}
    if links.get("website"):
        contact["website"] = links["website"]

    networks = []
    for network, value in (("GitHub", links.get("github")), ("LinkedIn", links.get("linkedin"))):
        if value and value != "TODO":
            networks.append({"network": network, "username": str(value).rstrip("/").split("/")[-1]})
    if networks:
        contact["social_networks"] = networks

    # ORCID and INSPIRE have no `social_networks` type; they ride along as plain links.
    extras = []
    if links.get("orcid") and links["orcid"] != "TODO":
        extras.append(f"[ORCID]({links['orcid']})")
    if links.get("inspire_author") and links["inspire_author"] != "TODO":
        extras.append(f"[INSPIRE]({links['inspire_author']})")
    return contact, extras


# ------------------------------------------------------------------------ build


def build(variant_name: str, render: bool) -> Path:
    spec_path = VARIANTS / f"{variant_name}.yml"
    if not spec_path.exists():
        raise SystemExit(f"no such variant: {spec_path.relative_to(ROOT)}")
    spec = yaml.safe_load(spec_path.read_text())

    sources = {name: load(name) for name in BUILDERS}
    basics = load("basics")
    contact, extras = header(basics, sources["experience"])

    sections: dict[str, list] = {}
    for section in spec["sections"]:
        title = section["title"]
        source = section["from"]

        if source == "publication_count":
            lines = publication_count_line()
            if lines:
                sections[title] = lines
            continue

        if source not in BUILDERS:
            raise SystemExit(f"variant {variant_name}: unknown source {source!r}")

        chosen = select(sources[source], section)
        if chosen:
            sections[title] = [BUILDERS[source](entry) for entry in chosen]

    if extras:
        sections["Identifiers"] = [" · ".join(extras)]

    document = {
        "cv": {**contact, "sections": sections},
        "design": {"theme": spec.get("theme", "classic"), **(spec.get("design") or {})},
    }

    OUT.mkdir(exist_ok=True)
    yaml_path = OUT / f"{variant_name}.rendercv.yaml"
    yaml_path.write_text(
        f"# GENERATED by build.py from _data/ + variants/{variant_name}.yml — do not edit.\n"
        + yaml.safe_dump(document, sort_keys=False, allow_unicode=True, width=100)
    )
    counts = ", ".join(f"{title}: {len(rows)}" for title, rows in sections.items())
    print(f"{variant_name}: {yaml_path.relative_to(ROOT)}\n  {counts}")

    if render:
        render_pdf(variant_name, yaml_path, spec.get("max_pages"))
    return yaml_path


def render_pdf(variant_name: str, yaml_path: Path, max_pages: int | None) -> None:
    rendercv = shutil.which("rendercv") or str(ROOT / ".venv" / "bin" / "rendercv")
    pdf = OUT / f"{variant_name}.pdf"
    result = subprocess.run(
        [
            rendercv, "render", str(yaml_path),
            "--output-folder", str(OUT / "_rendercv" / variant_name),
            "--pdf-path", str(pdf),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        sys.stderr.write(result.stdout + result.stderr)
        raise SystemExit(f"rendercv failed for {variant_name}")
    if not pdf.exists():
        raise SystemExit(f"rendercv produced no PDF for {variant_name}")
    shutil.rmtree(OUT / "_rendercv", ignore_errors=True)

    pages = count_pages(pdf)
    note = ""
    if max_pages and pages > max_pages:
        note = f"  ** over max_pages ({max_pages}) — tighten the variant's filters **"
    print(f"  {pdf.relative_to(ROOT)} ({pages} page{'s' if pages != 1 else ''}){note}")


def count_pages(pdf: Path) -> int:
    return len(re.findall(rb"/Type\s*/Page[^s]", pdf.read_bytes()))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("variants", nargs="*", help="variant names; default is all of them")
    parser.add_argument("--no-pdf", action="store_true", help="emit RenderCV YAML only")
    args = parser.parse_args()

    names = args.variants or sorted(path.stem for path in VARIANTS.glob("*.yml"))
    if not names:
        raise SystemExit("no variants found in variants/")
    for name in names:
        build(name, render=not args.no_pdf)
    return 0


if __name__ == "__main__":
    sys.exit(main())
