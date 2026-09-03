# 항목 H — pre-content 골격 «자리 실체화(빈 모듈)» ↔ 검사기 «클래스 하나» 상충 · 증거 수집 (2026-09-04)

격리 복제본: `scratchpad/fr2/H/spring/` (`git clone -q ~/Desktop/spring_dream_server` → `checkout --detach`). 원본 두 저장소·dddjango 저장소는 읽기만 했다.
검사기 실행: `run_rules.py`(27종 로스터 `checker_registry.REGISTRY` → 개별 `check-*.py <저장소 루트>` · `DJR_FINDINGS_JSON` sink → 규칙×`fortune_catalog` 경로 필터). 로그·jsonl은 `out/`.

## 1. 검사기 조건 표 (dev main = 설치본 2.17.16 — 두 검사기 파일 byte 동일 · `diff -rq` 차이는 public-surface-annotation·design_pregate·pregate_symbol_kinds·rulepack 4개뿐)

| 규칙 | 파일:줄 | 조건식 | 발화 계기 |
|---|---|---|---|
| #219 | `check-port-adapter-pairing.py:245-247` `_check_port_contract` | `classes=[공개 ClassDef in mod.body]; if len(classes)!=1` → «공개 클래스 N개 — 추상 인터페이스 «하나»가 온다» | **빈 파일 존재**(`ast.parse("")`→Module, 클래스 0) · 주석만 있어도 동일 |
| #635 | `check-usecase-dto-placement.py:383-385` `_check_entry` | `pubs=_top_public_classes(mod); if len(pubs)!=1` → «진입점은 클래스 «하나»다 — 공개 클래스가 N개다» | **빈 파일 존재** |
| #218 | `check-port-adapter-pairing.py:211-213` | `if not (cap/f"{cap.name}_port.py").is_file()` → «계약 파일 이름이 폴더와 다르다» | **파일 부재** |
| #193 | `check-usecase-dto-placement.py:342-343` | `entry=checker_target.slot_file(uc/f"{name}_use_case.py"); if entry is None` → «진입점 파일 이름은 … — 부재» | **파일 부재** |
| #576 | `check-port-adapter-pairing.py:1030-1046` `_check_fake` | `decl_stems={port.rglob("*_port.py") stems…}; fake py.stem not in decl_stems` → «짝이 될 «선언»이 없다» | **선언 파일 부재**(fake 파일이 있을 때) |
| (추가) #488 | `check-layer-skeleton.py:238-245` | fixed/reappear 칸 파일 `not target.is_file()` → «고정 파일 부재 — **비면 빈 파일로 만든다** (트리 41/47행)» | **파일 부재** — `standard_tree.py:78,84` `<use_case>_use_case.py`·`<capability>_port.py` = `reappear`(=fixed) |

세 검사기의 해당 줄은 `7f695bb`(2026-08-12) 이후 무변경 — v2.17.x 전 버전에 동일.

## 2. 재현 표 (커밋 3 × 검사기 세트 2 + 수동 왕복) — fortune_catalog 귀속 건수

| 상태 | #219 | #635 | #218 | #193 | #576 | #488 |
|---|---|---|---|---|---|---|
| `59d08c7` 골격(빈 5파일 있음) dev / inst | 2 / 2 | 3 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 0(27종 전수 dev) |
| `99253ce` 빈 5파일 제거 dev / inst | 0 / 0 | 0 / 0 | 2 / 2 | 3 / 3 | 2 / 2 | **5** (dev) |
| `9c8814e` 복원 dev / inst | 2 / 2 | 3 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 0 (dev) |
| 수동: 9c8814e에서 5개 `rm` dev / inst | 0 / 0 | 0 / 0 | 2 / 2 | 3 / 3 | 2 / 2 | 미측정 |
| 수동: 빈 파일 재생성 dev / inst | 2 / 2 | 3 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 미측정 |
| 수동: `# placeholder` 한 줄 파일 dev | 2 | 3 | 0 | 0 | 0 | 미측정 |

dev/inst 차이 **0**. 결정적: 빈 파일 있음 → {#219×2, #635×3}=5행 · 없음 → {#218×2, #193×3, #576×2, #488×5}=12행. 두 집합은 서로소이며 동시 만족 상태(위반 0)는 «클래스 하나가 든 파일»뿐이다.
발화 파일 5개: `application_layer/port/{active_service_bundle,relation_table}/<cap>_port.py` · `application_layer/catalog_inquiry/{list_fortune_types,resolve_fortune_support,select_visible_fortune_candidates}/<uc>_use_case.py`. #576 짝은 `test/fake/{active_service_bundle_port,relation_table_port}.py`(59d08c7에서 0바이트로 생성).
diff: `59d08c7` 100 files/+11(골격 전부 0바이트 + apps.py + INSTALLED_APPS) · `99253ce` 5 files 0/0(위 5개 삭제) · `9c8814e` 5 files 0/0(재추가). 5개는 `725fbe0`(14:37:36, S2)에서 내용이 채워짐.

## 3. 왕복 비용
`59d08c7` 13:55:30 → `99253ce` 14:05:40(+10:10) → `9c8814e` 14:09:12(+3:32) = **13분 42초 ≈14분** (주장 검증 ✓).

## 4. 표본 외

| 저장소·런 | 문서 | 기록 | 처리 |
|---|---|---|---|
| spring promotion-pricing(08-31) | `review-s2-r2.md:52`·`implementation-review-s3-discipline-blocker.md:52-53` | #219×2(0-byte port)·#635×4(0-byte use-case shell)·#477/#351×2 | «time-phased skeleton — 후속 슬라이스 Red 뒤 채움» 수용, 삭제 없음 |
| spring fortune-reading(08-31) | `pregate-report.md:22-29,2290-2294` | pre-gate 예보 #219×1·#576×3·#635×1 / #488×2·#193×1 | 설계 교정(`corrected`) |
| spring notification-bc(09-02) | `pregate-report.md:34,173` | #635(공개 클래스 2개) | 빈 파일 무관 |
| kkebi saju-chart-engine(08-23) | `scope.md:79` 외 15개 리뷰 문서 | S1 pre-content에 `#219×2+#477×2+#635×3=9` 조기 red | 잔존 허용·S2 내용으로 해소, 삭제 없음 |
| kkebi bug-report-analytics(08-25) | `mediation-g2-round1.md:456,462` | #219/#635 설계 논의 | 빈 파일 무관 |

git 이력 «0바이트 A→D→A»(`zero_byte_history.py`, `--all`): spring **5경로**(전부 catalog 위 5개) / kkebi **0** (추적 0바이트 .py 886/1331). 왕복은 catalog 1레인 유일. #219/#635 pre-content 발화 자체는 4런(spring 2·kkebi 1 + catalog)에서 반복.

## 5. 규범 문면
- `commands/dddjango.md`(전 절 graph-owned 마커 2,15,33,65,70,83,101,172,177,190,203): «골격 실체화·빈 파일·pre-content» 문면 **0건**. 105행 «슬라이스 0»=리팩터링 슬라이스(빚) · 126행 registry #4 «140행 골격(고정·자리표시자·재등장 칸)» 언급뿐. Coordinator는 골격 슬라이스를 지시하지 않는다.
- `agents/coder.md:38`(graph-owned §«작업 방식» 35→62) **R-2499** «골격 실현 의무 … 고정·재등장 칸은 내용이 없어도 … 파일은 빈 파일로 만든다(#488)» + R-2500/2501/2502.
- `discipline-houserules/references/final.md:21` #488 «파일도 비면 «빈 파일»로 만든다 … 빈 칸 실현의 정본 형태는 여전히 «빈 파일»» · `:24` #491 재등장=고정 · `:27` **R-3188** «coder 가 … 빈 채로라도 실현» · **R-3189**. 트리 41행 `<use_case>_use_case.py`·47/121행 `<capability>_port.py`.
- 카탈로그 빈 파일 근거: `design-spec.md:268` «슬라이스 0 — 골격: 표준 트리 빈 골격 전부(고정·재등장 칸 __init__.py/빈 파일) … 검증: check-layer-skeleton green» + `scope.md:28,38`(#488 인용). 즉 architect 명세 → coder R-2499 집행. pre-gate 스텁 아님(pregate-report 예보 1건 #392뿐 · «스텁 본문 `...`»). REPORT «lane 6» 라벨의 정의는 발주서·orders에 없음(미측정 — ledger는 레인 4).
- «존재-하나» 성문: #219·#635는 `check-*` 도크스트링(port:7 · usecase:19)과 final.md 트리 규칙(R-ID는 rulepack 매핑 — 미조회).

## 6. ⓐ/ⓑ 판단 재료
- ⓑ 위험(빈 모듈 영구 잔존): HEAD 추적 0바이트 .py(`__init__` 제외) spring 113(허용 칸 112 + `query_translation/.../translation_controller.py` 1, 08-31~) · kkebi 168(허용 칸 151 + **tarot domain 12**(6 애그리거트 `.py`+6 `_repository.py`, 08-25 이후 10일째) + billing controller 4 + `_out.py` 1). `_port.py`/`_use_case.py` 0바이트 잔존은 양쪽 0 — 그러나 #219/#635 급 «하나» 검사가 없는 칸(controller·애그리거트)은 실제로 비어 남아 있다.
- ⓐ 채택 시: 첫 슬라이스 전 부재 상태에서 #488×5(registry #4, 골격 선행 게이트 #487 — `registry_gate.py`에 조기 중단 처리 없음, 27종 전부 실행)+#218×2+#193×3+#576×2 가 결정적으로 발화한다(§2). ⓐ는 Coordinator 문면만이 아니라 R-2499·R-3188·#488 코드(«비면 빈 파일로 만든다» 메시지)와 정면 충돌 — 셋을 함께 개정해야 한다.
- 대안 표지: 다른 3런은 삭제 없이 «pre-content 잔존 red 허용 후 슬라이스에서 해소»로 처리했다(카탈로그만 삭제 왕복).
