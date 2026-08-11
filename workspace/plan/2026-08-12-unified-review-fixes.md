# 통합 적대적 리뷰 — 발견·처분 기록 (리빌드 계획 1번 · 2026-08-12)

**방법**: 렌즈 넷(계획 대비 완전성 ×2 · 코퍼스 정합 ×2 · 규칙 모순 · 과적합) × 발견 6 에이전트
→ 발견별 독립 반박 검증(기본값 refuted) → 완전성 비평 1 + 삭제분 회귀 감사 1.
**결과**: 확정 34(blocker 9 · major 17 · minor 8) · 기각 0 · 불확실 0 + 비평 사각 5 + 삭제 유실 1.
**처분**: 전부 해소(아래 ⑫ 항목으로 묶음) — 검증 배터리 fresh green
(spec_lint 538·0 / tree_mirror 140 / corpus 11/11 / checker_lint 27·0(보강판) / reverse_coverage 0
/ fixture_matrix 57/57 / backstop_matrix 675/675 / byte-copy 29/29 / LEGACY·미이관·옛 주소 grep 0).

## 최대 발견 — 공용 오류 스키마 정본 주소가 명세 밖이었다 (blocker ×3 동근)

㉡ repoint 가 `common/ninja/response/error_out.py` 를 **옛 모양 그대로** `framework/ninja/response/`
아래로 옮겼는데, 명세는 이미 답을 갖고 있었다 — **#414**(`framework/<technology>/` 아래는
`<module>.py` 만 · `response/` 같은 방향 축 하위 폴더 금지)·**#417**(정본 =
`framework/ninja/framework_error_schema.py`·`framework_validation_error_schema.py`). 그 결과
check-business-vocabulary(#414)와 API-error 3종이 같은 저장소에 정반대를 요구해 code-json
스코프는 어떤 상태로도 27종을 전부 green 으로 만들 수 없었다(상호배타 교착).

**해소 = 명세로 정렬(사용자 결정 불요 — 명세가 왕)**: 검사기 3종 + backstop matrix(675케이스)
+ 문서 전부를 `framework/ninja/framework_error_schema.py` · 클래스 `FrameworkErrorSchema`
(파일↔클래스 대응 — #572 `<Bc>ErrorSchema` 선례)로 재정렬. 옛 response/ 전용 패키지의
byte-empty·extra 금지 검사는 패키지 소멸과 함께 걷음(matrix 3케이스 개명·flip — 숨은 스키마
모듈은 noncanonical inventory 분석이 계속 문다).

## 처분 묶음

1. **acl 이중 수용 잔존**(blocker): ctx `_acl_dir`(비-adapter 옛 위치 포함)·port-adapter 별칭
   루프 제거 — `driven_layer/adapter/anticorruption_layer/` 하나만.
2. **루트 common 수용 튜플 4곳**(major): ctx #470·naming ⓓ#36·business-vocab(2)·broker —
   framework 단일화. common-container 의 `BUCKET_NAMES` 는 «검출»(#49)이라 존치.
3. **checker_lint ㉢ 그물 보강**(major): «acl 별칭 나란히» 꼴·«("framework","common") 튜플» 꼴
   (±3줄 #규칙 인용 창 허용) + 줄바꿈으로 갈라진 낱말(«이중\n수용») 정규화 검사 —
   보강 직후 red 6건 실측 → 수정 후 0(고정-먼저 규율).
4. **discipline-reviewer canonical 오염**(blocker): :59·:79 `driving_layer/schema/error_out.py`
   ·`<Bc>ErrorOut` → `driving_layer/api/bc_error_schema.py`·`<Bc>ErrorSchema` + codex 쌍둥이
   + rubric-metrix NJ-4/NJ-7 클론(비평 지적).
5. **검사기 구현을 명세에 정렬**(blocker·major): db-table #326 에 **#327 admin/** 면제** 추가 ·
   ctx #470 을 BC 식별 인자(`bc`·`bounded_context`)로 한정(kind·mode·is_* 는 일반 시그니처와
   구별 불가 — FP 실증) · ctx #149 를 라우팅·등록 데코레이터로 한정(호출형 일반 데코레이터 FP 제거) ·
   ctx #472 에 서드파티 절대 import 갈래 추가(문면의 절반만 집행하던 것) · naming #30 에
   트리 27·29·32행(OHS `contract/` 접미형 정본) 면제. **전부 임시 저장소 실증**: #472 발화 1 ·
   #470 mode 0/bc 1 · #149 lru_cache 0/router.get 1 · #30 OHS 0/도메인 재접미 1.
6. **문서 어휘 스윕**: 12-slot 라벨(`common FrameworkErrorSchema action/shape`·`BC ErrorSchema`)을
   참여 문서 10곳(코디네이터·에이전트 4·codex 쌍둥이 5) 일괄 개명 · ninja skill final.md §6.2
   전면 repoint · eval 3문서(역사 앵커 보존·EVAL-METHOD 에 «기준 불변 문구 정리» 명기) ·
   dddjango.md 의 걷힌 슬라이스 서술(S1–S3·legacy) 3곳 현행화 + codex 동문 · openapi·
   composition-root 진단 문구 폴더-정본화 · final.md 531→538 · skeleton 죽은 줄 삭제.
7. **README·AGENTS.md 재작성**(비평 사각 — 추적-무변경 파일): V1 트리 교시 통째 → 표준 트리
   140행 발췌·27종(19종 표기 4곳).
8. **codex book-skill SKILL.md 11종 재생성**(major): 변환 규칙 = `user-invocable: false` 행 제거뿐
   임을 실측 후 dddjango 원본에서 기계 재생성(옛 4계층 교시 전량 소멸).
9. **make release 게이트 보강**(비평 사각): [2/7] 이 corpus --check 하나 → 검증 세트 8종
   (corpus·spec_lint·checker_lint·tree_mirror·reverse_coverage·fixture_matrix·backstop_matrix·
   byte-copy diff). 전부 위반 시 비-0 exit 실측.
10. **삭제분 회귀 1건 복원**(감사): 「BC(앱)명↔애그리거트명 유사 변형 금지(`ordering` vs `order`)」
    — final.md §3 권장 불릿 + discipline-reviewer #82 물음 종속절로 복원(기계 검사기 없음 유지).
11. **matrix 재캘리브레이션**: E-스윕 + 3케이스 개명·flip(`schema-framework-ninja-extra-module-allowed`
    ·`schema-common-init-reexport-allowed`·`schema-untracked-framework-ninja-module-allowed`) → 675/675.
12. **과적합 판정**: broccoli 고유명사의 판정 로직 유입 = 공용 스키마 주소 1건(위에서 해소)뿐.
    migration_gate 고정 목록은 문서화된 역사 고정본으로 통과.

## 남긴 것 (명시 추적 — 침묵 아님)

- **final.md ⓐ 편입률**(major plan-master-2): §2 골격 선별·§3 스텁 상태로 규칙 «값» 다수가 매핑표
  순서 편입 대기 — 완료 자가 없다. 처분: 이 항목으로 추적 + 후보 기계화 = spec_lint 검사 ⑨(ⓐ 편입률).
  리빌드 4번 루프와 병행 점진.
- **runtime pytest 스위트**(`workspace/eval/fixtures/api_error_contract/` — 비평 지적): 자기완결
  단일 파일 fixture 라 repoint 무영향(자기 소유 shape — 검사기가 안 읽음). 배포(2번) 전 1회 실행 권고
  (pip 핀 설치 필요).
- 검증 그물의 알려진 구멍: checker_lint 의 ±3줄 #인용 창은 휴리스틱(인용 낀 수용은 통과 가능) —
  적대 리뷰가 보완 축.
