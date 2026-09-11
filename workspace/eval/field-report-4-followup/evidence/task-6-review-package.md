# task-6 review package

No commit was authorized. This package compares owned-file snapshots before this task with current bytes.

## ontology/rules/agent-design-architect.ttl

Before SHA256: a0a57735092853071940be471e086fff1777772651f8e7f706355f45b2e57a3e
After SHA256: 9865c8f5787809d3e0cd6e5cdcb119b859d20615a524d7fde1322330a4213f0a

```diff
--- before/ontology/rules/agent-design-architect.ttl
+++ after/ontology/rules/agent-design-architect.ttl
@@ -490,26 +490,32 @@
 
 djr:R-1616 a djr:Permission ;
     skos:prefLabel "slot 10 — 복수 internal failure 의 단일 public ErrorCode 수렴 허용"@ko ;
     djr:currentExpression <https://numchida.com/ns/djr#R-1616@2026-08-22> .
 
 <https://numchida.com/ns/djr#R-1616@2026-08-22> a djr:Expression ;
     prov:specializationOf djr:R-1616 ;
     djr:revision 1 .
 
 djr:R-1617 a djr:Obligation ;
-    skos:prefLabel "slot 10 — raw infra failure 의 기본 500 과 승인된 public meaning 한정 정규화"@ko ;
-    djr:currentExpression <https://numchida.com/ns/djr#R-1617@2026-08-22> .
+    skos:prefLabel "내부 실패 정규화와 공개 HTTP 계약 승인 분리"@ko ;
+    djr:currentExpression <https://numchida.com/ns/djr#R-1617@2026-09-11> .
 
 <https://numchida.com/ns/djr#R-1617@2026-08-22> a djr:Expression ;
     prov:specializationOf djr:R-1617 ;
     djr:revision 1 .
+
+<https://numchida.com/ns/djr#R-1617@2026-09-11> a djr:Expression ;
+    prov:specializationOf djr:R-1617 ;
+    prov:wasRevisionOf <https://numchida.com/ns/djr#R-1617@2026-08-22> ;
+    djr:revision 2 ;
+    djr:revisionKind djr:revision-amendment .
 
 djr:R-1618 a djr:Obligation ;
     skos:prefLabel "slot 10 — preserve 의 profile-native mapping 기록과 code-profile chain 비강제"@ko ;
     djr:currentExpression <https://numchida.com/ns/djr#R-1618@2026-08-22> .
 
 <https://numchida.com/ns/djr#R-1618@2026-08-22> a djr:Expression ;
     prov:specializationOf djr:R-1618 ;
     djr:revision 1 .
 
 djr:R-1619 a djr:Obligation ;
@@ -1678,50 +1684,62 @@
 
 djr:R-1760 a djr:Obligation ;
     skos:prefLabel "한 주제의 단일 lens 소유와 스킬 경계 준수"@ko ;
     djr:currentExpression <https://numchida.com/ns/djr#R-1760@2026-08-22> .
 
 <https://numchida.com/ns/djr#R-1760@2026-08-22> a djr:Expression ;
     prov:specializationOf djr:R-1760 ;
     djr:revision 1 .
 
 djr:R-3424 a djr:Obligation ;
-    skos:prefLabel "설계 명세 기계가독 채널 상시 작성 — 산문 추론 0·부재 fail-closed 전사"@ko ;
-    djr:currentExpression <https://numchida.com/ns/djr#R-3424@2026-09-01> .
+    skos:prefLabel "기계가독 다섯 채널과 선택 효과 — 무기재 의미·선언 검증·본문 미검증 분리"@ko ;
+    djr:currentExpression <https://numchida.com/ns/djr#R-3424@2026-09-11> .
 
 <https://numchida.com/ns/djr#R-3424@2026-09-01> a djr:Expression ;
     prov:specializationOf djr:R-3424 ;
     djr:revision 1 .
 
+<https://numchida.com/ns/djr#R-3424@2026-09-11> a djr:Expression ;
+    prov:specializationOf djr:R-3424 ;
+    prov:wasRevisionOf <https://numchida.com/ns/djr#R-3424@2026-09-01> ;
+    djr:revision 2 ;
+    djr:revisionKind djr:revision-amendment .
+
 djr:R-3425 a djr:Obligation ;
-    skos:prefLabel "file-plan 정규 블록 — 1행 1경로·조치 태그·금지 표기·삽화↔블록 차분 · 태그의 뜻은 기준선 기준(add 부재·update 실존(승격 형태 예외)·비후행 remove 실존·재라벨 도피는 형식 red)"@ko ;
-    djr:currentExpression <https://numchida.com/ns/djr#R-3425@2026-09-10> .
+    skos:prefLabel "file-plan 기준선 태그·제거와 실체화 0 선언 검증"@ko ;
+    djr:currentExpression <https://numchida.com/ns/djr#R-3425@2026-09-11> .
 
 <https://numchida.com/ns/djr#R-3425@2026-09-01> a djr:Expression ;
     prov:specializationOf djr:R-3425 ;
     djr:revision 1 .
 
 <https://numchida.com/ns/djr#R-3425@2026-09-03> a djr:Expression ;
     prov:specializationOf djr:R-3425 ;
     prov:wasRevisionOf <https://numchida.com/ns/djr#R-3425@2026-09-01> ;
     djr:revision 2 ;
     djr:revisionKind djr:revision-amendment .
 
 <https://numchida.com/ns/djr#R-3425@2026-09-10> a djr:Expression ;
     prov:specializationOf djr:R-3425 ;
     prov:wasRevisionOf <https://numchida.com/ns/djr#R-3425@2026-09-03> ;
     djr:revision 3 ;
     djr:revisionKind djr:revision-amendment .
 
+<https://numchida.com/ns/djr#R-3425@2026-09-11> a djr:Expression ;
+    prov:specializationOf djr:R-3425 ;
+    prov:wasRevisionOf <https://numchida.com/ns/djr#R-3425@2026-09-10> ;
+    djr:revision 4 ;
+    djr:revisionKind djr:revision-amendment .
+
 djr:R-3426 a djr:Obligation ;
-    skos:prefLabel "공개 심볼 전수 표기 — Base 닫힌 목록·베이스 유도표 공집합·값 축 유도 3행 등재(마이그레이션 칸 결손 보충)·`_`+대문자 사설 타입·필드 대입식 허용·수신자 관용 정규화·계약 필드·중첩 타입 소속 명시"@ko ;
-    djr:currentExpression <https://numchida.com/ns/djr#R-3426@2026-09-10b> .
+    skos:prefLabel "공개 심볼과 add/update 선언 후상태·본문 미검증 분리"@ko ;
+    djr:currentExpression <https://numchida.com/ns/djr#R-3426@2026-09-11> .
 
 <https://numchida.com/ns/djr#R-3426@2026-09-01> a djr:Expression ;
     prov:specializationOf djr:R-3426 ;
     djr:revision 1 .
 
 <https://numchida.com/ns/djr#R-3426@2026-09-02> a djr:Expression ;
     prov:specializationOf djr:R-3426 ;
     prov:wasRevisionOf <https://numchida.com/ns/djr#R-3426@2026-09-01> ;
     djr:revision 2 ;
     djr:revisionKind djr:revision-amendment .
@@ -1737,23 +1755,29 @@
     prov:wasRevisionOf <https://numchida.com/ns/djr#R-3426@2026-09-03> ;
     djr:revision 4 ;
     djr:revisionKind djr:revision-amendment .
 
 <https://numchida.com/ns/djr#R-3426@2026-09-10b> a djr:Expression ;
     prov:specializationOf djr:R-3426 ;
     prov:wasRevisionOf <https://numchida.com/ns/djr#R-3426@2026-09-10> ;
     djr:revision 5 ;
     djr:revisionKind djr:revision-amendment .
 
+<https://numchida.com/ns/djr#R-3426@2026-09-11> a djr:Expression ;
+    prov:specializationOf djr:R-3426 ;
+    prov:wasRevisionOf <https://numchida.com/ns/djr#R-3426@2026-09-10b> ;
+    djr:revision 6 ;
+    djr:revisionKind djr:revision-amendment .
+
 djr:R-3427 a djr:Obligation ;
-    skos:prefLabel "경계 import 표 — 검사기 판정 관련 경계 import 전부(테스트 파일 포함) · 경계 3분류(BC 밖 · BC 내부 층 경계 중 검사기 판정 항목 — 잎→port 예외 import 도 행으로 · 그 밖 재량) · 3단 실존 판정 입력(이 브랜치 기준 · 행 삭제 = 채널 은폐 · 부재 update 는 형식 red 선행·승격 예외분만 ⑴)"@ko ;
-    djr:currentExpression <https://numchida.com/ns/djr#R-3427@2026-09-10> .
+    skos:prefLabel "경계 import 실존·전사와 선언 출처 검증 분리"@ko ;
+    djr:currentExpression <https://numchida.com/ns/djr#R-3427@2026-09-11> .
 
 <https://numchida.com/ns/djr#R-3427@2026-09-01> a djr:Expression ;
     prov:specializationOf djr:R-3427 ;
     djr:revision 1 .
 
 <https://numchida.com/ns/djr#R-3427@2026-09-03> a djr:Expression ;
     prov:specializationOf djr:R-3427 ;
     prov:wasRevisionOf <https://numchida.com/ns/djr#R-3427@2026-09-01> ;
     djr:revision 2 ;
     djr:revisionKind djr:revision-amendment .
@@ -1769,63 +1793,87 @@
     prov:wasRevisionOf <https://numchida.com/ns/djr#R-3427@2026-09-03b> ;
     djr:revision 4 ;
     djr:revisionKind djr:revision-amendment .
 
 <https://numchida.com/ns/djr#R-3427@2026-09-10> a djr:Expression ;
     prov:specializationOf djr:R-3427 ;
     prov:wasRevisionOf <https://numchida.com/ns/djr#R-3427@2026-09-04> ;
     djr:revision 5 ;
     djr:revisionKind djr:revision-amendment .
 
+<https://numchida.com/ns/djr#R-3427@2026-09-11> a djr:Expression ;
+    prov:specializationOf djr:R-3427 ;
+    prov:wasRevisionOf <https://numchida.com/ns/djr#R-3427@2026-09-10> ;
+    djr:revision 6 ;
+    djr:revisionKind djr:revision-amendment .
+
 djr:R-3428 a djr:Obligation ;
-    skos:prefLabel "물리 신호 어노테이션 — markers/base/client 정형·무기재=물리 신호 없음"@ko ;
-    djr:currentExpression <https://numchida.com/ns/djr#R-3428@2026-09-10> .
+    skos:prefLabel "물리 신호 — add 부재·update marker 현행 유지/최종 목록·미지원 S5"@ko ;
+    djr:currentExpression <https://numchida.com/ns/djr#R-3428@2026-09-11> .
 
 <https://numchida.com/ns/djr#R-3428@2026-09-01> a djr:Expression ;
     prov:specializationOf djr:R-3428 ;
     djr:revision 1 .
 
 <https://numchida.com/ns/djr#R-3428@2026-09-10> a djr:Expression ;
     prov:specializationOf djr:R-3428 ;
     prov:wasRevisionOf <https://numchida.com/ns/djr#R-3428@2026-09-01> ;
     djr:revision 2 ;
     djr:revisionKind djr:revision-amendment .
 
+<https://numchida.com/ns/djr#R-3428@2026-09-11> a djr:Expression ;
+    prov:specializationOf djr:R-3428 ;
+    prov:wasRevisionOf <https://numchida.com/ns/djr#R-3428@2026-09-10> ;
+    djr:revision 3 ;
+    djr:revisionKind djr:revision-amendment .
+
 djr:R-3429 a djr:Obligation ;
-    skos:prefLabel "입장 표 header 영문 정본 6열 고정·셀 내 raw 파이프 금지"@ko ;
-    djr:currentExpression <https://numchida.com/ns/djr#R-3429@2026-09-01> .
+    skos:prefLabel "입장 표 6열·첫 artifact add/update 결합·후속 주소 비전파"@ko ;
+    djr:currentExpression <https://numchida.com/ns/djr#R-3429@2026-09-11> .
 
 <https://numchida.com/ns/djr#R-3429@2026-09-01> a djr:Expression ;
     prov:specializationOf djr:R-3429 ;
     djr:revision 1 .
+
+<https://numchida.com/ns/djr#R-3429@2026-09-11> a djr:Expression ;
+    prov:specializationOf djr:R-3429 ;
+    prov:wasRevisionOf <https://numchida.com/ns/djr#R-3429@2026-09-01> ;
+    djr:revision 2 ;
+    djr:revisionKind djr:revision-amendment .
 
 djr:R-3430 a djr:Obligation ;
     skos:prefLabel "예외 번역표 기계 블록 — published 예외↔raise 창구 표"@ko ;
     djr:currentExpression <https://numchida.com/ns/djr#R-3430@2026-09-10> .
 
 <https://numchida.com/ns/djr#R-3430@2026-09-01> a djr:Expression ;
     prov:specializationOf djr:R-3430 ;
     djr:revision 1 .
 
 <https://numchida.com/ns/djr#R-3430@2026-09-10> a djr:Expression ;
     prov:specializationOf djr:R-3430 ;
     prov:wasRevisionOf <https://numchida.com/ns/djr#R-3430@2026-09-01> ;
     djr:revision 2 ;
     djr:revisionKind djr:revision-amendment .
 
 djr:R-3431 a djr:Prohibition ;
-    skos:prefLabel "machine 마커 concrete 블록 한정 — 템플릿·예시 인용 부착 금지"@ko ;
-    djr:currentExpression <https://numchida.com/ns/djr#R-3431@2026-09-01> .
+    skos:prefLabel "machine 마커 concrete 계획 한정·명시 효과와 admin 소비 범위"@ko ;
+    djr:currentExpression <https://numchida.com/ns/djr#R-3431@2026-09-11> .
 
 <https://numchida.com/ns/djr#R-3431@2026-09-01> a djr:Expression ;
     prov:specializationOf djr:R-3431 ;
     djr:revision 1 .
+
+<https://numchida.com/ns/djr#R-3431@2026-09-11> a djr:Expression ;
+    prov:specializationOf djr:R-3431 ;
+    prov:wasRevisionOf <https://numchida.com/ns/djr#R-3431@2026-09-01> ;
+    djr:revision 2 ;
+    djr:revisionKind djr:revision-amendment .
 
 <https://numchida.com/ns/djr#d/dddjango/agents/design-architect.md> a djr:Document ;
     skos:prefLabel "agent-design-architect"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/agents/design-architect.md/s001> a djr:Section ;
     djr:headingSnapshot "---"@ko ;
     djr:inDocument <https://numchida.com/ns/djr#d/dddjango/agents/design-architect.md> ;
     djr:sectionOwner djr:owner-graph .
 
 <https://numchida.com/ns/djr#s/dddjango/agents/design-architect.md/s001/b1> a djr:Block ;
@@ -1965,21 +2013,21 @@
     djr:kind djr:kind-norm ;
     djr:order 10 ;
     djr:statesNorm djr:R-1611, djr:R-1612, djr:R-1613 ;
     djr:text "9. **`BC ErrorSchema`**: `dddjango-code-json`이면 error-BC별 common shape를 따르며 slot 6이 지정한 식별자 field 하나를 해당 BC `ErrorCode`로 좁힌 base Schema와 경로를 기록하고 public BC error가 없는 BC만 `none`일 수 있다. 좁힌 식별자 field는 공통의 default를 잃어 required여도 canon이다(식별자 field 한정·ErrorCode 좁힘 동반일 때만 — 2026-08-15). `preserve-established`이면 관찰된 profile-native status-specific schema/response artifact 또는 evidence가 있는 `none | not applicable`을 기록하고 `BC ErrorSchema`을 강제하지 않는다.\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/agents/design-architect.md/s005/b11> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/agents/design-architect.md/s005> ;
     djr:kind djr:kind-norm ;
     djr:order 11 ;
     djr:statesNorm djr:R-1614, djr:R-1615, djr:R-1616, djr:R-1617, djr:R-1618 ;
-    djr:text "10. **`prepared error mapping`**: `dddjango-code-json`이면 concrete domain/application exception 또는 조회의 `None` → no-arg concrete `ErrorSchema`, 또는 event-specific 값으로 명시적으로 채운 BC base `ErrorSchema` → controller의 direct `Status(<승인된 HTTP status 표현>, error)` chain과 각 output의 slot-6 exact literal body/approved header를 표로 기록한다. internal failure type과 output object를 명확히 구분한다. 여러 internal failures가 하나의 public ErrorCode로 수렴할 수 있다. raw infra failure는 기본 500이고, 승인된 안정적 public meaning이 있을 때만 consuming BC의 internal exception으로 정규화한 뒤 `ErrorSchema`을 만든다. `preserve-established`이면 관찰된 profile-native preparation/mapping artifact·behavior 또는 evidence가 있는 `none | not applicable`을 기록하고 code-profile chain을 강제하지 않는다.\n"@ko .
+    djr:text "10. **`prepared error mapping`**: `dddjango-code-json`이면 concrete domain/application exception 또는 조회의 `None` → no-arg concrete `ErrorSchema`, 또는 event-specific 값으로 명시적으로 채운 BC base `ErrorSchema` → controller의 direct `Status(<승인된 HTTP status 표현>, error)` chain과 각 output의 slot-6 exact literal body/approved header를 표로 기록한다. internal failure type과 output object를 명확히 구분한다. 여러 internal failures가 하나의 public ErrorCode로 수렴할 수 있다. 이미 잡은 IntegrityError의 승인된 알려진 제약 실패는 구체 계약 예외로, 나머지는 승인된 일반 저장소 실패 계약으로 번역한다. repository 실패 계약은 domain 소유, capability port 실패 계약은 해당 port 소유다. 이 내부 정규화는 공개 HTTP 오류 승인이 아니므로 일반 저장소 실패의 외부 응답은 기존 safe 500을 유지한다. 새 ErrorCode/ErrorSchema/4xx/503을 만들지 않는다. 잡지 않은 unknown 인프라 오류를 새로 catch-all하지 않는다. 안정된 public meaning이 별도로 승인된 경우에만 그 외부 계약에 맞는 controller mapping을 한다. 이미 선언된 계약 예외의 관찰 후 재던짐은 허용한다. `preserve-established`이면 관찰된 profile-native preparation/mapping artifact·behavior 또는 evidence가 있는 `none | not applicable`을 기록하고 code-profile chain을 강제하지 않는다.\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/agents/design-architect.md/s005/b12> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/agents/design-architect.md/s005> ;
     djr:kind djr:kind-norm ;
     djr:order 12 ;
     djr:statesNorm djr:R-1619, djr:R-1620, djr:R-1621, djr:R-1622, djr:R-1623, djr:R-1624, djr:R-1625 ;
     djr:text "11. **`controller mapping`**: `dddjango-code-json`이면 slot 10의 internal failure 형태에 따라 두 path 중 하나를 명시한다. exception path는 endpoint별 input preparation 뒤 정확히 한 번의 application call만 narrow `try`에 두고 승인된 concrete exception 또는 exception tuple만 catch한다. `None` path는 조회 use case가 대상이 없어 `None`을 돌려주는 경우에만 고르고, artificial `try`/`catch` 없이 application call을 정확히 한 번 실행한 뒤 그 직후 `is None` branch하며 exception을 fabricate하거나 raise하지 않는다. 실패가 둘 이상이거나 사유가 있으면 exception path다 — 실패를 Result variant·outcome 값으로 설계하지 않는다(`<use_case>_result.py`엔 성공 한 벌만 — #571). 두 path 모두 승인된 no-arg concrete 또는 event-specific 값으로 채운 BC-base `ErrorSchema`을 만들고, 승인된 header를 주입된 응답용(temporal) Django `HttpResponse`에 설정한 뒤 two-argument `Status(<literal/status constant 또는 slot-6 body field>, error)`를 직접 return한다. `status` body property를 발명하지 않는다. error helper/handler/factory/serializer/table 또는 mapping 추출은 만들지 않는다. `preserve-established`이면 관찰된 profile-native controller/handler mapping 또는 evidence가 있는 `none | not applicable`을 기록하고 direct `Status`를 강제하지 않는다.\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/agents/design-architect.md/s005/b13> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/agents/design-architect.md/s005> ;
@@ -2133,49 +2181,49 @@
     djr:kind djr:kind-norm ;
     djr:order 32 ;
     djr:statesNorm djr:R-1748, djr:R-1749 ;
     djr:text "  입장 표와 별도로 현재 계약의 유지·변경·종료·부재 의무를 짧게 설명해 각 행의 근거를 추적 가능하게 한다. 순수 구현 버그 수정도 관련 기존 coverage와 독자 failure를 판정해 `reuse/retain/add` 중 하나로 기록하며, 단순히 `테스트 계약 변화 없음`으로 심사를 생략하지 않는다.\n\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/agents/design-architect.md/s005/b33> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/agents/design-architect.md/s005> ;
     djr:kind djr:kind-norm ;
     djr:order 33 ;
     djr:statesNorm djr:R-3424, djr:R-3431 ;
-    djr:text "- **기계가독 채널(machine blocks)**(lens 무관, 항상 작성 — 12-slot 부재가 적법한 레인에서도 아래 블록·입장 표 규율은 상시다): 명세의 파일 계획·공개 심볼·경계 import·물리 신호·예외 번역은 산문 서술과 «별개로» 아래 다섯 정본 문법으로 성문한다 — pre-gate(`design_pregate.py`)는 이 채널만을 전사 재료로 쓰고 산문에서 추론하는 재료는 0이다. **채널에 없으면 «부재»로 전사된다(fail-closed)** — 부재가 위반이면 red 가 나는 것이 정답이다(예: 마커 무기재 → «설계가 물리 신호를 안 정했다»는 진탐). `<!-- machine: … -->` 마커는 **concrete 계획 블록에만** 단다 — 표준 140행 템플릿·예시 인용에 달지 않는다(인용과 실계획의 구별이 파서의 유일한 판별 근거다). *왜* — 21레인 실측에서 파일 계획 방언이 6종이라, 형식 규범 없이는 어떤 결정적 파싱도 성립하지 않았다.\n"@ko .
+    djr:text "- **기계가독 채널(machine blocks)**(lens 무관, 항상 작성 — 12-slot 부재가 적법한 레인에서도 아래 블록·입장 표 규율은 상시다): 명세의 파일 계획·공개 심볼·경계 import·물리 신호·예외 번역은 산문 서술과 «별개로» 기존 다섯 정본 문법으로 성문하고, 효과는 선택형 여섯 번째 입력으로 적는다 — pre-gate(`design_pregate.py`)는 이 채널만을 전사 재료로 쓰고 산문에서 추론하는 재료는 0이다. **채널의 무기재 의미를 구분한다** — add의 물리 신호 무기재는 부재로 전사하고, update marker 무기재는 현행 유지, 효과 무기재는 S5 미검증이다. 부재가 위반인 채널만 red다. `<!-- machine: … -->` 마커는 **concrete 계획 블록에만** 단다 — 표준 140행 템플릿·예시 인용에 달지 않는다(인용과 실계획의 구별이 파서의 유일한 판별 근거다). **명시 효과**는 `<!-- machine: use-case-effects -->` + ```effects 펜스에 `경로.py::UseCase read-only uow=none` 또는 `경로.py::UseCase write uow=<타입식>`으로 적는다. 어휘는 `read-only`/`write`, UoW는 `none` 또는 비어 있지 않은 타입식이며 add/update의 선행 클래스 선언에만 결합한다. 중복/상충·잘못된 어휘/타입식·선행 클래스 부재는 형식 red다. 명시 read-only+UoW와 출처가 확인된 UoW 주입의 모순은 선언 #197 확정, 미해소 출처는 후보, write 효과의 주입 불일치는 채널 메모다. 출처 결합 DTO의 공개 Result/Out/Response에서 사설·중첩 타입과 명시 별칭·표준 컨테이너를 따라 확인한 aggregate/entity 누수는 선언 #202 확정이고 VO/shared VO는 허용한다. 이름만 같거나 동적/불명 출처는 후보이며 OHS에 domain import를 합성하지 않는다. 선언 확정은 architect·해당 설계 리뷰/감수자가 처분하고 후보는 확인 질문으로 남긴다. S2의 내부 모순 사각은 이 명시 효과·출처 결합 DTO 지원 밖에 남는다. S1 생성 본문 미검증은 실제 구현 검증을 대신하지 않는다.\n\n**admin context 판정**: #493 주석 존재 유지 · #645 framework 소유 슬롯 Any 제한 허용 · #646 제네릭 런타임 안전 유지 · #647 열린 UI context 조립/병합/전달 허용 · #650 실제 JSON 소비 검증 유지다. 출처가 확인된 Django admin 및 Parler admin 계열의 고정 framework 슬롯에만 적용한다. `extra_context`/`context`의 받기·each_context·UI dict·copy/update·고정 UI 키 쓰기·framework render 전달과 연결된 private 전달 helper의 매개변수·반환·지역 context 주석을 허용한다. form/inline/media의 별도 조립은 context의 허용을 취소하지 않는다. 컨테이너 부재 처리와 request UI metadata의 담기·전달도 허용한다. 업무 읽기·비교·계산·상태 변경 또는 ORM/use case/업무 함수로의 값 전달은 실제 소비이므로 그 자리부터 기존 규칙을 적용한다. 출처나 소비가 미해소 또는 동적/재귀 호출로 escape한 연결 context는 후보로 남겨 확인한다. 이름만 context인 값·같은 함수의 별도 업무 dict·framework 고정 kwargs 밖 bare Any·admin 클래스/경로 전체는 면제하지 않는다. 생성 private helper는 본문이 없으므로 정확히 결합된 열린 dict 슬롯의 #645/#647만 S1 미검증으로 보고하고 G2에서 실제 소비 흐름으로 다시 판단한다.\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/agents/design-architect.md/s005/b34> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/agents/design-architect.md/s005> ;
     djr:kind djr:kind-norm ;
     djr:order 34 ;
     djr:statesNorm djr:R-3425 ;
-    djr:text "- **파일 계획 정규 블록**: `<!-- machine: file-plan -->` 마커 + ```paths 펜스. 1행 = `<태그> <경로>`(태그 선행·공백 구분·경로는 project-relative — 태그는 `add|update|remove[@Ln]|empty`)이고 `#` 주석만 허용한다. 브레이스 전개·`·` 병렬·`*`/`…` 축약·미해소 `<placeholder>`·승격 폴더 표기(경로는 언제나 `<칸>.py` — 동명 폴더 승격은 구현 캐스케이드 소유)·**동일 경로의 태그 이중 서술**은 전부 형식 위반이다(이중 서술은 파서 결정 불능을 낳는다). glyph 트리 삽화를 남기려면 블록에서 렌더해 생성하거나 파서의 삽화↔블록 차분 판정을 받는다 — 같은 계획의 이중 표현이 서로 어긋나는 드리프트 축을 봉쇄한다. **태그의 뜻은 기준선 기준이다**(G1 시점 HEAD — Phase 2 재발화 시 `--base` 기준선 · 2026-09-03 차단 승격): `add` = 기준선에 없는 경로(실존하면 형식 red «add 충돌») · `update` = 기준선에 실존하는 경로(부재면 형식 red «update 대상 부재» — 그 경로는 `add` 로 적는다 · 유효 승격 형태 `<칸>/__init__.py` ∧ `<칸>/<칸>.py` 의 기준선 실존은 실존이다) · `remove[@Ln]` = 기준선 실존 경로(비후행 remove 의 부재는 형식 red «remove 대상 부재» — 예외 없음 · 후행 `@Ln` 은 판정 밖 · `--base` 기준선은 이동하지 않으므로(재발화 판형 ②) 기실현 remove 는 실존이다 · 기준선에도 없는(승인 전에 이미 지워진) 경로는 remove 행을 거둔다) · `empty` = 새 빈 파일(add 와 같은 «새 파일» 태그 — 기준선 실존이면 형식 red «empty 충돌» · 기실현이면 `update`). 구형 명세에 블록을 소급 작성할 때 기실현 경로는 전부 `update` 다 — 실체화 0 이 나오면 그것이 정답이다(`add` 를 `update` 로 바꿔 red 를 피하는 것은 형식 red 로 잡힌다). 비후행 remove를 전사한 뒤 그 경로들의 조상 중 최종 사본에서 빈 부모 디렉터리만 정리한다(dirty overlay 선삭제 포함). 남은 파일(0B·init·미추적·add/empty 포함)이 있거나 후행 remove 실물이 남으면 보존하며, 무관한 빈 디렉터리와 symlink 경유 경로는 정리하지 않는다. 폴더 정리는 파일 실체화 건수와 별도로 보고한다 — 파일 실효 조치가 없으면 기존 실존 판정 뒤 skip한다. remove만 있는 BC를 신규 골격으로 다시 만들지 않는다.\n"@ko .
+    djr:text "- **파일 계획 정규 블록**: `<!-- machine: file-plan -->` 마커 + ```paths 펜스. 1행 = `<태그> <경로>`(태그 선행·공백 구분·경로는 project-relative — 태그는 `add|update|remove[@Ln]|empty`)이고 `#` 주석만 허용한다. 브레이스 전개·`·` 병렬·`*`/`…` 축약·미해소 `<placeholder>`·승격 폴더 표기(경로는 언제나 `<칸>.py` — 동명 폴더 승격은 구현 캐스케이드 소유)·**동일 경로의 태그 이중 서술**은 전부 형식 위반이다(이중 서술은 파서 결정 불능을 낳는다). glyph 트리 삽화를 남기려면 블록에서 렌더해 생성하거나 파서의 삽화↔블록 차분 판정을 받는다 — 같은 계획의 이중 표현이 서로 어긋나는 드리프트 축을 봉쇄한다. **태그의 뜻은 기준선 기준이다**(G1 시점 HEAD — Phase 2 재발화 시 `--base` 기준선 · 2026-09-03 차단 승격): `add` = 기준선에 없는 경로(실존하면 형식 red «add 충돌») · `update` = 기준선에 실존하는 경로(부재면 형식 red «update 대상 부재» — 그 경로는 `add` 로 적는다 · 유효 승격 형태 `<칸>/__init__.py` ∧ `<칸>/<칸>.py` 의 기준선 실존은 실존이다) · `remove[@Ln]` = 기준선 실존 경로(비후행 remove 의 부재는 형식 red «remove 대상 부재» — 예외 없음 · 후행 `@Ln` 은 판정 밖 · `--base` 기준선은 이동하지 않으므로(재발화 판형 ②) 기실현 remove 는 실존이다 · 기준선에도 없는(승인 전에 이미 지워진) 경로는 remove 행을 거둔다) · `empty` = 새 빈 파일(add 와 같은 «새 파일» 태그 — 기준선 실존이면 형식 red «empty 충돌» · 기실현이면 `update`). 구형 명세에 블록을 소급 작성할 때 기실현 경로는 전부 `update` 다 — 실체화 0도 적법하며 선언 검증은 계속 수행한다(`add` 를 `update` 로 바꿔 red 를 피하는 것은 형식 red 로 잡힌다). 비후행 remove를 전사한 뒤 그 경로들의 조상 중 최종 사본에서 빈 부모 디렉터리만 정리한다(dirty overlay 선삭제 포함). 남은 파일(0B·init·미추적·add/empty 포함)이 있거나 후행 remove 실물이 남으면 보존하며, 무관한 빈 디렉터리와 symlink 경유 경로는 정리하지 않는다. 폴더 정리는 파일 실체화 건수와 별도로 보고한다 — 파일 실효 조치가 없어도 선언 검증과 기존 실존 판정을 수행한 뒤 확정 없는 경우 skip한다. remove만 있는 BC를 신규 골격으로 다시 만들지 않는다.\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/agents/design-architect.md/s005/b35> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/agents/design-architect.md/s005> ;
     djr:kind djr:kind-norm ;
     djr:order 35 ;
     djr:statesNorm djr:R-3426 ;
-    djr:text "- **공개 심볼 표기**: 자리표시자 실현 파일의 **공개 심볼 전부**를 `<!-- machine: symbols -->` 마커 + ```symbols 펜스에 적는다(«대표 1회»가 아니라 전수다) — 1행 = `경로.py::Symbol(Base) {필드, …}`(Symbol 은 대문자 선두 또는 `_`+대문자 선두 — 주 계약이 참조하는 사설 보조 타입 `_Item` 도 적는다: 파서가 클래스로 분류하고 검사기의 사설 면제 판정 경로를 스텁이 그대로 탄다 · 소문자 선두는 함수다) · 메서드 행 `경로.py::Symbol.method(파라미터) -> 반환`(수신자는 무어노테이션 `self`/`cls` 에 한해 적어도·안 적어도 된다 — 실행기 파서가 정규화한다; 어노테이션 수신자는 중복 합성으로 형식 red 가 된다) · 필드 = `name: Type[ = default]` · `NAME = \"literal\"`(enum 멤버) · `name = <식>`(Django 필드 대입식 등)만 허용 — 타입도 값도 없는 bare 이름은 형식 red 다. Base 병기가 의무인 종류는 재량 목록이 아니라 **검사기 소스에서 기계 추출한 닫힌 목록**(소성물 `scripts/pregate_symbol_kinds.json` — rulepack 과 함께 재생성)이고, 명명규약으로 유도 가능한 생략은 **성문 유도표**(final.md §1 칸→베이스 결정표 — **아직 성문 전이다: 성문 전에는 생략 허용분이 공집합이라 전 심볼을 명기한다**) 등재분에 한한다 — 단 **값 축 유도 3행은 성문 등재됐다**(2026-09-02 · 3행째 2026-09-03): django_* `apps.py` 의 `name`(앱 폴더 전체 점 경로)/`label`(bc명) 정형, models/ 칸 `*Model` 의 `Meta.db_table`(`<bc>_<entity_snake>` — #630 유도 규칙), 그리고 마이그레이션 칸(`migrations/NNNN_*.py` — makemigrations 산출물 모양 #593: `Migration` 클래스 1 · `0001_` 만 `initial = True` · `migrations/__init__.py` 는 빈 파일)의 결손 보충. 이 결손은 실행기가 규약 상수로 보충하므로 규약대로라면 생략해도 된다(마이그레이션 칸은 file-plan `add` 만 적어도 된다 — symbols 전사가 있으면 전사 우선 · 규약 밖 값을 계획하면 반드시 기계 블록에 명기 — 산문 명기는 예보 표면 밖이다). **생략 = 규약 준수 확약**이다(생략분은 자동 정규화되어 위반 예보가 불능이 된다: 규약을 벗어날 계획이면 반드시 명기). published-language 칸(contract/·published_error)의 심볼은 **필드 목록**(`code` 필드 유무 포함)을 병기하고, **주 계약이 참조하는 보조·중첩 타입은 소속 파일을 명세가 명시**한다 — 안 박으면 coder 가 즉흥 배치해 예보·판정이 그 파일을 못 본다. **데코레이터·모듈 별칭도 symbols에 명시한다**: 클래스 행 뒤 `경로.py::Symbol @dataclass(frozen=True, slots=True, kw_only=True)`처럼 적는다(이름·속성 이름 또는 그 호출만 · 복수 행은 적은 순서대로 클래스 위에 전사 · 선행 클래스 없는 행은 형식 red). 이름/옵션/별칭은 원문 그대로이며 자동 dataclass 지정이나 import 추론은 없다 — `dataclass`·`dc.dataclass` 등 데코레이터와 모듈 별칭의 필요한 import는 boundary-imports에 명시한다. 모듈 별칭은 그 파일의 클래스/함수보다 먼저 `경로.py::alias 이름[: 타입] = 별칭식`으로 적는다. TYPE_CHECKING 분기는 `경로.py::alias[TYPE_CHECKING] _BookAdminBase: TypeAlias = admin.ModelAdmin[BookModel]` 다음에 `경로.py::alias[else] _BookAdminBase: type[admin.ModelAdmin] = admin.ModelAdmin`을 적는다(같은 파일·같은 이름의 인접한 유효 두 행, 주석/빈 줄 제외). 필요한 `TYPE_CHECKING`·`TypeAlias`·admin·모델 import는 boundary-imports에서 공급한다. 별칭은 단일 이름 Assign 또는 값 있는 AnnAssign이고 우변은 이름·속성·타입 첨자 및 그 내부 타입 표현식으로 한정한다(호출·복합문·클래스/함수 정의 불가). import 뒤 클래스 앞에 if TYPE_CHECKING/else와 두 대입의 어노테이션을 보존해 전사한다. 누락 분기·중복 별칭·다른 이름의 else·클래스/함수 뒤 별칭은 형식 red다. 비-add의 데코레이터·별칭 행도 문법을 검증하며 그 재료로 기존 본문을 바꾸지 않는다 — 완결된 별칭 이름만 update 자기 해소 근거이고 데코레이터 행만으로 이름을 선언하지 않는다. 미기재는 부재이며 산문에서 보충하지 않는다. 마이그레이션 정형이 무시하는 별칭 재료는 채널 메모로 병기한다. **update OHS 신규 함수 전사**: 표준 `open_host_service/<area>/<area>_service.py` 실물에 symbols로 명시한 신규 모듈 함수만 기존 본문 뒤에 전사한다. 기존 함수·클래스·별칭의 수정과 다른 update 칸은 S5다. 기존 바인딩/새 함수/합성 helper 충돌, 전사할 신규 함수 없음, 실물 부재·승격 형태는 사유를 적고 미시뮬레이션으로 남긴다. 기존 본문을 대체하거나 checker에 선언 이름을 주입하지 않는다. 함수 본문은 계속 스텁이므로 G2 실검증을 대체하지 않는다.\n"@ko .
+    djr:text "- **공개 심볼 표기**: 자리표시자 실현 파일의 **공개 심볼 전부**를 `<!-- machine: symbols -->` 마커 + ```symbols 펜스에 적는다(«대표 1회»가 아니라 전수다) — 1행 = `경로.py::Symbol(Base) {필드, …}`(Symbol 은 대문자 선두 또는 `_`+대문자 선두 — 주 계약이 참조하는 사설 보조 타입 `_Item` 도 적는다: 파서가 클래스로 분류하고 검사기의 사설 면제 판정 경로를 스텁이 그대로 탄다 · 소문자 선두는 함수다) · 메서드 행 `경로.py::Symbol.method(파라미터) -> 반환`(수신자는 무어노테이션 `self`/`cls` 에 한해 적어도·안 적어도 된다 — 실행기 파서가 정규화한다; 어노테이션 수신자는 중복 합성으로 형식 red 가 된다) · 필드 = `name: Type[ = default]` · `NAME = \"literal\"`(enum 멤버) · `name = <식>`(Django 필드 대입식 등)만 허용 — 타입도 값도 없는 bare 이름은 형식 red 다. Base 병기가 의무인 종류는 재량 목록이 아니라 **검사기 소스에서 기계 추출한 닫힌 목록**(소성물 `scripts/pregate_symbol_kinds.json` — rulepack 과 함께 재생성)이고, 명명규약으로 유도 가능한 생략은 **성문 유도표**(final.md §1 칸→베이스 결정표 — **아직 성문 전이다: 성문 전에는 생략 허용분이 공집합이라 전 심볼을 명기한다**) 등재분에 한한다 — 단 **값 축 유도 3행은 성문 등재됐다**(2026-09-02 · 3행째 2026-09-03): django_* `apps.py` 의 `name`(앱 폴더 전체 점 경로)/`label`(bc명) 정형, models/ 칸 `*Model` 의 `Meta.db_table`(`<bc>_<entity_snake>` — #630 유도 규칙), 그리고 마이그레이션 칸(`migrations/NNNN_*.py` — makemigrations 산출물 모양 #593: `Migration` 클래스 1 · `0001_` 만 `initial = True` · `migrations/__init__.py` 는 빈 파일)의 결손 보충. 이 결손은 실행기가 규약 상수로 보충하므로 규약대로라면 생략해도 된다(마이그레이션 칸은 file-plan `add` 만 적어도 된다 — symbols 전사가 있으면 전사 우선 · 규약 밖 값을 계획하면 반드시 기계 블록에 명기 — 산문 명기는 예보 표면 밖이다). **생략 = 규약 준수 확약**이다(생략분은 자동 정규화되어 위반 예보가 불능이 된다: 규약을 벗어날 계획이면 반드시 명기). published-language 칸(contract/·published_error)의 심볼은 **필드 목록**(`code` 필드 유무 포함)을 병기하고, **주 계약이 참조하는 보조·중첩 타입은 소속 파일을 명세가 명시**한다 — 안 박으면 coder 가 즉흥 배치해 예보·판정이 그 파일을 못 본다. **데코레이터·모듈 별칭도 symbols에 명시한다**: 클래스 행 뒤 `경로.py::Symbol @dataclass(frozen=True, slots=True, kw_only=True)`처럼 적는다(이름·속성 이름 또는 그 호출만 · 복수 행은 적은 순서대로 클래스 위에 전사 · 선행 클래스 없는 행은 형식 red). 이름/옵션/별칭은 원문 그대로이며 자동 dataclass 지정이나 import 추론은 없다 — `dataclass`·`dc.dataclass` 등 데코레이터와 모듈 별칭의 필요한 import는 boundary-imports에 명시한다. 모듈 별칭은 그 파일의 클래스/함수보다 먼저 `경로.py::alias 이름[: 타입] = 별칭식`으로 적는다. TYPE_CHECKING 분기는 `경로.py::alias[TYPE_CHECKING] _BookAdminBase: TypeAlias = admin.ModelAdmin[BookModel]` 다음에 `경로.py::alias[else] _BookAdminBase: type[admin.ModelAdmin] = admin.ModelAdmin`을 적는다(같은 파일·같은 이름의 인접한 유효 두 행, 주석/빈 줄 제외). 필요한 `TYPE_CHECKING`·`TypeAlias`·admin·모델 import는 boundary-imports에서 공급한다. 별칭은 단일 이름 Assign 또는 값 있는 AnnAssign이고 우변은 이름·속성·타입 첨자 및 그 내부 타입 표현식으로 한정한다(호출·복합문·클래스/함수 정의 불가). import 뒤 클래스 앞에 if TYPE_CHECKING/else와 두 대입의 어노테이션을 보존해 전사한다. 누락 분기·중복 별칭·다른 이름의 else·클래스/함수 뒤 별칭은 형식 red다. 비-add의 데코레이터·별칭 행도 문법을 검증하며 그 재료로 기존 본문을 바꾸지 않는다 — 완결된 별칭 이름만 update 자기 해소 근거이고 데코레이터 행만으로 이름을 선언하지 않는다. 미기재는 부재이며 산문에서 보충하지 않는다. 마이그레이션 정형이 무시하는 별칭 재료는 채널 메모로 병기한다. **update OHS 신규 함수 전사**: 표준 `open_host_service/<area>/<area>_service.py` 실물에 symbols로 명시한 신규 모듈 함수만 기존 본문 뒤에 전사한다. 기존 함수·클래스·별칭 본문 수정과 다른 update 칸의 본문 전사는 S5다. add/update의 명시 클래스·메서드·필드·별칭 선언은 별도로 보존해 효과/출처 결합 DTO의 선언 후상태를 검사한다. 이는 실물 클래스 본문을 덮어쓰지 않으며 본문 검증의 증명이 아니다. 기존 바인딩/새 함수/합성 helper 충돌, 전사할 신규 함수 없음, 실물 부재·승격 형태는 사유를 적고 미시뮬레이션으로 남긴다. 기존 본문을 대체하거나 checker에 선언 이름을 주입하지 않는다. 함수 본문은 계속 스텁이므로 G2 실검증을 대체하지 않는다.\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/agents/design-architect.md/s005/b36> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/agents/design-architect.md/s005> ;
     djr:kind djr:kind-norm ;
     djr:order 36 ;
     djr:statesNorm djr:R-3427 ;
-    djr:text "- **경계 import 표**: 검사기 판정에 관련되는 **경계 import 전부**를 `<!-- machine: boundary-imports -->` 마커의 ```imports 펜스(1행 = `<소비 파일>` + 탭 또는 공백 2+ + `<import 문 그대로>`)로 성문한다 — 타 BC OHS/contract·framework 공통만이 아니라, domain/contract 칸의 서드파티 라이브러리와 **테스트 파일의 경계 import 전부**(factories/타 급·타 BC OHS/published 계약 소비)까지. 파일별 전체 import 를 강제하는 것은 아니다 — **경계란 세 가지다**: ⑴ BC 밖(타 BC OHS/contract·framework 공통·서드파티·테스트 재료) ⑵ BC 안의 층 경계 중 **층 규율 검사기가 금지·예외 항목으로 판정하는 것**(driving 잎 → `application_layer/port/**` · domain → 상위 층 등 #92~#96·#185/#186 의 항목 — 잎이 port 예외를 잡을 계획이면 그 import 행을 그대로 적어 G1 에서 #93 예보를 받는다: 적을 수 없는 설계가 드러나는 것이 이 채널의 목적이다) ⑶ 그 밖은 구현 재량(성문 불요). 산문에만 적힌 경계 import 는 예보 표면 밖이다(pre-gate 보고 헤더의 사각 목록 S3). **각 행은 실행기가 격리 사본(기준선 + dirty overlay + 이 명세의 add)에서 3단 실존 판정**(⑴ 모듈 실존 · ⑵ 자리표시자 아님 · ⑶ 이름 최상위 정의)을 받는다(2026-09-03) — 저장소 밖(표준·서드파티)은 검사 밖, 이 명세가 add 하는 대상은 자기 해소(symbols 채널 소관 — 승격 폴더 부품 포함), ⑵ 는 이름 import(`from M import n`)의 대상 M 이 모듈일 때만이다. file-plan `update` 대상(사본에 실물이 있을 때만 — 기준선 부재 update 는 형식 red 로 먼저 서고, 유효 승격 형태 예외로 통과한 대상만 update 로는 생기지 않으므로 ⑴ 모듈 부재)의 이름은 그 칸의 symbols 에 선언하면 «자기 update 해소»이고 미선언이면 현재 표면에 있을 때만 실존 확인·아니면 판정 불능이다(표면은 이 명세 이후 상태 — update 로 새 심볼을 낼 계획이면 symbols 에 적는다 · ⑵⑶ 비적용). 판정 기준은 **이 브랜치**다 — 다른 워크트리·미머지 브랜치의 실물은 보지 않는다(부재 = «계약 실존 결손»으로 예보 · 소비자가 `update` 여도 행은 판정된다). 상류 소유 계약을 소비할 계획이면 그 행을 **그대로 적는다** — 결손 예보가 선행 조건의 기계 표현이며, 행을 빼서 green 을 만드는 것은 채널 은폐(경계 import 전수 의무 위반)다. 신규 함수가 전사되는 update OHS 서비스는 명시 boundary-imports도 충돌 없이 추가 가능한 경우에만 함께 전사한다. 기존 바인딩을 다른 출처로 덮는 등 안전한 합성이 불가하면 해당 서비스 전사를 통째로 보류하고 S5 사유를 보고한다. 행 전부를 대상으로 하는 기존 계약 실존/S′ 판정은 이 전사 여부와 별개로 유지한다.\n"@ko .
+    djr:text "- **경계 import 표**: 검사기 판정에 관련되는 **경계 import 전부**를 `<!-- machine: boundary-imports -->` 마커의 ```imports 펜스(1행 = `<소비 파일>` + 탭 또는 공백 2+ + `<import 문 그대로>`)로 성문한다 — 타 BC OHS/contract·framework 공통만이 아니라, domain/contract 칸의 서드파티 라이브러리와 **테스트 파일의 경계 import 전부**(factories/타 급·타 BC OHS/published 계약 소비)까지. 파일별 전체 import 를 강제하는 것은 아니다 — **경계란 세 가지다**: ⑴ BC 밖(타 BC OHS/contract·framework 공통·서드파티·테스트 재료) ⑵ BC 안의 층 경계 중 **층 규율 검사기가 금지·예외 항목으로 판정하는 것**(driving 잎 → `application_layer/port/**` · domain → 상위 층 등 #92~#96·#185/#186 의 항목 — 잎이 port 예외를 잡을 계획이면 그 import 행을 그대로 적어 G1 에서 #93 예보를 받는다: 적을 수 없는 설계가 드러나는 것이 이 채널의 목적이다) ⑶ 그 밖은 구현 재량(성문 불요). 산문에만 적힌 경계 import 는 예보 표면 밖이다(pre-gate 보고 헤더의 사각 목록 S3). **각 행은 실행기가 격리 사본(기준선 + dirty overlay + 이 명세의 add)에서 3단 실존 판정**(⑴ 모듈 실존 · ⑵ 자리표시자 아님 · ⑶ 이름 최상위 정의)을 받는다(2026-09-03) — 저장소 밖(표준·서드파티)은 검사 밖, 이 명세가 add 하는 대상은 자기 해소(symbols 채널 소관 — 승격 폴더 부품 포함), ⑵ 는 이름 import(`from M import n`)의 대상 M 이 모듈일 때만이다. file-plan `update` 대상(사본에 실물이 있을 때만 — 기준선 부재 update 는 형식 red 로 먼저 서고, 유효 승격 형태 예외로 통과한 대상만 update 로는 생기지 않으므로 ⑴ 모듈 부재)의 이름은 그 칸의 symbols 에 선언하면 «자기 update 해소»이고 미선언이면 현재 표면에 있을 때만 실존 확인·아니면 판정 불능이다(표면은 이 명세 이후 상태 — update 로 새 심볼을 낼 계획이면 symbols 에 적는다 · ⑵⑶ 비적용). 판정 기준은 **이 브랜치**다 — 다른 워크트리·미머지 브랜치의 실물은 보지 않는다(부재 = «계약 실존 결손»으로 예보 · 소비자가 `update` 여도 행은 판정된다). 상류 소유 계약을 소비할 계획이면 그 행을 **그대로 적는다** — 결손 예보가 선행 조건의 기계 표현이며, 행을 빼서 green 을 만드는 것은 채널 은폐(경계 import 전수 의무 위반)다. 신규 함수가 전사되는 update OHS 서비스는 명시 boundary-imports도 충돌 없이 추가 가능한 경우에만 함께 전사한다. 기존 바인딩을 다른 출처로 덮는 등 안전한 합성이 불가하면 해당 서비스 전사를 통째로 보류하고 S5 사유를 보고한다. 행 전부를 대상으로 하는 기존 계약 실존/S′ 판정은 이 전사 여부와 별개로 유지한다. S3의 물리 import 전사 범위와, 명시 import·별칭·타입으로 출처를 결합하는 선언 검증은 구별한다. 나머지 update 본문은 미검증이다.\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/agents/design-architect.md/s005/b37> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/agents/design-architect.md/s005> ;
     djr:kind djr:kind-norm ;
     djr:order 37 ;
     djr:statesNorm djr:R-3428, djr:R-3429 ;
-    djr:text "- **물리 신호 어노테이션**: 영구 테스트 입장 표의 `owner/path` 셀 안에 정형 어노테이션 `[markers: django_db,…] [base: TestCase] [client: yes]` 를 단다 — 테스트 물리 신호(마커·베이스·클라이언트)의 유일한 전사 채널이다. **무기재 = «물리 신호 없음»으로 전사된다(fail-closed)** — 마커를 안 적으면 red 가 그 결손을 알린다. 입장 표 header 는 영문 정본 6열(`candidate | protected contract/evidence | unique production failure | existing authoritative coverage | decision | owner/path`)로 고정하고 셀 안에 raw `|` 를 두지 않는다 — 열 구조가 곧 파서 계약이라, 열이 흔들리면 어노테이션 채널이 통째로 죽는다. owner/path에서 처음 나오는 Python 파일 주소(`경로.py` 또는 `경로.py::case`)가 그 행의 artifact다. code span과 bare 경로 모두 허용하며 앞선 `add` 같은 비경로 span은 건너뛴다. case 접미는 파일 주소 결합에서만 벗긴다(case 본문 전사 아님). 첫 파일 주소를 file-plan의 정확한 add 키에 결합하고, 뒤의 support/coverage 주소에는 신호를 전파하지 않는다. 첫 주소가 미등재·비-add여도 뒤 파일로 넘어가지 않는다.\n"@ko .
+    djr:text "- **물리 신호 어노테이션**: 영구 테스트 입장 표의 `owner/path` 셀 안에 정형 어노테이션 `[markers: django_db,…] [base: TestCase] [client: yes]` 를 단다 — 테스트 물리 신호(마커·베이스·클라이언트)의 유일한 전사 채널이다. **add 무기재 = 물리 신호 없음, update markers 무기재 = 기존 상태 유지**다. update의 `[markers:]`는 빈 목록, `[markers: slow]` 등은 module pytestmark 최종 목록의 교체다. 정적 Assign/AnnAssign/list/tuple·pytest 별칭을 지원하며 함수/class decorator·본문은 보존한다. 호출형·동적/중복/조건부/증분/subscript 변경·재바인딩 또는 update nodeid/class 주소는 S5다. update base/client는 미지원 S5이며 marker 후상태 성공이 본문 검증을 뜻하지 않는다. 입장 표 header 는 영문 정본 6열(`candidate | protected contract/evidence | unique production failure | existing authoritative coverage | decision | owner/path`)로 고정하고 셀 안에 raw `|` 를 두지 않는다 — 열 구조가 곧 파서 계약이라, 열이 흔들리면 어노테이션 채널이 통째로 죽는다. owner/path에서 처음 나오는 Python 파일 주소(`경로.py` 또는 `경로.py::case`)가 그 행의 artifact다. code span과 bare 경로 모두 허용하며 앞선 `add` 같은 비경로 span은 건너뛴다. case 접미는 파일 주소 결합에서만 벗긴다(case 본문 전사 아님). 첫 파일 주소를 file-plan의 정확한 add/update 키에 결합하고, 뒤의 support/coverage 주소에는 신호를 전파하지 않는다. 첫 주소가 미등재·비-add/update여도 뒤 파일로 넘어가지 않는다.\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/agents/design-architect.md/s005/b38> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/agents/design-architect.md/s005> ;
     djr:kind djr:kind-norm ;
     djr:order 38 ;
     djr:statesNorm djr:R-3430 ;
     djr:text "- **예외 번역표 기계 블록**: 이 명세가 이미 요구하는 예외 번역 산출물(도메인→published 매핑)을 `<!-- machine: exception-map -->` 마커의 ```exceptions 펜스(1행 = `<published 예외>` + 탭 또는 공백 2+ + `<raise 창구 파일>`)로 성문한다 — 번역표에 없는 published 예외는 어느 창구도 raise 하지 않는 «죽은 계약»으로 예보된다. add 창구 외에는, 명시 신규 함수가 실제 전사된 update OHS 서비스 파일에 한해 같은 파일 수준 raise helper로 전사한다. exception-map은 함수 주소가 아니므로 특정 함수의 raise 위치를 증명하지 않는다. 신규 함수가 없는 update 본문 변경과 산문에만 적힌 raise는 계속 S5이며, contract 안의 raise 진탐을 면제하지 않는다.\n\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/agents/design-architect.md/s005/b4> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/agents/design-architect.md/s005> ;

```

## ontology/rules/agent-design-review-api.ttl

Before SHA256: e83632a251018273422a9ed07d2471b824d1715e57b7c947e400020988aba101
After SHA256: 59106ddea0462475988cbcfdd1839f06c5d1a6ef8f72e6a4730ee5f275a32ba7

```diff
--- before/ontology/rules/agent-design-review-api.ttl
+++ after/ontology/rules/agent-design-review-api.ttl
@@ -570,26 +570,32 @@
 
 djr:R-2676 a djr:Prohibition ;
     skos:prefLabel "slot 10 — 공개 문자열의 str(exc) 자동 사용·sensitive data 노출 금지"@ko ;
     djr:currentExpression <https://numchida.com/ns/djr#R-2676@2026-08-22> .
 
 <https://numchida.com/ns/djr#R-2676@2026-08-22> a djr:Expression ;
     prov:specializationOf djr:R-2676 ;
     djr:revision 1 .
 
 djr:R-2677 a djr:Obligation ;
-    skos:prefLabel "slot 10 — raw infra 기본 500·승인된 안정 public meaning만 consuming BC internal exception 정규화 후 ErrorSchema 생성 확인"@ko ;
-    djr:currentExpression <https://numchida.com/ns/djr#R-2677@2026-08-22> .
+    skos:prefLabel "내부 실패 정규화와 공개 HTTP 계약 승인 분리 검수"@ko ;
+    djr:currentExpression <https://numchida.com/ns/djr#R-2677@2026-09-11> .
 
 <https://numchida.com/ns/djr#R-2677@2026-08-22> a djr:Expression ;
     prov:specializationOf djr:R-2677 ;
     djr:revision 1 .
+
+<https://numchida.com/ns/djr#R-2677@2026-09-11> a djr:Expression ;
+    prov:specializationOf djr:R-2677 ;
+    prov:wasRevisionOf <https://numchida.com/ns/djr#R-2677@2026-08-22> ;
+    djr:revision 2 ;
+    djr:revisionKind djr:revision-amendment .
 
 djr:R-2678 a djr:Exception ;
     skos:prefLabel "slot 10 — preserve의 profile-native preparation/mapping 또는 evidenced none|not applicable 인정·code-profile chain 미강제"@ko ;
     djr:currentExpression <https://numchida.com/ns/djr#R-2678@2026-08-22> .
 
 <https://numchida.com/ns/djr#R-2678@2026-08-22> a djr:Expression ;
     prov:specializationOf djr:R-2678 ;
     djr:revision 1 .
 
 djr:R-2679 a djr:Obligation ;
@@ -1099,21 +1105,21 @@
     djr:restates <https://numchida.com/ns/djr#s/dddjango/agents/design-architect.md/s005/b10> ;
     djr:statesNorm djr:R-2671, djr:R-2672, djr:R-2673 ;
     djr:text "9. **`BC ErrorSchema`**: `dddjango-code-json`은 common exact shape를 보존하면서 slot 6의 식별자 field 하나를 해당 BC Enum으로 좁힌 base이고 public BC error가 없는 BC만 `none`인지 본다. 좁힌 식별자 field는 공통의 default를 잃어 required여도 canon이다(식별자 field 한정·ErrorCode 좁힘 동반일 때만 — 2026-08-15). `preserve-established`는 observed profile-native status-specific schema/response artifact 또는 evidenced `none | not applicable`인지 보고 BC base를 강제하지 않는다.\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/agents/design-review-api.md/s006/b11> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/agents/design-review-api.md/s006> ;
     djr:kind djr:kind-norm ;
     djr:order 11 ;
     djr:restates <https://numchida.com/ns/djr#s/dddjango/agents/design-architect.md/s005/b11> ;
     djr:statesNorm djr:R-2674, djr:R-2675, djr:R-2676, djr:R-2677, djr:R-2678 ;
-    djr:text "10. **`prepared error mapping`**: `dddjango-code-json`은 concrete domain/application exception 또는 조회의 `None` → no-arg concrete `ErrorSchema`, 또는 event-specific 값으로 명시적으로 채운 BC base `ErrorSchema` → direct `Status(<승인된 HTTP status 표현>, error)` chain과 slot-6 exact literal body/approved header가 완전한지 본다. internal failure type과 output object를 혼동하면 blocker다. 공개 문자열은 `str(exc)`를 자동 사용하거나 sensitive data를 노출하면 안 된다. raw infra는 기본 500이고 approved stable public meaning만 consuming BC internal exception으로 정규화한 뒤 `ErrorSchema`을 만드는지 확인한다. `preserve-established`는 observed profile-native preparation/mapping 또는 evidenced `none | not applicable`인지 보고 code-profile chain을 강제하지 않는다.\n"@ko .
+    djr:text "10. **`prepared error mapping`**: `dddjango-code-json`은 concrete domain/application exception 또는 조회의 `None` → no-arg concrete `ErrorSchema`, 또는 event-specific 값으로 명시적으로 채운 BC base `ErrorSchema` → direct `Status(<승인된 HTTP status 표현>, error)` chain과 slot-6 exact literal body/approved header가 완전한지 본다. internal failure type과 output object를 혼동하면 blocker다. 공개 문자열은 `str(exc)`를 자동 사용하거나 sensitive data를 노출하면 안 된다. 이미 잡은 IntegrityError의 승인된 알려진 제약 실패는 구체 계약 예외로, 나머지는 승인된 일반 저장소 실패 계약으로 번역한다. repository 실패 계약은 domain 소유, capability port 실패 계약은 해당 port 소유다. 이 내부 정규화는 공개 HTTP 오류 승인이 아니므로 일반 저장소 실패의 외부 응답은 기존 safe 500을 유지한다. 새 ErrorCode/ErrorSchema/4xx/503을 만들지 않는다. 잡지 않은 unknown 인프라 오류를 새로 catch-all하지 않는다. 안정된 public meaning이 별도로 승인된 경우에만 그 외부 계약에 맞는 controller mapping을 한다. 이미 선언된 계약 예외의 관찰 후 재던짐은 허용한다. `preserve-established`는 observed profile-native preparation/mapping 또는 evidenced `none | not applicable`인지 보고 code-profile chain을 강제하지 않는다.\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/agents/design-review-api.md/s006/b12> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/agents/design-review-api.md/s006> ;
     djr:kind djr:kind-norm ;
     djr:order 12 ;
     djr:restates <https://numchida.com/ns/djr#s/dddjango/agents/design-architect.md/s005/b12> ;
     djr:statesNorm djr:R-2679, djr:R-2680, djr:R-2681, djr:R-2682, djr:R-2683, djr:R-2684, djr:R-2685 ;
     djr:text "11. **`controller mapping`**: `dddjango-code-json`은 slot 10의 internal failure 형태에 따라 두 path 중 하나가 선택됐는지 확인한다. exception path는 input preparation 뒤 정확히 한 번의 application call만 narrow `try`에 두고 승인된 concrete exception 또는 exception tuple만 catch해야 한다. `None` path는 조회 use case가 대상이 없어 `None`을 돌려주는 경우에만 선택돼야 하고, artificial `try`/`catch` 없이 application call을 정확히 한 번 실행한 뒤 그 직후 `is None` branch해야 하며, catch를 요구하거나 exception을 fabricate해 즉시 raise/catch하면 blocker다. 실패를 Result variant·outcome 값으로 설계한 명세는 blocker다(`<use_case>_result.py`엔 성공 한 벌만 — #571; exception path여야 한다). 두 path 모두 승인된 no-arg concrete 또는 event-specific 값으로 채운 BC-base `ErrorSchema`을 만들고, approved header를 주입된 응답용(temporal) Django `HttpResponse`에 설정한 뒤 two-argument `Status(<literal/status constant 또는 slot-6 body field>, error)`를 직접 return하는지 확인한다. `status` body property를 요구하면 blocker다. error helper/handler/factory/serializer/table 또는 mapping 추출로 이 semantic contract를 우회하면 발견으로 올리고 물리적 우회 여부는 discipline-reviewer에게 보낸다. `preserve-established`는 observed profile-native controller/handler mapping 또는 evidenced `none | not applicable`인지 보고 direct `Status`를 강제하지 않는다.\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/agents/design-review-api.md/s006/b13> a djr:Block ;

```

## ontology/rules/agent-discipline-reviewer.ttl

Before SHA256: 467e1e64963162052b340ea6e0e56e07eeb7d0d524fa1fc700282b32a7ec06fa
After SHA256: f95d45237c92e1ea22f799327de15b88b08677c6a20f371769b42e0b0ad4479b

```diff
--- before/ontology/rules/agent-discipline-reviewer.ttl
+++ after/ontology/rules/agent-discipline-reviewer.ttl
@@ -1686,26 +1686,32 @@
 
 djr:R-1036 a djr:Prohibition ;
     skos:prefLabel "global recognizer·retryable handler·문자열/SQLSTATE 분류 요구·신설 금지"@ko ;
     djr:currentExpression <https://numchida.com/ns/djr#R-1036@2026-08-22> .
 
 <https://numchida.com/ns/djr#R-1036@2026-08-22> a djr:Expression ;
     prov:specializationOf djr:R-1036 ;
     djr:revision 1 .
 
 djr:R-1037 a djr:Exception ;
-    skos:prefLabel "G1 명시 승인 시에만 owning infra/ACL의 정규화 후 controller 직접 흐름 mapping"@ko ;
-    djr:currentExpression <https://numchida.com/ns/djr#R-1037@2026-08-22> .
+    skos:prefLabel "내부 실패 계약 정규화와 safe 500 공개 경계"@ko ;
+    djr:currentExpression <https://numchida.com/ns/djr#R-1037@2026-09-11> .
 
 <https://numchida.com/ns/djr#R-1037@2026-08-22> a djr:Expression ;
     prov:specializationOf djr:R-1037 ;
     djr:revision 1 .
+
+<https://numchida.com/ns/djr#R-1037@2026-09-11> a djr:Expression ;
+    prov:specializationOf djr:R-1037 ;
+    prov:wasRevisionOf <https://numchida.com/ns/djr#R-1037@2026-08-22> ;
+    djr:revision 2 ;
+    djr:revisionKind djr:revision-amendment .
 
 djr:R-1038 a djr:Prohibition ;
     skos:prefLabel "raw infrastructure exception 합성·controller 직접 catch 우회 금지"@ko ;
     djr:currentExpression <https://numchida.com/ns/djr#R-1038@2026-08-22> .
 
 <https://numchida.com/ns/djr#R-1038@2026-08-22> a djr:Expression ;
     prov:specializationOf djr:R-1038 ;
     djr:revision 1 .
 
 djr:R-1039 a djr:Obligation ;
@@ -1970,26 +1976,32 @@
 
 djr:R-1070 a djr:Exception ;
     skos:prefLabel "ACL·upstream repository 안에서 승인 concrete로 소진된 실패의 누수 불인정"@ko ;
     djr:currentExpression <https://numchida.com/ns/djr#R-1070@2026-08-22> .
 
 <https://numchida.com/ns/djr#R-1070@2026-08-22> a djr:Expression ;
     prov:specializationOf djr:R-1070 ;
     djr:revision 1 .
 
 djr:R-1071 a djr:Exception ;
-    skos:prefLabel "raw DB/SDK/network unknown failure의 전수 집합 제외(safe framework 500 기본)"@ko ;
-    djr:currentExpression <https://numchida.com/ns/djr#R-1071@2026-08-22> .
+    skos:prefLabel "ACL known failure 전수 번역과 일반 내부 계약·공개 500 분리"@ko ;
+    djr:currentExpression <https://numchida.com/ns/djr#R-1071@2026-09-11> .
 
 <https://numchida.com/ns/djr#R-1071@2026-08-22> a djr:Expression ;
     prov:specializationOf djr:R-1071 ;
     djr:revision 1 .
+
+<https://numchida.com/ns/djr#R-1071@2026-09-11> a djr:Expression ;
+    prov:specializationOf djr:R-1071 ;
+    prov:wasRevisionOf <https://numchida.com/ns/djr#R-1071@2026-08-22> ;
+    djr:revision 2 ;
+    djr:revisionKind djr:revision-amendment .
 
 djr:R-1072 a djr:Obligation ;
     skos:prefLabel "ⓓ 후보 줄의 출력 계약(경로: 사실 — 물음 · exit 불산입)"@ko ;
     djr:currentExpression <https://numchida.com/ns/djr#R-1072@2026-08-22> .
 
 <https://numchida.com/ns/djr#R-1072@2026-08-22> a djr:Expression ;
     prov:specializationOf djr:R-1072 ;
     djr:revision 1 .
 
 djr:R-1073 a djr:Obligation ;
@@ -2234,26 +2246,32 @@
 
 djr:R-1103 a djr:Obligation ;
     skos:prefLabel "ⓓ#259 값인가 엔티티인가 물음(Q4)"@ko ;
     djr:currentExpression <https://numchida.com/ns/djr#R-1103@2026-08-22> .
 
 <https://numchida.com/ns/djr#R-1103@2026-08-22> a djr:Expression ;
     prov:specializationOf djr:R-1103 ;
     djr:revision 1 .
 
 djr:R-1104 a djr:Obligation ;
-    skos:prefLabel "ⓓ#268 타입 조합만으로 잘못된 값이 불가능한가(Q2)"@ko ;
-    djr:currentExpression <https://numchida.com/ns/djr#R-1104@2026-08-22> .
+    skos:prefLabel "닫힌 Enum 검증 제외·open Enum Q2와 트랜잭션 영역 후보 검수"@ko ;
+    djr:currentExpression <https://numchida.com/ns/djr#R-1104@2026-09-11> .
 
 <https://numchida.com/ns/djr#R-1104@2026-08-22> a djr:Expression ;
     prov:specializationOf djr:R-1104 ;
     djr:revision 1 .
+
+<https://numchida.com/ns/djr#R-1104@2026-09-11> a djr:Expression ;
+    prov:specializationOf djr:R-1104 ;
+    prov:wasRevisionOf <https://numchida.com/ns/djr#R-1104@2026-08-22> ;
+    djr:revision 2 ;
+    djr:revisionKind djr:revision-amendment .
 
 djr:R-1105 a djr:Obligation ;
     skos:prefLabel "ⓓ#301 «없을 때» 판정의 루트 메서드 표현 가능성"@ko ;
     djr:currentExpression <https://numchida.com/ns/djr#R-1105@2026-08-22> .
 
 <https://numchida.com/ns/djr#R-1105@2026-08-22> a djr:Expression ;
     prov:specializationOf djr:R-1105 ;
     djr:revision 1 .
 
 djr:R-1106 a djr:Obligation ;
@@ -2338,42 +2356,60 @@
 
 djr:R-1116 a djr:Obligation ;
     skos:prefLabel "ⓓ#629 이 입구가 안 와도 업무가 돌아가나"@ko ;
     djr:currentExpression <https://numchida.com/ns/djr#R-1116@2026-08-22> .
 
 <https://numchida.com/ns/djr#R-1116@2026-08-22> a djr:Expression ;
     prov:specializationOf djr:R-1116 ;
     djr:revision 1 .
 
 djr:R-1117 a djr:Obligation ;
-    skos:prefLabel "ⓓ#343 운영 기능인가 장고 배선인가"@ko ;
-    djr:currentExpression <https://numchida.com/ns/djr#R-1117@2026-08-22> .
+    skos:prefLabel "운영 기능/장고 배선·admin UI context 조립과 실제 소비 검수"@ko ;
+    djr:currentExpression <https://numchida.com/ns/djr#R-1117@2026-09-11> .
 
 <https://numchida.com/ns/djr#R-1117@2026-08-22> a djr:Expression ;
     prov:specializationOf djr:R-1117 ;
     djr:revision 1 .
 
+<https://numchida.com/ns/djr#R-1117@2026-09-11> a djr:Expression ;
+    prov:specializationOf djr:R-1117 ;
+    prov:wasRevisionOf <https://numchida.com/ns/djr#R-1117@2026-08-22> ;
+    djr:revision 2 ;
+    djr:revisionKind djr:revision-amendment .
+
 djr:R-1118 a djr:Obligation ;
-    skos:prefLabel "ⓓ#589 조건이 업무 판정인가(Q2)"@ko ;
-    djr:currentExpression <https://numchida.com/ns/djr#R-1118@2026-08-22> .
+    skos:prefLabel "표현 조건 업무 판정 Q2·admin context 출처/소비 미해소 후보"@ko ;
+    djr:currentExpression <https://numchida.com/ns/djr#R-1118@2026-09-11> .
 
 <https://numchida.com/ns/djr#R-1118@2026-08-22> a djr:Expression ;
     prov:specializationOf djr:R-1118 ;
     djr:revision 1 .
 
+<https://numchida.com/ns/djr#R-1118@2026-09-11> a djr:Expression ;
+    prov:specializationOf djr:R-1118 ;
+    prov:wasRevisionOf <https://numchida.com/ns/djr#R-1118@2026-08-22> ;
+    djr:revision 2 ;
+    djr:revisionKind djr:revision-amendment .
+
 djr:R-1119 a djr:Obligation ;
-    skos:prefLabel "ⓓ#227 자료를 원시값 인자로 펴서 넘길 수 있나"@ko ;
-    djr:currentExpression <https://numchida.com/ns/djr#R-1119@2026-08-22> .
+    skos:prefLabel "포트/어댑터 판정과 vendor 오류 속성 출처 후보 검수"@ko ;
+    djr:currentExpression <https://numchida.com/ns/djr#R-1119@2026-09-11> .
 
 <https://numchida.com/ns/djr#R-1119@2026-08-22> a djr:Expression ;
     prov:specializationOf djr:R-1119 ;
     djr:revision 1 .
+
+<https://numchida.com/ns/djr#R-1119@2026-09-11> a djr:Expression ;
+    prov:specializationOf djr:R-1119 ;
+    prov:wasRevisionOf <https://numchida.com/ns/djr#R-1119@2026-08-22> ;
+    djr:revision 2 ;
+    djr:revisionKind djr:revision-amendment .
 
 djr:R-1120 a djr:Obligation ;
     skos:prefLabel "ⓓ#233 무엇을 알고 싶은가가 이름에 있나(Q1)"@ko ;
     djr:currentExpression <https://numchida.com/ns/djr#R-1120@2026-08-22> .
 
 <https://numchida.com/ns/djr#R-1120@2026-08-22> a djr:Expression ;
     prov:specializationOf djr:R-1120 ;
     djr:revision 1 .
 
 djr:R-1121 a djr:Obligation ;
@@ -2960,21 +2996,21 @@
     djr:kind djr:kind-norm ;
     djr:order 22 ;
     djr:statesNorm djr:R-1023, djr:R-1024, djr:R-1025, djr:R-1026, djr:R-1027, djr:R-1028, djr:R-1029, djr:R-1030, djr:R-1031, djr:R-1032, djr:R-1033, djr:R-1034 ;
     djr:text "- **API instance·registrar·composition 규율**: active `dddjango-code-json` contract scope마다 project `<project>/api.py`가 API instance 하나를 소유한다. 각 BC의 side-effect-free api_router(`driving_layer/api/api_router.py`의 `register_<bc>_api` — final.md §1 9행)는 전달받은 API에 자기 controller만 등록하고, project `urls.py`가 각 registrar를 명시적으로 한 번 호출한 뒤 API를 mount한다. controller는 `auto_import=False`여야 하며 project API import·module-top-level 등록·dynamic registrar·import-time side effect·scope 안의 API 복수는 blocker다. HTTP registrar와 DI-only `composition_root/`(트리 2~4행)를 섞지 않고, root-local catalog/mapping 또는 registrar/composition lookalike도 직접 확인한다. controller 형태는 승인된 presentation 계약을 보존한다. 오류 대응, 특히 406/415를 이유로 승인된 class controller를 함수형 `Router`로 바꾸거나 별도 API instance로 격리하지 않는다. `preserve-established` scope 에서도 **registration/composition 은 이 표준으로 대조한다** — preserve 가 보존하는 것은 오류 wire 산출물이지 배선이 아니다(구 «native registration/API-instance layout 보존» 문구는 라운드 1′ 배선 답습의 통로로 실증되어 걷었다 — 2026-08-12). 배선 표준화가 오류 profile 이주를 뜻하지도 않는다 — 오류 산출물은 slot 승인대로 유지한다. Phase 1의 project-wide inventory와 mixed-profile sharing 점검은 profile에 관계없이 유지한다.\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/agents/discipline-reviewer.md/s007/b23> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/agents/discipline-reviewer.md/s007> ;
     djr:kind djr:kind-norm ;
     djr:order 23 ;
     djr:statesNorm djr:R-1035, djr:R-1036, djr:R-1037, djr:R-1038 ;
-    djr:text "- **raw infrastructure 기본 경계**: raw DB/SDK/network exception은 safe framework 500으로 둔다. global recognizer·retryable handler·문자열/SQLSTATE 분류를 요구하거나 새 code-profile에 추가하지 않는다. 특정 실패가 안정된 public meaning을 가진다고 G1에서 명시 승인된 경우에만 owning infra/ACL이 그 실패를 consuming BC의 own concrete domain/application exception으로 정규화하고, 그 BC controller가 위 직접 흐름으로 mapping한다. raw infrastructure exception을 합성하거나 controller에서 직접 catch하는 우회도 금지한다.\n"@ko .
+    djr:text "- **raw infrastructure 기본 경계**: raw DB/SDK/network exception은 safe framework 500으로 둔다. global recognizer·retryable handler·문자열/SQLSTATE 분류를 요구하거나 새 code-profile에 추가하지 않는다. 이미 잡은 IntegrityError의 승인된 알려진 제약 실패는 구체 계약 예외로, 나머지는 승인된 일반 저장소 실패 계약으로 번역한다. repository 실패 계약은 domain 소유, capability port 실패 계약은 해당 port 소유다. 이 내부 정규화는 공개 HTTP 오류 승인이 아니므로 일반 저장소 실패의 외부 응답은 기존 safe 500을 유지한다. 새 ErrorCode/ErrorSchema/4xx/503을 만들지 않는다. 잡지 않은 unknown 인프라 오류를 새로 catch-all하지 않는다. 안정된 public meaning이 별도로 승인된 경우에만 그 외부 계약에 맞는 controller mapping을 한다. 이미 선언된 계약 예외의 관찰 후 재던짐은 허용한다. raw infrastructure exception을 합성하거나 controller에서 직접 catch하는 우회도 금지한다.\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/agents/discipline-reviewer.md/s007/b24> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/agents/discipline-reviewer.md/s007> ;
     djr:kind djr:kind-norm ;
     djr:order 24 ;
     djr:statesNorm djr:R-1039, djr:R-1040, djr:R-1041 ;
     djr:text "- **`preserve-established` retryability 호환**: 관찰 evidence가 승인한 brownfield handler에 permanent/retryable 구분이 이미 계약으로 존재하면 그 구분을 보존하고 영구장애를 retryable로 넓히지 않는다. 이는 해당 preserve scope의 compatibility 점검일 뿐 active code-profile에 raw infrastructure handler·recognizer를 요구하거나 허용하는 레시피가 아니다.\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/agents/discipline-reviewer.md/s007/b25> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/agents/discipline-reviewer.md/s007> ;
@@ -3003,21 +3039,21 @@
     djr:order 28 ;
     djr:restates <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/SKILL.md/s004-1/b2>, <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/SKILL.md/s009-5/b1>, <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/references/final.md/s001/b1> ;
     djr:statesNorm djr:R-1052, djr:R-1053, djr:R-1054, djr:R-1055, djr:R-1056, djr:R-1057, djr:R-1058, djr:R-1059, djr:R-1060, djr:R-1061, djr:R-1062, djr:R-1063, djr:R-1064, djr:R-1065, djr:R-1066 ;
     djr:text "- **파일트리·구조·명명 준수 — 값은 정본, 기계 판정은 백스톱**: 트리·배치·명명의 «값»(어느 칸·어느 이름·어느 층·어느 파일)은 전부 `discipline-houserules` `references/final.md` §0(제1원칙)·§1(표준 트리 170행)·§2(골격 규칙)·§3(명명)·§4(이관 — brownfield=빚)가 소유한다 — 이 문서에는 값을 두지 않는다(값 사본은 썩는다 — 낡은 사본이 정본과 어긋난 사고가 이 절의 전신이다). 절차: ① 코드를 final.md 와 «직접» 대조한다 — 명세 부합만으로 통과시키지 않으며, **명세 자체가 §0 불변식·§2 골격 규칙·포트/칸 위치를 어긴 채 통과했으면 그 자체를 발견으로 올린다(설계 반송 — 명세 정당화는 면제 사유가 아니다)**. 레이아웃 대조 기준은 언제나 표준 트리다(houserules SKILL §1 — 소스 트리에 «기존 규약 존중» 케이스는 없다·기존 배치와의 일치는 통과 사유가 아니다; 승인된 test artifact 의 기존 테스트 위치(§1.2)만 예외로 그 위치와 대조한다). 이 대조의 대상은 **이번 작업의 diff(승인 스코프의 산출물)**다 — 범위 밖 legacy 잔존은 발견이 아니라 빚 보고 채널이고 거기서 수리·이동 지시를 만들지 않으며, 반대로 명세·구현이 승인 스코프 산출물 목록 밖 기존 파일을 이동·재배선했으면 «표준 트리 일치»는 통과 사유가 아니라 **그 이동 자체가 발견(설계 반송)**이다(2026-08-13 라운드 2 실증: 리뷰어가 «filesystem matches approved inventory»로 11 BC 이관을 통과시켰다). ② 경로·AST 로 서는 판정은 registry 결정적 백스톱(`commands/dddjango.md` 의 registry 표)이 소유한다 — 백스톱이 잡는 위반을 재판정하지 않고(이중 계상 금지), 반대로 **백스톱 exit 0 을 «의미 준수»의 증거로 읽지 않는다** — 형태로 못 가르는 의미 변종(개명 폴더·빈-정본 위장·변수 우회·간접 재수출·helper 재수출·이름-위장 클래스·모듈/lazy 싱글톤 공유 — build 팩토리가 반환·주입하는 객체가 import 나 첫 호출 시점 1회 생성으로 요청 간 공유되는 매요청 계약 위반 포함)은 네가 직접 읽는다. 단 «동명 폴더 승격» 폴더의 `__init__.py` 재수출은 세 조건 — 승격 허용 표기 칸 + 본체 `<이름>.py` 실존 + 자기 폴더 모듈의 명시적 이름 재수출(as-alias/`__all__`) — 전건 충족 시 정상 형태다(그 외 재수출 문면 판정은 그대로다). 어댑터 고정 패키지와 역할 폴더의 `__init__.py` 는 houserules §0의 재수출 전용 형태를 대조하며 승격 본체를 요구하지 않는다. 역할 배치·builder와 반환 계약의 동거·reader의 구현 소유도 해당 규범과 직접 대조한다. ③ 옛 이름 재등장은 트리 밖 칸 위반(#81·#490 — §4 이관 종료)이고 면제로 읽지 않는다. ④ 주석·docstring 언어가 프로젝트 관례(없으면 한국어)와 일치하는지도 여기서 본다(기계 밖). ⑤ 타입 규율은 `check-public-surface-annotation` 이 전면(시그니처·지역·속성·모듈/클래스) 기계 소유다 — 네 몫은 ⓓ#69 후보의 물음과, 면제 자리에 억지로 어노테이트해 ORM/enum 을 깨뜨리는 역방향 오류뿐이다.\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/agents/discipline-reviewer.md/s007/b29> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/agents/discipline-reviewer.md/s007> ;
     djr:kind djr:kind-norm ;
     djr:order 29 ;
     djr:statesNorm djr:R-1067, djr:R-1068, djr:R-1069, djr:R-1070, djr:R-1071 ;
-    djr:text "- **ACL 실패 번역 전수성(포트 계약 누수 — 기계 밖)**: ACL 이 호출하는 upstream 동작에서 consuming port/승인 명세가 known failure 로 선언한 의미는 consuming BC 의 own concrete 예외로 빠짐없이 번역되어야 한다 — 그 집합의 upstream 예외가 ACL 을 raw 통과하면 **blocker**. import 없는 propagation·helper·재수출 우회는 기계 밖이라 네가 직접 읽는다. 광범위 `except Exception` 을 요구하지 않으며, ACL·upstream repository 안에서 이미 승인 concrete 로 번역·소진된 실패는 누수가 아니다. raw DB/SDK/network unknown failure 는 이 전수 집합이 아니고 safe framework 500 이 기본이다(승인된 안정적 public meaning 이 있을 때만 owning infra/ACL 이 정규화).\n"@ko .
+    djr:text "- **ACL 실패 번역 전수성(포트 계약 누수 — 기계 밖)**: ACL 이 호출하는 upstream 동작에서 consuming port/승인 명세가 known failure 로 선언한 의미는 consuming BC 의 own concrete 예외로 빠짐없이 번역되어야 한다 — 그 집합의 upstream 예외가 ACL 을 raw 통과하면 **blocker**. import 없는 propagation·helper·재수출 우회는 기계 밖이라 네가 직접 읽는다. 광범위 `except Exception` 을 요구하지 않으며, ACL·upstream repository 안에서 이미 승인 concrete 로 번역·소진된 실패는 누수가 아니다. 잡지 않은 raw DB/SDK/network unknown failure는 이 전수 집합이 아니고 safe framework 500이 기본이다. 이미 잡은 IntegrityError의 승인된 알려진 제약 실패는 구체 계약 예외로, 나머지는 승인된 일반 저장소 실패 계약으로 번역한다. repository 실패 계약은 domain 소유, capability port 실패 계약은 해당 port 소유다. 이 내부 정규화는 공개 HTTP 오류 승인이 아니므로 일반 저장소 실패의 외부 응답은 기존 safe 500을 유지한다. 새 ErrorCode/ErrorSchema/4xx/503을 만들지 않는다. 잡지 않은 unknown 인프라 오류를 새로 catch-all하지 않는다. 안정된 public meaning이 별도로 승인된 경우에만 그 외부 계약에 맞는 controller mapping을 한다. 이미 선언된 계약 예외의 관찰 후 재던짐은 허용한다.\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/agents/discipline-reviewer.md/s007/b3> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/agents/discipline-reviewer.md/s007> ;
     djr:kind djr:kind-norm ;
     djr:order 3 ;
     djr:statesNorm djr:R-0923, djr:R-0924 ;
     djr:text "- **테스트 품질**: 행위중심인가(과도한 mock으로 리팩토링 내성을 해치지 않는가), AAA 구조·격리, 좋은 테스트 4대 특성(회귀 방지·리팩토링 내성·빠른 피드백·유지보수).\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/agents/discipline-reviewer.md/s007/b30> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/agents/discipline-reviewer.md/s007> ;
@@ -3135,21 +3171,21 @@
     djr:kind djr:kind-norm ;
     djr:order 45 ;
     djr:statesNorm djr:R-1099, djr:R-1100, djr:R-1101 ;
     djr:text "  - 결선·입구 — #86 이 분기는 업무를 가르는가(그렇다면 유스케이스로 내린다) · #511 이 입구의 계약을 바깥이 소유하는가(OAuth 콜백 포함 — 그러면 `webhook/<provider>/` 자리다) · #125 입구가 변환·1회 호출을 넘어 로직을 갖는가(그러면 유스케이스로 내린다).\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/agents/discipline-reviewer.md/s007/b46> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/agents/discipline-reviewer.md/s007> ;
     djr:kind djr:kind-norm ;
     djr:order 46 ;
     djr:statesNorm djr:R-1102, djr:R-1103, djr:R-1104, djr:R-1105, djr:R-1106, djr:R-1107 ;
-    djr:text "  - 도메인 모델 — #257 이 메서드 뒤에도 불변식이 참인가(Q4) · #259 이것이 값인가 엔티티인가(Q4) · #268 이 타입 조합만으로 잘못된 값이 «불가능»한가(Q2) · #301 이 규칙이 «없을 때»를 판정하나(루트 메서드로 표현될 수 있나) · #311 이 이름이 규칙 «행위»를 말하나 · #547 이 둘이 «동시에» 일어나면 업무가 정말 막아야 하나 / 서로 다른 일을 하는 두 사용자가 이 경계로 충돌하나(Q4) · #565 단계 이름(위 표).\n"@ko .
+    djr:text "  - 도메인 모델 — #257 이 메서드 뒤에도 불변식이 참인가(Q4) · #259 이것이 값인가 엔티티인가(Q4) · #268 닫힌 표준 Enum/StrEnum/IntEnum은 생성 검증 후보에서 제외하고, custom/open Enum은 raise 유무와 별개로 타입 조합만으로 잘못된 값이 «불가능»한지 묻는다(Q2) · #301 이 규칙이 «없을 때»를 판정하나(루트 메서드로 표현될 수 있나) · #311 이 이름이 규칙 «행위»를 말하나 · #546 해소된 동일 트랜잭션 영역의 서로 다른 repository/aggregate 타입 쓰기는 확정이고, 영역·출처 미해소는 후보로 같은 트랜잭션인지 확인한다(순차 독립 UoW는 합치지 않으며 nested/외부 atomic은 결합한다) · #547 이 둘이 «동시에» 일어나면 업무가 정말 막아야 하나 / 서로 다른 일을 하는 두 사용자가 이 경계로 충돌하나(Q4) · #565 단계 이름(위 표).\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/agents/discipline-reviewer.md/s007/b47> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/agents/discipline-reviewer.md/s007> ;
     djr:kind djr:kind-norm ;
     djr:order 47 ;
     djr:statesNorm djr:R-1108, djr:R-1109 ;
     djr:text "  - 사실(이벤트) — #271 이 이름이 «이미 일어난 사실»을 말하나 · #564 이 칸이 «패턴»이 아니라 «진행표»인가(단계 물음).\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/agents/discipline-reviewer.md/s007/b48> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/agents/discipline-reviewer.md/s007> ;
@@ -3177,28 +3213,28 @@
     djr:kind djr:kind-norm ;
     djr:order 50 ;
     djr:statesNorm djr:R-1114, djr:R-1115, djr:R-1116 ;
     djr:text "  - 놓칠 수 있는 입구 — #181 멱등(위 표) · #451 이 창구가 «혼자서» 답을 만들 수 있나 · #512 보내는 쪽 문서가 자기를 이 이름으로 부르나 · #629 이 입구가 «안 와도» 업무가 돌아가나.\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/agents/discipline-reviewer.md/s007/b51> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/agents/discipline-reviewer.md/s007> ;
     djr:kind djr:kind-norm ;
     djr:order 51 ;
     djr:statesNorm djr:R-1117, djr:R-1118 ;
-    djr:text "  - admin·표현 — #343 이 문장이 운영 «기능»인가 장고 «배선»인가 · #589 이 조건이 업무 판정인가(Q2) · #590 문구(위 표) · #347(위 격리 줄).\n"@ko .
+    djr:text "  - admin·표현 — #343 이 문장이 운영 «기능»인가 장고 «배선»인가 · #589 이 조건이 업무 판정인가(Q2) · #590 문구(위 표) · #347(위 격리 줄).\n\n  **admin context 판정**: #493 주석 존재 유지 · #645 framework 소유 슬롯 Any 제한 허용 · #646 제네릭 런타임 안전 유지 · #647 열린 UI context 조립/병합/전달 허용 · #650 실제 JSON 소비 검증 유지다. 출처가 확인된 Django admin 및 Parler admin 계열의 고정 framework 슬롯에만 적용한다. `extra_context`/`context`의 받기·each_context·UI dict·copy/update·고정 UI 키 쓰기·framework render 전달과 연결된 private 전달 helper의 매개변수·반환·지역 context 주석을 허용한다. form/inline/media의 별도 조립은 context의 허용을 취소하지 않는다. 컨테이너 부재 처리와 request UI metadata의 담기·전달도 허용한다. 업무 읽기·비교·계산·상태 변경 또는 ORM/use case/업무 함수로의 값 전달은 실제 소비이므로 그 자리부터 기존 규칙을 적용한다. 출처나 소비가 미해소 또는 동적/재귀 호출로 escape한 연결 context는 후보로 남겨 확인한다. 이름만 context인 값·같은 함수의 별도 업무 dict·framework 고정 kwargs 밖 bare Any·admin 클래스/경로 전체는 면제하지 않는다. 생성 private helper는 본문이 없으므로 정확히 결합된 열린 dict 슬롯의 #645/#647만 S1 미검증으로 보고하고 G2에서 실제 소비 흐름으로 다시 판단한다.\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/agents/discipline-reviewer.md/s007/b52> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/agents/discipline-reviewer.md/s007> ;
     djr:kind djr:kind-norm ;
     djr:order 52 ;
     djr:statesNorm djr:R-1119, djr:R-1120, djr:R-1121, djr:R-1122, djr:R-1123 ;
-    djr:text "  - 포트·어댑터 — #227 이 자료를 원시값 인자로 «펴서» 넘길 수 있나 · #233 무엇을 알고 싶은가가 이름에 있나(Q1) · #368 이게 «기계»인가 «값»인가 · #475 이 판정이 업무 규칙인가(Q2) · #485 이 이름이 무엇을 시키는지 말하나 · #553 Q2(위 표) · #594·#595 이름 안정(위 표).\n"@ko .
+    djr:text "  - 포트·어댑터 — #227 이 자료를 원시값 인자로 «펴서» 넘길 수 있나 · #233 무엇을 알고 싶은가가 이름에 있나(Q1) · #368 이게 «기계»인가 «값»인가 · #475 이 판정이 업무 규칙인가(Q2) · #485 이 이름이 무엇을 시키는지 말하나 · #553 Q2(위 표) · #594·#595 이름 안정(위 표). · #557 비교하는 code/errno/status_code 수신자의 출처가 확인된 vendor이면 확정, 확인된 우리 계약이면 허용, 미해소/혼합이면 후보로 그 코드의 주인을 묻는다.\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/agents/discipline-reviewer.md/s007/b53> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/agents/discipline-reviewer.md/s007> ;
     djr:kind djr:kind-norm ;
     djr:order 53 ;
     djr:statesNorm djr:R-1124, djr:R-1125, djr:R-1126, djr:R-1127 ;
     djr:text "  - framework·어휘 — #425 이 재료의 뜻을 밖(HTTP·pytest·시간)이 정하나 · #448 이 낱말의 뜻을 저장소 밖이 정하나 · #607 이 조건이 업무 규칙인가(Q2) · #618 문구(#590) · #619 이것이 원시값 하나로 되나 · #584 이름 안정(#595).\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/agents/discipline-reviewer.md/s007/b54> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/agents/discipline-reviewer.md/s007> ;

```

## ontology/rules/command-dddjango.ttl

Before SHA256: 9a7b9cd2220f255a2168d5ef3a69db43c0fedc103407a8b23e1d19ad9ce65e62
After SHA256: 454d396ab85aa5fa52b7c6172f197abc9605afd99e96691f3d93661ec6ee1f27

```diff
--- before/ontology/rules/command-dddjango.ttl
+++ after/ontology/rules/command-dddjango.ttl
@@ -2862,42 +2862,48 @@
 
 djr:R-0460 a djr:Obligation ;
     skos:prefLabel "자율 실행 STOP — 기록 파일 + 정지 커밋이 유효 종료 조건 · 기록이 정본이고 질문은 입력 채널(응답은 기록에 추기·재개 첫 커밋 포함)"@ko ;
     djr:currentExpression <https://numchida.com/ns/djr#R-0460@2026-08-22> .
 
 <https://numchida.com/ns/djr#R-0460@2026-08-22> a djr:Expression ;
     prov:specializationOf djr:R-0460 ;
     djr:revision 1 .
 
 djr:R-3432 a djr:Obligation ;
-    skos:prefLabel "pre-gate 실행 의무 — design-spec 내용 변경마다·배너 직전 최종본·override 후 dispatch 전 무조건(캐시 skip·재발화·Phase 2 최신성 판형은 R-3445)"@ko ;
-    djr:currentExpression <https://numchida.com/ns/djr#R-3432@2026-09-03b> .
+    skos:prefLabel "pre-gate 실행 의무 — 명세 변경/배너 직전/dispatch 전 최종 예보·선언 포함"@ko ;
+    djr:currentExpression <https://numchida.com/ns/djr#R-3432@2026-09-11> .
 
 <https://numchida.com/ns/djr#R-3432@2026-09-01> a djr:Expression ;
     prov:specializationOf djr:R-3432 ;
     djr:revision 1 .
 
 <https://numchida.com/ns/djr#R-3432@2026-09-03> a djr:Expression ;
     prov:specializationOf djr:R-3432 ;
     prov:wasRevisionOf <https://numchida.com/ns/djr#R-3432@2026-09-01> ;
     djr:revision 2 ;
     djr:revisionKind djr:revision-amendment .
 
 <https://numchida.com/ns/djr#R-3432@2026-09-03b> a djr:Expression ;
     prov:specializationOf djr:R-3432 ;
     prov:wasRevisionOf <https://numchida.com/ns/djr#R-3432@2026-09-03> ;
     djr:revision 3 ;
     djr:revisionKind djr:revision-clarification .
 
+<https://numchida.com/ns/djr#R-3432@2026-09-11> a djr:Expression ;
+    prov:specializationOf djr:R-3432 ;
+    prov:wasRevisionOf <https://numchida.com/ns/djr#R-3432@2026-09-03b> ;
+    djr:revision 4 ;
+    djr:revisionKind djr:revision-amendment .
+
 djr:R-3433 a djr:Obligation ;
-    skos:prefLabel "차단 모드 red 처분 — red 반송 의무 · 배너 근거 --check-report exit 0 · 예외 = 귀속 red 전건 ignored(빚)|filtered · path 등급 filtered 불가"@ko ;
-    djr:currentExpression <https://numchida.com/ns/djr#R-3433@2026-09-03b> .
+    skos:prefLabel "pre-gate 귀속 및 선언 확정 red 전건 처분·후보/S1 비차단 분리"@ko ;
+    djr:currentExpression <https://numchida.com/ns/djr#R-3433@2026-09-11> .
 
 <https://numchida.com/ns/djr#R-3433@2026-09-01> a djr:Expression ;
     prov:specializationOf djr:R-3433 ;
     djr:revision 1 .
 
 <https://numchida.com/ns/djr#R-3433@2026-09-02> a djr:Expression ;
     prov:specializationOf djr:R-3433 ;
     prov:wasRevisionOf <https://numchida.com/ns/djr#R-3433@2026-09-01> ;
     djr:revision 2 ;
     djr:revisionKind djr:revision-amendment .
@@ -2907,62 +2913,86 @@
     prov:wasRevisionOf <https://numchida.com/ns/djr#R-3433@2026-09-02> ;
     djr:revision 3 ;
     djr:revisionKind djr:revision-amendment .
 
 <https://numchida.com/ns/djr#R-3433@2026-09-03b> a djr:Expression ;
     prov:specializationOf djr:R-3433 ;
     prov:wasRevisionOf <https://numchida.com/ns/djr#R-3433@2026-09-03> ;
     djr:revision 4 ;
     djr:revisionKind djr:revision-redefinition .
 
+<https://numchida.com/ns/djr#R-3433@2026-09-11> a djr:Expression ;
+    prov:specializationOf djr:R-3433 ;
+    prov:wasRevisionOf <https://numchida.com/ns/djr#R-3433@2026-09-03b> ;
+    djr:revision 5 ;
+    djr:revisionKind djr:revision-amendment .
+
 djr:R-3434 a djr:Prohibition ;
-    skos:prefLabel "예보의 대체·축약 금지 — Phase 0 빚 스캔·G2 게이트 비대체·build_anchor 불간섭·HEAD 판형 유용 금지·계약 실존 채널의 G0 선행 조건·상류 머지 판단 비대체"@ko ;
-    djr:currentExpression <https://numchida.com/ns/djr#R-3434@2026-09-03> .
+    skos:prefLabel "예보·선언·생성 S1의 Phase 0/G2/G0 실증 비대체·앵커 불간섭"@ko ;
+    djr:currentExpression <https://numchida.com/ns/djr#R-3434@2026-09-11> .
 
 <https://numchida.com/ns/djr#R-3434@2026-09-01> a djr:Expression ;
     prov:specializationOf djr:R-3434 ;
     djr:revision 1 .
 
 <https://numchida.com/ns/djr#R-3434@2026-09-03> a djr:Expression ;
     prov:specializationOf djr:R-3434 ;
     prov:wasRevisionOf <https://numchida.com/ns/djr#R-3434@2026-09-01> ;
     djr:revision 2 ;
     djr:revisionKind djr:revision-amendment .
 
+<https://numchida.com/ns/djr#R-3434@2026-09-11> a djr:Expression ;
+    prov:specializationOf djr:R-3434 ;
+    prov:wasRevisionOf <https://numchida.com/ns/djr#R-3434@2026-09-03> ;
+    djr:revision 3 ;
+    djr:revisionKind djr:revision-amendment .
+
 djr:R-3435 a djr:Permission ;
-    skos:prefLabel "팬텀 스텁 = 스크립트의 결정적 투영물(격리 사본 한정) — 구현 코드 직접 작성 금지 경계 비저촉"@ko ;
-    djr:currentExpression <https://numchida.com/ns/djr#R-3435@2026-09-01> .
+    skos:prefLabel "격리 사본 결정적 투영물·명시 후상태와 기존 본문 미검증"@ko ;
+    djr:currentExpression <https://numchida.com/ns/djr#R-3435@2026-09-11> .
 
 <https://numchida.com/ns/djr#R-3435@2026-09-01> a djr:Expression ;
     prov:specializationOf djr:R-3435 ;
     djr:revision 1 .
 
+<https://numchida.com/ns/djr#R-3435@2026-09-11> a djr:Expression ;
+    prov:specializationOf djr:R-3435 ;
+    prov:wasRevisionOf <https://numchida.com/ns/djr#R-3435@2026-09-01> ;
+    djr:revision 2 ;
+    djr:revisionKind djr:revision-amendment .
+
 djr:R-3436 a djr:Prohibition ;
-    skos:prefLabel "pre-gate machine 블록 부재·공허 skip 금지 — 부재·0행 = 형식 red(exit 3) · 구형 명세 포함(«캐시 skip»·«실체화 0 skip» 과 구별)"@ko ;
-    djr:currentExpression <https://numchida.com/ns/djr#R-3436@2026-09-03b> .
+    skos:prefLabel "machine 부재/공허 형식 red·실체화 0에서도 선언 검증"@ko ;
+    djr:currentExpression <https://numchida.com/ns/djr#R-3436@2026-09-11> .
 
 <https://numchida.com/ns/djr#R-3436@2026-09-01> a djr:Expression ;
     prov:specializationOf djr:R-3436 ;
     djr:revision 1 .
 
 <https://numchida.com/ns/djr#R-3436@2026-09-03> a djr:Expression ;
     prov:specializationOf djr:R-3436 ;
     prov:wasRevisionOf <https://numchida.com/ns/djr#R-3436@2026-09-01> ;
     djr:revision 2 ;
     djr:revisionKind djr:revision-clarification .
 
 <https://numchida.com/ns/djr#R-3436@2026-09-03b> a djr:Expression ;
     prov:specializationOf djr:R-3436 ;
     prov:wasRevisionOf <https://numchida.com/ns/djr#R-3436@2026-09-03> ;
     djr:revision 3 ;
     djr:revisionKind djr:revision-redefinition .
 
+<https://numchida.com/ns/djr#R-3436@2026-09-11> a djr:Expression ;
+    prov:specializationOf djr:R-3436 ;
+    prov:wasRevisionOf <https://numchida.com/ns/djr#R-3436@2026-09-03b> ;
+    djr:revision 4 ;
+    djr:revisionKind djr:revision-amendment .
+
 djr:R-3437 a djr:Obligation ;
     skos:prefLabel "G1/G1′ 배너 pre-gate 예보 1행 병기 — 기계 출처 --check-report 요약 행(exit 0 일 때만 배너) · 귀속 N·실존 결손 M·처분 전건 기재·최종본 결속"@ko ;
     djr:currentExpression <https://numchida.com/ns/djr#R-3437@2026-09-03b> .
 
 <https://numchida.com/ns/djr#R-3437@2026-09-01> a djr:Expression ;
     prov:specializationOf djr:R-3437 ;
     djr:revision 1 .
 
 <https://numchida.com/ns/djr#R-3437@2026-09-03> a djr:Expression ;
     prov:specializationOf djr:R-3437 ;
@@ -3022,26 +3052,32 @@
 
 djr:R-3444 a djr:Obligation ;
     skos:prefLabel "G2 배너 pre-gate 최신성 1행 — --check-report 요약 행 기계 출처 · 불비면 G2 미제시(R-0411) · 구형 명세·변경 0 레인은 미실행 표기"@ko ;
     djr:currentExpression <https://numchida.com/ns/djr#R-3444@2026-09-03> .
 
 <https://numchida.com/ns/djr#R-3444@2026-09-03> a djr:Expression ;
     prov:specializationOf djr:R-3444 ;
     djr:revision 1 .
 
 djr:R-3445 a djr:Obligation ;
-    skos:prefLabel "pre-gate 캐시 skip·--base 재발화·Phase 2 최신성 — dispatch 전 재발화 · G2 전 --check-report exit 0 · 구형 명세·변경 0 레인 한정"@ko ;
-    djr:currentExpression <https://numchida.com/ns/djr#R-3445@2026-09-03> .
+    skos:prefLabel "선택 effects 포함 캐시 해시·기존 무기재 해시 보존·재발화 최신성"@ko ;
+    djr:currentExpression <https://numchida.com/ns/djr#R-3445@2026-09-11> .
 
 <https://numchida.com/ns/djr#R-3445@2026-09-03> a djr:Expression ;
     prov:specializationOf djr:R-3445 ;
     djr:revision 1 .
+
+<https://numchida.com/ns/djr#R-3445@2026-09-11> a djr:Expression ;
+    prov:specializationOf djr:R-3445 ;
+    prov:wasRevisionOf <https://numchida.com/ns/djr#R-3445@2026-09-03> ;
+    djr:revision 2 ;
+    djr:revisionKind djr:revision-amendment .
 
 <https://numchida.com/ns/djr#d/dddjango/commands/dddjango.md> a djr:Document ;
     skos:prefLabel "command-dddjango"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/commands/dddjango.md/s001> a djr:Section ;
     djr:headingSnapshot "---"@ko ;
     djr:inDocument <https://numchida.com/ns/djr#d/dddjango/commands/dddjango.md> ;
     djr:sectionOwner djr:owner-graph .
 
 <https://numchida.com/ns/djr#s/dddjango/commands/dddjango.md/s001/b1> a djr:Block ;
@@ -3314,21 +3350,21 @@
     djr:kind djr:kind-norm ;
     djr:order 1 ;
     djr:statesNorm djr:R-0207 ;
     djr:text "\n승인된 스코프와 활성 lens로 진행한다.\n\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/commands/dddjango.md/s006/b10> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/commands/dddjango.md/s006> ;
     djr:kind djr:kind-norm ;
     djr:order 10 ;
     djr:statesNorm djr:R-3445 ;
-    djr:text "**pre-gate 캐시 skip·재발화 판형**(2026-09-03): ① **캐시 skip** — 위 «기계가독 블록 해시가 불변이면 재실행을 skip 한다»의 해시는 실행기의 `scripts/design_pregate.py <산출물 폴더>/design-spec.md . --block-hash` 값(기계 블록 4종 + 영구 테스트 입장 표를 파서와 같은 추출로 이어 붙인 sha256[:12] — 출력 전용·판정 무접촉·git 0회)이고, 매 실행 리포트 헤더가 같은 값을 `블록 해시 <값>` 으로 병기한다. skip 조건은 **`--block-hash` 값이 직전 실행 리포트 헤더의 값과 동일**할 때뿐이며, skip 마다 pregate-report.md 말미에 1행 `- pre-gate skip — 블록 해시 <값> 불변 · 기준선 <sha12> · 재실행 생략 <UTC> · 직전 예보 <UTC>` 를 append 한다(기록 의무 — 이 행은 `## pre-gate 예보` 문자열을 쓰지 않는다). 값이 다르면 skip 불가이고, skip 행 없는 미실행은 규범 위반이다(«skip 행 부재 ∧ 해시 변동»으로 관측한다). ② **Phase 2 진입 후 재발화 판형** — 반송·STOP 으로 design-spec 이 개정돼 재실행할 때는 `--base <G1 승인 시점 기준선 SHA>` 를 명시한다(값은 G1 배너 직전 최종 실행의 pregate-report 헤더 «기준선 SHA» — `build_anchor` 는 읽지 않는다(R-3434)). 미커밋 WIP 는 커밋 또는 stash 후 실행한다. 실행기는 `--base` 명시 시(명시 `--base HEAD` 포함) 기준선 트리에 없던 계획 add 가 오버레이에 실존하면 «기실현 add»로 already-built 에 기록하고 사본에서 스텁으로 대체해 예보하며(실물 판정 혼입 0), 기준선 트리에 있는 add 는 여전히 형식 red(add 충돌 — 계획↔실물 모순)다. 재발화의 red 는 계획 red 로서 반송 사유이고(위 문단 — 차단 모드), 기실현 실물이 스텁과 다른 위반의 판정자만 G2 앵커 차분이다(사각 S7). ③ **Phase 2 최신성**(2026-09-03 차단 승격) — Phase 2 중 design-spec 변경(G1′ 반송·Contract mismatch 반송·수정 모드 개정 — 수정 모드 절)은 슬라이스 dispatch 전 ②의 `--base` 재발화가 선행한다. G2 배너 직전에는 `scripts/design_pregate.py <산출물 폴더>/design-spec.md . --check-report <산출물 폴더>/pregate-report.md` 의 exit 0(마지막 예보 절의 블록 해시 = 최종 명세 해시 ∧ 판정 비형식red ∧ red 면 예보 항목 전건 처분 기재)을 얻는다 — 다르면(stale) 재발화 후 G2 다 · skip 행·처분 절의 문자열은 대조 대상이 아니다. **한정**: 이 레인 산출물 폴더에 pregate-report 가 없고 design-spec 에 machine 블록도 없고 이 세션에서 design-spec 변경이 0 이면(형식 규범 이전 승인 명세의 순수 구현 수정) 최신성 행은 `미실행(구형 명세 · 변경 0)` 이고 `--check-report` 를 부르지 않는다 — 블록이 있는 명세는 이 한정에 들지 않는다(초안 수신 트리거로 리포트가 반드시 있다).\n\n"@ko .
+    djr:text "**pre-gate 캐시 skip·재발화 판형**(2026-09-03): ① **캐시 skip** — 위 «기계가독 블록 해시가 불변이면 재실행을 skip 한다»의 해시는 실행기의 `scripts/design_pregate.py <산출물 폴더>/design-spec.md . --block-hash` 값(기계 블록 4종 + 영구 테스트 입장 표, 선택형 use-case-effects를 파서와 같은 추출로 이어 붙인 sha256[:12] — 효과 블록이 없으면 기존 해시 알고리즘을 유지하고, 있으면 효과 마커와 원문을 마지막에 추가 — 출력 전용·판정 무접촉·git 0회)이고, 매 실행 리포트 헤더가 같은 값을 `블록 해시 <값>` 으로 병기한다. skip 조건은 **`--block-hash` 값이 직전 실행 리포트 헤더의 값과 동일**할 때뿐이며, skip 마다 pregate-report.md 말미에 1행 `- pre-gate skip — 블록 해시 <값> 불변 · 기준선 <sha12> · 재실행 생략 <UTC> · 직전 예보 <UTC>` 를 append 한다(기록 의무 — 이 행은 `## pre-gate 예보` 문자열을 쓰지 않는다). 값이 다르면 skip 불가이고, skip 행 없는 미실행은 규범 위반이다(«skip 행 부재 ∧ 해시 변동»으로 관측한다). ② **Phase 2 진입 후 재발화 판형** — 반송·STOP 으로 design-spec 이 개정돼 재실행할 때는 `--base <G1 승인 시점 기준선 SHA>` 를 명시한다(값은 G1 배너 직전 최종 실행의 pregate-report 헤더 «기준선 SHA» — `build_anchor` 는 읽지 않는다(R-3434)). 미커밋 WIP 는 커밋 또는 stash 후 실행한다. 실행기는 `--base` 명시 시(명시 `--base HEAD` 포함) 기준선 트리에 없던 계획 add 가 오버레이에 실존하면 «기실현 add»로 already-built 에 기록하고 사본에서 스텁으로 대체해 예보하며(실물 판정 혼입 0), 기준선 트리에 있는 add 는 여전히 형식 red(add 충돌 — 계획↔실물 모순)다. 재발화의 red 는 계획 red 로서 반송 사유이고(위 문단 — 차단 모드), 기실현 실물이 스텁과 다른 위반의 판정자만 G2 앵커 차분이다(사각 S7). ③ **Phase 2 최신성**(2026-09-03 차단 승격) — Phase 2 중 design-spec 변경(G1′ 반송·Contract mismatch 반송·수정 모드 개정 — 수정 모드 절)은 슬라이스 dispatch 전 ②의 `--base` 재발화가 선행한다. G2 배너 직전에는 `scripts/design_pregate.py <산출물 폴더>/design-spec.md . --check-report <산출물 폴더>/pregate-report.md` 의 exit 0(마지막 예보 절의 블록 해시 = 최종 명세 해시 ∧ 판정 비형식red ∧ red 면 예보 항목 전건 처분 기재)을 얻는다 — 다르면(stale) 재발화 후 G2 다 · skip 행·처분 절의 문자열은 대조 대상이 아니다. **한정**: 이 레인 산출물 폴더에 pregate-report 가 없고 design-spec 에 machine 블록도 없고 이 세션에서 design-spec 변경이 0 이면(형식 규범 이전 승인 명세의 순수 구현 수정) 최신성 행은 `미실행(구형 명세 · 변경 0)` 이고 `--check-report` 를 부르지 않는다 — 블록이 있는 명세는 이 한정에 들지 않는다(초안 수신 트리거로 리포트가 반드시 있다).\n\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/commands/dddjango.md/s006/b2> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/commands/dddjango.md/s006> ;
     djr:kind djr:kind-norm ;
     djr:order 2 ;
     djr:statesNorm djr:R-0208, djr:R-0209, djr:R-0210, djr:R-0211, djr:R-0212 ;
     djr:text "1. `dddjango:design-architect`를 호출한다(서브에이전트 지정은 항상 `dddjango:` 한정 표기 — 동명 에이전트를 가진 플러그인이 함께 설치될 수 있다 · 2026-08-15) — 입력: 스코프 메모 · 활성 lens 목록 · 설계 명세 저장 경로. architect는 기존 프로젝트 구조를 조사해 **패키지·테스트 구조 결정**과 모든 영구 test artifact `add/update/move/split/rename/remove/weaken` 후보의 최소 입장 표(`candidate | protected contract/evidence | unique production failure | existing authoritative coverage | decision | owner/path`)를 명세에 포함한다. decision은 `add/update/reuse/retain/remove/reject/pending` 일곱 값만 쓴다. 산출: 통합 설계 명세 1건.\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/commands/dddjango.md/s006/b3> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/commands/dddjango.md/s006> ;
@@ -3371,21 +3407,21 @@
     djr:order 8 ;
     djr:restates <https://numchida.com/ns/djr#s/dddjango/agents/design-architect.md/s005/b10> ;
     djr:statesNorm djr:R-0247, djr:R-0248, djr:R-0249, djr:R-0250, djr:R-0251, djr:R-0252, djr:R-0253, djr:R-0254, djr:R-0255, djr:R-0256, djr:R-0257, djr:R-0258 ;
     djr:text "Ninja endpoint/error contract/response Schema가 변경되는 scope에서는 **G1 제시 전과 사용자 승인 응답 뒤 Phase 2 dispatch 직전**에 current `design-spec.md`를 다시 읽는다. `Error response contract 12-slot`의 label과 순서는 정확히 `contract scope`; `scope evidence`; `error profile`; `compatibility/rollout`; `common FrameworkErrorSchema action`; `common FrameworkErrorSchema shape/approval`; `BC error module`; `BC ErrorCode`; `BC ErrorSchema`; `prepared error mapping`; `controller mapping`; `response/OpenAPI/tests`다. 12개 모두 구체적이고 선택 profile에 맞으며 서로 일관돼야 한다. `none | not applicable`은 해당 profile/slot이 허용하고 이유·evidence를 함께 기록한 경우에만 구체값이다. `dddjango-code-json`은 `error-bc`가 비어도 slot 5가 `reuse | create | approved-change`여야 하고 slot 6의 common shape가 필수다. plugin 기본 property 목록은 없으며 기존 프로젝트의 관찰된 exact shape 또는 신규 scope에서 별도로 승인된 exact shape를 그대로 사용한다. slot 9의 BC base가 slot 6의 식별자 field를 `<Bc>ErrorCode`로 좁히면서 공통의 default를 잃어 required가 되는 것은 canon이다(식별자 field 한정·ErrorCode 좁힘 동반일 때만 — 2026-08-15). 이때 slots 7–9는 public BC error 부재 이유와 함께 `none`일 수 있지만, slots 10–12는 승인된 empty mapping/runtime/OpenAPI inventory와 검증을 명시해 공백으로 넘기지 않는다. `preserve-established`의 slots 5–12는 관찰된 profile-native artifact/behavior 또는 evidence가 있는 `none | not applicable`이어야 하며 code-profile Enum·base·direct-`Status`를 강제하지 않는다. 누락·모호·모순이면 승인 입력이 있어도 Phase 2로 가지 않고 G1/G1′ 설계로 반송한다. Coordinator는 slot 값을 대신 결정하거나 조용히 보충·수정하지 않는다. `dddjango-code-json`에서 현재 common shape와 승인 shape가 다른데 `common FrameworkErrorSchema action=approved-change`와 **별도로 표면화해 받은 명시적 사용자 승인 evidence**가 함께 없으면 G1을 차단한다. 설계 전체에 대한 일반 G1 승인은 shape 변경 승인을 대신하지 않는다. 신규 scope의 최초 shape도 exact field/type/required/default/nullability/모든 `Field` metadata/model config·legacy `Config`/validator/serializer/computed field/Pydantic hook inventory와 effective semantics/wire 직렬화 결과와 각 field 의미를 보여 준 별도 명시 승인 없이는 생성하지 않는다. 재작업으로 profile·compatibility·wire 또는 그 밖의 API semantic slot이 바뀌면 API reviewer를 다시 호출하고, 물리 구조·소유권·controller mapping 결정이 바뀌면 discipline reviewer를 다시 호출해 반영한 뒤 새 G1을 제시한다.\n\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/commands/dddjango.md/s006/b9> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/commands/dddjango.md/s006> ;
     djr:kind djr:kind-norm ;
     djr:order 9 ;
     djr:statesNorm djr:R-3432, djr:R-3433, djr:R-3434, djr:R-3435, djr:R-3436 ;
-    djr:text "**pre-gate — 설계 명세 결정적 예보(차단 모드)**: `design-spec.md` 내용이 바뀔 때마다 실행한다 — architect 초안 수신 직후(위 2의 리뷰 다발과 병렬 1회 — 조기 신호), 리뷰 반영·개정 수신마다, 그리고 **G1/G1′ 배너 제시 직전 최종본과 G1 override(②/③) 반영 후 Phase 2 dispatch 전에는 무조건**(배너의 예보 1행은 항상 최종본에 대한 것 — 낡은 green 금지). 실행 판형은 `scripts/design_pregate.py <산출물 폴더>/design-spec.md . --report <산출물 폴더>/pregate-report.md` 다(`scripts/…` 는 registry 게이트와 같은 규약 — 스킬 폴더의 절대 경로로 펴고 cwd 는 타깃 프로젝트 루트다 · 기계가독 블록 해시가 불변이면 재실행을 skip 한다 — 캐시가 직렬 비용을 없앤다). 팬텀 스텁·git 호출은 전부 스크립트가 격리 사본(저장소 트리 밖) 위에서 수행하는 **결정적 투영물**이라 «구현 코드는 직접 쓰지 않는다» 경계와 충돌하지 않는다 — 너는 이 절차를 위해 bare git 을 직접 치지 않는다. 이 실행은 **게이트다**(차단 모드 — 2026-09-03 승격): 귀속 red(exit 2)·형식 red(exit 3 — 문법·블록 부재·블록 공허·add 충돌·update/remove 대상 기준선 부재 전부)는 architect **반송 의무**이며, red 인 최종본은 G1/G1′ 배너·무배너 재승인·Phase 2 슬라이스 dispatch 어느 것의 근거도 될 수 없다(`--base` 재발화의 red 도 같다 — G2 앵커 차분은 기실현 실물의 판정자이지 계획 red 의 대체가 아니다). 예보가 red 가 아닐 때(exit 0·4·5)만 배너를 제시하고, **배너(G1/G1′)의 근거는 언제나 `scripts/design_pregate.py <산출물 폴더>/design-spec.md . --check-report <산출물 폴더>/pregate-report.md` 의 exit 0 이다**(마지막 예보 절의 블록 해시 = 최종본 해시 ∧ 판정 비형식red ∧ red 면 예보 항목 전건 처분 기재 — 자기 판정이 아니다 · 낡은 green 은 stale 로 선다). 반송 없이 배너를 내는 유일한 경로는 **귀속 red(exit 2)의 예보 항목 전건**에 `ignored(빚: <legacy-debt 파일:행> · STOP <문서 경로>)` 또는 `filtered(ⓐ S<n> | ⓑ <같은 형태 실코드 경로 · 검사기 exit 0>)` 를 pregate-report 에 위 «처분 행 정형»(산출물 위치 절)으로 기재하고 배너 예보 1행에 `귀속 N건(처분 전건 기재)` 를 병기하는 것뿐이다 — `corrected` 는 이 경로에 없다(corrected 의 증거는 재실행에서의 소멸이라 재실행 결과가 곧 최종본이다 · corrected 행에는 «소멸 run 시각 · 블록 해시 전→후» 를 병기한다). 형식 red 는 안정 ID 가 없으므로 이 경로 자체가 없다. 계약 실존 결손(e-ID)은 «전건» 에 들지 않는다(exit 5 비차단 — 별도 게이트). 개정 수신 후 재실행 시점마다 각 red 의 처분 라벨을 그 red 절 뒤에 append 한다(이전 절의 처분은 재기재 — `--check-report` 는 마지막 절 이후만 읽는다). **라벨의 뜻은 채널별 닫힌 정의다** — **예보 항목(registry 귀속)의 처분 라벨은 `corrected | ignored | filtered`** 다: `corrected` = 개정으로 해소(다음 실행에서의 소멸이 증거) · `ignored` = 실위반으로 인지하되 개정하지 않음(실위반 확인 증거는 G2 귀속 red 해소 트레이스 **또는** legacy-debt 매칭 기록(STOP 병기) 둘 중 하나다 — 이관 빚 수용이 이 라벨이다 · 배너 시점에는 후자만 적법하다 — 전자는 G1 시점에 존재할 수 없다) · `filtered` = pre-gate 도구(스텁·문법·시뮬레이션) 한계 판정 — 이 채널에 `deferred` 는 없다(이연은 ignored+빚 매칭 또는 filtered 다). `filtered` 의 근거 유형은 둘뿐이다: ⓐ 리포트 사각 목록 항목 번호 인용(`S<n>` — 그 항목이 이 red 의 오탐 원인임을 한 줄로 잇는다) ⓑ 같은 형태의 실코드 파일이 해당 검사기에서 exit 0 인 대조 경로. **검사기 소스에서 판정 입력이 경로·폴더·파일 이름의 존재뿐인 구조 규칙**(rule-owner-map 등급 path — 예: #81 BC 직계 · #325 ORM 산출물 위치 · #188 area 1:1 · #318 driven_layer 자식 · #336 중앙 마이그레이션 · #490 트리 밖 경로)은 스텁 내용과 무관하므로 ⓑ 가 성립할 수 없고 filtered 대상이 아니다 — corrected 또는 ignored+빚 매칭이다. 경로와 내용을 함께 보는 규칙(예: #392 factories/ 의 factory_boy 부재)은 ⓑ 근거를 대면 filtered 가 가능하다. **계약 실존 결손(리포트 «계약 실존» 절 · 안정 ID `e-…`)의 처분 라벨은 `corrected | deferred | filtered`** 다(2026-09-03): `corrected` = 대상 실존 확보(다음 실행에서 실존 확인 K 증가·결손 소멸) 또는 경로 오기 정정(대상 기실존) — 행 삭제·소비 철회로 결손이 소멸하면 직전 리포트 대비 «결손 소멸 ∧ 행 수 R 감소»가 그것을 드러내며 처분은 `corrected(철회: <근거>)` 로 근거 병기 의무다(발주자 사안이면 STOP) · `deferred`(선행 대기) = 결손 대상이 상류 레인/후행 슬라이스 소유임을 명세가 명시하고 해소 조건을 병기한다 — 정형 `deferred(<소유 레인|Sn>; until <머지 SHA|Sn>)` 권고 · 증거는 조건 충족 시점 재실행에서의 소멸이다(dirty overlay·기준선 갱신이 자동 반영) · `filtered` = 도구 한계(네임스페이스 레이아웃·`import *`·파싱 불능 등 판정 불능 U 계열 — 근거 병기 의무) — 이 채널에 `ignored` 는 없다(부재는 수용 가능한 위반이 아니라 ImportError 예약이며 G2 귀속·legacy-debt 어느 증거도 성립하지 않는다). 실존 채널은 승격 판정식(P/S/I 표면 ∩ G2 귀속)의 **입력이 아니다** — 결손 건수·처분 분포·도구 오류를 별도 계수로만 보고한다(설계 v4 §8 ⑷). 각 채널의 정의 밖 재량 라벨은 없다 — 같은 도구 한계를 레인마다 다른 라벨로 처분하면 승격 판정식이 오염된다(2026-09-02 관찰 레인 1·2 실측). 결손은 권고다 — 도구가 레인을 세우지 않으며(exit 5 는 비차단), 선행 대기가 발주자 결정 사안이면 기존 STOP 규약(R-0459/R-0460)대로 상신한다. **예보는 Phase 0 빚 스캔과 Phase 2 step 6(G2 registry 게이트)의 실행·증거 요구를 어떤 형태로도 대체·축약하지 않는다** — 예보의 기준선은 «스텁 제외 현재 상태»라 `build_anchor` 를 읽지도 쓰지도 않으며, HEAD 판형 게이트 결과를 G2 증거로 유용하는 것은 차분 세탁으로 금지다. **계약 실존 채널도 G0 선행 조건 확인·상류 머지 판단(발주자 소관)을 대체하지 않는다 — 하드 검사가 아니다**(2026-09-03). green 의 뜻은 «설계 검증됨»이 아니라 «P/S/I급 결정 계약 위반 예보 0»이다(사각 목록·미시뮬레이션 목록은 리포트가 상시 병기한다). **machine 블록 부재 skip 금지**: file-plan 기계 블록 부재로 실행을 건너뛰지 않는다 — 부재는 형식 red(exit 3 «블록 부재»)이고 file-plan 0행(빈 펜스·주석뿐)도 형식 red(«블록 공허»)이며 반송은 위 형식 red 조항을 따른다(캐시 skip(아래 판형 ①)·실체화 0 skip(exit 4 — 공허 차분 가드)과 구별). 신규·개정·구형 명세를 가리지 않는다 — 구형 명세(형식 규범 이전 승인)는 개정 시점에 블록을 소급 작성한다(기준선 실존 경로는 `update` · 부재 경로만 `add`). *왜* — 승인 명세가 registry 결정 계약과 조인되지 않은 채 동결되면 그 위반은 G1 이후 반송(레인당 평균 ≈34분)으로야 드러난다: 같은 판정 의미론을 승인 전에 결정적으로 돌리면 그 손실이 배너의 예보 1행으로 당겨진다.\n\n"@ko .
+    djr:text "**pre-gate — 설계 명세 결정적 예보(차단 모드)**: `design-spec.md` 내용이 바뀔 때마다 실행한다 — architect 초안 수신 직후(위 2의 리뷰 다발과 병렬 1회 — 조기 신호), 리뷰 반영·개정 수신마다, 그리고 **G1/G1′ 배너 제시 직전 최종본과 G1 override(②/③) 반영 후 Phase 2 dispatch 전에는 무조건**(배너의 예보 1행은 항상 최종본에 대한 것 — 낡은 green 금지). 실행 판형은 `scripts/design_pregate.py <산출물 폴더>/design-spec.md . --report <산출물 폴더>/pregate-report.md` 다(`scripts/…` 는 registry 게이트와 같은 규약 — 스킬 폴더의 절대 경로로 펴고 cwd 는 타깃 프로젝트 루트다 · 기계가독 블록 해시가 불변이면 재실행을 skip 한다 — 캐시가 직렬 비용을 없앤다). 팬텀 스텁·git 호출은 전부 스크립트가 격리 사본(저장소 트리 밖) 위에서 수행하는 **결정적 투영물**이라 «구현 코드는 직접 쓰지 않는다» 경계와 충돌하지 않는다 — 너는 이 절차를 위해 bare git 을 직접 치지 않는다. 이 실행은 **게이트다**(차단 모드 — 2026-09-03 승격): 귀속 red(exit 2)·형식 red(exit 3 — 문법·블록 부재·블록 공허·add 충돌·update/remove 대상 기준선 부재 전부)는 architect **반송 의무**이며, red 인 최종본은 G1/G1′ 배너·무배너 재승인·Phase 2 슬라이스 dispatch 어느 것의 근거도 될 수 없다(`--base` 재발화의 red 도 같다 — G2 앵커 차분은 기실현 실물의 판정자이지 계획 red 의 대체가 아니다). 예보가 red 가 아닐 때(exit 0·4·5)만 배너를 제시하고, **배너(G1/G1′)의 근거는 언제나 `scripts/design_pregate.py <산출물 폴더>/design-spec.md . --check-report <산출물 폴더>/pregate-report.md` 의 exit 0 이다**(마지막 예보 절의 블록 해시 = 최종본 해시 ∧ 판정 비형식red ∧ red 면 예보 항목 전건 처분 기재 — 자기 판정이 아니다 · 낡은 green 은 stale 로 선다). 반송 없이 배너를 내는 유일한 경로는 **귀속 red(exit 2)의 예보 항목 전건**에 `ignored(빚: <legacy-debt 파일:행> · STOP <문서 경로>)` 또는 `filtered(ⓐ S<n> | ⓑ <같은 형태 실코드 경로 · 검사기 exit 0>)` 를 pregate-report 에 위 «처분 행 정형»(산출물 위치 절)으로 기재하고 배너 예보 1행에 `귀속 N건(처분 전건 기재)` 를 병기하는 것뿐이다 — `corrected` 는 이 경로에 없다(corrected 의 증거는 재실행에서의 소멸이라 재실행 결과가 곧 최종본이다 · corrected 행에는 «소멸 run 시각 · 블록 해시 전→후» 를 병기한다). 형식 red 는 안정 ID 가 없으므로 이 경로 자체가 없다. 계약 실존 결손(e-ID)은 «전건» 에 들지 않는다(exit 5 비차단 — 별도 게이트). 개정 수신 후 재실행 시점마다 각 red 의 처분 라벨을 그 red 절 뒤에 append 한다(이전 절의 처분은 재기재 — `--check-report` 는 마지막 절 이후만 읽는다). **라벨의 뜻은 채널별 닫힌 정의다** — **예보 항목(registry 귀속·선언 확정)의 처분 라벨은 `corrected | ignored | filtered`** 다: `corrected` = 개정으로 해소(다음 실행에서의 소멸이 증거) · `ignored` = 실위반으로 인지하되 개정하지 않음(실위반 확인 증거는 G2 귀속 red 해소 트레이스 **또는** legacy-debt 매칭 기록(STOP 병기) 둘 중 하나다 — 이관 빚 수용이 이 라벨이다 · 배너 시점에는 후자만 적법하다 — 전자는 G1 시점에 존재할 수 없다) · `filtered` = pre-gate 도구(스텁·문법·시뮬레이션) 한계 판정 — 이 채널에 `deferred` 는 없다(이연은 ignored+빚 매칭 또는 filtered 다). `filtered` 의 근거 유형은 둘뿐이다: ⓐ 리포트 사각 목록 항목 번호 인용(`S<n>` — 그 항목이 이 red 의 오탐 원인임을 한 줄로 잇는다) ⓑ 같은 형태의 실코드 파일이 해당 검사기에서 exit 0 인 대조 경로. **검사기 소스에서 판정 입력이 경로·폴더·파일 이름의 존재뿐인 구조 규칙**(rule-owner-map 등급 path — 예: #81 BC 직계 · #325 ORM 산출물 위치 · #188 area 1:1 · #318 driven_layer 자식 · #336 중앙 마이그레이션 · #490 트리 밖 경로)은 스텁 내용과 무관하므로 ⓑ 가 성립할 수 없고 filtered 대상이 아니다 — corrected 또는 ignored+빚 매칭이다. 경로와 내용을 함께 보는 규칙(예: #392 factories/ 의 factory_boy 부재)은 ⓑ 근거를 대면 filtered 가 가능하다. **계약 실존 결손(리포트 «계약 실존» 절 · 안정 ID `e-…`)의 처분 라벨은 `corrected | deferred | filtered`** 다(2026-09-03): `corrected` = 대상 실존 확보(다음 실행에서 실존 확인 K 증가·결손 소멸) 또는 경로 오기 정정(대상 기실존) — 행 삭제·소비 철회로 결손이 소멸하면 직전 리포트 대비 «결손 소멸 ∧ 행 수 R 감소»가 그것을 드러내며 처분은 `corrected(철회: <근거>)` 로 근거 병기 의무다(발주자 사안이면 STOP) · `deferred`(선행 대기) = 결손 대상이 상류 레인/후행 슬라이스 소유임을 명세가 명시하고 해소 조건을 병기한다 — 정형 `deferred(<소유 레인|Sn>; until <머지 SHA|Sn>)` 권고 · 증거는 조건 충족 시점 재실행에서의 소멸이다(dirty overlay·기준선 갱신이 자동 반영) · `filtered` = 도구 한계(네임스페이스 레이아웃·`import *`·파싱 불능 등 판정 불능 U 계열 — 근거 병기 의무) — 이 채널에 `ignored` 는 없다(부재는 수용 가능한 위반이 아니라 ImportError 예약이며 G2 귀속·legacy-debt 어느 증거도 성립하지 않는다). 실존 채널은 승격 판정식(P/S/I 표면 ∩ G2 귀속)의 **입력이 아니다** — 결손 건수·처분 분포·도구 오류를 별도 계수로만 보고한다(설계 v4 §8 ⑷). 각 채널의 정의 밖 재량 라벨은 없다 — 같은 도구 한계를 레인마다 다른 라벨로 처분하면 승격 판정식이 오염된다(2026-09-02 관찰 레인 1·2 실측). 결손은 권고다 — 도구가 레인을 세우지 않으며(exit 5 는 비차단), 선행 대기가 발주자 결정 사안이면 기존 STOP 규약(R-0459/R-0460)대로 상신한다. **예보는 Phase 0 빚 스캔과 Phase 2 step 6(G2 registry 게이트)의 실행·증거 요구를 어떤 형태로도 대체·축약하지 않는다** — 예보의 기준선은 «스텁 제외 현재 상태»라 `build_anchor` 를 읽지도 쓰지도 않으며, HEAD 판형 게이트 결과를 G2 증거로 유용하는 것은 차분 세탁으로 금지다. **계약 실존 채널도 G0 선행 조건 확인·상류 머지 판단(발주자 소관)을 대체하지 않는다 — 하드 검사가 아니다**(2026-09-03). 선언 검증은 실체화 0에서도 수행한다. 선언 확정은 귀속 red와 같은 전건 처분 의무/exit 2이고, 선언 후보와 생성 본문 S1 미검증은 별도 비차단 보고다. S1은 생성 위치·원본 record·정확한 슬롯 결합이 증명된 #376(after_commit 메서드)/#645/#647에 한하며 #566·bare Any·기존 실코드·미결합 진단은 유지한다. 명시 효과와 출처 결합 DTO의 지원 밖은 S2, 물리 import 전사 밖은 S3, update의 기존 본문 및 지원 밖 후상태는 S5로 남는다. green 의 뜻은 «설계 검증됨»이 아니라 «P/S/I급 결정 계약 위반 및 선언 확정 예보 0»이다(사각 목록·미시뮬레이션 목록은 리포트가 상시 병기한다). **machine 블록 부재 skip 금지**: file-plan 기계 블록 부재로 실행을 건너뛰지 않는다 — 부재는 형식 red(exit 3 «블록 부재»)이고 file-plan 0행(빈 펜스·주석뿐)도 형식 red(«블록 공허»)이며 반송은 위 형식 red 조항을 따른다(캐시 skip(아래 판형 ①)·실체화 0 skip(exit 4 — 선언 확정·실존 결손 없는 공허 차분 가드)과 구별). 신규·개정·구형 명세를 가리지 않는다 — 구형 명세(형식 규범 이전 승인)는 개정 시점에 블록을 소급 작성한다(기준선 실존 경로는 `update` · 부재 경로만 `add`). *왜* — 승인 명세가 registry 결정 계약과 조인되지 않은 채 동결되면 그 위반은 G1 이후 반송(레인당 평균 ≈34분)으로야 드러난다: 같은 판정 의미론을 승인 전에 결정적으로 돌리면 그 손실이 배너의 예보 1행으로 당겨진다.\n\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/commands/dddjango.md/s007> a djr:Section ;
     djr:headingSnapshot "## Phase 2 — 구현 (G2, 이중 루프 TDD)"@ko ;
     djr:inDocument <https://numchida.com/ns/djr#d/dddjango/commands/dddjango.md> ;
     djr:sectionOwner djr:owner-graph .
 
 <https://numchida.com/ns/djr#s/dddjango/commands/dddjango.md/s007/b1> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/commands/dddjango.md/s007> ;
     djr:kind djr:kind-norm ;
     djr:order 1 ;

```

## ontology/rules/discipline-houserules-final.ttl

Before SHA256: d9541bba84466676267f3c0f2c6d05f54a7ed97e04501f9863da6820ea183d40
After SHA256: bb03b9469a1fcef876db4f1c31287c0c34cea9585aeeda45cea886268835306a

```diff
--- before/ontology/rules/discipline-houserules-final.ttl
+++ after/ontology/rules/discipline-houserules-final.ttl
@@ -546,26 +546,32 @@
 
 djr:R-3409 a djr:Prohibition ;
     skos:prefLabel "승격 폴더 내부 파일 신설 재량 부정 — 신설 근거는 감사 발견·부품별 #192/#189 적용·정크드로어 금지"@ko ;
     djr:currentExpression <https://numchida.com/ns/djr#R-3409@2026-09-01> .
 
 <https://numchida.com/ns/djr#R-3409@2026-09-01> a djr:Expression ;
     prov:specializationOf djr:R-3409 ;
     djr:revision 1 .
 
 djr:R-3410 a djr:Obligation ;
-    skos:prefLabel "부품 출생 50행 하한과 부품 0개 퇴화의 환원 신호"@ko ;
-    djr:currentExpression <https://numchida.com/ns/djr#R-3410@2026-09-01> .
+    skos:prefLabel "부품 0 승격 폴더 환원 신호·신규 산출/기존 빚 처분"@ko ;
+    djr:currentExpression <https://numchida.com/ns/djr#R-3410@2026-09-11> .
 
 <https://numchida.com/ns/djr#R-3410@2026-09-01> a djr:Expression ;
     prov:specializationOf djr:R-3410 ;
     djr:revision 1 .
+
+<https://numchida.com/ns/djr#R-3410@2026-09-11> a djr:Expression ;
+    prov:specializationOf djr:R-3410 ;
+    prov:wasRevisionOf <https://numchida.com/ns/djr#R-3410@2026-09-01> ;
+    djr:revision 2 ;
+    djr:revisionKind djr:revision-amendment .
 
 djr:R-3411 a djr:Obligation ;
     skos:prefLabel "저장(save)류 쓰기 호출의 본체 한정"@ko ;
     djr:currentExpression <https://numchida.com/ns/djr#R-3411@2026-09-01> .
 
 <https://numchida.com/ns/djr#R-3411@2026-09-01> a djr:Expression ;
     prov:specializationOf djr:R-3411 ;
     djr:revision 1 .
 
 djr:R-3412 a djr:Obligation ;
@@ -606,26 +612,32 @@
     prov:specializationOf djr:R-3423 ;
     djr:revision 1 .
 
 <https://numchida.com/ns/djr#R-3423@2026-09-09> a djr:Expression ;
     prov:specializationOf djr:R-3423 ;
     prov:wasRevisionOf <https://numchida.com/ns/djr#R-3423@2026-09-01> ;
     djr:revision 2 ;
     djr:revisionKind djr:revision-amendment .
 
 djr:R-3468 a djr:Obligation ;
-    skos:prefLabel "#651 — 어댑터 고정 역할의 클래스별 파일과 상수 묶음"@ko ;
-    djr:currentExpression <https://numchida.com/ns/djr#R-3468@2026-09-09> .
+    skos:prefLabel "어댑터 고정 역할 골격과 승격 신호 비적용"@ko ;
+    djr:currentExpression <https://numchida.com/ns/djr#R-3468@2026-09-11> .
 
 <https://numchida.com/ns/djr#R-3468@2026-09-09> a djr:Expression ;
     prov:specializationOf djr:R-3468 ;
     djr:revision 1 .
+
+<https://numchida.com/ns/djr#R-3468@2026-09-11> a djr:Expression ;
+    prov:specializationOf djr:R-3468 ;
+    prov:wasRevisionOf <https://numchida.com/ns/djr#R-3468@2026-09-09> ;
+    djr:revision 2 ;
+    djr:revisionKind djr:revision-amendment .
 
 djr:R-3469 a djr:Obligation ;
     skos:prefLabel "어댑터 고정 골격과 역할 소유·builder·reader·상수·별칭 배치"@ko ;
     djr:currentExpression <https://numchida.com/ns/djr#R-3469@2026-09-09> .
 
 <https://numchida.com/ns/djr#R-3469@2026-09-09> a djr:Expression ;
     prov:specializationOf djr:R-3469 ;
     djr:revision 1 .
 
 <https://numchida.com/ns/djr#d/dddjango/skills/discipline-houserules/references/final.md> a djr:Document ;
@@ -680,35 +692,35 @@
     djr:kind djr:kind-norm ;
     djr:order 1 ;
     djr:statesNorm djr:R-3178 ;
     djr:text "\n**모든 검사보다 먼저 서는 원칙이다**(#487 — 골격이 어긋나면 나머지 검사를 돌릴 이유가 없다).\n\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/references/final.md/s003-0/b10> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/references/final.md/s003-0> ;
     djr:kind djr:kind-norm ;
     djr:order 10 ;
     djr:statesNorm djr:R-3409, djr:R-3410, djr:R-3411 ;
-    djr:text "승격 폴더는 «트리가 리프로 닫은 폴더»가 아니다 — 내부 재량은 **배열·명명 재량**이지 **파일 신설 재량이 아니다**. 부품 파일의 신설 근거는 감사 판정(동명 폴더 승격 발견)의 클러스터 열거 또는 후속 감사 신호뿐이고, #192(사설 조각은 제 파일 안 `_` 함수)·#189(유스케이스 간 돌려쓰기 금지)가 부품 파일 각각에 그대로 적용되며, 정크드로어 이름(`utils.py`·`helpers.py` 류)은 위반이다. 이번 작업에서 새로 나타난 승격 폴더의 각 부품(본체·`__init__.py` 제외)은 50행(물리 행·빈 줄 제외) 이상이어야 하고(출생 하한 — 기존 폴더의 사후 축소는 무관·환원 의무를 만들지 않는다), 부품이 0개(본체+`__init__.py` 뿐)가 된 승격 폴더는 위반이다(환원 신호 — 이번 작업 산출이면 발견 반영으로, 기존이면 G0 빚 경로로 환원한다). 저장(save)류 쓰기 호출은 본체에만 둔다.\n"@ko .
+    djr:text "승격 폴더는 «트리가 리프로 닫은 폴더»가 아니다 — 내부 재량은 **배열·명명 재량**이지 **파일 신설 재량이 아니다**. 부품 파일의 신설 근거는 감사 판정(동명 폴더 승격 발견)의 클러스터 열거 또는 후속 감사 신호뿐이고, #192(사설 조각은 제 파일 안 `_` 함수)·#189(유스케이스 간 돌려쓰기 금지)가 부품 파일 각각에 그대로 적용되며, 정크드로어 이름(`utils.py`·`helpers.py` 류)은 위반이다. 부품이 0개(본체+`__init__.py` 뿐)가 된 승격 폴더는 위반이다(환원 신호 — 이번 작업 산출이면 발견 반영으로, 기존이면 G0 빚 경로로 환원한다). 저장(save)류 쓰기 호출은 본체에만 둔다.\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/references/final.md/s003-0/b11> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/references/final.md/s003-0> ;
     djr:kind djr:kind-norm ;
     djr:order 11 ;
     djr:statesNorm djr:R-3412, djr:R-3413, djr:R-3414 ;
     djr:text "칸을 «파일»로 명명하는 규범·검사기 문면(#256·#123·#193 …)은 그 칸의 실현 — 파일 또는 승격 본체 — 을 가리킨다. 승격 허용 표기의 값은 §1 트리가 소유한다(정본 `docs/file_tree.html` 의 data-sw · `standard_tree.Row.swappable` — 허용 칸: 트리 12·14·15·18·20·21·24·41·61·74·92·94·96행). 배제는 사유로만 선다 — ⓐ 범위 밖 서브트리(`framework/**`·`<project>/**`)·비-py(templates) ⓑ 도구 생성물(migrations) ⓒ 형태 명문 고정(composition_root #497 · api_router #107 · cron_job #174/#178 · event_subscription #509 · event_router #508 · apps #535/#538 · bc_error_schema #114/#572 · admin panel #342/#343) ⓓ 개념 원자 — 성장 출구가 새 인스턴스 파일(entity·값 객체·event·exception·계약·port 선언·domain repository 선언·`<entity>_model` #335 …). 배제 칸의 비대는 그 칸의 기존 규범이 관할한다 — 승격은 출구가 아니다. 배제·허용 표기를 바꾸는 주어는 정본 트리(트리 개정)다 — 프로젝트 관찰·판정 반복은 개정 제안 신호이지 현장 변경 근거가 아니다.\n\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/references/final.md/s003-0/b12> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/references/final.md/s003-0> ;
     djr:kind djr:kind-norm ;
     djr:order 12 ;
     djr:statesNorm djr:R-3468, djr:R-3469 ;
-    djr:text "**어댑터 고정 골격** — `driven_layer/adapter/` 아래 ACL의 `anticorruption_layer/<other_bounded_context>/<capability>_adapter/`, 외부 시스템의 `external_system/<system>/<capability>_adapter/`, 그 밖 능력의 `<capability>/<technology>_adapter/` 는 처음부터 패키지다. 바깥 패키지와 `adapter/`·`command/`·`constant/`·`contract/`·`schema/` 다섯 역할 폴더에 `__init__.py` 를 반드시 둔다(#488). 역할 폴더는 내용이 없어도 생략하지 않는다. 초기화 파일은 재수출 전용이다(#640). 바깥에 구현 본체를 두거나 단일 `.py` 파일로 대체하지 않으며, 역할 폴더 안에 추가 폴더를 만들지 않는다(#490). 실제 내용 파일은 필요할 때만 만들며 50행 하한·200행 승격 신호의 대상이 아니다.\n\n**#651 클래스별 파일** — `adapter/`·`command/`·`contract/`·`schema/` 의 내용 파일은 비공개 클래스를 포함해 클래스 하나당 파일 하나다. 같은 역할의 클래스가 여러 개면 각각 파일을 만든다. `constant/` 는 클래스 없이 관련 상수끼리 한 파일에 묶는다. 내용 없는 골격 파일과 재수출 초기화 파일은 클래스 수 검사의 대상이 아니다.\n\n**역할 배치** — `adapter/` 는 포트를 구현하는 클래스를 소유한다. 외부 응답을 포트 반환값으로 바꾸는 reader 는 그 구현의 private 메서드 또는 본문에 둔다. `command/` 는 주입되는 호출 계약(Protocol 등)을 클래스별로 둔다. `contract/` 는 내부 계약 클래스를 소유하며 그 계약을 반환하는 builder 도 같은 파일에 둔다. `schema/` 는 외부 입출력 검증 클래스를 소유하며 관련 타입 별칭은 해당 스키마 파일에 둔다. `constant/` 는 프롬프트 등 관련 값을 `prompt.py` 같은 응집된 묶음으로 둔다. 반환 클래스가 포트 소유라는 이유로 외부 스키마를 아는 변환 함수를 포트 파일로 옮기지 않는다. 내부 참조는 모듈 직접 상대 import 로 연결한다. 기존 상속·명명·예외 번역 검사는 구현 역할 파일에, 의존 방향과 격리는 전체 역할 파일에 적용한다.\n"@ko .
+    djr:text "**어댑터 고정 골격** — `driven_layer/adapter/` 아래 ACL의 `anticorruption_layer/<other_bounded_context>/<capability>_adapter/`, 외부 시스템의 `external_system/<system>/<capability>_adapter/`, 그 밖 능력의 `<capability>/<technology>_adapter/` 는 처음부터 패키지다. 바깥 패키지와 `adapter/`·`command/`·`constant/`·`contract/`·`schema/` 다섯 역할 폴더에 `__init__.py` 를 반드시 둔다(#488). 역할 폴더는 내용이 없어도 생략하지 않는다. 초기화 파일은 재수출 전용이다(#640). 바깥에 구현 본체를 두거나 단일 `.py` 파일로 대체하지 않으며, 역할 폴더 안에 추가 폴더를 만들지 않는다(#490). 실제 내용 파일은 필요할 때만 만들며 200행 승격 신호의 대상이 아니다.\n\n**#651 클래스별 파일** — `adapter/`·`command/`·`contract/`·`schema/` 의 내용 파일은 비공개 클래스를 포함해 클래스 하나당 파일 하나다. 같은 역할의 클래스가 여러 개면 각각 파일을 만든다. `constant/` 는 클래스 없이 관련 상수끼리 한 파일에 묶는다. 내용 없는 골격 파일과 재수출 초기화 파일은 클래스 수 검사의 대상이 아니다.\n\n**역할 배치** — `adapter/` 는 포트를 구현하는 클래스를 소유한다. 외부 응답을 포트 반환값으로 바꾸는 reader 는 그 구현의 private 메서드 또는 본문에 둔다. `command/` 는 주입되는 호출 계약(Protocol 등)을 클래스별로 둔다. `contract/` 는 내부 계약 클래스를 소유하며 그 계약을 반환하는 builder 도 같은 파일에 둔다. `schema/` 는 외부 입출력 검증 클래스를 소유하며 관련 타입 별칭은 해당 스키마 파일에 둔다. `constant/` 는 프롬프트 등 관련 값을 `prompt.py` 같은 응집된 묶음으로 둔다. 반환 클래스가 포트 소유라는 이유로 외부 스키마를 아는 변환 함수를 포트 파일로 옮기지 않는다. 내부 참조는 모듈 직접 상대 import 로 연결한다. 기존 상속·명명·예외 번역 검사는 구현 역할 파일에, 의존 방향과 격리는 전체 역할 파일에 적용한다.\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/references/final.md/s003-0/b2> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/references/final.md/s003-0> ;
     djr:kind djr:kind-norm ;
     djr:order 2 ;
     djr:statesNorm djr:R-3179, djr:R-3180 ;
     djr:text "- **#486** — 어느 BC 를 열어도 이 트리의 골격이 «그대로» 있다 — 내용이 있든 없든 상관없다. 파일트리를 지키지 않는 구현·설계는 «반환»이다.\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/references/final.md/s003-0/b3> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/references/final.md/s003-0> ;

```

## ontology/rules/discipline-houserules-skill.ttl

Before SHA256: 6e3374ffec14a4cce4869a9072b10da58da4419ef89f2c35e6506e650816449e
After SHA256: 9f05cfd377fd819ac9e7abed29aee1283e9c5d9afa9144a7e6a58ca5c43f8a6a

```diff
--- before/ontology/rules/discipline-houserules-skill.ttl
+++ after/ontology/rules/discipline-houserules-skill.ttl
@@ -666,33 +666,39 @@
 
 djr:R-3416 a djr:Obligation ;
     skos:prefLabel "캐스케이드 ① 이동 — 수용성 확인·목적지 산출물 목록 한정·부품에도 적용"@ko ;
     djr:currentExpression <https://numchida.com/ns/djr#R-3416@2026-09-01> .
 
 <https://numchida.com/ns/djr#R-3416@2026-09-01> a djr:Expression ;
     prov:specializationOf djr:R-3416 ;
     djr:revision 1 .
 
 djr:R-3417 a djr:Obligation ;
-    skos:prefLabel "캐스케이드 ② 동명 폴더 승격 — 역할 밖 응집 술어(상태 클래스/참조 폐쇄 클러스터)·개별 50행 하한·관례 동거 예외·부품은 형제 분할·집행 전 모듈 객체 참조처 조사(패치 표면)"@ko ;
-    djr:currentExpression <https://numchida.com/ns/djr#R-3417@2026-09-01b> .
+    skos:prefLabel "소관·응집으로 동명 폴더 승격·행수 하한 없이 참조 전수 조사"@ko ;
+    djr:currentExpression <https://numchida.com/ns/djr#R-3417@2026-09-11> .
 
 <https://numchida.com/ns/djr#R-3417@2026-09-01> a djr:Expression ;
     prov:specializationOf djr:R-3417 ;
     djr:revision 1 .
 
 <https://numchida.com/ns/djr#R-3417@2026-09-01b> a djr:Expression ;
     prov:specializationOf djr:R-3417 ;
     prov:wasRevisionOf <https://numchida.com/ns/djr#R-3417@2026-09-01> ;
     djr:revision 2 ;
     djr:revisionKind djr:revision-amendment .
 
+<https://numchida.com/ns/djr#R-3417@2026-09-11> a djr:Expression ;
+    prov:specializationOf djr:R-3417 ;
+    prov:wasRevisionOf <https://numchida.com/ns/djr#R-3417@2026-09-01b> ;
+    djr:revision 3 ;
+    djr:revisionKind djr:revision-amendment .
+
 djr:R-3418 a djr:Obligation ;
     skos:prefLabel "캐스케이드 ③ 유지 — 본업 비대·역할 내 초대형은 한 파일"@ko ;
     djr:currentExpression <https://numchida.com/ns/djr#R-3418@2026-09-01> .
 
 <https://numchida.com/ns/djr#R-3418@2026-09-01> a djr:Expression ;
     prov:specializationOf djr:R-3418 ;
     djr:revision 1 .
 
 djr:R-3419 a djr:Obligation ;
     skos:prefLabel "감사 주도 배정 — coder 비발동·판정은 감사자·집행은 발견 반영"@ko ;
@@ -730,62 +736,86 @@
     prov:specializationOf djr:R-3421 ;
     djr:revision 1 .
 
 <https://numchida.com/ns/djr#R-3421@2026-09-09> a djr:Expression ;
     prov:specializationOf djr:R-3421 ;
     prov:wasRevisionOf <https://numchida.com/ns/djr#R-3421@2026-09-01> ;
     djr:revision 2 ;
     djr:revisionKind djr:revision-amendment .
 
 djr:R-3447 a djr:Prohibition ;
-    skos:prefLabel "Any 금지 — 시그니처(별표 인자 포함)·변수·클래스 속성·제네릭 인자 전부 · 프레임워크 오버라이드도 object/정확 타입 · 시그니처는 #645 차단·그 밖은 ⓓ 후보(#645) · dict/Mapping 값 자리 Any 는 #647 차단"@ko ;
-    djr:currentExpression <https://numchida.com/ns/djr#R-3447@2026-09-04b> .
+    skos:prefLabel "Any 기존 금지/후보와 확인된 framework admin 슬롯 제한 허용"@ko ;
+    djr:currentExpression <https://numchida.com/ns/djr#R-3447@2026-09-11> .
 
 <https://numchida.com/ns/djr#R-3447@2026-09-04> a djr:Expression ;
     prov:specializationOf djr:R-3447 ;
     djr:revision 1 .
 
 <https://numchida.com/ns/djr#R-3447@2026-09-04b> a djr:Expression ;
     prov:specializationOf djr:R-3447 ;
     prov:wasRevisionOf <https://numchida.com/ns/djr#R-3447@2026-09-04> ;
     djr:revision 2 ;
     djr:revisionKind djr:revision-amendment .
 
+<https://numchida.com/ns/djr#R-3447@2026-09-11> a djr:Expression ;
+    prov:specializationOf djr:R-3447 ;
+    prov:wasRevisionOf <https://numchida.com/ns/djr#R-3447@2026-09-04b> ;
+    djr:revision 3 ;
+    djr:revisionKind djr:revision-amendment .
+
 djr:R-3448 a djr:Obligation ;
-    skos:prefLabel "경계 입력은 object/정확 타입으로 받아 받는 즉시 좁힘(TypeIs·isinstance·type() is · 자리는 architecture-ddd §3.1) · JSON 은 TypeAdapter(TypedDict) 검증 파싱 · object 는 입구 매개변수·즉시 검증 지역 변수만(반환/속성 누수 #647 차단 · 반환 자리표시 object·json.load 무검증 흐름은 ⓓ #647/#650 · 예외 프레임워크 콜백 미러·이벤트 컬렉션) · 면제 Form.clean·TypeIs"@ko ;
-    djr:currentExpression <https://numchida.com/ns/djr#R-3448@2026-09-04b> .
+    skos:prefLabel "경계 object 즉시 좁힘·JSON 검증 유지·admin UI context 실제 소비 경계"@ko ;
+    djr:currentExpression <https://numchida.com/ns/djr#R-3448@2026-09-11> .
 
 <https://numchida.com/ns/djr#R-3448@2026-09-04> a djr:Expression ;
     prov:specializationOf djr:R-3448 ;
     djr:revision 1 .
 
 <https://numchida.com/ns/djr#R-3448@2026-09-04b> a djr:Expression ;
     prov:specializationOf djr:R-3448 ;
     prov:wasRevisionOf <https://numchida.com/ns/djr#R-3448@2026-09-04> ;
     djr:revision 2 ;
     djr:revisionKind djr:revision-redefinition .
 
+<https://numchida.com/ns/djr#R-3448@2026-09-11> a djr:Expression ;
+    prov:specializationOf djr:R-3448 ;
+    prov:wasRevisionOf <https://numchida.com/ns/djr#R-3448@2026-09-04b> ;
+    djr:revision 3 ;
+    djr:revisionKind djr:revision-amendment .
+
 djr:R-3451 a djr:Prohibition ;
-    skos:prefLabel "레코드(키 고정 값 묶음)를 딕셔너리로 들고 다니지 않는다 — 내부 리터럴은 TypedDict · 파싱 JSON 은 TypeAdapter 검증 · 도메인 개념은 값 객체 · dict/Mapping[str, object|Any] 주석은 구조 미정 신호(#647)"@ko ;
-    djr:currentExpression <https://numchida.com/ns/djr#R-3451@2026-09-04> .
+    skos:prefLabel "업무 레코드 구조 선언과 framework admin UI context 구분"@ko ;
+    djr:currentExpression <https://numchida.com/ns/djr#R-3451@2026-09-11> .
 
 <https://numchida.com/ns/djr#R-3451@2026-09-04> a djr:Expression ;
     prov:specializationOf djr:R-3451 ;
     djr:revision 1 .
 
+<https://numchida.com/ns/djr#R-3451@2026-09-11> a djr:Expression ;
+    prov:specializationOf djr:R-3451 ;
+    prov:wasRevisionOf <https://numchida.com/ns/djr#R-3451@2026-09-04> ;
+    djr:revision 2 ;
+    djr:revisionKind djr:revision-amendment .
+
 djr:R-3452 a djr:Obligation ;
-    skos:prefLabel "레코드(내부 리터럴) → TypedDict(종류 여럿이면 kind: Literal 판별 키 union) · dict/Mapping[str, object|Any] 금지"@ko ;
-    djr:currentExpression <https://numchida.com/ns/djr#R-3452@2026-09-04> .
+    skos:prefLabel "업무 레코드 TypedDict와 admin context 조립 경계"@ko ;
+    djr:currentExpression <https://numchida.com/ns/djr#R-3452@2026-09-11> .
 
 <https://numchida.com/ns/djr#R-3452@2026-09-04> a djr:Expression ;
     prov:specializationOf djr:R-3452 ;
     djr:revision 1 .
+
+<https://numchida.com/ns/djr#R-3452@2026-09-11> a djr:Expression ;
+    prov:specializationOf djr:R-3452 ;
+    prov:wasRevisionOf <https://numchida.com/ns/djr#R-3452@2026-09-04> ;
+    djr:revision 2 ;
+    djr:revisionKind djr:revision-amendment .
 
 djr:R-3453 a djr:Obligation ;
     skos:prefLabel "레코드(파싱한 JSON — 파일·타 시스템·json.loads · 우리가 쓴 파일도) → TypeAdapter(TypedDict).validate_python/json 검증 파싱(HTTP body 는 ninja Schema) · 파싱 전 값 사용 금지 · 검증 없는 -> TypedDict 반환·Any/object 흘리기 금지(ⓓ #650)"@ko ;
     djr:currentExpression <https://numchida.com/ns/djr#R-3453@2026-09-04> .
 
 <https://numchida.com/ns/djr#R-3453@2026-09-04> a djr:Expression ;
     prov:specializationOf djr:R-3453 ;
     djr:revision 1 .
 
 djr:R-3454 a djr:Obligation ;
@@ -806,26 +836,32 @@
 
 djr:R-3456 a djr:Obligation ;
     skos:prefLabel "구조 없는 임의 JSON 통과(직렬화·저장 경계) → 재귀 별칭 JsonValue(공변 Sequence/Mapping arm) · dict[str, object]·Any 금지"@ko ;
     djr:currentExpression <https://numchida.com/ns/djr#R-3456@2026-09-04> .
 
 <https://numchida.com/ns/djr#R-3456@2026-09-04> a djr:Expression ;
     prov:specializationOf djr:R-3456 ;
     djr:revision 1 .
 
 djr:R-3457 a djr:Obligation ;
-    skos:prefLabel "타입이 이미 있는 값(반환·매개변수·속성) → 실제 클래스 · 입구 밖 자리표시 object 금지(입구 매개변수·즉시 검증 지역 변수는 R-3448 · 반환 주석 object 는 ⓓ #647)"@ko ;
-    djr:currentExpression <https://numchida.com/ns/djr#R-3457@2026-09-04> .
+    skos:prefLabel "실제 타입 사용과 admin framework 슬롯 구분"@ko ;
+    djr:currentExpression <https://numchida.com/ns/djr#R-3457@2026-09-11> .
 
 <https://numchida.com/ns/djr#R-3457@2026-09-04> a djr:Expression ;
     prov:specializationOf djr:R-3457 ;
     djr:revision 1 .
+
+<https://numchida.com/ns/djr#R-3457@2026-09-11> a djr:Expression ;
+    prov:specializationOf djr:R-3457 ;
+    prov:wasRevisionOf <https://numchida.com/ns/djr#R-3457@2026-09-04> ;
+    djr:revision 2 ;
+    djr:revisionKind djr:revision-amendment .
 
 djr:R-3458 a djr:Obligation ;
     skos:prefLabel "django-stubs 제네릭 Django 기저(기본값 없는 타입 매개변수 — ModelForm·BaseInlineFormSet·ModelAdmin·InlineModelAdmin·CBV·mixin)는 모델 타입 인자를 적는다 — TYPE_CHECKING 별칭 기본 · monkeypatch 채택(§6.1 관찰) 시 직접 표기 · admin 선언 속성은 재선언 안 함 · 열린 매개변수는 bound"@ko ;
     djr:currentExpression <https://numchida.com/ns/djr#R-3458@2026-09-04> .
 
 <https://numchida.com/ns/djr#R-3458@2026-09-04> a djr:Expression ;
     prov:specializationOf djr:R-3458 ;
     djr:revision 1 .
 
 djr:R-3459 a djr:Prohibition ;
@@ -970,21 +1006,21 @@
     djr:kind djr:kind-norm ;
     djr:order 6 ;
     djr:statesNorm djr:R-3134, djr:R-3135, djr:R-3136, djr:R-3137 ;
     djr:text "**관찰이 결정 입력인 축은 닫힌 목록이다**(라운드 1 「트리 답습」·라운드 1′ 「배선 답습」의 봉인 — 2026-08-12): ① 오류 wire 계약(12-slot `preserve-established`) ② API 스택 «정체»(근거=소비자 의존) ③ 주석 언어(§5) ④ 도구·러너(§6.1) ⑤ 승인 test artifact 의 기존 위치(§1.2) ⑥ 지원 중 행동 계약. **여기 없는 축 — 파일트리·배선/등록·import 방향·테스트 규율·값 집합 선언·인증 경로·admin 구조·OpenAPI 문서 후가공 … — 에서 기존 실물의 관찰은 결정의 입력이 아니다.** 배선 «값»(#105~#112)은 Ninja 스택 조건부지만, ‹관찰 비입력› 원칙 자체는 무조건이다. 그리고 이 원칙은 **신규 산출물의 형태** 문장이다 — 승인 스코프 밖 기존 실물을 옮기거나 고칠 권한을 만들지 않는다(§1.1 판정 물음: 위반 판정은 빚 기록 권한일 뿐, 이동 권한은 G0 사용자 ⓐ 결정→슬라이스 0 한 경로). 그리고 닫힌 목록의 관찰 금지 대상은 **대상 저장소의 기존 실물**이다 — 이번 슬라이스 산출물의 자기 형상은 이 축의 주어가 아니며, «동명 폴더 승격» 캐스케이드(아래) 판정의 유일한 입력이다.\n\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/SKILL.md/s004-1/b7> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/SKILL.md/s004-1> ;
     djr:kind djr:kind-norm ;
     djr:order 7 ;
     djr:statesNorm djr:R-3415, djr:R-3416, djr:R-3417, djr:R-3418 ;
-    djr:text "**어댑터 고정 골격** — 세 종류의 BC 어댑터는 `references/final.md` §0·§1의 고정 역할 패키지로 작성한다. 내용이 없어도 골격을 먼저 실현하고 실제 내용 파일 경로를 명세에 적는다. 이 칸에는 아래 승격 캐스케이드를 적용하지 않는다.\n\n**동명 폴더 승격 캐스케이드** — 승격 허용 칸 파일이 커질 때의 분할 판정이다(값·형태는 `references/final.md` §0 이 소유한다 — #490 교체형). 분할은 **크기가 아니라 소관·응집으로** 가른다 — 행 수는 트리거가 아니라 감사 신호다(`discipline-cleancode` §15.1 의 수치 스멜도 신호다). (명세·G0·감사자는 파이프라인 용어다 — 파이프라인 밖에서는 사용자의 명시적 작업 지시가 명세·G0 ⓐ에 준하고, 검수를 맡은 주체가 감사자에 준한다.)\n\n1. **이동(①)** — 커진 부분이 다른 기존 칸의 소관이면 그 칸으로 옮긴다. 단 이동 후보 칸이 실제로 받을 수 있는지(의존 방향 역류 없음·역할 계약 부합)를 확인한 뒤에만, 그리고 목적지가 승인 산출물 목록 안일 때만 — 목록 밖이면 보고(설계 반송)다. ①은 승격 폴더의 부품에도 그대로 적용된다.\n2. **동명 폴더 승격(②)** — 어느 칸 소관도 아닌 «역할 밖 응집 단위»가 생겼으면 승격한다. 술어(둘 다 충족): (a) 칸의 역할 계약 밖 top-level 정의로서, 자기 상태·수명을 가진 클래스이거나 — 본업 정의가 직접 참조하지 않거나 단일 진입 이름으로만 참조하는 사적 정의들이 **서로만 참조하는 닫힌 성분**을 이루는 무상태 클러스터(예: 모델군+상수+함수 쌍 — 상수 모음만·타입 별칭 모음만·함수 하나는 클러스터가 아니다) (b) 클러스터 **개별 50행 이상**(물리 행·빈 줄 제외). 관례 동거는 예외다(Django Model+Manager+QuerySet(+그 불변 예외)·admin panel+inline). 주어가 승격 폴더 내부 부품이면 ②의 실현은 하위 폴더가 아니라 **형제 부품 파일 분할**이다. 승격을 **집행하기 전에**(발견을 집행하는 coder 는 집행 전 · 기존 파일 승격(G0 ⓐ→슬라이스 0)의 제안·실행자는 제안 전), 대상 모듈을 **모듈 객체·모듈 경로 문자열로 참조하는 곳** — 테스트 fixture 의 monkeypatch, `unittest.mock.patch(\"pkg.mod.attr\")` 문자열형, settings 등 dotted-path 문자열 참조, 동적 import — 을 저장소 전수에서 조사해 발견 전건을 승격 슬라이스 스코프에 편입한다. 재수출 `__init__` 의 import 표면 불변은 **읽기 표면**만 보증하고 **패치 표면**은 보증하지 않는다(패치는 패키지 객체에 걸리고 본체 모듈 전역은 그대로 남는다). 스코프 밖 발견이면 집행 전 보고(설계 반송)다 — 감사자의 판정 재료는 현행 유지다.\n3. **유지(③)** — 둘 다 아니면 한 파일(부품이면 한 부품 파일)을 유지한다. 전부 역할 내인 초대형 파일도 ③이다 — 크기는 트리거가 아니다.\n"@ko .
+    djr:text "**어댑터 고정 골격** — 세 종류의 BC 어댑터는 `references/final.md` §0·§1의 고정 역할 패키지로 작성한다. 내용이 없어도 골격을 먼저 실현하고 실제 내용 파일 경로를 명세에 적는다. 이 칸에는 아래 승격 캐스케이드를 적용하지 않는다.\n\n**동명 폴더 승격 캐스케이드** — 승격 허용 칸 파일이 커질 때의 분할 판정이다(값·형태는 `references/final.md` §0 이 소유한다 — #490 교체형). 분할은 **크기가 아니라 소관·응집으로** 가른다 — 행 수는 트리거가 아니라 감사 신호다(`discipline-cleancode` §15.1 의 수치 스멜도 신호다). (명세·G0·감사자는 파이프라인 용어다 — 파이프라인 밖에서는 사용자의 명시적 작업 지시가 명세·G0 ⓐ에 준하고, 검수를 맡은 주체가 감사자에 준한다.)\n\n1. **이동(①)** — 커진 부분이 다른 기존 칸의 소관이면 그 칸으로 옮긴다. 단 이동 후보 칸이 실제로 받을 수 있는지(의존 방향 역류 없음·역할 계약 부합)를 확인한 뒤에만, 그리고 목적지가 승인 산출물 목록 안일 때만 — 목록 밖이면 보고(설계 반송)다. ①은 승격 폴더의 부품에도 그대로 적용된다.\n2. **동명 폴더 승격(②)** — 어느 칸 소관도 아닌 «역할 밖 응집 단위»가 생겼으면 승격한다. 술어: 칸의 역할 계약 밖 top-level 정의로서, 자기 상태·수명을 가진 클래스이거나 — 본업 정의가 직접 참조하지 않거나 단일 진입 이름으로만 참조하는 사적 정의들이 **서로만 참조하는 닫힌 성분**을 이루는 무상태 클러스터(예: 모델군+상수+함수 쌍 — 상수 모음만·타입 별칭 모음만·함수 하나는 클러스터가 아니다). 관례 동거는 예외다(Django Model+Manager+QuerySet(+그 불변 예외)·admin panel+inline). 주어가 승격 폴더 내부 부품이면 ②의 실현은 하위 폴더가 아니라 **형제 부품 파일 분할**이다. 승격을 **집행하기 전에**(발견을 집행하는 coder 는 집행 전 · 기존 파일 승격(G0 ⓐ→슬라이스 0)의 제안·실행자는 제안 전), 대상 모듈을 **모듈 객체·모듈 경로 문자열로 참조하는 곳** — 테스트 fixture 의 monkeypatch, `unittest.mock.patch(\"pkg.mod.attr\")` 문자열형, settings 등 dotted-path 문자열 참조, 동적 import — 을 저장소 전수에서 조사해 발견 전건을 승격 슬라이스 스코프에 편입한다. 재수출 `__init__` 의 import 표면 불변은 **읽기 표면**만 보증하고 **패치 표면**은 보증하지 않는다(패치는 패키지 객체에 걸리고 본체 모듈 전역은 그대로 남는다). 스코프 밖 발견이면 집행 전 보고(설계 반송)다 — 감사자의 판정 재료는 현행 유지다.\n3. **유지(③)** — 둘 다 아니면 한 파일(부품이면 한 부품 파일)을 유지한다. 전부 역할 내인 초대형 파일도 ③이다 — 크기는 트리거가 아니다.\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/SKILL.md/s004-1/b8> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/SKILL.md/s004-1> ;
     djr:kind djr:kind-norm ;
     djr:order 8 ;
     djr:statesNorm djr:R-3419, djr:R-3420 ;
     djr:text "**감사 주도 배정** — coder 는 이 캐스케이드를 스스로 발동하지 않는다(승격 허용 칸은 파일형으로 작성한다). 신호는 `check-layer-skeleton` 이 후보 채널(ⓓ)로 무조건 방출한다 — 주어는 행위 칸 실현(controller 2종·service·use_case·repo/bypass/uow 구현·aggregate·domain_service — wiring 제외)과 그 칸의 승격 폴더 내부 .py(`__init__.py` 제외)의 200행 초과이고, 페이로드가 행수·top-level 정의 요약을 동봉한다(AST 산출은 백스톱 소유 — 감사자는 응집·소관·독립 변경 이유만 판정한다). **판정 의무의 주어만** «이번 diff 가 만들었거나 키운(판정 앵커 대비 물리 행수 순증>0) 파일»로 한정하고 그 적용자는 감사자다 — rename·`git mv` 는 «만들었음»으로 발화하고, 전 빌드 ③ 판정 파일은 역할 밖 후보가 새로 생긴 diff 에서만 재판정한다(판별 주체=감사자·판정은 감사 리포트에 기록한다). ①/② 판정은 권고가 아니라 반송 대상 발견이고 — coder 가 판단 없이 집행하며 발견의 클러스터 열거가 부품 파일 신설 근거다 — 신호 밖 허용 칸(schema_in/out 등)의 ② 판정은 홀리스틱 감사에서 허용하되 발견문에 «신호 밖 판정»을 명기한다.\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/SKILL.md/s004-1/b9> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/SKILL.md/s004-1> ;
@@ -1085,21 +1121,21 @@
     djr:kind djr:kind-norm ;
     djr:order 1 ;
     djr:statesNorm djr:R-3148, djr:R-3149, djr:R-3150 ;
     djr:text "\n**모든 이름은 «첫 대입»에 타입을 적는다 — 예외 0.** 함수·메서드 시그니처(인자·반환), 모듈 변수, 클래스 변수, **함수 지역 변수**, 테스트와 테스트 재료(`test/fake/`·`factories/`)까지 전부다. 「자명하니까 면제」를 두지 않는다 — 조건부 면제는 매 실행 흔들리는 암묵 판단으로 돌아온다.\n\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/SKILL.md/s007-4/b10> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/SKILL.md/s007-4> ;
     djr:kind djr:kind-table-row ;
     djr:order 10 ;
     djr:statesNorm djr:R-3452 ;
-    djr:text "| 키가 정해진 값 묶음(레코드) | 우리 코드가 리터럴로 만든 내부 데이터 | `TypedDict`(종류가 여럿이면 `kind: Literal[…]` 판별 키로 union) | `dict/Mapping[str, object\\|Any]` |\n" .
+    djr:text "| 키가 정해진 값 묶음(레코드) | 우리 업무 코드가 리터럴로 만든 내부 데이터(admin UI 조립/전달은 앞 절 판정) | `TypedDict`(종류가 여럿이면 `kind: Literal[…]` 판별 키로 union) | `dict/Mapping[str, object\\|Any]` |\n" .
 
 <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/SKILL.md/s007-4/b11> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/SKILL.md/s007-4> ;
     djr:kind djr:kind-table-row ;
     djr:order 11 ;
     djr:statesNorm djr:R-3453 ;
     djr:text "| 키가 정해진 값 묶음 | 파싱한 JSON(파일 `json.load`·타 시스템·`json.loads` — 우리가 쓴 파일도 같다) | `TypeAdapter(그TypedDict).validate_python/validate_json` 로 검증 파싱(HTTP body 는 ninja `Schema` 가 이미 검증) · 파싱 전 값 사용 금지 | 검증 없는 `-> TypedDict` 반환(strict `no-any-return`) · `Any`/`object` 로 흘리기(ⓓ #650) |\n" .
 
 <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/SKILL.md/s007-4/b12> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/SKILL.md/s007-4> ;
@@ -1120,21 +1156,21 @@
     djr:kind djr:kind-table-row ;
     djr:order 14 ;
     djr:statesNorm djr:R-3456 ;
     djr:text "| 구조를 모르는 임의 JSON 통과 | 직렬화·저장 경계 | 재귀 별칭 `JsonValue`(implementation-python §1.5 — arm 은 공변 `Sequence`/`Mapping`) | `dict[str, object]`·`Any` |\n" .
 
 <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/SKILL.md/s007-4/b15> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/SKILL.md/s007-4> ;
     djr:kind djr:kind-table-row ;
     djr:order 15 ;
     djr:statesNorm djr:R-3457 ;
-    djr:text "| 타입이 이미 있는 값 | 함수 반환·매개변수·속성 | 실제 클래스(`BuildPlan` 등) | **입구 밖**의 자리표시 `object`(입구 매개변수·즉시 검증 지역 변수는 위 R-3448 · 반환 주석의 `object` 는 ⓓ #647) |\n\n" .
+    djr:text "| 타입이 이미 있는 값 | 함수 반환·매개변수·속성(admin framework 슬롯은 앞 절 판정) | 실제 클래스(`BuildPlan` 등) | **입구 밖**의 자리표시 `object`(입구 매개변수·즉시 검증 지역 변수는 위 R-3448 · 반환 주석의 `object` 는 ⓓ #647) |\n\n" .
 
 <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/SKILL.md/s007-4/b16> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/SKILL.md/s007-4> ;
     djr:kind djr:kind-norm ;
     djr:order 16 ;
     djr:statesNorm djr:R-3458, djr:R-3459 ;
     djr:text "**django-stubs 가 제네릭으로 선언했지만 런타임은 subscript 못 하는 Django 기저는 모델 타입 인자를 적는다** — 타입 매개변수에 기본값이 없는 것들이다: `ModelForm`·`BaseInlineFormSet`·`ModelAdmin`·`InlineModelAdmin`(`TabularInline`/`StackedInline`)과 `ListView`·`DetailView`·`CreateView`·`UpdateView`·`DeleteView`·`FormView` 및 그 mixin, 그리고 `BaseFormSet`·`ModelChoiceField` 같은 폼셋·폼 필드 기저다(`View`·`TemplateView` 는 기본값이 있고 `RedirectView` 는 제네릭이 아니라 대상 밖 · 전수는 #646 집합 — django-stubs 6.1.0 기준). 맨몸 상속은 mypy strict `[type-arg]` 빚이고, `# type: ignore[type-arg]` 는 통과가 아니라 은폐라 붙이지 않는다 — 둘 다 #646 이 차단한다. 표기는 **`if TYPE_CHECKING:` 별칭이 기본**이다: `_ModelAdminBase: TypeAlias = admin.ModelAdmin[Parent]  # noqa: UP040` / `else: _ModelAdminBase: type[admin.ModelAdmin] = admin.ModelAdmin` — 기저에 직접 `X[Model]` 을 쓰면 import 시 `TypeError` 다(주석에만 쓰는 별칭은 `type` 문 — 지연 평가). 프로젝트가 `django_stubs_ext.monkeypatch()` 를 채택했으면(§6.1 의 관찰) 별칭 없이 `X[Model]` 직접 표기 — 채택은 레인이 도입하지 않는다. 스텁이 `ClassVar` 로 타입을 소유한 admin 선언 속성(`inlines` 등)은 재선언하지 않고(위 프레임워크 선언 면제), 프레임워크가 열어 둔 타입 매개변수는 bound(`Model`·`ModelForm[Model]`)로 적는다 — 예시는 implementation-django §18.\n\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/SKILL.md/s007-4/b2> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/SKILL.md/s007-4> ;
@@ -1169,28 +1205,28 @@
     djr:kind djr:kind-norm ;
     djr:order 6 ;
     djr:statesNorm djr:R-3155, djr:R-3156 ;
     djr:text "pydantic·ninja `Schema`·`dataclass` 필드는 `x: T` 가 있어야 동작한다 — bare 대입이면 규칙 위반이기 전에 버그다. 표준 문서군의 코드 예시는 개념 전달용 발췌라 적용 대상이 아니다 — 규칙은 생성하는 프로덕션·테스트 코드에 건다.\n\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/SKILL.md/s007-4/b7> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/SKILL.md/s007-4> ;
     djr:kind djr:kind-norm ;
     djr:order 7 ;
     djr:statesNorm djr:R-3447, djr:R-3448 ;
-    djr:text "**`Any` 는 타입이 아니라 검사 포기다 — 어디에도 쓰지 않는다.** 함수 시그니처(인자·`*args/**kwargs`·반환)·변수·클래스 속성·제네릭 인자(`dict[str, Any]`) 전부다 — 별표 인자 면제(ruff `allow-star-arg-any`) 관례와 다른 선택이다. 프레임워크 오버라이드가 스텁에서 `Any` 를 쓰더라도 우리 쪽 선언은 `object`(또는 정확 타입)로 쓴다 — mypy 는 이를 호환으로 본다. 시그니처의 `Any` 는 #645 가 차단하고, 변수·제네릭 안의 `Any` 는 ⓓ 후보(#645)로 표시된다 — 단 `dict`/`Mapping`/`MutableMapping` 의 **값 자리** `Any`(`dict[str, Any]` — 매개변수·반환·변수·속성 어디든)는 #647 이 차단하며 그 자리는 #645 후보로 남지 않는다. 후보는 감수자가 집행한다(§4.1 «시그니처만 강제하므로 나머지는 백스톱과 감수자» 와 같은 분담). 경계 입력(폼 `cleaned_data`·`request.user`·무스텁 서드파티·`json.loads` 결과)은 `object` 또는 프레임워크가 주는 정확한 타입으로 받아 **받는 즉시** 좁힌다(`TypeIs`·`isinstance`·`type() is` — implementation-python §1.12 · 좁히는 자리는 architecture-ddd §3.1 의 경계 규범대로 값 객체를 부르기 전). **JSON 문서는 `pydantic.TypeAdapter(그TypedDict).validate_python`/`validate_json` 으로 검증하며 받는다** — 대상은 파일·타 시스템·`json.loads` 결과이고 우리가 만든 JSON 도 파싱했으면 같다(strict `no-any-return`); HTTP body 는 ninja `Schema` 가 그 검증이다(implementation-python §12.0). 어떻게는 implementation-python §1.5, 무엇을 고르는지는 아래 결정표다. `object` 가 사는 자리는 좁히기·검증 도우미의 **매개변수**와 즉시 검증되는 **지역 변수**뿐이다(그 자리의 `dict/Mapping[…, object]` 는 #647 ⓓ 후보 — 감수자가 즉시 좁힘을 확인한다). **반환값·클래스 속성**에 `dict/Mapping[…, object]` 가 남으면 좁히지 않은 누수라 #647 이 차단한다. 면제는 둘 — 스텁이 강제하는 `forms.Form` 하위 `clean() -> dict[str, object]`(`ModelForm.clean` 은 `None` 이라 대상 아님)와 `TypeIs`/`TypeGuard[...]` 반환. `dict/Mapping` 값 자리가 아닌 반환 주석의 `object`(`-> object` 루트 · `tuple`/`list`/`Sequence` 원소)도 입구 밖 자리표시라 #647 ⓓ 후보다 — 예외는 스텁이 `object` 로 강제하는 프레임워크 콜백·오버라이드의 미러와 이벤트 컬렉션(`list[<Bc>Event]` 로 적을 수 있으면 그것이 답이다). `json.load(s)` 결과를 `TypeAdapter` 검증 없이 `object` 아닌 주석의 변수·`object` 아닌 반환·컴프리헨션·직접 첨자/속성 접근·리터럴 컨테이너 요소로 흘린 자리는 ⓓ #650 이다 — `x: object = json.loads(…)` 뒤 즉시 검증과 파서 직접 인자는 후보가 아니다.\n\n"@ko .
+    djr:text "**`Any` 는 타입이 아니라 검사 포기다 — 아래 확인된 framework 소유 admin 슬롯을 제외한 우리 선언에는 쓰지 않는다.** 함수 시그니처(인자·`*args/**kwargs`·반환)·변수·클래스 속성·제네릭 인자(`dict[str, Any]`) 전부다 — 별표 인자 면제(ruff `allow-star-arg-any`) 관례와 다른 선택이다. 확인된 admin 슬롯 밖에서 프레임워크 오버라이드가 스텁에서 `Any` 를 쓰더라도 우리 쪽 선언은 `object`(또는 정확 타입)로 쓴다 — mypy 는 이를 호환으로 본다. 시그니처의 `Any` 는 #645 가 차단하고, 변수·제네릭 안의 `Any` 는 ⓓ 후보(#645)로 표시된다 — 단 `dict`/`Mapping`/`MutableMapping` 의 **값 자리** `Any`(`dict[str, Any]` — 매개변수·반환·변수·속성 어디든)는 #647 이 차단하며 그 자리는 #645 후보로 남지 않는다. 후보는 감수자가 집행한다(§4.1 «시그니처만 강제하므로 나머지는 백스톱과 감수자» 와 같은 분담). 경계 입력(폼 `cleaned_data`·`request.user`·무스텁 서드파티·`json.loads` 결과)은 `object` 또는 프레임워크가 주는 정확한 타입으로 받아 **받는 즉시** 좁힌다(`TypeIs`·`isinstance`·`type() is` — implementation-python §1.12 · 좁히는 자리는 architecture-ddd §3.1 의 경계 규범대로 값 객체를 부르기 전). **JSON 문서는 `pydantic.TypeAdapter(그TypedDict).validate_python`/`validate_json` 으로 검증하며 받는다** — 대상은 파일·타 시스템·`json.loads` 결과이고 우리가 만든 JSON 도 파싱했으면 같다(strict `no-any-return`); HTTP body 는 ninja `Schema` 가 그 검증이다(implementation-python §12.0). 어떻게는 implementation-python §1.5, 무엇을 고르는지는 아래 결정표다. 아래 admin UI context 밖에서 `object` 가 사는 자리는 좁히기·검증 도우미의 **매개변수**와 즉시 검증되는 **지역 변수**뿐이다(그 자리의 `dict/Mapping[…, object]` 는 #647 ⓓ 후보 — 감수자가 즉시 좁힘을 확인한다). **반환값·클래스 속성**에 `dict/Mapping[…, object]` 가 남으면 좁히지 않은 누수라 #647 이 차단한다. 기존 면제는 둘 — 스텁이 강제하는 `forms.Form` 하위 `clean() -> dict[str, object]`(`ModelForm.clean` 은 `None` 이라 대상 아님)와 `TypeIs`/`TypeGuard[...]` 반환. `dict/Mapping` 값 자리가 아닌 반환 주석의 `object`(`-> object` 루트 · `tuple`/`list`/`Sequence` 원소)도 입구 밖 자리표시라 #647 ⓓ 후보다 — 예외는 스텁이 `object` 로 강제하는 프레임워크 콜백·오버라이드의 미러와 이벤트 컬렉션(`list[<Bc>Event]` 로 적을 수 있으면 그것이 답이다). `json.load(s)` 결과를 `TypeAdapter` 검증 없이 `object` 아닌 주석의 변수·`object` 아닌 반환·컴프리헨션·직접 첨자/속성 접근·리터럴 컨테이너 요소로 흘린 자리는 ⓓ #650 이다 — `x: object = json.loads(…)` 뒤 즉시 검증과 파서 직접 인자는 후보가 아니다.\n\n\n**admin context 판정**: #493 주석 존재 유지 · #645 framework 소유 슬롯 Any 제한 허용 · #646 제네릭 런타임 안전 유지 · #647 열린 UI context 조립/병합/전달 허용 · #650 실제 JSON 소비 검증 유지다. 출처가 확인된 Django admin 및 Parler admin 계열의 고정 framework 슬롯에만 적용한다. `extra_context`/`context`의 받기·each_context·UI dict·copy/update·고정 UI 키 쓰기·framework render 전달과 연결된 private 전달 helper의 매개변수·반환·지역 context 주석을 허용한다. form/inline/media의 별도 조립은 context의 허용을 취소하지 않는다. 컨테이너 부재 처리와 request UI metadata의 담기·전달도 허용한다. 업무 읽기·비교·계산·상태 변경 또는 ORM/use case/업무 함수로의 값 전달은 실제 소비이므로 그 자리부터 기존 규칙을 적용한다. 출처나 소비가 미해소 또는 동적/재귀 호출로 escape한 연결 context는 후보로 남겨 확인한다. 이름만 context인 값·같은 함수의 별도 업무 dict·framework 고정 kwargs 밖 bare Any·admin 클래스/경로 전체는 면제하지 않는다. 생성 private helper는 본문이 없으므로 정확히 결합된 열린 dict 슬롯의 #645/#647만 S1 미검증으로 보고하고 G2에서 실제 소비 흐름으로 다시 판단한다.\n\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/SKILL.md/s007-4/b8> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/SKILL.md/s007-4> ;
     djr:kind djr:kind-norm ;
     djr:order 8 ;
     djr:statesNorm djr:R-3451 ;
-    djr:text "**키가 정해진 값 묶음(레코드)은 딕셔너리로 들고 다니지 않는다** — 우리 코드가 리터럴로 만든 값은 `TypedDict`, 파싱한 JSON 은 `TypeAdapter(그TypedDict)` 검증 파싱, 도메인 개념은 값 객체(architecture-ddd §3.1). `dict/Mapping[str, object|Any]` 주석은 그 자체가 «구조를 안 정했다»는 신호다(#647). 레인이 바로 고르는 결정표:\n\n"@ko .
+    djr:text "**키가 정해진 값 묶음(레코드)은 딕셔너리로 들고 다니지 않는다** — framework 소유 admin UI context의 조립/전달은 앞 절 판정을 따르고, 우리 업무 코드가 리터럴로 만든 값은 `TypedDict`, 파싱한 JSON 은 `TypeAdapter(그TypedDict)` 검증 파싱, 도메인 개념은 값 객체(architecture-ddd §3.1). `dict/Mapping[str, object|Any]` 주석은 그 자체가 «구조를 안 정했다»는 신호다(#647). 레인이 바로 고르는 결정표:\n\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/SKILL.md/s007-4/b9> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/SKILL.md/s007-4> ;
     djr:kind djr:kind-table-row ;
     djr:order 9 ;
     djr:text "| 값의 모양 | 어디서 왔나 | 쓰는 도구 | 금지 |\n|---|---|---|---|\n" .
 
 <https://numchida.com/ns/djr#s/dddjango/skills/discipline-houserules/SKILL.md/s008-4.1> a djr:Section ;
     djr:headingSnapshot "### §4.1 왜 전부인가"@ko ;
     djr:inDocument <https://numchida.com/ns/djr#d/dddjango/skills/discipline-houserules/SKILL.md> ;

```

## ontology/rules/implementation-django-ninja-final.ttl

Before SHA256: e24b78dd3aab0a147d3458a3872d96c853f621395057a422860ac3ec5b0ddfce
After SHA256: b184ade4fccfa20554614d3460e2841ea800eb731ce54553d1f4adbf9d1339a9

```diff
--- before/ontology/rules/implementation-django-ninja-final.ttl
+++ after/ontology/rules/implementation-django-ninja-final.ttl
@@ -702,26 +702,32 @@
 
 djr:R-0083 a djr:Obligation ;
     skos:prefLabel "기본 경로 = framework 미식별 500"@ko ;
     djr:currentExpression <https://numchida.com/ns/djr#R-0083@2026-08-19> .
 
 <https://numchida.com/ns/djr#R-0083@2026-08-19> a djr:Expression ;
     prov:specializationOf djr:R-0083 ;
     djr:revision 1 .
 
 djr:R-0084 a djr:Exception ;
-    skos:prefLabel "G1 승인 시에만 infra/ACL 정규화 후 구체 exception 직접 흐름"@ko ;
-    djr:currentExpression <https://numchida.com/ns/djr#R-0084@2026-08-19> .
+    skos:prefLabel "인프라 내부 계약 정규화와 공개 오류 승인 분리"@ko ;
+    djr:currentExpression <https://numchida.com/ns/djr#R-0084@2026-09-11> .
 
 <https://numchida.com/ns/djr#R-0084@2026-08-19> a djr:Expression ;
     prov:specializationOf djr:R-0084 ;
     djr:revision 1 .
+
+<https://numchida.com/ns/djr#R-0084@2026-09-11> a djr:Expression ;
+    prov:specializationOf djr:R-0084 ;
+    prov:wasRevisionOf <https://numchida.com/ns/djr#R-0084@2026-08-19> ;
+    djr:revision 2 ;
+    djr:revisionKind djr:revision-amendment .
 
 djr:R-0085 a djr:Prohibition ;
     skos:prefLabel "인프라 예외 합성·타 BC exception 통과 금지"@ko ;
     djr:currentExpression <https://numchida.com/ns/djr#R-0085@2026-08-19> .
 
 <https://numchida.com/ns/djr#R-0085@2026-08-19> a djr:Expression ;
     prov:specializationOf djr:R-0085 ;
     djr:revision 1 .
 
 djr:R-0086 a djr:Obligation ;
@@ -3534,21 +3540,21 @@
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/skills/implementation-django-ninja/references/final.md/s023-6.2> ;
     djr:kind djr:kind-code ;
     djr:order 32 ;
     djr:text "```python\nfrom ninja.errors import AuthenticationError\nfrom ninja.security import HttpBearer\n\n\nclass BearerAuth(HttpBearer):\n    def authenticate(self, request, token):\n        principal = authenticate_token(token)\n        if principal is None:\n            return None\n        if principal.is_disabled:\n            raise AuthenticationError\n        return principal\n```\n\n" .
 
 <https://numchida.com/ns/djr#s/dddjango/skills/implementation-django-ninja/references/final.md/s023-6.2/b33> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/skills/implementation-django-ninja/references/final.md/s023-6.2> ;
     djr:kind djr:kind-norm ;
     djr:order 33 ;
     djr:statesNorm djr:R-0082, djr:R-0083, djr:R-0084, djr:R-0085 ;
-    djr:text "**인프라 오류 경계.** raw `OperationalError`, `IntegrityError`, SDK/network 오류를\ncontroller나 전역 recognizer가 문자열·SQLSTATE로 분류하지 않는다. 기본은 framework의\n미식별 500 경로다. 특정 실패가 안정된 공개 의미를 가진다고 G1에서 승인된 경우에만 infra/ACL이\n그 실패를 자기 BC의 구체 domain/application exception으로 정규화하고, controller가 그\n구체 exception을 위의 직접 흐름으로 처리한다. 인프라 예외를 합성하거나 다른 BC exception을\n그대로 통과시키지 않는다.\n\n"@ko .
+    djr:text "**인프라 오류 경계.** raw `OperationalError`, `IntegrityError`, SDK/network 오류를\ncontroller나 전역 recognizer가 문자열·SQLSTATE로 분류하지 않는다. 기본은 framework의\n미식별 500 경로다. 이미 잡은 IntegrityError의 승인된 알려진 제약 실패는 구체 계약 예외로, 나머지는 승인된 일반 저장소 실패 계약으로 번역한다. repository 실패 계약은 domain 소유, capability port 실패 계약은 해당 port 소유다. 이 내부 정규화는 공개 HTTP 오류 승인이 아니므로 일반 저장소 실패의 외부 응답은 기존 safe 500을 유지한다. 새 ErrorCode/ErrorSchema/4xx/503을 만들지 않는다. 잡지 않은 unknown 인프라 오류를 새로 catch-all하지 않는다. 안정된 public meaning이 별도로 승인된 경우에만 그 외부 계약에 맞는 controller mapping을 한다. 이미 선언된 계약 예외의 관찰 후 재던짐은 허용한다. 인프라 예외를 합성하거나 다른 BC exception을\n그대로 통과시키지 않는다.\n\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/skills/implementation-django-ninja/references/final.md/s023-6.2/b34> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/skills/implementation-django-ninja/references/final.md/s023-6.2> ;
     djr:kind djr:kind-norm ;
     djr:order 34 ;
     djr:statesNorm djr:R-0086, djr:R-0087, djr:R-0088, djr:R-0089, djr:R-0090 ;
     djr:text "**응답 선언과 OpenAPI.** controller가 직접 반환할 수 있는 각 BC 오류 status는 operation의\n`response={...}`에서 그 status에서 실제로 반환하는 오류 타입 집합과 정확히 같게 매핑한다 —\nconcrete 하나면 그 concrete, 둘 이상이면 `Union[...]`(`A | B`), 명시값으로 채운 base 인스턴스면\nbase. concrete class가 runtime instance를 고정하므로 OpenAPI도 그 concrete의 고정 code·message를\nendpoint별로 드러낸다 — base로 뭉뚱그려 선언하지 않는다(2026-08-25 개정). 직접 반환하지 않는\nframework status는 BC 오류로 선언하지 않는다. 오류 응답 선언을 `openapi_extra`로 보충하거나\n`get_openapi_schema` override, monkeypatch, postprocessor로 사후 변형하지 않는다 — 이 금지의\n대상은 **오류 응답(4xx·5xx) 항목**이다. `response=`로 직접 선언된 성공·리다이렉트\nstatus(100–399)의 **메타데이터 보충**(header 문서화 등)은 허용한다: 보충 status 집합이\n`response=` 선언 집합의 부분집합이고 키 전부가 **리터럴**(정수·숫자 문자열)일 때만이며,\n오류 status 동거·변수/상수 표현식 키·`**` splat 은 위반이다(fail-closed — 2026-09-01 개정).\n성공 항목의 content/schema 기입은 기계 판정 밖이다 — `response=` 선언과의 문서 정합은\n리뷰어 소관. 공개 OpenAPI\n후보가 중앙 입장 심사에서 `add/update`이면 mounted API의 생성 문서에서 status별로 선언한 오류 schema를 확인한다.\n\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/skills/implementation-django-ninja/references/final.md/s023-6.2/b35> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/skills/implementation-django-ninja/references/final.md/s023-6.2> ;

```

## ontology/rules/implementation-django-ninja-skill.ttl

Before SHA256: 369af739aae344af378c4c53a14ea5858464a0a6f5c4d7c284097e29f3fee947
After SHA256: 85fcd3471eeb56cecb0d99509941f44ed651c52bb2dda76ac549c7a057d6130a

```diff
--- before/ontology/rules/implementation-django-ninja-skill.ttl
+++ after/ontology/rules/implementation-django-ninja-skill.ttl
@@ -408,26 +408,32 @@
 
 djr:R-2940 a djr:Obligation ;
     skos:prefLabel "raw infra 실패의 기본 500"@ko ;
     djr:currentExpression <https://numchida.com/ns/djr#R-2940@2026-08-22> .
 
 <https://numchida.com/ns/djr#R-2940@2026-08-22> a djr:Expression ;
     prov:specializationOf djr:R-2940 ;
     djr:revision 1 .
 
 djr:R-2941 a djr:Exception ;
-    skos:prefLabel "승인된 안정 의미 한정 infra/ACL 의 자기 BC exception 정규화"@ko ;
-    djr:currentExpression <https://numchida.com/ns/djr#R-2941@2026-08-22> .
+    skos:prefLabel "인프라 내부 계약 번역과 공개 safe 500 유지"@ko ;
+    djr:currentExpression <https://numchida.com/ns/djr#R-2941@2026-09-11> .
 
 <https://numchida.com/ns/djr#R-2941@2026-08-22> a djr:Expression ;
     prov:specializationOf djr:R-2941 ;
     djr:revision 1 .
+
+<https://numchida.com/ns/djr#R-2941@2026-09-11> a djr:Expression ;
+    prov:specializationOf djr:R-2941 ;
+    prov:wasRevisionOf <https://numchida.com/ns/djr#R-2941@2026-08-22> ;
+    djr:revision 2 ;
+    djr:revisionKind djr:revision-amendment .
 
 djr:R-2942 a djr:Obligation ;
     skos:prefLabel "선언된 JSON 성공의 Schema/Status 반환"@ko ;
     djr:currentExpression <https://numchida.com/ns/djr#R-2942@2026-08-22> .
 
 <https://numchida.com/ns/djr#R-2942@2026-08-22> a djr:Expression ;
     prov:specializationOf djr:R-2942 ;
     djr:revision 1 .
 
 djr:R-2943 a djr:Permission ;
@@ -648,21 +654,21 @@
     djr:restates <https://numchida.com/ns/djr#s/dddjango/skills/implementation-django-ninja/references/final.md/s006-1.3/b1>, <https://numchida.com/ns/djr#s/dddjango/skills/implementation-django-ninja/references/final.md/s006-1.3/b3> ;
     djr:statesNorm djr:R-2901, djr:R-2902 ;
     djr:text "\n- Router는 HTTP 어댑터로 얇게: 요청 바인딩·auth hook·서비스 호출·응답 매핑만 (§1.3)\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/skills/implementation-django-ninja/SKILL.md/s004/b10> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/skills/implementation-django-ninja/SKILL.md/s004> ;
     djr:kind djr:kind-norm ;
     djr:order 10 ;
     djr:restates <https://numchida.com/ns/djr#s/dddjango/skills/implementation-django-ninja/references/final.md/s016-4.1/b6>, <https://numchida.com/ns/djr#s/dddjango/skills/implementation-django-ninja/references/final.md/s016-4.1/b7>, <https://numchida.com/ns/djr#s/dddjango/skills/implementation-django-ninja/references/final.md/s023-6.2/b31>, <https://numchida.com/ns/djr#s/dddjango/skills/implementation-django-ninja/references/final.md/s023-6.2/b33> ;
     djr:statesNorm djr:R-2938, djr:R-2939, djr:R-2940, djr:R-2941 ;
-    djr:text "- auth 실패는 `None` 또는 framework `AuthenticationError`이며 `request.auth`에 `ErrorSchema`를 넣지 않는다. raw infra 실패는 기본 500이고, 승인된 안정 의미만 infra/ACL이 자기 BC exception으로 정규화한다 (§4·§6.2)\n"@ko .
+    djr:text "- auth 실패는 `None` 또는 framework `AuthenticationError`이며 `request.auth`에 `ErrorSchema`를 넣지 않는다. 이미 잡은 IntegrityError의 승인된 알려진 제약 실패는 구체 계약 예외로, 나머지는 승인된 일반 저장소 실패 계약으로 번역한다. repository 실패 계약은 domain 소유, capability port 실패 계약은 해당 port 소유다. 이 내부 정규화는 공개 HTTP 오류 승인이 아니므로 일반 저장소 실패의 외부 응답은 기존 safe 500을 유지한다. 새 ErrorCode/ErrorSchema/4xx/503을 만들지 않는다. 잡지 않은 unknown 인프라 오류를 새로 catch-all하지 않는다. 안정된 public meaning이 별도로 승인된 경우에만 그 외부 계약에 맞는 controller mapping을 한다. 이미 선언된 계약 예외의 관찰 후 재던짐은 허용한다. (§4·§6.2)\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/skills/implementation-django-ninja/SKILL.md/s004/b11> a djr:Block ;
     djr:inSection <https://numchida.com/ns/djr#s/dddjango/skills/implementation-django-ninja/SKILL.md/s004> ;
     djr:kind djr:kind-norm ;
     djr:order 11 ;
     djr:restates <https://numchida.com/ns/djr#s/dddjango/skills/implementation-django-ninja/references/final.md/s009-2.2/b14>, <https://numchida.com/ns/djr#s/dddjango/skills/implementation-django-ninja/references/final.md/s023-6.2/b35> ;
     djr:statesNorm djr:R-2942, djr:R-2943 ;
     djr:text "- 선언된 JSON 성공은 Schema/`Status`로 반환한다. `FileResponse`·`StreamingHttpResponse`·redirect·schema-less 204는 성공 native carveout이며 오류 응답 우회를 허용하지 않는다 (§2.2·§6.2)\n"@ko .
 
 <https://numchida.com/ns/djr#s/dddjango/skills/implementation-django-ninja/SKILL.md/s004/b12> a djr:Block ;

```

## dddjango/skills/implementation-django-ninja/SKILL.md

Before SHA256: f31771a4af65e292446e896e504db2f032a05f0b56d902f11daabef9fdc4736c
After SHA256: ee52e8f2556c873d824797ca90ac270cf344f57b0a59b04e036b2791bf579e67

```diff
--- before/dddjango/skills/implementation-django-ninja/SKILL.md
+++ after/dddjango/skills/implementation-django-ninja/SKILL.md
@@ -22,21 +22,21 @@
 
 - Router는 HTTP 어댑터로 얇게: 요청 바인딩·auth hook·서비스 호출·응답 매핑만 (§1.3)
 - Request/Response schema는 명시적으로 분리, ModelSchema는 내부 구현 보호가 확실할 때만 (§3.1–§3.2)
 - 발행 이벤트 봉투의 discriminator는 1종째부터 domain StrEnum + `Literal[EventType.X]` 파생(birth-enum), 버전 태그는 리터럴 동결. union-enum 동기는 중앙 test admission 후보이며 승인된 공개 wire와 독자 failure가 `add/update`일 때만 검증한다 (§3.1)
 - Schema·framework 오류·OpenAPI·HTTP 검증은 중앙 test admission 후보다. `add/update` 뒤에만 mechanics recipe를 적용하고, 공개 HTTP는 실제 URLconf에 mount된 Django client로, 공개 OpenAPI는 그 mounted API가 생성한 문서로 검증한다. 별도 승인된 공개 Python consumer가 없으면 validator 위치·`ValidationError.loc`·Pydantic/Ninja 기본 직렬화·private/helper 직접 호출은 test 자격이 아니며 오류 helper/handler 내부 unit test는 만들지 않는다 (§3·§6.3·§8·§9)
 - dddjango는 공통 `FrameworkErrorSchema` property를 정하지 않는다. `reuse`는 관찰된 exact shape를 보존한다. `create`와 `approved-change`는 신규 G1 slot 6에서 field/type/required/default/nullability/모든 `Field` metadata/model config·legacy `Config`/validator/serializer/computed field/Pydantic hook inventory와 effective semantics/wire 직렬화/field 의미 전체를 일반 G1과 분리해 명시 승인받는다. 공통 오류 모듈은 `framework/ninja/framework_error_schema.py` 하나다(`framework/ninja/`는 공유 `<technology>` 폴더 — 이 계약 밖 `<module>.py`와 공존). 승인된 common Schema의 Pydantic validator/serializer/decorator/hook은 보존 대상이며 아래 HTTP 오류 변환·handler 금지 대상이 아니다 (§6.2)
 - 각 오류 BC는 `api/bc_error_schema.py` 하나에 `<Bc>ErrorCode(StrEnum)`·`<Bc>ErrorSchema`·no-arg concrete 오류를 둔다. BC/concrete는 공통 annotation/nullability·Field metadata를 보존하고(§6.2가 승인한 단일값 Literal·동일 default 병존 좁힘은 예외), 추가 필드·validator·child model_config·URI/instance·다중 오류 schema 파일은 만들지 않는다 (§6.2)
 - controller는 입력 준비 뒤 정확히 한 application call만 좁은 `try`에 두고 구체 known exception을 catch한다. concrete 오류를 준비해 `Status(<승인된 HTTP status 표현>, error)`로 직접 반환하고 성공 변환은 `try` 뒤에서 한다. `status` body property는 요구하지 않는다. 오류 tuple/raw Response·dict·helper/factory/ErrorSchema→HTTP response serializer/mapper·exception handler/handler 등록 decorator·generic response builder는 금지한다 (§2.2·§6.2)
 - 직접 반환하는 모든 BC 오류 status는 `response={...}`에 실제 반환하는 오류 타입 그대로 선언한다(concrete 하나=그 concrete·둘 이상=`Union`·명시값 base=base — base로 뭉뚱그리지 않는다). framework-owned 401/403/route 404/422/429/일반 `HttpError`/미식별 500은 BC 오류로 변환·광고하지 않으며 body를 정확한 code-profile 계약이라 주장하지 않는다. 오류 선언의 `openapi_extra` 보충과 OpenAPI override·monkeypatch·postprocessor도 금지한다 — 단 `response=`에 선언된 성공 status(100–399)의 리터럴 메타데이터 보충(⊆ 선언 집합)만 허용·그 밖 fail-closed(2026-09-01) (§6.2·§8)
 - 프로젝트 `api.py`가 `NinjaExtraAPI` 하나를 소유하고, 명시 registrar가 소유하는 controller는 `@api_controller(..., auto_import=False)`로 auto-import/global registry side effect를 끈다. BC는 side-effect-free `register_<bc>_api(api: NinjaExtraAPI)`를 노출하고(인자 타입 축자 — 본뜬 Protocol·별칭 금지) 프로젝트 `urls.py`가 registrar를 명시 호출·mount하며, BC `composition_root/`(`dependency_wiring.py`)는 use-case DI만 소유한다 (§2.3)
-- auth 실패는 `None` 또는 framework `AuthenticationError`이며 `request.auth`에 `ErrorSchema`를 넣지 않는다. raw infra 실패는 기본 500이고, 승인된 안정 의미만 infra/ACL이 자기 BC exception으로 정규화한다 (§4·§6.2)
+- auth 실패는 `None` 또는 framework `AuthenticationError`이며 `request.auth`에 `ErrorSchema`를 넣지 않는다. 이미 잡은 IntegrityError의 승인된 알려진 제약 실패는 구체 계약 예외로, 나머지는 승인된 일반 저장소 실패 계약으로 번역한다. repository 실패 계약은 domain 소유, capability port 실패 계약은 해당 port 소유다. 이 내부 정규화는 공개 HTTP 오류 승인이 아니므로 일반 저장소 실패의 외부 응답은 기존 safe 500을 유지한다. 새 ErrorCode/ErrorSchema/4xx/503을 만들지 않는다. 잡지 않은 unknown 인프라 오류를 새로 catch-all하지 않는다. 안정된 public meaning이 별도로 승인된 경우에만 그 외부 계약에 맞는 controller mapping을 한다. 이미 선언된 계약 예외의 관찰 후 재던짐은 허용한다. (§4·§6.2)
 - 선언된 JSON 성공은 Schema/`Status`로 반환한다. `FileResponse`·`StreamingHttpResponse`·redirect·schema-less 204는 성공 native carveout이며 오류 응답 우회를 허용하지 않는다 (§2.2·§6.2)
 - operation은 `summary`·`description`·`tags`로 문서화하고 반환 타입을 명시한다(`object` 금지) — 반환 주석의 `Status` 는 하나(`-> Status[Out | Err]`) · 성공 union 은 이름 붙은 `RootModel` 하나(`Schema` 병행·`response={200: A | B}` 금지) (§2.2·§3.1)
 - Idempotency-Key는 계약에 정의된 endpoint에만; 키 정책(scope·replay·conflict)은 `architecture-api`, 저장소·retention(테이블·unique constraint·fingerprint)은 `architecture-db`가 결정 (§7)
 - 공개 OpenAPI 변경 후보가 `add/update`이면 mounted API의 생성 문서를 확인한다 (§8)
 - 신규 API는 Django Ninja 목표, DRF는 legacy·migration 맥락에서만 보조 (§10)
 - 신규 도입 시 Django Ninja를 의존성 매니페스트에 버전 핀으로 추가(글로벌 임의 설치 금지) — 핀 표기는 프로젝트 기존 관례 (§2.1)
 - 라우팅 결정 전 계약·DB·도메인이 미결이면 각 소유 스킬 먼저 (§11)
 
 ## 상세 레퍼런스
 <!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

```

## codex-dddjango/skills/implementation-django-ninja/SKILL.md

Before SHA256: 9b24e3a408e860730da661f0b6811d5791c757980c1f229625b5cf132878b7e6
After SHA256: fbc91023e3326b394a69064435188eac0193004e14adac2eaa8b2cba891f3338

```diff
--- before/codex-dddjango/skills/implementation-django-ninja/SKILL.md
+++ after/codex-dddjango/skills/implementation-django-ninja/SKILL.md
@@ -18,21 +18,21 @@
 
 - Router는 HTTP 어댑터로 얇게: 요청 바인딩·auth hook·서비스 호출·응답 매핑만 (§1.3)
 - Request/Response schema는 명시적으로 분리, ModelSchema는 내부 구현 보호가 확실할 때만 (§3.1–§3.2)
 - 발행 이벤트 봉투의 discriminator는 1종째부터 domain StrEnum + `Literal[EventType.X]` 파생(birth-enum), 버전 태그는 리터럴 동결. union-enum 동기는 중앙 test admission 후보이며 승인된 공개 wire와 독자 failure가 `add/update`일 때만 검증한다 (§3.1)
 - Schema·framework 오류·OpenAPI·HTTP 검증은 중앙 test admission 후보다. `add/update` 뒤에만 mechanics recipe를 적용하고, 공개 HTTP는 실제 URLconf에 mount된 Django client로, 공개 OpenAPI는 그 mounted API가 생성한 문서로 검증한다. 별도 승인된 공개 Python consumer가 없으면 validator 위치·`ValidationError.loc`·Pydantic/Ninja 기본 직렬화·private/helper 직접 호출은 test 자격이 아니며 오류 helper/handler 내부 unit test는 만들지 않는다 (§3·§6.3·§8·§9)
 - dddjango는 공통 `FrameworkErrorSchema` property를 정하지 않는다. `reuse`는 관찰된 exact shape를 보존한다. `create`와 `approved-change`는 신규 G1 slot 6에서 field/type/required/default/nullability/모든 `Field` metadata/model config·legacy `Config`/validator/serializer/computed field/Pydantic hook inventory와 effective semantics/wire 직렬화/field 의미 전체를 일반 G1과 분리해 명시 승인받는다. 공통 오류 모듈은 `framework/ninja/framework_error_schema.py` 하나다(`framework/ninja/`는 공유 `<technology>` 폴더 — 이 계약 밖 `<module>.py`와 공존). 승인된 common Schema의 Pydantic validator/serializer/decorator/hook은 보존 대상이며 아래 HTTP 오류 변환·handler 금지 대상이 아니다 (§6.2)
 - 각 오류 BC는 `api/bc_error_schema.py` 하나에 `<Bc>ErrorCode(StrEnum)`·`<Bc>ErrorSchema`·no-arg concrete 오류를 둔다. BC/concrete는 공통 annotation/nullability·Field metadata를 보존하고(§6.2가 승인한 단일값 Literal·동일 default 병존 좁힘은 예외), 추가 필드·validator·child model_config·URI/instance·다중 오류 schema 파일은 만들지 않는다 (§6.2)
 - controller는 입력 준비 뒤 정확히 한 application call만 좁은 `try`에 두고 구체 known exception을 catch한다. concrete 오류를 준비해 `Status(<승인된 HTTP status 표현>, error)`로 직접 반환하고 성공 변환은 `try` 뒤에서 한다. `status` body property는 요구하지 않는다. 오류 tuple/raw Response·dict·helper/factory/ErrorSchema→HTTP response serializer/mapper·exception handler/handler 등록 decorator·generic response builder는 금지한다 (§2.2·§6.2)
 - 직접 반환하는 모든 BC 오류 status는 `response={...}`에 실제 반환하는 오류 타입 그대로 선언한다(concrete 하나=그 concrete·둘 이상=`Union`·명시값 base=base — base로 뭉뚱그리지 않는다). framework-owned 401/403/route 404/422/429/일반 `HttpError`/미식별 500은 BC 오류로 변환·광고하지 않으며 body를 정확한 code-profile 계약이라 주장하지 않는다. 오류 선언의 `openapi_extra` 보충과 OpenAPI override·monkeypatch·postprocessor도 금지한다 — 단 `response=`에 선언된 성공 status(100–399)의 리터럴 메타데이터 보충(⊆ 선언 집합)만 허용·그 밖 fail-closed(2026-09-01) (§6.2·§8)
 - 프로젝트 `api.py`가 `NinjaExtraAPI` 하나를 소유하고, 명시 registrar가 소유하는 controller는 `@api_controller(..., auto_import=False)`로 auto-import/global registry side effect를 끈다. BC는 side-effect-free `register_<bc>_api(api: NinjaExtraAPI)`를 노출하고(인자 타입 축자 — 본뜬 Protocol·별칭 금지) 프로젝트 `urls.py`가 registrar를 명시 호출·mount하며, BC `composition_root/`(`dependency_wiring.py`)는 use-case DI만 소유한다 (§2.3)
-- auth 실패는 `None` 또는 framework `AuthenticationError`이며 `request.auth`에 `ErrorSchema`를 넣지 않는다. raw infra 실패는 기본 500이고, 승인된 안정 의미만 infra/ACL이 자기 BC exception으로 정규화한다 (§4·§6.2)
+- auth 실패는 `None` 또는 framework `AuthenticationError`이며 `request.auth`에 `ErrorSchema`를 넣지 않는다. 이미 잡은 IntegrityError의 승인된 알려진 제약 실패는 구체 계약 예외로, 나머지는 승인된 일반 저장소 실패 계약으로 번역한다. repository 실패 계약은 domain 소유, capability port 실패 계약은 해당 port 소유다. 이 내부 정규화는 공개 HTTP 오류 승인이 아니므로 일반 저장소 실패의 외부 응답은 기존 safe 500을 유지한다. 새 ErrorCode/ErrorSchema/4xx/503을 만들지 않는다. 잡지 않은 unknown 인프라 오류를 새로 catch-all하지 않는다. 안정된 public meaning이 별도로 승인된 경우에만 그 외부 계약에 맞는 controller mapping을 한다. 이미 선언된 계약 예외의 관찰 후 재던짐은 허용한다. (§4·§6.2)
 - 선언된 JSON 성공은 Schema/`Status`로 반환한다. `FileResponse`·`StreamingHttpResponse`·redirect·schema-less 204는 성공 native carveout이며 오류 응답 우회를 허용하지 않는다 (§2.2·§6.2)
 - operation은 `summary`·`description`·`tags`로 문서화하고 반환 타입을 명시한다(`object` 금지) — 반환 주석의 `Status` 는 하나(`-> Status[Out | Err]`) · 성공 union 은 이름 붙은 `RootModel` 하나(`Schema` 병행·`response={200: A | B}` 금지) (§2.2·§3.1)
 - Idempotency-Key는 계약에 정의된 endpoint에만; 키 정책(scope·replay·conflict)은 `architecture-api`, 저장소·retention(테이블·unique constraint·fingerprint)은 `architecture-db`가 결정 (§7)
 - 공개 OpenAPI 변경 후보가 `add/update`이면 mounted API의 생성 문서를 확인한다 (§8)
 - 신규 API는 Django Ninja 목표, DRF는 legacy·migration 맥락에서만 보조 (§10)
 - 신규 도입 시 Django Ninja를 의존성 매니페스트에 버전 핀으로 추가(글로벌 임의 설치 금지) — 핀 표기는 프로젝트 기존 관례 (§2.1)
 - 라우팅 결정 전 계약·DB·도메인이 미결이면 각 소유 스킬 먼저 (§11)
 
 ## 상세 레퍼런스
 

```

## dddjango/skills/implementation-django-ninja/references/final.md

Before SHA256: c514e77509cd5be0051fcf2292e40f0f0436da802594787759b4433bb72a72c0
After SHA256: f6276de920006a6caf6c9eca74e23e81099e8a3a10ffb2fc829298eb339642f2

```diff
--- before/dddjango/skills/implementation-django-ninja/references/final.md
+++ after/dddjango/skills/implementation-django-ninja/references/final.md
@@ -822,23 +822,21 @@
         principal = authenticate_token(token)
         if principal is None:
             return None
         if principal.is_disabled:
             raise AuthenticationError
         return principal
 ```
 
 **인프라 오류 경계.** raw `OperationalError`, `IntegrityError`, SDK/network 오류를
 controller나 전역 recognizer가 문자열·SQLSTATE로 분류하지 않는다. 기본은 framework의
-미식별 500 경로다. 특정 실패가 안정된 공개 의미를 가진다고 G1에서 승인된 경우에만 infra/ACL이
-그 실패를 자기 BC의 구체 domain/application exception으로 정규화하고, controller가 그
-구체 exception을 위의 직접 흐름으로 처리한다. 인프라 예외를 합성하거나 다른 BC exception을
+미식별 500 경로다. 이미 잡은 IntegrityError의 승인된 알려진 제약 실패는 구체 계약 예외로, 나머지는 승인된 일반 저장소 실패 계약으로 번역한다. repository 실패 계약은 domain 소유, capability port 실패 계약은 해당 port 소유다. 이 내부 정규화는 공개 HTTP 오류 승인이 아니므로 일반 저장소 실패의 외부 응답은 기존 safe 500을 유지한다. 새 ErrorCode/ErrorSchema/4xx/503을 만들지 않는다. 잡지 않은 unknown 인프라 오류를 새로 catch-all하지 않는다. 안정된 public meaning이 별도로 승인된 경우에만 그 외부 계약에 맞는 controller mapping을 한다. 이미 선언된 계약 예외의 관찰 후 재던짐은 허용한다. 인프라 예외를 합성하거나 다른 BC exception을
 그대로 통과시키지 않는다.
 
 **응답 선언과 OpenAPI.** controller가 직접 반환할 수 있는 각 BC 오류 status는 operation의
 `response={...}`에서 그 status에서 실제로 반환하는 오류 타입 집합과 정확히 같게 매핑한다 —
 concrete 하나면 그 concrete, 둘 이상이면 `Union[...]`(`A | B`), 명시값으로 채운 base 인스턴스면
 base. concrete class가 runtime instance를 고정하므로 OpenAPI도 그 concrete의 고정 code·message를
 endpoint별로 드러낸다 — base로 뭉뚱그려 선언하지 않는다(2026-08-25 개정). 직접 반환하지 않는
 framework status는 BC 오류로 선언하지 않는다. 오류 응답 선언을 `openapi_extra`로 보충하거나
 `get_openapi_schema` override, monkeypatch, postprocessor로 사후 변형하지 않는다 — 이 금지의
 대상은 **오류 응답(4xx·5xx) 항목**이다. `response=`로 직접 선언된 성공·리다이렉트

```

## codex-dddjango/skills/implementation-django-ninja/references/final.md

Before SHA256: c514e77509cd5be0051fcf2292e40f0f0436da802594787759b4433bb72a72c0
After SHA256: f6276de920006a6caf6c9eca74e23e81099e8a3a10ffb2fc829298eb339642f2

```diff
--- before/codex-dddjango/skills/implementation-django-ninja/references/final.md
+++ after/codex-dddjango/skills/implementation-django-ninja/references/final.md
@@ -822,23 +822,21 @@
         principal = authenticate_token(token)
         if principal is None:
             return None
         if principal.is_disabled:
             raise AuthenticationError
         return principal
 ```
 
 **인프라 오류 경계.** raw `OperationalError`, `IntegrityError`, SDK/network 오류를
 controller나 전역 recognizer가 문자열·SQLSTATE로 분류하지 않는다. 기본은 framework의
-미식별 500 경로다. 특정 실패가 안정된 공개 의미를 가진다고 G1에서 승인된 경우에만 infra/ACL이
-그 실패를 자기 BC의 구체 domain/application exception으로 정규화하고, controller가 그
-구체 exception을 위의 직접 흐름으로 처리한다. 인프라 예외를 합성하거나 다른 BC exception을
+미식별 500 경로다. 이미 잡은 IntegrityError의 승인된 알려진 제약 실패는 구체 계약 예외로, 나머지는 승인된 일반 저장소 실패 계약으로 번역한다. repository 실패 계약은 domain 소유, capability port 실패 계약은 해당 port 소유다. 이 내부 정규화는 공개 HTTP 오류 승인이 아니므로 일반 저장소 실패의 외부 응답은 기존 safe 500을 유지한다. 새 ErrorCode/ErrorSchema/4xx/503을 만들지 않는다. 잡지 않은 unknown 인프라 오류를 새로 catch-all하지 않는다. 안정된 public meaning이 별도로 승인된 경우에만 그 외부 계약에 맞는 controller mapping을 한다. 이미 선언된 계약 예외의 관찰 후 재던짐은 허용한다. 인프라 예외를 합성하거나 다른 BC exception을
 그대로 통과시키지 않는다.
 
 **응답 선언과 OpenAPI.** controller가 직접 반환할 수 있는 각 BC 오류 status는 operation의
 `response={...}`에서 그 status에서 실제로 반환하는 오류 타입 집합과 정확히 같게 매핑한다 —
 concrete 하나면 그 concrete, 둘 이상이면 `Union[...]`(`A | B`), 명시값으로 채운 base 인스턴스면
 base. concrete class가 runtime instance를 고정하므로 OpenAPI도 그 concrete의 고정 code·message를
 endpoint별로 드러낸다 — base로 뭉뚱그려 선언하지 않는다(2026-08-25 개정). 직접 반환하지 않는
 framework status는 BC 오류로 선언하지 않는다. 오류 응답 선언을 `openapi_extra`로 보충하거나
 `get_openapi_schema` override, monkeypatch, postprocessor로 사후 변형하지 않는다 — 이 금지의
 대상은 **오류 응답(4xx·5xx) 항목**이다. `response=`로 직접 선언된 성공·리다이렉트

```

## dddjango/skills/discipline-houserules/SKILL.md

Before SHA256: d2d9038955f8d2c5b85a3b03377a23a92d505feb2d11fa9b28ba308cc2f4cc53
After SHA256: 1c1fc1f8d1e39e9ebe246b91c71d4051ca4c442a3026f65092c3e42fa8f8dfce

```diff
--- before/dddjango/skills/discipline-houserules/SKILL.md
+++ after/dddjango/skills/discipline-houserules/SKILL.md
@@ -32,21 +32,21 @@
 
 **백스톱 실행 계약** — 검사기의 TARGET 은 «저장소 루트»다(`application/` 의 부모). BC 폴더나 `application/` 컨테이너 자체를 주면 검사기가 사용 오류 exit 1 로 거절한다(라운드 1 실측: BC 폴더 호출이 «표준 미채택 clean» 조용 통과를 낳았다 — 그 사각은 닫혔다). **게이트 판정은 판정 차분이다**(라운드 1′ — brownfield 의 legacy red 가 «전체 green» 계약을 영구 불능으로 만들던 모순의 해소): 게이트 증거는 «Phase 2 진입 앵커 대비 **귀속(신규 위반) 0** + legacy 잔존 별도 보고»(`scripts/registry_gate.py`)다(`<산출물 폴더>/approved-merges.txt` 가 있으면 `--approved-merge-file` 동반 — 발주자 승인 머지 목록의 provenance 증명으로 분리된 **승인 유입은 exit 제외·별도 보고(기록 의무·즉석 수리 금지)**, **상호작용 위반(파일 무변·미증명)은 귀속 유지·별도 표기** · 2026-09-03) — legacy 잔존이 게이트를 차단하지는 않지만, **귀속 red 를 «확립 규약» 논리로 수용하는 것도 금지**다. 검사기를 골라 좁힌 TARGET·selector 로 얻은 green 은 게이트 증거가 아니다 — **귀속 목록을 경로 필터(sed/grep)로 나눈 서술도 게이트 증거가 아니다**(유입 분리는 provenance 채널뿐 · 2026-09-03). 승인 스코프의 산출물 목록에 없는 파일에서 귀속이 나면 1차 처방은 **그 변경의 철회**다 — 수리·재설계로 귀속을 0으로 만드는 것이 아니다(2026-08-13 라운드 2 — 귀속 138건을 «해소 목록»으로 읽은 재설계 소용돌이).
 
 **관찰이 결정 입력인 축은 닫힌 목록이다**(라운드 1 「트리 답습」·라운드 1′ 「배선 답습」의 봉인 — 2026-08-12): ① 오류 wire 계약(12-slot `preserve-established`) ② API 스택 «정체»(근거=소비자 의존) ③ 주석 언어(§5) ④ 도구·러너(§6.1) ⑤ 승인 test artifact 의 기존 위치(§1.2) ⑥ 지원 중 행동 계약. **여기 없는 축 — 파일트리·배선/등록·import 방향·테스트 규율·값 집합 선언·인증 경로·admin 구조·OpenAPI 문서 후가공 … — 에서 기존 실물의 관찰은 결정의 입력이 아니다.** 배선 «값»(#105~#112)은 Ninja 스택 조건부지만, ‹관찰 비입력› 원칙 자체는 무조건이다. 그리고 이 원칙은 **신규 산출물의 형태** 문장이다 — 승인 스코프 밖 기존 실물을 옮기거나 고칠 권한을 만들지 않는다(§1.1 판정 물음: 위반 판정은 빚 기록 권한일 뿐, 이동 권한은 G0 사용자 ⓐ 결정→슬라이스 0 한 경로). 그리고 닫힌 목록의 관찰 금지 대상은 **대상 저장소의 기존 실물**이다 — 이번 슬라이스 산출물의 자기 형상은 이 축의 주어가 아니며, «동명 폴더 승격» 캐스케이드(아래) 판정의 유일한 입력이다.
 
 **어댑터 고정 골격** — 세 종류의 BC 어댑터는 `references/final.md` §0·§1의 고정 역할 패키지로 작성한다. 내용이 없어도 골격을 먼저 실현하고 실제 내용 파일 경로를 명세에 적는다. 이 칸에는 아래 승격 캐스케이드를 적용하지 않는다.
 
 **동명 폴더 승격 캐스케이드** — 승격 허용 칸 파일이 커질 때의 분할 판정이다(값·형태는 `references/final.md` §0 이 소유한다 — #490 교체형). 분할은 **크기가 아니라 소관·응집으로** 가른다 — 행 수는 트리거가 아니라 감사 신호다(`discipline-cleancode` §15.1 의 수치 스멜도 신호다). (명세·G0·감사자는 파이프라인 용어다 — 파이프라인 밖에서는 사용자의 명시적 작업 지시가 명세·G0 ⓐ에 준하고, 검수를 맡은 주체가 감사자에 준한다.)
 
 1. **이동(①)** — 커진 부분이 다른 기존 칸의 소관이면 그 칸으로 옮긴다. 단 이동 후보 칸이 실제로 받을 수 있는지(의존 방향 역류 없음·역할 계약 부합)를 확인한 뒤에만, 그리고 목적지가 승인 산출물 목록 안일 때만 — 목록 밖이면 보고(설계 반송)다. ①은 승격 폴더의 부품에도 그대로 적용된다.
-2. **동명 폴더 승격(②)** — 어느 칸 소관도 아닌 «역할 밖 응집 단위»가 생겼으면 승격한다. 술어(둘 다 충족): (a) 칸의 역할 계약 밖 top-level 정의로서, 자기 상태·수명을 가진 클래스이거나 — 본업 정의가 직접 참조하지 않거나 단일 진입 이름으로만 참조하는 사적 정의들이 **서로만 참조하는 닫힌 성분**을 이루는 무상태 클러스터(예: 모델군+상수+함수 쌍 — 상수 모음만·타입 별칭 모음만·함수 하나는 클러스터가 아니다) (b) 클러스터 **개별 50행 이상**(물리 행·빈 줄 제외). 관례 동거는 예외다(Django Model+Manager+QuerySet(+그 불변 예외)·admin panel+inline). 주어가 승격 폴더 내부 부품이면 ②의 실현은 하위 폴더가 아니라 **형제 부품 파일 분할**이다. 승격을 **집행하기 전에**(발견을 집행하는 coder 는 집행 전 · 기존 파일 승격(G0 ⓐ→슬라이스 0)의 제안·실행자는 제안 전), 대상 모듈을 **모듈 객체·모듈 경로 문자열로 참조하는 곳** — 테스트 fixture 의 monkeypatch, `unittest.mock.patch("pkg.mod.attr")` 문자열형, settings 등 dotted-path 문자열 참조, 동적 import — 을 저장소 전수에서 조사해 발견 전건을 승격 슬라이스 스코프에 편입한다. 재수출 `__init__` 의 import 표면 불변은 **읽기 표면**만 보증하고 **패치 표면**은 보증하지 않는다(패치는 패키지 객체에 걸리고 본체 모듈 전역은 그대로 남는다). 스코프 밖 발견이면 집행 전 보고(설계 반송)다 — 감사자의 판정 재료는 현행 유지다.
+2. **동명 폴더 승격(②)** — 어느 칸 소관도 아닌 «역할 밖 응집 단위»가 생겼으면 승격한다. 술어: 칸의 역할 계약 밖 top-level 정의로서, 자기 상태·수명을 가진 클래스이거나 — 본업 정의가 직접 참조하지 않거나 단일 진입 이름으로만 참조하는 사적 정의들이 **서로만 참조하는 닫힌 성분**을 이루는 무상태 클러스터(예: 모델군+상수+함수 쌍 — 상수 모음만·타입 별칭 모음만·함수 하나는 클러스터가 아니다). 관례 동거는 예외다(Django Model+Manager+QuerySet(+그 불변 예외)·admin panel+inline). 주어가 승격 폴더 내부 부품이면 ②의 실현은 하위 폴더가 아니라 **형제 부품 파일 분할**이다. 승격을 **집행하기 전에**(발견을 집행하는 coder 는 집행 전 · 기존 파일 승격(G0 ⓐ→슬라이스 0)의 제안·실행자는 제안 전), 대상 모듈을 **모듈 객체·모듈 경로 문자열로 참조하는 곳** — 테스트 fixture 의 monkeypatch, `unittest.mock.patch("pkg.mod.attr")` 문자열형, settings 등 dotted-path 문자열 참조, 동적 import — 을 저장소 전수에서 조사해 발견 전건을 승격 슬라이스 스코프에 편입한다. 재수출 `__init__` 의 import 표면 불변은 **읽기 표면**만 보증하고 **패치 표면**은 보증하지 않는다(패치는 패키지 객체에 걸리고 본체 모듈 전역은 그대로 남는다). 스코프 밖 발견이면 집행 전 보고(설계 반송)다 — 감사자의 판정 재료는 현행 유지다.
 3. **유지(③)** — 둘 다 아니면 한 파일(부품이면 한 부품 파일)을 유지한다. 전부 역할 내인 초대형 파일도 ③이다 — 크기는 트리거가 아니다.
 **감사 주도 배정** — coder 는 이 캐스케이드를 스스로 발동하지 않는다(승격 허용 칸은 파일형으로 작성한다). 신호는 `check-layer-skeleton` 이 후보 채널(ⓓ)로 무조건 방출한다 — 주어는 행위 칸 실현(controller 2종·service·use_case·repo/bypass/uow 구현·aggregate·domain_service — wiring 제외)과 그 칸의 승격 폴더 내부 .py(`__init__.py` 제외)의 200행 초과이고, 페이로드가 행수·top-level 정의 요약을 동봉한다(AST 산출은 백스톱 소유 — 감사자는 응집·소관·독립 변경 이유만 판정한다). **판정 의무의 주어만** «이번 diff 가 만들었거나 키운(판정 앵커 대비 물리 행수 순증>0) 파일»로 한정하고 그 적용자는 감사자다 — rename·`git mv` 는 «만들었음»으로 발화하고, 전 빌드 ③ 판정 파일은 역할 밖 후보가 새로 생긴 diff 에서만 재판정한다(판별 주체=감사자·판정은 감사 리포트에 기록한다). ①/② 판정은 권고가 아니라 반송 대상 발견이고 — coder 가 판단 없이 집행하며 발견의 클러스터 열거가 부품 파일 신설 근거다 — 신호 밖 허용 칸(schema_in/out 등)의 ② 판정은 홀리스틱 감사에서 허용하되 발견문에 «신호 밖 판정»을 명기한다.
 **등가 조항** — «§1.1 판정 물음»의 낳는 근거 판정에서, 승격 허용 칸에 한해 명세·승인 산출물 목록의 `<칸>.py` 행은 그 칸의 두 실현(파일·동명 폴더 승격 — #490 교체형)을 모두 승인한 것이다. 승격이 만드는 본체·부품·`__init__.py` 의 낳는 근거는 그 행과 감사 발견이고, 명세는 언제나 `<칸>.py` 로 적는다(실현 형태는 구현 단계 캐스케이드 판정 소유). 기존 파일의 동명 폴더 승격은 기존 코드 이동이다 — G0 빚 결정(ⓐ)→슬라이스 0 경로뿐이며, 슬라이스 0 이 낳는 칸 실현은 신규 산출물이다.
 
 ## §2 충돌 중재
 <!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->
 
 코퍼스(`architecture-ddd` ↔ `implementation-django`)가 서로 다른 트리를 제시해도 **런타임에 택일하지 않는다** — `references/final.md` 가 단일 출처이고 코퍼스는 그 표준이 파생된 배경이다. 남는 변수는 «실현 형태» 하나뿐이고 그 택일은 §1 의 동명 폴더 승격 캐스케이드가 소유한다(값의 변수가 아니다 — 트리는 무조건 표준·§1.1). 테스트 타입 조직은 `implementation-test` §4.2 가 단독 소유한다.
 
 ## §3 구조 결정이 빠졌다는 신호
@@ -68,32 +68,35 @@
 **모든 이름은 «첫 대입»에 타입을 적는다 — 예외 0.** 함수·메서드 시그니처(인자·반환), 모듈 변수, 클래스 변수, **함수 지역 변수**, 테스트와 테스트 재료(`test/fake/`·`factories/`)까지 전부다. 「자명하니까 면제」를 두지 않는다 — 조건부 면제는 매 실행 흔들리는 암묵 판단으로 돌아온다.
 
 **빠지는 곳은 «문법이 없는 자리»뿐이다(면제가 아니라 불가능):**
 
 - `for x in xs:` · `with f() as x:` · `except E as e:` · 언패킹(`a, b = pair`) · 다중 대입(`a = b = 0`) · 증강 대입(`x += 1`)
 - 재대입(첫 바인딩에서 1회만 단다) · 인스턴스 속성 `self.x = ...`(타입은 클래스 본문에 `x: T`)
 - 프레임워크 선언: Django 모델 필드(`name = models.CharField(...)`)·폼 필드 · `class Meta` 옵션 · enum 멤버(`RED = 1`) — 달면 프레임워크 의미가 오작동한다 · admin 패널 클래스 본문의 Django 선언 속성(`model`·`inlines`·`list_display`·`readonly_fields` …) — 타입은 스텁의 `ClassVar` 가 소유하고 `inlines` 처럼 재선언이 불변성 red 가 되는 자리가 있어 적지 않는다(달 수 있는 자리라도 스텁 타입과 같아야 하고 그 타입에 `Any` 가 있으면(`inlines`) 달 수 없다 · 선언적 클래스 본문의 메서드는 면제가 아니다)
 
 pydantic·ninja `Schema`·`dataclass` 필드는 `x: T` 가 있어야 동작한다 — bare 대입이면 규칙 위반이기 전에 버그다. 표준 문서군의 코드 예시는 개념 전달용 발췌라 적용 대상이 아니다 — 규칙은 생성하는 프로덕션·테스트 코드에 건다.
 
-**`Any` 는 타입이 아니라 검사 포기다 — 어디에도 쓰지 않는다.** 함수 시그니처(인자·`*args/**kwargs`·반환)·변수·클래스 속성·제네릭 인자(`dict[str, Any]`) 전부다 — 별표 인자 면제(ruff `allow-star-arg-any`) 관례와 다른 선택이다. 프레임워크 오버라이드가 스텁에서 `Any` 를 쓰더라도 우리 쪽 선언은 `object`(또는 정확 타입)로 쓴다 — mypy 는 이를 호환으로 본다. 시그니처의 `Any` 는 #645 가 차단하고, 변수·제네릭 안의 `Any` 는 ⓓ 후보(#645)로 표시된다 — 단 `dict`/`Mapping`/`MutableMapping` 의 **값 자리** `Any`(`dict[str, Any]` — 매개변수·반환·변수·속성 어디든)는 #647 이 차단하며 그 자리는 #645 후보로 남지 않는다. 후보는 감수자가 집행한다(§4.1 «시그니처만 강제하므로 나머지는 백스톱과 감수자» 와 같은 분담). 경계 입력(폼 `cleaned_data`·`request.user`·무스텁 서드파티·`json.loads` 결과)은 `object` 또는 프레임워크가 주는 정확한 타입으로 받아 **받는 즉시** 좁힌다(`TypeIs`·`isinstance`·`type() is` — implementation-python §1.12 · 좁히는 자리는 architecture-ddd §3.1 의 경계 규범대로 값 객체를 부르기 전). **JSON 문서는 `pydantic.TypeAdapter(그TypedDict).validate_python`/`validate_json` 으로 검증하며 받는다** — 대상은 파일·타 시스템·`json.loads` 결과이고 우리가 만든 JSON 도 파싱했으면 같다(strict `no-any-return`); HTTP body 는 ninja `Schema` 가 그 검증이다(implementation-python §12.0). 어떻게는 implementation-python §1.5, 무엇을 고르는지는 아래 결정표다. `object` 가 사는 자리는 좁히기·검증 도우미의 **매개변수**와 즉시 검증되는 **지역 변수**뿐이다(그 자리의 `dict/Mapping[…, object]` 는 #647 ⓓ 후보 — 감수자가 즉시 좁힘을 확인한다). **반환값·클래스 속성**에 `dict/Mapping[…, object]` 가 남으면 좁히지 않은 누수라 #647 이 차단한다. 면제는 둘 — 스텁이 강제하는 `forms.Form` 하위 `clean() -> dict[str, object]`(`ModelForm.clean` 은 `None` 이라 대상 아님)와 `TypeIs`/`TypeGuard[...]` 반환. `dict/Mapping` 값 자리가 아닌 반환 주석의 `object`(`-> object` 루트 · `tuple`/`list`/`Sequence` 원소)도 입구 밖 자리표시라 #647 ⓓ 후보다 — 예외는 스텁이 `object` 로 강제하는 프레임워크 콜백·오버라이드의 미러와 이벤트 컬렉션(`list[<Bc>Event]` 로 적을 수 있으면 그것이 답이다). `json.load(s)` 결과를 `TypeAdapter` 검증 없이 `object` 아닌 주석의 변수·`object` 아닌 반환·컴프리헨션·직접 첨자/속성 접근·리터럴 컨테이너 요소로 흘린 자리는 ⓓ #650 이다 — `x: object = json.loads(…)` 뒤 즉시 검증과 파서 직접 인자는 후보가 아니다.
+**`Any` 는 타입이 아니라 검사 포기다 — 아래 확인된 framework 소유 admin 슬롯을 제외한 우리 선언에는 쓰지 않는다.** 함수 시그니처(인자·`*args/**kwargs`·반환)·변수·클래스 속성·제네릭 인자(`dict[str, Any]`) 전부다 — 별표 인자 면제(ruff `allow-star-arg-any`) 관례와 다른 선택이다. 확인된 admin 슬롯 밖에서 프레임워크 오버라이드가 스텁에서 `Any` 를 쓰더라도 우리 쪽 선언은 `object`(또는 정확 타입)로 쓴다 — mypy 는 이를 호환으로 본다. 시그니처의 `Any` 는 #645 가 차단하고, 변수·제네릭 안의 `Any` 는 ⓓ 후보(#645)로 표시된다 — 단 `dict`/`Mapping`/`MutableMapping` 의 **값 자리** `Any`(`dict[str, Any]` — 매개변수·반환·변수·속성 어디든)는 #647 이 차단하며 그 자리는 #645 후보로 남지 않는다. 후보는 감수자가 집행한다(§4.1 «시그니처만 강제하므로 나머지는 백스톱과 감수자» 와 같은 분담). 경계 입력(폼 `cleaned_data`·`request.user`·무스텁 서드파티·`json.loads` 결과)은 `object` 또는 프레임워크가 주는 정확한 타입으로 받아 **받는 즉시** 좁힌다(`TypeIs`·`isinstance`·`type() is` — implementation-python §1.12 · 좁히는 자리는 architecture-ddd §3.1 의 경계 규범대로 값 객체를 부르기 전). **JSON 문서는 `pydantic.TypeAdapter(그TypedDict).validate_python`/`validate_json` 으로 검증하며 받는다** — 대상은 파일·타 시스템·`json.loads` 결과이고 우리가 만든 JSON 도 파싱했으면 같다(strict `no-any-return`); HTTP body 는 ninja `Schema` 가 그 검증이다(implementation-python §12.0). 어떻게는 implementation-python §1.5, 무엇을 고르는지는 아래 결정표다. 아래 admin UI context 밖에서 `object` 가 사는 자리는 좁히기·검증 도우미의 **매개변수**와 즉시 검증되는 **지역 변수**뿐이다(그 자리의 `dict/Mapping[…, object]` 는 #647 ⓓ 후보 — 감수자가 즉시 좁힘을 확인한다). **반환값·클래스 속성**에 `dict/Mapping[…, object]` 가 남으면 좁히지 않은 누수라 #647 이 차단한다. 기존 면제는 둘 — 스텁이 강제하는 `forms.Form` 하위 `clean() -> dict[str, object]`(`ModelForm.clean` 은 `None` 이라 대상 아님)와 `TypeIs`/`TypeGuard[...]` 반환. `dict/Mapping` 값 자리가 아닌 반환 주석의 `object`(`-> object` 루트 · `tuple`/`list`/`Sequence` 원소)도 입구 밖 자리표시라 #647 ⓓ 후보다 — 예외는 스텁이 `object` 로 강제하는 프레임워크 콜백·오버라이드의 미러와 이벤트 컬렉션(`list[<Bc>Event]` 로 적을 수 있으면 그것이 답이다). `json.load(s)` 결과를 `TypeAdapter` 검증 없이 `object` 아닌 주석의 변수·`object` 아닌 반환·컴프리헨션·직접 첨자/속성 접근·리터럴 컨테이너 요소로 흘린 자리는 ⓓ #650 이다 — `x: object = json.loads(…)` 뒤 즉시 검증과 파서 직접 인자는 후보가 아니다.
 
-**키가 정해진 값 묶음(레코드)은 딕셔너리로 들고 다니지 않는다** — 우리 코드가 리터럴로 만든 값은 `TypedDict`, 파싱한 JSON 은 `TypeAdapter(그TypedDict)` 검증 파싱, 도메인 개념은 값 객체(architecture-ddd §3.1). `dict/Mapping[str, object|Any]` 주석은 그 자체가 «구조를 안 정했다»는 신호다(#647). 레인이 바로 고르는 결정표:
+
+**admin context 판정**: #493 주석 존재 유지 · #645 framework 소유 슬롯 Any 제한 허용 · #646 제네릭 런타임 안전 유지 · #647 열린 UI context 조립/병합/전달 허용 · #650 실제 JSON 소비 검증 유지다. 출처가 확인된 Django admin 및 Parler admin 계열의 고정 framework 슬롯에만 적용한다. `extra_context`/`context`의 받기·each_context·UI dict·copy/update·고정 UI 키 쓰기·framework render 전달과 연결된 private 전달 helper의 매개변수·반환·지역 context 주석을 허용한다. form/inline/media의 별도 조립은 context의 허용을 취소하지 않는다. 컨테이너 부재 처리와 request UI metadata의 담기·전달도 허용한다. 업무 읽기·비교·계산·상태 변경 또는 ORM/use case/업무 함수로의 값 전달은 실제 소비이므로 그 자리부터 기존 규칙을 적용한다. 출처나 소비가 미해소 또는 동적/재귀 호출로 escape한 연결 context는 후보로 남겨 확인한다. 이름만 context인 값·같은 함수의 별도 업무 dict·framework 고정 kwargs 밖 bare Any·admin 클래스/경로 전체는 면제하지 않는다. 생성 private helper는 본문이 없으므로 정확히 결합된 열린 dict 슬롯의 #645/#647만 S1 미검증으로 보고하고 G2에서 실제 소비 흐름으로 다시 판단한다.
+
+**키가 정해진 값 묶음(레코드)은 딕셔너리로 들고 다니지 않는다** — framework 소유 admin UI context의 조립/전달은 앞 절 판정을 따르고, 우리 업무 코드가 리터럴로 만든 값은 `TypedDict`, 파싱한 JSON 은 `TypeAdapter(그TypedDict)` 검증 파싱, 도메인 개념은 값 객체(architecture-ddd §3.1). `dict/Mapping[str, object|Any]` 주석은 그 자체가 «구조를 안 정했다»는 신호다(#647). 레인이 바로 고르는 결정표:
 
 | 값의 모양 | 어디서 왔나 | 쓰는 도구 | 금지 |
 |---|---|---|---|
-| 키가 정해진 값 묶음(레코드) | 우리 코드가 리터럴로 만든 내부 데이터 | `TypedDict`(종류가 여럿이면 `kind: Literal[…]` 판별 키로 union) | `dict/Mapping[str, object\|Any]` |
+| 키가 정해진 값 묶음(레코드) | 우리 업무 코드가 리터럴로 만든 내부 데이터(admin UI 조립/전달은 앞 절 판정) | `TypedDict`(종류가 여럿이면 `kind: Literal[…]` 판별 키로 union) | `dict/Mapping[str, object\|Any]` |
 | 키가 정해진 값 묶음 | 파싱한 JSON(파일 `json.load`·타 시스템·`json.loads` — 우리가 쓴 파일도 같다) | `TypeAdapter(그TypedDict).validate_python/validate_json` 로 검증 파싱(HTTP body 는 ninja `Schema` 가 이미 검증) · 파싱 전 값 사용 금지 | 검증 없는 `-> TypedDict` 반환(strict `no-any-return`) · `Any`/`object` 로 흘리기(ⓓ #650) |
 | 도메인 개념 | 도메인 계층 | dataclass·값 객체(architecture-ddd §3.1) | 딕셔너리 |
 | 키가 데이터인 모음(조회표) | 어디든 | `dict[K, V]` 에 K·V 구체 타입(V 가 레코드면 `TypedDict`) | 값 타입 `object`·`Any` |
 | 구조를 모르는 임의 JSON 통과 | 직렬화·저장 경계 | 재귀 별칭 `JsonValue`(implementation-python §1.5 — arm 은 공변 `Sequence`/`Mapping`) | `dict[str, object]`·`Any` |
-| 타입이 이미 있는 값 | 함수 반환·매개변수·속성 | 실제 클래스(`BuildPlan` 등) | **입구 밖**의 자리표시 `object`(입구 매개변수·즉시 검증 지역 변수는 위 R-3448 · 반환 주석의 `object` 는 ⓓ #647) |
+| 타입이 이미 있는 값 | 함수 반환·매개변수·속성(admin framework 슬롯은 앞 절 판정) | 실제 클래스(`BuildPlan` 등) | **입구 밖**의 자리표시 `object`(입구 매개변수·즉시 검증 지역 변수는 위 R-3448 · 반환 주석의 `object` 는 ⓓ #647) |
 
 **django-stubs 가 제네릭으로 선언했지만 런타임은 subscript 못 하는 Django 기저는 모델 타입 인자를 적는다** — 타입 매개변수에 기본값이 없는 것들이다: `ModelForm`·`BaseInlineFormSet`·`ModelAdmin`·`InlineModelAdmin`(`TabularInline`/`StackedInline`)과 `ListView`·`DetailView`·`CreateView`·`UpdateView`·`DeleteView`·`FormView` 및 그 mixin, 그리고 `BaseFormSet`·`ModelChoiceField` 같은 폼셋·폼 필드 기저다(`View`·`TemplateView` 는 기본값이 있고 `RedirectView` 는 제네릭이 아니라 대상 밖 · 전수는 #646 집합 — django-stubs 6.1.0 기준). 맨몸 상속은 mypy strict `[type-arg]` 빚이고, `# type: ignore[type-arg]` 는 통과가 아니라 은폐라 붙이지 않는다 — 둘 다 #646 이 차단한다. 표기는 **`if TYPE_CHECKING:` 별칭이 기본**이다: `_ModelAdminBase: TypeAlias = admin.ModelAdmin[Parent]  # noqa: UP040` / `else: _ModelAdminBase: type[admin.ModelAdmin] = admin.ModelAdmin` — 기저에 직접 `X[Model]` 을 쓰면 import 시 `TypeError` 다(주석에만 쓰는 별칭은 `type` 문 — 지연 평가). 프로젝트가 `django_stubs_ext.monkeypatch()` 를 채택했으면(§6.1 의 관찰) 별칭 없이 `X[Model]` 직접 표기 — 채택은 레인이 도입하지 않는다. 스텁이 `ClassVar` 로 타입을 소유한 admin 선언 속성(`inlines` 등)은 재선언하지 않고(위 프레임워크 선언 면제), 프레임워크가 열어 둔 타입 매개변수는 bound(`Model`·`ModelForm[Model]`)로 적는다 — 예시는 implementation-django §18.
 
 ### §4.1 왜 전부인가
 <!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->
 
 타입 추론은 기계에게는 공짜지만 **읽는 사람에게는 노동이다** — 호출 결과의 타입을 알려면 독자가 시그니처를 따라가 «추론을 재연»해야 한다. 이 플러그인은 그 노동을 코드 작성 시점에 한 번 지불하는 쪽을 택한다. 부수 효과로 판정이 결정적이 된다 — 「자명한가」를 묻지 않으므로 검사가 런마다 흔들리지 않는다. 주류(PEP 8·mypy 기본 관례)의 「추론 가능한 지역 변수엔 비권장」과 다른 선택임을 숨기지 않는다. mypy strict 는 시그니처만 강제하므로 나머지는 백스톱과 감수자가 집행한다.
 
 ## §5 코드 주석·docstring 언어
 <!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

```

## codex-dddjango/skills/dddjango-discipline-houserules/SKILL.md

Before SHA256: 45a4ef441709e4dfa5ad3d364594b26f8bc5d2af8e8b9adac4febdf97dfd8ccc
After SHA256: f0f81d47b30246c6eadf8eeb991017c286f2bf585b7b2293bf525842a18f4e0c

```diff
--- before/codex-dddjango/skills/dddjango-discipline-houserules/SKILL.md
+++ after/codex-dddjango/skills/dddjango-discipline-houserules/SKILL.md
@@ -28,21 +28,21 @@
 
 **백스톱 실행 계약** — 검사기의 TARGET 은 «저장소 루트»다(`application/` 의 부모). BC 폴더나 `application/` 컨테이너 자체를 주면 검사기가 사용 오류 exit 1 로 거절한다(라운드 1 실측: BC 폴더 호출이 «표준 미채택 clean» 조용 통과를 낳았다 — 그 사각은 닫혔다). **게이트 판정은 판정 차분이다**(라운드 1′ — brownfield 의 legacy red 가 «전체 green» 계약을 영구 불능으로 만들던 모순의 해소): 게이트 증거는 «Phase 2 진입 앵커 대비 **귀속(신규 위반) 0** + legacy 잔존 별도 보고»(`scripts/registry_gate.py`)다(`<산출물 폴더>/approved-merges.txt` 가 있으면 `--approved-merge-file` 동반 — 발주자 승인 머지 목록의 provenance 증명으로 분리된 **승인 유입은 exit 제외·별도 보고(기록 의무·즉석 수리 금지)**, **상호작용 위반(파일 무변·미증명)은 귀속 유지·별도 표기** · 2026-09-03) — legacy 잔존이 게이트를 차단하지는 않지만, **귀속 red 를 «확립 규약» 논리로 수용하는 것도 금지**다. 검사기를 골라 좁힌 TARGET·selector 로 얻은 green 은 게이트 증거가 아니다 — **귀속 목록을 경로 필터(sed/grep)로 나눈 서술도 게이트 증거가 아니다**(유입 분리는 provenance 채널뿐 · 2026-09-03). 승인 스코프의 산출물 목록에 없는 파일에서 귀속이 나면 1차 처방은 **그 변경의 철회**다 — 수리·재설계로 귀속을 0으로 만드는 것이 아니다(2026-08-13 라운드 2 — 귀속 138건을 «해소 목록»으로 읽은 재설계 소용돌이).
 
 **관찰이 결정 입력인 축은 닫힌 목록이다**(라운드 1 「트리 답습」·라운드 1′ 「배선 답습」의 봉인 — 2026-08-12): ① 오류 wire 계약(12-slot `preserve-established`) ② API 스택 «정체»(근거=소비자 의존) ③ 주석 언어(§5) ④ 도구·러너(§6.1) ⑤ 승인 test artifact 의 기존 위치(§1.2) ⑥ 지원 중 행동 계약. **여기 없는 축 — 파일트리·배선/등록·import 방향·테스트 규율·값 집합 선언·인증 경로·admin 구조·OpenAPI 문서 후가공 … — 에서 기존 실물의 관찰은 결정의 입력이 아니다.** 배선 «값»(#105~#112)은 Ninja 스택 조건부지만, ‹관찰 비입력› 원칙 자체는 무조건이다. 그리고 이 원칙은 **신규 산출물의 형태** 문장이다 — 승인 스코프 밖 기존 실물을 옮기거나 고칠 권한을 만들지 않는다(§1.1 판정 물음: 위반 판정은 빚 기록 권한일 뿐, 이동 권한은 G0 사용자 ⓐ 결정→슬라이스 0 한 경로). 그리고 닫힌 목록의 관찰 금지 대상은 **대상 저장소의 기존 실물**이다 — 이번 슬라이스 산출물의 자기 형상은 이 축의 주어가 아니며, «동명 폴더 승격» 캐스케이드(위) 판정의 유일한 입력이다.
 
 **어댑터 고정 골격** — 세 종류의 BC 어댑터는 `references/final.md` §0·§1의 고정 역할 패키지로 작성한다. 내용이 없어도 골격을 먼저 실현하고 실제 내용 파일 경로를 명세에 적는다. 이 칸에는 아래 승격 캐스케이드를 적용하지 않는다.
 
 **동명 폴더 승격 캐스케이드** — 승격 허용 칸 파일이 커질 때의 분할 판정이다(값·형태는 `references/final.md` §0 이 소유한다 — #490 교체형). 분할은 **크기가 아니라 소관·응집으로** 가른다 — 행 수는 트리거가 아니라 감사 신호다(`dddjango-discipline-cleancode` §15.1 의 수치 스멜도 신호다). (명세·G0·감사자는 파이프라인 용어다 — 파이프라인 밖에서는 사용자의 명시적 작업 지시가 명세·G0 ⓐ에 준하고, 검수를 맡은 주체가 감사자에 준한다.)
 
 1. **이동(①)** — 커진 부분이 다른 기존 칸의 소관이면 그 칸으로 옮긴다. 단 이동 후보 칸이 실제로 받을 수 있는지(의존 방향 역류 없음·역할 계약 부합)를 확인한 뒤에만, 그리고 목적지가 승인 산출물 목록 안일 때만 — 목록 밖이면 보고(설계 반송)다. ①은 승격 폴더의 부품에도 그대로 적용된다.
-2. **동명 폴더 승격(②)** — 어느 칸 소관도 아닌 «역할 밖 응집 단위»가 생겼으면 승격한다. 술어(둘 다 충족): (a) 칸의 역할 계약 밖 top-level 정의로서, 자기 상태·수명을 가진 클래스이거나 — 본업 정의가 직접 참조하지 않거나 단일 진입 이름으로만 참조하는 사적 정의들이 **서로만 참조하는 닫힌 성분**을 이루는 무상태 클러스터(예: 모델군+상수+함수 쌍 — 상수 모음만·타입 별칭 모음만·함수 하나는 클러스터가 아니다) (b) 클러스터 **개별 50행 이상**(물리 행·빈 줄 제외). 관례 동거는 예외다(Django Model+Manager+QuerySet(+그 불변 예외)·admin panel+inline). 주어가 승격 폴더 내부 부품이면 ②의 실현은 하위 폴더가 아니라 **형제 부품 파일 분할**이다. 승격을 **집행하기 전에**(발견을 집행하는 coder 는 집행 전 · 기존 파일 승격(G0 ⓐ→슬라이스 0)의 제안·실행자는 제안 전), 대상 모듈을 **모듈 객체·모듈 경로 문자열로 참조하는 곳** — 테스트 fixture 의 monkeypatch, `unittest.mock.patch("pkg.mod.attr")` 문자열형, settings 등 dotted-path 문자열 참조, 동적 import — 을 저장소 전수에서 조사해 발견 전건을 승격 슬라이스 스코프에 편입한다. 재수출 `__init__` 의 import 표면 불변은 **읽기 표면**만 보증하고 **패치 표면**은 보증하지 않는다(패치는 패키지 객체에 걸리고 본체 모듈 전역은 그대로 남는다). 스코프 밖 발견이면 집행 전 보고(설계 반송)다 — 감사자의 판정 재료는 현행 유지다.
+2. **동명 폴더 승격(②)** — 어느 칸 소관도 아닌 «역할 밖 응집 단위»가 생겼으면 승격한다. 술어: 칸의 역할 계약 밖 top-level 정의로서, 자기 상태·수명을 가진 클래스이거나 — 본업 정의가 직접 참조하지 않거나 단일 진입 이름으로만 참조하는 사적 정의들이 **서로만 참조하는 닫힌 성분**을 이루는 무상태 클러스터(예: 모델군+상수+함수 쌍 — 상수 모음만·타입 별칭 모음만·함수 하나는 클러스터가 아니다). 관례 동거는 예외다(Django Model+Manager+QuerySet(+그 불변 예외)·admin panel+inline). 주어가 승격 폴더 내부 부품이면 ②의 실현은 하위 폴더가 아니라 **형제 부품 파일 분할**이다. 승격을 **집행하기 전에**(발견을 집행하는 coder 는 집행 전 · 기존 파일 승격(G0 ⓐ→슬라이스 0)의 제안·실행자는 제안 전), 대상 모듈을 **모듈 객체·모듈 경로 문자열로 참조하는 곳** — 테스트 fixture 의 monkeypatch, `unittest.mock.patch("pkg.mod.attr")` 문자열형, settings 등 dotted-path 문자열 참조, 동적 import — 을 저장소 전수에서 조사해 발견 전건을 승격 슬라이스 스코프에 편입한다. 재수출 `__init__` 의 import 표면 불변은 **읽기 표면**만 보증하고 **패치 표면**은 보증하지 않는다(패치는 패키지 객체에 걸리고 본체 모듈 전역은 그대로 남는다). 스코프 밖 발견이면 집행 전 보고(설계 반송)다 — 감사자의 판정 재료는 현행 유지다.
 3. **유지(③)** — 둘 다 아니면 한 파일(부품이면 한 부품 파일)을 유지한다. 전부 역할 내인 초대형 파일도 ③이다 — 크기는 트리거가 아니다.
 **감사 주도 배정** — coder 는 이 캐스케이드를 스스로 발동하지 않는다(승격 허용 칸은 파일형으로 작성한다). 신호는 `check-layer-skeleton` 이 후보 채널(ⓓ)로 무조건 방출한다 — 주어는 행위 칸 실현(controller 2종·service·use_case·repo/bypass/uow 구현·aggregate·domain_service — wiring 제외)과 그 칸의 승격 폴더 내부 .py(`__init__.py` 제외)의 200행 초과이고, 페이로드가 행수·top-level 정의 요약을 동봉한다(AST 산출은 백스톱 소유 — 감사자는 응집·소관·독립 변경 이유만 판정한다). **판정 의무의 주어만** «이번 diff 가 만들었거나 키운(판정 앵커 대비 물리 행수 순증>0) 파일»로 한정하고 그 적용자는 감사자다 — rename·`git mv` 는 «만들었음»으로 발화하고, 전 빌드 ③ 판정 파일은 역할 밖 후보가 새로 생긴 diff 에서만 재판정한다(판별 주체=감사자·판정은 감사 리포트에 기록한다). ①/② 판정은 권고가 아니라 반송 대상 발견이고 — coder 가 판단 없이 집행하며 발견의 클러스터 열거가 부품 파일 신설 근거다 — 신호 밖 허용 칸(schema_in/out 등)의 ② 판정은 홀리스틱 감사에서 허용하되 발견문에 «신호 밖 판정»을 명기한다.
 **등가 조항** — «§1.1 판정 물음»의 낳는 근거 판정에서, 승격 허용 칸에 한해 명세·승인 산출물 목록의 `<칸>.py` 행은 그 칸의 두 실현(파일·동명 폴더 승격 — #490 교체형)을 모두 승인한 것이다. 승격이 만드는 본체·부품·`__init__.py` 의 낳는 근거는 그 행과 감사 발견이고, 명세는 언제나 `<칸>.py` 로 적는다(실현 형태는 구현 단계 캐스케이드 판정 소유). 기존 파일의 동명 폴더 승격은 기존 코드 이동이다 — G0 빚 결정(ⓐ)→슬라이스 0 경로뿐이며, 슬라이스 0 이 낳는 칸 실현은 신규 산출물이다.
 
 ## §2 충돌 중재
 
 코퍼스(`dddjango-architecture-ddd` ↔ `implementation-django`)가 서로 다른 트리를 제시해도 **런타임에 택일하지 않는다** — `references/final.md` 가 단일 출처이고 코퍼스는 그 표준이 파생된 배경이다. 남는 변수는 «실현 형태» 하나뿐이고 그 택일은 §1 의 동명 폴더 승격 캐스케이드가 소유한다(값의 변수가 아니다 — 트리는 무조건 표준·§1.1). 테스트 타입 조직은 `dddjango-implementation-test` §4.2 가 단독 소유한다.
 
 ## §3 구조 결정이 빠졌다는 신호
 
@@ -61,32 +61,35 @@
 **모든 이름은 «첫 대입»에 타입을 적는다 — 예외 0.** 함수·메서드 시그니처(인자·반환), 모듈 변수, 클래스 변수, **함수 지역 변수**, 테스트와 테스트 재료(`test/fake/`·`factories/`)까지 전부다. 「자명하니까 면제」를 두지 않는다 — 조건부 면제는 매 실행 흔들리는 암묵 판단으로 돌아온다.
 
 **빠지는 곳은 «문법이 없는 자리»뿐이다(면제가 아니라 불가능):**
 
 - `for x in xs:` · `with f() as x:` · `except E as e:` · 언패킹(`a, b = pair`) · 다중 대입(`a = b = 0`) · 증강 대입(`x += 1`)
 - 재대입(첫 바인딩에서 1회만 단다) · 인스턴스 속성 `self.x = ...`(타입은 클래스 본문에 `x: T`)
 - 프레임워크 선언: Django 모델 필드(`name = models.CharField(...)`)·폼 필드 · `class Meta` 옵션 · enum 멤버(`RED = 1`) — 달면 프레임워크 의미가 오작동한다 · admin 패널 클래스 본문의 Django 선언 속성(`model`·`inlines`·`list_display`·`readonly_fields` …) — 타입은 스텁의 `ClassVar` 가 소유하고 `inlines` 처럼 재선언이 불변성 red 가 되는 자리가 있어 적지 않는다(달 수 있는 자리라도 스텁 타입과 같아야 하고 그 타입에 `Any` 가 있으면(`inlines`) 달 수 없다 · 선언적 클래스 본문의 메서드는 면제가 아니다)
 
 pydantic·ninja `Schema`·`dataclass` 필드는 `x: T` 가 있어야 동작한다 — bare 대입이면 규칙 위반이기 전에 버그다. 표준 문서군의 코드 예시는 개념 전달용 발췌라 적용 대상이 아니다 — 규칙은 생성하는 프로덕션·테스트 코드에 건다.
 
-**`Any` 는 타입이 아니라 검사 포기다 — 어디에도 쓰지 않는다.** 함수 시그니처(인자·`*args/**kwargs`·반환)·변수·클래스 속성·제네릭 인자(`dict[str, Any]`) 전부다 — 별표 인자 면제(ruff `allow-star-arg-any`) 관례와 다른 선택이다. 프레임워크 오버라이드가 스텁에서 `Any` 를 쓰더라도 우리 쪽 선언은 `object`(또는 정확 타입)로 쓴다 — mypy 는 이를 호환으로 본다. 시그니처의 `Any` 는 #645 가 차단하고, 변수·제네릭 안의 `Any` 는 ⓓ 후보(#645)로 표시된다 — 단 `dict`/`Mapping`/`MutableMapping` 의 **값 자리** `Any`(`dict[str, Any]` — 매개변수·반환·변수·속성 어디든)는 #647 이 차단하며 그 자리는 #645 후보로 남지 않는다. 후보는 감수자가 집행한다(§4.1 «시그니처만 강제하므로 나머지는 백스톱과 감수자» 와 같은 분담). 경계 입력(폼 `cleaned_data`·`request.user`·무스텁 서드파티·`json.loads` 결과)은 `object` 또는 프레임워크가 주는 정확한 타입으로 받아 **받는 즉시** 좁힌다(`TypeIs`·`isinstance`·`type() is` — implementation-python §1.12 · 좁히는 자리는 dddjango-architecture-ddd §3.1 의 경계 규범대로 값 객체를 부르기 전). **JSON 문서는 `pydantic.TypeAdapter(그TypedDict).validate_python`/`validate_json` 으로 검증하며 받는다** — 대상은 파일·타 시스템·`json.loads` 결과이고 우리가 만든 JSON 도 파싱했으면 같다(strict `no-any-return`); HTTP body 는 ninja `Schema` 가 그 검증이다(implementation-python §12.0). 어떻게는 implementation-python §1.5, 무엇을 고르는지는 아래 결정표다. `object` 가 사는 자리는 좁히기·검증 도우미의 **매개변수**와 즉시 검증되는 **지역 변수**뿐이다(그 자리의 `dict/Mapping[…, object]` 는 #647 ⓓ 후보 — 감수자가 즉시 좁힘을 확인한다). **반환값·클래스 속성**에 `dict/Mapping[…, object]` 가 남으면 좁히지 않은 누수라 #647 이 차단한다. 면제는 둘 — 스텁이 강제하는 `forms.Form` 하위 `clean() -> dict[str, object]`(`ModelForm.clean` 은 `None` 이라 대상 아님)와 `TypeIs`/`TypeGuard[...]` 반환. `dict/Mapping` 값 자리가 아닌 반환 주석의 `object`(`-> object` 루트 · `tuple`/`list`/`Sequence` 원소)도 입구 밖 자리표시라 #647 ⓓ 후보다 — 예외는 스텁이 `object` 로 강제하는 프레임워크 콜백·오버라이드의 미러와 이벤트 컬렉션(`list[<Bc>Event]` 로 적을 수 있으면 그것이 답이다). `json.load(s)` 결과를 `TypeAdapter` 검증 없이 `object` 아닌 주석의 변수·`object` 아닌 반환·컴프리헨션·직접 첨자/속성 접근·리터럴 컨테이너 요소로 흘린 자리는 ⓓ #650 이다 — `x: object = json.loads(…)` 뒤 즉시 검증과 파서 직접 인자는 후보가 아니다.
+**`Any` 는 타입이 아니라 검사 포기다 — 아래 확인된 framework 소유 admin 슬롯을 제외한 우리 선언에는 쓰지 않는다.** 함수 시그니처(인자·`*args/**kwargs`·반환)·변수·클래스 속성·제네릭 인자(`dict[str, Any]`) 전부다 — 별표 인자 면제(ruff `allow-star-arg-any`) 관례와 다른 선택이다. 확인된 admin 슬롯 밖에서 프레임워크 오버라이드가 스텁에서 `Any` 를 쓰더라도 우리 쪽 선언은 `object`(또는 정확 타입)로 쓴다 — mypy 는 이를 호환으로 본다. 시그니처의 `Any` 는 #645 가 차단하고, 변수·제네릭 안의 `Any` 는 ⓓ 후보(#645)로 표시된다 — 단 `dict`/`Mapping`/`MutableMapping` 의 **값 자리** `Any`(`dict[str, Any]` — 매개변수·반환·변수·속성 어디든)는 #647 이 차단하며 그 자리는 #645 후보로 남지 않는다. 후보는 감수자가 집행한다(§4.1 «시그니처만 강제하므로 나머지는 백스톱과 감수자» 와 같은 분담). 경계 입력(폼 `cleaned_data`·`request.user`·무스텁 서드파티·`json.loads` 결과)은 `object` 또는 프레임워크가 주는 정확한 타입으로 받아 **받는 즉시** 좁힌다(`TypeIs`·`isinstance`·`type() is` — implementation-python §1.12 · 좁히는 자리는 dddjango-architecture-ddd §3.1 의 경계 규범대로 값 객체를 부르기 전). **JSON 문서는 `pydantic.TypeAdapter(그TypedDict).validate_python`/`validate_json` 으로 검증하며 받는다** — 대상은 파일·타 시스템·`json.loads` 결과이고 우리가 만든 JSON 도 파싱했으면 같다(strict `no-any-return`); HTTP body 는 ninja `Schema` 가 그 검증이다(implementation-python §12.0). 어떻게는 implementation-python §1.5, 무엇을 고르는지는 아래 결정표다. 아래 admin UI context 밖에서 `object` 가 사는 자리는 좁히기·검증 도우미의 **매개변수**와 즉시 검증되는 **지역 변수**뿐이다(그 자리의 `dict/Mapping[…, object]` 는 #647 ⓓ 후보 — 감수자가 즉시 좁힘을 확인한다). **반환값·클래스 속성**에 `dict/Mapping[…, object]` 가 남으면 좁히지 않은 누수라 #647 이 차단한다. 기존 면제는 둘 — 스텁이 강제하는 `forms.Form` 하위 `clean() -> dict[str, object]`(`ModelForm.clean` 은 `None` 이라 대상 아님)와 `TypeIs`/`TypeGuard[...]` 반환. `dict/Mapping` 값 자리가 아닌 반환 주석의 `object`(`-> object` 루트 · `tuple`/`list`/`Sequence` 원소)도 입구 밖 자리표시라 #647 ⓓ 후보다 — 예외는 스텁이 `object` 로 강제하는 프레임워크 콜백·오버라이드의 미러와 이벤트 컬렉션(`list[<Bc>Event]` 로 적을 수 있으면 그것이 답이다). `json.load(s)` 결과를 `TypeAdapter` 검증 없이 `object` 아닌 주석의 변수·`object` 아닌 반환·컴프리헨션·직접 첨자/속성 접근·리터럴 컨테이너 요소로 흘린 자리는 ⓓ #650 이다 — `x: object = json.loads(…)` 뒤 즉시 검증과 파서 직접 인자는 후보가 아니다.
 
-**키가 정해진 값 묶음(레코드)은 딕셔너리로 들고 다니지 않는다** — 우리 코드가 리터럴로 만든 값은 `TypedDict`, 파싱한 JSON 은 `TypeAdapter(그TypedDict)` 검증 파싱, 도메인 개념은 값 객체(dddjango-architecture-ddd §3.1). `dict/Mapping[str, object|Any]` 주석은 그 자체가 «구조를 안 정했다»는 신호다(#647). 레인이 바로 고르는 결정표:
+
+**admin context 판정**: #493 주석 존재 유지 · #645 framework 소유 슬롯 Any 제한 허용 · #646 제네릭 런타임 안전 유지 · #647 열린 UI context 조립/병합/전달 허용 · #650 실제 JSON 소비 검증 유지다. 출처가 확인된 Django admin 및 Parler admin 계열의 고정 framework 슬롯에만 적용한다. `extra_context`/`context`의 받기·each_context·UI dict·copy/update·고정 UI 키 쓰기·framework render 전달과 연결된 private 전달 helper의 매개변수·반환·지역 context 주석을 허용한다. form/inline/media의 별도 조립은 context의 허용을 취소하지 않는다. 컨테이너 부재 처리와 request UI metadata의 담기·전달도 허용한다. 업무 읽기·비교·계산·상태 변경 또는 ORM/use case/업무 함수로의 값 전달은 실제 소비이므로 그 자리부터 기존 규칙을 적용한다. 출처나 소비가 미해소 또는 동적/재귀 호출로 escape한 연결 context는 후보로 남겨 확인한다. 이름만 context인 값·같은 함수의 별도 업무 dict·framework 고정 kwargs 밖 bare Any·admin 클래스/경로 전체는 면제하지 않는다. 생성 private helper는 본문이 없으므로 정확히 결합된 열린 dict 슬롯의 #645/#647만 S1 미검증으로 보고하고 G2에서 실제 소비 흐름으로 다시 판단한다.
+
+**키가 정해진 값 묶음(레코드)은 딕셔너리로 들고 다니지 않는다** — framework 소유 admin UI context의 조립/전달은 앞 절 판정을 따르고, 우리 업무 코드가 리터럴로 만든 값은 `TypedDict`, 파싱한 JSON 은 `TypeAdapter(그TypedDict)` 검증 파싱, 도메인 개념은 값 객체(dddjango-architecture-ddd §3.1). `dict/Mapping[str, object|Any]` 주석은 그 자체가 «구조를 안 정했다»는 신호다(#647). 레인이 바로 고르는 결정표:
 
 | 값의 모양 | 어디서 왔나 | 쓰는 도구 | 금지 |
 |---|---|---|---|
-| 키가 정해진 값 묶음(레코드) | 우리 코드가 리터럴로 만든 내부 데이터 | `TypedDict`(종류가 여럿이면 `kind: Literal[…]` 판별 키로 union) | `dict/Mapping[str, object\|Any]` |
+| 키가 정해진 값 묶음(레코드) | 우리 업무 코드가 리터럴로 만든 내부 데이터(admin UI 조립/전달은 앞 절 판정) | `TypedDict`(종류가 여럿이면 `kind: Literal[…]` 판별 키로 union) | `dict/Mapping[str, object\|Any]` |
 | 키가 정해진 값 묶음 | 파싱한 JSON(파일 `json.load`·타 시스템·`json.loads` — 우리가 쓴 파일도 같다) | `TypeAdapter(그TypedDict).validate_python/validate_json` 로 검증 파싱(HTTP body 는 ninja `Schema` 가 이미 검증) · 파싱 전 값 사용 금지 | 검증 없는 `-> TypedDict` 반환(strict `no-any-return`) · `Any`/`object` 로 흘리기(ⓓ #650) |
 | 도메인 개념 | 도메인 계층 | dataclass·값 객체(dddjango-architecture-ddd §3.1) | 딕셔너리 |
 | 키가 데이터인 모음(조회표) | 어디든 | `dict[K, V]` 에 K·V 구체 타입(V 가 레코드면 `TypedDict`) | 값 타입 `object`·`Any` |
 | 구조를 모르는 임의 JSON 통과 | 직렬화·저장 경계 | 재귀 별칭 `JsonValue`(implementation-python §1.5 — arm 은 공변 `Sequence`/`Mapping`) | `dict[str, object]`·`Any` |
-| 타입이 이미 있는 값 | 함수 반환·매개변수·속성 | 실제 클래스(`BuildPlan` 등) | **입구 밖**의 자리표시 `object`(입구 매개변수·즉시 검증 지역 변수는 위 R-3448 · 반환 주석의 `object` 는 ⓓ #647) |
+| 타입이 이미 있는 값 | 함수 반환·매개변수·속성(admin framework 슬롯은 앞 절 판정) | 실제 클래스(`BuildPlan` 등) | **입구 밖**의 자리표시 `object`(입구 매개변수·즉시 검증 지역 변수는 위 R-3448 · 반환 주석의 `object` 는 ⓓ #647) |
 
 **django-stubs 가 제네릭으로 선언했지만 런타임은 subscript 못 하는 Django 기저는 모델 타입 인자를 적는다** — 타입 매개변수에 기본값이 없는 것들이다: `ModelForm`·`BaseInlineFormSet`·`ModelAdmin`·`InlineModelAdmin`(`TabularInline`/`StackedInline`)과 `ListView`·`DetailView`·`CreateView`·`UpdateView`·`DeleteView`·`FormView` 및 그 mixin, 그리고 `BaseFormSet`·`ModelChoiceField` 같은 폼셋·폼 필드 기저다(`View`·`TemplateView` 는 기본값이 있고 `RedirectView` 는 제네릭이 아니라 대상 밖 · 전수는 #646 집합 — django-stubs 6.1.0 기준). 맨몸 상속은 mypy strict `[type-arg]` 빚이고, `# type: ignore[type-arg]` 는 통과가 아니라 은폐라 붙이지 않는다 — 둘 다 #646 이 차단한다. 표기는 **`if TYPE_CHECKING:` 별칭이 기본**이다: `_ModelAdminBase: TypeAlias = admin.ModelAdmin[Parent]  # noqa: UP040` / `else: _ModelAdminBase: type[admin.ModelAdmin] = admin.ModelAdmin` — 기저에 직접 `X[Model]` 을 쓰면 import 시 `TypeError` 다(주석에만 쓰는 별칭은 `type` 문 — 지연 평가). 프로젝트가 `django_stubs_ext.monkeypatch()` 를 채택했으면(§6.1 의 관찰) 별칭 없이 `X[Model]` 직접 표기 — 채택은 레인이 도입하지 않는다. 스텁이 `ClassVar` 로 타입을 소유한 admin 선언 속성(`inlines` 등)은 재선언하지 않고(위 프레임워크 선언 면제), 프레임워크가 열어 둔 타입 매개변수는 bound(`Model`·`ModelForm[Model]`)로 적는다 — 예시는 implementation-django §18.
 
 ### §4.1 왜 전부인가
 
 타입 추론은 기계에게는 공짜지만 **읽는 사람에게는 노동이다** — 호출 결과의 타입을 알려면 독자가 시그니처를 따라가 «추론을 재연»해야 한다. 이 플러그인은 그 노동을 코드 작성 시점에 한 번 지불하는 쪽을 택한다. 부수 효과로 판정이 결정적이 된다 — 「자명한가」를 묻지 않으므로 검사가 런마다 흔들리지 않는다. 주류(PEP 8·mypy 기본 관례)의 「추론 가능한 지역 변수엔 비권장」과 다른 선택임을 숨기지 않는다. mypy strict 는 시그니처만 강제하므로 나머지는 백스톱과 감수자가 집행한다.
 
 ## §5 코드 주석·docstring 언어
 
 **기존 코드베이스의 주석 언어 관례를 우선한다.** 영어 주석이 지배적이면 영어로 맞춘다(일관성 최우선). 확립된 관례가 없으면 **한국어**로 쓴다. 언어는 코드 동작이 아니라 사람의 유지보수를 위한 것이므로, 한 코드베이스 안에서 섞지 않는다.

```

## dddjango/skills/discipline-houserules/references/final.md

Before SHA256: c099134b2ccc67c6137519293fba94ddef6ecb63792b985d5b6a8ef7a4334ae1
After SHA256: 768db015552547977d941d638c54a90ff5922229d70e1cbe99e6558bdc47cde1

```diff
--- before/dddjango/skills/discipline-houserules/references/final.md
+++ after/dddjango/skills/discipline-houserules/references/final.md
@@ -20,24 +20,24 @@
 - **#486** — 어느 BC 를 열어도 이 트리의 골격이 «그대로» 있다 — 내용이 있든 없든 상관없다. 파일트리를 지키지 않는 구현·설계는 «반환»이다.
 - **#488** — 고정 이름의 칸은 «부모가 있으면» 반드시 있다 — 폴더는 비어도 `__init__.py` 로, 파일도 비면 «빈 파일»로 만든다. 칸의 승격 실현(#490 교체형)이 이미 있으면 그 실현이 이 충족이다 — 동명 빈 파일을 병설하지 않는다. 승격 허용 파일 칸의 빈 실현은 «빈 파일»이다 — 승격형은 내용이 생긴 뒤의 대체 실현이며, 예비 폴더형을 미리 파지 않는다. 빈 파일로 실현된 칸의 **내용 규칙**(진입점·포트 «하나» 등)은 내용이 생긴 뒤부터 선다 — Coordinator 가 빈 모듈을 error inventory 에서 제외하는 것(R-0319)과 같은 시점이며, 검사기는 내용 없는 골격 파일(0바이트·docstring/주석뿐)을 내용 규칙에서 건너뛴다. 빈 파일을 지워 red 를 푸는 것은 #488 위반이다.
 - **#489** — `<…>` 가 붙은 자리표시자 칸만 그 개념이 실제로 생길 때 생긴다 — 그 외에 「이 BC 엔 없으니 뺀다」는 축소가 아니라 위반이다.
 - **#490** — `application/<bounded_context>/**` 안에 트리에 없는 경로가 하나라도 있으면 위반이다(`utils/`·`common/`·`helpers/`). 폐쇄는 **칸**(폴더 + 트리가 이름을 준 파일)에만 걸리고, 트리가 리프로 닫은 폴더 «안»의 추가 모듈은 작성자 재량이다(#15). `framework/`·`<project>/` 는 이 원칙의 주어가 아니다. 단, §1 트리의 **승격 허용 표기**가 붙은 파일 칸은 두 실현을 갖는다 — `<이름>.py`(기본) ⇄ 동명 폴더 `<이름>/`(**동명 폴더 승격**). 유효한 승격 폴더는 트리에 있는 실현이지 «트리에 없는 경로»가 아니다(형태 요건은 아래).
 - **#491** — 칸의 유형은 셋뿐이고 «조건부»는 없다 — ① 고정 이름 ② `<>` 첫 등장 ③ `<>` 재등장(조상이 이미 연 낱말이라 값이 이미 채워져 있어 ①과 같다). «조건부 없음»의 주어는 칸의 **존재**(생성 조건)다 — 승격 허용 표기는 존재가 아니라 실현 형태(#490)의 값이다.
 - **#492** — 「그 파일이 있어야 하나」는 트리가 정하고 「그것을 어떻게 쓰나」는 스킬이 정한다.
 
 골격의 실현 주체는 **coder** 다 — 승인 스코프의 BC 를 새로 만들거나 touched 하면(touched = G0 스코프의 그 BC — §4 와 같은 자 · 명세가 골격 실현을 지시한 데이터소스 BC 포함) 고정·재등장 칸을 빈 채로라도 실현한다. 위반은 `check-layer-skeleton` 이 잡는다. 칸의 승격 실현이 이미 있으면 그 실현이 곧 골격 실현이다 — 동명 빈 파일을 병설하지 않는다(#488).
 
 동명 폴더 승격의 형태: 승격 폴더는 안에 **본체 `<이름>.py`** 와 **재수출 전용 `__init__.py`** 를 반드시 가진다 — 본체 없는 폴더는 위장이고, 형제 `<이름>.py` 와 `<이름>/` 의 공존도 위반이다(파일시스템은 공존을 허용하고 import 는 패키지가 이겨 조용한 위장 중복이 된다). 내부는 **1단 평평**이다 — 하위 폴더는 위반이며, 부품 군집이 폴더를 요구하면 그것은 트리 개정 신호이지 중첩 근거가 아니다. `__init__.py` 재수출은 `from .<모듈> import <이름> as <이름>`(redundant alias) 또는 `__all__` 선언으로 한다(mypy strict `--no-implicit-reexport` 가 인정하는 두 형태) — 본체 코드를 `__init__.py` 에 두지 않고, 폴더 내부 상호 참조는 `__init__` 경유 없이 모듈 직접 상대 import 로 한다. 바깥 import 표면(`...<칸>` 모듈 경로로 공개되는 이름 집합)은 승격·환원 어느 방향이든 불변이어야 하고, 승격은 `git mv` 로 이력을 보존한다.
-승격 폴더는 «트리가 리프로 닫은 폴더»가 아니다 — 내부 재량은 **배열·명명 재량**이지 **파일 신설 재량이 아니다**. 부품 파일의 신설 근거는 감사 판정(동명 폴더 승격 발견)의 클러스터 열거 또는 후속 감사 신호뿐이고, #192(사설 조각은 제 파일 안 `_` 함수)·#189(유스케이스 간 돌려쓰기 금지)가 부품 파일 각각에 그대로 적용되며, 정크드로어 이름(`utils.py`·`helpers.py` 류)은 위반이다. 이번 작업에서 새로 나타난 승격 폴더의 각 부품(본체·`__init__.py` 제외)은 50행(물리 행·빈 줄 제외) 이상이어야 하고(출생 하한 — 기존 폴더의 사후 축소는 무관·환원 의무를 만들지 않는다), 부품이 0개(본체+`__init__.py` 뿐)가 된 승격 폴더는 위반이다(환원 신호 — 이번 작업 산출이면 발견 반영으로, 기존이면 G0 빚 경로로 환원한다). 저장(save)류 쓰기 호출은 본체에만 둔다.
+승격 폴더는 «트리가 리프로 닫은 폴더»가 아니다 — 내부 재량은 **배열·명명 재량**이지 **파일 신설 재량이 아니다**. 부품 파일의 신설 근거는 감사 판정(동명 폴더 승격 발견)의 클러스터 열거 또는 후속 감사 신호뿐이고, #192(사설 조각은 제 파일 안 `_` 함수)·#189(유스케이스 간 돌려쓰기 금지)가 부품 파일 각각에 그대로 적용되며, 정크드로어 이름(`utils.py`·`helpers.py` 류)은 위반이다. 부품이 0개(본체+`__init__.py` 뿐)가 된 승격 폴더는 위반이다(환원 신호 — 이번 작업 산출이면 발견 반영으로, 기존이면 G0 빚 경로로 환원한다). 저장(save)류 쓰기 호출은 본체에만 둔다.
 칸을 «파일»로 명명하는 규범·검사기 문면(#256·#123·#193 …)은 그 칸의 실현 — 파일 또는 승격 본체 — 을 가리킨다. 승격 허용 표기의 값은 §1 트리가 소유한다(정본 `docs/file_tree.html` 의 data-sw · `standard_tree.Row.swappable` — 허용 칸: 트리 12·14·15·18·20·21·24·41·61·74·92·94·96행). 배제는 사유로만 선다 — ⓐ 범위 밖 서브트리(`framework/**`·`<project>/**`)·비-py(templates) ⓑ 도구 생성물(migrations) ⓒ 형태 명문 고정(composition_root #497 · api_router #107 · cron_job #174/#178 · event_subscription #509 · event_router #508 · apps #535/#538 · bc_error_schema #114/#572 · admin panel #342/#343) ⓓ 개념 원자 — 성장 출구가 새 인스턴스 파일(entity·값 객체·event·exception·계약·port 선언·domain repository 선언·`<entity>_model` #335 …). 배제 칸의 비대는 그 칸의 기존 규범이 관할한다 — 승격은 출구가 아니다. 배제·허용 표기를 바꾸는 주어는 정본 트리(트리 개정)다 — 프로젝트 관찰·판정 반복은 개정 제안 신호이지 현장 변경 근거가 아니다.
 
-**어댑터 고정 골격** — `driven_layer/adapter/` 아래 ACL의 `anticorruption_layer/<other_bounded_context>/<capability>_adapter/`, 외부 시스템의 `external_system/<system>/<capability>_adapter/`, 그 밖 능력의 `<capability>/<technology>_adapter/` 는 처음부터 패키지다. 바깥 패키지와 `adapter/`·`command/`·`constant/`·`contract/`·`schema/` 다섯 역할 폴더에 `__init__.py` 를 반드시 둔다(#488). 역할 폴더는 내용이 없어도 생략하지 않는다. 초기화 파일은 재수출 전용이다(#640). 바깥에 구현 본체를 두거나 단일 `.py` 파일로 대체하지 않으며, 역할 폴더 안에 추가 폴더를 만들지 않는다(#490). 실제 내용 파일은 필요할 때만 만들며 50행 하한·200행 승격 신호의 대상이 아니다.
+**어댑터 고정 골격** — `driven_layer/adapter/` 아래 ACL의 `anticorruption_layer/<other_bounded_context>/<capability>_adapter/`, 외부 시스템의 `external_system/<system>/<capability>_adapter/`, 그 밖 능력의 `<capability>/<technology>_adapter/` 는 처음부터 패키지다. 바깥 패키지와 `adapter/`·`command/`·`constant/`·`contract/`·`schema/` 다섯 역할 폴더에 `__init__.py` 를 반드시 둔다(#488). 역할 폴더는 내용이 없어도 생략하지 않는다. 초기화 파일은 재수출 전용이다(#640). 바깥에 구현 본체를 두거나 단일 `.py` 파일로 대체하지 않으며, 역할 폴더 안에 추가 폴더를 만들지 않는다(#490). 실제 내용 파일은 필요할 때만 만들며 200행 승격 신호의 대상이 아니다.
 
 **#651 클래스별 파일** — `adapter/`·`command/`·`contract/`·`schema/` 의 내용 파일은 비공개 클래스를 포함해 클래스 하나당 파일 하나다. 같은 역할의 클래스가 여러 개면 각각 파일을 만든다. `constant/` 는 클래스 없이 관련 상수끼리 한 파일에 묶는다. 내용 없는 골격 파일과 재수출 초기화 파일은 클래스 수 검사의 대상이 아니다.
 
 **역할 배치** — `adapter/` 는 포트를 구현하는 클래스를 소유한다. 외부 응답을 포트 반환값으로 바꾸는 reader 는 그 구현의 private 메서드 또는 본문에 둔다. `command/` 는 주입되는 호출 계약(Protocol 등)을 클래스별로 둔다. `contract/` 는 내부 계약 클래스를 소유하며 그 계약을 반환하는 builder 도 같은 파일에 둔다. `schema/` 는 외부 입출력 검증 클래스를 소유하며 관련 타입 별칭은 해당 스키마 파일에 둔다. `constant/` 는 프롬프트 등 관련 값을 `prompt.py` 같은 응집된 묶음으로 둔다. 반환 클래스가 포트 소유라는 이유로 외부 스키마를 아는 변환 함수를 포트 파일로 옮기지 않는다. 내부 참조는 모듈 직접 상대 import 로 연결한다. 기존 상속·명명·예외 번역 검사는 구현 역할 파일에, 의존 방향과 격리는 전체 역할 파일에 적용한다.
 ## §1 표준 트리 — 170행
 <!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->
 
 행 번호는 정본의 행 번호이고, 규칙·검사기·명세가 「트리 N행」으로 이 번호를 가리킨다. `<…>` 는 자리표시자(§0 유형 ②③)다.
 
 <!-- TREE:BEGIN — tree_mirror_check 가 쓴다 · 손으로 고치지 않는다 -->

```

## codex-dddjango/skills/dddjango-discipline-houserules/references/final.md

Before SHA256: c099134b2ccc67c6137519293fba94ddef6ecb63792b985d5b6a8ef7a4334ae1
After SHA256: 768db015552547977d941d638c54a90ff5922229d70e1cbe99e6558bdc47cde1

```diff
--- before/codex-dddjango/skills/dddjango-discipline-houserules/references/final.md
+++ after/codex-dddjango/skills/dddjango-discipline-houserules/references/final.md
@@ -20,24 +20,24 @@
 - **#486** — 어느 BC 를 열어도 이 트리의 골격이 «그대로» 있다 — 내용이 있든 없든 상관없다. 파일트리를 지키지 않는 구현·설계는 «반환»이다.
 - **#488** — 고정 이름의 칸은 «부모가 있으면» 반드시 있다 — 폴더는 비어도 `__init__.py` 로, 파일도 비면 «빈 파일»로 만든다. 칸의 승격 실현(#490 교체형)이 이미 있으면 그 실현이 이 충족이다 — 동명 빈 파일을 병설하지 않는다. 승격 허용 파일 칸의 빈 실현은 «빈 파일»이다 — 승격형은 내용이 생긴 뒤의 대체 실현이며, 예비 폴더형을 미리 파지 않는다. 빈 파일로 실현된 칸의 **내용 규칙**(진입점·포트 «하나» 등)은 내용이 생긴 뒤부터 선다 — Coordinator 가 빈 모듈을 error inventory 에서 제외하는 것(R-0319)과 같은 시점이며, 검사기는 내용 없는 골격 파일(0바이트·docstring/주석뿐)을 내용 규칙에서 건너뛴다. 빈 파일을 지워 red 를 푸는 것은 #488 위반이다.
 - **#489** — `<…>` 가 붙은 자리표시자 칸만 그 개념이 실제로 생길 때 생긴다 — 그 외에 「이 BC 엔 없으니 뺀다」는 축소가 아니라 위반이다.
 - **#490** — `application/<bounded_context>/**` 안에 트리에 없는 경로가 하나라도 있으면 위반이다(`utils/`·`common/`·`helpers/`). 폐쇄는 **칸**(폴더 + 트리가 이름을 준 파일)에만 걸리고, 트리가 리프로 닫은 폴더 «안»의 추가 모듈은 작성자 재량이다(#15). `framework/`·`<project>/` 는 이 원칙의 주어가 아니다. 단, §1 트리의 **승격 허용 표기**가 붙은 파일 칸은 두 실현을 갖는다 — `<이름>.py`(기본) ⇄ 동명 폴더 `<이름>/`(**동명 폴더 승격**). 유효한 승격 폴더는 트리에 있는 실현이지 «트리에 없는 경로»가 아니다(형태 요건은 아래).
 - **#491** — 칸의 유형은 셋뿐이고 «조건부»는 없다 — ① 고정 이름 ② `<>` 첫 등장 ③ `<>` 재등장(조상이 이미 연 낱말이라 값이 이미 채워져 있어 ①과 같다). «조건부 없음»의 주어는 칸의 **존재**(생성 조건)다 — 승격 허용 표기는 존재가 아니라 실현 형태(#490)의 값이다.
 - **#492** — 「그 파일이 있어야 하나」는 트리가 정하고 「그것을 어떻게 쓰나」는 스킬이 정한다.
 
 골격의 실현 주체는 **coder** 다 — 승인 스코프의 BC 를 새로 만들거나 touched 하면(touched = G0 스코프의 그 BC — §4 와 같은 자 · 명세가 골격 실현을 지시한 데이터소스 BC 포함) 고정·재등장 칸을 빈 채로라도 실현한다. 위반은 `check-layer-skeleton` 이 잡는다. 칸의 승격 실현이 이미 있으면 그 실현이 곧 골격 실현이다 — 동명 빈 파일을 병설하지 않는다(#488).
 
 동명 폴더 승격의 형태: 승격 폴더는 안에 **본체 `<이름>.py`** 와 **재수출 전용 `__init__.py`** 를 반드시 가진다 — 본체 없는 폴더는 위장이고, 형제 `<이름>.py` 와 `<이름>/` 의 공존도 위반이다(파일시스템은 공존을 허용하고 import 는 패키지가 이겨 조용한 위장 중복이 된다). 내부는 **1단 평평**이다 — 하위 폴더는 위반이며, 부품 군집이 폴더를 요구하면 그것은 트리 개정 신호이지 중첩 근거가 아니다. `__init__.py` 재수출은 `from .<모듈> import <이름> as <이름>`(redundant alias) 또는 `__all__` 선언으로 한다(mypy strict `--no-implicit-reexport` 가 인정하는 두 형태) — 본체 코드를 `__init__.py` 에 두지 않고, 폴더 내부 상호 참조는 `__init__` 경유 없이 모듈 직접 상대 import 로 한다. 바깥 import 표면(`...<칸>` 모듈 경로로 공개되는 이름 집합)은 승격·환원 어느 방향이든 불변이어야 하고, 승격은 `git mv` 로 이력을 보존한다.
-승격 폴더는 «트리가 리프로 닫은 폴더»가 아니다 — 내부 재량은 **배열·명명 재량**이지 **파일 신설 재량이 아니다**. 부품 파일의 신설 근거는 감사 판정(동명 폴더 승격 발견)의 클러스터 열거 또는 후속 감사 신호뿐이고, #192(사설 조각은 제 파일 안 `_` 함수)·#189(유스케이스 간 돌려쓰기 금지)가 부품 파일 각각에 그대로 적용되며, 정크드로어 이름(`utils.py`·`helpers.py` 류)은 위반이다. 이번 작업에서 새로 나타난 승격 폴더의 각 부품(본체·`__init__.py` 제외)은 50행(물리 행·빈 줄 제외) 이상이어야 하고(출생 하한 — 기존 폴더의 사후 축소는 무관·환원 의무를 만들지 않는다), 부품이 0개(본체+`__init__.py` 뿐)가 된 승격 폴더는 위반이다(환원 신호 — 이번 작업 산출이면 발견 반영으로, 기존이면 G0 빚 경로로 환원한다). 저장(save)류 쓰기 호출은 본체에만 둔다.
+승격 폴더는 «트리가 리프로 닫은 폴더»가 아니다 — 내부 재량은 **배열·명명 재량**이지 **파일 신설 재량이 아니다**. 부품 파일의 신설 근거는 감사 판정(동명 폴더 승격 발견)의 클러스터 열거 또는 후속 감사 신호뿐이고, #192(사설 조각은 제 파일 안 `_` 함수)·#189(유스케이스 간 돌려쓰기 금지)가 부품 파일 각각에 그대로 적용되며, 정크드로어 이름(`utils.py`·`helpers.py` 류)은 위반이다. 부품이 0개(본체+`__init__.py` 뿐)가 된 승격 폴더는 위반이다(환원 신호 — 이번 작업 산출이면 발견 반영으로, 기존이면 G0 빚 경로로 환원한다). 저장(save)류 쓰기 호출은 본체에만 둔다.
 칸을 «파일»로 명명하는 규범·검사기 문면(#256·#123·#193 …)은 그 칸의 실현 — 파일 또는 승격 본체 — 을 가리킨다. 승격 허용 표기의 값은 §1 트리가 소유한다(정본 `docs/file_tree.html` 의 data-sw · `standard_tree.Row.swappable` — 허용 칸: 트리 12·14·15·18·20·21·24·41·61·74·92·94·96행). 배제는 사유로만 선다 — ⓐ 범위 밖 서브트리(`framework/**`·`<project>/**`)·비-py(templates) ⓑ 도구 생성물(migrations) ⓒ 형태 명문 고정(composition_root #497 · api_router #107 · cron_job #174/#178 · event_subscription #509 · event_router #508 · apps #535/#538 · bc_error_schema #114/#572 · admin panel #342/#343) ⓓ 개념 원자 — 성장 출구가 새 인스턴스 파일(entity·값 객체·event·exception·계약·port 선언·domain repository 선언·`<entity>_model` #335 …). 배제 칸의 비대는 그 칸의 기존 규범이 관할한다 — 승격은 출구가 아니다. 배제·허용 표기를 바꾸는 주어는 정본 트리(트리 개정)다 — 프로젝트 관찰·판정 반복은 개정 제안 신호이지 현장 변경 근거가 아니다.
 
-**어댑터 고정 골격** — `driven_layer/adapter/` 아래 ACL의 `anticorruption_layer/<other_bounded_context>/<capability>_adapter/`, 외부 시스템의 `external_system/<system>/<capability>_adapter/`, 그 밖 능력의 `<capability>/<technology>_adapter/` 는 처음부터 패키지다. 바깥 패키지와 `adapter/`·`command/`·`constant/`·`contract/`·`schema/` 다섯 역할 폴더에 `__init__.py` 를 반드시 둔다(#488). 역할 폴더는 내용이 없어도 생략하지 않는다. 초기화 파일은 재수출 전용이다(#640). 바깥에 구현 본체를 두거나 단일 `.py` 파일로 대체하지 않으며, 역할 폴더 안에 추가 폴더를 만들지 않는다(#490). 실제 내용 파일은 필요할 때만 만들며 50행 하한·200행 승격 신호의 대상이 아니다.
+**어댑터 고정 골격** — `driven_layer/adapter/` 아래 ACL의 `anticorruption_layer/<other_bounded_context>/<capability>_adapter/`, 외부 시스템의 `external_system/<system>/<capability>_adapter/`, 그 밖 능력의 `<capability>/<technology>_adapter/` 는 처음부터 패키지다. 바깥 패키지와 `adapter/`·`command/`·`constant/`·`contract/`·`schema/` 다섯 역할 폴더에 `__init__.py` 를 반드시 둔다(#488). 역할 폴더는 내용이 없어도 생략하지 않는다. 초기화 파일은 재수출 전용이다(#640). 바깥에 구현 본체를 두거나 단일 `.py` 파일로 대체하지 않으며, 역할 폴더 안에 추가 폴더를 만들지 않는다(#490). 실제 내용 파일은 필요할 때만 만들며 200행 승격 신호의 대상이 아니다.
 
 **#651 클래스별 파일** — `adapter/`·`command/`·`contract/`·`schema/` 의 내용 파일은 비공개 클래스를 포함해 클래스 하나당 파일 하나다. 같은 역할의 클래스가 여러 개면 각각 파일을 만든다. `constant/` 는 클래스 없이 관련 상수끼리 한 파일에 묶는다. 내용 없는 골격 파일과 재수출 초기화 파일은 클래스 수 검사의 대상이 아니다.
 
 **역할 배치** — `adapter/` 는 포트를 구현하는 클래스를 소유한다. 외부 응답을 포트 반환값으로 바꾸는 reader 는 그 구현의 private 메서드 또는 본문에 둔다. `command/` 는 주입되는 호출 계약(Protocol 등)을 클래스별로 둔다. `contract/` 는 내부 계약 클래스를 소유하며 그 계약을 반환하는 builder 도 같은 파일에 둔다. `schema/` 는 외부 입출력 검증 클래스를 소유하며 관련 타입 별칭은 해당 스키마 파일에 둔다. `constant/` 는 프롬프트 등 관련 값을 `prompt.py` 같은 응집된 묶음으로 둔다. 반환 클래스가 포트 소유라는 이유로 외부 스키마를 아는 변환 함수를 포트 파일로 옮기지 않는다. 내부 참조는 모듈 직접 상대 import 로 연결한다. 기존 상속·명명·예외 번역 검사는 구현 역할 파일에, 의존 방향과 격리는 전체 역할 파일에 적용한다.
 ## §1 표준 트리 — 170행
 <!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->
 
 행 번호는 정본의 행 번호이고, 규칙·검사기·명세가 「트리 N행」으로 이 번호를 가리킨다. `<…>` 는 자리표시자(§0 유형 ②③)다.
 
 <!-- TREE:BEGIN — tree_mirror_check 가 쓴다 · 손으로 고치지 않는다 -->

```

## dddjango/commands/dddjango.md

Before SHA256: 1b44e4286f54c2eedb85caaf8c19e71a8c3ed1cee574e2e38f2764e4d22c880b
After SHA256: 25fb90b6acd0211de2d441f2af96a428614f00a168e4ddd06985e6883d0621d0

```diff
--- before/dddjango/commands/dddjango.md
+++ after/dddjango/commands/dddjango.md
@@ -86,23 +86,23 @@
 
 1. `dddjango:design-architect`를 호출한다(서브에이전트 지정은 항상 `dddjango:` 한정 표기 — 동명 에이전트를 가진 플러그인이 함께 설치될 수 있다 · 2026-08-15) — 입력: 스코프 메모 · 활성 lens 목록 · 설계 명세 저장 경로. architect는 기존 프로젝트 구조를 조사해 **패키지·테스트 구조 결정**과 모든 영구 test artifact `add/update/move/split/rename/remove/weaken` 후보의 최소 입장 표(`candidate | protected contract/evidence | unique production failure | existing authoritative coverage | decision | owner/path`)를 명세에 포함한다. decision은 `add/update/reuse/retain/remove/reject/pending` 일곱 값만 쓴다. 산출: 통합 설계 명세 1건.
 2. 활성 lens별 리뷰어를 **병렬**로 호출한다: `dddjango:design-review-ddd` / `dddjango:design-review-api` / `dddjango:design-review-db` (활성 lens만). **병렬의 정의는 «한 응답 안의 서브에이전트 호출(Task/Agent — 하네스 명칭 무관) 다발»이다(2026-08-13)** — 리뷰어 전부(아래 3의 discipline lightweight 포함)를 한 메시지에서 동시에 호출한다. 하나 끝나면 다음을 부르는 순차 호출은 병렬이 아니다(라운드 2′ 실측: 문면 «병렬»인데 직렬 dispatch — Phase 1 벽시계 낭비의 최대 항목). **연속된 «개별» 응답으로 하나씩 백그라운드 배차하는 것도 순차 호출이다(라운드 3 실측 — 실행이 병렬로 겹쳐도 다발 문면 위반)** — 다발은 문자 그대로 한 응답 안이다. 모든 리뷰어는 타 노트를 받지 않으므로 순서 의존이 없다(편향 방지 원칙이 병렬을 지지한다). 단 **입력 준비가 다발보다 앞이다** — Error response contract scope 면 discipline 에 줄 project-wide tree·inventory 를 먼저 구성해 동봉한다(다발을 서두르느라 필수 입력을 비우지 않는다). 이 정의는 리뷰어를 **둘 이상 부르는 모든 호출**(재작업 재리뷰 포함)에 적용하고, 하나만 다시 부르는 재호출은 단독 호출이 정당하다. 다발에서 리뷰어를 누락했으면 늦은 단독 호출로라도 반드시 호출하고 병렬 미준수 사실을 보고한다 — 금지의 주어는 «계획된 순차»이지 «누락의 교정»이 아니다. G1 배너에 다발 크기 한 줄(예: `리뷰 다발 4종 1회`)을 남긴다. 각 리뷰어에는 architect의 명세 초안만 준다(타 리뷰 노트·코드는 주지 않는다 — 편향 방지). 입력에 플러그인 설치 루트 절대 경로를 함께 준다(로드 스킬 references 실독용 · 2026-08-17). API/DB reviewer는 자기 lens의 candidate·위험을 제안하고 각 관련 행의 evidence·독자 failure·중복을 감사하되 decision 없이 테스트를 의무화하지 않는다. 산출: lens별 리뷰 노트. 노트 수신 시 형식을 구문 검사한다 — 집행성 판정 1행, ddd 노트는 판정-소유 대조 표(또는 «판정 없음» 1행)가 없으면 그 리뷰어에게 반송한다(원문 대조는 하지 않는다 — 존재 검사만 · 2026-08-17).
 3. `dddjango:discipline-reviewer`를 **Phase 1 lightweight 모드**로 항상 호출해(위 2의 병렬 다발에 합류 — 별도 순차 호출 금지) 입장 표의 열·일곱 decision·protected contract·독자 failure·기존 coverage·owner를 독립 감사시킨다. `pending`, framework/private mechanics의 부당한 `add`, 의미 보존 재조직의 새 case/assertion/Red를 G1 전에 잡는다. Error response contract scope에서는 current project-wide tree도 함께 주어 기존 12-slot surface inventory와 물리 소유권·우회까지 추가 점검한다. 구현 코드·테스트 diff·실행 결과·슬라이스는 요구하지 않는다.
 4. `dddjango:design-architect`를 다시 호출해 리뷰 노트를 반영하고 리뷰어 간 충돌을 중재시킨다. **scope.md가 "범위 아님 / 필요 시 G1 제안"으로 명시한 항목(Y)은 architect가 기본(미적용)을 명세에 현재-상태로 commit하고 배너 override 항목으로 산출**한다(architect가 'Y감이냐'를 판정하지 않고 scope.md의 그 목록을 앵커로 쓴다). 스스로 해소 못 하는 트레이드오프(양자택일·리뷰어 충돌 등 Z)만 미해결 옵션으로 남긴다.
 5. **G1 배너**로 최종 설계 명세(경로)를 제시하고 승인받는다 — Y 항목은 "기본=미적용 · 추가할래?"로, Z는 옵션으로 보인다. 배너에는 입장 표의 `add/update/reuse/retain/remove/reject/pending`을 decision별로 직접 나열하고 각 행의 owner/path를 보여 준다(없으면 `없음`). `pending`이 하나라도 남으면 승인 입력을 Phase 2 진입으로 해석하지 않고 한정된 설계 질문으로 반송한다. 의미 보존 move/split/rename/reorganization은 새 case·assertion·Red가 없고 전후 보호가 같다는 기록까지 보여 준다. 설계 명세는 이후 테스트와 코드의 **단일 근거**다.
    - **G1 결정 처리**(승인 후): ① **기본 수락** → `design-architect` 재호출 없이 Phase 2로 진행한다(명세가 이미 단일 근거라 잠금 재호출 불요). ② **Y 항목 채택(override)** → *너(Coordinator)*가 `scope.md`를 갱신한다(그 항목을 "범위 아님"에서 `<항목>: G1 채택 (사용자 승인)` 형태의 *단독 줄*로 옮긴다 — `아님`·`않는다` 등 부정 토큰을 같은 줄에 두지 않는다) + `design-architect`를 **G1 override 입력**(Phase 1 입력 형식)으로 재호출해 해당 절만 반영시킨다. ③ **Z 옵션 결정·override** → `design-architect`를 G1 override 입력으로 재호출한다. ②·③도 override 반영이 끝나면 ①과 동일하게 Phase 2로 진행한다(분기는 결정을 반영하는 절차만 가르고 후속 단계는 같다 — 단 **dispatch 전에 pre-gate 를 무조건 재실행**한다: 무배너 경로라 예보 착지는 Phase 2 진입 한 줄 상태 + pregate-report 다 · 아래 pre-gate 문단). **너는 `design-spec.md`를 직접 쓰지 않는다**(②의 `scope.md` 갱신은 네 소유 파일이라 예외 — `design-spec`은 architect 전속). 이 전속은 경로 불문이다(2026-08-17) — G1 본선·리뷰 반송·G1′(수정 모드)·게이트 승인문이 design-spec 갱신을 명시 지시한 경우를 포함해, 집행은 언제나 `design-architect` 재호출로 위임한다(해당 경로의 확립된 형식으로: override 입력 또는 리뷰/반송 노트 전달). 승인이 «무엇을» 바꿀지 정해도 «누가» 바꾸는지는 바뀌지 않는다. `scope.md`(네 소유)에는 스코프 결정만 적는다 — 설계 결정·입장표 해석을 그리 옮겨 적거나 역할 지시문에 명세 재해석을 실어 우회하지 않는다. *왜* — 흔한 기본 수락에 architect 재호출(잠금)을 없애 비용·비결정을 줄이고, Y 채택 시 `scope.md` 갱신으로 백스톱 ⑩의 G1-승인 면제가 발화해 "미요청 단정 + 채택 코드"의 거짓 차단을 막는다.
 
 Ninja endpoint/error contract/response Schema가 변경되는 scope에서는 **G1 제시 전과 사용자 승인 응답 뒤 Phase 2 dispatch 직전**에 current `design-spec.md`를 다시 읽는다. `Error response contract 12-slot`의 label과 순서는 정확히 `contract scope`; `scope evidence`; `error profile`; `compatibility/rollout`; `common FrameworkErrorSchema action`; `common FrameworkErrorSchema shape/approval`; `BC error module`; `BC ErrorCode`; `BC ErrorSchema`; `prepared error mapping`; `controller mapping`; `response/OpenAPI/tests`다. 12개 모두 구체적이고 선택 profile에 맞으며 서로 일관돼야 한다. `none | not applicable`은 해당 profile/slot이 허용하고 이유·evidence를 함께 기록한 경우에만 구체값이다. `dddjango-code-json`은 `error-bc`가 비어도 slot 5가 `reuse | create | approved-change`여야 하고 slot 6의 common shape가 필수다. plugin 기본 property 목록은 없으며 기존 프로젝트의 관찰된 exact shape 또는 신규 scope에서 별도로 승인된 exact shape를 그대로 사용한다. slot 9의 BC base가 slot 6의 식별자 field를 `<Bc>ErrorCode`로 좁히면서 공통의 default를 잃어 required가 되는 것은 canon이다(식별자 field 한정·ErrorCode 좁힘 동반일 때만 — 2026-08-15). 이때 slots 7–9는 public BC error 부재 이유와 함께 `none`일 수 있지만, slots 10–12는 승인된 empty mapping/runtime/OpenAPI inventory와 검증을 명시해 공백으로 넘기지 않는다. `preserve-established`의 slots 5–12는 관찰된 profile-native artifact/behavior 또는 evidence가 있는 `none | not applicable`이어야 하며 code-profile Enum·base·direct-`Status`를 강제하지 않는다. 누락·모호·모순이면 승인 입력이 있어도 Phase 2로 가지 않고 G1/G1′ 설계로 반송한다. Coordinator는 slot 값을 대신 결정하거나 조용히 보충·수정하지 않는다. `dddjango-code-json`에서 현재 common shape와 승인 shape가 다른데 `common FrameworkErrorSchema action=approved-change`와 **별도로 표면화해 받은 명시적 사용자 승인 evidence**가 함께 없으면 G1을 차단한다. 설계 전체에 대한 일반 G1 승인은 shape 변경 승인을 대신하지 않는다. 신규 scope의 최초 shape도 exact field/type/required/default/nullability/모든 `Field` metadata/model config·legacy `Config`/validator/serializer/computed field/Pydantic hook inventory와 effective semantics/wire 직렬화 결과와 각 field 의미를 보여 준 별도 명시 승인 없이는 생성하지 않는다. 재작업으로 profile·compatibility·wire 또는 그 밖의 API semantic slot이 바뀌면 API reviewer를 다시 호출하고, 물리 구조·소유권·controller mapping 결정이 바뀌면 discipline reviewer를 다시 호출해 반영한 뒤 새 G1을 제시한다.
 
-**pre-gate — 설계 명세 결정적 예보(차단 모드)**: `design-spec.md` 내용이 바뀔 때마다 실행한다 — architect 초안 수신 직후(위 2의 리뷰 다발과 병렬 1회 — 조기 신호), 리뷰 반영·개정 수신마다, 그리고 **G1/G1′ 배너 제시 직전 최종본과 G1 override(②/③) 반영 후 Phase 2 dispatch 전에는 무조건**(배너의 예보 1행은 항상 최종본에 대한 것 — 낡은 green 금지). 실행 판형은 `scripts/design_pregate.py <산출물 폴더>/design-spec.md . --report <산출물 폴더>/pregate-report.md` 다(`scripts/…` 는 registry 게이트와 같은 규약 — 스킬 폴더의 절대 경로로 펴고 cwd 는 타깃 프로젝트 루트다 · 기계가독 블록 해시가 불변이면 재실행을 skip 한다 — 캐시가 직렬 비용을 없앤다). 팬텀 스텁·git 호출은 전부 스크립트가 격리 사본(저장소 트리 밖) 위에서 수행하는 **결정적 투영물**이라 «구현 코드는 직접 쓰지 않는다» 경계와 충돌하지 않는다 — 너는 이 절차를 위해 bare git 을 직접 치지 않는다. 이 실행은 **게이트다**(차단 모드 — 2026-09-03 승격): 귀속 red(exit 2)·형식 red(exit 3 — 문법·블록 부재·블록 공허·add 충돌·update/remove 대상 기준선 부재 전부)는 architect **반송 의무**이며, red 인 최종본은 G1/G1′ 배너·무배너 재승인·Phase 2 슬라이스 dispatch 어느 것의 근거도 될 수 없다(`--base` 재발화의 red 도 같다 — G2 앵커 차분은 기실현 실물의 판정자이지 계획 red 의 대체가 아니다). 예보가 red 가 아닐 때(exit 0·4·5)만 배너를 제시하고, **배너(G1/G1′)의 근거는 언제나 `scripts/design_pregate.py <산출물 폴더>/design-spec.md . --check-report <산출물 폴더>/pregate-report.md` 의 exit 0 이다**(마지막 예보 절의 블록 해시 = 최종본 해시 ∧ 판정 비형식red ∧ red 면 예보 항목 전건 처분 기재 — 자기 판정이 아니다 · 낡은 green 은 stale 로 선다). 반송 없이 배너를 내는 유일한 경로는 **귀속 red(exit 2)의 예보 항목 전건**에 `ignored(빚: <legacy-debt 파일:행> · STOP <문서 경로>)` 또는 `filtered(ⓐ S<n> | ⓑ <같은 형태 실코드 경로 · 검사기 exit 0>)` 를 pregate-report 에 위 «처분 행 정형»(산출물 위치 절)으로 기재하고 배너 예보 1행에 `귀속 N건(처분 전건 기재)` 를 병기하는 것뿐이다 — `corrected` 는 이 경로에 없다(corrected 의 증거는 재실행에서의 소멸이라 재실행 결과가 곧 최종본이다 · corrected 행에는 «소멸 run 시각 · 블록 해시 전→후» 를 병기한다). 형식 red 는 안정 ID 가 없으므로 이 경로 자체가 없다. 계약 실존 결손(e-ID)은 «전건» 에 들지 않는다(exit 5 비차단 — 별도 게이트). 개정 수신 후 재실행 시점마다 각 red 의 처분 라벨을 그 red 절 뒤에 append 한다(이전 절의 처분은 재기재 — `--check-report` 는 마지막 절 이후만 읽는다). **라벨의 뜻은 채널별 닫힌 정의다** — **예보 항목(registry 귀속)의 처분 라벨은 `corrected | ignored | filtered`** 다: `corrected` = 개정으로 해소(다음 실행에서의 소멸이 증거) · `ignored` = 실위반으로 인지하되 개정하지 않음(실위반 확인 증거는 G2 귀속 red 해소 트레이스 **또는** legacy-debt 매칭 기록(STOP 병기) 둘 중 하나다 — 이관 빚 수용이 이 라벨이다 · 배너 시점에는 후자만 적법하다 — 전자는 G1 시점에 존재할 수 없다) · `filtered` = pre-gate 도구(스텁·문법·시뮬레이션) 한계 판정 — 이 채널에 `deferred` 는 없다(이연은 ignored+빚 매칭 또는 filtered 다). `filtered` 의 근거 유형은 둘뿐이다: ⓐ 리포트 사각 목록 항목 번호 인용(`S<n>` — 그 항목이 이 red 의 오탐 원인임을 한 줄로 잇는다) ⓑ 같은 형태의 실코드 파일이 해당 검사기에서 exit 0 인 대조 경로. **검사기 소스에서 판정 입력이 경로·폴더·파일 이름의 존재뿐인 구조 규칙**(rule-owner-map 등급 path — 예: #81 BC 직계 · #325 ORM 산출물 위치 · #188 area 1:1 · #318 driven_layer 자식 · #336 중앙 마이그레이션 · #490 트리 밖 경로)은 스텁 내용과 무관하므로 ⓑ 가 성립할 수 없고 filtered 대상이 아니다 — corrected 또는 ignored+빚 매칭이다. 경로와 내용을 함께 보는 규칙(예: #392 factories/ 의 factory_boy 부재)은 ⓑ 근거를 대면 filtered 가 가능하다. **계약 실존 결손(리포트 «계약 실존» 절 · 안정 ID `e-…`)의 처분 라벨은 `corrected | deferred | filtered`** 다(2026-09-03): `corrected` = 대상 실존 확보(다음 실행에서 실존 확인 K 증가·결손 소멸) 또는 경로 오기 정정(대상 기실존) — 행 삭제·소비 철회로 결손이 소멸하면 직전 리포트 대비 «결손 소멸 ∧ 행 수 R 감소»가 그것을 드러내며 처분은 `corrected(철회: <근거>)` 로 근거 병기 의무다(발주자 사안이면 STOP) · `deferred`(선행 대기) = 결손 대상이 상류 레인/후행 슬라이스 소유임을 명세가 명시하고 해소 조건을 병기한다 — 정형 `deferred(<소유 레인|Sn>; until <머지 SHA|Sn>)` 권고 · 증거는 조건 충족 시점 재실행에서의 소멸이다(dirty overlay·기준선 갱신이 자동 반영) · `filtered` = 도구 한계(네임스페이스 레이아웃·`import *`·파싱 불능 등 판정 불능 U 계열 — 근거 병기 의무) — 이 채널에 `ignored` 는 없다(부재는 수용 가능한 위반이 아니라 ImportError 예약이며 G2 귀속·legacy-debt 어느 증거도 성립하지 않는다). 실존 채널은 승격 판정식(P/S/I 표면 ∩ G2 귀속)의 **입력이 아니다** — 결손 건수·처분 분포·도구 오류를 별도 계수로만 보고한다(설계 v4 §8 ⑷). 각 채널의 정의 밖 재량 라벨은 없다 — 같은 도구 한계를 레인마다 다른 라벨로 처분하면 승격 판정식이 오염된다(2026-09-02 관찰 레인 1·2 실측). 결손은 권고다 — 도구가 레인을 세우지 않으며(exit 5 는 비차단), 선행 대기가 발주자 결정 사안이면 기존 STOP 규약(R-0459/R-0460)대로 상신한다. **예보는 Phase 0 빚 스캔과 Phase 2 step 6(G2 registry 게이트)의 실행·증거 요구를 어떤 형태로도 대체·축약하지 않는다** — 예보의 기준선은 «스텁 제외 현재 상태»라 `build_anchor` 를 읽지도 쓰지도 않으며, HEAD 판형 게이트 결과를 G2 증거로 유용하는 것은 차분 세탁으로 금지다. **계약 실존 채널도 G0 선행 조건 확인·상류 머지 판단(발주자 소관)을 대체하지 않는다 — 하드 검사가 아니다**(2026-09-03). green 의 뜻은 «설계 검증됨»이 아니라 «P/S/I급 결정 계약 위반 예보 0»이다(사각 목록·미시뮬레이션 목록은 리포트가 상시 병기한다). **machine 블록 부재 skip 금지**: file-plan 기계 블록 부재로 실행을 건너뛰지 않는다 — 부재는 형식 red(exit 3 «블록 부재»)이고 file-plan 0행(빈 펜스·주석뿐)도 형식 red(«블록 공허»)이며 반송은 위 형식 red 조항을 따른다(캐시 skip(아래 판형 ①)·실체화 0 skip(exit 4 — 공허 차분 가드)과 구별). 신규·개정·구형 명세를 가리지 않는다 — 구형 명세(형식 규범 이전 승인)는 개정 시점에 블록을 소급 작성한다(기준선 실존 경로는 `update` · 부재 경로만 `add`). *왜* — 승인 명세가 registry 결정 계약과 조인되지 않은 채 동결되면 그 위반은 G1 이후 반송(레인당 평균 ≈34분)으로야 드러난다: 같은 판정 의미론을 승인 전에 결정적으로 돌리면 그 손실이 배너의 예보 1행으로 당겨진다.
-
-**pre-gate 캐시 skip·재발화 판형**(2026-09-03): ① **캐시 skip** — 위 «기계가독 블록 해시가 불변이면 재실행을 skip 한다»의 해시는 실행기의 `scripts/design_pregate.py <산출물 폴더>/design-spec.md . --block-hash` 값(기계 블록 4종 + 영구 테스트 입장 표를 파서와 같은 추출로 이어 붙인 sha256[:12] — 출력 전용·판정 무접촉·git 0회)이고, 매 실행 리포트 헤더가 같은 값을 `블록 해시 <값>` 으로 병기한다. skip 조건은 **`--block-hash` 값이 직전 실행 리포트 헤더의 값과 동일**할 때뿐이며, skip 마다 pregate-report.md 말미에 1행 `- pre-gate skip — 블록 해시 <값> 불변 · 기준선 <sha12> · 재실행 생략 <UTC> · 직전 예보 <UTC>` 를 append 한다(기록 의무 — 이 행은 `## pre-gate 예보` 문자열을 쓰지 않는다). 값이 다르면 skip 불가이고, skip 행 없는 미실행은 규범 위반이다(«skip 행 부재 ∧ 해시 변동»으로 관측한다). ② **Phase 2 진입 후 재발화 판형** — 반송·STOP 으로 design-spec 이 개정돼 재실행할 때는 `--base <G1 승인 시점 기준선 SHA>` 를 명시한다(값은 G1 배너 직전 최종 실행의 pregate-report 헤더 «기준선 SHA» — `build_anchor` 는 읽지 않는다(R-3434)). 미커밋 WIP 는 커밋 또는 stash 후 실행한다. 실행기는 `--base` 명시 시(명시 `--base HEAD` 포함) 기준선 트리에 없던 계획 add 가 오버레이에 실존하면 «기실현 add»로 already-built 에 기록하고 사본에서 스텁으로 대체해 예보하며(실물 판정 혼입 0), 기준선 트리에 있는 add 는 여전히 형식 red(add 충돌 — 계획↔실물 모순)다. 재발화의 red 는 계획 red 로서 반송 사유이고(위 문단 — 차단 모드), 기실현 실물이 스텁과 다른 위반의 판정자만 G2 앵커 차분이다(사각 S7). ③ **Phase 2 최신성**(2026-09-03 차단 승격) — Phase 2 중 design-spec 변경(G1′ 반송·Contract mismatch 반송·수정 모드 개정 — 수정 모드 절)은 슬라이스 dispatch 전 ②의 `--base` 재발화가 선행한다. G2 배너 직전에는 `scripts/design_pregate.py <산출물 폴더>/design-spec.md . --check-report <산출물 폴더>/pregate-report.md` 의 exit 0(마지막 예보 절의 블록 해시 = 최종 명세 해시 ∧ 판정 비형식red ∧ red 면 예보 항목 전건 처분 기재)을 얻는다 — 다르면(stale) 재발화 후 G2 다 · skip 행·처분 절의 문자열은 대조 대상이 아니다. **한정**: 이 레인 산출물 폴더에 pregate-report 가 없고 design-spec 에 machine 블록도 없고 이 세션에서 design-spec 변경이 0 이면(형식 규범 이전 승인 명세의 순수 구현 수정) 최신성 행은 `미실행(구형 명세 · 변경 0)` 이고 `--check-report` 를 부르지 않는다 — 블록이 있는 명세는 이 한정에 들지 않는다(초안 수신 트리거로 리포트가 반드시 있다).
+**pre-gate — 설계 명세 결정적 예보(차단 모드)**: `design-spec.md` 내용이 바뀔 때마다 실행한다 — architect 초안 수신 직후(위 2의 리뷰 다발과 병렬 1회 — 조기 신호), 리뷰 반영·개정 수신마다, 그리고 **G1/G1′ 배너 제시 직전 최종본과 G1 override(②/③) 반영 후 Phase 2 dispatch 전에는 무조건**(배너의 예보 1행은 항상 최종본에 대한 것 — 낡은 green 금지). 실행 판형은 `scripts/design_pregate.py <산출물 폴더>/design-spec.md . --report <산출물 폴더>/pregate-report.md` 다(`scripts/…` 는 registry 게이트와 같은 규약 — 스킬 폴더의 절대 경로로 펴고 cwd 는 타깃 프로젝트 루트다 · 기계가독 블록 해시가 불변이면 재실행을 skip 한다 — 캐시가 직렬 비용을 없앤다). 팬텀 스텁·git 호출은 전부 스크립트가 격리 사본(저장소 트리 밖) 위에서 수행하는 **결정적 투영물**이라 «구현 코드는 직접 쓰지 않는다» 경계와 충돌하지 않는다 — 너는 이 절차를 위해 bare git 을 직접 치지 않는다. 이 실행은 **게이트다**(차단 모드 — 2026-09-03 승격): 귀속 red(exit 2)·형식 red(exit 3 — 문법·블록 부재·블록 공허·add 충돌·update/remove 대상 기준선 부재 전부)는 architect **반송 의무**이며, red 인 최종본은 G1/G1′ 배너·무배너 재승인·Phase 2 슬라이스 dispatch 어느 것의 근거도 될 수 없다(`--base` 재발화의 red 도 같다 — G2 앵커 차분은 기실현 실물의 판정자이지 계획 red 의 대체가 아니다). 예보가 red 가 아닐 때(exit 0·4·5)만 배너를 제시하고, **배너(G1/G1′)의 근거는 언제나 `scripts/design_pregate.py <산출물 폴더>/design-spec.md . --check-report <산출물 폴더>/pregate-report.md` 의 exit 0 이다**(마지막 예보 절의 블록 해시 = 최종본 해시 ∧ 판정 비형식red ∧ red 면 예보 항목 전건 처분 기재 — 자기 판정이 아니다 · 낡은 green 은 stale 로 선다). 반송 없이 배너를 내는 유일한 경로는 **귀속 red(exit 2)의 예보 항목 전건**에 `ignored(빚: <legacy-debt 파일:행> · STOP <문서 경로>)` 또는 `filtered(ⓐ S<n> | ⓑ <같은 형태 실코드 경로 · 검사기 exit 0>)` 를 pregate-report 에 위 «처분 행 정형»(산출물 위치 절)으로 기재하고 배너 예보 1행에 `귀속 N건(처분 전건 기재)` 를 병기하는 것뿐이다 — `corrected` 는 이 경로에 없다(corrected 의 증거는 재실행에서의 소멸이라 재실행 결과가 곧 최종본이다 · corrected 행에는 «소멸 run 시각 · 블록 해시 전→후» 를 병기한다). 형식 red 는 안정 ID 가 없으므로 이 경로 자체가 없다. 계약 실존 결손(e-ID)은 «전건» 에 들지 않는다(exit 5 비차단 — 별도 게이트). 개정 수신 후 재실행 시점마다 각 red 의 처분 라벨을 그 red 절 뒤에 append 한다(이전 절의 처분은 재기재 — `--check-report` 는 마지막 절 이후만 읽는다). **라벨의 뜻은 채널별 닫힌 정의다** — **예보 항목(registry 귀속·선언 확정)의 처분 라벨은 `corrected | ignored | filtered`** 다: `corrected` = 개정으로 해소(다음 실행에서의 소멸이 증거) · `ignored` = 실위반으로 인지하되 개정하지 않음(실위반 확인 증거는 G2 귀속 red 해소 트레이스 **또는** legacy-debt 매칭 기록(STOP 병기) 둘 중 하나다 — 이관 빚 수용이 이 라벨이다 · 배너 시점에는 후자만 적법하다 — 전자는 G1 시점에 존재할 수 없다) · `filtered` = pre-gate 도구(스텁·문법·시뮬레이션) 한계 판정 — 이 채널에 `deferred` 는 없다(이연은 ignored+빚 매칭 또는 filtered 다). `filtered` 의 근거 유형은 둘뿐이다: ⓐ 리포트 사각 목록 항목 번호 인용(`S<n>` — 그 항목이 이 red 의 오탐 원인임을 한 줄로 잇는다) ⓑ 같은 형태의 실코드 파일이 해당 검사기에서 exit 0 인 대조 경로. **검사기 소스에서 판정 입력이 경로·폴더·파일 이름의 존재뿐인 구조 규칙**(rule-owner-map 등급 path — 예: #81 BC 직계 · #325 ORM 산출물 위치 · #188 area 1:1 · #318 driven_layer 자식 · #336 중앙 마이그레이션 · #490 트리 밖 경로)은 스텁 내용과 무관하므로 ⓑ 가 성립할 수 없고 filtered 대상이 아니다 — corrected 또는 ignored+빚 매칭이다. 경로와 내용을 함께 보는 규칙(예: #392 factories/ 의 factory_boy 부재)은 ⓑ 근거를 대면 filtered 가 가능하다. **계약 실존 결손(리포트 «계약 실존» 절 · 안정 ID `e-…`)의 처분 라벨은 `corrected | deferred | filtered`** 다(2026-09-03): `corrected` = 대상 실존 확보(다음 실행에서 실존 확인 K 증가·결손 소멸) 또는 경로 오기 정정(대상 기실존) — 행 삭제·소비 철회로 결손이 소멸하면 직전 리포트 대비 «결손 소멸 ∧ 행 수 R 감소»가 그것을 드러내며 처분은 `corrected(철회: <근거>)` 로 근거 병기 의무다(발주자 사안이면 STOP) · `deferred`(선행 대기) = 결손 대상이 상류 레인/후행 슬라이스 소유임을 명세가 명시하고 해소 조건을 병기한다 — 정형 `deferred(<소유 레인|Sn>; until <머지 SHA|Sn>)` 권고 · 증거는 조건 충족 시점 재실행에서의 소멸이다(dirty overlay·기준선 갱신이 자동 반영) · `filtered` = 도구 한계(네임스페이스 레이아웃·`import *`·파싱 불능 등 판정 불능 U 계열 — 근거 병기 의무) — 이 채널에 `ignored` 는 없다(부재는 수용 가능한 위반이 아니라 ImportError 예약이며 G2 귀속·legacy-debt 어느 증거도 성립하지 않는다). 실존 채널은 승격 판정식(P/S/I 표면 ∩ G2 귀속)의 **입력이 아니다** — 결손 건수·처분 분포·도구 오류를 별도 계수로만 보고한다(설계 v4 §8 ⑷). 각 채널의 정의 밖 재량 라벨은 없다 — 같은 도구 한계를 레인마다 다른 라벨로 처분하면 승격 판정식이 오염된다(2026-09-02 관찰 레인 1·2 실측). 결손은 권고다 — 도구가 레인을 세우지 않으며(exit 5 는 비차단), 선행 대기가 발주자 결정 사안이면 기존 STOP 규약(R-0459/R-0460)대로 상신한다. **예보는 Phase 0 빚 스캔과 Phase 2 step 6(G2 registry 게이트)의 실행·증거 요구를 어떤 형태로도 대체·축약하지 않는다** — 예보의 기준선은 «스텁 제외 현재 상태»라 `build_anchor` 를 읽지도 쓰지도 않으며, HEAD 판형 게이트 결과를 G2 증거로 유용하는 것은 차분 세탁으로 금지다. **계약 실존 채널도 G0 선행 조건 확인·상류 머지 판단(발주자 소관)을 대체하지 않는다 — 하드 검사가 아니다**(2026-09-03). 선언 검증은 실체화 0에서도 수행한다. 선언 확정은 귀속 red와 같은 전건 처분 의무/exit 2이고, 선언 후보와 생성 본문 S1 미검증은 별도 비차단 보고다. S1은 생성 위치·원본 record·정확한 슬롯 결합이 증명된 #376(after_commit 메서드)/#645/#647에 한하며 #566·bare Any·기존 실코드·미결합 진단은 유지한다. 명시 효과와 출처 결합 DTO의 지원 밖은 S2, 물리 import 전사 밖은 S3, update의 기존 본문 및 지원 밖 후상태는 S5로 남는다. green 의 뜻은 «설계 검증됨»이 아니라 «P/S/I급 결정 계약 위반 및 선언 확정 예보 0»이다(사각 목록·미시뮬레이션 목록은 리포트가 상시 병기한다). **machine 블록 부재 skip 금지**: file-plan 기계 블록 부재로 실행을 건너뛰지 않는다 — 부재는 형식 red(exit 3 «블록 부재»)이고 file-plan 0행(빈 펜스·주석뿐)도 형식 red(«블록 공허»)이며 반송은 위 형식 red 조항을 따른다(캐시 skip(아래 판형 ①)·실체화 0 skip(exit 4 — 선언 확정·실존 결손 없는 공허 차분 가드)과 구별). 신규·개정·구형 명세를 가리지 않는다 — 구형 명세(형식 규범 이전 승인)는 개정 시점에 블록을 소급 작성한다(기준선 실존 경로는 `update` · 부재 경로만 `add`). *왜* — 승인 명세가 registry 결정 계약과 조인되지 않은 채 동결되면 그 위반은 G1 이후 반송(레인당 평균 ≈34분)으로야 드러난다: 같은 판정 의미론을 승인 전에 결정적으로 돌리면 그 손실이 배너의 예보 1행으로 당겨진다.
+
+**pre-gate 캐시 skip·재발화 판형**(2026-09-03): ① **캐시 skip** — 위 «기계가독 블록 해시가 불변이면 재실행을 skip 한다»의 해시는 실행기의 `scripts/design_pregate.py <산출물 폴더>/design-spec.md . --block-hash` 값(기계 블록 4종 + 영구 테스트 입장 표, 선택형 use-case-effects를 파서와 같은 추출로 이어 붙인 sha256[:12] — 효과 블록이 없으면 기존 해시 알고리즘을 유지하고, 있으면 효과 마커와 원문을 마지막에 추가 — 출력 전용·판정 무접촉·git 0회)이고, 매 실행 리포트 헤더가 같은 값을 `블록 해시 <값>` 으로 병기한다. skip 조건은 **`--block-hash` 값이 직전 실행 리포트 헤더의 값과 동일**할 때뿐이며, skip 마다 pregate-report.md 말미에 1행 `- pre-gate skip — 블록 해시 <값> 불변 · 기준선 <sha12> · 재실행 생략 <UTC> · 직전 예보 <UTC>` 를 append 한다(기록 의무 — 이 행은 `## pre-gate 예보` 문자열을 쓰지 않는다). 값이 다르면 skip 불가이고, skip 행 없는 미실행은 규범 위반이다(«skip 행 부재 ∧ 해시 변동»으로 관측한다). ② **Phase 2 진입 후 재발화 판형** — 반송·STOP 으로 design-spec 이 개정돼 재실행할 때는 `--base <G1 승인 시점 기준선 SHA>` 를 명시한다(값은 G1 배너 직전 최종 실행의 pregate-report 헤더 «기준선 SHA» — `build_anchor` 는 읽지 않는다(R-3434)). 미커밋 WIP 는 커밋 또는 stash 후 실행한다. 실행기는 `--base` 명시 시(명시 `--base HEAD` 포함) 기준선 트리에 없던 계획 add 가 오버레이에 실존하면 «기실현 add»로 already-built 에 기록하고 사본에서 스텁으로 대체해 예보하며(실물 판정 혼입 0), 기준선 트리에 있는 add 는 여전히 형식 red(add 충돌 — 계획↔실물 모순)다. 재발화의 red 는 계획 red 로서 반송 사유이고(위 문단 — 차단 모드), 기실현 실물이 스텁과 다른 위반의 판정자만 G2 앵커 차분이다(사각 S7). ③ **Phase 2 최신성**(2026-09-03 차단 승격) — Phase 2 중 design-spec 변경(G1′ 반송·Contract mismatch 반송·수정 모드 개정 — 수정 모드 절)은 슬라이스 dispatch 전 ②의 `--base` 재발화가 선행한다. G2 배너 직전에는 `scripts/design_pregate.py <산출물 폴더>/design-spec.md . --check-report <산출물 폴더>/pregate-report.md` 의 exit 0(마지막 예보 절의 블록 해시 = 최종 명세 해시 ∧ 판정 비형식red ∧ red 면 예보 항목 전건 처분 기재)을 얻는다 — 다르면(stale) 재발화 후 G2 다 · skip 행·처분 절의 문자열은 대조 대상이 아니다. **한정**: 이 레인 산출물 폴더에 pregate-report 가 없고 design-spec 에 machine 블록도 없고 이 세션에서 design-spec 변경이 0 이면(형식 규범 이전 승인 명세의 순수 구현 수정) 최신성 행은 `미실행(구형 명세 · 변경 0)` 이고 `--check-report` 를 부르지 않는다 — 블록이 있는 명세는 이 한정에 들지 않는다(초안 수신 트리거로 리포트가 반드시 있다).
 
 ## Phase 2 — 구현 (G2, 이중 루프 TDD)
 <!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->
 
 1. **입장 결정과 조건부 테스트 러너 준비** — 승인된 입장 표를 먼저 읽는다. 새 영구 테스트 artifact가 필요한 `add/update` 행이 하나 이상 있을 때만 pytest 가용성을 확인하고, 그때 설정이 없으면 `implementation-django-ninja` §2.1 버전-핀 규율로 Tier-1(pytest·pytest-django·pytest-mock·factory_boy)을 설치한 뒤 루트 `[tool.pytest.ini_options]`에 프로젝트의 실제 `DJANGO_SETTINGS_MODULE`(manage.py/env에서 감지)을 기록한다. `reuse`는 확립된 기존 러너로 지정 anchor만 실행하며 dependency·manifest·runner config를 바꾸지 않는다. 일반 `retain`, `reject`, `remove`만 있는 변경도 runner setup write를 만들지 않는다. 기존 `TestCase` 스위트를 pytest 관용구로 재작성하지 않으며, 승인된 `add/update`로 새 테스트를 쓸 때만 pytest 관용구를 사용한다.
 2. 승인된 입장 표와 변경 URL·public symbol/use case·event/model/constraint명을 앵커로 **관련 테스트만 한정 검색**해 `existing authoritative coverage`를 확인한다. decision을 다시 만들지 말고 다음대로 dispatch한다: `add/update`만 새·변경 Red와 test edit, `reuse`는 지정 기존 anchor 실행만 하고 artifact write 0, 일반 `retain`은 무편집, `remove`는 승인된 exact target만 원 소유자에게, `reject`는 test 역할 dispatch 0, `pending`은 G1/G1′ 반송이다. 명시 승인된 의미 보존 `retain` 재조직만 새 case·assertion·Red 없이 같은 보호를 전후 기록한다. 외부 HTTP/event/user-observable/public contract 소유 행은 `dddjango:acceptance-tester`, domain/application/DB/adapter 소유 행은 `dddjango:coder`에 준다. 전체 suite를 discovery 대용으로 쓰지 않는다.
 3. 제품 구현 단위로 **슬라이스 목록을 도출**하고 각 슬라이스에 관련 입장 행을 붙인다. G0에서 「지금 정리」로 결정된 빚(`refactor-scope.md`)은 **리팩터링 슬라이스(슬라이스 0 · 동작 불변)**로 만들어 신규 개발 슬라이스보다 **앞에** 둔다 — 리팩터링과 기능 변경을 한 슬라이스에 섞지 않는다. 후보·recipe·coverage 목표만으로 test-adjustment/unit-Red 슬라이스를 만들지 않는다. 외부 `add/update` Red와 내부 `add/update` Red, 승인된 `remove` 대상만 해당 소유자의 test edit 입력이며, `reuse` anchor는 새 슬라이스 수를 압박하지 않는다.
 4. 슬라이스마다 `dddjango:coder`를 호출한다 — 입력: 승인 명세·패키지 구조·관련 입장 행·acceptance 결과(있으면)·이번 제품 구현 슬라이스·플러그인 설치 루트 절대 경로(검사기 확장-리터럴 호출용 · 2026-08-15). coder는 자기 소유의 `add/update`만 단위 Red→Green→Refactor로 편집하고, `remove`는 exact target만 제거한다. `reuse/reject`에서 내부 test write를 만들거나 외부 계약 테스트를 수정하지 않는다. 이번 실행이 Red를 위해 만든 loader/dynamic import guard/대체 decorator/skip/xfail/helper는 만든 동일 역할을 첫 Green 직후 다시 호출해 즉시 제거하며, 작업 전 기존 비계를 임의 삭제하지 않는다.
    - 슬라이스가 **3개 이상**이면 슬라이스마다 `dddjango:discipline-reviewer`를 **Phase 2 implementation 모드**의 해당 슬라이스 범위로 호출해 경량 감사하고 coder에 반영시킨다. 마지막 슬라이스는 홀리스틱 감사로 갈음할 수 있되 갈음은 조건부다(2026-08-17) — 홀리스틱 호출 입력에 «S_n 전용 경량 감사 생략 — S_n 범위 전량 실독 필수»를 명시하고, 홀리스틱 리포트가 전량 실독을 확인해야 갈음이 성립한다. 마지막 홀리스틱 1회는 갈음 여부와 무관하게 존치한다. 마지막이 아닌 슬라이스의 경량 감사 발견(blocker·important)은 다음 게이트 전에 원작성자 반송으로 반영을 완료한다(완료 = 원작성자의 처리 보고 수신 — 외부 계약 테스트 소유 발견이면 acceptance-tester가 원작성자다). 감사 대상 범위와 다음 슬라이스 작업 파일이 겹치면 감사 완료 후 배차한다(«같은 파일 병렬 편집 금지»의 적용) — 겹치지 않으면 병렬 배차 가능. Phase 2 시작 한 줄 상태에 슬라이스 목록·개수를 명시한다.
 5. **규율 감사**: `dddjango:discipline-reviewer`를 **Phase 2 implementation 모드**로 호출한다 — 필수 입력은 코드+테스트, 승인 입장 표, 역할별 최소 조정 보고, test diff·실행 결과와 슬라이스 목록이다. 감사 호출 입력에 `check-layer-skeleton`(registry #4)의 ⓓ 후보 채널 출력(행위 칸 200행 초과 신호·페이로드)과 `check-public-surface-annotation`(registry #11)의 ⓓ 후보(#645 — 변수·제네릭 안의 명시 `Any` · #647 — 입구 매개변수·즉시 검증 지역 변수의 `dict/Mapping[…, object]` 와 반환 주석의 자리표시 `object` · #650 — `json.load(s)` 결과의 무검증 흐름)를 동봉한다 — 두 채널 모두 동봉 범위는 registry_gate 가 앵커 차분으로 가른 **«ⓓ 신규(N′∖L′)»** 절·sidecar 레코드이고, 앵커에도 있던 «ⓓ legacy» 는 게이트 보고의 건수로만 적는다. 기본은 G2 직전 1회, 슬라이스 ≥3이면 슬라이스별 경량 감사(마지막은 조건부 홀리스틱 갈음 가능) + 마지막 홀리스틱 1회다. reviewer는 각 test diff hunk를 decision과 unique production failure에 대조하고, `reuse/reject` write 0, 일반 `retain` 무편집, `remove/weaken` 종료 근거·exact target, 의미 보존 재조직의 전후 보호, 첫-Green 비계 잔존을 감사한다. 기존 migration lifecycle과 관련 테스트 보존 규칙도 그대로 감사한다. 외부 assertion 지적은 acceptance-tester, 내부 assertion과 일반 구현 지적은 coder, 입장/설계 오류는 design-architect를 거쳐 G1/G1′으로 반송한다(반송으로 `design-spec.md` 가 개정되면 **재승인 전에 Phase 1 pre-gate 를 재실행**하고 예보 1행을 재승인 배너에 병기한다 — Phase 1 pre-gate 문단 · Phase 2 중이면 재발화 판형: `--base <G1 기준선 SHA>` 명시·WIP 커밋/stash).

```

## codex-dddjango/skills/dddjango/SKILL.md

Before SHA256: f550ca8f589f6487a0fd1b5235389fc413edac8ffbebe53792ebad4509f108ff
After SHA256: 231ee7dae528430291e0b2ad695f03e731655c88170cc06773584edfab758a41

```diff
--- before/codex-dddjango/skills/dddjango/SKILL.md
+++ after/codex-dddjango/skills/dddjango/SKILL.md
@@ -104,23 +104,23 @@
 
 1. `spawn_agent`로 **design-architect**를 띄운다 — 지시: "역할 스킬 `dddjango-design-architect`를 로드해 그 역할로 작동하라. 입력: 스코프 메모 · 활성 lens 목록 · 설계 명세 저장 경로." architect는 기존 프로젝트 구조를 조사해 **패키지·테스트 구조 결정**과 모든 영구 test artifact `add/update/move/split/rename/remove/weaken` 후보의 최소 입장 표(`candidate | protected contract/evidence | unique production failure | existing authoritative coverage | decision | owner/path`)를 명세에 포함한다. decision은 `add/update/reuse/retain/remove/reject/pending` 일곱 값만 쓴다. `wait_agent`로 통합 설계 명세 1건을 받는다.
 2. 활성 lens별 리뷰어를 **병렬로** 띄운다: 활성 lens마다 `spawn_agent`로 `dddjango-design-review-ddd` / `dddjango-design-review-api` / `dddjango-design-review-db`(활성 lens만). **병렬의 정의는 «전부 spawn 을 먼저, wait 는 그 뒤»다(2026-08-13)** — 리뷰어 전부(아래 3의 discipline lightweight 포함)를 연속 `spawn_agent`로 먼저 띄운 다음에야 `wait_agent` 수집을 시작한다. 하나를 spawn→wait 로 끝내고 다음을 띄우는 순차는 병렬이 아니다(라운드 2′ 실측: 양 레인 모두 직렬 dispatch — Phase 1 벽시계 낭비의 최대 항목). 모든 리뷰어는 타 노트를 받지 않으므로 순서 의존이 없다(편향 방지 원칙이 병렬을 지지한다). 단 **입력 준비가 다발보다 앞이다** — Error response contract scope 면 discipline 에 줄 project-wide tree·inventory 를 먼저 구성해 동봉한다(다발을 서두르느라 필수 입력을 비우지 않는다). 이 정의는 리뷰어를 **둘 이상 부르는 모든 호출**(재작업 재리뷰 포함)에 적용하고, 하나만 다시 부르는 재호출은 단독 호출이 정당하다. 다발에서 리뷰어를 누락했으면 늦은 단독 호출로라도 반드시 호출하고 병렬 미준수 사실을 보고한다 — 금지의 주어는 «계획된 순차»이지 «누락의 교정»이 아니다. G1 배너에 다발 크기 한 줄(예: `리뷰 다발 4종 1회`)을 남긴다. 각 리뷰어에는 architect의 명세 초안만 준다(타 리뷰 노트·코드는 주지 않는다 — 편향 방지). API/DB reviewer는 자기 lens의 candidate·위험을 제안하고 각 관련 행의 evidence·독자 failure·중복을 감사하되 decision 없이 테스트를 의무화하지 않는다. 모든 리뷰어(아래 3 의 discipline 포함)를 `wait_agent`로 수집한 뒤 `close_agent`로 슬롯을 정리한다. 산출: lens별 리뷰 노트. 노트 수신 시 형식을 구문 검사한다 — 집행성 판정 1행, ddd 노트는 판정-소유 대조 표(또는 «판정 없음» 1행)가 없으면 그 리뷰어에게 반송한다(원문 대조는 하지 않는다 — 존재 검사만 · 2026-08-17).
 3. `dddjango-discipline-reviewer`를 **Phase 1 lightweight 모드**로 항상 띄워(위 2의 병렬 spawn 다발에 합류 — 별도 순차 호출 금지) 입장 표의 열·일곱 decision·protected contract·독자 failure·기존 coverage·owner를 독립 감사시킨다. `pending`, framework/private mechanics의 부당한 `add`, 의미 보존 재조직의 새 case/assertion/Red를 G1 전에 잡는다. Error response contract scope에서는 current project-wide tree도 함께 주어 기존 12-slot surface inventory와 물리 소유권·우회까지 추가 점검한다. 구현 코드·테스트 diff·실행 결과·슬라이스는 요구하지 않는다.
 4. `spawn_agent`로 **design-architect**를 다시 띄워 리뷰 노트를 반영하고 리뷰어 간 충돌을 중재시킨다. **scope.md가 "범위 아님 / 필요 시 G1 제안"으로 명시한 항목(Y)은 architect가 기본(미적용)을 명세에 현재-상태로 commit하고 배너 override 항목으로 산출**한다(architect가 'Y감이냐'를 판정하지 않고 scope.md의 그 목록을 앵커로 쓴다). 스스로 해소 못 하는 트레이드오프(양자택일·리뷰어 충돌 등 Z)만 미해결 옵션으로 남긴다.
 5. **G1 배너**로 최종 설계 명세(경로)를 제시하고 승인받는다 — Y 항목은 "기본=미적용 · 추가할래?"로, Z는 옵션으로 보인다. 배너에는 입장 표의 `add/update/reuse/retain/remove/reject/pending`을 decision별로 직접 나열하고 각 행의 owner/path를 보여 준다(없으면 `없음`). `pending`이 하나라도 남으면 승인 입력을 Phase 2 진입으로 해석하지 않고 한정된 설계 질문으로 반송한다. 의미 보존 move/split/rename/reorganization은 새 case·assertion·Red가 없고 전후 보호가 같다는 기록까지 보여 준다. 설계 명세는 이후 테스트와 코드의 **단일 근거**다.
    - **G1 결정 처리**(승인 후): ① **기본 수락** → `design-architect`를 다시 띄우지 않고 Phase 2로 진행한다(명세가 이미 단일 근거라 잠금 재호출 불요). ② **Y 항목 채택(override)** → *너(코디네이터)*가 `scope.md`를 갱신한다(그 항목을 "범위 아님"에서 `<항목>: G1 채택 (사용자 승인)` 형태의 *단독 줄*로 옮긴다 — `아님`·`않는다` 등 부정 토큰을 같은 줄에 두지 않는다) + `spawn_agent`로 `design-architect`를 **G1 override 입력**(Phase 1 입력 형식)으로 다시 띄워 해당 절만 반영시킨다. ③ **Z 옵션 결정·override** → `spawn_agent`로 `design-architect`를 G1 override 입력으로 다시 띄운다. ②·③도 override 반영이 끝나면 ①과 동일하게 Phase 2로 진행한다(분기는 결정을 반영하는 절차만 가르고 후속 단계는 같다 — 단 **dispatch 전에 pre-gate 를 무조건 재실행**한다: 무배너 경로라 예보 착지는 Phase 2 진입 한 줄 상태 + pregate-report 다 · 아래 pre-gate 문단). **너는 `design-spec.md`를 직접 쓰지 않는다**(②의 `scope.md` 갱신은 네 소유 파일이라 예외 — `design-spec`은 architect 전속). 이 전속은 경로 불문이다(2026-08-17) — G1 본선·리뷰 반송·G1′(수정 모드)·게이트 승인문이 design-spec 갱신을 명시 지시한 경우를 포함해, 집행은 언제나 `design-architect` 재호출로 위임한다(해당 경로의 확립된 형식으로: override 입력 또는 리뷰/반송 노트 전달 — 재spawn이든 동일 architect 스레드 followup이든 기능 등가다). 승인이 «무엇을» 바꿀지 정해도 «누가» 바꾸는지는 바뀌지 않는다. `scope.md`(네 소유)에는 스코프 결정만 적는다 — 설계 결정·입장표 해석을 그리 옮겨 적거나 역할 지시문에 명세 재해석을 실어 우회하지 않는다. *왜* — 흔한 기본 수락에 architect 재호출(잠금)을 없애 비용·비결정을 줄이고, Y 채택 시 `scope.md` 갱신으로 백스톱 ⑩의 G1-승인 면제가 발화해 "미요청 단정 + 채택 코드"의 거짓 차단을 막는다.
 
 Ninja endpoint/error contract/response Schema가 변경되는 scope에서는 **G1 제시 전과 사용자 승인 응답 뒤 Phase 2 dispatch 직전**에 current `design-spec.md`를 다시 읽는다. `Error response contract 12-slot`의 label과 순서는 정확히 `contract scope`; `scope evidence`; `error profile`; `compatibility/rollout`; `common FrameworkErrorSchema action`; `common FrameworkErrorSchema shape/approval`; `BC error module`; `BC ErrorCode`; `BC ErrorSchema`; `prepared error mapping`; `controller mapping`; `response/OpenAPI/tests`다. 12개 모두 구체적이고 선택 profile에 맞으며 서로 일관돼야 한다. `none | not applicable`은 해당 profile/slot이 허용하고 이유·evidence를 함께 기록한 경우에만 구체값이다. `dddjango-code-json`은 `error-bc`가 비어도 slot 5가 `reuse | create | approved-change`여야 하고 slot 6의 common shape가 필수다. plugin 기본 property 목록은 없으며 기존 프로젝트의 관찰된 exact shape 또는 신규 scope에서 별도로 승인된 exact shape를 그대로 사용한다. slot 9의 BC base가 slot 6의 식별자 field를 `<Bc>ErrorCode`로 좁히면서 공통의 default를 잃어 required가 되는 것은 canon이다(식별자 field 한정·ErrorCode 좁힘 동반일 때만 — 2026-08-15). 이때 slots 7–9는 public BC error 부재 이유와 함께 `none`일 수 있지만, slots 10–12는 승인된 empty mapping/runtime/OpenAPI inventory와 검증을 명시해 공백으로 넘기지 않는다. `preserve-established`의 slots 5–12는 관찰된 profile-native artifact/behavior 또는 evidence가 있는 `none | not applicable`이어야 하며 code-profile Enum·base·direct-`Status`를 강제하지 않는다. 누락·모호·모순이면 승인 입력이 있어도 Phase 2로 가지 않고 G1/G1′ 설계로 반송한다. Coordinator는 slot 값을 대신 결정하거나 조용히 보충·수정하지 않는다. `dddjango-code-json`에서 현재 common shape와 승인 shape가 다른데 `common FrameworkErrorSchema action=approved-change`와 **별도로 표면화해 받은 명시적 사용자 승인 evidence**가 함께 없으면 G1을 차단한다. 설계 전체에 대한 일반 G1 승인은 shape 변경 승인을 대신하지 않는다. 신규 scope의 최초 shape도 exact field/type/required/default/nullability/모든 `Field` metadata/model config·legacy `Config`/validator/serializer/computed field/Pydantic hook inventory와 effective semantics/wire 직렬화 결과와 각 field 의미를 보여 준 별도 명시 승인 없이는 생성하지 않는다. 재작업으로 profile·compatibility·wire 또는 그 밖의 API semantic slot이 바뀌면 API reviewer를 다시 호출하고, 물리 구조·소유권·controller mapping 결정이 바뀌면 discipline reviewer를 다시 호출해 반영한 뒤 새 G1을 제시한다.
 
-**pre-gate — 설계 명세 결정적 예보(차단 모드)**: `design-spec.md` 내용이 바뀔 때마다 실행한다 — architect 초안 수신 직후(위 2의 리뷰어 spawn 다발을 **전부 띄운 뒤 wait 수집 전에** shell 로 1회 — 조기 신호·codex 병렬 정의와 정합), 리뷰 반영·개정 수신마다, 그리고 **G1/G1′ 배너 제시 직전 최종본과 G1 override(②/③) 반영 후 Phase 2 dispatch 전에는 무조건**(배너의 예보 1행은 항상 최종본에 대한 것 — 낡은 green 금지). 실행 판형은 `scripts/design_pregate.py <산출물 폴더>/design-spec.md . --report <산출물 폴더>/pregate-report.md` 다(`scripts/…` 는 registry 게이트와 같은 규약 — 이 스킬 폴더의 절대 경로로 펴고 cwd 는 타깃 프로젝트 루트다 · 기계가독 블록 해시가 불변이면 재실행을 skip 한다 — 캐시가 직렬 비용을 없앤다). 팬텀 스텁·git 호출은 전부 스크립트가 격리 사본(저장소 트리 밖) 위에서 수행하는 **결정적 투영물**이라 «구현 코드는 직접 쓰지 않는다» 경계와 충돌하지 않는다 — 너는 이 절차를 위해 bare git 을 직접 치지 않는다. 이 실행은 **게이트다**(차단 모드 — 2026-09-03 승격): 귀속 red(exit 2)·형식 red(exit 3 — 문법·블록 부재·블록 공허·add 충돌·update/remove 대상 기준선 부재 전부)는 architect **반송 의무**이며, red 인 최종본은 G1/G1′ 배너·무배너 재승인·Phase 2 슬라이스 dispatch 어느 것의 근거도 될 수 없다(`--base` 재발화의 red 도 같다 — G2 앵커 차분은 기실현 실물의 판정자이지 계획 red 의 대체가 아니다). 예보가 red 가 아닐 때(exit 0·4·5)만 배너를 제시하고, **배너(G1/G1′)의 근거는 언제나 `scripts/design_pregate.py <산출물 폴더>/design-spec.md . --check-report <산출물 폴더>/pregate-report.md` 의 exit 0 이다**(마지막 예보 절의 블록 해시 = 최종본 해시 ∧ 판정 비형식red ∧ red 면 예보 항목 전건 처분 기재 — 자기 판정이 아니다 · 낡은 green 은 stale 로 선다). 반송 없이 배너를 내는 유일한 경로는 **귀속 red(exit 2)의 예보 항목 전건**에 `ignored(빚: <legacy-debt 파일:행> · STOP <문서 경로>)` 또는 `filtered(ⓐ S<n> | ⓑ <같은 형태 실코드 경로 · 검사기 exit 0>)` 를 pregate-report 에 위 «처분 행 정형»(산출물 위치 절)으로 기재하고 배너 예보 1행에 `귀속 N건(처분 전건 기재)` 를 병기하는 것뿐이다 — `corrected` 는 이 경로에 없다(corrected 의 증거는 재실행에서의 소멸이라 재실행 결과가 곧 최종본이다 · corrected 행에는 «소멸 run 시각 · 블록 해시 전→후» 를 병기한다). 형식 red 는 안정 ID 가 없으므로 이 경로 자체가 없다. 계약 실존 결손(e-ID)은 «전건» 에 들지 않는다(exit 5 비차단 — 별도 게이트). 개정 수신 후 재실행 시점마다 각 red 의 처분 라벨을 그 red 절 뒤에 append 한다(이전 절의 처분은 재기재 — `--check-report` 는 마지막 절 이후만 읽는다). **라벨의 뜻은 채널별 닫힌 정의다** — **예보 항목(registry 귀속)의 처분 라벨은 `corrected | ignored | filtered`** 다: `corrected` = 개정으로 해소(다음 실행에서의 소멸이 증거) · `ignored` = 실위반으로 인지하되 개정하지 않음(실위반 확인 증거는 G2 귀속 red 해소 트레이스 **또는** legacy-debt 매칭 기록(STOP 병기) 둘 중 하나다 — 이관 빚 수용이 이 라벨이다 · 배너 시점에는 후자만 적법하다 — 전자는 G1 시점에 존재할 수 없다) · `filtered` = pre-gate 도구(스텁·문법·시뮬레이션) 한계 판정 — 이 채널에 `deferred` 는 없다(이연은 ignored+빚 매칭 또는 filtered 다). `filtered` 의 근거 유형은 둘뿐이다: ⓐ 리포트 사각 목록 항목 번호 인용(`S<n>` — 그 항목이 이 red 의 오탐 원인임을 한 줄로 잇는다) ⓑ 같은 형태의 실코드 파일이 해당 검사기에서 exit 0 인 대조 경로. **검사기 소스에서 판정 입력이 경로·폴더·파일 이름의 존재뿐인 구조 규칙**(rule-owner-map 등급 path — 예: #81 BC 직계 · #325 ORM 산출물 위치 · #188 area 1:1 · #318 driven_layer 자식 · #336 중앙 마이그레이션 · #490 트리 밖 경로)은 스텁 내용과 무관하므로 ⓑ 가 성립할 수 없고 filtered 대상이 아니다 — corrected 또는 ignored+빚 매칭이다. 경로와 내용을 함께 보는 규칙(예: #392 factories/ 의 factory_boy 부재)은 ⓑ 근거를 대면 filtered 가 가능하다. **계약 실존 결손(리포트 «계약 실존» 절 · 안정 ID `e-…`)의 처분 라벨은 `corrected | deferred | filtered`** 다(2026-09-03): `corrected` = 대상 실존 확보(다음 실행에서 실존 확인 K 증가·결손 소멸) 또는 경로 오기 정정(대상 기실존) — 행 삭제·소비 철회로 결손이 소멸하면 직전 리포트 대비 «결손 소멸 ∧ 행 수 R 감소»가 그것을 드러내며 처분은 `corrected(철회: <근거>)` 로 근거 병기 의무다(발주자 사안이면 STOP) · `deferred`(선행 대기) = 결손 대상이 상류 레인/후행 슬라이스 소유임을 명세가 명시하고 해소 조건을 병기한다 — 정형 `deferred(<소유 레인|Sn>; until <머지 SHA|Sn>)` 권고 · 증거는 조건 충족 시점 재실행에서의 소멸이다(dirty overlay·기준선 갱신이 자동 반영) · `filtered` = 도구 한계(네임스페이스 레이아웃·`import *`·파싱 불능 등 판정 불능 U 계열 — 근거 병기 의무) — 이 채널에 `ignored` 는 없다(부재는 수용 가능한 위반이 아니라 ImportError 예약이며 G2 귀속·legacy-debt 어느 증거도 성립하지 않는다). 실존 채널은 승격 판정식(P/S/I 표면 ∩ G2 귀속)의 **입력이 아니다** — 결손 건수·처분 분포·도구 오류를 별도 계수로만 보고한다(설계 v4 §8 ⑷). 각 채널의 정의 밖 재량 라벨은 없다 — 같은 도구 한계를 레인마다 다른 라벨로 처분하면 승격 판정식이 오염된다(2026-09-02 관찰 레인 1·2 실측). 결손은 권고다 — 도구가 레인을 세우지 않으며(exit 5 는 비차단), 선행 대기가 발주자 결정 사안이면 기존 STOP 규약(R-0459/R-0460)대로 상신한다. **예보는 Phase 0 빚 스캔과 Phase 2 6번(G2 registry 게이트)의 실행·증거 요구를 어떤 형태로도 대체·축약하지 않는다** — 예보의 기준선은 «스텁 제외 현재 상태»라 `build_anchor` 를 읽지도 쓰지도 않으며, HEAD 판형 게이트 결과를 G2 증거로 유용하는 것은 차분 세탁으로 금지다. **계약 실존 채널도 G0 선행 조건 확인·상류 머지 판단(발주자 소관)을 대체하지 않는다 — 하드 검사가 아니다**(2026-09-03). green 의 뜻은 «설계 검증됨»이 아니라 «P/S/I급 결정 계약 위반 예보 0»이다(사각 목록·미시뮬레이션 목록은 리포트가 상시 병기한다). **machine 블록 부재 skip 금지**: file-plan 기계 블록 부재로 실행을 건너뛰지 않는다 — 부재는 형식 red(exit 3 «블록 부재»)이고 file-plan 0행(빈 펜스·주석뿐)도 형식 red(«블록 공허»)이며 반송은 위 형식 red 조항을 따른다(캐시 skip(아래 판형 ①)·실체화 0 skip(exit 4 — 공허 차분 가드)과 구별). 신규·개정·구형 명세를 가리지 않는다 — 구형 명세(형식 규범 이전 승인)는 개정 시점에 블록을 소급 작성한다(기준선 실존 경로는 `update` · 부재 경로만 `add`). *왜* — 승인 명세가 registry 결정 계약과 조인되지 않은 채 동결되면 그 위반은 G1 이후 반송(레인당 평균 ≈34분)으로야 드러난다: 같은 판정 의미론을 승인 전에 결정적으로 돌리면 그 손실이 배너의 예보 1행으로 당겨진다.
-
-**pre-gate 캐시 skip·재발화 판형**(2026-09-03): ① **캐시 skip** — 위 «기계가독 블록 해시가 불변이면 재실행을 skip 한다»의 해시는 실행기의 `scripts/design_pregate.py <산출물 폴더>/design-spec.md . --block-hash` 값(기계 블록 4종 + 영구 테스트 입장 표를 파서와 같은 추출로 이어 붙인 sha256[:12] — 출력 전용·판정 무접촉·git 0회)이고, 매 실행 리포트 헤더가 같은 값을 `블록 해시 <값>` 으로 병기한다. skip 조건은 **`--block-hash` 값이 직전 실행 리포트 헤더의 값과 동일**할 때뿐이며, skip 마다 pregate-report.md 말미에 1행 `- pre-gate skip — 블록 해시 <값> 불변 · 기준선 <sha12> · 재실행 생략 <UTC> · 직전 예보 <UTC>` 를 append 한다(기록 의무 — 이 행은 `## pre-gate 예보` 문자열을 쓰지 않는다). 값이 다르면 skip 불가이고, skip 행 없는 미실행은 규범 위반이다(«skip 행 부재 ∧ 해시 변동»으로 관측한다). ② **Phase 2 진입 후 재발화 판형** — 반송·STOP 으로 design-spec 이 개정돼 재실행할 때는 `--base <G1 승인 시점 기준선 SHA>` 를 명시한다(값은 G1 배너 직전 최종 실행의 pregate-report 헤더 «기준선 SHA» — `build_anchor` 는 읽지 않는다(R-3434)). 미커밋 WIP 는 커밋 또는 stash 후 실행한다. 실행기는 `--base` 명시 시(명시 `--base HEAD` 포함) 기준선 트리에 없던 계획 add 가 오버레이에 실존하면 «기실현 add»로 already-built 에 기록하고 사본에서 스텁으로 대체해 예보하며(실물 판정 혼입 0), 기준선 트리에 있는 add 는 여전히 형식 red(add 충돌 — 계획↔실물 모순)다. 재발화의 red 는 계획 red 로서 반송 사유이고(위 문단 — 차단 모드), 기실현 실물이 스텁과 다른 위반의 판정자만 G2 앵커 차분이다(사각 S7). ③ **Phase 2 최신성**(2026-09-03 차단 승격) — Phase 2 중 design-spec 변경(G1′ 반송·Contract mismatch 반송·수정 모드 개정 — 수정 모드 절)은 슬라이스 dispatch 전 ②의 `--base` 재발화가 선행한다. G2 배너 직전에는 `scripts/design_pregate.py <산출물 폴더>/design-spec.md . --check-report <산출물 폴더>/pregate-report.md` 의 exit 0(마지막 예보 절의 블록 해시 = 최종 명세 해시 ∧ 판정 비형식red ∧ red 면 예보 항목 전건 처분 기재)을 얻는다 — 다르면(stale) 재발화 후 G2 다 · skip 행·처분 절의 문자열은 대조 대상이 아니다. **한정**: 이 레인 산출물 폴더에 pregate-report 가 없고 design-spec 에 machine 블록도 없고 이 세션에서 design-spec 변경이 0 이면(형식 규범 이전 승인 명세의 순수 구현 수정) 최신성 행은 `미실행(구형 명세 · 변경 0)` 이고 `--check-report` 를 부르지 않는다 — 블록이 있는 명세는 이 한정에 들지 않는다(초안 수신 트리거로 리포트가 반드시 있다).
+**pre-gate — 설계 명세 결정적 예보(차단 모드)**: `design-spec.md` 내용이 바뀔 때마다 실행한다 — architect 초안 수신 직후(위 2의 리뷰어 spawn 다발을 **전부 띄운 뒤 wait 수집 전에** shell 로 1회 — 조기 신호·codex 병렬 정의와 정합), 리뷰 반영·개정 수신마다, 그리고 **G1/G1′ 배너 제시 직전 최종본과 G1 override(②/③) 반영 후 Phase 2 dispatch 전에는 무조건**(배너의 예보 1행은 항상 최종본에 대한 것 — 낡은 green 금지). 실행 판형은 `scripts/design_pregate.py <산출물 폴더>/design-spec.md . --report <산출물 폴더>/pregate-report.md` 다(`scripts/…` 는 registry 게이트와 같은 규약 — 이 스킬 폴더의 절대 경로로 펴고 cwd 는 타깃 프로젝트 루트다 · 기계가독 블록 해시가 불변이면 재실행을 skip 한다 — 캐시가 직렬 비용을 없앤다). 팬텀 스텁·git 호출은 전부 스크립트가 격리 사본(저장소 트리 밖) 위에서 수행하는 **결정적 투영물**이라 «구현 코드는 직접 쓰지 않는다» 경계와 충돌하지 않는다 — 너는 이 절차를 위해 bare git 을 직접 치지 않는다. 이 실행은 **게이트다**(차단 모드 — 2026-09-03 승격): 귀속 red(exit 2)·형식 red(exit 3 — 문법·블록 부재·블록 공허·add 충돌·update/remove 대상 기준선 부재 전부)는 architect **반송 의무**이며, red 인 최종본은 G1/G1′ 배너·무배너 재승인·Phase 2 슬라이스 dispatch 어느 것의 근거도 될 수 없다(`--base` 재발화의 red 도 같다 — G2 앵커 차분은 기실현 실물의 판정자이지 계획 red 의 대체가 아니다). 예보가 red 가 아닐 때(exit 0·4·5)만 배너를 제시하고, **배너(G1/G1′)의 근거는 언제나 `scripts/design_pregate.py <산출물 폴더>/design-spec.md . --check-report <산출물 폴더>/pregate-report.md` 의 exit 0 이다**(마지막 예보 절의 블록 해시 = 최종본 해시 ∧ 판정 비형식red ∧ red 면 예보 항목 전건 처분 기재 — 자기 판정이 아니다 · 낡은 green 은 stale 로 선다). 반송 없이 배너를 내는 유일한 경로는 **귀속 red(exit 2)의 예보 항목 전건**에 `ignored(빚: <legacy-debt 파일:행> · STOP <문서 경로>)` 또는 `filtered(ⓐ S<n> | ⓑ <같은 형태 실코드 경로 · 검사기 exit 0>)` 를 pregate-report 에 위 «처분 행 정형»(산출물 위치 절)으로 기재하고 배너 예보 1행에 `귀속 N건(처분 전건 기재)` 를 병기하는 것뿐이다 — `corrected` 는 이 경로에 없다(corrected 의 증거는 재실행에서의 소멸이라 재실행 결과가 곧 최종본이다 · corrected 행에는 «소멸 run 시각 · 블록 해시 전→후» 를 병기한다). 형식 red 는 안정 ID 가 없으므로 이 경로 자체가 없다. 계약 실존 결손(e-ID)은 «전건» 에 들지 않는다(exit 5 비차단 — 별도 게이트). 개정 수신 후 재실행 시점마다 각 red 의 처분 라벨을 그 red 절 뒤에 append 한다(이전 절의 처분은 재기재 — `--check-report` 는 마지막 절 이후만 읽는다). **라벨의 뜻은 채널별 닫힌 정의다** — **예보 항목(registry 귀속·선언 확정)의 처분 라벨은 `corrected | ignored | filtered`** 다: `corrected` = 개정으로 해소(다음 실행에서의 소멸이 증거) · `ignored` = 실위반으로 인지하되 개정하지 않음(실위반 확인 증거는 G2 귀속 red 해소 트레이스 **또는** legacy-debt 매칭 기록(STOP 병기) 둘 중 하나다 — 이관 빚 수용이 이 라벨이다 · 배너 시점에는 후자만 적법하다 — 전자는 G1 시점에 존재할 수 없다) · `filtered` = pre-gate 도구(스텁·문법·시뮬레이션) 한계 판정 — 이 채널에 `deferred` 는 없다(이연은 ignored+빚 매칭 또는 filtered 다). `filtered` 의 근거 유형은 둘뿐이다: ⓐ 리포트 사각 목록 항목 번호 인용(`S<n>` — 그 항목이 이 red 의 오탐 원인임을 한 줄로 잇는다) ⓑ 같은 형태의 실코드 파일이 해당 검사기에서 exit 0 인 대조 경로. **검사기 소스에서 판정 입력이 경로·폴더·파일 이름의 존재뿐인 구조 규칙**(rule-owner-map 등급 path — 예: #81 BC 직계 · #325 ORM 산출물 위치 · #188 area 1:1 · #318 driven_layer 자식 · #336 중앙 마이그레이션 · #490 트리 밖 경로)은 스텁 내용과 무관하므로 ⓑ 가 성립할 수 없고 filtered 대상이 아니다 — corrected 또는 ignored+빚 매칭이다. 경로와 내용을 함께 보는 규칙(예: #392 factories/ 의 factory_boy 부재)은 ⓑ 근거를 대면 filtered 가 가능하다. **계약 실존 결손(리포트 «계약 실존» 절 · 안정 ID `e-…`)의 처분 라벨은 `corrected | deferred | filtered`** 다(2026-09-03): `corrected` = 대상 실존 확보(다음 실행에서 실존 확인 K 증가·결손 소멸) 또는 경로 오기 정정(대상 기실존) — 행 삭제·소비 철회로 결손이 소멸하면 직전 리포트 대비 «결손 소멸 ∧ 행 수 R 감소»가 그것을 드러내며 처분은 `corrected(철회: <근거>)` 로 근거 병기 의무다(발주자 사안이면 STOP) · `deferred`(선행 대기) = 결손 대상이 상류 레인/후행 슬라이스 소유임을 명세가 명시하고 해소 조건을 병기한다 — 정형 `deferred(<소유 레인|Sn>; until <머지 SHA|Sn>)` 권고 · 증거는 조건 충족 시점 재실행에서의 소멸이다(dirty overlay·기준선 갱신이 자동 반영) · `filtered` = 도구 한계(네임스페이스 레이아웃·`import *`·파싱 불능 등 판정 불능 U 계열 — 근거 병기 의무) — 이 채널에 `ignored` 는 없다(부재는 수용 가능한 위반이 아니라 ImportError 예약이며 G2 귀속·legacy-debt 어느 증거도 성립하지 않는다). 실존 채널은 승격 판정식(P/S/I 표면 ∩ G2 귀속)의 **입력이 아니다** — 결손 건수·처분 분포·도구 오류를 별도 계수로만 보고한다(설계 v4 §8 ⑷). 각 채널의 정의 밖 재량 라벨은 없다 — 같은 도구 한계를 레인마다 다른 라벨로 처분하면 승격 판정식이 오염된다(2026-09-02 관찰 레인 1·2 실측). 결손은 권고다 — 도구가 레인을 세우지 않으며(exit 5 는 비차단), 선행 대기가 발주자 결정 사안이면 기존 STOP 규약(R-0459/R-0460)대로 상신한다. **예보는 Phase 0 빚 스캔과 Phase 2 6번(G2 registry 게이트)의 실행·증거 요구를 어떤 형태로도 대체·축약하지 않는다** — 예보의 기준선은 «스텁 제외 현재 상태»라 `build_anchor` 를 읽지도 쓰지도 않으며, HEAD 판형 게이트 결과를 G2 증거로 유용하는 것은 차분 세탁으로 금지다. **계약 실존 채널도 G0 선행 조건 확인·상류 머지 판단(발주자 소관)을 대체하지 않는다 — 하드 검사가 아니다**(2026-09-03). 선언 검증은 실체화 0에서도 수행한다. 선언 확정은 귀속 red와 같은 전건 처분 의무/exit 2이고, 선언 후보와 생성 본문 S1 미검증은 별도 비차단 보고다. S1은 생성 위치·원본 record·정확한 슬롯 결합이 증명된 #376(after_commit 메서드)/#645/#647에 한하며 #566·bare Any·기존 실코드·미결합 진단은 유지한다. 명시 효과와 출처 결합 DTO의 지원 밖은 S2, 물리 import 전사 밖은 S3, update의 기존 본문 및 지원 밖 후상태는 S5로 남는다. green 의 뜻은 «설계 검증됨»이 아니라 «P/S/I급 결정 계약 위반 및 선언 확정 예보 0»이다(사각 목록·미시뮬레이션 목록은 리포트가 상시 병기한다). **machine 블록 부재 skip 금지**: file-plan 기계 블록 부재로 실행을 건너뛰지 않는다 — 부재는 형식 red(exit 3 «블록 부재»)이고 file-plan 0행(빈 펜스·주석뿐)도 형식 red(«블록 공허»)이며 반송은 위 형식 red 조항을 따른다(캐시 skip(아래 판형 ①)·실체화 0 skip(exit 4 — 선언 확정·실존 결손 없는 공허 차분 가드)과 구별). 신규·개정·구형 명세를 가리지 않는다 — 구형 명세(형식 규범 이전 승인)는 개정 시점에 블록을 소급 작성한다(기준선 실존 경로는 `update` · 부재 경로만 `add`). *왜* — 승인 명세가 registry 결정 계약과 조인되지 않은 채 동결되면 그 위반은 G1 이후 반송(레인당 평균 ≈34분)으로야 드러난다: 같은 판정 의미론을 승인 전에 결정적으로 돌리면 그 손실이 배너의 예보 1행으로 당겨진다.
+
+**pre-gate 캐시 skip·재발화 판형**(2026-09-03): ① **캐시 skip** — 위 «기계가독 블록 해시가 불변이면 재실행을 skip 한다»의 해시는 실행기의 `scripts/design_pregate.py <산출물 폴더>/design-spec.md . --block-hash` 값(기계 블록 4종 + 영구 테스트 입장 표, 선택형 use-case-effects를 파서와 같은 추출로 이어 붙인 sha256[:12] — 효과 블록이 없으면 기존 해시 알고리즘을 유지하고, 있으면 효과 마커와 원문을 마지막에 추가 — 출력 전용·판정 무접촉·git 0회)이고, 매 실행 리포트 헤더가 같은 값을 `블록 해시 <값>` 으로 병기한다. skip 조건은 **`--block-hash` 값이 직전 실행 리포트 헤더의 값과 동일**할 때뿐이며, skip 마다 pregate-report.md 말미에 1행 `- pre-gate skip — 블록 해시 <값> 불변 · 기준선 <sha12> · 재실행 생략 <UTC> · 직전 예보 <UTC>` 를 append 한다(기록 의무 — 이 행은 `## pre-gate 예보` 문자열을 쓰지 않는다). 값이 다르면 skip 불가이고, skip 행 없는 미실행은 규범 위반이다(«skip 행 부재 ∧ 해시 변동»으로 관측한다). ② **Phase 2 진입 후 재발화 판형** — 반송·STOP 으로 design-spec 이 개정돼 재실행할 때는 `--base <G1 승인 시점 기준선 SHA>` 를 명시한다(값은 G1 배너 직전 최종 실행의 pregate-report 헤더 «기준선 SHA» — `build_anchor` 는 읽지 않는다(R-3434)). 미커밋 WIP 는 커밋 또는 stash 후 실행한다. 실행기는 `--base` 명시 시(명시 `--base HEAD` 포함) 기준선 트리에 없던 계획 add 가 오버레이에 실존하면 «기실현 add»로 already-built 에 기록하고 사본에서 스텁으로 대체해 예보하며(실물 판정 혼입 0), 기준선 트리에 있는 add 는 여전히 형식 red(add 충돌 — 계획↔실물 모순)다. 재발화의 red 는 계획 red 로서 반송 사유이고(위 문단 — 차단 모드), 기실현 실물이 스텁과 다른 위반의 판정자만 G2 앵커 차분이다(사각 S7). ③ **Phase 2 최신성**(2026-09-03 차단 승격) — Phase 2 중 design-spec 변경(G1′ 반송·Contract mismatch 반송·수정 모드 개정 — 수정 모드 절)은 슬라이스 dispatch 전 ②의 `--base` 재발화가 선행한다. G2 배너 직전에는 `scripts/design_pregate.py <산출물 폴더>/design-spec.md . --check-report <산출물 폴더>/pregate-report.md` 의 exit 0(마지막 예보 절의 블록 해시 = 최종 명세 해시 ∧ 판정 비형식red ∧ red 면 예보 항목 전건 처분 기재)을 얻는다 — 다르면(stale) 재발화 후 G2 다 · skip 행·처분 절의 문자열은 대조 대상이 아니다. **한정**: 이 레인 산출물 폴더에 pregate-report 가 없고 design-spec 에 machine 블록도 없고 이 세션에서 design-spec 변경이 0 이면(형식 규범 이전 승인 명세의 순수 구현 수정) 최신성 행은 `미실행(구형 명세 · 변경 0)` 이고 `--check-report` 를 부르지 않는다 — 블록이 있는 명세는 이 한정에 들지 않는다(초안 수신 트리거로 리포트가 반드시 있다).
 
 ## Phase 2 — 구현 (G2, 이중 루프 TDD)
 
 1. **입장 결정과 조건부 테스트 러너 준비** — 승인된 입장 표를 먼저 읽는다. 새 영구 테스트 artifact가 필요한 `add/update` 행이 하나 이상 있을 때만 pytest 가용성을 확인하고, 그때 설정이 없으면 `implementation-django-ninja` §2.1 버전-핀 규율로 Tier-1(pytest·pytest-django·pytest-mock·factory_boy)을 설치한 뒤 루트 `[tool.pytest.ini_options]`에 프로젝트의 실제 `DJANGO_SETTINGS_MODULE`(manage.py/env에서 감지)을 기록한다. `reuse`는 확립된 기존 러너로 지정 anchor만 실행하며 dependency·manifest·runner config를 바꾸지 않는다. 일반 `retain`, `reject`, `remove`만 있는 변경도 runner setup write를 만들지 않는다. 기존 `TestCase` 스위트를 pytest 관용구로 재작성하지 않으며, 승인된 `add/update`로 새 테스트를 쓸 때만 pytest 관용구를 사용한다.
 2. 승인된 입장 표와 변경 URL·public symbol/use case·event/model/constraint명을 앵커로 **관련 테스트만 한정 검색**해 `existing authoritative coverage`를 확인한다. decision을 다시 만들지 말고 다음대로 dispatch한다: `add/update`만 새·변경 Red와 test edit, `reuse`는 지정 기존 anchor 실행만 하고 artifact write 0, 일반 `retain`은 무편집, `remove`는 승인된 exact target만 원 소유자에게, `reject`는 test 역할 dispatch 0, `pending`은 G1/G1′ 반송이다. 명시 승인된 의미 보존 `retain` 재조직만 새 case·assertion·Red 없이 같은 보호를 전후 기록한다. 외부 HTTP/event/user-observable/public contract 소유 행은 **acceptance-tester**, domain/application/DB/adapter 소유 행은 **coder**에 준다. 전체 suite를 discovery 대용으로 쓰지 않는다.
 3. 제품 구현 단위로 **슬라이스 목록을 도출**하고 각 슬라이스에 관련 입장 행을 붙인다. G0에서 「지금 정리」로 결정된 빚(`refactor-scope.md`)은 **리팩터링 슬라이스(슬라이스 0 · 동작 불변)**로 만들어 신규 개발 슬라이스보다 **앞에** 둔다 — 리팩터링과 기능 변경을 한 슬라이스에 섞지 않는다. 후보·recipe·coverage 목표만으로 test-adjustment/unit-Red 슬라이스를 만들지 않는다. 외부 `add/update` Red와 내부 `add/update` Red, 승인된 `remove` 대상만 해당 소유자의 test edit 입력이며, `reuse` anchor는 새 슬라이스 수를 압박하지 않는다.
 4. 슬라이스마다 `spawn_agent`로 **coder**를 띄운다 — 입력: 승인 명세·패키지 구조·관련 입장 행·acceptance 결과(있으면)·이번 제품 구현 슬라이스. coder는 자기 소유의 `add/update`만 단위 Red→Green→Refactor로 편집하고, `remove`는 exact target만 제거한다. `reuse/reject`에서 내부 test write를 만들거나 외부 계약 테스트를 수정하지 않는다. 이번 실행이 Red를 위해 만든 loader/dynamic import guard/대체 decorator/skip/xfail/helper는 만든 동일 역할을 첫 Green 직후 다시 호출해 즉시 제거하며, 작업 전 기존 비계를 임의 삭제하지 않는다. `wait_agent`로 결과를 받는다.
    - 슬라이스가 **3개 이상**이면 슬라이스마다 `dddjango-discipline-reviewer`를 **Phase 2 implementation 모드**의 해당 슬라이스 범위로 띄워 경량 감사하고 coder에 반영시킨다. 마지막 슬라이스는 홀리스틱 감사로 갈음할 수 있되 갈음은 조건부다(2026-08-17) — 홀리스틱 호출 입력에 «S_n 전용 경량 감사 생략 — S_n 범위 전량 실독 필수»를 명시하고, 홀리스틱 리포트가 전량 실독을 확인해야 갈음이 성립한다. 마지막 홀리스틱 1회는 갈음 여부와 무관하게 존치한다. 마지막이 아닌 슬라이스의 경량 감사 발견(blocker·important)은 다음 게이트 전에 원작성자 반송으로 반영을 완료한다(완료 = 원작성자의 처리 보고 수신 — 외부 계약 테스트 소유 발견이면 acceptance-tester가 원작성자다). 감사 대상 범위와 다음 슬라이스 작업 파일이 겹치면 감사 완료 후 배차한다(«같은 파일 병렬 편집 금지»의 적용) — 겹치지 않으면 병렬 배차 가능. Phase 2 시작 한 줄 상태에 슬라이스 목록·개수를 명시한다.
 5. **규율 감사**: `spawn_agent`로 `dddjango-discipline-reviewer`를 **Phase 2 implementation 모드**로 띄운다 — 필수 입력은 코드+테스트, 승인 입장 표, 역할별 최소 조정 보고, test diff·실행 결과와 슬라이스 목록이다. 감사 호출 입력에 `check-layer-skeleton`(registry #4)의 ⓓ 후보 채널 출력(행위 칸 200행 초과 신호·페이로드)과 `check-public-surface-annotation`(registry #11)의 ⓓ 후보(#645 — 변수·제네릭 안의 명시 `Any` · #647 — 입구 매개변수·즉시 검증 지역 변수의 `dict/Mapping[…, object]` 와 반환 주석의 자리표시 `object` · #650 — `json.load(s)` 결과의 무검증 흐름)를 동봉한다 — 두 채널 모두 동봉 범위는 registry_gate 가 앵커 차분으로 가른 **«ⓓ 신규(N′∖L′)»** 절·sidecar 레코드이고, 앵커에도 있던 «ⓓ legacy» 는 게이트 보고의 건수로만 적는다. reviewer는 각 test diff hunk를 decision과 unique production failure에 대조하고, `reuse/reject` write 0, 일반 `retain` 무편집, `remove/weaken` 종료 근거·exact target, 의미 보존 재조직의 전후 보호, 첫-Green 비계 잔존을 감사한다. 기존 migration lifecycle과 관련 테스트 보존 규칙도 그대로 감사한다. 기본은 G2 직전 1회, 슬라이스 ≥3이면 슬라이스별 경량 감사(마지막은 조건부 홀리스틱 갈음 가능) + 마지막 홀리스틱 1회다. 외부 assertion 지적은 acceptance-tester, 내부 assertion과 일반 구현 지적은 coder, 입장/설계 오류는 design-architect를 거쳐 G1/G1′으로 반송한다(반송으로 `design-spec.md` 가 개정되면 **재승인 전에 Phase 1 pre-gate 를 재실행**하고 예보 1행을 재승인 배너에 병기한다 — Phase 1 pre-gate 문단 · Phase 2 중이면 재발화 판형: `--base <G1 기준선 SHA>` 명시·WIP 커밋/stash).
    - 같은 파일에 외부 계약 assertion과 내부 assertion이 섞였으면 두 역할을 병렬 편집시키지 않는다. acceptance-tester→coder 순으로 호출하고 다음 역할은 최신 파일을 다시 읽는다.

```

## dddjango/agents/design-architect.md

Before SHA256: c9315a96c0a39bbbe8ce269eaa6a966ec6a855a790ce8d7317054d6939451aec
After SHA256: 6814957c64d98e04d21475516c871c10e3ab8d75e1754e1719337f6160638a13

```diff
--- before/dddjango/agents/design-architect.md
+++ after/dddjango/agents/design-architect.md
@@ -45,21 +45,21 @@
 
 1. **`contract scope`**: 프로젝트의 모든 API surface별 profile, API instance/namespace/version/public·internal 구분, scope 전체 BC와 그중 public BC error가 있는 error-BC subset, API/controller/URLconf/registrar/error/common module의 project-relative 경로, consumer·OpenAPI evidence, module sharing을 열거한다. repository artifact에는 project-relative 경로가 필수이고, greenfield artifact에는 명시적인 planned project-relative 경로를 쓰며, 없거나 적용되지 않는 항목은 그렇게 명시한다. planned 경로는 **이번 delivery가 승인 스코프 안에서 새로 만드는** artifact 전용이다 — 기존 artifact는 관찰된 실제 경로(legacy 위치 포함)로 적고, 타 BC의 표준 경로를 planned로 적지 않는다(2026-08-13).
 2. **`scope evidence`**: 위 inventory 각 행의 repository module/artifact에는 project-relative 경로와 관찰 내용을 기록한다. external consumer·사용자 발언·runtime-generated OpenAPI에는 stable external evidence identifier와 관찰을 쓸 수 있고, planned artifact는 아직 존재하지 않아도 slot 1의 planned 경로로 입증한다. 같은 profile의 common/error 재사용은 한 행으로 dedupe한다. mixed-profile shared module이나 한 source의 multiple API instances 때문에 surface/profile/sharing/contract 대응이 실제로 모호·상충하거나 inventory가 끝내 불완전할 때만 `STOP_FOR_USER_APPROVAL`로 보낸다. evidence가 external이거나 planned artifact가 아직 없다는 이유만으로 멈추지 않는다. inventory와 표준 트리의 불일치는 이동 지시가 아니라 관찰 기록이다.
 3. **`error profile`**: scope마다 `dddjango-code-json | preserve-established` 중 하나와 선택 근거를 쓴다. RFC 9457 wire가 관찰됐다면 `preserve-established`의 profile-native 계약으로 보존할 수 있지만 파일명이나 dependency 유무는 근거가 아니다. preserve scope는 code-profile artifact와 격리한다.
 4. **`compatibility/rollout`**: 지원 consumer와 현재 wire·OpenAPI·test 계약, 배포된 code 변경의 breaking 여부, 동시 migration 또는 version split, deprecation/Sunset과 종료 근거를 기록한다. 현재 승인된 제품 명세나 명시적 사용자 승인 없이 기존 계약을 끝내거나 바꾸지 않는다.
 5. **`common FrameworkErrorSchema action`**: `dddjango-code-json`이면 `reuse | create | approved-change` 중 하나이며 `none`은 금지한다. `approved-change`는 명시적 사용자 승인 evidence를 함께 기록하고, 없으면 `STOP_FOR_USER_APPROVAL`이다. `preserve-established`이면 관찰된 profile-native common/canonical error artifact의 action 또는 evidence가 있는 `none | not applicable`을 기록하고 common `ErrorSchema`을 새로 강제하지 않는다.
 6. **`common FrameworkErrorSchema shape/approval`**: `dddjango-code-json`이면 plugin 기본 property 없이, 기존 scope는 관찰된 common `ErrorSchema`을 기준선으로 삼고 신규 scope는 제안한 exact field set과 각 type·required/default/nullable·Field metadata·model config/legacy Config·validator/serializer/computed field/Pydantic hook inventory와 effective semantics·wire 직렬화, 어느 field를 BC ErrorCode로 좁힐지, project-relative canonical path를 기록한다. 신규 shape 생성과 현재 기준선의 property·type·존재성·변환 규칙·의미 변경은 일반 G1 승인과 분리해 명시적 사용자 승인을 받아야 한다. 변경이면 slot 5가 `approved-change`이고 이 slot에 별도 승인 evidence가 있어야 G1을 완료할 수 있다. `preserve-established`이면 관찰된 profile-native wire/media type/schema/handler shape와 approval evidence 또는 `none | not applicable`을 기록한다. 관찰된 RFC/schema/handler를 보존할 수 있지만 새 recipe로 일반화하지 않는다.
 7. **`BC error module`**: `dddjango-code-json`이면 error-BC별 side-effect-free module 경로와 common import를 기록하며 public BC error가 없는 BC만 `none`일 수 있다. `preserve-established`이면 관찰된 profile-native module/handler artifact 또는 evidence가 있는 `none | not applicable`을 기록하고 BC error module을 강제하지 않는다.
 8. **`BC ErrorCode`**: `dddjango-code-json`이면 error-BC별 단일 string Enum과 최소한의 literal public code 목록을 기록하며 public BC error가 없는 BC만 `none`일 수 있다. `preserve-established`이면 관찰된 profile-native code taxonomy/Enum artifact 또는 evidence가 있는 `none | not applicable`을 기록하고 `BC ErrorCode`를 강제하지 않는다.
 9. **`BC ErrorSchema`**: `dddjango-code-json`이면 error-BC별 common shape를 따르며 slot 6이 지정한 식별자 field 하나를 해당 BC `ErrorCode`로 좁힌 base Schema와 경로를 기록하고 public BC error가 없는 BC만 `none`일 수 있다. 좁힌 식별자 field는 공통의 default를 잃어 required여도 canon이다(식별자 field 한정·ErrorCode 좁힘 동반일 때만 — 2026-08-15). `preserve-established`이면 관찰된 profile-native status-specific schema/response artifact 또는 evidence가 있는 `none | not applicable`을 기록하고 `BC ErrorSchema`을 강제하지 않는다.
-10. **`prepared error mapping`**: `dddjango-code-json`이면 concrete domain/application exception 또는 조회의 `None` → no-arg concrete `ErrorSchema`, 또는 event-specific 값으로 명시적으로 채운 BC base `ErrorSchema` → controller의 direct `Status(<승인된 HTTP status 표현>, error)` chain과 각 output의 slot-6 exact literal body/approved header를 표로 기록한다. internal failure type과 output object를 명확히 구분한다. 여러 internal failures가 하나의 public ErrorCode로 수렴할 수 있다. raw infra failure는 기본 500이고, 승인된 안정적 public meaning이 있을 때만 consuming BC의 internal exception으로 정규화한 뒤 `ErrorSchema`을 만든다. `preserve-established`이면 관찰된 profile-native preparation/mapping artifact·behavior 또는 evidence가 있는 `none | not applicable`을 기록하고 code-profile chain을 강제하지 않는다.
+10. **`prepared error mapping`**: `dddjango-code-json`이면 concrete domain/application exception 또는 조회의 `None` → no-arg concrete `ErrorSchema`, 또는 event-specific 값으로 명시적으로 채운 BC base `ErrorSchema` → controller의 direct `Status(<승인된 HTTP status 표현>, error)` chain과 각 output의 slot-6 exact literal body/approved header를 표로 기록한다. internal failure type과 output object를 명확히 구분한다. 여러 internal failures가 하나의 public ErrorCode로 수렴할 수 있다. 이미 잡은 IntegrityError의 승인된 알려진 제약 실패는 구체 계약 예외로, 나머지는 승인된 일반 저장소 실패 계약으로 번역한다. repository 실패 계약은 domain 소유, capability port 실패 계약은 해당 port 소유다. 이 내부 정규화는 공개 HTTP 오류 승인이 아니므로 일반 저장소 실패의 외부 응답은 기존 safe 500을 유지한다. 새 ErrorCode/ErrorSchema/4xx/503을 만들지 않는다. 잡지 않은 unknown 인프라 오류를 새로 catch-all하지 않는다. 안정된 public meaning이 별도로 승인된 경우에만 그 외부 계약에 맞는 controller mapping을 한다. 이미 선언된 계약 예외의 관찰 후 재던짐은 허용한다. `preserve-established`이면 관찰된 profile-native preparation/mapping artifact·behavior 또는 evidence가 있는 `none | not applicable`을 기록하고 code-profile chain을 강제하지 않는다.
 11. **`controller mapping`**: `dddjango-code-json`이면 slot 10의 internal failure 형태에 따라 두 path 중 하나를 명시한다. exception path는 endpoint별 input preparation 뒤 정확히 한 번의 application call만 narrow `try`에 두고 승인된 concrete exception 또는 exception tuple만 catch한다. `None` path는 조회 use case가 대상이 없어 `None`을 돌려주는 경우에만 고르고, artificial `try`/`catch` 없이 application call을 정확히 한 번 실행한 뒤 그 직후 `is None` branch하며 exception을 fabricate하거나 raise하지 않는다. 실패가 둘 이상이거나 사유가 있으면 exception path다 — 실패를 Result variant·outcome 값으로 설계하지 않는다(`<use_case>_result.py`엔 성공 한 벌만 — #571). 두 path 모두 승인된 no-arg concrete 또는 event-specific 값으로 채운 BC-base `ErrorSchema`을 만들고, 승인된 header를 주입된 응답용(temporal) Django `HttpResponse`에 설정한 뒤 two-argument `Status(<literal/status constant 또는 slot-6 body field>, error)`를 직접 return한다. `status` body property를 발명하지 않는다. error helper/handler/factory/serializer/table 또는 mapping 추출은 만들지 않는다. `preserve-established`이면 관찰된 profile-native controller/handler mapping 또는 evidence가 있는 `none | not applicable`을 기록하고 direct `Status`를 강제하지 않는다.
 12. **`response/OpenAPI/tests`**: `dddjango-code-json`이면 승인된 runtime HTTP status/body/header mapping, framework-owned status non-advertising, mounted client와 공개 generated OpenAPI의 관련 operation/status/schema 후보·기존 evidence를 기록하고 아래 영구 테스트 입장 표의 행을 참조한다. slot 6의 shape 및 별도 변경 승인은 보존하지만 Pydantic private metadata·validator 위치·framework 기본 직렬화를 자동 영구 테스트로 만들지 않는다. 별도 공개 Python consumer 계약은 HTTP와 다른 행으로 심사한다. `preserve-established`이면 관찰된 profile-native media type/fields/status-specific schema·handler와 test/OpenAPI evidence 또는 `none | not applicable`을 기록한다. framework-owned 오류 smoke와 auth/header 검증도 승인 계약·독자 failure가 있는 후보만 입장시키며 exact framework body snapshot을 요구하지 않는다. native download/stream/redirect와 schema-less 204는 선언 Schema 규칙의 carveout이다.
 
 `dddjango-code-json`의 framework-owned 오류는 401/403/route 404/422/429/general `HttpError`/unknown 500이며 BC `ErrorSchema`으로 변환하거나 `response`에 광고하지 않는다. 모든 Ninja profile의 인증 실패에서는 `None`을 return하거나 framework `AuthenticationError`를 raise한다. `AuthenticationError` object나 `ErrorSchema`을 return하지 않고 어느 것도 `request.auth`에 저장하지 않는다. 406과 415는 각각 별도 사용자 승인을 받은 경우에만 tested version-compatible Ninja-owned pre-body/framework `HttpError` 경로로 구현하며 함수형 `Router`나 전역 handler를 강제하지 않는다. `preserve-established`는 관찰된 framework error body/협상 behavior를 그대로 기록하고 code-profile artifact를 도입하지 않는다.
 
 - **도메인(ddd)**: 애그리거트 경계와 불변식, 상태 전이, 유비쿼터스 언어, 관련 도메인 이벤트 채택 여부와 근거.
 - **계약(api)**: 외부에서 관찰되는 엔드포인트·요청/응답 계약·상태 코드·에러 profile·멱등성 정책. (저장·전달 보장 같은 데이터 측면은 db lens로 넘긴다.) 유한 재시도/CAS의 실패 outcome도 경계에서 승인된 안정적 public meaning이면 `prepared error mapping`에 승인 HTTP status·slot-6 exact body·header로 포함한다. 어떤 internal failure를 같은 public ErrorCode로 수렴할지와 retryable 503+`Retry-After` 또는 409 선택은 멱등성·재시도 trade-off와 consumer 구분 필요로 결정해 §5/G1에 올리고 임의 확정하지 않는다. 승인된 안정적 public meaning이 없는 raw infra·미식별 예외는 framework 500으로 둔다. application·domain은 HTTP status/body를 만들지 않는다.
 - **API 스택**(lens 무관, 새 API 표면이 생기면 항상 결정): 외부에 노출되는 새 HTTP/JSON API surface가 있으면 stack을 명세의 1급 결정으로 박는다. 신규 표면(이번 delivery가 새로 노출하는 route/operation — endpoint 단위; 기존 배포 endpoint의 수정은 이 결정의 대상이 아니다 — `implementation-django-ninja` §2.3 touched 조항 관할)의 stack은, 확립 스택(이 작업이 관찰하는 저장소 상태에서 배포·소비 evidence로 확인되는 스택)이 없으면 Django Ninja가 무언 기본이고, 확립 DRF·plain Django 스택이 존재하면 **스택 결정 자체를 `STOP_FOR_USER_APPROVAL`로 표면화**한다(선택지마다 대가 한 줄 — 표준 Ninja 채택: 확립 리소스와의 2-스택 분열 | 확립 스택 답습: 옛 스택 답습은 규약이 아니라 빚). 관찰은 스택 «정체» 식별과 STOP 선택지의 재료이지 답습 «채택»의 확정 근거가 아니며, Ninja 기본에서 벗어나는 신규 표면 스택 결정은 사유를 불문하고(답습·인프라/의존성 실물 부재·비-JSON 반환 메커니즘 포함) 이 STOP 경로로만 확정한다. G0 스코프 메모·발주서에 기록된 사용자의 명시적 스택 지시는 이 STOP 승인과 동격이다 — 명세는 그 기록(경로·인용)을 스택 결정 근거로 인용하고, 인용 가능한 명시 기록이 없으면 STOP이다(승인 효력은 그 발주의 명세에 한한다). 이 결정의 대상은 새 HTTP/JSON API surface뿐이다 — server-render HTML 표면(아래 HTML 문장·`implementation-django-web` §11 관할)·admin·정적 자원은 대상이 아니다. 오류 **wire 계약** 보존(«계약 profile» 축 — preserve-established)은 별개 축이다 — 확립(배포된) 표면의 wire 보존은 그대로되, 신규 endpoint의 error profile은 12-slot `error profile` 기준으로 별도 결정하고(같은 공개 namespace 합류는 스택·컨트롤러 형태 답습의 근거가 아니다), 신규 Ninja 표면에 preserve wire를 지우는 조합은 게이트 미열거라 그 취급 결정을 G1에서 표면화한다(STOP). SSE·스트리밍·파일 반환 표면의 기본 대안은 클래스 컨트롤러의 framework-native 반환(`implementation-django-ninja` §2.2 carveout)이며, plain 채택 선택지가 성립하려면 carveout으로 표현 불가하다는 관찰 근거를 그 STOP 대가 줄에 기록한다. dependency가 아직 manifest에 없다는 사실만으로 plain으로 낮추거나 `preserve-established`로 바꾸지 않는다. 새 Ninja surface는 `NinjaExtraAPI` + `@api_controller` class controller(aggregate 단위)이고, 승인된 scope마다 profile에 맞는 project API instance 하나를 둔다. **composition(배선·등록)은 profile 무관 표준이다**(2026-08-12 라운드 1′): `auto_import=False`의 side-effect-free BC registrar(`register_<bc>_api`), URLconf의 explicit registrar call과 mount로 구성하며 import-time registration은 하지 않는다 — 기존 BC 의 배선 실물(`*_api_router.py` 동형)은 배선 결정의 입력이 아니고, preserve 를 배선 답습의 근거로 명세에 박지 않는다. 이 문장들은 **신규 산출물의 형태**를 정할 뿐 **기존 코드의 처분 권한**이 아니다 — 명세는 승인 스코프의 산출물 목록 밖 기존 파일의 이동·개명·재배선을 결정으로 박지 않는다: 기존 코드의 처분은 G0 빚 결정(ⓐ/ⓑ)이 확정하고 명세는 ⓐ 승인 항목만 슬라이스 0으로 옮겨 적는다(2026-08-13 라운드 2 실증 — 명세가 «canonical 이관·면제 없음»을 자가 결정으로 박자 11 BC 100파일이 이동됐다). BC `composition_root/`(`dependency_wiring.py`의 `build_*` 팩토리 — final.md §1 트리 2~4행)가 DI만 소유한다. Controller는 one-statement application call에서 concrete domain/application exception을 catch하거나 조회의 `None`을 처리하고, no-arg concrete `ErrorSchema` 또는 event-specific 값으로 명시적으로 채운 BC base `ErrorSchema`을 만든 뒤 직접 `Status(<승인된 HTTP status 표현>, error)`를 반환한다. internal failure type과 output object를 명확히 구분하고 error handler/helper/factory/serializer로 빼지 않는다. `preserve-established`이면 관찰된 profile-native controller/handler/schema behavior를 보존하며 code-profile output/direct-`Status` recipe를 도입하지 않는다(보존 대상은 **오류 wire 산출물**까지 — registration/composition·트리·import 방향은 위 표준 그대로다). 성공 응답은 선언한 2xx `response` schema의 `Status`/schema 객체를 반환하고, 입력은 선언적 `payload: Schema`로 받는다. 406/415를 승인한 경우에도 tested version-compatible Ninja-owned pre-body/framework `HttpError` path를 쓰며 함수형 `Router`를 강제하거나 operation에서 raw body를 수동 parsing하지 않는다. **새 surface가 server-render HTML view면**(JSON API 아님) service의 domain/application exception은 view-local form re-render+`messages.error`(200), infra/unknown exception은 project `handler500`+`500.html`(`request`-only·empty Context), 승인된 transient contract는 `process_exception` retryable 503으로 표현하고 출처별 책임을 명세한다(`implementation-django-web` §11).
 - **데이터(db)**: 스키마 변화, 인덱스·제약, 트랜잭션 경계·격리·락 전략(`architecture-db` §9.5·§9.6 Risky Write), 마이그레이션 안전(rollout/backfill). **Risky Write(주문·결제·재고·예약·환불·권한·ledger 등 중복·race가 치명적인 쓰기)면 `architecture-db` §9.6 Risky Write Consistency Block을 *8행으로(표 또는 행 단위 블록) 명세에 박는다* — §9.6을 번호로 인용만 하지 말고 8행을 채운다: Transaction owner·Locking strategy·Rule ownership·Idempotency storage·API handoff·Side-effect timing·Isolation/retry·Test criteria. 각 행에 결정 내용을 적고, 해당 없으면 근거와 함께 '미적용'으로 둔다. ⚠ 스코프 가드 — Idempotency storage 행: 사용자가 멱등성(`Idempotency-Key`)을 요청하지 않았으면 이 행을 *silent하게 필수 서브시스템으로 빌드하지 않는다*: 기본은 '미적용'(알려진 한계)으로 명세에 *현재 상태로 commit*하고, 이를 **배너 override 항목**으로 함께 산출한다 — 별도 '미해결 옵션' 블록으로 열어두지 않는다. 사용자가 미적용을 수락하면 명세 재작성이 불필요하고, G1에서 채택을 택하면 Coordinator가 G1 override 입력으로 너를 재호출하니 그때 `architecture-api` §13대로 구현한다. 미요청 멱등성을 명세에 silent 의무로 박는 건 스코프 초과다(같은 원리로, scope.md가 '범위 아님 / 필요 시 G1 제안'으로 명시한 다른 견고성 결정도 기본 '미적용' commit + 배너 override 항목으로 산출한다 — architect가 'Y감이냐'를 판정하지 않고 scope.md의 그 목록을 앵커로 쓴다). Test criteria 행엔 concurrent request·oversell 등 동시성 검증 기준을 포함한다.** 바로 아래 엔진별 락·동시성 확정은 이 블록의 `Locking strategy`·`Isolation/retry` 행을 *채우는 근거*이지 블록을 대체하지 않는다. **락·동시성이 걸린 Risky Write는 개발(sqlite)·운영(Postgres) 엔진별 동작 차이까지 명세에서 확정한다** — 예: sqlite `select_for_update` no-op·DEFERRED begin 데드락 → 환경 무관 방어는 CHECK(불변식 백스톱)+낙관적 `version`/CAS 조건부 UPDATE이되 `WHERE`엔 경합 가드만 담고 비즈니스 판정(예: `stock>=qty`)은 인프라로 옮기지 않는다 — 판정·불변식은 도메인 애그리거트(또는 도메인 서비스)가 소유하고 프로덕션 경로에서 실행, 응용 서비스는 조회→도메인 메서드→영속화, repo는 결과만 저장(판정을 SQL·ORM으로 복제하면 빈혈, 원칙 `architecture-ddd` §3.2, 메커니즘 §9.5). 직렬화 필요 시 begin 모드 명시(§9.5). *왜* — coder는 한 환경만 보므로(coder 「경계」) 엔진차 락 공백을 구현에서 메우면 G1' 설계 반송이 된다.
 - **Test criteria admission**: Risky Write·outbox·제약·동시성의 Test criteria는 위험과 candidate를 드러내는 설계 입력이다. 각 영구 테스트는 아래 입장 표에서 DB 보장 근거, 독자 failure mechanism, 기존 coverage를 따로 판정하며 Test criteria 행 자체가 `add`를 자동 결정하지 않는다.
@@ -77,25 +77,27 @@
 
 - **영구 테스트 입장 표**(lens 무관, 항상 작성): 이번 변경과 관련된 모든 영구 test artifact의 `add/update/move/split/rename/remove/weaken` 및 의미 보존 재조직 후보를 다음 최소 열로 한 행씩 판정한다.
 
   | candidate | protected contract/evidence | unique production failure | existing authoritative coverage | decision | owner/path |
   |---|---|---|---|---|---|
 
   decision은 `add/update/reuse/retain/remove/reject/pending` 일곱 값만 쓴다. `pending`은 리뷰 뒤 0개여야 G1을 요청할 수 있고, `reuse`·`reject`는 test artifact write가 0이다. 일반 `retain`은 무편집이며, 명시적으로 승인한 의미 보존 move/split/rename/reorganization만 새 case·assertion·Red 없이 전후 같은 계약과 failure를 보호한다고 기록한다. `remove/weaken`에는 적용 가능한 support·deprecation/Sunset·rollout·영속 데이터/이벤트 종료 근거와 exact target을 적는다. framework/private/test-tool mechanics는 그 자체로 `reject` 방향이며, migration 파일·과거 state·forward/reverse 자체를 인수 기준으로 만들지 않는다. 기존 테스트나 현재 구현은 조사 증거일 뿐 현재 계약을 대신하지 않는다. 후보가 없으면 열을 유지한 빈 표와 `후보 없음`을 쓴다.
 
   입장 표와 별도로 현재 계약의 유지·변경·종료·부재 의무를 짧게 설명해 각 행의 근거를 추적 가능하게 한다. 순수 구현 버그 수정도 관련 기존 coverage와 독자 failure를 판정해 `reuse/retain/add` 중 하나로 기록하며, 단순히 `테스트 계약 변화 없음`으로 심사를 생략하지 않는다.
 
-- **기계가독 채널(machine blocks)**(lens 무관, 항상 작성 — 12-slot 부재가 적법한 레인에서도 아래 블록·입장 표 규율은 상시다): 명세의 파일 계획·공개 심볼·경계 import·물리 신호·예외 번역은 산문 서술과 «별개로» 아래 다섯 정본 문법으로 성문한다 — pre-gate(`design_pregate.py`)는 이 채널만을 전사 재료로 쓰고 산문에서 추론하는 재료는 0이다. **채널에 없으면 «부재»로 전사된다(fail-closed)** — 부재가 위반이면 red 가 나는 것이 정답이다(예: 마커 무기재 → «설계가 물리 신호를 안 정했다»는 진탐). `<!-- machine: … -->` 마커는 **concrete 계획 블록에만** 단다 — 표준 140행 템플릿·예시 인용에 달지 않는다(인용과 실계획의 구별이 파서의 유일한 판별 근거다). *왜* — 21레인 실측에서 파일 계획 방언이 6종이라, 형식 규범 없이는 어떤 결정적 파싱도 성립하지 않았다.
-- **파일 계획 정규 블록**: `<!-- machine: file-plan -->` 마커 + ```paths 펜스. 1행 = `<태그> <경로>`(태그 선행·공백 구분·경로는 project-relative — 태그는 `add|update|remove[@Ln]|empty`)이고 `#` 주석만 허용한다. 브레이스 전개·`·` 병렬·`*`/`…` 축약·미해소 `<placeholder>`·승격 폴더 표기(경로는 언제나 `<칸>.py` — 동명 폴더 승격은 구현 캐스케이드 소유)·**동일 경로의 태그 이중 서술**은 전부 형식 위반이다(이중 서술은 파서 결정 불능을 낳는다). glyph 트리 삽화를 남기려면 블록에서 렌더해 생성하거나 파서의 삽화↔블록 차분 판정을 받는다 — 같은 계획의 이중 표현이 서로 어긋나는 드리프트 축을 봉쇄한다. **태그의 뜻은 기준선 기준이다**(G1 시점 HEAD — Phase 2 재발화 시 `--base` 기준선 · 2026-09-03 차단 승격): `add` = 기준선에 없는 경로(실존하면 형식 red «add 충돌») · `update` = 기준선에 실존하는 경로(부재면 형식 red «update 대상 부재» — 그 경로는 `add` 로 적는다 · 유효 승격 형태 `<칸>/__init__.py` ∧ `<칸>/<칸>.py` 의 기준선 실존은 실존이다) · `remove[@Ln]` = 기준선 실존 경로(비후행 remove 의 부재는 형식 red «remove 대상 부재» — 예외 없음 · 후행 `@Ln` 은 판정 밖 · `--base` 기준선은 이동하지 않으므로(재발화 판형 ②) 기실현 remove 는 실존이다 · 기준선에도 없는(승인 전에 이미 지워진) 경로는 remove 행을 거둔다) · `empty` = 새 빈 파일(add 와 같은 «새 파일» 태그 — 기준선 실존이면 형식 red «empty 충돌» · 기실현이면 `update`). 구형 명세에 블록을 소급 작성할 때 기실현 경로는 전부 `update` 다 — 실체화 0 이 나오면 그것이 정답이다(`add` 를 `update` 로 바꿔 red 를 피하는 것은 형식 red 로 잡힌다). 비후행 remove를 전사한 뒤 그 경로들의 조상 중 최종 사본에서 빈 부모 디렉터리만 정리한다(dirty overlay 선삭제 포함). 남은 파일(0B·init·미추적·add/empty 포함)이 있거나 후행 remove 실물이 남으면 보존하며, 무관한 빈 디렉터리와 symlink 경유 경로는 정리하지 않는다. 폴더 정리는 파일 실체화 건수와 별도로 보고한다 — 파일 실효 조치가 없으면 기존 실존 판정 뒤 skip한다. remove만 있는 BC를 신규 골격으로 다시 만들지 않는다.
-- **공개 심볼 표기**: 자리표시자 실현 파일의 **공개 심볼 전부**를 `<!-- machine: symbols -->` 마커 + ```symbols 펜스에 적는다(«대표 1회»가 아니라 전수다) — 1행 = `경로.py::Symbol(Base) {필드, …}`(Symbol 은 대문자 선두 또는 `_`+대문자 선두 — 주 계약이 참조하는 사설 보조 타입 `_Item` 도 적는다: 파서가 클래스로 분류하고 검사기의 사설 면제 판정 경로를 스텁이 그대로 탄다 · 소문자 선두는 함수다) · 메서드 행 `경로.py::Symbol.method(파라미터) -> 반환`(수신자는 무어노테이션 `self`/`cls` 에 한해 적어도·안 적어도 된다 — 실행기 파서가 정규화한다; 어노테이션 수신자는 중복 합성으로 형식 red 가 된다) · 필드 = `name: Type[ = default]` · `NAME = "literal"`(enum 멤버) · `name = <식>`(Django 필드 대입식 등)만 허용 — 타입도 값도 없는 bare 이름은 형식 red 다. Base 병기가 의무인 종류는 재량 목록이 아니라 **검사기 소스에서 기계 추출한 닫힌 목록**(소성물 `scripts/pregate_symbol_kinds.json` — rulepack 과 함께 재생성)이고, 명명규약으로 유도 가능한 생략은 **성문 유도표**(final.md §1 칸→베이스 결정표 — **아직 성문 전이다: 성문 전에는 생략 허용분이 공집합이라 전 심볼을 명기한다**) 등재분에 한한다 — 단 **값 축 유도 3행은 성문 등재됐다**(2026-09-02 · 3행째 2026-09-03): django_* `apps.py` 의 `name`(앱 폴더 전체 점 경로)/`label`(bc명) 정형, models/ 칸 `*Model` 의 `Meta.db_table`(`<bc>_<entity_snake>` — #630 유도 규칙), 그리고 마이그레이션 칸(`migrations/NNNN_*.py` — makemigrations 산출물 모양 #593: `Migration` 클래스 1 · `0001_` 만 `initial = True` · `migrations/__init__.py` 는 빈 파일)의 결손 보충. 이 결손은 실행기가 규약 상수로 보충하므로 규약대로라면 생략해도 된다(마이그레이션 칸은 file-plan `add` 만 적어도 된다 — symbols 전사가 있으면 전사 우선 · 규약 밖 값을 계획하면 반드시 기계 블록에 명기 — 산문 명기는 예보 표면 밖이다). **생략 = 규약 준수 확약**이다(생략분은 자동 정규화되어 위반 예보가 불능이 된다: 규약을 벗어날 계획이면 반드시 명기). published-language 칸(contract/·published_error)의 심볼은 **필드 목록**(`code` 필드 유무 포함)을 병기하고, **주 계약이 참조하는 보조·중첩 타입은 소속 파일을 명세가 명시**한다 — 안 박으면 coder 가 즉흥 배치해 예보·판정이 그 파일을 못 본다. **데코레이터·모듈 별칭도 symbols에 명시한다**: 클래스 행 뒤 `경로.py::Symbol @dataclass(frozen=True, slots=True, kw_only=True)`처럼 적는다(이름·속성 이름 또는 그 호출만 · 복수 행은 적은 순서대로 클래스 위에 전사 · 선행 클래스 없는 행은 형식 red). 이름/옵션/별칭은 원문 그대로이며 자동 dataclass 지정이나 import 추론은 없다 — `dataclass`·`dc.dataclass` 등 데코레이터와 모듈 별칭의 필요한 import는 boundary-imports에 명시한다. 모듈 별칭은 그 파일의 클래스/함수보다 먼저 `경로.py::alias 이름[: 타입] = 별칭식`으로 적는다. TYPE_CHECKING 분기는 `경로.py::alias[TYPE_CHECKING] _BookAdminBase: TypeAlias = admin.ModelAdmin[BookModel]` 다음에 `경로.py::alias[else] _BookAdminBase: type[admin.ModelAdmin] = admin.ModelAdmin`을 적는다(같은 파일·같은 이름의 인접한 유효 두 행, 주석/빈 줄 제외). 필요한 `TYPE_CHECKING`·`TypeAlias`·admin·모델 import는 boundary-imports에서 공급한다. 별칭은 단일 이름 Assign 또는 값 있는 AnnAssign이고 우변은 이름·속성·타입 첨자 및 그 내부 타입 표현식으로 한정한다(호출·복합문·클래스/함수 정의 불가). import 뒤 클래스 앞에 if TYPE_CHECKING/else와 두 대입의 어노테이션을 보존해 전사한다. 누락 분기·중복 별칭·다른 이름의 else·클래스/함수 뒤 별칭은 형식 red다. 비-add의 데코레이터·별칭 행도 문법을 검증하며 그 재료로 기존 본문을 바꾸지 않는다 — 완결된 별칭 이름만 update 자기 해소 근거이고 데코레이터 행만으로 이름을 선언하지 않는다. 미기재는 부재이며 산문에서 보충하지 않는다. 마이그레이션 정형이 무시하는 별칭 재료는 채널 메모로 병기한다. **update OHS 신규 함수 전사**: 표준 `open_host_service/<area>/<area>_service.py` 실물에 symbols로 명시한 신규 모듈 함수만 기존 본문 뒤에 전사한다. 기존 함수·클래스·별칭의 수정과 다른 update 칸은 S5다. 기존 바인딩/새 함수/합성 helper 충돌, 전사할 신규 함수 없음, 실물 부재·승격 형태는 사유를 적고 미시뮬레이션으로 남긴다. 기존 본문을 대체하거나 checker에 선언 이름을 주입하지 않는다. 함수 본문은 계속 스텁이므로 G2 실검증을 대체하지 않는다.
-- **경계 import 표**: 검사기 판정에 관련되는 **경계 import 전부**를 `<!-- machine: boundary-imports -->` 마커의 ```imports 펜스(1행 = `<소비 파일>` + 탭 또는 공백 2+ + `<import 문 그대로>`)로 성문한다 — 타 BC OHS/contract·framework 공통만이 아니라, domain/contract 칸의 서드파티 라이브러리와 **테스트 파일의 경계 import 전부**(factories/타 급·타 BC OHS/published 계약 소비)까지. 파일별 전체 import 를 강제하는 것은 아니다 — **경계란 세 가지다**: ⑴ BC 밖(타 BC OHS/contract·framework 공통·서드파티·테스트 재료) ⑵ BC 안의 층 경계 중 **층 규율 검사기가 금지·예외 항목으로 판정하는 것**(driving 잎 → `application_layer/port/**` · domain → 상위 층 등 #92~#96·#185/#186 의 항목 — 잎이 port 예외를 잡을 계획이면 그 import 행을 그대로 적어 G1 에서 #93 예보를 받는다: 적을 수 없는 설계가 드러나는 것이 이 채널의 목적이다) ⑶ 그 밖은 구현 재량(성문 불요). 산문에만 적힌 경계 import 는 예보 표면 밖이다(pre-gate 보고 헤더의 사각 목록 S3). **각 행은 실행기가 격리 사본(기준선 + dirty overlay + 이 명세의 add)에서 3단 실존 판정**(⑴ 모듈 실존 · ⑵ 자리표시자 아님 · ⑶ 이름 최상위 정의)을 받는다(2026-09-03) — 저장소 밖(표준·서드파티)은 검사 밖, 이 명세가 add 하는 대상은 자기 해소(symbols 채널 소관 — 승격 폴더 부품 포함), ⑵ 는 이름 import(`from M import n`)의 대상 M 이 모듈일 때만이다. file-plan `update` 대상(사본에 실물이 있을 때만 — 기준선 부재 update 는 형식 red 로 먼저 서고, 유효 승격 형태 예외로 통과한 대상만 update 로는 생기지 않으므로 ⑴ 모듈 부재)의 이름은 그 칸의 symbols 에 선언하면 «자기 update 해소»이고 미선언이면 현재 표면에 있을 때만 실존 확인·아니면 판정 불능이다(표면은 이 명세 이후 상태 — update 로 새 심볼을 낼 계획이면 symbols 에 적는다 · ⑵⑶ 비적용). 판정 기준은 **이 브랜치**다 — 다른 워크트리·미머지 브랜치의 실물은 보지 않는다(부재 = «계약 실존 결손»으로 예보 · 소비자가 `update` 여도 행은 판정된다). 상류 소유 계약을 소비할 계획이면 그 행을 **그대로 적는다** — 결손 예보가 선행 조건의 기계 표현이며, 행을 빼서 green 을 만드는 것은 채널 은폐(경계 import 전수 의무 위반)다. 신규 함수가 전사되는 update OHS 서비스는 명시 boundary-imports도 충돌 없이 추가 가능한 경우에만 함께 전사한다. 기존 바인딩을 다른 출처로 덮는 등 안전한 합성이 불가하면 해당 서비스 전사를 통째로 보류하고 S5 사유를 보고한다. 행 전부를 대상으로 하는 기존 계약 실존/S′ 판정은 이 전사 여부와 별개로 유지한다.
-- **물리 신호 어노테이션**: 영구 테스트 입장 표의 `owner/path` 셀 안에 정형 어노테이션 `[markers: django_db,…] [base: TestCase] [client: yes]` 를 단다 — 테스트 물리 신호(마커·베이스·클라이언트)의 유일한 전사 채널이다. **무기재 = «물리 신호 없음»으로 전사된다(fail-closed)** — 마커를 안 적으면 red 가 그 결손을 알린다. 입장 표 header 는 영문 정본 6열(`candidate | protected contract/evidence | unique production failure | existing authoritative coverage | decision | owner/path`)로 고정하고 셀 안에 raw `|` 를 두지 않는다 — 열 구조가 곧 파서 계약이라, 열이 흔들리면 어노테이션 채널이 통째로 죽는다. owner/path에서 처음 나오는 Python 파일 주소(`경로.py` 또는 `경로.py::case`)가 그 행의 artifact다. code span과 bare 경로 모두 허용하며 앞선 `add` 같은 비경로 span은 건너뛴다. case 접미는 파일 주소 결합에서만 벗긴다(case 본문 전사 아님). 첫 파일 주소를 file-plan의 정확한 add 키에 결합하고, 뒤의 support/coverage 주소에는 신호를 전파하지 않는다. 첫 주소가 미등재·비-add여도 뒤 파일로 넘어가지 않는다.
+- **기계가독 채널(machine blocks)**(lens 무관, 항상 작성 — 12-slot 부재가 적법한 레인에서도 아래 블록·입장 표 규율은 상시다): 명세의 파일 계획·공개 심볼·경계 import·물리 신호·예외 번역은 산문 서술과 «별개로» 기존 다섯 정본 문법으로 성문하고, 효과는 선택형 여섯 번째 입력으로 적는다 — pre-gate(`design_pregate.py`)는 이 채널만을 전사 재료로 쓰고 산문에서 추론하는 재료는 0이다. **채널의 무기재 의미를 구분한다** — add의 물리 신호 무기재는 부재로 전사하고, update marker 무기재는 현행 유지, 효과 무기재는 S5 미검증이다. 부재가 위반인 채널만 red다. `<!-- machine: … -->` 마커는 **concrete 계획 블록에만** 단다 — 표준 140행 템플릿·예시 인용에 달지 않는다(인용과 실계획의 구별이 파서의 유일한 판별 근거다). **명시 효과**는 `<!-- machine: use-case-effects -->` + ```effects 펜스에 `경로.py::UseCase read-only uow=none` 또는 `경로.py::UseCase write uow=<타입식>`으로 적는다. 어휘는 `read-only`/`write`, UoW는 `none` 또는 비어 있지 않은 타입식이며 add/update의 선행 클래스 선언에만 결합한다. 중복/상충·잘못된 어휘/타입식·선행 클래스 부재는 형식 red다. 명시 read-only+UoW와 출처가 확인된 UoW 주입의 모순은 선언 #197 확정, 미해소 출처는 후보, write 효과의 주입 불일치는 채널 메모다. 출처 결합 DTO의 공개 Result/Out/Response에서 사설·중첩 타입과 명시 별칭·표준 컨테이너를 따라 확인한 aggregate/entity 누수는 선언 #202 확정이고 VO/shared VO는 허용한다. 이름만 같거나 동적/불명 출처는 후보이며 OHS에 domain import를 합성하지 않는다. 선언 확정은 architect·해당 설계 리뷰/감수자가 처분하고 후보는 확인 질문으로 남긴다. S2의 내부 모순 사각은 이 명시 효과·출처 결합 DTO 지원 밖에 남는다. S1 생성 본문 미검증은 실제 구현 검증을 대신하지 않는다.
+
+**admin context 판정**: #493 주석 존재 유지 · #645 framework 소유 슬롯 Any 제한 허용 · #646 제네릭 런타임 안전 유지 · #647 열린 UI context 조립/병합/전달 허용 · #650 실제 JSON 소비 검증 유지다. 출처가 확인된 Django admin 및 Parler admin 계열의 고정 framework 슬롯에만 적용한다. `extra_context`/`context`의 받기·each_context·UI dict·copy/update·고정 UI 키 쓰기·framework render 전달과 연결된 private 전달 helper의 매개변수·반환·지역 context 주석을 허용한다. form/inline/media의 별도 조립은 context의 허용을 취소하지 않는다. 컨테이너 부재 처리와 request UI metadata의 담기·전달도 허용한다. 업무 읽기·비교·계산·상태 변경 또는 ORM/use case/업무 함수로의 값 전달은 실제 소비이므로 그 자리부터 기존 규칙을 적용한다. 출처나 소비가 미해소 또는 동적/재귀 호출로 escape한 연결 context는 후보로 남겨 확인한다. 이름만 context인 값·같은 함수의 별도 업무 dict·framework 고정 kwargs 밖 bare Any·admin 클래스/경로 전체는 면제하지 않는다. 생성 private helper는 본문이 없으므로 정확히 결합된 열린 dict 슬롯의 #645/#647만 S1 미검증으로 보고하고 G2에서 실제 소비 흐름으로 다시 판단한다.
+- **파일 계획 정규 블록**: `<!-- machine: file-plan -->` 마커 + ```paths 펜스. 1행 = `<태그> <경로>`(태그 선행·공백 구분·경로는 project-relative — 태그는 `add|update|remove[@Ln]|empty`)이고 `#` 주석만 허용한다. 브레이스 전개·`·` 병렬·`*`/`…` 축약·미해소 `<placeholder>`·승격 폴더 표기(경로는 언제나 `<칸>.py` — 동명 폴더 승격은 구현 캐스케이드 소유)·**동일 경로의 태그 이중 서술**은 전부 형식 위반이다(이중 서술은 파서 결정 불능을 낳는다). glyph 트리 삽화를 남기려면 블록에서 렌더해 생성하거나 파서의 삽화↔블록 차분 판정을 받는다 — 같은 계획의 이중 표현이 서로 어긋나는 드리프트 축을 봉쇄한다. **태그의 뜻은 기준선 기준이다**(G1 시점 HEAD — Phase 2 재발화 시 `--base` 기준선 · 2026-09-03 차단 승격): `add` = 기준선에 없는 경로(실존하면 형식 red «add 충돌») · `update` = 기준선에 실존하는 경로(부재면 형식 red «update 대상 부재» — 그 경로는 `add` 로 적는다 · 유효 승격 형태 `<칸>/__init__.py` ∧ `<칸>/<칸>.py` 의 기준선 실존은 실존이다) · `remove[@Ln]` = 기준선 실존 경로(비후행 remove 의 부재는 형식 red «remove 대상 부재» — 예외 없음 · 후행 `@Ln` 은 판정 밖 · `--base` 기준선은 이동하지 않으므로(재발화 판형 ②) 기실현 remove 는 실존이다 · 기준선에도 없는(승인 전에 이미 지워진) 경로는 remove 행을 거둔다) · `empty` = 새 빈 파일(add 와 같은 «새 파일» 태그 — 기준선 실존이면 형식 red «empty 충돌» · 기실현이면 `update`). 구형 명세에 블록을 소급 작성할 때 기실현 경로는 전부 `update` 다 — 실체화 0도 적법하며 선언 검증은 계속 수행한다(`add` 를 `update` 로 바꿔 red 를 피하는 것은 형식 red 로 잡힌다). 비후행 remove를 전사한 뒤 그 경로들의 조상 중 최종 사본에서 빈 부모 디렉터리만 정리한다(dirty overlay 선삭제 포함). 남은 파일(0B·init·미추적·add/empty 포함)이 있거나 후행 remove 실물이 남으면 보존하며, 무관한 빈 디렉터리와 symlink 경유 경로는 정리하지 않는다. 폴더 정리는 파일 실체화 건수와 별도로 보고한다 — 파일 실효 조치가 없어도 선언 검증과 기존 실존 판정을 수행한 뒤 확정 없는 경우 skip한다. remove만 있는 BC를 신규 골격으로 다시 만들지 않는다.
+- **공개 심볼 표기**: 자리표시자 실현 파일의 **공개 심볼 전부**를 `<!-- machine: symbols -->` 마커 + ```symbols 펜스에 적는다(«대표 1회»가 아니라 전수다) — 1행 = `경로.py::Symbol(Base) {필드, …}`(Symbol 은 대문자 선두 또는 `_`+대문자 선두 — 주 계약이 참조하는 사설 보조 타입 `_Item` 도 적는다: 파서가 클래스로 분류하고 검사기의 사설 면제 판정 경로를 스텁이 그대로 탄다 · 소문자 선두는 함수다) · 메서드 행 `경로.py::Symbol.method(파라미터) -> 반환`(수신자는 무어노테이션 `self`/`cls` 에 한해 적어도·안 적어도 된다 — 실행기 파서가 정규화한다; 어노테이션 수신자는 중복 합성으로 형식 red 가 된다) · 필드 = `name: Type[ = default]` · `NAME = "literal"`(enum 멤버) · `name = <식>`(Django 필드 대입식 등)만 허용 — 타입도 값도 없는 bare 이름은 형식 red 다. Base 병기가 의무인 종류는 재량 목록이 아니라 **검사기 소스에서 기계 추출한 닫힌 목록**(소성물 `scripts/pregate_symbol_kinds.json` — rulepack 과 함께 재생성)이고, 명명규약으로 유도 가능한 생략은 **성문 유도표**(final.md §1 칸→베이스 결정표 — **아직 성문 전이다: 성문 전에는 생략 허용분이 공집합이라 전 심볼을 명기한다**) 등재분에 한한다 — 단 **값 축 유도 3행은 성문 등재됐다**(2026-09-02 · 3행째 2026-09-03): django_* `apps.py` 의 `name`(앱 폴더 전체 점 경로)/`label`(bc명) 정형, models/ 칸 `*Model` 의 `Meta.db_table`(`<bc>_<entity_snake>` — #630 유도 규칙), 그리고 마이그레이션 칸(`migrations/NNNN_*.py` — makemigrations 산출물 모양 #593: `Migration` 클래스 1 · `0001_` 만 `initial = True` · `migrations/__init__.py` 는 빈 파일)의 결손 보충. 이 결손은 실행기가 규약 상수로 보충하므로 규약대로라면 생략해도 된다(마이그레이션 칸은 file-plan `add` 만 적어도 된다 — symbols 전사가 있으면 전사 우선 · 규약 밖 값을 계획하면 반드시 기계 블록에 명기 — 산문 명기는 예보 표면 밖이다). **생략 = 규약 준수 확약**이다(생략분은 자동 정규화되어 위반 예보가 불능이 된다: 규약을 벗어날 계획이면 반드시 명기). published-language 칸(contract/·published_error)의 심볼은 **필드 목록**(`code` 필드 유무 포함)을 병기하고, **주 계약이 참조하는 보조·중첩 타입은 소속 파일을 명세가 명시**한다 — 안 박으면 coder 가 즉흥 배치해 예보·판정이 그 파일을 못 본다. **데코레이터·모듈 별칭도 symbols에 명시한다**: 클래스 행 뒤 `경로.py::Symbol @dataclass(frozen=True, slots=True, kw_only=True)`처럼 적는다(이름·속성 이름 또는 그 호출만 · 복수 행은 적은 순서대로 클래스 위에 전사 · 선행 클래스 없는 행은 형식 red). 이름/옵션/별칭은 원문 그대로이며 자동 dataclass 지정이나 import 추론은 없다 — `dataclass`·`dc.dataclass` 등 데코레이터와 모듈 별칭의 필요한 import는 boundary-imports에 명시한다. 모듈 별칭은 그 파일의 클래스/함수보다 먼저 `경로.py::alias 이름[: 타입] = 별칭식`으로 적는다. TYPE_CHECKING 분기는 `경로.py::alias[TYPE_CHECKING] _BookAdminBase: TypeAlias = admin.ModelAdmin[BookModel]` 다음에 `경로.py::alias[else] _BookAdminBase: type[admin.ModelAdmin] = admin.ModelAdmin`을 적는다(같은 파일·같은 이름의 인접한 유효 두 행, 주석/빈 줄 제외). 필요한 `TYPE_CHECKING`·`TypeAlias`·admin·모델 import는 boundary-imports에서 공급한다. 별칭은 단일 이름 Assign 또는 값 있는 AnnAssign이고 우변은 이름·속성·타입 첨자 및 그 내부 타입 표현식으로 한정한다(호출·복합문·클래스/함수 정의 불가). import 뒤 클래스 앞에 if TYPE_CHECKING/else와 두 대입의 어노테이션을 보존해 전사한다. 누락 분기·중복 별칭·다른 이름의 else·클래스/함수 뒤 별칭은 형식 red다. 비-add의 데코레이터·별칭 행도 문법을 검증하며 그 재료로 기존 본문을 바꾸지 않는다 — 완결된 별칭 이름만 update 자기 해소 근거이고 데코레이터 행만으로 이름을 선언하지 않는다. 미기재는 부재이며 산문에서 보충하지 않는다. 마이그레이션 정형이 무시하는 별칭 재료는 채널 메모로 병기한다. **update OHS 신규 함수 전사**: 표준 `open_host_service/<area>/<area>_service.py` 실물에 symbols로 명시한 신규 모듈 함수만 기존 본문 뒤에 전사한다. 기존 함수·클래스·별칭 본문 수정과 다른 update 칸의 본문 전사는 S5다. add/update의 명시 클래스·메서드·필드·별칭 선언은 별도로 보존해 효과/출처 결합 DTO의 선언 후상태를 검사한다. 이는 실물 클래스 본문을 덮어쓰지 않으며 본문 검증의 증명이 아니다. 기존 바인딩/새 함수/합성 helper 충돌, 전사할 신규 함수 없음, 실물 부재·승격 형태는 사유를 적고 미시뮬레이션으로 남긴다. 기존 본문을 대체하거나 checker에 선언 이름을 주입하지 않는다. 함수 본문은 계속 스텁이므로 G2 실검증을 대체하지 않는다.
+- **경계 import 표**: 검사기 판정에 관련되는 **경계 import 전부**를 `<!-- machine: boundary-imports -->` 마커의 ```imports 펜스(1행 = `<소비 파일>` + 탭 또는 공백 2+ + `<import 문 그대로>`)로 성문한다 — 타 BC OHS/contract·framework 공통만이 아니라, domain/contract 칸의 서드파티 라이브러리와 **테스트 파일의 경계 import 전부**(factories/타 급·타 BC OHS/published 계약 소비)까지. 파일별 전체 import 를 강제하는 것은 아니다 — **경계란 세 가지다**: ⑴ BC 밖(타 BC OHS/contract·framework 공통·서드파티·테스트 재료) ⑵ BC 안의 층 경계 중 **층 규율 검사기가 금지·예외 항목으로 판정하는 것**(driving 잎 → `application_layer/port/**` · domain → 상위 층 등 #92~#96·#185/#186 의 항목 — 잎이 port 예외를 잡을 계획이면 그 import 행을 그대로 적어 G1 에서 #93 예보를 받는다: 적을 수 없는 설계가 드러나는 것이 이 채널의 목적이다) ⑶ 그 밖은 구현 재량(성문 불요). 산문에만 적힌 경계 import 는 예보 표면 밖이다(pre-gate 보고 헤더의 사각 목록 S3). **각 행은 실행기가 격리 사본(기준선 + dirty overlay + 이 명세의 add)에서 3단 실존 판정**(⑴ 모듈 실존 · ⑵ 자리표시자 아님 · ⑶ 이름 최상위 정의)을 받는다(2026-09-03) — 저장소 밖(표준·서드파티)은 검사 밖, 이 명세가 add 하는 대상은 자기 해소(symbols 채널 소관 — 승격 폴더 부품 포함), ⑵ 는 이름 import(`from M import n`)의 대상 M 이 모듈일 때만이다. file-plan `update` 대상(사본에 실물이 있을 때만 — 기준선 부재 update 는 형식 red 로 먼저 서고, 유효 승격 형태 예외로 통과한 대상만 update 로는 생기지 않으므로 ⑴ 모듈 부재)의 이름은 그 칸의 symbols 에 선언하면 «자기 update 해소»이고 미선언이면 현재 표면에 있을 때만 실존 확인·아니면 판정 불능이다(표면은 이 명세 이후 상태 — update 로 새 심볼을 낼 계획이면 symbols 에 적는다 · ⑵⑶ 비적용). 판정 기준은 **이 브랜치**다 — 다른 워크트리·미머지 브랜치의 실물은 보지 않는다(부재 = «계약 실존 결손»으로 예보 · 소비자가 `update` 여도 행은 판정된다). 상류 소유 계약을 소비할 계획이면 그 행을 **그대로 적는다** — 결손 예보가 선행 조건의 기계 표현이며, 행을 빼서 green 을 만드는 것은 채널 은폐(경계 import 전수 의무 위반)다. 신규 함수가 전사되는 update OHS 서비스는 명시 boundary-imports도 충돌 없이 추가 가능한 경우에만 함께 전사한다. 기존 바인딩을 다른 출처로 덮는 등 안전한 합성이 불가하면 해당 서비스 전사를 통째로 보류하고 S5 사유를 보고한다. 행 전부를 대상으로 하는 기존 계약 실존/S′ 판정은 이 전사 여부와 별개로 유지한다. S3의 물리 import 전사 범위와, 명시 import·별칭·타입으로 출처를 결합하는 선언 검증은 구별한다. 나머지 update 본문은 미검증이다.
+- **물리 신호 어노테이션**: 영구 테스트 입장 표의 `owner/path` 셀 안에 정형 어노테이션 `[markers: django_db,…] [base: TestCase] [client: yes]` 를 단다 — 테스트 물리 신호(마커·베이스·클라이언트)의 유일한 전사 채널이다. **add 무기재 = 물리 신호 없음, update markers 무기재 = 기존 상태 유지**다. update의 `[markers:]`는 빈 목록, `[markers: slow]` 등은 module pytestmark 최종 목록의 교체다. 정적 Assign/AnnAssign/list/tuple·pytest 별칭을 지원하며 함수/class decorator·본문은 보존한다. 호출형·동적/중복/조건부/증분/subscript 변경·재바인딩 또는 update nodeid/class 주소는 S5다. update base/client는 미지원 S5이며 marker 후상태 성공이 본문 검증을 뜻하지 않는다. 입장 표 header 는 영문 정본 6열(`candidate | protected contract/evidence | unique production failure | existing authoritative coverage | decision | owner/path`)로 고정하고 셀 안에 raw `|` 를 두지 않는다 — 열 구조가 곧 파서 계약이라, 열이 흔들리면 어노테이션 채널이 통째로 죽는다. owner/path에서 처음 나오는 Python 파일 주소(`경로.py` 또는 `경로.py::case`)가 그 행의 artifact다. code span과 bare 경로 모두 허용하며 앞선 `add` 같은 비경로 span은 건너뛴다. case 접미는 파일 주소 결합에서만 벗긴다(case 본문 전사 아님). 첫 파일 주소를 file-plan의 정확한 add/update 키에 결합하고, 뒤의 support/coverage 주소에는 신호를 전파하지 않는다. 첫 주소가 미등재·비-add/update여도 뒤 파일로 넘어가지 않는다.
 - **예외 번역표 기계 블록**: 이 명세가 이미 요구하는 예외 번역 산출물(도메인→published 매핑)을 `<!-- machine: exception-map -->` 마커의 ```exceptions 펜스(1행 = `<published 예외>` + 탭 또는 공백 2+ + `<raise 창구 파일>`)로 성문한다 — 번역표에 없는 published 예외는 어느 창구도 raise 하지 않는 «죽은 계약»으로 예보된다. add 창구 외에는, 명시 신규 함수가 실제 전사된 update OHS 서비스 파일에 한해 같은 파일 수준 raise helper로 전사한다. exception-map은 함수 주소가 아니므로 특정 함수의 raise 위치를 증명하지 않는다. 신규 함수가 없는 update 본문 변경과 산문에만 적힌 raise는 계속 S5이며, contract 안의 raise 진탐을 면제하지 않는다.
 
 ## 리뷰 반영·충돌 중재
 <!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->
 
 Coordinator가 독립 리뷰어(ddd/api/db) 노트를 모아 전달하면:
 
 - 타당한 지적을 명세에 반영한다 — 반영·수정은 **해당 절을 제자리에서 고쳐 쓰는 것**이다. "G1 확정 요약 / G1' 보강 / G2 정정" 같은 게이트별 메타 요약 블록을 명세 위에 덧쌓지 마라(명세는 현재 상태만; 결정 이력은 Coordinator 대화·게이트 배너가 가짐). *왜* — 누적 블록은 본문과 어긋나 사후 정합 정정 비용을 낳는다.
 - 리뷰어 간 충돌(예: api 응답 형태 ↔ db 정규화)은 네가 **중재**해 명세에 결정과 근거를 명시한다.
 - 스스로 해소 못 하는 트레이드오프는 명세에 옵션으로 남겨 Coordinator가 G1에서 사용자에게 제시하게 한다.

```

## codex-dddjango/skills/dddjango-design-architect/SKILL.md

Before SHA256: 0ad014276cd8e97293b637421f7608b6c756035754189057bfc386e713c06ea9
After SHA256: 7ae9c454bc3fcb8b4156d79207f2b50e5a5dd081fbb9a9e75de9681e24ea5ba7

```diff
--- before/codex-dddjango/skills/dddjango-design-architect/SKILL.md
+++ after/codex-dddjango/skills/dddjango-design-architect/SKILL.md
@@ -41,21 +41,21 @@
 
 1. **`contract scope`**: 프로젝트의 모든 API surface별 profile, API instance/namespace/version/public·internal 구분, scope 전체 BC와 그중 public BC error가 있는 error-BC subset, API/controller/URLconf/registrar/error/common module의 project-relative 경로, consumer·OpenAPI evidence, module sharing을 열거한다. repository artifact에는 project-relative 경로가 필수이고, greenfield artifact에는 명시적인 planned project-relative 경로를 쓰며, 없거나 적용되지 않는 항목은 그렇게 명시한다. planned 경로는 **이번 delivery가 승인 스코프 안에서 새로 만드는** artifact 전용이다 — 기존 artifact는 관찰된 실제 경로(legacy 위치 포함)로 적고, 타 BC의 표준 경로를 planned로 적지 않는다(2026-08-13).
 2. **`scope evidence`**: 위 inventory 각 행의 repository module/artifact에는 project-relative 경로와 관찰 내용을 기록한다. external consumer·사용자 발언·runtime-generated OpenAPI에는 stable external evidence identifier와 관찰을 쓸 수 있고, planned artifact는 아직 존재하지 않아도 slot 1의 planned 경로로 입증한다. 같은 profile의 common/error 재사용은 한 행으로 dedupe한다. mixed-profile shared module이나 한 source의 multiple API instances 때문에 surface/profile/sharing/contract 대응이 실제로 모호·상충하거나 inventory가 끝내 불완전할 때만 `STOP_FOR_USER_APPROVAL`로 보낸다. evidence가 external이거나 planned artifact가 아직 없다는 이유만으로 멈추지 않는다. inventory와 표준 트리의 불일치는 이동 지시가 아니라 관찰 기록이다.
 3. **`error profile`**: scope마다 `dddjango-code-json | preserve-established` 중 하나와 선택 근거를 쓴다. RFC 9457 wire가 관찰됐다면 `preserve-established`의 profile-native 계약으로 보존할 수 있지만 파일명이나 dependency 유무는 근거가 아니다. preserve scope는 code-profile artifact와 격리한다.
 4. **`compatibility/rollout`**: 지원 consumer와 현재 wire·OpenAPI·test 계약, 배포된 code 변경의 breaking 여부, 동시 migration 또는 version split, deprecation/Sunset과 종료 근거를 기록한다. 현재 승인된 제품 명세나 명시적 사용자 승인 없이 기존 계약을 끝내거나 바꾸지 않는다.
 5. **`common FrameworkErrorSchema action`**: `dddjango-code-json`이면 `reuse | create | approved-change` 중 하나이며 `none`은 금지한다. `approved-change`는 명시적 사용자 승인 evidence를 함께 기록하고, 없으면 `STOP_FOR_USER_APPROVAL`이다. `preserve-established`이면 관찰된 profile-native common/canonical error artifact의 action 또는 evidence가 있는 `none | not applicable`을 기록하고 common `ErrorSchema`을 새로 강제하지 않는다.
 6. **`common FrameworkErrorSchema shape/approval`**: `dddjango-code-json`이면 plugin 기본 property 없이, 기존 scope는 관찰된 common `ErrorSchema`을 기준선으로 삼고 신규 scope는 제안한 exact field set과 각 type·required/default/nullable·Field metadata·model config/legacy Config·validator/serializer/computed field/Pydantic hook inventory와 effective semantics·wire 직렬화, 어느 field를 BC ErrorCode로 좁힐지, project-relative canonical path를 기록한다. 신규 shape 생성과 현재 기준선의 property·type·존재성·변환 규칙·의미 변경은 일반 G1 승인과 분리해 명시적 사용자 승인을 받아야 한다. 변경이면 slot 5가 `approved-change`이고 이 slot에 별도 승인 evidence가 있어야 G1을 완료할 수 있다. `preserve-established`이면 관찰된 profile-native wire/media type/schema/handler shape와 approval evidence 또는 `none | not applicable`을 기록한다. 관찰된 RFC/schema/handler를 보존할 수 있지만 새 recipe로 일반화하지 않는다.
 7. **`BC error module`**: `dddjango-code-json`이면 error-BC별 side-effect-free module 경로와 common import를 기록하며 public BC error가 없는 BC만 `none`일 수 있다. `preserve-established`이면 관찰된 profile-native module/handler artifact 또는 evidence가 있는 `none | not applicable`을 기록하고 BC error module을 강제하지 않는다.
 8. **`BC ErrorCode`**: `dddjango-code-json`이면 error-BC별 단일 string Enum과 최소한의 literal public code 목록을 기록하며 public BC error가 없는 BC만 `none`일 수 있다. `preserve-established`이면 관찰된 profile-native code taxonomy/Enum artifact 또는 evidence가 있는 `none | not applicable`을 기록하고 `BC ErrorCode`를 강제하지 않는다.
 9. **`BC ErrorSchema`**: `dddjango-code-json`이면 error-BC별 common shape를 따르며 slot 6이 지정한 식별자 field 하나를 해당 BC `ErrorCode`로 좁힌 base Schema와 경로를 기록하고 public BC error가 없는 BC만 `none`일 수 있다. 좁힌 식별자 field는 공통의 default를 잃어 required여도 canon이다(식별자 field 한정·ErrorCode 좁힘 동반일 때만 — 2026-08-15). `preserve-established`이면 관찰된 profile-native status-specific schema/response artifact 또는 evidence가 있는 `none | not applicable`을 기록하고 `BC ErrorSchema`을 강제하지 않는다.
-10. **`prepared error mapping`**: `dddjango-code-json`이면 concrete domain/application exception 또는 조회의 `None` → no-arg concrete `ErrorSchema`, 또는 event-specific 값으로 명시적으로 채운 BC base `ErrorSchema` → controller의 direct `Status(<승인된 HTTP status 표현>, error)` chain과 각 output의 slot-6 exact literal body/approved header를 표로 기록한다. internal failure type과 output object를 명확히 구분한다. 여러 internal failures가 하나의 public ErrorCode로 수렴할 수 있다. raw infra failure는 기본 500이고, 승인된 안정적 public meaning이 있을 때만 consuming BC의 internal exception으로 정규화한 뒤 `ErrorSchema`을 만든다. `preserve-established`이면 관찰된 profile-native preparation/mapping artifact·behavior 또는 evidence가 있는 `none | not applicable`을 기록하고 code-profile chain을 강제하지 않는다.
+10. **`prepared error mapping`**: `dddjango-code-json`이면 concrete domain/application exception 또는 조회의 `None` → no-arg concrete `ErrorSchema`, 또는 event-specific 값으로 명시적으로 채운 BC base `ErrorSchema` → controller의 direct `Status(<승인된 HTTP status 표현>, error)` chain과 각 output의 slot-6 exact literal body/approved header를 표로 기록한다. internal failure type과 output object를 명확히 구분한다. 여러 internal failures가 하나의 public ErrorCode로 수렴할 수 있다. 이미 잡은 IntegrityError의 승인된 알려진 제약 실패는 구체 계약 예외로, 나머지는 승인된 일반 저장소 실패 계약으로 번역한다. repository 실패 계약은 domain 소유, capability port 실패 계약은 해당 port 소유다. 이 내부 정규화는 공개 HTTP 오류 승인이 아니므로 일반 저장소 실패의 외부 응답은 기존 safe 500을 유지한다. 새 ErrorCode/ErrorSchema/4xx/503을 만들지 않는다. 잡지 않은 unknown 인프라 오류를 새로 catch-all하지 않는다. 안정된 public meaning이 별도로 승인된 경우에만 그 외부 계약에 맞는 controller mapping을 한다. 이미 선언된 계약 예외의 관찰 후 재던짐은 허용한다. `preserve-established`이면 관찰된 profile-native preparation/mapping artifact·behavior 또는 evidence가 있는 `none | not applicable`을 기록하고 code-profile chain을 강제하지 않는다.
 11. **`controller mapping`**: `dddjango-code-json`이면 slot 10의 internal failure 형태에 따라 두 path 중 하나를 명시한다. exception path는 endpoint별 input preparation 뒤 정확히 한 번의 application call만 narrow `try`에 두고 승인된 concrete exception 또는 exception tuple만 catch한다. `None` path는 조회 use case가 대상이 없어 `None`을 돌려주는 경우에만 고르고, artificial `try`/`catch` 없이 application call을 정확히 한 번 실행한 뒤 그 직후 `is None` branch하며 exception을 fabricate하거나 raise하지 않는다. 실패가 둘 이상이거나 사유가 있으면 exception path다 — 실패를 Result variant·outcome 값으로 설계하지 않는다(`<use_case>_result.py`엔 성공 한 벌만 — #571). 두 path 모두 승인된 no-arg concrete 또는 event-specific 값으로 채운 BC-base `ErrorSchema`을 만들고, 승인된 header를 주입된 응답용(temporal) Django `HttpResponse`에 설정한 뒤 two-argument `Status(<literal/status constant 또는 slot-6 body field>, error)`를 직접 return한다. `status` body property를 발명하지 않는다. error helper/handler/factory/serializer/table 또는 mapping 추출은 만들지 않는다. `preserve-established`이면 관찰된 profile-native controller/handler mapping 또는 evidence가 있는 `none | not applicable`을 기록하고 direct `Status`를 강제하지 않는다.
 12. **`response/OpenAPI/tests`**: `dddjango-code-json`이면 승인된 runtime HTTP status/body/header mapping, framework-owned status non-advertising, mounted client와 공개 generated OpenAPI의 관련 operation/status/schema 후보·기존 evidence를 기록하고 아래 영구 테스트 입장 표의 행을 참조한다. slot 6의 shape 및 별도 변경 승인은 보존하지만 Pydantic private metadata·validator 위치·framework 기본 직렬화를 자동 영구 테스트로 만들지 않는다. 별도 공개 Python consumer 계약은 HTTP와 다른 행으로 심사한다. `preserve-established`이면 관찰된 profile-native media type/fields/status-specific schema·handler와 test/OpenAPI evidence 또는 `none | not applicable`을 기록한다. framework-owned 오류 smoke와 auth/header 검증도 승인 계약·독자 failure가 있는 후보만 입장시키며 exact framework body snapshot을 요구하지 않는다. native download/stream/redirect와 schema-less 204는 선언 Schema 규칙의 carveout이다.
 
 `dddjango-code-json`의 framework-owned 오류는 401/403/route 404/422/429/general `HttpError`/unknown 500이며 BC `ErrorSchema`으로 변환하거나 `response`에 광고하지 않는다. 모든 Ninja profile의 인증 실패에서는 `None`을 return하거나 framework `AuthenticationError`를 raise한다. `AuthenticationError` object나 `ErrorSchema`을 return하지 않고 어느 것도 `request.auth`에 저장하지 않는다. 406과 415는 각각 별도 사용자 승인을 받은 경우에만 tested version-compatible Ninja-owned pre-body/framework `HttpError` 경로로 구현하며 함수형 `Router`나 전역 handler를 강제하지 않는다. `preserve-established`는 관찰된 framework error body/협상 behavior를 그대로 기록하고 code-profile artifact를 도입하지 않는다.
 
 - **도메인(ddd)**: 애그리거트 경계와 불변식, 상태 전이, 유비쿼터스 언어, 관련 도메인 이벤트 채택 여부와 근거.
 - **계약(api)**: 외부에서 관찰되는 엔드포인트·요청/응답 계약·상태 코드·에러 profile·멱등성 정책. (저장·전달 보장 같은 데이터 측면은 db lens로 넘긴다.) 유한 재시도/CAS의 실패 outcome도 경계에서 승인된 안정적 public meaning이면 `prepared error mapping`에 승인 HTTP status·slot-6 exact body·header로 포함한다. 어떤 internal failure를 같은 public ErrorCode로 수렴할지와 retryable 503+`Retry-After` 또는 409 선택은 멱등성·재시도 trade-off와 consumer 구분 필요로 결정해 §5/G1에 올리고 임의 확정하지 않는다. 승인된 안정적 public meaning이 없는 raw infra·미식별 예외는 framework 500으로 둔다. application·domain은 HTTP status/body를 만들지 않는다.
 - **API 스택**(lens 무관, 새 API 표면이 생기면 항상 결정): 외부에 노출되는 새 HTTP/JSON API surface가 있으면 stack을 명세의 1급 결정으로 박는다. 신규 표면(이번 delivery가 새로 노출하는 route/operation — endpoint 단위; 기존 배포 endpoint의 수정은 이 결정의 대상이 아니다 — `implementation-django-ninja` §2.3 touched 조항 관할)의 stack은, 확립 스택(이 작업이 관찰하는 저장소 상태에서 배포·소비 evidence로 확인되는 스택)이 없으면 Django Ninja가 무언 기본이고, 확립 DRF·plain Django 스택이 존재하면 **스택 결정 자체를 `STOP_FOR_USER_APPROVAL`로 표면화**한다(선택지마다 대가 한 줄 — 표준 Ninja 채택: 확립 리소스와의 2-스택 분열 | 확립 스택 답습: 옛 스택 답습은 규약이 아니라 빚). 관찰은 스택 «정체» 식별과 STOP 선택지의 재료이지 답습 «채택»의 확정 근거가 아니며, Ninja 기본에서 벗어나는 신규 표면 스택 결정은 사유를 불문하고(답습·인프라/의존성 실물 부재·비-JSON 반환 메커니즘 포함) 이 STOP 경로로만 확정한다. G0 스코프 메모·발주서에 기록된 사용자의 명시적 스택 지시는 이 STOP 승인과 동격이다 — 명세는 그 기록(경로·인용)을 스택 결정 근거로 인용하고, 인용 가능한 명시 기록이 없으면 STOP이다(승인 효력은 그 발주의 명세에 한한다). 이 결정의 대상은 새 HTTP/JSON API surface뿐이다 — server-render HTML 표면(아래 HTML 문장·`implementation-django-web` §11 관할)·admin·정적 자원은 대상이 아니다. 오류 **wire 계약** 보존(«계약 profile» 축 — preserve-established)은 별개 축이다 — 확립(배포된) 표면의 wire 보존은 그대로되, 신규 endpoint의 error profile은 12-slot `error profile` 기준으로 별도 결정하고(같은 공개 namespace 합류는 스택·컨트롤러 형태 답습의 근거가 아니다), 신규 Ninja 표면에 preserve wire를 지우는 조합은 게이트 미열거라 그 취급 결정을 G1에서 표면화한다(STOP). SSE·스트리밍·파일 반환 표면의 기본 대안은 클래스 컨트롤러의 framework-native 반환(`implementation-django-ninja` §2.2 carveout)이며, plain 채택 선택지가 성립하려면 carveout으로 표현 불가하다는 관찰 근거를 그 STOP 대가 줄에 기록한다. dependency가 아직 manifest에 없다는 사실만으로 plain으로 낮추거나 `preserve-established`로 바꾸지 않는다. 새 Ninja surface는 `NinjaExtraAPI` + `@api_controller` class controller(aggregate 단위)이고, 승인된 scope마다 profile에 맞는 project API instance 하나를 둔다. **composition(배선·등록)은 profile 무관 표준이다**(2026-08-12 라운드 1′): `auto_import=False`의 side-effect-free BC registrar(`register_<bc>_api`), URLconf의 explicit registrar call과 mount로 구성하며 import-time registration은 하지 않는다 — 기존 BC 의 배선 실물(`*_api_router.py` 동형)은 배선 결정의 입력이 아니고, preserve 를 배선 답습의 근거로 명세에 박지 않는다. 이 문장들은 **신규 산출물의 형태**를 정할 뿐 **기존 코드의 처분 권한**이 아니다 — 명세는 승인 스코프의 산출물 목록 밖 기존 파일의 이동·개명·재배선을 결정으로 박지 않는다: 기존 코드의 처분은 G0 빚 결정(ⓐ/ⓑ)이 확정하고 명세는 ⓐ 승인 항목만 슬라이스 0으로 옮겨 적는다(2026-08-13 라운드 2 실증 — 명세가 «canonical 이관·면제 없음»을 자가 결정으로 박자 11 BC 100파일이 이동됐다). BC `composition_root/`(`dependency_wiring.py`의 `build_*` 팩토리 — final.md §1 트리 2~4행)가 DI만 소유한다. Controller는 one-statement application call에서 concrete domain/application exception을 catch하거나 조회의 `None`을 처리하고, no-arg concrete `ErrorSchema` 또는 event-specific 값으로 명시적으로 채운 BC base `ErrorSchema`을 만든 뒤 직접 `Status(<승인된 HTTP status 표현>, error)`를 반환한다. internal failure type과 output object를 명확히 구분하고 error handler/helper/factory/serializer로 빼지 않는다. `preserve-established`이면 관찰된 profile-native controller/handler/schema behavior를 보존하며 code-profile output/direct-`Status` recipe를 도입하지 않는다(보존 대상은 **오류 wire 산출물**까지 — registration/composition·트리·import 방향은 위 표준 그대로다). 성공 응답은 선언한 2xx `response` schema의 `Status`/schema 객체를 반환하고, 입력은 선언적 `payload: Schema`로 받는다. 406/415를 승인한 경우에도 tested version-compatible Ninja-owned pre-body/framework `HttpError` path를 쓰며 함수형 `Router`를 강제하거나 operation에서 raw body를 수동 parsing하지 않는다. **새 surface가 server-render HTML view면**(JSON API 아님) service의 domain/application exception은 view-local form re-render+`messages.error`(200), infra/unknown exception은 project `handler500`+`500.html`(`request`-only·empty Context), 승인된 transient contract는 `process_exception` retryable 503으로 표현하고 출처별 책임을 명세한다(`implementation-django-web` §11).
 - **데이터(db)**: 스키마 변화, 인덱스·제약, 트랜잭션 경계·격리·락 전략(`architecture-db` §9.5·§9.6 Risky Write), 마이그레이션 안전(rollout/backfill). **Risky Write(주문·결제·재고·예약·환불·권한·ledger 등 중복·race가 치명적인 쓰기)면 `architecture-db` §9.6 Risky Write Consistency Block을 *8행으로(표 또는 행 단위 블록) 명세에 박는다* — §9.6을 번호로 인용만 하지 말고 8행을 채운다: Transaction owner·Locking strategy·Rule ownership·Idempotency storage·API handoff·Side-effect timing·Isolation/retry·Test criteria. 각 행에 결정 내용을 적고, 해당 없으면 근거와 함께 '미적용'으로 둔다. ⚠ 스코프 가드 — Idempotency storage 행: 사용자가 멱등성(`Idempotency-Key`)을 요청하지 않았으면 이 행을 *silent하게 필수 서브시스템으로 빌드하지 않는다*: 기본은 '미적용'(알려진 한계)으로 명세에 *현재 상태로 commit*하고, 이를 **배너 override 항목**으로 함께 산출한다 — 별도 '미해결 옵션' 블록으로 열어두지 않는다. 사용자가 미적용을 수락하면 명세 재작성이 불필요하고, G1에서 채택을 택하면 코디네이터가 G1 override 입력으로 너를 재호출하니 그때 `architecture-api` §13대로 구현한다. 미요청 멱등성을 명세에 silent 의무로 박는 건 스코프 초과다(같은 원리로, scope.md가 '범위 아님 / 필요 시 G1 제안'으로 명시한 다른 견고성 결정도 기본 '미적용' commit + 배너 override 항목으로 산출한다 — architect가 'Y감이냐'를 판정하지 않고 scope.md의 그 목록을 앵커로 쓴다). Test criteria 행엔 concurrent request·oversell 등 동시성 검증 기준을 포함한다.** 바로 아래 엔진별 락·동시성 확정은 이 블록의 `Locking strategy`·`Isolation/retry` 행을 *채우는 근거*이지 블록을 대체하지 않는다. **락·동시성이 걸린 Risky Write는 개발(sqlite)·운영(Postgres) 엔진별 동작 차이까지 명세에서 확정한다** — 예: sqlite `select_for_update` no-op·DEFERRED begin 데드락 → 환경 무관 방어는 CHECK(불변식 백스톱)+낙관적 `version`/CAS 조건부 UPDATE이되 `WHERE`엔 경합 가드만 담고 비즈니스 판정(예: `stock>=qty`)은 인프라로 옮기지 않는다 — 판정·불변식은 도메인 애그리거트(또는 도메인 서비스)가 소유하고 프로덕션 경로에서 실행, 응용 서비스는 조회→도메인 메서드→영속화, repo는 결과만 저장(판정을 SQL·ORM으로 복제하면 빈혈, 원칙 `dddjango-architecture-ddd` §3.2, 메커니즘 §9.5). 직렬화 필요 시 begin 모드 명시(§9.5). *왜* — coder는 한 환경만 보므로(coder 「경계」) 엔진차 락 공백을 구현에서 메우면 G1' 설계 반송이 된다.
 - **Test criteria admission**: Risky Write·outbox·제약·동시성의 Test criteria는 위험과 candidate를 드러내는 설계 입력이다. 각 영구 테스트는 아래 입장 표에서 DB 보장 근거, 독자 failure mechanism, 기존 coverage를 따로 판정하며 Test criteria 행 자체가 `add`를 자동 결정하지 않는다.
@@ -71,25 +71,27 @@
 
 - **영구 테스트 입장 표**(lens 무관, 항상 작성): 이번 변경과 관련된 모든 영구 test artifact의 `add/update/move/split/rename/remove/weaken` 및 의미 보존 재조직 후보를 다음 최소 열로 한 행씩 판정한다.
 
   | candidate | protected contract/evidence | unique production failure | existing authoritative coverage | decision | owner/path |
   |---|---|---|---|---|---|
 
   decision은 `add/update/reuse/retain/remove/reject/pending` 일곱 값만 쓴다. `pending`은 리뷰 뒤 0개여야 G1을 요청할 수 있고, `reuse`·`reject`는 test artifact write가 0이다. 일반 `retain`은 무편집이며, 명시적으로 승인한 의미 보존 move/split/rename/reorganization만 새 case·assertion·Red 없이 전후 같은 계약과 failure를 보호한다고 기록한다. `remove/weaken`에는 적용 가능한 support·deprecation/Sunset·rollout·영속 데이터/이벤트 종료 근거와 exact target을 적는다. framework/private/test-tool mechanics는 그 자체로 `reject` 방향이며, migration 파일·과거 state·forward/reverse 자체를 인수 기준으로 만들지 않는다. 기존 테스트나 현재 구현은 조사 증거일 뿐 현재 계약을 대신하지 않는다. 후보가 없으면 열을 유지한 빈 표와 `후보 없음`을 쓴다.
 
   입장 표와 별도로 현재 계약의 유지·변경·종료·부재 의무를 짧게 설명해 각 행의 근거를 추적 가능하게 한다. 순수 구현 버그 수정도 관련 기존 coverage와 독자 failure를 판정해 `reuse/retain/add` 중 하나로 기록하며, 단순히 `테스트 계약 변화 없음`으로 심사를 생략하지 않는다.
 
-- **기계가독 채널(machine blocks)**(lens 무관, 항상 작성 — 12-slot 부재가 적법한 레인에서도 아래 블록·입장 표 규율은 상시다): 명세의 파일 계획·공개 심볼·경계 import·물리 신호·예외 번역은 산문 서술과 «별개로» 아래 다섯 정본 문법으로 성문한다 — pre-gate(`design_pregate.py`)는 이 채널만을 전사 재료로 쓰고 산문에서 추론하는 재료는 0이다. **채널에 없으면 «부재»로 전사된다(fail-closed)** — 부재가 위반이면 red 가 나는 것이 정답이다(예: 마커 무기재 → «설계가 물리 신호를 안 정했다»는 진탐). `<!-- machine: … -->` 마커는 **concrete 계획 블록에만** 단다 — 표준 140행 템플릿·예시 인용에 달지 않는다(인용과 실계획의 구별이 파서의 유일한 판별 근거다). *왜* — 21레인 실측에서 파일 계획 방언이 6종이라, 형식 규범 없이는 어떤 결정적 파싱도 성립하지 않았다.
-- **파일 계획 정규 블록**: `<!-- machine: file-plan -->` 마커 + ```paths 펜스. 1행 = `<태그> <경로>`(태그 선행·공백 구분·경로는 project-relative — 태그는 `add|update|remove[@Ln]|empty`)이고 `#` 주석만 허용한다. 브레이스 전개·`·` 병렬·`*`/`…` 축약·미해소 `<placeholder>`·승격 폴더 표기(경로는 언제나 `<칸>.py` — 동명 폴더 승격은 구현 캐스케이드 소유)·**동일 경로의 태그 이중 서술**은 전부 형식 위반이다(이중 서술은 파서 결정 불능을 낳는다). glyph 트리 삽화를 남기려면 블록에서 렌더해 생성하거나 파서의 삽화↔블록 차분 판정을 받는다 — 같은 계획의 이중 표현이 서로 어긋나는 드리프트 축을 봉쇄한다. **태그의 뜻은 기준선 기준이다**(G1 시점 HEAD — Phase 2 재발화 시 `--base` 기준선 · 2026-09-03 차단 승격): `add` = 기준선에 없는 경로(실존하면 형식 red «add 충돌») · `update` = 기준선에 실존하는 경로(부재면 형식 red «update 대상 부재» — 그 경로는 `add` 로 적는다 · 유효 승격 형태 `<칸>/__init__.py` ∧ `<칸>/<칸>.py` 의 기준선 실존은 실존이다) · `remove[@Ln]` = 기준선 실존 경로(비후행 remove 의 부재는 형식 red «remove 대상 부재» — 예외 없음 · 후행 `@Ln` 은 판정 밖 · `--base` 기준선은 이동하지 않으므로(재발화 판형 ②) 기실현 remove 는 실존이다 · 기준선에도 없는(승인 전에 이미 지워진) 경로는 remove 행을 거둔다) · `empty` = 새 빈 파일(add 와 같은 «새 파일» 태그 — 기준선 실존이면 형식 red «empty 충돌» · 기실현이면 `update`). 구형 명세에 블록을 소급 작성할 때 기실현 경로는 전부 `update` 다 — 실체화 0 이 나오면 그것이 정답이다(`add` 를 `update` 로 바꿔 red 를 피하는 것은 형식 red 로 잡힌다). 비후행 remove를 전사한 뒤 그 경로들의 조상 중 최종 사본에서 빈 부모 디렉터리만 정리한다(dirty overlay 선삭제 포함). 남은 파일(0B·init·미추적·add/empty 포함)이 있거나 후행 remove 실물이 남으면 보존하며, 무관한 빈 디렉터리와 symlink 경유 경로는 정리하지 않는다. 폴더 정리는 파일 실체화 건수와 별도로 보고한다 — 파일 실효 조치가 없으면 기존 실존 판정 뒤 skip한다. remove만 있는 BC를 신규 골격으로 다시 만들지 않는다.
-- **공개 심볼 표기**: 자리표시자 실현 파일의 **공개 심볼 전부**를 `<!-- machine: symbols -->` 마커 + ```symbols 펜스에 적는다(«대표 1회»가 아니라 전수다) — 1행 = `경로.py::Symbol(Base) {필드, …}`(Symbol 은 대문자 선두 또는 `_`+대문자 선두 — 주 계약이 참조하는 사설 보조 타입 `_Item` 도 적는다: 파서가 클래스로 분류하고 검사기의 사설 면제 판정 경로를 스텁이 그대로 탄다 · 소문자 선두는 함수다) · 메서드 행 `경로.py::Symbol.method(파라미터) -> 반환`(수신자는 무어노테이션 `self`/`cls` 에 한해 적어도·안 적어도 된다 — 실행기 파서가 정규화한다; 어노테이션 수신자는 중복 합성으로 형식 red 가 된다) · 필드 = `name: Type[ = default]` · `NAME = "literal"`(enum 멤버) · `name = <식>`(Django 필드 대입식 등)만 허용 — 타입도 값도 없는 bare 이름은 형식 red 다. Base 병기가 의무인 종류는 재량 목록이 아니라 **검사기 소스에서 기계 추출한 닫힌 목록**(소성물 `scripts/pregate_symbol_kinds.json` — rulepack 과 함께 재생성)이고, 명명규약으로 유도 가능한 생략은 **성문 유도표**(final.md §1 칸→베이스 결정표 — **아직 성문 전이다: 성문 전에는 생략 허용분이 공집합이라 전 심볼을 명기한다**) 등재분에 한한다 — 단 **값 축 유도 3행은 성문 등재됐다**(2026-09-02 · 3행째 2026-09-03): django_* `apps.py` 의 `name`(앱 폴더 전체 점 경로)/`label`(bc명) 정형, models/ 칸 `*Model` 의 `Meta.db_table`(`<bc>_<entity_snake>` — #630 유도 규칙), 그리고 마이그레이션 칸(`migrations/NNNN_*.py` — makemigrations 산출물 모양 #593: `Migration` 클래스 1 · `0001_` 만 `initial = True` · `migrations/__init__.py` 는 빈 파일)의 결손 보충. 이 결손은 실행기가 규약 상수로 보충하므로 규약대로라면 생략해도 된다(마이그레이션 칸은 file-plan `add` 만 적어도 된다 — symbols 전사가 있으면 전사 우선 · 규약 밖 값을 계획하면 반드시 기계 블록에 명기 — 산문 명기는 예보 표면 밖이다). **생략 = 규약 준수 확약**이다(생략분은 자동 정규화되어 위반 예보가 불능이 된다: 규약을 벗어날 계획이면 반드시 명기). published-language 칸(contract/·published_error)의 심볼은 **필드 목록**(`code` 필드 유무 포함)을 병기하고, **주 계약이 참조하는 보조·중첩 타입은 소속 파일을 명세가 명시**한다 — 안 박으면 coder 가 즉흥 배치해 예보·판정이 그 파일을 못 본다. **데코레이터·모듈 별칭도 symbols에 명시한다**: 클래스 행 뒤 `경로.py::Symbol @dataclass(frozen=True, slots=True, kw_only=True)`처럼 적는다(이름·속성 이름 또는 그 호출만 · 복수 행은 적은 순서대로 클래스 위에 전사 · 선행 클래스 없는 행은 형식 red). 이름/옵션/별칭은 원문 그대로이며 자동 dataclass 지정이나 import 추론은 없다 — `dataclass`·`dc.dataclass` 등 데코레이터와 모듈 별칭의 필요한 import는 boundary-imports에 명시한다. 모듈 별칭은 그 파일의 클래스/함수보다 먼저 `경로.py::alias 이름[: 타입] = 별칭식`으로 적는다. TYPE_CHECKING 분기는 `경로.py::alias[TYPE_CHECKING] _BookAdminBase: TypeAlias = admin.ModelAdmin[BookModel]` 다음에 `경로.py::alias[else] _BookAdminBase: type[admin.ModelAdmin] = admin.ModelAdmin`을 적는다(같은 파일·같은 이름의 인접한 유효 두 행, 주석/빈 줄 제외). 필요한 `TYPE_CHECKING`·`TypeAlias`·admin·모델 import는 boundary-imports에서 공급한다. 별칭은 단일 이름 Assign 또는 값 있는 AnnAssign이고 우변은 이름·속성·타입 첨자 및 그 내부 타입 표현식으로 한정한다(호출·복합문·클래스/함수 정의 불가). import 뒤 클래스 앞에 if TYPE_CHECKING/else와 두 대입의 어노테이션을 보존해 전사한다. 누락 분기·중복 별칭·다른 이름의 else·클래스/함수 뒤 별칭은 형식 red다. 비-add의 데코레이터·별칭 행도 문법을 검증하며 그 재료로 기존 본문을 바꾸지 않는다 — 완결된 별칭 이름만 update 자기 해소 근거이고 데코레이터 행만으로 이름을 선언하지 않는다. 미기재는 부재이며 산문에서 보충하지 않는다. 마이그레이션 정형이 무시하는 별칭 재료는 채널 메모로 병기한다. **update OHS 신규 함수 전사**: 표준 `open_host_service/<area>/<area>_service.py` 실물에 symbols로 명시한 신규 모듈 함수만 기존 본문 뒤에 전사한다. 기존 함수·클래스·별칭의 수정과 다른 update 칸은 S5다. 기존 바인딩/새 함수/합성 helper 충돌, 전사할 신규 함수 없음, 실물 부재·승격 형태는 사유를 적고 미시뮬레이션으로 남긴다. 기존 본문을 대체하거나 checker에 선언 이름을 주입하지 않는다. 함수 본문은 계속 스텁이므로 G2 실검증을 대체하지 않는다.
-- **경계 import 표**: 검사기 판정에 관련되는 **경계 import 전부**를 `<!-- machine: boundary-imports -->` 마커의 ```imports 펜스(1행 = `<소비 파일>` + 탭 또는 공백 2+ + `<import 문 그대로>`)로 성문한다 — 타 BC OHS/contract·framework 공통만이 아니라, domain/contract 칸의 서드파티 라이브러리와 **테스트 파일의 경계 import 전부**(factories/타 급·타 BC OHS/published 계약 소비)까지. 파일별 전체 import 를 강제하는 것은 아니다 — **경계란 세 가지다**: ⑴ BC 밖(타 BC OHS/contract·framework 공통·서드파티·테스트 재료) ⑵ BC 안의 층 경계 중 **층 규율 검사기가 금지·예외 항목으로 판정하는 것**(driving 잎 → `application_layer/port/**` · domain → 상위 층 등 #92~#96·#185/#186 의 항목 — 잎이 port 예외를 잡을 계획이면 그 import 행을 그대로 적어 G1 에서 #93 예보를 받는다: 적을 수 없는 설계가 드러나는 것이 이 채널의 목적이다) ⑶ 그 밖은 구현 재량(성문 불요). 산문에만 적힌 경계 import 는 예보 표면 밖이다(pre-gate 보고 헤더의 사각 목록 S3). **각 행은 실행기가 격리 사본(기준선 + dirty overlay + 이 명세의 add)에서 3단 실존 판정**(⑴ 모듈 실존 · ⑵ 자리표시자 아님 · ⑶ 이름 최상위 정의)을 받는다(2026-09-03) — 저장소 밖(표준·서드파티)은 검사 밖, 이 명세가 add 하는 대상은 자기 해소(symbols 채널 소관 — 승격 폴더 부품 포함), ⑵ 는 이름 import(`from M import n`)의 대상 M 이 모듈일 때만이다. file-plan `update` 대상(사본에 실물이 있을 때만 — 기준선 부재 update 는 형식 red 로 먼저 서고, 유효 승격 형태 예외로 통과한 대상만 update 로는 생기지 않으므로 ⑴ 모듈 부재)의 이름은 그 칸의 symbols 에 선언하면 «자기 update 해소»이고 미선언이면 현재 표면에 있을 때만 실존 확인·아니면 판정 불능이다(표면은 이 명세 이후 상태 — update 로 새 심볼을 낼 계획이면 symbols 에 적는다 · ⑵⑶ 비적용). 판정 기준은 **이 브랜치**다 — 다른 워크트리·미머지 브랜치의 실물은 보지 않는다(부재 = «계약 실존 결손»으로 예보 · 소비자가 `update` 여도 행은 판정된다). 상류 소유 계약을 소비할 계획이면 그 행을 **그대로 적는다** — 결손 예보가 선행 조건의 기계 표현이며, 행을 빼서 green 을 만드는 것은 채널 은폐(경계 import 전수 의무 위반)다. 신규 함수가 전사되는 update OHS 서비스는 명시 boundary-imports도 충돌 없이 추가 가능한 경우에만 함께 전사한다. 기존 바인딩을 다른 출처로 덮는 등 안전한 합성이 불가하면 해당 서비스 전사를 통째로 보류하고 S5 사유를 보고한다. 행 전부를 대상으로 하는 기존 계약 실존/S′ 판정은 이 전사 여부와 별개로 유지한다.
-- **물리 신호 어노테이션**: 영구 테스트 입장 표의 `owner/path` 셀 안에 정형 어노테이션 `[markers: django_db,…] [base: TestCase] [client: yes]` 를 단다 — 테스트 물리 신호(마커·베이스·클라이언트)의 유일한 전사 채널이다. **무기재 = «물리 신호 없음»으로 전사된다(fail-closed)** — 마커를 안 적으면 red 가 그 결손을 알린다. 입장 표 header 는 영문 정본 6열(`candidate | protected contract/evidence | unique production failure | existing authoritative coverage | decision | owner/path`)로 고정하고 셀 안에 raw `|` 를 두지 않는다 — 열 구조가 곧 파서 계약이라, 열이 흔들리면 어노테이션 채널이 통째로 죽는다. owner/path에서 처음 나오는 Python 파일 주소(`경로.py` 또는 `경로.py::case`)가 그 행의 artifact다. code span과 bare 경로 모두 허용하며 앞선 `add` 같은 비경로 span은 건너뛴다. case 접미는 파일 주소 결합에서만 벗긴다(case 본문 전사 아님). 첫 파일 주소를 file-plan의 정확한 add 키에 결합하고, 뒤의 support/coverage 주소에는 신호를 전파하지 않는다. 첫 주소가 미등재·비-add여도 뒤 파일로 넘어가지 않는다.
+- **기계가독 채널(machine blocks)**(lens 무관, 항상 작성 — 12-slot 부재가 적법한 레인에서도 아래 블록·입장 표 규율은 상시다): 명세의 파일 계획·공개 심볼·경계 import·물리 신호·예외 번역은 산문 서술과 «별개로» 기존 다섯 정본 문법으로 성문하고, 효과는 선택형 여섯 번째 입력으로 적는다 — pre-gate(`design_pregate.py`)는 이 채널만을 전사 재료로 쓰고 산문에서 추론하는 재료는 0이다. **채널의 무기재 의미를 구분한다** — add의 물리 신호 무기재는 부재로 전사하고, update marker 무기재는 현행 유지, 효과 무기재는 S5 미검증이다. 부재가 위반인 채널만 red다. `<!-- machine: … -->` 마커는 **concrete 계획 블록에만** 단다 — 표준 140행 템플릿·예시 인용에 달지 않는다(인용과 실계획의 구별이 파서의 유일한 판별 근거다). **명시 효과**는 `<!-- machine: use-case-effects -->` + ```effects 펜스에 `경로.py::UseCase read-only uow=none` 또는 `경로.py::UseCase write uow=<타입식>`으로 적는다. 어휘는 `read-only`/`write`, UoW는 `none` 또는 비어 있지 않은 타입식이며 add/update의 선행 클래스 선언에만 결합한다. 중복/상충·잘못된 어휘/타입식·선행 클래스 부재는 형식 red다. 명시 read-only+UoW와 출처가 확인된 UoW 주입의 모순은 선언 #197 확정, 미해소 출처는 후보, write 효과의 주입 불일치는 채널 메모다. 출처 결합 DTO의 공개 Result/Out/Response에서 사설·중첩 타입과 명시 별칭·표준 컨테이너를 따라 확인한 aggregate/entity 누수는 선언 #202 확정이고 VO/shared VO는 허용한다. 이름만 같거나 동적/불명 출처는 후보이며 OHS에 domain import를 합성하지 않는다. 선언 확정은 architect·해당 설계 리뷰/감수자가 처분하고 후보는 확인 질문으로 남긴다. S2의 내부 모순 사각은 이 명시 효과·출처 결합 DTO 지원 밖에 남는다. S1 생성 본문 미검증은 실제 구현 검증을 대신하지 않는다.
+
+**admin context 판정**: #493 주석 존재 유지 · #645 framework 소유 슬롯 Any 제한 허용 · #646 제네릭 런타임 안전 유지 · #647 열린 UI context 조립/병합/전달 허용 · #650 실제 JSON 소비 검증 유지다. 출처가 확인된 Django admin 및 Parler admin 계열의 고정 framework 슬롯에만 적용한다. `extra_context`/`context`의 받기·each_context·UI dict·copy/update·고정 UI 키 쓰기·framework render 전달과 연결된 private 전달 helper의 매개변수·반환·지역 context 주석을 허용한다. form/inline/media의 별도 조립은 context의 허용을 취소하지 않는다. 컨테이너 부재 처리와 request UI metadata의 담기·전달도 허용한다. 업무 읽기·비교·계산·상태 변경 또는 ORM/use case/업무 함수로의 값 전달은 실제 소비이므로 그 자리부터 기존 규칙을 적용한다. 출처나 소비가 미해소 또는 동적/재귀 호출로 escape한 연결 context는 후보로 남겨 확인한다. 이름만 context인 값·같은 함수의 별도 업무 dict·framework 고정 kwargs 밖 bare Any·admin 클래스/경로 전체는 면제하지 않는다. 생성 private helper는 본문이 없으므로 정확히 결합된 열린 dict 슬롯의 #645/#647만 S1 미검증으로 보고하고 G2에서 실제 소비 흐름으로 다시 판단한다.
+- **파일 계획 정규 블록**: `<!-- machine: file-plan -->` 마커 + ```paths 펜스. 1행 = `<태그> <경로>`(태그 선행·공백 구분·경로는 project-relative — 태그는 `add|update|remove[@Ln]|empty`)이고 `#` 주석만 허용한다. 브레이스 전개·`·` 병렬·`*`/`…` 축약·미해소 `<placeholder>`·승격 폴더 표기(경로는 언제나 `<칸>.py` — 동명 폴더 승격은 구현 캐스케이드 소유)·**동일 경로의 태그 이중 서술**은 전부 형식 위반이다(이중 서술은 파서 결정 불능을 낳는다). glyph 트리 삽화를 남기려면 블록에서 렌더해 생성하거나 파서의 삽화↔블록 차분 판정을 받는다 — 같은 계획의 이중 표현이 서로 어긋나는 드리프트 축을 봉쇄한다. **태그의 뜻은 기준선 기준이다**(G1 시점 HEAD — Phase 2 재발화 시 `--base` 기준선 · 2026-09-03 차단 승격): `add` = 기준선에 없는 경로(실존하면 형식 red «add 충돌») · `update` = 기준선에 실존하는 경로(부재면 형식 red «update 대상 부재» — 그 경로는 `add` 로 적는다 · 유효 승격 형태 `<칸>/__init__.py` ∧ `<칸>/<칸>.py` 의 기준선 실존은 실존이다) · `remove[@Ln]` = 기준선 실존 경로(비후행 remove 의 부재는 형식 red «remove 대상 부재» — 예외 없음 · 후행 `@Ln` 은 판정 밖 · `--base` 기준선은 이동하지 않으므로(재발화 판형 ②) 기실현 remove 는 실존이다 · 기준선에도 없는(승인 전에 이미 지워진) 경로는 remove 행을 거둔다) · `empty` = 새 빈 파일(add 와 같은 «새 파일» 태그 — 기준선 실존이면 형식 red «empty 충돌» · 기실현이면 `update`). 구형 명세에 블록을 소급 작성할 때 기실현 경로는 전부 `update` 다 — 실체화 0도 적법하며 선언 검증은 계속 수행한다(`add` 를 `update` 로 바꿔 red 를 피하는 것은 형식 red 로 잡힌다). 비후행 remove를 전사한 뒤 그 경로들의 조상 중 최종 사본에서 빈 부모 디렉터리만 정리한다(dirty overlay 선삭제 포함). 남은 파일(0B·init·미추적·add/empty 포함)이 있거나 후행 remove 실물이 남으면 보존하며, 무관한 빈 디렉터리와 symlink 경유 경로는 정리하지 않는다. 폴더 정리는 파일 실체화 건수와 별도로 보고한다 — 파일 실효 조치가 없어도 선언 검증과 기존 실존 판정을 수행한 뒤 확정 없는 경우 skip한다. remove만 있는 BC를 신규 골격으로 다시 만들지 않는다.
+- **공개 심볼 표기**: 자리표시자 실현 파일의 **공개 심볼 전부**를 `<!-- machine: symbols -->` 마커 + ```symbols 펜스에 적는다(«대표 1회»가 아니라 전수다) — 1행 = `경로.py::Symbol(Base) {필드, …}`(Symbol 은 대문자 선두 또는 `_`+대문자 선두 — 주 계약이 참조하는 사설 보조 타입 `_Item` 도 적는다: 파서가 클래스로 분류하고 검사기의 사설 면제 판정 경로를 스텁이 그대로 탄다 · 소문자 선두는 함수다) · 메서드 행 `경로.py::Symbol.method(파라미터) -> 반환`(수신자는 무어노테이션 `self`/`cls` 에 한해 적어도·안 적어도 된다 — 실행기 파서가 정규화한다; 어노테이션 수신자는 중복 합성으로 형식 red 가 된다) · 필드 = `name: Type[ = default]` · `NAME = "literal"`(enum 멤버) · `name = <식>`(Django 필드 대입식 등)만 허용 — 타입도 값도 없는 bare 이름은 형식 red 다. Base 병기가 의무인 종류는 재량 목록이 아니라 **검사기 소스에서 기계 추출한 닫힌 목록**(소성물 `scripts/pregate_symbol_kinds.json` — rulepack 과 함께 재생성)이고, 명명규약으로 유도 가능한 생략은 **성문 유도표**(final.md §1 칸→베이스 결정표 — **아직 성문 전이다: 성문 전에는 생략 허용분이 공집합이라 전 심볼을 명기한다**) 등재분에 한한다 — 단 **값 축 유도 3행은 성문 등재됐다**(2026-09-02 · 3행째 2026-09-03): django_* `apps.py` 의 `name`(앱 폴더 전체 점 경로)/`label`(bc명) 정형, models/ 칸 `*Model` 의 `Meta.db_table`(`<bc>_<entity_snake>` — #630 유도 규칙), 그리고 마이그레이션 칸(`migrations/NNNN_*.py` — makemigrations 산출물 모양 #593: `Migration` 클래스 1 · `0001_` 만 `initial = True` · `migrations/__init__.py` 는 빈 파일)의 결손 보충. 이 결손은 실행기가 규약 상수로 보충하므로 규약대로라면 생략해도 된다(마이그레이션 칸은 file-plan `add` 만 적어도 된다 — symbols 전사가 있으면 전사 우선 · 규약 밖 값을 계획하면 반드시 기계 블록에 명기 — 산문 명기는 예보 표면 밖이다). **생략 = 규약 준수 확약**이다(생략분은 자동 정규화되어 위반 예보가 불능이 된다: 규약을 벗어날 계획이면 반드시 명기). published-language 칸(contract/·published_error)의 심볼은 **필드 목록**(`code` 필드 유무 포함)을 병기하고, **주 계약이 참조하는 보조·중첩 타입은 소속 파일을 명세가 명시**한다 — 안 박으면 coder 가 즉흥 배치해 예보·판정이 그 파일을 못 본다. **데코레이터·모듈 별칭도 symbols에 명시한다**: 클래스 행 뒤 `경로.py::Symbol @dataclass(frozen=True, slots=True, kw_only=True)`처럼 적는다(이름·속성 이름 또는 그 호출만 · 복수 행은 적은 순서대로 클래스 위에 전사 · 선행 클래스 없는 행은 형식 red). 이름/옵션/별칭은 원문 그대로이며 자동 dataclass 지정이나 import 추론은 없다 — `dataclass`·`dc.dataclass` 등 데코레이터와 모듈 별칭의 필요한 import는 boundary-imports에 명시한다. 모듈 별칭은 그 파일의 클래스/함수보다 먼저 `경로.py::alias 이름[: 타입] = 별칭식`으로 적는다. TYPE_CHECKING 분기는 `경로.py::alias[TYPE_CHECKING] _BookAdminBase: TypeAlias = admin.ModelAdmin[BookModel]` 다음에 `경로.py::alias[else] _BookAdminBase: type[admin.ModelAdmin] = admin.ModelAdmin`을 적는다(같은 파일·같은 이름의 인접한 유효 두 행, 주석/빈 줄 제외). 필요한 `TYPE_CHECKING`·`TypeAlias`·admin·모델 import는 boundary-imports에서 공급한다. 별칭은 단일 이름 Assign 또는 값 있는 AnnAssign이고 우변은 이름·속성·타입 첨자 및 그 내부 타입 표현식으로 한정한다(호출·복합문·클래스/함수 정의 불가). import 뒤 클래스 앞에 if TYPE_CHECKING/else와 두 대입의 어노테이션을 보존해 전사한다. 누락 분기·중복 별칭·다른 이름의 else·클래스/함수 뒤 별칭은 형식 red다. 비-add의 데코레이터·별칭 행도 문법을 검증하며 그 재료로 기존 본문을 바꾸지 않는다 — 완결된 별칭 이름만 update 자기 해소 근거이고 데코레이터 행만으로 이름을 선언하지 않는다. 미기재는 부재이며 산문에서 보충하지 않는다. 마이그레이션 정형이 무시하는 별칭 재료는 채널 메모로 병기한다. **update OHS 신규 함수 전사**: 표준 `open_host_service/<area>/<area>_service.py` 실물에 symbols로 명시한 신규 모듈 함수만 기존 본문 뒤에 전사한다. 기존 함수·클래스·별칭 본문 수정과 다른 update 칸의 본문 전사는 S5다. add/update의 명시 클래스·메서드·필드·별칭 선언은 별도로 보존해 효과/출처 결합 DTO의 선언 후상태를 검사한다. 이는 실물 클래스 본문을 덮어쓰지 않으며 본문 검증의 증명이 아니다. 기존 바인딩/새 함수/합성 helper 충돌, 전사할 신규 함수 없음, 실물 부재·승격 형태는 사유를 적고 미시뮬레이션으로 남긴다. 기존 본문을 대체하거나 checker에 선언 이름을 주입하지 않는다. 함수 본문은 계속 스텁이므로 G2 실검증을 대체하지 않는다.
+- **경계 import 표**: 검사기 판정에 관련되는 **경계 import 전부**를 `<!-- machine: boundary-imports -->` 마커의 ```imports 펜스(1행 = `<소비 파일>` + 탭 또는 공백 2+ + `<import 문 그대로>`)로 성문한다 — 타 BC OHS/contract·framework 공통만이 아니라, domain/contract 칸의 서드파티 라이브러리와 **테스트 파일의 경계 import 전부**(factories/타 급·타 BC OHS/published 계약 소비)까지. 파일별 전체 import 를 강제하는 것은 아니다 — **경계란 세 가지다**: ⑴ BC 밖(타 BC OHS/contract·framework 공통·서드파티·테스트 재료) ⑵ BC 안의 층 경계 중 **층 규율 검사기가 금지·예외 항목으로 판정하는 것**(driving 잎 → `application_layer/port/**` · domain → 상위 층 등 #92~#96·#185/#186 의 항목 — 잎이 port 예외를 잡을 계획이면 그 import 행을 그대로 적어 G1 에서 #93 예보를 받는다: 적을 수 없는 설계가 드러나는 것이 이 채널의 목적이다) ⑶ 그 밖은 구현 재량(성문 불요). 산문에만 적힌 경계 import 는 예보 표면 밖이다(pre-gate 보고 헤더의 사각 목록 S3). **각 행은 실행기가 격리 사본(기준선 + dirty overlay + 이 명세의 add)에서 3단 실존 판정**(⑴ 모듈 실존 · ⑵ 자리표시자 아님 · ⑶ 이름 최상위 정의)을 받는다(2026-09-03) — 저장소 밖(표준·서드파티)은 검사 밖, 이 명세가 add 하는 대상은 자기 해소(symbols 채널 소관 — 승격 폴더 부품 포함), ⑵ 는 이름 import(`from M import n`)의 대상 M 이 모듈일 때만이다. file-plan `update` 대상(사본에 실물이 있을 때만 — 기준선 부재 update 는 형식 red 로 먼저 서고, 유효 승격 형태 예외로 통과한 대상만 update 로는 생기지 않으므로 ⑴ 모듈 부재)의 이름은 그 칸의 symbols 에 선언하면 «자기 update 해소»이고 미선언이면 현재 표면에 있을 때만 실존 확인·아니면 판정 불능이다(표면은 이 명세 이후 상태 — update 로 새 심볼을 낼 계획이면 symbols 에 적는다 · ⑵⑶ 비적용). 판정 기준은 **이 브랜치**다 — 다른 워크트리·미머지 브랜치의 실물은 보지 않는다(부재 = «계약 실존 결손»으로 예보 · 소비자가 `update` 여도 행은 판정된다). 상류 소유 계약을 소비할 계획이면 그 행을 **그대로 적는다** — 결손 예보가 선행 조건의 기계 표현이며, 행을 빼서 green 을 만드는 것은 채널 은폐(경계 import 전수 의무 위반)다. 신규 함수가 전사되는 update OHS 서비스는 명시 boundary-imports도 충돌 없이 추가 가능한 경우에만 함께 전사한다. 기존 바인딩을 다른 출처로 덮는 등 안전한 합성이 불가하면 해당 서비스 전사를 통째로 보류하고 S5 사유를 보고한다. 행 전부를 대상으로 하는 기존 계약 실존/S′ 판정은 이 전사 여부와 별개로 유지한다. S3의 물리 import 전사 범위와, 명시 import·별칭·타입으로 출처를 결합하는 선언 검증은 구별한다. 나머지 update 본문은 미검증이다.
+- **물리 신호 어노테이션**: 영구 테스트 입장 표의 `owner/path` 셀 안에 정형 어노테이션 `[markers: django_db,…] [base: TestCase] [client: yes]` 를 단다 — 테스트 물리 신호(마커·베이스·클라이언트)의 유일한 전사 채널이다. **add 무기재 = 물리 신호 없음, update markers 무기재 = 기존 상태 유지**다. update의 `[markers:]`는 빈 목록, `[markers: slow]` 등은 module pytestmark 최종 목록의 교체다. 정적 Assign/AnnAssign/list/tuple·pytest 별칭을 지원하며 함수/class decorator·본문은 보존한다. 호출형·동적/중복/조건부/증분/subscript 변경·재바인딩 또는 update nodeid/class 주소는 S5다. update base/client는 미지원 S5이며 marker 후상태 성공이 본문 검증을 뜻하지 않는다. 입장 표 header 는 영문 정본 6열(`candidate | protected contract/evidence | unique production failure | existing authoritative coverage | decision | owner/path`)로 고정하고 셀 안에 raw `|` 를 두지 않는다 — 열 구조가 곧 파서 계약이라, 열이 흔들리면 어노테이션 채널이 통째로 죽는다. owner/path에서 처음 나오는 Python 파일 주소(`경로.py` 또는 `경로.py::case`)가 그 행의 artifact다. code span과 bare 경로 모두 허용하며 앞선 `add` 같은 비경로 span은 건너뛴다. case 접미는 파일 주소 결합에서만 벗긴다(case 본문 전사 아님). 첫 파일 주소를 file-plan의 정확한 add/update 키에 결합하고, 뒤의 support/coverage 주소에는 신호를 전파하지 않는다. 첫 주소가 미등재·비-add/update여도 뒤 파일로 넘어가지 않는다.
 - **예외 번역표 기계 블록**: 이 명세가 이미 요구하는 예외 번역 산출물(도메인→published 매핑)을 `<!-- machine: exception-map -->` 마커의 ```exceptions 펜스(1행 = `<published 예외>` + 탭 또는 공백 2+ + `<raise 창구 파일>`)로 성문한다 — 번역표에 없는 published 예외는 어느 창구도 raise 하지 않는 «죽은 계약»으로 예보된다. add 창구 외에는, 명시 신규 함수가 실제 전사된 update OHS 서비스 파일에 한해 같은 파일 수준 raise helper로 전사한다. exception-map은 함수 주소가 아니므로 특정 함수의 raise 위치를 증명하지 않는다. 신규 함수가 없는 update 본문 변경과 산문에만 적힌 raise는 계속 S5이며, contract 안의 raise 진탐을 면제하지 않는다.
 
 ## 리뷰 반영·충돌 중재
 
 코디네이터가 독립 리뷰어(ddd/api/db) 노트를 모아 전달하면:
 
 - 타당한 지적을 명세에 반영한다 — 반영·수정은 **해당 절을 제자리에서 고쳐 쓰는 것**이다. "G1 확정 요약 / G1' 보강 / G2 정정" 같은 게이트별 메타 요약 블록을 명세 위에 덧쌓지 마라(명세는 현재 상태만; 결정 이력은 코디네이터 대화·게이트 배너가 가짐). *왜* — 누적 블록은 본문과 어긋나 사후 정합 정정 비용을 낳는다.
 - 리뷰어 간 충돌(예: api 응답 형태 ↔ db 정규화)은 네가 **중재**해 명세에 결정과 근거를 명시한다.
 - 스스로 해소 못 하는 트레이드오프는 명세에 옵션으로 남겨 코디네이터가 G1에서 사용자에게 제시하게 한다.
 

```

## dddjango/agents/design-review-api.md

Before SHA256: ce8053f563384964b81e1ee02b02e6f0aa5687a9816a2632b31efe4919437c4b
After SHA256: 7db60d7a67888d2fd2874ead2d59f6bafd7f3d05e8fdc47efcdb8ed2ccf503be

```diff
--- before/dddjango/agents/design-review-api.md
+++ after/dddjango/agents/design-review-api.md
@@ -63,21 +63,21 @@
 
 1. **`contract scope`**: 모든 project API surface, profile, API instance/namespace/version/public·internal, scope 전체 BC와 error-BC subset, API/controller/URLconf/registrar/error/common module, consumer·OpenAPI evidence와 module sharing이 열거됐는지 본다. repository artifact는 project-relative path, greenfield artifact는 explicit planned project-relative path, absent/inapplicable item은 명시값인지 확인한다.
 2. **`scope evidence`**: repository module/artifact는 project-relative path와 observation으로 입증하는지 본다. external consumer·사용자 발언·runtime-generated OpenAPI는 stable external evidence identifier/observation을 허용하고 planned artifact는 planned path로 입증할 수 있다. 같은 profile reuse는 dedupe됐는지 확인한다. external/planned evidence라는 이유만으로 멈추게 하지 말고, mixed-profile sharing·한 source의 multiple API instances 등으로 surface/profile/sharing/contract가 실제로 모호·상충하거나 inventory가 끝내 불완전할 때만 `STOP_FOR_USER_APPROVAL`인지 본다.
 3. **`error profile`**: 새 dddjango Ninja scope는 `dddjango-code-json`인지, observed deployed/external/brownfield contract는 현재 승인된 product-spec·consumer·wire·OpenAPI evidence로 확인되거나 explicit user approval이 있으면 `preserve-established`인지 확인한다. 둘 모두를 요구하거나 dependency/file name으로 profile을 추론하면 blocker다. RFC 9457은 preserve scope가 선택한 profile-native contract일 수 있으며, 위반은 선택 profile과 wire/implementation의 mismatch다.
 4. **`compatibility/rollout`**: deployed public code/wire 변경을 breaking으로 취급하고 support consumer, simultaneous migration 또는 version split, deprecation/Sunset과 종료 근거를 확인한다. `dddjango-code-json` client는 contract당 하나의 Enum을 소비하는지 보고, `preserve-established` client는 관찰된 profile-native consumer contract를 유지하는지 본다. `preserve-established`가 RFC 9457 contract를 선택한 scope의 기존 RFC test를 끝내거나 바꾸려면 compatibility evidence와 현재 승인된 product-spec 또는 explicit user approval이 필요하다.
 5. **`common FrameworkErrorSchema action`**: `dddjango-code-json`은 `reuse | create | approved-change`이고 `none`이 아니며, `approved-change`에는 explicit user approval evidence가 있는지 본다. `preserve-established`는 observed profile-native common/canonical artifact action 또는 evidenced `none | not applicable`인지 보고 common `ErrorSchema`을 강제하지 않는다.
 6. **`common FrameworkErrorSchema shape/approval`**: `dddjango-code-json`에는 plugin 기본 property가 없어야 한다. 기존 scope는 관찰된 shape를 기준선으로 삼고 신규 scope는 exact field set·type·required/default/nullable·Field metadata·model config/legacy Config·validator/serializer/computed field/Pydantic hook inventory와 effective semantics·wire 직렬화와 ErrorCode로 좁힐 식별자 field를 제안했는지 본다. 신규 shape와 기준선의 property·type·존재성·변환 규칙·의미 변경에는 일반 G1 승인과 분리된 explicit user approval evidence가 있어야 한다. `preserve-established`는 observed profile-native wire/media type/schema/handler shape와 approval 또는 evidenced `none | not applicable`인지 보며, observed RFC/schema/handler 보존을 새 recipe로 바꾸지 않는다.
 7. **`BC error module`**: `dddjango-code-json`은 error-BC마다 side-effect-free module이 있고 public BC error가 없는 BC만 `none`인지 본다. `preserve-established`는 observed profile-native module/handler artifact 또는 evidenced `none | not applicable`인지 보고 BC module을 강제하지 않는다. 물리 배치나 helper 우회 판정은 discipline-reviewer에게 보낸다.
 8. **`BC ErrorCode`**: `dddjango-code-json`은 client-distinguishable하고 observable한 최소 public code의 단일 string Enum인지 본다. 여러 internal failures는 한 code를 공유할 수 있고 같은 code에서 안정적이어야 할 body field는 slot 6/10이 지정한 것만 요구한다. `title` property를 발명하지 않는다. `preserve-established`는 observed profile-native code taxonomy/Enum 또는 evidenced `none | not applicable`인지 보고 BC Enum을 강제하지 않는다.
 9. **`BC ErrorSchema`**: `dddjango-code-json`은 common exact shape를 보존하면서 slot 6의 식별자 field 하나를 해당 BC Enum으로 좁힌 base이고 public BC error가 없는 BC만 `none`인지 본다. 좁힌 식별자 field는 공통의 default를 잃어 required여도 canon이다(식별자 field 한정·ErrorCode 좁힘 동반일 때만 — 2026-08-15). `preserve-established`는 observed profile-native status-specific schema/response artifact 또는 evidenced `none | not applicable`인지 보고 BC base를 강제하지 않는다.
-10. **`prepared error mapping`**: `dddjango-code-json`은 concrete domain/application exception 또는 조회의 `None` → no-arg concrete `ErrorSchema`, 또는 event-specific 값으로 명시적으로 채운 BC base `ErrorSchema` → direct `Status(<승인된 HTTP status 표현>, error)` chain과 slot-6 exact literal body/approved header가 완전한지 본다. internal failure type과 output object를 혼동하면 blocker다. 공개 문자열은 `str(exc)`를 자동 사용하거나 sensitive data를 노출하면 안 된다. raw infra는 기본 500이고 approved stable public meaning만 consuming BC internal exception으로 정규화한 뒤 `ErrorSchema`을 만드는지 확인한다. `preserve-established`는 observed profile-native preparation/mapping 또는 evidenced `none | not applicable`인지 보고 code-profile chain을 강제하지 않는다.
+10. **`prepared error mapping`**: `dddjango-code-json`은 concrete domain/application exception 또는 조회의 `None` → no-arg concrete `ErrorSchema`, 또는 event-specific 값으로 명시적으로 채운 BC base `ErrorSchema` → direct `Status(<승인된 HTTP status 표현>, error)` chain과 slot-6 exact literal body/approved header가 완전한지 본다. internal failure type과 output object를 혼동하면 blocker다. 공개 문자열은 `str(exc)`를 자동 사용하거나 sensitive data를 노출하면 안 된다. 이미 잡은 IntegrityError의 승인된 알려진 제약 실패는 구체 계약 예외로, 나머지는 승인된 일반 저장소 실패 계약으로 번역한다. repository 실패 계약은 domain 소유, capability port 실패 계약은 해당 port 소유다. 이 내부 정규화는 공개 HTTP 오류 승인이 아니므로 일반 저장소 실패의 외부 응답은 기존 safe 500을 유지한다. 새 ErrorCode/ErrorSchema/4xx/503을 만들지 않는다. 잡지 않은 unknown 인프라 오류를 새로 catch-all하지 않는다. 안정된 public meaning이 별도로 승인된 경우에만 그 외부 계약에 맞는 controller mapping을 한다. 이미 선언된 계약 예외의 관찰 후 재던짐은 허용한다. `preserve-established`는 observed profile-native preparation/mapping 또는 evidenced `none | not applicable`인지 보고 code-profile chain을 강제하지 않는다.
 11. **`controller mapping`**: `dddjango-code-json`은 slot 10의 internal failure 형태에 따라 두 path 중 하나가 선택됐는지 확인한다. exception path는 input preparation 뒤 정확히 한 번의 application call만 narrow `try`에 두고 승인된 concrete exception 또는 exception tuple만 catch해야 한다. `None` path는 조회 use case가 대상이 없어 `None`을 돌려주는 경우에만 선택돼야 하고, artificial `try`/`catch` 없이 application call을 정확히 한 번 실행한 뒤 그 직후 `is None` branch해야 하며, catch를 요구하거나 exception을 fabricate해 즉시 raise/catch하면 blocker다. 실패를 Result variant·outcome 값으로 설계한 명세는 blocker다(`<use_case>_result.py`엔 성공 한 벌만 — #571; exception path여야 한다). 두 path 모두 승인된 no-arg concrete 또는 event-specific 값으로 채운 BC-base `ErrorSchema`을 만들고, approved header를 주입된 응답용(temporal) Django `HttpResponse`에 설정한 뒤 two-argument `Status(<literal/status constant 또는 slot-6 body field>, error)`를 직접 return하는지 확인한다. `status` body property를 요구하면 blocker다. error helper/handler/factory/serializer/table 또는 mapping 추출로 이 semantic contract를 우회하면 발견으로 올리고 물리적 우회 여부는 discipline-reviewer에게 보낸다. `preserve-established`는 observed profile-native controller/handler mapping 또는 evidenced `none | not applicable`인지 보고 direct `Status`를 강제하지 않는다.
 12. **`response/OpenAPI/tests`**: 승인 HTTP status/body/header와 mounted runtime, 공개 generated OpenAPI의 관련 operation/status/schema 후보가 입장 표의 행과 연결됐는지 본다. slot 6 shape와 별도 변경 승인은 유지하되 Pydantic private metadata·validator 위치·framework 기본 직렬화를 자동 제품 테스트로 바꾸면 blocker다. 공개 Python consumer 계약은 HTTP와 별도 행이어야 한다. `preserve-established`는 observed profile-native media type/fields/status-specific schema·handler와 test/OpenAPI evidence 또는 `none | not applicable`인지 본다. framework-owned 오류·auth/header smoke도 승인된 계약과 독자 failure가 있는 행만 허용하며 exact framework body snapshot을 요구하지 않는다.
 
 - `dddjango-code-json`에서 framework-owned 401/403/route 404/422/429/general `HttpError`/unknown 500을 BC response로 광고하거나 변환하지 않았는지, established framework header dependency를 보존하고 테스트하는지 본다.
 - 모든 Ninja profile의 인증 실패는 `None`을 return하거나 framework `AuthenticationError`를 raise해야 한다. `AuthenticationError` object나 `ErrorSchema`을 return하거나 어느 것도 `request.auth`에 저장하면 blocker다. 별도 승인된 406/415는 tested version-compatible Ninja-owned pre-body/framework `HttpError` path여야 하고 함수형 `Router`나 global handler를 강제하면 안 된다. `preserve-established`는 관찰된 profile-native error body/협상 behavior를 보존해야 한다.
 - native download/stream/redirect와 schema-less 204 carveout을 존중하는지 본다. 구조·파일 위치·import DRY와 helper-circumvention의 물리 판단은 discipline-reviewer 소유이며, 여기서는 그 선택 때문에 생긴 semantic contract inconsistency만 지적한다.
 - 영구 테스트 입장 표의 `remove/weaken` 행이 API 기대에 적용 가능한 지원 소비자·버전·deprecation/Sunset 의무의 실제 종료 evidence와 exact target을 제시하는가. 명세의 침묵이나 새 성공 응답 부재만으로 종료를 승인하지 않고 `pending`으로 반송한다.
 - 페이지네이션·정렬·필터·레이트리밋 계약이 일관된가.
 - 엔드포인트 표면(URL)을 점검할 때, 신규 표준 표면은 ninja-extra **클래스 컨트롤러**라 **최종 URL = `@api_controller("/prefix")`(클래스가 소유) + `@route.*("path")` 메서드 경로의 합성**으로 읽는다. side-effect-free BC registrar가 `register_controllers`로 해당 승인 scope의 project API instance에 등록되고 URLconf가 명시적으로 registrar를 호출·mount하는 흐름까지 확인한다(prefix와 메서드 경로가 둘로 나뉘므로 한쪽만 보고 URL을 판단하지 않는다). 계약 lens는 형태(함수형/클래스) 중립이지만, 경로 합성과 등록을 모르면 endpoint surface를 잘못 읽는다.
 

```

## codex-dddjango/skills/dddjango-design-review-api/SKILL.md

Before SHA256: d8427e2ba2550eca62eefdc478bfa89a85e2c642f9bcda249936ca61884e3675
After SHA256: 255c67d1c85643ed841f978c3a7c6e2e8537c6686fb8fa44fc65eb83ba5f2ce4

```diff
--- before/codex-dddjango/skills/dddjango-design-review-api/SKILL.md
+++ after/codex-dddjango/skills/dddjango-design-review-api/SKILL.md
@@ -59,21 +59,21 @@
 
 1. **`contract scope`**: 모든 project API surface, profile, API instance/namespace/version/public·internal, scope 전체 BC와 error-BC subset, API/controller/URLconf/registrar/error/common module, consumer·OpenAPI evidence와 module sharing이 열거됐는지 본다. repository artifact는 project-relative path, greenfield artifact는 explicit planned project-relative path, absent/inapplicable item은 명시값인지 확인한다.
 2. **`scope evidence`**: repository module/artifact는 project-relative path와 observation으로 입증하는지 본다. external consumer·사용자 발언·runtime-generated OpenAPI는 stable external evidence identifier/observation을 허용하고 planned artifact는 planned path로 입증할 수 있다. 같은 profile reuse는 dedupe됐는지 확인한다. external/planned evidence라는 이유만으로 멈추게 하지 말고, mixed-profile sharing·한 source의 multiple API instances 등으로 surface/profile/sharing/contract가 실제로 모호·상충하거나 inventory가 끝내 불완전할 때만 `STOP_FOR_USER_APPROVAL`인지 본다.
 3. **`error profile`**: 새 dddjango Ninja scope는 `dddjango-code-json`인지, observed deployed/external/brownfield contract는 현재 승인된 product-spec·consumer·wire·OpenAPI evidence로 확인되거나 explicit user approval이 있으면 `preserve-established`인지 확인한다. 둘 모두를 요구하거나 dependency/file name으로 profile을 추론하면 blocker다. RFC 9457은 preserve scope가 선택한 profile-native contract일 수 있으며, 위반은 선택 profile과 wire/implementation의 mismatch다.
 4. **`compatibility/rollout`**: deployed public code/wire 변경을 breaking으로 취급하고 support consumer, simultaneous migration 또는 version split, deprecation/Sunset과 종료 근거를 확인한다. `dddjango-code-json` client는 contract당 하나의 Enum을 소비하는지 보고, `preserve-established` client는 관찰된 profile-native consumer contract를 유지하는지 본다. `preserve-established`가 RFC 9457 contract를 선택한 scope의 기존 RFC test를 끝내거나 바꾸려면 compatibility evidence와 현재 승인된 product-spec 또는 explicit user approval이 필요하다.
 5. **`common FrameworkErrorSchema action`**: `dddjango-code-json`은 `reuse | create | approved-change`이고 `none`이 아니며, `approved-change`에는 explicit user approval evidence가 있는지 본다. `preserve-established`는 observed profile-native common/canonical artifact action 또는 evidenced `none | not applicable`인지 보고 common `ErrorSchema`을 강제하지 않는다.
 6. **`common FrameworkErrorSchema shape/approval`**: `dddjango-code-json`에는 plugin 기본 property가 없어야 한다. 기존 scope는 관찰된 shape를 기준선으로 삼고 신규 scope는 exact field set·type·required/default/nullable·Field metadata·model config/legacy Config·validator/serializer/computed field/Pydantic hook inventory와 effective semantics·wire 직렬화와 ErrorCode로 좁힐 식별자 field를 제안했는지 본다. 신규 shape와 기준선의 property·type·존재성·변환 규칙·의미 변경에는 일반 G1 승인과 분리된 explicit user approval evidence가 있어야 한다. `preserve-established`는 observed profile-native wire/media type/schema/handler shape와 approval 또는 evidenced `none | not applicable`인지 보며, observed RFC/schema/handler 보존을 새 recipe로 바꾸지 않는다.
 7. **`BC error module`**: `dddjango-code-json`은 error-BC마다 side-effect-free module이 있고 public BC error가 없는 BC만 `none`인지 본다. `preserve-established`는 observed profile-native module/handler artifact 또는 evidenced `none | not applicable`인지 보고 BC module을 강제하지 않는다. 물리 배치나 helper 우회 판정은 discipline-reviewer에게 보낸다.
 8. **`BC ErrorCode`**: `dddjango-code-json`은 client-distinguishable하고 observable한 최소 public code의 단일 string Enum인지 본다. 여러 internal failures는 한 code를 공유할 수 있고 같은 code에서 안정적이어야 할 body field는 slot 6/10이 지정한 것만 요구한다. `title` property를 발명하지 않는다. `preserve-established`는 observed profile-native code taxonomy/Enum 또는 evidenced `none | not applicable`인지 보고 BC Enum을 강제하지 않는다.
 9. **`BC ErrorSchema`**: `dddjango-code-json`은 common exact shape를 보존하면서 slot 6의 식별자 field 하나를 해당 BC Enum으로 좁힌 base이고 public BC error가 없는 BC만 `none`인지 본다. 좁힌 식별자 field는 공통의 default를 잃어 required여도 canon이다(식별자 field 한정·ErrorCode 좁힘 동반일 때만 — 2026-08-15). `preserve-established`는 observed profile-native status-specific schema/response artifact 또는 evidenced `none | not applicable`인지 보고 BC base를 강제하지 않는다.
-10. **`prepared error mapping`**: `dddjango-code-json`은 concrete domain/application exception 또는 조회의 `None` → no-arg concrete `ErrorSchema`, 또는 event-specific 값으로 명시적으로 채운 BC base `ErrorSchema` → direct `Status(<승인된 HTTP status 표현>, error)` chain과 slot-6 exact literal body/approved header가 완전한지 본다. internal failure type과 output object를 혼동하면 blocker다. 공개 문자열은 `str(exc)`를 자동 사용하거나 sensitive data를 노출하면 안 된다. raw infra는 기본 500이고 approved stable public meaning만 consuming BC internal exception으로 정규화한 뒤 `ErrorSchema`을 만드는지 확인한다. `preserve-established`는 observed profile-native preparation/mapping 또는 evidenced `none | not applicable`인지 보고 code-profile chain을 강제하지 않는다.
+10. **`prepared error mapping`**: `dddjango-code-json`은 concrete domain/application exception 또는 조회의 `None` → no-arg concrete `ErrorSchema`, 또는 event-specific 값으로 명시적으로 채운 BC base `ErrorSchema` → direct `Status(<승인된 HTTP status 표현>, error)` chain과 slot-6 exact literal body/approved header가 완전한지 본다. internal failure type과 output object를 혼동하면 blocker다. 공개 문자열은 `str(exc)`를 자동 사용하거나 sensitive data를 노출하면 안 된다. 이미 잡은 IntegrityError의 승인된 알려진 제약 실패는 구체 계약 예외로, 나머지는 승인된 일반 저장소 실패 계약으로 번역한다. repository 실패 계약은 domain 소유, capability port 실패 계약은 해당 port 소유다. 이 내부 정규화는 공개 HTTP 오류 승인이 아니므로 일반 저장소 실패의 외부 응답은 기존 safe 500을 유지한다. 새 ErrorCode/ErrorSchema/4xx/503을 만들지 않는다. 잡지 않은 unknown 인프라 오류를 새로 catch-all하지 않는다. 안정된 public meaning이 별도로 승인된 경우에만 그 외부 계약에 맞는 controller mapping을 한다. 이미 선언된 계약 예외의 관찰 후 재던짐은 허용한다. `preserve-established`는 observed profile-native preparation/mapping 또는 evidenced `none | not applicable`인지 보고 code-profile chain을 강제하지 않는다.
 11. **`controller mapping`**: `dddjango-code-json`은 slot 10의 internal failure 형태에 따라 두 path 중 하나가 선택됐는지 확인한다. exception path는 input preparation 뒤 정확히 한 번의 application call만 narrow `try`에 두고 승인된 concrete exception 또는 exception tuple만 catch해야 한다. `None` path는 조회 use case가 대상이 없어 `None`을 돌려주는 경우에만 선택돼야 하고, artificial `try`/`catch` 없이 application call을 정확히 한 번 실행한 뒤 그 직후 `is None` branch해야 하며, catch를 요구하거나 exception을 fabricate해 즉시 raise/catch하면 blocker다. 실패를 Result variant·outcome 값으로 설계한 명세는 blocker다(`<use_case>_result.py`엔 성공 한 벌만 — #571; exception path여야 한다). 두 path 모두 승인된 no-arg concrete 또는 event-specific 값으로 채운 BC-base `ErrorSchema`을 만들고, approved header를 주입된 응답용(temporal) Django `HttpResponse`에 설정한 뒤 two-argument `Status(<literal/status constant 또는 slot-6 body field>, error)`를 직접 return하는지 확인한다. `status` body property를 요구하면 blocker다. error helper/handler/factory/serializer/table 또는 mapping 추출로 이 semantic contract를 우회하면 발견으로 올리고 물리적 우회 여부는 discipline-reviewer에게 보낸다. `preserve-established`는 observed profile-native controller/handler mapping 또는 evidenced `none | not applicable`인지 보고 direct `Status`를 강제하지 않는다.
 12. **`response/OpenAPI/tests`**: 승인 HTTP status/body/header와 mounted runtime, 공개 generated OpenAPI의 관련 operation/status/schema 후보가 입장 표의 행과 연결됐는지 본다. slot 6 shape와 별도 변경 승인은 유지하되 Pydantic private metadata·validator 위치·framework 기본 직렬화를 자동 제품 테스트로 바꾸면 blocker다. 공개 Python consumer 계약은 HTTP와 별도 행이어야 한다. `preserve-established`는 observed profile-native media type/fields/status-specific schema·handler와 test/OpenAPI evidence 또는 `none | not applicable`인지 본다. framework-owned 오류·auth/header smoke도 승인된 계약과 독자 failure가 있는 행만 허용하며 exact framework body snapshot을 요구하지 않는다.
 
 - `dddjango-code-json`에서 framework-owned 401/403/route 404/422/429/general `HttpError`/unknown 500을 BC response로 광고하거나 변환하지 않았는지, established framework header dependency를 보존하고 테스트하는지 본다.
 - 모든 Ninja profile의 인증 실패는 `None`을 return하거나 framework `AuthenticationError`를 raise해야 한다. `AuthenticationError` object나 `ErrorSchema`을 return하거나 어느 것도 `request.auth`에 저장하면 blocker다. 별도 승인된 406/415는 tested version-compatible Ninja-owned pre-body/framework `HttpError` path여야 하고 함수형 `Router`나 global handler를 강제하면 안 된다. `preserve-established`는 관찰된 profile-native error body/협상 behavior를 보존해야 한다.
 - native download/stream/redirect와 schema-less 204 carveout을 존중하는지 본다. 구조·파일 위치·import DRY와 helper-circumvention의 물리 판단은 discipline-reviewer 소유이며, 여기서는 그 선택 때문에 생긴 semantic contract inconsistency만 지적한다.
 - 영구 테스트 입장 표의 `remove/weaken` 행이 API 기대에 적용 가능한 지원 소비자·버전·deprecation/Sunset 의무의 실제 종료 evidence와 exact target을 제시하는가. 명세의 침묵이나 새 성공 응답 부재만으로 종료를 승인하지 않고 `pending`으로 반송한다.
 - 페이지네이션·정렬·필터·레이트리밋 계약이 일관된가.
 - 엔드포인트 표면(URL)을 점검할 때, 신규 표준 표면은 ninja-extra **클래스 컨트롤러**라 **최종 URL = `@api_controller("/prefix")`(클래스가 소유) + `@route.*("path")` 메서드 경로의 합성**으로 읽는다. side-effect-free BC registrar가 `register_controllers`로 해당 승인 scope의 project API instance에 등록되고 URLconf가 명시적으로 registrar를 호출·mount하는 흐름까지 확인한다(prefix와 메서드 경로가 둘로 나뉘므로 한쪽만 보고 URL을 판단하지 않는다). 계약 lens는 형태(함수형/클래스) 중립이지만, 경로 합성과 등록을 모르면 endpoint surface를 잘못 읽는다.
 

```

## dddjango/agents/discipline-reviewer.md

Before SHA256: 606c18ee2d0f77274bb1f7d701f56153f26f4b1d671af533eb431235349fe10e
After SHA256: c6cf298c7a61a76473a0ddca945dd338bff4660dd74eb393e2f85dbad252bb05

```diff
--- before/dddjango/agents/discipline-reviewer.md
+++ after/dddjango/agents/discipline-reviewer.md
@@ -84,52 +84,54 @@
 - **상수 승격·심볼 소비 규율(백스톱 사각 전담)**: **이번 작업이 touched한 코드만 본다 — untouched 기존 리터럴은 면제(grandfather)**. ① 닫힌 집합의 원소(도메인 상태·종류·wire enum성 문자열)를 우리 코드가 분기·판정하는데 집합 타입(domain `StrEnum`/`choices` 파생) 없이 원시 리터럴로 산재하면 **important**(1곳째부터 승격 — `discipline-cleancode` §2.14; 단 그 산재가 같은-지식 중복 정리 사안이면 위 클린코드 불릿의 DRY로만 분류, 이중 계상 금지). ② Enum/choices가 *선언돼 있는데* 소비처가 리터럴로 비교·`.filter()`·대입하면 **important** — 결정적 백스톱 `check-choices-literal-consumption`이 직접형(`default=` 리터럴·`<Model>.objects.filter(<field>="…")`)을 잡으므로 네가 보는 건 그 사각이다: 변수 우회·간접 queryset(`qs.filter(...)`)·비교식(`x.status == "…"`)·`__in` 변종. **심볼 치환은 판정 소유 위반을 면책하지 않는다** — 그 사건이 복합 판정의 소유 문제면 위 '죽은 도메인 메서드·판정 인프라 누수' 불릿 하나로만 분류한다(이중 계상 금지). ③ 도메인 판정 값 집합이 `models.TextChoices`로 선언돼 domain이 ORM 타입을 역참조하면 **important**(계층 소유 — 단일 출처는 domain enum·ORM은 `.value` 평탄화 파생; `implementation-django` §2.5. 구조 이주 사안이면 아래 파일트리 불릿과 이중 계상 금지 — 값 집합 소유만 여기). ④ 테스트가 **외부 관찰 계약**(HTTP 응답·DB 저장값·이벤트)의 assert 기댓값에 프로덕션 Enum·상수를 역수입하면 **important**(자기참조 오라클 — `implementation-test` §15.4; 위 테스트 품질 불릿과는 별개 렌즈 — 오라클 자기참조만 여기). ⑤ 우리 BC가 **발행하는 이벤트 봉투의 discriminator**(태그드 유니온 태그 — `event_type` 류)가 domain `StrEnum` 파생(`Literal[EventType.X] = EventType.X`) 없이 맨 문자열 `Literal["…"]`·원시 str로 선언되면 **important**(1종째부터 — birth-enum `architecture-ddd` §3.7; 대응 백스톱 없음 — 버전 태그와 AST 형태가 동일해 형태 판정은 FP 불가피, "발행 봉투인가"의 위치 판정은 전적으로 네 몫). union-enum 동기 후보는 별도 입장 행이 `add/update`이고 독자 failure를 승인한 경우에만 그 행의 mechanics를 감사한다. 입장 행이 없으면 동기 테스트를 즉석에서 요구하지 않고 candidate로 설계 반송한다. **⑤의 제외**: `payload_schema_version`류 버전 태그(리터럴 동결이 정답 — enum화가 오히려 위반 방향), 상류 이벤트를 중계만 하는 소비 측 스키마의 태그(published language 수용 — 소비 BC는 발행 enum을 import하지 않는다), 데이터소스 BC, OHS published contract(`open_host_service/*/contract/`)의 discriminator wire `Literal`(contract 무의존이 우선 — houserules `references/final.md` §1 트리 22~32행 — OHS 내부 구조; 동기 테스트는 승인 입장 행이 있을 때만 감사한다). ①과 배타: ①은 분기·판정 앵커의 미승격, ⑤는 발행 봉투 위치의 선언 형태(분기 존재 무관) — 한 사건은 하나로만 분류(이중 계상 금지). **거짓지적 방지(잡지 않는다)**: 도메인 내부 단위 테스트의 심볼 단언·테스트 arrange/act의 심볼 사용, 로그·예외 메시지 등 사람 대상 서술, Enum·상수 정의부 우변, `.value` 평탄화 파생(`default=OrderStatus.PENDING.value`), `Literal[...]`로 잠긴 인자 자리(단 발행 봉투 discriminator는 ⑤의 대상 — 맨 문자열 Literal이면 잡는다; 버전 태그는 여기 그대로 허용), 외부 프로토콜 소유 문자열(분기 조건인데 adapter 정규화 부재면 nit로만), 설정 키·환경변수명, 마이그레이션 historical value(살아있는 Enum 참조가 오히려 위반 — `implementation-django` §10.4), pass-through 저장·데이터소스 BC의 미승격, 한 파일 로컬 문자열, 우연히 같은 값·다른 지식의 미통합(합치면 오히려 위반). 근거 `discipline-cleancode` §2.14·`implementation-django` §2.5·§10.4·`architecture-ddd` §2.5·§3.2·§3.7·`implementation-test` §15.4·§15.5.
 - **메커니즘-소유권 규율**: 엔진·연결의 트랜잭션·락·격리 *메커니즘*은 설계(architect)가 소유한다 — 코드가 명세 승인 없이 그 의미를 바꾸지 않았는가. 레드 플래그(**blocker**): 프로덕션 `DATABASES.ENGINE`를 커스텀 백엔드로 교체, `DatabaseWrapper` 상속으로 `BEGIN`/begin 모드·`_start_transaction_under_autocommit` 변경, 런타임 몽키패치, `connection_created` 시그널, `OPTIONS.init_command`로 `BEGIN`/PRAGMA 주입, `isolation_level`·`locking_mode` 조작, DB 미들웨어, 테스트 conftest 패치 — *어떤 형태든* 동일 위반(`implementation-django` §16.4·`architecture-db` §9.5). **허용(통과)**: stock `OPTIONS`(`transaction_mode`[5.1+]·`timeout`)와 안전 PRAGMA 화이트리스트(`foreign_keys`·`busy_timeout`·`synchronous`·`cache_size`), 그리고 명세가 명시 승인한 메커니즘. **예외**: 이번 diff에 새로 들어온 변경만 본다(기존 코드 존중), 프로덕션 경로에 배선되지 않은 테스트 격리 전용 설정은 통과. 이는 **책임 배치·소유권 규율**(메커니즘을 누가 정하는가)이지 ORM/쿼리 정확성 판정이 아니다 — 네가 본다.
 - **API 오류 규율 1 — common/BC 소유권·승인 shape(blocker)**: active `dddjango-code-json` scope의 canonical common module은 승인된 공통 `FrameworkErrorSchema` 하나와 승인 shape만 소유하며 BC concrete를 두지 않는다. 공통 shape를 새로 만들거나 바꾸면서 일반 G1과 분리된 명시적 사용자 shape-승인 evidence가 없으면 blocker다. public 오류가 있는 각 BC의 canonical `driving_layer/api/bc_error_schema.py`만 `<Bc>ErrorCode(StrEnum)` 하나·`<Bc>ErrorSchema` 하나·그 BC concrete 전부를 소유한다. Ninja/`FrameworkErrorSchema`/HTTP DTO를 domain·application에 import하지 않는 것만으로는 부족하다. import-free DTO·VO라도 HTTP `status`/`code` 의미를 inner layer에 운반해 presentation이 소비하면 blocker다. 이름이 `status`인 정당한 도메인 상태는 값의 의미와 소비 경로가 HTTP 선택과 무관한지로 구별한다.
 - **API 오류 규율 2 — helper/handler/factory/serializer/mapping 우회(blocker)**: active code-profile managed surface에는 `@*.exception_handler`, `add_exception_handler`, `FrameworkErrorSchema` serializer·response helper, central converter, concrete fixed-value factory, exception→`FrameworkErrorSchema` dict/table, generic response builder나 이름만 바꾼 동형 추출을 만들거나 호출하지 않는다. controller의 짧은 failure→prepared error→`Status` mapping 반복은 의도된 명시성이므로 DRY 위반으로 잡지 않는다. 성공 Schema·download·streaming·redirect·schema-less 204의 framework-native 반환은 이 오류-helper 금지 밖이다. 승인된 `preserve-established` scope의 기존 handler는 관찰 evidence가 지정한 범위에서만 보존하며 새 code-profile의 정당화로 재사용하지 않는다.
 - **API 오류 규율 3 — controller path·좁은 try·구체 catch(blocker)**: active `dddjango-code-json` scope에서 10번 slot이 승인한 path와 코드를 대조한다. exception path는 입력·request·use-case 준비를 `try` 밖에 두고 `try` 안에는 최외곽 application call 정확히 한 문장만 둔다. branch·성공 변환·logging을 함께 넣지 않으며, 같은 owning BC에서 import한 승인 concrete exception 또는 concrete만 든 tuple만 catch한다. bare/`Exception`/`BaseException`, raw DB·SDK·framework exception, controller의 cross-BC exception, broad base의 재수출 alias, non-concrete가 하나라도 섞인 tuple은 blocker다. managed `try` 안에서 방금 raise해 즉시 catch하기, `HttpError` forwarding, re-raise, handler forwarding도 금지한다. `None` path(조회의 «없다» 한정)는 application call을 정확히 한 번 수행하고 인위적 `try`·exception 없이 call 직후 `is None` branch에서 직접 mapping한다. 실패를 Result variant·outcome 값으로 돌려받아 분기하는 controller는 blocker다(`<use_case>_result.py`엔 성공 한 벌만 — #571; exception path여야 한다). ACL/OHS가 승인된 known upstream failure를 consuming BC의 own concrete exception으로 번역하는 것은 controller의 금지된 cross-BC catch와 구별한다.
 - **API 오류 규율 4 — prepared FrameworkErrorSchema·직접 응답(blocker)**: active `dddjango-code-json` scope에서 승인된 concrete는 full approved slot-6 common shape 중 그 concrete의 fixed value로 승인된 모든 field 값을 class default로 제공하고 인자 없이 생성 가능해야 한다. class default는 concrete가 직접 선언하거나 intended value와 같은 승인된 base default를 상속할 수 있으며, 후자라면 불필요한 재선언을 요구하지 않는다. 사건별 direct BC-base construction이 승인됐으면 owning BC base에 승인 slot-6 required field 전부와 사건별로 기본값을 덮어써야 하는 approved optional field만 명시적으로 공급한다. catch 또는 failed branch는 그 error를 준비한 직후 두 인자 `Status(<literal/status constant 또는 slot-6 body field>, error)`를 직접 반환한다. plugin이 `status` body property를 요구하면 blocker다. 승인된 response header는 그 직전 controller에 주입된 응답용(temporal) Django `HttpResponse`에 쓴다. 오류 tuple, raw `Response`/`JsonResponse`/`HttpResponse`, dict body, factory·serializer·helper indirection은 blocker다.
 - **API 오류 규율 5 — returned status·OpenAPI·framework default(blocker)**: active `dddjango-code-json` scope에서 operation이 실제 직접 반환하는 모든 BC 오류 status는 `response={...}`에서 실제 반환하는 오류 타입 그대로(concrete·`Union`·명시값 base — base 뭉뚱그림 금지) 선언되어야 하고, 승인된 endpoint→status→schema mapping tuple·runtime 반환·generated OpenAPI의 status/schema 출현은 완전하며 서로 같아야 한다. framework-owned 401/403/route 404/422/429/general `HttpError`/unknown 500은 BC 오류로 직접 반환하거나 BC 오류로 광고하지 않는다. auth backend는 성공 시 identity/principal, 실패 시 `None` 또는 framework `AuthenticationError`만 반환·raise하며 truthy `FrameworkErrorSchema`/Schema를 `request.auth`에 넣지 않는다. framework-established header dependency를 숨기거나 명세에 없는 header를 꾸며내지 않는다. status→schema 선언만으로 허용 식별자 subset이 증명되지 않으므로 실제 runtime mapping case 검증을 생략하지 않는다.
 - **API 오류 5축 profile 경계**: 위 1~5축은 active `dddjango-code-json` scope에만 적용한다. `preserve-established` scope는 slot/evidence가 승인한 native exception forwarding·handler·body/return form·mapping mechanism을 보존하며, 이 5축을 이유로 code-profile에 이주하지 않는다. (이 경계는 오류 5축에 한한다 — 배선·등록은 아래 «API instance·registrar·composition 규율»이 profile 무관으로 소유한다.)
 - **API 오류 checker/reviewer 사각(명시 검토)**: 관련 checker가 exit 0이어도 semantic compliance의 증거가 아니다. 반드시 (a) 직접 import한 1-hop class method mutation·2-hop helper·선택 source 밖 helper·renamed converter, (b) dynamic import/registration·required symbol 재수출, (c) 문법상 concrete 이름이나 의미상 broad base인 exception, (d) Ninja/`FrameworkErrorSchema` import 없이 inner layer를 흐르는 HTTP status/code DTO, (e) project-wide inventory 완전성·mixed-profile shared module·scope 안의 API instance 복수, (f) root-local catalog/mapping·registrar/composition lookalike, (g) auth backend의 truthy `FrameworkErrorSchema`/Schema와 숨은 framework-header dependency를 직접 읽는다.
 - **API instance·registrar·composition 규율**: active `dddjango-code-json` contract scope마다 project `<project>/api.py`가 API instance 하나를 소유한다. 각 BC의 side-effect-free api_router(`driving_layer/api/api_router.py`의 `register_<bc>_api` — final.md §1 9행)는 전달받은 API에 자기 controller만 등록하고, project `urls.py`가 각 registrar를 명시적으로 한 번 호출한 뒤 API를 mount한다. controller는 `auto_import=False`여야 하며 project API import·module-top-level 등록·dynamic registrar·import-time side effect·scope 안의 API 복수는 blocker다. HTTP registrar와 DI-only `composition_root/`(트리 2~4행)를 섞지 않고, root-local catalog/mapping 또는 registrar/composition lookalike도 직접 확인한다. controller 형태는 승인된 presentation 계약을 보존한다. 오류 대응, 특히 406/415를 이유로 승인된 class controller를 함수형 `Router`로 바꾸거나 별도 API instance로 격리하지 않는다. `preserve-established` scope 에서도 **registration/composition 은 이 표준으로 대조한다** — preserve 가 보존하는 것은 오류 wire 산출물이지 배선이 아니다(구 «native registration/API-instance layout 보존» 문구는 라운드 1′ 배선 답습의 통로로 실증되어 걷었다 — 2026-08-12). 배선 표준화가 오류 profile 이주를 뜻하지도 않는다 — 오류 산출물은 slot 승인대로 유지한다. Phase 1의 project-wide inventory와 mixed-profile sharing 점검은 profile에 관계없이 유지한다.
-- **raw infrastructure 기본 경계**: raw DB/SDK/network exception은 safe framework 500으로 둔다. global recognizer·retryable handler·문자열/SQLSTATE 분류를 요구하거나 새 code-profile에 추가하지 않는다. 특정 실패가 안정된 public meaning을 가진다고 G1에서 명시 승인된 경우에만 owning infra/ACL이 그 실패를 consuming BC의 own concrete domain/application exception으로 정규화하고, 그 BC controller가 위 직접 흐름으로 mapping한다. raw infrastructure exception을 합성하거나 controller에서 직접 catch하는 우회도 금지한다.
+- **raw infrastructure 기본 경계**: raw DB/SDK/network exception은 safe framework 500으로 둔다. global recognizer·retryable handler·문자열/SQLSTATE 분류를 요구하거나 새 code-profile에 추가하지 않는다. 이미 잡은 IntegrityError의 승인된 알려진 제약 실패는 구체 계약 예외로, 나머지는 승인된 일반 저장소 실패 계약으로 번역한다. repository 실패 계약은 domain 소유, capability port 실패 계약은 해당 port 소유다. 이 내부 정규화는 공개 HTTP 오류 승인이 아니므로 일반 저장소 실패의 외부 응답은 기존 safe 500을 유지한다. 새 ErrorCode/ErrorSchema/4xx/503을 만들지 않는다. 잡지 않은 unknown 인프라 오류를 새로 catch-all하지 않는다. 안정된 public meaning이 별도로 승인된 경우에만 그 외부 계약에 맞는 controller mapping을 한다. 이미 선언된 계약 예외의 관찰 후 재던짐은 허용한다. raw infrastructure exception을 합성하거나 controller에서 직접 catch하는 우회도 금지한다.
 - **`preserve-established` retryability 호환**: 관찰 evidence가 승인한 brownfield handler에 permanent/retryable 구분이 이미 계약으로 존재하면 그 구분을 보존하고 영구장애를 retryable로 넓히지 않는다. 이는 해당 preserve scope의 compatibility 점검일 뿐 active code-profile에 raw infrastructure handler·recognizer를 요구하거나 허용하는 레시피가 아니다.
 - **framework-default 운영 보안**: unknown failure는 framework 500 경로를 유지한다. 배포 설정에서 `DEBUG=False`, traceback·sensitive data 비노출, BC `FrameworkErrorSchema` 변환 부재를 확인한다. framework-owned 401/403/route 404/422/429/general `HttpError` body는 정확한 code/profile 형식으로 고정하거나 exact-format 테스트를 요구하지 않는다.
 - **서버렌더 오류 분류 규율(plain Django view·CBV — API 규칙과 독립)**: 사용자에게 복구 가능한 도메인·애플리케이션 오류는 view-local 폼 재렌더와 `messages.error`로 입력·의미를 보존하고, 인프라·미식별 시스템 오류는 중앙 `handler500`/`500.html`로 보낸다(`implementation-django-web` §11). 레드 플래그(**important**): (a) view가 시스템 오류를 잡아 자체 에러 페이지나 200으로 삼킴, (b) 사용자 오류를 `handler500`으로 보내 메시지·입력을 잃음, (c) HTML용 local `process_exception`/middleware가 `OperationalError`의 permanent/retryable 의미를 구별하지 않고 통째 503/5xx로 올림, (d) view의 broad `except Exception`이 인프라 오류를 사용자 메시지로 둔갑시킴. invalid POST 폼 재렌더·승인된 transient를 local middleware가 503으로 분류함·HTMX error fragment(200/422)는 정상이다. 이 규율은 API error profile·handler 유무와 무관한 독립 server-rendered 의미 판정이며 reviewer가 직접 본다.
 - **외부 식별자 수치 입력의 상한(입력 계약)**: API operation 입력 schema의 외부 식별자·수치 필드(`product_id` 등)가 하한(`ge=`)만 두고 *상한*(`le=`/`lt=`/범위 validator)을 선언하지 않으면 **important** — 거대 입력이 스토리지 오버플로로 500이 되어 클라이언트 입력 오류(400/422 클래스)가 5xx로 오분류된다(`architecture-api` §5.1). **판정은 상한 *선언 유무*만**(값 불문) — 구체 경계값(매직넘버 `2^31-1`·`2^63-1`)은 필드·DB 타입 몫이라 특정 값을 강요하지 않는다.
 - **파일트리·구조·명명 준수 — 값은 정본, 기계 판정은 백스톱**: 트리·배치·명명의 «값»(어느 칸·어느 이름·어느 층·어느 파일)은 전부 `discipline-houserules` `references/final.md` §0(제1원칙)·§1(표준 트리 170행)·§2(골격 규칙)·§3(명명)·§4(이관 — brownfield=빚)가 소유한다 — 이 문서에는 값을 두지 않는다(값 사본은 썩는다 — 낡은 사본이 정본과 어긋난 사고가 이 절의 전신이다). 절차: ① 코드를 final.md 와 «직접» 대조한다 — 명세 부합만으로 통과시키지 않으며, **명세 자체가 §0 불변식·§2 골격 규칙·포트/칸 위치를 어긴 채 통과했으면 그 자체를 발견으로 올린다(설계 반송 — 명세 정당화는 면제 사유가 아니다)**. 레이아웃 대조 기준은 언제나 표준 트리다(houserules SKILL §1 — 소스 트리에 «기존 규약 존중» 케이스는 없다·기존 배치와의 일치는 통과 사유가 아니다; 승인된 test artifact 의 기존 테스트 위치(§1.2)만 예외로 그 위치와 대조한다). 이 대조의 대상은 **이번 작업의 diff(승인 스코프의 산출물)**다 — 범위 밖 legacy 잔존은 발견이 아니라 빚 보고 채널이고 거기서 수리·이동 지시를 만들지 않으며, 반대로 명세·구현이 승인 스코프 산출물 목록 밖 기존 파일을 이동·재배선했으면 «표준 트리 일치»는 통과 사유가 아니라 **그 이동 자체가 발견(설계 반송)**이다(2026-08-13 라운드 2 실증: 리뷰어가 «filesystem matches approved inventory»로 11 BC 이관을 통과시켰다). ② 경로·AST 로 서는 판정은 registry 결정적 백스톱(`commands/dddjango.md` 의 registry 표)이 소유한다 — 백스톱이 잡는 위반을 재판정하지 않고(이중 계상 금지), 반대로 **백스톱 exit 0 을 «의미 준수»의 증거로 읽지 않는다** — 형태로 못 가르는 의미 변종(개명 폴더·빈-정본 위장·변수 우회·간접 재수출·helper 재수출·이름-위장 클래스·모듈/lazy 싱글톤 공유 — build 팩토리가 반환·주입하는 객체가 import 나 첫 호출 시점 1회 생성으로 요청 간 공유되는 매요청 계약 위반 포함)은 네가 직접 읽는다. 단 «동명 폴더 승격» 폴더의 `__init__.py` 재수출은 세 조건 — 승격 허용 표기 칸 + 본체 `<이름>.py` 실존 + 자기 폴더 모듈의 명시적 이름 재수출(as-alias/`__all__`) — 전건 충족 시 정상 형태다(그 외 재수출 문면 판정은 그대로다). 어댑터 고정 패키지와 역할 폴더의 `__init__.py` 는 houserules §0의 재수출 전용 형태를 대조하며 승격 본체를 요구하지 않는다. 역할 배치·builder와 반환 계약의 동거·reader의 구현 소유도 해당 규범과 직접 대조한다. ③ 옛 이름 재등장은 트리 밖 칸 위반(#81·#490 — §4 이관 종료)이고 면제로 읽지 않는다. ④ 주석·docstring 언어가 프로젝트 관례(없으면 한국어)와 일치하는지도 여기서 본다(기계 밖). ⑤ 타입 규율은 `check-public-surface-annotation` 이 전면(시그니처·지역·속성·모듈/클래스) 기계 소유다 — 네 몫은 ⓓ#69 후보의 물음과, 면제 자리에 억지로 어노테이트해 ORM/enum 을 깨뜨리는 역방향 오류뿐이다.
-- **ACL 실패 번역 전수성(포트 계약 누수 — 기계 밖)**: ACL 이 호출하는 upstream 동작에서 consuming port/승인 명세가 known failure 로 선언한 의미는 consuming BC 의 own concrete 예외로 빠짐없이 번역되어야 한다 — 그 집합의 upstream 예외가 ACL 을 raw 통과하면 **blocker**. import 없는 propagation·helper·재수출 우회는 기계 밖이라 네가 직접 읽는다. 광범위 `except Exception` 을 요구하지 않으며, ACL·upstream repository 안에서 이미 승인 concrete 로 번역·소진된 실패는 누수가 아니다. raw DB/SDK/network unknown failure 는 이 전수 집합이 아니고 safe framework 500 이 기본이다(승인된 안정적 public meaning 이 있을 때만 owning infra/ACL 이 정규화).
+- **ACL 실패 번역 전수성(포트 계약 누수 — 기계 밖)**: ACL 이 호출하는 upstream 동작에서 consuming port/승인 명세가 known failure 로 선언한 의미는 consuming BC 의 own concrete 예외로 빠짐없이 번역되어야 한다 — 그 집합의 upstream 예외가 ACL 을 raw 통과하면 **blocker**. import 없는 propagation·helper·재수출 우회는 기계 밖이라 네가 직접 읽는다. 광범위 `except Exception` 을 요구하지 않으며, ACL·upstream repository 안에서 이미 승인 concrete 로 번역·소진된 실패는 누수가 아니다. 잡지 않은 raw DB/SDK/network unknown failure는 이 전수 집합이 아니고 safe framework 500이 기본이다. 이미 잡은 IntegrityError의 승인된 알려진 제약 실패는 구체 계약 예외로, 나머지는 승인된 일반 저장소 실패 계약으로 번역한다. repository 실패 계약은 domain 소유, capability port 실패 계약은 해당 port 소유다. 이 내부 정규화는 공개 HTTP 오류 승인이 아니므로 일반 저장소 실패의 외부 응답은 기존 safe 500을 유지한다. 새 ErrorCode/ErrorSchema/4xx/503을 만들지 않는다. 잡지 않은 unknown 인프라 오류를 새로 catch-all하지 않는다. 안정된 public meaning이 별도로 승인된 경우에만 그 외부 계약에 맞는 controller mapping을 한다. 이미 선언된 계약 예외의 관찰 후 재던짐은 허용한다.
 - **ⓓ 후보 마무리 — 백스톱이 좁히고 네가 닫는다(네 소유)**: 검사기는 기계로 못 닫는 자리를 `[ⓓ#N] 경로: 사실 — 물음: …` 줄로 낸다(exit 불산입 — 후보는 아직 위반이 아니다). 이 줄의 판정자는 너 하나다: 후보마다 그 물음에 답하고, 위반이면 심각도·근거(`파일:라인` + 규칙 번호)를 붙여 발견으로, 아니면 «후보 기각 — 사유 한 줄»로 리포트에 남긴다. 무응답 금지 — 후보를 흘리면 그 규칙은 판정자가 없다. 검사기가 후보를 아직 안 내는 자리도 물음은 같다(코드를 직접 볼 때 이 목록을 쓴다). 규칙 «번호»가 정본이고 어느 검사기가 내는지는 매핑표(rule-owner-map)가 소유한다. 물음 여덟이 후보 대부분을 덮는다(소유자 번호로 인용 · #628 재료의 실체는 `scripts/business_vocab.py`):
 
   | 물음(소유자) | 문면 | 쓰는 자리 |
   |---|---|---|
   | #181 | 두 번 와도 결과가 같나(멱등) | #181 · #532 · #603⑵ |
   | #595 | 그것(공급자·계기·수단)이 바뀌어도 이 이름이 그대로인가 | #584 · #594 · #512 |
   | #553 | 이 조건이 업무 규칙인가(Q2) | #553 · #607 · #589 · #475 · #316 (+Q2 표기 후보 전부) |
   | #565 | 업무가 이 단계 이름을 입으로 부르나 | #564 · #565 |
   | #590 | 이 값이 사람이 읽을 문구인가 | #590 · #618 |
   | #628 | 이 낱말이 이 BC 의 업무 어휘인가(도메인 공개 심볼 토큰 집합) | #425 · #448 (확정 소비자 #47·#372·#617 등은 기계) |
   | #11 | 이 손잡이를 «연 쪽»이 «닫기»까지 하나 | #11 |
   | #355 | 주어가 애그리거트인가 화면인가 | #355 · #285 |
 
   개별 물음(검사기 출력과 같은 문면 — 답의 기준):
   - 트리·골격 — #82 이 BC 폴더 이름이 업무의 낱말인가(#628 토큰 0회 후보 · 애그리거트명과 한 글자·복수형 «유사 변형»(`ordering` vs `order`)이면 반송 후보 — houserules final.md §3) · #36 이 이름에 예/아니오로 답하는 물음이 붙나 · #17·#18 이 이름이 업무의 낱말인가(Q1).
   - 컨텍스트 격리·창구 — #11 손잡이(위 표) · #151 이 창구 이름이 «무엇을 해 주는가»를 말하나 · #153 이 문장이 «계약↔응용 DTO 변환»인가 · #171 부르는 쪽이 이름만 보고 분기할 수 있나 · #347 이 조작을 사용자 API 도 하나.
   - 유스케이스·자료 — #68 이 검사의 값은 어디서 왔나(Q2) · #103 이것이 «되돌려 굽기»인가 업무 사용인가 · #140 검증이 다른 자리로 샜나(Q2) · #191 이 이름이 «판정이 되는 물음»인가(Q1) · #194 이 판정의 주인이 유스케이스인가(Q2) · #69 이 검사는 런타임이 아니라 테스트·타입 체커의 몫인가.
   - 결선·입구 — #86 이 분기는 업무를 가르는가(그렇다면 유스케이스로 내린다) · #511 이 입구의 계약을 바깥이 소유하는가(OAuth 콜백 포함 — 그러면 `webhook/<provider>/` 자리다) · #125 입구가 변환·1회 호출을 넘어 로직을 갖는가(그러면 유스케이스로 내린다).
-  - 도메인 모델 — #257 이 메서드 뒤에도 불변식이 참인가(Q4) · #259 이것이 값인가 엔티티인가(Q4) · #268 이 타입 조합만으로 잘못된 값이 «불가능»한가(Q2) · #301 이 규칙이 «없을 때»를 판정하나(루트 메서드로 표현될 수 있나) · #311 이 이름이 규칙 «행위»를 말하나 · #547 이 둘이 «동시에» 일어나면 업무가 정말 막아야 하나 / 서로 다른 일을 하는 두 사용자가 이 경계로 충돌하나(Q4) · #565 단계 이름(위 표).
+  - 도메인 모델 — #257 이 메서드 뒤에도 불변식이 참인가(Q4) · #259 이것이 값인가 엔티티인가(Q4) · #268 닫힌 표준 Enum/StrEnum/IntEnum은 생성 검증 후보에서 제외하고, custom/open Enum은 raise 유무와 별개로 타입 조합만으로 잘못된 값이 «불가능»한지 묻는다(Q2) · #301 이 규칙이 «없을 때»를 판정하나(루트 메서드로 표현될 수 있나) · #311 이 이름이 규칙 «행위»를 말하나 · #546 해소된 동일 트랜잭션 영역의 서로 다른 repository/aggregate 타입 쓰기는 확정이고, 영역·출처 미해소는 후보로 같은 트랜잭션인지 확인한다(순차 독립 UoW는 합치지 않으며 nested/외부 atomic은 결합한다) · #547 이 둘이 «동시에» 일어나면 업무가 정말 막아야 하나 / 서로 다른 일을 하는 두 사용자가 이 경계로 충돌하나(Q4) · #565 단계 이름(위 표).
   - 사실(이벤트) — #271 이 이름이 «이미 일어난 사실»을 말하나 · #564 이 칸이 «패턴»이 아니라 «진행표»인가(단계 물음).
   - 트랜잭션·리포지토리 — #285 이 수가 «애그리거트 컬렉션»을 세거나 합친 것인가 · #355 주어(위 표).
   - 브로커 — #520 이 사실이 안 나가면 내가 할 일이 있나 · #529 듣는 쪽이 따로 배포되나 · #532 받는 쪽이 「안 왔을 때」와 「두 번 왔을 때」를 메우고 있나(#181).
   - 놓칠 수 있는 입구 — #181 멱등(위 표) · #451 이 창구가 «혼자서» 답을 만들 수 있나 · #512 보내는 쪽 문서가 자기를 이 이름으로 부르나 · #629 이 입구가 «안 와도» 업무가 돌아가나.
   - admin·표현 — #343 이 문장이 운영 «기능»인가 장고 «배선»인가 · #589 이 조건이 업무 판정인가(Q2) · #590 문구(위 표) · #347(위 격리 줄).
-  - 포트·어댑터 — #227 이 자료를 원시값 인자로 «펴서» 넘길 수 있나 · #233 무엇을 알고 싶은가가 이름에 있나(Q1) · #368 이게 «기계»인가 «값»인가 · #475 이 판정이 업무 규칙인가(Q2) · #485 이 이름이 무엇을 시키는지 말하나 · #553 Q2(위 표) · #594·#595 이름 안정(위 표).
+
+  **admin context 판정**: #493 주석 존재 유지 · #645 framework 소유 슬롯 Any 제한 허용 · #646 제네릭 런타임 안전 유지 · #647 열린 UI context 조립/병합/전달 허용 · #650 실제 JSON 소비 검증 유지다. 출처가 확인된 Django admin 및 Parler admin 계열의 고정 framework 슬롯에만 적용한다. `extra_context`/`context`의 받기·each_context·UI dict·copy/update·고정 UI 키 쓰기·framework render 전달과 연결된 private 전달 helper의 매개변수·반환·지역 context 주석을 허용한다. form/inline/media의 별도 조립은 context의 허용을 취소하지 않는다. 컨테이너 부재 처리와 request UI metadata의 담기·전달도 허용한다. 업무 읽기·비교·계산·상태 변경 또는 ORM/use case/업무 함수로의 값 전달은 실제 소비이므로 그 자리부터 기존 규칙을 적용한다. 출처나 소비가 미해소 또는 동적/재귀 호출로 escape한 연결 context는 후보로 남겨 확인한다. 이름만 context인 값·같은 함수의 별도 업무 dict·framework 고정 kwargs 밖 bare Any·admin 클래스/경로 전체는 면제하지 않는다. 생성 private helper는 본문이 없으므로 정확히 결합된 열린 dict 슬롯의 #645/#647만 S1 미검증으로 보고하고 G2에서 실제 소비 흐름으로 다시 판단한다.
+  - 포트·어댑터 — #227 이 자료를 원시값 인자로 «펴서» 넘길 수 있나 · #233 무엇을 알고 싶은가가 이름에 있나(Q1) · #368 이게 «기계»인가 «값»인가 · #475 이 판정이 업무 규칙인가(Q2) · #485 이 이름이 무엇을 시키는지 말하나 · #553 Q2(위 표) · #594·#595 이름 안정(위 표). · #557 비교하는 code/errno/status_code 수신자의 출처가 확인된 vendor이면 확정, 확인된 우리 계약이면 허용, 미해소/혼합이면 후보로 그 코드의 주인을 묻는다.
   - framework·어휘 — #425 이 재료의 뜻을 밖(HTTP·pytest·시간)이 정하나 · #448 이 낱말의 뜻을 저장소 밖이 정하나 · #607 이 조건이 업무 규칙인가(Q2) · #618 문구(#590) · #619 이것이 원시값 하나로 되나 · #584 이름 안정(#595).
   - 정본 문서(주어가 코드가 아니다) — #492 이 행이 «있어야 하나»를 말하나 «어떻게 쓰나»를 말하나.
 - **human 판정 둘 — 검사기가 아예 없다(전적으로 네 몫)**: ① **#254** 애그리거트 폴더는 «항상 함께 옳아야 하는 것» 한 묶음이다 — 기계(#546·#547)는 «너무 갈린 쪽»만 본다. «너무 묶인 쪽»은 네가 묻는다: 「서로 다른 일을 하는 두 사용자가 이 경계로 충돌하나」 — 충돌하면 가짜 불변식이라 경계를 쪼개는 방향으로 발견을 올린다(설계 반송). ② **#316** 재료를 한 번에 못 모으는 경우(판정 결과에 따라 다음 조회가 달라질 때)에도 규칙을 풀지 않는다 — 판정이 「도메인 판정 → 응용 조회 → 도메인 판정」 두 조각으로 쪼개졌는지 본다(전건이 코드에 흔적을 안 남기니 유스케이스 흐름을 직접 읽는다 — Q2).
 - **면제 조문 — 새 의무 금지**: #15 #16 #23 #24 #25 #26 #27 #56 #100 #127 #137 #145 #248 #346 #522 #625 는 «면제»를 선언하는 조문이다(문면은 정본 명세 소유). 이 번호들로 새 검사·새 의무를 만들지 않으며, 후보·발견이 이 조문의 면제에 정확히 들면 그 번호를 인용해 기각한다.
 
 로드한 discipline-cleancode·discipline-tdd·implementation-test·discipline-houserules 스킬의 절을 근거로 인용한다.
 
 ## 경계
 <!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->
 

```

## codex-dddjango/skills/dddjango-discipline-reviewer/SKILL.md

Before SHA256: a684feab856e82966cfedacab9f1f3152f17c80e96039b76fd307b2d98c3b676
After SHA256: 1a9c7ce4f52c1ac2f3fbfdbeb77017792764d3ff4673134648b8f0425df19f3f

```diff
--- before/codex-dddjango/skills/dddjango-discipline-reviewer/SKILL.md
+++ after/codex-dddjango/skills/dddjango-discipline-reviewer/SKILL.md
@@ -77,52 +77,54 @@
 - **상수 승격·심볼 소비 규율(백스톱 사각 전담)**: **이번 작업이 touched한 코드만 본다 — untouched 기존 리터럴은 면제(grandfather)**. ① 닫힌 집합의 원소(도메인 상태·종류·wire enum성 문자열)를 우리 코드가 분기·판정하는데 집합 타입(domain `StrEnum`/`choices` 파생) 없이 원시 리터럴로 산재하면 **important**(1곳째부터 승격 — `dddjango-discipline-cleancode` §2.14; 단 그 산재가 같은-지식 중복 정리 사안이면 위 클린코드 불릿의 DRY로만 분류, 이중 계상 금지). ② Enum/choices가 *선언돼 있는데* 소비처가 리터럴로 비교·`.filter()`·대입하면 **important** — 결정적 백스톱 `check-choices-literal-consumption`이 직접형(`default=` 리터럴·`<Model>.objects.filter(<field>="…")`)을 잡으므로 네가 보는 건 그 사각이다: 변수 우회·간접 queryset(`qs.filter(...)`)·비교식(`x.status == "…"`)·`__in` 변종. **심볼 치환은 판정 소유 위반을 면책하지 않는다** — 그 사건이 복합 판정의 소유 문제면 위 '죽은 도메인 메서드·판정 인프라 누수' 불릿 하나로만 분류한다(이중 계상 금지). ③ 도메인 판정 값 집합이 `models.TextChoices`로 선언돼 domain이 ORM 타입을 역참조하면 **important**(계층 소유 — 단일 출처는 domain enum·ORM은 `.value` 평탄화 파생; `implementation-django` §2.5. 구조 이주 사안이면 아래 파일트리 불릿과 이중 계상 금지 — 값 집합 소유만 여기). ④ 테스트가 **외부 관찰 계약**(HTTP 응답·DB 저장값·이벤트)의 assert 기댓값에 프로덕션 Enum·상수를 역수입하면 **important**(자기참조 오라클 — `dddjango-implementation-test` §15.4; 위 테스트 품질 불릿과는 별개 렌즈 — 오라클 자기참조만 여기). ⑤ 우리 BC가 **발행하는 이벤트 봉투의 discriminator**(태그드 유니온 태그 — `event_type` 류)가 domain `StrEnum` 파생(`Literal[EventType.X] = EventType.X`) 없이 맨 문자열 `Literal["…"]`·원시 str로 선언되면 **important**(1종째부터 — birth-enum `dddjango-architecture-ddd` §3.7; 대응 백스톱 없음 — 버전 태그와 AST 형태가 동일해 형태 판정은 FP 불가피, "발행 봉투인가"의 위치 판정은 전적으로 네 몫). union-enum 동기 후보는 별도 입장 행이 `add/update`이고 독자 failure를 승인한 경우에만 그 행의 mechanics를 감사한다. 입장 행이 없으면 동기 테스트를 즉석에서 요구하지 않고 candidate로 설계 반송한다. **⑤의 제외**: `payload_schema_version`류 버전 태그(리터럴 동결이 정답 — enum화가 오히려 위반 방향), 상류 이벤트를 중계만 하는 소비 측 스키마의 태그(published language 수용 — 소비 BC는 발행 enum을 import하지 않는다), 데이터소스 BC, OHS published contract(`open_host_service/*/contract/`)의 discriminator wire `Literal`(contract 무의존이 우선 — houserules `references/final.md` §1 트리 22~32행 — OHS 내부 구조; 동기 테스트는 승인 입장 행이 있을 때만 감사한다). ①과 배타: ①은 분기·판정 앵커의 미승격, ⑤는 발행 봉투 위치의 선언 형태(분기 존재 무관) — 한 사건은 하나로만 분류(이중 계상 금지). **거짓지적 방지(잡지 않는다)**: 도메인 내부 단위 테스트의 심볼 단언·테스트 arrange/act의 심볼 사용, 로그·예외 메시지 등 사람 대상 서술, Enum·상수 정의부 우변, `.value` 평탄화 파생(`default=OrderStatus.PENDING.value`), `Literal[...]`로 잠긴 인자 자리(단 발행 봉투 discriminator는 ⑤의 대상 — 맨 문자열 Literal이면 잡는다; 버전 태그는 여기 그대로 허용), 외부 프로토콜 소유 문자열(분기 조건인데 adapter 정규화 부재면 nit로만), 설정 키·환경변수명, 마이그레이션 historical value(살아있는 Enum 참조가 오히려 위반 — `implementation-django` §10.4), pass-through 저장·데이터소스 BC의 미승격, 한 파일 로컬 문자열, 우연히 같은 값·다른 지식의 미통합(합치면 오히려 위반). 근거 `dddjango-discipline-cleancode` §2.14·`implementation-django` §2.5·§10.4·`dddjango-architecture-ddd` §2.5·§3.2·§3.7·`dddjango-implementation-test` §15.4·§15.5.
 - **메커니즘-소유권 규율**: 엔진·연결의 트랜잭션·락·격리 *메커니즘*은 설계(architect)가 소유한다 — 코드가 명세 승인 없이 그 의미를 바꾸지 않았는가. 레드 플래그(**blocker**): 프로덕션 `DATABASES.ENGINE`를 커스텀 백엔드로 교체, `DatabaseWrapper` 상속으로 `BEGIN`/begin 모드·`_start_transaction_under_autocommit` 변경, 런타임 몽키패치, `connection_created` 시그널, `OPTIONS.init_command`로 `BEGIN`/PRAGMA 주입, `isolation_level`·`locking_mode` 조작, DB 미들웨어, 테스트 conftest 패치 — *어떤 형태든* 동일 위반(`implementation-django` §16.4·`architecture-db` §9.5). **허용(통과)**: stock `OPTIONS`(`transaction_mode`[5.1+]·`timeout`)와 안전 PRAGMA 화이트리스트(`foreign_keys`·`busy_timeout`·`synchronous`·`cache_size`), 그리고 명세가 명시 승인한 메커니즘. **예외**: 이번 diff에 새로 들어온 변경만 본다(기존 코드 존중), 프로덕션 경로에 배선되지 않은 테스트 격리 전용 설정은 통과. 이는 **책임 배치·소유권 규율**(메커니즘을 누가 정하는가)이지 ORM/쿼리 정확성 판정이 아니다 — 네가 본다.
 - **API 오류 규율 1 — common/BC 소유권·승인 shape(blocker)**: active `dddjango-code-json` scope의 canonical common module은 승인된 공통 `FrameworkErrorSchema` 하나와 승인 shape만 소유하며 BC concrete를 두지 않는다. 공통 shape를 새로 만들거나 바꾸면서 일반 G1과 분리된 명시적 사용자 shape-승인 evidence가 없으면 blocker다. public 오류가 있는 각 BC의 canonical `driving_layer/api/bc_error_schema.py`만 `<Bc>ErrorCode(StrEnum)` 하나·`<Bc>ErrorSchema` 하나·그 BC concrete 전부를 소유한다. Ninja/`FrameworkErrorSchema`/HTTP DTO를 domain·application에 import하지 않는 것만으로는 부족하다. import-free DTO·VO라도 HTTP `status`/`code` 의미를 inner layer에 운반해 presentation이 소비하면 blocker다. 이름이 `status`인 정당한 도메인 상태는 값의 의미와 소비 경로가 HTTP 선택과 무관한지로 구별한다.
 - **API 오류 규율 2 — helper/handler/factory/serializer/mapping 우회(blocker)**: active code-profile managed surface에는 `@*.exception_handler`, `add_exception_handler`, `FrameworkErrorSchema` serializer·response helper, central converter, concrete fixed-value factory, exception→`FrameworkErrorSchema` dict/table, generic response builder나 이름만 바꾼 동형 추출을 만들거나 호출하지 않는다. controller의 짧은 failure→prepared error→`Status` mapping 반복은 의도된 명시성이므로 DRY 위반으로 잡지 않는다. 성공 Schema·download·streaming·redirect·schema-less 204의 framework-native 반환은 이 오류-helper 금지 밖이다. 승인된 `preserve-established` scope의 기존 handler는 관찰 evidence가 지정한 범위에서만 보존하며 새 code-profile의 정당화로 재사용하지 않는다.
 - **API 오류 규율 3 — controller path·좁은 try·구체 catch(blocker)**: active `dddjango-code-json` scope에서 10번 slot이 승인한 path와 코드를 대조한다. exception path는 입력·request·use-case 준비를 `try` 밖에 두고 `try` 안에는 최외곽 application call 정확히 한 문장만 둔다. branch·성공 변환·logging을 함께 넣지 않으며, 같은 owning BC에서 import한 승인 concrete exception 또는 concrete만 든 tuple만 catch한다. bare/`Exception`/`BaseException`, raw DB·SDK·framework exception, controller의 cross-BC exception, broad base의 재수출 alias, non-concrete가 하나라도 섞인 tuple은 blocker다. managed `try` 안에서 방금 raise해 즉시 catch하기, `HttpError` forwarding, re-raise, handler forwarding도 금지한다. `None` path(조회의 «없다» 한정)는 application call을 정확히 한 번 수행하고 인위적 `try`·exception 없이 call 직후 `is None` branch에서 직접 mapping한다. 실패를 Result variant·outcome 값으로 돌려받아 분기하는 controller는 blocker다(`<use_case>_result.py`엔 성공 한 벌만 — #571; exception path여야 한다). ACL/OHS가 승인된 known upstream failure를 consuming BC의 own concrete exception으로 번역하는 것은 controller의 금지된 cross-BC catch와 구별한다.
 - **API 오류 규율 4 — prepared FrameworkErrorSchema·직접 응답(blocker)**: active `dddjango-code-json` scope에서 승인된 concrete는 full approved slot-6 common shape 중 그 concrete의 fixed value로 승인된 모든 field 값을 class default로 제공하고 인자 없이 생성 가능해야 한다. class default는 concrete가 직접 선언하거나 intended value와 같은 승인된 base default를 상속할 수 있으며, 후자라면 불필요한 재선언을 요구하지 않는다. 사건별 direct BC-base construction이 승인됐으면 owning BC base에 승인 slot-6 required field 전부와 사건별로 기본값을 덮어써야 하는 approved optional field만 명시적으로 공급한다. catch 또는 failed branch는 그 error를 준비한 직후 두 인자 `Status(<literal/status constant 또는 slot-6 body field>, error)`를 직접 반환한다. plugin이 `status` body property를 요구하면 blocker다. 승인된 response header는 그 직전 controller에 주입된 응답용(temporal) Django `HttpResponse`에 쓴다. 오류 tuple, raw `Response`/`JsonResponse`/`HttpResponse`, dict body, factory·serializer·helper indirection은 blocker다.
 - **API 오류 규율 5 — returned status·OpenAPI·framework default(blocker)**: active `dddjango-code-json` scope에서 operation이 실제 직접 반환하는 모든 BC 오류 status는 `response={...}`에서 같은 BC base로 선언되어야 하고, 승인된 endpoint→status→BC-base mapping tuple·runtime 반환·generated OpenAPI의 status/schema 출현은 완전하며 서로 같아야 한다. framework-owned 401/403/route 404/422/429/general `HttpError`/unknown 500은 BC 오류로 직접 반환하거나 BC base로 광고하지 않는다. auth backend는 성공 시 identity/principal, 실패 시 `None` 또는 framework `AuthenticationError`만 반환·raise하며 truthy `FrameworkErrorSchema`/Schema를 `request.auth`에 넣지 않는다. framework-established header dependency를 숨기거나 명세에 없는 header를 꾸며내지 않는다. status→BC base 선언만으로 허용 식별자 subset이 증명되지 않으므로 실제 runtime mapping case 검증을 생략하지 않는다.
 - **API 오류 5축 profile 경계**: 위 1~5축은 active `dddjango-code-json` scope에만 적용한다. `preserve-established` scope는 slot/evidence가 승인한 native exception forwarding·handler·body/return form·mapping mechanism을 보존하며, 이 5축을 이유로 code-profile에 이주하지 않는다. (이 경계는 오류 5축에 한한다 — 배선·등록은 아래 «API instance·registrar·composition 규율»이 profile 무관으로 소유한다.)
 - **API 오류 checker/reviewer 사각(명시 검토)**: 관련 checker가 exit 0이어도 semantic compliance의 증거가 아니다. 반드시 (a) 직접 import한 1-hop class method mutation·2-hop helper·선택 source 밖 helper·renamed converter, (b) dynamic import/registration·required symbol 재수출, (c) 문법상 concrete 이름이나 의미상 broad base인 exception, (d) Ninja/`FrameworkErrorSchema` import 없이 inner layer를 흐르는 HTTP status/code DTO, (e) project-wide inventory 완전성·mixed-profile shared module·scope 안의 API instance 복수, (f) root-local catalog/mapping·registrar/composition lookalike, (g) auth backend의 truthy `FrameworkErrorSchema`/Schema와 숨은 framework-header dependency를 직접 읽는다.
 - **API instance·registrar·composition 규율**: active `dddjango-code-json` contract scope마다 project `<project>/api.py`가 API instance 하나를 소유한다. 각 BC의 side-effect-free api_router(`driving_layer/api/api_router.py`의 `register_<bc>_api` — final.md §1 9행)는 전달받은 API에 자기 controller만 등록하고, project `urls.py`가 각 registrar를 명시적으로 한 번 호출한 뒤 API를 mount한다. controller는 `auto_import=False`여야 하며 project API import·module-top-level 등록·dynamic registrar·import-time side effect·scope 안의 API 복수는 blocker다. HTTP registrar와 DI-only `composition_root/`(트리 2~4행)를 섞지 않고, root-local catalog/mapping 또는 registrar/composition lookalike도 직접 확인한다. controller 형태는 승인된 presentation 계약을 보존한다. 오류 대응, 특히 406/415를 이유로 승인된 class controller를 함수형 `Router`로 바꾸거나 별도 API instance로 격리하지 않는다. `preserve-established` scope 에서도 **registration/composition 은 이 표준으로 대조한다** — preserve 가 보존하는 것은 오류 wire 산출물이지 배선이 아니다(구 «native registration/API-instance layout 보존» 문구는 라운드 1′ 배선 답습의 통로로 실증되어 걷었다 — 2026-08-12). 배선 표준화가 오류 profile 이주를 뜻하지도 않는다 — 오류 산출물은 slot 승인대로 유지한다. Phase 1의 project-wide inventory와 mixed-profile sharing 점검은 profile에 관계없이 유지한다.
-- **raw infrastructure 기본 경계**: raw DB/SDK/network exception은 safe framework 500으로 둔다. global recognizer·retryable handler·문자열/SQLSTATE 분류를 요구하거나 새 code-profile에 추가하지 않는다. 특정 실패가 안정된 public meaning을 가진다고 G1에서 명시 승인된 경우에만 owning infra/ACL이 그 실패를 consuming BC의 own concrete domain/application exception으로 정규화하고, 그 BC controller가 위 직접 흐름으로 mapping한다. raw infrastructure exception을 합성하거나 controller에서 직접 catch하는 우회도 금지한다.
+- **raw infrastructure 기본 경계**: raw DB/SDK/network exception은 safe framework 500으로 둔다. global recognizer·retryable handler·문자열/SQLSTATE 분류를 요구하거나 새 code-profile에 추가하지 않는다. 이미 잡은 IntegrityError의 승인된 알려진 제약 실패는 구체 계약 예외로, 나머지는 승인된 일반 저장소 실패 계약으로 번역한다. repository 실패 계약은 domain 소유, capability port 실패 계약은 해당 port 소유다. 이 내부 정규화는 공개 HTTP 오류 승인이 아니므로 일반 저장소 실패의 외부 응답은 기존 safe 500을 유지한다. 새 ErrorCode/ErrorSchema/4xx/503을 만들지 않는다. 잡지 않은 unknown 인프라 오류를 새로 catch-all하지 않는다. 안정된 public meaning이 별도로 승인된 경우에만 그 외부 계약에 맞는 controller mapping을 한다. 이미 선언된 계약 예외의 관찰 후 재던짐은 허용한다. raw infrastructure exception을 합성하거나 controller에서 직접 catch하는 우회도 금지한다.
 - **`preserve-established` retryability 호환**: 관찰 evidence가 승인한 brownfield handler에 permanent/retryable 구분이 이미 계약으로 존재하면 그 구분을 보존하고 영구장애를 retryable로 넓히지 않는다. 이는 해당 preserve scope의 compatibility 점검일 뿐 active code-profile에 raw infrastructure handler·recognizer를 요구하거나 허용하는 레시피가 아니다.
 - **framework-default 운영 보안**: unknown failure는 framework 500 경로를 유지한다. 배포 설정에서 `DEBUG=False`, traceback·sensitive data 비노출, BC `FrameworkErrorSchema` 변환 부재를 확인한다. framework-owned 401/403/route 404/422/429/general `HttpError` body는 정확한 code/profile 형식으로 고정하거나 exact-format 테스트를 요구하지 않는다.
 - **서버렌더 오류 분류 규율(plain Django view·CBV — API 규칙과 독립)**: 사용자에게 복구 가능한 도메인·애플리케이션 오류는 view-local 폼 재렌더와 `messages.error`로 입력·의미를 보존하고, 인프라·미식별 시스템 오류는 중앙 `handler500`/`500.html`로 보낸다(`implementation-django-web` §11). 레드 플래그(**important**): (a) view가 시스템 오류를 잡아 자체 에러 페이지나 200으로 삼킴, (b) 사용자 오류를 `handler500`으로 보내 메시지·입력을 잃음, (c) HTML용 local `process_exception`/middleware가 `OperationalError`의 permanent/retryable 의미를 구별하지 않고 통째 503/5xx로 올림, (d) view의 broad `except Exception`이 인프라 오류를 사용자 메시지로 둔갑시킴. invalid POST 폼 재렌더·승인된 transient를 local middleware가 503으로 분류함·HTMX error fragment(200/422)는 정상이다. 이 규율은 API error profile·handler 유무와 무관한 독립 server-rendered 의미 판정이며 reviewer가 직접 본다.
 - **외부 식별자 수치 입력의 상한(입력 계약)**: API operation 입력 schema의 외부 식별자·수치 필드(`product_id` 등)가 하한(`ge=`)만 두고 *상한*(`le=`/`lt=`/범위 validator)을 선언하지 않으면 **important** — 거대 입력이 스토리지 오버플로로 500이 되어 클라이언트 입력 오류(400/422 클래스)가 5xx로 오분류된다(`architecture-api` §5.1). **판정은 상한 *선언 유무*만**(값 불문) — 구체 경계값(매직넘버 `2^31-1`·`2^63-1`)은 필드·DB 타입 몫이라 특정 값을 강요하지 않는다.
 - **파일트리·구조·명명 준수 — 값은 정본, 기계 판정은 백스톱**: 트리·배치·명명의 «값»(어느 칸·어느 이름·어느 층·어느 파일)은 전부 `dddjango-discipline-houserules` `references/final.md` §0(제1원칙)·§1(표준 트리 170행)·§2(골격 규칙)·§3(명명)·§4(이관 — brownfield=빚)가 소유한다 — 이 문서에는 값을 두지 않는다(값 사본은 썩는다 — 낡은 사본이 정본과 어긋난 사고가 이 절의 전신이다). 절차: ① 코드를 final.md 와 «직접» 대조한다 — 명세 부합만으로 통과시키지 않으며, **명세 자체가 §0 불변식·§2 골격 규칙·포트/칸 위치를 어긴 채 통과했으면 그 자체를 발견으로 올린다(설계 반송 — 명세 정당화는 면제 사유가 아니다)**. 레이아웃 대조 기준은 언제나 표준 트리다(houserules SKILL §1 — 소스 트리에 «기존 규약 존중» 케이스는 없다·기존 배치와의 일치는 통과 사유가 아니다; 승인된 test artifact 의 기존 테스트 위치(§1.2)만 예외로 그 위치와 대조한다). 이 대조의 대상은 **이번 작업의 diff(승인 스코프의 산출물)**다 — 범위 밖 legacy 잔존은 발견이 아니라 빚 보고 채널이고 거기서 수리·이동 지시를 만들지 않으며, 반대로 명세·구현이 승인 스코프 산출물 목록 밖 기존 파일을 이동·재배선했으면 «표준 트리 일치»는 통과 사유가 아니라 **그 이동 자체가 발견(설계 반송)**이다(2026-08-13 라운드 2 실증: 리뷰어가 «filesystem matches approved inventory»로 11 BC 이관을 통과시켰다). ② 경로·AST 로 서는 판정은 registry 결정적 백스톱(`commands/dddjango.md` 의 registry 표)이 소유한다 — 백스톱이 잡는 위반을 재판정하지 않고(이중 계상 금지), 반대로 **백스톱 exit 0 을 «의미 준수»의 증거로 읽지 않는다** — 형태로 못 가르는 의미 변종(개명 폴더·빈-정본 위장·변수 우회·간접 재수출·helper 재수출·이름-위장 클래스·모듈/lazy 싱글톤 공유 — build 팩토리가 반환·주입하는 객체가 import 나 첫 호출 시점 1회 생성으로 요청 간 공유되는 매요청 계약 위반 포함)은 네가 직접 읽는다. 단 «동명 폴더 승격» 폴더의 `__init__.py` 재수출은 세 조건 — 승격 허용 표기 칸 + 본체 `<이름>.py` 실존 + 자기 폴더 모듈의 명시적 이름 재수출(as-alias/`__all__`) — 전건 충족 시 정상 형태다(그 외 재수출 문면 판정은 그대로다). 어댑터 고정 패키지와 역할 폴더의 `__init__.py` 는 houserules §0의 재수출 전용 형태를 대조하며 승격 본체를 요구하지 않는다. 역할 배치·builder와 반환 계약의 동거·reader의 구현 소유도 해당 규범과 직접 대조한다. ③ 옛 이름 재등장은 트리 밖 칸 위반(#81·#490 — §4 이관 종료)이고 면제로 읽지 않는다. ④ 주석·docstring 언어가 프로젝트 관례(없으면 한국어)와 일치하는지도 여기서 본다(기계 밖). ⑤ 타입 규율은 `check-public-surface-annotation` 이 전면(시그니처·지역·속성·모듈/클래스) 기계 소유다 — 네 몫은 ⓓ#69 후보의 물음과, 면제 자리에 억지로 어노테이트해 ORM/enum 을 깨뜨리는 역방향 오류뿐이다.
-- **ACL 실패 번역 전수성(포트 계약 누수 — 기계 밖)**: ACL 이 호출하는 upstream 동작에서 consuming port/승인 명세가 known failure 로 선언한 의미는 consuming BC 의 own concrete 예외로 빠짐없이 번역되어야 한다 — 그 집합의 upstream 예외가 ACL 을 raw 통과하면 **blocker**. import 없는 propagation·helper·재수출 우회는 기계 밖이라 네가 직접 읽는다. 광범위 `except Exception` 을 요구하지 않으며, ACL·upstream repository 안에서 이미 승인 concrete 로 번역·소진된 실패는 누수가 아니다. raw DB/SDK/network unknown failure 는 이 전수 집합이 아니고 safe framework 500 이 기본이다(승인된 안정적 public meaning 이 있을 때만 owning infra/ACL 이 정규화).
+- **ACL 실패 번역 전수성(포트 계약 누수 — 기계 밖)**: ACL 이 호출하는 upstream 동작에서 consuming port/승인 명세가 known failure 로 선언한 의미는 consuming BC 의 own concrete 예외로 빠짐없이 번역되어야 한다 — 그 집합의 upstream 예외가 ACL 을 raw 통과하면 **blocker**. import 없는 propagation·helper·재수출 우회는 기계 밖이라 네가 직접 읽는다. 광범위 `except Exception` 을 요구하지 않으며, ACL·upstream repository 안에서 이미 승인 concrete 로 번역·소진된 실패는 누수가 아니다. 잡지 않은 raw DB/SDK/network unknown failure는 이 전수 집합이 아니고 safe framework 500이 기본이다. 이미 잡은 IntegrityError의 승인된 알려진 제약 실패는 구체 계약 예외로, 나머지는 승인된 일반 저장소 실패 계약으로 번역한다. repository 실패 계약은 domain 소유, capability port 실패 계약은 해당 port 소유다. 이 내부 정규화는 공개 HTTP 오류 승인이 아니므로 일반 저장소 실패의 외부 응답은 기존 safe 500을 유지한다. 새 ErrorCode/ErrorSchema/4xx/503을 만들지 않는다. 잡지 않은 unknown 인프라 오류를 새로 catch-all하지 않는다. 안정된 public meaning이 별도로 승인된 경우에만 그 외부 계약에 맞는 controller mapping을 한다. 이미 선언된 계약 예외의 관찰 후 재던짐은 허용한다.
 - **ⓓ 후보 마무리 — 백스톱이 좁히고 네가 닫는다(네 소유)**: 검사기는 기계로 못 닫는 자리를 `[ⓓ#N] 경로: 사실 — 물음: …` 줄로 낸다(exit 불산입 — 후보는 아직 위반이 아니다). 이 줄의 판정자는 너 하나다: 후보마다 그 물음에 답하고, 위반이면 심각도·근거(`파일:라인` + 규칙 번호)를 붙여 발견으로, 아니면 «후보 기각 — 사유 한 줄»로 리포트에 남긴다. 무응답 금지 — 후보를 흘리면 그 규칙은 판정자가 없다. 검사기가 후보를 아직 안 내는 자리도 물음은 같다(코드를 직접 볼 때 이 목록을 쓴다). 규칙 «번호»가 정본이고 어느 검사기가 내는지는 매핑표(rule-owner-map)가 소유한다. 물음 여덟이 후보 대부분을 덮는다(소유자 번호로 인용 · #628 재료의 실체는 `scripts/business_vocab.py`):
 
   | 물음(소유자) | 문면 | 쓰는 자리 |
   |---|---|---|
   | #181 | 두 번 와도 결과가 같나(멱등) | #181 · #532 · #603⑵ |
   | #595 | 그것(공급자·계기·수단)이 바뀌어도 이 이름이 그대로인가 | #584 · #594 · #512 |
   | #553 | 이 조건이 업무 규칙인가(Q2) | #553 · #607 · #589 · #475 · #316 (+Q2 표기 후보 전부) |
   | #565 | 업무가 이 단계 이름을 입으로 부르나 | #564 · #565 |
   | #590 | 이 값이 사람이 읽을 문구인가 | #590 · #618 |
   | #628 | 이 낱말이 이 BC 의 업무 어휘인가(도메인 공개 심볼 토큰 집합) | #425 · #448 (확정 소비자 #47·#372·#617 등은 기계) |
   | #11 | 이 손잡이를 «연 쪽»이 «닫기»까지 하나 | #11 |
   | #355 | 주어가 애그리거트인가 화면인가 | #355 · #285 |
 
   개별 물음(검사기 출력과 같은 문면 — 답의 기준):
   - 트리·골격 — #82 이 BC 폴더 이름이 업무의 낱말인가(#628 토큰 0회 후보 · 애그리거트명과 한 글자·복수형 «유사 변형»(`ordering` vs `order`)이면 반송 후보 — houserules final.md §3) · #36 이 이름에 예/아니오로 답하는 물음이 붙나 · #17·#18 이 이름이 업무의 낱말인가(Q1).
   - 컨텍스트 격리·창구 — #11 손잡이(위 표) · #151 이 창구 이름이 «무엇을 해 주는가»를 말하나 · #153 이 문장이 «계약↔응용 DTO 변환»인가 · #171 부르는 쪽이 이름만 보고 분기할 수 있나 · #347 이 조작을 사용자 API 도 하나.
   - 유스케이스·자료 — #68 이 검사의 값은 어디서 왔나(Q2) · #103 이것이 «되돌려 굽기»인가 업무 사용인가 · #140 검증이 다른 자리로 샜나(Q2) · #191 이 이름이 «판정이 되는 물음»인가(Q1) · #194 이 판정의 주인이 유스케이스인가(Q2) · #69 이 검사는 런타임이 아니라 테스트·타입 체커의 몫인가.
   - 결선·입구 — #86 이 분기는 업무를 가르는가(그렇다면 유스케이스로 내린다) · #511 이 입구의 계약을 바깥이 소유하는가(OAuth 콜백 포함 — 그러면 `webhook/<provider>/` 자리다) · #125 입구가 변환·1회 호출을 넘어 로직을 갖는가(그러면 유스케이스로 내린다).
-  - 도메인 모델 — #257 이 메서드 뒤에도 불변식이 참인가(Q4) · #259 이것이 값인가 엔티티인가(Q4) · #268 이 타입 조합만으로 잘못된 값이 «불가능»한가(Q2) · #301 이 규칙이 «없을 때»를 판정하나(루트 메서드로 표현될 수 있나) · #311 이 이름이 규칙 «행위»를 말하나 · #547 이 둘이 «동시에» 일어나면 업무가 정말 막아야 하나 / 서로 다른 일을 하는 두 사용자가 이 경계로 충돌하나(Q4) · #565 단계 이름(위 표).
+  - 도메인 모델 — #257 이 메서드 뒤에도 불변식이 참인가(Q4) · #259 이것이 값인가 엔티티인가(Q4) · #268 닫힌 표준 Enum/StrEnum/IntEnum은 생성 검증 후보에서 제외하고, custom/open Enum은 raise 유무와 별개로 타입 조합만으로 잘못된 값이 «불가능»한지 묻는다(Q2) · #301 이 규칙이 «없을 때»를 판정하나(루트 메서드로 표현될 수 있나) · #311 이 이름이 규칙 «행위»를 말하나 · #546 해소된 동일 트랜잭션 영역의 서로 다른 repository/aggregate 타입 쓰기는 확정이고, 영역·출처 미해소는 후보로 같은 트랜잭션인지 확인한다(순차 독립 UoW는 합치지 않으며 nested/외부 atomic은 결합한다) · #547 이 둘이 «동시에» 일어나면 업무가 정말 막아야 하나 / 서로 다른 일을 하는 두 사용자가 이 경계로 충돌하나(Q4) · #565 단계 이름(위 표).
   - 사실(이벤트) — #271 이 이름이 «이미 일어난 사실»을 말하나 · #564 이 칸이 «패턴»이 아니라 «진행표»인가(단계 물음).
   - 트랜잭션·리포지토리 — #285 이 수가 «애그리거트 컬렉션»을 세거나 합친 것인가 · #355 주어(위 표).
   - 브로커 — #520 이 사실이 안 나가면 내가 할 일이 있나 · #529 듣는 쪽이 따로 배포되나 · #532 받는 쪽이 「안 왔을 때」와 「두 번 왔을 때」를 메우고 있나(#181).
   - 놓칠 수 있는 입구 — #181 멱등(위 표) · #451 이 창구가 «혼자서» 답을 만들 수 있나 · #512 보내는 쪽 문서가 자기를 이 이름으로 부르나 · #629 이 입구가 «안 와도» 업무가 돌아가나.
   - admin·표현 — #343 이 문장이 운영 «기능»인가 장고 «배선»인가 · #589 이 조건이 업무 판정인가(Q2) · #590 문구(위 표) · #347(위 격리 줄).
-  - 포트·어댑터 — #227 이 자료를 원시값 인자로 «펴서» 넘길 수 있나 · #233 무엇을 알고 싶은가가 이름에 있나(Q1) · #368 이게 «기계»인가 «값»인가 · #475 이 판정이 업무 규칙인가(Q2) · #485 이 이름이 무엇을 시키는지 말하나 · #553 Q2(위 표) · #594·#595 이름 안정(위 표).
+
+  **admin context 판정**: #493 주석 존재 유지 · #645 framework 소유 슬롯 Any 제한 허용 · #646 제네릭 런타임 안전 유지 · #647 열린 UI context 조립/병합/전달 허용 · #650 실제 JSON 소비 검증 유지다. 출처가 확인된 Django admin 및 Parler admin 계열의 고정 framework 슬롯에만 적용한다. `extra_context`/`context`의 받기·each_context·UI dict·copy/update·고정 UI 키 쓰기·framework render 전달과 연결된 private 전달 helper의 매개변수·반환·지역 context 주석을 허용한다. form/inline/media의 별도 조립은 context의 허용을 취소하지 않는다. 컨테이너 부재 처리와 request UI metadata의 담기·전달도 허용한다. 업무 읽기·비교·계산·상태 변경 또는 ORM/use case/업무 함수로의 값 전달은 실제 소비이므로 그 자리부터 기존 규칙을 적용한다. 출처나 소비가 미해소 또는 동적/재귀 호출로 escape한 연결 context는 후보로 남겨 확인한다. 이름만 context인 값·같은 함수의 별도 업무 dict·framework 고정 kwargs 밖 bare Any·admin 클래스/경로 전체는 면제하지 않는다. 생성 private helper는 본문이 없으므로 정확히 결합된 열린 dict 슬롯의 #645/#647만 S1 미검증으로 보고하고 G2에서 실제 소비 흐름으로 다시 판단한다.
+  - 포트·어댑터 — #227 이 자료를 원시값 인자로 «펴서» 넘길 수 있나 · #233 무엇을 알고 싶은가가 이름에 있나(Q1) · #368 이게 «기계»인가 «값»인가 · #475 이 판정이 업무 규칙인가(Q2) · #485 이 이름이 무엇을 시키는지 말하나 · #553 Q2(위 표) · #594·#595 이름 안정(위 표). · #557 비교하는 code/errno/status_code 수신자의 출처가 확인된 vendor이면 확정, 확인된 우리 계약이면 허용, 미해소/혼합이면 후보로 그 코드의 주인을 묻는다.
   - framework·어휘 — #425 이 재료의 뜻을 밖(HTTP·pytest·시간)이 정하나 · #448 이 낱말의 뜻을 저장소 밖이 정하나 · #607 이 조건이 업무 규칙인가(Q2) · #618 문구(#590) · #619 이것이 원시값 하나로 되나 · #584 이름 안정(#595).
   - 정본 문서(주어가 코드가 아니다) — #492 이 행이 «있어야 하나»를 말하나 «어떻게 쓰나»를 말하나.
 - **human 판정 둘 — 검사기가 아예 없다(전적으로 네 몫)**: ① **#254** 애그리거트 폴더는 «항상 함께 옳아야 하는 것» 한 묶음이다 — 기계(#546·#547)는 «너무 갈린 쪽»만 본다. «너무 묶인 쪽»은 네가 묻는다: 「서로 다른 일을 하는 두 사용자가 이 경계로 충돌하나」 — 충돌하면 가짜 불변식이라 경계를 쪼개는 방향으로 발견을 올린다(설계 반송). ② **#316** 재료를 한 번에 못 모으는 경우(판정 결과에 따라 다음 조회가 달라질 때)에도 규칙을 풀지 않는다 — 판정이 「도메인 판정 → 응용 조회 → 도메인 판정」 두 조각으로 쪼개졌는지 본다(전건이 코드에 흔적을 안 남기니 유스케이스 흐름을 직접 읽는다 — Q2).
 - **면제 조문 — 새 의무 금지**: #15 #16 #23 #24 #25 #26 #27 #56 #100 #127 #137 #145 #248 #346 #522 #625 는 «면제»를 선언하는 조문이다(문면은 정본 명세 소유). 이 번호들로 새 검사·새 의무를 만들지 않으며, 후보·발견이 이 조문의 면제에 정확히 들면 그 번호를 인용해 기각한다.
 
 로드한 dddjango-discipline-cleancode·discipline-tdd·dddjango-implementation-test·dddjango-discipline-houserules 스킬의 절을 근거로 인용한다.
 
 ## 경계
 
 - 코드·테스트를 수정하지 않는다(읽기 전용). 반영은 코더가 한다.

```

## workspace/design/2026-08-08-tree-revision-spec.md

Before SHA256: bdb75a96497e134f2d8d421c71894bc43333a36a6195ddc3a9e16b07fa4aebfc
After SHA256: a8ae660448410f884023a7c2049b2f9985a1cbf69f2126baea902704e9a1fe67

```diff
--- before/workspace/design/2026-08-08-tree-revision-spec.md
+++ after/workspace/design/2026-08-08-tree-revision-spec.md
@@ -208,22 +208,22 @@
 | **532** | 「반드시 도달을 **전제**한다」 → 「**요구**로 적되 보장은 설정에 산다」 |
 | **629** | **신설** — 「놓칠 수 있는 입구」 |
 
 ## 판정 — 네 값
 
 **이 컬럼은 「이 규칙을 검사하는 데 필요한 «최소 수단»」이다.** 「사람이 봐야 하나」가 아니다 — C5 초반에 그 뜻을 「판정 재료가 어디 있나」로 바꿔 읽는 바람에 재분류가 계속 어긋났고, ㉰ 에서 원뜻으로 되돌리면서 **`ast+` 를 신설했다.**
 
 | 값 | 뜻 | 개수 |
 |---|---|---|
 | **`path`** | 경로·파일명만으로 판정된다. 파일을 안 열어도 된다 | **172** |
-| **`ast`** | 파일 내용을 파싱하면 판정된다. **사람 판단 0** | **293** |
-| **`ast+`** | **기계가 «후보»를 좁히고 사람이 «마무리»한다** — 검사기가 경고를 내고 리뷰어가 판단하는 자리 | **60** |
+| **`ast`** | 파일 내용을 파싱하면 판정된다. **사람 판단 0** | **290** |
+| **`ast+`** | **기계가 «후보»를 좁히고 사람이 «마무리»한다** — 검사기가 경고를 내고 리뷰어가 판단하는 자리 | **63** |
 | **`human`** | 기계 술어가 아예 없다. 사람에게 «묻는» 수밖에 없다 | **27** |
 
 ### ★ `ast+` 가 왜 필요했나 — D45 를 값 하나로는 못 적는다
 
 D45 축자가 *「기계가 후보를 좁히고 사람이 마무리한다」* 인데, 값이 셋뿐이라 그 모양이 전부 `human` 으로 눌려 **«전부 사람 몫»으로 읽혔다.**
 
 ```
 #547  애그리거트 경계
       기계 — #546(서로 다른 리포지토리에 쓰기 둘)이 후보 목록을 낸다
       사람 — 「이 둘이 «항상 함께 옳아야» 하나?」 한 물음만
@@ -256,43 +256,43 @@
 1. **한 술어를 두 행이 나눠 갖고 한쪽만 `human` 이던 자리가 여럿이었다** — #179↔#509 · #207↔#202 · #269↔#270 · #259↔#260 · #213↔#229 · #389↔#387 · #617↔#518·#587. ㉯ 가 걷은 «중복»의 잔여다.
 2. **`#628` 을 «쓰면 안 되는» 자리가 있다** — #228(포트 자료)의 금지선은 «어휘»가 아니라 **«정의 위치»**다. 토큰 검사를 걸면 「펴서 싣는」 `child_id` 가 전부 오탐이 된다. #518·#587(framework)은 업무 어휘가 0이어야 해서 토큰 검사가 서지만 포트 `<data>_*` 는 아니다.
 3. **`#607` 도 잴 수 있다** — 규칙 자신이 「중립 이름으로 갈아입어도 어휘 집합이 못 잡는다」고 적지만, **`viewer_id` 로 갈아입어도 `if amount > 100_000` 의 «리터럴»은 못 갈아입는다.** 반환형 `bool`(#606 이 이미 가짐) + 조건식의 정책 리터럴 + 갈래마다 다른 반환값이 후보 술어다.
 
 ## 어겼을 때 — 네 값
 
 **★ 이 트리에는 «어겨도 되는 규칙»이 없다.** `warning` 층을 만들려고 문면을 훑었지만, 완화 표현이 붙은 것은 **전부 「여기는 규정하지 않는다」**(관할 밖)였지 「어겨도 된다」가 아니었다. D10 이 그렇게 정해 놨다 — **트리는 «검사할 수 있는 데까지만» 규정하고, 규정한 것은 절대다.** 그래서 값이 이렇게 갈린다.
 
 | 값 | 테스트 | 개수 |
 |---|---|---|
-| **`blocker`** | 어긴 것을 **파일 하나로 지목**할 수 있고, 어긴 채 두면 다른 규칙이 성립하지 않는다 | **479** |
+| **`blocker`** | 어긴 것을 **파일 하나로 지목**할 수 있고, 어긴 채 두면 다른 규칙이 성립하지 않는다 | **500** |
 | **`면제`** | 규칙 자체가 「여기는 규정하지 않는다」거나 «허가문»이라 위반 주체가 없다 | **22** |
 | **`검사기`** | 어길 수 있는 것이 **코드가 아니라 검사기**다(검사 범위·채택 신호·fail-open·라우팅) | **20** |
 | **`이행`** | 이관 절차 규칙 — 한 시점의 코드로는 참·거짓이 안 갈린다 | **10** |
 
 **`판정` × `어겼을 때` — 5번이 쓸 표** *(C8 + Q0 이동 후 파일에서 재실측 — 2026-08-11)*
 
 | 판정 | blocker | 검사기 | 이행 | 면제 | 계 |
 |---|---|---|---|---|---|
 | `path` | 154 | 9 | 4 | 5 | **172** |
-| `ast` | 281 | 7 | 4 | 1 | **293** |
-| `ast+` | 60 | 1 | 0 | 0 | **61** |
+| `ast` | 278 | 7 | 4 | 1 | **290** |
+| `ast+` | 62 | 1 | 0 | 0 | **63** |
 | `human` | 6 | 3 | 2 | 16 | **27** |
-| **계** | **501** | **20** | **10** | **22** | **553** |
+| **계** | **500** | **20** | **10** | **22** | **552** |
 
 <span>*(3단계에서 24건이 들어와 447 → 471, 3차 리뷰 반영으로 10건이 들어와 481, T26·T27(D39) 반영으로 4건이 들어와 **485**, 그리고 **D40~D59 회수로 110건이 들어와 595** 가 됐다. 3차에서 허가문 9건이 blocker → `면제`, 검사 범위 6건이 → `검사기` 로 바로잡혔고, «파일 내용을 세는» path 9건이 `ast` 로, 크로스-BC·어휘 판정 4건이 `human` 으로, «두 번째 BC» 3건이 `human` → `ast` 로 옮겨갔다. 복합 제안(ast+human)은 상위 수단 하나로 적는다 — 판정 컬럼은 «충분한 최소 수단»이다. **회수분 110건의 갈림은 `ast` 57 · `human` 30 · `path` 23** 이다 — 신설 칸이 대부분 «파일 안의 모양»을 규정해서다.)*</span>
 
 **읽는 법 — 6번이 만들 것이 세 덩어리다.**
 
 | | 몇 | 무엇 |
 |---|---|---|
-| `path`+`ast` 의 blocker | **435** | **결정적 백스톱** — 기계가 혼자 판정하고 반송한다 |
-| `ast+` 의 blocker | **60** | **후보를 좁히는 검사** — 경고를 내고 리뷰어가 마무리한다. 술어 셋(확정·후보·물음)이 `2026-08-11-predicates.md` 에 있다 |
+| `path`+`ast` 의 blocker | **432** | **결정적 백스톱** — 기계가 혼자 판정하고 반송한다 |
+| `ast+` 의 blocker | **62** | **후보를 좁히는 검사** — 경고를 내고 리뷰어가 마무리한다. 술어 셋(확정·후보·물음)이 `2026-08-11-predicates.md` 에 있다 |
 | `human` 의 blocker | **6** | 기계 술어가 아예 없다 — `#254`·`#316`·`#526`·`#530`·`#563`·`#626` |
 
 <span>08-11 · C5 ㉰ — **옛 문면의 「`human` blocker 148」은 «소거법»으로 매겨진 수였다.** 「기계가 못 하면 human」이라 성질이 다른 것이 한 칸에 뭉쳐 있었고, 전수 재분류로 **131건이 `human` 을 벗고 `ast+` 가 신설됐다**. 남은 실질 `human` 은 **11건**이고 그중 blocker 는 **6건**이다.</span>
 **★ 그중 `#486~#492`(제1원칙)는 «다른 모든 검사보다 먼저» 도는 자리라 6번에서 별도 게이트로 뽑는다** — 골격이 어긋나면 나머지 **525개**를 돌릴 이유가 없다.
 
 ## 3단계 — 회수한 24건
 
 목록은 **결정 카드가 32장일 때** 뽑혔다. 그 뒤에 선 넷(**D35 · D36 · D37 · D38**)의 규칙이 **하나도 없었다.** 카드를 다시 읽어 24건을 뽑아 넣었다(번호 **448~471**).
 
 | 카드 | 뽑은 것 | 몇 |
@@ -511,29 +511,29 @@
 |---|---|---|---|---|---|---|
 | 182 | `application_layer/` 의 직속 자식 폴더는 `<area>/` · `port/` **둘뿐**이다 — `domain_bypass_query/` 와 `unit_of_work/` 는 `port/` 안으로 들어갔다. | 트리 38행+D30+D14+D37 | `path` | both | `measured_ok` | **blocker** |
 | 183 | `application_layer/` 아래에 `validation/` 폴더나 `*_validation.py` 파일을 두지 않는다. | 트리 38행+D30 | `path` | both | `measured_ok` | **blocker** |
 | 185 | `application_layer` 는 `driven_layer` 와 `driving_layer` 를 import 하지 않는다. | D14 결정③ | `ast` | principle |  | **blocker** |
 | 186 | `application_layer` 는 타 BC 를 직접 부르지 않고 자기 `port/` 를 거친다. | D14 결정③ | `ast` | principle |  | **blocker** |
 | 187 | 포트 선언에 BC 최상위 칸을 만들지 않는다 — 애그리거트에 안 붙는 포트는 `application_layer/port/` 에만 산다. | D2 | `path` | principle |  | **blocker** |
 | 188 | `application_layer/<area>/` 는 `driving_layer/api/<area>/` 와 같은 이름으로 1:1 대응한다. | 트리 39행+D14 | `path` | principle |  | **blocker** |
 | 189 | `<use_case>/` 폴더 안 모듈은 그 유스케이스 소유다 — 다른 유스케이스가 그 안을 import 하면 위반이다. 함께 쓸 것이 생기면 «올리는» 것이 아니라 제자리로 보낸다: 업무 판정이면 `domain_layer/`(#194), 바깥 능력이면 `port/`, 기술이면 `framework/`, 어디도 아니면 각 유스케이스의 진입점 안에 중복해 둔다(성급한 공통화 금지). <span>08-11 · T61 ⓑ — 옛 처방부(«`<area>/` 바로 아래로 올린다»)는 트리 39행에 파일 칸이 없어 #490 과 모순인 죽은 처방이었고, 원전 조사(CA ch.16 우발적 중복 경고·Entities 정의·VSA «push into the domain» — 2026-08-11-cross-usecase-sharing-research.md)가 «공유는 옆이 아니라 아래로»를 확인해 개정.</span> <span>2026-09-01 · **동명 폴더 승격 부칙** — 배차표에 «역할 밖 응집 단위 + 하한 충족 → 동명 폴더 승격» 가지가 추가된다 — 「진입점 안에 중복」의 진입점은 승격 시 그 폴더다(부품도 유스케이스 간 돌려쓰기 금지의 주어).</span> | 트리 39·40행+D28 | `ast` | measured | `measured_ok` | **blocker** |
 | 190 | 유스케이스 하나 = 폴더 하나 = 진입점 하나다. | 트리 40행+D14 | `path` | principle |  | **blocker** |
 | 191 | `<use_case>/` 폴더 이름은 동사로 짓는다(`start_turn/` · `evict_child/`). | 트리 40행+D14 | `ast+` | principle |  | **blocker** |
-| 192 | 절차가 길어도 `<use_case>/` 에 파일을 늘리지 않는다 — 조각은 `<use_case>_use_case.py` 안 `_` 사설 함수로 두고, `service/` 같은 종류 폴더도 만들지 않는다. 사설 조각이 자라면 도메인으로 내릴 판정이 남았다는 신호다(#194). <span>08-11 · T61 ⓑ 부속 — 옛 문면(«쪼갠 모듈도 폴더 안에»)은 트리 40행이 파일 넷으로 닫혀 있어 #490 과 모순(죽은 처방)이라 트리 정합으로 개정. #189 의 «중복해 둔다»가 설 자리도 이 문면이 정한다(진입점 안 사설).</span> <span>2026-09-01 · **동명 폴더 승격 부칙** — 「파일을 늘리지 않는다」는 캐스케이드 ③(역할 내)의 형태다 — ②(역할 밖 응집·50행 하한) 성립 시 동명 폴더 승격이 예외이고, 승격 폴더 내부 부품 각각에 이 규칙이 그대로 적용된다.</span> | 트리 40행+D28 | `path` | measured | `measured_ok` | **blocker** |
+| 192 | 절차가 길어도 `<use_case>/` 에 파일을 늘리지 않는다 — 조각은 `<use_case>_use_case.py` 안 `_` 사설 함수로 두고, `service/` 같은 종류 폴더도 만들지 않는다. 사설 조각이 자라면 도메인으로 내릴 판정이 남았다는 신호다(#194). <span>08-11 · T61 ⓑ 부속 — 옛 문면(«쪼갠 모듈도 폴더 안에»)은 트리 40행이 파일 넷으로 닫혀 있어 #490 과 모순(죽은 처방)이라 트리 정합으로 개정. #189 의 «중복해 둔다»가 설 자리도 이 문면이 정한다(진입점 안 사설).</span> <span>2026-09-01 · **동명 폴더 승격 부칙** — 「파일을 늘리지 않는다」는 캐스케이드 ③(역할 내)의 형태다 — ②(역할 밖 응집) 성립 시 동명 폴더 승격이 예외이고, 승격 폴더 내부 부품 각각에 이 규칙이 그대로 적용된다.</span> | 트리 40행+D28 | `path` | measured | `measured_ok` | **blocker** |
 | 193 | 유스케이스의 진입점 파일 이름은 `<use_case>_use_case.py` 다. | 트리 41행+D14+D28 | `path` | principle |  | **blocker** |
 | 194 | 유스케이스는 업무 규칙을 갖지 않는다 — 조건문이 «무엇이 옳은가»를 가르기 시작하면 그 조건은 도메인으로 내려간다. | 트리 41행+파트 [application] 목표 | `ast+` | principle |  | **blocker** |
 | 195 | 상태를 바꾸는 유스케이스는 애그리거트를 건너뛰지 않는다 — 건너뛸 수 있는 것은 조회 전용·순수 위임·외부 조회뿐이다. | D14 | `ast` | principle |  | **blocker** |
 | 196 | Input Boundary · Output Boundary · Presenter 는 `application_layer` 에 넣지 않는다. | D14 결정① | `ast` | principle |  | **blocker** |
-| 197 | 읽기 전용 유스케이스는 UnitOfWork 를 받지 않는다. <span>2026-08-25 · **문면 확인** — 검사기 측정 정밀화(factory 호출형 `with` 인식·도달 범위의 쓰기/repository 전달 인정)는 이 문면의 집행 정밀화이지 개정이 아니다. «with uow» 진입 자체는 쓰기 사용이 아니다 — 읽기 전용+UoW 는 문면 그대로 위반이다(kkebi reconcile 실증).</span> | D14 | `ast` | principle |  | **blocker** |
+| 197 | 읽기 전용 유스케이스는 UnitOfWork 를 받지 않는다. <span>2026-08-25 · **문면 확인** — 검사기 측정 정밀화(factory 호출형 `with` 인식·도달 범위의 쓰기/repository 전달 인정)는 이 문면의 집행 정밀화이지 개정이 아니다. «with uow» 진입 자체는 쓰기 사용이 아니다 — 읽기 전용+UoW 는 문면 그대로 위반이다(kkebi reconcile 실증).</span> 설계 pre-gate는 명시 read-only/UoW 모순과 출처가 확인된 UoW 주입을 선언 확정, 미해소 출처를 선언 후보로 분리한다. 선언 처분은 architect·해당 설계 리뷰/감수자 소유이며 기존 실코드 검사 범위와 다르다. 효과 무기재는 미검증이다. | D14 | `ast` | principle |  | **blocker** |
 | 200 | 커밋 뒤 부작용은 `unit_of_work.after_commit(...)` 에 맡긴다 — 응용이 `transaction.on_commit` 이나 `connection.in_atomic_block` 을 직접 부르지 않는다. | D31 | `ast` | both | `measured_ok` | **blocker** |
 | 201 | 유스케이스가 주고받는 자료는 그 `<use_case>/` 바로 아래 세 파일(`<use_case>_command.py` · `<use_case>_query.py` · `<use_case>_result.py`)로 둔다 — `dto/` 겹을 만들지 않는다(파일 «이름»에서 `dto` 를 뗀 근거는 D55 이고, 산문에서 이 자료를 「응용 DTO」라 부르는 것은 그대로다). | 트리 40·42·43·44행+D14+D28+D55 | `path` | principle |  | **blocker** |
-| 202 | DTO 에는 애그리거트도 엔티티도 ORM 행도 담기지 않는다. | 트리 42·44행+D14 | `ast` | principle |  | **blocker** |
+| 202 | DTO 에는 애그리거트도 엔티티도 ORM 행도 담기지 않는다. 설계 pre-gate는 add/update 공개 Result/Out/Response에서 명시 import·별칭·중첩/사설 DTO·표준 컨테이너로 출처가 결합된 aggregate/entity 누수를 선언 확정으로, 미해소 출처를 후보로 보고한다. VO/shared VO는 허용하고 이름만으로 확정하거나 OHS import를 합성하지 않는다. 선언 처분은 architect·해당 설계 리뷰/감수자 소유이며 실코드 검사를 대체하지 않는다. | 트리 42·44행+D14 | `ast` | principle |  | **blocker** |
 | 204 | 응용 DTO 백스톱의 검사 대상은 `application_layer/**/<use_case>_{command,query,result}.py` 전부다 — 코드 쪽 규칙(#67 «raise 하지 않는다»)과 겹치던 중복 문면을 검사 범위 규칙으로 갈랐다(3차 T9). | 트리 42·43·44행+D30 | `path` | both | `measured_ok` | **검사기** |
 | 205 | DTO 는 자기 유스케이스 폴더 안에서만 쓰인다 — 유스케이스끼리 DTO 를 돌려쓰지 않는다. | D14 | `ast` | principle |  | **blocker** |
 | 206 | 유스케이스가 받는 값의 파일 이름은 `<use_case>_command.py` 다. | 트리 42·43행+D8+D14 | `path` | principle |  | **blocker** |
 | 207 | `<use_case>_command` 의 기본형은 id 와 원시값이고 도메인 값 객체는 그대로 온다 — 못 담는 것은 둘뿐이다: 애그리거트·ORM 로우, 그리고 «안쪽이 바깥을 알게 만드는» 타입(`UploadedFile` 처럼 장고·닌자가 자기에게 편한 모양으로 빚은 것). 뒤엣것은 이 칸이 아니라 전역 제약 ②가 막는다. | 트리 42행+D14 | `ast` | principle |  | **blocker** |
 | 208 | `<use_case>_command` 은 바깥 `schema_in.py` 와 짝이지만 같은 타입을 쓰지 않는다. | 트리 42행+D8 | `ast` | principle |  | **blocker** |
 | 209 | 유스케이스가 내보내는 자료의 파일 이름은 `<use_case>_result.py` 다. | 트리 44행+D8+D14 | `path` | principle |  | **blocker** |
 | 210 | 컨트롤러가 `<use_case>_result` 만 보고 응답을 만들 수 있어야 한다 — 값이 빠져 컨트롤러가 도메인을 들여다보게 되면 위반이다. | 트리 44행 | `ast` | principle |  | **blocker** |
 | 211 | 흐름을 내보내는 유스케이스는 `Iterator[<use_case>Out]` 로 돌려주고 흐르는 알맹이가 `<use_case>_result` 이어야 한다 — `<use_case>_result` 은 개수를 규정하지 않는다. | 트리 44행+D14 | `ast` | principle |  | **blocker** |
 | 212 | `port/` 에는 선언만 온다 — 구현은 한 줄도 없다. | 트리 45행+파트 [application] | `ast` | principle |  | **blocker** |
 | 213 | DB 조회 계약도 `port/` 아래에 둔다 — 포트의 판정은 «바깥에 행위자가 있나»가 아니라 **«이 층 밖인가»**이고, 우리 DB 도 이 층 밖이다. | 트리 45행+트리 51행+D2+D29+D37 | `path` | principle |  | **blocker** |
@@ -806,21 +806,21 @@
 **목록은 결정 카드가 39장일 때 뽑혔다.** 그 뒤에 선 스무 장(**D40~D59**)의 규칙이 **하나도 없었고**, 트리가 107행에서 138행으로 늘며 생긴 칸 **22개**가 규칙 0건이었다. 카드와 신설 칸을 다시 읽어 아래를 넣는다.
 
 **맨 앞의 일곱(486~492)이 D54 = 제1원칙이다** — 이 검사가 «다른 모든 검사보다 먼저» 돌고, 걸리면 나머지를 돌리지 않고 반환한다.
 
 | # | 규칙 | 자리 | 판정 | 근거 | 3차 | 어겼을 때 |
 |---|---|---|---|---|---|---|
 | 486 | 어느 BC 를 열어도 이 트리의 골격이 «그대로» 있다 — 내용이 있든 없든 상관없다. 파일트리를 지키지 않는 구현·설계는 «반환»이다. | 트리 1행+D54 | `path` | principle |  | **blocker** |
 | 487 | 이 검사는 다른 모든 검사보다 «먼저» 돈다 — 걸리면 나머지 검사를 돌리지 않고 반환한다. | 트리 1행+D54 | `path` | principle |  | **검사기** |
 | 488 | 고정 이름의 칸은 «부모가 있으면» 반드시 있다 — 폴더는 비어도 `__init__.py` 로, 파일도 비면 «빈 파일»로 만든다. <span>2026-09-01 · **동명 폴더 승격 부칙** — 칸의 승격 실현(#490 교체형)이 이미 있으면 그 실현이 이 충족이다 — 동명 빈 파일을 병설하지 않는다.</span> 세 어댑터 패키지도 `adapter/`·`command/`·`constant/`·`contract/`·`schema/` 를 내용 없이 모두 만들고, 바깥 패키지와 각 역할 폴더의 `__init__.py` 를 둔다. | 트리 1행+D54 | `path` | principle |  | **blocker** |
 | 489 | `<…>` 가 붙은 자리표시자 칸만 그 개념이 실제로 생길 때 생긴다 — 그 외에 「이 BC 엔 없으니 뺀다」는 축소가 아니라 위반이다. | 트리 1행+D54 | `path` | principle |  | **blocker** |
-| 490 | `application/<bounded_context>/**` 안에 트리에 없는 경로가 하나라도 있으면 위반이다(`utils/`·`common/`·`helpers/`). 폐쇄는 **칸**(폴더 + 트리가 이름을 준 파일)에만 걸리고, 트리가 리프로 닫은 폴더 «안»의 추가 모듈은 #15 의 재량이다. `framework/`·`<project>/` 는 이 원칙의 주어가 아니다(D54 축자: 「이 원칙의 주어는 «BC»다」). <span>2026-09-01 · **동명 폴더 승격 부칙** — §1 트리의 승격 허용 표기가 붙은 파일 칸은 두 실현(`<이름>.py` ⇄ 동명 폴더)을 갖고, 유효한 승격 폴더는 «트리에 없는 경로»가 아니다(형태 요건 #638~#643).</span> 세 어댑터 칸은 고정 패키지이므로 단일 파일·바깥 본체 파일·역할 아래 추가 폴더로 실현할 수 없다. | 트리 1행+D54 | `path` | principle |  | **blocker** |
+| 490 | `application/<bounded_context>/**` 안에 트리에 없는 경로가 하나라도 있으면 위반이다(`utils/`·`common/`·`helpers/`). 폐쇄는 **칸**(폴더 + 트리가 이름을 준 파일)에만 걸리고, 트리가 리프로 닫은 폴더 «안»의 추가 모듈은 #15 의 재량이다. `framework/`·`<project>/` 는 이 원칙의 주어가 아니다(D54 축자: 「이 원칙의 주어는 «BC»다」). <span>2026-09-01 · **동명 폴더 승격 부칙** — §1 트리의 승격 허용 표기가 붙은 파일 칸은 두 실현(`<이름>.py` ⇄ 동명 폴더)을 갖고, 유효한 승격 폴더는 «트리에 없는 경로»가 아니다(형태 요건 #638~#641·#643).</span> 세 어댑터 칸은 고정 패키지이므로 단일 파일·바깥 본체 파일·역할 아래 추가 폴더로 실현할 수 없다. | 트리 1행+D54 | `path` | principle |  | **blocker** |
 | 491 | 칸의 유형은 셋뿐이고 «조건부»는 없다 — ① 고정 이름 ② `<>` 첫 등장 ③ `<>` 재등장(조상이 이미 연 낱말이라 값이 이미 채워져 있어 ①과 같다). 「있을 수도 없을 수도」라고 적힌 칸은 셋 중 하나로 다시 분류한다. <span>2026-09-01 · **동명 폴더 승격 부칙** — «조건부 없음»의 주어는 칸의 존재다 — 승격 허용 표기는 실현 형태(#490)의 값이다.</span> | 트리 1행+D54(T52) | `path` | principle |  | **blocker** |
 | 492 | 「그 파일이 있어야 하나」는 트리가 정하고 「그것을 어떻게 쓰나」는 스킬이 정한다 — 트리에 조건을 적어 두 채널로 만들지 않는다. | D54+D10+D30 | `ast+` | principle |  | **blocker** |
 | 493 | 모든 이름은 «첫 대입»에 타입을 적는다 — 시그니처·속성·지역 변수에 예외가 없다. 빠지는 것은 **문법이 없는 여덟 자리뿐**이다: `for x in xs:` · `with … as f:` · `except … as e:` · `a, b = pair` · `a = b = 0` · `x += 1` · walrus · 컴프리헨션. 그리고 **재대입**(첫 바인딩이 아니다)과 **선언적 클래스 본문**(ORM 모델 필드·ninja Schema 필드)은 면제다. | D58+§4 | `ast` | principle |  | **blocker** |
 | 494 | 「자명하니까 면제」를 두지 않는다 — 조건을 하나라도 열면 「어디까지가 자명한가」가 되돌아와 규칙이 무너진다. **[Q0]** <span>08-11 — 「어겼을 때」를 `blocker` → `검사기` 로 옮겼다. **이 행의 주어는 «코드»가 아니라 «판정하는 사람»이라 반송할 파일을 지목할 수 없다**(Q0). 코드 쪽 귀결은 다른 행이 이미 `ast` 로 갖는다.</span> | D58 | `human` | principle |  | **검사기** |
 | 495 | mypy strict 는 「구성돼 있으면」이 아니라 «항상» 돈다 — 이 게이트가 타입 규칙의 결정적 백스톱이고, 없으면 강제가 0이다. | D58+§4 | `ast` | principle |  | **검사기** |
 | 496 | 타입 검사의 `tests.*` 면제를 두지 않는다 — `test/`·`fake/` 가 면제되면 페이크의 리스코프 위반이 그대로 통과한다. | D58+D56 | `ast` | principle |  | **검사기** |
 | 497 | `composition_root/` 는 파일이 아니라 폴더이고 «결선 하나 = 파일 하나»다 — 지금은 `dependency_wiring.py` 와 `event_wiring.py` 둘이다. | 트리 2·3·4행+D40+D6 | `path` | principle |  | **blocker** |
 | 498 | `event_wiring.py` 는 `event_router` 를 브로커에 «꽂는» 것만 한다 — 표를 여기서 만들지 않는다. | 트리 4행+D40 | `ast` | principle |  | **blocker** |
 | 500 | 구독으로 넘기는 것은 «모듈 최상단에 정의된 이름 있는 함수»뿐이다 — 람다·`functools.partial`·지역 정의 함수를 넘기면 매번 «다른 객체»라 멱등이 성립하지 않는다. 검사는 브로커가 아니라 «넘기는 자리»에 선다. | 트리 4행+D59 | `ast` | principle |  | **blocker** |
 | 501 | `event_wiring.py` 에서 DB 를 만지면 위반이다 — 모든 관리 명령에서 도는 자리다. | 트리 4행+D59 | `ast` | principle |  | **blocker** |
@@ -858,32 +858,32 @@
 | 535 | `apps.py` 의 `ready()` 본문은 «한 줄»이다 — 자기 BC 의 `composition_root/event_wiring.py` 를 부른다. | 트리 77행+D59+D15 | `ast` | principle |  | **blocker** |
 | 536 | 그 import 가 `ready()` «밖»에 있으면 위반이다 — 부팅 1단계에서는 모델을 못 읽는다. | 트리 77행+D59 | `ast` | principle |  | **blocker** |
 | 537 | `ready()` 에서 DB 를 만지면 위반이다 — 원전 축자: *“`manage.py test` would still execute some queries against your **production** database”*. | 트리 77행+D59 | `ast` | principle |  | **blocker** |
 | 538 | `apps.py` 의 모듈 최상단 import 는 django 것뿐이다 — 리스너를 여기서 «정의»하면 위반이고, 이 한 줄이 부모의 리프 규칙(django 말고 import 0)의 «유일한» 면제다. | 트리 77행+D59 | `ast` | principle |  | **blocker** |
 | 539 | 사실 발행은 «세 걸음»이고 «순서»가 규칙이다 — ① **유스케이스가** 애그리거트에서 `pull_events()` 를 부른다 ② 저장 ③ 옮겨 담아 `uow.after_commit(…)` 으로 브로커에. **리포지토리 구현이 `pull_events()` 를 부르면 위반**이다(그것이 D59 가 근거 셋으로 기각한 «저장 경계 자동 수거»다). | 트리 41·92행+D59 | `ast` | principle |  | **blocker** |
 | 540 | 도메인 사실을 «그대로» 브로커에 넘기면 위반이다 — 타입이 다르고 1:1 도 아니다. 옮겨 담는 일은 유스케이스가 한다. | 트리 41행+D59+D40 | `ast` | principle |  | **blocker** |
 | 541 | 커밋 «전»에 발행하면 위반이다 — 그 부작용이 같은 트랜잭션에 들어간다는 뜻이라 「한 트랜잭션 = 애그리거트 하나」(D43)와 정면으로 부딪힌다. | 트리 41행+D59+D43 | `ast` | principle |  | **blocker** |
 | 542 | 사실은 «애그리거트»가 만든다 — 상태를 바꾼 그 메서드 안에서 기록한다. 유스케이스가 지어내면 「불변식에 걸려 안 바뀌었는데 사실은 나가는」 경우가 생기고, 같은 메서드를 부르는 유스케이스가 둘이 되면 한쪽이 빠뜨려도 아무도 모른다. | 트리 61행+D59+D12 | `ast` | principle |  | **blocker** |
 | 543 | 꺼내는 창구는 `pull_events()` 하나이고 «꺼내면 비운다» — `events` 프로퍼티처럼 «안 비우고 읽는» 길을 함께 두면 위반이다. <span>2026-08-25 · **저널 애그리거트 인정 형태** — 이벤트가 곧 도메인 실체인 저널 애그리거트(실체 저장소와 발행 대기 큐가 «서로 다른 두 필드»로 분리된 이중 구조)는 pending 조회 property(같은 저장소의 tuple 사본) + 실소거 창구(같은 저장소를 실제로 비우는 메서드 — no-op 은 불인정)를 «꺼내는 창구»의 인정 형태로 둔다. 실체 저장소의 공개 표면은 불변이어야 한다(관찰 조항 — 집행은 후속·repo save 의 pending 가드 조인은 #545 소관). **저널이 아닌 애그리거트의 이 관용구 채택은 위반이다(관찰)**. `_pending_events` 명명 단독 채택이 검사 창(`_events`/`events`) 밖인 것은 기존 사각이며 이 부칙의 인정이 아니다(kkebi billing_event_stream 실증).</span> | 트리 61행+D59 | `ast` | principle |  | **blocker** |
 | 545 | 리포지토리 구현 `save()` 는 애그리거트에 «안 꺼낸 사실»이 남아 있으면 **예외를 던진다** — 검사는 「그 가드가 구현 안에 있나」다. <span>08-15 · 인정 형태 명문화 — 그 가드가 애그리거트의 `_events` 를 **비소모로 읽는**(꺼내지 않고 남았는지만 보는) 형태는 인정 형태다(검사기가 이미 수용하는 형태의 명문화 — 검사기 무변).</span> <span>2026-08-25 · **적용 술어와 가드 의미** — 적용은 이벤트 채택 애그리거트(`domain_layer/<agg>/event/` 비-`__init__` 실재, 또는 루트의 사적 pending 저장소+실소거/소모 창구)의 리포지토리에 한한다: eventless root 는 비적용이다(가드 강제는 dead seam 만 낳는다 — saju·billing 실증). event/ 만 있고 루트 pending API 가 없는 반쪽 채택은 후보 발화다. 인정 가드는 save 수신자의 pending 상태를 **비소모로** 질의해 **잔존(truthy) 시 persistence 전에** 예외에 도달하는 형태다 — 이름 토큰의 존재(죽은 분기·지역 이름·무관 수신자·빈-경우-예외·raise 삼킴·쓰기 후 가드)는 가드가 아니다.</span> | 트리 92행+D59+D50 | `ast` | principle |  | **blocker** |
-| 546 | 한 트랜잭션은 애그리거트 «하나»를 바꾼다 — 검사는 「서로 다른 **애그리거트 리포지토리**에 «쓰기»가 둘」이다. **세는 대상은 타입이 `domain_layer/<aggregate>/<aggregate>_repository.py` 에서 온 것뿐이다** — 「애그리거트 = 트랜잭션 경계」(D50)라 **애그리거트를 안 가진 것은 애초에 대상이 아니다**: `domain_bypass_query/`(#465 가 「애그리거트를 안 거치므로 리포지토리가 아니다」로 이미 뺐다) · 도메인 객체의 메서드(`order.lines.remove`) · 이름만 `save` 인 남의 포트. <span>08-11 · C7 — 옛 문면은 주어가 그냥 「리포지토리」라 **4차 리뷰가 오탐 셋으로 blocker 를 냈다**(CHK-1+2). 주어를 좁히면 셋이 한꺼번에 빠진다 — 별칭(`repo = self._order_repository`)은 **타입이 같아 «하나»로** 세어지고, 나머지 둘은 타입이 그 파일에서 안 온다. 시그니처 어노테이션(#547 전제)은 그 **타입을 «읽을 수 있게» 하는 앞 단계**이지 이 술어 자체가 아니다.</span> | 트리 60행+D43+D50 | `ast` | principle |  | **blocker** |
+| 546 | 한 트랜잭션은 애그리거트 «하나»를 바꾼다 — 검사는 「서로 다른 **애그리거트 리포지토리**에 «쓰기»가 둘」이다. **세는 대상은 타입이 `domain_layer/<aggregate>/<aggregate>_repository.py` 에서 온 것뿐이다** — 「애그리거트 = 트랜잭션 경계」(D50)라 **애그리거트를 안 가진 것은 애초에 대상이 아니다**: `domain_bypass_query/`(#465 가 「애그리거트를 안 거치므로 리포지토리가 아니다」로 이미 뺐다) · 도메인 객체의 메서드(`order.lines.remove`) · 이름만 `save` 인 남의 포트. <span>08-11 · C7 — 옛 문면은 주어가 그냥 「리포지토리」라 **4차 리뷰가 오탐 셋으로 blocker 를 냈다**(CHK-1+2). 주어를 좁히면 셋이 한꺼번에 빠진다 — 별칭(`repo = self._order_repository`)은 **타입이 같아 «하나»로** 세어지고, 나머지 둘은 타입이 그 파일에서 안 온다. 시그니처 어노테이션(#547 전제)은 그 **타입을 «읽을 수 있게» 하는 앞 단계**이지 이 술어 자체가 아니다.</span> 확정은 해소된 동일 트랜잭션 영역에서 서로 다른 repository/aggregate 타입 쓰기다. 순차 독립 UoW는 분리하고 nested UoW·외부 Django atomic은 결합한다. 영역·출처 미해소는 후보이며 같은 트랜잭션인지 감수자가 확인한다. | 트리 60행+D43+D50 | `ast+` | principle |  | **blocker** |
 | 547 | 애그리거트는 «정의상» 트랜잭션 경계다 — 서로 «다른 일»을 하는 두 사용자가 이 경계 때문에 충돌하면 그건 업무 규칙이 아니라 개발자가 만든 제약이다. 트랜잭션을 늘리지 말고 «경계를 쪼갠다». | 트리 60행+D50 | `ast+` | principle |  | **blocker** |
 | 548 | 다른 애그리거트는 «식별자 값 객체»로만 문다 — 타입 힌트에 남의 애그리거트 클래스가 나오면 위반이다. 면제는 하나, 조회가 실제로 느려 직접 참조가 필요할 때(원전 Reason Four)다. | 트리 60행+D50+D12 | `ast` | principle |  | **blocker** |
 | 549 | 수정하려고 꺼내는 조회는 캐시를 «우회한다» — 선은 애그리거트가 아니라 «트랜잭션»이고, `select_for_update` 를 캐시하면 DB 락이 무용지물이 된다. | 트리 60·92행+D50 | `ast` | principle |  | **blocker** |
 | 550 | 배치 면제는 «생성»에만 걸린다 — 이미 있는 것을 여럿 «고치는» 것은 면제가 아니다. | 트리 60행+D43 | `ast` | principle |  | **blocker** |
 | 551 | 계약은 `ABC` 를 상속하고 메서드는 전부 `@abstractmethod` 다 — 미구현은 인스턴스화에서 `TypeError` 로 잡힌다. | 트리 47·68·145·151행+D44 | `ast` | principle |  | **blocker** |
 | 552 | 구현은 그 계약을 «상속»한다 — 상속만 하면 미구현을 런타임이 잡으므로 강제할 것은 「상속했나」 하나다. | 트리 92·101·114·126·155행+D44 | `ast` | principle |  | **blocker** |
 | 553 | 어댑터가 하는 일은 «바꾸고 · 부르고 · 바꾼다» 셋뿐이다 — 도메인에 «시키면» 위반이고, 업무 판정을 여기서 하면 위반이다. | 트리 89행+D45 | `ast+` | principle |  | **blocker** |
 | 554 | 어댑터는 «계약이 선언한 실패»로 바꿔 내보낸다 — 계약이 어디 사느냐가 답을 정한다: 리포지토리(도메인)면 도메인 예외, 능력 포트면 포트 예외다. 어댑터는 결정하지 않고 «이름만» 바꾼다. | 트리 89·92행+D51 | `ast` | principle |  | **blocker** |
 | 555 | 어댑터가 벤더·django 예외를 «그대로» 위로 흘리면 위반이다 — 그러면 전역 제약 ②가 자료의 모양이 아니라 «실패의 모양»으로 깨진다. | 트리 89행+D51 | `ast` | principle |  | **blocker** |
 | 556 | 재시도의 «판정»은 driven 이 지고, «기계»만 `framework/` 가 지며, «다시 부르기»는 입구가 한다 — 셋을 한 낱말로 뭉쳐 한 칸에 두면 위반이다. | 트리 89·142행+D52 | `ast` | principle |  | **blocker** |
-| 557 | 일시 실패(transient)의 정규화는 그 인프라를 «소유한» 어댑터가 한다 — 위층이 벤더 오류 코드를 보고 판정하면 위반이다. | 트리 89행+D52+D51 | `ast` | principle |  | **blocker** |
+| 557 | 일시 실패(transient)의 정규화는 그 인프라를 «소유한» 어댑터가 한다 — 위층이 벤더 오류 코드를 보고 판정하면 위반이다. code/errno/status_code 비교의 수신자가 확인된 vendor 출처이면 확정, 확인된 domain 또는 application의 command/query/result/port 계약이면 허용한다. 미해소·혼합·재바인딩 출처는 후보로 그 코드의 주인을 감수자가 묻는다. except 구문이나 속성 이름만으로 vendor를 확정하지 않는다. | 트리 89행+D52+D51 | `ast+` | principle |  | **blocker** |
 | 558 | `framework/` 는 «링»이 아니다 — 링은 폴더가 아니라 «파일»이 진다. `framework/` 아래 파일도 각자 자기 링의 규칙을 따른다. | 트리 142행+D47 | `ast` | principle |  | **blocker** |
 | 559 | `framework/pure/` 에는 순수 계산과 그 계산이 주고받는 «순수 자료»가 온다 — 판정이 곧 이름이다: 「이 파일이 순수한가」. | 트리 158행+D47 | `ast` | principle |  | **blocker** |
 | 560 | `framework/pure/` 는 그 **밖의** 저장소 파일을 import 하지 않는다 — 같은 `pure/` 안의 순수 자료 모듈(`Page`·`SortSpec`)은 예외다. 표준 라이브러리는 #561 이 따로 건다. | 트리 158·159행+D47 | `ast` | principle |  | **blocker** |
 | 561 | `pure/` 에 부작용이 있으면 위반이다 — `datetime`·`time`·`random`·`secrets`·`uuid`·`os`·`io` 가 나오면 그건 «2차 행위자»라 `<capability>/` 다. 목록은 예시이고 **판정은 「같은 인자로 두 번 불러 같은 답이 나오나」**다(ast 근사). | 트리 158·159행+D47 | `ast` | principle |  | **blocker** |
 | 562 | `pure/` 아래에 `*_port.py`·`*_adapter.py` 가 있으면 위반이고, **업무 어휘가 한 글자라도 나오면 위반**이다 — 뒤엣것이 이 트리에서 Shared Kernel 을 막는 기계다. | 트리 158·159행+D47+D24 | `path` | principle |  | **blocker** |
 | 563 | BC 를 가로지르는 단계는 물음 «둘»로 갈린다 — ① 「실패하면 내가 할 일이 있나」(예: 지시 / 아니오: 사실) ② 「응답을 기다리게 해도 되나」(예: 요청 / 아니오: 워커). **[Q3]** | D48+D42 | `human` | principle |  | **blocker** |
 | 564 | 진행 상태를 기억하는 «진행표»를 만들지 않는다 — 순서는 유스케이스가 지고, 중재자는 «칸»이 아니라 «패턴»이다. | D48+D42 | `ast+` | principle |  | **blocker** |
 | 565 | BC 가 «단계»를 도메인에 들려면 업무가 그 단계 이름을 «입으로 부를 때»만이다 — 아니면 워크플로를 도메인 어휘로 위장한 것이라 자리는 유스케이스다. | 트리 60행+D42 | `ast+` | principle |  | **blocker** |
 | 566 | 사실 발행 콜백은 앞 콜백의 실패로 «통째로» 사라질 수 있는 자리에 두지 않는다 — 장고 `on_commit` 의 기본값이 그 모양이다. | 트리 96행+D49 | `ast` | principle |  | **blocker** |
 | 567 | `schema` 는 «기술 실물»의 이름이라 `dto` 로 부르지 않는다 — `dto` 는 Fowler 의 «프로세스 사이» 패턴 이름이고 우리 것은 같은 프로세스다. | 트리 13·42·44·49행+D55 | `ast` | principle |  | **blocker** |
@@ -921,20 +921,21 @@
 
 | 걷어낸 # | 무엇이었나 | 왜 | 대신 |
 |---|---|---|---|
 | **177** | 「통합 이벤트용 넷째 입구 칸을 만들지 않는다」 | D34 를 **D40 이 뒤집었다** — `event_subscription/` 이 트리 35행에 실재한다. 이걸 두면 **모든 BC 가 골격만으로 blocker** | #90 · #507~#509 |
 | **176** | 「주기가 아닌 비동기 작업이 생겨도 칸은 안 는다」 | 같은 이유 | #90 |
 | **22 · 317** | 「채워질 때 만든다」 | **D54 가 §0 항상-생성을 되살렸다.** D55 가 *「그대로 뒀으면 §0 을 뒤엎을 뻔했다」*고 이미 경고했고, #317 은 #27(「「나중에 그때」로 끝나는 문장은 그 자체가 결함」)을 **자기가 어겼다** | #488 · #489 |
 | **115** | 「HTTP 오류를 안 여는 BC 에는 만들지 않는다」 | **D54 가 「하나 있던 조건부 노드를 지웠다」고 이름까지 댔다** | #488 · #114 |
 | **45 · 461** | 「어댑터 파일 이름 = 선언 파일 이름」 | **T48/D57 이 뒤집었다** — `<capability>/` 아래는 `<technology>_adapter.py` 라 이름이 다르다. 뒤집힘 표에 **#353 만 올렸다** | #353 · #582 |
 | **158 · 161** | 「`_request`·`_response` 를 붙이지 않는다」 | **D41 이 필수로 만들었다** — 트리 27·29행이 `<request>_request.py`·`<response>_response.py` | #30 · #483 |
 | **32** | 「접미사는 이름이 충돌할 때만」 | 같은 결정을 **다른 자**로 재서 같은 파일에 반대 판정을 냈다 — 자는 하나여야 한다 | #30 |
+| **642** | 「승격 부품 50행 출생 하한」 | 소관·응집 판정에 불필요한 크기 하한을 폐지한다. 부품 0 환원과 200행 감사 신호는 유지한다(2026-09-11). | #643 · #644 |
 | **255** | 「리포지토리 둘은 위반이 아니라 검토 대상」 | 근거가 *「위반 술어가 없다」*였는데 **D43·D50 이 술어를 만들었다** → 같은 코드에 `검사기` 와 `blocker` 가 동시에 났다 | #546 |
 | **223 · 381 · 410** | 「`Port`·`Adapter`·`Gateway` 는 파일 이름에 안 나온다」 ×3 | **#41 과 «글자까지» 같은 사본.** 사본이 있으면 정정이 한 자리에서만 일어나지 않는다 — 이번 병의 원인 그 자체다 | #41(폴더명 금지로 정정) |
 
 **★ 이 병을 다시 안 만들려면 자가 하나 더 필요하다** — 지금까지의 완료 판정 둘(「규칙 0건인 칸 0」·「인용 0건인 카드 0」)은 **«빠진 것»만 세고 «남아 있으면 안 되는 것»은 안 센다.** 셋째 자: **「뒤집힌 카드를 근거로 든 규칙이 0인가」**.
 
 ## C2 반영 — 5개 (620~624)
 
 **`framework/test/fake/` 칸 신설**(트리 138 → 140행). 승격의 자가 «소유»가 되면서 framework 포트의 페이크가 **첫 BC 때부터** framework 에 사는데, 그 칸이 없어 진짜 계약과 같은 평면에 놓여 있었다(5차 · L10 F2 · L14 F11 두 렌즈 수렴).
 
 | # | 규칙 | 나온 자리 | 판정 | 근거 | 실측 | 어겼을 때 |
@@ -1161,26 +1162,25 @@
 | 632 | ORM 모델 클래스 이름은 «상시» `<Name>Model` 이다 — 도메인 쪽이 bare(`Order`), ORM 쪽이 `OrderModel` 로 늘 갈린다. «이름이 충돌할 때만»이 아니다 — alias import 로 충돌을 피해도 규칙은 남는다(파일 축은 #335 가 진다). <span>08-11 · T60-1 복원(사용자 승인).</span> | 트리 79행 | `ast` | principle |  | **blocker** |
 | 633 | `<service>_service.py` 의 공개 함수는 인자로 그 연산의 request 계약 **하나**만 받는다 — 맨 스칼라·다중 인자는 위반이고, 인자 0개는 입력 없는 `_query` 만 허용한다. <span>08-11 · T60-2 복원(사용자 승인).</span> | 트리 24행 | `ast` | principle |  | **blocker** |
 | 634 | `<service>_service.py` 의 공개 표면은 모듈 수준 «함수»뿐이다 — 공개 클래스를 두지 않는다(계약 클래스는 `contract/` 에 산다 · `_` 사설은 자유). <span>08-11 · T60-3 복원(사용자 승인).</span> | 트리 24행 | `ast` | principle |  | **blocker** |
 | 635 | `<use_case>_use_case.py` 의 진입점은 클래스 하나이고 실행 메서드는 `execute` 하나다 — 자기 `<use_case>_command.py`/`_query.py` 의 계약 객체 하나를 받아 `<use_case>_result.py` 의 result(스트림이면 `Iterator[<UseCase>Result]` — D40)를 돌려준다. <span>08-11 · T60-4 복원(사용자 승인).</span> | 트리 41행 | `ast` | principle |  | **blocker** |
 | 636 | `bc_error_schema.py` 의 `<Bc>ErrorCode` 는 `StrEnum` 이다 — `Literal`·맨 문자열 상수 모음으로 대신하지 않는다(#572 가 정한 동거의 «타입» 축). <span>08-11 · T60-5 복원(사용자 승인).</span> | 트리 10행 | `ast` | principle |  | **blocker** |
 | 637 | `test/` 아래 어디에도 migration 산출물(파일·operation·적용 순서·과거 state·DDL)을 오라클로 삼는 테스트를 두지 않는다 — `migrations/` 는 `makemigrations` 가 생성한 것이라 테스트 대상이 아니며 기존 것도 삭제한다(신호: `django.db.migrations`·`MigrationExecutor`/`MigrationLoader`/`ProjectState`/`MigrationRecorder`·migration 모듈 import). <span>08-25 · tarot 잔존 판정 5(사용자 «절대 규칙» 확정) — `check-test-config`.</span> | 트리 160~164행 | `ast` | principle |  | **blocker** |
 | 638 | 동명 폴더 승격(#490 교체형)의 승격 폴더는 안에 본체 `<이름>.py` 를 반드시 가진다 — 본체 없는 폴더는 위장이라 위반이다(`__init__.py` 도 함께 있어야 한다). <span>09-01 · 동명 폴더 승격 규범화 — `check-layer-skeleton`.</span> | 승격 허용 13행(§0 교체형) | `path` | principle |  | **blocker** |
 | 639 | 형제 `<이름>.py` 와 승격 폴더 `<이름>/` 의 공존은 위반이다 — 파일시스템은 공존을 허용하고 import 는 패키지가 이겨 조용한 위장 중복이 된다. <span>09-01 · 동명 폴더 승격 규범화.</span> | 승격 허용 13행(§0 교체형) | `path` | principle |  | **blocker** |
 | 640 | 세 어댑터의 바깥 패키지와 고정 역할 폴더의 `__init__.py` 는 재수출 전용이다. 승격 폴더의 `__init__.py` 는 재수출 전용(`from .<모듈> import <이름> as <이름>` 또는 `__all__`)이다 — 본체 코드 동거는 위반이고, 폴더 안 정크드로어 이름(`utils.py`·`helpers.py` 류)도 위반이다. <span>09-01 · 동명 폴더 승격 규범화.</span> | 승격 허용 13행 및 어댑터 고정 패키지 | `ast` | principle |  | **blocker** |
 | 641 | 승격 폴더 내부는 1단 평평이다 — 하위 폴더는 위반이다(부품 군집이 폴더를 요구하면 그것은 트리 개정 신호이지 중첩 근거가 아니다). <span>09-01 · 동명 폴더 승격 규범화.</span> | 승격 허용 13행(§0 교체형) | `path` | principle |  | **blocker** |
-| 642 | 승격 폴더의 각 부품(본체·`__init__.py` 제외)은 50행(물리 행·빈 줄 제외) 이상이다 — 미만이면 위반이고, 신규 여부는 게이트 앵커 차분이 가른다(기존분은 잔존 보고 — 부품 통합 신호이지 승격 환원 의무가 아니다). <span>09-01 · 동명 폴더 승격 규범화.</span> | 승격 허용 13행(§0 교체형) | `ast` | principle |  | **blocker** |
 | 643 | 부품이 0개(본체+`__init__.py` 뿐)가 된 승격 폴더는 위반이다 — 환원 신호다(파일 실현으로 되돌린다 · 기존 폴더면 G0 빚 경로). <span>09-01 · 동명 폴더 승격 규범화.</span> | 승격 허용 13행(§0 교체형) | `path` | principle |  | **blocker** |
-| 644 | 행위 칸 실현(파일 또는 승격 본체·부품)이 200행(물리 행·빈 줄 제외)을 넘으면 캐스케이드 판정 의무 후보다 — ⑴ 확정 위반: 형태 위반은 #638~#643 이 잡는다 ⑵ 후보: 200행 초과(ⓓ 채널·exit 불산입·무조건 방출 — diff 한정은 감사자 몫) ⑶ 물음: 역할 밖 응집 단위가 있는가(①이동/②동명 폴더 승격/③유지 — houserules §1). <span>09-01 · 동명 폴더 승격 규범화 — `check-layer-skeleton` ⓓ.</span> | 승격 허용 13행(§0 교체형) | `ast+` | principle |  | **blocker** |
-| 645 | 명시 `Any` 는 타입이 아니라 검사 포기다 — 함수 시그니처(인자·`*args/**kwargs`·반환)의 bare `Any`(`Optional[Any]`·`Any` 와 None 의 합집합·문자열·별칭·`typing.Any` 포함)는 확정 위반이고, 시그니처 안 제네릭 인자·변수·클래스 속성의 `Any` 는 ⓓ 후보다(감수자가 마무리 — `object`/정확 타입으로 받아 즉시 좁힌다). 프레임워크 오버라이드가 스텁에서 `Any` 를 쓰더라도 우리 선언은 `object` 다(#493 «주석 존재» 와 독립). <span>09-04 · 현장 보고 E — `Any` 정책(하우스룰 §4 R-3447/R-3448).</span> | D58+§4 | `ast+` | principle |  | **blocker** |
+| 644 | 행위 칸 실현(파일 또는 승격 본체·부품)이 200행(물리 행·빈 줄 제외)을 넘으면 캐스케이드 판정 의무 후보다 — ⑴ 확정 위반: 형태 위반은 #638~#641·#643 이 잡는다 ⑵ 후보: 200행 초과(ⓓ 채널·exit 불산입·무조건 방출 — diff 한정은 감사자 몫) ⑶ 물음: 역할 밖 응집 단위가 있는가(①이동/②동명 폴더 승격/③유지 — houserules §1). <span>09-01 · 동명 폴더 승격 규범화 — `check-layer-skeleton` ⓓ.</span> | 승격 허용 13행(§0 교체형) | `ast+` | principle |  | **blocker** |
+| 645 | 명시 `Any` 는 타입이 아니라 검사 포기다 — 함수 시그니처(인자·`*args/**kwargs`·반환)의 bare `Any`(`Optional[Any]`·`Any` 와 None 의 합집합·문자열·별칭·`typing.Any` 포함)는 확정 위반이고, 시그니처 안 제네릭 인자·변수·클래스 속성의 `Any` 는 ⓓ 후보다(감수자가 마무리 — `object`/정확 타입으로 받아 즉시 좁힌다). 확인된 admin 슬롯 밖에서 프레임워크 오버라이드가 스텁에서 `Any` 를 쓰더라도 우리 선언은 `object` 다(#493 «주석 존재» 와 독립). <span>09-04 · 현장 보고 E — `Any` 정책(하우스룰 §4 R-3447/R-3448).</span> admin 허용은 확인된 Django/Parler framework 슬롯과 연결된 private 전달 helper의 열린 UI context 조립·병합·전달에 한한다. 업무 읽기·비교·계산·상태 변경 또는 업무 함수로 값 전달부터 기존 규칙을 적용한다. 출처나 소비가 미해소이면 후보로 흐름을 묻는다. framework 고정 kwargs 밖 bare Any·별도 업무 dict·admin 경로 전체는 면제하지 않는다. #493·#646·#650은 유지한다. | D58+§4 | `ast+` | principle |  | **blocker** |
 | 646 | django-stubs 가 제네릭으로 선언했지만 런타임은 subscript 못 하는 Django 기저(타입 매개변수에 기본값이 없는 것 — admin·forms·CBV)는 모델 타입 인자를 적는다 — `if TYPE_CHECKING:` 별칭(또는 분기 안 중간 ClassDef)이 기본이고 monkeypatch 채택 시 직접 표기다. 맨몸 상속과 `# type: ignore[type-arg]`(헤더·속성 줄)는 확정 위반이고, code 없는 `# type: ignore` 헤더와 `TYPE_CHECKING` 밖 subscript(런타임 `TypeError` 후보)는 ⓓ 후보다. <span>09-04 · 현장 보고 3 S-1(하우스룰 §4 R-3458/R-3459).</span> | D58+§4 | `ast+` | principle |  | **blocker** |
-| 647 | 키가 정해진 값 묶음(레코드)은 딕셔너리로 들고 다니지 않는다 — `dict`/`Mapping`/`MutableMapping` 값 자리의 `Any` 는 전 자리(매개변수·반환·변수·속성) 확정 위반, `object` 는 반환·클래스 속성에 남으면 확정 위반(좁히지 않은 누수)이고 입구 매개변수·즉시 검증 지역 변수는 ⓓ 후보다(면제: `TypeIs/TypeGuard` 반환 · 스텁이 강제하는 `Form.clean`·`Field.deconstruct` 오버라이드). 반환 주석의 자리표시 `object`(루트·시퀀스 원소)도 ⓓ 후보다. <span>09-04 · 현장 보고 3 S-4(하우스룰 §4 R-3447 rev2/R-3448 rev2 · 결정표 R-3451~R-3457).</span> | D58+§4 | `ast+` | principle |  | **blocker** |
+| 647 | 키가 정해진 값 묶음(레코드)은 딕셔너리로 들고 다니지 않는다 — `dict`/`Mapping`/`MutableMapping` 값 자리의 `Any` 는 전 자리(매개변수·반환·변수·속성) 확정 위반, `object` 는 반환·클래스 속성에 남으면 확정 위반(좁히지 않은 누수)이고 입구 매개변수·즉시 검증 지역 변수는 ⓓ 후보다(면제: `TypeIs/TypeGuard` 반환 · 스텁이 강제하는 `Form.clean`·`Field.deconstruct` 오버라이드). 반환 주석의 자리표시 `object`(루트·시퀀스 원소)도 ⓓ 후보다. <span>09-04 · 현장 보고 3 S-4(하우스룰 §4 R-3447 rev2/R-3448 rev2 · 결정표 R-3451~R-3457).</span> admin 허용은 확인된 Django/Parler framework 슬롯과 연결된 private 전달 helper의 열린 UI context 조립·병합·전달에 한한다. 업무 읽기·비교·계산·상태 변경 또는 업무 함수로 값 전달부터 기존 규칙을 적용한다. 출처나 소비가 미해소이면 후보로 흐름을 묻는다. framework 고정 kwargs 밖 bare Any·별도 업무 dict·admin 경로 전체는 면제하지 않는다. #493·#646·#650은 유지한다. | D58+§4 | `ast+` | principle |  | **blocker** |
 | 648 | 컨트롤러 반환 주석의 `Status` 상자는 하나다 — 성공·오류 union 을 한 `Status[…]` 안에 넣거나(`Status[…]` 하나 안에 `Out` 과 `Err` 의 union) `Out` 과 `Status[Err]` 의 union 으로 쓴다. 상자 둘(`Status[A]` 와 `Status[B]` 의 union)은 `Status[T]` 가 불변이라 concrete 직접 반환이 mypy strict 에서 막히고 값 변수를 base 로 주석해 통과시킨 형태도 같은 금지다(형태 금지). <span>09-04 · 현장 보고 3 S-5(ninja §2.2 R-3463 · `check-api-error-controller-contract` 표준 트리 슬라이스 · 프로필 무관).</span> | D58+§4 | `ast` | principle |  | **blocker** |
 | 649 | 성공 응답이 판별 키로 갈리는 union 이면 이름 붙은 `RootModel` 하나로 선언한다 — ninja `Schema` 를 함께 상속하지 않는다(메타클래스 충돌 · `[metaclass]`·`[call-arg] root`). <span>09-04 · 현장 보고 3 S-5(ninja §3.1 R-3464 · 표준 트리 슬라이스).</span> | D58+§4 | `ast` | principle |  | **blocker** |
 | 650 | `json.load(s)` 결과는 `TypeAdapter(그TypedDict)` 로 검증하며 받거나 `x: object` 로 받아 즉시 좁힌다 — 결과가 `object` 아닌 선언 자리(주석 변수·반환·컴프리헨션·직접 접근·리터럴 컨테이너 원소)로 그냥 흐른 자리는 ⓓ 후보다(확정 위반은 #647 소유). <span>09-04 · 현장 보고 3 S-4(R-3448 rev2 · 결정표 R-3453).</span> | D58+§4 | `ast+` | principle |  | **blocker** |
 | 651 | 세 어댑터의 `adapter/`·`command/`·`contract/`·`schema/` 내용 파일은 비공개 클래스를 포함해 클래스 하나당 파일 하나다. `constant/` 는 클래스 없이 관련 상수를 묶는다. 내용 없는 골격 파일·재수출 초기화 파일은 클래스 수 검사에서 제외한다. | 트리 100~109·113~122·125~134행+#488+#490 | `ast` | principle |  | **blocker** |
 
 ## 5차 적대적 리뷰 회수 — 20개 (596~619)
 
 **14개 렌즈(29148·Smells·모순·중복·DDD·Clean·Hexagonal·pub/sub·ATAM·인지차원·Connascence·SAAM·백스톱·framework 승격)가 연 구멍을 메운다.**
 
 앞선 정정에서 **규칙 14건을 걷어냈고**(뒤집힌 카드에서 나온 것 · 축자 사본) **65건의 문면을 고쳤다** — 그 목록은 아래 «걷어낸 것» 절에.

```

## workspace/design/2026-08-11-predicates.md

Before SHA256: c9252a46e9fb330a2f8e0cf8b2baa9f11f2c323a3bf14aea325e27c3c8efe717
After SHA256: 2176d4e20b464ee7fa7f1f1c56431ac088d3d430f5ce51afd5e7bb8ad92c2ce0

```diff
--- before/workspace/design/2026-08-11-predicates.md
+++ after/workspace/design/2026-08-11-predicates.md
@@ -112,44 +112,45 @@
 # 묶음 2 — `#111` ~ `#294`
 
 | # | 바꿈 | 술어 |
 |---|---|---|
 | 111 | ast | `api_router.py` 모듈 AST 에 ①자기 BC 컨트롤러 import ②`def register_<bc>_api(api)` 하나 ③그 본문의 `api.register_controllers(...)`·리터럴 — 이 셋 밖 노드가 있으면 위반 |
 | 124 | ast | `@api_controller` 클래스에서 (public 메서드 수) ≠ (라우트 데코레이터 수)이면 위반 |
 | 125 | ast+ | 후보: 컨트롤러 메서드 중 ①유스케이스 호출 0 또는 2회↑ ②`try/except` 뺀 제어흐름 ③`_command`/`schema_out` 생성이 아닌 호출 / 물음: 「이 문장이 «변환»인가 «판정»인가」 |
 | 132 | ast | 모든 라우트 메서드에 ①라우트 데코레이터 ②인증 인자 ③상태 코드가 «그 파일 안에» 있어야 한다 |
 | 140 | ast+ | 후보: `schema_in` 필드를 `if` 로 검사 후 `raise` 하는 자리 + 제약 선언(`Field(...)`·`@field_validator`)이 0인 스키마 / 물음: **Q2** |
 | 151 | ast+ | 확정: 창구 폴더 이름 토큰에 기술 이름·다른 BC 이름 / 후보: 이름이 `domain_layer/<aggregate>/` 와 «같은» 것 / 물음: **Q1** |
-| 153 | ast+ | 확정: `except <도메인 예외> as e:` 안에서 `e.<attr>` 접근이 있으면 위반 / 후보: 공개 함수 중 유스케이스 호출 0/2회↑ 또는 `except` 밖 제어흐름 / 물음: 「이 문장이 «계약↔응용 DTO 변환»인가」 |
+| 153 | ast+ | 확정: `except <도메인 예외> as e:` 안에서 `e.<attr>` 접근이 있으면 위반 / 후보: 공개 함수 중 출처가 확인된 usecase 실행 횟수가 1이 아니거나 실행 출처/반복 횟수가 미해소(미호출 nested 정의 제외, builder 준비는 실행 수에 불산입) 또는 `except` 밖 제어흐름 / 물음: 「이 문장이 «계약↔응용 DTO 변환»인가」 |
 | 156 | ast | `contract/request/*.py` 클래스 중 `<service>_service.py` 공개 함수 «파라미터» 애너테이션에 0회면 위반, 반환에만 나오면 자리 오배치 |
 | 159 | ast | 거울 — `contract/response/*.py` 클래스가 «반환» 애너테이션에 0회면 위반 |
 | 171 | ast+ | 후보: `contract/exception/` 클래스 중 ①기저를 뺀 이름이 접미사뿐 ②이름 토큰 ∩ #628 = ∅ / 물음: 「부르는 쪽이 이름만 보고 분기할 수 있나」 |
 | 178 | ast | **독립 위반 주체 0** — #179 ∧ #509 ∧ #490 의 합. 검사기를 새로 만들지 않는다(D30) |
 | 179 | ast | task 함수 본문 = `build_<use_case>()` 1회 + 유스케이스 1회 호출 + (선택)command 생성. 그 밖 문장이 있으면 위반. 파일당 task 하나 |
 | 181 | ast+ | 확정: `cron_job/**` 에 「이미 했나」 판정(조회 후 조기 반환·`get_or_create`·중복 키·락) / 후보: **바깥이 부르는 입구 전부**(`cron_job/`·`webhook/**/*_controller.py`·`event_subscription/`) → 도달 유스케이스 중 리포지토리 읽기 0 + `save()` 만 있는 것 / 물음: 「두 번 와도 결과가 같나」 ← **멱등 물음의 소유자**(08-11 · C8 에 #513 에서 이관) |
 | 191 | ast+ | 자동 통과: 첫 토큰이 애그리거트 루트 공개 메서드 이름과 같은 것 / 후보: 이름 전체가 애그리거트 이름이거나 `_list`·`_info`·`_detail`·`_status` 로 끝나는 것 / 물음: **Q1** |
 | 194 | ast+ | 후보: `<use_case>_use_case.py` 의 `If`/`Match`/`Assert` 중 피연산자가 도메인 타입 속성 접근·값 객체 비교인 것 (제외: `Is None` 존재 확인 · 포트 실패 필드 확인) / 물음: **Q2** |
 | 195 | ast | `repository.save/remove` 인자가 «같은 함수 안에서 루트 메서드 호출을 받은» 객체가 아니면 위반. `unit_of_work` 를 받았는데 루트 메서드 호출 0이어도 위반. 면제 셋(조회 전용·순수 위임·외부 조회)이 전부 기계로 보인다 |
 | 196 | ast | `application_layer/**` 에 ①`port/` 밖 `ABC`/`Protocol` 상속 ②이름 `*Presenter`·`*InputBoundary`·`*OutputBoundary` ③진입 함수 반환이 `None` 인데 결과를 다른 객체에 넘김 |
-| 197 | ast | 파라미터 애너테이션에 `*UnitOfWork` 가 있는데 본문에 `with <uow>:`·`save`·`remove`·`after_commit` 이 0이면 위반 |
+| 197 | ast | 파라미터 애너테이션에 `*UnitOfWork` 가 있는데 본문에 `with <uow>:`·`save`·`remove`·`after_commit` 이 0이면 위반 / 설계 선언 별도: 설계 pre-gate는 명시 read-only/UoW 모순과 출처가 확인된 UoW 주입을 선언 확정, 미해소 출처를 선언 후보로 분리한다. 선언 처분은 architect·해당 설계 리뷰/감수자 소유이며 기존 실코드 검사 범위와 다르다. 효과 무기재는 미검증이다. |
+| 202 | ast | 실코드 DTO의 domain aggregate/entity/ORM 누수 검사를 유지한다. 설계 선언 별도: 설계 pre-gate는 add/update 공개 Result/Out/Response에서 명시 import·별칭·중첩/사설 DTO·표준 컨테이너로 출처가 결합된 aggregate/entity 누수를 선언 확정으로, 미해소 출처를 후보로 보고한다. VO/shared VO는 허용하고 이름만으로 확정하거나 OHS import를 합성하지 않는다. 선언 처분은 architect·해당 설계 리뷰/감수자 소유이며 실코드 검사를 대체하지 않는다. |
 | 207 | ast | `<use_case>_command.py` 필드 타입이 ①애그리거트 루트 ②`entity/` 클래스 ③ORM 모델이면 위반. 값 객체는 통과 |
 | 210 | ast | `schema_out` 생성 인자가 참조하는 이름이 그 메서드의 `<use_case>_result`·요청 스키마 밖에서 오면 위반 |
 | 213 | path | `*_query.py`(클래스 접미사 `…DomainBypassQuery`)가 `port/domain_bypass_query/<capability>/` 밖에 있으면 위반 |
 | 227 | ast+ | 확정: 필드 타입이 `domain_layer/**` 면 위반(#228) / 후보: 필드가 하나뿐이거나 전부 표준 타입인 `<data>_*` 클래스 / 물음: 「이 자료를 원시값 인자로 «펴서» 넘길 수 있나」 |
 | 228 | ast | ①import 에 `domain_layer` ②필드 애너테이션이 가리키는 심볼의 «정의 파일»이 `domain_layer/**` ③`<use_case>_{command,query,result}` 참조 — 하나라도 있으면 위반. **★ 토큰 검사를 쓰지 않는다**(`child_id` 오탐) |
 | 231 | ast | `<A>_repository.py` 메서드 중 파라미터·반환에 그 애그리거트가 0회이고 반환형이 `bool`/`int` 도 아니면 위반 |
 | 233 | ast+ | 확정: 폴더 이름 토큰 ∩ ({기술 이름}∪{BC 이름}∪{모델 표 이름}) ≠ ∅ / 후보: 이름이 명사 하나뿐 / 물음: **Q1** |
 | 241 | ast | `<capability>_port.py` 클래스가 `__enter__`/`__exit__`/`commit`/`rollback`/`after_commit` 을 가지면 위반. 거꾸로 `*_unit_of_work.py` 가 셋(#245) 밖 메서드를 가지면 위반 |
 | 254 | **human** | **Q4** — 기계는 «너무 갈린 쪽»(#546)만 보고 «너무 묶인 쪽»에 신호가 0이다 |
 | 257 | ast+ | 확정: 응용·입구에서 리포지토리 객체에 «속성 접근 후 메서드 호출»(`order.line.change(...)`) / 후보: 루트 공개 메서드 중 자기 속성에 대입하면서 마지막 문장이 검증 호출/`raise` 조건이 아닌 것 / 물음: **Q4** |
 | 259 | ast+ | 확정: `entity/` 클래스에 식별자 필드 0(#260) / 후보: ①`value_object/` 인데 `id`·`*_id` 를 가진 것 ②`entity/` 인데 `__eq__` 를 «전 필드»로 정의 / 물음: **Q4** |
-| 268 | ast+ | 후보: 값 객체 클래스 중 `__post_init__`/`__init__` 에 `raise` 가 0인 것 / 물음: **Q2**(이 타입 조합만으로 잘못된 값이 «불가능»한가) |
+| 268 | ast+ | 허용: 출처가 확인된 닫힌 표준 Enum/StrEnum/IntEnum의 생성 검증 / 후보: 일반 값 객체의 생성자 raise 부재 또는 custom/open Enum(raise 유무와 별개; 동적 멤버·추가 base/metaclass·생성 hook·변경된 출처는 닫힌 증명이 아님) / 물음: **Q2**(이 타입 조합만으로 잘못된 값이 «불가능»한가) |
 | 269 | ast | `domain_layer/<A>/event/<E>.py` 클래스가 같은 BC 안에서 한 번도 참조되지 않으면 위반 |
 | 271 | ast+ | 확정: 클래스 이름 첫 토큰이 애그리거트 루트 공개 메서드 이름과 같은 것(`ReduceInventory`↔`Inventory.reduce()`) / 후보: 마지막 토큰이 `-ed`/`-en` 도 아니고 불규칙 과거분사 목록에도 없는 것 / 물음: **Q1** |
 | 280 | ast | 핸들러의 이벤트 파라미터가 `Call.args` 에 «통째»(`Name`)로 들어가면 위반. `Attribute(Name(e),'sku')` 처럼 필드만 넘기면 통과. `apply`/`handle`/`on_*` 이름의 애그리거트 메서드 호출도 위반 |
 | 285 | ast+ | 후보: `<capability>_query.py` 메서드 중 반환이 `bool`/`int` 이고 그 구현이 애그리거트 리포지토리와 «같은 ORM 모델»을 질의 / 물음: 「이 수가 «애그리거트 컬렉션»을 세거나 합친 것인가」 |
 | 292 | ast | `application/<bc>/**` 에서 `Exception` 하위 `ClassDef` 의 파일 경로가 셋(+`domain_bypass_query/**/exception.py`) 밖이면 위반 |
 | 294 | ast | `adapter/persistence/**` 와 `port/unit_of_work/**` 에 `Exception` 상속 `ClassDef` 가 있으면 위반(넷째 자리) |
 | 127 137 145 248 | human | **면제라 대상 밖** |
 
 ---
 
@@ -206,24 +207,26 @@
 |---|---|---|
 | 511 | ast+ | 후보 ㉠서명검증 데코레이터(#517)가 붙은 라우트 ㉡`<area>` 토큰이 벤더 사전에 있는 것 ㉢`webhook/<provider>/` 인데 provider 가 #628 업무 어휘 / 물음: 「이 스키마를 우리가 고칠 수 있나」 |
 | 512 | ast+ | 후보: `<provider>` 토큰이 벤더 사전에 **없고** #628 어휘나 역할 접미(`_gateway|_provider|_client|_service|_api|_system`)와 겹치는 것 / 물음: 「보내는 쪽이 자기를 이렇게 부르나」 |
 | 512 | ast+ | 확정: `webhook/<provider>/` 이름이 능력·역할 낱말 deny-list{gateway,provider,payment,billing,notification,auth,external}에 들면 위반 / 후보: #511 ㉡ 의 벤더 사전에 없는 이름 / 물음: 「보내는 쪽 문서가 자기를 이 이름으로 부르나」 |
 | 516 | ast | `webhook/**` 공개 함수에 HTTP 라우트 데코레이터가 없거나 비-HTTP 소켓 라이브러리(`pika`·`kombu`·`confluent_kafka`·`grpcio`)를 import 하면 위반 |
 | 520 | ast+ | 후보: 발행 호출이 ㉠`try:` 안 ㉡반환값을 바인딩·분기 ㉢발행 뒤 같은 함수에서 ACL·OHS 호출 / 물음: 「이 사실이 안 나가면 내가 할 일이 있나」 |
 | 526 | **human** | **Q3** |
 | 529 | ast+ | 후보: `external_broker_port.py` 를 쓰는 발행 자리 × 그 사실의 `<event>_subscription.py` 가 이 저장소 안에 있는 짝 / 물음: 「듣는 쪽이 따로 배포되나」 |
 | 530 | **human** | **Q3** — 기계 몫은 #529 가 갖는다 |
 | 532 | ast+ | 후보: external 구독 경로 유스케이스 + #533 봉투 인자 유무 / 물음: #181 과 같은 물음. **「도달 보장」은 술어가 안 선다** — 미들웨어 «설정»에 있어 저장소 밖이다(#603⑷ 가 선언 유무만 잰다) |
+| 546 | ast+ | 확정은 해소된 동일 트랜잭션 영역에서 서로 다른 repository/aggregate 타입 쓰기다. 순차 독립 UoW는 분리하고 nested UoW·외부 Django atomic은 결합한다. 영역·출처 미해소는 후보이며 같은 트랜잭션인지 감수자가 확인한다. / 물음: 이 쓰기들이 실제 같은 트랜잭션인가? 같은 타입 두 인스턴스는 별도 식별하지 않는다. |
 | 547 | ast+ | 후보 ⑴#546 의 잔여(대상은 **애그리거트 리포지토리** 타입 · 쓰기 메서드는 #597 이 `save`/`remove` 로 고정) ⑵`<A>_repository.py` 를 쓰는 `<use_case>/` 들의 부모 `<area>/` 집합 크기 ≥2 ⑶루트의 무제한 컬렉션 필드·`entity/` 수 / 물음: 「이 둘이 «동시에» 일어나면 업무가 정말 막아야 하나」 |
 | 549 | ast | `adapter/persistence/repository/**` 에서 캐시 API 사용 0 · `select_for_update()` 결과에 캐시 0 · UoW 블록 안 캐시 읽기 0 |
 | 553 | ast+ | 후보 ㉠#628 어휘가 조건식에 ㉡반환형 `bool` ㉢도메인 필드에 걸린 비교·산술 ㉣도메인 인스턴스 «메서드» 호출(재구성 제외) / 물음: **Q2** ← **Q2 의 소유자** |
-| 556 | ast | ㉠도메인·응용에 재시도 기계(`tenacity`·`backoff`·`retrying`·`sleep` 루프) 0 ㉡벤더 오류 코드 비교가 `adapter/**` 밖 0(=#557) ㉢유스케이스 재호출은 `driving_layer/**` 에서만 |
+| 556 | ast | ㉠도메인·응용에 재시도 기계(`tenacity`·`backoff`·`retrying`·`sleep` 루프) 0 ㉡확인된 vendor 출처의 오류 코드 비교가 `adapter/**` 밖 0(미해소 후보 처분은 #557 소유) ㉢유스케이스 재호출은 `driving_layer/**` 에서만 |
+| 557 | ast+ | code/errno/status_code 비교의 수신자가 확인된 vendor 출처이면 확정, 확인된 domain 또는 application의 command/query/result/port 계약이면 허용한다. 미해소·혼합·재바인딩 출처는 후보로 그 코드의 주인을 감수자가 묻는다. except 구문이나 속성 이름만으로 vendor를 확정하지 않는다. / 물음: 이 속성은 vendor 코드인가 승인된 우리 계약의 필드인가? |
 | 558 | ast | #614 의 링 라벨로 파일마다 링을 정하고 그 링 규칙(#4·#5·#560·#615)을 건다 · 검사기 경로 필터에 `framework/` 통째 면제가 있으면 위반 |
 | 559 | ast | **새 술어 0** — #560 ∧ #561 ∧ #562 가 곧 「이 파일이 순수한가」 |
 | 563 | **human** | **Q3** |
 | 564 | ast+ | 후보 ㉠트리 밖 `saga/`·`process_manager/`(#490) ㉡값 토큰이 `<use_case>/` 폴더 이름과 겹치는 Enum 필드를 가진 ORM 모델 / 물음: 「업무가 이 단계 이름을 입으로 부르나」 |
 | 565 | ast+ | 후보: `domain_layer/**` 의 Enum 중 값 토큰이 `<use_case>/`·`<service>/` 이름과 겹치는 것 / 물음: **Q1** ← **단계 이름 물음의 소유자** |
 | 567 | ast | 저장소 어디에도 `dto` 토큰이 폴더·파일·클래스·별칭 이름에 없다 |
 | 571 | ast+ | 확정: result 모듈의 공개 클래스가 2개 이상 / 후보: 공개 클래스 이름에 `Error`·`Failure`·`Exception` 토큰이 있음 / 물음: 도메인 명사를 담은 성공 결과인가, 유스케이스 실패를 값으로 반환하는가? 후자만 위반이다. 필드명만으로 확정하지 않는다. |
 | 580 | ast | **#579 와 같은 술어** — `test/`·`framework/test/` 밖에서 `fake/` import 하면 위반 + `dependency_wiring.py` 가 설정·플래그 분기로 페이크를 꽂으면 위반 |
 | 584 594 595 512 | ast+ | **공통 사전 술어** — 폴더 이름 토큰 T ∩ (의존성 배포 이름 ∪ `framework/<technology>/`·`external_system/<system>/` 이름 ∪ 계기 낱말{nightly,daily,hourly,weekly,realtime,on_*} ∪ 전달 수단 접미{_client,_sdk,_api,_driver,_gateway,_queue}) ≠ ∅ → 후보 / 물음: 「그것이 바뀌어도 이 이름이 그대로인가」 ← **#595 가 소유자** |
 | 584 | ast+ | 확정·후보: #595 의 술어를 `framework/<capability>/` 에 적용 / 물음: =#595 |
@@ -234,24 +237,24 @@
 | 593 | ast | 허용: `ImportFrom(django.db → migrations, models)` · `ClassDef Migration` 하나 · 대입은 initial·dependencies·operations·replaces 넷뿐 · operations 원소는 전부 `migrations.*` 호출 / 위반: 그 밖의 `FunctionDef`·`RunPython`·`RunSQL`·`if`/`for`·도메인 import·데코레이터·최상단 상수. 보조: `makemigrations --check --dry-run` |
 | 594 | ast+ | 확정·후보: #595 의 술어를 `port/<capability>/` 에 적용 / 물음: =#595 |
 | 595 | ast+ | 확정: 이름의 `_`-토큰이 기술 이름 집합(#19)에 정확 일치(`smtp`·`redis`·`celery`) / 후보: 수단·계기 낱말 집합{client,cache,sync,cron,queue,http,rest}에 드는 토큰이 있는 이름 / 물음: 「그것(공급자·계기·수단)이 바뀌어도 이 이름이 그대로인가」 ← 물음의 소유자(#584·#594 가 참조) |
 | 601 | ast | `E = {(subscription, use_case)}`(#509 로 간선 결정적) · `publishes(u) ⟺ uow.after_commit(...) 인자에 브로커 publish`(#539③) · `∃(s,u)∈E. publishes(u)` 면 위반(두 겹) |
 | 603 | ast | 일곱 중 여섯이 «있나» 검사 — ⑴outbox 모델 + 같은 트랜잭션 쓰기 ⑶#533 ⑷데드레터 선언 ⑸순서 보장 선언 ⑹직렬화기 ⑺버전 필드 / 사람은 ⑵ 소비자 멱등(=#181) 하나 |
 | 607 | ast+ | 후보 ㉠반환형 `bool`(#606⑴ 을 framework 전 파일로 확대) ㉡조건식에 «정책 리터럴»(숫자 임계값·상태 문자열) ㉢갈래마다 서로 다른 반환 리터럴 / 물음: **Q2**(#553 과 술어 공유) |
 | 617 | ast | `framework/<capability>/<data>_out.py` 의 {식별자 ∪ 문자열 리터럴 키} 토큰 ∩ #628 합집합 ≠ ∅ 이면 위반 ※ **#628 이 재료 소비자로 이미 지명했고 형제 #518·#562·#587 이 전부 `ast` 였다** |
 | 618 | ast+ | ㉠`_()`·`gettext`·`format_lazy`·`babel` 호출 0(=#588) ㉡필드 이름 ∩ 채널 설정 낱말(`host`·`port`·`url`·`endpoint`·`api_key`·`token`·`timeout`·`region`·`bucket`·`template_id`) ≠ ∅ → 위반 / 남는 후보는 #590 의 물음 |
 | 619 | ast+ | 후보: 자료 클래스 중 필드가 «하나»이거나 모든 필드가 표준 타입이고 계약 시그니처에서 한 번만 쓰이는 것 / 물음: 「이것이 원시값 하나로 되나」 (뒷문장 「#228 자동 성립」은 `framework/`→`domain_layer/` import 0 으로 이미 기계 확정) |
 | 629 | ast+ | 확정: 없음 / **후보: 집합 차** — `webhook/**`·`event_subscription/**` 이 부르는 유스케이스가 «쓰는» 애그리거트 집합 **A**, `cron_job/**` 이 부르는 유스케이스가 «쓰는» 집합 **B** → **A − B ≠ ∅ 이면 후보** (그 애그리거트는 바깥이 안 부르면 영영 안 채워진다) / 물음: 「이 입구가 «안 와도» 업무가 돌아가나」 |
-| 644 | ast+ | 후보 ⑴행위 칸 실현(파일 또는 승격 본체·부품 — `__init__.py` 제외)의 물리 행수(빈 줄 제외) >200 — `check-layer-skeleton` ⓓ 채널이 행수·top-level 요약 페이로드로 방출(무조건 방출·exit 불산입 — diff 한정은 감사자 몫) ⑵확정 위반은 형태 규칙 #638~#643 소유 / 물음: 「역할 밖 응집 단위가 있는가 — ①이동/②동명 폴더 승격/③유지(houserules §1 캐스케이드)」 |
-| 645 | ast+ | 확정 ⑴함수·메서드 시그니처(인자·`*args`·`**kwargs`·반환)의 애너테이션이 bare `Any` — 루트가 `Any`(모듈 import 로 `typing`/`typing_extensions` 의 `Any` 에 바인딩된 이름·`typing.Any` 속성·문자열 주석 재파싱 포함)이거나 `X` 와 None 의 합집합(파이프·`Optional[X]`·`Union[…]`)을 평탄화해 None 을 뺀 구성원에 `Any` 가 하나라도 있거나(`Any` 는 합집합을 삼킨다) `Annotated[Any, …]` 의 루트가 `Any` — 모듈 수준에서 비-Any 로 그림자되지 않은 `Any` 이름은 fail-closed 로 Any · `Literal["Any"]` 의 문자열은 값이라 제외 — `check-public-surface-annotation` 이 위반으로 방출(수신자 `self`/`cls` 만 제외 · 함수 이름 dunder 는 면제 아님) / 후보 ⑵시그니처 안 제네릭 인자(`dict[str, Any]`·`Callable[..., Any]`)와 변수·클래스 속성(AnnAssign)의 `Any` — ⓓ 채널(exit 불산입) / 물음: 「이 `Any` 를 `object`(즉시 좁힘)·정확 타입으로 바꿀 수 있나 — 프레임워크 계약이라도 우리 선언은 `object` 다」 |
+| 644 | ast+ | 후보 ⑴행위 칸 실현(파일 또는 승격 본체·부품 — `__init__.py` 제외)의 물리 행수(빈 줄 제외) >200 — `check-layer-skeleton` ⓓ 채널이 행수·top-level 요약 페이로드로 방출(무조건 방출·exit 불산입 — diff 한정은 감사자 몫) ⑵확정 위반은 형태 규칙 #638~#641·#643 소유 / 물음: 「역할 밖 응집 단위가 있는가 — ①이동/②동명 폴더 승격/③유지(houserules §1 캐스케이드)」 |
+| 645 | ast+ | 확정 ⑴함수·메서드 시그니처(인자·`*args`·`**kwargs`·반환)의 애너테이션이 bare `Any` — 루트가 `Any`(모듈 import 로 `typing`/`typing_extensions` 의 `Any` 에 바인딩된 이름·`typing.Any` 속성·문자열 주석 재파싱 포함)이거나 `X` 와 None 의 합집합(파이프·`Optional[X]`·`Union[…]`)을 평탄화해 None 을 뺀 구성원에 `Any` 가 하나라도 있거나(`Any` 는 합집합을 삼킨다) `Annotated[Any, …]` 의 루트가 `Any` — 모듈 수준에서 비-Any 로 그림자되지 않은 `Any` 이름은 fail-closed 로 Any · `Literal["Any"]` 의 문자열은 값이라 제외 — `check-public-surface-annotation` 이 위반으로 방출(수신자 `self`/`cls` 만 제외 · 함수 이름 dunder 는 면제 아님) / 후보 ⑵시그니처 안 제네릭 인자(`dict[str, Any]`·`Callable[..., Any]`)와 변수·클래스 속성(AnnAssign)의 `Any` — ⓓ 채널(exit 불산입) / 물음: 「이 `Any` 를 `object`(즉시 좁힘)·정확 타입으로 바꿀 수 있나 — 확인된 admin framework 슬롯 밖의 우리 선언은 `object` 다」 / admin 허용은 확인된 Django/Parler framework 슬롯과 연결된 private 전달 helper의 열린 UI context 조립·병합·전달에 한한다. 업무 읽기·비교·계산·상태 변경 또는 업무 함수로 값 전달부터 기존 규칙을 적용한다. 출처나 소비가 미해소이면 후보로 흐름을 묻는다. framework 고정 kwargs 밖 bare Any·별도 업무 dict·admin 경로 전체는 면제하지 않는다. #493·#646·#650은 유지한다. |
 | 646 | ast+ | 확정 ⑴클래스 기저가 django-stubs 제네릭 Django 기저(타입 매개변수에 기본값이 없는 admin 5·forms 9·CBV 32 — origin 은 모듈 import 바인딩으로 dotted 해소 · 모듈 수준 별칭은 뒤 정의 우선으로 추적)로 해소되는데 맨몸(Name/Attribute)이다 ⑵클래스 헤더 범위(`class` 줄부터 괄호 깊이 0 의 첫 `:` 줄 · 데코레이터 제외)나 기저 집합 클래스 본문 직계 대입 줄에 `# type: ignore[type-arg]` 가 있다(⑴⑵ 동시는 클래스당 1건) — `check-public-surface-annotation` 이 `application/`·`framework/` 루트에서 위반으로 방출 / 후보 ⑶헤더의 code 없는 `# type: ignore` ⑷`TYPE_CHECKING` 밖 subscript(별칭·헤더 직접) / 물음: ⑶덮은 진단이 `[type-arg]` 인가 ⑷`django_stubs_ext.monkeypatch()` 를 채택했는가(houserules §6.1 관찰) |
-| 647 | ast+ | 확정 ⑴`dict`/`Dict`/`Mapping`/`MutableMapping` 값 자리(마지막 슬라이스 원소 · 문자열 주석 재파싱 · `Literal` 안 제외 · import 별칭 해소)가 `Any` 인 애너테이션(매개변수·별표 인자·반환·변수·클래스 속성 어디든) ⑵값 자리가 `object` 인 반환 애너테이션·클래스 직계 속성(면제: 반환 루트 `TypeIs/TypeGuard` · `clean()`×Form 계열 · `deconstruct()`×Field 계열 오버라이드) — `application/`·`framework/` 루트 · #645 nested 후보는 같은 애너테이션에서 생략 / 후보 ⑶값 자리 `object` 인 매개변수·변수 ⑷반환 애너테이션의 자리표시 `object`(루트·union 구성원·tuple/list/Sequence/Iterable/Iterator/set/frozenset/Collection 원소) / 물음: ⑶입구인가 — 받는 즉시 `TypeAdapter`/`TypeIs` 로 좁히는가 ⑷정확 타입·도메인 이벤트 union·`JsonValue` 로 바꿀 수 있는가(좁히기 도우미면 `TypeIs` 반환 · 스텁이 강제한 콜백 미러면 통과) |
+| 647 | ast+ | 확정 ⑴`dict`/`Dict`/`Mapping`/`MutableMapping` 값 자리(마지막 슬라이스 원소 · 문자열 주석 재파싱 · `Literal` 안 제외 · import 별칭 해소)가 `Any` 인 애너테이션(매개변수·별표 인자·반환·변수·클래스 속성 어디든) ⑵값 자리가 `object` 인 반환 애너테이션·클래스 직계 속성(면제: 반환 루트 `TypeIs/TypeGuard` · `clean()`×Form 계열 · `deconstruct()`×Field 계열 오버라이드) — `application/`·`framework/` 루트 · #645 nested 후보는 같은 애너테이션에서 생략 / 후보 ⑶값 자리 `object` 인 매개변수·변수 ⑷반환 애너테이션의 자리표시 `object`(루트·union 구성원·tuple/list/Sequence/Iterable/Iterator/set/frozenset/Collection 원소) / 물음: ⑶입구인가 — 받는 즉시 `TypeAdapter`/`TypeIs` 로 좁히는가 ⑷정확 타입·도메인 이벤트 union·`JsonValue` 로 바꿀 수 있는가(좁히기 도우미면 `TypeIs` 반환 · 스텁이 강제한 콜백 미러면 통과) / admin 허용은 확인된 Django/Parler framework 슬롯과 연결된 private 전달 helper의 열린 UI context 조립·병합·전달에 한한다. 업무 읽기·비교·계산·상태 변경 또는 업무 함수로 값 전달부터 기존 규칙을 적용한다. 출처나 소비가 미해소이면 후보로 흐름을 묻는다. framework 고정 kwargs 밖 bare Any·별도 업무 dict·admin 경로 전체는 면제하지 않는다. #493·#646·#650은 유지한다. |
 | 650 | ast+ | 후보 ⑴`json.load(s)`(모듈 별칭·from import 바인딩 해소) 결과가 «선언 값 타입이 `object` 가 아닌 자리»로 흐른다 — AnnAssign 주석 루트 · Return 의 반환 주석 루트 · 리터럴 컨테이너 원소(그 리터럴이 AnnAssign/Return 값이면 원소 슬롯 · 호출 인자면 비후보) · 컴프리헨션 요소 · 직접 첨자/속성 접근(union 은 전 구성원 `object` 일 때만 비후보 · `x: object = …`·파서 직접 인자·무주석 Assign 은 후보 아님) ⑵확정 위반은 #647 소유 / 물음: 「`TypeAdapter(<TypedDict>).validate_python/validate_json` 으로 검증하며 받았거나 `x: object` 로 받아 즉시 좁혔는가」 |
 | 651 | ast | 세 어댑터 패키지의 고정 역할 직계 내용 파일에서 비공개·중첩을 포함한 ClassDef 수를 센다 — adapter·command·contract·schema 는 정확히 1, constant 는 0. __init__.py 와 내용 없는 골격 파일은 제외한다. |
 | 648 | ast | 확정 ⑴표준 트리 슬라이스 대상(api/** 전 파일 + OHS `*_service.py` · 프로필 무관) 함수의 반환 애너테이션을 평탄화(파이프 union·`Optional`·`Union`·문자열 주석 재파싱)한 구성원 중 `Status[…]`(origin `ninja.Status`/`ninja.responses.Status` — 모듈 import 바인딩으로 dotted 해소)가 2개 이상이면 위반 — `check-api-error-controller-contract` 가 def 줄 좌표로 방출(overlap 억제 비대상 · `-> Status[Out 과 Err 의 union]` 또는 `-> Out 과 Status[Err] 의 union` 은 통과) |
 | 649 | ast | 확정 ⑴ClassDef 기저에 ninja `Schema`(origin `ninja.Schema`/`ninja.schema.Schema`)와 pydantic `RootModel`(`pydantic.RootModel`/`pydantic.root_model.RootModel`)이 함께 있으면 위반 — 파일 한정 없음(트리 슬라이스 대상 파일 전부) · class 줄 좌표 · `RootModel[Annotated[…, Field(discriminator=…)]]` 단독 상속은 통과 |
 | 626 | **human** | **Q3** — 다만 **처방 이행**(받는 쪽에 `cron_job/` + `anticorruption_layer/<owner>/` 경로가 있나)은 `path` 로 «잰다» |
 | 627 | ast | 구독 경로 유스케이스 안에서 사실 payload 의 «식별자 아닌»(`*_id` 아닌) 필드가 애그리거트 생성·변경 인자 → `save()` 로 흐르면 위반. `+=`·`Sum`·`count` 로 자기 저장 필드를 집계해도 위반 |
 | 630 | ast | `models/**` 의 `Model` 하위 ClassDef 중 `Meta` 에 `abstract`/`proxy`/`managed=False` 가 없는 «신규»(diff 기준 추가) 클래스에 ⑴`db_table` 대입이 없거나 ⑵값 ≠ `<app_label>_` + snake(클래스명 − `Model`) 이면 위반. 기존 클래스는 테이블명 보존이라 면제 |
 | 631 | ast | `models/**` 의 관계 필드(`ForeignKey`·`OneToOneField`·`ManyToManyField`) 첫 인자가 가리키는 모델이 «다른 BC 의» `models/**` 에 살면 위반 — 문자열 `"app.Model"` 은 app_label 로, 클래스 참조는 import 경로로 푼다(장고 contrib 등 BC 밖 모델은 대상 아님) |
 | 632 | ast | `models/**` 의 `django.db.models.Model` 하위(가접 포함) ClassDef 이름이 `Model` 로 끝나지 않으면 위반 |
 | 633 | ast | `<service>_service.py` 공개 함수의 파라미터가 2개 이상이면 위반 · 1개면 애너테이션 타입이 같은 서비스 `contract/request/**` 의 클래스가 아니면 위반 · 0개는 함수명이 `_query` 로 끝날 때만 |

```

## workspace/plan/2026-08-11-rule-owner-map.md

Before SHA256: aaf43bd127b3185f99154fa55d4dda25cf0478df0c0f3fd4c2556da96d421e95
After SHA256: f059d7380d62a249d2c4922c2e432c8e723222ec7930226d92f89160b6d01317

```diff
--- before/workspace/plan/2026-08-11-rule-owner-map.md
+++ after/workspace/plan/2026-08-11-rule-owner-map.md
@@ -1,17 +1,18 @@
 # 규칙 → 소유자 매핑표 (Phase 0 산출물)
 
 생성: `python3 workspace/tools/spec_lint.py --emit-owner-map` · 검증: 같은 도구 ⑧
 
 - **ⓐ 정본**(`skills/discipline-houserules/references/final.md`)은 **전 규칙**의 값 소유자라 컬럼에 없다. ⓑ SKILL.md 는 포인터만(값 0).
 - 모양: `path`·`ast`→ⓒ 하나 · `ast+`→ⓒ+ⓓ · `human`→ⓓ 하나. `어겼을 때=검사기`인 행의 ⓒ 는 검사기의 검사기(`workspace/tools/checker_lint.py`)다.
 - **작업**: `신설`=그 자리에 새로 쓴다(백스톱 실측 0 이라 대부분) · `재작성`=있는 로직을 다시 · `치환`=이름 갈이 · `무변`.
+- 폐지 #642: 행수 하한 제거. 현행 승격 형태는 #638~#641·#643, 감사 신호는 #644가 소유한다.
 - `#486~#492`(제1원칙)는 다른 모든 검사보다 먼저 도는 **별도 게이트**다(명세 «읽는 법»).
 
 | # | 판정 | ⓒ 검사기 | ⓓ 에이전트 | 작업 | 비고 |
 |---|---|---|---|---|---|
 | 1 | ast | scripts/check-context-isolation.py | — | 신설 |  |
 | 2 | ast | scripts/check-context-isolation.py | — | 신설 |  |
 | 3 | ast | scripts/check-context-isolation.py | — | 신설 |  |
 | 4 | ast | scripts/check-transaction-boundary.py (신설) | — | 신설 |  |
 | 5 | ast | scripts/check-context-isolation.py | — | 신설 |  |
 | 7 | ast | scripts/check-event-publish.py (신설) | — | 신설 |  |
@@ -161,29 +162,29 @@
 | 181 | ast+ | scripts/check-missable-entrance.py (신설) | agents/discipline-reviewer.md | 신설 |  |
 | 182 | path | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
 | 183 | path | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
 | 185 | ast | scripts/check-context-isolation.py | — | 신설 |  |
 | 186 | ast | scripts/check-context-isolation.py | — | 신설 |  |
 | 187 | path | scripts/check-layer-skeleton.py | — | 재작성 |  |
 | 188 | path | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
 | 189 | ast | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
 | 190 | path | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
 | 191 | ast+ | scripts/check-usecase-dto-placement.py | agents/discipline-reviewer.md | 재작성 |  |
-| 192 | path | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
+| 192 | path | scripts/check-usecase-dto-placement.py | — | 재작성 | 행수 하한 없는 역할 밖 응집 승격 예외; 부품 각각 기존 규칙 적용 |
 | 193 | path | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
 | 194 | ast+ | scripts/check-usecase-dto-placement.py | agents/discipline-reviewer.md | 재작성 |  |
 | 195 | ast | scripts/check-transaction-boundary.py (신설) | — | 신설 |  |
 | 196 | ast | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
-| 197 | ast | scripts/check-transaction-boundary.py (신설) | — | 신설 |  |
+| 197 | ast | scripts/check-transaction-boundary.py (신설) | — | 신설 | 설계 pre-gate는 명시 read-only/UoW 모순과 출처가 확인된 UoW 주입을 선언 확정, 미해소 출처를 선언 후보로 분리한다. 선언 처분은 architect·해당 설계 리뷰/감수자 소유이며 기존 실코드 검사 범위와 다르다. 효과 무기재는 미검증이다. |
 | 200 | ast | scripts/check-transaction-boundary.py (신설) | — | 신설 |  |
 | 201 | path | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
-| 202 | ast | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
+| 202 | ast | scripts/check-usecase-dto-placement.py | — | 재작성 | 설계 pre-gate는 add/update 공개 Result/Out/Response에서 명시 import·별칭·중첩/사설 DTO·표준 컨테이너로 출처가 결합된 aggregate/entity 누수를 선언 확정으로, 미해소 출처를 후보로 보고한다. VO/shared VO는 허용하고 이름만으로 확정하거나 OHS import를 합성하지 않는다. 선언 처분은 architect·해당 설계 리뷰/감수자 소유이며 실코드 검사를 대체하지 않는다. |
 | 204 | path | workspace/tools/checker_lint.py (신설) | — | 신설 |  |
 | 205 | ast | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
 | 206 | path | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
 | 207 | ast | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
 | 208 | ast | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
 | 209 | path | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
 | 210 | ast | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
 | 211 | ast | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
 | 212 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
 | 213 | path | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
@@ -454,32 +455,32 @@
 | 535 | ast | scripts/check-db-table.py | — | 신설 |  |
 | 536 | ast | scripts/check-db-table.py | — | 신설 |  |
 | 537 | ast | scripts/check-db-table.py | — | 신설 |  |
 | 538 | ast | scripts/check-db-table.py | — | 신설 |  |
 | 539 | ast | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
 | 540 | ast | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
 | 541 | ast | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
 | 542 | ast | scripts/check-domain-model.py (신설) | — | 신설 |  |
 | 543 | ast | scripts/check-domain-model.py (신설) | — | 신설 |  |
 | 545 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
-| 546 | ast | scripts/check-domain-model.py (신설) | — | 신설 |  |
+| 546 | ast+ | scripts/check-domain-model.py (신설) | agents/discipline-reviewer.md | 신설 | 확정은 해소된 동일 트랜잭션 영역에서 서로 다른 repository/aggregate 타입 쓰기다. 순차 독립 UoW는 분리하고 nested UoW·외부 Django atomic은 결합한다. 영역·출처 미해소는 후보이며 같은 트랜잭션인지 감수자가 확인한다. |
 | 547 | ast+ | scripts/check-domain-model.py (신설) | agents/discipline-reviewer.md | 신설 |  |
 | 548 | ast | scripts/check-domain-model.py (신설) | — | 신설 |  |
 | 549 | ast | scripts/check-domain-model.py (신설) | — | 신설 |  |
 | 550 | ast | scripts/check-domain-model.py (신설) | — | 신설 |  |
 | 551 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
 | 552 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
 | 553 | ast+ | scripts/check-port-adapter-pairing.py (신설) | agents/discipline-reviewer.md | 신설 |  |
 | 554 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
 | 555 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
 | 556 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
-| 557 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
+| 557 | ast+ | scripts/check-port-adapter-pairing.py (신설) | agents/discipline-reviewer.md | 신설 | code/errno/status_code 비교의 수신자가 확인된 vendor 출처이면 확정, 확인된 domain 또는 application의 command/query/result/port 계약이면 허용한다. 미해소·혼합·재바인딩 출처는 후보로 그 코드의 주인을 감수자가 묻는다. except 구문이나 속성 이름만으로 vendor를 확정하지 않는다. |
 | 558 | ast | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
 | 559 | ast | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
 | 560 | ast | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
 | 561 | ast | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
 | 562 | path | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
 | 563 | human | — | agents/design-architect.md | 치환 |  |
 | 564 | ast+ | scripts/check-event-publish.py (신설) | agents/discipline-reviewer.md | 신설 |  |
 | 565 | ast+ | scripts/check-domain-model.py (신설) | agents/discipline-reviewer.md | 신설 |  |
 | 566 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
 | 567 | ast | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
@@ -545,20 +546,19 @@
 | 632 | ast | scripts/check-db-table.py | — | 신설 |  |
 | 633 | ast | scripts/check-context-isolation.py | — | 신설 |  |
 | 634 | ast | scripts/check-context-isolation.py | — | 신설 |  |
 | 635 | ast | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
 | 636 | ast | scripts/check-error-centralization.py | — | 신설 |  |
 | 637 | ast | scripts/check-test-config.py | — | 신설 | 08-25 tarot 잔존 판정 5 — migration 전용 테스트 절대 금지(기존 포함) |
 | 638 | path | scripts/check-layer-skeleton.py | — | 신설 | 09-01 동명 폴더 승격 — 본체 부재 위장 |
 | 639 | path | scripts/check-layer-skeleton.py | — | 신설 | 09-01 동명 폴더 승격 — 형제 공존 |
 | 640 | ast | scripts/check-layer-skeleton.py | — | 신설 | 09-01 동명 폴더 승격 — __init__ 재수출 전용·정크드로어 |
 | 641 | path | scripts/check-layer-skeleton.py | — | 신설 | 09-01 동명 폴더 승격 — 1단 평평 |
-| 642 | ast | scripts/check-layer-skeleton.py | — | 신설 | 09-01 동명 폴더 승격 — 부품 출생 50행 하한 |
 | 643 | path | scripts/check-layer-skeleton.py | — | 신설 | 09-01 동명 폴더 승격 — 부품 0개 퇴화 |
 | 644 | ast+ | scripts/check-layer-skeleton.py | agents/discipline-reviewer.md | 신설 | 09-01 동명 폴더 승격 — ⓓ 캐스케이드 후보 신호 |
-| 645 | ast+ | scripts/check-public-surface-annotation.py | agents/discipline-reviewer.md | 신설 | 09-04 현장 보고 E — 명시 `Any` 정책(시그니처 bare = 위반 · 제네릭 안·변수 = ⓓ 후보) |
+| 645 | ast+ | scripts/check-public-surface-annotation.py | agents/discipline-reviewer.md | 신설 | 09-04 현장 보고 E — 명시 `Any` 정책(시그니처 bare = 위반 · 제네릭 안·변수 = ⓓ 후보)admin 허용은 확인된 Django/Parler framework 슬롯과 연결된 private 전달 helper의 열린 UI context 조립·병합·전달에 한한다. 업무 읽기·비교·계산·상태 변경 또는 업무 함수로 값 전달부터 기존 규칙을 적용한다. 출처나 소비가 미해소이면 후보로 흐름을 묻는다. framework 고정 kwargs 밖 bare Any·별도 업무 dict·admin 경로 전체는 면제하지 않는다. #493·#646·#650은 유지한다. |
 | 646 | ast+ | scripts/check-public-surface-annotation.py | agents/discipline-reviewer.md | 신설 | 09-04 현장 보고 3 S-1 — django-stubs 제네릭 기저(맨몸·`type: ignore[type-arg]` 위반 · code 없는 ignore·런타임 subscript ⓓ 후보) |
-| 647 | ast+ | scripts/check-public-surface-annotation.py | agents/discipline-reviewer.md | 신설 | 09-04 현장 보고 3 S-4 — 딕셔너리-레코드(`dict/Mapping` 값 `Any` 전 자리·`object` 반환/속성 위반 · 입구 `object`·반환 자리표시 ⓓ 후보) |
+| 647 | ast+ | scripts/check-public-surface-annotation.py | agents/discipline-reviewer.md | 신설 | 09-04 현장 보고 3 S-4 — 딕셔너리-레코드(`dict/Mapping` 값 `Any` 전 자리·`object` 반환/속성 위반 · 입구 `object`·반환 자리표시 ⓓ 후보)admin 허용은 확인된 Django/Parler framework 슬롯과 연결된 private 전달 helper의 열린 UI context 조립·병합·전달에 한한다. 업무 읽기·비교·계산·상태 변경 또는 업무 함수로 값 전달부터 기존 규칙을 적용한다. 출처나 소비가 미해소이면 후보로 흐름을 묻는다. framework 고정 kwargs 밖 bare Any·별도 업무 dict·admin 경로 전체는 면제하지 않는다. #493·#646·#650은 유지한다. |
 | 648 | ast | scripts/check-api-error-controller-contract.py | — | 신설 | 09-04 현장 보고 3 S-5 — 반환 주석 `Status` 상자 하나(표준 트리 슬라이스 · 프로필 무관) |
 | 649 | ast | scripts/check-api-error-controller-contract.py | — | 신설 | 09-04 현장 보고 3 S-5 — `Schema`+`RootModel` 동시 상속 금지(표준 트리 슬라이스) |
 | 650 | ast+ | scripts/check-public-surface-annotation.py | agents/discipline-reviewer.md | 신설 | 09-04 현장 보고 3 S-4 — `json.load(s)` 무검증 흐름 ⓓ 전용(확정 위반은 #647) |
 | 651 | ast | scripts/check-port-adapter-pairing.py | — | 신설 | 09-09 어댑터 고정 역할의 클래스별 파일·상수 묶음 |

```

## docs/file_tree.html

Before SHA256: c9ca32c587d73cfd1a23ca48de4073ce120188feebd1dfcd9fe2a80cdb376b17
After SHA256: 62cefa2c055b9a02653f52c2fd5fc9e2615a0b8a02faba7602d82590bd314fe0

```diff
--- before/docs/file_tree.html
+++ after/docs/file_tree.html
@@ -3286,29 +3286,29 @@
       })();
       </script>
     </div>
   </div>
 
   <aside class="note settled" id="adapter-layout" style="max-width:none">
     <span class="lbl">어댑터 고정 골격 — 다섯 역할 폴더</span>
     <p>ACL의 <code>&lt;other_bounded_context&gt;/&lt;capability&gt;_adapter/</code>, 외부 시스템의 <code>&lt;system&gt;/&lt;capability&gt;_adapter/</code>, 그 밖 능력의 <code>&lt;capability&gt;/&lt;technology&gt;_adapter/</code> 에 같은 골격을 강제한다.</p>
     <p><b><code>adapter/</code> · <code>command/</code> · <code>constant/</code> · <code>contract/</code> · <code>schema/</code> 는 내용이 없어도 모두 만든다.</b> 바깥 패키지와 다섯 폴더에 <code>__init__.py</code> 를 둔다. 초기화 파일은 재수출 전용이고 실제 내용 파일은 필요할 때 만든다.</p>
     <p>구현·호출 계약·내부 계약·검증 스키마는 <b>클래스마다 파일 하나</b>다. 여러 구현이나 Protocol 도 해당 역할 폴더에 각각 둔다. 프롬프트 상수는 <code>constant/prompt.py</code> 처럼 관련 값끼리 묶는다. 계약을 만드는 builder 는 그 계약 클래스 파일에, 스키마 별칭은 관련 스키마 파일에 둔다. 외부 응답을 포트 반환값으로 바꾸는 reader 는 어댑터 구현에 둔다.</p>
-    <p>이 세 칸은 처음부터 고정 패키지다. 50행 최소치·200행 감사 신호·본체 파일을 요구하는 아래 승격 규칙의 대상이 아니다.</p>
+    <p>이 세 칸은 처음부터 고정 패키지다. 200행 감사 신호·본체 파일을 요구하는 아래 승격 규칙의 대상이 아니다.</p>
   </aside>
 
   <aside class="note settled" id="promotion" style="max-width:none">
     <span class="lbl">⇄ 파일 칸의 동명 폴더 승격 — 13개 허용 칸</span>
     <p><b>기본은 <code>&lt;이름&gt;.py</code>, 승격은 <code>&lt;이름&gt;/</code> 다.</b> 허용 행은 12·14·15·18·20·21·24·41·61·74·92·94·96다.
     승격 폴더 안에 본체 <code>&lt;이름&gt;.py</code>, 재수출 전용 <code>__init__.py</code>, 감사에서 열거한 부품을 둔다. 형제 파일·폴더 공존, 본체 없는 폴더, 내부 하위 폴더는 허용하지 않는다.</p>
     <p><b>① 기존 칸으로 이동 → ② 동명 폴더 승격 → ③ 유지</b> 순서로 소관과 응집을 판정한다. 다른 기존 칸이 받을 수 있으면 먼저 이동하고, 어느 칸의 소관도 아닌 역할 밖 응집 단위가 생긴 경우에만 승격한다.
-    <b>200행 초과는 감사 신호이고 자동 분할 기준이 아니다.</b> 새 승격 부품은 각 50행 이상(물리 행·빈 줄 제외)이어야 한다. 본체·<code>__init__.py</code> 만 남은 승격 폴더는 환원 신호다.</p>
+    <b>200행 초과는 감사 신호이고 자동 분할 기준이 아니다.</b> 승격은 소관·응집으로 판정하며 부품 행수 하한은 없다. 본체·<code>__init__.py</code> 만 남은 승격 폴더는 환원 신호다.</p>
     <p><b>감사자가 판정하고 coder 가 집행한다.</b> coder 의 기본 작성형은 파일이다. 크기만으로 분할하거나 예비 패키지를 미리 만들지 않는다. 부품도 다른 유스케이스의 공용 helper 로 쓸 수 없고 저장(save)류 호출은 본체에 둔다.</p>
     <p>바깥 import 경로·공개 이름을 유지하고 <code>git mv</code> 로 이력을 보존한다. 재수출은 redundant alias 또는 <code>__all__</code>, 내부 참조는 모듈 직접 상대 import 로 쓴다.
     실행 전 모듈 객체·monkeypatch·<code>patch("pkg.mod.attr")</code>·설정 문자열·동적 import 참조를 전수 확인한다. 필요한 수정이 승인 범위 밖이면 먼저 보고한다.
     상세 판정과 기존 폴더의 처리 경로는 <a href="../dddjango/skills/discipline-houserules/SKILL.md">동명 폴더 승격 캐스케이드</a>를 따른다.</p>
   </aside>
 
   <div class="duo" style="margin-top:20px">
     <aside class="note settled" style="max-width:none">
       <span class="lbl">구역 배정 — 어느 칸이 어느 계보의 말을 쓰나</span>
       <p><code>domain_layer/</code> → <b>DDD</b> · <code>application_layer/</code> → <b>클린</b> · <code>driving_layer/</code>·<code>driven_layer/</code> → <b>헥사고날</b>.</p>

```

## docs/mkrev2.py

Before SHA256: 049fcc6a03289f1321d53a6192740a0cb4c43529f8b1dd7f0244b37b3ace7c4d
After SHA256: 6192fe66215f6f38f87b279cfc9282adb30bb5c2c31716a82cfa492b6848491d

```diff
--- before/docs/mkrev2.py
+++ after/docs/mkrev2.py
@@ -6669,29 +6669,29 @@
       })();
       </script>
     </div>
   </div>
 
   <aside class="note settled" id="adapter-layout" style="max-width:none">
     <span class="lbl">어댑터 고정 골격 — 다섯 역할 폴더</span>
     <p>ACL의 <code>&lt;other_bounded_context&gt;/&lt;capability&gt;_adapter/</code>, 외부 시스템의 <code>&lt;system&gt;/&lt;capability&gt;_adapter/</code>, 그 밖 능력의 <code>&lt;capability&gt;/&lt;technology&gt;_adapter/</code> 에 같은 골격을 강제한다.</p>
     <p><b><code>adapter/</code> · <code>command/</code> · <code>constant/</code> · <code>contract/</code> · <code>schema/</code> 는 내용이 없어도 모두 만든다.</b> 바깥 패키지와 다섯 폴더에 <code>__init__.py</code> 를 둔다. 초기화 파일은 재수출 전용이고 실제 내용 파일은 필요할 때 만든다.</p>
     <p>구현·호출 계약·내부 계약·검증 스키마는 <b>클래스마다 파일 하나</b>다. 여러 구현이나 Protocol 도 해당 역할 폴더에 각각 둔다. 프롬프트 상수는 <code>constant/prompt.py</code> 처럼 관련 값끼리 묶는다. 계약을 만드는 builder 는 그 계약 클래스 파일에, 스키마 별칭은 관련 스키마 파일에 둔다. 외부 응답을 포트 반환값으로 바꾸는 reader 는 어댑터 구현에 둔다.</p>
-    <p>이 세 칸은 처음부터 고정 패키지다. 50행 최소치·200행 감사 신호·본체 파일을 요구하는 아래 승격 규칙의 대상이 아니다.</p>
+    <p>이 세 칸은 처음부터 고정 패키지다. 200행 감사 신호·본체 파일을 요구하는 아래 승격 규칙의 대상이 아니다.</p>
   </aside>
 
   <aside class="note settled" id="promotion" style="max-width:none">
     <span class="lbl">⇄ 파일 칸의 동명 폴더 승격 — 13개 허용 칸</span>
     <p><b>기본은 <code>&lt;이름&gt;.py</code>, 승격은 <code>&lt;이름&gt;/</code> 다.</b> 허용 행은 12·14·15·18·20·21·24·41·61·74·92·94·96다.
     승격 폴더 안에 본체 <code>&lt;이름&gt;.py</code>, 재수출 전용 <code>__init__.py</code>, 감사에서 열거한 부품을 둔다. 형제 파일·폴더 공존, 본체 없는 폴더, 내부 하위 폴더는 허용하지 않는다.</p>
     <p><b>① 기존 칸으로 이동 → ② 동명 폴더 승격 → ③ 유지</b> 순서로 소관과 응집을 판정한다. 다른 기존 칸이 받을 수 있으면 먼저 이동하고, 어느 칸의 소관도 아닌 역할 밖 응집 단위가 생긴 경우에만 승격한다.
-    <b>200행 초과는 감사 신호이고 자동 분할 기준이 아니다.</b> 새 승격 부품은 각 50행 이상(물리 행·빈 줄 제외)이어야 한다. 본체·<code>__init__.py</code> 만 남은 승격 폴더는 환원 신호다.</p>
+    <b>200행 초과는 감사 신호이고 자동 분할 기준이 아니다.</b> 승격은 소관·응집으로 판정하며 부품 행수 하한은 없다. 본체·<code>__init__.py</code> 만 남은 승격 폴더는 환원 신호다.</p>
     <p><b>감사자가 판정하고 coder 가 집행한다.</b> coder 의 기본 작성형은 파일이다. 크기만으로 분할하거나 예비 패키지를 미리 만들지 않는다. 부품도 다른 유스케이스의 공용 helper 로 쓸 수 없고 저장(save)류 호출은 본체에 둔다.</p>
     <p>바깥 import 경로·공개 이름을 유지하고 <code>git mv</code> 로 이력을 보존한다. 재수출은 redundant alias 또는 <code>__all__</code>, 내부 참조는 모듈 직접 상대 import 로 쓴다.
     실행 전 모듈 객체·monkeypatch·<code>patch("pkg.mod.attr")</code>·설정 문자열·동적 import 참조를 전수 확인한다. 필요한 수정이 승인 범위 밖이면 먼저 보고한다.
     상세 판정과 기존 폴더의 처리 경로는 <a href="../dddjango/skills/discipline-houserules/SKILL.md">동명 폴더 승격 캐스케이드</a>를 따른다.</p>
   </aside>
 
   <div class="duo" style="margin-top:20px">
     <aside class="note settled" style="max-width:none">
       <span class="lbl">구역 배정 — 어느 칸이 어느 계보의 말을 쓰나</span>
       <p><code>domain_layer/</code> → <b>DDD</b> · <code>application_layer/</code> → <b>클린</b> · <code>driving_layer/</code>·<code>driven_layer/</code> → <b>헥사고날</b>.</p>

```

## ontology/LEDGER.tsv

Before SHA256: 7459b5d6779531bf22a153eff20b1d0fba9e2a360cae7cb90b4e8df028cd1fcf
After SHA256: 6697fe96cd028983be6c78125107a0af8ac74870626c0eb18b06dfa54bfcbf82

```diff
--- before/ontology/LEDGER.tsv
+++ after/ontology/LEDGER.tsv
@@ -1616,10 +1616,21 @@
 discipline-houserules-final	s011-3	e16a01d3665ba1478585708b2a3109b7da72193d737a7353be8b3a5ebaeaba49	graph	-	-	-	-	rebaseline:2026-09-09 사용자 승인 어댑터 고정 역할 골격·클래스별 파일·170행 트리 및 배치/감수 포인터 반영(R-3468·R-3469)
 discipline-houserules-final	s018-5	2bfb014acd8678e8ee297d28f586481e632f66b7ae34ee5feb1acc6fc3e271a3	graph	-	-	-	-	rebaseline:2026-09-09 사용자 승인 어댑터 고정 역할 골격·클래스별 파일·170행 트리 및 배치/감수 포인터 반영(R-3468·R-3469)
 discipline-houserules-skill	s001	b9abaf0f652433c1b2802530ad52e5acc821ef50365916ce3b3bd27c7e084311	graph	-	-	-	-	rebaseline:2026-09-09 사용자 승인 어댑터 고정 역할 골격·클래스별 파일·170행 트리 및 배치/감수 포인터 반영(R-3468·R-3469)
 discipline-houserules-skill	s004-1	df111cd3187a211e3bce3ea8111c2d88534697e30b2520badfcd5f7d2fab17b4	graph	-	-	-	-	rebaseline:2026-09-09 사용자 승인 어댑터 고정 역할 골격·클래스별 파일·170행 트리 및 배치/감수 포인터 반영(R-3468·R-3469)
 agent-design-architect	s005	6377a97df67c27bbb393c4daca89392da0844eafc795e804beb04d309a402ce9	graph	-	-	-	-	rebaseline:2026-09-10 pre-gate 전사 수리 — R-3425 rev3 빈 부모 정리 · R-3426 rev4 decorator/TYPE_CHECKING alias 명시 전사
 command-dddjango	s003	8354295f89f632aad21c24dc55d2d55d2f7556de5749ef03f4db32ee4473eb34	graph	-	-	-	-	rebaseline:2026-09-10 field-report-4 — 무응답 결정 금지/현재 삭제 정책/OHS 신규 함수 및 artifact 주소 전사 안내
 command-dddjango	s011	2eebd2edcb47d8c727d254407efe5581e0ae3111e1f138881caf4a49984cb722	graph	ccaa3b536a63ce6d4ae457e623ba329e639f66063a287aa6664292744dc524cf	6	15	pending	rebaseline:2026-09-10 field-report-4 — 무응답 결정 금지/현재 삭제 정책/OHS 신규 함수 및 artifact 주소 전사 안내
 architecture-ddd-final	s017-3.2	73a2ad110ec8962a809dede99ab4961187f034a2e184f97271fcc9c32f5956b5	graph	f72075797a2748ed7e8440284b5062f8f45b77e10b75fd1ea26988afe7813f92	9	20	ceb3c6a	rebaseline:2026-09-10 field-report-4 — 무응답 결정 금지/현재 삭제 정책/OHS 신규 함수 및 artifact 주소 전사 안내
 agent-design-architect	s005	70ccdb4c222061e4b0c2eb250f7e08dc98f1269a088b4161e44236d428990304	graph	-	-	-	-	rebaseline:2026-09-10 field-report-4 — 무응답 결정 금지/현재 삭제 정책/OHS 신규 함수 및 artifact 주소 전사 안내
 architecture-ddd-final	s017-3.2	00364679eaf41bb6ce60ed31007f7d127d9413135cf6a4ff322d4e2d810a5b20	graph	f72075797a2748ed7e8440284b5062f8f45b77e10b75fd1ea26988afe7813f92	9	20	ceb3c6a	rebaseline:2026-09-10 F4-6 구현 리뷰 — hard delete 범위·현재 승인 guard 보존/종료 guard 복구 금지 명확화
+agent-design-architect	s005	273e582ab5bf506a12a5d02a373b7ae5f09a769d2fda6de7275a004b5f1f868e	graph	-	-	-	-	rebaseline:2026-09-11 Task6 approved field-report-4 followup — existing Work amendments; rendered graph baseline aligned, migrated provenance/owner/counts preserved
+agent-design-review-api	s006	c05d22c6bf514bb82cc894518be0e291f1362332f3518c52379f5f04baeb52c9	graph	-	-	-	-	rebaseline:2026-09-11 Task6 approved field-report-4 followup — existing Work amendments; rendered graph baseline aligned, migrated provenance/owner/counts preserved
+agent-discipline-reviewer	s007	afd8ca21c14cb27e2089e14a00cf7bf5c6fe0af4dbf8966c872c580847d1cb0d	graph	-	-	-	-	rebaseline:2026-09-11 Task6 approved field-report-4 followup — existing Work amendments; rendered graph baseline aligned, migrated provenance/owner/counts preserved
+command-dddjango	s006	288b3693a492dee2b39c07dfa3c330eb7832060c11175494ed37d3c61e012205	graph	-	-	-	-	rebaseline:2026-09-11 Task6 approved field-report-4 followup — existing Work amendments; rendered graph baseline aligned, migrated provenance/owner/counts preserved
+discipline-houserules-final	s003-0	337f2f48e8157c93be09c8431e909b638192d8eb9b4068a7f2ae6258f251722d	graph	-	-	-	-	rebaseline:2026-09-11 Task6 approved field-report-4 followup — existing Work amendments; rendered graph baseline aligned, migrated provenance/owner/counts preserved
+discipline-houserules-skill	s004-1	a1df8096b8c764514d96383c87200e93f8771f97f6bbccc6398a293d8b162331	graph	-	-	-	-	rebaseline:2026-09-11 Task6 approved field-report-4 followup — existing Work amendments; rendered graph baseline aligned, migrated provenance/owner/counts preserved
+discipline-houserules-skill	s007-4	40c1c8416963eaf8c72560627b272c8ccf2bd63dcf4d2fb7cbb215fc1f04e5df	graph	-	-	-	-	rebaseline:2026-09-11 Task6 approved field-report-4 followup — existing Work amendments; rendered graph baseline aligned, migrated provenance/owner/counts preserved
+implementation-django-ninja-final	s023-6.2	68ea52bea42066fd7d5d2f22e08f089fe392fba9d1af66d321935b70a8b0e70d	graph	-	-	-	-	rebaseline:2026-09-11 Task6 approved field-report-4 followup — existing Work amendments; rendered graph baseline aligned, migrated provenance/owner/counts preserved
+implementation-django-ninja-skill	s004	ffe4dcd624079791fb136eb456a4edc39ffb8994d879dba9ab895cca16555a2d	graph	-	-	-	-	rebaseline:2026-09-11 Task6 approved field-report-4 followup — existing Work amendments; rendered graph baseline aligned, migrated provenance/owner/counts preserved
+discipline-houserules-final	s003-0	337f2f48e8157c93be09c8431e909b638192d8eb9b4068a7f2ae6258f251722d	graph	1b4fddca027005fc52618807bbbea8b088d5b77b141c29d404a09dd9747ae5f1	-	-	-	source-address:2026-09-11 Task6 verified unique pre-Task6 preserved workspace source span; previous migrated field absent (-); records preserved source address, not an asserted original migration date; current baseline/owner/counts unchanged
+implementation-django-ninja-final	s023-6.2	68ea52bea42066fd7d5d2f22e08f089fe392fba9d1af66d321935b70a8b0e70d	graph	11b862b4cbcab5bf329b7fa3939e97c6813446543bbb1604ebd2f60b4ad2eba2	-	-	-	source-address:2026-09-11 Task6 verified unique pre-Task6 preserved workspace source span; previous migrated field absent (-); records preserved source address, not an asserted original migration date; current baseline/owner/counts unchanged

```

## ontology/ISSUED

Before SHA256: 5d173e6db330ef3805629c3e6027dd061988e265dc573011a6208234eb4ab226
After SHA256: 5d173e6db330ef3805629c3e6027dd061988e265dc573011a6208234eb4ab226

```diff

```

## dddjango/scripts/rulepack.json

Before SHA256: 9c95472d5db364c416095120c4976013fbbab79a2aa197331255a1b48a191fbe
After SHA256: eca32486b4c7f9eda77e58c86e8b6a690289d80990037d714bb65088e477bb55

```diff
--- before/dddjango/scripts/rulepack.json
+++ after/dddjango/scripts/rulepack.json
@@ -4,37 +4,37 @@
     {
       "path": "ontology/rules/agent-acceptance-tester.ttl",
       "sha256": "a286502c3b54796dd2f7c4e4e9bade93754604dcc84be912b3d4d59a7298421d"
     },
     {
       "path": "ontology/rules/agent-coder.ttl",
       "sha256": "e31a4e3302bd81baf6e691f67c3fe61cfc7b58f68c8df9d8c63ac8a2dce351a3"
     },
     {
       "path": "ontology/rules/agent-design-architect.ttl",
-      "sha256": "a0a57735092853071940be471e086fff1777772651f8e7f706355f45b2e57a3e"
+      "sha256": "9865c8f5787809d3e0cd6e5cdcb119b859d20615a524d7fde1322330a4213f0a"
     },
     {
       "path": "ontology/rules/agent-design-review-api.ttl",
-      "sha256": "e83632a251018273422a9ed07d2471b824d1715e57b7c947e400020988aba101"
+      "sha256": "59106ddea0462475988cbcfdd1839f06c5d1a6ef8f72e6a4730ee5f275a32ba7"
     },
     {
       "path": "ontology/rules/agent-design-review-db.ttl",
       "sha256": "bddf495d1b4a38e95b8c9889fc94c2d7ff1b0187d03f98059af5549e307a6a2a"
     },
     {
       "path": "ontology/rules/agent-design-review-ddd.ttl",
       "sha256": "b7ebef6bf026863ae56694bd7177b1db9d55a55706c1dc218b2c88e17fb8d2e4"
     },
     {
       "path": "ontology/rules/agent-discipline-reviewer.ttl",
-      "sha256": "467e1e64963162052b340ea6e0e56e07eeb7d0d524fa1fc700282b32a7ec06fa"
+      "sha256": "f95d45237c92e1ea22f799327de15b88b08677c6a20f371769b42e0b0ad4479b"
     },
     {
       "path": "ontology/rules/architecture-api-final.ttl",
       "sha256": "295e5d4b6b4528265d4a20cf458c229a82101dc7c7b9e5f8c015bb81cce083be"
     },
     {
       "path": "ontology/rules/architecture-api-skill.ttl",
       "sha256": "b1bfe23e95d1ea361a52ef54c67166e8fa80b41d0437d47dede71dfea324f21d"
     },
     {
@@ -48,57 +48,57 @@
     {
       "path": "ontology/rules/architecture-ddd-final.ttl",
       "sha256": "3e7f49940592d370e0ee88147b21f8cf5a50d0520f71a5506ea50a8ebf9ea2df"
     },
     {
       "path": "ontology/rules/architecture-ddd-skill.ttl",
       "sha256": "b19060041be312fdd0c19e2030957abae7214e9e0e5892c030bf9044529fcadd"
     },
     {
       "path": "ontology/rules/command-dddjango.ttl",
-      "sha256": "9a7b9cd2220f255a2168d5ef3a69db43c0fedc103407a8b23e1d19ad9ce65e62"
+      "sha256": "454d396ab85aa5fa52b7c6172f197abc9605afd99e96691f3d93661ec6ee1f27"
     },
     {
       "path": "ontology/rules/discipline-cleancode-final.ttl",
       "sha256": "4d7d42c43f0df94188f5d73cdcfe2dadd17899434aad4c3715d35337610f455c"
     },
     {
       "path": "ontology/rules/discipline-cleancode-skill.ttl",
       "sha256": "fe14a2f3b6380340388568d403f2b1dbbfeb6c1ab8de14d646e2ec8a6162a127"
     },
     {
       "path": "ontology/rules/discipline-houserules-final.ttl",
-      "sha256": "d9541bba84466676267f3c0f2c6d05f54a7ed97e04501f9863da6820ea183d40"
+      "sha256": "bb03b9469a1fcef876db4f1c31287c0c34cea9585aeeda45cea886268835306a"
     },
     {
       "path": "ontology/rules/discipline-houserules-skill.ttl",
-      "sha256": "6e3374ffec14a4cce4869a9072b10da58da4419ef89f2c35e6506e650816449e"
+      "sha256": "9f05cfd377fd819ac9e7abed29aee1283e9c5d9afa9144a7e6a58ca5c43f8a6a"
     },
     {
       "path": "ontology/rules/discipline-tdd-final.ttl",
       "sha256": "27b5a5ab5ce515c3870e875b4e50c022fb36582338ca6f682f4a8022a333ba2c"
     },
     {
       "path": "ontology/rules/discipline-tdd-skill.ttl",
       "sha256": "40fc102a525fd0302bd441034244d82610629fcb57d7c9775645e25846bd2484"
     },
     {
       "path": "ontology/rules/implementation-django-final.ttl",
       "sha256": "e3874e731465c1fcae9ecfded93398e02e0765bea9d1707df3346d6ac74aa57d"
     },
     {
       "path": "ontology/rules/implementation-django-ninja-final.ttl",
-      "sha256": "e24b78dd3aab0a147d3458a3872d96c853f621395057a422860ac3ec5b0ddfce"
+      "sha256": "b184ade4fccfa20554614d3460e2841ea800eb731ce54553d1f4adbf9d1339a9"
     },
     {
       "path": "ontology/rules/implementation-django-ninja-skill.ttl",
-      "sha256": "369af739aae344af378c4c53a14ea5858464a0a6f5c4d7c284097e29f3fee947"
+      "sha256": "85fcd3471eeb56cecb0d99509941f44ed651c52bb2dda76ac549c7a057d6130a"
     },
     {
       "path": "ontology/rules/implementation-django-skill.ttl",
       "sha256": "1bf460caa61502ce15e86057d467eced5706ba641969d342d4c52bcfe3c4204f"
     },
     {
       "path": "ontology/rules/implementation-django-web-final.ttl",
       "sha256": "00a18a24100b44db806e6c1c0a1c1c5e937a48aab70d72129044a755e698061f"
     },
     {
@@ -8898,22 +8898,22 @@
     },
     "R-0084": {
       "agents": [
         "command-dddjango"
       ],
       "aliases": [],
       "block": "dddjango/skills/implementation-django-ninja/references/final.md/s023-6.2/b33",
       "block_order": 33,
       "checkers": [],
       "document": "dddjango/skills/implementation-django-ninja/references/final.md",
-      "expression": "https://numchida.com/ns/djr#R-0084@2026-08-19",
-      "label": "G1 승인 시에만 infra/ACL 정규화 후 구체 exception 직접 흐름",
+      "expression": "https://numchida.com/ns/djr#R-0084@2026-09-11",
+      "label": "인프라 내부 계약 정규화와 공개 오류 승인 분리",
       "order_rank": 2682,
       "section": "dddjango/skills/implementation-django-ninja/references/final.md/s023-6.2",
       "section_number": "6.2"
     },
     "R-0085": {
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/skills/implementation-django-ninja/references/final.md/s023-6.2/b33",
@@ -23594,22 +23594,22 @@
     },
     "R-1037": {
       "agents": [
         "command-dddjango"
       ],
       "aliases": [],
       "block": "dddjango/agents/discipline-reviewer.md/s007/b23",
       "block_order": 23,
       "checkers": [],
       "document": "dddjango/agents/discipline-reviewer.md",
-      "expression": "https://numchida.com/ns/djr#R-1037@2026-08-22",
-      "label": "G1 명시 승인 시에만 owning infra/ACL의 정규화 후 controller 직접 흐름 mapping",
+      "expression": "https://numchida.com/ns/djr#R-1037@2026-09-11",
+      "label": "내부 실패 계약 정규화와 safe 500 공개 경계",
       "order_rank": 819,
       "section": "dddjango/agents/discipline-reviewer.md/s007",
       "section_number": null
     },
     "R-1038": {
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/agents/discipline-reviewer.md/s007/b23",
@@ -24133,22 +24133,22 @@
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/agents/discipline-reviewer.md/s007/b29",
       "block_order": 29,
       "checkers": [
         "check-api-error-controller-contract.py"
       ],
       "document": "dddjango/agents/discipline-reviewer.md",
-      "expression": "https://numchida.com/ns/djr#R-1071@2026-08-22",
-      "label": "raw DB/SDK/network unknown failure의 전수 집합 제외(safe framework 500 기본)",
+      "expression": "https://numchida.com/ns/djr#R-1071@2026-09-11",
+      "label": "ACL known failure 전수 번역과 일반 내부 계약·공개 500 분리",
       "order_rank": 853,
       "section": "dddjango/agents/discipline-reviewer.md/s007",
       "section_number": null
     },
     "R-1072": {
       "agents": [
         "command-dddjango"
       ],
       "aliases": [],
       "block": "dddjango/agents/discipline-reviewer.md/s007/b30",
@@ -24687,22 +24687,22 @@
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/agents/discipline-reviewer.md/s007/b46",
       "block_order": 46,
       "checkers": [
         "check-domain-model.py"
       ],
       "document": "dddjango/agents/discipline-reviewer.md",
-      "expression": "https://numchida.com/ns/djr#R-1104@2026-08-22",
-      "label": "ⓓ#268 타입 조합만으로 잘못된 값이 불가능한가(Q2)",
+      "expression": "https://numchida.com/ns/djr#R-1104@2026-09-11",
+      "label": "닫힌 Enum 검증 제외·open Enum Q2와 트랜잭션 영역 후보 검수",
       "order_rank": 886,
       "section": "dddjango/agents/discipline-reviewer.md/s007",
       "section_number": null
     },
     "R-1105": {
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/agents/discipline-reviewer.md/s007/b46",
@@ -24908,56 +24908,56 @@
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/agents/discipline-reviewer.md/s007/b51",
       "block_order": 51,
       "checkers": [
         "check-naming.py"
       ],
       "document": "dddjango/agents/discipline-reviewer.md",
-      "expression": "https://numchida.com/ns/djr#R-1117@2026-08-22",
-      "label": "ⓓ#343 운영 기능인가 장고 배선인가",
+      "expression": "https://numchida.com/ns/djr#R-1117@2026-09-11",
+      "label": "운영 기능/장고 배선·admin UI context 조립과 실제 소비 검수",
       "order_rank": 899,
       "section": "dddjango/agents/discipline-reviewer.md/s007",
       "section_number": null
     },
     "R-1118": {
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/agents/discipline-reviewer.md/s007/b51",
       "block_order": 51,
       "checkers": [
         "check-naming.py"
       ],
       "document": "dddjango/agents/discipline-reviewer.md",
-      "expression": "https://numchida.com/ns/djr#R-1118@2026-08-22",
-      "label": "ⓓ#589 조건이 업무 판정인가(Q2)",
+      "expression": "https://numchida.com/ns/djr#R-1118@2026-09-11",
+      "label": "표현 조건 업무 판정 Q2·admin context 출처/소비 미해소 후보",
       "order_rank": 900,
       "section": "dddjango/agents/discipline-reviewer.md/s007",
       "section_number": null
     },
     "R-1119": {
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/agents/discipline-reviewer.md/s007/b52",
       "block_order": 52,
       "checkers": [
         "check-port-adapter-pairing.py"
       ],
       "document": "dddjango/agents/discipline-reviewer.md",
-      "expression": "https://numchida.com/ns/djr#R-1119@2026-08-22",
-      "label": "ⓓ#227 자료를 원시값 인자로 펴서 넘길 수 있나",
+      "expression": "https://numchida.com/ns/djr#R-1119@2026-09-11",
+      "label": "포트/어댑터 판정과 vendor 오류 속성 출처 후보 검수",
       "order_rank": 901,
       "section": "dddjango/agents/discipline-reviewer.md/s007",
       "section_number": null
     },
     "R-1120": {
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/agents/discipline-reviewer.md/s007/b52",
@@ -32544,22 +32544,22 @@
         "agent-design-review-api",
         "command-dddjango"
       ],
       "aliases": [],
       "block": "dddjango/agents/design-architect.md/s005/b11",
       "block_order": 11,
       "checkers": [
         "check-transient-overmapping.py"
       ],
       "document": "dddjango/agents/design-architect.md",
-      "expression": "https://numchida.com/ns/djr#R-1617@2026-08-22",
-      "label": "slot 10 — raw infra failure 의 기본 500 과 승인된 public meaning 한정 정규화",
+      "expression": "https://numchida.com/ns/djr#R-1617@2026-09-11",
+      "label": "내부 실패 정규화와 공개 HTTP 계약 승인 분리",
       "order_rank": 273,
       "section": "dddjango/agents/design-architect.md/s005",
       "section_number": null
     },
     "R-1618": {
       "agents": [
         "agent-design-review-api",
         "command-dddjango"
       ],
       "aliases": [],
@@ -48969,22 +48969,22 @@
         "agent-design-review-api"
       ],
       "aliases": [],
       "block": "dddjango/agents/design-review-api.md/s006/b11",
       "block_order": 11,
       "checkers": [
         "check-api-error-controller-contract.py",
         "check-synthetic-infra-exc.py"
       ],
       "document": "dddjango/agents/design-review-api.md",
-      "expression": "https://numchida.com/ns/djr#R-2677@2026-08-22",
-      "label": "slot 10 — raw infra 기본 500·승인된 안정 public meaning만 consuming BC internal exception 정규화 후 ErrorSchema 생성 확인",
+      "expression": "https://numchida.com/ns/djr#R-2677@2026-09-11",
+      "label": "내부 실패 정규화와 공개 HTTP 계약 승인 분리 검수",
       "order_rank": 496,
       "section": "dddjango/agents/design-review-api.md/s006",
       "section_number": null
     },
     "R-2678": {
       "agents": [
         "agent-design-review-api"
       ],
       "aliases": [],
       "block": "dddjango/agents/design-review-api.md/s006/b11",
@@ -53059,22 +53059,22 @@
         "command-dddjango"
       ],
       "aliases": [],
       "block": "dddjango/skills/implementation-django-ninja/SKILL.md/s004/b10",
       "block_order": 10,
       "checkers": [
         "check-context-isolation.py",
         "check-synthetic-infra-exc.py"
       ],
       "document": "dddjango/skills/implementation-django-ninja/SKILL.md",
-      "expression": "https://numchida.com/ns/djr#R-2941@2026-08-22",
-      "label": "승인된 안정 의미 한정 infra/ACL 의 자기 BC exception 정규화",
+      "expression": "https://numchida.com/ns/djr#R-2941@2026-09-11",
+      "label": "인프라 내부 계약 번역과 공개 safe 500 유지",
       "order_rank": 2442,
       "section": "dddjango/skills/implementation-django-ninja/SKILL.md/s004",
       "section_number": null
     },
     "R-2942": {
       "agents": [],
       "aliases": [],
       "block": "dddjango/skills/implementation-django-ninja/SKILL.md/s004/b11",
       "block_order": 11,
       "checkers": [
@@ -60346,22 +60346,22 @@
     },
     "R-3410": {
       "agents": [],
       "aliases": [],
       "block": "dddjango/skills/discipline-houserules/references/final.md/s003-0/b10",
       "block_order": 10,
       "checkers": [
         "check-layer-skeleton.py"
       ],
       "document": "dddjango/skills/discipline-houserules/references/final.md",
-      "expression": "https://numchida.com/ns/djr#R-3410@2026-09-01",
-      "label": "부품 출생 50행 하한과 부품 0개 퇴화의 환원 신호",
+      "expression": "https://numchida.com/ns/djr#R-3410@2026-09-11",
+      "label": "부품 0 승격 폴더 환원 신호·신규 산출/기존 빚 처분",
       "order_rank": 2168,
       "section": "dddjango/skills/discipline-houserules/references/final.md/s003-0",
       "section_number": "0"
     },
     "R-3411": {
       "agents": [
         "agent-coder",
         "agent-discipline-reviewer"
       ],
       "aliases": [],
@@ -60456,22 +60456,22 @@
     "R-3417": {
       "agents": [
         "agent-coder",
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/skills/discipline-houserules/SKILL.md/s004-1/b7",
       "block_order": 7,
       "checkers": [],
       "document": "dddjango/skills/discipline-houserules/SKILL.md",
-      "expression": "https://numchida.com/ns/djr#R-3417@2026-09-01b",
-      "label": "캐스케이드 ② 동명 폴더 승격 — 역할 밖 응집 술어(상태 클래스/참조 폐쇄 클러스터)·개별 50행 하한·관례 동거 예외·부품은 형제 분할·집행 전 모듈 객체 참조처 조사(패치 표면)",
+      "expression": "https://numchida.com/ns/djr#R-3417@2026-09-11",
+      "label": "소관·응집으로 동명 폴더 승격·행수 하한 없이 참조 전수 조사",
       "order_rank": 2096,
       "section": "dddjango/skills/discipline-houserules/SKILL.md/s004-1",
       "section_number": "1"
     },
     "R-3418": {
       "agents": [
         "agent-coder",
         "agent-discipline-reviewer"
       ],
       "aliases": [],
@@ -60570,107 +60570,107 @@
       "agents": [
         "agent-design-architect"
       ],
       "aliases": [],
       "block": "dddjango/agents/design-architect.md/s005/b33",
       "block_order": 33,
       "checkers": [
         "design_pregate.py"
       ],
       "document": "dddjango/agents/design-architect.md",
-      "expression": "https://numchida.com/ns/djr#R-3424@2026-09-01",
-      "label": "설계 명세 기계가독 채널 상시 작성 — 산문 추론 0·부재 fail-closed 전사",
+      "expression": "https://numchida.com/ns/djr#R-3424@2026-09-11",
+      "label": "기계가독 다섯 채널과 선택 효과 — 무기재 의미·선언 검증·본문 미검증 분리",
       "order_rank": 406,
       "section": "dddjango/agents/design-architect.md/s005",
       "section_number": null
     },
     "R-3425": {
       "agents": [
         "agent-design-architect"
       ],
       "aliases": [],
       "block": "dddjango/agents/design-architect.md/s005/b34",
       "block_order": 34,
       "checkers": [
         "design_pregate.py"
       ],
       "document": "dddjango/agents/design-architect.md",
-      "expression": "https://numchida.com/ns/djr#R-3425@2026-09-10",
-      "label": "file-plan 정규 블록 — 1행 1경로·조치 태그·금지 표기·삽화↔블록 차분 · 태그의 뜻은 기준선 기준(add 부재·update 실존(승격 형태 예외)·비후행 remove 실존·재라벨 도피는 형식 red)",
+      "expression": "https://numchida.com/ns/djr#R-3425@2026-09-11",
+      "label": "file-plan 기준선 태그·제거와 실체화 0 선언 검증",
       "order_rank": 408,
       "section": "dddjango/agents/design-architect.md/s005",
       "section_number": null
     },
     "R-3426": {
       "agents": [
         "agent-design-architect"
       ],
       "aliases": [],
       "block": "dddjango/agents/design-architect.md/s005/b35",
       "block_order": 35,
       "checkers": [
         "design_pregate.py"
       ],
       "document": "dddjango/agents/design-architect.md",
-      "expression": "https://numchida.com/ns/djr#R-3426@2026-09-10b",
-      "label": "공개 심볼 전수 표기 — Base 닫힌 목록·베이스 유도표 공집합·값 축 유도 3행 등재(마이그레이션 칸 결손 보충)·`_`+대문자 사설 타입·필드 대입식 허용·수신자 관용 정규화·계약 필드·중첩 타입 소속 명시",
+      "expression": "https://numchida.com/ns/djr#R-3426@2026-09-11",
+      "label": "공개 심볼과 add/update 선언 후상태·본문 미검증 분리",
       "order_rank": 409,
       "section": "dddjango/agents/design-architect.md/s005",
       "section_number": null
     },
     "R-3427": {
       "agents": [
         "agent-design-architect"
       ],
       "aliases": [],
       "block": "dddjango/agents/design-architect.md/s005/b36",
       "block_order": 36,
       "checkers": [
         "design_pregate.py"
       ],
       "document": "dddjango/agents/design-architect.md",
-      "expression": "https://numchida.com/ns/djr#R-3427@2026-09-10",
-      "label": "경계 import 표 — 검사기 판정 관련 경계 import 전부(테스트 파일 포함) · 경계 3분류(BC 밖 · BC 내부 층 경계 중 검사기 판정 항목 — 잎→port 예외 import 도 행으로 · 그 밖 재량) · 3단 실존 판정 입력(이 브랜치 기준 · 행 삭제 = 채널 은폐 · 부재 update 는 형식 red 선행·승격 예외분만 ⑴)",
+      "expression": "https://numchida.com/ns/djr#R-3427@2026-09-11",
+      "label": "경계 import 실존·전사와 선언 출처 검증 분리",
       "order_rank": 410,
       "section": "dddjango/agents/design-architect.md/s005",
       "section_number": null
     },
     "R-3428": {
       "agents": [
         "agent-design-architect"
       ],
       "aliases": [],
       "block": "dddjango/agents/design-architect.md/s005/b37",
       "block_order": 37,
       "checkers": [
         "design_pregate.py"
       ],
       "document": "dddjango/agents/design-architect.md",
-      "expression": "https://numchida.com/ns/djr#R-3428@2026-09-10",
-      "label": "물리 신호 어노테이션 — markers/base/client 정형·무기재=물리 신호 없음",
+      "expression": "https://numchida.com/ns/djr#R-3428@2026-09-11",
+      "label": "물리 신호 — add 부재·update marker 현행 유지/최종 목록·미지원 S5",
       "order_rank": 411,
       "section": "dddjango/agents/design-architect.md/s005",
       "section_number": null
     },
     "R-3429": {
       "agents": [
         "agent-design-architect"
       ],
       "aliases": [],
       "block": "dddjango/agents/design-architect.md/s005/b37",
       "block_order": 37,
       "checkers": [
         "design_pregate.py"
       ],
       "document": "dddjango/agents/design-architect.md",
-      "expression": "https://numchida.com/ns/djr#R-3429@2026-09-01",
-      "label": "입장 표 header 영문 정본 6열 고정·셀 내 raw 파이프 금지",
+      "expression": "https://numchida.com/ns/djr#R-3429@2026-09-11",
+      "label": "입장 표 6열·첫 artifact add/update 결합·후속 주소 비전파",
       "order_rank": 412,
       "section": "dddjango/agents/design-architect.md/s005",
       "section_number": null
     },
     "R-3430": {
       "agents": [
         "agent-design-architect"
       ],
       "aliases": [],
       "block": "dddjango/agents/design-architect.md/s005/b38",
@@ -60689,97 +60689,97 @@
       "agents": [
         "agent-design-architect"
       ],
       "aliases": [],
       "block": "dddjango/agents/design-architect.md/s005/b33",
       "block_order": 33,
       "checkers": [
         "design_pregate.py"
       ],
       "document": "dddjango/agents/design-architect.md",
-      "expression": "https://numchida.com/ns/djr#R-3431@2026-09-01",
-      "label": "machine 마커 concrete 블록 한정 — 템플릿·예시 인용 부착 금지",
+      "expression": "https://numchida.com/ns/djr#R-3431@2026-09-11",
+      "label": "machine 마커 concrete 계획 한정·명시 효과와 admin 소비 범위",
       "order_rank": 407,
       "section": "dddjango/agents/design-architect.md/s005",
       "section_number": null
     },
     "R-3432": {
       "agents": [
         "command-dddjango"
       ],
       "aliases": [],
       "block": "dddjango/commands/dddjango.md/s006/b9",
       "block_order": 9,
       "checkers": [],
       "document": "dddjango/commands/dddjango.md",
-      "expression": "https://numchida.com/ns/djr#R-3432@2026-09-03b",
-      "label": "pre-gate 실행 의무 — design-spec 내용 변경마다·배너 직전 최종본·override 후 dispatch 전 무조건(캐시 skip·재발화·Phase 2 최신성 판형은 R-3445)",
+      "expression": "https://numchida.com/ns/djr#R-3432@2026-09-11",
+      "label": "pre-gate 실행 의무 — 명세 변경/배너 직전/dispatch 전 최종 예보·선언 포함",
       "order_rank": 1066,
       "section": "dddjango/commands/dddjango.md/s006",
       "section_number": null
     },
     "R-3433": {
       "agents": [
         "command-dddjango"
       ],
       "aliases": [],
       "block": "dddjango/commands/dddjango.md/s006/b9",
       "block_order": 9,
       "checkers": [],
       "document": "dddjango/commands/dddjango.md",
-      "expression": "https://numchida.com/ns/djr#R-3433@2026-09-03b",
-      "label": "차단 모드 red 처분 — red 반송 의무 · 배너 근거 --check-report exit 0 · 예외 = 귀속 red 전건 ignored(빚)|filtered · path 등급 filtered 불가",
+      "expression": "https://numchida.com/ns/djr#R-3433@2026-09-11",
+      "label": "pre-gate 귀속 및 선언 확정 red 전건 처분·후보/S1 비차단 분리",
       "order_rank": 1067,
       "section": "dddjango/commands/dddjango.md/s006",
       "section_number": null
     },
     "R-3434": {
       "agents": [
         "command-dddjango"
       ],
       "aliases": [],
       "block": "dddjango/commands/dddjango.md/s006/b9",
       "block_order": 9,
       "checkers": [],
       "document": "dddjango/commands/dddjango.md",
-      "expression": "https://numchida.com/ns/djr#R-3434@2026-09-03",
-      "label": "예보의 대체·축약 금지 — Phase 0 빚 스캔·G2 게이트 비대체·build_anchor 불간섭·HEAD 판형 유용 금지·계약 실존 채널의 G0 선행 조건·상류 머지 판단 비대체",
+      "expression": "https://numchida.com/ns/djr#R-3434@2026-09-11",
+      "label": "예보·선언·생성 S1의 Phase 0/G2/G0 실증 비대체·앵커 불간섭",
       "order_rank": 1068,
       "section": "dddjango/commands/dddjango.md/s006",
       "section_number": null
     },
     "R-3435": {
       "agents": [
         "command-dddjango"
       ],
       "aliases": [],
       "block": "dddjango/commands/dddjango.md/s006/b9",
       "block_order": 9,
       "checkers": [],
       "document": "dddjango/commands/dddjango.md",
-      "expression": "https://numchida.com/ns/djr#R-3435@2026-09-01",
-      "label": "팬텀 스텁 = 스크립트의 결정적 투영물(격리 사본 한정) — 구현 코드 직접 작성 금지 경계 비저촉",
+      "expression": "https://numchida.com/ns/djr#R-3435@2026-09-11",
+      "label": "격리 사본 결정적 투영물·명시 후상태와 기존 본문 미검증",
       "order_rank": 1069,
       "section": "dddjango/commands/dddjango.md/s006",
       "section_number": null
     },
     "R-3436": {
       "agents": [
         "command-dddjango"
       ],
       "aliases": [],
       "block": "dddjango/commands/dddjango.md/s006/b9",
       "block_order": 9,
       "checkers": [],
       "document": "dddjango/commands/dddjango.md",
-      "expression": "https://numchida.com/ns/djr#R-3436@2026-09-03b",
-      "label": "pre-gate machine 블록 부재·공허 skip 금지 — 부재·0행 = 형식 red(exit 3) · 구형 명세 포함(«캐시 skip»·«실체화 0 skip» 과 구별)",
+      "expression": "https://numchida.com/ns/djr#R-3436@2026-09-11",
+      "label": "machine 부재/공허 형식 red·실체화 0에서도 선언 검증",
       "order_rank": 1070,
       "section": "dddjango/commands/dddjango.md/s006",
       "section_number": null
     },
     "R-3437": {
       "agents": [
         "command-dddjango"
       ],
       "aliases": [],
       "block": "dddjango/commands/dddjango.md/s003/b10",
@@ -60899,22 +60899,22 @@
     },
     "R-3445": {
       "agents": [
         "command-dddjango"
       ],
       "aliases": [],
       "block": "dddjango/commands/dddjango.md/s006/b10",
       "block_order": 10,
       "checkers": [],
       "document": "dddjango/commands/dddjango.md",
-      "expression": "https://numchida.com/ns/djr#R-3445@2026-09-03",
-      "label": "pre-gate 캐시 skip·--base 재발화·Phase 2 최신성 — dispatch 전 재발화 · G2 전 --check-report exit 0 · 구형 명세·변경 0 레인 한정",
+      "expression": "https://numchida.com/ns/djr#R-3445@2026-09-11",
+      "label": "선택 effects 포함 캐시 해시·기존 무기재 해시 보존·재발화 최신성",
       "order_rank": 1071,
       "section": "dddjango/commands/dddjango.md/s006",
       "section_number": null
     },
     "R-3446": {
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/skills/implementation-python/references/final.md/s032-4.4/b3",
@@ -60931,39 +60931,39 @@
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/skills/discipline-houserules/SKILL.md/s007-4/b7",
       "block_order": 7,
       "checkers": [
         "check-public-surface-annotation.py"
       ],
       "document": "dddjango/skills/discipline-houserules/SKILL.md",
-      "expression": "https://numchida.com/ns/djr#R-3447@2026-09-04b",
-      "label": "Any 금지 — 시그니처(별표 인자 포함)·변수·클래스 속성·제네릭 인자 전부 · 프레임워크 오버라이드도 object/정확 타입 · 시그니처는 #645 차단·그 밖은 ⓓ 후보(#645) · dict/Mapping 값 자리 Any 는 #647 차단",
+      "expression": "https://numchida.com/ns/djr#R-3447@2026-09-11",
+      "label": "Any 기존 금지/후보와 확인된 framework admin 슬롯 제한 허용",
       "order_rank": 2120,
       "section": "dddjango/skills/discipline-houserules/SKILL.md/s007-4",
       "section_number": "4"
     },
     "R-3448": {
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/skills/discipline-houserules/SKILL.md/s007-4/b7",
       "block_order": 7,
       "checkers": [
         "check-public-surface-annotation.py"
       ],
       "document": "dddjango/skills/discipline-houserules/SKILL.md",
-      "expression": "https://numchida.com/ns/djr#R-3448@2026-09-04b",
-      "label": "경계 입력은 object/정확 타입으로 받아 받는 즉시 좁힘(TypeIs·isinstance·type() is · 자리는 architecture-ddd §3.1) · JSON 은 TypeAdapter(TypedDict) 검증 파싱 · object 는 입구 매개변수·즉시 검증 지역 변수만(반환/속성 누수 #647 차단 · 반환 자리표시 object·json.load 무검증 흐름은 ⓓ #647/#650 · 예외 프레임워크 콜백 미러·이벤트 컬렉션) · 면제 Form.clean·TypeIs",
+      "expression": "https://numchida.com/ns/djr#R-3448@2026-09-11",
+      "label": "경계 object 즉시 좁힘·JSON 검증 유지·admin UI context 실제 소비 경계",
       "order_rank": 2121,
       "section": "dddjango/skills/discipline-houserules/SKILL.md/s007-4",
       "section_number": "4"
     },
     "R-3449": {
       "agents": [
         "agent-design-review-ddd"
       ],
       "aliases": [],
       "block": "dddjango/skills/architecture-ddd/references/final.md/s023-3.6/b3",
@@ -60997,39 +60997,39 @@
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/skills/discipline-houserules/SKILL.md/s007-4/b8",
       "block_order": 8,
       "checkers": [
         "check-public-surface-annotation.py"
       ],
       "document": "dddjango/skills/discipline-houserules/SKILL.md",
-      "expression": "https://numchida.com/ns/djr#R-3451@2026-09-04",
-      "label": "레코드(키 고정 값 묶음)를 딕셔너리로 들고 다니지 않는다 — 내부 리터럴은 TypedDict · 파싱 JSON 은 TypeAdapter 검증 · 도메인 개념은 값 객체 · dict/Mapping[str, object|Any] 주석은 구조 미정 신호(#647)",
+      "expression": "https://numchida.com/ns/djr#R-3451@2026-09-11",
+      "label": "업무 레코드 구조 선언과 framework admin UI context 구분",
       "order_rank": 2122,
       "section": "dddjango/skills/discipline-houserules/SKILL.md/s007-4",
       "section_number": "4"
     },
     "R-3452": {
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/skills/discipline-houserules/SKILL.md/s007-4/b10",
       "block_order": 10,
       "checkers": [
         "check-public-surface-annotation.py"
       ],
       "document": "dddjango/skills/discipline-houserules/SKILL.md",
-      "expression": "https://numchida.com/ns/djr#R-3452@2026-09-04",
-      "label": "레코드(내부 리터럴) → TypedDict(종류 여럿이면 kind: Literal 판별 키 union) · dict/Mapping[str, object|Any] 금지",
+      "expression": "https://numchida.com/ns/djr#R-3452@2026-09-11",
+      "label": "업무 레코드 TypedDict와 admin context 조립 경계",
       "order_rank": 2123,
       "section": "dddjango/skills/discipline-houserules/SKILL.md/s007-4",
       "section_number": "4"
     },
     "R-3453": {
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/skills/discipline-houserules/SKILL.md/s007-4/b11",
@@ -61095,22 +61095,22 @@
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/skills/discipline-houserules/SKILL.md/s007-4/b15",
       "block_order": 15,
       "checkers": [
         "check-public-surface-annotation.py"
       ],
       "document": "dddjango/skills/discipline-houserules/SKILL.md",
-      "expression": "https://numchida.com/ns/djr#R-3457@2026-09-04",
-      "label": "타입이 이미 있는 값(반환·매개변수·속성) → 실제 클래스 · 입구 밖 자리표시 object 금지(입구 매개변수·즉시 검증 지역 변수는 R-3448 · 반환 주석 object 는 ⓓ #647)",
+      "expression": "https://numchida.com/ns/djr#R-3457@2026-09-11",
+      "label": "실제 타입 사용과 admin framework 슬롯 구분",
       "order_rank": 2128,
       "section": "dddjango/skills/discipline-houserules/SKILL.md/s007-4",
       "section_number": "4"
     },
     "R-3458": {
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/skills/discipline-houserules/SKILL.md/s007-4/b16",
@@ -61272,22 +61272,22 @@
     },
     "R-3468": {
       "agents": [],
       "aliases": [],
       "block": "dddjango/skills/discipline-houserules/references/final.md/s003-0/b12",
       "block_order": 12,
       "checkers": [
         "check-port-adapter-pairing.py"
       ],
       "document": "dddjango/skills/discipline-houserules/references/final.md",
-      "expression": "https://numchida.com/ns/djr#R-3468@2026-09-09",
-      "label": "#651 — 어댑터 고정 역할의 클래스별 파일과 상수 묶음",
+      "expression": "https://numchida.com/ns/djr#R-3468@2026-09-11",
+      "label": "어댑터 고정 역할 골격과 승격 신호 비적용",
       "order_rank": 2173,
       "section": "dddjango/skills/discipline-houserules/references/final.md/s003-0",
       "section_number": "0"
     },
     "R-3469": {
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/skills/discipline-houserules/references/final.md/s003-0/b12",

```

## codex-dddjango/skills/dddjango/scripts/rulepack.json

Before SHA256: 9c95472d5db364c416095120c4976013fbbab79a2aa197331255a1b48a191fbe
After SHA256: eca32486b4c7f9eda77e58c86e8b6a690289d80990037d714bb65088e477bb55

```diff
--- before/codex-dddjango/skills/dddjango/scripts/rulepack.json
+++ after/codex-dddjango/skills/dddjango/scripts/rulepack.json
@@ -4,37 +4,37 @@
     {
       "path": "ontology/rules/agent-acceptance-tester.ttl",
       "sha256": "a286502c3b54796dd2f7c4e4e9bade93754604dcc84be912b3d4d59a7298421d"
     },
     {
       "path": "ontology/rules/agent-coder.ttl",
       "sha256": "e31a4e3302bd81baf6e691f67c3fe61cfc7b58f68c8df9d8c63ac8a2dce351a3"
     },
     {
       "path": "ontology/rules/agent-design-architect.ttl",
-      "sha256": "a0a57735092853071940be471e086fff1777772651f8e7f706355f45b2e57a3e"
+      "sha256": "9865c8f5787809d3e0cd6e5cdcb119b859d20615a524d7fde1322330a4213f0a"
     },
     {
       "path": "ontology/rules/agent-design-review-api.ttl",
-      "sha256": "e83632a251018273422a9ed07d2471b824d1715e57b7c947e400020988aba101"
+      "sha256": "59106ddea0462475988cbcfdd1839f06c5d1a6ef8f72e6a4730ee5f275a32ba7"
     },
     {
       "path": "ontology/rules/agent-design-review-db.ttl",
       "sha256": "bddf495d1b4a38e95b8c9889fc94c2d7ff1b0187d03f98059af5549e307a6a2a"
     },
     {
       "path": "ontology/rules/agent-design-review-ddd.ttl",
       "sha256": "b7ebef6bf026863ae56694bd7177b1db9d55a55706c1dc218b2c88e17fb8d2e4"
     },
     {
       "path": "ontology/rules/agent-discipline-reviewer.ttl",
-      "sha256": "467e1e64963162052b340ea6e0e56e07eeb7d0d524fa1fc700282b32a7ec06fa"
+      "sha256": "f95d45237c92e1ea22f799327de15b88b08677c6a20f371769b42e0b0ad4479b"
     },
     {
       "path": "ontology/rules/architecture-api-final.ttl",
       "sha256": "295e5d4b6b4528265d4a20cf458c229a82101dc7c7b9e5f8c015bb81cce083be"
     },
     {
       "path": "ontology/rules/architecture-api-skill.ttl",
       "sha256": "b1bfe23e95d1ea361a52ef54c67166e8fa80b41d0437d47dede71dfea324f21d"
     },
     {
@@ -48,57 +48,57 @@
     {
       "path": "ontology/rules/architecture-ddd-final.ttl",
       "sha256": "3e7f49940592d370e0ee88147b21f8cf5a50d0520f71a5506ea50a8ebf9ea2df"
     },
     {
       "path": "ontology/rules/architecture-ddd-skill.ttl",
       "sha256": "b19060041be312fdd0c19e2030957abae7214e9e0e5892c030bf9044529fcadd"
     },
     {
       "path": "ontology/rules/command-dddjango.ttl",
-      "sha256": "9a7b9cd2220f255a2168d5ef3a69db43c0fedc103407a8b23e1d19ad9ce65e62"
+      "sha256": "454d396ab85aa5fa52b7c6172f197abc9605afd99e96691f3d93661ec6ee1f27"
     },
     {
       "path": "ontology/rules/discipline-cleancode-final.ttl",
       "sha256": "4d7d42c43f0df94188f5d73cdcfe2dadd17899434aad4c3715d35337610f455c"
     },
     {
       "path": "ontology/rules/discipline-cleancode-skill.ttl",
       "sha256": "fe14a2f3b6380340388568d403f2b1dbbfeb6c1ab8de14d646e2ec8a6162a127"
     },
     {
       "path": "ontology/rules/discipline-houserules-final.ttl",
-      "sha256": "d9541bba84466676267f3c0f2c6d05f54a7ed97e04501f9863da6820ea183d40"
+      "sha256": "bb03b9469a1fcef876db4f1c31287c0c34cea9585aeeda45cea886268835306a"
     },
     {
       "path": "ontology/rules/discipline-houserules-skill.ttl",
-      "sha256": "6e3374ffec14a4cce4869a9072b10da58da4419ef89f2c35e6506e650816449e"
+      "sha256": "9f05cfd377fd819ac9e7abed29aee1283e9c5d9afa9144a7e6a58ca5c43f8a6a"
     },
     {
       "path": "ontology/rules/discipline-tdd-final.ttl",
       "sha256": "27b5a5ab5ce515c3870e875b4e50c022fb36582338ca6f682f4a8022a333ba2c"
     },
     {
       "path": "ontology/rules/discipline-tdd-skill.ttl",
       "sha256": "40fc102a525fd0302bd441034244d82610629fcb57d7c9775645e25846bd2484"
     },
     {
       "path": "ontology/rules/implementation-django-final.ttl",
       "sha256": "e3874e731465c1fcae9ecfded93398e02e0765bea9d1707df3346d6ac74aa57d"
     },
     {
       "path": "ontology/rules/implementation-django-ninja-final.ttl",
-      "sha256": "e24b78dd3aab0a147d3458a3872d96c853f621395057a422860ac3ec5b0ddfce"
+      "sha256": "b184ade4fccfa20554614d3460e2841ea800eb731ce54553d1f4adbf9d1339a9"
     },
     {
       "path": "ontology/rules/implementation-django-ninja-skill.ttl",
-      "sha256": "369af739aae344af378c4c53a14ea5858464a0a6f5c4d7c284097e29f3fee947"
+      "sha256": "85fcd3471eeb56cecb0d99509941f44ed651c52bb2dda76ac549c7a057d6130a"
     },
     {
       "path": "ontology/rules/implementation-django-skill.ttl",
       "sha256": "1bf460caa61502ce15e86057d467eced5706ba641969d342d4c52bcfe3c4204f"
     },
     {
       "path": "ontology/rules/implementation-django-web-final.ttl",
       "sha256": "00a18a24100b44db806e6c1c0a1c1c5e937a48aab70d72129044a755e698061f"
     },
     {
@@ -8898,22 +8898,22 @@
     },
     "R-0084": {
       "agents": [
         "command-dddjango"
       ],
       "aliases": [],
       "block": "dddjango/skills/implementation-django-ninja/references/final.md/s023-6.2/b33",
       "block_order": 33,
       "checkers": [],
       "document": "dddjango/skills/implementation-django-ninja/references/final.md",
-      "expression": "https://numchida.com/ns/djr#R-0084@2026-08-19",
-      "label": "G1 승인 시에만 infra/ACL 정규화 후 구체 exception 직접 흐름",
+      "expression": "https://numchida.com/ns/djr#R-0084@2026-09-11",
+      "label": "인프라 내부 계약 정규화와 공개 오류 승인 분리",
       "order_rank": 2682,
       "section": "dddjango/skills/implementation-django-ninja/references/final.md/s023-6.2",
       "section_number": "6.2"
     },
     "R-0085": {
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/skills/implementation-django-ninja/references/final.md/s023-6.2/b33",
@@ -23594,22 +23594,22 @@
     },
     "R-1037": {
       "agents": [
         "command-dddjango"
       ],
       "aliases": [],
       "block": "dddjango/agents/discipline-reviewer.md/s007/b23",
       "block_order": 23,
       "checkers": [],
       "document": "dddjango/agents/discipline-reviewer.md",
-      "expression": "https://numchida.com/ns/djr#R-1037@2026-08-22",
-      "label": "G1 명시 승인 시에만 owning infra/ACL의 정규화 후 controller 직접 흐름 mapping",
+      "expression": "https://numchida.com/ns/djr#R-1037@2026-09-11",
+      "label": "내부 실패 계약 정규화와 safe 500 공개 경계",
       "order_rank": 819,
       "section": "dddjango/agents/discipline-reviewer.md/s007",
       "section_number": null
     },
     "R-1038": {
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/agents/discipline-reviewer.md/s007/b23",
@@ -24133,22 +24133,22 @@
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/agents/discipline-reviewer.md/s007/b29",
       "block_order": 29,
       "checkers": [
         "check-api-error-controller-contract.py"
       ],
       "document": "dddjango/agents/discipline-reviewer.md",
-      "expression": "https://numchida.com/ns/djr#R-1071@2026-08-22",
-      "label": "raw DB/SDK/network unknown failure의 전수 집합 제외(safe framework 500 기본)",
+      "expression": "https://numchida.com/ns/djr#R-1071@2026-09-11",
+      "label": "ACL known failure 전수 번역과 일반 내부 계약·공개 500 분리",
       "order_rank": 853,
       "section": "dddjango/agents/discipline-reviewer.md/s007",
       "section_number": null
     },
     "R-1072": {
       "agents": [
         "command-dddjango"
       ],
       "aliases": [],
       "block": "dddjango/agents/discipline-reviewer.md/s007/b30",
@@ -24687,22 +24687,22 @@
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/agents/discipline-reviewer.md/s007/b46",
       "block_order": 46,
       "checkers": [
         "check-domain-model.py"
       ],
       "document": "dddjango/agents/discipline-reviewer.md",
-      "expression": "https://numchida.com/ns/djr#R-1104@2026-08-22",
-      "label": "ⓓ#268 타입 조합만으로 잘못된 값이 불가능한가(Q2)",
+      "expression": "https://numchida.com/ns/djr#R-1104@2026-09-11",
+      "label": "닫힌 Enum 검증 제외·open Enum Q2와 트랜잭션 영역 후보 검수",
       "order_rank": 886,
       "section": "dddjango/agents/discipline-reviewer.md/s007",
       "section_number": null
     },
     "R-1105": {
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/agents/discipline-reviewer.md/s007/b46",
@@ -24908,56 +24908,56 @@
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/agents/discipline-reviewer.md/s007/b51",
       "block_order": 51,
       "checkers": [
         "check-naming.py"
       ],
       "document": "dddjango/agents/discipline-reviewer.md",
-      "expression": "https://numchida.com/ns/djr#R-1117@2026-08-22",
-      "label": "ⓓ#343 운영 기능인가 장고 배선인가",
+      "expression": "https://numchida.com/ns/djr#R-1117@2026-09-11",
+      "label": "운영 기능/장고 배선·admin UI context 조립과 실제 소비 검수",
       "order_rank": 899,
       "section": "dddjango/agents/discipline-reviewer.md/s007",
       "section_number": null
     },
     "R-1118": {
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/agents/discipline-reviewer.md/s007/b51",
       "block_order": 51,
       "checkers": [
         "check-naming.py"
       ],
       "document": "dddjango/agents/discipline-reviewer.md",
-      "expression": "https://numchida.com/ns/djr#R-1118@2026-08-22",
-      "label": "ⓓ#589 조건이 업무 판정인가(Q2)",
+      "expression": "https://numchida.com/ns/djr#R-1118@2026-09-11",
+      "label": "표현 조건 업무 판정 Q2·admin context 출처/소비 미해소 후보",
       "order_rank": 900,
       "section": "dddjango/agents/discipline-reviewer.md/s007",
       "section_number": null
     },
     "R-1119": {
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/agents/discipline-reviewer.md/s007/b52",
       "block_order": 52,
       "checkers": [
         "check-port-adapter-pairing.py"
       ],
       "document": "dddjango/agents/discipline-reviewer.md",
-      "expression": "https://numchida.com/ns/djr#R-1119@2026-08-22",
-      "label": "ⓓ#227 자료를 원시값 인자로 펴서 넘길 수 있나",
+      "expression": "https://numchida.com/ns/djr#R-1119@2026-09-11",
+      "label": "포트/어댑터 판정과 vendor 오류 속성 출처 후보 검수",
       "order_rank": 901,
       "section": "dddjango/agents/discipline-reviewer.md/s007",
       "section_number": null
     },
     "R-1120": {
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/agents/discipline-reviewer.md/s007/b52",
@@ -32544,22 +32544,22 @@
         "agent-design-review-api",
         "command-dddjango"
       ],
       "aliases": [],
       "block": "dddjango/agents/design-architect.md/s005/b11",
       "block_order": 11,
       "checkers": [
         "check-transient-overmapping.py"
       ],
       "document": "dddjango/agents/design-architect.md",
-      "expression": "https://numchida.com/ns/djr#R-1617@2026-08-22",
-      "label": "slot 10 — raw infra failure 의 기본 500 과 승인된 public meaning 한정 정규화",
+      "expression": "https://numchida.com/ns/djr#R-1617@2026-09-11",
+      "label": "내부 실패 정규화와 공개 HTTP 계약 승인 분리",
       "order_rank": 273,
       "section": "dddjango/agents/design-architect.md/s005",
       "section_number": null
     },
     "R-1618": {
       "agents": [
         "agent-design-review-api",
         "command-dddjango"
       ],
       "aliases": [],
@@ -48969,22 +48969,22 @@
         "agent-design-review-api"
       ],
       "aliases": [],
       "block": "dddjango/agents/design-review-api.md/s006/b11",
       "block_order": 11,
       "checkers": [
         "check-api-error-controller-contract.py",
         "check-synthetic-infra-exc.py"
       ],
       "document": "dddjango/agents/design-review-api.md",
-      "expression": "https://numchida.com/ns/djr#R-2677@2026-08-22",
-      "label": "slot 10 — raw infra 기본 500·승인된 안정 public meaning만 consuming BC internal exception 정규화 후 ErrorSchema 생성 확인",
+      "expression": "https://numchida.com/ns/djr#R-2677@2026-09-11",
+      "label": "내부 실패 정규화와 공개 HTTP 계약 승인 분리 검수",
       "order_rank": 496,
       "section": "dddjango/agents/design-review-api.md/s006",
       "section_number": null
     },
     "R-2678": {
       "agents": [
         "agent-design-review-api"
       ],
       "aliases": [],
       "block": "dddjango/agents/design-review-api.md/s006/b11",
@@ -53059,22 +53059,22 @@
         "command-dddjango"
       ],
       "aliases": [],
       "block": "dddjango/skills/implementation-django-ninja/SKILL.md/s004/b10",
       "block_order": 10,
       "checkers": [
         "check-context-isolation.py",
         "check-synthetic-infra-exc.py"
       ],
       "document": "dddjango/skills/implementation-django-ninja/SKILL.md",
-      "expression": "https://numchida.com/ns/djr#R-2941@2026-08-22",
-      "label": "승인된 안정 의미 한정 infra/ACL 의 자기 BC exception 정규화",
+      "expression": "https://numchida.com/ns/djr#R-2941@2026-09-11",
+      "label": "인프라 내부 계약 번역과 공개 safe 500 유지",
       "order_rank": 2442,
       "section": "dddjango/skills/implementation-django-ninja/SKILL.md/s004",
       "section_number": null
     },
     "R-2942": {
       "agents": [],
       "aliases": [],
       "block": "dddjango/skills/implementation-django-ninja/SKILL.md/s004/b11",
       "block_order": 11,
       "checkers": [
@@ -60346,22 +60346,22 @@
     },
     "R-3410": {
       "agents": [],
       "aliases": [],
       "block": "dddjango/skills/discipline-houserules/references/final.md/s003-0/b10",
       "block_order": 10,
       "checkers": [
         "check-layer-skeleton.py"
       ],
       "document": "dddjango/skills/discipline-houserules/references/final.md",
-      "expression": "https://numchida.com/ns/djr#R-3410@2026-09-01",
-      "label": "부품 출생 50행 하한과 부품 0개 퇴화의 환원 신호",
+      "expression": "https://numchida.com/ns/djr#R-3410@2026-09-11",
+      "label": "부품 0 승격 폴더 환원 신호·신규 산출/기존 빚 처분",
       "order_rank": 2168,
       "section": "dddjango/skills/discipline-houserules/references/final.md/s003-0",
       "section_number": "0"
     },
     "R-3411": {
       "agents": [
         "agent-coder",
         "agent-discipline-reviewer"
       ],
       "aliases": [],
@@ -60456,22 +60456,22 @@
     "R-3417": {
       "agents": [
         "agent-coder",
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/skills/discipline-houserules/SKILL.md/s004-1/b7",
       "block_order": 7,
       "checkers": [],
       "document": "dddjango/skills/discipline-houserules/SKILL.md",
-      "expression": "https://numchida.com/ns/djr#R-3417@2026-09-01b",
-      "label": "캐스케이드 ② 동명 폴더 승격 — 역할 밖 응집 술어(상태 클래스/참조 폐쇄 클러스터)·개별 50행 하한·관례 동거 예외·부품은 형제 분할·집행 전 모듈 객체 참조처 조사(패치 표면)",
+      "expression": "https://numchida.com/ns/djr#R-3417@2026-09-11",
+      "label": "소관·응집으로 동명 폴더 승격·행수 하한 없이 참조 전수 조사",
       "order_rank": 2096,
       "section": "dddjango/skills/discipline-houserules/SKILL.md/s004-1",
       "section_number": "1"
     },
     "R-3418": {
       "agents": [
         "agent-coder",
         "agent-discipline-reviewer"
       ],
       "aliases": [],
@@ -60570,107 +60570,107 @@
       "agents": [
         "agent-design-architect"
       ],
       "aliases": [],
       "block": "dddjango/agents/design-architect.md/s005/b33",
       "block_order": 33,
       "checkers": [
         "design_pregate.py"
       ],
       "document": "dddjango/agents/design-architect.md",
-      "expression": "https://numchida.com/ns/djr#R-3424@2026-09-01",
-      "label": "설계 명세 기계가독 채널 상시 작성 — 산문 추론 0·부재 fail-closed 전사",
+      "expression": "https://numchida.com/ns/djr#R-3424@2026-09-11",
+      "label": "기계가독 다섯 채널과 선택 효과 — 무기재 의미·선언 검증·본문 미검증 분리",
       "order_rank": 406,
       "section": "dddjango/agents/design-architect.md/s005",
       "section_number": null
     },
     "R-3425": {
       "agents": [
         "agent-design-architect"
       ],
       "aliases": [],
       "block": "dddjango/agents/design-architect.md/s005/b34",
       "block_order": 34,
       "checkers": [
         "design_pregate.py"
       ],
       "document": "dddjango/agents/design-architect.md",
-      "expression": "https://numchida.com/ns/djr#R-3425@2026-09-10",
-      "label": "file-plan 정규 블록 — 1행 1경로·조치 태그·금지 표기·삽화↔블록 차분 · 태그의 뜻은 기준선 기준(add 부재·update 실존(승격 형태 예외)·비후행 remove 실존·재라벨 도피는 형식 red)",
+      "expression": "https://numchida.com/ns/djr#R-3425@2026-09-11",
+      "label": "file-plan 기준선 태그·제거와 실체화 0 선언 검증",
       "order_rank": 408,
       "section": "dddjango/agents/design-architect.md/s005",
       "section_number": null
     },
     "R-3426": {
       "agents": [
         "agent-design-architect"
       ],
       "aliases": [],
       "block": "dddjango/agents/design-architect.md/s005/b35",
       "block_order": 35,
       "checkers": [
         "design_pregate.py"
       ],
       "document": "dddjango/agents/design-architect.md",
-      "expression": "https://numchida.com/ns/djr#R-3426@2026-09-10b",
-      "label": "공개 심볼 전수 표기 — Base 닫힌 목록·베이스 유도표 공집합·값 축 유도 3행 등재(마이그레이션 칸 결손 보충)·`_`+대문자 사설 타입·필드 대입식 허용·수신자 관용 정규화·계약 필드·중첩 타입 소속 명시",
+      "expression": "https://numchida.com/ns/djr#R-3426@2026-09-11",
+      "label": "공개 심볼과 add/update 선언 후상태·본문 미검증 분리",
       "order_rank": 409,
       "section": "dddjango/agents/design-architect.md/s005",
       "section_number": null
     },
     "R-3427": {
       "agents": [
         "agent-design-architect"
       ],
       "aliases": [],
       "block": "dddjango/agents/design-architect.md/s005/b36",
       "block_order": 36,
       "checkers": [
         "design_pregate.py"
       ],
       "document": "dddjango/agents/design-architect.md",
-      "expression": "https://numchida.com/ns/djr#R-3427@2026-09-10",
-      "label": "경계 import 표 — 검사기 판정 관련 경계 import 전부(테스트 파일 포함) · 경계 3분류(BC 밖 · BC 내부 층 경계 중 검사기 판정 항목 — 잎→port 예외 import 도 행으로 · 그 밖 재량) · 3단 실존 판정 입력(이 브랜치 기준 · 행 삭제 = 채널 은폐 · 부재 update 는 형식 red 선행·승격 예외분만 ⑴)",
+      "expression": "https://numchida.com/ns/djr#R-3427@2026-09-11",
+      "label": "경계 import 실존·전사와 선언 출처 검증 분리",
       "order_rank": 410,
       "section": "dddjango/agents/design-architect.md/s005",
       "section_number": null
     },
     "R-3428": {
       "agents": [
         "agent-design-architect"
       ],
       "aliases": [],
       "block": "dddjango/agents/design-architect.md/s005/b37",
       "block_order": 37,
       "checkers": [
         "design_pregate.py"
       ],
       "document": "dddjango/agents/design-architect.md",
-      "expression": "https://numchida.com/ns/djr#R-3428@2026-09-10",
-      "label": "물리 신호 어노테이션 — markers/base/client 정형·무기재=물리 신호 없음",
+      "expression": "https://numchida.com/ns/djr#R-3428@2026-09-11",
+      "label": "물리 신호 — add 부재·update marker 현행 유지/최종 목록·미지원 S5",
       "order_rank": 411,
       "section": "dddjango/agents/design-architect.md/s005",
       "section_number": null
     },
     "R-3429": {
       "agents": [
         "agent-design-architect"
       ],
       "aliases": [],
       "block": "dddjango/agents/design-architect.md/s005/b37",
       "block_order": 37,
       "checkers": [
         "design_pregate.py"
       ],
       "document": "dddjango/agents/design-architect.md",
-      "expression": "https://numchida.com/ns/djr#R-3429@2026-09-01",
-      "label": "입장 표 header 영문 정본 6열 고정·셀 내 raw 파이프 금지",
+      "expression": "https://numchida.com/ns/djr#R-3429@2026-09-11",
+      "label": "입장 표 6열·첫 artifact add/update 결합·후속 주소 비전파",
       "order_rank": 412,
       "section": "dddjango/agents/design-architect.md/s005",
       "section_number": null
     },
     "R-3430": {
       "agents": [
         "agent-design-architect"
       ],
       "aliases": [],
       "block": "dddjango/agents/design-architect.md/s005/b38",
@@ -60689,97 +60689,97 @@
       "agents": [
         "agent-design-architect"
       ],
       "aliases": [],
       "block": "dddjango/agents/design-architect.md/s005/b33",
       "block_order": 33,
       "checkers": [
         "design_pregate.py"
       ],
       "document": "dddjango/agents/design-architect.md",
-      "expression": "https://numchida.com/ns/djr#R-3431@2026-09-01",
-      "label": "machine 마커 concrete 블록 한정 — 템플릿·예시 인용 부착 금지",
+      "expression": "https://numchida.com/ns/djr#R-3431@2026-09-11",
+      "label": "machine 마커 concrete 계획 한정·명시 효과와 admin 소비 범위",
       "order_rank": 407,
       "section": "dddjango/agents/design-architect.md/s005",
       "section_number": null
     },
     "R-3432": {
       "agents": [
         "command-dddjango"
       ],
       "aliases": [],
       "block": "dddjango/commands/dddjango.md/s006/b9",
       "block_order": 9,
       "checkers": [],
       "document": "dddjango/commands/dddjango.md",
-      "expression": "https://numchida.com/ns/djr#R-3432@2026-09-03b",
-      "label": "pre-gate 실행 의무 — design-spec 내용 변경마다·배너 직전 최종본·override 후 dispatch 전 무조건(캐시 skip·재발화·Phase 2 최신성 판형은 R-3445)",
+      "expression": "https://numchida.com/ns/djr#R-3432@2026-09-11",
+      "label": "pre-gate 실행 의무 — 명세 변경/배너 직전/dispatch 전 최종 예보·선언 포함",
       "order_rank": 1066,
       "section": "dddjango/commands/dddjango.md/s006",
       "section_number": null
     },
     "R-3433": {
       "agents": [
         "command-dddjango"
       ],
       "aliases": [],
       "block": "dddjango/commands/dddjango.md/s006/b9",
       "block_order": 9,
       "checkers": [],
       "document": "dddjango/commands/dddjango.md",
-      "expression": "https://numchida.com/ns/djr#R-3433@2026-09-03b",
-      "label": "차단 모드 red 처분 — red 반송 의무 · 배너 근거 --check-report exit 0 · 예외 = 귀속 red 전건 ignored(빚)|filtered · path 등급 filtered 불가",
+      "expression": "https://numchida.com/ns/djr#R-3433@2026-09-11",
+      "label": "pre-gate 귀속 및 선언 확정 red 전건 처분·후보/S1 비차단 분리",
       "order_rank": 1067,
       "section": "dddjango/commands/dddjango.md/s006",
       "section_number": null
     },
     "R-3434": {
       "agents": [
         "command-dddjango"
       ],
       "aliases": [],
       "block": "dddjango/commands/dddjango.md/s006/b9",
       "block_order": 9,
       "checkers": [],
       "document": "dddjango/commands/dddjango.md",
-      "expression": "https://numchida.com/ns/djr#R-3434@2026-09-03",
-      "label": "예보의 대체·축약 금지 — Phase 0 빚 스캔·G2 게이트 비대체·build_anchor 불간섭·HEAD 판형 유용 금지·계약 실존 채널의 G0 선행 조건·상류 머지 판단 비대체",
+      "expression": "https://numchida.com/ns/djr#R-3434@2026-09-11",
+      "label": "예보·선언·생성 S1의 Phase 0/G2/G0 실증 비대체·앵커 불간섭",
       "order_rank": 1068,
       "section": "dddjango/commands/dddjango.md/s006",
       "section_number": null
     },
     "R-3435": {
       "agents": [
         "command-dddjango"
       ],
       "aliases": [],
       "block": "dddjango/commands/dddjango.md/s006/b9",
       "block_order": 9,
       "checkers": [],
       "document": "dddjango/commands/dddjango.md",
-      "expression": "https://numchida.com/ns/djr#R-3435@2026-09-01",
-      "label": "팬텀 스텁 = 스크립트의 결정적 투영물(격리 사본 한정) — 구현 코드 직접 작성 금지 경계 비저촉",
+      "expression": "https://numchida.com/ns/djr#R-3435@2026-09-11",
+      "label": "격리 사본 결정적 투영물·명시 후상태와 기존 본문 미검증",
       "order_rank": 1069,
       "section": "dddjango/commands/dddjango.md/s006",
       "section_number": null
     },
     "R-3436": {
       "agents": [
         "command-dddjango"
       ],
       "aliases": [],
       "block": "dddjango/commands/dddjango.md/s006/b9",
       "block_order": 9,
       "checkers": [],
       "document": "dddjango/commands/dddjango.md",
-      "expression": "https://numchida.com/ns/djr#R-3436@2026-09-03b",
-      "label": "pre-gate machine 블록 부재·공허 skip 금지 — 부재·0행 = 형식 red(exit 3) · 구형 명세 포함(«캐시 skip»·«실체화 0 skip» 과 구별)",
+      "expression": "https://numchida.com/ns/djr#R-3436@2026-09-11",
+      "label": "machine 부재/공허 형식 red·실체화 0에서도 선언 검증",
       "order_rank": 1070,
       "section": "dddjango/commands/dddjango.md/s006",
       "section_number": null
     },
     "R-3437": {
       "agents": [
         "command-dddjango"
       ],
       "aliases": [],
       "block": "dddjango/commands/dddjango.md/s003/b10",
@@ -60899,22 +60899,22 @@
     },
     "R-3445": {
       "agents": [
         "command-dddjango"
       ],
       "aliases": [],
       "block": "dddjango/commands/dddjango.md/s006/b10",
       "block_order": 10,
       "checkers": [],
       "document": "dddjango/commands/dddjango.md",
-      "expression": "https://numchida.com/ns/djr#R-3445@2026-09-03",
-      "label": "pre-gate 캐시 skip·--base 재발화·Phase 2 최신성 — dispatch 전 재발화 · G2 전 --check-report exit 0 · 구형 명세·변경 0 레인 한정",
+      "expression": "https://numchida.com/ns/djr#R-3445@2026-09-11",
+      "label": "선택 effects 포함 캐시 해시·기존 무기재 해시 보존·재발화 최신성",
       "order_rank": 1071,
       "section": "dddjango/commands/dddjango.md/s006",
       "section_number": null
     },
     "R-3446": {
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/skills/implementation-python/references/final.md/s032-4.4/b3",
@@ -60931,39 +60931,39 @@
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/skills/discipline-houserules/SKILL.md/s007-4/b7",
       "block_order": 7,
       "checkers": [
         "check-public-surface-annotation.py"
       ],
       "document": "dddjango/skills/discipline-houserules/SKILL.md",
-      "expression": "https://numchida.com/ns/djr#R-3447@2026-09-04b",
-      "label": "Any 금지 — 시그니처(별표 인자 포함)·변수·클래스 속성·제네릭 인자 전부 · 프레임워크 오버라이드도 object/정확 타입 · 시그니처는 #645 차단·그 밖은 ⓓ 후보(#645) · dict/Mapping 값 자리 Any 는 #647 차단",
+      "expression": "https://numchida.com/ns/djr#R-3447@2026-09-11",
+      "label": "Any 기존 금지/후보와 확인된 framework admin 슬롯 제한 허용",
       "order_rank": 2120,
       "section": "dddjango/skills/discipline-houserules/SKILL.md/s007-4",
       "section_number": "4"
     },
     "R-3448": {
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/skills/discipline-houserules/SKILL.md/s007-4/b7",
       "block_order": 7,
       "checkers": [
         "check-public-surface-annotation.py"
       ],
       "document": "dddjango/skills/discipline-houserules/SKILL.md",
-      "expression": "https://numchida.com/ns/djr#R-3448@2026-09-04b",
-      "label": "경계 입력은 object/정확 타입으로 받아 받는 즉시 좁힘(TypeIs·isinstance·type() is · 자리는 architecture-ddd §3.1) · JSON 은 TypeAdapter(TypedDict) 검증 파싱 · object 는 입구 매개변수·즉시 검증 지역 변수만(반환/속성 누수 #647 차단 · 반환 자리표시 object·json.load 무검증 흐름은 ⓓ #647/#650 · 예외 프레임워크 콜백 미러·이벤트 컬렉션) · 면제 Form.clean·TypeIs",
+      "expression": "https://numchida.com/ns/djr#R-3448@2026-09-11",
+      "label": "경계 object 즉시 좁힘·JSON 검증 유지·admin UI context 실제 소비 경계",
       "order_rank": 2121,
       "section": "dddjango/skills/discipline-houserules/SKILL.md/s007-4",
       "section_number": "4"
     },
     "R-3449": {
       "agents": [
         "agent-design-review-ddd"
       ],
       "aliases": [],
       "block": "dddjango/skills/architecture-ddd/references/final.md/s023-3.6/b3",
@@ -60997,39 +60997,39 @@
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/skills/discipline-houserules/SKILL.md/s007-4/b8",
       "block_order": 8,
       "checkers": [
         "check-public-surface-annotation.py"
       ],
       "document": "dddjango/skills/discipline-houserules/SKILL.md",
-      "expression": "https://numchida.com/ns/djr#R-3451@2026-09-04",
-      "label": "레코드(키 고정 값 묶음)를 딕셔너리로 들고 다니지 않는다 — 내부 리터럴은 TypedDict · 파싱 JSON 은 TypeAdapter 검증 · 도메인 개념은 값 객체 · dict/Mapping[str, object|Any] 주석은 구조 미정 신호(#647)",
+      "expression": "https://numchida.com/ns/djr#R-3451@2026-09-11",
+      "label": "업무 레코드 구조 선언과 framework admin UI context 구분",
       "order_rank": 2122,
       "section": "dddjango/skills/discipline-houserules/SKILL.md/s007-4",
       "section_number": "4"
     },
     "R-3452": {
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/skills/discipline-houserules/SKILL.md/s007-4/b10",
       "block_order": 10,
       "checkers": [
         "check-public-surface-annotation.py"
       ],
       "document": "dddjango/skills/discipline-houserules/SKILL.md",
-      "expression": "https://numchida.com/ns/djr#R-3452@2026-09-04",
-      "label": "레코드(내부 리터럴) → TypedDict(종류 여럿이면 kind: Literal 판별 키 union) · dict/Mapping[str, object|Any] 금지",
+      "expression": "https://numchida.com/ns/djr#R-3452@2026-09-11",
+      "label": "업무 레코드 TypedDict와 admin context 조립 경계",
       "order_rank": 2123,
       "section": "dddjango/skills/discipline-houserules/SKILL.md/s007-4",
       "section_number": "4"
     },
     "R-3453": {
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/skills/discipline-houserules/SKILL.md/s007-4/b11",
@@ -61095,22 +61095,22 @@
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/skills/discipline-houserules/SKILL.md/s007-4/b15",
       "block_order": 15,
       "checkers": [
         "check-public-surface-annotation.py"
       ],
       "document": "dddjango/skills/discipline-houserules/SKILL.md",
-      "expression": "https://numchida.com/ns/djr#R-3457@2026-09-04",
-      "label": "타입이 이미 있는 값(반환·매개변수·속성) → 실제 클래스 · 입구 밖 자리표시 object 금지(입구 매개변수·즉시 검증 지역 변수는 R-3448 · 반환 주석 object 는 ⓓ #647)",
+      "expression": "https://numchida.com/ns/djr#R-3457@2026-09-11",
+      "label": "실제 타입 사용과 admin framework 슬롯 구분",
       "order_rank": 2128,
       "section": "dddjango/skills/discipline-houserules/SKILL.md/s007-4",
       "section_number": "4"
     },
     "R-3458": {
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/skills/discipline-houserules/SKILL.md/s007-4/b16",
@@ -61272,22 +61272,22 @@
     },
     "R-3468": {
       "agents": [],
       "aliases": [],
       "block": "dddjango/skills/discipline-houserules/references/final.md/s003-0/b12",
       "block_order": 12,
       "checkers": [
         "check-port-adapter-pairing.py"
       ],
       "document": "dddjango/skills/discipline-houserules/references/final.md",
-      "expression": "https://numchida.com/ns/djr#R-3468@2026-09-09",
-      "label": "#651 — 어댑터 고정 역할의 클래스별 파일과 상수 묶음",
+      "expression": "https://numchida.com/ns/djr#R-3468@2026-09-11",
+      "label": "어댑터 고정 역할 골격과 승격 신호 비적용",
       "order_rank": 2173,
       "section": "dddjango/skills/discipline-houserules/references/final.md/s003-0",
       "section_number": "0"
     },
     "R-3469": {
       "agents": [
         "agent-discipline-reviewer"
       ],
       "aliases": [],
       "block": "dddjango/skills/discipline-houserules/references/final.md/s003-0/b12",

```

## workspace/tools/field_report_checker_smoke.py

Before SHA256: 37a22b3cb4d5148b4da32c2d483264c9acb6b83f79702753c7e076f830e988ee
After SHA256: c3864f94a996ff8e345a7d35854d95219e0fad6ae94239b61052f116fd1b2ab2

```diff
--- before/workspace/tools/field_report_checker_smoke.py
+++ after/workspace/tools/field_report_checker_smoke.py
@@ -146,20 +146,35 @@
         for symbol in ("build_missing_use_case", "unrelated"):
             self.assertIn("#153", self.ohs_rules(f"from application.lesson.composition_root.books import {symbol}\ndef read_query(request):\n    {symbol}().execute()\n")[1])
         found, _ = self.ohs_rules("from application.lesson.domain_layer.book.error import BookError\ndef read_query(request):\n    try: work()\n    except BookError as exc: return exc.code\n")
         self.assertIn("#153", found)
 
     def enum_rules(self, source):
         py = self.write("application/lesson/domain_layer/book/value_object/kind.py", source)
         f, c = domain.Findings(defer=True), domain.Candidates(defer=True)
         domain._check_value_object_file(self.root, py, f, c)
         return [e.rule for e in f.entries], [e.rule for e in c.entries]
+
+    def test_open_enum_reason_does_not_claim_constructor_raise_is_absent(self):
+        for source, expected in (
+            ("from enum import Enum\nclass Kind(Enum):\n    ONE = 1\n    def __init__(self, value):\n        if value < 0: raise ValueError()\n", "닫힌 표준 Enum 생성 검증을 확정할 수 없다"),
+            ("class Kind:\n    value: str\n", "__init__/__post_init__ 에 raise 가 없다"),
+        ):
+            with self.subTest(source=source):
+                self.write("application/lesson/domain_layer/book/value_object/kind.py", source)
+                result = subprocess.run([sys.executable, "-B", str(SCRIPTS / "check-domain-model.py"), str(self.root)],
+                                        capture_output=True, text=True, env=self.env)
+                reasons = [line for line in (result.stdout + result.stderr).splitlines() if "[ⓓ#268]" in line]
+                self.assertEqual(len(reasons), 1, result.stdout + result.stderr)
+                self.assertIn(expected, reasons[0])
+                if "Enum" in source:
+                    self.assertNotIn("raise 가 없다", reasons[0])
 
     def test_closed_enum_validation_and_dynamic_opposites(self):
         for header, base in [("from enum import Enum", "Enum"), ("from enum import StrEnum as Closed", "Closed"), ("import enum as standard", "standard.IntEnum")]:
             with self.subTest(base=base):
                 self.assertNotIn("#268", self.enum_rules(header + f"\nclass Kind({base}):\n    ONE = 1\n")[1])
         variants = [
             "from enum import Flag\nclass Kind(Flag):\n    ONE = 1",
             "from enum import IntFlag\nclass Kind(IntFlag):\n    ONE = 1",
             "from custom import Enum\nclass Kind(Enum):\n    ONE = 1",
             "from enum import Enum\nEnum = other\nclass Kind(Enum):\n    ONE = 1",
@@ -813,20 +828,61 @@
                     victim.unlink()
                 elif change == "nested":
                     (promoted / "nested").mkdir()
                 elif change == "junk":
                     (promoted / "utils.py").write_text("pass\n")
                 else:
                     (promoted.parent / "order_controller.py").write_text("pass\n")
                 self.assertIn(rule, self.run_checker("check-layer-skeleton.py"))
 
 
+class NormativeContractRegression(unittest.TestCase):
+    """문면 전파 대조이며 역할 에이전트의 실제 수행 증명은 아니다."""
+
+    def test_internal_normalization_and_public_500_are_distinct_in_six_sources(self):
+        for rel in (
+            "dddjango/agents/design-architect.md", "dddjango/agents/design-review-api.md",
+            "dddjango/agents/discipline-reviewer.md", "dddjango/skills/implementation-django-ninja/SKILL.md",
+            "dddjango/skills/implementation-django-ninja/references/final.md",
+        ):
+            with self.subTest(path=rel):
+                text = (ROOT / rel).read_text()
+                expected_count = 2 if rel.endswith("discipline-reviewer.md") else 1
+                for phrase in ("이미 잡은 IntegrityError", "일반 저장소 실패 계약", "기존 safe 500", "새로 catch-all하지 않는다"):
+                    self.assertEqual(text.count(phrase), expected_count, (rel, phrase))
+
+    def test_admin_policy_names_actual_consumption_boundary(self):
+        for rel in ("dddjango/skills/discipline-houserules/SKILL.md", "dddjango/agents/design-architect.md",
+                    "dddjango/agents/discipline-reviewer.md"):
+            with self.subTest(path=rel):
+                text = (ROOT / rel).read_text()
+                for phrase in ("private 전달 helper", "업무 읽기·비교·계산·상태 변경", "출처나 소비가 미해소"):
+                    self.assertIn(phrase, text)
+
+    def test_promotion_has_no_birth_floor_and_keeps_zero_part_reversion(self):
+        skill = (ROOT / "dddjango/skills/discipline-houserules/SKILL.md").read_text()
+        reference = (ROOT / "dddjango/skills/discipline-houserules/references/final.md").read_text()
+        self.assertNotIn("개별 50행 이상", skill)
+        self.assertNotIn("출생 하한", reference)
+        self.assertIn("부품이 0개", reference)
+        for rel in ("docs/file_tree.html", "docs/mkrev2.py"):
+            self.assertNotIn("새 승격 부품은 각 50행 이상", (ROOT / rel).read_text())
+
+    def test_optional_effects_poststate_and_s1_limits_are_explicit(self):
+        architect = (ROOT / "dddjango/agents/design-architect.md").read_text()
+        coordinator = (ROOT / "dddjango/commands/dddjango.md").read_text()
+        for phrase in ("<!-- machine: use-case-effects -->", "read-only", "uow=none", "module pytestmark 최종 목록", "출처 결합 DTO"):
+            self.assertIn(phrase, architect)
+        for phrase in ("효과 블록이 없으면 기존 해시", "선언 확정", "S1 미검증"):
+            self.assertIn(phrase, coordinator)
+
+
 class SourceMirrorRegression(unittest.TestCase):
     """규범 개정 뒤에도 이관 원문 주소와 현재 렌더 주소를 혼동하지 않는다."""
 
     def setUp(self) -> None:
         self.tmp = tempfile.TemporaryDirectory(prefix="field-mirror-")
         self.addCleanup(self.tmp.cleanup)
         self.root = Path(self.tmp.name)
         self.paths = corpus.paths_for(self.root, "architecture-ddd")
         old = "## Policy\n\nOriginal approved policy.\n"
         current = "## Policy\n\nAmended approved policy.\n"

```

## workspace/reference/implementation-django-ninja/reference/final.md

Before SHA256: 41ed9da0145ce9d1fe6acb5ba03a44c3652e143cb31c947271709c7cd718d621
After SHA256: 41ed9da0145ce9d1fe6acb5ba03a44c3652e143cb31c947271709c7cd718d621

```diff

```

## workspace/reference/discipline-houserules/reference/final.md

Before SHA256: 8a9468a2d119e9752b8c84df7dc95ab61dee5ba1e2ab6e446ab55f53a6070349
After SHA256: 8a9468a2d119e9752b8c84df7dc95ab61dee5ba1e2ab6e446ab55f53a6070349

```diff

```

## dddjango/scripts/check-context-isolation.py

Before SHA256: c87498928cc0f23103c8b3b35a6b2d7f01b2dbc3825021ae1ca9e371d5256e0e
After SHA256: 9248add559f8f27481284a1c451db45aba991e32e62eeb7545bc668046b4c075

```diff
--- before/dddjango/scripts/check-context-isolation.py
+++ after/dddjango/scripts/check-context-isolation.py
@@ -20,21 +20,22 @@
          #166/#167/#168/#170 기저 예외·상속·1클래스=1모듈·_v1 금지 · #453/#454 «없다»는 답
          #455 사유는 코드로 · #472 contract 는 stdlib·같은 BC 계약만 · #482/#483/#484 명명
          #633 인자는 request 하나 · #634 공개 표면은 함수만 · #295 raw 재노출 금지
   ACL    #361 상대 BC 하나=폴더 하나 · #363 클래스명 <Bc><Capability>Adapter
          #364 포트 파일명에 공급자 BC 금지 · #450 상호 ACL 금지 · #473 기저 예외를 잡는다
   기타   #14 `with unit_of_work:` 안에서 크로스-BC 포트 호출 금지 · #110 auto_import=False
          #117 두 번째 ErrorCode 컨테이너 금지 · #291/#292 예외의 자리 셋 · #431 부작용 등록 금지
 
 ast+ 후보 채널 (㉰ — exit 불산입, 마무리는 discipline-reviewer):
   #151(창구 이름 — 기술·타 BC 토큰은 «확정» 위반) · #153(도메인 예외 속성 접근은 «확정»,
-  유스케이스 호출 0/2회↑는 후보) · #171(접미사뿐인 예외 이름) · #347(admin feature 의
+  출처가 확인된 usecase 실행 수가 1이 아니거나 출처·반복 횟수가 미해소이면 후보;
+  builder 준비·미호출 nested 정의는 실행 수에 불산입) · #171(접미사뿐인 예외 이름) · #347(admin feature 의
   애그리거트 쓰기) · #11(경계 애너테이션의 Model/QuerySet 은 «확정», 그 외 후보)
 
   framework #470 강등의 사후 신호 — 공개 시그니처에 `kind`·`mode`·`bc`·`is_*` 매개변수(D38)
   <project> #433 규칙을 «주소·예외 목록»으로 적지 않는다 — BC 경로 리터럴 컬렉션
          (INSTALLED_APPS 등록은 제외)·도메인 예외 이름 컬렉션
 
 CLI 호환 심: registry 가 렌더하는 `--error-profile`·selector 들은 «수용하되 무시»한다 —
 그 lane(API error contract)은 전용 검사기 4종의 소유가 됐고, 실행·종료 계약은 무변이다.
 
 사용법: check-context-isolation.py [TARGET_DIR] [--error-profile …] [selector …]

```

## codex-dddjango/skills/dddjango/scripts/check-context-isolation.py

Before SHA256: c87498928cc0f23103c8b3b35a6b2d7f01b2dbc3825021ae1ca9e371d5256e0e
After SHA256: 9248add559f8f27481284a1c451db45aba991e32e62eeb7545bc668046b4c075

```diff
--- before/codex-dddjango/skills/dddjango/scripts/check-context-isolation.py
+++ after/codex-dddjango/skills/dddjango/scripts/check-context-isolation.py
@@ -20,21 +20,22 @@
          #166/#167/#168/#170 기저 예외·상속·1클래스=1모듈·_v1 금지 · #453/#454 «없다»는 답
          #455 사유는 코드로 · #472 contract 는 stdlib·같은 BC 계약만 · #482/#483/#484 명명
          #633 인자는 request 하나 · #634 공개 표면은 함수만 · #295 raw 재노출 금지
   ACL    #361 상대 BC 하나=폴더 하나 · #363 클래스명 <Bc><Capability>Adapter
          #364 포트 파일명에 공급자 BC 금지 · #450 상호 ACL 금지 · #473 기저 예외를 잡는다
   기타   #14 `with unit_of_work:` 안에서 크로스-BC 포트 호출 금지 · #110 auto_import=False
          #117 두 번째 ErrorCode 컨테이너 금지 · #291/#292 예외의 자리 셋 · #431 부작용 등록 금지
 
 ast+ 후보 채널 (㉰ — exit 불산입, 마무리는 discipline-reviewer):
   #151(창구 이름 — 기술·타 BC 토큰은 «확정» 위반) · #153(도메인 예외 속성 접근은 «확정»,
-  유스케이스 호출 0/2회↑는 후보) · #171(접미사뿐인 예외 이름) · #347(admin feature 의
+  출처가 확인된 usecase 실행 수가 1이 아니거나 출처·반복 횟수가 미해소이면 후보;
+  builder 준비·미호출 nested 정의는 실행 수에 불산입) · #171(접미사뿐인 예외 이름) · #347(admin feature 의
   애그리거트 쓰기) · #11(경계 애너테이션의 Model/QuerySet 은 «확정», 그 외 후보)
 
   framework #470 강등의 사후 신호 — 공개 시그니처에 `kind`·`mode`·`bc`·`is_*` 매개변수(D38)
   <project> #433 규칙을 «주소·예외 목록»으로 적지 않는다 — BC 경로 리터럴 컬렉션
          (INSTALLED_APPS 등록은 제외)·도메인 예외 이름 컬렉션
 
 CLI 호환 심: registry 가 렌더하는 `--error-profile`·selector 들은 «수용하되 무시»한다 —
 그 lane(API error contract)은 전용 검사기 4종의 소유가 됐고, 실행·종료 계약은 무변이다.
 
 사용법: check-context-isolation.py [TARGET_DIR] [--error-profile …] [selector …]

```

## dddjango/scripts/check-domain-model.py

Before SHA256: 0bdf4f1212c535d83dc634ff34f0ea9d482cefb70144e6da2266870c4dd7586d
After SHA256: 1dc8871ef71255e22c586e540a07a0f3d8b258a6fe2f26e4e1cb1cbe2bdde428

```diff
--- before/dddjango/scripts/check-domain-model.py
+++ after/dddjango/scripts/check-domain-model.py
@@ -17,21 +17,22 @@
   #258 [ast]  entity/ 직접 참조 금지 — 애그리거트 밖에서 붙잡는 것은 루트뿐.
   #259 [ast+] entity/ 판정은 식별자 — 후보: id 를 가진 value_object(자리 뒤바뀜 신호).
   #260 [ast]  entity/ 클래스는 식별자(id·*_id)를 가진다.
   #261 [ast]  엔티티 하나 = 파일 하나.        #262 [path] `_entity` 접미 금지.
   #263 [path] 이름 겹칠 때 `_model` 은 ORM 쪽만 — 도메인과 같은 stem 의 models 파일 금지.
   #264 [ast]  값 객체 불변 — __init__/__post_init__ 밖 self 대입 금지.
   #265 [ast]  <A>/value_object/ 는 그 애그리거트 밖에서 안 쓰인다 — #266 과 같은 술어라
               #266 의 진단이 함께 진다(중복 진단 금지 · 유스케이스의 값 변환은 정상이라 제외).
   #266 [ast]  다른 애그리거트가 쓰면 shared_value_object/ 로 올린다(도메인 쪽 사용 검출).
   #267 [ast]  값 객체 하나 = 파일 하나(shared 포함 — #459 와 같은 규칙).
-  #268 [ast+] 후보: __init__/__post_init__ 에 raise 0 인 값 객체(Q2 — 잘못된 값이 불가능한가).
+  #268 [ast+] 후보: 일반 VO 생성자 raise 부재 또는 custom/open Enum의 생성 검증 미확정.
+              출처가 확인된 닫힌 표준 Enum/StrEnum/IntEnum만 제외(Q2 — 잘못된 값이 불가능한가).
   #269 [ast]  <A>/event/ 는 BC 안에서 읽혀야 한다 — 0 참조면 위반(#270: 그건 알림이라
               자리는 application_layer/port/ 다).
   #270 [ast]  driven 어댑터만 읽는 사실은 이벤트가 아니라 «알림» — 자리는 port/.
   #272 [ast]  루트는 이벤트를 기록만 한다 — publish/dispatch 호출 금지.
   #275 [ast]  과거형 사실 하나 = 파일 하나.   #276 [ast] 이벤트는 필드만(메서드 금지).
   #289 [path] 불변식 예외는 exception/ «폴더» — <A>/exception.py 파일이면 위반.
   #290 [path] exception/ 안 «깨진 불변식 하나 = 파일 하나» — 한 파일 여러 예외면 위반.
   #298 [ast]  shared_value_object 는 자기 안 + exception 모듈만 import.
   #299 [path] 애그리거트 꼴 — <X>_repository.py 부재면 위반(<X>.py 부재는 #256).
   #300 [path] <aggregate>/domain_service/ 금지 — BC 레벨 한 칸뿐.
@@ -43,32 +44,34 @@
   #307 [ast]  시그니처는 값 객체 — 전 인자가 원시 타입이면 계산 함수다.
   #308 [ast]  위반의 알림은 도메인 예외 — bool 반환 선언이면 위반.
   #310 [ast]  무상태 규칙 하나 = 파일 하나.
   #311 [ast+] 후보: 파일명이 접미사(_service)를 달거나 애그리거트 어휘 0(행위 이름 물음).
   #315 [path] Factory 는 그 애그리거트 폴더 안.
   #459 [path] shared_value_object 파일 규칙 동일 — 하위 폴더 금지.
   #505 [ast]  <A>/event/ 는 «내부용» — BC 밖 import 금지(밖은 published_event 로 옮겨 담는다).
   #506 [ast]  발행 장치(레지스트리·dispatch·signal)는 domain_layer 에 살지 않는다.
   #542 [ast]  사실은 «애그리거트»가 만든다 — 유스케이스의 도메인 이벤트 생성이면 위반.
   #543 [ast]  꺼내는 창구는 pull_events() 하나 — «안 비우는» events 프로퍼티 병존 금지.
-  #546 [ast]  한 트랜잭션 = 애그리거트 하나 — «서로 다른 애그리거트 리포지토리 타입»에
-              쓰기 둘이면 위반(세는 대상은 «타입이 <A>_repository.py 에서 온 것»뿐 — C7).
+  #546 [ast+] 해소된 동일 트랜잭션 영역에 서로 다른 repository/aggregate 타입 쓰기는 확정.
+              순차 UoW 분리·nested/외부 atomic 결합; 영역·출처 미해소는 후보.
   #547 [ast+] 후보: 한 리포지토리를 여러 <area>/ 가 쓰거나 루트가 비대(엔티티 3+·컬렉션
               필드)한 것 — 「이 둘이 동시에 일어나면 업무가 정말 막아야 하나」(경계를 쪼갠다).
   #548 [ast]  다른 애그리거트는 «식별자 값 객체»로만 — 타입 힌트의 남의 루트 클래스 위반.
   #549 [ast]  수정 조회는 캐시 우회 — select_for_update 와 캐시가 한 함수에 있으면 위반.
   #550 [ast]  배치 면제는 «생성»에만 — 조회로 꺼낸 것들의 save_all 이면 위반.
   #565 [ast+] 후보: 도메인 Enum 값이 유스케이스·서비스 이름과 겹침 — 「업무가 이 단계
               이름을 입으로 부르나」(워크플로 위장 신호).
 
 단순화(정직 기록): #269/#270 의 «읽힘»은 BC 파일 텍스트의 이름 등장으로 잰다. #546 의
 타입 해소는 파라미터·__init__ 애너테이션의 `*Repository` 이름과 import 경로 대조다.
+트랜잭션 영역은 표준 UoW 주입·factory·별칭과 Django atomic의 AST 범위로 한정한다.
+같은 repository 타입의 여러 인스턴스는 구별하지 않으며 미해소 영역은 통과 증명이 아니다.
 
 이관 계약(명세 조각 ⓐ): 채택 신호 2원(#78) · 대상 0건 가드(#74) · ImportError
 fail-closed · ⓓ 후보 exit 불산입.
 
 사용법: check-domain-model.py [TARGET_DIR]   (기본: 현재 디렉터리)
 종료코드: 0=clean(또는 표준 미채택) · 1=사용/분석 오류 · 2=blocker(발견 출력)
 구조화 레코드: DJR_FINDINGS_JSON=<경로> 지정 시 findings.py(공용 모듈)가 JSON lines 를
 추가 방출한다 — 라인 출력·exit 의미론 무변(T0 B2).
 
 그래프 좌표(T2-2): 규범 정본 = 온톨로지 그래프(`ontology/rules/`) · 이 검사기의 #N ↔ Work 조인은
@@ -537,22 +540,24 @@
             if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) \
                     and (node.target.id == "id" or node.target.id.endswith("_id")):
                 cand.add("#259", _rel(root, py, node.lineno),
                          f"값 객체 `{cls.name}` 이 식별자 `{node.target.id}` 를 가진다 — "
                          "식별자를 갖고 값이 바뀌어도 같은 것이면 그것은 엔티티다",
                          "Q4 — 이것이 값인가 엔티티인가")
                 break
         closed_enum, enum_based = _closed_standard_enum(mod, cls)
         if not closed_enum and (not has_validation or enum_based):
             cand.add("#268", _rel(root, py, cls.lineno),
-                     f"`{cls.name}` 의 __init__/__post_init__ 에 raise 가 없다 — 값 객체는 "
-                     "만들어지는 시점에 스스로 검증한다",
+                     (f"`{cls.name}` 의 닫힌 표준 Enum 생성 검증을 확정할 수 없다 — "
+                      "custom/open 생성 경로를 검토한다" if enum_based else
+                      f"`{cls.name}` 의 __init__/__post_init__ 에 raise 가 없다 — 값 객체는 "
+                      "만들어지는 시점에 스스로 검증한다"),
                      "Q2 — 이 타입 조합만으로 잘못된 값이 «불가능»한가")
 
 
 def _check_domain_events(root: Path, bc: Path, agg: Path, ev_dir: Path, f: Findings) -> None:
     bc_texts: dict[Path, str] = {}
     for py in _py_files(bc):
         try:
             bc_texts[py] = py.read_text(encoding="utf-8")
         except (OSError, UnicodeDecodeError):
             continue

```

## codex-dddjango/skills/dddjango/scripts/check-domain-model.py

Before SHA256: 0bdf4f1212c535d83dc634ff34f0ea9d482cefb70144e6da2266870c4dd7586d
After SHA256: 1dc8871ef71255e22c586e540a07a0f3d8b258a6fe2f26e4e1cb1cbe2bdde428

```diff
--- before/codex-dddjango/skills/dddjango/scripts/check-domain-model.py
+++ after/codex-dddjango/skills/dddjango/scripts/check-domain-model.py
@@ -17,21 +17,22 @@
   #258 [ast]  entity/ 직접 참조 금지 — 애그리거트 밖에서 붙잡는 것은 루트뿐.
   #259 [ast+] entity/ 판정은 식별자 — 후보: id 를 가진 value_object(자리 뒤바뀜 신호).
   #260 [ast]  entity/ 클래스는 식별자(id·*_id)를 가진다.
   #261 [ast]  엔티티 하나 = 파일 하나.        #262 [path] `_entity` 접미 금지.
   #263 [path] 이름 겹칠 때 `_model` 은 ORM 쪽만 — 도메인과 같은 stem 의 models 파일 금지.
   #264 [ast]  값 객체 불변 — __init__/__post_init__ 밖 self 대입 금지.
   #265 [ast]  <A>/value_object/ 는 그 애그리거트 밖에서 안 쓰인다 — #266 과 같은 술어라
               #266 의 진단이 함께 진다(중복 진단 금지 · 유스케이스의 값 변환은 정상이라 제외).
   #266 [ast]  다른 애그리거트가 쓰면 shared_value_object/ 로 올린다(도메인 쪽 사용 검출).
   #267 [ast]  값 객체 하나 = 파일 하나(shared 포함 — #459 와 같은 규칙).
-  #268 [ast+] 후보: __init__/__post_init__ 에 raise 0 인 값 객체(Q2 — 잘못된 값이 불가능한가).
+  #268 [ast+] 후보: 일반 VO 생성자 raise 부재 또는 custom/open Enum의 생성 검증 미확정.
+              출처가 확인된 닫힌 표준 Enum/StrEnum/IntEnum만 제외(Q2 — 잘못된 값이 불가능한가).
   #269 [ast]  <A>/event/ 는 BC 안에서 읽혀야 한다 — 0 참조면 위반(#270: 그건 알림이라
               자리는 application_layer/port/ 다).
   #270 [ast]  driven 어댑터만 읽는 사실은 이벤트가 아니라 «알림» — 자리는 port/.
   #272 [ast]  루트는 이벤트를 기록만 한다 — publish/dispatch 호출 금지.
   #275 [ast]  과거형 사실 하나 = 파일 하나.   #276 [ast] 이벤트는 필드만(메서드 금지).
   #289 [path] 불변식 예외는 exception/ «폴더» — <A>/exception.py 파일이면 위반.
   #290 [path] exception/ 안 «깨진 불변식 하나 = 파일 하나» — 한 파일 여러 예외면 위반.
   #298 [ast]  shared_value_object 는 자기 안 + exception 모듈만 import.
   #299 [path] 애그리거트 꼴 — <X>_repository.py 부재면 위반(<X>.py 부재는 #256).
   #300 [path] <aggregate>/domain_service/ 금지 — BC 레벨 한 칸뿐.
@@ -43,32 +44,34 @@
   #307 [ast]  시그니처는 값 객체 — 전 인자가 원시 타입이면 계산 함수다.
   #308 [ast]  위반의 알림은 도메인 예외 — bool 반환 선언이면 위반.
   #310 [ast]  무상태 규칙 하나 = 파일 하나.
   #311 [ast+] 후보: 파일명이 접미사(_service)를 달거나 애그리거트 어휘 0(행위 이름 물음).
   #315 [path] Factory 는 그 애그리거트 폴더 안.
   #459 [path] shared_value_object 파일 규칙 동일 — 하위 폴더 금지.
   #505 [ast]  <A>/event/ 는 «내부용» — BC 밖 import 금지(밖은 published_event 로 옮겨 담는다).
   #506 [ast]  발행 장치(레지스트리·dispatch·signal)는 domain_layer 에 살지 않는다.
   #542 [ast]  사실은 «애그리거트»가 만든다 — 유스케이스의 도메인 이벤트 생성이면 위반.
   #543 [ast]  꺼내는 창구는 pull_events() 하나 — «안 비우는» events 프로퍼티 병존 금지.
-  #546 [ast]  한 트랜잭션 = 애그리거트 하나 — «서로 다른 애그리거트 리포지토리 타입»에
-              쓰기 둘이면 위반(세는 대상은 «타입이 <A>_repository.py 에서 온 것»뿐 — C7).
+  #546 [ast+] 해소된 동일 트랜잭션 영역에 서로 다른 repository/aggregate 타입 쓰기는 확정.
+              순차 UoW 분리·nested/외부 atomic 결합; 영역·출처 미해소는 후보.
   #547 [ast+] 후보: 한 리포지토리를 여러 <area>/ 가 쓰거나 루트가 비대(엔티티 3+·컬렉션
               필드)한 것 — 「이 둘이 동시에 일어나면 업무가 정말 막아야 하나」(경계를 쪼갠다).
   #548 [ast]  다른 애그리거트는 «식별자 값 객체»로만 — 타입 힌트의 남의 루트 클래스 위반.
   #549 [ast]  수정 조회는 캐시 우회 — select_for_update 와 캐시가 한 함수에 있으면 위반.
   #550 [ast]  배치 면제는 «생성»에만 — 조회로 꺼낸 것들의 save_all 이면 위반.
   #565 [ast+] 후보: 도메인 Enum 값이 유스케이스·서비스 이름과 겹침 — 「업무가 이 단계
               이름을 입으로 부르나」(워크플로 위장 신호).
 
 단순화(정직 기록): #269/#270 의 «읽힘»은 BC 파일 텍스트의 이름 등장으로 잰다. #546 의
 타입 해소는 파라미터·__init__ 애너테이션의 `*Repository` 이름과 import 경로 대조다.
+트랜잭션 영역은 표준 UoW 주입·factory·별칭과 Django atomic의 AST 범위로 한정한다.
+같은 repository 타입의 여러 인스턴스는 구별하지 않으며 미해소 영역은 통과 증명이 아니다.
 
 이관 계약(명세 조각 ⓐ): 채택 신호 2원(#78) · 대상 0건 가드(#74) · ImportError
 fail-closed · ⓓ 후보 exit 불산입.
 
 사용법: check-domain-model.py [TARGET_DIR]   (기본: 현재 디렉터리)
 종료코드: 0=clean(또는 표준 미채택) · 1=사용/분석 오류 · 2=blocker(발견 출력)
 구조화 레코드: DJR_FINDINGS_JSON=<경로> 지정 시 findings.py(공용 모듈)가 JSON lines 를
 추가 방출한다 — 라인 출력·exit 의미론 무변(T0 B2).
 
 그래프 좌표(T2-2): 규범 정본 = 온톨로지 그래프(`ontology/rules/`) · 이 검사기의 #N ↔ Work 조인은
@@ -537,22 +540,24 @@
             if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) \
                     and (node.target.id == "id" or node.target.id.endswith("_id")):
                 cand.add("#259", _rel(root, py, node.lineno),
                          f"값 객체 `{cls.name}` 이 식별자 `{node.target.id}` 를 가진다 — "
                          "식별자를 갖고 값이 바뀌어도 같은 것이면 그것은 엔티티다",
                          "Q4 — 이것이 값인가 엔티티인가")
                 break
         closed_enum, enum_based = _closed_standard_enum(mod, cls)
         if not closed_enum and (not has_validation or enum_based):
             cand.add("#268", _rel(root, py, cls.lineno),
-                     f"`{cls.name}` 의 __init__/__post_init__ 에 raise 가 없다 — 값 객체는 "
-                     "만들어지는 시점에 스스로 검증한다",
+                     (f"`{cls.name}` 의 닫힌 표준 Enum 생성 검증을 확정할 수 없다 — "
+                      "custom/open 생성 경로를 검토한다" if enum_based else
+                      f"`{cls.name}` 의 __init__/__post_init__ 에 raise 가 없다 — 값 객체는 "
+                      "만들어지는 시점에 스스로 검증한다"),
                      "Q2 — 이 타입 조합만으로 잘못된 값이 «불가능»한가")
 
 
 def _check_domain_events(root: Path, bc: Path, agg: Path, ev_dir: Path, f: Findings) -> None:
     bc_texts: dict[Path, str] = {}
     for py in _py_files(bc):
         try:
             bc_texts[py] = py.read_text(encoding="utf-8")
         except (OSError, UnicodeDecodeError):
             continue

```

## dddjango/scripts/check-port-adapter-pairing.py

Before SHA256: b6bcf57161a163e072fd9fb18a47bd11f1122ef2792ffc0d1f48a1cc215c522a
After SHA256: 9fe24b4df8df90a6cdfdf53d735a805db830c02830a50f7ec6ae791b007c5b5b

```diff
--- before/dddjango/scripts/check-port-adapter-pairing.py
+++ after/dddjango/scripts/check-port-adapter-pairing.py
@@ -28,21 +28,22 @@
          #352 폴더 아님 · #354 Django<Aggregate>Repository · #356 thin read 는 domain 비
          의존 · #359 Django<Capability>DomainBypassQuery · #365 acl 은 우리 BC 이름만 ·
          #367 소켓 여는 import 는 external_system 어댑터 안뿐(목록은 데이터 — 닫지 않는다) ·
          #368[ast+] 값의 자리에 기계(후보) · #369 벤더=폴더 · #370 <System><Capability>
          Adapter · #371~#373 나머지 어댑터 자리·이름 · #464 command/query 분할 금지 ·
          #477 리포지토리 구현은 domain import 필수 · #582 패키지는 기술을 말한다 ·
          #651 고정 역할의 클래스별 파일·상수 묶음 ·
          #583 양방향 1:1 은 셋뿐 · #545 save() 는 «안 꺼낸 사실» 가드 · #551 계약은
          ABC+@abstractmethod · #552 구현은 계약 상속 · #553[ast+] 어댑터의 업무 판정(후보) ·
          #554 계약이 선언한 실패로 · #555 벤더 예외 그대로 흘림 금지 · #556 재시도 기계는
-         framework 몫 · #557 벤더 오류 코드 판정은 어댑터 안뿐
+         framework 몫 · #557[ast+] code/errno/status_code 비교 수신자의 확인된 vendor 출처는 확정,
+         확인된 domain 또는 application의 command/query/result/port 계약은 허용, 미해소·혼합 출처는 후보
   fake   #575 test/fake/ 에만 · #576 짝 선언 없는 페이크(한 방향) · #577 선언 상속·같은
          이름 · #578 기술 만지면 어댑터 · #579 프로덕션의 페이크 import · #580
          dependency_wiring 의 페이크 주입 · #581 평평하게
   기타   #134 컨트롤러는 build_* 만(직접 생성 금지) · #574 <data>_in 생성은 어댑터만 ·
          #71(=#304·#305·#8)·#40(=#403·#408·#219·#220)·#463(=#319)·#480(dto 이름 — usecase-dto
          관할과 자리 분리해 port 구역만) — 참조·중복 진단 금지 원칙대로 실체는 한 곳만.
 
 이관 계약(명세 조각 ⓐ): 채택 신호 2원(#78) · 대상 0건 가드(#74) · ImportError
 fail-closed · ⓓ 후보 exit 불산입.
 

```

## codex-dddjango/skills/dddjango/scripts/check-port-adapter-pairing.py

Before SHA256: b6bcf57161a163e072fd9fb18a47bd11f1122ef2792ffc0d1f48a1cc215c522a
After SHA256: 9fe24b4df8df90a6cdfdf53d735a805db830c02830a50f7ec6ae791b007c5b5b

```diff
--- before/codex-dddjango/skills/dddjango/scripts/check-port-adapter-pairing.py
+++ after/codex-dddjango/skills/dddjango/scripts/check-port-adapter-pairing.py
@@ -28,21 +28,22 @@
          #352 폴더 아님 · #354 Django<Aggregate>Repository · #356 thin read 는 domain 비
          의존 · #359 Django<Capability>DomainBypassQuery · #365 acl 은 우리 BC 이름만 ·
          #367 소켓 여는 import 는 external_system 어댑터 안뿐(목록은 데이터 — 닫지 않는다) ·
          #368[ast+] 값의 자리에 기계(후보) · #369 벤더=폴더 · #370 <System><Capability>
          Adapter · #371~#373 나머지 어댑터 자리·이름 · #464 command/query 분할 금지 ·
          #477 리포지토리 구현은 domain import 필수 · #582 패키지는 기술을 말한다 ·
          #651 고정 역할의 클래스별 파일·상수 묶음 ·
          #583 양방향 1:1 은 셋뿐 · #545 save() 는 «안 꺼낸 사실» 가드 · #551 계약은
          ABC+@abstractmethod · #552 구현은 계약 상속 · #553[ast+] 어댑터의 업무 판정(후보) ·
          #554 계약이 선언한 실패로 · #555 벤더 예외 그대로 흘림 금지 · #556 재시도 기계는
-         framework 몫 · #557 벤더 오류 코드 판정은 어댑터 안뿐
+         framework 몫 · #557[ast+] code/errno/status_code 비교 수신자의 확인된 vendor 출처는 확정,
+         확인된 domain 또는 application의 command/query/result/port 계약은 허용, 미해소·혼합 출처는 후보
   fake   #575 test/fake/ 에만 · #576 짝 선언 없는 페이크(한 방향) · #577 선언 상속·같은
          이름 · #578 기술 만지면 어댑터 · #579 프로덕션의 페이크 import · #580
          dependency_wiring 의 페이크 주입 · #581 평평하게
   기타   #134 컨트롤러는 build_* 만(직접 생성 금지) · #574 <data>_in 생성은 어댑터만 ·
          #71(=#304·#305·#8)·#40(=#403·#408·#219·#220)·#463(=#319)·#480(dto 이름 — usecase-dto
          관할과 자리 분리해 port 구역만) — 참조·중복 진단 금지 원칙대로 실체는 한 곳만.
 
 이관 계약(명세 조각 ⓐ): 채택 신호 2원(#78) · 대상 0건 가드(#74) · ImportError
 fail-closed · ⓓ 후보 exit 불산입.
 

```

## dddjango/scripts/design_pregate.py

Before SHA256: 50b530a0fa498fdb3d19650e790d758ae2cae2740a6bd914a132362e1902dabd
After SHA256: 4d0dcb064ee6a7b49dfb7b7a1b8dd15fb707b2179a17601d4d29b2f58e8b66a8

```diff
--- before/dddjango/scripts/design_pregate.py
+++ after/dddjango/scripts/design_pregate.py
@@ -2449,29 +2449,29 @@
     if m is None:
         return None
     lo: "tuple[int, int]" = (int(m.group(1)), int(m.group(2)))
     if sys.version_info[:2] >= lo:
         return None
     return (f"실행기 인터프리터 py{sys.version_info[0]}.{sys.version_info[1]} < 대상 하한 {lo[0]}.{lo[1]} — 계약 실존 ⑶ 판정의 "
             f"파싱 실패는 판정 불능으로 병기된다(실행기를 대상 venv 인터프리터로 실행하면 사라진다)")
 
 
 BLIND_SPOTS: "tuple[str, ...]" = (
-    "S1 C급(함수 본문·행위 규칙): 스텁 본문이 `...` 뿐이라 예보 표면 밖이다.",
-    "S2 ④형(명세 내부 의미 모순·규범 과잉결정): 검출 대상이 아니다.",
+    "S1 C급(함수 본문·행위 규칙): 생성 본문은 미검증이다. 정확한 생성 위치/슬롯 결합의 #376/#645/#647만 별도 보고하며 실제 구현 검증을 대신하지 않는다.",
+    "S2 ④형(명세 내부 의미 모순·규범 과잉결정): 명시 read-only/UoW와 출처 결합 DTO의 선언 확정/후보 밖은 미검증이다.",
     "S3 BC 내부 계층 의존(#92/#93류): 유도 삽입은 규약 준수형이라 예보 불가 · 블록에 기재된 경계 import 는 스텁에 "
     "방출되어 예보된다 — 산문에만 적힌 경계 import(블록 미기재)는 전사되지 않아 표면 밖이다 · 전사는 add 소비자와 "
-    "새 함수가 전사되는 실존 OHS 서비스 update의 안전한 import만이다(나머지 update는 실존 판정만 받는다).",
+    "새 함수가 전사되는 실존 OHS 서비스 update의 안전한 import만이다. 명시 import/별칭/타입을 결합한 선언 검증은 물리 전사와 별개이며 나머지 update 본문은 미검증이다.",
     "S4 앵커·상태 축: 예보 기준선은 «스텁 제외 현재 상태»다 — G2 build_anchor 차분과 다르며, "
     "HEAD 판형 게이트 결과의 G2 증거 유용은 차분 세탁으로 금지된다.",
     "S5 미시뮬레이션: update는 실존 OHS 서비스의 명시 새 모듈 함수·안전한 import·파일 수준 raise helper만 "
-    "전사한다. 기존 signature/body·decorator/alias/class 변경과 나머지 update·후행 remove(@Ln)는 위 목록 병기.",
+    "전사하고, 정적으로 해소된 module pytestmark 최종 목록을 반영한다. add/update 명시 선언 후상태는 별도 검사하며 기존 signature/body·decorator/alias/class 본문 변경, 효과 무기재, 지원 밖 marker/base/client와 후행 remove(@Ln)는 미검증으로 위 목록 병기.",
     "S6 정형 보충(apps.py name/label·모델 Meta.db_table·마이그레이션 칸): 결손 시 규약 유도값을 합성한다 — 기계 블록 "
     "전사가 있으면 전사 우선이지만, «산문»으로만 규약 밖 값을 계획한 일탈은 예보 표면 밖이다.",
     "S7 기실현 add(`--base` 명시 시 — 명시 `--base HEAD` 포함): 사본 = 기준선 트리 + (worktree−HEAD) 오버레이 — 기준선 "
     "이후 커밋분은 사본에 없다. 오버레이 실존 add 는 앵커 커밋 전에 걷어내고 스텁으로 실체화해 예보하므로(앵커 스냅숏 "
     "무오염·실물 판정 혼입 0 — 커밋된 add 와 같은 ID·exit) 실물이 스텁과 다른 위반은 예보 표면 밖이고, 유일 판정자는 "
     "G2 앵커 차분이다.",
     "S8 계약 실존(boundary-imports 3단): 판정 기준은 **이 브랜치**의 격리 사본(기준선 + dirty overlay + 이 명세의 add — "
     "`--base` 명시 시 기준선 이후 커밋분은 사본에 없다: 재발화 판형)이다 — 다른 워크트리·미머지 브랜치의 실물은 보지 "
     "않는다(부재 = 결손 · 상류 소유 계약의 선행 대기는 `deferred` 처분으로 명세가 소유 레인·해소 조건을 명시한다). "
     "자기 add 대상의 이름 정의(⑶)는 symbols 채널 소관이라 생략하고, update 대상은 symbols 선언 이름을 자기 update 해소로 "

```

## codex-dddjango/skills/dddjango/scripts/design_pregate.py

Before SHA256: 50b530a0fa498fdb3d19650e790d758ae2cae2740a6bd914a132362e1902dabd
After SHA256: 4d0dcb064ee6a7b49dfb7b7a1b8dd15fb707b2179a17601d4d29b2f58e8b66a8

```diff
--- before/codex-dddjango/skills/dddjango/scripts/design_pregate.py
+++ after/codex-dddjango/skills/dddjango/scripts/design_pregate.py
@@ -2449,29 +2449,29 @@
     if m is None:
         return None
     lo: "tuple[int, int]" = (int(m.group(1)), int(m.group(2)))
     if sys.version_info[:2] >= lo:
         return None
     return (f"실행기 인터프리터 py{sys.version_info[0]}.{sys.version_info[1]} < 대상 하한 {lo[0]}.{lo[1]} — 계약 실존 ⑶ 판정의 "
             f"파싱 실패는 판정 불능으로 병기된다(실행기를 대상 venv 인터프리터로 실행하면 사라진다)")
 
 
 BLIND_SPOTS: "tuple[str, ...]" = (
-    "S1 C급(함수 본문·행위 규칙): 스텁 본문이 `...` 뿐이라 예보 표면 밖이다.",
-    "S2 ④형(명세 내부 의미 모순·규범 과잉결정): 검출 대상이 아니다.",
+    "S1 C급(함수 본문·행위 규칙): 생성 본문은 미검증이다. 정확한 생성 위치/슬롯 결합의 #376/#645/#647만 별도 보고하며 실제 구현 검증을 대신하지 않는다.",
+    "S2 ④형(명세 내부 의미 모순·규범 과잉결정): 명시 read-only/UoW와 출처 결합 DTO의 선언 확정/후보 밖은 미검증이다.",
     "S3 BC 내부 계층 의존(#92/#93류): 유도 삽입은 규약 준수형이라 예보 불가 · 블록에 기재된 경계 import 는 스텁에 "
     "방출되어 예보된다 — 산문에만 적힌 경계 import(블록 미기재)는 전사되지 않아 표면 밖이다 · 전사는 add 소비자와 "
-    "새 함수가 전사되는 실존 OHS 서비스 update의 안전한 import만이다(나머지 update는 실존 판정만 받는다).",
+    "새 함수가 전사되는 실존 OHS 서비스 update의 안전한 import만이다. 명시 import/별칭/타입을 결합한 선언 검증은 물리 전사와 별개이며 나머지 update 본문은 미검증이다.",
     "S4 앵커·상태 축: 예보 기준선은 «스텁 제외 현재 상태»다 — G2 build_anchor 차분과 다르며, "
     "HEAD 판형 게이트 결과의 G2 증거 유용은 차분 세탁으로 금지된다.",
     "S5 미시뮬레이션: update는 실존 OHS 서비스의 명시 새 모듈 함수·안전한 import·파일 수준 raise helper만 "
-    "전사한다. 기존 signature/body·decorator/alias/class 변경과 나머지 update·후행 remove(@Ln)는 위 목록 병기.",
+    "전사하고, 정적으로 해소된 module pytestmark 최종 목록을 반영한다. add/update 명시 선언 후상태는 별도 검사하며 기존 signature/body·decorator/alias/class 본문 변경, 효과 무기재, 지원 밖 marker/base/client와 후행 remove(@Ln)는 미검증으로 위 목록 병기.",
     "S6 정형 보충(apps.py name/label·모델 Meta.db_table·마이그레이션 칸): 결손 시 규약 유도값을 합성한다 — 기계 블록 "
     "전사가 있으면 전사 우선이지만, «산문»으로만 규약 밖 값을 계획한 일탈은 예보 표면 밖이다.",
     "S7 기실현 add(`--base` 명시 시 — 명시 `--base HEAD` 포함): 사본 = 기준선 트리 + (worktree−HEAD) 오버레이 — 기준선 "
     "이후 커밋분은 사본에 없다. 오버레이 실존 add 는 앵커 커밋 전에 걷어내고 스텁으로 실체화해 예보하므로(앵커 스냅숏 "
     "무오염·실물 판정 혼입 0 — 커밋된 add 와 같은 ID·exit) 실물이 스텁과 다른 위반은 예보 표면 밖이고, 유일 판정자는 "
     "G2 앵커 차분이다.",
     "S8 계약 실존(boundary-imports 3단): 판정 기준은 **이 브랜치**의 격리 사본(기준선 + dirty overlay + 이 명세의 add — "
     "`--base` 명시 시 기준선 이후 커밋분은 사본에 없다: 재발화 판형)이다 — 다른 워크트리·미머지 브랜치의 실물은 보지 "
     "않는다(부재 = 결손 · 상류 소유 계약의 선행 대기는 `deferred` 처분으로 명세가 소유 레인·해소 조건을 명시한다). "
     "자기 add 대상의 이름 정의(⑶)는 symbols 채널 소관이라 생략하고, update 대상은 symbols 선언 이름을 자기 update 해소로 "

```
