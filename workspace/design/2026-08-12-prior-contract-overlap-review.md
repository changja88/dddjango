# 선행-계약 검사기 7종 — 트리 규칙 겹침 재검토

**2026-08-12 · 8번 이관 ㉠** · 대상: 538 매핑표에 ⓒ 규칙이 0건인 검사기 7종
(`reverse_coverage.py` 가 실증 — 이들의 문면은 트리 개정 명세 «밖» 선행 계약이 소유).

재검토 물음: 「트리 규칙(538)이 이 검사기의 술어를 이미 갖고 있나 — 같은 사건에
두 검사기가 발화하나(중복 진단), 같은 표면을 다른 술어로 보나(보완), 아예 안 겹치나」.

| 검사기 | 선행 계약 | 판정 | 근거 |
|---|---|---|---|
| `check-response-schema-bypass` | 08-04 API-error | **안 겹침** | JSON 성공 응답 형태는 트리 규칙 관할 밖(성공 lane — 트리는 오류·구조만) |
| `check-transient-overmapping` | 08-04 API-error | **안 겹침** | preserve handler 의 permanent/retryable 폭 — 트리 규칙에 대응 술어 없음 |
| `check-synthetic-infra-exc`※ | 08-04 API-error | 안 겹침(#129 는 이관받은 트리 규칙 — 매핑표 1건 보유라 7종 밖) | catch-all 번역 슬라이스만 트리 소유 |
| `check-choices-literal-consumption` | 2026-07-06 상수 승격 | **안 겹침** | Enum/choices 리터럴 소비 ≠ #565(Enum 값∩단계 이름)·#607(임계값) — 다른 지식 |
| `check-idempotency-scope-creep` | architecture-api §13 | **안 겹침 — 경계 명문화** | §13 의 `Idempotency-Key` 서브시스템(승인 필요·스코프 가드)과 #181 의 «입구 재실행 멱등»(무승인 의무)은 **다른 층위**다. #181 이 요구하는 get_or_create·조기 반환은 이 검사기의 «미승인 산출물»이 아니다 — 충돌 없음 |
| `check-app-container` | 구 규약(컨테이너 위치) | **안 겹침(유일 실체)** | 트리 검사기들은 `application/` «안»만 스캔한다(skeleton BC 발견=rglob application 직계). 루트 평면 Django 앱(밖으로의 탈주)을 잡는 술어는 이 검사기뿐 |
| `check-common-container` | D38(승격/강등) | **보완(같은 표면·다른 술어)** | `application/framework|common/` 오배치 버킷: 이 검사기는 «층 폴더 없는 진짜 버킷»만 잡고(FP≈0 그물), #49⑴(트리 밖 BC 폴더)은 ctx 문서화 규칙으로 실발화 0 — 이중 발화 실측 없음. 실체는 이 검사기 |
| `check-ninja-boundary-middleware` | 08-04 API-error | **겹침 1건 발견 → 걷음** | `<project>` settings 의 `MIDDLEWARE = ["application.<bc>…"]` 한 항목에 #433(ctx — BC 경로 리터럴)과 이 검사기(자가등록)가 **둘 다 발화**했다. MIDDLEWARE 안의 BC 경로는 «주소 목록»이 아니라 «금지된 자가등록»이므로 실체는 이 검사기(#8) — **#433 에서 MIDDLEWARE 대입을 면제**(INSTALLED_APPS 와 같은 자리·참조 주석) · 2026-08-12 반영 |

## 남는 것

- 7종의 문면 소유는 각 선행 계약 문서 + registry 설명문(`commands/dddjango.md`)이 진다 —
  538 매핑표에 편입하지 않는다(명세의 관할이 다르다).
- 이 재검토로 8번 ㉠의 «겹침 재검토» 항목 종결. 남은 8번 ㉡(V1 옛 기계·preserve 조기
  반환·이중 수용 걷기)는 **대상 저장소들이 새 표준 채택을 마친 뒤**의 작업이다 —
  지금 걷으면 옛 모양 저장소에서 검사가 무동작이 된다(fail-open 재생산).
