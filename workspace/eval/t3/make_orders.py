"""T3 발주서 생성기 — 동결 센서스(2026-08-19)에서 웨이브별 문서 발주서를 기계 생성.

사용: python3 workspace/eval/t3/make_orders.py <doc_key>...
출력: workspace/eval/t3/orders/<doc_key>.md (REF 절 스코프 표 + 드리프트 경고)
파일럿 이관 절 4건은 자동 제외. 센서스 행 번호는 참고값 — 드리프트 문서는 현재 파일 기준 재확정 지시 포함.
"""
import csv, glob, sys, pathlib

CEN = 'workspace/design/2026-08-19-ontology-t1-census/'
PILOT = {('implementation-django-ninja-final','s022-6.1'), ('implementation-django-ninja-final','s023-6.2'),
         ('architecture-ddd-final','s017-3.2'), ('architecture-ddd-final','s051-8')}

secs = {}
for r in csv.DictReader(open(CEN+'sections.tsv'), delimiter='\t'):
    secs[(r['doc_key'], r['section_key'])] = r
cls = []
for f in sorted(glob.glob(CEN+'E*-classify.tsv')):
    cls += list(csv.DictReader(open(f), delimiter='\t'))
manifest = {r['doc_key']: r for r in csv.DictReader(open(CEN+'corpus-manifest.tsv'), delimiter='\t')}

for doc in sys.argv[1:]:
    m = manifest[doc]
    cur_lines = sum(1 for _ in open(m['path'], 'rb'))
    drift = cur_lines != int(m['expected_lines'])
    rows = [c for c in cls if c['doc_key'] == doc and c['type'] == 'REF' and (doc, c['section_key']) not in PILOT]
    tot_norm = sum(int(c['norm_count'] or 0) for c in rows)
    out = [f"# T3 발주 — {doc}", '',
           f"- 원문: `{m['path']}` (현재 {cur_lines}행" + (f" — **센서스 {m['expected_lines']}행에서 드리프트: 아래 행 번호는 참고값, spec은 반드시 현재 파일에서 재확정**)" if drift else ' — 센서스와 일치)'),
           f"- 스코프: REF {len(rows)}절 · 규범 {tot_norm}문장 (파일럿 기이관 절 제외됨)",
           f"- 산출: `workspace/eval/t3/specs/{doc}.spec.json` + `workspace/eval/t3/worksheets/{doc}.md`", '',
           '| section_key | 헤딩 | 센서스 행 | 규범 수 | 운반체 | 재진술 | 비고 |', '|---|---|---|---|---|---|---|']
    for c in rows:
        s = secs[(doc, c['section_key'])]
        note = (c['note'] or '').replace('|', '\\|')[:180]
        out.append(f"| {c['section_key']} | {s['heading'][:60]} | {s['line_start']}–{s['line_end']} | {c['norm_count']} | {c['carriers']} | {c['restate']} | {note} |")
    p = pathlib.Path(f'workspace/eval/t3/orders/{doc}.md')
    p.write_text('\n'.join(out) + '\n')
    print(f"{doc}: REF {len(rows)}절 · 규범 {tot_norm}문장 · {cur_lines}행" + (' [드리프트]' if drift else ''))
