수정 대상: skill

# P5 source-reference-audit 중복 정책 수정 계획

## 수정 범위

- `dddjango/skills/source-reference-audit/SKILL.md`
- runtime cache sync가 필요한 경우 active plugin cache의 같은 skill 파일

## 순서

1. `SKILL.md`에서 `source-governance.md`와 중복된 세부 정책을 줄인다.
2. section headings와 validator-required phrase는 보존한다.
3. `validate_skill_docs.py --phase all --skills-dir dddjango/skills`로 runtime guardrail 보존을 확인한다.
4. cache/source parity가 깨지면 cache sync 후 `diff -qr`로 확인한다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- 관련 plan constraint validator
- source bucket validator
- 이 skill 변경 때문에 source targeted case가 영향을 받으면 `case-source-metadata-cache-sync` targeted eval 재실행

## 완료 조건

- skill body와 bundled reference의 중복이 줄어든다.
- validator-required leakage/path-boundary phrases가 유지된다.
- 리뷰 결과 Blocker 0, Major 0, 열린 Minor 0이다.
