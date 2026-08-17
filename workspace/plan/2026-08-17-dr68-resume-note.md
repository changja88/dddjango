# DR-68 재개 노트 (compact 대비 상태 외재화 — 2026-08-17)

> 세션 컨텍스트 압축 후 이 파일만 읽으면 이어서 작업 가능하도록 쓴 상태 스냅샷.
> 피드백 라운드가 이어질 예정 — 사용자가 compact 후 피드백을 준다고 예고함.

## 지금 상태 한 줄

**DR-68 집행 + 사후 완전성 대조(독립 3갈래 — 렌즈 노트 §G) + 정정 처분 완료·전 검증 green.** 사용자 결정(2026-08-17): 잔여 지적 A(명세 정정)·B(현지화 기록)·C(도구 정리) 전건 처리 + 버전업 — 본 트리를 커밋하고 `release: v2.12.0`(태그 `dddjango--v2.12.0`)으로 잇는다.

## 완료된 것

- 웨이브 1 실런 감사(4세션) → 3렌즈 적대 리뷰(44건) → 중재 → 재검(12건) → 집행 → 집행 diff 모순 재검 PASS → 재검 지적 정정까지 전 사이클 완료.
- 변경: tracked 22파일(+69/−49) + 신규 5파일(증거 문서 4 + 도구 1). 양판 plugin.json **2.12.0**, DEVLOG **DR-68** 등재.
- 핵심 산출물:
  - `workspace/tools/anchor_integrity_check.py` — 코퍼스 lint(개발 도구, registry 밖). 스킬 § 앵커 6형 문법 추출→절·«제목» 실재·이중 §공간 충돌 기계 판정. 현재 **255/255 OK**.
  - 정본 라벨 부착: `architecture-ddd/references/final.md` §3.2 말미 «판정 소유→구조 이주» 라벨+항-(1)(2)(3) (내용 무변경 — word-diff 확인). 에이전트 사본 2벌(design-review-ddd·design-architect) 압축.
  - 개정 1: ddd 리뷰어 판정-소유 대조 표(양판)+Coordinator 수신 구문 검사+리뷰어 경로 전달+«명세만» 관할 명시.
  - 개정 2: design-spec 전속 «경로 불문»(양판 — claude L80·L148 동일 구멍)+scope.md/지시문 우회 봉쇄+codex 지식 스킬 열람 제한.
  - 개정 3: 슬라이스 감사 정본 일원화+조건부 갈음+원작성자 반송+게이트 배너 상시 필드 2행+TodoWrite 명칭 정합.

## 정본 문서 (전부 커밋 대기 중)

- 명세: `workspace/design/2026-08-17-observance-hardening-spec.md` (v2.1+집행 정정 — §0.5 «라벨 부착» 정정·§7 중재표 44건·§8 DR 초안)
- 렌즈 노트: `workspace/design/2026-08-17-observance-hardening-adversarial-review.md` (§A~C 3렌즈·§D 댕글링 발견·§E 재검·§F 집행 재검)
- 감사 증거: `workspace/design/2026-08-16-wave1-skill-usage-audit-{claude,codex}.md`
- DEVLOG: §0 기준선 2026-08-17(2.12.0)·§2 DR-68

## 검증 재현 명령

```
python3 workspace/tools/anchor_integrity_check.py        # 255/255 OK · exit 0
python3 workspace/tools/corpus_mirror_sync.py --check    # 11/11 in-sync
python3 -m py_compile dddjango/scripts/check-composition-root.py dddjango/scripts/check-app-container.py workspace/tools/anchor_integrity_check.py
cmp dddjango/scripts/check-composition-root.py codex-dddjango/skills/dddjango/scripts/check-composition-root.py  # 미러 동일
```

## 미결·이월

- **해소(2026-08-17)**: 커밋+2.12.0 릴리스 집행(사용자 «A·B·C 처리 + 버전업» 지시). 남은 전달 사항 1건: 리빌드 조정자에게 `rebuild/specs/discipline/` 동결 사본 cmp 재확인 메모(리빌드는 2.11.0 캐시 고정이라 동작은 독립 — 메모는 사용자 경유 전달).
- **동적 관측(§6)**: 릴리스 후 첫 실런 transcript 감사 1회 — ddd 대조 표 존재·배너 필드·patch_apply 0건. 미충족 시 조항 강등. task 필드는 미사용+미기재 재발 시 B안(강등) 재논의 일몰.
- **이월(spec §5)**: 전면 인용-실독(재관측 후 승격)·claude 열람 제한(재발 시)·houserules §공간 재편·codex 병렬 문면 자구·«같은 파일 병렬 편집 금지» 자구 정비(§5-⑨).

## 맥락 (이 작업의 유래 — 피드백 라운드 배경)

발단은 사용자의 dddjango 플러그인 개선 논의: ① web 스킬(`implementation-django-web`) 보강 구상 — 클로드 디자인 인입(dddart의 DesignSync 메커니즘 이식·조건부 게이트)과 driving_layer controller 소비 패턴, 스킬/커맨드/houserules 4곳 분할 배치까지 방향 합의(설계 미착수) ② 웨이브 1 스킬 사용 점검 → 본 DR-68. XR·조정자 운영 문제는 별개 트랙(리빌드 런북 소관)으로 분리 합의됨.
