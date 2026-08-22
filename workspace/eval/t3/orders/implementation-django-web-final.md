# T3 발주 — implementation-django-web-final

- 원문: `dddjango/skills/implementation-django-web/references/final.md` (현재 424행 — 센서스와 일치)
- 스코프: REF 12절 · 규범 129문장 (파일럿 기이관 절 제외됨)
- 산출: `workspace/eval/t3/specs/implementation-django-web-final.spec.json` + `workspace/eval/t3/worksheets/implementation-django-web-final.md`

| section_key | 헤딩 | 센서스 행 | 규범 수 | 운반체 | 재진술 | 비고 |
|---|---|---|---|---|---|---|
| s001 | Django Web 구현 가이드 | 1–19 | 2 | none | N | 머리말 소유 위임 2문장. 출처 약어 [DDoc] 등은 근거 표기이지 규범 아님 |
| s002-1 | 1. 책임 범위와 handoff | 20–36 | 12 | table | Y:implementation-django-web-skill/s003 | 위임표 6행 행당 1규범+스코프 선언 2 보수 포함. skill s004 요약줄과도 중복 |
| s003-2 | 2. TemplateView, Generic CBV, FBV 선택 | 37–98 | 11 | table,code | Y:implementation-django-web-skill/s004 | 선택표 5행 행당 1규범. «적합하다» 권고 1건 보수 포함 |
| s004-3 | 3. Context 준비와 표시 값 | 99–110 | 10 | none | Y:implementation-django-web-skill/s004 | 중앙 영구 테스트 입장 심사 판정 주체 명시 |
| s005-4 | 4. Templates, base template, includes/components | 111–149 | 15 | code | Y:implementation-django-web-final/s002-1 | 기준 3묶음(base 4·includes 4·style 5)+선두 2. 템플릿 책임 규칙이 §1·skill s004와 3중 |
| s006-5 | 5. Static files, CSS, JavaScript | 150–162 | 10 | none | N | skill s004 요약에서 누락된 절(사본 커버리지 구멍) |
| s007-6 | 6. Web forms와 POST flow | 163–206 | 7 | code | Y:implementation-django-web-skill/s004 | validation order 서술은 사실 진술로 제외(P0 승계) |
| s008-7 | 7. HTMX fragment와 AJAX | 207–237 | 6 | code | Y:implementation-django-web-skill/s004 | «HTMX view는 web adapter다» 정의문 제외 |
| s009-8 | 8. CSRF, XSS, security setting | 238–250 | 12 | none | Y:implementation-django-web-skill/s004 | check --deploy 실행·미실행 보고 의무 포함 |
| s010-9 | 9. View auth와 permission | 251–261 | 6 | none | N | skill s004 요약에서 누락된 절 |
| s011-10 | 10. Render acceptance checks | 262–280 | 14 | table | Y:implementation-django-web-skill/s004 | 검증 행렬 8행 행당 1규범+선두 4+말미 2 |
| s012-11 | 11. 서버렌더 에러 처리 | 281–424 | 24 | code | Y:implementation-django-web-skill/s004 | 최대 밀도 절. 코드 펜스 5개(예제 비계수·펜스 사이 산문 1 보수 포함). «discipline-houserules §2» 참조 표류 의심(P0 발견 3) |
