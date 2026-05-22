수정 대상: case

## 목표

`case-response-django-web-page`의 public prompt, answer oracle, targeted run 판정이 같은 web form acceptance 기준을 검증하게 한다.

## 수정 순서

1. public case에서 web form 요구를 GET, valid POST, invalid POST, error rendering, `ModelForm.Meta.fields`까지 명확히 쓴다.
2. answer oracle scoring check에서 해당 form subpath 누락을 pass 금지로 명시한다.
3. response bucket validator와 targeted eval을 다시 실행한다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`
- `make eval-one BUCKET=response CASE=case-response-django-web-page TRY_NUMBER=1 SCOPE=targeted TOPIC=django-web-p4 EXTRA_ARGS=--rerun JOBS=1`

## 완료 조건

- answer-oracle evaluation이 form subpath 결손을 pass로 완화하지 않는다.
- targeted response run status가 passed이고 review Minor가 닫힌다.
