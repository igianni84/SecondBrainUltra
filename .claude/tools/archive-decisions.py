#!/usr/bin/env python3
"""When decisions/INDEX.md goes over its cap (55 KB, measured by .claude/hooks/check-index-caps.sh),
move the rows up to a given month to the archive. The rows land unchanged in
decisions/_archive/INDEX.md, under the same section: nothing is deleted. The last row of a
section stays where it is, so no section empties and no decision loses its only link.

Usage:  python3 .claude/tools/archive-decisions.py 2026-06            (dry run: says what would move)
        python3 .claude/tools/archive-decisions.py 2026-06 --write
        python3 .claude/tools/archive-decisions.py --test
"""
import os, re, sys, time

ROW = re.compile(r'^\| *\*{0,2}(\d{4}-\d{2})-\d{2}')
DAY = re.compile(r'\d{4}-\d{2}-\d{2}')
HEAD = '| Date | Decision | Status | Tag |\n|---|---|---|---|'      # used when a section has no table header
POINTER = re.compile(r'^> Rows up to .* live in the \[\[decisions/_archive/INDEX\|index archive\]\]\.$', re.M)
MONTHS = 'January February March April May June July August September October November December'.split()


def month(ym):
    return f'{MONTHS[int(ym[5:7]) - 1]} {ym[:4]}'


def move(index, archive, upto):
    """Return (new index, new archive, rows moved)."""
    lines = index.split('\n')
    sec, rows, heads = None, {}, {}
    for i, l in enumerate(lines):
        if l.startswith('## '):
            sec = l[3:].strip()
        elif sec and ROW.match(l):
            rows.setdefault(sec, []).append(l)
            if sec not in heads and i >= 2 and lines[i - 1].startswith('|') and lines[i - 2].startswith('|'):
                heads[sec] = lines[i - 2] + '\n' + lines[i - 1]
    out = {}
    for s, rs in rows.items():
        v = [r for r in rs if ROW.match(r).group(1) <= upto]
        if len(v) == len(rs):               # the section would empty: its newest row stays
            v.remove(max(v, key=lambda r: DAY.search(r).group(0)))
        if v:
            out[s] = v
    gone = {r for v in out.values() for r in v}
    if not gone:
        return index, archive, 0
    new = '\n'.join(l for l in lines if l not in gone)
    pointer = f'> Rows up to {month(upto)} live in the [[decisions/_archive/INDEX|index archive]].'
    if POINTER.search(new):
        new = POINTER.sub(lambda m: pointer, new, count=1)
    else:                                   # right after the first block of "> " lines, or after the title
        nl = new.split('\n')
        quote = [i for i, l in enumerate(nl) if l.startswith('> ')]
        at = next((i for i in quote if i + 1 not in quote), None) if quote else None
        if at is None:
            at = next((i for i, l in enumerate(nl) if l.startswith('# ')), 0)
            nl[at + 1:at + 1] = ['', pointer]
        else:
            nl[at + 1:at + 1] = [pointer]
        new = '\n'.join(nl)
    new = re.sub(r'^updated: .*$', 'updated: ' + time.strftime('%Y-%m-%d'), new, count=1, flags=re.M)
    arch = archive or ('---\ntype: meta\ndescription: Rows moved out of decisions/INDEX.md to keep it under its cap\n'
                       'status: evergreen\ntags: [archive]\n---\n\n# Decisions — index archive\n\n'
                       '> Rows moved unchanged from [[decisions/INDEX|decisions/INDEX]] by '
                       '`.claude/tools/archive-decisions.py`. The decision files stay in `decisions/`.\n')
    for s, v in out.items():
        title, head = f'## {s}\n', heads.get(s, HEAD)
        if title not in arch:
            arch = arch.rstrip('\n') + f'\n\n{title}\n{head}\n'
        before, rest = arch.split(title, 1)
        body, tail = (rest.split('\n## ', 1) + [None])[:2]
        old = [l for l in body.split('\n') if ROW.match(l)]
        allrows = sorted(set(old + v), key=lambda r: DAY.search(r).group(0), reverse=True)
        arch = before + title + f'\n{head}\n' + '\n'.join(allrows) + '\n' + ('\n## ' + tail if tail is not None else '')
    return new, arch, len(gone)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if '--test' in sys.argv:
        return test()
    if len(args) != 1 or not re.fullmatch(r'\d{4}-\d{2}', args[0]):
        sys.exit(__doc__)
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    pi, pa = os.path.join(root, 'decisions', 'INDEX.md'), os.path.join(root, 'decisions', '_archive', 'INDEX.md')
    with open(pi, encoding='utf-8') as f:
        index = f.read()
    archive = ''
    if os.path.exists(pa):
        with open(pa, encoding='utf-8') as f:
            archive = f.read()
    new, arch, n = move(index, archive, args[0])
    kb = lambda t: len(t.encode()) / 1024
    print(f'rows up to {month(args[0])}: {n} · index {kb(index):.1f} KB -> {kb(new):.1f} KB · archive {kb(archive):.1f} KB -> {kb(arch):.1f} KB')
    if n and '--write' in sys.argv:
        os.makedirs(os.path.dirname(pa), exist_ok=True)
        with open(pa, 'w', encoding='utf-8') as f:      # the archive first: a crash halfway leaves a duplicate, not a hole
            f.write(arch)
        with open(pi, 'w', encoding='utf-8') as f:
            f.write(new)
        print('written: decisions/INDEX.md, decisions/_archive/INDEX.md')
    elif n:
        print('dry run: nothing written. Add --write to move the rows.')


def test():
    head = '| Date | Decision | Status | Key tag |\n|---|---|---|---|'
    r = lambda d, s: f'| {d} | [[decisions/{d}-{s}\\|{s}]] | active | t |'
    ind = ('---\ntype: meta\nupdated: 2026-01-01\n---\n\n# Decisions\n\n> Intro line one.\n> Intro line two.\n\n'
           f'## A\n\n{head}\n{r("2026-07-02", "a3")}\n{r("2026-06-10", "a2")}\n{r("2026-05-01", "a1")}\n\n'
           f'## B\n\n{head}\n{r("2026-05-20", "b2")}\n{r("2026-05-03", "b1")}\n\n## How to add\n\n- x\n')
    n1, a1, k = move(ind, '', '2026-06')
    assert k == 3, k
    assert 'a3' in n1 and 'a2' not in n1 and 'a1' not in n1
    assert 'b2' in n1 and 'b1' not in n1                 # the last row of section B stays
    assert all(x in a1 for x in ('a2', 'a1', 'b1')) and 'b2' not in a1
    assert a1.index('a2') < a1.index('a1')               # newest on top
    assert 'Key tag' in a1                               # the archive reuses the index's own table header
    assert '> Intro line two.\n> Rows up to June 2026 live in the [[decisions/_archive/INDEX|index archive]].' in n1
    assert '## How to add' in n1 and '- x' in n1
    n2, a2, k2 = move(n1, a1, '2026-06')
    assert k2 == 0 and n2 == n1 and a2 == a1             # run again: nothing moves
    ind3 = n1.replace(r('2026-07-02', 'a3'), r('2026-09-01', 'a4') + '\n' + r('2026-07-02', 'a3'))
    n3, a3, k3 = move(ind3, a1, '2026-07')               # second round: the pointer is updated, the archive grows
    assert k3 == 1 and 'a3' in a3 and 'a4' in n3
    assert n3.count('index archive]]') == 1 and 'Rows up to July 2026' in n3
    assert a3.index('a3') < a3.index('a2')
    print('ok')


if __name__ == '__main__':
    main()
