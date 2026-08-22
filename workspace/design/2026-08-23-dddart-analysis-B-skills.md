# dddart 전수 분석 B — 스킬 11종 (2026-08-23)

> dddjango-web 2단계 산출물. 소스: 마켓 클론 `~/.claude/plugins/marketplaces/changja88-dddart/dddart/skills/` (SKILL.md 11 + final.md 11 + undecidable.md 1 전문 실측). 태그 = 차이 5축.

## 공통 판형

- 라우팅 표 축 11종 동일(행=질문/주제, 열=«질문|위치(final.md §N)»). 전 SKILL.md 말미 "각 절은 필요한 절만 읽는다(`## §N.` grep — 전체 로드 불필요)". 전부 `user-invocable: false`.
- 부속 reference는 houserules의 undecidable.md(109행) 하나뿐 — 4개 architecture 스킬이 원격 참조.

## 스킬별 절 인벤토리 (요약)

### architecture-ddd (final 239행, §1–§11) — 전절 [BC][MODEL]
§1 간소화 지도(채택/비채택 표) · §2 전략 어휘(BC 물리형태·교차 4채널·라벨 verbatim) · §3 VO·엔티티(freezed·수기 fromJson 금지·라우터 인자 String) · §4 애그리거트(루트 경유 3규칙·MD1) · §5 판정 소유·강등(1곳째 domain·시간은 인자) · §6 도메인 서비스(주어 귀속) · §7 Specification · §8 UseCase 관문 · §9 빈혈 vs 풍부 · §10 비채택 11종 음성 지식 · §11 요약

### architecture-ui (final 116행, §1–§8) — §S2에서 이미 현지화 완료
§1 3단 판별표(VM 보유/화면 전속/재사용 — 3문항) · §2 view 규율(자기 VM watch만·NM17) · §3 section·widget(dumb·접두·Key 짝[TEST]) · §4 승격 표(신호→이동 3행+역방향 절제) · §5 ui_extension(도메인→UI 매핑 유일 자리) · §6 라우팅 짝(리터럴 단일 출처·navigator View import 금지) · §7 design_system 사용(7토큰·show() 금지) · §8 크기 연결(추출 치수 전수·빈칸 0·형상은 코퍼스 밖)

### architecture-state (final 188행, §1–§10) — 전절 [STATE]
§1 지도(VM 3변종 표: 상태·구동원·수명) · §2 VM(번역만·no-DI) · §3 State 계약(freezed·error 필드) · §4 에러 2채널(정식 예제) · §5 SharedState(과거형 사건명 금지) · §6 Service(능동/수동) · §7 교차 BC 상태(watch 금지) · §8 refresh 채널 처방 · §9 keepAlive 결정 · §10 합성 루트 상태(거의 빈 VM)

### architecture-data (final 165행, §1–§8)
§1 지도(종류 3+local_storage·no-DI) · §2 safeApiCall 정규화[FLUTTER] · §3 Either(Right=성공) · §4 DataSource 직반환(DTO 없음)[MODEL] · §5 로컬 2층[FLUTTER][BC] · §6 infra service · **§7 계약 스냅샷 체계(중립! — openapi-full G0 동결 vs server-contract G1 기계 절단·독자 표)** · **§8 계약 위험 행위(중립 — tracer 앵커)**

### discipline-cleancode (final 2852행, §1–§18+요약 30행)
**원본 = dddjango 소스판(2026-06-12 반입) — 예제만 Dart 치환.** 출처 서지 9종([CC][IP][OO][PC][APoSD][CodeC][PP][Ref][WELC]). §1 정의 · §2 이름 · §3 함수(작게+모듈은 깊게) · §4 주석 · §5 형식 · §6 추상화·캡슐화 · §7 깊은 모듈[APoSD] · §8 객체 설계 · §9 SOLID(9.1에 dddart Fat 스멜표 삽입·9.5 DIP 단서=DI 없음) · §10 패턴 · §11 상태(변수 스코프 의미) · §12 오류 처리 · §13 DRY(지식의 중복) · §14 협력(14.6 Repo 단서) · §15 리팩토링(스멜 5군 표) · §16 레거시(dddart 단서: 테스트 인프라 비강제) · §17 설계 철학 · **§18 dddart 신설: 반복>상속(base 클래스·믹스인 금지 — 작성자가 AI coder라 반복이 더 결정적)**. dddart 고유 삽입부 14곳 목록 확보.

### discipline-houserules (final 338행, §1–§8 + undecidable.md 소유)
SKILL.md 자체가 §1–§4 절차 문서(트리 결정 순서 5단계·충돌 중재·레드 플래그 10·백스톱 연동). final: §1 표준 트리 전문(4원칙: 실측 기준·간소화 DDD·철저한 MVVM·**파일트리가 곧 규약** + root/area/test 핵심 사실) · §2 성장 규칙(개념 1차·종류 2차 — domain 항상/app·pres 둘째 개념 시/infra 평면·분할 후 기존 동결·같은 개념 같은 철자) · §3 골격 완비(전부·비어도 .gitkeep·선택 폴더 없음·test/만 sparse 예외·국소 analysis_options) · §4 명명 총괄표(공통 원칙 6 + 위치 27행 표: 위치|접두|파일명|클래스명) · §5 import 방향(계층 매트릭스 5×5 + 교차 4채널 + 방향 규칙 8) · §6 common·design_system 입장 판별(4문항 표·«편의 버킷 아님»·부품군=접미사=클래스) · §7 표기 표준화(변형→표준 46행 교정 사전·적용 경계 ⓐ표기는 파일 ⓑ구조는 단위) · §8 백스톱 연동(러너 CLI·게이트 의미론·반송 패밀리→교정 절 백링크)

### undecidable.md (109행) — 판별 18종 배정표
행=§1~§13, 열=«판별|1차 결정|검증». §1 view/section(architect→ui→discipline) · §2 화면 전속 · §3 BC 어휘·귀속 tie-break 4단·조립 vs 투영 · §4 게이트 화면 · §5 handler 입장 · §6 거의 빈 VM·푸시 정규화 · §7 common 살아있는 상태 · §8 판정 귀속(domain 기본) · §9 두 번째 개념·같은 철자(coder=2차 발견자) · §10 과거형 사건명 · §11 main 최소형(**1차 판정자 coder인 유일 행**) · §12 계약 위험 표기(중립) · §13 접두↔area(**판정은 사용자·config 영속**)

### discipline-test (final 163행) — 전절 [TEST]
§1 회귀 안전망(TDD 아님·무게중심 thick domain) · §2 오라클은 명세에서(비-vacuity 자가점검) · §3 단언 FORM 6소절(구별=집합 크기/순서=뒤섞기+orderedEquals/위치=keyed-slot/탭=non-edge/양갈래/매핑=case별 핀) · §4 생략 목록 · §5 red=코드 수정(테스트 약화 금지)

### implementation-dart (final 160행) — 전절 [FLUTTER]
§1 SDK ^3.9 · §2 Effective Dart 선별+의도적 일탈 3 · §3 널 안전(promotion 지역 복사) · §4 freezed 3.x 계약 · §5 switch 패턴(when/map 제거) · §6 Dart 3 문법 · §7 json_serializable(@JsonKey 명시) · §8 dartz Either 최소 표면

### implementation-flutter (final 256행) — 전절 [FLUTTER]
§1 버전 · §2 go_router 표기 · §3 탭 재탭 2단(root_view 소유) · §4 dio·retrofit · §5 hive_ce(typeId 대역) · §6 위젯 수명·BuildContext 안전 · §7 테스트 위임(목차 누락 관찰) · **§8 정적 이미지 에셋(asset-manifest SSOT·AppAsset 토큰·pubspec 멱등 — 이식 후보)** · **§9 레이아웃 형상 — 시안 충실 재현(«재현이지 직수입이 아니다» — 이미 채택)**

### implementation-riverpod (final 150행) — 전절 [FLUTTER][STATE]
§1 버전 짝 · §2 @riverpod 변종 화이트리스트 · §3 keepAlive 표기 · §4 ref 규율(mounted 가드) · §5 AsyncValue · §6 invalidateSelf · §7 View 측 표기 · §8 재시도 전역 OFF · §9 금지 표면 · §10 lint 연동

### implementation-test (final 173행) — 전절 [TEST]
§1 mocktail(코드젠 0) · §2 격리 seam 3 · §3 더블·matcher · §4 펌프 결정성 · §5 날짜 주입 · §6 네트워크 이미지 목 · §7 헬퍼 계약(screenProbes) · §8 안 쓰는 것(golden 비채택)

## 경계망 (상호 위임)

- SKILL.md «경계» 블록 11종 + final.md 본문 위임 문장 46건 수집 완료(원 보고 참조— 4단계 작성 시 dddjango-web 판 경계망 재구축의 기준).
- 판형: 값(houserules)/절차(architecture)/표기(implementation)/규율(discipline) 4계 분업 + 대칭 위임 문구 + undecidable 공유 적재("1차 결정자와 검증자가 같은 파일").

## 문서 내부 불일치 관찰 (이식 시 반복 금지)

1. discipline-test 형 수 표기 3중 불일치(5형/4형/6소절) 2. implementation-flutter 목차 §7 누락 3. houserules SKILL.md와 final.md 간 사실 중복 서술 1건 4. data §2 봉투 철자 예시가 골든 코드에 하드코딩 5. root_vm keepAlive 명시적 공백
