#!/usr/bin/env python3
"""lint-scan — structural scanner of the wiki (read-only).

NOT a runtime hook (it isn't in settings.json): it's the **measuring tool** of
the `/lint` skill, run by its Step 1. It lives in `.claude/` because that's
the schema layer, and it's committed because a scratchpad is per-session: a
scanner left there is gone by the next lint, which then re-derives the same
false positives from scratch and reports an inflated first measure.
If a check asks for an extra action, a mechanism measures it — prose that
recommends it isn't enough.

Usage:
    python3 .claude/hooks/lint-scan.py            # readable report
    python3 .claude/hooks/lint-scan.py --json     # structured dump on stdout
    python3 .claude/hooks/lint-scan.py --only links,seed

Checks covered (numbering of the /lint skill):
    1  orphans            2  broken wikilinks    3  frontmatter/type
    10 stagnant seeds     11 open callouts
    +  hypothesis decay · hot.md caps · lessons.md words
Checks 4-9 need judgment: they stay in the skill.

⚠️ The scanner sees STRUCTURE, not merit. It doesn't judge whether a claim is
true or whether a [!gap] matters.
"""

import argparse
import datetime
import json
import os
import re
import statistics
import subprocess
import sys
from collections import defaultdict

VAULT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
TODAY = datetime.date.today()

# ─────────────────────────────────────────────────────────────────────────────
# PERIMETER — exclusions are constants, not command lines rewritten each time.
# Each entry here is a family of false positives.
# ─────────────────────────────────────────────────────────────────────────────

EXCLUDED_TOP = {"raw"}                     # immutable inbox: read, never linted
EXCLUDED_DIR_NAMES = {                     # wherever they appear in the path
    "_archive",                            # frozen history
    "node_modules",
    ".venv", "venv", "__pycache__",
}
# Nested git repos (folders with their own .git, e.g. a macro area that is its
# own repo) are self-contained trees, not wiki pages.
EXCLUDE_NESTED_GIT = True
# Hidden folders (.claude/, .obsidian/): tooling, not wiki.
EXCLUDE_HIDDEN_DIRS = True
# Gitignored files and folders (exports, tmp/, lint-report.md): not wiki pages.
EXCLUDE_GITIGNORED = True

# Sources whose wikilinks are SYNTAX EXAMPLES, not real links.
DOC_SOURCES = re.compile(
    r"(^|/)(CLAUDE|README|MEMORY|SKILL)\.md$"
    r"|_template"
    r"|^lint-report\.md$"
)

# Targets that are syntax placeholders, not missing files.
# ⚠ Applied ONLY to targets that don't resolve: a file that exists and is named
# "…slug…" must not be discarded.
PLACEHOLDER = re.compile(r"\{[^}]*\}|YYYY|Www\b|HH:MM|\.\.\.", re.IGNORECASE)

ORPHAN_EXEMPT = re.compile(r"(^|/)(INDEX|README|MEMORY|CLAUDE)\.md$|_template", re.I)

# Orphans in these areas get a ⚠ in the report; the others are listed plainly.
WIKI_AREAS = re.compile(r"^(daily|weekly|decisions|people|knowledge|plans|log)/|/initiatives/")

# Frontmatter — the `type:` enum of ../CLAUDE.md §4. `.claude/memory/` has its
# own schema and is out of the perimeter anyway (hidden folder).
VALID_TYPES = {
    "decision", "knowledge", "hypothesis", "rule", "person",
    "initiative", "daily", "weekly", "plan", "client", "meta", "lessons", "log",
    "log-archive", "lint-report",
}
FM_EXEMPT = re.compile(r"(^|/)(CLAUDE|README|MEMORY|SKILL)\.md$")

# Date fields per page. ⚑ people/ uses `last-interaction`, weekly/ uses
# `date-end`: a lint that looks only for `updated` sees them all as undated.
DATE_FIELDS = ("updated", "created", "date", "last-interaction", "date-end", "generated")

# Thresholds
SEED_STALE_DAYS = 30      # /lint check 10
HYPO_STALE_DAYS = 90      # decay: 1/3 stuck for >90 days → a person decides whether to demote it
HOT_TOTAL_WORDS = 700     # ../CLAUDE.md §4bis
LESSONS_CAP = 3000        # words of lessons.md: measures, doesn't block
# Per-section caps of hot.md, from ../CLAUDE.md §4bis.
# (bullet_max, words_per_bullet | None, words_total | None)
HOT_SECTION_CAPS = {
    "Key Recent Facts": (5, 60, None),
    "Recent Changes": (3, None, None),
    "Active Threads": (4, None, None),
    "Open Patterns / Hypotheses": (None, None, 60),
}

# ─────────────────────────────────────────────────────────────────────────────
# Parsing
# ─────────────────────────────────────────────────────────────────────────────

# A target may contain single '[' and ']' (e.g. "[PRD]" in a file name) but not ']]'.
WIKILINK = re.compile(r"!?\[\[((?:[^\[\]]|\[(?!\[)|\](?!\]))+?)\]\]")
FENCE = re.compile(r"^(```|~~~)")
INLINE_CODE = re.compile(r"(`+).*?\1")        # matched backtick runs
FM_BLOCK = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
FM_LINE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$")
ISO_DATE = re.compile(r"(\d{4}-\d{2}-\d{2})")
# Only real callouts: lines starting with `>` (nested too). A quote in running
# text or in a table cell is not a callout.
CALLOUT_LINE = re.compile(r"^\s*(?:>\s*)+\[!(gap|contradiction)\]", re.M)


def find_nested_git(root):
    """Folders (relative) that contain their own .git. The root doesn't count."""
    nested = set()
    for dirpath, dirnames, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        if rel == ".":
            if ".git" in dirnames:
                dirnames.remove(".git")
            continue
        if ".git" in dirnames or ".git" in filenames:
            nested.add(rel)
            dirnames[:] = []          # no recursion inside a nested repo
            continue
        if ".git" in dirnames:
            dirnames.remove(".git")
    return nested


# Folders that can't be a wikilink target: kept out of the resolution index too
# (otherwise thousands of files, and a [[README]] that resolves at random).
# ⚠ Nested repos and _archive/ STAY in the index: they're out of the perimeter
# as *pages*, but they're legitimate link targets.
NEVER_A_TARGET = {".git", "node_modules", ".venv", "venv", "__pycache__",
                  ".next", "dist", "vendor", ".pytest_cache", ".ruff_cache"}


def find_gitignored(root):
    """Gitignored untracked paths (folders end with /). Without git: empty."""
    if not EXCLUDE_GITIGNORED:
        return set()
    try:
        out = subprocess.run(
            ["git", "ls-files", "-z", "-oi", "--exclude-standard", "--directory"],
            cwd=root, capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return set()
    return {p for p in out.decode("utf-8", "replace").split("\0") if p}


def list_disk_files(root, nested_git):
    """Every file on disk (non-.md too: they're legitimate link targets)."""
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in NEVER_A_TARGET]
        rel_root = os.path.relpath(dirpath, root)
        rel_root = "" if rel_root == "." else rel_root
        for fn in filenames:
            out.append(os.path.join(rel_root, fn) if rel_root else fn)
    return out


def in_perimeter(rel, nested_git, ignored=frozenset()):
    parts = rel.split(os.sep)
    if parts[0] in EXCLUDED_TOP:
        return False
    if any(p in EXCLUDED_DIR_NAMES for p in parts):
        return False
    if EXCLUDE_HIDDEN_DIRS and any(p.startswith(".") for p in parts[:-1]):
        return False
    if EXCLUDE_NESTED_GIT:
        d = os.path.dirname(rel)
        while d:
            if d in nested_git:
                return False
            d = os.path.dirname(d)
    if ignored and (rel in ignored or any(
            rel.startswith(i) for i in ignored if i.endswith("/"))):
        return False
    return True


def extract_links(text):
    """(line, target) of the wikilinks outside fences and inline code.

    Obsidian doesn't render as a link what sits in `backticks`: counting those
    is a classic false positive.
    """
    in_fence = False
    for ln, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line.strip()):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for m in WIKILINK.finditer(INLINE_CODE.sub("", line)):
            inner = m.group(1)
            # escaped pipe (\|) in tables: without this the \ ends up in the path
            target = re.split(r"\\\||\|", inner, maxsplit=1)[0]
            target = re.split(r"[#^]", target, maxsplit=1)[0].strip().strip("/")
            if target:
                yield ln, target


def parse_frontmatter(text):
    m = FM_BLOCK.match(text)
    if not m:
        return False, {}
    fm = {}
    for line in m.group(1).split("\n"):
        mm = FM_LINE.match(line)
        if mm:
            fm[mm.group(1)] = mm.group(2).strip().strip("\"'")
    return True, fm


def first_date(fm):
    """(date, field) from the first populated date field. See DATE_FIELDS."""
    for k in DATE_FIELDS:
        v = fm.get(k)
        if not v:
            continue
        m = ISO_DATE.search(str(v))
        if m:
            try:
                return datetime.date.fromisoformat(m.group(1)), k
            except ValueError:
                pass
    return None, None


def strip_code(text):
    """Text without fences or inline code — to count only callouts actually used."""
    out, in_fence = [], False
    for line in text.splitlines():
        if FENCE.match(line.strip()):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(INLINE_CODE.sub("", line))
    return "\n".join(out)


# ─────────────────────────────────────────────────────────────────────────────
# Checks
# ─────────────────────────────────────────────────────────────────────────────

def build_index(disk_files):
    by_path, by_base = {}, defaultdict(list)
    for f in disk_files:
        noext = f[:-3] if f.lower().endswith(".md") else f
        by_path[noext.lower()] = f
        by_path[f.lower()] = f
        by_base[os.path.basename(noext).lower()].append(f)
    return by_path, by_base


def resolve(target, by_path, by_base, disk_files):
    t = target.strip().strip("/")
    if not t:
        return []
    tn = t.lower()
    if tn in by_path:
        return [by_path[tn]]
    if tn + ".md" in by_path:
        return [by_path[tn + ".md"]]
    base = os.path.basename(tn)
    if base in by_base:
        return list(by_base[base])
    # Obsidian "shortest path" link: tail of the path
    suffix = "/" + t
    hits = [p for p in disk_files if p.endswith(suffix) or p.endswith(suffix + ".md")]
    return hits


def scan(root):
    nested_git = find_nested_git(root)
    disk_files = list_disk_files(root, nested_git)
    by_path, by_base = build_index(disk_files)
    ignored = find_gitignored(root)

    pages = sorted(f for f in disk_files
                   if f.lower().endswith(".md") and in_perimeter(f, nested_git, ignored))

    contents = {}
    for p in pages:
        try:
            with open(os.path.join(root, p), encoding="utf-8", errors="replace") as fh:
                contents[p] = fh.read()
        except OSError as e:
            contents[p] = ""
            print(f"READ ERROR {p}: {e}", file=sys.stderr)

    res = {
        "meta": {
            "vault": root,
            "today": str(TODAY),
            "pages_in_perimeter": len(pages),
            "files_on_disk": len(disk_files),
            "nested_git_repos": sorted(nested_git),
        }
    }

    # ── 2. wikilinks ─────────────────────────────────────────────────────────
    inbound = defaultdict(set)
    broken, placeholders, doc_examples = defaultdict(list), defaultdict(list), defaultdict(list)
    n_links = 0
    for src in pages:
        is_doc = bool(DOC_SOURCES.search(src))
        for ln, target in extract_links(contents[src]):
            hits = resolve(target, by_path, by_base, disk_files)
            if hits:
                n_links += 1
                for h in hits:
                    if h != src:
                        inbound[h].add(src)
                continue
            where = (src, ln)
            if PLACEHOLDER.search(target):
                placeholders[target].append(where)
            elif is_doc:
                doc_examples[target].append(where)
            else:
                n_links += 1
                broken[target].append(where)

    res["links"] = {
        "resolved": n_links - sum(len(v) for v in broken.values()),
        "evaluated": n_links,
        "broken": {k: v for k, v in sorted(broken.items())},
        "placeholders_skipped": {k: len(v) for k, v in sorted(placeholders.items())},
        "doc_examples_skipped": {k: len(v) for k, v in sorted(doc_examples.items())},
    }

    # ── 1. orphans ───────────────────────────────────────────────────────────
    orphans = [p for p in pages if not inbound.get(p) and not ORPHAN_EXEMPT.search(p)]
    res["orphans"] = {
        "wiki_areas": [o for o in orphans if WIKI_AREAS.search(o)],
        "other": [o for o in orphans if not WIKI_AREAS.search(o)],
    }

    # ── 3. frontmatter / type ────────────────────────────────────────────────
    no_fm, bad_type, fms = [], [], {}
    for p in pages:
        if FM_EXEMPT.search(p):
            continue
        present, fm = parse_frontmatter(contents[p])
        fms[p] = fm
        if not present:
            no_fm.append(p)
            continue
        t = fm.get("type", "")
        if not t:
            no_fm.append(p + "  (frontmatter without type:)")
        elif t not in VALID_TYPES:
            bad_type.append((p, t))
    res["frontmatter"] = {"missing": no_fm, "unknown_type": bad_type}

    # ── 10. stagnant seeds ───────────────────────────────────────────────────
    seed = []
    for p, fm in fms.items():
        if fm.get("status") != "seed":
            continue
        d, field = first_date(fm)
        age = (TODAY - d).days if d else None
        if age is None or age > SEED_STALE_DAYS:
            seed.append({"page": p, "age_days": age, "date": str(d), "date_field": field})
    res["seed_stale"] = sorted(seed, key=lambda x: -(x["age_days"] or 9999))

    # ── 11. open callouts ────────────────────────────────────────────────────
    live, historical = [], []
    for p in pages:
        # they document the syntax, they don't use it. ⚑ A README with
        # frontmatter is a real page: its callouts count.
        if DOC_SOURCES.search(p) and not (
                os.path.basename(p) == "README.md" and FM_BLOCK.match(contents[p])):
            continue
        kinds = CALLOUT_LINE.findall(strip_code(contents[p]))
        g, c = kinds.count("gap"), kinds.count("contradiction")
        if not (g or c):
            continue
        row = {"page": p, "gap": g, "contradiction": c}
        # daily/decisions/weekly/log = historical record: the gap is *part* of
        # the snapshot, not a question still open. Only live pages are actionable.
        (historical if p.startswith(("daily/", "decisions/", "weekly/", "log/"))
         else live).append(row)
    res["callouts"] = {
        "live": sorted(live, key=lambda r: -(r["gap"] + r["contradiction"])),
        "historical": sorted(historical, key=lambda r: r["page"]),
    }

    # ── hypotheses: counts and age of the last confirmation ──────────────────
    res["hypotheses"] = scan_hypotheses(root)

    # ── hot.md: caps of ../CLAUDE.md §4bis ───────────────────────────────────
    res["hot"] = scan_hot(root)

    # ── lessons.md: total words ──────────────────────────────────────────────
    lp = os.path.join(root, "lessons.md")
    if os.path.isfile(lp):
        words = len(open(lp, encoding="utf-8", errors="replace").read().split())
        res["lessons"] = {"words": words, "cap": LESSONS_CAP}

    return res


def scan_hypotheses(root):
    """n/3 count and age of the last confirmation for every hypothesis.

    What matters is not the file's length (punishing richness is wrong) but its
    TAIL: the 1/3 stuck for months and the 2/3 one confirmation away from
    promotion. Measured here instead of recommended in prose.

    Markers (.claude/CLAUDE.md §Knowledge System):
      - a confirmation bullet that says "does NOT count" keeps its date out
        of the count (e.g. two cases from the same call count as one);
      - a promoted hypothesis says "PROMOTED" in its heading, or "promoted to
        rule" on its Confirmations line.
    """
    out, base = [], os.path.join(root, "knowledge")
    domains = sorted(os.listdir(base)) if os.path.isdir(base) else []
    for domain in domains:
        path = os.path.join(base, domain, "hypotheses.md")
        if not os.path.isfile(path):
            continue
        text = open(path, encoding="utf-8", errors="replace").read()
        parts = re.split(r"(?m)^(#{2,3} .*)$", text)
        for i in range(1, len(parts), 2):
            header, body = parts[i], parts[i + 1] if i + 1 < len(parts) else ""
            if "Hypothesis" not in header:
                continue
            m = re.search(r"Confirmations:?\**:? *(\d+)/3", body)
            count = int(m.group(1)) if m else None
            dates = []
            if m:
                # ⚠ Start from the line AFTER the match: in the bold format
                # (`**Confirmations: 2/3**`) the match ends before the closing
                # `**`, and reading from m.end() would stop the loop at its
                # first step and drop EVERY date.
                for line in body[m.end():].split("\n")[1:]:
                    s = line.strip()
                    if s.startswith("-"):
                        dm = ISO_DATE.search(s)
                        if dm and "NOT count" not in s:
                            try:
                                dates.append(datetime.date.fromisoformat(dm.group(1)))
                            except ValueError:
                                pass
                    elif s and not s.startswith(("*(", "~~", ">")):
                        break
            last = max(dates) if dates else None
            conf_line = body[m.start():m.end() + 200].split("\n")[0] if m else ""
            promoted = "PROMOTED" in header or "promoted to rule" in conf_line
            out.append({
                "domain": domain,
                "title": header.lstrip("#").strip()[:90],
                "count": count,
                "n_confirmations_listed": len(dates),
                "last": str(last) if last else None,
                "age_days": (TODAY - last).days if last else None,
                "promoted": promoted,
                # tombstone with a stale counter: promoted, but the line says <3
                "stale_tombstone": bool(promoted and count is not None and count < 3),
            })
    active = [h for h in out if not h["promoted"]]
    ages = [h["age_days"] for h in active if h["age_days"] is not None]
    return {
        "total": len(out),
        "active": len(active),
        "median_age_days": statistics.median(ages) if ages else None,
        "stale_1of3": sorted(
            [h for h in active if h["count"] == 1 and (h["age_days"] or 0) > HYPO_STALE_DAYS],
            key=lambda h: -(h["age_days"] or 0)),
        "near_promotion_2of3": sorted(
            [h for h in active if h["count"] == 2],
            key=lambda h: -(h["age_days"] or 0)),
        "stale_tombstones": [h for h in out if h["stale_tombstone"]],
        "items": out,
    }


def scan_hot(root):
    path = os.path.join(root, "hot.md")
    if not os.path.isfile(path):
        return {}
    text = open(path, encoding="utf-8", errors="replace").read()
    present, fm = parse_frontmatter(text)
    updated = fm.get("updated", "")
    sections = []
    for s in re.split(r"^## ", text, flags=re.M)[1:]:
        name = s.splitlines()[0].strip()
        body = s[len(name):]
        bullets = [ln for ln in body.splitlines() if ln.startswith("- ")]
        # tolerant match: real titles may carry emoji or variants
        cap_key = next((k for k in HOT_SECTION_CAPS
                        if k.lower() in name.lower() or name.lower() in k.lower()), None)
        n_max, w_bullet, w_total = HOT_SECTION_CAPS.get(cap_key, (None, None, None))
        words_total = len(body.split())
        sections.append({
            "section": name,
            "bullets": len(bullets),
            "bullets_cap": n_max,
            "over_bullet_count": bool(n_max and len(bullets) > n_max),
            "words": words_total,
            "words_cap": w_total,
            "over_words_total": bool(w_total and words_total > w_total),
            "over_cap": ([{"words": len(b.split()), "text": b[:70]}
                          for b in bullets if len(b.split()) > w_bullet]
                         if w_bullet else []),
        })
    return {
        "words": len(text.split()),
        "cap": HOT_TOTAL_WORDS,
        # ⛔ updated: only YYYY-MM-DD, never a chain of sessions (../CLAUDE.md §4bis)
        "updated_is_single_date": bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", updated.strip())),
        "updated_raw": updated,
        "sections": sections,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Report
# ─────────────────────────────────────────────────────────────────────────────

def report(res, only=None):
    def want(k):
        return not only or k in only

    m = res["meta"]
    print(f"PERIMETER: {m['pages_in_perimeter']} pages "
          f"({m['files_on_disk']} files on disk) · {m['today']}")
    print(f"  nested git repos excluded: {len(m['nested_git_repos'])} "
          f"{m['nested_git_repos'] if m['nested_git_repos'] else ''}")

    if want("links"):
        L = res["links"]
        nb_t = len(L["broken"])
        nb_o = sum(len(v) for v in L["broken"].values())
        print(f"\n=== 2. WIKILINKS — {L['evaluated']} evaluated, {L['resolved']} resolved ===")
        print(f"    broken: {nb_t} targets / {nb_o} occurrences")
        for t, occ in L["broken"].items():
            print(f"  [[{t}]]  ({len(occ)} occ)")
            for f, ln in occ:
                print(f"     - {f}:{ln}")
        print(f"    skipped: {len(L['placeholders_skipped'])} placeholders · "
              f"{len(L['doc_examples_skipped'])} examples in docs/templates")

    if want("orphans"):
        O = res["orphans"]
        print(f"\n=== 1. ORPHANS — {len(O['wiki_areas'])} in wiki areas, "
              f"{len(O['other'])} elsewhere ===")
        for o in O["wiki_areas"]:
            print(f"  ⚠ {o}")
        for o in O["other"]:
            print(f"    {o}")

    if want("frontmatter"):
        F = res["frontmatter"]
        print(f"\n=== 3. FRONTMATTER — {len(F['missing'])} missing, "
              f"{len(F['unknown_type'])} unknown types ===")
        for x in F["missing"]:
            print(f"  {x}")
        for f, t in F["unknown_type"]:
            print(f"  {f} -> type: {t}")

    if want("seed"):
        S = res["seed_stale"]
        print(f"\n=== 10. STAGNANT SEEDS (>{SEED_STALE_DAYS}d) — {len(S)} ===")
        for s in S:
            age = f"{s['age_days']}d" if s["age_days"] is not None else "undated"
            where = f"  [{s['date_field']}={s['date']}]" if s["date_field"] else ""
            print(f"  {age:>8}  {s['page']}{where}")

    if want("callouts"):
        C = res["callouts"]
        live_occ = sum(r["gap"] + r["contradiction"] for r in C["live"])
        hist_occ = sum(r["gap"] + r["contradiction"] for r in C["historical"])
        print(f"\n=== 11. OPEN CALLOUTS — {len(C['live'])} live pages "
              f"({live_occ} occ) · {len(C['historical'])} historical ({hist_occ} occ) ===")
        for r in C["live"]:
            bits = []
            if r["gap"]:
                bits.append(f"gap x{r['gap']}")
            if r["contradiction"]:
                bits.append(f"contradiction x{r['contradiction']}")
            print(f"  {r['page']}  -> {', '.join(bits)}")

    if want("hypotheses"):
        H = res["hypotheses"]
        med = H["median_age_days"]
        print(f"\n=== HYPOTHESES — {H['active']} active of {H['total']} · "
              f"median last confirmation {f'{med}d' if med is not None else 'n/a'} ===")
        print(f"  ⚠ 1/3 stuck for >{HYPO_STALE_DAYS}d (demote to knowledge.md? a person decides): "
              f"{len(H['stale_1of3'])}")
        for h in H["stale_1of3"]:
            print(f"     {h['age_days']:>4}d  [{h['domain']}]  {h['title'][:70]}")
        print(f"  → 2/3, one confirmation from promotion: {len(H['near_promotion_2of3'])}")
        for h in H["near_promotion_2of3"]:
            age = f"{h['age_days']}d" if h["age_days"] is not None else "undated"
            print(f"     {age:>8}  [{h['domain']}]  {h['title'][:70]}")
        if H["stale_tombstones"]:
            print(f"  ⚠ tombstones with a stale counter: {len(H['stale_tombstones'])}")
            for h in H["stale_tombstones"]:
                print(f"     {h['count']}/3 but promoted  [{h['domain']}]  {h['title'][:70]}")

    if want("hot"):
        h = res.get("hot") or {}
        if h:
            flag = "✅" if h["words"] <= h["cap"] else "⚠"
            print(f"\n=== hot.md — {h['words']} words / cap {h['cap']} {flag} ===")
            if not h["updated_is_single_date"]:
                print(f"  ⛔ updated: is not a single date → {h['updated_raw']!r}")
            for s in h["sections"]:
                if s["over_bullet_count"]:
                    print(f"  ⚠ [{s['section']}] {s['bullets']} bullets "
                          f"(cap {s['bullets_cap']})")
                if s["over_words_total"]:
                    print(f"  ⚠ [{s['section']}] {s['words']} words "
                          f"(cap {s['words_cap']})")
                for b in s["over_cap"]:
                    print(f"  ⚠ [{s['section']}] bullet at {b['words']} words: {b['text']}…")

    if want("lessons"):
        ls = res.get("lessons") or {}
        if ls:
            flag = "✅" if ls["words"] <= ls["cap"] else "⚠"
            print(f"\n=== lessons.md — {ls['words']} words / cap {ls['cap']} {flag} ===")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true", help="structured dump on stdout")
    ap.add_argument("--only", default="", help="checks to print, comma-separated "
                                               "(links,orphans,frontmatter,seed,callouts,"
                                               "hypotheses,hot,lessons)")
    ap.add_argument("--vault", default=VAULT)
    args = ap.parse_args()

    res = scan(os.path.abspath(args.vault))
    if args.json:
        json.dump(res, sys.stdout, indent=1, ensure_ascii=False, default=str)
        print()
    else:
        report(res, {s.strip() for s in args.only.split(",") if s.strip()})


if __name__ == "__main__":
    main()
