#!/usr/bin/env bash
# Stop hook — measures the compaction caps of the indexes. The skills run it too,
# right after they write an index: a Stop hook's output doesn't reach the model.
#
# Why it exists: a cap written as a sentence inside a skill holds when the rule
# shapes ONE line written from scratch (a log.md entry), and fails when it asks
# to EVICT from a file that keeps growing (an index): eviction is a second,
# costly action, and it gets skipped.
#
# So this hook doesn't repeat the rule: it REPORTS THE MEASURE. That's the
# difference. It doesn't block (no exit 2), like HOT_CACHE_REMINDER.

# The root is resolved with git, so the hook works from a session started in
# any subfolder.
ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
cd "$ROOT" 2>/dev/null || exit 0

# Outside the meta-layer -> exit silently.
[ -f INDEX.md ] && [ -f hot.md ] || exit 0

# An index not touched in this session -> no noise. The commits of the last
# 3 hours count too: /end-session commits in the same turn, so at Stop the diff
# is already empty.
TOUCHED=$({ git diff --name-only HEAD 2>/dev/null; git log --since=3.hours --name-only --format= 2>/dev/null; })

if printf '%s\n' "$TOUCHED" | grep -qx 'INDEX.md'; then
awk '
BEGIN {
  # Caps — the only place they are enforced. Keep them in sync with
  # .claude/CLAUDE.md §"Compaction"; the keys are the "## " titles of INDEX.md.
  cap["Daily logs"] = 14
  cap["Decisions (top-5 recent)"] = 5
  cap["Recently ingested"] = 14
  GLOSS_MAX = 25       # words per entry
  FILE_MAX  = 30720    # 30 KB
  nsec = 0
}
/^## / {
  sec = substr($0, 4)
  sub(/[ \t]+$/, "", sec)
  if (!(sec in seen)) { seen[sec] = 1; order[++nsec] = sec }
  next
}
/^[ \t]*[-*] / {
  if (sec == "") next
  n[sec]++
  # Count the words of the READABLE gloss: wikilink targets cost nothing
  # (a file name with spaces would count as prose otherwise).
  line = $0
  gsub(/\[\[[^]|]*\|/, "", line)   # [[path|label]] -> label]]
  gsub(/\[\[|\]\]/,   "", line)    # leftover [[ ]]
  gsub(/^[ \t]*[-*][ \t]*/, "", line)
  gsub(/^[ \t]+|[ \t]+$/, "", line)
  w = (line == "") ? 0 : split(line, _tmp, /[ \t]+/)
  if (w > GLOSS_MAX) { over[sec]++; if (w > maxw[sec]) maxw[sec] = w }
}
END {
  nviol = 0
  for (i = 1; i <= nsec; i++) {
    s = order[i]
    if (!(s in cap)) continue
    bad_count = (n[s] > cap[s])
    bad_gloss = (over[s] > 0)
    if (!bad_count && !bad_gloss) continue
    line = "  · ## " s ": " n[s] " entries (cap " cap[s] ")"
    if (bad_gloss) line = line " — " over[s] " glosses >" GLOSS_MAX " words, max " maxw[s]
    msg[++nviol] = line
  }

  size = 0
  while ((getline l < "INDEX.md") > 0) size += length(l) + 1
  close("INDEX.md")
  bad_size = (size > FILE_MAX)

  if (nviol == 0 && !bad_size) exit 0

  print "INDEX_CAPS_REMINDER: INDEX.md is over its compaction caps (.claude/CLAUDE.md §\"Compaction\")."
  for (i = 1; i <= nviol; i++) print msg[i]
  if (bad_size) printf "  · file: %d B (cap %d B)\n", size, FILE_MAX
  print "Evict the entries over the cap (an evicted entry LEAVES, it is not shortened) and bring every"
  print "gloss back to 1 line <=" GLOSS_MAX " words. The evicted content already lives in the daily/,"
  print "decisions/ and raw/ pages it links to: check that first, then cut."
}
' INDEX.md
fi

# Sub-indexes with one row per page (people/INDEX.md, every */initiatives/INDEX.md):
# the last cell of a row is a pointer — status or date, source, one sentence. Left
# unmeasured it turns into a journal: each update is appended to the cell instead of
# replacing it, and the index ends up copying the pages it points to.
last_cell() {   # file
awk -v file="$1" '
BEGIN { MAX = 30; over = 0; maxw = 0 }   # 30 = status/date + source + a 20-word sentence
index($0, "| [[") == 1 {
  cell = $0
  sub(/[ \t]*\|[ \t]*$/, "", cell)                                  # the closing |
  while (match(cell, /[^\\]\|/)) cell = substr(cell, RSTART + 2)   # after the last unescaped |
  gsub(/\[\[[^]|]*\|/, "", cell); gsub(/\[\[|\]\]/, "", cell)      # link targets cost nothing
  gsub(/^[ \t]+|[ \t]+$/, "", cell)
  w = (cell == "") ? 0 : split(cell, t, /[ \t]+/)
  if (w > MAX) { over++; if (w > maxw) maxw = w }
}
END {
  if (over == 0) exit 0
  print "INDEX_CAPS_REMINDER: " file " — " over " rows whose last cell is over " MAX " words (max " maxw ")."
  print "The cell holds status or date, source and one sentence of at most 20 words: replace it, do not append. The history lives in the page."
}
' "$1"
}
printf '%s\n' "$TOUCHED" | grep -E '^(people|.+/initiatives)/INDEX\.md$' | sort -u | while IFS= read -r f; do
  [ -f "$f" ] && last_cell "$f"
done

# decisions/INDEX.md is a full catalog, so it only grows. Over the cap the oldest
# month leaves: its rows move unchanged to decisions/_archive/INDEX.md.
DEC_MAX=56320    # 55 KB
if printf '%s\n' "$TOUCHED" | grep -qx 'decisions/INDEX.md' && [ -f decisions/INDEX.md ]; then
  size=$(wc -c < decisions/INDEX.md | tr -d ' ')
  if [ "$size" -gt "$DEC_MAX" ]; then
    echo "INDEX_CAPS_REMINDER: decisions/INDEX.md — $size B (cap $DEC_MAX B)."
    echo "Move the oldest month to the archive: python3 .claude/tools/archive-decisions.py YYYY-MM for a dry run, then with --write."
  fi
fi

exit 0
