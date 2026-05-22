수정 대상: answer

# response P5 order-create answer basis 계획

## 수정 범위

- `workspace/develop/eval/response/answer/case-response-order-create.yaml`

## 순서

1. Broad `workspace/develop/eval` reference basis를 제거한다.
2. `source-reference-audit/SKILL.md`와 workflow role-map처럼 이 response case의 owning basis가 아닌 항목을 제거한다.
3. 필요한 경우 implementation-django runtime reference를 추가해 transaction/on_commit handoff basis를 owning implementation 근거로 둔다.
4. response bucket validator와 targeted eval을 실행한다.

## 완료 조건

- Answer oracle은 response design case의 owning skill/source references만 든다.
- Workflow 실행 평가와 response mixed design 평가가 분리된다.
- Targeted eval pass run이 현재 파일 기준으로 남는다.
