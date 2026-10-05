#!/usr/bin/env bash
# Stop hook — measures the compaction caps of INDEX.md.
#
# Why it exists: a cap written as a sentence inside a skill holds when the rule
# shapes ONE line written from scratch (a log.md entry), and fails when it asks
# to EVICT from a file that keeps growing (INDEX.md): eviction is a second,
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

# INDEX.md not touched in this session -> no noise. The commits of the last
# 3 hours count too: /end-session commits in the same turn, so at Stop the diff
# is already empty.
TOUCHED=$({ git diff --name-only HEAD 2>/dev/null; git log --since=3.hours --name-only --format= 2>/dev/null; })
printf '%s\n' "$TOUCHED" | grep -qx 'INDEX.md' || exit 0

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

exit 0
