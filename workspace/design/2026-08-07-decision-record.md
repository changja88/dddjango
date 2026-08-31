# 결정 기록 — 각 칸을 왜 그렇게 정했나

정본 `docs/file_tree.html` 은 **플러그인을 쓸 사람에게 공개하는 문서**라 이 기록을 담지 않는다.
근거 · 버린 안 · 뒤집은 판단은 **여기가 유일한 보관소**다.
고칠 자리는 `docs/mkrev2.py` 의 `CARDS` 이고 이 파일은 생성물이다 — `PYTHONUTF8=1 python3 docs/mkrev2.py`.
정본 트리의 **D 표식에 마우스를 올리면** 같은 내용이 툴팁으로도 뜬다.

---

## D53 · 입구의 1차 축은 «누가»가 아니라 «어떤 전송으로»다 — 웹훅이 처음으로 둘을 갈랐다

**확정 · 08-09 · T44** · 자리 — <b>트리 120 → 124행</b> &nbsp;·&nbsp; <code>api/webhook/&lt;provider&gt;/</code> &nbsp;·&nbsp; <b>죽은 문장 둘 삭제</b> &nbsp;·&nbsp; 흐름 번호 12곳 재매핑

<dl class="kv">
<dt class="ans-dt">물음 — <b>토스 결제 웹훅이 갈 칸이 없다</b></dt>
<dd class="ans-dd filled">외부 결제사가 <code>POST /webhooks/payments/toss</code> 로 「결제됐다」를 보낸다. 넷을 다 대 봤는데 전부 아니다.
<div class="pre-wrap"><pre><code>api/                 「바깥 «사람이» 부르는 HTTP」      → 토스 서버는 사람이 아니다     ✘
open_host_service/   「다른 «BC» 가 부른다」              → 토스는 우리 BC 가 아니다      ✘
cron_job/            「«스케줄러»가 부르는 정기 실행」      → 스케줄러가 아니다            ✘
event_subscription/  「남의 published_event/ 말고는 ✗」   → 우리 BC 들끼리다             ✘</code></pre></div>
<b>그런데 같은 칸의 행 note 는 「외부(HTTP) 입구」라 <code>api/</code> 가 맞다고 한다</b> — 한 칸이 자기 안에서 두 답을 준다.
게다가 트리가 「<b>새 종류의 행위자가 실제로 생기기 전에는 자식이 늘지 않는다</b>」고 못 박아 놨는데 웹훅 발신자는 정확히 새 종류다.</dd>

<dt>축이 셋으로 흔들리고 있었다</dt>
<dd><div class="pre-wrap"><table class="mini">
<tr><th>어디</th><th>뭐라고 적혔나</th><th>축</th></tr>
<tr><td><code>api/</code> 행</td><td>외부(HTTP) 입구</td><td><b>전송</b></td></tr>
<tr><td>패널 inn</td><td>바깥 «사람이» 부르는 HTTP</td><td>행위자</td></tr>
<tr><td><code>WHAT[7]</code></td><td>자식은 «행위자 종류»로 갈린다</td><td>행위자</td></tr>
<tr><td>패널 goal</td><td>자식 목록이 곧 «행위자가 몇 종류인가»의 답</td><td>행위자</td></tr></table></div>
<b>여태 안 드러난 까닭은 행위자와 전송이 1:1 로 붙어 있어서다</b> — HTTP=사람 · 함수 호출=타 BC · celery=스케줄러 · 브로커=남의 사실.
<b>웹훅이 처음으로 둘을 갈랐다</b>: <b>행위자는 새 종류인데 전송은 기존 것</b>이다.</dd>

<dt class="ans-dt">결정 ① <b>1차 축은 «어떤 전송으로 오나»</b></dt>
<dd class="ans-dd filled"><b>바꿔도 기존 넷이 하나도 안 무너진다</b> — HTTP · 같은 프로세스 함수 호출 · celery · 브로커로 <b>넷 다 전송이 다르다</b>.
그리고 <b>확장에 더 강하다</b>: 외부가 gRPC 로 부르면 <b>정본 트리 개정으로</b> 형제가 늘고, SQS 로 보내면 <code>event_subscription/</code> 이 이미 브로커라 그쪽이다.
반대로 「행위자」 축이면 <code>webhook/</code> 안에 gRPC 를 넣어야 해 <b>이름이 깨진다</b>.
<br><b>★ 원전이 이 구분을 «병»으로 지목한다.</b> Cockburn 의 Motivation —
<em>“it becomes impossible to shift from a <b>human-driven use of the system to a batch-run system</b>; For still the same reason,
it becomes difficult or impossible to allow the program to be <b>driven by another program</b> when that becomes attractive.”</em>
<b>「사람이 부르면 <code>api/</code>」는 이 패턴이 고치려는 그 구분을 구조에 새긴 것이었다.</b>
<br>그가 primary/secondary 를 가르는 자도 하나다 — <em>“The distinction between primary and secondary lies in
<b>who triggers or is in charge of the conversation</b>.”</em> <b>«사람이냐»는 어디에도 없다.</b>
그리고 사람·테스트 하네스·배치 드라이버·원격 HTTP 앱·다른 로컬 앱을 <b>같은 포트에 꽂히는 여러 어댑터</b>로 한 줄에 나열하며,
<em>“…pretending briefly that <b>all external items are identical from the perspective of the application</b>.”</em> 이라 적는다.</dd>

<dt class="ans-dt">결정 ② <b>2차 축은 «계약을 누가 소유하나»</b> — <code>api/webhook/&lt;provider&gt;/</code></dt>
<dd class="ans-dd filled"><b>전송이 같으니 지붕은 <code>api/</code> 하나다</b> — 라우터·미들웨어·인증이 한 기계를 쓴다.
<b>그 아래에서 «누가 부르나»가 갈린다.</b>
<div class="pre-wrap"><pre><code>api/
  api_router.py         ← 웹훅 라우트도 여기서 꽂는다
  bc_error_schema.py          ← BC 당 «정확히» 한 파일이라 웹훅과 무관
  &lt;area&gt;/            계약 주인 = 우리
  webhook/&lt;provider&gt;/   계약 주인 = 바깥        ← 신설</code></pre></div>
<b>«1차가 둘이 된 것»이 아니다</b> — <code>application_layer/</code> 가 <code>&lt;area&gt;/</code> 옆에 <code>port/</code> 를 두는 것과 <b>같은 꼴</b>이고,
그 근거(<b>D14</b> 「주인이 하나가 아닌 것이라 형제」)가 여기 그대로 걸린다.
<b>검사도 선다</b> — 「<code>api/</code> 아래 폴더 중 <code>webhook/</code> 이 아니면 area」라 <b>area 이름 목록을 몰라도 경로 문자열로 판정된다</b>.
<br><b>★ Evans 가 이 방향을 직접 다룬다.</b>
<em>“There are cases, however, when the other subsystem may need to <b>request something of your subsystem or notify it of some event</b>.
An ANTICORRUPTION LAYER <b>can be bi-directional</b>…”</em> — 그리고 전송과 번역을 갈라 놓는다:
<em>“…it shouldn’t be confused with an ANTI-CORRUPTION LAYER, <b>which is not a mechanism for sending messages</b>…”</em> ·
<em>“These are implementation and deployment decisions… <b>They have no bearing on the conceptual role</b>.”</em>
<b>그래서 전송(라우트·서명)은 입구가, 번역은 컨트롤러의 첫 줄이 진다.</b></dd>

<dt>이 칸이 지는 규칙 넷 — 지금까지 «한 칸에만» 있거나 아예 없던 것</dt>
<dd><div class="pre-wrap"><table class="mini">
<tr><th></th><th>규칙</th><th>T44 전</th></tr>
<tr><td>서명 검증</td><td><code>framework/&lt;technology&gt;/</code> 인증 틀로 붙인다 — 라우트 데코레이터라 <b>세 줄을 안 건드린다</b></td><td>자리는 있고 규칙 0</td></tr>
<tr><td>멱등</td><td>발신자가 재시도한다 — <b>애그리거트가 그 사실을 든다</b>(진행표 ✗)</td><td><code>cron_job/</code> 에만</td></tr>
<tr><td>예외</td><td>「답을 내려고」가 아니라 <b>「재시도를 멈추려고」</b> 잡고 <b>ack</b> 로 답한다</td><td><code>cron_job/</code> 에만(T38)</td></tr>
<tr><td>스키마</td><td><b>우리가 못 고친다</b> — 허용 key 닫기·이름 규칙이 <b>안 걸린다</b></td><td>없음</td></tr></table></div>
<b>4xx 로 답하면 발신자가 며칠을 재시도한다</b> — 이것이 <code>&lt;area&gt;_controller.py</code> 와 갈리는 유일한 점이다.</dd>

<dt>기각 셋</dt>
<dd><b>⑴ 다섯째 입구(<code>driving_layer/webhook/</code>)</b> — 전송이 같은데 지붕을 둘로 나누면 라우터가 갈린다.
<br><b>⑵ 이름 대칭(<code>api/external_system/</code> ↔ <code>driven_layer/external_system/</code>)</b> —
<b>★ 사용자가 잡았다</b>: 「대칭시키면 external 로 들어온 요청이 external(driven) 에 있는 걸 써야 할 것 같다」.
실제로 <b>D11</b> 이 컨트롤러의 <code>driven_layer/**</code> import 를 <b>금지</b>하므로
<b>이름이 금지된 경로를 가리키게 된다</b>. 그리고 둘은 <b>같은 «대화»가 아니다</b>(한쪽만 있을 수도 있다) — <b>D37</b> 의 1:1 짝맞춤과 다르다.
<br><b>⑶ <code>api/inhouse/</code> + <code>api/webhook/</code> 대칭</b> — 얻는 것은 「1차 예외가 없어진다」인데 <b>그 예외가 애초에 없었고</b>(위 ②),
㉠ 파트너 공개 API 가 생기면 <b>이름이 거짓말</b>이 되고(축은 「사내냐」가 아니라 「계약 주인」이다) ㉡ 웹훅 없는 BC 에서 <b>가를 것이 없는 폴더</b>가 되고
㉢ 모든 BC 의 컨트롤러 경로가 한 겹 깊어진다.</dd>

<dt>딸려 걷은 죽은 문장 둘</dt>
<dd><b>⑴</b> 「<b>넷째 입구가 필요해 보이는 순간은 그 껍데기가 «조율»을 시작할 때인데, 그건 새 칸이 아니라 «입구에 로직 금지» 위반이다</b>」 —
<b>D40</b> 이 <b>넷째 입구를 실제로 열었다</b>(4차 리뷰 C-3b).
<b>⑵</b> 「브로커가 들어와 통합 이벤트를 소비하게 돼도 같다: 그 task 는 <code>open_host_service/</code> 를 부르는 얇은 껍데기다」 — 같은 이유로 죽었다.
<br><b>부수 — 2장 흐름의 행 번호 12곳이 낡아 있었다.</b> <code>_st()</code> 는 재매핑을 받아 왔는데 <b><code>fbox(…, r=N)</code> 은 한 번도 안 받았다</b>
(<code>r=53</code> 이 <code>&lt;aggregate&gt;.py</code> 를, <code>r=31</code> 이 <code>cron_job/</code> 을 가리키고 있었다). <b>라벨 기준으로 12곳을 다시 매겼다.</b>
<span class="dim">검사법 — 렌더된 HTML 에서 <code>class="fgo"</code> 의 <code>data-r</code> 과 <code>rd-N</code> 이름을 대조한다. 43건 중 템플릿 이름은 정상 불일치라 거른다.</span></dd>

<dt>규율 ⑤ — 미리 적어 두는 둘</dt>
<dd><b>⑴</b> 여기는 <b>HTTP 로 오는 것만</b>이다. 외부가 큐나 gRPC 로 보내면 그건 <b>다른 전송</b>이라 <b>여기 넣으면 위반</b>이고, 받을 칸은 <b>정본 트리를 «개정»해야</b> 생긴다 — <b>BC 가 스스로 형제를 늘리지 않는다</b>(08-11 · C6).
<b>⑵</b> 파트너용 <b>공개 API</b> 가 생겨도 <b>계약 주인이 우리</b>라 <code>&lt;area&gt;/</code> 쪽이다 — 새 칸이 아니다.</dd>
</dl>

## D52 · 실패는 «층마다» 다른 일을 한다 — 「재시도 판정 → framework/」가 셋을 한 낱말에 뭉치고 있었다

**확정 · 08-09 · T42** · 자리 — <b>트리 행 신설 0</b> &nbsp;·&nbsp; 행 둘(<code>port/unit_of_work/</code> · <code>&lt;aggregate&gt;/exception/</code>) &nbsp;·&nbsp; <b>D14 정정 둘</b> &nbsp;·&nbsp; D12 표식

<dl class="kv">
<dt class="ans-dt">물음 — <b>D14 가 자기 안에서 부딪혔다</b></dt>
<dd class="ans-dd filled"><div class="pre-wrap"><table class="mini">
<tr><th>같은 카드가</th><th>적은 것</th></tr>
<tr><td>분류</td><td>저장 실패는 셋으로 갈린다 — 업무 의미→도메인 예외 · <b>재시도 판정→<code>framework/</code></b> · 나머지→선언 안 함</td></tr>
<tr><td>배치</td><td>「중복 · <b>낙관적 락 충돌</b> → <code>domain_layer/&lt;aggregate&gt;/exception/</code>」</td></tr>
</table></div>
<b>락 충돌은 재시도 대상인데 «업무 의미» 쪽으로 보냈다.</b> 그리고 받는 폴더의 정의가 <em>「불변식 위반의 이름」</em> 이라 <b>담기지도 않았다</b>.</dd>

<dt class="ans-dt">★ 사용자가 물었다 — <b>「재시도 판정 → <code>framework/</code>? DB 는 driven 에 있는데 왜 framework 가 나오나」</b></dt>
<dd class="ans-dd filled"><b>맞는 지적이고, 플러그인이 이미 다르게 정해 놨다.</b> <code>discipline-houserules</code> <em>final.md</em> §193 <b>transient 짝 조항</b>:
<div class="pre-wrap"><pre><code>raw OperationalError 같은 미승인 인프라 실패는 published 오류로 감싸거나
… 분류하지 않는다. HTTP까지 도달하면 framework의 미식별 500이 기본이다.
안정된 공개 의미가 승인된 실패만 owning infra/ACL이 자기 BC의 구체
domain/application exception으로 정규화하고, 그 BC controller가 직접 매핑한다.</code></pre></div>
<b>「owning infra」 = driven 어댑터다.</b> 판정도 번역도 거기서 한다. 그리고 결정적 백스톱 <code>check-transient-overmapping</code> 이 <b>「영구장애 구별 분기 없이 통째로 503/409 로 매핑」을 blocker 로 잡는다</b> — 「일시적인가」는 <b>그 기술을 아는 곳에서 갈라야 한다</b>고 이미 강제하고 있었다.
<br><b class="dim">※ §193 의 「framework」는 <b>django/ninja 프레임워크</b>를 말하는 것이지 트리의 <code>framework/</code> 폴더가 아니다. <b>D14 가 그 둘을 겹쳐 읽은 것으로 보인다.</b></b></dd>

<dt class="ans-dt">결정 — <b>세 가지가 서로 다른 층의 일이다</b></dt>
<dd class="ans-dd filled"><b>「재시도 판정 → <code>framework/</code>」 한 줄이 셋을 뭉치고 있었다.</b>
<div class="pre-wrap"><pre><code>driven      기술 실패를 «계약이 선언한 실패»로 번역한다              ← D51
            「일시적인가 / 영구인가」도 여기서 가른다                  ← 그 기술을 아는 유일한 곳
            승인 안 된 것은 번역하지 않는다 → 미식별 500              ← 플러그인 §193

domain      아무것도 «하지» 않는다 — 「무엇이 옳은가」만
            실패의 «이름»만 domain_layer/&lt;aggregate&gt;/exception/ 에 산다

application 실패를 받아 «되돌리기 · 보상»을 한다                      ← D48 ①

driving     «다시 부를지» 정한다
              HTTP → 409 를 준다 (사용자가 다시 시도)
              워커 → 다시 부른다 (멱등이 이미 필수 · D48 ②)

framework   재시도 «기계»만 준다 (백오프 · 횟수) — 판정이 아니라 도구</code></pre></div>
<b>재시도가 도메인에 못 사는 까닭</b> — 사용자가 <em>「재시도 로직은 domain 에서」</em> 를 제안했는데 <b>여기만 갈렸다</b>. 다시 시도하려면 <b>트랜잭션을 다시 열고</b>(UoW 는 <code>application_layer/port/</code> 에 있다) <b>리포지토리를 다시 불러야</b> 하는데, 도메인은 리포지토리를 «선언»만 하고 «호출»은 유스케이스가 한다. <b>도메인에 두면 도메인이 트랜잭션과 리포지토리 호출을 알게 되어 전역 제약 ①이 깨진다.</b>
<br><b>재시도는 «다시 부르는» 일이고, 도메인은 «부르는 쪽»이 아니다.</b> 「한 번 더 해 봐라」는 절차이지 업무 규칙이 아니다.</dd>

<dt>낙관적 락 충돌은 <b>도메인 예외가 맞다</b></dt>
<dd>D14 자신이 이미 근거를 적어 놨다 — <em>「중복」과 「낙관적 락 충돌」은 <b>도메인 사실</b>이다: 「이 값은 유일하다」·「내가 읽은 뒤 남이 바꿨다」</em>. <b>틀린 것은 배치가 아니라 «폴더 정의»였다.</b>
<div class="pre-wrap"><pre><code>옛 정의   불변식 위반의 이름
새 정의   이 애그리거트를 저장하지 못하게 만든 «업무적 사실»의 이름
          — 불변식 위반이 대부분이고, DB 가 «대신 지켜 주는» 것도 여기다</code></pre></div>
<b>실용적으로도 그래야 한다</b> — 컨트롤러가 이 실패를 갈라 409 로 바꾸려면 <b>그 타입을 import 할 수 있어야</b> 하는데, 도메인 예외만 그게 된다(<code>port/</code>·<code>framework/</code> 직접 참조는 막혀 있다). 플러그인도 같은 자리를 적는다 — <em>「그 BC controller가 직접 매핑한다」</em>.
<br><b>다만 문은 좁다</b> — 플러그인은 <b>「승인된 실패만」</b> 정규화하라고 못 박는다. <b>기본은 번역하지 않고 미식별 500</b>이다.</dd>

<dt>★ 세 번째다 — <b>사용자가 «한 층 위»를 물어서 풀렸다</b></dt>
<dd>내가 물은 것은 <b>「락 충돌 예외가 어디 사나」(칸 하나)</b> 였고, 사용자가 물은 것은 <b>「층마다 무엇을 처리하나」(그 답을 정하는 규칙)</b> 였다. 규칙을 세우니 칸이 저절로 정해졌고, <b>덤으로 D14 의 「재시도 판정 → <code>framework/</code>」가 틀렸다는 것까지 나왔다</b>.
<br><span class="dim">같은 일이 <b>D49</b>(「사실인데 반드시 도달해야 한다는 칸이 없다」)와 <b>D50</b>(「애그리거트의 정의부터」)에서도 있었다.</span></dd>
</dl>

## D51 · 어댑터는 «계약이 선언한 실패»로 바꿔 내보낸다 — 「도메인 예외 금지」는 지킬 대상이 0이었다

**확정 · 08-09 · T36** · 자리 — <b>트리 행 신설 0</b> &nbsp;·&nbsp; <code>adapter/</code> 검사 셋(③④⑤) &nbsp;·&nbsp; <b>D45 정정 넷</b>

<dl class="kv">
<dt class="ans-dt">물음 — <b>규칙 둘이 정면으로 부딪히고, 한쪽은 지킬 대상이 0이었다</b></dt>
<dd class="ans-dd filled"><div class="pre-wrap"><table class="mini">
<tr><th>어디</th><th>무엇을 적었나</th></tr>
<tr><td><code>adapter/</code> 검사 ⑤</td><td>「<b>도메인 예외를 던지면 위반</b> — 포트 예외로 «번역해서» 던진다」</td></tr>
<tr><td><b>D14</b></td><td>「중복 · 낙관적 락 충돌 → <code>domain_layer/&lt;aggregate&gt;/exception/</code> — <b>어댑터가 번역해서 던진다</b>」</td></tr>
</table></div>
<b>더 나쁜 점 — 번역할 «포트 예외»가 리포지토리에는 존재하지 않는다.</b> 같은 D14 가 「<code>exception.py</code> 는 여기 두지 않는다」로 그 자리를 없앴다. <b>즉 이 규칙은 지킬 수 있는 대상이 0이었다.</b></dd>

<dt class="ans-dt">★ 사용자 물음이 답을 좁혔다 — <b>「DB 작업인데 왜 도메인 예외를 던지나」</b></dt>
<dd class="ans-dd filled"><b>처음에 나는 「그건 판정이라 위반」이라고 답했다. 틀린 답이었다.</b>
<div class="pre-wrap"><pre><code>DB 가 말한 것        IntegrityError(constraint="uq_user_email")
어댑터가 하는 것      「이 이메일은 이미 있다」를 도메인의 말로 «옮긴다»
도메인에 도착하는 것   EmailAlreadyTaken</code></pre></div>
<b>어댑터는 「이 이메일이 중복인가」를 «결정하지» 않는다 — DB 가 결정했다.</b> 어댑터는 그 사실의 <b>이름만</b> 바꾼다. 그것이 Cockburn 의 <em>converts</em>(바꾸고) 그 자체이고, 이 칸이 금지한 «판정»은 <b>「조건을 보고 갈래를 고르는 것」</b>이다.
<br><b>그리고 정보가 어댑터에만 있다</b> — <em>“The <b>repository is the only code that knows</b> it talks to Doctrine. So the catch belongs there.”</em> · <em>“Your business logic knows the MySQL error code for a duplicate key… The day you move to Postgres, that number changes to <code>23505</code>, and your use case is <b>wrong everywhere it guessed</b>.”</em>
<br><b>반례 하나로 결판난다</b> — 한 애그리거트에 유니크 제약이 <b>둘</b>이면(email · username), 포트 예외 <code>AlreadyExists</code> 만 올려서는 <b>유스케이스가 어느 쪽인지 알 수 없다</b>. 제약 → 업무 의미의 매핑을 아는 코드는 어댑터뿐이라 <b>위로 올리면 정보가 사라진다</b>.</dd>

<dt class="ans-dt">결정 — <b>갈래를 적지 않는다. 규칙 하나면 둘이 자동으로 갈린다</b></dt>
<dd class="ans-dd filled"><b>「기술 실패는 «자기가 구현한 계약이 선언한 실패»로 바꿔 내보낸다.」</b>
<div class="pre-wrap"><pre><code>리포지토리 어댑터
  계약이 사는 곳   domain_layer/&lt;aggregate&gt;/&lt;aggregate&gt;_repository.py
  → 선언된 실패    domain_layer/&lt;aggregate&gt;/exception/            = 도메인 예외

능력 어댑터
  계약이 사는 곳   application_layer/port/&lt;capability&gt;/
  → 선언된 실패    application_layer/port/&lt;capability&gt;/exception.py = 포트 예외</code></pre></div>
<b>「계약이 어디 사느냐」가 답을 정한다.</b> 리포지토리 계약은 트리가 이미 도메인에 두기로 했으므로(「<code>port/</code> 밖에 있는 유일한 계약」) 그 실패도 도메인 것이다. <b>예외 조항도 갈래도 아니고, 이미 있는 규칙의 귀결</b>이며 같은 칸의 형제 검사(「자기 선언을 상속한다」·「파일 이름이 선언과 같다」)와 <b>같은 축</b>이다.
<br><b>옛 규칙의 걱정은 살린다</b> — 「업무 규칙을 어겼다」와 「바깥이 죽었다」가 같은 <code>except</code> 에 걸리면 안 된다. <b>날것의 django·SDK 예외를 그대로 올리면 위반</b>이라는 쪽이 그 걱정을 그대로 담고, <b>그물만 좁아졌다</b>.</dd>

<dt>같이 고친 것 둘 — <b>검사가 정상 코드를 잡고 있었다</b></dt>
<dd><b>④ 재구성 면제</b> — 리포지토리가 저장된 행을 애그리거트로 되살릴 때 <code>order.add_line(…)</code> 을 부르는 것은 「도메인에게 시킨」 것이 아니다. <b>가르는 물음은 「인자로 받았나, 내가 만들었나」</b> 이고 <code>ast</code> 로 갈린다.
<br><b>③ «근사» 표기를 행으로</b> — 「판정이 없다」는 <b>이름 없는 판정</b>(<code>if payload.amount &gt; 100_000</code>)을 못 잡는다. 이 고백이 <b>툴팁 안에만</b> 있었는데, 이 문서 자신의 규율이 <em>「카드 본문은 정본에 안 들어간다 — 강제는 행/패널에」</em> 라 <b>한계 표기가 카드에만 있는 것은 그 규율을 어긴 것</b>이다.</dd>

<dt><b>D45</b> 정정 넷 — <b>결론은 다 서고 근거가 갈렸다</b></dt>
<dd><div class="pre-wrap"><table class="mini">
<tr><th>무엇</th><th>어떻게</th></tr>
<tr><td><b>facade ↔ adapter 를 맞바꿔 읽었다</b> — 「facade 는 «프로토콜을 감추는» 역할」이라 적었는데 <b>프로토콜을 맞추는 것은 adapter 의 일</b>이고 facade 는 «거친 인터페이스를 간추리는» 것이다</td><td><b>더 센 근거로 교체</b> — facade 가 간추릴 것이 없다(우리 상대는 <code>open_host_service/</code> 계약으로 이미 깎인 표면). <b>2차 자료 넷에 기대는 «우리 판단»</b>이라고 적었다 — Evans 원문 축자는 못 구했다</td></tr>
<tr><td><b>Martin «판정» 침묵 논증</b> — 「원전 셋 다 «판정»이라는 낱말이 <b>없다</b>」. 반례가 원전 안에 있다 — 같은 링에 <em>“if buttons should be <b>disabled</b> or not”</em> 을 판정하는 <b>Presenter</b> 가 산다</td><td>결론은 살리고 <b>«우리 결정»으로 표기</b></td></tr>
<tr><td><b>Evans 인용이 Blue Book 이 아니다</b> — <em>“encapsulated the translation…”</em> 은 <b>2007년 실무 보고서</b>다</td><td><b>인용 표식을 뗐다.</b> 대체 문장(DDD Reference p.34)은 <b>원문 확인 전이라 아직 안 붙인다</b></td></tr>
<tr><td><b><code>port/&lt;capability&gt;/exception.py</code> «필수»는 원전에 없다</b> — Cockburn 의 포트 정의에 <b>실패 선언이 없고</b>, 그는 예외를 누가 소유하는지 말하지 않는다</td><td><b>«우리 결정»</b>이다. 원전이 준 것처럼 서 있던 문면을 고쳤다</td></tr>
</table></div></dd>

<dt>떼어 낸 것 하나 — <b>T42 (같은 날 닫혔다 · <b>D52</b>)</b></dt>
<dd><b>D14</b> 가 <b>자기 안에서 부딪힌다</b> — 저장 실패를 「업무 의미 → 도메인 예외 · <b>재시도 판정 → <code>framework/</code></b> · 나머지 → 선언 안 함」 셋으로 갈라 놓고, 같은 카드가 <b>「낙관적 락 충돌 → <code>domain_layer/…/exception/</code>」</b> 이라 적는다. <b>락 충돌은 업무 규칙 위반이 아니라 재시도 대상</b>이고, 받는 폴더의 정의(<em>「불변식 위반의 이름」</em>)와도 안 맞는다.
<br><b>이 카드의 규칙은 그와 무관하게 선다</b> — 「계약이 «선언한» 실패」라서 그 안에 무엇이 들어 있든 문장이 같다. <b>별건으로 뗀다.</b></dd>
</dl>

## D50 · 애그리거트 경계 = 트랜잭션 경계 — 규칙은 «정의»이고, 검사는 «경계가 틀렸다»는 신호다

**확정 · 08-09 · T35** · 자리 — <b>트리 행 신설 0</b> &nbsp;·&nbsp; 행 셋(<code>&lt;aggregate&gt;/</code> · <code>&lt;aggregate&gt;_repository.py</code> · <code>&lt;use_case&gt;_use_case.py</code>) &nbsp;·&nbsp; <code>&lt;aggregate&gt;/</code>·<code>unit_of_work/</code> 의 «무엇이 오나» &nbsp;·&nbsp; 1장 «규칙 셋»→«넷» &nbsp;·&nbsp; <b>D43 정정 넷</b>

<dl class="kv">
<dt class="ans-dt">물음 ⑴ — <b>검사기를 실제로 돌려 봤더니 안 선다</b></dt>
<dd class="ans-dd filled">D43 의 검사는 <em>「한 <code>with unit_of_work:</code> 안에서 «서로 다른» 리포지토리에 쓰기가 둘이면 위반」</em> 이다. 돌려 본 결과:
<div class="pre-wrap"><table class="mini">
<tr><th></th><th>코드</th><th>왜</th></tr>
<tr><td><b>오탐</b></td><td><code>repo = self._order_repository</code> 로 <b>별칭</b>을 만들고 둘 다 저장</td><td><b>같은</b> 리포지토리인데 배치 면제가 깨진다 <b>→ 타입이 같아 «하나»로 센다</b></td></tr>
<tr><td><b>오탐</b></td><td><code>self._audit_log.save(…)</code> + <code>self._order_repository.save(…)</code></td><td>감사 로그는 <b>애그리거트</b> 리포지토리가 아니다 <b>→ 타입이 <code>&lt;aggregate&gt;_repository.py</code> 에서 안 왔다</b></td></tr>
<tr><td><b>오탐</b></td><td><code>self._order_repository.save(order)</code> + <code>order.lines.remove(line)</code></td><td>뒤엣것은 도메인 객체의 메서드다 <b>→ 같은 까닭으로 빠진다</b></td></tr>
<tr><td>미탐</td><td>루프 · 사설 메서드 경유 · <code>with</code> 없이</td><td>통과한다</td></tr>
</table></div>
<b>원인이 한 줄이다</b> — 카드가 「검사가 서려면 «무엇이 쓰기인가»를 기계가 알아야 한다」를 <b>스스로 발견해 메서드 이름은 닫아 놓고</b>, 똑같이 필요한 <b>«무엇이 리포지토리인가»는 안 닫았다</b>.<br><b>★ 08-11 · C7 — 답도 한 줄이었다.</b> 세는 대상은 «리포지토리»가 아니라 <b>«애그리거트 리포지토리»</b>다. <b>D50 이 「애그리거트 = 트랜잭션 경계」라 못 박았으니 애그리거트를 안 가진 것은 애초에 셈에 들어오지 않는다</b> — 타입이 <code>domain_layer/&lt;aggregate&gt;/&lt;aggregate&gt;_repository.py</code> 에서 온 것만 세면 <b>위 오탐 셋이 한꺼번에 사라진다</b>. <b>근거는 이미 트리 안에 있었다</b> — <code>domain_bypass_query/</code> 칸이 <em>「이 칸은 애그리거트를 안 거치므로 <b>리포지토리가 아니다</b>」</em> 로 자기를 이미 뺐다. <span class="dim">「감사 로그가 어디 사나」는 이 물음이 아니었다 — 그 코드는 4차 리뷰가 <b>검사기를 돌려 보려고 지은 것</b>이고 저장소에도 트리에도 없다. 「리포지토리가 «아니다»」라고만 적고 «왜 아닌지»를 안 적어서 <b>읽는 사람이 「그럼 무엇이냐」로 가게 만든 것</b>이 진짜 결함이었다.</span></dd>

<dt class="ans-dt">★ 물음 ⑵ — <b>그리고 규칙이 «왜» 그런지를 한 글자도 안 적고 있었다</b></dt>
<dd class="ans-dd filled">사용자가 물었다 — <em>「UoW 가 트랜잭션을 관리할 수 있는데 왜 애그리거트 둘을 못 바꾸나. 도메인 서비스는 애초에 여러 애그리거트를 다루는 것 아닌가」</em>. <b>정당한 물음이었고, 문서에 답이 없었다.</b>
<br><b>원전이 답한다 — 애그리거트는 «정의상» 트랜잭션 경계다.</b> Vernon, <em>Effective Aggregate Design Part I</em>:
<div class="pre-wrap"><pre><code>“An invariant is a business rule that must always be consistent…
 When discussing invariants, we are referring to transactional consistency.”

“Thus, aggregate is synonymous with transactional consistency boundary.”</code></pre></div>
<b>그러면 「한 트랜잭션 = 한 애그리거트」는 임의의 제약이 아니라 «정의를 다시 말한 것»이다.</b> 어길 수 있다는 것은 어긴 게 아니라 <b>선을 잘못 그었다</b>는 뜻이고, 그래서 Vernon 이 <em>“a strong indication that your <b>consistency boundaries are wrong</b>… it is <b>waving its hands and shouting at you</b>”</em> 라고 쓴다.
<br><b>Part I 전체가 그 실제 사례다</b> — 팀이 <code>Product</code> 를 큰 덩어리 하나로 묶었더니 서로 상관없는 두 작업(백로그 계획 · 릴리스 일정)이 계속 충돌했다. 진단은 <em>“designed with <b>false invariants</b> in mind, not real business rules… <b>artificial constraints imposed by developers</b>”</em> 였고, 고친 방법은 트랜잭션이 아니라 <b>덩어리를 넷으로 쪼갠 것</b>이었다 — <em>“we've solved the transaction failure issue by <b>modeling it away</b>.”</em>
<br><b>그래서 판정 하나를 신설했다</b> — <b>「서로 «다른 일»을 하는 두 사용자가 이 경계 때문에 충돌하면 위반」</b>. 지금까지 트리에는 <b>「걸렸을 때 어디로 가나」(Evans 의 「그 사용자 «자신»의 일인가」)만 있고 그 «앞» 단계가 없었다</b>.</dd>

<dt class="ans-dt">물음 ⑶ — <b>「도메인 서비스는 여러 애그리거트를 다루지 않나」</b></dt>
<dd class="ans-dd filled"><b>다룬다. 그러나 «참조»와 «수정»은 갈린다.</b> Vernon, Part II 축자:
<div class="pre-wrap"><pre><code>“Use a repository or domain service to look up dependent objects
 ahead of invoking the aggregate behavior.
 A client application service may control this, then dispatch to the aggregate”

“…referencing multiple aggregates in one request does not give license
 to cause modification on two or more of them.”</code></pre></div>
<b>도메인 서비스는 «미리 찾아보고», 바꾸는 것은 애그리거트 하나다.</b> 그리고 조정 주체는 <b>application service</b> 라고 원전이 못 박는다 — <b>이 트리는 구조로 이미 강제하고 있다</b>: <code>unit_of_work/</code> 는 <code>application_layer/port/</code> 에 있어 도메인이 볼 수 없다(전역 제약 ①).
<br><b>반대 진영도 실재한다</b> — Richardson: <em>“I don't interpret [it] as requiring a database transaction to a single aggregate”</em> · <em>“limiting each transaction to a single domain <b>demonstrably adds complexity</b> without any of the upsides of microservices”</em>. <b>그가 말하는 것은 «모듈을 가로지르는 ACID»이고 이 트리는 전역 제약 ③ 으로 이미 금지했다</b> — 실제로 걸리는 범위는 «한 BC 안 애그리거트 둘» 하나뿐이라 그 자리에선 Vernon 이 맞다.</dd>

<dt class="ans-dt">결정 — <b>수단은 «이미 있었다»</b></dt>
<dd class="ans-dd filled">오탐 셋을 없애려면 <code>self._order_repository</code> 의 <b>타입</b>을 알아야 한다. 처음에는 이것을 <b>전역 제약 ④ 로 신설</b>하려 했는데, <b>사용자가 「플러그인이 이미 타입을 강제하고 있을 것」이라고 짚었고 사실이었다</b>.
<div class="pre-wrap"><pre><code>시그니처(인자·반환)   mypy strict --disallow-untyped-defs
모듈·클래스 변수      check-public-surface-annotation.py    ← 시그니처는 «안» 본다
함수 지역 변수        잡는 도구가 없다 — 백스톱을 넓힌다</code></pre></div>
<span class="dim"><b>08-10 · T49 — 이 표가 «틀려» 있었다.</b> <code>check-public-surface-annotation.py</code> 는 <code>FunctionDef</code> 를 만나면 <code>continue</code> 로 <b>함수 본문을 통째로 스킵</b>해 시그니처를 못 본다 — <b>이 검사가 필요로 하는 바로 그것</b>이다. 그리고 §4 는 시그니처 강제를 「타입 검사가 <b>구성돼 있으면</b>」으로 걸어 두고 지역 변수는 「권장」이었다. <b>사용자 결정으로 셋 다 «무조건»이 됐다</b> — 전역 제약 옆의 «전제».</span>
<b>§4.1 이 그 이유까지 적어 놨고, 그것이 정확히 이 검사가 필요로 하는 성질이다</b> — <em>“실익은 <b>생성 결정성과 계약 가독성</b>이다 … <b>AST로 100% 판정돼 런마다 흔들리지 않는다</b>”</em>.
<br><b>그래서 전역 제약은 셋 그대로 두고, 검사가 그 전제를 «인용»한다.</b> 새 규칙이 아니라 <b>이미 선 것 위에 얹는 것</b>이라 논거가 더 세다.
<br><b>기각 — 「신호로 강등」</b>(위반이 아니라 «검토 대상»으로 되돌리기 · 스펙 #255). <b>「검토 대상」으로 내리면 아무도 안 본다</b> — 이 트리의 근본 논거가 Cockburn 의 <em>「약속만 하고 «검출 기계»가 없으면 몇 년 뒤 그 층이 업무 로직으로 가득 찬다」</em> 다. <b>대신 «왜»와 «면제»를 문면이 말하게 해서 임의의 금지로 읽히지 않게 했다.</b></dd>

<dt>D43 정정 넷</dt>
<dd><div class="pre-wrap"><table class="mini">
<tr><th>무엇</th><th>어떻게</th></tr>
<tr><td><b>면제가 «넷»이 아니라 «셋»이다</b> — 원전의 <em>Reason Four: Query Performance</em> 는 <em>“it's best to <b>hold direct object references</b> to other aggregates”</em> 라 <b>«식별자 참조» 규칙의 면제</b>이지 트랜잭션 면제가 아니다</td><td>셋으로 고치고, <b>넷째는 «식별자로만 참조» 줄의 면제로</b> 옮겼다</td></tr>
<tr><td>「<b>우리가</b> 못 쓴다」 — 면제를 <b>이 저장소의 현재 사실</b> 위에서 지웠다. 표준을 읽는 사람에게 「우리」는 <b>자기 팀</b>으로 읽힌다</td><td><b>조건으로</b> — 「<code>broker/</code> 를 연 저장소에선 못 쓴다」 · 「그 조건이 실제로 있을 때만 선다」</td></tr>
<tr><td>배치 면제는 원전에서 <b>«생성»에만</b> 걸리는데 검사는 «수정»까지 통과시켰다. 그리고 <em>user-aggregate affinity</em>(같은 사용자가 그 묶음에만 집중하나) 조건이 빠져 있었다</td><td>둘 다 행에 명시</td></tr>
<tr><td>스펙 #255 는 <em>「위반이 <b>아니라</b> 검토 대상 — 위반 술어가 없다(3차 T13)」</em> 였다. <b>D43 이 뒤집으면서 기록을 안 남겼다</b></td><td><b>여기 남긴다.</b> 술어는 <b>플러그인의 어노테이션 강제</b> 위에서 «있다» — 뒤집은 것이 맞고 근거가 이제 선다</td></tr>
</table></div></dd>

<dt>되돌린 것 둘 — <b>내가 잘못 고쳤다</b></dt>
<dd><b>⑴ 「장고의 FK 접근이 곧 직접 참조라 가장 흔한 경로다」</b> — <b>이 트리에서는 거짓이다.</b> ORM 모델은 <code>persistence/</code> 밖으로 못 나가서(<em>AST 한 줄</em>) <b>도메인은 장고 FK 를 볼 수 없다</b>. 남의 글을 우리 트리에 대보지 않고 옮겼다. 규칙은 살고 근거만 바꿨다 — 실제로 생기는 자리는 <b>매퍼가 남의 루트를 통째로 물려줄 때</b>다.
<br><b>⑵ 「검사가 세는 «쓰기»는 <code>-&gt; None</code> 인 추상 메서드 전부」</b> — <b>되돌렸다.</b> D43 자신이 <em>「리포지토리는 트리가 계약을 통째로 소유한 유일한 포트」</em> 라고 적었다. <b>통째로 소유하면 닫힌 목록은 «병»이 아니라 «정의»다</b>(D46 이 병으로 진단한 것은 «통제하지 못하는 것»을 닫을 때다). 그러면 <code>bulk_upsert</code> 는 검사의 미탐이 아니라 <b>「쓰기는 둘뿐」의 위반</b>이다. 게다가 바꾼 자에는 구멍이 있었다 — <code>def save(self, order) -&gt; Order:</code> 처럼 <b>반환이 있는 쓰기</b>를 놓친다.</dd>
</dl>

## D49 · 사실은 «유실될 수 있다» — 못 지킬 약속이 규칙으로 적혀 있었다

**확정 · 08-09 · T33 · 개정 08-10 · C4** · 자리 — <b>트리 행 신설 0</b> &nbsp;·&nbsp; 행 둘(<code>broker_port.py</code> · <code>&lt;boundary&gt;_unit_of_work.py</code>) &nbsp;·&nbsp; <code>application_layer/</code> 패널 &nbsp;·&nbsp; <b>D40 기각 근거 정정</b><br><b>개정 08-10 · C4</b> — <b>축 신설 0 · 트리 신설 0</b> &nbsp;·&nbsp; <code>application_layer/</code> 패널 &nbsp;·&nbsp; 행 다섯(<code>internal_broker_port.py</code> · <code>&lt;event&gt;.py</code> · <code>cron_job/</code> · <code>open_host_service/</code> · <code>&lt;service&gt;_service.py</code>)

<dl class="kv">
<dt class="ans-dt">물음 — <b>규칙 하나가 못 지킬 약속을 하고 있었다</b></dt>
<dd class="ans-dd filled"><code>broker_port.py</code> 에 <em>「발행 등록이 업무 트랜잭션과 «같은» 트랜잭션에 들어야 한다」</em> 라고 적혀 있었다. <b>「저장됐으면 사실은 반드시 나간다」로 읽히는데 절반만 참이다.</b>
<div class="pre-wrap"><pre><code>롤백됐다  →  사실도 안 나간다        ✔  보장된다
커밋됐다  →  사실이 반드시 나간다     ✘  보장 안 된다</code></pre></div>
원전은 <b>양쪽</b>을 말한다 — <em>“Messages are guaranteed to be sent <b>if and only if</b> the database transaction commits”</em> · <em>“if a service sends a message <b>after committing</b> the transaction there’s no guarantee that it won’t crash before sending the message”</em>. <b><code>on_commit</code> 은 한쪽만 준다.</b></dd>

<dt>새는 창이 «하나가 아니라 셋»이다</dt>
<dd><div class="pre-wrap"><table class="mini">
<tr><th>#</th><th>언제 사라지나</th><th>얼마나</th></tr>
<tr><td>①</td><td>커밋 성공 → 콜백 실행 전에 프로세스가 죽는다. <em>장고 공식 문서: “if your database connection is dropped because your process was killed … your rollback hook will never run”</em></td><td>드묾</td></tr>
<tr><td><b>②</b></td><td><b>앞에 예약된 콜백 하나가 던지면 뒤엣것이 전부 안 돈다.</b> <em>장고 공식 문서: “If one on-commit function registered with <code>robust=False</code> … raises an uncaught exception, <b>no later registered functions in that same transaction will run</b>.”</em> 그리고 <b><code>robust=False</code> 가 기본값</b>이다</td><td><b>흔함</b></td></tr>
<tr><td>③</td><td>리스너 하나가 실패한다 — 「나머지는 간다」는 이미 규칙인데 <b>실패한 그 하나의 기록이 없다</b></td><td>가끔</td></tr>
</table></div>
<b>②는 2장 흐름이 정확히 그 모양이다</b> — ⓑ 확인 메일(<code>uow.after_commit</code>) 다음에 ⑧ 사실 발행. <b>메일 서버가 죽으면 사실 발행이 통째로 사라진다.</b> 아무도 설계한 적 없는 결합이라 판정이 아니라 <b>구현 계약</b>으로 막는다.</dd>

<dt class="ans-dt">★ 결정 — <b>갈림길이 아니었다.</b> <b>D48</b> ①이 이미 답했다</dt>
<dd class="ans-dd filled"><div class="pre-wrap"><pre><code>「이 단계가 실패하면 «내가» 할 일이 있나?」

있다  →  유스케이스가 직접 부른다   →  같은 요청 안에서 돈다  →  «사라질 곳이 없다»
없다  →  브로커로 사실을 공표한다   →  사라져도 «상관없다»고 이미 판정한 것</code></pre></div>
<b>「사실인데 반드시 도달해야 한다」는 칸이 애초에 없다.</b> 그러니 outbox 도, 고를 갈래도 없었다. 남은 것은 <b>못 지킬 약속을 지우는 일</b>과 <b>②라는 실제 결함</b>뿐이다.
<br><b class="dim">※ 정직한 단서 — <b>이 카드를 열게 한 예시가 오분류된 예시였다.</b> 「자녀는 탈퇴했는데 기기가 영영 회수 안 된다」를 문제로 들었는데, <b>그 상황을 못 견딘다면 ①이 이미 «지시»로 보냈어야 한다</b>. 판정을 틀리게 한 예를 들고 와서 배달 장치를 요구한 것이고, 「사라지면 안 되는 건 직접 시켜라」를 <b>새 규칙처럼 내놓아 없던 갈림길을 만들었다</b>. 사용자가 <em>「이건 애초에 발생하는 문제가 아닌 것 같다 — use_case 로 해결하면 되는 것 아니냐」</em> 로 잡았다.</b></dd>

<dt class="ans-dt">★ 개정 <b>08-10 · C4</b> — <b>「못 견딘다」에 «누가»가 빠져 있었다</b></dt>
<dd class="ans-dd filled">위 결정은 <b>보내는 쪽</b>에만 참이다. <b>받는 쪽</b>이 못 견디는 경우가 남아 있었고, 그 자리는 <b>어느 칸으로도 못 갔다</b>.
<div class="pre-wrap"><table class="mini">
<tr><th></th><th>결제 완료 → 정산 일일 마감</th></tr>
<tr><td>①로 판정하면</td><td>결제는 정산이 실패해도 <b>할 일이 없다</b> → 정직하게 «사실»이다</td></tr>
<tr><td>그런데</td><td>알림이 하루 <b>한 건만</b> 사라져도 정산이 안 맞는다</td></tr>
<tr><td>이 카드의 처방</td><td>「그럼 «지시»였어야」 → <b>결제가 정산의 실패를 져야 한다. 못 진다</b></td></tr>
</table></div>
<b>갈래를 하나 이었다 — 축은 안 늘고 트리도 안 는다.</b>
<div class="pre-wrap"><pre><code>보내는 쪽이 못 견딘다  →  처음부터 ①의 «있다»였다 — 직접 부른다

받는  쪽이 못 견딘다  →  그 자료를 «사실»에 기대는 것 자체가 잘못이다
                          받는 쪽이 cron_job/ 으로 깨어나
                          남의 open_host_service/ 에 «묻는다»</code></pre></div>
<b>답은 이 카드가 이미 그은 선 «안쪽»에 있었다</b> — 아래 「고친 것 넷」의 셋째가 <b>이 트리가 다루는 사실은 Event Notification 하나</b>라고 못 박았고,
그 패턴의 정의가 <em>상세를 안 싣고 «필요하면 소스에 되묻는다»</em> 이다. <b>사실은 «깨우는» 것이지 «나르는» 것이 아니다 — 알림이 사라져도 장부는 남는다.</b>
<br><b>둘을 함께 써도 된다</b> — 구독으로 깨어나되 자료는 물어서 얻는다. <em>실무의 정산이 실제로 이 두 겹이다: 놓쳐도 되는 알림 + 시각이 부르는 대사.</em>
<br><b class="dim">※ 리뷰가 든 예시도 화살표가 틀렸다 — 「결제 완료 → 정산 마감」이라 그렸지만 <b>마감을 부르는 것은 결제 완료가 아니라 «자정»</b>이다.
결제가 1,000건 일어나도 마감은 한 번 돈다 — <b>알림과 1:1 이 아니다.</b> 「알림이 사라지면 마감이 안 된다」는 것은
<b>정산이 이미 내 장부의 사본(Event-Carried State Transfer)을 쌓고 있었다</b>는 신호이고, 그것은 이 카드가 <b>관할 밖</b>으로 보낸 그것이다.
<b>같은 병이 이 문서에서 세 번째다</b> — D14 의 「유스케이스가 열고 <b>컨트롤러가 닫는다</b>」에서 주어가 지워져 <code>dto/</code> 가 막혔던 것(T43)과 같은 모양이다.</b></dd>

<dt>그래서 outbox 를 «안» 연다 — 근거가 「나중에」가 아니다</dt>
<dd>발행할 사실을 커밋과 <b>같은 트랜잭션에서 DB 행으로</b> 적고 별도 릴레이가 끝까지 재시도하는 것 — <b>유일하게 「iff」를 주는 방법</b>이다. 대가는 테이블 + 릴레이 + <b>중복 배달</b>이고(<em>“The Message relay might publish a message more than once”</em>), 그러면 <b>모든 구독자가 멱등이어야</b> 한다.
<br><b>안 여는 근거는 「지금 안 쓰여서」가 아니라 「그 칸이 ①에서 이미 «지시»로 갔기 때문」</b>이다. 미결이 아니라 <b>판정으로 닫힌 것</b>이라 규율 ⑤ 를 통과한다.
<br><b>여는 계기는 이미 적혀 있다</b> — 브로커가 «네트워크 너머»로 나가는 때이고, 그 조건(<em>「트랜잭션을 나눠야 하나」</em>)은 <b>D40</b> 가 이미 들고 있다. 그때는 사실만이 아니라 <b>지시도 함께</b> 배달 문제가 된다.</dd>

<dt>고친 것 넷</dt>
<dd><div class="pre-wrap"><table class="mini">
<tr><th>어디</th><th>무엇</th></tr>
<tr><td><code>broker_port.py</code></td><td>검사 셋 → <b>넷</b>. 「같은 트랜잭션」 → <b>「‘반드시 도달’을 기대는 코드가 이 통로에 붙으면 위반」</b> · <b>「실패한 리스너를 삼키면 위반」</b> 신설</td></tr>
<tr><td><code>&lt;boundary&gt;_unit_of_work.py</code></td><td><b><code>on_commit(…, robust=True)</code> 가 아니면 위반</b> — ②를 한 줄로 막는다. <code>connection</code>·<code>transaction</code> 을 아는 유일한 칸이라 자리도 여기다</td></tr>
<tr><td><code>application_layer/</code> 패널</td><td>①의 따름정리(«없다»를 고르는 것은 «유실돼도 된다»까지 고르는 것) + <b>관할 범위</b> — 이 트리가 다루는 사실은 <b>Event Notification</b> 하나이고 ECST · Event Sourcing · CQRS 는 <b>관할 밖</b></td></tr>
<tr><td><b>D40</b> 기각 근거</td><td>signals 를 <b>「전달 보장이 0」</b> 으로 기각했는데 <b>우리 브로커에도 참</b>이라 비대칭이었다 — 근거를 <b>«계약이 없다»·«실패 기록이 없다»</b> 쪽으로 갈랐다</td></tr>
</table></div></dd>
</dl>

## D48 · BC 를 가로지르는 단계 — 물음 «둘»로 자리가 정해진다

**확정 · 08-08 · T34** · 자리 — <b>트리 행 신설 0</b> &nbsp;·&nbsp; 행 넷(<code>&lt;use_case&gt;_use_case.py</code> · <code>broker/</code> · <code>cron_job/</code> · <code>open_host_service/</code>) &nbsp;·&nbsp; <code>application_layer/</code> 패널 &nbsp;·&nbsp; <b>D42 정정 다섯</b>

<dl class="kv">
<dt class="ans-dt">물음 — <b>D42 의 «근거»가 원전 대조에서 무너졌다</b></dt>
<dd class="ans-dd filled"><div class="pre-wrap"><table class="mini">
<tr><th>D42 가 적은 것</th><th>원전</th></tr>
<tr><td>「<b>Vernon 의</b> Process Manager」</td><td>Vernon 책에 <b>0건</b>. <em>“혼동을 피하려고 <b>Long-Running Process</b> 라는 이름을 골랐다”</em>. Process Manager 는 <b>Hohpe·Woolf</b> 것</td></tr>
<tr><td>「진행 상태는 적지 않는다」(Vernon 근거)</td><td>Vernon 이 <b>가장 두텁게 다룬 것이 «적는» 쪽</b>이다</td></tr>
<tr><td>「절차를 애그리거트에 — <b>불가능</b>」</td><td>Vernon 은 <b>그게 가장 단순하다</b>고 한다</td></tr>
<tr><td>「업무가 그 이름을 부를 때만 성립」</td><td><b>원전에 없는 조건</b> — 우리 판단이다</td></tr>
</table></div>
<b>근거가 틀렸으면 결론이 맞아도 다시 연다</b> — <b>D29</b> 가 스스로 세운 규율이다. 다시 열었고, <b>결론은 다시 섰다. 훨씬 센 근거로.</b></dd>

<dt class="ans-dt">답 — <b>물음 둘, 자리 셋</b></dt>
<dd class="ans-dd filled"><div class="pre-wrap"><pre><code>① 이 단계가 실패하면 «내가» 할 일이 있나?          ← 누가 순서를 지나
     있다  →  유스케이스가 «지시»로 직접 부른다      application_layer/&lt;use_case&gt;/
     없다  →  브로커로 «사실»을 공표하고 잊는다      framework/broker/

② 응답을 기다리게 해도 되나?                       ← 언제 도나
     된다     →  그 요청 안에서 돈다
     안 된다  →  그 유스케이스를 워커가 부른다       driving_layer/cron_job/</code></pre></div>
<b>②는 ①과 «별개 축»이다</b> — 지시든 사실이든 워커로 넘길 수 있다. 워커는 «무엇을 하나»가 아니라 «언제 부르나»만 바꾼다.<br>
<b>셋 어디에도 «진행표»는 없다</b> — ①이면 <b>콜 스택이 곧 진행</b>이고, ②면 알 필요가 없다.</dd>

<dt class="ans-dt">★ 「결과를 걱정하면 지시였어야 한다」 — <b>Fowler 가 이름 붙인 함정이다</b></dt>
<dd class="ans-dd filled">이 문장은 우리가 만든 것이 아니다.
<blockquote><em>“A simple example of this trap is when an event is used as a <b>passive-aggressive command</b>. This happens when the source system <b>expects the recipient to carry out an action</b>, and <b>ought to use a command message to show that intention</b>, but styles the message as an event instead.”</em></blockquote>
그래서 <code>framework/broker/</code> 에 <b>「사실을 보내 놓고 그 결과를 «걱정하고» 있으면 위반」</b> 을 박았다. <b>이 한 줄이 진행표를 남발하는 것을 막는다</b> — 「멈추면 큰일 난다」고 느껴지는 순간 그건 애초에 ①이었어야 한다는 신호다.</dd>

<dt>원전 정합 — <b>독자 아키텍처가 아니다</b></dt>
<dd><div class="pre-wrap"><table class="mini">
<tr><th>우리</th><th>원전</th></tr>
<tr><td>②「알 필요 없으면 사실」</td><td>Fowler, <em>Event Notification</em> — <em>“the source system <b>doesn’t really care much about the response</b>”</em></td></tr>
<tr><td>①과 ②를 둘 다 둔다</td><td>Grzybek — <em>“it is best to use <b>Direct Call and Messaging together</b>. Some modules can communicate synchronously and some asynchronously, depending on the need.”</em></td></tr>
<tr><td>① 유스케이스가 직접 부른다</td><td>모듈러 모놀리스 통설 — <em>“cross-module workflows coordinate with events <b>or explicit orchestration through public APIs</b>”</em></td></tr>
</table></div>
<b>Fowler 자신이 ②의 약점도 적어 뒀다</b> — 여러 사실에 걸친 흐름은 <b>코드 어디에도 명시되지 않아 추적이 어렵고</b>, 보려면 «살아 있는 시스템 모니터링»을 봐야 한다. <b>그가 문제만 적고 끝낸 자리에 D42 가 처방을 붙였다</b>(생성물로 체인을 뽑는다).</dd>

<dt>어긋나는 자리 <b>하나</b> — 그리고 그것이 남는 조건이다</dt>
<dd>Richardson 계열은 <b>단순하면 코레오그래피 · 복잡하면 오케스트레이션</b>으로 가르고, <b>그 오케스트레이터는 상태를 저장</b>한다 — <em>“the saga is created, invokes first participant, <b>persists state in DB</b>, waits for a reply”</em>. <b>우리 ①은 오케스트레이션인데 상태를 저장하지 않는다.</b><br>
<b>왜 대개 괜찮은가</b> — 문헌의 참가자는 <b>네트워크 너머</b>라 응답이 나중에 온다. 그래서 «기다리는 동안» 상태를 저장해야 한다. 우리 ①은 <b>같은 프로세스 함수 호출</b>이라 <b>콜 스택이 곧 상태</b>다.<br>
<b>언제 안 괜찮은가 — ②와 겹칠 때다.</b> 워커에서 돌면 요청자는 이미 「접수됐습니다」를 받았고, 워커가 2단계에서 죽으면 <b>아무도 모른다</b>. 그래서 문장으로 못 박았다 — <em>「<code>cron_job/</code> 워커에서 돌면서 단계가 둘 이상이면 그때는 진행을 저장한다」</em>. 자리는 <code>domain_layer/</code> 다.</dd>

<dt>기각 — <b>진행 애그리거트를 «지금» 여는 것</b></dt>
<dd>오는 길에 후보 셋을 지웠다 — <code>cross_context_process/</code> · <code>long_running_process/</code> · 「애그리거트 + 유스케이스 + 구독」 세 조각. <b>판정 물음을 제대로 대니 자리가 안 생겼다</b>: 실패가 «내 일»이면 ①이라 유스케이스가 알고, «내 일이 아니»면 ②라 알 필요가 없다.<br>
<b>「나중에」로 닫은 것이 아니다</b> — 여는 <b>조건</b>(워커 + 2단계 이상)과 <b>자리</b>(<code>domain_layer/</code>)를 둘 다 적었다. 규율 ⑤ 가 벌하는 것은 「안 만든다」가 아니라 「말 안 한다」다.</dd>

<dt>범위</dt>
<dd><b>이 물음은 «BC 사이»에만 적용된다.</b> 외부 시스템이 웹훅으로 나중에 답하는 경우는 「할 일이 있나」로 안 갈린다 — <b>있는데 지금 못 받는 것</b>이라 다른 문제다.</dd>

<dt>세기</dt>
<dd><code>human</code> — ①의 판정(「내가 할 일이 있나」)과 <code>open_host_service/</code> 의 순서 판정.
<code>ast</code> — 「워커가 부르는 유스케이스는 멱등」은 <b>검출이 안 된다</b>(사람 판정). <b>이건 정직하게 적는다.</b>
<code>path</code> — <code>cron_job/</code> 가 부르는 유스케이스 목록은 경로로 뽑힌다.</dd>
</dl>

## D47 · framework/ 는 «링»이 아니다 — 링은 폴더가 아니라 «파일»이 진다

**확정 · 08-08 · T32** · 자리 — <b>트리 117 → 120행</b> &nbsp;·&nbsp; <code>&lt;capability&gt;/exception.py</code> &nbsp;·&nbsp; <code>pure/</code> &nbsp;·&nbsp; 갈래 자 <b>4단</b> &nbsp;·&nbsp; <b>D37 논거 폐기</b>

<dl class="kv">
<dt class="ans-dt">물음 — <b>의존 규칙이 반대로 걸려 있었다</b></dt>
<dd class="ans-dd filled">이 칸을 <em>「클린이 가장 바깥 링을 부르는 이름(<b>Frameworks &amp; Drivers</b>)을 그대로 썼다」</em> 라고 선언해 놓고,
같은 칸의 규칙이 <em>「<b>BC 의 유스케이스는 이 파일만 import 한다</b>」</em> 였다.
<div class="pre-wrap"><pre><code>application_layer/…/use_case  ──import──▶  framework/clock/clock_port.py
        (가장 안쪽)                            (가장 바깥이라고 «선언»한 칸)</code></pre></div>
<b>가장 안쪽이 가장 바깥을 알도록 «규칙이» 강제한다.</b> <code>framework/broker/broker_port.py</code> 도 같은 모양이다.<br>
<b>★ 그리고 그 위에 논거가 쌓였다</b> — <b>D37</b>:
<em>「어댑터만 <code>framework/</code> 로 올릴 수도 없다 — <b>포트를 상속해야 하니</b> «framework → application 0건»이 첫 줄에서 깨진다」</em>.
<b>클린 기준으로 그 «깨짐»이 정상이다</b>(바깥이 안쪽을 안다). 결함을 근거로 삼은 것이고,
<b>D44</b> 가 상속을 강제해 그 전제를 코드로 봉인했다.</dd>

<dt class="ans-dt">★ 원전 둘이 같은 답을 준다 — 그런데 «우리 문제»는 안 다룬다</dt>
<dd class="ans-dd filled">Martin, <em>Clean Architecture</em> 22장 — <em>“Nothing in an inner circle can know anything at all about something in an outer circle.”</em><br>
Cockburn, 2023 슬라이드 8·15·16 — <em>“Driven ports: <b>The app owns the interface</b>”</em> · <em>“B ‘implements’ the interface. <b>A owns the interface definition.</b>”</em><br>
<b>둘 다 「포트는 앱이 갖는다」로 같다.</b> 그런데 <b>원전은 전부 «앱이 하나»라는 전제</b>다.
우리는 BC 가 여럿이고 <code>clock</code> 을 그 여럿이 «공유»한다 — <b>「어느 앱이 이 포트를 소유하나」라는 물음 자체가 원전에 없다</b>.</dd>

<dt class="ans-dt">결정 — <b>구조는 그대로, «이름표»를 뗀다</b></dt>
<dd class="ans-dd filled"><b>틀린 것은 배치가 아니라 이름표와 그 위에 쌓은 논거였다.</b>
<code>&lt;capability&gt;_port.py</code> 는 django 를 <b>한 글자도 안 쓰는 순수 <code>ABC</code></b> 다.
그 파일을 «가장 바깥 링»이라 부르는 것이 파일의 성질과 안 맞았다.
<div class="pre-wrap"><pre><code>링은 폴더가 아니라 «파일»이 진다
   &lt;capability&gt;_port.py       순수 ABC       안쪽
   &lt;technology&gt;_adapter.py    django·SDK    바깥

한 폴더에 살아도 화살표는 «바깥 → 안쪽» 하나뿐이다
그리고 밖으로 나가는 화살표는 composition_root 하나뿐이다</code></pre></div>
<b>「<code>framework/</code> → <code>application/</code> import 0」 규칙은 그대로 산다 — 근거만 바뀐다.</b>
«링»이 아니라 <b>«공용성»</b>이다: <em>공용 코드가 특정 BC 를 알면 그건 이미 공용이 아니다.</em>
이 근거가 훨씬 참이고 검사는 한 글자도 안 바뀐다.<br>
<b>D37 의 «결론»은 오히려 세진다</b> — 계약이 안쪽이고 구현이 바깥이면 <b>둘이 한 폴더에 있어도 방향이 안 어긋난다</b>. 폐기되는 것은 논거 한 줄뿐이다.</dd>

<dt>기각 — <b>계약을 각 BC 의 <code>port/</code> 로 내린다</b></dt>
<dd>원전에 가장 충실하지만 <b>«공유»를 없애야 성립한다</b>. <code>framework/clock/django_adapter.py</code> 가 <b>어느 BC 의 <code>ClockPort</code> 를 상속하나</b> —
N 개를 다 상속하거나 D44 를 여기서만 예외로 둬야 한다.
그리고 <b>D38</b> 의 자격(<em>「뜻을 밖이 정하나」</em>)을 <b>물을 자리가 사라진다</b> —
계약이 BC 마다 따로 살면 그 계약 자체가 «그 BC 의 것»이 되어 버린다.</dd>

<dt>기각 — <b>계약만 모으는 루트 구역을 새로 연다</b></dt>
<dd>가장 정직하지만 <b>루트 구역이 셋이 된다</b>(지금 <code>framework/</code> · <code>&lt;project&gt;/</code> 둘). 위 결정이 같은 일을 <b>이름표 정정만으로</b> 한다.</dd>

<dt class="ans-dt">딸려 잡은 것 넷 — <b>전부 진짜 구멍이었다</b></dt>
<dd class="ans-dd filled"><div class="pre-wrap"><table class="mini">
<tr><th>무엇</th><th>어땠나</th><th>어떻게</th></tr>
<tr><td><b>갈래 자</b></td><td>「이 파일이 «어떤 계약의 <b>구현</b>»인가」가 <code>broker/</code>·<code>test/</code> 를 못 담았다 — <code>broker_port.py</code> 는 계약이라 «아니오»로 기술 폴더에 오판된다</td><td><b>4단</b>으로</td></tr>
<tr><td><b>«실패» 칸 0</b></td><td>형제는 「대화 하나의 어휘 <b>셋</b>(계약·자료·실패)」인데 여기만 안 갔다. <b>어댑터가 번역할 대상이 없으면 django·SDK 예외가 유스케이스로 새어 전역 제약 ②가 깨진다</b></td><td><code>exception.py</code> <b>신설</b></td></tr>
<tr><td><b>이름 규칙 0</b></td><td>D46(누가·언제·어떻게)이 복제가 안 돼 <b><code>smtp_client/</code> 가 통과</b>한다. <b>유스케이스가 그 이름을 직접 import 하므로 여기서 값이 더 센데도</b></td><td>이름 슬롯에 복제</td></tr>
<tr><td><b><code>broker/</code> 세 이름</b></td><td>설명 「계약과 배달이 <b>한 파일</b>에」 ↔ 트리 <code>broker_port.py</code> ↔ D40 카드 <code>broker.py</code>. <b>한 파일이면 «어댑터는 <code>composition_root</code> 밖에서 아무도 import 하지 않는다» 검사의 대상이 0건</b>이 된다</td><td><b>두 파일</b>로 통일</td></tr>
</table></div></dd>

<dt class="ans-dt">★ <code>pure/</code> — <b>「유스케이스가 framework 를 쓸 일이 있나」에서 나왔다</b></dt>
<dd class="ans-dd filled">유스케이스가 <code>framework/</code> 를 쓰는 자리는 <b><code>&lt;capability&gt;/</code> 하나뿐</b>이고(<code>&lt;technology&gt;/</code>·<code>test/</code> 는 입구·조립·테스트가 쓴다),
거기 사는 것은 <b>util 이 아니라 «2차 행위자»</b>다 — 시계·난수·브로커는 <b>밖에 물어보고, 답이 매번 다르다</b>.
포트가 필요한 이유는 갈아끼움이 아니라 <b>테스트에서 «고정»하기 위해서</b>이고, 없애면 셋이 깨진다:
⑴ 유스케이스가 결정적으로 테스트가 안 된다 ⑵ 전역 제약 ②가 깨진다 ⑶ 「어댑터는 <code>composition_root</code> 밖에서 아무도 import 하지 않는다」가 무너진다.<br>
<b>그런데 «순수 계산»은 실재하고 갈 자리가 없었다</b> — 업무 어휘가 0이라 <code>&lt;capability&gt;/</code> 로 밀리면 <b>포트를 요구받고</b>, 라이브러리가 필요 없어 <code>&lt;technology&gt;/</code> 도 아니다.
<b>둘 다 아닌 것이 갈 데가 없었다(규율 ⑤).</b>
<div class="pre-wrap"><pre><code>판정 — 「같은 인자로 두 번 불러 같은 답이 나오고, 부작용이 없나」

  now()              아니오 → 2차 행위자 → &lt;capability&gt;/ · 포트 필수
  uuid4()            아니오 → 2차 행위자
  broker.publish()   아니오(부작용)
  round_half_up(x)   예     → pure/ · 포트 없음
  slugify(s)         예     → pure/</code></pre></div>
<b>포트가 없으면 그건 «어댑터»가 아니다</b>(어댑터 = 포트의 구현). 그래서 파일 이름도 <code>&lt;module&gt;.py</code> 다.</dd>

<dt class="ans-dt">이름 — <b><code>util/</code> 이 아니라 <code>pure/</code></b></dt>
<dd class="ans-dd filled"><b>정본이 이미 <code>util</code> 을 뺐다</b> — <b>D24</b> 가 이름을 세 번 만에 정할 때
<em>「<code>support</code>·<code>util</code>·<code>shared</code> 도 같은 병이라 후보에서 뺐다」</em> 라고 적었고, 기준은 <b>「판정 질문이 곧 이름이 된다」</b> 였다.
<code>pure/</code> 는 그 기준을 그대로 통과한다 — <b>「이 파일이 순수한가?」가 곧 검사 ①②다.</b><br>
<b>그래도 서랍이 될 위험은 남으므로 기계를 단다</b> — Cockburn 이 <em>「약속만 하고 <b>검출 기계가 없으면</b> 몇 년 뒤 그 층이 업무 로직으로 가득 찬다」</em> 고 적은 그 자리다.
<b>결정적인 것은 첫 줄</b>이다: <em>「저장소 안의 다른 파일을 import 하지 않는다」</em> — 그러면 여기 살 수 있는 것은 <b>자기 인자만 보고 답을 내는 함수</b>뿐이라 BC 헬퍼도 설정 상수도 물리적으로 못 들어온다.</dd>

<dt>세기</dt>
<dd><code>path</code> — 갈래 자 4단 · <code>*_port.py</code>/<code>*_adapter.py</code> 금지 · <code>exception.py</code> 존재.
<code>ast</code> — 「저장소 안 다른 파일 import 0」 · 「도메인 예외 상속 안 함」.
<b><code>ast</code> 근사</b> — 「부작용이 없다」(import 목록으로 재므로 <code>__import__</code>·전역 상태는 못 잡는다).
<code>human</code> — 이름 규칙 둘.</dd>
</dl>

## D46 · 포트 이름에는 «바뀔 수 있는 것»을 넣지 않는다 — 누가 · 언제 · 어떻게

**확정 · 08-08 · T1′** · 자리 — <b>트리 행 신설 0</b> &nbsp;·&nbsp; <code>&lt;capability&gt;/</code> 의 «이름» 슬롯 한 곳 &nbsp;·&nbsp; <span class="no">child_eviction_notification/</span> → <span class="yes">device_access_revocation/</span>

<dl class="kv">
<dt class="ans-dt">물음 — <b>규칙이 «누가»만 막고 있었다</b></dt>
<dd class="ans-dd filled">이 칸의 이름 규칙은 <em>「무엇이 필요한가」로 짓고 <b>누가 해 주는지는 넣지 않는다</b>」</em>(<span class="yes">email_sender/</span> ✔ · <span class="no">smtp_client/</span> ✗)였다.<br>
<b>그래서 <code>child_eviction_notification/</code> 이 이 규칙을 «통과»한다</b> — 공급자를 안 넣었으니까. 그런데 이 이름은 <b>계기</b>(<code>child_eviction</code> — 왜 부르나)와 <b>전달 수단</b>(<code>notification</code> — 어떻게 보내나)을 말하고 <b>정작 시키는 일(기기 권한 회수)을 안 말한다</b>.</dd>

<dt class="ans-dt">★ 메서드에는 이미 박혀 있던 자였다 — <b>비대칭</b></dt>
<dd class="ans-dd filled">같은 칸의 <b>메서드</b> 규칙(<b>D39</b>)이 이렇게 센다 — <em>「<span class="no">notify()</span>·<span class="no">handle()</span>·<span class="no">execute()</span> 처럼 <b>무엇을 시키는지 안 말하는 이름은 위반</b>」</em>.<br>
<b><code>notify()</code> 는 위반인데 <code>…_notification/</code> 은 통과하고 있었다.</b> 자가 없었던 게 아니라 <b>한 칸에만 있었다</b>.</dd>

<dt class="ans-dt">결정 — <b>기존 규칙의 «논리»를 그대로 넓힌다</b></dt>
<dd class="ans-dd filled">옛 규칙의 이유는 <em>「공급자를 넣으면 그 능력을 다른 쪽이 맡을 때 <b>유스케이스까지 고치게 된다</b>」</em> 였다. <b>계기와 수단도 정확히 같은 이유로 바뀐다.</b> 그래서 낱말 셋을 한 줄로 묶고 <b>판정 물음</b>을 붙였다.
<div class="pre-wrap"><pre><code>포트 이름에는 «바뀔 수 있는 것»을 넣지 않는다
   누가(공급자) · 언제(계기) · 어떻게(전달 수단)

판정 —「그것이 바뀌어도 이 이름이 그대로인가」

child_eviction_notification/
   계기가 바뀌면?  「부모가 해지해서」도 기기를 회수한다   → 이름이 틀린다  ✗
   수단이 바뀌면?  알림이 아니라 직접 호출이 된다         → 이름이 틀린다  ✗
device_access_revocation/
   계기·수단이 바뀌어도 그대로                                          ✔</code></pre></div>
<b>폴더는 능력의 «명사화», 메서드는 «명령형 동사구»</b> — <code>device_access_revocation/</code> + <code>revoke_for_child()</code>. D39 의 「파일에는 «종류», 함수에는 «의도»」와 결이 같다.
<span class="dim"><code>device_access/</code> 도 후보였는데 <b>「접근을 어쩌라는 건지」가 안 읽혀</b> 뺐다 — 「무엇이 필요한가」에 답하지 못한다.</span></dd>

<dt>기각 — <b>전달 수단 낱말을 «닫힌 목록»으로 막기</b></dt>
<dd><code>_notification</code>·<code>_event</code>·<code>_message</code>·<code>_sync</code> 를 <code>path</code> 검사로 금지하면 기계로 서긴 한다. <b>그런데 <b>D25</b> 가 진단한 병(«규칙을 쓴 게 아니라 목록을 썼다»)을 다시 부른다</b> — 새 수단 낱말이 나오면 조용히 빠져나가고 목록 관리가 일이 된다. <b>판정 물음 하나가 그 낱말들을 전부 자동으로 잡는다.</b></dd>

<dt>세기 — <code>human</code></dt>
<dd>「계기냐 능력이냐」는 기계가 못 가른다. 이름 규칙 대부분이 이미 그렇고(#33 도 <code>human</code>), <b>판정 물음이 있으면 리뷰어가 한 줄로 답할 수 있다</b> — 「이게 바뀌어도 이름이 그대로인가?」</dd>
</dl>

## D45 · 어댑터는 «바꾸고 · 부르고 · 바꾼다» — 그 사이에 판정이 없다

**확정 · 08-08 · T18** · 자리 — <b>트리 행 신설 0</b> &nbsp;·&nbsp; <code>adapter/</code> 에 검사 셋 &nbsp;·&nbsp; <code>framework/&lt;technology&gt;_adapter.py</code> 에 한 줄 &nbsp;·&nbsp; 입구 <code>&lt;area&gt;_controller.py</code> 의 <b>출구 대칭</b>

<dl class="kv">
<dt class="ans-dt">물음 — <b>입구는 못 박혀 있고 출구는 안 박혀 있었다</b></dt>
<dd class="ans-dd filled">정본이 컨트롤러에는 <em>「요청 하나당 메서드 하나. 각 메서드는 «세 줄»이다 — <code>schema_in</code> 을 <code>command</code> 으로 바꾸고, 유스케이스를 한 번 부르고, <code>result</code> 을 <code>schema_out</code> 으로 바꾼다」</em> 라고 적어 놨다. <b>어댑터에 대응하는 문장이 없었다.</b><br>
어댑터 칸들이 하는 말은 전부 «번역»이다 — 「상대의 계약 타입을 우리 도메인 어휘로 옮기는 번역이 여기서 일어난다」·「<code>OrderModel</code> 로우를 <code>Order</code> 로 되돌리고 저장할 때 도로 편다」. <b>번역이 무엇인지는 말하는데 «번역만 한다»는 말이 없었다.</b><br>
<b>D3 이 반쯤 막아 놓은 상태였다</b> — 「어댑터가 <b>유스케이스</b>를 부르면 위반」(제어 흐름이 뒤집힌다). <b>그런데 «애그리거트에게 시키는 것»은 안 막혀 있었다</b> — 한 칸 아래가 뚫려 있었다.</dd>

<dt class="ans-dt">★ 자료조사 — <b>헥사고날의 저자가 «약속만 하는 것»을 실패 양식으로 적어 놨다</b></dt>
<dd class="ans-dd filled">Cockburn 의 <b>Motivation</b> 절 첫 문단이다.<br>
<em>“The attempted solution, repeated in many organizations, is to create a new layer in the architecture, <b>with the promise that this time, really and truly, no business logic will be put into the new layer</b>. However, <b>having no mechanism to detect when a violation of that promise occurs</b>, the organization finds a few years later that the new layer is cluttered with business logic and the old problem has reappeared.”</em><br>
<b>「약속 + 검출 기계」가 한 세트여야 한다</b>는 뜻이라, <b>«한 줄만 적고 끝»은 저자가 이미 실패로 분류해 둔 길</b>이다.<br>
<b>출구 대칭도 저자가 직접 말한다</b> — <em>“An interesting similar problem exists on what is normally considered <b>‘the other side’ of the application</b>, where the application logic gets tied to an external database or other service.”</em></dd>

<dt>어댑터의 일은 <b>«변환»</b> — 원전 셋이 같은 낱말을 쓴다</dt>
<dd><b>Cockburn</b> — <em>“a technology-specific adapter <b>converts</b> it into a usable procedure call or message and <b>passes it to</b> the application”</em> · <em>“an adapter that <b>converts</b> the API definition to the signals needed by that device <b>and vice versa</b>”</em><br>
<b>Martin(클린)</b> — 인터페이스 어댑터 층은 <em>“a set of adapters that <b>convert data</b> from the format most convenient for the use cases and entities, to the format most convenient for some external agency such as the database or the web”</em><br>
<b>Evans(ACL)</b> — <em>“encapsulated the <b>translation</b> of conceptual objects and actions between the two systems, <b>insulating the domain layer from knowing the existence of the other system</b>”</em><br>
<b>셋 다 「변환하고 넘긴다」로 이 칸을 서술한다.</b> 우리 규칙 <em>「바꾸고 · 부르고 · 바꾼다」</em> 는 Cockburn 의 <em>converts … and vice versa</em> 를 그대로 옮긴 것이다.
<br><b class="dim">※ 08-09 · T36(<b>D51</b>) — 옛 문장은 「셋 다 <b>«판정»이라는 낱말이 «없다»</b>」 였다. <b>침묵을 근거로 삼은 것이고 반례가 원전 안에 있다</b> — Martin 의 같은 링에 <em>“labels for buttons, if buttons should be <b>disabled</b> or not”</em> 을 <b>판정하는 Presenter</b> 가 산다. 결론(이 칸은 판정하지 않는다)은 그대로 서지만 <b>그것은 «우리 결정»이지 원전이 준 것이 아니다</b>.</b></dd>

<dt>검사 ② <b>도메인 객체는 «만들고 읽기»만</b> — 근거가 참조 구현에 그대로 있다</dt>
<dd>Microsoft 의 DDD 지속성 층 가이드(eShopOnContainers)다.<br>
<em>“a repository allows you to <b>populate data in memory</b> that comes from the database in the form of the domain entities. Once the entities are in memory, <b>they can be changed</b> and then persisted back.”</em><br>
<em>“your logic operates on domain entities in memory. <b>It assumes the repository class has delivered those.</b> Once your logic <b>modifies</b> the domain entities, it assumes the repository class will <b>store</b> them correctly.”</em><br>
<b>리포지토리는 «전달»하고 «저장»한다 — 「바꾸는」 것은 그 다음 사람의 일이다.</b> 기계 판정은 <b>생성자 · <code>classmethod</code> 팩토리 · 읽기 외의 도메인 메서드 호출</b>이면 위반.</dd>

<dt>검사 ③ <b>기술 실패는 «계약이 선언한 실패»로 바꿔 내보낸다</b></dt>
<dd>트리는 이미 두 칸에 <b>「포트 예외는 도메인 예외를 상속하지 않는다」</b> 를 박아 뒀고, 그 이유는 <em>「업무 규칙을 어겼다」와 「바깥이 죽었다」가 같은 <code>except</code> 에 걸리면 안 된다</em> 였다. <b>걱정은 옳다</b> — 날것의 django·SDK 예외가 안쪽으로 올라가면 정확히 그 일이 벌어진다.
<br><b class="dim">※ 08-09 · T36(<b>D51</b>) — 옛 문장은 <b>「도메인 예외를 던지면 위반 — 포트 예외로 번역해서 던진다」</b> 였고 <b>그물이 너무 넓었다</b>. 리포지토리는 도메인 예외를 던지는 것이 «설계»이고(D14), 그때 던질 «포트 예외»는 존재하지도 않아 <b>지킬 대상이 0인 규칙</b>이었다. 지금 문장은 갈래를 안 적고도 둘을 다 덮는다 — <b>계약이 어디 사느냐가 답을 정하기 때문</b>이다.</b></dd>

<dt>정직한 한계 — <b>②는 근사다</b></dt>
<dd>「무엇이 «행위» 메서드인가」를 기계가 완전히는 못 가린다. 도메인이 읽기 메서드를 프로퍼티가 아닌 일반 메서드로 두면 오탐이 난다. <b>그래서 ①(사람 판정)을 같이 둔다</b> — 기계가 후보를 좁히고 사람이 마무리한다.<br>
<b>불완전한 검출이라도 «약속만»보다 낫다</b> — Cockburn 의 진단대로 실패는 「검출이 부정확해서」가 아니라 <b>「검출이 없어서」</b> 온다.</dd>

<dt>부수 확인 — <b>우리 ACL 이 파일 하나인 것</b></dt>
<dd>Evans 의 ACL 은 원래 <b>셋</b>(facade · adapter · translator)이다. 우리는 <code>&lt;capability&gt;_adapter.py</code> 하나로 접었다. <b>접은 것이 정당하다 — 새로 열 칸 0.</b>
<br><b class="dim">※ 08-09 · T36(<b>D51</b>) — <b>근거가 틀렸었다.</b> 옛 문장은 「<b>facade</b> 는 «프로토콜을 감추는» 역할」이었는데 <b>프로토콜을 맞추는 것은 adapter 의 일</b>이고 facade 는 «지저분한 인터페이스를 간추리는» 것이다. <b>더 센 대체 근거</b> — facade 는 상대의 거친 표면을 간추리려고 있는데 <b>우리 상대는 트리가 이미 <code>open_host_service/</code> 계약으로 깎아 놓은 표면</b>이라 간추릴 것이 없다. <span class="dim">2차 자료 넷이 일관되게 이렇게 적지만 <b>Evans 원문 축자는 확인하지 못했다</b> — 그래서 이 문단은 «우리 판단»이다.</span></b></dd>

<dt><code>framework/&lt;technology&gt;_adapter.py</code> 는 한 줄로 더 세게</dt>
<dd>여기는 <b>도메인을 아예 모른다</b>(<code>framework/</code> → <code>application/</code> import 0). 그래서 위 셋을 따로 적을 것 없이 <b>「도메인 타입이 한 글자도 안 나온다」</b> 한 줄이면 «업무 판정»이 구조적으로 불가능해진다.</dd>

<dt class="ans-dt"><b>여기서 금지하는 «판정»은 «업무» 판정이다 — 기술 분기는 안 걸린다</b> <span class="dim">08-09 · T45</span></dt>
<dd class="ans-dd filled"><b>4차 리뷰가 이 카드를 「모든 분기 금지」로 읽고 캐시를 blocker 로 올렸다</b>(<em>「cache-aside 는 정의상 판정이라 D45 에 정면으로 걸린다」</em>).
<b>그 독법은 이 카드의 검사 셋과 안 맞는다</b> — 셋이 전부 <b>도메인</b>에 관한 것이다(도메인 객체는 «만들고 읽기»만 · 도메인 타입이 한 글자도 안 나온다 · 기술 실패를 계약이 선언한 실패로).
<b>어디에도 「조건문을 쓰면 안 된다」가 없다.</b>
<div class="pre-wrap"><table class="mini">
<tr><th></th><th>예</th><th></th></tr>
<tr><td><b>업무 판정</b> — 걸린다</td><td>「이 주문을 취소해도 되나」 · 「한도를 넘었나」</td><td><b>✘</b></td></tr>
<tr><td><b>기술 분기</b> — 안 걸린다</td><td>캐시 히트 · 재시도 여부 · 배치 크기 · 커넥션 재사용</td><td>✔</td></tr></table></div>
<b>원전이 이 쪽을 직접 지지한다</b> — Evans 는 리포지토리 «안»의 캐시를 <b>이점</b>으로 든다:
<em>“Take advantage of the decoupling from the client… You can take advantage of this to optimize for performance,
by varying the query technique or <b>by caching objects in memory</b>, freely switching persistence strategies at any time.”</em>
Vernon 도 <em>“Repository implementations for relational databases, document stores, <b>distributed cache</b>, and in-memory stores”</em> 라 적는다.</dd>

<dt>그럼 캐시의 선은 어디인가 — <b>«애그리거트»가 아니라 «트랜잭션»</b></dt>
<dd><b>처음엔 「애그리거트는 캐시하지 않는다」로 그으려 했고, 그건 원전과 어긋난다</b>(위 두 인용이 애그리거트 캐시를 허용한다).
<b>원전이 긋는 선은 트랜잭션이다.</b>
<div class="pre-wrap"><pre><code>Evans   캐시 이야기 «바로 다음» 항목이 “Leave transaction control to the client.
        …it will ordinarily not commit anything… the client presumably has the context
        to correctly initiate and commit units of work.”
        → 리포지토리의 캐시 자유는 «트랜잭션이 그어진 상태 안»의 이야기다

Fowler  Identity Map 의 범위가 “a single business transaction”
        이유: “loading the same database record into multiple distinct objects…
        reconciling those changes back to the database becomes problematic and error-prone”

Django  응답 캐시는 “caches GET and HEAD responses with status 200” — 쓰기에 애초에 못 닿는다
        저수준 API 는 “lists of model objects” 를 캐시 예시로 «든다» — 여기가 새는 자리

실증    django-cachalot 1.4.0 — “QuerySet.select_for_update was cached, but it's not correct
        since it does not lock data in the database once data was cached,
        leading to the database lock being useless in some cases”
        → 고친 것은 «모델 캐시»가 아니라 «락 거는 조회» 하나였다</code></pre></div>
<b>그래서 규칙은 한 문장이고 새 규칙도 아니다</b> — <b><b>D50</b>「애그리거트 = 트랜잭션 경계」의 귀결</b>이다.
<b>캐시된 값은 정의상 그 경계가 그어지기 «전»에 만들어진 것</b>이라, 그것으로 저장하면 남이 바꾼 것을 덮는다.
자리는 <code>adapter/persistence/repository/&lt;aggregate&gt;_repository.py</code> 행이고 <b>조회 캐시는 막지 않는다</b>.
<span class="dim">T38·T43 과 같은 모양 — <b>자는 트리에 이미 있었고 이 자리에만 안 걸려 있었다.</b></span></dd>

<dt>여기 답이 «아닌» 것 둘 — 6번(플러그인)으로 넘긴다</dt>
<dd><b>⑴ ORM 자동 캐시</b>(<code>django-cachalot</code>·<code>django-cacheops</code>)는 <b>코드에 한 글자도 안 남는다</b> —
<code>INSTALLED_APPS</code> 와 설정에만 있어서 <b>트리도 AST 검사도 볼 수 없다</b>. 「켤 거면 쓰기 경로를 제외한다」는 <b>플러그인 규칙</b>이다.
<br><b>⑵ 플러그인 <em>implementation-django</em> §12.2 의 예시</b>가 <code>Article</code> 모델을 캐시 키·무효화 대상으로 다룬다 —
<b>조회 모델이면 맞고 애그리거트면 위험한데 단서가 없다</b>. 같은 문서가 <code>select_for_update()</code> 를 길게 다루면서 <b>캐시와의 충돌은 한 줄도 안 적는다</b>.
<span class="dim">캐시 코퍼스는 «비어» 있지 않다 — <b>「쓰는 법」으로 채워져 있고 「두면 안 되는 자리」만 비어 있다</b>.</span></dd>
</dl>

## D44 · 구현은 선언을 «상속»한다 — 주석이 아니라 코드가 말한다

**확정 · 08-08 · T17** · 자리 — <b>트리 행 신설 0</b> &nbsp;·&nbsp; 계약은 <code>ABC</code> + <code>@abstractmethod</code> &nbsp;·&nbsp; <code>adapter/</code> 1:1 검사에 «상속»을 얹는다 &nbsp;·&nbsp; 흐름 시그니처 일곱 정정

<dl class="kv">
<dt class="ans-dt">물음 — <b>트리는 상속을 «전제»하고 결정을 내렸는데, 규칙으로는 0건이었다</b></dt>
<dd class="ans-dd filled">두 자리가 이미 상속 위에 서 있다.<br>
<b><b>D37</b></b> — <em>「어댑터만 <code>framework/</code> 로 올릴 수도 없다 — <b>포트를 상속해야 하니</b> «<code>framework/</code> → <code>application</code> 0건»이 첫 줄에서 깨진다」</em><br>
<b><b>D3</b></b> — <em>「<code>port/</code> 아래 셋은 <b>구현하려고</b> 잡는다(<b>선언을 상속한다</b>). <code>&lt;area&gt;/</code> 는 <b>부르려고</b> 잡는다」</em><br>
<b>D37 은 이 전제 없이는 성립하지 않는다</b> — 구조적 타이핑이면 구현이 계약을 <code>import</code> 할 필요가 없어 「어댑터만 올리면 import 가 생긴다」가 거짓이 된다.<br>
<b>그런데 규칙은 0건이었고, 2장 흐름 넷은 상속 «없이»(주석으로만) 그려져 있었다</b> — <code>class DjangoOrderRepository:</code> <em># 선언과 파일 이름이 같다</em>. <b>「상속 안 한다」를 정한 카드는 없다</b>. <b>D33</b> 의 <em>「ABC 를 가졌나를 볼 필요도 없다」</em> 는 «이게 계약이냐 구현이냐»를 <b>판정할 때</b> 무엇을 보느냐는 답이지 「상속하지 마라」가 아니다. <b>결정이 아니라 사고였다.</b></dd>

<dt class="ans-dt">결정 — <b><code>ABC</code> + <code>@abstractmethod</code>, 구현은 상속 강제</b></dt>
<dd class="ans-dd filled"><b>가독성이 자였다</b> — <code>class SesEmailSenderAdapter(EmailSenderPort):</code> 는 첫 줄이 「무엇의 구현인가」를 말한다. 주석은 검사되지 않고 <b>썩는다</b>(원칙 07).
<div class="pre-wrap"><pre><code># 선언 — application_layer/port/email_sender/email_sender_port.py
class EmailSenderPort(ABC):
    @abstractmethod
    def send(self, notice: CancellationNotice) -&gt; None: ...

# 구현 — driven_layer/adapter/external_system/ses/email_sender_adapter.py
class SesEmailSenderAdapter(EmailSenderPort):
    def send(self, notice: CancellationNotice) -&gt; None: ...</code></pre></div>
<b><code>@abstractmethod</code> 가 없으면 상속해도 소용이 없다</b> — 실측으로 확인했다:
<div class="pre-wrap"><pre><code>abstractmethod 없이 명시 상속 + 미구현 → 인스턴스화 : 됨 (런타임이 안 막는다)
abstractmethod 붙이고  명시 상속 + 미구현 → 인스턴스화 : TypeError
        Can't instantiate abstract class B with abstract method do</code></pre></div>
그래서 <b>둘은 한 몸</b>이다 — 상속만 강제하고 <code>@abstractmethod</code> 를 빼면 «빈 껍데기 구현»이 조용히 통과한다.</dd>

<dt>검사 — <b>1:1 이 «이름»에서 «내용»까지 내려간다</b></dt>
<dd>지금까지 <code>adapter/</code> 의 검사는 <em>「파일 이름이 그 선언과 같다」</em> 하나였고 <b>이름만</b> 봤다. 여기에 <b>「그 선언 클래스를 상속한다」</b> 를 얹으면 <b>선언을 경로에서 유도</b>할 수 있다 — <code>x_adapter.py</code> → <code>port/x/x_port.py</code> 의 <code>XPort</code>. <b>이름은 맞는데 딴 걸 구현한 파일</b>이 이제 걸린다.<br>
<b>범위</b> — <code>driven_layer/adapter/</code> 전부 + <code>framework/&lt;capability&gt;/&lt;technology&gt;_adapter.py</code>. <b>계약 쪽</b>은 <code>port/</code> 한 줄로 묶고, <code>domain_layer/&lt;aggregate&gt;_repository.py</code>(<code>port/</code> 밖에 있는 유일한 계약)와 <code>framework/&lt;capability&gt;_port.py</code> 에만 따로 적었다.</dd>

<dt>기각 — <b><code>Protocol</code> + 명시 상속</b></dt>
<dd>기술적으로는 된다 — <code>Protocol</code> 은 <code>ABCMeta</code> 위에 서 있어 <code>@abstractmethod</code> 를 붙이면 <b>명시 상속한 클래스의 미구현을 런타임이 막고</b>, 그러면서 <b>상속 안 한 테스트 더블은 그대로 통과</b>한다(위 실측의 셋째 줄).<br>
<b>그런데 그 «자유»가 우리에겐 값이 아니라 구멍이다</b> — 가짜가 낡아도 조용히 통과한다는 뜻이기 때문이다. <code>ABC</code> 로 못 박으면 <b>가짜도 계약을 따라가도록 강제</b>되고, 계약이 바뀌면 가짜가 같이 깨진다. 그리고 어차피 <b>구현이 계약을 몰라도 되는 값을 우리는 쓰지 않는다</b> — 어댑터는 같은 저장소 안에서 계약을 import 한다.<br>
<span class="dim">부수 효과 — <b>D14</b> 의 <code>class &lt;Bc&gt;UnitOfWork(ABC):</code> 만 <code>ABC</code> 이고 흐름 셋만 <code>Protocol</code> 이던 <b>어법 갈림이 없어진다</b>.</span></dd>

<dt>딸려 잡은 것 — <b><b>D41</b> 개명이 2장 흐름을 안 훑었다</b></dt>
<dd>경로 넷이 옛 이름 그대로였다 — <code>port/shipment_status/<b>shipment_status.py</b></code> · <code>anticorruption_layer/delivery/<b>shipment_status.py</b></code> · <code>port/email_sender/<b>email_sender.py</b></code> · <code>external_system/ses/<b>email_sender.py</b></code>. 넷 다 <code>_port</code>/<code>_adapter</code> 를 달았다.<br>
<b>재사용할 점검</b> — <b>개명 스윕은 트리 행뿐 아니라 «2장 흐름의 경로»와 «시그니처»까지 훑는다</b>. 흐름은 트리와 다른 자료구조(<code>_st()</code>)라 트리만 고치면 조용히 어긋난다.</dd>
</dl>

## D43 · 한 트랜잭션은 애그리거트 «하나»를 바꾼다

**확정 · 08-08 · T19①** · 자리 — <b>트리 행 신설 0</b> &nbsp;·&nbsp; 검사 셋 + 판정 물음 하나 &nbsp;·&nbsp; 리포지토리 «쓰기»의 <b>판정 둘</b> <span class='dim'>(08-09 · T37 — 옛 «둘뿐»에서 바뀌었다)</span>

<dl class="kv">
<dt class="ans-dt">물음 — <b>트리가 «자기 논거»로 든 규칙 셋 중 하나를 안 적고 있었다</b></dt>
<dd class="ans-dd filled">1장 «왜»가 <em>「애그리거트 경계는 규칙 <b>셋</b>을 만든다 — 바깥에서는 루트만 참조한다 · 애그리거트당 리포지토리는 하나다 · <b>트랜잭션은 애그리거트 하나를 넘지 않는다</b>」</em> 라고 써 놓고, 앞의 둘만 칸에 있었다.
셋째는 정본 전체에 <b>한 번</b>, 그것도 「폴더를 왜 애그리거트로 가르나」의 <b>근거로만</b> 나왔다 — 트랜잭션을 «여는» 칸(<code>&lt;use_case&gt;_use_case.py</code>·<code>unit_of_work/</code>)에는 한 글자도 없었다.</dd>

<dt>자료조사 — <b>진영이 둘이고, 부딪치는 자리가 우리 트리엔 없다</b></dt>
<dd><b>진영 A(Vernon·Evans)</b> — <em>“A properly designed Bounded Context modifies only one Aggregate instance per transaction in all cases.”</em> 다만 Vernon 본인이 <b>깨도 되는 이유 넷</b>을 열거한다: ⑴ UI 편의(배치 생성) ⑵ 메시징 수단 없음 ⑶ 글로벌 트랜잭션 ⑷ 조회 성능.<br>
<b>진영 B(Chris Richardson · 모듈러 모놀리스)</b> — <em>“While this rule makes sense, I don’t interpret [it] as requiring a database transaction to a single aggregate.”</em> 같은 DB 인데 사가를 쓰는 것은 「마이크로서비스의 이점 없이 복잡도만 더한다」.<br>
<b>그런데 B 가 말하는 것은 «모듈을 가로지르는 ACID»</b>이고, <b>우리 트리는 그걸 이미 금지했다</b>(전역 제약 ③ — 남의 BC 리포지토리를 <b>얻을 수단 자체가 없다</b>). <b>그래서 T19① 이 실제로 걸리는 범위는 «한 BC 안 애그리거트 둘» 하나뿐</b>이고, 거기서는 A 가 맞다.<br>
<span class="dim"><code>order</code>/<code>inventory</code> 는 대개 <b>다른 BC</b> 라 우리 트리에선 한 UoW 로 묶는 상황이 <b>발생하지 않는다</b> — ACL → 상대 OHS 를 거치고, 그건 D42 가 정한 체인이다.</span></dd>

<dt class="ans-dt">검사 — <b>서로 다른 리포지토리에 쓰기가 둘이면 위반</b></dt>
<dd class="ans-dd filled"><div class="pre-wrap"><pre><code>✗ 위반 — 서로 다른 애그리거트 리포지토리에 쓰기 둘
with self._unit_of_work:
    self._order_repository.save(order)
    self._coupon_repository.save(coupon)

✓ 정상 — 읽기는 몇 개든 자유
with self._unit_of_work:
    member = self._member_repository.find(member_id)
    order.place(member.grade)
    self._order_repository.save(order)

✓ 정상 — 같은 리포지토리에 여럿 (배치)
with self._unit_of_work:
    for d in descriptions:
        self._backlog_item_repository.save(BacklogItem(d))</code></pre></div>
<b>셋째가 통과하는 것은 임의 완화가 아니라 원전의 면제 ① 그대로다</b> — <em>“if creating a batch of aggregate instances all at once is semantically no different from creating one at a time repeatedly, it represents one reason to break the rule of thumb <b>with impunity</b>.”</em> 그리고 <b>「서로 다른 리포지토리냐 / 같은 리포지토리냐」로 그 면제가 기계적으로 갈린다</b>.<br>
<b>못 잡는 것 — 같은 타입 두 인스턴스</b>(계좌 이체 <code>account_repository.save(from); save(to)</code>). 원전 기준으로도 위반이지만 배치와 구분이 안 돼 <b>사람 판정으로 남긴다</b>.</dd>

<dt class="ans-dt">걸렸을 때 어느 쪽으로 고치나 — <b>Evans 가 준 판정 물음</b></dt>
<dd class="ans-dd filled">Vernon 이 <b>Eric Evans 와 직접 논의해 얻었다</b>고 적은 대목이다.<br>
<em>“ask whether it’s the job of the user executing the use case to make the data consistent. If it is, try to make it transactionally consistent, <b>but only by adhering to the other rules of aggregate</b>. If it is another user’s job, or the job of the system, allow it to be eventually consistent.”</em>
<div class="pre-wrap"><pre><code>한 트랜잭션이 애그리거트 둘을 바꾼다
  ├ 「그 사용자 «자신»의 일」이다   → 애그리거트를 «하나로» 다시 긋는다
  └ 「다른 사람·시스템의 일」이다   → 나눈다 (사실 공표 + 상대가 자기 트랜잭션에서)
  ⇒ 어느 쪽이든 «지금 코드»는 고친다 — 예외로 통과시키는 자가 아니다</code></pre></div>
<b>「그 사람 일이면 그대로 둬도 된다」가 아니다</b> — 뒷 절 <em>“but only by adhering to the other rules of aggregate”</em> 가 그걸 막는다. 트랜잭션 일관성이 필요하다는 것은 <b>애그리거트가 하나여야 한다</b>는 뜻이다.
Vernon 자신의 말도 같다 — <em>“it may be a strong indication that your consistency boundaries are wrong… a concept of your ubiquitous language has not yet been discovered <b>although it is waving its hands and shouting at you</b>.”</em><br>
<span class="dim">Evans 의 원전도 같은 선이다 — <em>[DDD p128] “Any rule that spans AGGREGATES will not be expected to be up-to-date at all times.”</em></span></dd>

<dt>딸려 온 결정 — <b>리포지토리 «쓰기» 메서드 이름을 닫는다</b> <span class="dim">08-09 · T37 에 반쯤 뒤집혔다 — 아래</span></dt>
<dd>검사가 서려면 「무엇이 쓰기인가」를 기계가 알아야 한다. BC 마다 <code>add</code>/<code>store</code>/<code>persist</code> 로 갈리면 <b>검사가 아예 못 선다</b>. <s><code>save()</code>·<code>remove()</code> 둘뿐.</s><br>
<span class='no'>add()</span> 를 안 쓰는 것은 <b>이미 있는 것을 다시 넣을 때 거짓말이 되기 때문</b>이고(Evans 의 컬렉션 은유엔 맞지만), <code>save()</code> 는 신규·수정 둘 다 참이며 <code>Model.save()</code> 와 어휘가 같다. <code>remove()</code> 는 「지운다」가 아니라 <b>「컬렉션에서 뺀다」</b> 라 원전 어휘 그대로다. <b>이 문단은 그대로 산다</b> — 뒤집힌 것은 «둘뿐»이라는 <b>개수</b>다.<br>
<b>D39 의 「포트 메서드는 문법 형태만」에 예외를 하나 만든다</b> — 리포지토리는 <b>트리가 계약을 통째로 소유한 유일한 포트</b>(애그리거트당 하나 · 클래스 이름 고정 · 무엇을 담을지까지 규정)라 어긋나지 않는다.</dd>

<dt class="ans-dt">★ <b>08-09 · T37 — 「이름 고정」과 「개수 한정」이 한 문장에 뭉쳐 있었다</b></dt>
<dd class="ans-dd filled">사용자가 물었다 — <em>「<code>save</code>·<code>remove</code> 만 있는 건 이상해. <code>update</code> 도 있어야 하고 bulk 도 가능해야 해. 그리고 <b>함수 개수를 한정하는 장점이 뭐야?</b>」</em>
<br><b>세어 보니 개수는 이득을 하나도 안 내고 있었다.</b>
<div class="pre-wrap"><table class="mini">
<tr><th>주장한 이득</th><th>「둘」이어야 성립하나</th></tr>
<tr><td>㉮ 기계가 «쓰기»를 셀 수 있다(위 검사가 선다)</td><td><b>아니다</b> — 이름이 <code>save</code>·<code>remove</code> 로 «시작»만 하면 된다</td></tr>
<tr><td>㉯ 리포지토리가 DAO 로 미끄러지지 않는다</td><td><b>아니다</b> — 「인자가 애그리거트인가」가 <b>더 정확히</b> 막는다(<code>save_by_status(...)</code> 도 걸린다)</td></tr>
<tr><td>㉰ 저장할 때 «반드시 하는 일»(낙관 가드·이벤트)이 한 자리에 모인다</td><td><b>아니다</b> — <code>save_all</code> 은 <code>save</code> 와 같은 경로를 탄다</td></tr>
</table></div>
<b>이 병은 세 번째다</b> — <b>D52</b> 가 D14 에서 잡은 「프레임워크」(라이브러리 ↔ 폴더), T39 가 D11 에서 잡은 같은 낱말, 그리고 여기 「쓰기 어휘」(이름 ↔ 개수). <b>규칙 한 문장이 서로 다른 둘을 덮으면, 강한 쪽의 근거로 약한 쪽이 정당화된다.</b>
<div class="pre-wrap"><pre><code>옛   «쓰기» 메서드는 save() · remove() 둘뿐

새   ① 인자가 «애그리거트(또는 그 목록)»인가, «조건·필드»인가
        조건·필드  →  판정이 SQL 로 갔다 = 빈혈        → 위반
     ② 이름이 save · remove 로 «시작»하나            ← 검사가 서는 조건은 이것뿐

     save(주문) · save_all(주문들) · remove(주문)     통과
     update(주문) · bulk_update(조건, 필드)           위반</code></pre></div></dd>

<dt><code>update</code> 를 안 여는 이유 — <b>셋으로 읽히는데 셋 다 열 이유가 안 된다</b></dt>
<dd><div class="pre-wrap"><table class="mini">
<tr><th>무슨 뜻</th><th>왜 안 여나</th></tr>
<tr><td><code>update(주문)</code> — 있는 것만 저장</td><td><code>save()</code> 와 같다. 「없으면 에러」는 낙관 가드가 이미 한다</td></tr>
<tr><td><code>update(id, status=…)</code> — 필드만</td><td><b>애그리거트를 안 거친다.</b> 「배송 시작된 주문은 취소 못 함」이 통째로 건너뛰어진다</td></tr>
<tr><td>insert 와 구분하려고</td><td>Evans 의 <code>add()</code> 자리인데 위 문단이 이미 기각했다</td></tr>
</table></div>
<b>Evans 가 이 안티패턴에 이름을 붙여 놨다</b> — 9·11장의 야간 배치 예제에서:
<em>“At some point, <b>the nightly batch started being a place we swept stuff under the rug</b>. There is <b>domain logic implicit in what the script does</b>, and it’s been getting more and more complicated.”</em>
리팩터링의 이득 목록 셋째가 <em>“<b>Removes domain knowledge (e.g., which ledger to post to) from the script and into the domain layer.</b>”</em> 다.</dd>

<dt class="ans-dt">bulk — <b>Django 소스가 선을 그어 준다</b></dt>
<dd class="ans-dd filled">사용자가 <em>「bulk 로 저장하는 건 django 쪽 기술 문제 같은데」</em> 라고 짚었고, <b>설치된 Django 6.0 소스를 읽으니 그 말이 맞았다</b>.
<div class="pre-wrap"><pre><code>django/db/models/query.py:945-963   bulk_update()

    when_statements.append(When(pk=obj.pk, then=attr))    # 조건은 pk 뿐
    ...
    queryset.filter(pk__in=pks).update(**update_kwargs)   # WHERE 도 pk 뿐

  UPDATE 주문 SET 상태 = CASE WHEN id=101 THEN … END WHERE id IN (…)
                                    ↑ AND version = N 을 «행마다» 끼울 자리가 없다</code></pre></div>
업서트 경로도 막혀 있다 — <code>postgresql/operations.py:374</code> 가 <code>"ON CONFLICT(%s) DO UPDATE SET %s"</code> 만 내고 <b>PostgreSQL 이 지원하는 <code>WHERE</code> 절을 안 붙인다</b>.
<br><b>그런데 이게 «계약»을 닫는 근거는 아니다.</b> 처음에 나는 「Django 가 못 주니 <code>save_all</code> 을 열면 안 된다」고 적었는데, <b>사용자가 <em>「<code>with uow: repo.bulk_save()</code> 로 하면? 안에서는 반복문으로 하나씩 저장하는 거지」</em> 로 뒤집었다</b> — 구현 하나의 한계를 계약 전체로 늘린 것이었다.
<br><b>그리고 계약을 열어야 «가능해지는» 최적화가 있다</b> — 어댑터가 <code>select_for_update()</code> 로 잠그며 현재 version 을 읽고(1 쿼리) 나머지를 <code>bulk_update</code> 로 쓰면(1 쿼리), <b>비관적 락이 낙관 가드를 대신해</b> 500 쿼리가 2 쿼리가 된다. 플러그인도 <em>「고경합 핫 로우는 <b>비관적 락도 고려</b>한다」</em> 로 허용한다. <b>유스케이스가 <code>for: save()</code> 를 돌면 이 최적화가 아예 불가능하다.</b></dd>

<dt><code>add_all</code> 을 열었다가 <b>같은 날 접었다</b></dt>
<dd>한때 <em>「생성 bulk 는 경합이 없으니 <code>add_all</code> 로 열고, 수정 bulk 는 안 연다」</em> 가 결론이었다. 원전(Vernon 의 면제 ①이 «생성»)·트리(<code>&lt;aggregate&gt;/</code> 행의 「«생성»에만 걸린다」)·Django(<code>bulk_create</code> 는 가드가 필요 없다) <b>셋이 같은 선에서 만났기 때문</b>이다.
<br><b>사용자가 접었다</b> — <em>「함수는 <code>save</code> 가 고정이니까 <code>save_all</code> 로 맞추는 게 좋을 것 같아. <code>add</code> 에는 수정은 안 될 것 같은 느낌이기도 해」</em>. <b>그게 바로 위 문단이 <code>add()</code> 를 기각한 이유였다</b> — 「이미 있는 것을 다시 넣을 때 거짓말이 된다」. 복수형이라고 면제되지 않는다.
<br><b>신규와 수정을 가르는 것은 «이름»이 아니라 «구현»이다</b> — 어댑터가 pk 유무로 갈라 신규는 <code>bulk_create</code>, 수정은 루프(또는 <code>FOR UPDATE</code>+<code>bulk_update</code>)로 처리한다. <code>save()</code> 가 이미 하는 일의 복수형이라 새 판정이 아니다.
<br><span class="dim">그 대신 「생성 / 수정」의 선은 <b>어댑터 안의 구현 규칙</b>으로 내려갔다. <code>bulk_create</code> 가 못 하는 것도 그때 확인했다 — m2m 은 따로 붙여야 하고, <code>auto_now</code>·<code>validate()</code> 를 안 태운다. 다중 테이블 상속은 우리가 안 써서 안 걸리고, PostgreSQL 이라 <b>pk 는 채워진다</b>(<code>postgresql/features.py:13</code> · <code>can_return_rows_from_bulk_insert = True</code>).</span></dd>

<dt>정직한 표기 — <b>내가 쓴 「500개」에는 근거가 없었다</b></dt>
<dd>배치 예시에 <code>limit=500</code>·<code>chunk=500</code> 을 반복해서 썼는데 사용자가 물었다 — <em>「왜 500개야?」</em> <b>근거가 없다.</b> 플러그인 예제의 <code>batch_size=500</code> 도 예시 숫자이고, Django 의 기본값 <code>connection.ops.bulk_batch_size()</code> 는 <b>「SQL 파라미터 개수 한도」만</b> 계산한다 — 성능이나 락 시간과 무관하다.
<br><b>적정 크기는 트리가 정할 값이 아니다</b> — 표의 폭·인덱스 수·락 경합·replication lag 이 정하고, 플러그인 <code>architecture-db</code> §11.2 가 <em>「batch 크기와 pause 정책을 정한다」</em> 로 이미 소유한다. 그래서 행에는 숫자를 안 적고 <b>「크기는 부르는 쪽이 정한다」</b> 로만 적었다.</dd>

<dt>대량 «데이터» 채우기의 자리 — <b>migrations 를 제안했다가 철회했다</b></dt>
<dd>업무 규칙이 0인 대량 변경(「기존 100만 행에 기본값 채우기」)의 자리로 <code>migrations/</code> + <code>RunPython</code> 을 제안했다. 플러그인 <code>implementation-django</code> §10.2 에 그 예제가 있어서다.
<br><b>사용자가 기각했다</b> — <em>「migrations 폴더 안은 사람이 직접 손대면 안 되는 걸로 알고 있어. 파일이 쌓이면 <b>압축(squash)</b> 하는 경우도 있으니까」</em>.
<div class="pre-wrap"><pre><code>django/db/migrations/operations/base.py:160-170

    def reduce(self, operation, app_label):
        if self.elidable:        return [operation]   # elidable 이면 «지워진다»
        elif operation.elidable: return [self]
        return False                                  # 기본값이면 «최적화가 막힌다»</code></pre></div>
<b>메커니즘은 사용자 말이 맞고, 플러그인 문면이 뒤집혀 있었다</b> — §10.2 는 <em>「데이터 마이그레이션은 <code>squashmigrations</code>에서 <b>보존되지 않으므로</b> 별도 관리한다」</em> 라고 적었는데, 기본값에서는 <b>보존되고 대신 그 지점에서 최적화가 끊긴다</b>. 지워지는 것은 <code>elidable=True</code> 를 명시했을 때뿐이다.
<br><b>그리고 더 큰 이유를 내가 안 대조했다</b> — 마이그레이션은 <b>「돌았다 / 안 돌았다」 두 상태뿐</b>이라 §11.2 가 요구하는 <em>「batch 크기와 pause 정책」·「실패한 batch 를 재실행해도 안전하도록」·「진행률 모니터링」</em> 을 <b>하나도 못 한다</b>. Expand → Backfill → Contract 는 원래 <b>사람이 배포 절차로 관리하는 3단계</b>이지 마이그레이션 파일 하나가 아니다.
<br><b>갈 곳은 이미 있었다</b> — <b>D22</b> 의 <code>scripts/</code>(「임시 · 일회성」 · 트리 <b>밖</b> · 관할 밖). <b>거기에는 한 글자도 안 적었다</b> — 사용자가 <em>「scripts 는 임시로 쓰고 버리는 일회성이 많으니까 아무런 규칙도 없는 게 좋겠다」</em> 로 못 박았고, D22 자신이 이미 「규정하지 않는다」이다. 대신 트리 <b>안</b> 칸인 <code>migrations/</code> 에 경계만 그었다.
<br><b>플러그인 정정 셋이 스펙으로 나갔다</b> — §10.2 를 금지로 · 무한 루프 <code>.save()</code> 예제 제거 · squash 서술 정정.</dd>

<dt>같이 올린 것 — <b>트랜잭션 안에서 BC 를 넘지 않는다</b></dt>
<dd>2장 흐름 ⓐ 의 산문(<em>「커밋 <b>앞</b>이어야 한다 — 트랜잭션을 연 채 남을 기다리면 DB 락을 쥐고 기다리는 것이다」</em>)에만 있던 것을 <code>unit_of_work/</code> 칸의 <b>검사</b>로 올렸다. 락을 쥐고 네트워크를 기다리는 것도 문제지만, <b>남은 이미 커밋했는데 내가 롤백되면 불일치가 남는다</b>.</dd>

<dt>우리가 «쓸 수 없는» 면제 하나</dt>
<dd>Vernon 의 이유 ⑵ <b>「메시징 수단이 없다」</b> — <em>“Eventual consistency requires the use of some kind of out-of-band processing capability… What if the project you are working on has no provision for any such mechanism?”</em> <b>D40 이 그 수단을 줬으므로 우리는 이 면제를 못 쓴다.</b> ⑶ 글로벌 트랜잭션·⑷ 조회 성능도 우리 조건이 아니다. <b>살아남는 면제는 ⑴ 배치 하나뿐</b>이고, 그것만 검사가 통과시킨다.</dd>
</dl>

## D42 · BC 를 가로지르는 «순서»는 칸이 아니라 유스케이스가 진다

**확정 · 08-08 · T30** · 자리 — <b>트리 행 신설 0</b> &nbsp;·&nbsp; 문장 다섯 — <code>domain_layer/</code> · <code>&lt;aggregate&gt;/</code> · <code>&lt;use_case&gt;_use_case.py</code> · <code>open_host_service/</code> · <code>framework/broker/</code>

<dl class="kv">
<dt class="ans-dt">물음 — <b>「A 다음 B, B 가 실패하면 되돌려라」를 아는 코드가 갈 칸이 0이었다</b></dt>
<dd class="ans-dd filled"><code>framework/broker/</code> 가 <em>「단계·순서·보상을 기억하는 상태가 있으면 위반 — 그건 «중재자»다」</em> 로 <b>내치기만 하고 갈 곳을 안 줬다</b>. 규율 ⑤ 다 — <b>이 칸 자체에 결함이 있다</b>.<br>
<b>둘을 갈라야 한다</b> — <b>기억할 게 없는 순서</b>(탈퇴 → 회수 → 알림, 한 번에 쭉 간다)는 <b>이미 산다</b>. 유스케이스가 포트를 차례로 부르면 끝이다. 비어 있던 것은 <b>기억해야 하는 순서</b> 하나 — 각 단계가 «남의 답»을 기다려서 그 사이에 요청이 끝나 버리는 경우다.</dd>

<dt class="ans-dt">답 — <b>체인으로 선다. 순서 지식은 유스케이스가 진다</b></dt>
<dd class="ans-dd filled"><b>축이 둘이고 문헌의 이름이 서로 다르다</b> — 유스케이스가 차례로 «부르면» <em>오케스트레이션</em>(조정자가 곧 그 유스케이스다)이고, «사실»로 이으면 <em>코레오그래피</em>다.
<span class="dim">08-08 · T34 — 옛 문장은 커맨드 사슬까지 <em>코레오그래피</em> 라 불렀다. <b>원전에서 코레오그래피는 «이벤트 발행»으로 정의</b>되고 커맨드 사슬은 «조정자 없는 오케스트레이션»이 아니라 <b>조정자가 유스케이스인 오케스트레이션</b>이다. 어느 쪽인지가 D48 의 물음 ①로 갈린다.</span>
<b>우리 트리는 둘 다 이미 갖고 있다</b> — 커맨드 축(<code>port/&lt;capability&gt;/</code> → ACL → 상대 OHS)과 이벤트 축(<code>framework/broker/</code> → <code>event_subscription/</code>)이 둘 다 열려 있고, <code>event_subscription/&lt;event&gt;_subscription.py</code> 는 이미 <em>「유스케이스 하나만 부른다」</em> 로 껍데기까지 정해져 있다. <b>신설 0.</b></dd>

<dt>진행 상태는 어디에 적나 — <b>적지 않는다</b></dt>
<dd>유스케이스는 한 번 불리고 죽어 「지금 몇 단계인지」를 못 든다. 그래서 어딘가 적어야 할 것 같지만, <b>각 단계가 그 BC 의 도메인 상태를 실제로 바꾸는 한 이미 적혀 있다</b> — 자녀 BC 의 자녀가 «탈퇴중», 기기 BC 의 기기가 «회수됨», 결제 BC 의 구독이 «환불됨». <b>셋을 합치면 진행이 읽힌다.</b> 별도 진행표는 그 셋을 <b>두 번째로 적는 일</b>이고, 두 벌은 반드시 어긋난다.
<br><b class="dim">※ 08-08 · T34(<b>D48</b>) — <b>결론은 그대로 서지만 근거가 바뀌었다.</b> 「합치면 읽힌다」는 <b>합칠 주체가 없어서</b> 약했다. 지금 근거는 <b>판정 물음</b>이다 — 「실패하면 내가 할 일이 있나」에 «있다»면 유스케이스가 직접 부르니 콜 스택이 곧 진행이고, «없다»면 애초에 알 필요가 없다.</b></dd>

<dt>기각 ① — <b>절차를 애그리거트에 두는 것</b></dt>
<dd><b>«불변식»을 남의 BC 에 걸면 불가능하다.</b> 불변식은 <b>한 트랜잭션 안에서 참임이 보장</b>돼야 성립하는데 남의 BC 는 다른 트랜잭션이라 <b>「지금 참인지」를 알 방법이 없다</b> — 물어본 순간 이미 낡은 답이다.
<br><b class="dim">※ 08-08 · T34(<b>D48</b>) — <b>이 문장이 두 가지를 한데 묶고 있었다.</b> «불변식»(항상 참이어야 하는 규칙)은 위 이유로 불가능하지만, «진행 기록»(어디까지 왔다는 메모)은 남에게 «묻지» 않고 돌아온 사실을 받아 적을 뿐이라 불가능하지 않다. <b>Vernon 은 실제로 그것을 애그리거트로 두라고 한다.</b> 우리가 안 여는 이유는 «불가능»이 아니라 <b>판정 물음으로 자리가 생기지 않아서</b>다.</b><br>
<b>판정 자 둘이 같은 답을 줘야 한다</b> — ① <b>「이 규칙을 지키려면 남의 BC 에 «물어봐야» 하나」</b> ② <b>「업무 하는 사람이 이 단계 이름을 «입으로» 부르나」</b>.
<div class="pre-wrap"><pre><code>Order 가 「결제됨 → 배송중 → 완료」를 든다
   ① 묻지 않는다. 배송 BC 가 «알려 준» 것을 받아 자기 상태를 바꿀 뿐        ✓
   ② 고객이 「내 주문 배송중이야?」 라고 입으로 말한다                       ✓
   → 프로세스 매니저가 아니라 그냥 주문 BC 의 도메인이다

ChildWithdrawal 이 「회수대기 → 환불대기 → 종료」를 든다
   ① 통보만 받으니 겉으론 통과한다                                         △
   ② 업무는 「회수대기」라는 말을 «하지 않는다» — 구현하려고 만든 칸이다      ✗
   → 워크플로를 도메인 어휘로 위장한 것. 자리는 유스케이스다</code></pre></div>
<b>자 하나만으로는 안 갈린다</b> — ①만 보면 둘 다 통과한다. 그리고 <code>domain_layer/</code> 의 「나가는 화살표 0」은 <b>import 를 잡지 «어휘 위장»을 못 잡는다</b>. 그래서 문장이 필요했다.<br>
<span class="dim">08-08 · T34 — <b>이름과 전제를 둘 다 잘못 적었었다.</b> <em>Process Manager</em> 는 <b>Hohpe·Woolf</b> 의 패턴이고 Vernon 은 <em>“혼동을 피하려고 <b>Long-Running Process</b> 라는 이름을 골랐다”</em> 고 직접 적는다. 그리고 «업무가 그 절차 이름을 부를 때만 성립한다»는 <b>원전에 없는 조건</b>이다 — 그건 우리 판단이고, 그렇게 적어야 한다.</span></dd>

<dt>기각 ② — <b>중재자를 <code>framework/</code> 에</b></dt>
<dd><b class="dim">※ 이것은 «자리»의 기각이지 «패턴»의 기각이 아니다(08-08 · T34 · <b>D48</b>) — <b>중재자 노릇은 유스케이스가 한다.</b> 「실패하면 내가 할 일이 있나」에 «있다»면 유스케이스가 순서·실패·되돌리기를 전부 지고, 그것이 문헌의 오케스트레이션이다.</b><br>
<b>규칙 둘이 물리적으로 막는다.</b> <code>framework/</code> 는 <em>「여기서 <code>application/</code> 쪽으로 나가는 import 가 <b>0</b>」</em> 인데 중재자는 상대 BC 의 OHS 계약을 import 해야 순서를 짤 수 있다. 그리고 D38 «자격» — <em>「계약의 이름에도 시그니처에도 어느 BC 의 업무 어휘가 한 글자도 안 나온다」</em> — 인데 「탈퇴 → 회수 → 환불」이 곧 업무 어휘다. <span class="dim">Richards 의 중재자가 내보내는 것은 <b>사실이 아니라 지시</b>다 — 그의 mediator topology 에서 processing event 는 <em>“다음 단계를 수행하라”</em> 는 명령이라 <b>반드시 실행돼야</b> 한다. <b>08-08 · T34 — 옛 문장은 축자 인용인 것처럼 «원전 문면으로» 표식을 달았는데 그 문자열을 책에서 찾지 못했다.</b> 주장은 그대로 서고 표식만 뗐다.</span></dd>

<dt>「한눈에 안 보인다」 — <b>코드가 아니라 «생성물»로 푼다</b></dt>
<dd>체인의 값은 순서가 <b>어느 한 곳에도 안 적혀 있다</b>는 것이다. 그렇다고 순서표를 손으로 적으면 <b>코드와 그 표가 어긋난다</b>(적는 걸 잊으면 끝). <b>기계가 매번 세게 한다</b> — <code>published_event/</code>(누가 무엇을 공표하나) × <code>event_subscription/event_router.py</code>(누가 무엇을 듣나) × <code>composition_root/dependency_wiring.py</code>(누가 누구를 시키나) 를 이으면 체인이 나온다. 백스톱이 <b>이미 import 그래프를 읽으니</b> 거의 공짜고, <b>코드가 바뀌면 그림도 바뀐다</b>.</dd>

<dt class="ans-dt">규율 ⑤ — <b>조건 하나만 남는다</b></dt>
<dd class="ans-dd filled">체인이 깨지는 지점은 하나다 — <b>c 가 실패했을 때 a 를 되돌려야 할 때</b>. 체인에선 c 가 「a 를 되돌려라」를 알아야 하고 그건 화살표가 거꾸로 서는 일이다. <b>그런데 그때 여는 것도 «유스케이스»다</b> — 되돌려야 한다는 것은 「실패하면 내가 할 일이 있다」는 뜻이고, 그러면 <b>애초에 «지시»로 불렀어야</b> 한다.<br>
그리고 <code>open_host_service/</code> 에 <b>「되돌릴 수 없는 단계는 순서의 맨 끝에, 실패할 수 있는 검사는 맨 앞에」</b> 를 박았다 — 뒤엣것이 더 세다. <b>실패 가능한 검사를 앞으로 당기면 되돌릴 것이 아예 안 남는다.</b>
<br><b class="dim">※ 08-08 · T34(<b>D48</b>) — 옛 문장은 <b>「조건부 없이 닫는다」</b> 였고 근거는 <em>「오케스트레이터 없이 지킬 수 있는 유일한 안전장치」</em> 였다. <b>둘 다 고쳤다</b> — ⑴ 조건이 하나 남는다: <b><code>cron_job/</code> 워커에서 돌면서 단계가 둘 이상이면 콜 스택이 끊기므로 진행을 저장해야 한다</b>(문헌의 오케스트레이터가 상태를 저장하는 이유다). 자리는 <code>domain_layer/</code> 이고 지금은 열지 않는다. ⑵ 「유일한」은 과장이었다 — 원전은 <b>실패 가능 단계를 앞으로 당겨 보상을 아예 없애는</b> 더 센 것을 준다.</b></dd>
</dl>

## D41 · «Repository» 를 뗀다 — 도메인을 우회하는 조회는 리포지토리가 아니다

**확정 · 08-08 · T22** · 자리 — <code>domain_bypass_query/</code> &nbsp;·&nbsp; <b>파일에 «종류» 접미사</b> 16칸 &nbsp;·&nbsp; <code>…_query</code>·<code>…_request</code>·<code>…_response</code>·<code>…_exception</code>·<code>…_form</code>·<code>…_cron_job</code> &nbsp;·&nbsp; <b>트리 행 변화 0 — 이름만</b>

<dl class="kv">
<dt class="ans-dt">물음 — <b>「이 칸의 이름에 «Repository» 를 써도 되나」</b></dt>
<dd class="ans-dd filled"><b>안 쓴다.</b> <b>원전 둘이 이 물건을 리포지토리라 부르지 않는다</b> — Greg Young 의 <em>Thin Read Layer</em> · eShopOnContainers 의 <code>…Queries</code>.
<span class="dim">08-10 · 4차 리뷰 — 옛 문장은 <b>「Vernon 의 <code>QueryService</code>」를 셋째로 들었는데 IDDD 에 그 «패턴 이름»이 없다</b>(2건 모두 GemFire API 호출). Vernon 이 실제로 쓰는 것은 <b>Use Case Optimal Query</b> 이고 <b>그는 그것을 리포지토리에 둔다</b> — 즉 이 항목은 <b>우리 편이 아니라 반대편</b>이었다. 근거를 둘로 줄였고, <b>주근거는 아래 Evans 쪽</b>이라 결론은 그대로 선다.</span>
Evans 의 <em>Repository</em> 는 «애그리거트 루트의 컬렉션»인데 <b>이 칸에는 애그리거트가 없다</b>.<br>
<b>이 칸은 그 값을 스스로 적어 두고 있었다</b> — 46행 «무엇이 오나»의 <em>「계보가 한 겹 흐려진다」</em>. 3차 리뷰가 그걸 물었고(D-3), 답은 <b>«값을 치른다»가 아니라 «안 치른다»</b>였다.</dd>

<dt>그러면 <b>D29</b> 의 <code>query_repository/</code> 기각은 무너지나 — <b>아니다</b></dt>
<dd>그때 기각한 것은 <b>«조회냐»라는 판정어</b>였다. 「조회냐」로 물으면 <b>애그리거트 리포지토리도 조회를 해서</b>(<code>find_by_id</code>·<code>count</code>) 아무것도 안 갈린다.
새 이름은 <b>판정어 <code>domain_bypass</code> 를 그대로 붙들고 «종류» 낱말만 갈았다</b> — 「도메인을 거쳤나」는 예·아니오로 갈리고, 84행의 검사(<em><code>domain_layer</code> 를 import 하면 위반</em>)가 바로 그 물음이다.
<span class="dim">그래서 <code>…Queries</code> 를 그대로 쓰지 않았다 — 원전의 낱말이지만 <b>판정어가 빠진다</b>.</span></dd>

<dt class="ans-dt">파일에도 <b>종류를 단다</b> — <code>&lt;capability&gt;_query.py</code></dt>
<dd class="ans-dd filled"><b>능력 이름만으로는 «무엇인지»가 안 보인다.</b> <code>child_lesson_digest.py</code> 는 열기 전에는 그게 조회인지 알 수 없다 —
50행이 <code>&lt;boundary&gt;_unit_of_work.py</code> 에 쓴 자와 <b>같은 자</b>다(<em>「경계 이름만으로는 «무엇인지»가 안 보여 파일이 종류를 단다」</em>).<br>
<b>형제가 이미 그렇게 하고 있었다</b> — <code>adapter/persistence/</code> 의 자식 셋 중 <code>repository/&lt;aggregate&gt;_repository.py</code> 와 <code>unit_of_work/&lt;boundary&gt;_unit_of_work.py</code> 는 접미사를 달고 있고 <b>이 칸만 안 달고 있었다</b>. 셋이 같은 모양이 된다.<br>
<b>같은 자를 트리 전체에 걸었다</b> — 리프 이름이 자리표시자인 칸을 전수로 훑어 <b>열여섯 칸</b>이 종류를 단다:
<div class="pre-wrap"><pre><code>port/&lt;capability&gt;/&lt;capability&gt;_port.py
port/&lt;capability&gt;/&lt;payload&gt;_payload.py
port/domain_bypass_query/&lt;capability&gt;/&lt;capability&gt;_query.py
port/domain_bypass_query/&lt;capability&gt;/&lt;payload&gt;_payload.py
adapter/persistence/domain_bypass_query/&lt;capability&gt;_query.py
open_host_service/&lt;service&gt;/contract/request/&lt;request&gt;_request.py
open_host_service/&lt;service&gt;/contract/response/&lt;response&gt;_response.py
open_host_service/&lt;service&gt;/contract/exception/&lt;exception&gt;_exception.py
driving_layer/event_subscription/&lt;event&gt;_subscription.py
cron_job/&lt;job&gt;_cron_job.py
adapter/{anticorruption_layer,external_system,&lt;capability&gt;}/…/&lt;capability&gt;_adapter.py
framework/&lt;capability&gt;/&lt;capability&gt;_port.py · &lt;technology&gt;_adapter.py
cron_job/&lt;job&gt;_cron_job.py
admin/&lt;entity&gt;/form/&lt;form&gt;_form.py</code></pre></div>
<b>안 단 칸들</b> — <code>&lt;event&gt;.py</code>(<code>order_placed</code>) · <code>&lt;exception&gt;.py</code>(<code>order_already_placed</code>) · <code>&lt;value_object&gt;.py</code>(<code>money</code>) · <code>&lt;domain_service&gt;.py</code> · <code>&lt;area&gt;.py</code>.
<b>이름이 곧 서술문이거나 동사구라 그 자체로 무엇인지 읽힌다.</b><br>
<b>딸려 갈린 자 하나</b> — <b>D9</b> 의 «낱말은 한 경로에서 한 번만»이 <b>폴더에만</b> 걸리게 좁아졌다.
<span class="dim">그 자는 이미 <code>repository/&lt;aggregate&gt;_repository.py</code>·<code>unit_of_work/&lt;boundary&gt;_unit_of_work.py</code> 두 자리에서 지켜지지 않고 있었다 — 예외가 아니라 <b>다른 자가 이기고 있었다는 뜻</b>이다.</span><br>
<b>「폴더 이름과 같은 파일 = 계약」이라는 자는 버린 게 아니라 갈아끼웠다</b> — <code>*_port.py</code> 가 있나로 바뀐다.
101행이 <code>framework/</code> 의 «능력 vs 기술»을 가르는 데 쓰는 그 자인데, <b>폴더 이름이 우연히 같은 것에 기대는 대신 접미사가 직접 «계약»이라고 말한다</b>. 판정 결과는 그대로다.<br>
<b>「선언과 파일 이름이 같다」 1:1 검사도 안 깨진다</b> — 선언과 구현이 <b>같이</b> 접미사를 달거나(<code>_query</code>), <b>어간이 같고 접미사만 갈리기</b>(<code>_port</code> ↔ <code>_adapter</code>) 때문이다.</dd>

<dt>계보 — <b>바뀐 것은 매번 낱말 하나</b></dt>
<dd><b>D29</b> 칸 신설(<code>query_repository/</code>) →
<b>D33</b>·F6 <b>판정어를 붙였다</b>(<code>domain_bypass_repository/</code>) →
<b>D41 «Repository» 를 뗐다</b>(<code>domain_bypass_query/</code>). <b>판정은 D33 이후 그대로다.</b></dd>

<dt class="ans-dt">안 바뀌는 것</dt>
<dd class="ans-dd filled"><b>트리 행 0 · 자리 0 · 검사 0.</b> 44~48행(선언)과 84~85행(구현)의 <b>모양·자식·규칙</b>이 그대로고 바뀐 것은 <b>이름뿐</b>이다.
<b>클래스 가족 규칙도 그대로</b> — <code>Query</code> 는 <b>구현에도 참인 낱말</b>이라 선언·구현이 접미사를 공유하고 <b>접두사(<code>Django…</code>)가 가른다</b>. 바뀐 것은 <b>낱말 하나</b>다.</dd>
</dl>

## D40 · 이벤트 축을 연다 — 사실은 도메인이 낳고, 배달은 브로커가 한다

**확정 · 08-08 · T1·T2·T19·T28·T29** · 자리 — <code>published_event/</code> &nbsp;·&nbsp; <code>driving_layer/event_subscription/</code> &nbsp;·&nbsp; <code>framework/broker/</code> &nbsp;·&nbsp; <code>composition_root/</code> &nbsp;·&nbsp; <b>트리 107 → 117행</b>

<dl class="kv">
<dt class="ans-dt">물음 — <b>「경계를 넘는 메시지 셋 중 «사실»만 갈 자리가 없다. 열 것인가」</b></dt>
<dd class="ans-dd filled"><b>연다.</b> 지금 트리에는 <b>커맨드</b>(<code>port/</code> ↔ <code>open_host_service/</code>)와 <b>자료</b>(<code>response/</code>·<code>result</code>·<code>schema_out</code>) 자리가 있는데 <b>사실만 없다</b>. 셋 중 하나가 비면 트리가 «이 경우는 안 다룬다»고 말하는 것이고, 그건 <b>규율 ⑤ 위반</b>이다.<br>
<b><b>D34</b> 를 뒤집는다.</b> 옛 결론(«칸을 열지 않는다»)의 근거는 <b>「계약이 앉을 자리가 없다」</b>였는데, 그건 <b>자리를 만들면 되는 문제</b>였다. 실측 근거는 이미 08-07 에 강등됐고, 남은 배치 근거가 이렇게 풀린다.</dd>

<dt>판정 — <b>자 둘이 같은 답을 줘야 한다</b></dt>
<dd><b>①「실패했을 때 발신 BC 에서 «처리할 게» 있나」</b> — 있으면 <b>커맨드</b>, 없으면 <b>사실</b>. <em><code>except</code> 에 쓸 것이 있나로 답이 나온다.</em><br>
<b>②「동사를 누가 골랐나」</b> — 발신자가 골랐으면 <b>지시</b>(커맨드), 받는 쪽이 고르면 <b>배달</b>(사실).<br>
<b>둘이 어긋나면 설계가 틀린 것</b>이다. 사실로 보내놓고 속으로 처리를 기대하면 결합이 없어진 게 아니라 <b>안 보이게 된 것</b>이다.<br>
<b>사실 하나에 전파가 여럿이고, 전파마다 따로 판정한다</b> — 「자녀가 탈퇴했다」 하나에서 기기 권한 회수(커맨드)와 부모 알림(사실)이 <b>같이</b> 나온다. <b>두 축 중 하나를 고르는 게 아니다.</b></dd>

<dt>구조로도 갈린다 — <b>기계가 오분류를 잡는다</b></dt>
<dd><b>커맨드는 소비자가 «정확히 하나»</b>이고 <b>스키마 주인이 «받는 쪽»</b>이다. <b>사실은 소비자가 «0~N»</b>이고 <b>스키마 주인이 «보내는 쪽»</b>이다.<br>
주인 방향이 반대라 <b>두 계약이 한 폴더에 못 산다</b> — <code>open_host_service/&lt;service&gt;/contract/</code> 와 <code>published_event/</code> 가 갈리는 이유가 이것이다.<br>
그리고 <b>「이 포트의 소비자가 둘 이상」은 import 그래프로 센다</b> — 사실이었어야 할 것이 커맨드로 서 있으면 기계가 지목한다.</dd>

<dt>배치 — <b>새 칸 열, 트리 107 → 117행</b></dt>
<dd><b><code>published_event/&lt;event&gt;.py</code></b> 공표 계약 — <b>층에 속하지 않는다</b>. 남이 import 해도 되는 사실 표면은 여기뿐이고, <code>domain_layer/**/event/</code> 는 «내부용»으로 남아 밖에서 읽으면 위반이다.<br>
<b><code>driving_layer/event_subscription/</code></b> <b>넷째 입구</b> — <code>event_router.py</code>(어느 사실 → 어느 핸들러)와 <code>&lt;event&gt;.py</code>(껍데기). <code>api/</code> 의 <code>api_router.py</code> 와 <b>같은 모양</b>이다.<br>
<b><code>framework/broker/broker_port.py</code> + <code>&lt;technology&gt;_adapter.py</code></b> 배달 기계 — <b>계약과 배달을 한 파일에 두지 않는다</b>(한 파일이면 «어댑터는 <code>composition_root</code> 밖에서 아무도 import 하지 않는다» 검사의 대상이 0건이 된다). 업무 어휘 0이라 <b>D38</b> 자격을 통과한다.<br>
<b><code>composition_root/</code></b> 가 폴더가 된다 — 결선이 둘(<code>dependency_wiring.py</code> · <code>event_wiring.py</code>)이라서다. <b>«단일 지점»은 파일이 아니라 폴더가 진다</b>(Seemann 의 정의도 <em>“unique <b>location</b>”</em> 이다).<br>
<b>발행 포트·어댑터는 새 칸이 아니다</b> — <code>port/&lt;capability&gt;/</code>·<code>adapter/&lt;capability&gt;/</code> 일반형이 흡수한다.</dd>

<dt>기각한 것 — <b>근거가 중요하다</b></dt>
<dd><b>중재자(Mediator)를 <code>framework/</code> 에</b> — ✗. Richards 의 중재자는 <b>워크플로를 «소유»</b>하고, 워크플로는 업무 지식이라 D38 «자격»에 걸린다. 그리고 중재자가 내보내는 것은 <b>사실이 아니라 지시</b>다 — 그의 mediator topology 에서 processing event 는 「다음 단계를 수행하라」는 명령이라 <b>반드시 실행돼야</b> 한다. <span class="dim">08-08 · T34 — 옛 문장은 <em>“processing events (which function more like commands)”</em> 를 «원전 문면»이라 표식했는데 <b>그 문자열을 책에서 찾지 못했다</b>. 주장은 그대로 서고 표식만 뗐다.</span> 완료를 기다리는 순간 「알림이 막히면 원래 일도 막힌다」가 되어 요구사항 자체가 깨진다.<br>
<b>Django signals 를 채널로</b> — ✗. <b>계약이 없고</b>(<code>broker_port.py</code> 같은 겨냥할 면이 안 생긴다), <b>실패한 리스너의 기록도 없으며</b>, 등록이 임포트 부작용이라 동작이 «어느 모듈이 임포트됐나»에 달린다(원칙 07). <b>Django 공식 문서 자신이 말린다</b> — <em>“Where possible you should opt for <b>directly calling the handling code</b>”</em>. 그리고 「브로커 없음」은 signals 없이도 이미 참이다.
<span class="dim">08-09 · T33 — 옛 근거의 첫 줄은 <b>「전달 보장이 0」</b> 이었는데 <b>그건 우리 브로커에도 참이다</b>(둘 다 at-most-once). 비대칭이라 근거를 «계약»과 «기록» 쪽으로 갈랐다.</span><br>
<b>도메인 이벤트를 그대로 공표</b> — ✗. 남의 BC 가 내 내부 모델에 묶여 필드 하나 바꿀 때마다 깨진다. <b>번역이 낭비가 아니라 요점</b>이다.<br>
<b>브로커(kafka·rabbitmq)</b> — <b>지금은 아니다.</b> 판정은 <b>「트랜잭션을 나눠야 하나」</b>이고, 다른 저장소·다른 배포 단위·「실패해도 발신자가 진행」 <b>셋 다 아직 아니다</b>. 「안 쓰여서」가 아니라 <b>「나눌 이유가 없어서」</b>이므로 규율 ⑤ 에 걸리지 않는다.</dd>

<dt>부팅 — <b>가능한지부터 쟀다</b></dt>
<dd>Django 는 <code>django.setup()</code> 을 <b>3단계</b>로 돈다 — ①앱 설정 임포트(모델 금지) ②모델 임포트 ③<b><code>ready()</code></b>. <b>③에서는 모든 모델이 이미 로드돼 있다</b>.<br>
<b>「모든 앱의 <code>ready()</code> 가 끝난 뒤」 훅은 없다</b> — 그런데 <b>우리 배치는 그게 필요 없다</b>. 각 BC 가 자기 구독만 등록하므로 <b>BC 간 부팅 순서 의존이 0</b>이다. <em>남의 BC 레지스트리에 등록하면 「그쪽이 먼저 켜졌나」에 동작이 달리는데, 그게 옛 구현이 틀렸던 자리다.</em><br>
<b>대신 조건 셋</b> — ⑴등록은 <b>멱등</b>(문서 명시: <em>“in tests … <code>ready</code> might be called more than one time … write <b>idempotent</b> methods”</em>) ⑵<code>ready()</code> 에서 <b>DB 금지</b>(<em>“<code>manage.py test</code> would still execute some queries against your <b>production</b> database”</em>) ⑶wiring 임포트는 <b><code>ready()</code> 안에서</b>(1단계에서는 모델을 못 읽는다).<br>
<b>잃는 것 하나</b> — 「이 사실에 구독자가 0」을 부팅 때 못 잡는다. <b>정적 검사로 옮긴다</b>(그리고 사실은 소비자 0도 정상이라 <b>위반이 아니라 경고</b>다).</dd>

<dt><b>딸려 닫힌 것 둘</b></dt>
<dd><b>T28</b> — <code>exception.py</code> 가 <b><code>exception/</code> 폴더</b>가 된다. 같은 애그리거트가 내는 것인데 <code>event/</code> 는 폴더고 예외는 파일이었다. <b>자는 「하나면 파일, 둘 이상이면 폴더」</b>이고 불변식은 여럿이다. <em>덤 — 「파일이 길어지면 애그리거트를 본다」는 신호가 «파일 수»로 바뀌면서 사람 판정에서 기계 판정으로 내려온다.</em><br>
<b>T29</b> — 애그리거트는 사실을 <b>«수집»</b>하고(<code>pull_events()</code>) <b>유스케이스가 꺼낸다</b>. 참조 구현은 저장 경계가 자동으로 걷지만(cosmicpython 은 UoW, Spring Data 는 리포지토리) <b>우리는 43행이 UoW 에 협력자 속성을 금지</b>해서 그 길이 막혀 있다.
<span class="dim">08-10 · T50 — <b>그 「잊으면」의 답이 D59 에서 바뀌었다</b>: 「테스트가 잡는다」는 <b>테스트 없는 경로를 못 잡으므로</b>,
<b>저장이 「안 꺼낸 사실이 남았나」를 보고 터뜨린다</b>(<code>&lt;aggregate&gt;_repository.py</code> 구현 칸).</span></dd>
</dl>

## D39 · 창구의 «의도»는 함수 이름이 진다 — 그리고 관문 규칙 하나가 반쪽이었다

**확정 · 08-08 · T26·T27** · 자리 — <code>&lt;service&gt;_service.py</code> &nbsp;·&nbsp; <code>contract/{request,response}/</code> &nbsp;·&nbsp; <code>port/&lt;capability&gt;/</code> &nbsp;·&nbsp; <b>새 칸 0 · 규칙 넷 + 확장 하나</b>

<dl class="kv">
<dt class="ans-dt">물음 — <b>「호출되는 쪽이 계약을 갖는 게 맞다면, <code>request/</code> 를 <code>command/</code> 로 바꿔야 하지 않나」</b></dt>
<dd class="ans-dd filled"><b>전제는 맞고 결론은 안 따라온다.</b> OHS 로 들어오는 것은 조회든 뭐든 전부 <b>커맨드 «모양»</b>이다(절차를 부르고 · 답이 오고 · 실패가 돌아온다). 그런데 <b>그 폴더에 든 것은 커맨드가 아니라 커맨드의 «인자»</b>다.<br>
<b>커맨드는 «객체»로 존재하지 않는다.</b> EIP 는 <em>“a Command Message is simply a regular message that <b>happens to contain a command</b>”</em> 라 적어 커맨드를 메시지 «안»의 것으로 두고, GoF 는 그 커맨드를 <b>receiver 참조 + 파라미터 + <code>execute()</code> 셋이 한 몸인 객체</b>로 정의한다 — <em>“Values for parameters of the receiver method are <b>stored in the command</b>.”</em> 우리는 직접 호출이라 그 셋이 흩어져 있다: receiver 는 <code>build_&lt;use_case&gt;()</code> 가 · 파라미터는 <code>contract/request/</code> 가 · 실행은 함수 본체가 진다. <b>셋을 묶는 자리가 «그 함수»</b>다.<br>
그래서 <code>command/</code> 는 <b>어느 쪽으로 읽어도 안 선다</b> — <b>«의도»로 읽으면</b> 의도는 폴더가 정하는 게 아니라 이름·실패·받는 이가 정하고, <b>«요청서»로 읽으면</b> 우리 트리엔 그게 없다. 게다가 <code>request/</code>↔<code>response/</code> 는 <b>«방향» 한 축</b>이라 <code>command/</code> 로 바꾸면 <b>반대편 짝이 사라지고</b>, 판정이 <code>path</code>(들어오나 나가나)에서 <b>사람 판정</b>(이게 커맨드인가)으로 내려앉는다.</dd>

<dt class="ans-dt">그런데 진짜 구멍은 따로 있었다 — <b>이름 규칙이 «함수»에는 0건</b></dt>
<dd class="ans-dd filled"><code>&lt;request&gt;.py</code> 의 이름 규칙은 <b>「명사로 짓는다」 한 줄</b>이었고, <code>&lt;service&gt;_service.py</code> 의 <b>공개 함수 이름 규칙과 <code>port/</code> 메서드 이름 규칙은 아예 없었다</b>. 그래서 「이 창구에 무엇을 시킬 수 있나 · 이걸 다시 불러도 되나」가 <b>경로에도 시그니처에도 안 적혀 있었다</b>.<br>
<b>왜 「명사」로 굳었는지도 나왔다</b> — 2장 흐름의 OHS 예시가 <b>질의 하나뿐</b>이라, <b>커맨드가 이 창구로 들어오는 경우를 이름 규칙이 한 번도 안 겪었다</b>.<br>
<b>왜 <code>api/</code> 는 안 그런가</b> — 거긴 <b>프로토콜이 동사를 준다</b>(<code>POST</code>/<code>GET</code>). OHS 는 그냥 파이썬 함수 호출이라 <b>이름 말고 의도를 말할 것이 없다</b>. 이 비대칭이 신설의 근거다.</dd>

<dt class="ans-dt">결정 ① — <b>공개 함수는 <code>_command</code> 또는 <code>_query</code> 로 끝난다</b></dt>
<dd class="ans-dd filled">상태를 바꾸면 커맨드, 안 바꾸면 질의다. <b>둘 중 무엇이냐는 사람 판정이지만 「안 밝혔다」는 <code>ast</code> 한 줄이 잡는다</b> — 그게 지금 비어 있던 자리다. <b>유스케이스 이름에서 파생할 수 없다</b>는 것이 근거다: <code>evict_child/</code> 어디에도 「상태를 바꾸나」가 없다.<br>
<b><code>_command</code> 하나만 강제하지 않는 이유</b> — 조회에도 붙게 되고, <b>전부에 붙는 표식은 정보가 0</b>이 된다. 그리고 트리 자기 예시(<code>current_status</code>)가 반례다.</dd>

<dt class="ans-dt">결정 ② — <b>파일 이름 = 함수 이름 − 접미사</b> · <b>클래스는 <code>&lt;Operation&gt;Request</code>/<code>&lt;Operation&gt;Response</code></b></dt>
<dd class="ans-dd filled"><code>evict_child_command()</code> ↔ <code>contract/request/evict_child_request.py</code> ↔ <code>contract/response/evict_child_response.py</code> — <b>연산 하나가 셋으로 1:1</b>이라 <code>path</code> 로 선다. <code>ls contract/request/</code> 한 번에 <b>그 창구의 연산 목록</b>이 읽힌다.<br>
<b><span class="no">&lt;Operation&gt;Result</span> 는 기각</b> — 어감으로는 「커맨드에는 결과」가 맞지만, <b><code>request</code> 의 짝은 <code>response</code> 이고 <code>result</code> 는 짝이 없는 «인과» 어휘</b>라 방향 축이 깨진다. 반환 타입에서 커맨드/질의를 다시 가르면 <b>같은 판정을 두 번</b> 하게 되고 둘이 어긋날 수 있다. 그리고 이 폴더의 정의가 <b>「이 창구가 낼 수 있는 답 전부 — 거절도 답」</b>(D36)이라 <code>Result</code> 는 «성공의 산물»로 기울어 정의를 좁힌다. <b>관례도 같은 쪽</b> — AWS SDK for Java 는 v1 의 <code>*Result</code> 를 v2 에서 <b>전부 <code>*Response</code> 로 바꿨다</b>(변이 연산 포함).</dd>

<dt class="ans-dt">결정 ③ — <b><code>port/</code> 메서드는 «문법 형태»만 요구한다 (접미사 없음)</b></dt>
<dd class="ans-dd filled"><b>시키면 명령형 동사구</b>(<code>revoke_for_child()</code>) · <b>물으면 묻는 꼴</b>(<code>current_status()</code>·<code>has_shipped()</code>). <span class="no">notify()</span>·<span class="no">handle()</span>·<span class="no">execute()</span> 처럼 무엇을 시키는지 안 말하는 이름은 위반이다.<br>
<b>창구와 달리 접미사를 안 붙이는 이유</b> — 클래스가 이미 <code>&lt;Capability&gt;Port</code> 로 자리를 말했다. <b>그리고 이 규칙이 T1 의 뿌리를 덮는다</b> — <code>child_eviction_notification</code> 의 <code>notify()</code> 가 정확히 이 빈 자리에서 나왔다.</dd>

<dt class="ans-dt">함께 박은 구분선 — <b>파일에는 «종류», 함수에는 «의도»</b></dt>
<dd class="ans-dd filled"><code>&lt;use_case&gt;_use_case.py</code> 의 이름 규칙은 <b><code>_command</code>·<code>_query</code> 를 «금지»</b>하고 있다(«종류»가 아니라 옛 축이라서). 같은 낱말을 한 곳에서 금지하고 다른 곳에서 강제하게 되므로 <b>양쪽 «이름» 슬롯에 이유를 함께 적었다</b> — <b>파일 이름에는 종류가 오고 함수 이름에는 의도가 온다.</b> 자리가 다르지 낱말이 뒤집힌 게 아니다.</dd>

<dt class="ans-dt">확인하다 나온 것 — <b>관문 규칙 하나가 반쪽이었다 (T27)</b></dt>
<dd class="ans-dd filled">「도메인 예외는 «타입»으로만 쓴다 — <code>except … as e</code> 로 묶은 이름을 참조하면 위반」이 <b><code>&lt;area&gt;_controller.py</code> 에만</b> 걸려 있었다. 그런데 트리 자신이 OHS 관문을 <b>「컨트롤러와 같은 자리이고 하는 일도 같다」</b>고 적고, <b>「도메인 예외를 그대로 내보내면 상대 BC 가 우리 내부 모델에 결합되어 내부를 못 고치게 된다」</b>고도 적는다. <b>OHS 쪽이 더 세다</b> — HTTP 는 클라이언트가 문자열을 보는 것이고 OHS 는 상대 BC 가 <b>파이썬 타입을 <code>import</code></b> 하는 것이다. <b>확장한다.</b><br>
<b>반론 검토</b> — 「번역할 때 사유 코드를 옮기려면 필드를 읽어야 하지 않나」. 트리는 그걸 다르게 푼다: <code>exception/</code> 의 판정이 <b>「이 창구가 혼자서 답을 만들 수 있나」</b>라, <b>사유를 옮겨야 하면 애초에 <code>response/</code> 로 가야 한다</b>.<br>
<b>안 연 것 둘</b> — ⒜ <code>raise X from exc</code> 예외 허용: 금지해도 <b>트레이스백에서 원인을 잃지 않는다</b>(<code>except</code> 블록 안에서 새로 던지면 파이썬이 <code>__context__</code> 를 자동으로 단다). 허용하면 검사가 「<code>as</code> 는 되지만 <code>str(e)</code>·<code>e.field</code> 는 안 된다」로 넓어져 <b><code>ast</code> 가 사실상 <code>human</code> 으로 내려앉는다</b>. ⒝ <code>cron_job/&lt;job&gt;.py</code> 포함: <b>바깥에 공개하는 계약이 없어</b> 규칙의 목적이 안 걸린다(규율 ⑤).</dd>
</dl>

## D38 · framework/ 로 «올리는» 자와 «되돌리는» 자 — 자격만으로는 안 올린다

**확정 · 08-08 · F8** · 자리 — <code>framework/</code> &nbsp;·&nbsp; <b>흩어져 있던 승격 규칙 넷을 하나로 · 강등 규칙 신설 · 새 칸 0</b>

<dl class="kv">
<dt class="ans-dt">물음 — <b>「처음엔 BC 에 있다가 어느 시점에 <code>framework/</code> 로 넘어가도록 «관리»해야 한다」</b></dt>
<dd class="ans-dd filled"><b>맞는데, 지금 트리는 그 반대로 적힌 자리가 셋이다.</b> 승격 규칙이 <b>넷</b>인데 축이 둘로 갈려 있었다.
<div class="pre-wrap"><table class="mini">
<tr><th>자리</th><th>적혀 있던 조건</th><th>축</th></tr>
<tr><td><code>framework/&lt;capability&gt;/</code></td><td>「업무 어휘가 한 글자도 안 나온다」</td><td><b>성질</b></td></tr>
<tr><td><code>framework/&lt;technology&gt;/</code></td><td>「어느 BC 에 놓아도 똑같이 동작한다」</td><td><b>성질</b></td></tr>
<tr><td><code>adapter/&lt;capability&gt;/</code> → framework</td><td>「업무 어휘가 0이면 올린다」</td><td><b>성질</b></td></tr>
<tr><td><code>framework/test/&lt;module&gt;.py</code></td><td><b>「두 번째 BC 가 같은 걸 만들면 그때」</b> + BC 독립</td><td><b>시점</b> + 성질</td></tr></table></div>
<b>셋은 「성질이 맞으면 바로 올린다」이고 하나만 「두 번째 사용자가 생기면 올린다」였다.</b>
<span class="dim"><b>08-10 · C2 — 그 하나를 셋 쪽으로 맞췄다.</b> 「시점」 축이 통째로 없어졌다 — 아래 결정 ① 참조.</span></dd>

<dt class="ans-dt">결정 ① — <b>자는 하나다: 「이 낱말의 뜻을 «누가» 정하나」</b> <span class="dim">08-10 · C2 개정</span></dt>
<dd class="ans-dd filled"><div class="pre-wrap"><table class="mini">
<tr><th>뜻을 정하는 자</th><th>보기</th><th>자리</th></tr>
<tr><td><b>저장소 밖</b> — 표준 · 프레임워크 · OS · 프로토콜</td><td><code>now()</code> · <code>send_email()</code> · JSON Patch · RFC 9457 오류 표현</td><td><b><code>framework/</code></b></td></tr>
<tr><td><b>우리 업무</b></td><td>「요청 시각으로 유효한지 판단」 · 「환불 7일」</td><td><b>그 BC</b> — 두 BC 가 같은 값을 갖고 있어도 각자</td></tr></table></div>
<b>개수는 안 묻는다.</b> BC 가 하나여도 그 BC 것이 아니면 처음부터 <code>framework/</code> 에 만들고,
두 BC 가 똑같은 업무 규칙을 갖고 있어도 그건 여전히 <b>각자의 것</b>이다.
<span class="dim"><b>08-10 · C2 — 옛 결정은 «자격 + 계기» 둘이었고 계기가 「두 번째 BC」였다.</b>
걷어낸 까닭 셋 — ⑴ <b>수가 소유를 검증하지 못한다</b>(두 BC 가 같은 업무 규칙을 가져도 각자 것이고, 시계는 BC 가 하나여도 BC 것이 아니다) ·
⑵ 「둘」의 유일한 근거가 <b>실측 한 줄</b>이었다(<code>jpatch</code> 7벌) — 원전 넷 중 수를 말하는 것은 Roberts/Fowler 하나이고 그건 «셋»이다 ·
⑶ 남겨 두면 <b>「둘이 됐으니 올려도 되겠지」가 소유 판정을 건너뛴다</b> — 약한 자가 강한 자를 밀어낸다.
<b>「셋」으로 올리는 안도 기각했다</b> — 같은 지식인 걸 알면서 두 벌을 더 오래 유지하라는 뜻이 되어 DRY 와 정면으로 부딪힌다.</span>
<span class="dim"><b>자료조사가 셋 다 같은 쪽을 가리켰다.</b>
<b>Sandi Metz</b>(The Wrong Abstraction) — 「잘못된 추상은 중복보다 비싸다」. 실패 순서가 정해져 있다: 추상을 만듦 → 안 맞는 요구 → <b>매개변수와 조건 분기</b> → 반복 → 못 읽는 코드. ·
<b>Grzybek</b>(Modular Monolith with DDD) — <b>공유 폴더를 아예 안 만든다.</b> 모듈을 넘는 것은 통합 이벤트 계약뿐이고 인프라 구현은 각 모듈에 남는다. ·
<b>DDD Crew</b>(Context Mapping) — Shared Kernel 은 「작게 유지하고 <b>바꾸기 전에 협의</b>한다」. 공유는 협의 비용을 낳는다.</span></dd>

<dt class="ans-dt">예외 0 — <b>다섯 자식이 «같은 자»를 받는다</b> <span class="dim">08-10 · C2 개정</span></dt>
<dd class="ans-dd filled">옛 결정은 <code>&lt;technology&gt;/</code> 에만 «계기» 면제를 줬다. 계기가 없어지면서 <b>예외도 함께 없어졌다</b>.
<b><code>&lt;capability&gt;/</code></b>(시계·난수) — 시계가 시계인 것은 BC 가 몇 개든 상관없다. <b><code>&lt;technology&gt;/</code></b> — Ninja 타입 없이는 문장이 성립하지 않는다.
<b><code>pure/</code></b> — 업무 어휘 0 이 정의다. <b><code>broker/</code>·<code>test/</code></b> — 고정 이름 칸이라 <b>존재 자체가 제1원칙</b>이고 판단 대상이 아니다.
<span class="dim">옛 자(「BC 안에 자리가 있었던 적이 있나」)는 <b>「기다릴 첫 번째가 있나」를 묻는 자</b>였다 — 기다리기를 없애니 물을 것이 없다.</span></dd>

<dt class="ans-dt">결정 ② — <b>강등 규칙을 새로 넣는다</b> <span class="dim">지금 트리에 승격 넷 · 강등 0 이었다</span></dt>
<dd class="ans-dd filled"><b><code>framework/&lt;capability&gt;/&lt;capability&gt;_port.py</code> 의 시그니처에 «BC 를 가르는 인자»가 나오면 위반</b>(<code>kind</code>·<code>mode</code>·<code>bc</code>·<code>is_…</code>).
<b>능력이 하나가 아니라 둘이었다</b>는 뜻이라, 매개변수를 더 받는 게 아니라 <b>인라인해서 각 BC 로 돌려보내고 다시 뽑는다</b>.
<br>Metz 의 신호가 정확히 이것이다 — 「<b>공유 코드에 매개변수와 조건 분기를 넣고 있으면 그 추상은 틀렸다</b>」. 그리고 그가 말한 실패의 핵심은 <b>「올라간 게 못 내려온다」</b>이다.
<b>승격만 있고 강등이 없으면 틀린 추상이 영원히 남는다.</b> <em>AST 한 줄로 선다.</em></dd>

<dt class="ans-dt">결정 ③ — <b><code>&lt;technology&gt;</code> 가 양쪽에 나오는 혼동은 «판정 교체»로 푼다</b></dt>
<dd class="ans-dd filled">같은 낱말이 <b>깊이가 다른 두 자리</b>에서 다른 역할을 한다:
<div class="pre-wrap"><pre><code>framework/&lt;capability&gt;/&lt;technology&gt;.py    파일 · 기술이 2차 축   clock/django.py
framework/&lt;technology&gt;/&lt;module&gt;.py        폴더 · 기술이 1차 축   ninja/framework_error_schema.py</code></pre></div>
기계는 갈리는데(폴더 안에 <code>*_port.py</code> 가 있나) <b>사람이 새 파일을 놓을 때</b> 「django 관련이니 <code>django/</code> 로?」라고 생각하기 쉽다.
<b><code>clock/django_adapter.py</code> 는 거기 가면 안 되는데 그 이유가 이름에서 안 보인다.</b>
<br><b>판정을 <code>driven_layer/adapter/</code> 와 같은 자로 바꾼다 — 「이 파일이 «어떤 계약의 구현»인가」.</b>
예면 그 계약 폴더, 아니면 기술 폴더. <b>새 낱말 0 · 새 칸 0</b>이고, 기계 검사가 그대로 뒤에서 받친다.
<span class="dim">실무 관례는 <b>기술 이름을 «클래스 접두사»로 쓰고 폴더로는 잘 안 쓴다</b> — Vernon 의 IDDD 도 <code>port/adapter/persistence/</code> 아래에 <code>LevelDB…Repository</code> 로 둔다.
우리도 그렇게 하는데(<code>Django&lt;Capability&gt;Adapter</code>) <b>이 칸만 예외</b>인 것은, 여기 사는 코드가 어느 계약의 구현도 아니라 <b>붙일 능력 폴더가 없기 때문</b>이다. 대안 <code>infrastructure/</code> 는 <b>D37</b> 에서 이미 기각됐다(지층 이름).</span></dd>
</dl>

## D37 · port/ ↔ adapter/ 로 짝을 맞춘다 — 층 이름은 «방향», 폴더 이름은 «부품»

**확정 · 08-08 · F6+F7** · 자리 — <code>application_layer/port/</code> &nbsp;·&nbsp; <code>driven_layer/adapter/</code> &nbsp;·&nbsp; <b>트리 102 → 107행 · 카드 여섯을 다시 열었다</b>

<dl class="kv">
<dt class="ans-dt">물음 — <b>「<code>driven_layer/&lt;capability&gt;.py</code> 를 폴더로 할까 · 애초에 그 칸이 필요한가」</b></dt>
<dd class="ans-dd filled"><b>둘 다 «그렇다»인데, 그 칸의 «무엇이 오나»가 자기 판정에 한 건도 안 맞았다.</b>
판정은 <em>「계약에 업무 어휘가 있으면 여기, 0이면 <code>framework/</code>」</em> 인데 예시가 <b>시계·난수·락·스레드·파일시스템</b> 다섯이었다 —
<code>now()</code>·<code>uuid4()</code>·<code>acquire(key)</code>·<code>read(path)</code>, <b>다섯 다 업무 어휘가 0</b>이라 전부 <code>framework/&lt;capability&gt;/</code> 로 간다.
실제로 <code>framework/&lt;capability&gt;/</code> 가 드는 예시가 <code>clock/</code>·<code>random/</code> 이다 — <b>같은 것을 두 칸이 서로 자기 것이라고 적고 있었다.</b></dd>

<dt class="ans-dt">그 칸에 실제로 사는 것 — <b>밖에 «상대»는 없는데 «기술»이 필요한 일</b></dt>
<dd class="ans-dd filled">주문서를 PDF 로 빚기 · QR 만들기 · 정산 엑셀 뽑기 · 썸네일.
<div class="pre-wrap"><table class="mini">
<tr><th>옮겨보면</th><th>왜 안 되나</th></tr>
<tr><td><code>external_system/</code></td><td>거긴 「저장소 밖의 <b>상대</b>」 자리인데 <b>물어볼 상대가 없다</b></td></tr>
<tr><td><code>domain_layer/</code></td><td>전역 제약 ② — <b>라이브러리 없이는 못 하는 일</b>이다</td></tr>
<tr><td><code>framework/&lt;capability&gt;/</code></td><td>거긴 「어느 BC 것도 아닌 것」 자리인데 <b>«주문서» 레이아웃은 업무 지식</b>이다</td></tr>
</table></div>
<b>판정이 3단이 된다</b> — ① 밖에 상대가 있나 → ② 없으면 기술이 필요한가 → ③ 계약에 업무 어휘가 있나. 옛 문면은 ③ 만 있었다.
<span class="dim"><b>정직한 단서 — 사용자가 예시 셋을 반박해 근거를 다시 세우게 했다.</b>
내가 든 «메일»은 상대가 SMTP 서버라 <code>external_system/</code> 이고(나는 «장고 내장이라 벤더가 아니다»로 봤는데, 그 칸의 판정은 <b>어떤 라이브러리를 쓰나가 아니라 상대가 저장소 밖이냐</b>였다),
«영업일 계산»은 바깥에 아무것도 안 물어서 <b>도메인</b>이고, «시계»는 애초에 이 칸 얘기가 아니었다.
내가 처음에 낸 「필요하다」 논증은 <b>「여기 뭔가 산다」를 전제로 「지우면 갈 데가 없다」를 편 것</b>이라 전제부터 안 세워져 있었다.</span></dd>

<dt class="ans-dt">그래서 폴더가 됐고, 그 김에 <b>안팎의 이름을 짝지었다</b></dt>
<dd class="ans-dd filled"><b>선언은 전부 <code>port/</code> 아래로, 구현은 전부 <code>adapter/</code> 아래로.</b>
<div class="pre-wrap"><pre><code>application_layer/port/                     driven_layer/adapter/
  &lt;capability&gt;/            ──────────▶        anticorruption_layer/&lt;bc&gt;/
                           ──────────▶        external_system/&lt;system&gt;/
                           ──────────▶        &lt;capability&gt;/
  domain_bypass_query/&lt;cap&gt;/ ─────▶      persistence/domain_bypass_query/&lt;cap&gt;.py
  unit_of_work/            ──────────▶        persistence/unit_of_work/
domain_layer/&lt;aggregate&gt;_repository.py ▶      persistence/repository/&lt;aggregate&gt;_repository.py</code></pre></div>
<b>하나만 하나가 셋으로 갈린다</b> — «필요»는 하나인데 «누가 해 주나»는 여럿일 수 있어서다.
<b>D17</b> 의 <b>「포트는 «필요»로, 어댑터는 «누구»로」</b> 가 그대로 산다.</dd>

<dt class="ans-dt"><code>adapter/</code> 를 만든 근거 — <b>D17 의 전제가 낡았다</b></dt>
<dd class="ans-dd filled">D17 이 <code>adapter/</code> 를 접은 문장은 <em>「이 칸에 있는 것이 <b>전부</b> Adapter 라 그런 폴더는 아무 선도 긋지 못한다」</em> 였다.
<b>전부가 아니다</b> — <code>django_&lt;bounded_context&gt;/</code> 는 어댑터가 아니라 표 정의·마이그레이션·운영 화면이고, <b>지키는 약속이 없다</b>.
그 하나가 선을 긋는다: <code>ls driven_layer/</code> 가 <b>「프레임워크가 정한 것 / 우리가 정한 것」</b> 으로 읽힌다.
그리고 겹이 규칙을 하나 만든다 — <b><code>adapter/</code> 아래 모든 <code>.py</code> 는 «어떤 선언의 구현»이고 그 선언을 «경로»가 가리킨다.</b>
<span class="dim">08-10 · CHK-3 — 옛 문장은 「파일 이름이 그 선언과 같다」였다. <b><code>repository/</code> 쪽에서만 참</b>이고 <code>&lt;capability&gt;/</code> 아래는 <b>폴더가 선언을 · 파일이 기술을</b> 말한다(T48).</span></dd>

<dt class="ans-dt">기각 — <b><code>adapter_layer/</code> 개명 · <code>infrastructure/</code> · <code>repository/{command,query}</code></b></dt>
<dd class="ans-dd filled"><b><code>adapter_layer/</code></b> — 자료 조사가 둘 다 막는다.
<b>Cockburn 은 «어댑터»를 층 이름으로 쓰지 않는다</b>(육각형에는 «층» 축 자체가 없다 — 있는 것은 안팎과 primary/secondary 역할 구분뿐이다).
<b>Martin 의 「Interface Adapters」는 입구까지 함께 담는다</b>(컨트롤러·프레젠터·게이트웨이가 한 링) — 그러니 한쪽만 그렇게 부르면 <b>「저쪽은 어댑터가 아니다」는 거짓말</b>이 된다.
트리도 이미 그렇게 적고 있었다 — <code>driving_layer/</code> 는 <b>Primary Adapter</b>, <code>driven_layer/</code> 는 <b>Secondary Adapter</b> 자리다.
<br><b><code>infrastructure/</code></b> — 「인프라냐」는 <b>정도로 재는 말</b>이라 서랍이 된다. 그 칸 전부가 인프라 구현이다.
<br><b><code>repository/{command, query}</code></b> — <b><code>command</code> 가 거짓</b>이 된다. 애그리거트 리포지토리는 <code>find_by_id</code>·<code>exists</code>·<code>count</code> 로 <b>읽기도 한다</b>.
그리고 그 겹에는 <b>공통 규칙이 0</b>이다 — 아래 둘의 도메인 import 가 <b>필수 ↔ 금지</b>로 정반대다.
<span class="dim"><b>겹이 정당해지는 조건</b>은 «공통 규칙이 있나»다. 그래서 셋으로 넓혀 <code>persistence/</code> 가 됐다 —
<b>ORM 모델을 import 할 수 있는 것은 이 폴더 안뿐</b>이라는 규칙 하나가 생긴다. 이름은 Vernon 의 것이다(IDDD 의 실제 경로가 <code>port/adapter/persistence/</code>).</span></dd>

<dt class="ans-dt">이름 둘을 갈았다 — <b><code>query_repository</code> → <code>domain_bypass_query</code></b> · <b><code>transaction</code> → <code>unit_of_work</code></b></dt>
<dd class="ans-dd filled"><b>가르는 축은 「도메인을 거쳤나」</b>이지 CQRS 의 command/query 가 아니다.
<code>query_repository</code> 는 「조회냐」로 물어서 <b>애그리거트 리포지토리와 안 갈린다</b> — 이름이 사람을 틀린 데로 민다.
<code>common/</code>·<code>utils/</code> 를 기각한 잣대(<b>「판정이 되는 물음이 있나」</b>)가 여기에도 걸린다.
<br><code>bypass_repository</code> 로는 <b>무엇을 우회하는지가 빠져</b> <code>domain_</code> 을 붙였다.
<br><code>transaction</code> 은 <b>장고의 낱말</b>이고, 트리가 <em>「<code>connection</code>·<code>transaction</code> 을 아는 것은 여기(드리븐)까지」</em> 라고 못박아 두고 <b>응용층 폴더 이름에 그 말을 쓰고 있었다</b>.
파일도 클래스도 이미 <code>unit_of_work</code> 였다. <span class="dim"><code>uow/</code> 는 규율 ④(약어를 쓰지 않는다)에 걸린다.</span></dd>

<dt class="ans-dt">파일에는 <b>접미사를 안 붙인다</b> — <code>domain_bypass_query/&lt;capability&gt;.py</code>
<span class="dim">← <b>08-08 · D41 이 이 절을 뒤집었다.</b> 아래는 그때의 기록.</span></dt>
<dd class="ans-dd filled"><b>D33</b> 이 정한 대로 <b>«종류»는 클래스가 진다</b>(<code>Django&lt;Capability&gt;DomainBypassQuery</code>).
붙이면 <b>한 경로에 같은 낱말이 두 번</b>이고, <b>「파일 이름이 선언과 같다」 검사가 깨진다</b>.
형제 셋(<code>anticorruption_layer/</code>·<code>external_system/</code>·<code>&lt;capability&gt;/</code>)도 전부 <code>&lt;capability&gt;.py</code> 다 —
<code>repository/&lt;aggregate&gt;_repository.py</code> 만 접미사가 있는데 그건 <b>붙인 게 아니라 선언에서 물려받은 것</b>이다(<code>domain_layer/</code> 에는 폴더가 말해 주지 않는다).
<span class="dim"><b>틀린 자리 둘.</b> ⑴ <b>형제를 잘못 골랐다</b> — 이 칸의 형제는 <code>adapter/</code> 의 자식이 아니라 <code>persistence/</code> 의 자식 셋이고, 그중 <b>둘이 이미 접미사를 달고 있었다</b>(<code>&lt;aggregate&gt;_repository.py</code> · <code>&lt;boundary&gt;_unit_of_work.py</code>). ⑵ <b>「검사가 깨진다」가 거짓</b>이다 — 선언과 구현이 <b>같이</b> 달면 1:1 은 그대로 선다.</span></dd>

<dt class="ans-dt">치른 값 — <b>카드 여섯을 다시 열었다</b></dt>
<dd class="ans-dd filled"><b>D17</b>(<code>adapter/</code> 금지가 뒤집힘) ·
<b>D20</b>(허용 목록이 <b>넷 → 둘</b>) ·
<b>D29</b>(<code>port/</code> 의 «형제» → «아래») ·
<b>D31</b>(폴더 이름) ·
<b>D33</b>(<code>…QueryRepository</code> → <code>…DomainBypassRepository</code> — <em>그 뒤 D41 이 «Repository» 를 뗐다</em>) ·
<b>D14</b>(«UoW 는 <code>port/</code> 가 아니다»의 자리 결론 — <em>3차 리뷰 T3 에서 뒤늦게 목록에 넣었다; «괄호» 판정은 산다</em>).
경로가 한 마디 길어진다(최장 <code>driven_layer/adapter/persistence/domain_bypass_query/&lt;capability&gt;.py</code>).
<br><b>얻은 것</b> — D20 의 허용 목록이 <b>넷에서 둘로</b> 준다. 08-07(F5)에 그 목록이 낡아 <b>트리 두 줄이 자기 선언조차 import 할 수 없는 상태</b>였다. 목록이 짧을수록 낡을 자리도 준다.</dd>
</dl>

## D36 · 계약을 지켰으면 답이 나와야 한다 — 예외는 «답을 못 만들 때»만이다

**확정 · 08-07 · F4 (판정 축 1회 교체) · 08-09 · T38** · 자리 — <code>contract/{response,exception}/</code> &nbsp;·&nbsp; <code>anticorruption_layer/&lt;bc&gt;/&lt;capability&gt;.py</code> &nbsp;·&nbsp; <b>새 칸 0 · 규칙 넷</b> &nbsp;·&nbsp; <span class='dim'>08-09 · T38 — <b>같은 논증이 «BC 안»에는 안 걸린다</b> · 트리 신설 0 · 검사 하나</span>

<dl class="kv">
<dt class="ans-dt">물음 — <b>「기저 예외가 필요한가 · 애초에 예외 없이 <code>response</code> 만으로 되지 않나」</b></dt>
<dd class="ans-dd filled">뒤엣것부터. <b>안 된다 — 셋이 같은 방향이다.</b>
<div class="pre-wrap"><table class="mini">
<tr><th>없애면</th><th>무엇이 깨지나</th></tr>
<tr><td><b>번역할 «대상»이 사라진다</b></td><td>이 칸이 하는 일은 「도메인 예외를 잡아 <b>공개 타입으로 바꿔 다시 던진다</b>」인데, 던질 타입이 없으면 <b>도메인 예외가 그대로 상대에게 나간다</b>. <code>port/&lt;capability&gt;/exception.py</code> 를 «필수»로 만든 것과 <b>같은 이유</b>다</td></tr>
<tr><td><b>성공 응답이 흐려진다</b></td><td><code>response/</code> 는 「여기 있는 필드가 곧 상대가 우리에게서 알 수 있는 것의 전부」인데, 실패를 같이 담으면 성공 경로의 필드가 <b>전부 «있을 수도 없을 수도»</b> 가 된다</td></tr>
<tr><td><b>무시해도 아무 말이 없다</b></td><td>파이썬은 반환값을 버려도 조용하다 — <code>publish(req)</code> 한 줄이면 실패가 사라진다. 예외는 무시하려면 <code>try/except: pass</code> 를 <b>직접 써야</b> 한다</td></tr></table></div>
<b>그런데 물음이 진짜 구멍을 짚었다 — 트리는 「예외 폴더가 있다」만 말하고 「무엇이 예외인가」를 안 말했다.</b></dd>

<dt class="ans-dt">★ 판정 축을 한 번 갈아끼웠다 — <b>처음 것은 창구가 «부르는 쪽»을 추측하는 물음이었다</b></dt>
<dd class="ans-dd filled"><b>사용자 지적</b>: <em>「요청을 보낸 쪽이 계약을 지켜서 요청하면 받은 쪽은 <b>응답이 무조건 가능해야</b> 한다. 그래야 계약에 의미가 있다. A→B 「물건 리스트 줘」면 B 는 물건이 없을 때 <b>예외가 아니라 빈 리스트</b>를 보내고, 빈 리스트가 오면 <b>A 가</b> 그걸 예외로 처리한다. <b>보내는 쪽은 어떻게 쓸지 모르기 때문에 예외 처리가 불가능하다.</b>」</em><br>
<b>맞는 말이고, 이건 Design by Contract 그대로다</b> — 「호출자가 선행조건을 지키면 피호출자는 후행조건을 <b>반드시</b> 낸다」. <span class="dim">F2 조사에서 확인했듯 DDD 원전의 <code>contract</code> 도 정확히 Meyer 의 이 뜻이다.</span><br>
<b>처음에 넣었던 판정이 틀린 자리에 있었다</b> — <em>「부르는 쪽이 그걸 받고 «계속» 하나?」</em> 였는데, <b>창구는 부르는 쪽을 모른다</b>. 답할 수 없는 것을 묻고 있었다.
<div class="pre-wrap"><pre><code>옛 판정   「부르는 쪽이 계속 하나?」      ← B 가 A 의 사정을 추측한다
새 판정   「이 창구가 «혼자서» 답을      ← B 자신만 보면 답이 나온다
           만들 수 있나?」</code></pre></div></dd>

<dt class="ans-dt">결정 ㉮ — <b>답을 낼 수 있으면 전부 <code>response/</code>, 낼 수 없을 때만 <code>exception/</code></b></dt>
<dd class="ans-dd filled">
<div class="pre-wrap"><table class="mini">
<tr><th>상황</th><th>창구가 답을 낼 수 있나</th><th>어디로</th></tr>
<tr><td>물건이 없다</td><td><b>낼 수 있다</b> — 빈 목록</td><td><code>response/</code></td></tr>
<tr><td>이미 접수돼 있다</td><td><b>낼 수 있다</b> — 「못 했다 + 사유」</td><td><code>response/</code></td></tr>
<tr><td>업무 규칙이 거절한다</td><td><b>낼 수 있다</b> — 「못 했다 + 사유」</td><td><code>response/</code></td></tr>
<tr><td>모양이 틀린 요청</td><td>계약 위반 — <b>우리 편 개발자 실수</b></td><td>테스트·타입 체커</td></tr>
<tr><td><b>저장소가 죽었다 · 우리가 부르는 바깥이 응답 없다</b></td><td><b>낼 수 없다 — 돌려줄 것이 아예 없다</b></td><td><b><code>exception/</code></b></td></tr></table></div>
<b>결과가 나빠서 예외인 게 아니라, 돌려줄 것이 없어서 예외다.</b> 「없다」·「거절됐다」가 심각한 일인지는 <b>부르는 쪽만 안다</b> — 창구가 예외를 던지면 그 판단을 가로챈다.</dd>

<dt class="ans-dt">결정 ㉯ — <b><code>response/</code> 의 뜻이 바뀐다</b></dt>
<dd class="ans-dd filled">«성공의 모양»이 아니라 <b>«이 창구가 낼 수 있는 답 전부»</b>다. <b>거절도 답이다.</b><br>
<b>못 해 준 사유는 «코드»로 담는다 — 문장이 아니다.</b> 자유 문자열을 넣으면 부르는 쪽이 그걸 파싱해 분기하고, <b>문구를 다듬는 순간 남의 BC 가 깨진다</b>. 코드 목록이 곧 «이 창구가 낼 수 있는 답의 갈래»이고, 그게 는다는 건 계약이 바뀐다는 뜻이라 눈에 보여야 한다. <span class="dim">도메인 예외를 <code>bc_error_schema.py</code> 의 «코드»로 바꿔 내보내는 것과 같은 자다(<b>D11</b> · F1).</span></dd>

<dt>딸려 오는 것 — <b><code>exception/</code> 이 작아지고, 그만큼 import 도 준다</b></dt>
<dd>이 판정으로 재면 공개 예외에 남는 것은 <b>인프라 실패 갈래</b>뿐이다. 그러면 부르는 쪽이 <b>상대의 예외 타입을 import 할 일 자체가 줄어든다</b> — <b>D35</b> 가 「계약 import 는 안전하다」고 했지만 <b>적게 import 하는 편이 여전히 낫다</b>.<br>
<b>그래도 폴더는 남는다</b> — 부르는 쪽이 「저쪽이 잠시 죽었다(다시 걸어볼 일)」와 「내 코드 버그」를 갈라야 하고, 이름이 없으면 못 가른다.</dd>

<dt>치르는 값 — <b>부르는 쪽이 응답을 «안 보면» 조용히 지나간다</b></dt>
<dd><code>결과 = 창구.접수(요청)</code> 에서 <code>결과.접수됨</code> 을 안 보면, 거절됐는데 된 줄 알고 다음으로 간다. <b>예외는 무시하려면 <code>try/except: pass</code> 를 직접 써야 하지만 반환값은 그냥 버려도 조용하다.</b><br>
트리의 자로 재면 이건 <b>개발자 실수라 테스트·타입 체커 몫</b>이다(<code>&lt;use_case&gt;_command.py</code> 와 같은 자). 논리는 닫히지만 <b>결제 거절 같은 갈래는 실제로 위험하다</b> — <span class="dim">기록해 둔다. 규칙을 무르는 근거는 아니고, 이 선택의 대가다.</span></dd>

<dt>기저 예외 — <b>있던 이유가 «편의»였다</b></dt>
<dd>옛 문장은 <em>「부르는 쪽이 <code>except &lt;Service&gt;PublishedError</code> 한 줄로 <b>가족 전체를 잡을 수 있어야</b> 한다」</em> 였다. <b>편의는 근거가 못 된다</b> — 「전체를 한 줄로 잡아 하나로 매핑할 거면 갈래를 왜 나눴나」에 바로 무너진다.<br>
<b>진짜 이유는 <code>anticorruption_layer/</code> 의 약속을 성립시키는 조건이다.</b> 그 칸이 한 약속은 「상대 BC 의 것은 나를 지나가지 못한다」이고 <b>예외도 상대 BC 의 것</b>이다. <span class="dim">㉮ 로 폴더가 작아져도 이 규칙은 그대로다 — 인프라 실패 갈래는 <b>저쪽 인프라가 바뀌면 는다</b>.</span> 잡는 방법이 둘뿐인데 —
<div class="pre-wrap"><pre><code>⒜ 하나씩 나열한다        except (거절됨, 충돌, 일시장애):
   → 상대가 예외를 «하나 더» 만들면 목록이 낡는다.
     이쪽 코드는 한 글자도 안 바뀌었는데 약속이 깨진다.
     새 예외는 ACL 을 그냥 통과 → 컨트롤러가 매핑 못 함 → 조용히 500

⒝ 한 줄로 «전부» 를 가리킨다   except 배송창구실패:
   → 파이썬의 except 는 «자식도 같이» 잡으므로 부모 하나면 끝난다.
     그러려면 전부를 아우르는 이름이 하나 필요하다 = 기저 예외</code></pre></div>
<b>기저 없이 ⒝ 를 하려면 <code>except Exception</code> 뿐인데, 그건 상대 것뿐 아니라 내 코드의 버그(<code>AttributeError</code> 같은 것)까지 삼킨다.</b> <span class="dim"><b>D27</b> ③ 이 이미 <code>except Exception</code> 을 금지하고 있었다 — 그 조문이 성립하려면 기저가 있어야 한다.</span></dd>

<dt class="ans-dt">결정 ㉯ — <b>그물을 «있어도 되는 것»에서 «반드시 있어야 하는 것»으로 올린다</b></dt>
<dd class="ans-dd filled"><code>anticorruption_layer/&lt;bc&gt;/&lt;capability&gt;_adapter.py</code> 는 <b>상대 창구의 기저 예외를 반드시 잡는다</b> — 구체 타입을 앞에 몇 개 잡든 자유고, <b>마지막에 부모가 있어야 한다</b>. AST 한 줄.<br>
생산자 쪽 짝도 검사가 된다 — <b>그 창구의 공개 예외 중 기저를 상속하지 않는 것이 있으면 위반</b>(중간에 한 단계 더 두는 것은 되고, 끝까지 따라가면 기저에 닿아야 한다).<br>
<b>이 둘이 짝이라야 약속이 닫힌다</b> — 생산자가 «전부 기저 밑에» 두고, 소비자가 «마지막에 기저를» 잡는다. 한쪽만 있으면 구멍이 남는다.</dd>

<dt>거절 사유가 늘어나는 것은 <b>이제 계약 변경이 된다</b></dt>
<dd>상태와 업무 규칙은 상대 BC 안에 있어서 <b>저쪽 세계가 자라면 거절 사유가 는다</b> — 이쪽은 그대로인데. 옛 판정에서는 그게 <b>예외가 하나 느는 것</b>이라 조용히 지나갔는데, ㉯ 로 옮기면 <b><code>response/</code> 의 코드 목록이 느는 것</b>이라 <b>계약 파일이 바뀐다</b>. <span class="dim">이게 값이다 — 「남의 BC 가 알아야 하는 변화」가 계약 diff 에 드러난다.</span></dd>

<dt class="ans-dt"><b>08-09 · T38 — 같은 논증을 «BC 안»에 대려다 무너졌다</b></dt>
<dd class="ans-dd filled">4차 리뷰(SC-B)가 <b>blocker</b> 로 올린 것 — <em>「도메인 예외에 기저가 없어서 불변식을 하나 더하면 컨트롤러의 어느 <code>except</code> 에도 안 걸리고 <code>&lt;project&gt;/api.py</code> 로 흘러 «조용히 500» 이 된다. 위 ⒜/⒝ 논증을 <b>같은 BC 안에도</b> 적용해 기저를 두고, 컨트롤러가 «마지막 절»로 잡자」</em>.
<br><b>구멍은 진짜다. 처분이 틀렸다 — 상황이 다르다.</b>
<div class="pre-wrap"><table class="mini">
<tr><th></th><th>ACL — 위 ⒜/⒝ 가 선 자리</th><th>같은 BC 안</th></tr>
<tr><td><b>예외를 늘리는 사람</b></td><td><b>남의 BC</b> — 내 코드는 한 글자도 안 바뀌었는데 깨진다</td><td><b>나</b> — 같은 커밋에서 고칠 수 있다</td></tr>
<tr><td><b>내가 할 수 있는 일</b></td><td><b>없다</b> → 런타임 그물이 유일한 답</td><td><b>있다</b> → 커밋 시점에 기계가 세면 된다</td></tr>
<tr><td><b>기저 + 마지막 절을 두면</b></td><td>약속이 닫힌다</td><td><b>500 이 4xx 로 내려가 알람이 꺼진다</b> — 실수가 «정상 응답»으로 위장된다</td></tr></table></div>
<b>그리고 그 처분은 이 카드가 «버린» 근거를 되살린다</b> — 바로 위에서 「가족 전체를 한 줄로」를 <em>「하나로 매핑할 거면 갈래를 왜 나눴나」</em> 로 기각했는데, 리뷰안의 «마지막 절»이 정확히 그것이다.
<br><b>플러그인도 반대쪽에 서 있다</b> — <code>assert_never</code> 를 설명하며 <em>「새 variant 나 untyped 값은 조용히 반환되거나 BC 오류로 <b>꾸며지지 않고</b> framework-owned <b>500 계약 위반으로 «드러난다»</b>」</em> 라 적는다. <b>플러그인에게 500 은 «조용한» 것이 아니라 «드러나는» 것</b>이고, 「전역 handler 나 <b>catch-all mapper 로 가로채지 않는다</b>」를 못 박아 뒀다.</dd>

<dt class="ans-dt">결정 — <b>규칙이 먼저고 검사는 백스톱이다</b></dt>
<dd class="ans-dd filled"><b>「예외를 만들었다는 것 자체가 어딘가에서 처리하기 위함인데, 만들기만 하고 처리하는 곳이 없다면 명백하게 설계가 잘못된 것이다. 기계적인 검사는 최후의 백스톱 아닌가」</b>(사용자). <b>맞다 — 그리고 이게 처분의 순서를 뒤집었다.</b> 처음 안은 검사를 «1차»로 세웠는데, 그러면 <b>검사가 규칙 노릇</b>을 하게 되고 사람은 걸릴 때마다 <code>except</code> 를 한 줄 붙여 넘긴다.
<div class="pre-wrap"><pre><code>규칙  예외는 «잡는 자리»와 함께 태어난다        ← 정의를 다시 말한 것
검사  이 BC 안 어느 except 에도 안 나오면 위반   ← 그 약속이 깨졌는지만 본다</code></pre></div>
<b><b>D50</b> 과 같은 구조다</b> — 애그리거트는 «정의상» 트랜잭션 경계이고 검사는 「경계가 틀렸다」는 신호였다. 여기서도 <b>예외는 «정의상» 잡히기 위해 있고</b>, 검사는 <b>「계약이 덜 됐다」는 신호</b>다. <span class="dim">백스톱 철학 자체가 이 순서다 — Cockburn: <em>「약속만 하고 «검출 기계»가 없으면 몇 년 뒤 그 층이 업무 로직으로 가득 찬다」</em>. 약속이 먼저 있고 기계는 그게 지켜지는지를 본다.</span>
<br><b>★ 그리고 이 자는 트리에 «이미» 있었다</b> — <b>D37</b> 의 <code>port/</code> ↔ <code>adapter/</code> <b>1:1 짝맞춤</b>. 「선언만 있고 짝이 없으면 설계가 덜 된 것」을 트리가 내내 쓰고 있었는데 <b>예외에만 안 걸려 있었다</b>.
<br><b>잡는 자리는 입구만이 아니다</b> — 유스케이스가 잡아 다른 흐름으로 돌려도 되고, ACL 이 공개 타입으로 번역해도 된다. 그래서 주어를 「컨트롤러」나 「입구 넷」으로 좁히지 않고 <b>「이 BC 안」</b> 하나로 닫았다. <b>BC 안에서 닫히므로 「BC 하나를 지우면 바뀌나」 판정을 통과</b>하고, BC 이름이 한 개도 안 나오니 <b>D25</b> 의 「규칙이지 목록이 아니다」도 통과한다.
<br><b>이 검사가 실제로 무엇을 잡을지는 이미 나와 있다</b> — <b>D40</b> 이 가장 큰 예외 파일(<code>family_usage_quota</code> 16클래스)을 하나씩 재 봤을 때 <b>8이 «여기 있으면 안 되는 것»</b>이었다(포트 너머 6 · 재시도 판정 1 · 미선언 1). <b>답이 「매핑을 추가하라」가 아니라 「그 예외는 여기 것이 아니다」인 경우가 더 많다</b> — 그래서 갈래 셋(계약 누락 · 자리가 틀림 · 가짜 불변식)을 <b>검사가 아니라 칸의 «무엇이 오나»에</b> 적었다.</dd>

<dt><b>기저는 여전히 안 둔다 — «근거»만 갈았다</b></dt>
<dd>옛 문장은 <em>「창구 쪽은 남이 묶어서 잡으라고 기저를 주지만, 여기 것은 «타입»으로만 잡히므로 묶을 대상이 없다」</em> 였는데 <b>앞 절에서 뒤 절이 안 나온다 — 기저도 «타입»이다</b>.
<div class="pre-wrap"><pre><code>㉠ 속성을 안 읽는다 (D11)               참이다 · 그대로 산다
㉡ 도메인 ↔ 포트를 한 except 에 금지     참이다 · 그대로 산다 — «둘을 서로» 묶지 말라는 말
㉢ 그러므로 기저를 두지 않는다           ㉠·㉡ 어느 쪽에서도 안 나온다</code></pre></div>
<b>새 근거는 이 카드가 이미 갖고 있던 것이다</b> — 갈래마다 답이 달라서 <b>묶어서 잡을 일이 없다</b>. <span class="dim">이건 <b>한 문장이 «둘»을 덮은 네 번째</b>다 — <b>D52</b>(「프레임워크」= 라이브러리↔폴더) · T39(D11 의 같은 낱말) · T37(「이름 고정」↔「개수 한정」) · <b>T38(「속성 안 읽기」↔「상속 금지」)</b>.</span></dd>

<dt><b>포트 예외는 안 건드린다 — 리뷰가 둘을 잘못 묶었다</b></dt>
<dd>리뷰의 둘째 축은 <em>「<code>port/&lt;capability&gt;/exception.py</code> 도 같은 «조용한 500» 의 그물이다」</em> 였다. <b>둘은 같은 문제가 아니다.</b>
<div class="pre-wrap"><table class="mini">
<tr><th></th><th>도메인 예외</th><th>포트 예외</th></tr>
<tr><td><b>뜻</b></td><td>업무 규칙을 어겼다</td><td>바깥이 죽었다</td></tr>
<tr><td><b>바깥이 받아야 할 답</b></td><td>「배송된 주문은 취소할 수 없습니다」</td><td>「서버 오류」 · 「잠시 후 다시」</td></tr>
<tr><td><b>안 잡혀 500 이 나가면</b></td><td><b>버그다</b> — 의미 있는 답을 못 냈다</td><td><b>정상이다</b> — 500 이 원래 맞는 답</td></tr></table></div>
플러그인도 인프라 오류를 <b>「기본은 framework 의 미식별 500 경로다」</b> 로 못 박는다. 여기에 기저나 검사를 걸면 <b>오탐만 남는다</b>. <span class="dim">이 축은 <b>D51</b> 이 이미 닫은 자리이기도 하다 — 어댑터는 «계약이 선언한 실패»로 바꿔 내보내고, 그 계약이 어디 사느냐가 답을 정한다.</span></dd>

<dt>딸려 나온 것 — <code>cron_job/</code> 의 재시도</dt>
<dd>그 칸은 <em>「멱등해야 한다 — 재시도가 전제」</em> 만 적고 있었는데, <b>업무 규칙 위반은 다시 돌려도 영원히 같다</b>. 안 잡으면 <b>재시도가 무한히 돈다</b>. 그래서 여기서도 잡되 <b>«답을 내려고»가 아니라 «재시도를 멈추려고»</b> 잡는다 — <b>실패는 층마다 다른 일을 한다</b>(<b>D52</b>).</dd>
</dl>

## D35 · BC 는 서로 부르지 않는다 — 계약 import 는 안전하고, 서로 부르는 것이 안 안전하다

**확정 · 08-07 · F3** · 자리 — <code>open_host_service/&lt;service&gt;/contract/</code> &nbsp;·&nbsp; <code>anticorruption_layer/&lt;bounded_context&gt;/</code> &nbsp;·&nbsp; <b>새 칸 0 · 규칙 둘</b>

<dl class="kv">
<dt class="ans-dt">물음 — <b>「타 BC 의 계약 타입을 import 하면 BC 의존이 생기는데 좋은 방향인가」</b></dt>
<dd class="ans-dd filled"><b>의존을 만드는 것은 import 가 아니라 «호출»이다.</b> 이쪽 BC 가 저쪽 BC 를 부르기로 한 순간 의존은 이미 있고, 계약 타입 import 는 그것을 <b>새로 만드는 게 아니라 «이름 붙이는»</b> 것이다. 타입을 안 쓰고 <code>dict</code> 를 넘겨도 의존은 그대로 있고, <b>깨지는 자리만 CI 에서 런타임으로 옮겨간다</b>.<br>
<b>참조 구현이 만장일치다</b> — 한 프로세스 안에서 도는 모듈러 모놀리스는 <b>예외 없이</b> 상대의 공개 계약 타입을 코드로 import 한다(Grzybek 은 <code>.csproj</code> 참조가 실제로 걸려 있고, Spring Modulith 예제·<code>spring-restbucks</code>·파이썬 예제들도 같다). <b>import 하지 않는 사례는 전부 프로세스가 갈린다</b> — Vernon 의 <code>IDDD_Samples</code> 는 HTTP 표현 문자열, eShop 은 타입 재선언 + 이름 문자열 매칭인데, 둘 다 <b>네트워크 너머라 import 할 방법 자체가 없다</b>.</dd>

<dt>그런데 <b>안전한 반쪽과 위험한 반쪽</b>이 있다</dt>
<dd>크로스-BC import 는 둘로 갈린다. <b>위험한 쪽은 물어본 쪽이 아니다.</b>
<div class="pre-wrap"><table class="mini">
<tr><th>무엇을 import 하나</th><th>무엇이 딸려 오나</th><th>고리</th></tr>
<tr><td><b>계약 타입</b> <code>contract/request/&lt;request&gt;.py</code></td><td><code>dataclass</code> 하나 — <b>그래프의 끝</b></td><td><b>절대 못 낀다</b></td></tr>
<tr><td><b>관문 함수</b> <code>&lt;service&gt;_service.py</code></td><td>→ <code>composition_root</code> → <b>그 BC 의 배선 전체</b></td><td><b>여기서 닫힌다</b></td></tr></table></div>
<b>관문 파일만 «입구인 동시에 남이 import 하는 파일»이다.</b> 컨트롤러도 <code>build_&lt;use_case&gt;()</code> 를 부르지만 아무도 컨트롤러를 import 하지 않으니 진입점으로 끝난다 — <code>open_host_service/</code> 만 그 이중성을 갖는다.<br>
<b>수정안만으로 최소 재현을 지어 확인했다</b>(현행 코드 한 줄도 안 썼다):
<div class="pre-wrap"><pre><code>① A/…/anticorruption_layer/B/&lt;cap&gt;.py   →  B 의 관문 함수
② B/…/open_host_service/…_service.py    →  B/composition_root          D11 와이어링 예외
③ B/composition_root.py                 →  B/…/anticorruption_layer/A/  어댑터를 꽂는다
④ A/…/open_host_service/…_service.py    →  A/composition_root          ②와 같은 이유
⑤ A/composition_root.py                 →  A/…/anticorruption_layer/B/  ③과 같은 이유
⑥ 그 파일이 ① 로 되돌아온다 — ① 은 아직 첫 줄에서 멈춰 있다

ImportError: cannot import name … from partially initialized module
             (most likely due to a circular import)</code></pre></div>
<b>계약만 import 하는 판으로 바꾸면 그대로 부팅된다</b> — 계약이 표준 라이브러리에서 끝나기 때문이다.</dd>

<dt>원전은 <b>여기서 침묵한다</b> — 답한 것은 Martin 하나뿐이다</dt>
<dd><b>Evans</b> 는 서로 필요한 관계에 <b>Partnership</b> 이라는 이름을 붙였지만 처방이 <b>전부 조직·프로세스</b>다(공동 계획 · 같은 릴리스 · 상대 CI 에 계약 테스트). <b>폴더·의존 방향 지시가 한 줄도 없고</b>, 컨텍스트 사이의 «고리»는 아홉 패턴 어디에도 없다. <b>Vernon</b> 은 목차·색인 전수에 「양방향」·「상호 의존」이 <b>0건</b>이고 예제 컨텍스트 맵은 단방향이다. <b>Cockburn</b> 은 앱-대-앱을 «받는 쪽 primary 포트의 어댑터»로만 분류한 뒤 <em>「여기서 secondary 포트에 관한 정보는 보이지 않는다」</em>고 <b>본인이 적어 놨다</b>.<br>
<b>답한 것은 Martin 의 ADP 하나다</b> — 「컴포넌트 의존 그래프에 순환이 있어서는 안 된다」. 깨는 법도 둘로 못 박았다: <b>DIP 로 방향을 뒤집거나, 공통을 새 컴포넌트로 빼거나</b>. 다만 ADP 는 <b>한 빌드 안의 릴리스 단위</b>를 다루므로, 이걸 BC 에 적용하는 것은 <b>우리 확장이다</b>.<br>
<b>도구는 이미 강제한다</b> — Spring Modulith <code>verify()</code> 의 세 규칙 중 <b>1번이 「모듈 의존은 방향 있는 비순환 그래프여야 한다」</b>이고, 파이썬에는 <code>import-linter</code> 의 <code>acyclic_siblings</code>·<code>independence</code> 가 있으며 모듈 27,637개짜리 Django 저장소가 <b>모든 PR 검사</b>에 걸어 쓴다.</dd>

<dt class="ans-dt">결정 — <b>새 칸 0. 규칙 둘.</b></dt>
<dd class="ans-dd filled"><b>㉮ 계약은 «표준 라이브러리»와 «같은 BC 의 다른 계약» 말고는 import 하지 않는다.</b> 이게 있어야 «계약 import 는 안전하다»가 <b>참이 된다</b> — 계약이 남의 BC 를 물면 계약도 고리에 낀다. 덤으로 두 가지가 검사로 내려온다: 요청·응답이 도메인 객체를 담는 것(담으면 <b>부르는 쪽이 만들 수 없는 계약</b>이 된다)과, 계약이 django·SDK 를 무는 것(전역 제약 ②).<br>
<b>㉯ 두 BC 가 서로의 <code>anticorruption_layer/</code> 에 들어 있으면 위반이다.</b> 검사는 <b>폴더 목록 두 번</b>이라 <code>ls</code> 로 선다.<br>
<b>위반이 뜨면 답이 셋이고, 가르는 물음은 «양쪽이 다 일을 시키나, 한쪽은 읽기만 하나»다</b> — 한쪽이 읽기만 하면 <b>경계는 맞고 «호출»이 틀린 것</b>(필요한 필드만 내 쪽에 두거나 좁은 조회 계약 하나만 연다) · 양쪽이 다 일을 시키면 <b>경계가 틀린 것</b>(합친다) · 합칠 수 없으면 <b>개념 하나가 빠진 것</b>(그 흐름을 맡는 BC 를 꺼낸다).</dd>

<dt>버린 안 — <b>배선을 고치는 쪽</b></dt>
<dd><code>open_host_service/</code> 가 <code>composition_root</code> 를 <b>부르지 않게</b> 하고 협력자를 주입받게 하면, 서로 불러도 고리가 안 닫힌다. <code>cosmicpython</code> 의 <code>bootstrap.py</code> 가 정확히 그 모양이다 — <b>합성 루트를 import 하는 것이 진입점과 테스트뿐</b>이라 그래프의 <b>끝</b>에 있다.<br>
<b>접은 이유 둘</b> — ⑴ 물음 하나로 <b>결정 넷이 딸려 열린다</b>(<b>D6</b> 합성 루트 · <b>D11</b> 입구 규칙 · 트리 2행 · 88행) ⑵ 그리고 <b>애초에 F3 의 물음이 아니다</b> — 「합성 루트를 어디에 두나」는 D6·D11 의 물음이다. <span class="dim">고칠 값이 없다는 뜻은 아니다. 이 문단이 그 물음의 자리다.</span></dd>

<dt>같이 못 쓰게 된 것 — <b>Evans 의 Partnership</b></dt>
<dd>상호 의존을 정당화하는 유일한 원전 패턴인데, 그 처방이 전부 <b>«두 팀» 사이의 조율 계약</b>이다(<em>「팀들 사이에 파트너십을 맺어라」</em> · 같은 릴리스에 완료되도록 일정 편성 · 상대 CI 의 계약 테스트). <b>한 저장소·한 팀에서는 그 정당화 근거가 통째로 증발하고 순수한 기술적 고리만 남는다.</b> <span class="dim">판단이지 도출이 아니다 — 기록해 둔다.</span></dd>

<dt>안 쓰기로 한 문장 — <b>「이벤트로 바꾸면 결합이 없어진다」</b></dt>
<dd><b>사실이 아니다.</b> Grzybek 은 모듈 간 통신을 <b>전부 이벤트</b>로 하는데도 <b>모듈 사이 고리가 둘</b> 있다 — 이벤트를 «받으려면» 그 이벤트 타입을 여전히 import 해야 하기 때문이다. Spring Modulith 의 순환 검사도 <b>이벤트 리스너를 봐주지 않아</b>, 두 모듈이 서로의 이벤트를 듣기만 해도 실패한다.<br>
<b>이벤트가 하는 일은 화살표를 «한 방향으로 고정»하는 것이지 «없애는» 것이 아니다.</b> 사라지는 것은 시간 결합뿐이고, 대신 <em>「그 흐름이 어떤 프로그램 텍스트에도 안 보인다」</em>(Fowler)는 새 비용이 붙는다.</dd>

<dt>못 쓰는 우회 둘 — <b>실측으로 떨어뜨렸다</b></dt>
<dd><b>함수 안 지연 import</b> — 부팅은 되지만 <code>import-linter</code> 가 <b>그대로 위반으로 잡는다</b>(파일을 읽어 판정하지 실행해 보고 판정하지 않는다). <b><code>import a.b.c</code> 모듈 형태</b> — 되지만 <b>고리에 낀 파일 «전부»가 지켜야</b> 하고, 모듈 레벨에서 속성을 만지는 순간(기본 인자·상수·베이스 클래스·데코레이터) 무너진다. <b>둘 다 고리를 «없애는» 게 아니라 증상을 미룬다.</b></dd>
</dl>

## D34 · 통합 이벤트 칸은 열지 않는다 — 없는 것에 자리를 만들지 않는다 <b>(08-08 · D40 이 뒤집었다)</b>

**확정 · 08-06** · 자리 — ① 칸 &nbsp;·&nbsp; <b>D13</b> 의 «정직한 공백» &nbsp;·&nbsp; <b>새 칸 0</b>

<dl class="kv">
<dt class="ans-dt"><b>★ 2026-08-08 — 이 결정은 뒤집혔다</b></dt>
<dd class="ans-dd filled"><b>D40</b> 이 <b>칸을 «연다»</b>로 바꿨다. 아래 결론(«칸을 열지 않는다»)의 마지막 버팀목이 <b>「계약이 앉을 자리가 없다」</b>였는데, 그건 <b>자리를 만들면 되는 문제</b>였다 — 배치 논증이지 원리가 아니었다.<br><b>남는 것</b> — 여기 적힌 <b>현행 구현 진단</b>(방향이 둘 · 가변 전역 · <code>ready()</code> 가 안 돌면 조용히 사라진다)은 <b>그대로 참이고</b>, D40 의 배치가 그 셋을 그대로 고친다. <b>바뀐 것은 「그래서 포트 하나로 접는다」뿐</b>이다 — 이제 <b>전파마다</b> 커맨드인지 사실인지를 묻는다.</dd>
<dt class="ans-dt">물음 — <b>트리가 이미 «없어야 한다»고 찍고 있던 코드가 남아 있었다</b></dt>
<dd class="ans-dd filled">트리 항목이 다 닫힌 뒤 절 단위로 재보니 <b>답을 안 채운 절이 정확히 하나</b> 남아 있었다. <code>accounts</code> → <code>pairing</code> 이벤트 채널이고, 조각은 다섯이다.
<div class="pre-wrap"><pre><code>ChildEvicted 클래스                          자리가 바뀐다 — event/ 가 아니라 port/ 의 payload
dispatch_child_evicted()                     없어야 한다
register_child_evicted_handler() + _handlers 없어야 한다
published_service/lifecycle_subscription_service/  (7파일)   없어야 한다
django_pairing/apps.py 의 ready() 구독 + 핸들러              없어야 한다</code></pre></div>
<b>08-07 · 2차 리뷰 S2 — 물음을 거꾸로 물었었다.</b> 옛 문장은 <em>「조각 다섯 중 넷이 «갈 자리가 없다»」</em> 였는데, 이건 <b>«현행을 수정안에 매핑»하는 물음</b>이라 <b>규율 ① 위반</b>이다<span class="dim">(네 번째다 — 앞의 셋은 실측으로 미룬 둘과 «지나가는 것»에 칸을 물은 하나)</span>. 정확히는 <b>트리 59행이 그 넷을 문면으로 금지하고 있었다</b> — 「<b>발행 장치(레지스트리·dispatch)는 여기 안 산다 — 밖으로 나갈 일이면 애초에 포트다</b>」. <b>자리가 없는 게 아니라 «없는 것이 맞는» 것</b>이다.<br>
<b>세 관점이 다 같은 말을 한다 — 현행 구현은 정당하지 않다.</b>
<div class="pre-wrap"><table class="mini">
<tr><th>관점</th><th>무엇이 틀렸나</th></tr>
<tr><td><b>DDD</b></td><td><b>도메인 계층이 «발행 메커니즘»을 소유한다</b> — 한 파일에 사실 객체·레지스트리·팬아웃 루프가 같이 산다. 도메인 모델은 «무엇»이지 «어떻게 전달하나»가 아니다. 게다가 <code>accounts</code> 안에서 <code>ChildEvicted</code> 를 <b>읽는 것이 0</b>이라 58행 판정으로 <b>애초에 이벤트가 아니라 «알림»</b>이다</td></tr>
<tr><td><b>클린</b></td><td><code>_handlers</code> 가 <b>모듈 레벨 가변 전역</b>이다 — 시스템 동작이 «부팅 때 누가 등록했나»에 달린다(원칙 07 · 명시적이고 예측 가능한 코드). 그리고 <code>evict_child_command</code>(응용)가 <code>django.db.transaction</code> 을 <b>직접</b> import 한다 — 전역 제약 ② 위반이고 <b>D31</b> 이 <code>uow.after_commit(…)</code> 로 정한 이유다</td></tr>
<tr><td><b>헥사고날</b></td><td><b>포트가 없다.</b> 「바깥에 이런 능력이 있어야 한다」 대신 <b>「아무나 등록해라」라는 열린 구멍</b>이다. <code>ready()</code> 가 안 돌면 <code>dispatch</code> 는 빈 리스트에서 no-op 이라 <b>알림이 조용히 사라진다</b> — 실패가 안 보인다</td></tr></table></div>
<b>현행 도크스트링이 스스로 실토한다</b> — <em>「upstream 은 downstream 을 모른 채로 유지된다(올바른 의존성 방향)」</em> 를 지키려고 <b>가변 전역 레지스트리</b>를 들였다. <b>목적은 옳고 수단이 더 나쁘다.</b><br>
<b>그래서 방향이 둘</b>이다 — 등록은 <code>pairing</code> 의 <b>가장 바깥 링</b>(<code>AppConfig.ready()</code>)이 <code>accounts</code> 의 <b>도메인 레지스트리</b>를 건드리고, 발생은 <code>accounts → pairing</code> 이다. <b>트리의 모든 칸은 방향이 하나</b>다.</dd>

<dt>수정안으로 처음부터 지었으면 <b>이 코드는 생기지 않는다</b></dt>
<dd>요구는 하나다 — <em>「아이가 내보내지면 <code>pairing</code> 이 그 기기를 revoke 하고 살아있는 요청을 종료한다」</em>. 트리대로 지으면 이렇게 간다.
<div class="pre-wrap"><pre><code>① child.evict() 가 사실을 만들려는 순간 58행 규칙에 걸린다
     「이 BC 안에서 읽는 게 없으면 이벤트가 아니라 «알림»이다 → port/ 로」
   → ChildEvicted 를 event/ 에 만들지 «않는다»
② application_layer/port/child_eviction_notification/     계약 하나
③ uow.after_commit(lambda: notification.notify(child_id))  D31
④ driven_layer/adapter/anticorruption_layer/pairing/      번역
⑤ pairing/driving_layer/open_host_service/…                관문</code></pre></div>
<b>레지스트리도 dispatch 도 구독 서비스도 <code>ready()</code> 훅도 안 생긴다</b> — «만들 자리가 없어서»가 아니라 <b>«만들 이유가 없어서»</b>다. 포트 하나면 끝난다.<br>
<b>이게 이 카드의 진짜 결론이다</b> — 트리가 결손을 드러낸 게 아니라 <b>코드의 결함을 드러냈다</b>.</dd>

<dt class="ans-dt">결정 — 칸을 열지 않는다. <b>넷은 없어지고, 남는 하나는 자리가 바뀐다</b></dt>
<dd class="ans-dd filled"><div class="pre-wrap"><pre><code>accounts/application_layer/port/child_eviction_notification.py       이미 있는 칸
accounts/…/evict_child/evict_child_use_case.py
    with uow: …;  uow.after_commit(lambda: notification.notify(child_id))
accounts/driven_layer/adapter/anticorruption_layer/pairing/          이미 있는 칸
    child_eviction_notification.py  →  pairing OHS 호출
pairing/driving_layer/open_host_service/child_lifecycle_service/     이미 있는 칸
    cleanup_evicted_child(request)  →  CleanupEvictedChildCommand (이미 있다)</code></pre></div>
<b>«방향이 둘»이던 것이 없어진다</b> — 등록도 콜백도 사라지고 <code>accounts → pairing</code> 한 방향만 남는다. <code>after_commit</code> 은 <b>D31</b> 이 이미 정해놨다.</dd>

<dt>근거 ① — <b>트리 규칙이 이미 판정하고 있었다</b></dt>
<dd><b>D13</b> 의 <code>&lt;event&gt;.py</code> 규칙이 <b>«같은 BC 안에서만 읽는다»</b> 인데, 실측하면 <b><code>accounts</code> 안에서 <code>ChildEvicted</code> 를 읽는 것이 하나도 없다</b> — 애그리거트가 만들고, 유스케이스가 <code>on_commit</code> 에 예약하고, dispatch 가 밖으로 보내는 게 전부다. <b>경계를 넘는 것이 유일한 용도</b>다.<br>
<b>그러면 이건 도메인 이벤트가 아니라 «알림»이고, 알림 자리는 트리에 이미 있다.</b> 규칙을 새로 만든 게 아니라 <b>있던 규칙을 반대편으로 읽었다</b>.</dd>

<dt>규모 — <b>근거가 아니라 «고칠 코드의 크기»다</b> <span class="dim">08-07 · 2차 리뷰 S2 에 «근거 ②»에서 강등했다</span></dt>
<dd>운영 의존성 <b>14개</b>에 <b>celery·kombu·pika·kafka·redis 가 하나도 없다</b>. 「이벤트」라 부르지만 실물은 <b>같은 프로세스 안 함수 호출</b>이다. <code>event/</code> 폴더 <b>47개 중 46개가 파일 0개</b> · 이벤트 클래스 <b>1개</b> · 채널 <b>1개</b> · 구독자 <b>1개</b> — BC 16개 중 <b>한 쌍</b>이다.<br>
<span class="dim">옛 문장은 여기에 <em>「규율 ⑤ 가 그대로 걸린다」</em> 를 붙여 <b>실측 0 을 «칸을 안 여는 근거»로</b> 썼다. <b>R13 이 <b>D26</b> 에서 정확히 같은 논법을 뒤집었다</b> — 실측 0 을 근거로 미루는 것은 규율 ① 과 부딪힌다. 여기도 같아서 강등한다. <b>결론은 근거 ①·③ 과 전역 제약 ③ 이 지탱하므로 안 바뀐다</b> — 이 수치가 말하는 것은 <b>고칠 코드의 크기</b>뿐이다.</span></dd>

<dt>근거 ③ — <b>«upstream 은 downstream 을 모른다»는 이미 절대 원칙이 아니다</b></dt>
<dd>현행 주석이 <em>「accounts 는 consumer 를 절대 import 하지 않으므로 upstream 은 downstream 을 모른 채로 유지된다(올바른 의존성 방향)」</em>라고 지키던 것인데, <b><code>accounts</code> 는 지금도 <code>delivery</code> 를 안다</b>(<code>accounts/infra_layer/acl/delivery_phone_verification_sms_adapter.py</code>). 받는 쪽 <code>pairing</code> 도 OHS 를 이미 갖고 있다.<br>
<b>08-07 · F3 — 이 자리에 「BC 사이 양방향은 순환이 아니다」라고 써 있었다. 틀렸다.</b>
맞는 부분은 <em>「<code>accounts</code> 가 <code>delivery</code> 를 아는 것 자체는 정상이다」</em> 까지다 — <b>한 방향</b>은 관문을 지나는 한 얼마든지 있어도 된다.
틀린 부분은 «양방향»이다: <code>A</code> 와 <code>B</code> 가 <b>서로의 <code>anticorruption_layer/</code> 에 들어 있으면</b> 각자의 관문이 각자의 <code>composition_root</code> 를 부르고 그게 상대 관문을 불러 <b>파이썬이 import 하다 죽는다</b>.
<b>D35</b> 가 이걸 규칙으로 닫았다.</dd>

<dt>치르는 값 — 정직하게</dt>
<dd><b><code>accounts</code> 가 <code>pairing</code> 을 알게 된다.</b> <code>anticorruption_layer/pairing/</code> 이 생기고, <b>D17</b> 의 <em>«폴더 목록이 곧 이 BC 가 누구에게 기대나»</em> 에 한 줄이 는다.<br>
<b>구독자가 여럿이 되면 — 전역 제약 ③ 이 이미 답했다.</b> <b>BC 경계는 관문으로만 넘는다</b>에 예외가 없으니, 듣는 BC 가 셋이면 <b>ACL 폴더가 셋</b>이 되고 각각이 상대의 관문을 부른다. <b>전부 이미 있는 칸이고 트리는 안 바뀐다.</b> 그 목록이 곧 <b>D17</b> 이 말한 <em>«이 BC 가 누구에게 기대나»</em> 의 기록이다.<br>
<b>「누가 듣는지 «모르는 채로» 발행한다」는 곧 «관문 없이 넘는다»</b>라 전역 제약 ③ 이 <b>정의상 금지</b>한다. 트리에 그 자리가 없는 것은 <b>결손이 아니라 결정</b>이다.<br>
<b>브로커가 들어와도 같다</b> — 발행은 <code>port/&lt;capability&gt;/</code> + <code>driven_layer/adapter/external_system/&lt;broker&gt;/</code>, 수신은 각 BC 의 <code>driving_layer/</code> 입구가 <b>얇은 껍데기</b>로 자기 관문을 부른다(<b>D26</b> — 입구의 축은 «주기냐»가 아니라 «누가 부르나»다).<br>
<span class="dim"><b>08-07 · 2차 리뷰 S2</b> — 옛 문장은 <em>「구독자가 여럿이 되면 … 그때 발신·수신 칸을 «짝으로» 연다」</em> 였다. 두 가지가 틀렸다 — ⑴ R13 이 세운 자에 걸린다(「나중에 그때 연다」로 끝나는 문장은 <b>그 자체가 결함</b>) ⑵ 더 나쁜 것은, 그 문장이 <b>지금 코드의 «레지스트리+구독» 모양을 미래로 연장</b>한 것이라는 점이다. 위에서 본 대로 그 모양 자체가 세 관점에서 정당하지 않으니, <b>연장할 것이 아니라 없앨 것</b>이었다.</span></dd>

<dt class="ans-dt">딸려 나온 것 — <b>빈 폴더 154개</b> <span class="dim">08-09 · T51 에 결론이 뒤집혔다 — 아래</span></dt>
<dd class="ans-dd filled"><code>event/</code> 를 세다 나왔다. 원인은 트리가 아니라 <b>플러그인 조문</b>이다 — <em>「<code>domain_service</code>/<code>event</code>/<code>specification</code> 는 <b>폴더를 항상 두되</b> 트리거 미충족 시 비어 있을 수 있다(§0)」</em>.
<div class="pre-wrap"><pre><code>event/          47폴더  파일0 46      trees 에 있음
specification/  47폴더  파일0 46      D13 이 이미 뺐음
port/           51폴더  파일0 28      D32 가 이미 없앴음
domain_service/ 48폴더  파일0 26      08-07 에 칸이 없어져 48 이 통째로 사라진다
repository/     66폴더  파일0  8      트리에 있음</code></pre></div>
<b><b>D7</b> 근거② 가 예측이 아니라 이미 실현돼 있었다.</b> 트리를 고칠 일이 아니라는 것도 맞다 — <code>repository/</code> 도 8개가 비어 있고 리포지토리를 뺄 수는 없다.
<br><b>★ 08-09 · T51 — 그런데 처방이 반대였다.</b> 옛 문장은 <em>「§0 「항상 두되」를 <b>「채워질 때 만든다」</b>로 바꾸는 것이 답이고, 이건 플러그인 몫」</em> 이었다.
<b>플러그인이 옳고 이 문장이 틀렸다</b> — 골격은 <b>비어도 실현된다</b>. 자세한 것은 <b>D54</b>.
<b>이 표가 말하는 것은 «위반 154건»이 아니라 «골격이 실현돼 있다»</b>이고, 여기서 진짜로 쓸 것은 <b><code>domain_service/</code> 48 이 칸과 함께 사라진다</b>는 한 줄뿐이다.</dd>
</dl>

## D55 · 경계 자료의 낱말 — 다섯이 서로 «다른 축»이었다

**확정 · 08-09 · T53** · 자리 — <code>bc_error_schema</code> ↔ <code>framework_error_schema</code> &nbsp;·&nbsp; <code>webhook/&lt;provider&gt;/schema/</code> &nbsp;·&nbsp; <b>신설 2행 · 개명 7</b> &nbsp;·&nbsp; <code>&lt;area&gt;/</code> &nbsp;·&nbsp; <code>&lt;use_case&gt;_command|_query|_result.py</code> &nbsp;·&nbsp; <code>&lt;data&gt;_out|_in.py</code>

<dl class="kv">
<dt class="ans-dt">물음 — <b>「쌍을 이루는 게 여럿인데 낱말이 제각각이다. 계약에 의한 설계에서 힌트를 찾아 봐」</b></dt>
<dd class="ans-dd filled">경계를 넘는 자료가 <b>다섯 자리</b>에 있는데 낱말이 넷이었다.
<b>세어 보니 문제는 「낱말이 여럿」이 아니라 「낱말들이 서로 다른 «종류»」였다.</b>
<div class="pre-wrap"><table class="mini">
<tr><th>낱말</th><th>무엇을 말하는 낱말인가</th><th>계보</th></tr>
<tr><td><code>schema</code></td><td><b>기술 실물</b> — pydantic <code>Schema</code> 클래스 그 자체</td><td>django-ninja</td></tr>
<tr><td><code>dto</code></td><td><b>패턴 이름</b> — 「이건 DTO 패턴이다」</td><td>Fowler PoEAA</td></tr>
<tr><td><code>payload</code></td><td><b>자료의 «자리»</b> — 메시지 본문에 실린 것</td><td>통신 어휘</td></tr>
<tr><td><code>request</code>/<code>response</code></td><td><b>계약 항목</b> — 부르는 쪽이 내미나, 불리는 쪽이 돌려주나</td><td>Meyer · Martin</td></tr></table></div>
한 축이 아니라 네 축이라 <b>「어느 게 맞나」를 물으면 답이 안 나온다</b>. 물어야 할 것은 <b>「이 자리에서 이름이 무엇을 말해야 하나」</b>다.</dd>

<dt class="ans-dt">조사 — <b>계약에 의한 설계는 «방향»이 아니라 «계약 자신»을 기준점으로 쓴다</b></dt>
<dd class="ans-dd filled"><b>Meyer</b> — <em>“the client (<b>the caller</b>) and the supplier (<b>the called routine</b>)”</em> ·
<em>“The precondition expresses requirements that <b>any call must satisfy</b>…; the postcondition expresses properties that are <b>ensured in return by the execution of the call</b>.”</em>
계약 표의 축은 <b>Party(Client/Supplier) × Obligations/Benefits</b> 이고 <b>어디에도 «어느 쪽으로 흐르나»가 없다</b>.
<br><b>그리고 Meyer 에 <code>request</code> 라는 낱말은 0회</b>다 — DbC 어휘는 <code>argument</code>·<code>Result</code>·<code>require</code>/<code>ensure</code> 뿐이라,
<b>이 조사는 <code>request</code>/<code>response</code> 를 직접 지지하지 않는다</b>. 지지하는 것은 «축»이지 «낱말»이 아니다.
<br><b>Ada</b>(RM 6.2) — <em>“copy the value of the actual parameter <b>into the associated formal parameter</b>, if the mode is <code>in</code>… copy the value of the formal parameter <b>back into the actual parameter</b>, if the mode is <code>out</code>”</em>.
<b><code>in</code>/<code>out</code> 낱말의 정통 계보도 기준점이 «불리는 쪽»</b>이다.</dd>

<dt class="ans-dt">결정 ① — <b><code>schema_in</code>/<code>schema_out</code> 은 그대로 둔다</b></dt>
<dd class="ans-dd filled">다섯 중 <b><code>schema</code> 만 낱말이 «실물»과 같다</b> — 진짜 pydantic 클래스이고,
<b>유일하게 검증하고</b>(허용 <code>sort</code>·<code>filter</code> key · 페이지 상한), <b>유일하게 JSON 으로 직렬화된다</b>.
나머지 넷은 전부 순수 파이썬 타입이라 그 셋 중 어느 것도 참이 아니다.
<br><b><code>_in</code>/<code>_out</code> 의 기준점 문제도 이 자리에서는 안 생긴다</b> — HTTP 요청이 컨트롤러 «안으로», 응답이 «밖으로» 가서
<b>방향 축과 계약 축이 «일치»</b>한다. 갈리는 자리는 따로 있다.</dd>

<dt class="ans-dt">결정 ② — <b><code>webhook/&lt;provider&gt;/</code> 에도 <code>schema/</code> 겹을 둔다</b> · 트리가 <b>자기 모순을 적고</b> 있었다</dt>
<dd class="ans-dd filled"><div class="pre-wrap"><table class="mini">
<tr><th>이미 트리에 있던 문장</th><th>그런데</th></tr>
<tr><td><code>&lt;provider&gt;_controller.py</code> — <em>「업무가 실패해도 <b>ack 를 돌려준다</b>」</em></td><td><b>그 ack 의 모양을 둘 자리가 없었다</b></td></tr>
<tr><td><code>schema_in.py</code>(webhook) — <em>「<code>&lt;area&gt;/schema/</code> 쪽과 <b>같은 이름</b>을 쓴다. <b>종류가 같아서</b>다」</em></td><td>이름이 같다고 적어 놓고 <b>겹만 안 만들었다</b></td></tr>
<tr><td><b>D54</b> 제1원칙</td><td>같은 종류의 자리 둘이 <b>다른 골격</b>을 갖고 있었다</td></tr></table></div>
<b>「웹훅은 200 만 주면 된다」가 거짓인 것도 확인된다</b> — <b>돌려준 값을 되돌려 주지 않으면 등록 자체가 안 끝나는</b> 상대가 있고,
돌려준 본문이 <b>사람이 보는 화면</b>으로 그대로 쓰이는 경우도 있다. 본문이 없는 상대는 <b>빈 파일</b>이다(D54).
<span class="dim">T43·T44·T45·T46 과 <b>같은 모양</b> — 자는 트리에 이미 있었고 이 자리에만 안 걸려 있었다. 이번이 <b>다섯 번째</b>다.</span></dd>

<dt class="ans-dt">결정 ③ — <b><code>error_out.py</code> → <code>error_schema.py</code></b> · 클래스도 <code>&lt;Bc&gt;ErrorSchema</code></dt>
<dd class="ans-dd filled"><b><code>_out</code> 이 여기서 거짓말을 한다</b> — 트리 전체에서 <code>_out</code> 은 <b>«쌍의 한쪽»</b>인데
<b>이 파일만 짝이 없어 접미사가 아무것도 안 말했다</b>.
<br><b>플러그인이 이미 같은 쪽에 서 있었다</b> — 현행 경로가 <code>presentation_layer/<b>schema</b>/error_schema.py</code> 라
<b>이 파일을 이미 «스키마»로 분류</b>하고 있었다. 수정본에서 <code>&lt;area&gt;/schema/</code> 가 생기면서 <b>BC 당 하나인 이 파일이 밖으로 밀려났을 뿐</b>이다.
<br><b>반론 하나를 검토했다</b> — 이 파일에는 <code>&lt;Bc&gt;ErrorCode(StrEnum)</code> 도 사는데 <b>enum 은 스키마가 아니다</b>.
그런데 그 코드는 <b>응답 스키마의 <code>code</code> 필드 «타입»</b>이라(플러그인 축자 — <em>「식별자 field 하나를 해당 BC <code>ErrorCode</code> 로 좁힌 base Schema」</em>)
<b>스키마에 종속돼 있다</b>. 묶여도 맞다.
<br><b>규칙 하나가 딸려 나왔다</b> — <b><code>schema/</code> 폴더 «안»이면 접두</b>(<code>schema_in</code>), <b>«밖»이면 접미</b>(<code>error_schema</code>).
기존에 적혀 있던 <em>「<span class='no'>schema_error_out.py</span> 로 짓지 않는다 — <code>schema/</code> 는 «옆»이지 부모가 아니다」</em> 는 <b>접두 금지</b>였고, 이 접미와 충돌하지 않는다.</dd>

<dt class="ans-dt">결정 ④ — <b><code>&lt;area&gt;/</code></b> · 겹은 «둘» 그대로다</dt>
<dd class="ans-dd filled"><b>물음은 「<code>feature</code> 라고 하면 아래에 하나만 올 것처럼 읽힌다」</b>였고, <b>지적은 맞는데 구조는 이미 그렇지 않았다</b> —
트리가 <em>「유스케이스 폴더«들이» 여기 들어온다」</em>·<em>「업무 묶음 하나 — 컨트롤러 «여럿»이 한 업무로 묶여 사는 자리」</em>라 적고 있었다. <b>고칠 것은 낱말 하나였다.</b>
<div class="pre-wrap"><table class="mini">
<tr><th>후보</th><th>출처</th><th>판정</th></tr>
<tr><td><b><code>area</code></b></td><td>ASP.NET Core — <em>“Areas are … used to <b>organize related functionality into a group</b> as a separate namespace for <b>routing</b> and <b>folder structure</b>”</em> · 예시가 <em>checkout · billing · search</em></td><td><b>채택</b> — <b>라우팅과 폴더를 «함께» 가르는 개념</b>이라 <code>api/&lt;area&gt;/</code> ↔ <code>application_layer/&lt;area&gt;/</code> 의 1:1 과 정확히 같은 모양이고, 충돌이 0이다</td></tr>
<tr><td><code>module</code></td><td>Evans <em>MODULES (AKA PACKAGES)</em> · Jacobson package</td><td><b>기각</b> — 파이썬에서 <code>module</code> 은 <b>파일</b>이고 트리에 <code>&lt;module&gt;.py</code> 가 셋이다. 게다가 Evans MODULES 는 <b>도메인 «모델» 안</b>을 나누는 패턴이라 자리도 다르다</td></tr>
<tr><td><code>group</code></td><td><b>관례 0</b></td><td><b>기각</b> — 그 개념에 실제로 붙은 이름이 <code>Area</code>·<code>Module</code>·<code>Feature</code> 셋이다</td></tr></table></div>
<b>부수 효과 하나</b> — 트리에 <code>feature</code> 가 <b>두 자리</b>에 있었다(업무 범주 · <code>admin/&lt;entity&gt;/feature/</code> 의 «운영 기능»). <b>개명으로 그 중복이 사라졌다.</b></dd>

<dt class="ans-dt">결정 ⑤ — <b><code>&lt;use_case&gt;_command.py</code> / <code>_query.py</code> / <code>_result.py</code></b> · <code>dto/</code> 겹은 없앤다</dt>
<dd class="ans-dd filled"><b><code>dto</code> 는 낱말이 틀렸다</b> — Fowler 축자로 <em>“carries data <b>between processes</b>”</em> 이고 로컬 사용은 <em>“<b>they are actually harmful</b>”</em>(LocalDTO)인데,
우리 것은 <b>같은 프로세스·같은 파이썬 타입</b>이다. <b>D43</b> 에서 이미 <b>「Fowler 계보가 아니라 Martin 계보」</b>라고 정해 놓고 <b>폴더 이름만 Fowler 낱말</b>을 쓰고 있었다.
<br><b>겹을 없앤 근거는 실물이다</b> — Uncle Bob 저장소(<code>cleancoders/CleanCodeCaseStudy</code>)는 <code>CodecastSummaries<b>ResponseModel</b>.java</code> 를 <b>유스케이스 폴더에 평평하게</b> 두고 <code>dto/</code> 같은 겹을 안 만든다. <b><code>dto</code> 라는 낱말은 저장소 전체에 0건</b>이다.
<div class="pre-wrap"><table class="mini">
<tr><th></th><th>내가 반대했던 근거</th><th>사용자 재정의 뒤</th></tr>
<tr><td><b>CQRS</b></td><td>Fowler — <em>“CQRS should only be used on <b>specific portions</b> of a system … <b>not the system as a whole</b>”</em> 인데 골격은 전체에 강제된다</td><td><b>무효</b> — <b>CQRS 를 채택하는 게 아니라 낱말만 빌려 «종류»를 드러내는 것</b>이면 읽기 모델도 별도 저장소도 안 따라온다</td></tr>
<tr><td><b>D39 「파일엔 종류」</b></td><td><code>command</code> 는 «의도» 축이라 함수 몫</td><td><b>오히려 정합</b> — <b>«유스케이스의 종류»</b>로 두면 파일이 종류를 지는 규칙 그대로다</td></tr>
<tr><td><b>CQS 정의</b></td><td>Fowler — <em>“Commands: Change the state of a system but <b>do not return a value</b>”</em></td><td><b>남는다</b> — 다만 <b>정의를 채택한 게 아니라 낱말을 빌린 것</b>이라 «오용»이 아니라 «차용»이다</td></tr></table></div>
<b>Vernon 은 오히려 이쪽을 든다</b> — <em>“a better approach may be to design <b>Command [Gamma et al.] objects</b> instead. <b>There is not necessarily a right or wrong way.</b>”</em>
<b>원전이 「정답이 없다」고 적으면 트리의 자로 정한다</b>: 이름만으로 «이 유스케이스가 상태를 바꾸나»가 보이고, <b><code>_command.py</code>·<code>_query.py</code> 중 정확히 하나</b>는 <b>기계가 잰다</b>.</dd>

<dt><b>세 겹으로 늘리자는 안</b> — 원전이 <b>「이미 셋 다 있다」</b>로 답했다</dt>
<dd><b>Cockburn 의 goal level 셋</b>이 우리 트리에 그대로 있다.
<div class="pre-wrap"><table class="mini">
<tr><th>Cockburn</th><th>축자</th><th>우리 자리</th></tr>
<tr><td><b>Summary</b></td><td><em>“<b>encompasses multiple user goals</b>”</em></td><td><code>&lt;area&gt;/</code></td></tr>
<tr><td><b>User goal</b></td><td>“one person, one place, one time” · 이름은 <b>Active Verb Phrase (Goal)</b></td><td><code>&lt;use_case&gt;/</code> — <b>「동사로 짓는다」가 이미 그 규칙</b></td></tr>
<tr><td><b>Subfunction</b></td><td><em>“Needed to support a user-goal UC; <b>not independently valuable</b>”</em></td><td><code>&lt;use_case&gt;/</code> <b>안의 조각</b> — 「수명이 이 폴더를 넘지 않는다」</td></tr></table></div>
<b>세 번째 레벨을 «폴더»로 올리지 않는 것이 원전과 맞다</b> — 독립적 가치가 없다고 정의된 것에 독립 경로를 줄 근거가 없다.</dd>

<dt><b>남은 위험 하나</b> — 플러그인이 <code>Result</code> 를 «다른 뜻»으로 쓴다</dt>
<dd>플러그인 축자 — <em>「<b>exception path</b> … / <b>failed Result</b>/<code>None</code>/<b>outcome path</b> 는 artificial <code>try</code>/<code>catch</code> 없이 …」</em>.
거기서 <code>Result</code> 는 <b>「실패를 «값»으로 돌려주는 방식」</b>(Rust·Kotlin 계보)이고 <b>exception path 의 «대안»</b>이다. 우리 트리는 <b>exception 노선</b>이다.
<b>막는 자리는 트리에 박았다</b> — <code>&lt;use_case&gt;_result.py</code> 행이 <em>「실패를 여기 담으면 위반 · 플러그인의 <code>failed Result</code> 는 <b>다른 낱말</b>」</em> 이라 적는다. <b>6번에서 플러그인 문면을 맞출 때 같이 정리한다.</b></dd>

<dt class="ans-dt">결정 ⑥ — 포트 자리표시자 <b><code>&lt;payload&gt;</code> → <code>&lt;data&gt;</code></b> · 헥사고날 어휘로 간다</dt>
<dd class="ans-dd filled"><b>사용자가 축을 잡았다</b> — <em>「여기는 헥사고날이니 이쪽 어휘를 쓰는 게 맞겠다」</em>. <b>그 자로 재니 남는 낱말이 하나뿐이었다.</b>
<div class="pre-wrap"><table class="mini">
<tr><th>Cockburn 낱말</th><th>회수</th><th>그가 가리키는 것</th><th>이 자리에</th></tr>
<tr><td><b><code>data</code></b></td><td><b>50</b></td><td><b>포트로 오가는 것</b> — <em>trigger-data</em> · <em>notification data</em> · <em>subscriber data</em></td><td><b>채택</b></td></tr>
<tr><td><code>protocol</code></td><td>7</td><td><b>포트의 API</b> = 계약 자체</td><td><b>기각</b> — 자료가 아니고 파이썬 <code>typing.Protocol</code> 과 정면 충돌</td></tr>
<tr><td><code>event</code></td><td>6</td><td>바깥에서 도착하는 것</td><td><b>기각</b> — <code>&lt;event&gt;</code>(도메인 이벤트)가 이미 있다</td></tr>
<tr><td><code>conversation</code></td><td>4</td><td><b>포트 자체</b> — <em>“A port identifies a purposeful conversation”</em></td><td><b>기각</b> — 자료가 아니다</td></tr>
<tr><td><code>message</code></td><td>1</td><td>어댑터가 만든 것</td><td><b>기각</b> — 브로커 자리와 겹친다</td></tr></table></div>
<b><code>payload</code> 는 헥사고날 계보의 낱말이 아니었다</b> — Cockburn 원논문·사이트 최신본 <b>둘 다 0회</b>. Martin 0 · Meyer 0 · Evans 0.
<b>그리고 유일하게 쓰는 Vernon 의 뜻이 우리와 정반대다</b> — <em>Domain Payload Object</em> 는 축자로
<em>“designed to contain references to <b>whole Aggregate instances</b>, not individual attributes”</em> 인데,
<b>이 자리의 네 행은 전부 「애그리거트가 오면 위반」을 박고 있다</b>. <b><code>dto</code> 가 Fowler 축자로 틀렸던 것과 같은 모양</b>이다.</dd>

<dt>딸려 나온 것 — <b>방향 낱말 <code>_out</code>/<code>_in</code> 이 «이미» Cockburn 축이었다</b></dt>
<dd><em>“the primary purpose of this pattern is to focus on the <b>inside-outside asymmetry</b>”</em> —
<b>안팎 비대칭이 이 패턴의 «주된 목적»이라고 그가 직접 적는다.</b> 기준점도 «안쪽(애플리케이션)»이라 우리 <code>_in</code>(우리에게 들어옴)과 일치한다.
<br><b>그래서 <b>D46</b> 이 보류했던 「기준점 뒤집기」를 확정 기각한다</b> — 뒤집으면 오히려 이 축에서 벗어난다.
<br><b>실제 파일 이름은 이미 Cockburn 꼴이다</b> — <code>cancellation_notice_out.py</code> 는 <em>&lt;purpose&gt; + 방향</em>이고,
그가 <em>trigger-<b>data</b></em> 로 목적을 앞에 붙인 것과 겹이 같다. <b>자리표시자는 「자료 이름이 온다」만 말하면 된다.</b>
<span class="dim">「<code>data</code> 는 너무 넓다」는 반론은 선다. 다만 <b>좁힐 낱말을 원전이 안 만들었다</b> — Cockburn 은 목적을 그때그때 앞에 붙였고,
헥사고날 표준 예제(Hombergs <em>buckpal</em>)의 <code>port/out/</code> 에는 <b>자료 파일이 아예 0개</b>다. <code>&lt;aggregate&gt;</code>·<code>&lt;event&gt;</code> 처럼 좁은 종류 이름을 가질 수 있는 자리가 아니다.</span></dd>

<dt><b>고친 결함 하나</b> — 왼쪽 트리의 이름 규칙이 <b>D46</b> 을 안 받고 있었다</dt>
<dd>T46 이 이 파일을 <code>_out</code>/<code>_in</code> 둘로 쪼갰는데 <b>왼쪽 트리 이름 규칙은 쪼개기 전 것 하나가 남아</b>
<b>지금 트리에 없는 접미사 <code>_payload</code></b> 를 표시하고 있었다(<code>_in</code> 쪽은 규칙이 아예 없었다).
<div class="pre-wrap"><pre><code>49 &lt;data&gt;_out.py   명사 + _payload   →  명사 + _out
50 &lt;data&gt;_in.py    (없음)           →  명사 + _in      (신설)
54 &lt;data&gt;_out.py   명사 + _payload   →  명사 + _out
55 &lt;data&gt;_in.py    (없음)           →  명사 + _in      (신설)</code></pre></div>
<b>오른쪽 패널의 «이름» 줄은 T46 때 이미 갱신됐었다</b> — 어긋난 것은 왼쪽뿐이다. <b>개명과 무관하게 틀린 것</b>이라 같이 고쳤다.</dd>

<dt class="ans-dt">결정 ⑦ — <b>오류 스키마 둘이 이름으로 갈린다</b> <span class="dim">08-09 · T54</span></dt>
<dd class="ans-dd filled"><b>같은 종류의 파일이 두 자리에 있는데 한쪽만 개명돼 있었다.</b>
<div class="pre-wrap"><pre><code>BC 안   application/&lt;bounded_context&gt;/driving_layer/api/<b>bc_</b>error_schema.py
        이 BC 가 내는 오류 «코드 목록»          &lt;Bc&gt;ErrorCode · &lt;Bc&gt;ErrorSchema

BC 밖   framework/ninja/<b>framework_</b>error_schema.py
        모든 BC 가 쓰는 오류 응답 «봉투»        ErrorSchema
        framework/ninja/framework_validation_error_schema.py</code></pre></div>
<b>개명 근거는 BC 것과 «같은 사건»이다</b> — 현행은 <code>common/ninja/<b>response</b>/error_out.py</code> 라 <b>폴더가 짝 노릇</b>을 했는데,
<b>D24</b> 가 <code>response/</code> 겹을 걷어내며 <b><code>_out</code> 의 짝이 사라졌다</b>. BC 것도 <code>schema/</code> 밑에서 나오며 똑같이 잃었다.
<br><b>접두를 붙이는 까닭은 «함께 import 되기 때문»</b>이다 — 컨트롤러 하나가 <b>봉투와 코드 목록을 둘 다</b> 가져온다.
트리에 같은 이름이 두 자리인 것은 이미 있지만(<code>exception.py</code>·<code>schema_in.py</code>) <b>그것들은 함께 쓰이지 않는다</b>. <b>가르는 자는 「한 파일이 둘 다 import 하나」</b>다.
<div class="pre-wrap"><table class="mini">
<tr><th>공통 쪽 접두 후보</th><th>판정</th></tr>
<tr><td><b><code>framework_</code></b></td><td><b>채택</b> — 트리의 접두는 <b>«내가 속한 곳»</b>을 말하고(<code>&lt;area&gt;_controller</code>·<code>&lt;aggregate&gt;_repository</code>·<code>&lt;use_case&gt;_command</code>), 이 파일의 조상이 <code>framework/</code> 다</td></tr>
<tr><td><code>common_</code></td><td><b>기각</b> — <b>이 폴더가 <code>common/</code> 에서 개명한 그 낱말</b>이다. D24 축자: <em>「공통이냐」는 <b>성질이 아니라 정도</b>라 서랍이 된다</em>. 폴더에서 걷어낸 낱말을 파일 이름으로 되들일 수 없다</td></tr>
<tr><td><code>ninja_</code></td><td><b>기각</b> — 이 칸은 <b>기술 이름을 접두로 안 붙인다</b>(<code>authentication.py</code> 가 <span class='no'>ninja_authentication.py</span> 가 아니다). 폴더가 이미 말했다</td></tr>
<tr><td><code>platform_</code>·<code>foundation_</code></td><td><b>기각</b> — D24 가 폴더 이름 고를 때 이미 떨어뜨렸다(파이썬 stdlib 충돌 · 「내용이 토대가 아니다」)</td></tr></table></div>
<b>딸려 나온 정정 — 이 칸의 이름 규칙이 자기 예시와 안 맞았다.</b> 트리가 <em>「안에 오는 모듈은 «무엇을 하나»로 이름 붙는다」</em> 라 적는데
여기 사는 넷 중 <b><code>authentication.py</code> 하나만</b> 그렇고 나머지 셋(<code>error_out</code>·<code>validation_error_out</code>·<code>retryable_database_error</code>)은 <b>«무엇인가»</b>다.
규칙을 <b>「«하는 일» 또는 «무엇인가» · 기술 이름은 안 붙인다」</b>로 고쳤다.</dd>
</dl>

## D54 · 제1원칙 — 모든 BC 는 같은 골격을 «내용과 무관하게» 갖는다

**확정 · 08-09 · T51** · 자리 — ① 칸 &nbsp;·&nbsp; <b>다른 모든 것보다 앞선다</b> &nbsp;·&nbsp; 백스톱 1순위 &nbsp;·&nbsp; <b>유형 셋 · 조건부 0 · 예외 0</b> <span class='dim'>T52</span>

<dl class="kv">
<dt class="ans-dt">결정 — <b>이 트리는 «권고»가 아니라 «형태»다</b></dt>
<dd class="ans-dd filled"><b>어느 BC 를 열어도 같은 골격이 나온다.</b> 폴더에 내용이 있든 없든 상관없다 —
<b>비어 있으면 <code>__init__.py</code> 만 둔 빈 패키지로 존속</b>시킨다(git 은 빈 디렉터리를 추적하지 않으므로 이 파일이 골격을 버전관리에 남긴다).
<div class="pre-wrap"><table class="mini">
<tr><th></th><th>언제 생기나</th></tr>
<tr><td><b>고정 이름</b> — 폴더 <code>port/</code>·<code>event/</code>·<code>schema/</code>·<code>contract/</code> · 파일 <code>schema_in.py</code>·<code>exception.py</code>·<code>event_wiring.py</code> …</td><td><b>부모가 있으면 반드시.</b> 폴더는 비면 <code>__init__.py</code> 만, <b>파일도 비면 빈 파일로</b> 둔다</td></tr>
<tr><td><b>자리표시자 · «첫 등장»</b> — <code>&lt;aggregate&gt;/</code>·<code>&lt;area&gt;/</code>·<code>&lt;capability&gt;/</code>·<code>&lt;service&gt;/</code>·<code>&lt;event&gt;.py</code> …</td><td><b>그 기능이 실제로 필요할 때.</b> 없는데 만들면 그게 위반</td></tr><tr><td><b>자리표시자 · «재등장»</b> — <code>&lt;area&gt;_controller.py</code>·<code>&lt;capability&gt;_port.py</code>·<code>&lt;use_case&gt;_result.py</code>·<code>django_&lt;bounded_context&gt;/</code> … <span class="dim">조상이 이미 그 낱말을 열었다</span></td><td><b>고정 이름과 같다 — 무조건.</b> 값이 이미 정해졌으니 새로 정할 것이 없다<span class="dim"> 08-09 · T52 신설</span></td></tr></table></div>
<b>셋을 가르는 자는 이름 자체다</b> — <code>&lt;…&gt;</code> 가 붙었으면 «채워질 이름»이고, 고정 이름이면 «형태»다. 그리고 <b>같은 <code>&lt;…&gt;</code> 도 «처음 나올 때»만 자리표시자다</b> — 조상이 이미 연 낱말이 아래에서 다시 나오면 그건 «채워질 이름»이 아니라 <b>이미 채워진 값</b>이다<span class="dim"> 08-09 · T52</span>.
<b>「항상」이 아니라 「부모가 있으면」인 것이 요점</b>이다 — 이 한 마디로 트리 전체가 <b>재귀적으로 결정</b>된다.
<div class="pre-wrap"><pre><code>open_host_service/       고정 → BC 가 있으면 항상        ← 창구가 0개여도 «있다»
  &lt;service&gt;/             개념 → 노출할 창구가 있을 때
    contract/            고정 → &lt;service&gt;/ 가 있으면 «전부 함께»
      request/ response/ 고정 →        "                     ← 연산이 0-인자여도 폴더는 있다
      exception/         고정 →        "

api/                     고정 → 항상
  &lt;area&gt;/             개념 → area 가 있을 때
    schema/              고정 → &lt;area&gt;/ 가 있으면 항상
      schema_in.py       고정 →        "        «둘 다»
      schema_out.py      고정 →        "</code></pre></div>
<b>「무조건 있다」와 「생기기 전엔 없다」가 서로 다른 규칙이 아니다</b> — <b>「부모까지 왔으면 반드시」</b> 하나로 둘 다 나온다.
<b>골격은 YAGNI 의 대상이 아니다</b> — 「이 BC 엔 표현 관심사가 없으니 <code>api/</code> 를 빼자」는 <b>축소가 아니라 위반</b>이다.
<span class="dim">★ 이 원칙은 트리 한 자리에 <b>이미 서 있었다</b> — <code>domain_layer/&lt;aggregate&gt;/event/</code> 행이 <em>「<b>이 폴더가 비어 있는 것은 결함이 아니다</b> — 자기 안에서 소비할 사실이 없는 애그리거트가 대부분이다」</em> 라고 적는다. 한 칸에만 있고 전체로 안 올라가 있었다.</span></dd>

<dt class="ans-dt"><b>이것보다 우선하는 것은 없다</b> — 그래서 백스톱이 1순위로 돈다</dt>
<dd class="ans-dd filled"><b>파일트리를 지키지 않는 구현과 설계는 «반환»이다.</b> 다른 검사를 통과했는지는 보지 않는다 —
<b>골격 검사가 먼저 돌고, 거기서 걸리면 나머지를 돌릴 것도 없다</b>.
<div class="pre-wrap"><pre><code>1순위  골격 검사   ① 고정 이름       — 부모가 있는데 없으면 위반 (폴더·파일 둘 다)
                    ② &lt;…&gt; «첫 등장»  — 그 기능이 없는데 있으면 위반
                    ③ &lt;…&gt; «재등장»  — 값이 정해졌다 → ① 과 «같다»
                    ④ 폐쇄            — ①②③ 어디에도 «매칭 안 되는 경로»가 있으면 위반
       ↓ 통과해야만
2순위  나머지 규칙    import 방향 · 이름 · 판정 자리 · 예외 계약 …</code></pre></div>
<b>④ 가 이 원칙의 «닫는» 쪽이다</b> — ①②③ 만으로는 <code>application_layer/service/</code>·<code>utils/</code>·<code>helpers/</code>·<code>common/</code> 을 만들어도 <b>전부 통과한다</b>.
<b>파일트리는 «허용 목록»이다 — 여기 없는 모양은 존재할 수 없다.</b>
<span class="dim">4차 리뷰 SC-C 가 <em>「개발자가 <code>framework/common/</code> 을 만들게 된다 — 이름 규칙이 금지한 그 자리」</em> 로 지적한 것이 정확히 ④ 의 부재였다.</span></dd>

<dt class="ans-dt">조건부 노드를 <b>없앴다</b> — 남는 유형은 셋뿐이다 <span class="dim">08-09 · T52</span></dt>
<dd class="ans-dd filled"><b>「~일 때만」이라 적힌 노드는 반드시 표류한다</b> — 사람이 판단하기 때문이다.
트리에 그런 노드가 <b>딱 하나</b> 있었고(<code>bc_error_schema.py</code> 「HTTP 오류를 공개하는 BC 만」), <b>지웠다</b>.
<div class="pre-wrap"><pre><code>✗ 「HTTP 오류를 공개하는 BC 만」   ← 사람이 판단한다 · 「공개하나」는 «내용»이지 «골격»이 아니다
✔ 부모 api/ 가 항상이니 이 파일도 항상   ← 아직 안 여는 BC 에는 «빈 파일»</code></pre></div>
<b>사용자 결정</b> — <em>「아직 있다와 없다의 차이는 <code>&lt;&gt;</code> 에서만 발생하는 거고,
없다면 «아직 해당 BC 에는 그 기능이 없다» 로 해석해야 한다」</em>.
<b>그래서 「없다」와 「아직 없다」를 구별하려는 조건은 애초에 필요가 없다</b> — 빈 칸이 그 답을 이미 하고 있다.</dd>

<dt class="ans-dt">전수로 훑어 어긋난 자리 <b>넷</b> — 전부 «표기»가 틀린 것이었다</dt>
<dd class="ans-dd filled"><b>규칙이 아니라 트리가 틀렸다.</b> 129행을 조상 대조로 전수 분류하니 어긋난 것이 넷이다.
<div class="pre-wrap"><table class="mini">
<tr><th>어긋난 자리</th><th>규칙이 내리는 답</th><th>고친 것</th></tr>
<tr><td><code>anticorruption_layer/&lt;bounded_context&gt;/</code></td>
<td>조상이 이미 연 낱말 → <b>재등장 → 값은 «나 자신»</b><br><code>payment/anticorruption_layer/payment/</code></td>
<td><b><code>&lt;other_bounded_context&gt;/</code></b> — 여기 오는 것은 «남»이라 <b>새 낱말이어야 한다</b></td></tr>
<tr><td><code>migrations/0001_initial.py</code></td>
<td>고정 이름 → <b>「비면 빈 파일로라도」</b><br>그런데 <b>사람이 만들 수 없다</b>(<code>makemigrations</code> 전용)</td>
<td><b><code>&lt;migration&gt;.py</code></b> — 애초에 고정 이름이 아니었다(<code>0002_…</code> 로 «는다»)</td></tr>
<tr><td><code>&lt;use_case&gt;_command.py</code> / <code>_query.py</code></td>
<td>둘 다 재등장 → <b>둘 다 무조건</b><br>그런데 트리는 <b>「둘 중 정확히 하나」</b></td>
<td><b>둘 다 온다.</b> 검사는 <b>«클래스가 정의된 것이 정확히 하나»</b>로 내려간다 — 「둘 중 하나」는 <b>«존재» 규칙이 아니라 «내용» 규칙</b>이었다</td></tr>
<tr><td><code>&lt;project&gt;/</code> · <code>settings/&lt;environment&gt;.py</code></td>
<td>첫 등장 → 「필요할 때」<br>그런데 <b>장고 프로젝트는 무조건 하나</b></td>
<td><b>대상 밖이다</b> — 이 원칙의 주어는 <b>«BC»</b>이고 <code>framework/</code>·<code>&lt;project&gt;/</code> 는 BC 가 아니다.
<span class="dim">여기서 <code>&lt;…&gt;</code> 는 「없을 수 있다」가 아니라 「이름을 우리가 안 정했다」를 뜻한다 — 범위를 안 넓히는 근거다</span></td></tr></table></div>
<b>규칙이 «못 잡지만» 다른 규칙이 잡는 셋</b> — <code>adapter/persistence/repository/&lt;aggregate&gt;_repository.py</code> ·
<code>…/domain_bypass_query/&lt;capability&gt;_query.py</code> · <code>adapter/unit_of_work/&lt;boundary&gt;_unit_of_work.py</code> 는
조상 경로에 그 낱말이 없어 «첫 등장»으로 읽히는데, <b><b>D37</b> 의 짝맞춤이 이미 1:1 을 강제</b>한다. <b>규칙을 늘리지 않는다.</b>
<span class="dim">스코프를 「조상」이 아니라 「BC 전체」로 넓히면 이 셋도 잡히지만 <code>&lt;capability&gt;</code> 가 깨진다 —
<code>port/</code>·<code>adapter/</code>·<code>external_system/&lt;system&gt;/</code>·<code>framework/</code> 의 그것은 <b>서로 다른 집합</b>이다.</span></dd>

<dt>고정 이름 «파일»도 예외가 아니다</dt>
<dd><b>사용자 결정</b> — <em>「이건 미리 만들어 놔야 해. 왜냐하면 <b>부모가 있기 때문</b>이야. 즉 부모 폴더가 생길 수 있는 상황이면 자식은 반드시 와야 해」</em>.
<div class="pre-wrap"><table class="mini">
<tr><th></th><th>구독이 0개 / celery 를 안 써도</th></tr>
<tr><td><code>composition_root/event_wiring.py</code></td><td><b>만든다.</b> 부모 <code>composition_root/</code> 가 있다</td></tr>
<tr><td><code>&lt;project&gt;/celery.py</code></td><td><b>만든다.</b> 부모 <code>&lt;project&gt;/</code> 가 있다</td></tr></table></div>
<b>폴더의 <code>__init__.py</code> 와 같은 취지다</b> — 형태가 같아야 «어느 BC 를 열어도 같다»가 참이 되고, <b>「없는 것」과 「아직 안 만든 것」을 구별할 필요가 사라진다</b>.</dd>
<b>이 순서가 값을 낸다</b> — 골격이 흔들리면 <b>다른 검사의 «경로 전제»가 통째로 무너진다</b>.
「<code>application_layer/port/**</code> 를 컨트롤러가 import 하면 위반」 같은 규칙은 <b>그 경로가 실제로 그 자리에 있다는 전제</b> 위에 서 있고,
폴더가 없으면 검사기는 <b>위반을 못 찾은 것</b>과 <b>대상이 없는 것</b>을 구별하지 못한다.
<span class="dim">이미 그 병을 한 번 다뤘다 — 경로 계약 명세의 <b>「채택 신호는 있는데 대상 0건이면 <code>exit 2</code>」</b>(fail-open 금지)가 같은 문제의 다른 면이다.</span></dd>

<dt>플러그인이 이미 이렇게 적고 있었다 — 뒤집힌 것은 «우리 쪽»이다</dt>
<dd><em>houserules §0-4</em> 가 축자로 답을 갖고 있었다.
<div class="pre-wrap"><pre><code>“종류 2차 폴더 전체를 «항상 폴더로 생성»한다. 내용이 없으면 빈 패키지(__init__.py만)로
  둔다 — 평면 파일(repository.py)로 접지 않는다. 빈 폴더의 __init__.py는 «유지한다»
  (regular package) — git은 빈 디렉터리를 추적하지 않으므로 이 파일이 골격을
  버전관리에 존속시키고 … PEP 420을 이유로 __init__.py를 지우지 않는다.
  ([선택] 마커는 “비어 있을 수 있음”이지 «생략 가능»이 아니다.)”

§0-2  “계층에 들어갈 내용물이 없어도 그 계층 폴더는 빈 패키지로라도 항상 생성한다 …
       §6.8 YAGNI는 계층·종류 골격에 적용하지 않는다.”</code></pre></div>
<b>그런데 <b>D34</b> 가 이걸 「§0 을 «채워질 때 만든다»로 바꾸자」로 뒤집어 놨고</b>,
그 문장이 <b>옛 적용 계획 4번(명세)의 «씨앗»에 그대로 실려</b> 있었다 — 그대로 뒀으면 <b>플러그인 §0 을 뒤엎는 규칙이 명세에 박힐 뻔했다</b>.
<b>원인은 실측이다</b> — 「빈 폴더 154개」를 <b>«문제»로 읽은 것</b>인데, 골격이 실현돼 있다는 <b>«증거»</b>였다.
<span class="dim">실측을 근거로 삼아 어긋난 다섯 번째다(D26 · D34 · D45 · T46 의 「아직 안 뒤집혔다」 · 여기).</span></dd>

<dt>딸려서 갈아 낀 근거 셋</dt>
<dd>「<b>빈 한 겹이 생긴다</b>」를 <b>나쁨의 근거로 쓴 자리</b>가 셋 있었고, 제1원칙 아래서는 <b>빈 것이 정상</b>이라 그대로는 못 쓴다. <b>결론은 셋 다 살아남고 근거만 갈렸다.</b>
<div class="pre-wrap"><table class="mini">
<tr><th>자리</th><th>새 근거</th></tr>
<tr><td><code>ninja/</code> 폴더를 안 만든다 (<b>D7</b>)</td><td><b>고를 값이 하나뿐이라 «축»이 아니다</b> — 빈 겹은 이유가 아니다</td></tr>
<tr><td><code>specification/</code> 를 안 만든다</td><td><b>모든 애그리거트가 갖는 구조 요소가 아니다</b> — 골격은 비어도 «영구히» 지므로 자격이 더 엄해진다</td></tr>
<tr><td>「빈 폴더 48개가 사라진다」를 <b>이득</b>으로 센 것</td><td><b>이득이 아니다.</b> 칸이 없어진 <b>결과</b>일 뿐이다</td></tr></table></div>
<b>★ 오히려 자격이 «세졌다»</b> — 비어도 영구히 존속하므로, 골격에 칸을 하나 올리는 값이 예전보다 비싸다.</dd>
</dl>

## D33 · 접미사는 «자리»가 정한다 — 파일엔 안 붙이고 클래스엔 붙인다

**확정 · 08-06 · 08-08 에 어휘 하나 교체** · 자리 — ② 이름 &nbsp;·&nbsp; 포트·어댑터 <b>클래스</b> 이름 &nbsp;·&nbsp; 닫는 문제 <b>P10</b>

<dl class="kv">
<dt class="ans-dt">검사 대상은 <b>«자리»가 정한다</b> <span class="dim">08-06 · R4</span></dt>
<dd class="ans-dd filled"><b>접미사 규칙을 파일 전체에 걸면 오탐이 난다.</b> 포트 파일 안에는 인터페이스만 사는 게 아니라
<em>주고받는 자료</em>와 <em>던지는 실패</em>도 같이 살기 때문이다 — <code>FcmPushPayload</code>·<code>VerifiedSocialIdentity</code>·<code>NotificationDispatchPlan</code> 에
<code>Port</code> 접미사를 요구하면 전부 위반으로 찍힌다.<br>
<b><b>D14</b> 가 포트를 폴더로 만들면서 이 문제가 «자리»로 풀렸다</b> —
<code>&lt;capability&gt;/&lt;capability&gt;.py</code> 안의 클래스만 접미사 대상이고,
같은 폴더의 <code>exception.py</code>·<code>&lt;payload&gt;.py</code> 는 <b>애초에 대상이 아니다</b>.
「ABC 를 가졌나」를 볼 필요도 없다 — <b>경로 한 줄로 갈린다.</b><br>
<span class="dim">이렇게 안 하면 <b>D25</b> 가 진단한 병(«규칙을 쓴 게 아니라 목록을 썼다»)이 <b>예외 목록으로 재발한다</b>.</span></dd>
<dt class="ans-dt">물음 — 클래스 이름 규칙이 <b>트리에 한 줄도 없었다</b></dt>
<dd class="ans-dd filled">수정안이 클래스 이름을 말하는 자리는 셋뿐이고 <b>셋 다 «접두사»</b>다 — §4(<em>기술은 이름의 한정자로</em>) · <code>&lt;area&gt;_controller.py</code>(<code>NinjaTurnController</code>) · <code>&lt;aggregate&gt;_repository.py</code>(<code>DjangoOrderRepository</code>). <b>접미사 규칙은 없었다.</b> 실물은 <b>69개</b>(<code>Port</code> 37 · <code>Adapter</code> 32).</dd>

<dt>정직한 단서 — <b>먼저 낸 추천이 반대였다</b></dt>
<dd>P10 판정에서 <b>「접미사를 없애야 한다」</b>고 썼다. 근거는 <em>「접두사가 이미 «누구»를 말하니 접미사가 하는 일이 없다」</em>(<code>AccountsFamilyMembershipAdapter</code> — 실측 32 중 31이 접두사를 달고 있다).<br>
<b>사용자가 「접미사는 다 붙이는 게 가독성이 좋겠다」고 했고, 재보니 그쪽이 맞았다.</b> 내 근거는 <b>«구별이 되나»만</b> 봤고 <b>«무엇과 구별되나»를 안 봤다</b>.</dd>

<dt class="ans-dt">실측이 뒤집었다 — 떼면 <b>7개가 도메인 개념과 부딪힌다</b></dt>
<dd class="ans-dd filled"><div class="pre-wrap"><table class="mini">
<tr><th>포트</th><th>떼면</th><th>부딪히는 것</th><th>같은 BC</th></tr>
<tr><td><code>ModelAssignmentPort</code></td><td><code>ModelAssignment</code></td><td>llm_meta <b>애그리거트 루트</b></td><td></td></tr>
<tr><td><code>UsageReservationPort</code></td><td><code>UsageReservation</code></td><td>usage_quota <b>애그리거트 루트</b></td><td></td></tr>
<tr><td><code>TurnSettlementPort</code></td><td><code>TurnSettlement</code></td><td>ai_chat 값 객체</td><td><b>✔</b></td></tr>
<tr><td><code>ChildTargetingProfilePort</code></td><td><code>ChildTargetingProfile</code></td><td>managed_copy 값 객체</td><td><b>✔</b></td></tr>
<tr><td><code>ChildConversationPort</code></td><td><code>ChildConversation</code></td><td>report 값 객체</td><td><b>✔</b></td></tr>
<tr><td><code>OtpCodeGenerator</code></td><td><code>OtpCode</code></td><td>accounts 값 객체</td><td><b>✔</b></td></tr>
<tr><td><code>ChildNicknamePort</code></td><td><code>ChildNickname</code></td><td>accounts 값 객체</td><td></td></tr></table></div>
<b>넷이 같은 BC 안</b>이다 — <b>D21</b> 이 <code>&lt;entity&gt;_model.py</code> 에 접미사를 필수로 만든 조건과 <b>정확히 같은 모양</b>이다.</dd>

<dt>충돌은 <b>우연이 아니라 구조적</b>이다</dt>
<dd>Evans 의 SERVICE 조건 ②가 <em>「인터페이스는 도메인 모델의 다른 요소들로 정의된다」</em>이다(<b>D12</b> 의 원전 대조). <b>포트가 도메인 어휘를 쓰는 건 규칙</b>이라, 접미사를 떼면 <b>반드시</b> 부딪힌다. 지금 7개인 건 <em>지금까지</em>다.</dd>

<dt class="ans-dt">결정 — 접미사는 «자리»가 정한다</dt>
<dd class="ans-dd filled"><div class="pre-wrap"><pre><code>application_layer/port/&lt;cap&gt;/&lt;cap&gt;_port.py                  →  &lt;Capability&gt;Port
port/domain_bypass_query/&lt;cap&gt;/&lt;cap&gt;_query.py               →  &lt;Capability&gt;DomainBypassQuery
adapter/persistence/domain_bypass_query/&lt;cap&gt;_query.py      →  Django&lt;Capability&gt;DomainBypassQuery
adapter/anticorruption_layer/&lt;bc&gt;/&lt;cap&gt;_adapter.py          →  &lt;Bc&gt;&lt;Capability&gt;Adapter
adapter/external_system/&lt;system&gt;/&lt;cap&gt;_adapter.py           →  &lt;System&gt;&lt;Capability&gt;Adapter
driven_layer/adapter/&lt;cap&gt;/&lt;cap&gt;_adapter.py                 →  &lt;기술&gt;&lt;Capability&gt;Adapter
framework/&lt;cap&gt;/&lt;cap&gt;_port.py                              →  &lt;Capability&gt;Port
framework/&lt;cap&gt;/&lt;technology&gt;_adapter.py                     →  &lt;기술&gt;&lt;Capability&gt;Adapter</code></pre></div>
<span class="dim">아래 둘은 08-07 에 더했다 — <b>«계약이면 <code>Port</code>, 구현이면 <code>Adapter</code>»가 자리를 옮겨도 그대로 돈다</b>. 새 규칙이 아니라 같은 규칙의 적용이다.</span>
<b>클래스 이름 = 접두사(누구·기술) + 파일 이름 CamelCase + 자리 접미사.</b> AST 한 줄로 검사된다.</dd>

<dt>파일엔 안 붙이는데 클래스엔 붙이는 이유
<span class="dim">← <b>08-08 · D41 이 이 절을 뒤집었다</b> — 파일도 클래스와 같은 낱말을 단다. 아래는 그때의 기록.</span></dt>
<dd><b>파일은 늘 폴더와 같이 읽히고 클래스는 혼자 돌아다닌다.</b>
<div class="pre-wrap"><pre><code>port/family_membership.py                      ← 「port/」 가 같이 보인다
def __init__(self, family_membership: ???)     ← 아무것도 같이 안 보인다</code></pre></div>
<b>D21</b> 의 «접미사는 겹칠 때만»은 <b>파일 규칙</b>이고, 이 결정과 어긋나지 않는다.</dd>

<dt class="ans-dt">어휘 가족이 둘인 이유 — <b>「이 낱말이 구현에도 참인가」</b></dt>
<dd class="ans-dd filled"><div class="pre-wrap"><table class="mini">
<tr><th>계약</th><th>선언</th><th>구현</th><th>무엇이 가르나</th></tr>
<tr><td><code>&lt;agg&gt;_repository.py</code></td><td><code>ProductRepository</code></td><td><code>DjangoProductRepository</code></td><td><b>접두사</b></td></tr>
<tr><td><code>&lt;boundary&gt;_unit_of_work.py</code></td><td><code>&lt;Boundary&gt;UnitOfWork</code></td><td><code>Django&lt;Boundary&gt;UnitOfWork</code></td><td><b>접두사</b></td></tr>
<tr><td><code>domain_bypass_query/&lt;cap&gt;.py</code></td><td><code>ChildLessonDigestDomainBypassQuery</code></td><td><code>DjangoChildLessonDigestDomainBypassQuery</code></td><td><b>접두사</b></td></tr>
<tr><td><code>&lt;capability&gt;.py</code></td><td><code>FamilyMembershipPort</code></td><td><code>AccountsFamilyMembershipAdapter</code></td><td><b>접미사</b></td></tr></table></div>
<b>모순이 아니다.</b> <code>Repository</code>·<code>UnitOfWork</code>·<code>DomainBypassQuery</code> 는 <b>구현에도 참인 역할 이름</b>이라 양쪽이 공유하고 접두사가 가른다. <code>Port</code> 는 <b>구현에는 거짓</b>이다(구현은 포트가 아니라 어댑터다) — 그래서 접미사가 갈라야 한다. <span class="dim">실측이 이미 그렇게 돌고 있다 — <code>UnitOfWork</code> 3/3 · <code>Repository</code> 전부.</span><br>
<span class="dim">08-06 · R12 — <code>query_repository/</code> 가 생기면서 <b>드리븐 <code>repository/</code> 의 <code>&lt;capability&gt;.py</code> 가 <code>…Adapter</code> 에서 <code>…QueryRepository</code> 로 옮겨간다</b>. 규칙을 바꾼 게 아니라 <b>이 규칙이 그렇게 판정한 것</b>이다 — <code>QueryRepository</code> 는 구현에도 참인 낱말이다. 덤으로 <code>Adapter</code> 가 «BC 밖·시스템 밖과 이야기하는 것»만 가리키게 되어 어휘가 좁아진다.</span></dd>

<dt class="ans-dt">딸려 닫힌 것 ① — <code>Gateway</code> 24개를 <b>흡수</b>한다</dt>
<dd class="ans-dd filled"><code>FcmPushGateway</code> → <code>port/fcm_push.py</code> · <code>FcmPushPort</code>. <b><code>Gateway</code>·<code>Adapter</code>·<code>Port</code> 는 패턴 이름이고 <code>Issuer</code>·<code>Generator</code>·<code>Sender</code> 는 동사에서 온 능력 이름</b>이다 — 앞의 것만 자리가 대신 말한다.<br>
<b>D18</b> 이 <code>gateway/</code> 폴더를 기각하며 <em>「«게이트웨이»는 이미 <code>port/</code> 쪽 어휘」</em>라고 적어둔 긴장이 <b>여기서 없어진다</b> — 종류 접미사가 두 벌에서 한 벌이 된다.</dd>

<dt class="ans-dt">딸려 닫힌 것 ② — <code>TurnSettlement</code> 는 <b>행위 이름</b>으로</dt>
<dd class="ans-dd filled"><b>D32</b> 가 <code>domain_service/</code> 로 보낸 셋 중 하나가 <b>같은 BC 의 값 객체와 겹친다</b>. 도메인 서비스 파일은 «접미사 0건»이라 접미사로 못 푼다 — <b>무상태 규칙이니 행위 이름이 맞는다</b>.
<div class="pre-wrap"><pre><code>value_object/turn_settlement.py   TurnSettlement            그대로
domain_service/settle_turn.py     SettleTurn                개명
domain_service/turn_preparation.py          TurnPreparation           충돌 없음
domain_service/conversation_summarization.py ConversationSummarization 충돌 없음</code></pre></div>
<b>셋을 다 행위로 바꾸지는 않는다</b> — 실측 43개와 대조가 필요하고, <b>D10</b> 대로 <b>판정이 서는 데까지만</b> 쓴다. 규칙은 <em>「겹치면 행위로」</em> 한 줄이다.</dd>

<dt>이 칸에서 검사되는 것</dt>
<dd><b>①</b> <code>port/</code> 안의 계약은 전부 <code>…Port</code> 로 끝난다<br>
<b>②</b> <code>port/&lt;capability&gt;/&lt;capability&gt;.py</code> 를 구현하는 클래스는 전부 <code>…Adapter</code> 로 끝난다<br>
<b>③</b> 클래스 이름에서 자리 접미사를 뗀 뒤가 <b>«능력을 말하는 쪽»의 CamelCase 를 접미사로 포함</b>한다 — <b>보통은 파일 이름이고, 파일이 «기술»만 말하는 자리에서는 그 폴더 이름</b>이다<br>
<span class="dim"><b>08-07 · 2차 리뷰 S6</b> — 옛 문장은 앵커가 «파일 이름» 하나뿐이라 <b>트리 107행(당시 번호)의 자기 예시를 위반으로 찍었다</b>: <code>framework/clock/django.py</code> 의 <code>DjangoClockAdapter</code> 에서 접미사를 떼면 <code>DjangoClock</code> 인데 파일은 <code>django</code> → <code>Django</code> 라 <code>endswith</code> 가 거짓이다. <b>이 자리에서 능력을 말하는 것은 파일이 아니라 폴더 <code>clock/</code></b> 이고, 그건 형제 <code>&lt;technology&gt;/</code> 칸이 스스로 적고 있다(<em>「폴더가 이미 능력을 말하니 파일은 기술만 말한다」</em>). 여덟 행 중 08-07 에 더한 이 한 행만 깨졌고 한 절로 닫힌다.</span><br>
<b>④</b> <code>Port</code>·<code>Adapter</code>·<code>Gateway</code> 는 <b>파일 이름에 나오지 않는다</b></dd>

<dt>치르는 값 — 정직하게</dt>
<dd><b>이름이 길어진다.</b> <code>NotificationsPairingApprovalNotificationAdapter</code> 는 45자다. 접두사(BC)+능력+접미사가 다 붙어서인데, <b>셋 다 다른 말을 하고 있어</b> 뺄 것이 없다.<br>
<b>§4 의 예시 하나가 바뀐다</b> — <code>DjangoUtcClockAdapter</code> 는 그대로 맞지만 <code>OpenAiLlmStreamingGateway</code> 는 <code>OpenAiLlmStreamingAdapter</code> 가 된다. <span class="dim">예시 둘이 서로 다른 접미사 정책을 태우고 있었다는 것 자체가 이 칸이 열려 있던 증거다.</span></dd>
</dl>

## D32 · 파이프라인은 도메인 판정이었다 — 두 방향이 동시에 일어난다

**확정 · 08-06** · 자리 — ① 칸 &nbsp;·&nbsp; <code>domain_layer/domain_service/</code> &nbsp;·&nbsp; <b>새 칸 0 · 규칙 한 줄</b>

<dl class="kv">
<dt class="ans-dt">물음 — <code>driven_layer/pipeline/</code> 을 어디에 두나</dt>
<dd class="ans-dd filled">대조에서 <code>ai_chat/infra_layer/pipeline/child/</code> 3파일(149줄)이 나왔다. 트리의 <code>driven_layer/</code> 다섯 칸에 하나도 안 맞는다 — <b>셋 다 바깥과 이야기하지 않는다</b>. import 가 전부 <code>domain_layer</code> 의 포트·값 객체뿐이다.</dd>

<dt>정직한 단서 — <b>두 번 잘못 짚었다</b></dt>
<dd><b>①</b> 「지금 담긴 게 상수 3개니 비즈니스 로직이 아니다」 — <b>현행이 골격이라 그렇게 보였을 뿐</b>이다. 사용자가 <em>「파이프라인이 실제로 추가되었다고 가정하고 판단하라」</em>고 해서 잡혔다. <b>규율 ① 이 경고하는 바로 그 함정</b>이다.<br>
<b>②</b> 「I/O 를 하니 응용 서비스다」 — <b>그 자는 트리 어디에도 없다.</b> 유스케이스도 리포지토리를 부르고, 그게 응용인 이유는 <b>조율</b>이지 I/O 가 아니다. 사용자가 <em>「준비하는 게 왜 비즈니스 로직이 아니냐」</em>고 되물어 바로잡혔다.</dd>

<dt class="ans-dt">정체 — <b>도메인 판정이다</b></dt>
<dd class="ans-dd filled">채워지면 <code>prepare()</code> 가 정하는 것: <b>LLM 을 부를까 거절할까</b>(<code>LlmCallPlan</code> vs <code>NoLlmPlan</code>) · <b>거절 사유</b>(안전 차단·사용량 초과) · <b>시스템 지시문</b>(아이에게 어떻게 말하나) · <b>프로필을 어디에 담나</b> · <b>어떤 위젯을 줄 수 있나</b> · <b>이 턴에 얼마를 예약할까</b>. <b>전부 이 제품의 핵심 업무 규칙</b>이다.<br>
결과도 도메인 값 객체다 — <code>LlmCallPlan.__post_init__</code> 이 도구 이름 중복을, <code>NoLlmPlan.__post_init__</code> 이 이벤트 어휘를 막는다. <b>판정 결과가 자기 불변식을 갖는다.</b><br>
<b>Evans 의 SERVICE 3조건을 전부 만족한다</b> — 애그리거트에 안 붙는 도메인 개념 · 인터페이스가 도메인 어휘(<code>TurnContext</code> → <code>TurnPlan</code>) · 무상태.</dd>

<dt class="ans-dt">결정 ① 칸 — <b>새 칸을 만들지 않는다. 두 방향이 동시에 일어난다</b></dt>
<dd class="ans-dd filled">
<div class="pre-wrap"><pre><code>판정하는 것      → 안으로   infra_layer/pipeline/  →  domain_layer/domain_service/      6
바깥과 말하는 것  → 밖으로   domain_layer/*/port/   →  application_layer/port/         64</code></pre></div>
지금은 <b>둘이 서로 반대편에 잘못 가 있다</b> — 판정은 인프라에, I/O 포트는 도메인에. <b>D12</b> 의 선이 하는 일이 정확히 이것이다.<br>
<b>선언 3개도 같이 들어온다</b> — <code>TurnPreparationPort</code> 는 <b>포트가 아니라 도메인 서비스 인터페이스</b>다(<code>Port</code> 접미사를 떼는 것은 남은 이름 규칙 몫). <code>infra_layer/pipeline/</code> 폴더는 통째로 사라진다. <b><code>ChatPipeline</code> 은 08-07 에 자리를 고쳤다</b> — <code>turn/value_object/</code> 에 두면 <code>conversation_room</code> 것을 붙들어 <b>D13</b> 검사① 에 걸린다. 셋과 <b>같은 <code>domain_layer/domain_service/</code></b> 로 간다. <span class="dim">Evans 의 <b>STRATEGY(AKA POLICY)</b> 그 자체다 — 「종류마다 판정 방식이 다르다」를 명시적 객체로 만든 것이고, 원전의 Route Finding 예제가 정책을 <em>「passed into the Routing Service as a parameter」</em> 하는 것과 같은 모양이다. 저장되지 않는 것도 정상이다 — SERVICE·STRATEGY 는 무상태다.</span> <code>composition_root</code> 조립도 D12 결정 ③ 이 이미 허용한다.</dd>

<dt class="ans-dt">그래서 규칙 — <b>인터페이스가 있는 «이유»로 자리가 갈린다</b></dt>
<dd class="ans-dd filled">
<div class="pre-wrap"><pre><code>왜 인터페이스인가                    어디

바깥을 갈아끼우려고                  application_layer/port/  선언
  DB · SMS · LLM · 타 BC             driven_layer/            구현      ← 층이 갈린다

업무가 종류별로 갈려서                domain_layer/domain_service/
  판정의 변종                                                          ← 선언·구현 같은 자리</code></pre></div>
<b>판정은 기계로 된다</b> — <em>구현이 <code>domain_layer</code> 밖을 import 하면 첫째, 아니면 둘째</em>.<br>
<b>왜 하나는 층이 갈리고 하나는 안 갈리나</b>도 같은 근거다 — 리포지토리 구현이 층을 넘는 건 <b>기술을 알기 때문</b>이고, 도메인만 아는 구현은 넘을 이유가 없다.</dd>

<dt>검사 ③ 을 유지한다 — 그리고 원전 예제와 <b>정확히 겹친다</b></dt>
<dd>「도메인 서비스는 순수하다」를 풀면 변종이 포트를 들게 되고 <b><code>domain_layer/*/port/</code> 51개 폴더가 되살아난다</b>(D12 뒤집기). 실측 3건을 위해 전역 규칙을 풀 이유가 없고, <b>풀 필요도 없다</b> — 예약을 뼈대가 잡으면 그대로 순수해진다.<br>
그렇게 뒤집으면 원전의 배치와 그대로 맞는다:
<div class="pre-wrap"><pre><code>Funds Transfer App Service      ↔  turn_streaming_service (뼈대)   조율 · 예약 · 조회
Funds Transfer Domain Service   ↔  child_turn_preparation         판정
Send Notification Service       ↔  usage_quota ACL                바깥</code></pre></div>
<b>검사 ③ 유지가 원전에서 멀어지는 것이 아니라 원전 예제의 모양 그대로다.</b> <span class="dim">검사 ③ 자체가 원전 밖이라는 대조는 D12 에 적었다.</span></dd>

<dt class="ans-dt"><b>플러그인이 정반대를 «결정적 blocker» 로 못 박고 있다</b> <span class="dim">08-06 · R5</span></dt>
<dd class="ans-dd filled"><b>이 결정과 플러그인이 정면으로 부딪힌다.</b> 트리는 협력 포트를 <code>application_layer/port/</code> 로 올리는데,
플러그인은 <b><code>domain_layer/&lt;aggregate&gt;/port/</code> 소유</b>를 세 겹으로 박아 놨다 —
그리고 <b>이건 이름 문제가 아니라 소유자가 뒤집히는 설계 역전</b>이라 <b>D27</b> 이 닫은
«경로 이름 셋»과 성격이 다르다.
<div class="pre-wrap"><pre><code>① 검사 스크립트   scripts/check-layer-skeleton.py:106
                  FOREIGN_PORT_LAYERS = ("application_layer", "infra_layer")
                  이 층 밑 port/ 에 실파일이 있으면 exit 2 = 커밋 차단

② 리뷰어 지침     agents/discipline-reviewer.md:82
                  「협력 포트가 application_layer/&lt;area&gt;/port/ 에 배치 … blocker —
                   명세 정당화는 면제 사유가 아님 · 설계 반송」

③ 표준 문서       skills/discipline-houserules/SKILL.md:66
                  skills/discipline-houserules/references/final.md:87 · 156
                  트리 그림이 &lt;aggregate&gt;/port/ 를 그리고 있다</code></pre></div>
<b>지금은 <code>application_layer/**/port/</code> 실파일이 0이라 통과한다.</b> 트리대로 옮기는 순간 <b>같은 커밋에서 전부 위반</b>이 된다.</dd>
<dt><b>트리가 정본이다 — 근거는 클린이 명시적이다</b> <span class="dim">08-06 · R5</span></dt>
<dd><b>«인터페이스는 그것을 «쓰는» 정책과 같은 링에 산다»</b>가 클린의 문장이다.
플러그인의 핵심 문구는 <em>「애그리거트가 직접 import 하지 않아도 협력 포트의 소유·위치는 도메인이다」</em>인데,
<b>안 쓰는 쪽이 소유한다</b>는 뜻이라 그 원칙과 정면으로 반대다. 그리고 「그것이 도메인의 어휘다」라는 주장의 <b>증거가 없다</b> —
도메인이 그 낱말을 한 번도 쓰지 않는다.<br>
<b>도메인이 실제로 그 협력을 필요로 하면 어떻게 되나</b> — <b>D13</b> 의 규칙이 그대로 답한다:
<em>도메인 서비스는 불러오지 않고 «받는다»</em>. 리포지토리에 이미 걸린 규칙을 협력 포트에 똑같이 적용하면
<b>「도메인은 아무것도 불러오지 않는다」</b> 하나로 통일된다.
<div class="pre-wrap"><pre><code>def select(items, port: RandomDrawPort):   # 도메인이 «부르는» 모양 — 금지
    return items[port.draw(len(items))]

def select(items, draw: int):              # 도메인이 «받는» 모양 — 이게 규칙
    return items[draw]                     # 유스케이스가 뽑아서 넘긴다</code></pre></div></dd>
<dt><b>이행 순서 — 플러그인 먼저, 코드 나중</b> <span class="dim">08-06 · R5</span></dt>
<dd>위 셋을 <b>한 커밋에서 같이</b> 바꾸고, <b>그 다음에</b> 코드를 옮긴다. 순서를 뒤집으면 첫 커밋이 blocker 에 걸려 아예 안 나간다.<br>
<b>이 절을 남기는 까닭</b> — 나중에 이 blocker 를 만난 사람이 <em>「트리가 틀렸나 보다」</em> 하고 되돌리는 것을 막기 위해서다.
<b>몰라서 어긋난 게 아니라 알고 이긴 것</b>이라는 기록이 필요하다.<br>
<span class="dim">덧 — <b>D13</b> 이 남긴 «도메인 서비스가 포트를 부르는» 1건(<code>weighted_copy_selection_service</code> ← <code>random_draw_port</code>)도 여기서 답을 얻는다: 난수를 <b>받도록</b> 바꾸고 포트는 응용에 둔다.</span></dd>

<dt><b>순서만으로는 부족했다 — 개명하는 순간 «조용히 꺼지는» 검사가 있다</b> <span class="dim">08-07 · 2차 리뷰 S3</span></dt>
<dd>결정적 백스톱 19종 중 여럿이 <b>«검사할 파일 목록»을 층 폴더 이름 «문자열»로</b> 만든다.
<div class="pre-wrap"><pre><code># check-response-schema-bypass.py — 진입 게이트
if "presentation_layer" not in parts:
    continue                     # ← 이 폴더 아래가 아니면 건너뛴다</code></pre></div>
개명하면 이 목록이 <b>151개에서 0개</b>가 된다. 검사할 것이 없으니 <b>위반이 있든 없든 <code>exit 0</code></b> 이고, <b>「검사했고 깨끗하다」와 「검사할 것이 없었다」가 같은 숫자로 보고된다</b>(Coordinator 는 숫자만 본다). 같은 위반 파일을 옛 경로·새 경로에 각각 심어 확인했다 — <b>옛 경로 <code>exit 2</code> · 새 경로 <code>exit 0</code></b>.<br>
<b>이건 버그가 아니라 의도된 설계다</b> — 스크립트가 <em>「표준 레이아웃 미적용 → <code>exit 0</code>」</em> 을 명시로 적어 놨다. 표준을 안 쓰는 저장소에서도 돌아야 해서다. <b>문제는 개명이 «표준을 쓰는 우리»를 «안 쓰는 저장소»처럼 보이게 만든다</b>는 것이다.<br>
<b>대상 여섯</b> — <code>check-response-schema-bypass</code>(151→0) · <code>check-openapi-error-declaration</code>(151→0) · <code>check-synthetic-infra-exc</code>(420→0) · <code>check-db-table</code>(16→0) · <code>check-ninja-boundary-middleware</code>(정규식 붕괴) · <code>check-usecase-dto-placement</code>(127→0 — 개명과 무관하게 <code>command/</code>·<code>query/</code> 가 트리에 없어 <b>이미 죽어 있다</b>). <b>그중 셋은 이 문서의 결정 카드 어디에도 이름이 없었다.</b></dd>

<dt class="ans-dt">그래서 정한 것 — <b>이중 수용 + 「채택했는데 대상이 0이면 blocker」</b> <span class="dim">08-07 · 사용자 결정</span></dt>
<dd class="ans-dd filled"><b>㉠ 이중 수용</b> — 이관 기간에는 <b>옛 이름과 새 이름을 둘 다</b> 받는다(<code>presentation_layer</code>·<code>driving_layer</code> 둘 다 통과).<br>
<b>㉡ 가드</b> — 「저장소가 표준을 채택한 신호는 있는데 <b>검사 대상이 0건</b>」이면 <b><code>exit 2</code></b>.
<div class="pre-wrap"><pre><code>targets = _find_..._files(root)     # 경로가 만든 대상 집합
if not targets:
    if layout_adopted(root):        # ← 가드는 «여기»
        return 2                    #   경로가 안 맞아서 0건 = 결함
    return 0                        #   표준 미적용 = 정상(기존 동작 그대로)
# ↓ 여기서부터 touched 필터 — 여기서 0건이 되는 것은 «정상»이다</code></pre></div>
<b>둘은 짝이어야 한다.</b> 이 카드의 순서가 «플러그인 먼저»라, 고친 직후에는 <b>16개 BC 가 전부 옛 이름</b>이다. 이중 수용 없이 가드만 넣으면 그 구간에 매번 <code>exit 2</code> 가 나서 <b>이관 자체가 막힌다.</b><br>
<b>가드를 두는 «자리»가 결정적이다</b> — <code>touched</code> 필터 <b>앞</b>이다. 플러그인은 <em>「중간 커밋 뒤에는 touched 가 비어 검사가 비어 돈다」</em> 를 <b>의도된 성질</b>로 적어 놨으니, 뒤에 두면 <b>정상 커밋마다 blocker</b> 가 난다. 막을 것은 <b>«경로가 안 맞아서 0건» 하나뿐</b>이다.<br>
<b>발명이 아니다</b> — <code>check-layer-skeleton.py</code> 는 이미 채택 신호를 <b>둘</b> 쓴다: <em>층 폴더가 있나</em> <b>또는</b> <em>Django 앱 산출물(<code>apps.py</code>·<code>migrations/</code>)이 있나</em>. <b>두 번째는 층 이름이 바뀌어도 안 죽는다.</b> 꺼지는 여섯은 신호가 하나뿐이라 죽는 것이고, 이 결정은 <b>한 군데서 이미 하는 것을 나머지에 맞추는 일</b>이다.<br>
<b>이 카드의 <code>port/</code> 역전만은 이중 수용이 «안 된다»</b> — 옛 규칙은 「<code>application_layer/port/</code> 는 위반」이고 트리는 「정답」이라, <b>같은 자리를 위반이자 정답이라고 동시에 말할 수 없다.</b> 그것만 바로 반전한다.<br>
<b>⚠ 이관이 끝나면 옛 이름을 지운다.</b> 옛 이름이 살아 있는 한 「경로가 안 맞아서 0건」이 <b>영영 안 일어나</b> 가드가 <b>한 번도 안 도는 죽은 코드</b>가 된다. <b>이관 완료 조건에 명시로 넣는다.</b></dd>

<dt>딸려 나온 것 — <b>플러그인이 «트리에 없는 구조»를 요구하는 자리 둘</b> <span class="dim">08-07 · 2차 리뷰 S4</span></dt>
<dd><code>check-layer-skeleton.py</code> 의 상수 둘은 <b>만족시킬 대상이 아예 없는 조건</b>이다.
<div class="pre-wrap"><table class="mini">
<tr><th>플러그인이 요구하는 것</th><th>트리</th></tr>
<tr><td><code>AGG_CORE_KIND_DIRS</code> 가 <code>repository</code> 를 <b>디렉터리</b>로 요구</td><td>트리 60행은 <b>파일</b>이다(<code>&lt;aggregate&gt;_repository.py</code>) — <b>애그리거트당 하나</b>라서. 폴더 검사를 <b>파일 검사로</b> 바꾼다</td></tr>
<tr><td><code>REQUIRED_KIND_DIRS</code> 의 BC 레벨 <code>schema/</code></td><td>트리의 <code>schema/</code> 는 <code>api/&lt;area&gt;/</code> 밑뿐이고 <b>BC 레벨은 존재 자체가 없다</b>(<b>D27</b>). 필수 조건에서 <b>뺀다</b></td></tr></table></div>
<b>이 카드의 <code>port/</code> 역전과 성격이 같다</b> — 몰라서 어긋난 게 아니라 <b>트리가 이겼고</b>, 플러그인을 트리에 맞춘다.</dd>
<dt>적어두는 신호 — <b>재료를 한 번에 못 모으는 경우</b></dt>
<dd>「재료는 응용이 모아 값으로 넘긴다」가 항상 되지는 않는다 — <b>판정 결과에 따라 다음 조회가 달라지면</b>(A 를 보고 B 를 조회할지 정한다) 한 번에 못 모은다. <b>지금 실측에는 없다.</b><br>
생기면 답은 <b>판정을 두 조각으로 쪼개는 것</b>이다(도메인 판정 → 응용 조회 → 도메인 판정). <b>규칙을 푸는 것이 아니다.</b></dd>

<dt>3-a 는 트리가 이미 답했다</dt>
<dd>파다가 나온 것 — <b><code>domain_layer/*/port/</code> 폴더 51개 · 파일 54 · 클래스 70(그중 ABC/Protocol 선언 54)</b>. D12 가 이 칸을 명시적으로 기각했는데 실측이 통째로 어긋나 있었다. 구현이 무엇과 이야기하는지로 재면 <b>django·SDK·HTTP 15 · ACL(타 BC) 23 · adapter(벤더) 10 · 구현 미발견 16</b> 이고 <b>바깥이 «없는» 것은 정확히 3</b> — 그게 이 카드의 셋이다. <b>측정이 물음을 그대로 재현했다.</b> 나머지 64 는 <code>application_layer/port/</code> 로 가는 <b>코드 고칠 목록</b> 항목이다.</dd>
</dl>

## D31 · 커밋 뒤에 보내기 — 묻지 말고 맡긴다

**확정 · 08-06 · 08-08 에 폴더 개명** · 자리 — ① 칸 &nbsp;·&nbsp; <code>application_layer/port/unit_of_work/</code> &nbsp;·&nbsp; <b>계약에 한 줄을 더한다. 칸은 안 는다</b>

<dl class="kv">
<dt class="ans-dt"><b>08-08 · F6 — 폴더 이름이 <code>transaction/</code> 에서 <code>unit_of_work/</code> 로 바뀌었다.</b></dt>
<dd class="ans-dd filled"><code>transaction</code> 은 <b>장고의 낱말</b>이고, 트리가 <em>「<code>connection</code>·<code>transaction</code> 을 아는 것은 여기(드리븐)까지」</em> 라고 못박아 두고
<b>응용층 폴더 이름에 그 말을 쓰고 있었다</b>. 파일도 클래스도 이미 <code>unit_of_work</code> 였다. <span class="dim"><code>uow/</code> 는 규율 ④(약어를 쓰지 않는다)에 걸린다.</span> <b>D37</b></dd>
<dt class="ans-dt">물음 — <b>응용이 django 의 <code>connection</code> 을 보고 있다</b></dt>
<dd class="ans-dd filled">실측 13곳이 <code>connection.in_atomic_block</code> 을 읽는데 그중 <b>응용 2 · OHS 1 이 층 위반</b>이다(<code>from django.db import connection</code>). 전역 제약 ②(안쪽은 구체 기술을 모른다)에 걸린다.</dd>

<dt>무엇을 막으려던 코드였나 — <b>알림은 되돌릴 수 없다</b></dt>
<dd>DB 는 롤백되지만 <b>이미 보낸 푸시는 못 거둔다</b>. 그래서 순서가 계약이다.
<div class="pre-wrap"><pre><code>알림 → 저장 실패 → 롤백     「발급됐어요!」 는 갔는데 DB 엔 없다
저장 → 커밋 → 알림          알림이 갔다면 DB 에도 반드시 있다</code></pre></div>
<b>그런데 «<code>with</code> 밖에서 부른다»로는 부족하다</b> — 누군가 이 유스케이스를 <code>transaction.atomic()</code> 으로 감싸면 안쪽 <code>with</code> 를 나와도 <b>중첩(savepoint)이라 진짜 커밋은 바깥이 끝나야</b> 일어난다. 그래서 코드가 <b>«지금 누가 나를 감싸고 있나»</b> 를 묻는다 — 메서드 이름이 그대로 <code>_ensure_no_ambient_transaction</code> 이다.<br>
<span class="dim">즉 «내가 올바르게 짰다»는 유스케이스가 스스로 보장할 수 있지만 <b>«아무도 나를 안 감쌌다»는 못 한다</b>. 가드는 그걸 확인하는 코드였다.</span></dd>

<dt class="ans-dt">실측 — <b>같은 문제에 답이 둘, 정확히 반반이었다</b></dt>
<dd class="ans-dd filled">
<div class="pre-wrap"><pre><code>① transaction.on_commit(...)        7곳   pairing 5 · accounts 1 · lessons 1
     감싸여도 안전 — 바깥이 커밋될 때 실행, 롤백되면 «아예 실행 안 됨»

② with 밖에서 직접 부르고 가드       7곳   응용 2 · OHS 1 · ACL 4
     감싸이면 깨진다 → 그래서 in_atomic_block 을 묻는다</code></pre></div>
<b>①로 통일한다.</b> 검사가 아니라 <b>구조가 보장</b>하고, 갈래 ② 7곳이 통째로 없어진다.</dd>

<dt class="ans-dt">결정 ① 칸 — <b>칸을 만들지 않는다. 계약에 한 줄을 더한다</b></dt>
<dd class="ans-dd filled">
<div class="pre-wrap"><pre><code>class &lt;Bc&gt;UnitOfWork(ABC):
    def __enter__(self) -&gt; …
    def __exit__(self, …) -&gt; …
    def after_commit(self, callback: Callable[[], None]) -&gt; None: ...   ← 더한다</code></pre></div>
<div class="pre-wrap"><pre><code>with self._uow_factory() as unit_of_work:
    unit_of_work.entitlements.save(entitlement)
    unit_of_work.after_commit(lambda: self._notification.publish(...))
# 커밋되면 실행 · 롤백되면 «안» 실행 — 감싸여도 같다</code></pre></div>
<b>구현은 <code>driven_layer/unit_of_work.py</code> 가 <code>transaction.on_commit</code> 으로 채운다.</b> <code>connection</code>·<code>transaction</code> 을 아는 건 거기까지다.</dd>

<dt>왜 이 모양은 맞고 <code>is_active</code> 는 아니었나</dt>
<dd>처음엔 <code>uow.is_active</code>(«지금 트랜잭션 안이냐»)를 검토했다. <b>모양이 안 맞는다</b> — 그걸 물어야 하는 시점은 <code>with</code> <b>밖</b>이라 인스턴스가 없다. <br>
<b><code>after_commit</code> 은 <code>with</code> «안»에서 맡기는 것</b>이라 인스턴스가 있다. <b>같은 문제인데 «묻기»에서 «맡기기»로 바꾸니 자리가 생겼다.</b></dd>

<dt class="ans-dt"><b>D14</b> 가 <b>이걸 가리키고 있었다</b></dt>
<dd class="ans-dd filled">UoW 를 트리에 올린 이유 ⒝ 가 이렇게 적혀 있다 — <em>«유스케이스가 «커밋 시점»을 알아야 한다. <b>D13</b> 이 «이벤트는 커밋 뒤에 발행»으로 정했다. 커밋 지점을 알아야 그 뒤가 어디인지 안다»</em>.<br>
<b>«커밋 시점을 안다»의 실행 수단이 <code>after_commit</code> 이다.</b> 이유는 적어놓고 <b>계약에 넣는 걸 빠뜨렸던 것</b>이고, 그 구멍으로 응용이 django 를 직접 부르게 됐다.</dd>

<dt class="ans-dt">결정 ③ 화살표 · ④ 앎의 범위</dt>
<dd class="ans-dd filled"><b><code>application_layer</code> 는 <code>django.db</code> 를 import 하지 않는다</b> — AST 로 판정된다. 커밋 뒤 부작용은 <b>UoW 를 거친다</b>.<br>
<b>남는 것은 정당하다</b> — 실측 13곳 중 <b>6곳은 그대로 둔다</b>: 락 조회 앞의 <em>«트랜잭션 «안»이어야 한다»</em> 3곳(<code>select_for_update</code> 는 트랜잭션 안에서만 의미가 있고 그걸 아는 게 리포지토리 구현의 일이다)과 <b>UoW 구현 자신</b> 3곳. <b>둘 다 <code>driven_layer</code> 라 층 위반이 아니다.</b></dd>

<dt>관문 방어를 남길지는 <b>트리가 정하지 않는다</b></dt>
<dd><code>notifications</code> 와 <code>delivery</code> 의 <b>관문 2곳</b>은 남의 BC 실수를 막는 <b>공개 계약의 선행조건</b>이다. 모든 호출자가 <code>after_commit</code> 을 쓰면 <b>도달 불가</b>가 되지만, 관문이 굳이 방어하겠다면 그것도 <b>포트를 거쳐야</b> 한다. <b>어느 쪽이든 트리는 안 바뀐다</b> — <b>D10</b> 로 구현 판단에 남긴다.</dd>

<dt>정직한 단서 — <b>사용자가 먼저 옳은 방향을 짚었다</b></dt>
<dd>«UoW 를 두 개 쓰면 되지 않나 — 알림 전까지 하나, 알림 하나»가 물음이었다. <b>로컬 구조로는 정확히 그게 답이고 실측 <code>entitlements</code> 가 그렇게 짜여 있다.</b> 부족한 건 하나뿐이었다 — <b>«바깥이 감쌌을 때»</b>. <code>on_commit</code> 은 그 한 칸을 마저 메운다.</dd>
</dl>

## D30 · DTO 는 검사하지 않는다 — 폴더가 아니라 «복제»가 문제였다

**확정 · 08-06** · 자리 — ① 칸 &nbsp;·&nbsp; <code>application_layer/&lt;area&gt;/&lt;use_case&gt;/</code> &nbsp;·&nbsp; <b>칸을 만들지 않는다</b>

<dl class="kv">
<dt class="ans-dt">물음 — <code>application_layer/*/validation/</code> 에 칸을 줄까</dt>
<dd class="ans-dd filled">대조에 딱 하나 걸렸다.
<div class="pre-wrap"><pre><code>products/application_layer/application_contract/validation/dto_validation.py   44줄 · 함수 6개
   └ 쓰는 곳: product_catalog/ 의 DTO 6개</code></pre></div>
<b>잔챙이 1건이라 넘기려다 열어 보니 칸 문제가 아니었다.</b></dd>

<dt class="ans-dt">답 — <b>칸을 만들지 않는다. 트리가 이미 금지하고 있었다</b></dt>
<dd class="ans-dd filled"><code>application_layer/</code> 의 자식 폴더는 <b><code>&lt;area&gt;/</code>·<code>port/</code> 둘뿐</b>이다<span class="dim">(08-06 에 <code>transaction/</code> · 08-07 에 <code>query_repository/</code> 가 늘어 넷이었다가, <b>08-08 에 둘이 <code>port/</code> 아래로 들어가 둘로 줄었다</b> — <b>D37</b>)</span>. <code>application_contract/</code> 는 어디에도 안 들어간다 — <b>새 발견이 아니라 이미 막혀 있던 것</b>이다. 실측 넷이 같은 말을 한다:
<div class="pre-wrap"><pre><code>16개 BC 중 products 하나만 갖고 있다              표준이 아니라 표류
형제는 전부 area 이름인데 이것만 종류 이름     §0-4(도메인 축 1차) 위반
폴더 안에 폴더 하나, 그 안에 파일 하나            2겹 껍데기
이름과 내용이 다르다                             DTO 는 &lt;use_case&gt;/ 에 있다</code></pre></div>
<span class="dim">«application contract» 는 <b>DTO 자체</b>를 가리키는 말이다 — 플러그인의 <code>check-usecase-dto-placement</code> 가 «유스케이스 데이터 계약»으로 쓴다. 정작 그 폴더엔 검사 함수만 있다(원칙 07).</span></dd>

<dt>왜 폴더가 생겼나 — <b>공유가 폴더를 낳았다</b></dt>
<dd>
<div class="pre-wrap"><pre><code>DTO 6개가 같은 검사를 쓴다
   → 함수를 파일로 뺀다      dto_validation.py
      → 파일을 폴더에 넣는다   validation/
         → 폴더를 폴더에 넣는다 application_contract/</code></pre></div>
그런데 <b>그 «공유할 것»의 정체가 도메인 규칙 복제였다.</b> <code>Product</code> 애그리거트가 <b>같은 상수·같은 로직·같은 메시지 문자열</b>을 이미 갖고 있다.
<div class="pre-wrap"><pre><code>dto_validation.py                     product.py
_MAX_SIGNED_BIGINT                    _MAX_SIGNED_BIGINT
_MAX_PRODUCT_NAME_LENGTH = 100        _MAX_PRODUCT_NAME_LENGTH = 100
normalize_product_name                Product._normalize_name
validate_positive_signed_bigint       Product._validate_positive_token_limit
validate_nonnegative_signed_bigint    Product._validate_price</code></pre></div>
다른 건 <b>예외 타입 하나</b>다 — <code>TypeError</code>/<code>ValueError</code> vs <code>InvalidProduct</code>. <b>같은 규칙 위반이 두 채널로 나간다</b>(D27 과 어긋난다). <b>도메인에서 가져다 썼으면 공유할 게 없고 파일도 폴더도 안 생긴다.</b></dd>

<dt class="ans-dt">그래서 규칙 — <b>「막을 게 사용자냐 개발자냐」</b></dt>
<dd class="ans-dd filled">
<div class="pre-wrap"><pre><code>값이 어디서 왔나            누가 막나                나가는 오류
─────────────────────      ──────────────────       ──────────
바깥 (HTTP · 폼)            입구 schema_in           pydantic → 422   (D27)
저장소 (DB rehydrate)       애그리거트                도메인 예외
우리 자신 (방금 만든 값)     아무도                    —</code></pre></div>
<b>개발자 실수를 막는 검사는 런타임이 아니라 테스트·타입 체커의 몫이다</b> — 런타임에 두면 프로덕션에서 500 이 나고, 테스트에 두면 CI 가 빨개진다. 실측 6개 함수를 이 자로 재면 <b>둘은 개발자용(<code>result</code> DTO 검사), 넷은 사용자용인데 셋은 도메인이 이미 한다</b>. <b>남을 것 0.</b><br>
<span class="dim">장치가 이미 다 켜져 있다 — <code>[tool.mypy] strict = true · warn_unreachable = true</code> 에 pre-commit 훅, 그리고 어드민은 <code>forms.ModelForm</code> 이 런타임 강제를 한다. <code>type(value) is not bool</code> 을 런타임에 묻는 건 <b>이미 보장된 걸 세 번째로 묻는 것</b>이다.</span></dd>

<dt>같은 자가 <b>BC 전체를 재게 한다</b></dt>
<dd>
<div class="pre-wrap"><pre><code>응용 DTO 214개 · 검사하는 것 8         → 남을 것 0
   products 6      도메인이 이미 한다  (안쪽에서 막힌다)
   managed_copy 2  입구가 이미 한다    (Literal 이 좁혀서 «도달 불가»)</code></pre></div>
<b>출력 스키마도 같은 자로 갈린다</b> — <code>schema_out.py</code> 18개 중 검사 10지점: <b>좁히기(<code>X | None → X</code>) 6 · 전수 분기의 나머지 1 은 정당</b>(검사가 아니라 <em>변환이 불가능한 경우</em>다), <b>자기검사 2 는 지운다</b>(<code>managed_copy</code> 와 <code>billing</code> — 후자는 주석에 «도달 불가 방어»라고 스스로 적어놨다), <b>입력 파싱 1 은 자리가 틀렸다</b>(<code>lessons</code> 의 status 필터 — <code>schema_in</code> 것).<br>
<span class="dim">반례로 확인 — <code>CopyType.require_general</code> 은 <b>애그리거트 안에서는 필요하다</b>. <code>rehydrate</code> 로 <b>DB 행</b>이 들어오기 때문이고 그건 타입으로 못 막는다. 호출 5곳 중 <b>애그리거트 2 만 남는다</b>. 「검사를 다 없앤다」가 아니라 <b>「값이 온 곳이 막는다」</b>가 규칙이다.</span></dd>

<dt>플러그인이 이걸 <b>다시 못 만들게</b> 한다 <span class="dim">사용자 요청 · 4번 ⓐ</span></dt>
<dd>결정적 백스톱 세 슬라이스를 <b>4번 ⓐ</b> 에 넣었다 — <b>S1</b> <code>application_layer/**/&lt;use_case&gt;_{command|query}.py</code> 가 <code>raise</code> 한다(<em>검사는 반드시 raise 하고 정규화·파생값은 안 해서 오탐이 없다</em>) · <b>S2</b> <code>application_layer/</code> 아래 <code>validation/</code> 폴더나 <code>*_validation.py</code>(<em>실물이 <code>dto/</code> 밑이 아니었다</em>) · <b>S3</b> <code>application_layer/</code> 직속 자식이 <b><code>&lt;area&gt;/</code>·<code>port/</code> 둘 밖</b>(<em><code>application_contract/</code> 를 직격</em>). touched 한정이라 기존 코드는 grandfather 된다.<br>
<span class="dim"><b>08-07 · 2차 리뷰 S1</b> — S3 의 허용 목록이 <b>둘</b>이었다. 적힌 대로 구현하면 <b>정상 폴더 <code>transaction/</code>·<code>query_repository/</code> 가 첫 커밋에서 blocker</b> 다. 이 카드가 트리의 목록을 안 따라간 다섯 자리 중 하나였고, 다섯 중 <b>집행으로 새는 것은 이 줄뿐</b>이다.</span></dd>
</dl>

## D29 · 리포지토리는 어디까지인가 — 원전이 선을 그어줬다

**확정 · 08-06 · 08-08 에 자리·이름 개정** · 자리 — ① 칸 &nbsp;·&nbsp; ② 이름 &nbsp;·&nbsp; ③ 화살표 &nbsp;·&nbsp; ④ 앎의 범위 &nbsp;·&nbsp; <b>자료조사로 정했다</b>

<dl class="kv">
<dt class="ans-dt"><b>08-08 · F6 — 자리와 이름이 바뀌었다. 판정선은 그대로다.</b></dt>
<dd class="ans-dd filled">선언이 <code>port/</code> 의 «형제»에서 <b>«아래»</b>로 들어갔고(<code>application_layer/port/domain_bypass_query/</code>),
구현은 <code>driven_layer/adapter/persistence/domain_bypass_query/</code> 로 <b>분가</b>했다 — 옆 칸과 도메인 import 가 <b>필수 ↔ 금지</b>로 정반대라 이제 <b>검사가 폴더 단위로 선다</b>.
<b>이름</b>은 <code>query_repository</code> 가 「조회냐」로 물어서 <b>애그리거트 리포지토리와 안 갈렸다</b>(그쪽도 <code>find_by_id</code>·<code>count</code> 를 한다).
<b>형제였던 근거도 낡았다</b> — <em>「포트는 바깥에 «행위자»가 있어야 하는데 DB 는 행위자가 아니다」</em> 였는데, <b>Cockburn 의 2차 행위자 표준 예가 바로 DB·시계라 「행위자가 아니다」부터 원전 오독이었다</b>. 아래 문단들에 그 문장이 남아 있다. <b>D37</b></dd>

<dt class="ans-dt">★ <b>08-09 · T40 — 판정이 «주인»을 안 물었다</b></dt>
<dd class="ans-dd filled"><b>옛 판정은 한 줄이었다</b> — <em>「돌려주는 것이 애그리거트면 리포지토리, 화면 자료면 여기」</em>.
그런데 <b>「남의 BC 에서 받아온 화면 자료」도 이 문장을 통과한다.</b> 실제로 사용자가 그렇게 읽었다 —
<em>「실패한 결제 <b>ID 만</b> 받아오는 거니까 이런 게 bypass 아니야?」</em>
<br>막고 있던 것은 <b>구현 쪽 규칙</b>뿐이었다(<code>persistence/</code> 는 «내» ORM 모델만 만진다). 그래서
<b>개발자가 어댑터를 짜다가야 「어, 남의 표를 못 읽네」를 알게 된다</b> — 선언 자리에서 갈렸어야 했다. <b>판정을 2단으로 고쳤다.</b>
<div class="pre-wrap"><pre><code>① 이 자료의 «주인»이 나인가
     남   →  port/&lt;capability&gt;/ + ACL  →  상대 창구
             (먼저 「정말 남의 것인가」를 물을 것)
     나   →  ②

② 돌려주는 것이 애그리거트인가, 화면 자료인가
     애그리거트  →  domain_layer/&lt;aggregate&gt;_repository.py
     화면 자료   →  여기</code></pre></div></dd>

<dt>자료조사 — <b>「업무 로직이 없으면 BC 를 안 가로지르는 것 아닌가」</b></dt>
<dd><b>이 물음이 T40 의 출발점이었고, 답은 «반만 맞다» 다.</b>
<br><b>맞는 쪽</b> — 조회에는 업무 판단이 없으니 <b>D48</b> 의 자(「실패하면 내가 할 일이 있나」)로는 <b>아무것도 안 갈린다</b>. 조회는 «단계»가 아니다.
<br><b>갈리는 쪽</b> — <b>cross-BC 의 값은 «로직»이 아니라 «스키마 소유권»이다.</b> 남의 표를 조인하면 로직이 0이어도 결합이 생기고, 그 결합은 <b>조용히</b> 깨진다.
<div class="pre-wrap"><pre><code>Kamil Grzybek — Modular Monolith: Integration Styles (공유 DB 방식)
  "modules share their state which couples them together"
  "one little change to database structure or even data itself
   can break another module without notice"</code></pre></div>
<b>장고에서는 더 심하다</b> — FK 한 줄로 경계를 «조용히» 넘을 수 있다.
<em>Makimo, <b>Modular Monolith in Django</b>: “we need to make sure that there are <b>no DB relations (Foreign Keys, etc.) between models from distinct modules</b>” · “Instead of relations, we will <b>just use the IDs</b>” · “Each view should <b>not use Django models directly</b> but rather call necessary <b>public interface functions</b>.”</em>
<b>이 트리는 이미 그렇게 막고 있다</b> — <code>persistence/</code>(ORM 은 이 폴더 안에서만) + <code>anticorruption_layer/</code>(타 BC 는 여기서만).</dd>

<dt>한 BC <b>안</b>에서는 조인이 «정식»이다 — 원전</dt>
<dd><b>Vernon, IDDD — <b class="v d">Use Case Optimal Query</b></b> ✔:
<em>“you might instead use what is called a <b>use case optimal query</b>, where you design your Repository with finder query methods that <b>compose a custom object as a superset of one or more Aggregate instances</b>.”</em>
<br><b>즉 여러 애그리거트를 한 조회로 합치는 것은 금지가 아니라 이름 붙은 패턴이다.</b> 이 칸이 바로 그 자리이고, <b>갈리는 것은 «BC 를 넘느냐»뿐</b>이다.</dd>

<dt>BC 를 넘을 때 — <b>원전들이 순위를 매겨 놨다</b></dt>
<dd>Grzybek 이 정확히 이 물음(<em>“How do you join data from different module if needed?”</em>)에 답한 목록이다.
<div class="pre-wrap"><table class="mini">
<tr><th>순위</th><th>방법</th><th>원문</th></tr>
<tr><td>1</td><td><b>사실로 받아 내 표에 저장</b></td><td><em>“send an event like <code>PremiumUserActivated</code> and 'Article' module will save this information”</em></td></tr>
<tr><td>2</td><td><b>입구에서 두 번 불러 합친다</b></td><td><em>“Execute 2 calls from GUI/API layer … and combine data”</em></td></tr>
<tr><td>3</td><td>리포팅 전용 모듈</td><td><em>“Get data by subscribing to events or using ETL”</em></td></tr>
<tr><td>4</td><td>직접 호출</td><td><em>“as <b>last resort</b>”</em></td></tr>
<tr><td>5</td><td><b>DB 공유(조인)</b></td><td><em>“as <b>last, last, last, last, last resort</b>”</em></td></tr>
</table></div>
<b>Vernon 도 같은 편이다</b> — <em>“<b>Read Model Projections</b> … are also quite useful for <b>sharing information between Bounded Contexts</b> … realized through a simple set of <b>Domain Event subscribers</b>.”</em>
<br><b>이 트리가 택한 것은 1·2 이고, 순서는 «2 → 1» 이다</b> — 창구에 물어 식별자를 받고 내 표에서 좁히는 것이 기본이고(<code>&lt;use_case&gt;_use_case.py</code> 행), 사본(1)은 그게 못 돌 때다.
<b>사본은 «칸»으로 열지 않는다</b> — 읽기 모델 갱신(CQRS)은 이 트리가 <b>관할 밖</b>으로 이미 못 박았고(2장), 저장·재생·정합이 전부 새 문제다. 여는 날의 쓰기 자리는 <b>T37</b> 과 한 칸이다.</dd>

<dt>정직한 표기 — <b>예시를 두 번 잘못 들었다</b></dt>
<dd>「수업 ↔ 선생님」과 「주문 ↔ 결제 금액」을 cross-BC 예로 들었는데 <b>둘 다 아니었다</b>. 선생님은 수업과 같이 바뀌고, <b>주문 금액은 주문 것</b>이다(결제 BC 가 갖는 것은 승인번호·PG·환불·정산이다).
<b>사용자가 둘 다 잡았고, 그 사실 자체가 답의 일부다</b> — <b>남의 BC 값으로 «정렬·필터»해야 하는 경우는 실제로 드물다.</b>
<br><b>진짜로 갈리는 예</b>는 주인이 확실히 다른 것이다 — <em>「기기 <b>배송</b>이 아직 안 끝난 학생의 예정 수업」</em>. 배송 상태는 운송장·택배사·재배송이 딸린 물류 업무라 수업 표에 넣으면 그 셋이 따라 들어온다.</dd>

<dt class="ans-dt">물음 — <b>애그리거트당 리포지토리 하나가 맞나</b></dt>
<dd class="ans-dd filled">대조에서 <code>accounts/parent/otp_challenge_repository.py</code> 가 나왔다 — <b>한 애그리거트에 리포지토리가 둘</b>. 그래서 물음이 열렸다: <b><code>&lt;aggregate&gt;_repository.py</code> 를 폴더로 바꾸고 안을 <code>command/</code>·<code>query/</code> 로 가를까?</b> 드리븐 쪽도 짝으로 가르고.</dd>

<dt>정직한 단서 — <b>두 번 기각했는데 근거가 둘 다 틀렸다</b></dt>
<dd><b>①</b> 「실측에 안 갈려 있으니 안 가른다」 — <b>규율 ① 위반</b>이다. 원리로 짓고 실측은 뒤에 대는 것인데 실측을 근거로 썼다.<br>
<b>②</b> 「층으로 가르는 게 더 세다 — 읽기는 응용에서만 일어나니까」 — <b>재보니 51:1 로 반대였다</b>. 읽기 유스케이스 52개 중 <b>51개가 도메인 리포지토리로 읽는다</b>(응용 포트 직행은 1건).<br>
<b>기각은 살아남았지만 근거는 통째로 갈렸다.</b> 아래가 새 근거다.</dd>

<dt class="ans-dt">원전이 이 물음에 <b>직접</b> 답한다 <span class="dim">Greg Young, <em>CQRS Documents</em> (2010) 3·6장</span></dt>
<dd class="ans-dd filled">
<div class="pre-wrap"><pre><code>"The domain has been bypassed. There is now a new concept called a
 'Thin Read Layer'. This layer reads directly from the database and
 projects DTOs."

"repositories have very few if any query methods aside from GetById"

"With CQRS the only query that exists within the domain is GetById"</code></pre></div>
<b>CQRS 가 가르는 것은 «메서드»가 아니라 «모델»이다.</b> 조회 쪽은 옆 폴더로 옮기는 게 아니라 <b>도메인을 통째로 우회</b>해 DB 에서 바로 DTO 를 만든다. 그리고 <b><code>GetById</code> 는 도메인에 남는다</b> — 읽기 메서드인데 <b>쓰기 쪽 물건</b>이다.<br>
<span class="dim">교차 확인 — Microsoft 의 표준 CQRS 예제도 명령 핸들러가 <b>리포지토리 «하나»</b>(<code>IRepository&lt;Product&gt;</code>)를 들고 <code>Find()</code> 와 <code>Save()</code> 를 부른다. 읽기 모델은 아예 다른 물건이다(<code>ReadModel.ProductsDao</code> → <code>ProductDisplay</code>). <b>반환 타입이 다른 것</b>이 CQRS 가 가른 것이다.</span></dd>

<dt><code>command/</code>·<code>query/</code> 폴더는 <b>선을 정반대로 긋는다</b></dt>
<dd>
<div class="pre-wrap"><pre><code>원전                            command/query 폴더
──────────────────────────      ──────────────────────────
GetById    → 도메인에 남는다     GetById    → query/ 로 나간다   ← 뒤집혔다
그 밖 조회 → 도메인을 «떠난다»    그 밖 조회 → 옆 폴더에 남는다   ← 안 떠났다</code></pre></div>
그리고 <b>양쪽이 여전히 같은 애그리거트를 돌려준다</b>. 모델이 안 갈렸으니 CQRS 가 주는 것(읽기 전용 스키마·비정규화 뷰·독립 확장)이 <b>하나도 안 생긴다</b> — 이름만 CQRS 다.<br>
<b>실측이 같은 말을 한다</b> <span class="dim">08-06 · R8 에서 넓혀 다시 쟀다</span> — 응용이 실제로 부르는 «값을 돌려주는» 리포지토리 메서드 <b>96개</b> 중 <b>69개(72%)가 쓰기 유스케이스에서만 불린다</b>(읽기 전용 19 · 양쪽 8). 가장 많이 불리는 둘이 <code>find_by_id</code> <b>command 18 : query 14</b> · <code>get</code> <b>command 20 : query 5</b> 다. <code>query/</code> 를 만들면 <b>그 안의 대부분을 <code>command/</code> 가 import 한다</b> — 폴더 이름이 거짓말을 한다.<br>
<b>판정도 안 선다</b> — <code>load_for_update</code>(이름부터 읽어서 쓰겠다) · <code>get_or_open</code>(없으면 만든다) · <code>list_reminder_candidates</code>(배치가 «발송하려고» 뽑는다) · <code>mark_reminder_sent</code>(CAS 라 결과를 읽어 돌려준다). <b>D10 «판정 가능성이 있는 데까지만»</b> 에 걸린다.<br>
<span class="dim">덤 — <code>&lt;aggregate&gt;_repository.py</code> 가 둘이 되면 <code>save</code> 의 낙관 가드가 «<code>get</code> 이 읽은 시점의 상태 토큰»을 쓰는데 <b>그 한 쌍이 두 파일로 갈린다</b>.</span></dd>

<dt class="ans-dt">원전은 <b>«세 자리»에 각각 이름을 붙여 놨다</b> <span class="dim">08-06 · R8 재조사</span></dt>
<dd class="ans-dd filled">처음 이 칸이 잡은 축(«애그리거트 <b>루트</b>를 돌려주느냐»)은 <b>자기가 지키려던 코드를 위반으로 찍었다</b> — 「나갈 11개」로 직접 지목한 반환형이 <code>PricePeriod</code>·<code>CurrentUsageBuckets</code>·<code>NotificationRecordPage</code> 처럼 <b>전부 도메인 타입</b>이라, 나가면 ③ 검사(<code>domain_layer</code> 를 import 하지 않는다)에 걸려 <b>만들 수가 없다</b>. <span class="dim">덤 — <code>UsageQuotaDecision</code> 은 HEAD 에 <b>도메인 타입으로 존재하지 않는다</b>(마이그레이션에만 남은 삭제 모델).</span><br>
원전을 다시 읽으니 <b>세 자리가 각각 이름을 갖고 있었다</b>:
<div class="pre-wrap"><pre><code>① 애그리거트를 꺼내고 넣는다 · 그 컬렉션을 세고 합친다
      Evans  「A REPOSITORY … acts like a collection」
             「can also return summary information, such as a count of
              how many instances meet some criteria」

② 여러 애그리거트를 가로지르되 도메인 어휘로 답한다
      Vernon 「Use Case Optimal Query」 — 상위 집합을 값 객체에 담는다.
             「DTO 가 아니라 값 객체다 — 그 질의가 도메인 특유이기 때문」

③ 도메인을 안 거치고 화면 자료를 빚는다
      Young      「Thin Read Layer」
      Millett·Tune 『PPPDDD』 26장 「Queries: Domain Reporting」</code></pre></div>
<b>①②는 리포지토리에 남고 ③만 나간다.</b> <code>NotificationRecordPage</code>·<code>CurrentUsageBuckets</code> 는 없애야 할 오분류가 아니라 <b>②에 이름이 있는 정당한 패턴</b>이었다.<br>
<b>Evans 는 이 칸이 잡았던 규칙 모양을 이름 들어 경고한다</b> — <em>「a non-object query such as mathematical summaries of selected objects. <b>Frameworks that don’t allow for such contingencies tend to distort the domain design or get bypassed by developers.</b>」</em><br>
<span class="dim">교훈은 R2·R3·R7 과 같다 — 규칙이 코드를 위반으로 찍으면 «예외를 어디 낼까»가 아니라 <b>«규칙 문장이 원전의 목적보다 넓거나 어긋나게 쓰였나»</b>를 먼저 본다.</span></dd>

<dt class="ans-dt">결정 ① 칸 — <b>가르는 축은 «주어가 그 애그리거트인가»</b></dt>
<dd class="ans-dd filled">
<div class="pre-wrap"><pre><code>domain_layer/&lt;aggregate&gt;/&lt;aggregate&gt;_repository.py      ①② 애그리거트를 꺼내고 넣는다
                                                            그 컬렉션을 세고 합친 요약값도 여기
port/domain_bypass_query/&lt;capability&gt;/             ③  도메인을 «우회»하는 조회의 계약  ← 신설
adapter/persistence/domain_bypass_query/&lt;cap&gt;.py   ③  그 구현 — Thin Read Layer     ← 신설</code></pre></div>
<b>«읽기냐 쓰기냐»도 «루트를 돌려주느냐»도 아니다.</b> 묻는 것은 하나 — <em>이 메서드의 <b>주어</b>가 그 애그리거트인가, 화면인가</em>. 그 애그리거트 얘기면 <b>반환형이 <code>bool</code> 이든 <code>int</code> 든 남고</b>, 화면이 필요해서 여러 애그리거트를 가로질러 표를 만드는 것만 나간다.<br>
<s><b>선언이 <code>port/</code> 가 아니라 <code>query_repository/</code> 인 이유</b> — 포트의 판정은 «바깥에 <b>행위자</b>가 있나»인데 <b>DB 는 바깥 행위자가 아니라 우리 저장소</b>다.</s> <b>08-08 · F6 에 이 근거가 무너졌다</b> — <b>Cockburn 의 2차 행위자 표준 예가 바로 DB·시계라 「행위자가 아니다」부터 원전 오독이었다</b>. 그 자로는 아무것도 안 갈렸고, 선언은 <code>port/domain_bypass_query/</code> 로 <b>들어갔다</b>. <b>D37</b> <b>「응용 계층에 둔다」는 결론은 그대로다.</b> <span class="dim">참조 구현 <b>둘</b>이 이 계약을 <b>응용 계층</b>에 둔다 — Microsoft eShopOnContainers <code>Application/Queries/</code> · Grzybek <code>Application/…QueryHandler</code>. 둘 다 SQL 까지 응용에 두는데, 우리는 전역 제약 ②(안쪽은 구체 기술을 모른다) 때문에 <b>구현만 한 칸 더 바깥</b>으로 민다.</span></dd>

<dt>이 자를 현행에 대면 <b>몇 개가 움직이나</b> <span class="dim">181 : 0 — 규칙의 근거가 아니라 이관 규모다</span></dt>
<dd>
<div class="pre-wrap"><pre><code>도메인 리포지토리 43개 · 공개 메서드 181     (옛 「187」은 틀렸다 — 사설 메서드 0)
   -&gt; None                     37   전부 쓰기            남는다
   값을 돌려주는 것           144
      시그니처에 도메인 어휘  136   ①②                  남는다
      원시 타입 반환            8
         원자 CAS 쓰기          5   쓰기는 우회 불가      남는다
         요약·식별자 조회       3   Evans 가 명시로 허용  남는다
                                    ───────────────────
                                    181 : 0</code></pre></div>
<b>지금은 나가는 것이 하나도 없다.</b> 이 저장소의 조회는 전부 애그리거트로 답이 나온다 — <code>port/domain_bypass_query/</code> 와 그 구현 칸은 <b>비어 있다</b>. 읽기 모델이 쓰기 모델과 갈라지는 순간 열린다.<br>
<span class="dim">옛 「나갈 11」은 전부 남는다 — <code>PricePeriod</code>·<code>CurrentUsageBuckets</code>·<code>NotificationRecordPage</code> 는 도메인 타입, <code>Collection[bool]</code> 은 인자가 <code>EffectivePeriod</code>·<code>LlmProvider</code>(도메인 값 객체), <code>UsageQuotaDecision</code> 은 <b>코드에 없다</b>.</span><br>
<span class="dim">반환형이 문제인 것 둘은 <b>자리가 아니라 이름</b>을 고친다(4번 ⓑ) — <code>attempts_summary -&gt; tuple[dict[str, Any], ...]</code> 와 <code>list_pending_…_ids -&gt; list[int]</code> 는 이름 붙인 값 객체를 줘야 한다.</span><br>
<span class="dim"><b>08-07 · 2차 리뷰 S5 — 이 「0」은 술어가 낼 수 있는 유일한 값이었다.</b> 위 표를 낸 기계 술어는 <em>「반환·인자 어노테이션에 원시·컨테이너가 아닌 식별자가 있으면 남는다」</em> 인데, <b>«나간다» 로 떨어지는 버킷이 구조적으로 없다</b> — 「이름 붙인 DTO 를 돌려준다」도 정의상 «도메인 어휘» 에 걸려 <b>남는 쪽</b>으로 센다. 그래서 0 은 «나갈 것이 없다»의 증거가 아니라 <b>«이 축은 기계가 못 센다»의 표시</b>이고, 위에 적은 대로 <b>축은 사람 판정</b>이라는 말과 같다. 「도메인 어휘 136」 버킷 중 <b>손으로 훑은 것은 20건</b>이다. <b>규칙은 이 수에 기대지 않으므로 결론은 안 바뀐다</b> — 수가 말하는 것은 이관 규모뿐이다.</span></dd>

<dt class="ans-dt">결정 ② 이름 — <b>새 폴더를 만들지 않는다</b></dt>
<dd class="ans-dd filled"><b>드리븐 쪽</b> 얘기다 — <code>driven_layer/read_model/</code> 을 만들려다 접고 <b><code>repository/</code> 안에 함께 둔다</b>. <code>&lt;capability&gt;.py</code> 는 <code>anticorruption_layer/</code>·<code>external_system/</code> 이 <b>이미 쓰는 이름</b>이라 규칙이 하나도 안 는다 — «선언 파일과 이름이 같다»가 세 번째로 적용될 뿐이다.<br>
<b>기각 근거는 D7 근거②</b> — <b>이 칸에 올 것이 지금 0개</b>다. 폴더를 따로 파면 <b>16개 BC 전부에 빈 폴더가 하나씩</b> 생긴다.<br>
<span class="dim">헷갈리지 말 것 — 기각한 것은 <b>드리븐의 <code>read_model/</code></b> 이고, 응용 쪽에 새로 만든 <code>port/domain_bypass_query/</code> 는 <b>«계약»의 자리</b>라 성격이 다르다. 구현은 <code>adapter/persistence/domain_bypass_query/</code> 에 온다.</span><br>
<span class="dim">치르는 값 — 한 폴더에 성격이 다른 둘이 산다(애그리거트를 아는 것 / 모르는 것). <b>파일 이름이 그 둘을 이미 가르고</b>(<code>&lt;aggregate&gt;_repository.py</code> vs <code>&lt;capability&gt;.py</code>), 아래 ③ 이 기계로 가른다.</span></dd>

<dt class="ans-dt">결정 ③ 화살표 — <b>폴더 대신 검사가 우회를 보장한다</b></dt>
<dd class="ans-dd filled"><b><code>adapter/persistence/domain_bypass_query/&lt;capability&gt;_query.py</code> 는 <code>domain_layer</code> 를 import 하지 않는다.</b> AST 로 판정된다. «도메인을 우회한다»가 <b>말이 아니라 검사</b>가 된다 — 폴더를 만드는 것보다 세다.<br>
<b>이 검사는 ③ 차선에만 건다.</b> ①②는 <b>도메인 어휘를 쓰는 것이 규칙</b>이라 같은 검사를 걸면 정반대를 잡는다 — 축과 검사가 <b>같은 말</b>이 되도록 맞춘 것이 R8 이 고친 것이다.<br>
나머지는 그대로다 — <code>&lt;aggregate&gt;_repository.py</code>(구현)는 <b>애그리거트와 ORM 모델을 동시에 아는 유일한 자리</b>다. <b>같은 폴더 안에서 두 파일의 앎이 정반대</b>인 것이 이 칸의 성질이다.</dd>

<dt class="ans-dt">결정 ④ 앎의 범위</dt>
<dd class="ans-dd filled"><b>Thin Read Layer 는 도메인을 모르고 ORM 을 안 거쳐도 된다.</b> 원전이 직접 허락한다 — «It is also <b>not necessarily bad to use stored procedures</b> for reading» · «Developers working on the Query side <b>do not need to understand the domain model</b>».<br>
대신 <b>바깥으로는 DTO 만 나간다</b> — ORM 로우도 <code>QuerySet</code> 도 응용에 넘기지 않는다. <b>D8</b> 의 «경계를 넘는 것은 단순 자료구조»와 같은 선이다.</dd>

<dt>덤 — <b>원전이 이름 들어 지목한 냄새가 우리 코드에 있다</b></dt>
<dd>«Large numbers of read methods on repositories <b>often also including paging or sorting information</b>» — 실측 <b>페이징·정렬 인자가 붙은 조회 12개</b>. 최악은 <code>LessonRepository</code> — <b>19메서드 전원이 값을 돌려주고 <code>-&gt; None</code> 이 하나도 없다</b>(<code>list_for_child(page=LessonListPage)</code>).<br>
<b>새 축으로 재면 12개가 전부 남는다</b> — 하나도 빠짐없이 <em>그 애그리거트의 컬렉션</em>을 훑는 것이라서다. <b>규칙과 냄새가 어긋나는 유일한 자리라 적어둔다</b> — 트리를 바꿀 일은 아니고 이관 때 다시 본다.</dd>
</dl>

## D28 · 쪼갠 조각은 어디 사나 — 두 칸을 실측이 갈랐다

**확정 · 08-06** · 자리 — ① 칸 &nbsp;·&nbsp; <code>application_layer/&lt;use_case&gt;/</code> &nbsp;·&nbsp; <code>domain_layer/domain_service/</code> &nbsp;·&nbsp; <b>대조에서 나온 첫 «칸 없는 코드»</b> &nbsp;·&nbsp; <b>②는 08-07 에 뒤집었다</b>

<dl class="kv">
<dt class="ans-dt">문제 — <b>실측에 있는데 트리에 자리가 없었다</b></dt>
<dd class="ans-dd filled">새 트리를 실측 폴더에 하나씩 대보니 둘이 갈 곳이 없었다.
<div class="pre-wrap"><pre><code>application_layer/&lt;area&gt;/service/     18파일   트리에 칸 없음
domain_layer/&lt;aggregate&gt;/domain_service/  43파일   트리는 BC 레벨 하나만</code></pre></div>
<b>둘 다 같은 자로 갈렸다</b> — <em>「몇 개가 나눠 쓰나」</em>. <code>schema_in/out</code> 과 <code>bc_error_schema</code> 을 가른 그 자다.</dd>

<dt class="ans-dt">① <code>service/</code> 18파일 — <b>새 칸이 필요 없었다</b></dt>
<dd class="ans-dd filled">
<div class="pre-wrap"><pre><code>유스케이스 «몇 개»가 이 파일을 쓰나
   0개  7파일   ← service 끼리만 부른다 = 아래 것들에 «딸린» 조각
   1개  8파일   ← 그 유스케이스 «전용»
   2개  2파일
   6개  1파일</code></pre></div>
<b>15/18 이 「한 유스케이스 전용」</b>이라 그 <code>&lt;use_case&gt;/</code> 폴더 안에 두면 된다. 나머지는 — 추상 6은 <code>application_layer/port/</code>(자리 있음) · <code>sync_llm_meta_defaults</code> 는 관리 명령이 부르니 <b>유스케이스로 승격</b> · <code>product_write_retry</code> 는 <code>OperationalError</code> 를 잡는 재시도라 <b><code>driven_layer</code> 로 내림</b> · <code>missed_lesson_transition</code> 1건만 6개가 공유한다.<br>
<b>「833줄 9클래스」가 실은 공개 하나였다</b> — <code>turn_streaming_service.py</code> 를 열어보니 <code>TurnStreamingService</code>(446줄, 공개 메서드 <code>run()</code> 하나) + <b><code>_</code> 로 시작하는 사설 클래스 8개</b>다. <b>공개 표면이 하나</b>라 트리의 「하나 = 파일 하나」와 같은 모양이고, 규칙을 어기지 않는다.</dd>

<dt class="ans-dt">이름을 짓지 않았다 — <b>계보에 없는 말이라</b></dt>
<dd class="ans-dd filled">한때 <code>&lt;collaborator&gt;.py</code> 라는 행을 만들려 했다. <b>클린 아키텍처를 조사하고 접었다</b> — 유스케이스 계층에 이름 붙은 역할은 <b>넷뿐</b>이다:
<div class="pre-wrap"><pre><code>Interactor              유스케이스 구현        →  &lt;use_case&gt;_use_case.py
Input/Output Boundary   경계 인터페이스        →  port/&lt;capability&gt;/&lt;capability&gt;.py
Request/Response Model  경계를 넘는 자료구조    →  &lt;use_case&gt;_{command|query}.py · _result.py
Data Access Interface   출력 포트             →  &lt;aggregate&gt;_repository.py</code></pre></div>
<b>「인터랙터가 위임하는 조각」에는 이름이 없다.</b> 원전은 <em>「여러 유스케이스를 한 인터랙터에 섞으면 SRP 위반」</em> · <em>「데이터 접근이면 Repository 로, 재사용 행위면 평범한 클래스로 추출」</em>까지만 말하고 <b>그걸 뭐라 부르라고는 안 한다</b>. <b>D9</b> 가 <em>「원전 패턴 이름은 풀어 쓴다 — 계보 어휘라 정확도가 값이다」</em>라고 한 자리에 <b>없는 말을 지어 넣을 수는 없다</b>.<br>
<b>그래서 행이 아니라 노트 한 문장</b>이다 — <em>「쪼갠 모듈도 이 안에 둔다. 둘 이상의 유스케이스가 쓰면 위로 올린다」</em>. 「진입점 하나」가 이미 제약이라 파일이 늘어도 규칙은 지켜진다. <b>D10</b> 의 「검사할 수 있는 데까지」다.</dd>

<dt class="ans-dt">② <code>domain_service/</code> — <b>두 층으로 갈랐다가 08-07 에 되물렀다</b></dt>
<dd class="ans-dd filled">트리는 BC 레벨 하나만 뒀는데 <b>실측 43개가 전부 애그리거트 밑</b>이었다. 「그럼 다 올리면 되지」가 답인지 재봤다 — <em>이 파일이 몇 개 애그리거트를 import 하나</em>:
<div class="pre-wrap"><pre><code>자기 애그리거트만        37   ← 주인이 «있다»
남의 것도 건드림          6   ← 주인이 «없다»
     accounts/family/household_membership_service      → child · family · parent
     ai_chat/…/transcript_assembler                    → conversation_item · room · turn
     llm_meta/…/assignment_catalog_conformance         → catalog_entry · model_assignment
     usage_quota/…/member_usage_share_calculator       → family_usage_quota · usage_reservation</code></pre></div>
<b>37 을 BC 레벨로 올리면 「어느 애그리거트 것인가」가 사라진다.</b> 그리고 <b>이 칸에 원래 붙어 있던 문구가 그대로 판정 기준</b>이었다 — <em>「주인이 없는 규칙」</em> = <b>「남의 애그리거트를 건드리나?」</b>. 37:6 이 그 선을 정확히 지지한다.<br>
플러그인도 둘 다 갖고 있다(<code>&lt;aggregate&gt;/domain_service/</code> [선택] + 「여러 애그리거트에 걸치면 공용 위치로」).</dd>

<dt class="ans-dt">08-07 · R10 — <b>되물렀다. 한 칸이다</b></dt>
<dd class="ans-dd filled"><b>이 결정이 판정 축을 잘못 골랐다.</b> 「몇 개 애그리거트를 import 하나」로 갈랐는데, 참조 구현 넷을 펴 보니 <b>갈림길은 그게 아니라 «누가 부르나»</b> 였다.
<div class="tw"><table class="pairtbl"><thead><tr><th>구현</th><th>애그리거트별 폴더</th><th>도메인 규칙의 자리</th><th><b>누가 부르나</b></th></tr></thead><tbody>
<tr><td>dddsample-core <span class="dim">Citerus · Evans 감수</span></td><td>✅</td><td class="mono">domain/service/ <b>BC 레벨 하나</b></td><td>응용</td></tr>
<tr><td>IDDD_Samples <span class="dim">Vernon</span></td><td>❌ 모듈에 평평</td><td class="mono">모듈에 나란히(5개)</td><td>응용</td></tr>
<tr><td>modular-monolith-with-ddd <span class="dim">Grzybek</span></td><td>✅</td><td class="mono">&lt;Aggregate&gt;/Rules/ <b>안</b>(27개)</td><td><b>애그리거트 자신</b></td></tr>
<tr><td>eShopOnContainers <span class="dim">Microsoft</span></td><td>✅</td><td>둘 다 없음 — 루트 메서드</td><td>—</td></tr>
</tbody></table></div>
<b>Grzybek 만 애그리거트 «안»에 두는데, 그건 애그리거트가 자기가 부르기 때문이다</b> — <code>Meeting.cs</code> 안에서 <code>this.CheckRule(new …Rule(...))</code> 이 8회 넘게 나온다. Evans 어휘로는 SERVICE 가 아니라 SPECIFICATION 쪽이다.
<b>응용이 부르는 도메인 서비스를 애그리거트 폴더 안에 넣은 참조 구현은 넷 중 0개다.</b></dd>

<dt>실측이 어느 쪽인지 <b>한 줄로 갈렸다</b></dt>
<dd><div class="pre-wrap"><pre><code>domain_service/ 공개 클래스 52 — 누가 import 하나

응용(유스케이스)이 직접 부른다        43   ← Evans 의 SERVICE
와이어링도 부른다(조립해 주입)             17
바깥 층이 부른다                       6
자기 애그리거트 «안에서만» 불린다        1   ← Grzybek 의 Rules/
아무도 안 부른다                       5   (죽은 코드 후보)</code></pre></div>
<b>43 : 1.</b> 우리 것은 Grzybek 의 <code>Rules/</code> 가 아니라 <b>Evans 의 SERVICE</b> 다. 그리고 Evans 의 SERVICE 는 dddsample 에서 <b>애그리거트 밖 폴더 하나</b>, Vernon 에서 <b>모듈에 평평</b>하다.<br>
<b>루트 메서드 후보는 0/52 였다</b> — 루트를 아예 안 받는 것 42 · 없거나 둘을 받는 것 6 · 컬렉션 1 · 애그리거트가 아닌 폴더 3. Evans 가 SERVICE 를 설명하며 든 말이 그대로다 — <em>「to put the “transfer” operation on Account is <b>awkward, since it involves two accounts and some global rules</b>」</em>.</dd>

<dt>이 결정의 <b>유일한 근거</b>도 실측이 지웠다</dt>
<dd>「37 을 BC 레벨로 올리면 <b>어느 애그리거트 것인가가 사라진다</b>」가 두 칸을 만든 근거였다. 재보니 <b>파일 이름이 이미 애그리거트 어휘를 담은 것이 32/45</b> 이고 안 담는 것은 <b>13</b> 뿐이다.
<b>이름 규칙 한 줄로 닫힌다</b> — <em>「도메인 서비스 파일 이름은 주어가 되는 애그리거트 어휘를 담는다」</em>. 폴더를 하나 더 여는 것보다 싸고, <code>&lt;aggregate&gt;_repository.py</code>·<code>&lt;entity&gt;_model.py</code> 가 이미 같은 수법이다.<br>
합쳤을 때 폴더 크기도 문제가 아니다 — <b>BC 당 중앙값 3 · 평균 3.5 · 최대 15</b>(report). Vernon 의 <code>identity/</code> 한 폴더보다 작다.</dd>

<dt>따라온 값 셋</dt>
<dd><b>⒜ <b>D13</b> 원안으로 돌아간다</b> — D13 결정① 이 «<code>&lt;aggregate&gt;/</code> 형제로 <code>domain_service/</code>» 라고 쓴 그대로다. 이 카드가 층을 하나 더한 것을 되무른 것뿐이다.<br>
<b>⒝ <code>ChatPipeline</code> 문제가 같이 닫힌다</b> — 두 자리가 하나면 «어느 애그리거트 것인가»를 물을 일이 없다. 검사① 도 예외 조항 대신 한 줄로 끝난다.<br>
<b>⒞ 빈 폴더 48개가 사라진다</b> — 위 「빈 폴더 154개」 표의 <code>domain_service/ 48폴더(빈 것 26)</code> 는 애그리거트 밑 폴더였다. 칸이 없어지면 통째로 없어진다.</dd>

<dt>치르는 값 — 정직하게</dt>
<dd><b>플러그인과 어긋난다</b> — 플러그인은 <code>&lt;aggregate&gt;/domain_service/</code> 를 [선택]으로 갖고 있다. <b>플러그인 쪽을 지운다</b>(적용 단계 9).<br>
<b>그리고 «이 규칙이 누구 얘기인가»가 폴더에서 이름으로 내려간다</b> — 검사 가능한 구조에서 이름 규칙으로 약해지는 것이 맞다. 다만 13개는 <b>지금 이름부터 고쳐야</b> 한다.</dd>

<dt>남은 것 — 대조 때</dt>
<dd><code>service/</code> 18파일 재배치 · <code>domain_service</code> <b>52개 전부</b>를 BC 레벨로 이동(+ 이름에 애그리거트 어휘 없는 <b>13개</b> 개명 · 아무도 안 부르는 <b>5개</b> 확인) · <code>product_write_retry</code> 를 <code>driven_layer</code> 로. 그리고 <b><code>turn_event_subscription</code> 을 입구가 2건 부른다</b> — <b>D11</b> 위반(「<code>driving_layer</code> 는 <code>application_layer/port/</code> 를 import 하지 않는다」).</dd>
</dl>

## D27 · 예외 — 세 자리가 이미 정해져 있었다 (플러그인 대조)

**확정 · 08-06** · 자리 — ① 칸 · ③ 화살표 &nbsp;·&nbsp; <b>새로 정한 게 아니라 «옮겨 적은» 결정</b> &nbsp;·&nbsp; 출처: 플러그인 <code>discipline-houserules</code> · <code>implementation-django-ninja</code>

<dl class="kv">
<dt class="ans-dt">① 칸 — <b>도메인 예외는 애그리거트 밑 파일 하나</b></dt>
<dd class="ans-dd filled"><b>트리가 이미 낸 답과 정확히 같았다.</b> <b>D12</b> 는 <code>exception/</code> <b>폴더</b>를 기각하면서 이렇게 적었다 — <em>「예외는 불변식 위반의 이름이고, 불변식의 주인은 애그리거트다」</em>. 그런데 <b>파일 행을 안 넣었다.</b> <span class="dim">08-09 · T42 — <b>앞 절이 좁았다</b>: 「이 값은 유일하다」·「내가 읽은 뒤 남이 바꿨다」처럼 <b>DB 가 대신 지켜 주는 업무적 사실</b>도 여기 산다. <b>결론(주인은 애그리거트)은 그대로</b>다(<b>D52</b>).</span> 플러그인은 같은 자리를 이미 <b>코어(필수)</b>로 못 박고 있었다:
<div class="pre-wrap"><pre><code>domain_layer/&lt;aggregate&gt;/
├ &lt;aggregate&gt;.py · entity/ · value_object/ · &lt;aggregate&gt;_repository.py
└ exception.py          ← 단일 파일 · 코어
                           check-layer-skeleton.py 가 없으면 blocker</code></pre></div>
<b><code>&lt;aggregate&gt;_repository.py</code> 와 같은 모양</b>이다 — 애그리거트당 하나라 폴더가 아니라 파일. 실측 <b>60파일 · 304클래스</b>가 이제 자리를 얻는다.<br><span class="dim"><b>08-08 · T28 — 이 한 줄이 뒤집혔다(<b>D40</b>).</b> 리포지토리는 애그리거트당 <b>하나</b>라 파일이 맞지만 <b>불변식은 여럿</b>이라, 같은 자(하나면 파일·둘 이상이면 폴더)를 대면 예외는 <b>폴더</b>가 된다. 아래 두 문단은 그때의 기록이다.</span><br>
<span class="dim"><b>08-07 · 2차 리뷰 S2 — 「(커지면 <code>exception/</code> 패키지)」를 지웠다.</b> 플러그인 원문에 있던 단서인데 <b>세 군데에 같은 말이 퍼져 있었고</b>(여기 · 트리 61행 규칙 · 61행 «이 칸에 오는 것») 전부 「나중에 그때」 형태다. <b>현행에 <code>exception/</code> 폴더는 0개</b>이고, 가장 큰 파일 16클래스 중 <b>8이 이 칸에 있으면 안 되는 것</b>이었다(아래 재판정). <b>규칙은 「폴더가 아니라 파일」 하나로 끝난다</b> — 길어지면 애그리거트를 본다. <b>← 이 줄이 D40 에서 뒤집혔다.</b> 지웠어야 할 것은 <b>「나중에 그때」라는 조건</b>이었고, 「길어지면 애그리거트를 본다」는 자는 그대로 살아 <b>«파일 수»</b>가 됐다.</span><br>
<b>08-06 보강(R4) — 예외의 자리가 둘이 아니라 셋이다.</b> 이 카드는 «애그리거트 불변식»과 «BC 경계 계약» 둘로만 닫았는데,
<b>바깥이 죽는 방식</b>에는 자리가 없었다. <b>D14</b> 가 하나를 더 열었다.
<div class="pre-wrap"><pre><code>domain_layer/&lt;aggregate&gt;/exception.py              업무 규칙을 어겼다     ← 이 카드 ①
open_host_service/…/contract/exception/            남에게 공개하는 실패   ← 이 카드 ②
application_layer/port/&lt;capability&gt;/exception.py   바깥 행위자가 죽었다   ← 신설</code></pre></div>
<b>셋째는 도메인 예외를 상속하지 않는다</b> — 「업무 규칙을 어겼다」와 「바깥이 죽었다」가 같은 <code>except</code> 에 걸리면
상태 코드도 재시도 정책도 갈리지 않는다.<br>
<b>«저장»이 실패하는 방식에는 넷째 자리를 두지 않았다</b> — 리포지토리는 «메모리 컬렉션의 착각»이라 <b>바깥 행위자가 아니고</b>,
실패가 <em>업무 의미가 있는 것</em>(→①) · <em>그 밖</em>(→선언 안 함 · 미식별 500) 둘로 갈려 <b>중간이 없다</b>. <b class="dim">※ 08-09 · T42(<b>D52</b>) — 옛 문장은 가운데에 <b>「재시도 판정 → <code>framework/</code>」</b> 를 두었는데 <b>세 가지를 한 낱말에 뭉친 것</b>이었다: <b>「일시적인가」를 «가르는» 것은 그 기술을 아는 어댑터</b>, <code>framework/</code> 는 재시도 <b>«기계»</b>, <b>«다시 부를지»는 입구</b>. 그래서 이 자리에 남는 갈래는 둘이다.</b>
그래서 ③의 <em>「폴백은 도메인·응용 base 단위 catch」</em> 에서 «응용 base» 는 <b>포트 실패의 기저</b>를 가리킨다.<br>
<b>실측이 두 층으로 갈려 있던 것</b>(BC 바로 밑 <b>12파일·16클래스</b> + 애그리거트별 <b>48파일·288클래스</b>)은 <b>표준이 아니라 표류</b>다 — 표준은 애그리거트 밑 하나뿐이다. <span class="dim">08-07 정정 — 옛 갈래 「11 + 44」는 합이 60 이 안 됐다. HEAD 재측정으로 12 + 48 = 60 · 16 + 288 = 304 로 맞춘다.</span></dd>

<dt>이 자를 가장 큰 파일에 대 보면 — <b>절반이 여기 있으면 안 되는 것</b> <span class="dim">08-07 · 2차 리뷰 S2</span></dt>
<dd>「파일이 커지면 폴더로 쪼갠다」를 지우기 전에 <b>정말 큰지</b>를 봤다. 가장 큰 것이 <code>usage_quota/domain_layer/family_usage_quota/exception.py</code> <b>16클래스·88줄</b>인데, 위 표의 자로 하나씩 재면 —
<div class="pre-wrap"><pre><code>남는다 (애그리거트 불변식)                                              8
  InvalidFamilyUsageQuota · InvalidUsageActor · InvalidHeldTokenAmount
  UsageFamilyNotFound · UsageFamilyAccessDenied · UsageQuotaNoPlan
  UsageTopUpNoParentRecipient  …

나간다                                                                  8
  FamilyMembership{Unavailable,Internal}     타 BC 소스가 죽었다   → port/&lt;cap&gt;/exception.py
  FamilyUsageLimit{Unavailable,Internal}     타 BC 소스가 죽었다   → port/&lt;cap&gt;/exception.py
  UsageTopUpPublication{Retryable,Permanent} 발행이 죽었다         → port/&lt;cap&gt;/exception.py
  UsageQuotaRetryable                        어댑터가 가른다       → 이름은 안 남긴다
  UsageQuotaInternal                         그 밖                 → 선언하지 않는다</code></pre></div>
<b>파일이 커 보인 이유가 «불변식이 많아서»가 아니라 «다른 층의 실패가 섞여서»였다.</b> 같은 자를 <code>billing/payment</code>(15) 에 대면 <code>EntitlementGrant{Unavailable,PermanentlyFailed}</code> 둘이 나가고, <code>lessons/lesson</code>(15) 은 <b>거의 다 남는다</b> — 그 파일이 <b>61줄</b>이다.<br>
<b>그리고 <code>exception/</code> 폴더는 현행에 0개다</b> — 「커져서 폴더가 됐다」가 <b>한 번도 안 일어났다</b>. <span class="dim">보이는 <code>contract/exception/</code> 폴더들은 OHS 공개 실패(이 카드 ②)라 성격이 다르다.</span></dd>

<dt class="ans-dt">② 관문 — <b><code>contract/exception/</code> 는 서비스 스코프이고 기저가 하나다</b></dt>
<dd class="ans-dd filled">「이름 겹침은 작은 미결」로 남겨 뒀던 칸을 플러그인이 이미 닫아 놨다.
<div class="pre-wrap"><pre><code>contract/exception/
├ &lt;service&gt;_published_error.py   서비스당 기저 하나 — 나머지가 전부 상속(중간층 경유 허용)
└ &lt;exception&gt;.py                 예외 클래스당 1모듈
연산 축이 아니라 «서비스» 스코프 — request/response 는 연산당 1파일인데 여기만 다르다</code></pre></div>
<b>08-07 · F4 — 여기 「기저가 하나인 이유는 소비자다(한 줄로 가족 전체를 잡을 수 있어야)」라고 써 있었다. 이유를 바꿨다.</b> 그건 <b>편의</b>라 「전체를 한 줄로 잡을 거면 갈래를 왜 나눴나」에 못 버틴다. <b>기저는 부르는 쪽이 칠 «마지막 그물»이다</b> — 구체 타입 열거는 <b>이쪽 코드가 안 바뀌었는데 저쪽에 예외가 늘면 낡고</b>, 그러면 새 예외가 ACL 을 통과해 조용히 500 이 된다. 기저가 없으면 그물이 <code>except Exception</code> 뿐인데 그건 내 버그까지 삼킨다. <b>D36</b> 가 이걸 <b>ACL 쪽 검사</b>로 세웠다.<br>
<b>③ 화살표 — 도메인 예외를 raw 로 전파·재노출하지 않는다.</b> <code>__all__</code> 재노출도 금지다. 재노출하면 소비 BC가 우리 <code>domain_layer</code> <b>타입 정체성에 결합</b>해 published language 경계가 무력화된다. 번역은 <b>알려진 구체 예외의 전수 명시 매핑</b>으로 하고, <b>폴백을 «둘 경우»</b> 도메인·응용 base 단위 catch 로 한정한다(<code>except Exception</code> 금지 — 프로그래밍 오류는 raw 전파가 정상).<br>
<span class="dim"><b>08-07 · 2차 리뷰 S11</b> — 옛 문장은 <em>「폴백은 … 한정한다」</em> 라 <b>폴백이 필수인 것처럼</b> 읽혔다. 플러그인 원문은 <em>「폴백을 «둘 경우» … 한정하며」</em> 로 <b>조건절</b>이고, 조문의 뜻은 «폴백을 두라» 가 아니라 <b>«둔다면 그 범위를 넘지 마라»</b> 다. 전수 명시 매핑만으로 닫히면 폴백은 없어도 된다.</span></dd>

<dt class="ans-dt">③ HTTP 표면 — <b>두 자리, 그리고 전역 핸들러 금지</b></dt>
<dd class="ans-dd filled">
<div class="pre-wrap"><pre><code>공통  framework/ninja/framework_error_schema.py   ErrorSchema — 첫 HTTP BC 부터 쓴다
BC    driving_layer/api/bc_error_schema.py       BC 당 «정확히» 한 파일 · 항상</code></pre></div>
<b>여기가 이번 대조의 최대 수확이다</b> — 플러그인은 <b>전역 예외 핸들러를 이미 금지</b>하고 있었다:
<div class="pre-wrap"><pre><code>&lt;project&gt;/api.py   API 인스턴스 1개를 «소유» 만 한다
                   금지: BC controller/registrar import · exception 매핑 · ErrorSchema 정의·생성
framework 오류     401·403·404·422·429·HttpError·미식별 500 은 framework 가 소유한다
                   전역 handler 나 catch-all mapper 로 «가로채지 않는다»
controller         짧은 exception→concrete ErrorSchema 매핑을 «직접» 소유한다
                   helper·factory·serializer·handler 등록 decorator·global mapper 금지
                   여러 controller 의 짧은 반복은 «이 명시성을 위해» 허용한다
                   보는 것은 예외의 «타입»뿐 — 속성을 읽지 않는다 (08-07 · F1 · D11)</code></pre></div>
<b><b>D25</b> 가 <code>api.py</code> 에서 찾아낸 것이 정확히 이 금지의 위반이다</b> — 도메인 예외 92개 목록 · 핸들러 20개 · <code>_DOMAIN_PROBLEMS</code> 81행. <b>규칙은 이미 있었고 구현이 안 따라갔다.</b><br>
<b>OpenAPI 도 같다</b> — <em>「오류 응답 선언을 <code>openapi_extra</code> 로 보충하거나 <code>get_openapi_schema</code> override · monkeypatch · postprocessor 로 사후 변형하지 않는다」</em>. <code>response={status: &lt;Bc&gt;ErrorSchema}</code> 으로 <b>operation 이 직접 선언</b>한다.</dd>

<dt class="ans-dt">플러그인 경로와 어긋나던 셋 — <b>둘을 닫았다</b></dt>
<dd class="ans-dd filled">플러그인 하우스룰은 이 경로들을 <b>「rename·move·대체하지 않는다」</b>고 못 박았고, 트리 개편이 셋을 건드렸다. <b>둘은 트리 어휘로 받았다.</b>
<div class="pre-wrap"><pre><code>            플러그인 (현행 계약)                  →  이 트리
공통 오류    common/ninja/response/error_out.py      framework/ninja/framework_error_schema.py  닫힘
                                                    common→framework · response/ 제거(D24)
BC 오류      presentation_layer/schema/error_out.py  driving_layer/api/bc_error_schema.py  닫힘
등록         presentation_layer/registrar.py         api/api_router.py               방식만 받음
                                                    이름은 트리 · 플러그인을 나중에 고친다</code></pre></div>
<b>BC 오류가 <code>schema/</code> 밑이 아니라 <code>api/</code> 바로 밑 파일인 이유</b> — 플러그인은 <b>「BC 당 정확히 한 파일」</b>인데 이 트리의 <code>schema/</code> 는 <code>&lt;area&gt;/</code> 밑이라 BC 레벨이 없다. <code>&lt;area&gt;/</code> 옆에 <code>schema/</code> 를 두면 <b>종류가 개념과 나란히 와 §0-4 를 깬다</b>. <b>하나뿐이면 폴더가 아니라 파일</b>이 이 트리의 답이고(선례 <code>unit_of_work.py</code> — <em>「BC 당 하나 · 그래야 찾을 수 있다」</em>), <code>api/</code> 바로 밑 파일 선례도 이미 있다(<code>&lt;bounded_context&gt;_api_router.py</code>).<br>
<b>area 밑으로 내리는 안은 «같은 오류 언어를 여러 번 다시 선언하게 되어» 접혔다</b> — 그 횟수를 실측이 말한다: 상태코드가 몇 개 area 에 걸치는지 세니 <b>401 은 23개 전부</b>, 422 는 20개, 503 은 19개다. area 마다 두면 <b>같은 오류 언어를 스물세 번 다시 선언</b>하게 된다. <span class="dim"><b>08-07 정정</b> — 옛 값 「13개 area 전부 · 422 는 11 · 503 은 9」에서 <b>13 은 area 수가 아니라 BC 수</b>였고 11·9 는 어느 단위로도 재현되지 않았다. HEAD 재측정(컨트롤러 파일 23개 기준): 401 23/23·BC 13 · 422 20/23·BC 10 · 503 19/23·BC 12. <b>방향은 논거를 강화한다.</b></span> 플러그인 백스톱도 BC 경로를 하드코딩하고(<code>application/&lt;bc&gt;/…/error_out.py</code>) <b>「second ErrorCode 컨테이너」를 차단</b>한다.<br>
<b>이름은 <code>error_out.py</code></b> — <code>schema_error_out.py</code> 를 검토하고 접었다. <b>이 트리에서 접두는 「내가 속한 곳」을 말한다</b>(<code>&lt;bounded_context&gt;_api_router</code>·<code>&lt;aggregate&gt;_repository</code>·<code>&lt;area&gt;_controller</code>·<code>command</code>·<code>schema_in</code> — 전부 자기 부모·조상 폴더 이름). <code>api/</code> 밑에서 <code>schema_</code> 를 달면 <b>자기가 안 사는 옆 폴더</b>를 가리켜 읽는 사람이 <code>schema/</code> 안을 찾는다. 그리고 지금 <b>「같은 접두 = 같은 스코프」</b>가 지켜지는데(<code>dto_*</code> 는 유스케이스당, <code>schema_*</code> 는 area 당) <code>schema_error_out</code> 은 <b>접두는 같은데 스코프가 다른 첫 사례</b>가 된다 — 이름이 <b>70/70 대 23/23</b> 의 차이를 지운다. <em>자리가 <code>schema/</code> 안이었다면 그 이름이 맞았다 — 이름이 나쁜 게 아니라 자리가 거기가 아니다.</em>
<span class="dim"><b>08-09 · T53 정정</b> — <b>논거는 그대로 살아 있고 결론만 바뀐다</b>. 여기서 접은 것은 <b>접두</b> <code>schema_error_out.py</code> 였고, 그 금지는 지금도 유효하다.
바뀐 것은 <b>접미</b>다 — <code>error_schema.py</code>. <code>_out</code> 은 이 트리에서 <b>«쌍의 한쪽»</b>을 뜻하는데 <b>이 파일만 짝이 없어 그 접미사가 아무것도 안 말했고</b>, 종류를 말하는 접미사가 그 자리를 대신한다.
규칙으로는 <b><code>schema/</code> 폴더 «안»이면 접두, «밖»이면 접미</b>다.</span><br>
<b>셋째 — 등록.</b> 이름만 다른 게 아니라 <b>등록 방식이 달랐고, 값은 방식에 있었다</b>. <b>방식은 받는다</b>(<code>def register_&lt;bc&gt;_api(api)</code> · <code>auto_import=False</code> · <code>urls.py</code> 명시 호출) — 자세한 건 <b>D6</b>. <b>이름과 자리는 트리를 따른다</b>: <code>driving_layer/api/api_router.py</code>. 자리는 <b>등록 대상이 전부 HTTP</b>라서다 — 실측 13파일이 등록하는 건 <code>register_controllers</code> 15건 + Django <code>urlpatterns</code> 2건뿐이고, <code>open_host_service/</code>(타 BC 가 함수를 직접 부름)와 <code>cron_job/</code>(celery 가 경로로 찾음)은 <b>등록 함수가 없다</b>. <code>driving_layer/</code> 밑에 두면 「다른 입구도 여기서 등록하나」라는 <b>안 쓰이는 여지</b>가 생긴다(규율 ⑤).<br>
<b>그래서 플러그인 쪽을 고쳐야 한다</b> — 경로 계약 셋 중 둘은 트리 어휘로 받았고 하나는 이름이 갈렸다. <b>구현에 들어갈 때 플러그인 문서·백스톱을 트리에 맞춘다.</b> 대조(P1~P12)의 항목이다.</dd>

<dt>딸려 닫힌 것 — <code>_v1</code> 접미사</dt>
<dd>「<code>contract/exception/</code> 72개 중 55가 <code>_v1</code>」을 작은 미결로 두고 있었다. 플러그인 규칙은 <b>예외 클래스당 1모듈 · 파일명은 주 클래스명 snake_case</b>이고 <code>_v1</code> 조항이 없다 — <b>표준이 아니라 표류</b>다. 대조 때 걷는다.</dd>

<dt>출처</dt>
<dd><code>dddjango/skills/discipline-houserules/references/final.md</code> §0·§2 · <code>implementation-django-ninja/references/final.md</code> §6.2 · 결정적 백스톱 <code>check-layer-skeleton</code>·<code>check-error-centralization</code>·<code>check-api-error-controller-contract</code>·<code>check-catch-all-handler</code>·<code>check-openapi-error-declaration</code>·<code>check-synthetic-infra-exc</code>·<code>check-transient-overmapping</code>. 커밋 <code>5a87b2f</code>→<code>4a3c838</code>.</dd>
</dl>

## D26 · cron_job/ — 세 번째 입구. 규칙은 새로 쓸 게 없었다

**확정 · 08-06 · 08-07 R10 ⒞** · 자리 — ① 칸 · ② 이름 · ③ 화살표 · ④ 앎의 범위 &nbsp;·&nbsp; <code>driving_layer/</code> 의 셋째 칸 &nbsp;·&nbsp; <b>실측할 현행이 없는 유일한 칸</b>

<dl class="kv">
<dt class="ans-dt">① 칸 — <b><code>driving_layer/</code> 안, <code>api/</code>·<code>open_host_service/</code> 와 나란히</b></dt>
<dd class="ans-dd filled">셋의 성질이 같다 — <b>밖에서 나를 부른다</b>.
<div class="pre-wrap"><pre><code>api/                HTTP 요청이 부른다
open_host_service/  타 BC 가 부른다
cron_job/           celery 워커가 부른다</code></pre></div>
<b>경로 강제가 없어서 여기 둘 수 있다</b> — Django 관리 명령은 <code>&lt;app&gt;/management/commands/</code> 를 강제하지만 celery 는 <b><code>autodiscover_tasks(packages=…)</code> 로 우리가 정한다</b>. <span class="dim"><b>08-07 · R10 정정</b> — 옛 문장은 «<code>related_name</code>·<code>imports</code> 로 정한다»였는데 <b>둘 다 틀렸다</b>. 원전 확인: Django fixup 이 넘기는 package 는 <code>[config.name for config in apps.get_app_configs()]</code>(<code>celery/fixups/django.py</code>)라 우리 트리에선 <code>application.&lt;bc&gt;.driven_layer.django_&lt;bc&gt;</code> 이고, <code>find_related_module</code> 이 <code>import_module(f"{package}.{related_name}")</code> 를 부르니 <b><code>driving_layer/</code> 로 «위로» 못 올라간다</b>. <code>imports=</code> 는 모듈 전체 경로를 나열하는 것이라 <b>D25</b> 의 «규칙이 아니라 목록» 병이다.</span> <b>D22</b> 에서 이게 답을 뒤집은 지점이었다.<br>
<b>하위 폴더 없이 파일 하나씩</b> — 실측 3개가 각각 22~44줄에 유스케이스 하나만 부른다. 선례 <code>driven_layer/unit_of_work.py</code>. 접미사도 안 붙인다(폴더가 이미 종류를 말했다 — <code>entity/&lt;entity&gt;.py</code> 와 같은 규칙).</dd>

<dt class="ans-dt">② 이름 — <b><code>celery/</code> 가 아니라 <code>cron_job/</code></b></dt>
<dd class="ans-dd filled"><b>폴더는 역할, 기술은 그 안에.</b> 이게 이미 이 트리의 규칙이고 <code>api/</code> 가 그대로 그렇다 — 클래스는 <code>TurnController</code>·<code>PairingController</code>(역할)인데 <b>22개 파일 전부가 ninja 를 직접 import</b> 한다(기술이 안에 있다).<br>
<b>정직한 값</b> — <code>cron</code> 은 엄밀히는 Unix 프로그램 이름이고 celery beat 는 cron 이 아니다. 다만 k8s 가 <code>CronJob</code>, GitHub Actions 가 <code>schedule: cron:</code> 을 쓸 만큼 <b>「주기 실행」의 보통명사</b>가 됐고, <code>api/</code> 가 특정 프레임워크 이름이 아닌 것과 같은 층위다. 그리고 <b>실측 3개가 전부 주기 배치</b>라 정확히 맞는다.<br>
<b>주기가 아닌 비동기 작업(응답에서 떼어내는 발송 같은)이 생겨도 칸은 안 는다</b> — ① 이 세운 축은 «주기냐»가 아니라 <b>«누가 나를 부르나»</b> 이고(<code>api/</code> HTTP · <code>open_host_service/</code> 타 BC · <code>cron_job/</code> celery 워커), 비주기 작업도 <b>부르는 것은 같은 celery 워커</b>다. 이름이 좁게 들리는 것은 바로 위에 적은 <b>«정직한 값»</b> 이지 칸이 갈릴 이유가 아니다. <b>그 task 가 껍데기를 넘어 조율을 시작하면</b> 그건 새 칸이 필요한 게 아니라 <b>D11</b>(입구에 로직 금지) 위반이다.<br>
<span class="dim"><b>08-07 · 2차 리뷰 S2</b> — 옛 문장은 <em>「그때 칸을 하나 더 연다」</em> 였고 근거로 <code>framework/test/</code> 의 <em>「두 번째 BC 가 같은 걸 만들면 그때 올린다」</em> 를 달았다. <b>둘 다 죽었다</b> — ⑴ 「나중에 그때 연다」로 끝나는 문장은 <b>그 자체가 결함</b>이라고 R13 이 못 박았고 <b>같은 카드 아래 «통합 이벤트 칸» 절이 이미 정반대를 결론냈다</b>(«입구 셋이 그대로 다 받는다» · «그때는 칸이 아니라 D11 위반을 고칠 때») — R13 이 아랫절만 고치고 이 문장을 안 지웠다. ⑵ 근거로 든 그 승격 게이트도 <b>08-07 · R11 에 «BC 하나를 지우면 바뀌나» 로 갈렸다.</b></span></dd>

<dt class="ans-dt">③ 화살표 — <b>타 BC 를 모른다.</b> 그런데 <em>새로 쓸 게 없었다</em></dt>
<dd class="ans-dd filled"><b><b>D11</b> 이 이미 답했다</b> — <code>application_layer/&lt;area&gt;/</code> 아래만. 칸이 기존 규칙에 그냥 들어맞는 건 <b>잘 놓였다는 신호</b>다.<br>
<b>이유는 「필요 없다」가 아니라 「이미 그 길이 있다」</b> — 실측 <code>application_layer</code> 가 타 BC 를 직접 import 한 건수 <b>0건</b>. 살아있는 예가 바로 이 칸에 들어올 배치다:
<div class="pre-wrap"><pre><code>send_due_lesson_reminders_command.py  (lessons)   자녀 기기 발송 = delivery BC 일
  _SendLessonReminder = Callable[..., None]        ← 포트로만 잡는다
  # application 은 delivery 를 직접 import 하지 않는다   ← 코드 주석이 스스로 말한다
composition_root  →  send_lesson_reminder 어댑터를 꽂는다  →  어댑터가 넘어간다</code></pre></div>
<b><code>api/</code> 가 같은 선례다</b> — 컨트롤러가 자기 BC 밖을 import 하는 27건은 <b>전부 인증</b>이고 <b>D24</b> 가 이미 없앴다(틀은 <code>framework/</code>, 해석은 관문). 적용 후 0건. <b>입구 셋이 같은 규칙을 쓴다.</b></dd>

<dt class="ans-dt">④ 앎의 범위 — <b>재시도를 모른다</b></dt>
<dd class="ans-dd filled">지금 배치 3개가 전부 <b>「다음 주기가 재시도한다」</b>를 전제하는데(코드 주석 6곳) <b>스케줄러가 저장소에 없다</b> — 실패한 리마인더는 영영 안 나간다(<b>D22</b> 가 남긴 구멍).<br>
<b>celery beat 가 「주기」를, celery 가 「재시도」를 갖는다 — 둘 다 설정이지 코드가 아니다.</b> <code>cron_job/</code> 이 재시도를 알면 <b>로직이 생겨</b> D11 을 어긴다(22줄 껍데기가 재시도 루프를 갖게 된다). 멱등성은 이미 유스케이스가 갖고 있다 — <em>「재실행은 멱등이라 두 번째 실행 count 는 0」</em>. <b>celery 도입이 구멍을 메우고 트리는 안 바뀐다.</b></dd>

<dt class="ans-dt"><b>통합 이벤트 칸은 만들지 않는다</b></dt>
<dd class="ans-dd filled">한때 celery 와 한 칸으로 묶을지가 열려 있었다(둘 다 「메시지가 나를 부른다」). <b>실측이 닫았다</b>:
<div class="pre-wrap"><pre><code>브로커(kafka·pika·rabbitmq·sqs·kombu)   설치 0 · 코드 0
통합 이벤트                              0건
도메인 이벤트 8개                        ← 있다. 그런데 구독자가 0건</code></pre></div>
<b>08-07 · R13 — 근거를 갈아끼웠다. 결론은 그대로고 이유가 반대다.</b> 옛 문장은 <b>규율 ⑤</b> 를 들고 <em>「브로커가 실제로 들어오면 그때 넷째 칸을 연다」</em> 로 끝났다. <b>두 군데가 틀렸다</b> — ⑴ 실측 0 을 근거로 미루는 것이라 <b>규율 ① 과 부딪히고</b>(R10 에서 같은 논법이 뒤집혔다), ⑵ <b>«커버 안 된 상황을 남겨두는 문장»</b> 이라 이 트리의 목표와 어긋난다. 그리고 <b>지위가 다르다는 말도 틀렸다</b> — celery 를 도입하면 브로커(redis·rabbitmq)가 <b>같이 들어온다</b>.<br>        <b>새 근거 — 「지금 안 쓰여서」가 아니라 «넣을 것이 없어서»다.</b> <b>D34</b> 가 BC 사이를 오가는 메시지의 <b>조각 다섯을 하나씩 짚었고 전부 기존 칸에 들어간다</b> — 보내는 쪽 <code>application_layer/port/&lt;capability&gt;/</code> + <code>uow.after_commit(…)</code>(<b>D31</b>) + <code>driven_layer/anticorruption_layer/&lt;bc&gt;/</code>, 받는 쪽 <code>driving_layer/open_host_service/</code>. <b>실측 0 과는 다른 종류의 근거다.</b><br>        <b>celery 가 들어와도 안 바뀐다</b> — 같은 알림을 비동기로 보내게 되면 받는 쪽은 celery task 인데, 그 task 는 <code>open_host_service/</code> 를 부르는 <b>얇은 껍데기</b>다. <code>cron_job/</code> 이 유스케이스를 부르는 것과 <b>같은 모양</b>이고, 그래서 <b>입구 셋이 그대로 다 받는다</b>.<br>        <b>넷째 칸이 정말 필요해지는 조건은 따로 있다</b> — 소비 task 가 <b>껍데기를 넘어 조율을 시작할 때</b>다. 그런데 그건 <b>D11</b>(입구에 로직 금지)이 <b>이미 막는다</b>. <span class="dim">즉 「그때 연다」가 아니라 <b>「그때는 칸이 아니라 D11 위반을 고칠 때」</b> 다.</span></dd>

<dt>딸려 정해진 것 — <code>&lt;project&gt;/celery.py</code></dt>
<dd><code>Celery(...)</code> 인스턴스와 <code>autodiscover_tasks(...)</code> 는 <b>조립</b>이라 <b>D25</b> 의 칸으로 간다. 그 규칙(<b>「<code>application</code> 을 등록만 하고 타입으로 알지 않는다」</b>)을 그대로 통과한다 — <b>경로 문자열만</b> 쓴다.<br><b>08-07 · R10 — 인자를 정정했다.</b> 기본 호출로는 못 닿아서 <code>packages</code> 를 준다. 원전이 <em>「This argument may also be a callable, in which case the value returned is used」</em> · <em>「If <code>None</code> will only try to import the package」</em> 라고 둘 다 허용한다(<code>celery/app/base.py</code>).<div class="pre-wrap"><pre><code>autodiscover_tasks(
    packages=lambda: [f"application.{c.label}.driving_layer.cron_job"
                      for c in apps.get_app_configs() if c.name.startswith("application.")],
    related_name=None,
)</code></pre></div><b>목록이 아니라 규칙이라 <b>D25</b> 판정을 통과한다</b> — BC 이름이 한 개도 안 나온다. <b>이걸 가능하게 한 건 <b>D15</b> 의 검사 ④</b> 다: «<code>apps.py</code> 가 <code>label</code> 을 명시 선언하고 <b>그 값이 BC 폴더 이름과 같다</b>» — 그래서 <code>c.label</code> 하나로 <code>application/&lt;bounded_context&gt;/</code> 경로가 선다.<br>
<span class="dim"><b>08-07 · 2차 리뷰 S9 — 근거를 갈아끼웠다. 결론은 그대로다.</b> 옛 근거는 <em>「<code>label</code> 은 절대 안 바뀐다」</em> 였는데 <b>필요한 것과 다른 말</b>이다 — 이 람다가 서려면 «안 바뀐다»가 아니라 <b>«<code>label</code> == BC 폴더 이름»</b> 이어야 한다. 그리고 옛 D15 이행 규칙은 그 등식을 <b>깨는 쪽을 권했다</b>(「폴더만 바꾸고 <code>label</code> 은 옛 이름」). <b>D15 를 고쳐 등식을 정본으로 삼았고</b>(BC 이름이 바뀌면 둘을 같이 바꾼다), 이제 근거와 필요가 같은 문장이다.</span><br><b>딸려 나온 규칙 하나</b> — <code>cron_job/</code> 은 «패키지»라 <code>__init__.py</code> 가 <code>&lt;job&gt;</code> 들을 <b>재수출해야</b> <code>@shared_task</code> 가 등록된다. <span class="dim">이 재수출은 목록이지만 <b>BC 안의 목록</b>이라 D25 판정에 안 걸린다 — 그 BC 를 지우면 이 파일도 같이 사라진다.</span></dd>

<dt>전제를 적어 둔다</dt>
<dd><b>이 칸은 celery 도입을 전제한다.</b> 실측상 celery 는 설치 0 · 코드 0 이고, 근거는 <em>「cron 은 celery 쓰게 될 건데?」</em> 하나다. D22 가 <b>실측하지 않은 미래 변수에 통째로 뒤집힌</b> 적이 있어 여기 적어 둔다 — 도입이 무산되면 이 칸과 D22 의 「배치 3 → celery」가 같이 무너진다.</dd>
</dl>

## D25 · &lt;project&gt;/ — 조립 구역. 규칙을 목록으로 쓰면 여기가 열린다

**확정 · 08-05** · 자리 — ① 칸 · ② 이름 · ③ 화살표 &nbsp;·&nbsp; <code>broccoli_server/</code> &nbsp;·&nbsp; <b>트리 밖에 있던 두 번째 구역</b> <span class="dim">(첫째는 <b>D24</b>)</span>

<dl class="kv">
<dt class="ans-dt">① 칸 — <b>자리는 그대로 두고 규칙 하나를 건다</b></dt>
<dd class="ans-dd filled">파일 20개를 하나씩 판정했다. 판정 물음은 하나다 — <em>「BC 하나를 통째로 지웠을 때 이 파일이 바뀌나?」</em>
<div class="pre-wrap"><pre><code>안 바뀐다   settings/4개 · asgi · wsgi · health · home · test/5개    커밋 1~2회
바뀐다      api.py · urls.py · openapi_schema.py · response_policies.py</code></pre></div>
<b>깨끗하게 갈린다.</b> 그래서 자리를 옮기는 문제가 아니라 <b>둘째 줄이 첫째 줄이 되게 하는</b> 문제다.</dd>

<dt class="ans-dt">③ 화살표 — <b><code>application</code> 을 「등록」만 하고 「타입」으로 알지 않는다</b></dt>
<dd class="ans-dd filled">
<div class="pre-wrap"><pre><code>허용   urls.py 가 register_&lt;bc&gt;_api(api) 를 «명시 호출» 한다
금지   그 외 전부 — 부작용 등록(# noqa: F401) 포함        실측 위반 41건
       api.py 28(도메인 예외 92개) · urls.py 부작용 등록 11 · urls.py 심볼 2</code></pre></div>
<b>「추가 금지」로는 부족하다</b> — 지금 있는 41건이 그대로 남는다. <span class="dim">08-07 재측정 — 옛 43 에 들어 있던 <code>broccoli_server/test/</code> 2건은 커밋 <code>4febcbfe</code> 로 삭제됐다.</span> 그리고 <code>urls.py</code> 의 심볼 2건이 <b>두 BC 만 루트에 마운트</b>해서, 그걸 되돌리는 <code>get_paths</code> 오버라이드 20줄을 낳았다. 규칙 하나가 둘을 같이 잡는다.<br>
<b>08-06 정정</b> — 처음엔 <code># noqa: F401</code> 등록 import 11건을 <b>허용</b>으로 뒀다(「심볼을 안 쓰니 타입을 모른다」). 플러그인 대조에서 뒤집혔다 — 그건 <b>「숨은 import-side-effect 등록」으로 이미 금지</b>돼 있었고, <b>D6</b> 의 <code>register_&lt;bc&gt;_api(api)</code> 명시 호출이 그 자리를 대신한다. <em>「심볼을 안 쓴다」를 안전의 근거로 삼은 게 틀렸다 — 부작용은 심볼 없이도 일어난다.</em></dd>

<dt class="ans-dt">왜 이 구역이 열려 있었나 — <b>규칙을 목록으로 썼다</b></dt>
<dd class="ans-dd filled">이 저장소 741커밋에서 <code>api.py</code> 는 <b>5번째로 많이 바뀐 파일</b>이고, <b>38번 열린 것 중 BC 코드를 안 건드린 커밋이 0건</b>이다. 세 파일이 같은 병이었다.
<div class="pre-wrap"><pre><code>                      원래 규칙                    어떻게 썼나        결과
openapi_schema.py     모든 에러는 problem+json      주소 8개 목록     236 중 79 만 맞음
response_policies.py  모든 에러는 no-store          주소 2개 목록     13 BC 중 1개만
api.py                예외는 관문을 거친다          예외 92개 목록    관문 97개를 0번 씀</code></pre></div>
<b>목록은 빠뜨리고 규칙은 안 빠뜨린다.</b> 실측 대가 — 문서가 401 <b>61건 중 11건</b>, 503 <b>38건 중 13건</b>만 맞고, 에러 <b>157건</b>이 틀린 media type 으로 적혀 있다.</dd>

<dt class="ans-dt">그래서 <b>둘은 트리에 없다</b></dt>
<dd class="ans-dd filled"><code>openapi_schema.py</code> <b>403줄 — 통째로 소멸한다</b>. 죽은 코드 34줄(빈 dict 를 도는 기계) · <code>api.py</code> 테이블의 손복사본 46줄 · <code>get_paths()</code> 되돌리기 20줄 · 나머지는 <b>다 만들어진 dict 를 밖에서 주소로 찾아 고치는 후처리</b>다.
<div class="pre-wrap"><pre><code>① get_paths() 되돌리기   → 이 카드 ③ 규칙이 없앤다 (위 「규칙 하나가 둘을 같이 잡는다」)
② 예제·헤더·설명 덧대기   → 갈 자리가 «이미» 있다
                            예제 → Schema 자신(json_schema_extra)
                            헤더 → 컨트롤러가 소유 (플러그인이 이미 정했다)
                            설명·태그 → 데코레이터 인자(summary·description·tags)
③ 그 둘을 켜는 스위치     → ①② 가 없어지면 «켤 것»이 없다</code></pre></div>
<b>①②③ 은 스위치 하나에 매달려 있다</b> — <code>BroccoliOpenAPISchema</code> 도 <code>augment_openapi_schema</code> 도 <code>&lt;project&gt;/api.py</code> 의 <code>get_openapi_schema</code> <b>안에서만</b> 불린다. 하나가 꺼지면 <b>403줄 전체가 죽은 코드</b>가 된다.<br>
<span class="dim">08-09 · T41 — 옛 문장은 <em>「나머지는 <b>규칙 클래스 약 40줄</b>로 접힌다 … 접힌 클래스는 <code>framework/ninja/</code> 로 간다」</em> 였다. <b>접을 곳이 없다.</b> ninja 의 <code>get_schema()</code> 가 <code>OpenAPISchema</code> 를 <b>하드코딩</b>해서 서브클래스를 정의만 하면 <b>안 쓰인다</b>. 쓰이게 하려면 <code>NinjaAPI.get_openapi_schema</code> 를 override 해야 하는데 <b>그건 </b><b>D27</b> <b>이 이름 들어 금지한 것</b>이고, 플러그인이 <b>08-04 에 검사기로 못 박았다</b>(<code>check-openapi-error-declaration.py</code> — override · monkeypatch · setattr · 직접 호출·후처리 · <code>openapi_extra</code> 수동 선언). <b>「관문을 쓰면 236/236」은 «닿을 수 없는» 관문이었다.</b></span><br>
<code>response_policies.py</code> <b>30줄</b> — <b>소멸</b>. 「저장하지 마」는 두 주소의 사정이 아니라 <b>모든 에러의 규칙</b>이라 에러를 만드는 함수 안 <b>한 줄</b>이면 된다. 절반은 안 일어나는 일을 막고 있었다 — 이 앱은 <code>ETag</code>·<code>Last-Modified</code> 를 <b>만드는 코드가 0개</b>인데 지우고 있고, 테스트가 <b>직접 그 헤더를 넣어놓고</b> 지워지는지 본다.</dd>

<dt class="ans-dt"><b>08-09 · T41 — 딸려 나온 자: 「있어야 하나」와 「어떻게 쓰나」</b></dt>
<dd class="ans-dd filled">4차 리뷰(PY-1)가 <b>blocker</b> 로 올린 것 — <em>「이 카드가 «관문을 쓰자»고 하는데 그 관문에 닿는 길은 <b>D27</b> 이 금지한 둘뿐이다. 명세가 이대로 가면 <b>플러그인이 자기 규칙으로 자기 설계를 blocker 로 찍는다</b>」</em>. <b>지적이 맞고, 답은 «예외를 내는 것»이 아니라 «접지 않는 것»이었다</b>(위).
<br><b>그러면서 이름 하나가 트리에서 빠진다</b> — <code>framework/ninja/openapi_rule.py</code>. 그 자리에 있던 것이 <b>«규칙»이지 «코드»가 아니었기</b> 때문이다.
<div class="pre-wrap"><table class="mini">
<tr><th></th><th>트리가 정한다</th><th>스킬이 정한다</th></tr>
<tr><td><b>물음</b></td><td>그 파일이 <b>«있어야» 하나</b></td><td>그 파일을 <b>«어떻게 쓰나»</b></td></tr>
<tr><td><code>authentication.py</code> · <code>framework_error_schema.py</code></td><td><b>✔</b> 실제 코드가 사는 칸</td><td>작성법</td></tr>
<tr><td><code>openapi_rule.py</code></td><td><b>✗ 규칙이지 코드가 아니다</b></td><td><b>✔ 여기가 전부</b></td></tr></table></div>
OpenAPI 를 어떻게 쓰나는 <code>implementation-django-ninja</code> 가 <b>통째로 진다</b> — <code>response={status: Schema}</code> 로 «미리» 선언 · framework status(401·403·404·422·429·500)는 BC <code>ErrorOut</code> 으로 <b>광고하지 않음</b> · <code>summary</code>·<code>description</code>·<code>tags</code> 는 데코레이터 인자 · 후처리 금지. 그 스킬의 문장이 <em>「operation 의 <code>response=</code> 가 <b>runtime 과 OpenAPI 가 «함께 아는»</b> 계약이다」</em> 다 — <b>따로 손볼 자리를 두지 않는 것이 요지</b>다.
<br><b><code>framework/ninja/</code> 칸 자체는 남는다</b> — 빠지는 것은 <b>예시 이름 하나</b>뿐이고 <b>트리 행 변화는 0</b>이다. <span class="dim">이 자는 <b>D10</b> 의 「구현 판단은 트리가 정하지 않는다」를 <b>파일 단위로</b> 내린 것이다.</span></dd>

<dt class="ans-dt"><b>트리에 칸을 만들지 않는 것 셋</b></dt>
<dd class="ans-dd filled"><b><code>test/</code></b> — 실측 5개가 <b>전부 HTTP 로만 구동</b>해서 성질은 맞다. 그래도 안 만든다: <b>칸이 있으면 쓰게 되고, 그건 방금 건 규칙과 반대로 간다</b>. 그리고 여기 있던 건 죄다 <b>전역 규칙의 테스트</b>(에러 핸들러 · problem 계약 · 라우팅)라 <b>규칙이 <code>framework/</code> 으로 가면 테스트도 따라간다</b> — <code>framework/test/unit/</code> 이 이미 그 자리다.<br>
<b><code>health.py</code> · <code>home.py</code></b> — <b>개발자가 명시적으로 요청해서 들어간 것</b>이다. 도메인이 없어 BC 를 못 만들고, 표준 트리가 <b>모든 프로젝트에 요구할 것도 아니다</b>. 칸을 만들면 「여기는 아무거나 놓아도 되는 자리」가 된다.<br>
<b><code>asgi.py</code> · <code>wsgi.py</code></b> — Django 가 만들어 주는 것이라 정할 게 없다.<br>
셋 다 <b>D22</b> 의 <code>scripts/</code> 와 같은 취급 — <b>예외가 아니라 관할 밖</b>이다.</dd>

<dt>② 이름</dt>
<dd><code>broccoli_server</code> 는 <b>제품명</b>이라 트리에 그대로 못 쓴다 — <b>D24</b> 가 <code>broccoli/</code> 를 기각한 이유와 같다. <code>&lt;project&gt;/</code> 는 <code>django-admin startproject</code> 가 만드는 그 칸이고, <b>프로젝트마다 이름이 다른 자리</b>라 자리표시자가 맞다.</dd>

<dt>남은 것 — 대조 때</dt>
<dd>위반 32건을 걷는 일은 <b>계약 변경</b>이다(다른 12개 BC 의 에러 응답에 <code>no-store</code> 가 새로 붙고, 목록에 없던 상태를 검증하는 테스트 12건이 바뀐다). 채팅에서 손으로 고칠 게 아니라 <b>파이프라인을 탄다</b>.</dd>
</dl>

## D3 · 네 계층의 이름을 그대로 두나

**확정 · 08-04** · 자리 — ② 이름 &nbsp;·&nbsp; 닫는 문제 <b>P7</b> &nbsp;·&nbsp; <b>08-03 판단을 뒤집었다</b>

<dl class="kv">
<dt class="ans-dt">결정</dt>
<dd class="ans-dd filled"><b><code>presentation_layer/</code> → <code>driving_layer/</code>.</b> <em>이 칸만 정한다.</em> <code>infra_layer</code>의 이름은 <b>그 칸을 다룰 차례에</b> 정한다. <span class="dim">→ 08-05 에 <b>D16</b> 으로 닫혔다: <code>driven_layer/</code>.</span></dd>
<dt>왜 뒤집혔나</dt>
<dd>08-03에는 «얻는 게 이름의 정확도뿐이라 비용이 이익을 넘는다»로 유지를 골랐다. 그런데 <b>이 칸의 의미가 «표현»에서 «모든 요청의 입구»로 바뀌면서</b> 이름이 <em>부정확한</em> 것에서 <b>틀린</b> 것이 됐다 — 타 BC가 부르는 서비스 API는 표현이 아니다. 계산이 뒤집혔다.</dd>
<dt>R1 의 직접 귀결</dt>
<dd>R1 이 이 두 칸을 <b>헥사고날 구역</b>으로 배정했다. 구역 담당 계보의 어휘를 쓰기로 했으므로 헥사고날 이름을 쓴다. <code>presentation</code>은 <b>DDD 어휘</b>(Evans 원문 «User Interface Layer (or Presentation Layer)»)라 애초에 구역 배정과 어긋나 있었다.</dd>
<dt>왜 <code>_adapter</code> 가 아니라 <code>_layer</code> 인가</dt>
<dd>처음에 <code>driving_layer/</code>로 잡았다가 <b>넷 중 하나만 접미사가 달라</b> 되돌렸다 — <code>domain_layer</code>·<code>application_layer</code>·<code>driven_layer</code> 옆에서 혼자 튄다. 의미도 성립한다: <b>이 계층이 안쪽을 구동한다</b>(presentation → application). <span class="dim">정직한 단서 — «driving <b>adapter</b>»가 Cockburn 의 결합이고 «driving <b>layer</b>»는 우리가 만든 결합이다. <code>*_layer</code> 넷을 맞추는 값이 그보다 크다고 봤다.</span></dd>
<dt>딸린 후보 — <s>결정 아님</s> <b>08-05 에 닫혔다</b></dt>
<dd>짝을 맞추면 <code>infra_layer</code> → <code>driven_layer</code>가 된다. <b>다만 그 칸을 열지 않은 채 정하지 않는다</b>고 미뤘다 — 아래를 안 보고 위를 확정하는 것이 앞선 안이 무너진 방식이었다.<br><b>그 칸을 열고 나서 그대로 갔다</b> — <b>D16</b>. 미룬 값을 실제로 받았다: 안을 보기 전이었다면 <em>«짝이 예쁘다»</em> 말고 댈 근거가 없었는데, 열고 보니 <b>1차 축이 「내가 무엇을 구동하나」</b>였다(<b>D15</b>) — <b>이름이 축을 그대로 말하게 됐다.</b></dd>
<dt>역할 이름의 이득</dt>
<dd>«종류»가 아니라 <b>«역할»</b>로 이름 붙였기 때문에 하위 종류가 늘어도 이름이 안 깨진다. Cockburn 이 든 driver 는 «사용자·프로그램·<b>테스트</b>·<b>배치</b>»다 — 나중에 CLI 든 스케줄러든 메시지 컨슈머든, «밖이 나를 구동한다»는 이유만으로 <b>정의상 들어온다</b>. <b>P4</b>(adapter 가 수용소가 됨)와 정확히 반대 방향이다.</dd>
<dt>비용</dt>
<dd><code>presentation_layer</code> <b>119건 · 45파일</b>(프로덕션 105 · 테스트 14). 경로 접두사 치환이라 기계 변환된다. <span class="dim">참고: <code>infra_layer</code>를 나중에 바꾸면 <b>618건 · 300파일</b>이 든다 — 실제로 바꿨다(<b>D16</b>).</span></dd>
<dt>기각한 대안</dt>
<dd><code>primary_adapter</code>(Cockburn 원문이나 방향을 안 말함) · <code>inbound_adapter</code>(계보 원전 어휘가 아님) · <code>interface_layer</code>(뜻이 너무 많음) · 유지(의미가 틀려짐).</dd>
</dl>

## D1 · 타 BC 입구를 어디 두나

**확정 · 08-04** · 자리 — ① 칸 &nbsp;·&nbsp; 닫는 문제 <b>P6</b>

<dl class="kv">
<dt class="ans-dt">결정</dt>
<dd class="ans-dd filled"><code>published_service/</code>를 <b><code>driving_layer/open_host_service/</code></b>로 옮긴다. 최상위 칸 하나가 사라지고 <code>driving_layer/</code> 안으로 내려간다.</dd>
<dt>세 관점이 모두 지지한다</dt>
<dd><b>헥사고날</b> — driving 의 정의 그대로다. Cockburn 의 동기가 «사용자·프로그램·테스트·배치 어느 쪽에서든 똑같이 구동». <b>DDD</b> — Evans 는 UI 계층을 정의하며 «외부 행위자가 사람이 아니라 <em>다른 컴퓨터 시스템</em>일 수 있다»고 명시한다. <b>클린</b> — Interface Adapters 링의 Controller. 프로그램 호출자를 위한 컨트롤러다. <b>이번 논의에서 셋이 다 지지한 첫 항목이다.</b></dd>
<dt>실측이 뒷받침한다</dt>
<dd><code>&lt;service&gt;_service.py</code> 44파일이 안쪽을 <b>155번</b> 부른다(domain 64 · application 55 · composition_root 36) — <b>안쪽을 호출하는 어댑터</b>다. 반대로 <b>BC 안쪽이 자기 OHS 를 부르는 건 0건</b>. 방향이 driving 그 자체다.</dd>
<dt>기각한 대안</dt>
<dd>⒜ 최상위 유지 — 「이 BC 의 대외 창구」가 <code>ls</code> 한 번에 보이는 이점이 있으나, <b>역할이 같은 것을 두 칸에 나눠 두게 된다</b>(HTTP 입구와 BC 입구). ⒞ 계약·구현 쪼개기 — 소비 파일이 <b>두 경로를 import</b>하게 된다(함수 1회당 계약 3.6개).</dd>
<dt>비용</dt>
<dd>크로스-BC import <b>215건</b>(프로덕션 125 · 테스트 90). 접두사 치환.</dd>
<dt>남긴 것</dt>
<dd>이름과 내부 구성은 <b>D9</b>에서 이어 정했다 — <code>open_host_service/</code>.</dd>
</dl>

## D7 · api/ 의 조직 축

**확정 · 08-04** · 자리 — <code>driving_layer/api/</code>

<dl class="kv">
<dt class="ans-dt">결정</dt>
<dd class="ans-dd filled"><b><code>api/&lt;area&gt;/</code> — area 1차를 유지한다.</b> 기술 폴더(<code>ninja/</code>)는 <b>만들지 않는다</b>. 기술은 <b>이름</b>에 붙인다 — <code>NinjaTurnController</code>.</dd>
<dt>근거 ① 트리 전체의 규칙</dt>
<dd><code>domain_layer/&lt;aggregate&gt;/</code> · <code>application_layer/&lt;area&gt;/</code> 전부 <b>도메인 축 1차 · 종류 2차</b>다. 정본 <b>§0-4</b>가 «종류 2차 폴더 · 평면 금지»로 못 박았다. <code>api/ninja/</code>를 넣으면 <b>트리에서 유일하게 기술이 1차인 자리</b>가 된다.</dd>
<dt>근거 ② 값이 하나인 축으로는 폴더를 만들지 않는다</dt>
<dd>«아직 쓰이지 않는 확장 지점은 만들지 않는다»가 원칙이다. 기술이 둘 이상이 되기 전에는 축이 아니다. 값이 하나인 축으로 폴더를 만들면 §0 항상-생성과 겹쳐 <b>16개 BC 에 <code>ninja/</code> 한 겹이 무조건 생기고 안에는 언제나 하나만</b> 들어간다.</dd>
<dt>근거 ③ 정본이 이미 다른 방식을 갖고 있다</dt>
<dd>§4 는 기술을 <b>이름의 한정자</b>로 표시한다 — <code>DjangoUtcClockAdapter</code> · <code>OpenAiLlmStreamingGateway</code>. 게다가 상위 폴더가 <code>driving_layer/</code>라 «갈아끼울 수 있는 어댑터»는 <b>이미 이름에 선언</b>돼 있다. <code>ninja/</code>는 같은 말을 두 번 하는 것이다.</dd>
</dl>

## D8 · schema/ 의 자리

**확정 · 08-04** · 자리 — <code>driving_layer/api/</code>

<dl class="kv">
<dt class="ans-dt">결정</dt>
<dd class="ans-dd filled"><b><code>api/&lt;area&gt;/schema/</code></b> — area 밑으로 내린다. 최상위 형제였던 <code>schema/</code>는 사라진다.</dd>
<dt>근거 — 축 일관</dt>
<dd><code>schema/</code>는 <b>그 area 의 입출력 계약</b>이다. 트리 전체가 도메인 축 1차이므로 area 밑에 온다. 최상위 형제로 두면 축이 하나만 어긋난다.</dd>
<dt>왜 <code>api/</code> 밖이면 안 되나</dt>
<dd>스키마는 <b>HTTP 계약</b>이다 — <code>api/</code> 것이다. 최상위 형제로 두면 «<b>누구의</b> 스키마인가»가 흐려진다. <code>open_host_service/</code>도 자기 계약을 갖기 때문이다.</dd>
<dt>안은 방향으로만 가른다</dt>
<dd><code>schema_in.py</code> · <code>schema_out.py</code> <b>둘</b>이다. 그 안의 클래스 구성은 <b>작성자 재량</b>이다 — <b>D10</b>.</dd>
<dt>왜 방향은 규정하나</dt>
<dd>입력과 출력은 <b>검사 대상</b>이다 — «응답 스키마가 도메인 타입을 직접 노출하는가» «요청 스키마가 도메인 객체를 만드는가»는 파일 단위로 판정된다. 그리고 안쪽 <code>application_layer/&lt;area&gt;/&lt;use_case&gt;/</code> 가 클린의 <b>Input Data · Output Data</b> 자리이므로, 바깥 스키마도 같은 축으로 갈리는 것이 <b>대칭</b>이다.</dd>
<dt>생기는 대칭</dt>
<dd>안쪽 <code>application_layer/&lt;area&gt;/&lt;use_case&gt;/</code> ↔ 바깥 <code>api/&lt;area&gt;/schema/</code> ↔ 타 BC용 <code>open_host_service/&lt;service&gt;/contract/</code>.</dd>

<dt class="ans-dt">08-06 재검 — <b>실측이 전제를 확인했다</b></dt>
<dd class="ans-dd filled">근거가 「축 일관·대칭」이라는 설계 논증뿐이었다. 판정 물음을 실측으로 던졌다 — <em>「이 스키마를 여러 area 가 나눠 쓰나?」</em>
<div class="pre-wrap"><pre><code>schema 클래스 63개 중 컨트롤러가 쓰는 것 43개
   1개 area 만 씀   43 클래스   ← 전부
   2개 이상이 공유      0 클래스</code></pre></div>
<b>컨트롤러가 쓰는 70클래스가 전부 area 하나에만 갇혀 있고 공유는 0건이다.</b> <span class="dim">HEAD 재측정 — schema 클래스 <b>총 101 · 쓰임 70 · 안 쓰임 31</b>(옛 값 「63/43/20」은 BC 층만 센 것).</span> 같은 자로 <code>bc_error_schema</code> 을 재면 정반대다 — <b>401 이 컨트롤러 보유 area 23개 전부</b>에 걸린다(422 는 20개, 503 은 19개 · BC 로는 13·10·12). <b>그래서 하나는 <code>&lt;area&gt;/</code> 밑이고 하나는 <code>api/</code> 바로 밑이다.</b><br>
<b>현행이 BC 층인 건 반증이 아니라 증상</b>이었다 — 실측 16개 BC 전부 <code>schema/</code> 가 BC 층인데, 열어 보면 <code>accounts/…/schema_in.py</code> 한 파일에 <b>세 area 것 6클래스</b>가 뭉쳐 있다(<code>SocialLoginIn</code>·<code>PhoneRegisterIn</code>·<code>PhoneVerifyIn</code> / <code>ChildIn</code>·<code>ChildProfileReplaceIn</code> / <code>InvitationAcceptIn</code>). <b>한 area 만 쓰는 것들이 모여 있었을 뿐</b>이라 나누면 각자 자리로 간다.<br>
<em>덤 — 63개 중 <b>20개는 컨트롤러가 안 쓴다</b>. 중첩 사용인지 죽은 것인지는 대조 때 본다.</em></dd>

<dt class="ans-dt">이름 — <b><code>schema_in</code>·<code>schema_out</code> 은 반복이 아니다</b></dt>
<dd class="ans-dd filled">「폴더가 종류를 말하면 파일은 반복하지 않는다」에 걸리는 것처럼 보인다. 트리 전체를 세어 보니 <b>규칙의 선이 거기가 아니었다</b>:
<div class="pre-wrap"><pre><code>자리표시자 · 접미사 없음 26   →  폴더가 이미 종류를 말했다
   &lt;entity&gt;.py · &lt;value_object&gt;.py · &lt;event&gt;.py · &lt;request&gt;.py · &lt;exception&gt;.py …
자리표시자 · 접미사 있음  9   →  폴더가 «이름»이라 파일이 종류를 말한다 (꼴 7)
   &lt;use_case&gt;_use_case.py · &lt;service&gt;_service.py · &lt;boundary&gt;_unit_of_work.py …
고정 이름                16   →  그냥 이름을 쓴다 (꼴 14)
   schema_in.py · schema_out.py · &lt;use_case&gt;_command.py · &lt;use_case&gt;_result.py · bc_error_schema.py
   composition_root.py · panel.py · api.py · urls.py · celery.py · apps.py …</code></pre></div>
<b>자리표시자일 때만 접미사를 뗀다.</b> 파일이 늘 때마다 접미사가 같이 늘기 때문이다(<code>&lt;value_object&gt;.py</code> 는 166파일). 고정 이름은 <b>둘로 끝</b>이라 반복 비용이 없고, <code>command</code>/<code>result</code> 과 <b>같은 어휘를 쓰는 것이 위 대칭을 눈에 보이게 한다</b>.<br>
대안 둘을 재봤다 — <code>input.py</code>/<code>output.py</code> 는 <b><code>command</code>/<code>result</code> 과 어휘가 어긋나</b> 대칭이 깨지고, <code>request.py</code>/<code>response.py</code> 는 <b><code>contract/request/</code> 와 같은 말</b>이 되어 한 트리에서 <code>request</code> 가 두 층을 가리킨다. 그리고 <code>schema/in.py</code> 는 <b><code>in</code> 이 파이썬 예약어라 애초에 import 가 안 된다</b>.</dd>
</dl>

## D9 · 타 BC 입구의 이름과 내부

**확정 · 08-04** · 자리 — <code>driving_layer/open_host_service/</code> &nbsp;·&nbsp; 닫는 문제 <b>P6</b>

<dl class="kv">
<dt class="ans-dt">결정</dt>
<dd class="ans-dd filled"><b>이름은 <code>open_host_service/</code></b> — Evans 패턴명을 <b>줄이지 않고 그대로</b> 쓴다. 내부는 <b><code>&lt;service&gt;/{ &lt;service&gt;_service.py, contract/ }</code></b> — <b>원리로 도출되고 실측이 이미 그 형태다</b>.</dd>
<dt>왜 이 이름인가 — 출구와 쌍이다</dt>
<dd>둘 다 Evans <b>컨텍스트 맵 패턴</b>이고 방향만 반대다 — <b>Open Host Service</b> 는 <b>남이 나를 부르는</b> 입구, <b>Anticorruption Layer</b> 는 <b>내가 남을 부를 때</b> 방어하는 출구. <b>이름 쌍이 전역 제약 ③(BC 경계는 관문으로만)을 그대로 드러낸다.</b> 지금 이름 <code>published_service/</code>는 <b>조어</b>다 — Evans 에는 <b>Open Host Service</b> 와 <b>Published Language</b> 가 별개 패턴인데 둘을 섞었다.</dd>
<dt>줄여 쓰지 않는다 — 그리고 경계</dt>
<dd><b>원전 패턴 이름은 풀어 쓴다.</b> 계보 어휘라 정확도가 값이고, 약어는 «무슨 말인지 아는 사람만» 읽힌다. 다만 <b>일반어가 된 약어는 그대로 둔다</b> — <code>api</code>를 <code>application_programming_interface</code>로 쓰지는 않는다. <span class="dim">이 방침은 다른 칸에도 걸린다: <code>acl/</code> → <code>anticorruption_layer/</code> · <code>driven_layer</code> 의 <code>infra</code> 도 약어다. <b>각 칸 차례에 적용한다.</b></span></dd>
<dt>내부 — 원리로 도출된다</dt>
<dd>도메인 축 1차(<b>D7</b>)를 따르면 <code>&lt;service&gt;/</code>가 1차다. 그 안에는 <b>입구 함수</b>와 <b>계약 타입</b> 둘이 필요하고, 계약은 요청·응답·예외 셋으로 갈린다 — <code>api/</code>가 controller + schema 인 것과 같은 골격이다. <span class="dim">나중 대조 — 지금 구현이 28개 서비스 · 10개 BC 에서 <b>예외 0건</b>으로 이 형태다.</span></dd>
<dt><code>api/</code> 와 같은 모양이 된다</dt>
<dd><code>api/&lt;area&gt;/{ controller, schema/ }</code> ↔ <code>open_host_service/&lt;service&gt;/{ service.py, contract/ }</code>. 둘 다 driving 어댑터이고 <b>«입구 함수 + 계약 타입»</b>이며 <b>호출자만 다르다</b>. <b>D7</b>의 «도메인 축 1차»도 그대로 지켜진다.</dd>
<dt><code>boundary/</code> 의 실수는 아니다</dt>
<dd>«선언(<code>contract/</code>)과 구현(<code>service.py</code>)이 한 폴더»가 <b>N1 의 재발 아니냐</b>가 당연한 걱정이다. 아니다 — <code>boundary/</code>가 깨진 이유는 <code>port/</code>가 <b>안쪽이 의존하는 것</b>인데 바깥 칸에 있어서였다. <code>contract/</code>는 다르다: 실측상 <b>BC 안쪽이 자기 OHS 를 부르는 건 0건</b>이다. 둘 다 바깥을 향한 얼굴이고 링이 같다.</dd>
<dt class="ans-dt">남긴 작은 것 — <b>닫았다</b> <span class="dim">08-07 · F2</span></dt>
<dd class="ans-dd filled"><code>contract/request_contract/</code>는 «계약/요청_계약»으로 <b>말이 겹쳤다</b>. <b><code>contract/{request, response, exception}</code> 으로 개명한다.</b>
<div class="pre-wrap"><pre><code>지금   contract/request_contract/&lt;request&gt;.py
개명   contract/request/&lt;request&gt;.py</code></pre></div>
<b>트리가 이미 갖고 있던 자를 이 자리에만 안 걸고 있었다</b> — 「폴더가 방향을 말하면 아래 파일이 그것을 반복하지 않는다」. 그 자는 <b>부모 폴더에도 똑같이 걸려야 한다</b>: 낱말은 한 경로에서 <b>한 번만</b> 말한다.<span class="dim"><b>08-08 · D41 이 이 자를 반으로 갈랐다</b> — <b>폴더 이름</b>에는 그대로 걸리고(<code>request_contract/</code> ✗), <b>파일 이름</b>에는 안 걸린다. 파일은 «이름만으로 무엇인지 보이나»로 판정한다. 이미 <code>repository/&lt;aggregate&gt;_repository.py</code> 와 <code>unit_of_work/&lt;boundary&gt;_unit_of_work.py</code> 두 자리가 이 자를 어기고 있었고, 그게 예외가 아니라 <b>다른 자가 이기고 있었다는 뜻</b>이었다.</span>
<br><b>파일 이름은 그대로 <code>&lt;request&gt;.py</code> 다</b> — 접미사를 파일로 내리면 중복을 없앤 게 아니라 자리만 옮긴 것이 된다.
<span class="dim">현행은 실제로 세 겹이다 — <code>contract/request_contract/parent_can_access_child_request_contract.py</code> 에서 «contract» 가 <b>세 번</b>, «request» 가 <b>두 번</b> 나온다. 개명하면 <code>contract/request/parent_can_access_child_request.py</code> 다.</span></dd>
</dl>

## D10 · 트리는 어디까지 규정하나

**확정 · 08-04** · 자리 — 모든 칸에 걸리는 규칙

<dl class="kv">
<dt class="ans-dt">결정</dt>
<dd class="ans-dd filled">트리는 <b>«그 구분으로 규칙을 쓰거나 검사를 할 수 있는 데까지만»</b> 규정한다. 그 아래는 작성자 재량이다.</dd>
<dt>판정 기준</dt>
<dd>그 구분이 없으면 <b>규칙을 못 쓰거나 검사를 못 할 때</b>만 폴더로 못 박는다. 그 외에는 작성자 재량이다 — 강제하면 <b>§0 항상-생성 비용</b>만 늘고 얻는 게 없다.</dd>
<dt>이 칸에서의 적용</dt>
<dd><code>contract/{request, response, exception}</code> — <b>규정한다</b>. <b>BC 경계를 넘는 표면</b>이고, 특히 <code>exception/</code> 는 «어떤 예외가 경계를 넘나»를 폴더로 드러내 <b>전역 제약 ③</b>과 직결된다.<br><code>&lt;area&gt;_controller.py</code> · <code>&lt;service&gt;_service.py</code> — <b>규정한다</b>. «진입점이 하나»를 못 박는다.<br><code>schema/{ schema_in.py, schema_out.py }</code> — <b>규정한다</b>. <b>방향은 검사 대상</b>이기 때문이다.<br>그 <b>안의 클래스 구성</b> — <b>규정하지 않는다</b>. 엔드포인트마다 달라지는 형식이라 검사할 골격이 없다.</dd>
<dt>«폴더까지»가 아니라 «검사할 수 있는 데까지»</dt>
<dd>처음에는 «폴더와 진입점까지»로 잡았다가 <code>schema/</code> 안에서 <b>방향(in/out)이 검사 대상</b>임이 드러나 고쳤다. <b>깊이가 기준이 아니라 판정 가능성이 기준이다</b> — 파일이든 폴더든, 그 구분으로 규칙을 쓸 수 있으면 규정하고 없으면 안 한다.</dd>
<dt>§0-4 와 충돌하지 않는다</dt>
<dd>«평면 금지»는 <b>도메인 축을 안 쓴 것</b>을 막는 규칙이다. <code>schema/</code>는 이미 <code>&lt;area&gt;/</code> 아래에 있어 <b>도메인 축이 한 단계 위에서 적용</b>됐다 — 그 안이 평면이어도 규약을 어기지 않는다.</dd>
<dt>왜 규칙으로 남기나</dt>
<dd>이 물음은 <b>모든 칸에서 되풀이된다</b>. 칸마다 즉흥으로 정하면 어떤 칸은 파일까지, 어떤 칸은 폴더까지 규정하는 상태가 된다 — 지금 트리가 겪는 «자리마다 규칙이 다르다»가 그렇게 생겼다.</dd>
</dl>

## D11 · driving_layer 의 화살표와 앎의 범위

**확정 · 08-06** · 자리 — ③ 화살표 · ④ 앎의 범위 &nbsp;·&nbsp; <code>driving_layer/</code> 를 닫는 마지막 두 줄 &nbsp;·&nbsp; <b>08-06 에 사정거리를 한 번 더 좁혔다(R2)</b>

<dl class="kv">
<dt class="ans-dt">결정 ③ 나가는 화살표</dt>
<dd class="ans-dd filled"><b><code>driving_layer/</code> 의 리프 전부</b> — <code>api/&lt;area&gt;/</code> · <code>open_host_service/&lt;service&gt;/</code> · <code>cron_job/&lt;job&gt;.py</code> <b>아래</b>는 <b><code>application_layer/&lt;area&gt;/</code> 아래에 더해, <code>domain_layer</code> 의 <code>exception</code> 과 <code>value_object</code> 만</b> 의존한다.
<code>driven_layer</code> 도, <b><code>application_layer/port/</code> 도</b> import 하지 않는다. <code>domain_layer</code> 안에서도 <b>애그리거트·엔티티·리포지토리 선언·이벤트는 금지</b>다.
<b><code>framework/</code> 에서는 <code>&lt;technology&gt;/</code> 만</b> 열린다 — <em>닌자가 이해하는 인증 클래스와 오류 형식은 «주도 어댑터의 부속»이라 입구 물건이다. 나머지 넷은 각자 주인이 따로 있다(<code>&lt;capability&gt;_port.py</code>=유스케이스 · <code>broker/</code>=유스케이스와 <code>composition_root</code> · <code>pure/</code>=계산 · <code>test/</code>=테스트)</em>.
여기에 <b>와이어링 예외 하나</b>가 붙는다 — <b>자기 BC 의 <code>composition_root</code> 에서 <code>build_</code> 로 시작하는 이름만</b> 가져올 수 있다(아래 «와이어링 예외»).<br>
열어 준 <code>exception</code> 에는 <b>«어디까지 쓰나»가 붙는다 — 타입만이다</b>. <code>except &lt;DomainError&gt;:</code> 로 갈래를 가르고 <code>bc_error_schema.py</code> 의 코드로 바꿔 내보내되,
<b>예외 객체의 속성은 읽지 않는다</b>(아래 «타입만 본다»).<br>
<span class="dim"><b>08-07 · 2차 리뷰 S8 — 주어를 «리프 전부»로 되돌렸다.</b> 옛 주어는 <code>api/</code>·<code>open_host_service/</code> 둘뿐이라 <b><code>cron_job/&lt;job&gt;.py</code> 에 와이어링 예외가 문면상 안 닿았다</b> — 배치도 유스케이스를 <code>build_&lt;use_case&gt;()</code> 로 받아야 하는데(<b>D26</b> ③이 «D11 이 이미 답했다» 고 적었다) 허용 목록에 없으니 위반으로 찍힌다. 둘로 좁혔던 이유는 <b>D6</b> 의 <b>와이어링 파일</b>(<code>api/&lt;bounded_context&gt;_api_router.py</code>)을 빼기 위해서였는데, 그건 <b>«칸 바로 밑»이라 리프가 아니다</b> — 리프로 적으면 그 파일은 저절로 빠진다.</span><br>
<span class="dim">→ <b>08-06 에 두 종류를 열었다</b>(<b>R2</b>) — 08-04·08-05 문구는 「<code>domain_layer</code> 는 통째로 금지」였는데, 그러면 <b>D27</b> ③(<em>컨트롤러가 예외→<code>ErrorOut</code> 매핑을 «직접» 소유한다</em>)과 <b>동시에 참일 수 없다</b>. 파이썬의 <code>except</code> 는 <b>클래스 객체</b>를 받으므로 <code>except InvalidLesson</code> 을 쓰려면 그 클래스를 import 해야 한다. 자세한 셈은 아래 «왜 <code>domain_layer</code> 를 통째로 막았다가 풀었나».</span><br>
<span class="dim">→ <b>08-05 에 사정거리를 좁혔다</b>(<b>D6</b>) — 「<code>driving_layer</code> 는」이었는데 <b>칸 바로 밑의 와이어링 파일</b>(<code>api/&lt;bounded_context&gt;_api_router.py</code>)이 프로젝트 전역 <code>api</code> 객체를 잡아야 해서다. <b>와이어링은 정의상 안팎을 동시에 안다</b> — 예외를 내는 대신 <b>규칙이 닿는 범위를 정확히 적었다</b>.</span></dd>
<dt class="ans-dt">열어 준 <code>exception</code> 을 «어디까지» 쓰나 — <b>타입만 본다</b> <span class="dim">08-07 · F1</span></dt>
<dd class="ans-dd filled"><b>이 규칙의 값은 «자료지 협력자가 아니다»를 기계로 재게 만드는 것</b>이다. 그 문장은 뜻은 맞는데 <b>그때까지 사람 판정이었다</b> — import 만 보면 «자료로 쓰는지»를 알 수 없다.
<div class="pre-wrap"><pre><code>except OrderAlreadyShipped:                      # OK — 갈래만 가른다
    return 409, OrderErrorSchema(code="already_shipped")

except OrderAlreadyShipped as e:                 # 위반 — 속성을 읽는다
    return 409, OrderErrorSchema(code="already_shipped", shipped_at=e.shipped_at)</code></pre></div>
<b>왜 아래가 나쁜가</b> — 바깥 JSON 이 <b>도메인 예외의 «구조»에 묶인다</b>. 그 예외에 필드가 하나 붙거나 이름이 바뀔 때마다 응답 계약이 흔들리고,
그러면 <b>도메인이 자기 불변식을 고치려다 API 를 깬다</b>. 트리가 애그리거트를 <code>schema_out</code> 에 못 싣게 한 것과 <b>정확히 같은 이유</b>이고, 예외만 빠져 있었다.
<br><b>원전에서 온 선</b> — Fowler 의 <b class="v c">Notification</b> 이 이 자리를 정의로 삼는다: <em>오류 «코드»는 프레젠테이션과 도메인이 공유하는 클래스에 있어야 하고 도메인 어휘로 설계된다. 그러나 도메인 객체에 대한 참조는 실어 보내지 않는다.</em>
<b>«코드는 공유, 객체는 금지»</b> 가 그 선이고, 파이썬 예외에 옮기면 <b>«타입은 공유, 속성은 금지»</b> 가 된다.
RFC 9457 도 같은 편이다 — <em>소비자는 <code>detail</code> 을 파싱해 정보를 얻으면 안 되고, problem type 마다 함께 쓸 상태 코드를 문서화해야 한다</em>. <b>실패의 정체는 문장이 아니라 코드가 진다.</b>
<br><b>그래서 바깥에 더 말할 것이 생기면</b> 예외에 필드를 붙이는 게 아니라 <code>bc_error_schema.py</code> 에 <b>코드를 하나 더</b> 만든다. 값을 실어야 하면 그건 실패가 아니라 <b>정상 응답</b>이므로 <code>result</code> 으로 나간다.
<br><span class="dim"><b>이 규칙은 원전 인용이 아니라 확장이다.</b> 의존 «방향»은 셋이 다 허용한다 — Evans 의 계층 규칙은 「자기 <b>아래 계층들</b>」이고(「바로 아래 한 층」은 POSA 의 엄격 변형·Vernon 이 이름 붙인 Strict/Relaxed 에서 온 읽기다), Martin 의 의존 규칙은 <b>한 방향뿐</b>이라 바깥이 안쪽을 아는 것은 금지 조항 자체가 없으며, Cockburn 은 방향 규칙을 두지 않았다.
참조 구현도 전부 그렇게 한다 — <code>dddsample-core</code> 는 인터페이스 계층에서 도메인을 <b>57번</b> import 하고(<code>CargoTrackingRestService</code> 는 리포지토리까지 직접 주입한다), Vernon 의 <code>IDDD_Samples</code> 는 REST 리소스가 애그리거트를 그대로 import 한다.
<b>그러나 «예외를 어떻게 번역하나»는 셋 다 침묵한다</b> — Evans 는 불변식이 어디서 지켜지는지만 정하고, Martin 은 예외를 한 번도 언급하지 않으며, Vernon 의 샘플에는 <b>도메인 예외 클래스가 0개</b>다. 여기부터는 우리가 그은 선이다.</span></dd>
<dt>«<code>application_layer</code> 만»에서 «<code>&lt;use_case&gt;/</code> 만»으로 조인 이유 <span class="dim">08-04 보강</span></dt>
<dd>처음 문구는 «<code>application_layer</code> 만»이었는데, <b>D14</b> 가 그 안에 <code>port/</code> 를 만들면서 <b>문구에 구멍이 생겼다</b> — 컨트롤러가 <code>port/Clock</code> 을 import 해도 문구상 위반이 아니게 된다.<br>막아야 한다. 클린의 모양은 <b>Controller → Interactor</b> 이지 컨트롤러가 포트를 직접 잡는 것이 아니다. 잡는 순간 <b>컨트롤러가 조율을 시작한다</b>. 컨트롤러에 필요한 <code>command</code>·<code>result</code> 은 <code>&lt;use_case&gt;/</code> 에 있으므로 이걸로 충분하다.</dd>
<dt>셋이 같은 곳을 가리킨다</dt>
<dd><b>클린</b> — Controller 는 요청을 <b>Input Data</b> 로 바꿔 Interactor 에 넘긴다. 엔티티를 직접 만지지 않는다. <b>헥사고날</b> — driving 어댑터는 <b>포트를 통해서만</b> 안으로 들어간다. 포트 너머로 손을 뻗지 않는다. <b>DDD</b> — UI 계층은 Application 계층에 말한다.</dd>
<dt>왜 <code>domain_layer</code> 를 통째로 막았다가 풀었나 <span class="dim">08-06 개정 · R2</span></dt>
<dd><b>막으려던 것은 이것 하나다.</b>
<div class="pre-wrap"><pre><code># driving_layer/api/lesson/lesson_controller.py 안에서 — 통째로 열면 가능해진다
lesson = self._repository.find(lesson_id)   # 컨트롤러가 저장소를 직접 읽고
lesson.cancel()                             # 업무 규칙을 직접 실행하고
self._repository.save(lesson)               # 저장까지 한다
#  application_layer 를 통째로 건너뛰었다 — 트랜잭션 경계도 이벤트 발행도 빠진다
#  그리고 이 경로는 HTTP 로만 부를 수 있어 크론도 타 BC 도 같은 일을 못 한다</code></pre></div>
<b>그런데 「<code>domain_layer</code> 통째로 금지」는 그물이 너무 컸다.</b> 그 안에는 <em>업무를 실행하게 만드는 것</em>과 <em>자료일 뿐인 것</em>이 같이 있다.
<div class="pre-wrap"><table class="mini"><tr><th><code>domain_layer</code> 안의 무엇</th><th>입구가 쥐면 할 수 있는 일</th><th>판정</th></tr>
<tr><td><code>&lt;aggregate&gt;.py</code> · <code>entity/</code></td><td><code>lesson.cancel()</code> — <b>업무를 실행한다</b></td><td><b>금지</b></td></tr>
<tr><td><code>&lt;aggregate&gt;_repository.py</code></td><td><b>저장소를 직접 읽고 쓴다</b></td><td><b>금지</b></td></tr>
<tr><td><code>event/</code></td><td><b>도메인 사건을 직접 만든다</b></td><td><b>금지</b></td></tr>
<tr><td><code>exception.py</code></td><td><code>except InvalidLesson</code> — <b>잡기만 한다</b></td><td><b>허용</b></td></tr>
<tr><td><code>value_object/</code></td><td><code>LessonStatus("missed")</code> — <b>문자열을 타입으로 바꾸기만 한다</b></td><td><b>허용</b></td></tr></table></div>
<b>허용한 둘은 «협력자»가 아니라 «자료»다</b> — 불변이고, 저장소를 안 건드리고, 부른다고 상태가 안 바뀐다. <b>막으려던 셋은 그대로 다 막힌다.</b><br>
<b>실측으로 잰 대가</b> — 현행 입구 → 도메인 import <b>133건 · 58파일 · 16개 BC 전부</b>.
<div class="pre-wrap"><pre><code>값 객체      74      ← 허용                   *_service.py(관문)   50
예외 모듈     33      ← 허용                   schema_out.py        34
엔티티·기타   20      ← 금지(남는다)            *_controller.py      19
리포지토리 선언 3      ← 금지(남는다)            schema_in.py         14
포트 선언      2      ← 금지(남는다)            _exception_translation.py 7
이벤트        1      ← 금지(남는다)            그 밖                  9
                                        ─────────────────────────
허용 107 / 금지 26</code></pre></div>
남는 <b>26건</b>은 R2 가 아니라 <b>D14</b>(출력 DTO·Presenter)와 <b>D27</b>(포트 실패의 칸)에서 따로 닫는다.<br>
<span class="dim">한 가지 더 — 현행에는 <code>_exception_translation.py</code> 가 <b>3개 있고 decorator 로 매핑을 옮겨 놨다</b>. D27 ③이 명시적으로 금지한 모양이다. 즉 현행은 D11 도 D27 도 안 지키고 있었다.</span></dd>
<dt>그래도 <b>도메인 타입을 응답에 그대로 싣지는 않는다</b></dt>
<dd>값 객체를 열었다고 <code>schema_out</code> 이 애그리거트를 받아도 된다는 뜻이 아니다. 응답에 필요한 값은 <b>응용의 출력 DTO 로 온다</b>. 열린 것은 <b>«쿼리 문자열 <code>?status=missed</code> 를 <code>LessonStatus</code> 로 파싱하고, 되돌릴 때 다시 문자열로 굽는»</b> 딱 그 폭이다.</dd>
<dt class="ans-dt"><b>와이어링 예외 — 컨트롤러가 유스케이스를 얻는 한 줄</b> <span class="dim">08-06 · R6</span></dt>
<dd class="ans-dd filled"><b>컨트롤러는 «만들어진» 유스케이스가 있어야 일한다.</b> 유스케이스는 리포지토리 구현체·어댑터·UnitOfWork 를 받아야 생기고,
그걸 컨트롤러가 직접 만들면 <code>driven_layer</code> 를 알게 되어 <b>훨씬 큰 위반</b>이 된다. 그래서 조립은
<b>D6</b> 가 <code>composition_root</code> 에 맡겨 놨다 — <code>build_&lt;use_case&gt;()</code>.
<div class="pre-wrap"><pre><code># driving_layer/api/lesson/lesson_controller.py
from application.lessons.composition_root import build_cancel_lesson_use_case

def cancel(self, request, lesson_id: int):
    use_case = build_cancel_lesson_use_case()      # 매 요청 새로 만든다
    return use_case.execute(...)</code></pre></div>
<b>그런데 결정③은 «허용 목록»이라, 목록에 없는 <code>composition_root</code> 가 금지로 찍혔다.</b>
D6 는 방식을 정했고 이 카드는 그걸 몰랐다 — <b>두 카드가 서로를 안 본 것</b>이고, 같은 날 <b>D27</b> 과 부딪혔던 것과 <b>같은 병</b>이다.<br>
<b>여는 폭을 두 번 좁힌다.</b>
<div class="pre-wrap"><pre><code>「build_ 로 시작하는 이름만」   composition_root 를 열되 아무거나 못 꺼낸다.
                              리포지토리 구현체를 꺼내려는 순간 검사에 걸린다.
「자기 BC 만」                  남의 composition_root 를 부르는 건 관문(OHS) 우회다.
                              D9 가 이미 위반 3건으로 잡아 놨다.</code></pre></div>
<b>플러그인과도 같은 편이다</b> — 리뷰어 지침이 이미 <em>「presentation 은 <code>build_…()</code> 팩토리를 «매요청 호출만» 한다」</em>로 규정하고 있다.
<span class="dim">이름만 다르다(플러그인 <code>build_&lt;usecase&gt;_command()</code> · 트리 <code>build_&lt;use_case&gt;()</code>) — <b>4번 ⓐ</b> 에서 맞춘다.</span></dd>
<dt>★ 이것은 <b>원전을 «알고» 어기는 명시적 예외다</b> <span class="dim">08-09 · T39</span></dt>
<dd><b>Martin Ch26 에 정면으로 걸린다.</b>
<div class="pre-wrap"><pre><code>"Main is the ultimate detail—the lowest-level policy.
 Nothing, other than the operating system, depends on it."</code></pre></div>
<b>위의 «와이어링은 정의상 안팎을 동시에 안다»로는 이 자리를 못 덮는다</b> — 그 문장은 <b>칸 바로 밑의 와이어링 파일</b>(<code>api_router.py</code>)을 위한 것이고, 여기 주어는 <b>리프인 컨트롤러</b>다. 이 카드가 스스로 「규칙의 주어는 <code>driving_layer/</code> 의 <b>리프 전부</b>」라고 못 박아 놨다.
<br><b>그래서 «정당화»가 아니라 «예외»로 적는다.</b> 까닭은 하나다 — <b>장고·닌자가 컨트롤러를 «만든다»</b>. 순수한 Main 이라면 Main 이 컨트롤러를 만들어 주입해야 하는데 <b>그 화살표가 프레임워크 쪽에 있어서 뒤집을 수가 없다</b>. <b>설계 실수가 아니라 장고를 쓰는 값이다</b>(<b>D6</b> 가 이 셈을 이미 적어 놨다 — <code>ninja-extra</code> + <code>injector</code> 라는 <b>대안이 있고, 값이 비싸서</b> 안 쓴다).
<br><b>모양은 Service Locator 인데 «해악»은 안 따라온다</b> — 진짜 Service Locator 는 <em>무엇이든 꺼내는 범용 컨테이너</em>라 의존이 어디에도 안 드러나는 게 병인데, <code>build_&lt;use_case&gt;()</code> 는 <b>이름이 무엇을 꺼내는지 말하고 · 반환 타입이 정적으로 드러나고 · 없는 함수는 import 시점에 터지고 · 컨트롤러의 의존이 본문에 그대로 보여 AST 로 셀 수 있다</b>.
<br><span class="dim">이 절은 D6 에만 있던 것을 여기로 복제한 것이다. <b>4차 리뷰(CA-2)가 D11 만 보고 「정당화가 안 선다」고 읽었는데, D11 만 놓고 보면 그 판단이 맞았다</b> — 근거가 카드 하나에만 살면 그 카드를 안 편 사람에게는 없는 것과 같다.</span></dd>
<dt class="ans-dt">결정 ④ 앎의 범위</dt>
<dd class="ans-dd filled"><b>프레임워크를 알아도 된다.</b> 이 칸은 <b>어댑터</b>다 — 기술을 아는 것이 이 칸의 일이다. 전역 제약 ②(안쪽은 구체 기술을 모른다)는 <b>안쪽</b>에 걸리는 규칙이고 여기는 바깥이다.</dd>
<dt>들어오는 화살표</dt>
<dd><b>아무도 <code>driving_layer</code> 를 import 하지 않는다.</b> 예외 둘 — ⒜ <b>다른 BC 가 <code>open_host_service/</code> 를 부른다</b>(이 칸이 있는 이유다) ⒝ <code>composition_root</code>(Main 은 다 안다).<br><span class="dim"><b>08-05 재검 — 세 번째가 있었고, <b>D24</b> 가 없앴다.</b> <code>api/</code> 가 <b>타 BC 의 <code>authentication.py</code> 를 27건</b> 부르고 있었다(13개 BC). <b>인증 틀이 <code>framework/</code> 으로, 해석이 관문으로 갈리면서 이 27건이 사라진다</b> — 예외는 다시 둘이다.</span></dd>
<dt>검사</dt>
<dd><b>AST 로 판정된다</b> — <code>api/&lt;area&gt;/**</code>·<code>open_host_service/&lt;service&gt;/**</code>·<code>cron_job/**</code> 의 import 를 이렇게 가른다<span class="dim">(칸 바로 밑 와이어링 파일 <code>api/&lt;bounded_context&gt;_api_router.py</code> 는 리프가 아니라 대상이 아니다 — <b>D6</b>)</span>.
<div class="pre-wrap"><pre><code>이 표는 «허용 목록»이다 — 아래 어디에도 없는 저장소 안 경로는 «위반»으로 찍는다

허용   application_layer/&lt;area&gt;/**
       domain_layer/**/exception          ← 모듈 이름이 exception
       domain_layer/**/value_object/**    ← 경로에 value_object 가 있다
       domain_layer/shared_value_object/**
       framework/&lt;technology&gt;/**          ← 닌자·장고가 «이해하는» 물건. 주도 어댑터의 부속이다
       &lt;자기 BC&gt;/composition_root         ← 꺼내는 이름이 build_ 로 시작할 때만
금지   domain_layer 의 그 밖 전부(애그리거트·엔티티·리포지토리 선언·포트·이벤트)
       driven_layer/**
       application_layer/port/**
       framework 의 그 밖(&lt;capability&gt;_port.py · broker/ · pure/ · test/)
       타 BC 의 composition_root          ← 관문(OHS) 우회다</code></pre></div>
<b>모듈 경로 문자열만 보면 갈린다</b> — 심볼을 따라갈 필요가 없다. 타 BC 의 <code>driving_layer</code> 는 <code>open_host_service/</code> 아래만 허용.
<br><span class="dim"><b>08-09 · T39 — <code>framework/</code> 가 허용에도 금지에도 «없었다».</b> 그런데 <b>D24</b> 가 인증 틀을 거기로 올렸고 닌자 인증은 <b>라우트 데코레이터에 선언</b>하니 <b>부르는 쪽이 곧 컨트롤러</b>다 — 실제로 흐르고 있는 경로가 규칙 밖에 있었다. 빠진 까닭은 <b>낱말이 겹쳤기 때문</b>이다: 아래 결정④의 «프레임워크»는 <b>장고·닌자 라이브러리</b>를 말하는데, 트리에 <code>framework/</code> <b>폴더</b>가 생기면서 그 문장이 폴더까지 덮는 것처럼 읽혔다. <b><b>D52</b> 가 D14 에서 잡은 것과 같은 병이다</b>(플러그인 §193 의 「framework」를 트리 폴더로 겹쳐 읽은 자리). <b>그리고 이 표가 «허용»과 «금지»를 둘 다 적어 두어 목록에 없는 것의 판정이 안 섰다</b> — 허용 목록으로 못 박았다.</span></dd>
</dl>

## D12 · domain_layer 의 1차 축

**확정 · 08-06** · 자리 — ① 칸 &nbsp;·&nbsp; ② 이름 &nbsp;·&nbsp; 닫는 문제 <b>P1</b>

<dl class="kv">
<dt class="ans-dt">결정</dt>
<dd class="ans-dd filled"><b>1차 폴더는 <code>&lt;aggregate&gt;/</code></b> 다. <code>entity/</code>·<code>value_object/</code> 는 <b>그 안</b>으로 내린다. 리포지토리 선언은 <b>폴더가 아니라 파일</b>(<code>&lt;aggregate&gt;_repository.py</code>). 여러 애그리거트가 쓰는 값 객체는 형제 자리에 <b><code>shared_value_object/</code></b>.</dd>
<dt>D10 으로 재면 축이 갈린다</dt>
<dd>«그 구분으로 <b>규칙을 쓰거나 검사를 할 수 있나</b>»가 기준이다.<br>
<b><code>&lt;aggregate&gt;/</code> 가 만드는 규칙</b> — ① <code>&lt;A&gt;/</code> 는 <code>&lt;B&gt;/</code> 의 <b>루트 모듈만</b> import 한다 ② 리포지토리 선언은 애그리거트당 <b>하나</b> ③ 한 유스케이스가 서로 다른 애그리거트의 리포지토리 둘을 쓰면 트랜잭션 경계 검토 대상.<br>
<b><code>entity/</code> vs <code>value_object/</code> 가 1차일 때 만드는 규칙</b> — <b>없다</b>. 둘 사이에 import 규칙 차이가 없고, 불변성·식별자 유무는 <em>폴더가 아니라 클래스 속성</em>이라 폴더 없이도 AST 가 판정한다.</dd>
<dt>왜 그 축이 더 중한가</dt>
<dd>DDD 가 트리에 대해 말하는 가장 중요한 주장 하나는 <b>«애그리거트가 불변식의 주인이다»</b>이다. 종류로 먼저 쪼개면 <b>그 경계가 트리에서 사라진다</b> — <code>entity/</code> 안에 <code>order.py</code> 와 <code>order_line.py</code> 가 나란히 있으면 둘이 <em>한 경계 안인지 별개 애그리거트인지</em> 트리로는 판별이 안 된다. 종류 축은 <b>분류</b>를 말하고, 애그리거트 축은 <b>불변식의 소유</b>를 말한다.</dd>
<dt>§0-4(1차 폴더는 도메인 이름만)와도 맞는다</dt>
<dd>«1차 폴더는 도메인 이름만». <code>api/&lt;area&gt;/</code>·<code>open_host_service/&lt;service&gt;/</code> 로 정해놓고 여기서만 종류를 앞에 두면 <b>트리가 두 어법을 쓴다</b>.</dd>
<dt>그래도 종류 어휘는 잃지 않는다</dt>
<dd>한 단계 내리면 <code>entity/</code>·<code>value_object/</code> 는 <b>거기서 D10 을 통과한다</b> — 폴더 단위로 쓸 수 있는 규칙이 실제로 있다: «이 폴더 안 클래스는 불변», «이 폴더 안 클래스는 식별자를 가진다». 생성기가 강제할 수 있는 종류의 규율이다. <b>1차가 아닐 뿐 사라지지 않는다.</b></dd>
<dt>리포지토리 — 셋 중 성격이 다르다</dt>
<dd>나머지 둘은 «종류»지만 이건 <b>선언(드리븐 포트)</b>이다. 그리고 <b>애그리거트당 하나</b>이므로 폴더가 아니라 <b>파일</b>이어야 한다 — 폴더로 두면 «여러 개 들어갈 수 있다»는 신호를 트리가 보내고, 그 순간 «애그리거트당 하나»를 트리가 말하지 못하게 된다.</dd>
<dt>Evans 가 정하고 클린은 양립한다 — R1 이 타이브레이커</dt>
<dd>Evans 는 리포지토리를 <b>도메인 계층에 애그리거트 루트당 하나</b>로 명시하고, 헥사고날은 <b>안쪽이 선언하는 드리븐 포트</b>로 본다. <b>클린은 갈린다</b> — 원칙은 «인터페이스는 그것을 쓰는 정책과 같은 링»인데, Uncle Bob 은 자기 예시에서 Gateway 인터페이스를 <b>유스케이스 링에</b> 그린다. <span class="dim">처음에 «세 계보 일치»라고 썼는데 <b>과했다</b> — 정정한다.</span><br>다만 <b>결론은 같다</b>. 어느 쪽에 둬도 의존 방향은 안쪽이라 <em>정오의 문제가 아니다</em>. 그리고 <b>도메인 쪽에 둬야 «애그리거트당 하나»가 구조로 강제된다</b> — <code>application_layer</code> 에 area 별로 두면 그 규칙을 트리가 말하지 못한다. D10 기준으로 도메인 쪽이 이기고, <b>R1(이 칸은 DDD 구역)</b> 이 타이브레이커다.</dd>
<dt>정직한 단서 — 한 줄 검사가 아니다</dt>
<dd>처음엔 «D11 과 똑같은 <b>한 줄</b> 검사»라고 했는데 <b>틀렸다</b>. <code>Money</code>·<code>EmailAddress</code> 처럼 <b>여러 애그리거트가 같이 쓰는 값 객체</b>가 그 규칙을 바로 반증한다 — 어느 애그리거트 폴더에 넣든 다른 애그리거트가 <em>남의 내부</em>를 import 하게 된다. 그래서 <code>shared_value_object/</code> 자리가 필요하고, 검사는 <b>두 줄</b>이 된다.</dd>
<dt>검사 두 줄 <span class="dim">08-06 개정 · R3</span></dt>
<dd><code>domain_layer/&lt;A&gt;/**</code> 는 <code>domain_layer/&lt;B&gt;/</code> 의 <b>루트 모듈만</b> import 한다<br>
<code>domain_layer/shared_value_object/</code> 는 <b>같은 <code>shared_value_object/</code> 안과 <code>exception</code> 말고는 아무것도 import 하지 않는다</b>(사실상 리프)</dd>
<dt>둘째 줄이 «아무것도»였다가 왜 풀렸나 <span class="dim">08-06 · R3</span></dt>
<dd><b>값 객체가 자기 불변식을 지키려면 예외를 던져야 하고, 던지려면 import 해야 한다.</b> «아무것도»는 <b>불변식을 가진 값 객체를 만들 수 없게</b> 만든다.
<div class="pre-wrap"><pre><code># domain_layer/shared_value_object/money.py
from .currency import Currency                       # ← 옛 규칙이면 위반
from ..&lt;aggregate&gt;.exception import CurrencyMismatch  # ← 옛 규칙이면 위반

def add(self, other: Money) -&gt; Money:
    if self.currency != other.currency:
        raise CurrencyMismatch(...)                  # 이걸 못 쓰면 값 객체가 아니라 자료 묶음이다</code></pre></div>
<span class="dim"><b>08-07 · 2차 리뷰 S10 — 예제의 import 경로가 트리에 없는 자리를 가리키고 있었다.</b> 옛 줄은 <code>from ..exception import …</code>, 즉 <b>BC 레벨 <code>domain_layer/exception.py</code></b> 인데 그 자리는 <b>D27</b> ①이 <b>«표준이 아니라 표류»</b> 로 판정해 트리에서 뺐다. 트리에 있는 <code>exception</code> 모듈은 <b><code>domain_layer/&lt;aggregate&gt;/exception.py</code> 하나뿐</b>이다. <b>검사는 멀쩡하다</b> — 둘째 줄이 «경로»가 아니라 <b>«모듈 이름»</b> 을 앵커로 쓰므로(<em>「<code>exception</code> 말고는」</em> · <b>D11</b> 검사표의 <code>domain_layer/**/exception</code> 과 같은 어법) 이 자리를 그대로 통과시킨다. <b>고친 것은 예제 한 줄이다.</b></span>
<b>실측</b> — 현행에서 <b>둘 이상의 애그리거트가 함께 쓰는 값 객체 156개</b> 중 <b>81개</b>가 도메인 것을 import 한다(값 객체 67 · 예외 53 · 그 밖 7). <b>절반이 위반으로 찍혔다.</b><br>
<b>다만 범위를 제한한다</b> — <code>&lt;aggregate&gt;/value_object/</code> 는 <b>여전히 못 본다</b>. 공유 자리가 특정 애그리거트에 묶이면 «공유»가 아니게 되고, 잡동사니 통을 막던 힘도 같이 풀린다. 애그리거트·리포지토리·포트·이벤트·프레임워크는 <b>그대로 전부 금지</b>다.</dd>
<dt>둘째 줄이 핵심 안전장치다</dt>
<dd>이게 없으면 공유 자리가 <b>잡동사니 통</b>이 된다. 그리고 이건 <code>boundary/</code> 안을 갈랐던 그 축 — <b>선언(리프) vs 구현(뿌리)</b> — 이 다시 나온 것이다.</dd>
<dt>왜 <code>shared_</code> 를 붙이나</dt>
<dd><b>비대칭이 맞다.</b> 안쪽은 <code>value_object/</code>(기본값 = 그 애그리거트 것), 바깥은 <code>shared_value_object/</code>(예외 = 공유). 표시는 <b>예외에만</b> 붙는다 — 깊이 관습을 몰라도 이름만으로 구분된다. <b>이름이 검사 규칙을 그대로 말하고</b>(shared = 누구나 import 가능 + 리프), 애그리거트 하나만 쓰는 VO 를 넣으려는 순간 <em>«이게 정말 shared 인가»</em> 를 이름이 되묻는다.<br><span class="dim">기록해 둘 것 — DDD 에서 <b>Shared Kernel</b> 은 <em>BC 사이</em> 패턴이라 «shared»가 그쪽으로 읽힐 여지가 있다. 다만 여기는 <code>domain_layer/</code> 안이고 <code>_value_object</code> 로 종류가 못 박혀 혼동 여지는 작다고 봤다.</span></dd>
<dt>선언의 <b>모양</b>도 규칙이다 <span class="dim">08-04 보강</span></dt>
<dd><b>리포지토리는 애그리거트를 주고받는다.</b> <code>get(id) -&gt; Aggregate</code> · <code>save(aggregate)</code>. <b>필드 단위 갱신 메서드를 두지 않는다</b>(<code>update_status(id, status)</code> 같은 것).<br>Evans 가 리포지토리를 «메모리 안의 컬렉션 같은 착각»이라 한 게 이 뜻이다 — <b>컬렉션은 객체를 주지 필드를 갱신해주지 않는다</b>. 이 모양이면 «애그리거트를 건너뛰고 상태를 바꾸는» 경로가 <b>애초에 존재하지 않는다</b> — <code>save(order)</code> 를 부르려면 손에 <code>Order</code> 가 있어야 하고, 그러려면 <code>get()</code> 으로 불러와 메서드를 부를 수밖에 없다. <b>규칙을 문서가 아니라 시그니처가 지킨다.</b></dd>
<dt>덤 — Factory 자리가 저절로 생긴다</dt>
<dd>Evans 의 building block 중 <b>Factory</b> 는 지금까지 트리에 자리가 없었다. 복잡한 애그리거트 조립은 <b>그 애그리거트 폴더 안</b>이다 — 축을 바꾸니 따라온다.</dd>
<dt>안 채택한 원전 노선 — 애그리거트 사이 참조는 «id 로만»</dt>
<dd><span class="dim"><b>Vernon</b>(IDDD)은 애그리거트 사이 참조를 <b>식별자로만</b> 하라는 노선이다. 이 트리는 <b>Evans 준거</b>라 직접 객체 참조를 규칙으로 막지 않는다 — 세우지 않은 것은 «누락»이 아니라 <b>선택</b>임을 적어 둔다(3차 리뷰 D-7).</span></dd>
<dt>기각한 대안</dt>
<dd><b>⒜ 종류 1차</b>(<code>entity/</code>·<code>value_object/</code>·<code>repository/</code>) — 도메인 안에서 «package by layer»를 한 번 더 하는 것이다. <code>Order</code> 규칙 하나가 바뀌면 <b>세 폴더를 연다</b>. 무엇보다 애그리거트 경계를 트리 말고 <em>무엇으로</em> 표시할지가 남아 <b>P1 이 안 닫힌다</b>.<br><b>⒝ 공유 VO 금지 + 애그리거트마다 복제</b> — <code>Money</code> 는 <b>같은 도메인 지식</b>이라 모으는 쪽이 맞다(«불일치 위험이 큰 지식의 중복은 더 일찍 모아도 된다»).</dd>
</dl>

## D13 · 애그리거트 밖에 남는 것 · 그리고 이 칸을 닫는 두 줄

**확정 · 08-06** · 자리 — ① 칸 &nbsp;·&nbsp; ③ 화살표 &nbsp;·&nbsp; ④ 앎의 범위 &nbsp;·&nbsp; 닫는 문제 <b>P5</b>

<dl class="kv">
<dt class="ans-dt">결정 ① 칸</dt>
<dd class="ans-dd filled"><code>&lt;aggregate&gt;/</code> 형제로 <b><code>domain_service/</code></b>, 애그리거트 안에 <b><code>&lt;aggregate&gt;/event/</code></b>. <b>현행의 <code>specification/</code>·<code>exception/</code>·<code>port/</code> 는 안 가져온다.</b>
<span class="dim">(<code>exception</code> 은 <em>폴더</em>를 안 가져온다는 뜻이고 <b>D27</b> 이 <code>exception.py</code> <em>파일</em>로 되살렸다.)</span><br>
<span class="dim">→ <b><code>port/</code> 를 없애는 이 결정은 플러그인이 «결정적 blocker» 로 정반대를 못 박은 것과 충돌한다</b>(<b>D32</b> 의 «플러그인이 정반대를 못 박고 있다» 절). <b>몰라서 어긋난 게 아니라 알고 이긴 것</b>이고, 이행은 <b>플러그인 먼저 → 코드 나중</b> 순서다.</span></dd>
<dt>왜 <code>domain_service/</code> 인가 — 주인이 없는 규칙이 있다</dt>
<dd>이체는 <b>어느 계좌의 규칙도 아니다</b>. «잔액이 모자라면 안 된다»는 A 것, «받으면 늘어난다»는 B 것인데 «이체»라는 규칙 자체는 두 애그리거트 사이에 걸쳐 있다. 자리가 없으면 셋 중 하나로 가고 <b>셋 다 나쁘다</b> — ⒜ 억지로 A 안에(<b>경계가 뚫린다</b>) ⒝ <code>application_layer</code> 로(<b>도메인이 빈혈이 된다</b>) ⒞ 아무 유틸 파일(<b>아무도 못 찾는다</b>).</dd>
<dt>도메인 서비스 ≠ 유스케이스</dt>
<dd>둘은 닮아 보이고, 여기가 무너지면 도메인이 껍데기가 된다. 도메인 서비스는 <b>«이체란 무엇인가»</b>, 유스케이스는 <b>«사용자가 이체를 요청하면 무슨 일이 일어나는가»</b>다.<br><b>판별법 한 줄 — 불러오거나 저장하면 그건 유스케이스다.</b> 다르게 말하면 <b>도메인 서비스는 DB 없이 순수하게 테스트된다</b>. 이 선이 검사 규칙 ③으로 그어진다.<br><span class="dim">남용 방지선 — 한 애그리거트로 표현되면 거기 넣는다. 정말 둘 이상에 걸칠 때만 여기다(Evans 본인의 경고).</span></dd>
<dt>②③에 면제를 넣었다 — <b>규칙이 자기가 지키려던 코드를 위반으로 찍고 있었다</b> <span class="dim">08-06 개정 · R3</span></dt>
<dd><b>③의 의도는 옳다</b> — 리포지토리를 import 못 하면 <em>불러올 수가 없고, 받을 수밖에 없다</em>. 그래서 「불러오거나 저장하면 그건 유스케이스다」가 구조로 강제된다.
<b>그런데 «애그리거트 루트만»은 시그니처를 쓰는 순간 깨진다.</b>
<div class="pre-wrap"><pre><code># domain_layer/domain_service/transfer_service.py
from ..account.account import Account         # 애그리거트 루트 — 통과
from ..shared_value_object.money import Money # 값 객체 — 옛 규칙이면 위반
from ..exception import InsufficientBalance   # 예외  — 옛 규칙이면 위반

def transfer(source: Account, target: Account, amount: Money) -&gt; None:
    if source.balance &lt; amount:
        raise InsufficientBalance(...)</code></pre></div>
<b><code>Money</code> 없이는 «얼마를»을 쓸 수가 없다.</b> 인자를 <code>Decimal</code> 로 쓰면 그건 도메인 서비스가 아니라 계산 함수다.<br>
<b>실측 — 규칙이 잡으려던 것은 0건, 대신 정상 코드를 잡았다.</b>
<div class="pre-wrap"><pre><code>도메인 서비스 44파일 중 28파일이 domain_layer 를 import · 총 67건

  값 객체        36   ← 면제 대상
  예외           16   ← 면제 대상
  애그리거트 루트   12   ← 옛 규칙에서 통과한 것은 67건 중 이것뿐
  포트 선언        1   ← R5 로 넘긴다(도메인 서비스가 포트를 쓸 수 있나)
  내부 엔티티       1   ← 진짜 위반 · 고칠 목록으로
  도메인 서비스     1   ← 진짜 위반 · 고칠 목록으로

  리포지토리 import  0   ← 이 규칙이 막으려던 것. 애초에 한 건도 없었다</code></pre></div>
<b>면제 한 줄</b> — <em>같은 <code>domain_layer</code> 의 <code>value_object</code> 와 <code>exception</code> 은 예외다</em>. 둘은 <b>협력자가 아니라 자료</b>라서(불변 · 저장소를 안 건드림 · 불러도 상태가 안 바뀜) 규칙이 막으려던 일을 <b>하나도 가능하게 만들지 않는다</b>. <b>D11</b> 을 08-06 에 좁힌 것과 <b>같은 자</b>다.<br>
<b>막으려던 것은 그대로 다 막힌다</b> — 리포지토리 선언 · 내부 엔티티 · 포트는 <b>여전히 금지</b>이고, 「도메인 서비스는 애그리거트를 <em>받는다</em>」도 그대로 산다.</dd>
<dt>도메인 서비스는 애그리거트를 <b>«인자로 받는다»</b> <span class="dim">08-04 명시</span></dt>
<dd><b>새 규칙이 아니라 검사 규칙 ③ 의 귀결이다.</b> 리포지토리를 import 못 하니 <b>불러올 수가 없고, 받을 수밖에 없다</b> — «결과»로만 있던 것을 «의도»로 적어둔다.<br>그래서 <b>갈림선은 «순수한가»가 아니라 «무엇을 받는가»</b> 다. 도메인 서비스는 <b>애그리거트</b>를 받고(이미 손에 있으니 불러올 일이 없다), 유스케이스는 <b>id·원시값</b>을 받는다(DTO 니까 — 그래서 반드시 불러와야 한다).<br><span class="dim"><b>08-09 · T43 — 이 줄이 «폐쇄 목록»으로 굳어 트리에 옮겨 갔다.</b>
여기서 막는 것은 <b>애그리거트</b> 하나이고 「id·원시값」은 그 <b>대비</b>다. 그런데 <code>command</code> 칸에 <b>「원시값과 id 로만 이루어지고」</b> 로 적히면서
<b>들어오는 흐름(<code>Iterator[bytes]</code>)까지 떨어뜨렸다</b> — 업로드가 갈 통로가 없어진 까닭이 여기다.</span><span class="dim">구멍 하나 — 타입 힌트 없이 리포지토리를 <em>파라미터로</em> 받으면 import 없이 빠져나갈 수 있다. 시그니처 타입을 강제하면 같이 닫힌다.</span></dd>
<dt>그럼 <b>애그리거트를 쓰는 유스케이스</b>와 뭐가 다른가</dt>
<dd>둘 다 애그리거트를 만지지만 <b>거의 모든 축이 다르다</b>.
<div class="pre-wrap"><table class="mini"><tr><th></th><th>도메인 서비스</th><th>유스케이스</th></tr>
<tr><td>입력</td><td><b>애그리거트</b></td><td>id · 원시값(DTO)</td></tr>
<tr><td>애그리거트를 어떻게</td><td><b>받는다</b></td><td><b>불러온다</b>(리포지토리)</td></tr>
<tr><td>저장</td><td>안 한다</td><td>한다</td></tr>
<tr><td>트랜잭션</td><td><b>모른다</b></td><td>긋는다(UnitOfWork)</td></tr>
<tr><td>반환</td><td>도메인 값 · void</td><td>DTO</td></tr>
<tr><td>테스트</td><td><b>아무것도 없이</b></td><td>가짜 포트가 필요</td></tr>
<tr><td>단위</td><td><b>재사용</b> — 여러 유스케이스가 공유</td><td><b>진입점</b> — 시나리오 하나</td></tr>
<tr><td><b>바뀌는 이유</b></td><td><b>업무 규칙이 바뀔 때</b></td><td><b>절차가 바뀔 때</b></td></tr></table></div>
마지막 줄이 제일 깊다 — «이체 수수료 계산이 바뀐다»면 도메인 서비스, «이체할 때 알림도 보낸다»면 유스케이스다. <b>규칙이 바뀌면 도메인, 절차가 바뀌면 응용.</b></dd>
<dt>이름을 <code>service/</code> 로 줄이지 않는다</dt>
<dd><code>open_host_service/&lt;service&gt;_service.py</code> 가 이미 있어 «서비스»가 두 뜻으로 읽힌다. <code>domain_layer/</code> 안이라 <code>domain_</code> 이 중복처럼 보이지만 <b>혼동 방지 값이 더 크다</b>.</dd>
<dt>§0-4(1차 폴더는 도메인 이름만)와 부딪히지 않는다</dt>
<dd>«1차 폴더는 도메인 이름만»은 <b>애그리거트에 속한 것</b>에 걸린다. <code>shared_value_object/</code> 도 같은 이유로 종류 이름을 쓴다 — <b>주인이 하나가 아닌 것은 종류로 이름 붙는다.</b></dd>
<dt>왜 <code>event/</code> 인가 — 직접 부르면 셋이 한꺼번에 깨진다</dt>
<dd><code>Order.place()</code> 안에서 재고·회원·알림을 직접 부르면 <b>남의 애그리거트를 만지고</b>, 트랜잭션이 셋으로 부풀고, <b>주문이 재고를 알게 된다</b>. 그래서 방향을 뒤집는다 — <b>이벤트는 명령이 아니라 사실이다.</b> <code>ReduceInventory</code>(재고를 줄여라)가 아니라 <code>OrderPlaced</code>(주문이 완료됐다). 사실만 남기니 <b>발행자가 구독자를 모른다</b> — 쿠폰 발급이 붙어도 <code>Order</code> 는 안 바뀐다.</dd>
<dt>수명 — 누가 만들고 누가 소비하나</dt>
<dd><b>만든다</b>: 애그리거트 루트가 <em>기록만</em> 한다(리스트에 append). 메시지 버스를 모르고 I/O 를 안 한다.<br><b>발행한다</b>: 유스케이스가 <b>커밋 뒤에</b>. 먼저 발행했다 롤백되면 «일어나지 않은 일»을 알린 셈이 된다.<br><b>듣는다</b>: 핸들러 = <b>또 하나의 유스케이스</b>(<code>application_layer</code>). 도메인이 아니다 — «불러오고 시키고 저장한다»는 전부 조율이다. 그리고 <b>핸들러가 번역한다</b> — <code>inventory.reduce(sku, qty)</code> 이지 <code>inventory.apply(event)</code> 가 아니다.</dd>
<dt>왜 발행자 폴더 안인가</dt>
<dd><code>OrderPlaced</code> 는 <b>주문의 사실</b>이다 — 주인이 분명하다. 주인이 없어서 형제로 뺀 <code>shared_value_object/</code> 와 처지가 다르다. 그리고 이 모양은 트리에 이미 있다: <code>open_host_service/&lt;service&gt;/contract/</code> 가 똑같다 — <b>발행하는 쪽 옆에 계약을 두고 남이 읽는다.</b></dd>
<dt>다른 BC 는 이걸 직접 못 받는다</dt>
<dd>전역 제약 ③ 에 걸리고, 그래야 맞다 — <b>도메인 이벤트와 통합 이벤트는 다른 물건</b>이다. <code>OrderPlaced</code> 를 그대로 내보내면 <b>남의 BC 가 내 내부 모델에 묶여</b> 필드 하나 바꿀 때마다 깨진다. 번역이 낭비가 아니라 요점이다.<br><span class="dim">정직한 공백 — 그 번역과 발신 채널은 <b>네 칸이 다 닫힌 지금도 트리에 자리가 없다</b>. <code>open_host_service/</code> 는 «남이 나를 부르는» 동기 입구라 방향이 반대다. <b>받는 쪽(「메시지 입구」)과 짝이라 한 칸으로 같이 연다</b> — 선언 자리와는 별개 문제라 이 결정을 막지 않는다.</span><br><b>08-06 닫혔다 — 칸을 열지 않는다</b>(<b>D34</b>). 실측하니 <b>이 저장소에 통합 이벤트가 없다</b> — 비동기 인프라 0 · 채널 1 · 구독자 1 이고, 그 하나도 <b>같은 프로세스 안 함수 호출</b>이다. <b>위 규칙이 그대로 판정한다</b>: 이 BC 안에서 읽는 게 없으면 이벤트가 아니라 알림이고, 알림 자리는 이미 있다.</dd>
<dt>안 가져오는 셋</dt>
<dd><b><code>specification/</code></b> — 블루북 9장의 정식 패턴이지만 <b>구조 요소가 아니라 조건부 관용구</b>다. <b>골격은 «비어도» 실현되므로</b>(제1원칙) 한번 올리면 <b>안 쓰는 애그리거트까지 영구히 그 겹을 진다</b> — 그래서 골격에 오르는 자격은 <b>「모든 애그리거트가 갖는가」</b> 하나다. 폴더 고유 규칙도 없다.<span class="dim"> ← 08-09 · T51 에 근거를 갈았다. 옛 문장은 «빈 한 겹이 생긴다»를 나쁨으로 들었는데, 제1원칙 아래서 빈 것은 <b>정상</b>이다.</span><br><b><code>exception/</code></b> — <b>세 계보 어느 쪽의 building block 도 아니다</b>(언어 기능). 그리고 자리는 이미 정해져 있다: 예외는 <b>불변식 위반의 이름</b>이고 불변식의 주인은 애그리거트다. «어떤 예외가 경계를 넘나»는 <b>BC 경계</b>의 물음이라 <code>contract/exception/</code> 가 이미 답했다.<br><b><code>port/</code></b> — <b>이 칸에서 아예 없앤다.</b> 붙는 포트(리포지토리)는 D12 로 자리가 났고, 안 붙는 포트(시계·게이트웨이·알림)는 <b>도메인 것이 아니다</b> — 도메인 객체가 시계를 부르면 순수해야 할 규칙이 I/O 를 하는 것이다. <b>D2 가 이 칸에서 완전히 빠진다.</b></dd>
<dt class="ans-dt">결정 ③ 화살표</dt>
<dd class="ans-dd filled"><b><code>domain_layer</code> 는 아무것도 import 하지 않는다</b> — 자기 자신 말고는. 나가는 화살표가 <b>0</b> 이다. 애그리거트는 이벤트를 <em>기록만</em> 하고 아무도 부르지 않으므로 <code>event/</code> 를 더해도 안 흔들린다.<br><b>들어오는 화살표</b>: <code>application_layer</code>(유스케이스·핸들러) · <code>driven_layer</code>(리포지토리 구현이 애그리거트를 반환해야 한다) · <code>composition_root</code>. <b><code>driving_layer</code> 는 금지</b>(D11).<br><span class="dim"><b>08-05 재검 — 실은 6건이 나가고 있었다.</b> <code>delivery</code>·<code>notifications</code> 의 도메인이 <code>common/broccoli/notification_navigation</code> 을 부른다. 안 걸린 이유는 하나 — <b>세는 범위가 <code>application/</code> 안이었고 <code>common/</code> 은 트리 밖이었다</b>. <b>D24</b> 가 그 파일을 두 BC 로 가르면서 <b>다시 0 이 된다</b>.</span></dd>
<dt class="ans-dt">결정 ④ 앎의 범위</dt>
<dd class="ans-dd filled"><b>아무것도 몰라도 된다 — 거의 공짜로 정해진다.</b> 전역 제약 ①(의존은 안쪽으로만)과 ②(안쪽은 구체 기술을 모른다)를 합치면 가장 안쪽인 이 칸에는 <b>남는 것이 없다</b>. 프레임워크·ORM·시계·HTTP 전부 모른다.</dd>
<dt>검사 네 줄</dt>
<dd><b>①</b> <code>&lt;A&gt;/**</code> 는 <code>&lt;B&gt;/</code> 의 <b>루트 모듈만</b> import 한다 <span class="dim">— 대상은 «애그리거트 구성원»이다. <code>domain_service/</code> 는 애그리거트 밖이라 해당 없다(08-07 · R10)</span><br>
<b>②</b> <code>shared_value_object/</code> 는 <b>같은 <code>shared_value_object/</code> 안과 <code>exception</code></b> 말고는 import 하지 않는다<br>
<b>③</b> <code>domain_service/</code> 는 <b>애그리거트 루트 · <code>value_object</code> · <code>exception</code> · 같은 폴더의 다른 도메인 서비스만</b> import 한다 — 내부 엔티티도 <b>리포지토리 선언도</b> 안 된다 <span class="dim">— 「같은 폴더」는 08-07 에 더했다(Vernon 의 <code>AuthorizationService</code> → <code>GroupMemberService</code>)</span><br>
<b>④</b> <code>&lt;aggregate&gt;_repository.py</code> 는 <b><code>domain_layer</code> 안에서 아무도 import 하지 않는다</b> — <code>application_layer</code>·<code>driven_layer</code>·<code>composition_root</code> 뿐이다<br>
<span class="dim">②③의 «<code>value_object</code>·<code>exception</code> 면제»는 <b>08-06 에 넣었다</b>(R3) — 아래 절.</span></dd>
<dt>④ 가 왜 필요했나 <span class="dim">08-04 보강</span></dt>
<dd>③ 이 <code>domain_service/</code> 에만 걸려 있어서 <b><code>&lt;aggregate&gt;.py</code> 가 옆에 있는 자기 리포지토리를 import 하는 길이 열려 있었다</b> — 같은 칸 안이라 «나가는 화살표 0» 에도 안 걸린다.<br>그런데 애그리거트가 리포지토리를 부르면 <b>순수해야 할 도메인이 I/O 를 한다</b>. 도메인 서비스에 걸었던 이유가 애그리거트에는 더 강하게 걸린다. <b>선언은 도메인에 살지만 부르는 건 언제나 바깥이다</b> — 이게 드리븐 포트의 정의 그 자체다.</dd>
<dt class="ans-dt">08-06 원전 대조 — <b>검사 ③ 은 원전 밖이다</b></dt>
<dd class="ans-dd filled">Evans 가 SERVICE 에 규정하는 것은 <b>셋뿐</b>이다:
<div class="pre-wrap"><pre><code>1. The operation relates to a domain concept that is not a natural part
   of an ENTITY or VALUE OBJECT.
2. The interface is defined in terms of other elements of the domain model.
3. The operation is stateless.</code></pre></div>
패턴 요약도 같다 — <em>«Define the interface in terms of the language of the model … Make the SERVICE stateless.»</em> <b>조건이 «인터페이스»에 걸리고, 구현이 무엇을 부르는지는 말하지 않는다.</b><br>
<b>그래서 「리포지토리 선언도 import 하지 않는다」는 우리가 더한 것이다.</b> 근거는 <b>D10</b> — 「리포지토리를 들어도 되지만 적당히」는 <b>판정이 안 서고</b>, 「하나도 안 된다」는 <b>grep 한 줄</b>이다.<br>
<b>다만 원전의 예가 방향은 같다</b> — funds transfer 에서 <b>알림을 보내는 건 «응용 서비스»</b>다(Funds Transfer App Service → Send Notification Service). 도메인 서비스(Funds Transfer Domain Service)는 차변·대변 판정만 한다. <b>조율과 인프라 호출은 응용 몫</b>이라는 것이 원전의 배치다.</dd>
<dt>정직한 단서 — 예외 절을 붙였다 뺐다</dt>
<dd>처음엔 규칙 ① 에 «<code>&lt;B&gt;/event/</code> 도 허용» 이라는 예외를 붙이려 했다. <b>필요 없었다</b> — 이벤트를 읽는 건 언제나 <code>application_layer</code> 의 핸들러이고, 핸들러가 값으로 풀어서 애그리거트에 넘긴다. <b>애그리거트가 남의 이벤트를 import 할 일이 없다.</b> 수명을 따져보니 규칙이 오히려 단순해졌다.</dd>
</dl>

## D14 · application_layer 의 1차 축과 구성

**확정 · 08-06** · 자리 — ① 칸 &nbsp;·&nbsp; ② 이름 &nbsp;·&nbsp; ③ 화살표 &nbsp;·&nbsp; <b>자료조사로 정했다</b>

<dl class="kv">
<dt class="ans-dt">결정 ① 칸 · ② 이름</dt>
<dd class="ans-dd filled">1차 <b><code>&lt;area&gt;/</code></b> · 2차 <b><code>&lt;use_case&gt;/</code></b>. 안은 <b><code>&lt;use_case&gt;_use_case.py</code> + <code>{ &lt;use_case&gt;_command.py, &lt;use_case&gt;_result.py }</code></b>. 형제는 <b><code>port/</code></b> 하나다. <b>Input/Output Boundary 와 Presenter 는 넣지 않는다.</b><br>
<span class="dim">→ <b>08-06 개정(R4)</b> — 형제가 둘에서 <b>셋</b>이 됐다. <code>port/</code> 안에 있던 <code>unit_of_work.py</code> 를 <b><code>transaction/</code> 으로 내보냈다</b>. 아래 «UoW 는 포트가 아니다».</span></dd>
<dt>클린이 이 링에 두는 것은 여섯이다</dt>
<dd><b>Interactor · Input Data · Output Data · Data Access Interface · Input Boundary · Output Boundary.</b> 반대로 <b>Controller · Presenter · View Model 은 Interface Adapters 링</b> — 우리 트리의 <code>driving_layer/</code> 다. <span class="dim">출처: Uncle Bob, <em>The Clean Architecture</em> 및 <em>Clean Architecture</em> Part 5.</span></dd>
<dt>왜 유스케이스가 폴더 단위인가</dt>
<dd><b>Screaming Architecture 가 클린의 명시적 답이다</b> — «최상위 디렉터리를 보면 아키텍처가 <em>«의료 시스템»</em> 이라고 외쳐야지 <em>«Rails»</em> 라고 외치면 안 된다». Ch.21 이 반대하는 대상은 <b>프레임워크</b>다 — <em>“Frameworks are tools to be used, <b>not architectures to be conformed to</b>.”</em>
<span class="dim">08-10 · 5차 리뷰 — 옛 문장은 <em>「그리고 <b>package by layer</b>(controllers/services/repositories)를 <b>이름을 들어 반대한다</b>」</em> 였는데, <b>Ch.21 전문과 2011 블로그 전문에 그 어구가 0회</b>다.
<code>controllers</code>·<code>services</code>·<code>repositories</code> 를 폴더 이름으로 든 자리도 0회이고, 블로그의 유일한 근처 문장은 오히려 <em>“those are details that <b>needn't concern you at the moment</b>”</em> 다.
«package by layer» 를 이름 들어 다루는 것은 <b>같은 책 34장, Simon Brown 의 절</b>이다 — <b>바로 아래 dim 이 34장을 「Brown 이 쓴 장」이라 정확히 갈라 적어 놓고도 이 문장의 귀속은 안 고쳐져 있었다</b>.
없는 인용을 만든 탓에 그것을 무마하는 방어 문장(<em>「층 폴더의 전면 금지가 아니고」</em>)이 한 줄 더 필요했다 — Ch.21 의 실제 주장만 쓰면 그 방어가 필요 없다.</span><br>R1 이 이 칸을 <b>클린 구역</b>으로 배정했으므로 이 답을 쓴다. D10 으로도 규칙이 나온다 — <b>폴더 하나 = 유스케이스 하나 = 진입점 하나</b> · <b>DTO 는 자기 폴더 안에서만 쓰인다</b>(유스케이스끼리 DTO 를 돌려쓰는 냄새를 구조가 막는다).<br><span class="dim">«무엇이 1차냐»와는 별개다 — <code>&lt;area&gt;/</code> 도 기술이 아니라 <b>업무</b> 이름이므로 Screaming 은 그대로 성립한다. 아래 참조.</span></dd>
<dt>1차를 <code>&lt;area&gt;/</code> 로 둔다 — <code>api/</code> 와 <b>1:1</b> <span class="dim">08-04 · 원안을 뒤집었다</span></dt>
<dd><b>원안은 <code>&lt;use_case&gt;/</code> 평면이었다.</b> 유스케이스가 BC 당 20개쯤이면 평면이 오히려 읽힌다는 이유였는데, <b>대칭을 택했다</b>.
<div class="pre-wrap"><pre><code>driving_layer/api/&lt;area&gt;/  { &lt;area&gt;_controller.py , schema/{in,out} }
application_layer/&lt;area&gt;/  { &lt;use_case&gt;/{ use_case , {command|query, result} } }</code></pre></div>
<b>안팎이 같은 축으로 갈린다.</b> 컨트롤러의 엔드포인트 하나가 유스케이스 하나를 부르므로, <code>api/order/</code> 를 열면 <code>application_layer/order/</code> 에 짝이 있다 — <b>찾아가는 길이 한 가지</b>가 된다.<br>
Screaming Architecture 는 «최상위가 <em>기술</em>이 아니라 <em>업무</em>를 외쳐야 한다»가 요지다. <code>&lt;area&gt;/</code> 도 업무 이름이므로 <b>어긋나지 않는다</b> — <code>controller/</code>·<code>service/</code> 처럼 종류로 나누는 것이 그 글이 반대한 것이다.
<span class="dim">인용을 마저 적는다 — 같은 책 34장(The Missing Chapter — <b>Martin 이 아니라 Simon Brown 이 쓴 장</b>)은 <b>ports-and-adapters 식 패키징을 정합한 선택지로 함께 든다</b>. 여기서 반대하는 것은 «층 이름 평면 나열»이지 층 폴더의 전면 금지가 아니다.
<b>★ 34장의 결론은 «도구로 강제하라»가 아니다</b> — 축자는 <em>“I would certainly encourage you to <b>lean on the compiler</b> to enforce your architectural principles, <b>rather than relying on self-discipline and post-compilation tooling</b>.”</em> 이고, 그 앞에 <em>“they are <b>fallible</b>, and the <b>feedback loop is longer than it should be</b>”</em> 가 붙는다.
<b>우리 백스톱(<code>scripts/check-*.py</code>)은 정확히 «post-compilation tooling» 이고 <code>discipline-reviewer</code> 는 정확히 «self-discipline» 이다</b> — Brown 이 이름 들어 물린 그 둘이다.
<b>그리고 그가 컴파일러를 쓸 수 있는 근거는 자바의 package-private 접근 제어인데 파이썬에는 그 기능이 없다</b> — 우리는 그의 1순위를 «안 고른» 것이 아니라 <b>«쓸 수가 없다»</b>. 그래서 치르는 값이 <b>피드백 지연</b>이다: 규칙을 어긴 import 한 줄이 <b>CI 가 도는 다음 번까지, 그리고 그 검사기의 대상 필터에 그 파일이 걸리는 한에서만</b> 잡힌다.
<span class="dim">08-10 · 5차 리뷰 — 옛 문장은 이 인용을 «우리 백스톱이 정확히 그 답이다»로 뒤집어 적어, <b>대가를 계상하지 않고 더 볼 것이 없다고 닫아 놨다</b>.</span></span><br>
<span class="dim">치르는 값 — 한 겹이 깊어지고, 유스케이스가 적은 BC 에서는 <code>&lt;area&gt;/</code> 안에 하나만 들어간다. <b>대칭이 그 값보다 크다고 봤다.</b></span></dd>
<dt>왜 <code>dto/</code> 인가 — 원문이 직접 말한다</dt>
<dd>«경계를 넘는 데이터는 <b>단순한 자료구조</b>다… <b>엔티티나 DB 행을 넘기는 편법을 쓰지 않는다.</b>» <b>D8</b> 이 세운 <code>schema/</code> ↔ 유스케이스 입출력 대칭의 근거가 이 문장이다.</dd>
<dt>Boundary 둘을 빼는 이유 — <b>클린 본인의 잣대다</b></dt>
<dd>부분 경계 장의 문장: «<b>경계를 구현하는 비용과 무시하는 비용 사이에 트레이드오프가 있다</b>. 단순한 시스템에 엄격한 경계를 미리 넣으면 <b>과설계</b>다.»<br><b>Input Boundary</b> — 컨트롤러가 구체 인터랙터에 안 묶이게 하는 장치인데, 우리는 <code>driving_layer</code>(바깥) → <code>application_layer</code>(안쪽)이라 <b>이미 방향이 맞다</b>. 넣으면 유스케이스마다 파일이 하나 늘 뿐 방향은 그대로다.<br><b>Output Boundary + Presenter</b> — 이건 진짜로 방향을 뒤집는다. 원문이 조건을 명시한다: <em>«유스케이스가 안쪽 인터페이스(Output Port)를 «부르고» 바깥의 프레젠터가 그걸 구현한다 — 제어 흐름이 컨트롤러에서 시작해 유스케이스를 거쳐 «프레젠터에서 끝난다»»</em>. <b>흐름이 뒤집힐 때</b> 쓰는 장치다. 우리는 컨트롤러가 유스케이스의 출력을 <b>당겨오므로</b> 방향이 이미 맞다.</dd>
<dt>대신 «필요해지는 순간»을 적어둔다 <span class="dim">08-06 정정 · R7</span></dt>
<dd><b>제어 흐름이 «유스케이스 → 프레젠터»로 뒤집히는 출력</b>이 생기면 그때 꺼낼 패턴이 <b>Output Boundary + Presenter</b> 다. 자리를 미리 비워두는 게 아니라 <b>신호를 기록</b>해 둔다.<br>
<span class="dim">※ 08-04 에는 이 조건을 <b>«밀어내는 출력이 생기면»</b>이라 쓰고 <em>「요청 하나에 응답 하나인 API 에는 밀어낼 일이 없다」</em>고 단정했다. <b>그 단정이 사실과 달랐다</b> — 이 저장소에 <code>ai_chat</code> SSE 가 있다. 다만 <b>판단 자체는 옳았다</b>: 지금은 컨트롤러가 <b>당겨오는</b> 모양이라 흐름이 안 뒤집혔고, 그래서 Presenter 는 여전히 필요 없다.</span></dd>

<dt class="ans-dt"><b>Presenter 는 «칸»이 아니라 «경계마다 되풀이되는 모양»이다</b> <span class="dim">08-09 · T46</span></dt>
<dd class="ans-dd filled"><b>4차 리뷰가 「알림·메일 본문을 빚는 자리가 Presenter 인데 그 칸을 안 만들었다」를 major 로 올렸다.</b>
<b>원전을 보면 그 처방이 안 선다</b> — Martin 은 Presenter 를 <b class="v c">Humble Object</b> 의 <b>«한 사례»</b>로 들고,
<b>Service Listeners · Database Gateways · Data Mappers 를 나란한 사례로</b> 든다. <b>칸의 이름이 아니라 경계의 모양이다.</b>
<div class="pre-wrap"><pre><code>Presenter          “if the application wants a date displayed in a field, it will hand
                   the Presenter a Date object. Then the Presenter will format that data
                   into an appropriate string and place it in … the View Model.”

Service Listeners  “the application will load data into simple data structures and then
                   pass those structures across the boundary to modules that properly
                   format the data and send it to external services.”
                   ← 바깥 서비스로 «나가는» 경우를 Martin 이 따로 적어 두었다</code></pre></div>
<b>그 모양은 우리 트리에 이미 넷 서 있다</b> — <code>&lt;area&gt;_controller.py</code>+<code>schema_out.py</code> ·
<code>adapter/</code> · <code>open_host_service/</code> · <code>admin/</code>+<code>templates/</code>.
<b>없던 것은 «칸»이 아니라 그 경계에 걸린 «규칙»이었다.</b></dd>

<dt class="ans-dt"><b>그래서 사람이 읽을 «문구»는 안쪽을 지나가지 못한다</b> <span class="dim">08-09 · T46</span></dt>
<dd class="ans-dd filled"><b>물음은 한 줄이었다 — 「취소 확인 메일을 보낼 때 <code>CancellationNotice</code> 안에 뭐가 드나」.</b>
<div class="pre-wrap"><pre><code>✗ CancellationNotice(to=…, subject="주문이 취소되었습니다",
                      body="홍길동님, 환불 32,000원은 3영업일 내…")

✔ CancellationNotice(to=…, order_number="A-12345", refund_amount=Money(32000,"KRW"),
                      reason_code=CancellationReason.CUSTOMER_REQUEST, locale="ko")</code></pre></div>
<b>원전 셋이 각각 다른 이유로 같은 답을 준다.</b>
<div class="pre-wrap"><table class="mini">
<tr><th>원전</th><th>무엇을 정하나</th></tr>
<tr><td><b>Martin</b> — 위 Service Listeners</td><td><code>refund_amount</code> 는 <b><code>Money</code> 객체</b>다. <span class='no'>"32,000원"</span> 은 <b>format 의 결과</b>라 경계 «너머» 것이다</td></tr>
<tr><td><b>Cockburn</b> — <em>“architect the interfaces <b>by purpose rather than by technology</b>… technologies be <b>substitutable</b> by adapters”</em></td><td><b><code>subject</code>·<code>body</code> 가 없다.</b> 넣는 순간 그 포트는 «메일 전용»이 되어 <b>문자·푸시 어댑터로 못 간다</b> — 그가 고치라는 바로 그 병이다</td></tr>
<tr><td><b>Vernon</b> — <em>“Textual descriptions are generally valid <b>only in the User Interface Layer</b>… must be <b>localized</b>…, making this <b>inappropriate to support in the model</b>”</em></td><td><code>reason_code</code> 는 <b>enum «이름»</b>이다. 그 설명 문구(<em>“고객 요청으로 취소”</em>)를 enum 에 <b>필드로 달지 않는다</b></td></tr>
<tr><td><b>Evans</b> — UI 층은 <em>“Responsible for showing information to the user… The external actor might sometimes be <b>another computer system</b> rather than a human user”</em></td><td>메일 어댑터는 <code>driven_layer</code> 에 있어도 <b>하는 일은 UI 층 일</b>이다 — 거기서 문구를 빚는 것이 <b>층 위반이 아니다</b></td></tr></table></div>
<b>★ 그리고 이 자는 트리에 이미 두 자리 있었다</b> — <code>bc_error_schema.py</code> 의 <b>「바깥이 분기해야 하는 것은 «코드»지 메시지가 아니다」</b> 와
<code>open_host_service/…/exception/</code> 의 <b>「못 해 준 사유는 «코드»로 담는다 — 문장이 아니다」</b>.
<b>«나가는» 페이로드에만 안 걸려 있었다.</b> <span class="dim">T38·T43·T45 와 네 번째로 같은 모양이다.</span></dd>

<dt>실증 — 장고가 ㉠을 «조용히 틀리게» 만든다</dt>
<dd>이건 취향 문제가 아니다. 우리 트리는 메일을 <code>uow.after_commit(...)</code> 으로 <b>커밋 뒤</b>에 보내는데,
장고 공식 문서는 <em>“activating a translation catalog is done on a <b>per-thread basis</b>”</em> 라고 적는다.
<div class="pre-wrap"><table class="mini">
<tr><th>유스케이스가 <code>gettext()</code> 를 부르면</th><th>결과</th></tr>
<tr><td>관리자가 고객 주문을 <b>대신 취소</b></td><td>활성 로케일이 <b>관리자 것</b> → 한국어 고객에게 영어 메일</td></tr>
<tr><td>발송을 <b>워커로 이관</b></td><td>활성 로케일이 <b>아예 없음</b> → 서버 기본값으로 샌다</td></tr></table></div>
<b>둘 다 예외도 경고도 안 난다.</b> 고치는 법은 어댑터가 <code>with translation.override(notice.locale):</code> 로 감싸는 것이고,
<b>그러려면 로케일이 «값»으로 실려 와야 한다</b>. <span class="dim">D45 가 금지하는 «판정»은 «업무» 판정이라(08-09 · T45) 로케일로 판을 고르는 것은 안 걸린다.</span></dd>

<dt class="ans-dt"><b>포트 페이로드를 «방향»으로 가른다</b> — 형제 셋 중 여기만 안 갈랐었다 <span class="dim">08-09 · T46</span></dt>
<dd class="ans-dd filled"><b>사용자가 짚었다</b> — <em>「다른 곳들은 <code>request</code>·<code>response</code> 로 들어가는 것과 나가는 것을 구분하잖아. 여기도 구분하는 게 좋다고 생각하는데」</em>.
<b>맞고, 내가 든 반론 셋이 다 무너졌다.</b>
<div class="pre-wrap"><table class="mini">
<tr><th>내 반론</th><th>검증</th></tr>
<tr><td>「같은 자료가 양쪽에 쓰일 수 있다」</td><td><b>플러그인이 이미 풀어 놨다</b> — <em>「request·response 양쪽 필드에 쓰이는 타입은 <b>response_contract 가 소유하고 request 연산 파일이 import</b>한다」</em></td></tr>
<tr><td>「아예 0개일 수도 있다」</td><td>OHS 도 <em>「<code>None</code> 반환 연산은 파일 없음」</em> 이다. 같은 조건인데 <b>저기는 갈랐다</b></td></tr>
<tr><td>「방향은 포트 시그니처가 이미 말한다」</td><td><b>자기부정이다</b> — 유스케이스 시그니처도 <code>execute(command) -&gt; result</code> 인데 <b>거기선 갈랐다</b></td></tr></table></div>
<b>실측도 사용자 쪽이다</b> — <code>schema_in</code>/<code>schema_out</code> · <code>command</code>/<code>result</code> · <code>request/</code>/<code>response/</code> · <b><code>&lt;payload&gt;_payload.py</code> ← 넷 중 셋이 가르고 여기만 안 갈랐다.</b>
<span class="dim">★ 그리고 이건 «결정»이 아니라 «규정이 없던 것»이었다 — 내가 그걸 의도된 설계처럼 사후 정당화했다.</span></dd>

<dt>낱말은 <code>_in</code>/<code>_out</code> — <b><code>_request</code>/<code>_response</code> 를 쓰면 방향이 «반대»가 된다</b></dt>
<dd><div class="pre-wrap"><pre><code>OHS   request  = 남이 «우리에게» 보내는 것      (들어온다)
포트   request? = 우리가 «남에게» 보내는 것      (나간다)   ← 같은 낱말이 반대 방향</code></pre></div>
<b><code>_in</code>/<code>_out</code> 은 형제 셋과 기준점이 같다</b> — 전부 <b>«그 자리의 안쪽»</b> 기준이다(<code>command</code> 은 유스케이스로, <code>schema_in</code> 은 컨트롤러로, 포트 <code>_in</code> 은 우리에게 들어온다).
<b>트리 순서는 «흐름 순서»</b>라 포트는 <code>_out</code> 이 먼저다 — 우리가 «건네고» 바깥이 «답한다».
<br><b>클래스에는 접미사를 안 단다</b> — <code>CancellationNotice</code> ✔ · <span class='no'>…Payload</span> ✗ · <span class='no'>…Out</span> ✗. 파일이 이미 종류와 방향을 말했다(D41).</dd>

<dt><b>폴더가 아니라 «파일»로 가른 이유</b> — <b>D54</b> 가 답을 정했다</dt>
<dd>처음엔 <code>payload/</code> 폴더 + <code>_in</code>/<code>_out</code>(<code>dto/</code> 와 같은 꼴)이 유력했다.
<b>그런데 제1원칙이 서면서 그 안이 탈락했다</b> — <code>payload/</code> 는 <b>고정 이름</b>이 되어 <b>«모든» <code>&lt;capability&gt;/</code> 가 영구히 그 겹을 진다</b>.
페이로드는 「<b>원시값·값 객체로 안 될 때만 생긴다</b>」라 <b>모든 능력이 갖는 구조 요소가 아니다</b>.
<b><code>specification/</code> 을 골격에 안 올린 것과 «같은 자»</b>다.
<span class="dim">제1원칙은 「칸을 막 만들어도 된다」가 아니라 정반대다 — <b>비어도 영구히 존속하므로 골격에 칸 하나 올리는 값이 더 비싸다</b>.</span>
<br><b>같은 갈래가 <code>port/domain_bypass_query/</code> 에도 그대로 걸린다</b> — 조회도 «조건»을 건네고 «결과»를 받으므로 두 파일이다. <b>트리 125 → 127행.</b></dd>

<dt>딸려 온 것 — 트리 한 줄과, 안 여는 칸</dt>
<dd><b>연 것은 하나다</b> — <code>django_&lt;bounded_context&gt;/templates/&lt;bounded_context&gt;/&lt;capability&gt;/&lt;template&gt;.html</code>.
<b>어드민 템플릿의 형제</b>이고, 갈리는 것은 «누가 여는가»뿐이다(저기는 장고 어드민, 여기는 <code>external_system/</code> 어댑터).
<br><b>안 연 것</b> — <code>Accept-Language</code> 를 받는 자리는 <b>안 만든다</b>. <code>bc_error_schema.py</code> 가 메시지가 아니라 «코드»를 내보내므로
<b>번역은 부르는 쪽 몫</b>이고, 우리가 로케일을 알아야 하는 것은 <b>«우리가 사람에게 직접 닿을 때»</b>뿐이다.</dd>

<dt class="ans-dt"><b>«흐름»을 내보내는 유스케이스 — <code>result</code> 은 개수를 정하지 않는다</b> <span class="dim">08-06 · R7</span></dt>
<dd class="ans-dd filled"><b>원전이 형태를 못 박지 않는다.</b>
<div class="pre-wrap"><pre><code>“Typically the data that crosses the boundaries is simple data structures.
 You can use basic structs or simple Data Transfer objects if you like.
 Or the data can simply be arguments in function calls.
 Or you can pack it into a hashmap, or construct it into an object.”

“The important thing is that isolated, simple, data structures are passed
 across the boundaries. We don't want to cheat and pass Entities or Database rows.”</code></pre></div>
«Typically»이고 형태를 <b>넷</b> 열어 놨다. <b>금지선은 「엔티티·DB 행」 하나</b>이고, 「유스케이스는 객체 하나를 <code>return</code> 한다」는 말은 없다.
즉 <code>result</code> 은 <b>«나가는 자료의 모양»</b>이지 <b>«몇 개를 내보내는가»</b>가 아니다.<br>
<b>그래서 스트리밍 유스케이스는 특별대우가 필요 없다</b> — 흐름을 돌려주고, 흐르는 알맹이가 <code>result</code> 이면 된다.
<div class="pre-wrap"><pre><code>class StreamTurnUseCase:
    def execute(self, request) -&gt; Iterator[TurnEventResult]:
        subscription = self._subscription_port.attach(request.turn_id)
        try:
            for event in subscription:          # StreamEvent — 도메인 값 객체
                yield TurnEventResult.of(event)    # result 으로 빚어서 내보낸다
        finally:
            subscription.close()                # 자원은 «안»에서 열고 «안»에서 닫는다</code></pre></div>
<b>구독 손잡이는 경계를 넘지 않는다.</b> 이게 핵심이다 — 손잡이를 <code>result</code> 에 실으면
<em>열린 파일·소켓과 같은 부류</em>가 되어 <b>닫을 책임이 층을 가로지른다</b>. 유스케이스가 열고 컨트롤러가 닫는 모양은
「엔티티·DB 행」에는 안 걸리지만 <b>더 나쁜 결합</b>이다.<br>
<b>손잡이 «선언»의 자리는 <code>port/</code> 다</b> — 「진행 중인 턴에 붙어 이벤트를 받는다」는 <em>응용이 요구하고 방식은 갈아끼워지는</em> 능력이라서다(스레드+큐 ↔ Redis Stream ↔ DB 폴링). 재접속(<code>resume</code>)이 없었다면 이 추상 자체가 필요 없고 유스케이스가 그냥 <code>yield</code> 하면 된다.<br>
<span class="dim">실무 대조 — 안드로이드 클린 아키텍처는 유스케이스가 <code>Flow</code>·<code>Flowable</code> 를 돌려주는 것이 기본형이다. 「DTO 하나」로 못 박은 구현이 오히려 소수다.</span><br>
<b>이건 SSE 예외가 아니라 «흐름을 내보내는 유스케이스» 일반 규칙</b>이다 — 대용량 내보내기도 같은 모양이 된다.
<br><span class="dim"><b>08-09 · T43 — 이 문단은 맞는데 «주어»가 트리로 안 따라갔다.</b> 여기 적은 것은 <b>「유스케이스가 열고 컨트롤러가 닫는 모양」</b> 인데,
<code>dto/</code> 칸 설명으로 올라가면서 <b>「살아 있는 자원 핸들도 안 된다」</b> 가 되어 <b>«누가 열었나»가 사라졌다</b>.
그 문장이 <b>들어오는 업로드까지 막았고</b>, 남는 길이 <code>bytes</code> 전량 읽기 하나였다.</span></dd>

<dt class="ans-dt"><b>«흐름»을 받는 유스케이스 — 판정은 「연 쪽이 닫나」다</b> <span class="dim">08-09 · T43</span></dt>
<dd class="ans-dd filled"><b>나가는 쪽만 열어 두고 들어오는 쪽은 규정 자체가 없었다.</b> 500&nbsp;MB CSV 업로드에 남는 길이 하나뿐이었다 —
<code>command(content=file.read())</code>, 전량 메모리.
<div class="pre-wrap"><pre><code>「이 손잡이를 «연 쪽»이 «닫기»까지 하나?」

✔ 유스케이스가 열고 유스케이스가 닫는다    result  Iterator[&lt;UseCase&gt;Result]   ← 위 절이 이미 적었다
✔ 프레임워크가 열고 프레임워크가 닫는다     command   Iterator[bytes]           ← 여기가 빈 자리였다
✘ 한쪽이 열고 «받는 쪽»이 닫아야 한다       위반                              ← 원래 막으려던 것</code></pre></div>
<b>둘째 줄이 성립하는 근거는 장고 소스에 있다</b> — <code>HttpRequest.close()</code> 가 <code>_files</code> 를 순회하며 전부 닫고,
<code>core/handlers/base.py</code> 가 그것을 <code>response._resource_closers</code> 에 걸어 둔다. <b>업로드는 장고가 열고 장고가 닫는다</b> — 유스케이스는 닫을 책임을 지지 않는다.
<div class="pre-wrap"><pre><code>def import_lessons(self, file: UploadedFile = File(...)):          # 컨트롤러 — 세 줄 그대로
    result = self._use_case.execute(ImportLessonsCommand(chunks=file.chunks()))
    return ImportLessonsOut(key=result.key)</code></pre></div>
<code>File.chunks()</code> 는 제너레이터라 <b><code>Iterator[bytes]</code> 는 순수 파이썬 타입</b>이다 — <b>전역 제약 ②를 안 건드린다</b>.
정작 막아야 할 것은 <code>ninja.files.UploadedFile</code>(장고 <code>UploadedFile</code> 의 서브클래스)이 <b>dto 필드 타입으로 들어오는 것</b>이고,
그건 <b>원전의 둘째 금지선</b>이 이미 잡는다 — <em>“We don’t want the data structures to have any kind of dependency that violates The Dependency Rule.”</em>
<br><b>리뷰의 처분안(「입구가 먼저 저장하고 dto 는 «키»만 든다 → D11 허용 목록을 한 줄 연다」)은 안 받는다.</b> 셋이 걸린다 —
⑴ <b>문제를 D11 쪽으로 옮길 뿐</b>이고 그 표면은 T39 에서 겨우 «허용 목록»으로 못 박은 자리다
⑵ <b>저장 실패를 컨트롤러가 다뤄야 해서</b> 세 줄과 충돌한다(「받아 둔다」가 업무 단계면 그건 유스케이스다)
⑶ <b>「먼저 저장」하려면 그 저장에 바이트가 필요하니 원점</b>이다.
<br><b>2단계(받아 둔다 → 나중에 처리한다)도 새 규칙이 0이다</b> — 유스케이스가 청크를 스토리지 포트로 흘려 넣고 <b>«키»를 <code>result</code> 으로</b> 돌려주면
두 번째 단계는 키로 시작한다(<b>D48</b> 의 워커 갈래). <b>새 칸 0 · D11 개정 0.</b></dd>

<dt>원전 대조 — 우리가 더한 것이 무엇인지</dt>
<dd><b>Martin 의 금지선은 둘이고, 「자원 핸들」·「직렬화 가능」·「원시값만」은 그중에 없다.</b>
<div class="pre-wrap"><pre><code>“The important thing is that isolated, simple, data structures are passed across the boundaries.
 We don’t want to cheat and pass Entities or Database rows.
 We don’t want the data structures to have any kind of dependency that violates The Dependency Rule.”

“…many database frameworks return a convenient data format… We might call this a RowStructure.
 We don’t want to pass that row structure inwards across a boundary. That would violate The Dependency Rule
 because it would force an inner circle to know something about an outer circle.”

“So when we pass data across a boundary, it is always in the form that is most convenient for the inner circle.”
                                                          — Martin, The Clean Architecture (2012)</code></pre></div>
<b>두 번째 인용이 우리 문제 그 자체다</b> — 「프레임워크가 «자기에게 편하게» 돌려주는 자료 형식」. <code>UploadedFile</code> 이 정확히 그것이고,
금지 이유는 <b>«자원 핸들이라서»가 아니라 «안쪽이 바깥을 알게 되어서»</b> 다. 그리고 마지막 문장이 <b><code>Iterator[bytes]</code> 를 고르는 이유</b>다.
<br><b>어휘 전수</b> — 원전 두 편(2012 블로그 · 2011 글)에 <code>resource</code>·<code>open file</code>·<code>socket</code>·<code>stream</code>·<code>serializ</code>·<code>primitive</code> 가 <b>전부 0회</b>다.
<br><b>「직렬화 가능해야 한다」는 다른 계보다</b> — Fowler 의 DTO 는 <em>“An object that carries data <b>between processes</b>… It needs to be <b>serializable</b> to go across the connection.”</em> 이고,
<b>Fowler 자신이 로컬 사용을 <em>“actually harmful”</em> 이라 적는다</b>(<em>LocalDTO</em>). 우리는 in-process 라 <b>그 요구가 오지 않는다</b> —
우리 <code>dto/</code> 는 <b>Fowler 계보가 아니라 Martin 계보</b>이고, 근거는 «원격 호출 비용»이 아니라 <b>«의존 규칙»</b> 하나다.
<span class="dim">Vernon 도 DTO 를 <em>[Fowler, P of EAA]</em> 로 인용하며 <em>“albeit often technically unnecessary”</em> 라 적는다.
· 책 <em>Clean Architecture</em> 20장 「Request and Response Models」의 <em>“These data structures are not dependent on anything.”</em> 은 <b>2차 노트 경유</b>라 논거로 쓰지 않는다.</span></dd>
<dt>이벤트 핸들러는 새 칸이 필요 없다</dt>
<dd><b>D13</b> 에서 «핸들러 = 또 하나의 유스케이스»라고 했고 실제로 그렇다 — <b>입력이 이벤트일 뿐 하는 일이 같다</b>. <code>reduce_inventory/</code> 처럼 <b>하는 일로</b> 이름 붙이면 일반 유스케이스와 구분할 이유도 없다.</dd>
<dt class="ans-dt"><b>UoW 는 포트가 아니다 — <code>transaction/</code> 으로 내보냈다</b> <span class="dim">08-06 개정 · R4</span></dt>
<dd class="ans-dd filled"><b>선언의 자리는 «누가 구현하냐»가 아니라 «누구의 어휘냐»가 정한다.</b> 이 트리가 이미 그렇게 서 있다 —
<code>&lt;aggregate&gt;_repository.py</code> 도 DIP 인터페이스이고 바깥이 구현하지만 <code>port/</code> 가 아니라 <b>도메인</b>에 산다. 도메인 어휘라서다.<br>
<b>포트 판정 질문 셋을 대면 UoW 는 두 번째에서 떨어진다.</b>
<div class="pre-wrap"><table class="mini">
<tr><th></th><th>바깥에 행위자가 있나</th><th>시그니처가 업무 어휘인가</th><th>어댑터를 갈면 다른 세계와</th></tr>
<tr><td><code>email_sender</code></td><td>메일 서버 ✔</td><td><code>send(message)</code> ✔</td><td>SMTP ↔ SendGrid ✔</td></tr>
<tr><td><code>clock</code></td><td>시스템 시계 ✔</td><td><code>now() -&gt; Instant</code> ✔</td><td>실제 ↔ 고정 ✔</td></tr>
<tr><td><b><code>unit_of_work</code></b></td><td>DB ✔</td><td><b><code>commit()</code> — 업무 낱말 0</b> ✘</td><td>✔</td></tr></table></div>
<b>더 근본적으로 — UoW 는 «대화»가 아니라 «대화들을 묶는 괄호»다.</b>
<div class="pre-wrap"><pre><code>with self._unit_of_work:                 # 괄호 — 여기서 바깥과 하는 «업무» 대화는 0
    self._order_repository.save(order)   # 대화 — 이게 포트다
    self._stock_repository.save(stock)   # 대화</code></pre></div>
괄호는 대화의 참가자가 아니다. 그리고 <b>이 카드 자신이 아래에서 「UoW 는 커밋 지점을 유스케이스 «안»에 표시하기 위한 것」</b>이라고 적어 놨다 —
<b>«표시»는 조율의 일부이고 조율은 응용의 일</b>이다. 셋이 같은 곳을 가리킨다:
<b>Vernon</b> <em>«Application Services control transactions»</em> · <b>클린</b> 무엇이 한 원자인가는 인터랙터의 조율 ·
<b>헥사고날</b> 포트는 육각형 <em>경계</em>의 장치, UoW 는 육각형 <em>안쪽</em>의 장치.
<br><span class="dim"><b>08-08 · F6 — 자리 결론만 뒤집혔다.</b> <b>D37</b> 이 선언 셋을 <code>port/</code> «아래»로 모으면서 이 폴더는 <code>port/unit_of_work/</code> 가 됐다.
«대화가 아니라 괄호»라는 판정은 그대로 살아 <code>&lt;capability&gt;/</code>(대화 계약)와 형제로 갈린다 — 「포트가 아니다」는 이제 「<b>대화 계약이 아니다</b>」로 좁혀 읽는다.
D37 의 «다시 연 카드» 목록에 이 카드가 빠져 있던 것을 3차 리뷰(T3)가 잡았다.</span></dd>
<dt><b>폴더인 이유</b> <span class="dim">08-06 · R4</span></dt>
<dd><b>⒜ 여럿이 되는 순간 그게 «중대한 사실»이다.</b> UoW 가 여럿일 수 있는 축은 하나뿐이다 — <b>원자성이 «분리된» 저장소가 둘 이상</b>일 때.
(격리 수준·전파 모드는 축이 아니라 같은 경계의 <em>인자</em>이고, 사가·분산 트랜잭션은 UoW 가 아니다.)
보통 하나인 건 맞지만, 둘이 되면 그건 <b>「이 BC 는 원자성이 갈린 저장소를 둘 쓴다」</b>는 뜻이다 —
파일로 못 박으면 트리가 그 말을 못 하고, 폴더면 <code>ls</code> 한 번에 드러난다.
<code>anticorruption_layer/&lt;bounded_context&gt;/</code> 에서 <em>「폴더 목록이 곧 «이 BC 가 누구에게 기대나»」</em>라고 쓴 것과 <b>같은 논리</b>다.<br>
<b>⒝ 슬롯이 반복 가능하면 폴더다.</b> <code>models/&lt;entity&gt;_model.py</code>·<code>migrations/</code> 와 같은 모양이고,
<em>파일 하나로 못 박으면 「경계는 언제나 하나」라는 말을 트리가 하게 된다</em>.</dd>
<dt><b><code>exception.py</code> 는 여기 두지 않는다</b> <span class="dim">08-06 · R4 재수정</span></dt>
<dd><span class="dim">※ 처음엔 <code>transaction/exception.py</code> 를 뒀다가 <b>철회했다</b> — 근거로 든 셋 중 둘이 <em>트랜잭션</em>이 아니라 <em>리포지토리</em> 얘기였다(사용자가 「트랜잭션에 예외가 필요하냐」로 잡았다).</span><br>
<b>Evans 가 리포지토리를 «메모리 안의 컬렉션 같은 착각»이라 한 것이 여기서 결정적이다</b> — 컬렉션은 «바깥 행위자»가 아니라
<b>도메인 모델의 연장</b>이다. 그래서 저장 실패에는 <b>중간이 없고</b>, 셋으로 갈리는데 <b>셋 다 이미 자리가 있다</b>.
<div class="pre-wrap"><table class="mini">
<tr><th>저장이 실패하는 방식</th><th>응용이 다르게 행동하나</th><th>자리</th></tr>
<tr><td><b>업무 의미가 있다</b> — 중복 · 낙관적 락 충돌</td><td>예</td><td><code>domain_layer/&lt;aggregate&gt;/exception.py</code> — <b>어댑터가 번역해서 던진다</b></td></tr>
<tr><td><b>재시도할 수 있나</b></td><td>판정이 필요할 뿐</td><td><code>framework/</code> — <b>BC 마다 다르지 않다</b></td></tr>
<tr><td>그 밖 — 연결 끊김 · 내부 오류</td><td>아니오</td><td><b>선언하지 않는다</b> — framework 가 <b>미식별 500</b> 을 소유한다(<b>D27</b> ③)</td></tr></table></div>
<span class="dim"><b>08-07 · 2차 리뷰 S11 — 근거에서 503 을 뺐다.</b> 옛 문장은 «framework 가 500·503 을 소유한다» 였는데 <b>근거로 단 D27 ③ 목록에 503 이 없다</b>(<code>401·403·404·422·429·HttpError·미식별 500</code>). 503 은 «옆 BC 가 죽음 — 포트 너머» 라 <b>BC 컨트롤러가 포트 실패를 매핑해서 낸다</b>(1장 «실패가 어디서 터지나» 표). 이 표의 줄은 «DB 가 죽음» 이라 <b>애초에 500 쪽</b>이고, 셈은 안 바뀐다.</span>
<b>「중복」과 「낙관적 락 충돌」은 도메인 사실이다</b> — 「이 값은 유일하다」·「내가 읽은 뒤 남이 바꿨다」. 애그리거트 불변식이지 DB 사정이 아니다.
실물로 재보면 남는 게 없다:
<div class="pre-wrap"><pre><code>usage_quota/application_layer/persistence_exception.py  6클래스
  …RecordUniqueConflict  ·  …BucketUniqueConflict  ·  …CasConflict  → 도메인 예외
  …TransientPersistenceError                                        → 어댑터가 가른다 · 이름 안 남김
  …PersistenceInternal                                              → 선언 안 함 · framework 500
  …PersistenceError (기저)                                           → 위가 다 나가면 남을 게 없다</code></pre></div>
<b>그럼 <code>port/&lt;capability&gt;/exception.py</code> 는 왜 필수인가 — 대칭이 아니다.</b>
<div class="pre-wrap"><table class="mini">
<tr><th></th><th>저장소</th><th>바깥 포트</th></tr>
<tr><td>무엇인가</td><td><b>메모리 컬렉션의 착각</b> — 도메인 모델의 연장</td><td><b>바깥 행위자</b> — 도메인이 존재를 모른다</td></tr>
<tr><td>실패를 도메인 어휘로</td><td><b>번역된다</b>(중복·충돌은 도메인 사실)</td><td><b>안 된다</b> — 도메인은 메일도 결제사도 모른다</td></tr>
<tr><td>어댑터를 갈면</td><td>갈 일이 거의 없다</td><td>SMTP → SendGrid. <b>예외 타입이 바뀌면 안 된다</b></td></tr>
<tr><td>응용이 잡아 다르게 행동하나</td><td>거의 아니오</td><td><b>예</b> — 재시도 큐 · 보상 · 부분 성공</td></tr></table></div>
<b>포트는 선언이 없으면 <code>smtplib.SMTPException</code> 이 안쪽까지 올라온다.</b> 저장소는 그 자리에 <b>이미 도메인 예외가 있다.</b></dd>
<dt><b>«BC 당 하나» 제약은 쓰지 않는다</b> <span class="dim">08-06 · R4</span></dt>
<dd>개수는 규칙이 아니라 <b>UoW 의 «모양»이 정한다</b>.
<div class="pre-wrap"><pre><code>모양 A — 경계만 연다             ← 이걸로 못 박는다
  __enter__ / commit / rollback / after_commit(callback)

모양 B — 리포지토리를 노출한다    ← 금지
  uow.payments -&gt; PaymentRepository</code></pre></div>
<b>모양 B 는 클린·헥사고날 원리상 쓰면 안 된다</b> — 유스케이스가 <code>uow.payments</code> 로 리포지토리를 얻으면
<b>생성자 시그니처가 협력자를 말하지 못하게</b> 되고 의존이 UoW 뒤로 숨는다(<b>D6</b>·<b>D11</b> 이 지키려던 것).
모양 B 를 막으면 <b>애그리거트별 변종이 생길 이유가 사라지고</b>, 파일이 하나인 건 강제가 아니라 <b>귀결</b>이 된다.<br>
<b>검사 한 줄</b> — <em><code>transaction/</code> 의 클래스는 리포지토리 타입을 반환하는 멤버를 갖지 않는다</em>.</dd>
<dt>그래도 UoW 자체가 <b>왜 필요한가</b> <span class="dim">08-04 확정</span></dt>
<dd><b>원자성만이면 <code>transaction.atomic</code> 을 그냥 쓰면 된다.</b> UoW 가 자리를 얻는 이유는 둘이고, 둘째가 결정적이다.<br>
<b>⒜ 없으면 <b>D4</b> 가 무너진다</b> — <code>transaction</code> <b>37건</b>이 갈 데가 없어져 «전부 금지»를 못 고르고 «transaction 만 예외»로 타협하게 된다.<br>
<b>⒝ 유스케이스가 «커밋 시점»을 알아야 한다</b> — <b>D13</b> 이 «이벤트는 <b>커밋 뒤에</b> 발행»으로 정했다. 커밋 지점을 알아야 그 뒤가 어디인지 안다.</dd>
<dt><code>port/</code> 안을 어디까지 규정하나 <span class="dim">08-04 · 08-06 재작성</span></dt>
<dd><span class="dim">※ 08-04 에는 판정선이 <b>«항상-생성이 정당화되는가»</b>였고, 그 자로 UoW 만 올렸다. <b>08-06 에 판정선을 «누구의 어휘인가»로 바꿨다</b>(R4) — UoW 는 아예 <code>port/</code> 밖으로 나갔고, 대신 <b>포트 안이 폴더로 규정된다</b>: <code>&lt;capability&gt;/{&lt;capability&gt;.py, exception.py, &lt;payload&gt;.py}</code>. 아래는 08-04 시점 서술이다.</span><br>
처음엔 «<code>port/</code> 안은 규정하지 않는다»로 끝냈는데 <b>거칠었다</b>. UoW 는 나머지 포트와 성격이 다르다.<br>
<b>나머지</b>(시계·게이트웨이·알림·조회 포트) — 그 도메인이 필요할 때만 생기고 이름도 그때그때다. <code>clock.py</code> 를 트리에 올리면 <b>시간을 안 쓰는 BC 에 빈 파일이 항상 생긴다</b> — D7 근거②(값이 비어 있을 축으로는 만들지 않는다)에 걸린다.<br>
<b>UoW</b> — <b>쓰기가 있는 거의 모든 BC 에 있고 BC 당 하나</b>다. 그리고 <b>트리가 이름을 못 박지 않으면</b> 한 BC 는 <code>uow.py</code>, 다른 BC 는 <code>transaction.py</code> 가 되어 «이 BC 의 트랜잭션 경계가 어디냐»를 <b>기계가 못 찾는다</b>. <b>D12</b> 가 <code>&lt;aggregate&gt;_repository.py</code> 를 파일로 올린 것과 <b>같은 논리</b>다 — 이름을 고정해야 검사가 생긴다.<br>
<span class="dim">판정선 — «항상-생성이 정당화되는가». UoW 는 통과하고 나머지 포트는 못 한다.</span></dd>
<dt>그래서 «밖에서 감싸기» 대안이 안 된다</dt>
<dd><b>기각한 대안</b> — 유스케이스는 트랜잭션을 아예 모르게 두고 <code>composition_root</code> 가 <code>atomic</code> 데코레이터로 <b>통째로 감싼다</b>. 유스케이스가 더 순수해지고 포트도 하나 준다.<br>그런데 <b><code>execute()</code> 가 끝나야 커밋된다</b> — 이벤트 발행을 유스케이스 <em>안</em> 에서 할 수가 없고, <b>조율이 유스케이스 밖으로 새어나간다</b>. 그래서 대체가 안 된다.<br><b>UoW 는 «트랜잭션을 걸기 위한 것»이 아니라 «커밋 지점을 유스케이스 안에 표시하기 위한 것»이다.</b></dd>
<dt>정직하게 — Fowler 의 원형이 아니다</dt>
<dd>원 패턴의 핵심은 <b>변경 추적 후 일괄 flush</b> 인데 <b>Django 에는 그 역할이 없다</b> — ORM 이 <code>.save()</code> 즉시 쓴다(SQLAlchemy 세션 같은 게 없다). 우리 것은 <b>⒜ 기술 감추기 + ⒝ 커밋 지점 표시</b> 에 집중한 <b>축소판</b>이다. 이름은 그대로 맞다 — «한 업무 단위의 경계»라는 뜻은 살아 있다.<br><span class="dim">과설계 판정 — 무시하면 D4 와 D13 이 <b>둘 다 깨진다</b>. 반대로 도메인 이벤트도 없고 django 금지도 없었다면 <code>atomic</code> 을 직접 쓰는 게 맞다.</span></dd>
<dt>안 받는 유스케이스도 있다</dt>
<dd><b>읽기 전용은 UoW 를 안 받는다.</b> 조회만 하는데 트랜잭션 경계가 있을 이유가 없다 — 아래 «건너뛰어도 되나»와 같은 선이다.<br><span class="dim">남는 실무 위험 — 리포지토리를 UoW 에 매달지 않으므로(<code>uow.orders</code> 방식을 안 씀) <code>with</code> 밖에서 <code>save()</code> 하는 실수를 <b>구조가 못 막는다</b>. Django 의 <code>atomic()</code> 은 커넥션 단위라 «돌아가긴» 하고 autocommit 으로 샌다. <b>테스트로 막는다</b> — 진입 안 됐으면 터지는 가짜 UoW 하나면 잡힌다. <em>트리가 아니라 지침의 몫이다(D10).</em></span></dd>
<dt>유스케이스가 애그리거트를 <b>건너뛰어도 되나</b> <span class="dim">08-04 보강</span></dt>
<dd><b>읽기면 된다. 쓰기면 안 된다.</b><br><b>건너뛰어도 되는 것</b> — 조회 전용(목록·검색) · 순수 위임(영수증 PDF·업로드 URL) · 외부 조회(배송추적·환율). 도메인 규칙이 없으므로 <code>port/</code> 로 바로 간다. <b>«모든 유스케이스가 애그리거트를 거쳐야 한다»고 정한 적이 없다.</b><br><b>안 되는 것</b> — <b>상태를 바꾸면서</b> 건너뛰기. «배송이 시작된 주문은 취소할 수 없다» 같은 규칙이 <b>갈 곳을 잃는다</b> — 유스케이스에 쓰면 도메인 규칙이 응용으로 새고, 안 쓰면 버그다. <b>빈혈 도메인이 생기는 정확한 경로가 이것이다.</b><br><span class="dim">다만 이건 지키자고 다짐할 규칙이 아니다 — <b>D12</b> 의 «리포지토리는 애그리거트를 주고받는다»가 <b>그 경로를 아예 없앤다</b>.</span></dd>
<dt>조회 전용(CQRS 읽기)에 <b>새 칸이 필요 없다</b> <span class="dim">08-04 보강</span></dt>
<dd>목록 100건을 조인해서 보여주는 화면은 애그리거트로 가면 손해다 — 100개를 통째로 불러오고 쓰는 건 필드 셋이다. 이럴 땐 <b>납작한 DTO 를 바로 받는 게</b> 맞다.<br><b>그런데 자리가 이미 다 있다</b> — <code>list_orders/</code> 도 유스케이스이고, <b>«조회 포트»에 의존</b>하며, 결과는 <code>&lt;use_case&gt;_result.py</code> 다. <b>칸이 하나도 안 는다.</b><br>
<span class="dim"><b>08-06 문구 정정 — 「리포지토리 대신」이 아니다.</b> 그렇게 쓰면 «읽으면 포트, 쓰면 리포지토리»로 읽힌다. <b>D29</b> 가 실측으로 뒤집었다 — <b>읽기 유스케이스 52개 중 51개가 도메인 리포지토리로 읽는다</b>(포트 직행은 1건). 선은 <b>«도메인을 우회하느냐»</b>이고, 우회할 때만 포트다.</span></dd>
<dt>배치가 «읽기/쓰기»를 저절로 표현한다</dt>
<dd><b>리포지토리</b>는 <code>domain_layer/&lt;aggregate&gt;/</code> 에서 <b>애그리거트</b>를 주고받고, <b>조회 포트</b>는 <code>application_layer/port/</code> 에서 <b>납작한 DTO</b> 를 준다. <b>D12</b> 와 <b>D2</b> 를 따로 정했는데 <b>합쳐놓고 보니 배치가 이미 선을 그어놨다.</b><br>
<span class="dim"><b>08-06 — 그 선의 이름을 고쳤다.</b> 「쓰기는 도메인 경유 · 읽기는 직행」이라고 적었는데 <b>읽기도 대개 도메인 경유다</b>(51:1). 선은 <b>«애그리거트를 돌려주느냐»</b> — <b>D29</b>.</span></dd>
<dt class="ans-dt">결정 ③ 화살표</dt>
<dd class="ans-dd filled"><b><code>domain_layer</code> 와 자기 <code>port/</code> 만 의존한다.</b> <code>driven_layer</code>·<code>driving_layer</code> import 금지. <b>타 BC 도 직접 부르지 않는다</b> — 전역 제약 ③ 이므로 <code>port/</code> 를 거친다(그 어댑터가 Evans 의 <b>Anticorruption Layer</b> 이고, <b>어느 칸에 두는지는 <code>driven_layer</code> 차례에</b>).</dd>
<dt>원문이 넷을 강요하지 않는다</dt>
<dd>«원은 <b>도식</b>일 뿐이다. 넷보다 많아도 되고 반드시 넷이어야 한다는 규칙은 없다. <b>다만 의존 규칙은 언제나 적용된다.</b>» 칸을 넷으로 유지하는 게 클린을 어기는 것이 아님을 원문이 직접 허락한다.</dd>
<dt>현행 <code>service/</code> 는 어디로 가나 — <b>위에서부터 묻는다</b> <span class="dim">08-04</span></dt>
<dd><div class="pre-wrap"><pre><code>1. 한 애그리거트 안에서 끝나나?           → 애그리거트 메서드   domain_layer/&lt;aggregate&gt;/
2. 애그리거트를 인자로 받아 규칙만 판정하나? → 도메인 서비스      domain_layer/domain_service/
3. id 를 받아 불러오고·시키고·저장하나?     → 유스케이스        application_layer/&lt;area&gt;/&lt;use_case&gt;/
4. 바깥 기술(SMTP·S3·HTTP)을 쓰나?        → 포트 + 어댑터     port/ + driven_layer/</code></pre></div>
<b>«위에서부터»가 중요하다</b> — 한 칸 내려갈 때마다 <b>바깥으로 한 발</b> 나가는 것이고, 위에서 답이 나오면 거기가 집이다. 순서를 안 지키면 습관적으로 3번에 넣게 되는데 <b>그게 빈혈 도메인이 생기는 가장 흔한 경로</b>다(«일단 서비스에 짜고 나중에 옮기지»가 안 옮겨진다).</dd>
<dt>그래서 <code>service</code> → <code>use_case</code> 는 <b>개명이 아니라 분류</b>다</dt>
<dd><b>3번만 <code>application_layer</code> 에 남는다.</b> 1·2번은 <code>domain_layer</code> 로, 4번은 선언만 남기고 구현이 <code>driven_layer</code> 로 나간다.<br>그리고 <b>파일 하나가 폴더 여럿이 된다</b> — <code>order_service.py</code> 의 함수 다섯이 <code>place_order/</code>·<code>cancel_order/</code>·<code>ship_order/</code>… 로 갈린다(D14 의 «폴더 하나 = 진입점 하나»). <b><code>presentation_layer → driving_layer</code>(119건 기계 치환)와 성격이 완전히 다른 작업이다</b> — 치환이 아니라 <b>함수마다 판정</b>이다.</dd>
<dt>기각한 대안</dt>
<dd><b><code>&lt;use_case&gt;/</code> 평면</b>(원안) — «이 시스템이 뭘 하는지»가 최상위에서 바로 보인다는 이점이 있었으나, <code>api/&lt;area&gt;/</code> 와 <b>축이 어긋나</b> 짝을 찾을 때 머릿속 변환이 필요했다.<br><b>평면 <code>services.py</code></b>(Cosmic Python 방식) — 그 책 스스로 부록에서 «이 모듈 안은 완전히 평면이고 <b>더 복잡한 프로젝트는 이 계층을 키워야 한다</b>»고 적어둔다. 예제용이지 표준 트리의 답이 아니다.</dd>
</dl>

## D2 · 포트 선언에 최상위 칸이 필요한가

**확정 · 08-04** · 자리 — ① 칸 &nbsp;·&nbsp; 닫는 문제 <b>P1</b> <b>P2</b> <b>P5</b> <b>P10</b>

<dl class="kv">
<dt class="ans-dt">결정</dt>
<dd class="ans-dd filled"><b>최상위 칸은 만들지 않는다.</b> 포트는 <b>둘로 갈려 각자 자리를 찾았다</b> — 애그리거트에 <b>붙는</b> 것은 <code>domain_layer/&lt;aggregate&gt;/&lt;aggregate&gt;_repository.py</code>(D12), <b>안 붙는</b> 것은 <code>application_layer/port/</code>.</dd>
<dt>클린 조사가 이걸 확인해줬다</dt>
<dd>Uncle Bob 은 <b>Data Access Interface 를 Use Cases 링에 직접 배치</b>한다. 즉 «안 붙는 포트는 응용의 것»이 <b>클린의 기본형</b>이다. R1 이 <code>application_layer/</code> 를 클린 구역으로 배정했으므로 그대로 쓴다.</dd>
<dt>왜 최상위가 아닌가</dt>
<dd>D1 에서 «입구는 역할로 묶는다»가 섰고 포트는 <em>출구</em>이므로 대칭을 맞추면 최상위가 답처럼 보였다. <b>그런데 대칭이 깨지는 지점이 있다</b> — 입구는 <b>누가 봐도 하나의 표면</b>이지만, 출구는 <b>주인이 갈린다</b>: 리포지토리는 애그리거트가 주인이고 시계·게이트웨이는 유스케이스가 주인이다. <b>주인이 다른 것을 한 칸에 모으면 그게 <code>boundary/</code> 가 무너진 방식이다.</b></dd>
<dt>남은 것</dt>
<dd><code>port/</code> 안을 종류로 더 나눌지 — <b>나누지 않는다</b>(D10). 시계·게이트웨이·알림·UnitOfWork 사이에 <b>폴더 단위로 쓸 규칙이 없다.</b></dd>
</dl>

## D4 · 안쪽 칸이 무엇을 알아도 되나

**확정 · 08-04** · 자리 — ④ 앎의 범위 &nbsp;·&nbsp; 닫는 문제 <b>P12</b> <b>P3</b>

<div class="pre-wrap">
<pre><code>domain_layer      ← 바깥 기술 :   0건   깨끗하다
application_layer ← django    :  61건

  from django.db import transaction     37   ← 정본 219줄이 UoW 실현으로 허용
  from django.utils import timezone     20   ← 허용 조문 없음
  from django.db import connection       3   ← 없음
  IntegrityError · OperationalError      5   ← 없음</code></pre>
</div>
<dl class="kv">
<dt class="ans-dt">결정</dt>
<dd class="ans-dd filled"><b>⒜ 전부 금지.</b> <code>application_layer</code> 는 django 를 <b>하나도 import 하지 않는다</b>. 필요한 것은 전부 <code>port/</code> 뒤로 간다.</dd>
<dt>원리로 따라온다 — 고를 게 없었다</dt>
<dd><b>전역 제약 ②</b>가 «안쪽은 구체 기술을 모른다»이고, 네 칸 중 <code>domain_layer</code>·<code>application_layer</code> 가 <b>안쪽</b>이다. django 는 구체 기술이다. <b>⒝ 도 ⒞ 도 제약을 어긴다</b> — 예외를 두려면 «왜 이것만 안쪽이 알아도 되나»를 답해야 하는데, <b>D14</b> 가 <code>port/</code> 자리를 만든 순간 <b>답할 필요가 없어졌다.</b></dd>
<dt>어디로 가나</dt>
<dd><code>from django.db import transaction</code> <b>37</b> → <code>port/</code> 의 <b>UnitOfWork</b><br><code>timezone.now()</code> <b>20</b> → <code>port/</code> 의 <b>Clock</b><br><code>connection</code>·<code>IntegrityError</code>·<code>OperationalError</code> <b>8</b> → <code>port/</code> <span class="dim">(DB 예외를 응용이 잡는다는 건 이미 «안쪽이 ORM 을 안다»는 뜻이다)</span></dd>
<dt>정본 219줄의 예외 조문은 없어진다</dt>
<dd>정본이 <code>transaction</code> 을 «UoW 실현»으로 허용하고 있었는데, <b>UnitOfWork 를 포트로 세우면 그 조문이 필요 없다.</b> 예외 조문을 지우는 것이 <b>규칙이 하나 줄어드는</b> 방향이다.</dd>
<dt>이미 답이 코드 안에 있었다</dt>
<dd>어떤 BC 에는 이미 <code>UtcClockPort</code> 가 있다 — <b>같은 관심사를 BC 마다 다르게</b> 처리하던 것을, <b>이미 있던 그 답을 표준으로</b> 삼는 것이다.</dd>
<dt>이 결정의 값</dt>
<dd>남은 것 중 <b>유일하게 AST 한 줄로 검사된다</b> — <code>application_layer/**</code> 의 import 에 <code>django</code> 가 있으면 위반. <b>정하는 즉시 백스톱에 넣을 수 있다.</b></dd>
</dl>

## D20 · driven_layer 의 화살표와 앎의 범위 — 이 칸을 닫는다

**확정 · 08-05** · 자리 — ③ 화살표 &nbsp;·&nbsp; ④ 앎의 범위 &nbsp;·&nbsp; <b>넷이 다 찼다</b>

<dl class="kv">
<dt class="ans-dt">결정 ③ 나가는 화살표</dt>
<dd class="ans-dd filled"><b>판정 — «구현하려고» 잡으면 허용, «부르려고» 잡으면 금지.</b> 그래서 <b><code>domain_layer</code> 와 «선언이 사는 자리» 만</b> 의존한다:
<div class="pre-wrap"><pre><code>domain_layer/                        애그리거트 · 리포지토리 선언 · 값 객체 · 예외
application_layer/port/              바깥에 있어야 하는 것 전부 — 셋이 그 아래 산다</code></pre></div>
<b><code>application_layer/&lt;area&gt;/</code> 는 금지</b> — 유스케이스를 부르지 않는다. <code>driving_layer</code> 도 금지. 타 BC 는 <code>anticorruption_layer/</code> 아래에서만, 그것도 <code>open_host_service/</code> 아래만.<br>
<span class="dim"><b>08-07 · F5 — 목록에 뒤의 둘이 빠져 있었다.</b> 이 카드를 쓸 때는 선언 자리가 <code>port/</code> 하나였는데 그 뒤로 <b>D29</b>(<code>query_repository/</code>)와 <b>D31</b>(<code>transaction/</code>)이 생겼고 <b>이 문장이 안 따라왔다</b>. 문면 그대로면 트리 85행(<code>Django&lt;Capability&gt;DomainBypassQuery</code>)과 87행(드리븐 UoW)이 <b>자기 선언조차 import 할 수 없어 구현이 불가능</b>했다. <b>그래서 목록이 아니라 «판정»을 앞에 뒀다</b> — 선언 자리가 또 생겨도 이 카드를 다시 열 필요가 없다.</span></dd>
<dt>«유스케이스 금지» 가 이 칸의 정의다</dt>
<dd>어댑터가 유스케이스를 부르면 <b>제어 흐름이 뒤집힌다</b> — <code>driven</code> 은 정의상 <b>불려가는 쪽</b>이다. 브로커 컨슈머처럼 «밖이 나를 구동해서 유스케이스를 부르는» 것은 <b><code>driving</code> 이다</b>(그 자리는 아직 없다 — <b>D3</b> 이 «메시지 입구»로 남겨뒀다).<br>
<b>이 한 줄이 driving 과 driven 을 코드로 가른다.</b> 이름만으로 갈라 두면 «어댑터니까 여기 두지»로 흐르는데, <em>어느 쪽이 어느 쪽을 부르나</em>는 AST 로 판정된다.</dd>
<dt>왜 <code>port/</code> 는 되고 <code>&lt;area&gt;/</code> 는 안 되나</dt>
<dd><code>port/</code> 아래 셋은 <b>구현하려고</b> 잡는다(선언을 상속한다). <code>&lt;area&gt;/</code> 는 <b>부르려고</b> 잡는다. <b>D11</b> 이 <code>driving_layer</code> 에 <em>정확히 반대로</em> 그은 선이다 — 컨트롤러는 <code>&lt;area&gt;/</code> 만, 어댑터는 <code>port/</code> 만. <b>두 줄이 서로의 거울이다.</b></dd>
<dt class="ans-dt">결정 ④ 앎의 범위</dt>
<dd class="ans-dd filled"><b>전부 알아도 된다.</b> django · ORM · HTTP · 벤더 SDK · 브로커 — <b>기술을 아는 것이 이 칸의 일</b>이다. 전역 제약 ②(안쪽은 구체 기술을 모른다)는 <b>안쪽</b>에 걸리는 규칙이고, 여기는 가장 바깥이다.</dd>
<dt>들어오는 화살표</dt>
<dd><b><code>composition_root</code> 뿐이다.</b> <code>application_layer</code> 도 <code>domain_layer</code> 도 <code>driving_layer</code> 도 이 칸을 import 하지 않는다. <span class="dim">나중 대조 — 실측 <code>application → infra</code> import <b>0 건</b>. 코드는 이미 이 규칙을 지키고 있었다.</span></dd>
<dt>검사 — 여섯 줄로 모인다</dt>
<dd><b>①</b> <code>driven_layer/**</code> 가 <code>application</code> 안에서 잡을 수 있는 것은 <code>domain_layer</code> · <code>application_layer/port/</code> <b>뿐</b>이다 — <code>driving_layer</code> 나 <code>application_layer/&lt;area&gt;/</code> 가 나오면 위반<span class="dim">(08-07 · F5 — 옛 문장은 «금지 목록»이라 결정 ③의 «허용 목록»과 어긋났다. <b>둘이 다르게 읽히면 구현하는 사람마다 답이 갈린다</b>)</span><br>
<b>②</b> <code>django_&lt;bounded_context&gt;/</code> 는 django 와 같은 폴더 말고 <b>아무것도</b> import 하지 않는다 <span class="dim">D15</span><br>
<span class="dim"><b>①②의 대상에서 <code>django_&lt;bounded_context&gt;/admin/**</code> 는 뺀다</b> — <b>장고가 등록과 쓰기 경로를 소유하는 축이라 이 둘이 걸릴 자리가 없다</b>(<code>AdminSite.register</code> 가 «Model 클래스»를 받고 <code>save_model→obj.save()</code> 를 프레임워크가 수행한다 · 트리 74행 · <b>D21</b>). <b>④(타 BC)·⑤(벤더 SDK)는 어드민에도 그대로 걸린다.</b> <b>08-07 · 2차 리뷰 S7</b> — <code>**</code> 와일드카드라 이 면제가 <b>검사 문면에 없었다</b>. 트리를 안 보고 이 카드만으로 구현하면 어드민 8개가 그대로 위반으로 찍힌다.</span><br>
<b>③</b> <code>django_&lt;bounded_context&gt;/</code> 를 import 하는 것은 <code>repository/</code> 뿐 <span class="dim">D15</span><br>
<b>④</b> 타 BC 는 <code>anticorruption_layer/</code> 아래에서만 · <code>open_host_service/</code> 아래만 <span class="dim">D17</span><br>
<b>⑤</b> HTTP 클라이언트·벤더 SDK 는 <code>external_system/</code> 아래만 <span class="dim">D18</span></dd>
<dt class="ans-dt">이 칸이 닫혔다 — <b>자리 하나를 유예하고</b></dt>
<dd class="ans-dd filled">① 칸(D15 D17 D18) · ② 이름(D16) · ③ 화살표 · ④ 앎의 범위 — <b>넷이 다 참</b>이다. <b>네 칸이 모두 닫혔고 <b>D5</b> 도 같이 닫힌다.</b><br>
<span class="dim">유예했던 것 하나 — <b>통합 이벤트를 밖으로 내보내는 자리</b>. <b>D13</b> 의 «정직한 공백».</span> <b>08-06 닫혔다</b>(<b>D34</b>) — <b>칸을 열지 않는다</b>. 예상대로 화살표는 안 흔들렸고, <b>흔들릴 칸이 아예 안 생겼다</b>.</dd>
</dl>

## D18 · 바깥 시스템은 어디로 — 형제를 하나 더 세운다

**확정 · 08-05** · 자리 — ① 칸 &nbsp;·&nbsp; ② 이름 &nbsp;·&nbsp; <code>driven_layer/</code> 가 상대하는 «바깥»은 하나가 아니다

<dl class="kv">
<dt class="ans-dt">결정</dt>
<dd class="ans-dd filled"><b><code>external_system/&lt;system&gt;/</code> 를 형제로 세운다.</b> 결제·저장·LLM·알림 같은 <b>남이 만든 시스템</b>은 여기다 — <code>anticorruption_layer/</code> 에 같이 넣지 않는다.</dd>
<dt>«바깥»이 네 종류다</dt>
<dd><div class="pre-wrap"><table class="mini">
<tr><th>상대</th><th>예</th><th>우리가 고칠 수 있나</th><th>계약이 어디 있나</th></tr>
<tr><td>우리 저장소</td><td>Postgres</td><td>—</td><td>우리가 정의</td></tr>
<tr><td><b>다른 BC</b></td><td>billing · inventory</td><td><b>고칠 수 있다</b></td><td><b>저장소 안</b> — <code>contract/</code></td></tr>
<tr><td><b>바깥 시스템</b></td><td>토스 · S3 · OpenAI</td><td><b>못 고친다</b></td><td><b>저장소 밖</b> — 남의 문서</td></tr>
<tr><td>런타임</td><td>시계 · UUID · 트랜잭션</td><td>—</td><td>없다</td></tr></table></div>
<b>2행과 3행이 갈리는 지점이 결정적이다.</b></dd>
<dt>왜 <code>anticorruption_layer/</code> 에 같이 안 넣나</dt>
<dd><b>둘은 서로 다른 제약을 지킨다.</b><br>
<code>anticorruption_layer/</code> — <b>BC 경계</b>(전역 제약 ③). 검사는 «타 BC 의 <code>open_host_service/</code> 만 import».<br>
<code>external_system/</code> — <b>시스템 경계</b>. 검사는 «<b>프로세스 밖으로 소켓을 여는 라이브러리</b>를 여기서만 import» — <b>대상이 다른 검사</b>다. <em>가르는 자는 <b>「소켓을 여나」 하나</b>이고 이름 목록은 «저장소가 실제로 쓰는 의존성에 맞춰 유지하는 데이터»다 — <code>httpx</code>·<code>requests</code>·<code>boto3</code>·<code>openai</code>·<code>redis</code>·<code>kafka-python</code>·<code>pika</code>·<code>grpcio</code>·<code>smtplib</code> 처럼 <b>HTTP 만이 아니라 브로커·캐시·메일도 들어온다</b>. <b>이름을 나열해 «닫으면» 새 의존성이 들어올 때 검사가 조용히 통과한다</b><span class='dim'> 08-11 · C5 — 옛 문면이 셋(httpx·boto3·openai)으로 닫아 두어 바로 아래 판별법이 든 Redis·Kafka 를 «이 검사가 못 잡고» 있었다</span></em><br>
그리고 <b>계약의 소재가 실무를 가른다</b>: 타 BC 계약이 바뀌면 <b>CI 가 깨지고</b>, 외부 계약이 바뀌면 <b>런타임에 터진다</b>. 그래서 <b>타임아웃·재시도·서킷 브레이커·레이트리밋이 «필요한 자리»는 <code>external_system/</code> 쪽</b>이다. 한 폴더에 섞으면 이 규칙을 못 쓴다. <em>다만 «필요한 자리»와 «사는 자리»는 다르다 — <b>«값»(몇 초·몇 번·언제 열림)은 이 어댑터가 정하고, «기계»(재시도 루프·백오프·차단기)는 <code>framework/</code> 가 주며, «다시 부르기»는 입구가 한다</b><span class='dim'> 08-11 · C5 — 옛 문면 「external_system/ 에만 산다」와 D52 의 「기계만 framework/」를 둘 다 켜면 재시도 기계가 살 자리가 0이 됐다</span></em></dd>
<dt>덤 — <code>ls</code> 한 번이 답하는 질문이 하나 더 생긴다</dt>
<dd>«우리가 어떤 바깥에 돈과 데이터를 맡기고 있나» — <b>보안 리뷰와 벤더 종속성 점검이 실제로 묻는 질문</b>이다. <code>anticorruption_layer/</code> 의 «폴더 목록 = 의존 BC 목록»과 <b>같은 방식의 이득</b>이고, 둘이 섞이면 <b>둘 다 흐려진다</b>.</dd>
<dt>판별법 — 위에서부터 묻는다</dt>
<dd><div class="pre-wrap"><pre><code>1. 우리 DB 를 만지나?                      → adapter/persistence/
2. 우리가 만든 다른 BC 인가?               → adapter/anticorruption_layer/&lt;bounded_context&gt;/
3. 네트워크 너머의 «남의 것»인가?           → adapter/external_system/&lt;system&gt;/
4. 상대가 아예 없는데 기술이 필요한가?      → adapter/&lt;capability&gt;/
   (업무 어휘가 0이면 framework/&lt;capability&gt;/)</code></pre></div>
<span class="dim"><b>08-08 · F6</b> — 4 번이 «칸 바로 아래 파일»이었고 예시가 «시계·UUID·트랜잭션»이었다. <b>셋 다 그 자리가 아니다</b> — 시계·UUID 는 업무 어휘가 0이라 <code>framework/</code>, 트랜잭션은 <code>persistence/unit_of_work/</code> 다(<b>D37</b>).</span> 다만 <code>unit_of_work.py</code> 는 <b>D14</b> 가 선언을 트리에 올린 논리(BC 당 하나 · 이름 고정) 그대로 <b>파일로 올린다</b>.<br>
<span class="dim">Redis 캐시처럼 «우리가 운영하는 인프라»는 <b>3 번</b>이다 — 판정선이 «남의 회사냐»가 아니라 <b>«계약이 저장소 밖이고 네트워크 너머라 런타임에 터지나»</b> 이기 때문이다.</span></dd>
<dt class="ans-dt">② 이름 — 다시 봤고 <code>external_system/</code> 으로 둔다</dt>
<dd class="ans-dd filled"><b>판정 근거다</b> — 이 폴더의 이름이 위 판별법 <b>3 번을 그대로 말한다</b>. 파일을 어디 둘지 고민할 때 폴더 이름이 답을 준다.</dd>
<dt>기각한 대안</dt>
<dd><b><code>external_service/</code></b> — <b><code>service</code> 가 이미 세 뜻</b>이다(<code>open_host_service</code> · <code>domain_service</code> · 현행 <code>service/</code>). 네 번째를 늘리면 안 된다.<br>
<b><code>gateway/</code></b> — <em>가장 아까운 후보</em>다. Fowler·Uncle Bob 의 <b>원전 패턴명</b>이고 형제(<code>repository/</code>·<code>anticorruption_layer/</code>)와 어휘 결이 맞는다. 그래도 접었다: ⒜ Fowler 의 Gateway 는 <b>정의상 DB 를 포함</b>해서 «리포지토리도 게이트웨이 아닌가»가 반드시 나온다 — 우리가 갈라둔 선을 이름이 흐린다. ⒝ <b>«게이트웨이»는 이미 <code>port/</code> 쪽 어휘</b>다(<b>D2</b>·D14 의 예시). 구현 폴더에 같은 말을 쓰면 <b>«포트는 «필요»로, 어댑터는 «누구»로»</b>(<b>D17</b>)와 어긋난다.<br>
<b><code>third_party/</code></b> — 계보 어휘가 아니고, <b>우리가 운영하는 Redis 를 못 담는다</b>(판정선과 어긋난다). <b><code>external_adapter/</code></b> — 칸 전부가 어댑터다(D17 이 <code>adapter/</code> 를 접은 논리). <b><code>vendor/</code></b> — 역시 자체 운영 인프라를 못 담는다.</dd>
<dt>정직하게 — 걸리는 것 둘</dt>
<dd><b>⒜ Evans 의 ACL 은 외부 레거시까지 포함하는 개념</b>이라, <code>external_system/</code> 안의 어댑터도 <b>하는 일은 ACL 이다</b>. 폴더를 가른 건 <em>개념이 달라서가 아니라</em> <b>상대가 다르면 다루는 법이 달라서</b>다.<br>
<b>⒝ 형제 넷의 이름이 한 축이 아니다</b> — <code>django_&lt;bounded_context&gt;/</code>(기술) · <code>repository/</code>(패턴) · <code>anticorruption_layer/</code>(패턴) · <code>external_system/</code>(상대). <b>D15</b> 가 말한 «1차 축»은 <b>무엇이 갈리는가</b>(구동 대상)이지 <b>이름 짓는 방식</b>이 아니었다 — 그건 이 칸에서 애초에 하나였던 적이 없다. <span class="dim">판단이지 도출이 아니다. 기록해 둔다.</span></dd>
</dl>

## D17 · 타 BC 출구를 만들고, adapter/ 는 안 만든다 → 08-08 에 뒤집혔다

**확정 · 08-05 · 08-08 에 뒷절 폐기** · 자리 — ① 칸 &nbsp;·&nbsp; ② 이름 &nbsp;·&nbsp; <b>흐름을 그려서 갈랐다</b>

<dl class="kv">
<dt class="ans-dt">결정</dt>
<dd class="ans-dd filled"><b><code>anticorruption_layer/&lt;bounded_context&gt;/</code> 를 만든다.</b> <s><b><code>adapter/</code> 는 만들지 않는다</b> — 나머지 포트 어댑터는 칸 바로 아래 파일로 둔다.</s>
<span class="dim"><b>08-08 · F6 — 뒷절이 뒤집혔다(<b>D37</b>).</b>
접은 근거가 <em>「이 칸에 있는 것이 <b>전부</b> Adapter 라 그런 폴더는 아무 선도 긋지 못한다」</em> 였는데 <b>전부가 아니었다</b> —
<code>django_&lt;bounded_context&gt;/</code> 는 어댑터가 아니라 표 정의·마이그레이션·운영 화면이고 <b>지키는 약속이 없다</b>. 그 하나가 선을 긋는다.
그리고 겹이 규칙을 하나 만든다 — <b><code>adapter/</code> 아래 모든 <code>.py</code> 는 «어떤 선언의 구현»이고 그 선언을 «경로»가 가리킨다</b>.
<b>앞절과 아래 「포트는 «필요»로, 어댑터는 «누구»로」는 그대로 산다.</b>
<br>아래에서 <code>adapter/</code> 후보로 든 셋(UnitOfWork · Clock · 메일)은 <b>지금 기준으론 셋 다 그 자리가 아니다</b> —
UoW 는 <code>persistence/unit_of_work/</code>, Clock 은 업무 어휘가 0이라 <code>framework/clock/</code>, 메일은 상대가 SMTP 서버라 <code>external_system/</code> 이다.
<b>「도해에서 서로 가장 먼 것들」이라는 근거도 함께 낡았다.</b></span></dd>
<dt><code>anticorruption_layer/</code> — <b>어댑터의 한 종류가 아니라 «경계를 넘는 지점»이다</b></dt>
<dd>D10 으로 재면 규칙이 나온다: <b>«타 BC 의 <code>open_host_service/</code> 를 import 하는 것은 여기뿐»</b>. 이건 편의 규칙이 아니라 <b>전역 제약 ③(BC 경계는 관문으로만)의 출구 쪽 집행 지점</b>이다.<br>
지금까지 ③ 은 <b>입구만</b> 트리에 있었다(<code>driving_layer/open_host_service/</code>). 나가는 쪽은 조문으로만 있었는데, 이걸로 <b>양쪽이 대칭</b>이 된다 — 그리고 둘 다 Evans 의 컨텍스트 맵 패턴이라 <b>이름 쌍이 제약을 그대로 말한다</b>(<b>D9</b>).<br>
없으면 <b>크로스-BC 호출이 어느 어댑터에나 흩어진다</b> — 현행 프로덕션 125건이 그 모습이고, 그러면 «이 BC 가 누구에게 기대나»를 트리가 답하지 못한다.</dd>
<dt>안은 <code>&lt;bounded_context&gt;/</code> 하나까지만</dt>
<dd><b>폴더 목록이 곧 의존 BC 목록</b>이다 — <code>ls</code> 한 번이면 «이 BC 가 누구에게 기대나»가 나온다. 그 아래는 규정하지 않는다(D10) — 안에 몇 개가 필요한지는 상대 BC 가 무엇을 여느냐에 달렸다.<br><code>open_host_service/&lt;service&gt;/</code> 와 <b>같은 골격</b>이고 축도 같다(도메인 이름 1차).</dd>
<dt>포트는 «필요»로, 어댑터는 «누구»로 이름 붙는다 <span class="dim">08-05 정정</span></dt>
<dd>도해에 처음 <code>port/&lt;other_bc&gt;_gateway.py</code> 라고 적었다가 <b>고쳤다</b> — <code>port/&lt;capability&gt;/&lt;capability&gt;.py</code> 다.<br>
<b>공급자 BC 의 이름이 안쪽으로 새고 있었다.</b> 나머지 포트가 <code>clock_port.py</code>(<em>django</em>가 아니라) · <code>email_sender_port.py</code>(<em>ses</em>가 아니라)인 것과 어긋난다. 그리고 실질적으로도 다르다 — <b>그 능력을 다른 BC 가 맡게 되면 <code>&lt;other_bc&gt;_gateway</code> 는 유스케이스까지 고치게 만들고, <code>&lt;capability&gt;</code> 는 어댑터만 갈아끼우면 된다.</b> DIP 를 세운 이유 그 자체다.<br>
<b>«누가 주나»는 <code>anticorruption_layer/&lt;bounded_context&gt;/</code> 가 안다</b> — 그래서 이 폴더의 «폴더 목록 = 의존 BC 목록»이 <em>유일한</em> 답이 되고, 같은 사실이 두 군데 적히지 않는다.</dd>
<dt>이름을 <code>acl/</code> 로 줄이지 않는다</dt>
<dd>약어인 데다 <b>다른 뜻으로 먼저 읽힌다</b> — <code>acl</code> 은 거의 언제나 access control list 다. 지금까지 나온 약어 중 <b>오독 위험까지 있는 유일한 것</b>이다.
<br><b>이 금지는 «폴더 이름»에만 걸린다</b> — 이 문서의 설명글이 <code>open_host_service/</code> 를 <b>OHS</b> 로 줄여 쓰는 것과는 축이 다르다.
<b>폴더 이름은 코드에 박혀 오래 가고 검사기가 읽지만, 설명글의 줄임말은 그 문단에서만 산다.</b>
<span class="dim">08-10 · G-18 — 4차 리뷰가 <em>「약어는 오독이라 해 놓고 문서에서 OHS 를 쓴다」</em> 를 비대칭으로 지적했다. <b>비대칭이 아니라 축이 둘이었다</b> — 다만 그 구분이 어디에도 안 적혀 있었다.</span></dd>
<dt class="ans-dt">그럼 <code>adapter/</code> 는 — <b>안 만든다</b></dt>
<dd class="ans-dd filled"><b>선을 하나도 안 바꾸고, 규칙을 하나도 안 만들고, 정의가 «나머지»다.</b> 셋이 겹치면 그게 <b>P4</b>(adapter 가 수용소가 됨)로 가는 정확한 조건이다.</dd>
<dt>흐름을 그려보니 더 분명해졌다</dt>
<dd><code>adapter/</code> 를 넣어도 <b>유스케이스가 부르는 이름 · import 방향 · <code>composition_root</code> 가 꽂는 것 · 갈아끼울 때 바뀌는 것</b> 넷이 다 같다. 느는 건 <b>경로에 마디 하나</b>뿐이다.<br>
그런데 흐름을 보면 <b>더 나쁜 게 보인다</b> — <code>adapter/</code> 에 들어갈 셋은 도해에서 <b>서로 가장 먼 것들</b>이다: <b>UnitOfWork</b> 는 정거장이 아니라 <b>구간</b>(점선 상자) · <b>Clock</b> 은 정거장도 아닌 조용한 질의 · <b>메일</b> 은 <b>빨간 점선으로 따로 그린 것</b>(되돌릴 수 없다). <b>도해가 다른 기호로 그리려고 애쓰는 것을 트리가 한 이름으로 묶는 셈</b>이다.</dd>
<dt>형제 넷 중 하나만 규칙이 없다</dt>
<dd><div class="pre-wrap"><table class="mini">
<tr><th>폴더</th><th>그 폴더 단위로 쓸 수 있는 규칙</th></tr>
<tr><td class="mono">django_&lt;bounded_context&gt;/</td><td>django 말고 아무것도 import 안 한다(리프)</td></tr>
<tr><td class="mono">repository/</td><td>선언과 1:1 · 애그리거트를 주고받는다</td></tr>
<tr><td class="mono">anticorruption_layer/</td><td>타 BC 의 <code>open_host_service/</code> 만 import 한다</td></tr>
<tr><td class="mono"><b>adapter/</b></td><td><b>— 없다. 정의가 «나머지»다</b></td></tr></table></div></dd>
<dt>§0-4 «평면 금지»는 안 걸린다</dt>
<dd>나머지를 칸 바로 아래 파일로 두면 걸리는 줄 알았는데 <b>아니다</b>. <code>driven_layer/</code> 는 평면이 아니다 — <b>폴더가 셋 있고</b> 파일들은 하위 구조가 없는 리프다. <code>application/&lt;bounded_context&gt;/</code> 가 <code>composition_root/dependency_wiring.py</code> 를 바로 아래 두는 것과 같은 모양이다.</dd>
<dt class="ans-dt">08-07 · R10 — <b>그 «나머지»를 트리에 그렸다</b></dt>
<dd class="ans-dd filled">이 결정이 「칸 바로 아래 파일로 둔다」로 자리를 정해 놨는데 <b>트리에 그 행이 없었다</b> — <code>&lt;boundary&gt;_unit_of_work.py</code> 하나만 예시로 실려 있어서, 그림만 보면 <b>그 자리가 UnitOfWork 전용처럼 읽혔다</b>.
그래서 목적지 다섯 중 넷만 그려진 상태였고, <b>다섯째로 갈 것이 실측 19개</b>였다. 그림의 빈칸이 바로 이 카드가 금지한 <code>adapter/</code> 를 만들게 민다.<br>
<b><code>driven_layer/&lt;capability&gt;.py</code> 행을 넣었다.</b> 규칙은 하나도 안 바뀐다 — <b>D33</b> 의 접미사 표가 이미 이 경로를 쓰고 있었다.<br>
<b>그러면서 «나머지»가 다시 둘로 갈렸다</b> — 계약에 업무 어휘가 있으면 BC 안(여기), 한 글자도 없으면 <code>framework/&lt;capability&gt;/</code>(<b>D24</b> 가 08-07 에 연 칸). <em>실측 16 중 14 : 2.</em>
<span class="dim">그리고 어댑터가 아닌 둘이 드러났다 — <code>ProviderProjection</code>(포트를 구현하지 않는다. 애그리거트→벤더 payload 번역이라 벤더 폴더로) · <code>subject_marking_response_schema</code>(클래스도 없는 상수 dict).</span></dd>

<dt>뒤집을 조건</dt>
<dd>«나머지»가 늘어 눈에 거슬리면, 답은 <code>adapter/</code> 라는 <b>바구니</b>가 아니라 <b>구동 대상별 폴더</b>(<code>mail/</code>·<code>object_storage/</code>)다 — 1차 축(«내가 무엇을 구동하나»)을 한 번 더 쓰는 것이고, 그때는 각 폴더에 <b>규칙이 생긴다</b>.</dd>
<dt>딸려 나온 검사 한 줄 <span class="dim">흐름에서</span></dt>
<dd><b><code>with unit_of_work:</code> 블록 안에서 크로스-BC 포트를 부르면 위반.</b> 트랜잭션을 연 채 남의 응답을 기다리면 <b>DB 락을 쥐고 네트워크를 기다린다</b>. 게다가 남은 이미 커밋했는데 내가 롤백되면 불일치가 남는다. <b>ⓐ 는 상자 앞, ⑧ 은 상자 뒤</b> — 둘 다 경계를 넘지만 커밋 선의 반대편이다.</dd>
</dl>

## D16 · 이 칸의 이름 — 짝을 맞춘다

**확정 · 08-05** · 자리 — ② 이름 &nbsp;·&nbsp; <b>D3</b> 가 «딸린 후보 — 결정 아님»으로 남긴 것

<dl class="kv">
<dt class="ans-dt">결정</dt>
<dd class="ans-dd filled"><b><code>infra_layer/</code> → <code>driven_layer/</code>.</b> 네 칸이 <code>domain_layer</code> · <code>application_layer</code> · <code>driving_layer</code> · <code>driven_layer</code> 가 된다.</dd>
<dt>D3 과 <b>같은 근거</b>다 — R1 의 직접 귀결</dt>
<dd>R1 이 이 칸을 <b>헥사고날 구역</b>으로 배정했고, <b>driving / driven 은 Cockburn 본인의 어휘</b>다. <code>presentation</code> 이 DDD 어휘라서 배정과 어긋났던 것과 똑같이, <code>infra</code> 는 <b>어느 계보의 어휘도 아니다</b> — 그냥 «기반 시설»이라는 일반 명사이고, 계층을 <b>역할</b>이 아니라 <b>기술 지층</b>으로 부르는 이름이다.</dd>
<dt>명명 방침 위반 하나가 같이 없어진다</dt>
<dd><code>infra</code> 는 <b>약어</b>다(<code>infrastructure</code>). 방침은 «원전 패턴명은 풀어 쓰고, <b>일반어가 된 약어</b>(<code>api</code>)는 둔다»인데 <code>infra</code> 는 <b>둘 다 아니다</b> — 원전 어휘도 아니고 <code>api</code> 만큼 굳은 일반어도 아니다. <b><code>infrastructure_layer/</code> 로 늘리는 길도 있었지만</b>, 그러면 약어만 풀릴 뿐 <em>역할이 아니라 지층으로 부르는 문제</em>는 그대로다. <b>개명이 두 문제를 한 번에 없앤다.</b></dd>
<dt>미뤄서 실제로 얻은 것</dt>
<dd>D3 은 «그 칸을 열지 않은 채 정하지 않는다»로 미뤘다. <b>그 값을 받았다</b> — 안을 열기 전이었다면 근거가 <em>«짝이 예쁘다»</em> 뿐이었는데, 열고 보니 <b>D15</b> 의 1차 축이 <b>«내가 무엇을 구동하나»</b> 였다. <b>이름이 그 축을 그대로 말한다.</b><br>
<div class="pre-wrap"><pre><code>driving_layer/   누가 나를 구동하나   api/ · open_host_service/
driven_layer/    내가 무엇을 구동하나  django_&lt;bounded_context&gt;/ · repository/ · …</code></pre></div>
<code>infra_layer</code> 였다면 이 대칭이 <b>주석으로만</b> 있었을 것이다.</dd>
<dt>이미 한 번 철회한 반론</dt>
<dd>08-04 에 «<code>infra_layer</code> 를 driven 이라 부르면 <b>틀린 이름</b>»이라고 썼다가 <b>철회했다</b> — 클린의 링 구분(Interface Adapters / Frameworks &amp; Drivers)을 헥사고날 판정에 잘못 섞은 것이었다. <b>헥사고날 기준으로는 이 칸 전부가 driven 이다</b>: DB 는 secondary actor 이고 ORM 은 그 기술이다. <b>D15</b> 가 두 링을 <b>폴더로 갈라</b> 답하면서 이 반론은 완전히 없어졌다.</dd>
<dt>치르는 값 — <b>정직하게 둘</b></dt>
<dd><b>⒜ 가장 비싼 개명이다</b> — <code>infra_layer</code> <b>618건 · 300파일</b>. 트리에서 가장 크다. 다만 <code>presentation_layer</code>(119건)와 <b>성격이 같다</b>: 경로 접두사 치환이라 <b>기계 변환</b>된다. 함수마다 판정해야 하는 <code>service</code> → <code>use_case</code>(<b>D14</b>)와 전혀 다르다.<br>
<b>⒝ <code>driving</code> 과 <code>driven</code> 이 두 글자 차이다</b> — 눈으로 훑을 때 헷갈릴 수 있다. <b>이건 계보 어휘에 딸린 값이지 우리가 만든 것이 아니다</b>. <span class="dim">완화 — 둘은 BC 바로 아래 <b>첫 마디</b>라 항상 같은 자리에 오고, 문자열이 서로 다르므로 <b>기계 검사에는 모호함이 없다</b>. 사람이 훑을 때만 걸린다.</span></dd>
<dt>기각한 대안</dt>
<dd><b><code>infrastructure_layer/</code></b> — 약어만 풀린다. 여전히 역할이 아니라 지층 이름이고 <b>훨씬 길다</b>.<br><b><code>driven_adapter/</code></b> — Cockburn 의 결합에는 더 가깝지만 <b>넷 중 하나만 접미사가 달라진다</b>. D3 이 <code>driving_adapter</code> 를 접고 <code>driving_layer</code> 로 간 것과 같은 이유다.<br><b><code>secondary_adapter/</code></b> — 원문 어휘이나 <b>방향을 안 말한다</b>. D3 이 <code>primary_adapter</code> 를 기각한 것과 같다.<br><b>유지</b> — 이름이 <em>틀리지는</em> 않는다. 다만 <b>약어 + 지층 이름 + 짝 안 맞음</b> 셋이 겹치고, 이 칸은 <b>지금 열고 있다</b> — 나중에 바꾸면 그때 618건이 더 커져 있다.</dd>
</dl>

## D15 · driven_layer 의 1차 축 — 그리고 첫 두 칸

**확정 · 08-05** · 자리 — ① 칸 &nbsp;·&nbsp; ② 이름 &nbsp;·&nbsp; <b>이 칸을 연 첫 결정</b>

<dl class="kv">
<dt class="ans-dt">결정 ① 1차 축</dt>
<dd class="ans-dd filled">1차는 <b>«내가 무엇을 구동하나»</b> 다. 지금 <b>둘</b>을 못 박는다 — <b><code>django_&lt;bounded_context&gt;/</code></b>(ORM · 마이그레이션) · <b><code>repository/</code></b>(선언의 구현). 나머지 셋은 아래에 적어둔다.</dd>
<dt><code>driving_layer</code> 의 <b>거울</b>이다</dt>
<dd>어댑터 칸 둘은 <b>같은 축</b>으로 갈린다 — <code>driving_layer/{ api, open_host_service }</code> 는 <b>«누가 나를 구동하나»</b>(외부 HTTP · 다른 BC), <code>driven_layer/</code> 는 <b>«내가 무엇을 구동하나»</b>(저장소 · 다른 BC · 나머지 바깥). Cockburn 의 포트-어댑터가 어댑터를 <b>건너편 행위자</b>로 묶는 것 그대로다. <b>도메인 이름은 그 아래에 온다.</b></dd>
<dt>§0-4(1차 폴더는 도메인 이름만)와 부딪히지 않는다 — <b>어댑터 칸은 이미 예외였다</b></dt>
<dd>«1차 폴더는 도메인 이름만»은 정확히는 <b>칸 안에서 «도메인 것»을 나눌 때</b> 종류를 앞에 두지 말라는 규칙이다. <code>api/</code> 도 <code>open_host_service/</code> 도 도메인 이름이 아니다 — <b>어댑터 칸의 1차는 바깥 행위자</b>이고 그건 도메인 것이 아니다. §0-4 가 실제로 무는 곳은 <b>안쪽 두 칸</b>(<code>&lt;aggregate&gt;/</code>·<code>&lt;area&gt;/</code>)이다.</dd>
<dt class="ans-dt">결정 ② <code>django_&lt;bounded_context&gt;/</code> — 프레임워크가 이름을 정하는 <b>유일한</b> 자리</dt>
<dd class="ans-dd filled"><b>이 폴더는 «ORM 을 모아둔 곳»이 아니라 그 자체가 장고 앱이다.</b> 장고는 모델이 <b>설치된 앱 패키지의 <code>models</code> 모듈</b>에 있어야 인식하므로, 이 칸이 있어야 하는 것은 우리 취향이 아니라 <b>프레임워크의 요구</b>다 — 이름이 프레임워크 쪽을 따르는 근거도 그것이다.<br>
<b>이름은 BC 하나가 둘을 동시에 정한다</b> — 폴더는 <code>django_&lt;bounded_context&gt;/</code>, <code>app_label</code> 은 <code>&lt;bounded_context&gt;</code>. <b>유일성은 공짜로 따라온다</b> — BC 는 <code>application/</code> 아래 <b>형제 폴더</b>라 이름이 겹칠 수 없다(파일시스템이 보장한다). <em>실측 16/16 — BC:앱 <b>1:1</b> · 폴더 = <code>django_</code>+BC · <code>label</code> = BC. 예외 0.</em></dd>
<dt><b>단서</b> — 겨루는 상대는 우리 BC 만이 아니다</dt>
<dd><code>app_label</code> 은 <code>INSTALLED_APPS</code> <b>전체</b>에서 유일해야 한다. 실측 24줄 중 남의 것이 <b>8</b> — <code>unfold</code> · <code>ninja_extra</code> · <code>django.contrib.{admin, auth, contenttypes, sessions, messages, staticfiles}</code>.<br>
<b>조문 — BC 이름은 설치된 다른 앱의 <code>label</code> 과 겹치지 않는다.</b> <b>D24</b> 의 «루트 패키지는 파이썬 표준 라이브러리 모듈명과 겹치지 않는다»와 <b>같은 모양</b>이다 — <b>이름을 짓는 자리마다 «피해야 할 목록»이 하나씩 붙는다</b>. 둘 다 한 줄 검사다.</dd>
<dt><code>label</code> 을 <b>«명시»로 적는 이유</b> — 기본값에 기대면 접두사가 샌다</dt>
<dd>선언을 생략하면 장고가 <b><code>name</code> 의 마지막 조각</b>을 <code>label</code> 로 쓴다(<code>django/apps/config.py</code>). 그러면 <code>label</code> 이 <code>django_accounts</code> 가 되어 <b><code>django_</code> 가 표 이름 · 마이그레이션 의존 · 어드민 URL 로 전부 샌다</b>. 그래서 <code>apps.py</code> 가 <b>손으로</b> 적는다 — <em>실측 16/16 이 명시 선언이고, 폴더 이름을 그대로 쓴 앱은 <b>0개</b>다.</em><br>
<span class="dim">덤 — <code>orm/</code> 으로 뒀다면 선언을 생략했을 때 기본 <code>label</code> 이 BC 마다 <code>orm</code> 으로 겹쳐 <code>ImproperlyConfigured</code>(「Application labels aren't unique」)가 난다. 다만 이건 <b>부차 근거</b>다 — <code>label</code> 을 명시하면 <code>orm/</code> 도 돌아가므로 <b>이 논거 하나로는 폴더 이름을 고를 수 없다</b>. 08-06 · R9 에서 근거를 갈아끼웠다.</span></dd>
<dt class="ans-dt"><b>이행 규칙 — BC 이름이 바뀌면 <code>label</code> 도 «같이» 바꾼다</b> <span class="dim">08-07 · 2차 리뷰 S9 에 뒤집었다</span></dt>
<dd class="ans-dd filled"><b><code>label</code> 은 BC 이름이다.</b> BC 이름을 바꾼다는 건 <code>application/&lt;bounded_context&gt;/</code> 폴더 이름이 바뀐다는 뜻이고, 그러면 <code>label</code> 도 바뀌는 것이 <b>같은 사실의 두 자리</b>다. 한쪽만 바꾸면 <b>이름이 두 뜻</b>이 된다 — 폴더는 새 이름, 어드민·마이그레이션은 영원히 옛 이름.
<div class="pre-wrap"><pre><code>같이 바꿀 때 치르는 값 — 셋
① apps.get_model("&lt;옛 label&gt;", …)      89곳 · 35파일
② 마이그레이션 dependencies 튜플         45파일  ("&lt;옛 label&gt;", "000N_…")
③ django_migrations 테이블의 app 열      UPDATE 한 번
     안 하면 django 가 «적용된 적 없는 앱»으로 보고 0001 부터 다시 돌리려 한다

테이블은 «안 움직인다» — 모델 47개가 전부 Meta.db_table 을 명시한다(47/47)</code></pre></div>
<b>③이 유일하게 손으로 하는 것</b>이고 나머지 둘은 문자열 치환이다. <b>BC 이름을 바꿀 때만 한 번 낸다.</b><br>
<span class="dim"><b>08-07 정정 — 옛 규칙은 정반대였다.</b> <em>「BC 이름을 바꾸고 싶어지면 «폴더만» 바꾸고 <code>label</code> 은 옛 이름으로 둔다 — 깨는 쪽이 압도적으로 싸다」</em>. <b>셋이 틀렸다</b> —
⑴ <b>같은 카드의 검사 ④가 그 이행을 위반으로 찍는다</b>(「<code>label</code> 값이 BC 폴더 이름과 같다」). 이 문서에서 <b>아홉 번째</b> «규칙이 자기가 지키려던 것을 위반으로 찍는» 자리다.
⑵ <b>근거 수치가 HEAD 와 안 맞았다</b> — 「95곳 + 76파일」 → 재측정 <b><code>apps.get_model</code> 89곳 · 마이그레이션 60파일(그중 label 참조 45)</b>.
⑶ <b>가장 큰 근거를 안 셌다</b> — <em>「바꾸면 스키마 이력이 끊긴다」</em> 라고 했는데 <b>모델 47/47 이 <code>db_table</code> 을 명시</b>해서 <b>테이블은 하나도 안 바뀐다</b>. 끊기는 것은 마이그레이션 «그래프»뿐이고 그건 위 셋으로 잇는다. <b>되돌릴 수 없는 것이 아니라 한 번 치르는 값</b>이었다.
<b>그리고 원전이 반대편에 있다</b> — Evans 의 <b class="v d">Ubiquitous Language</b> 는 진화하고 <b>그 진화가 코드에 반영돼야</b> 한다. 옛 이름을 <code>label</code> 에 화석으로 남기는 것은 그 반대다.</span></dd>
<dt><code>startapp</code> 은 이 뼈대를 만들어 주지 못한다</dt>
<dd>실측 <code>django/conf/app_template/</code> 이 주는 것 — <code>apps.py</code>(<code>name</code> 만, <b><code>label</code> 없음</b>) · <code>models.py</code> <b>파일</b> · <code>admin.py</code> <b>파일</b> · <code>views.py</code> · <code>tests.py</code> · <code>migrations/</code>. <b>6개 중 우리 트리와 맞는 건 <code>migrations/</code> 하나</b>다 — 우리는 <code>models/</code> 와 <code>admin/</code> 가 <b>패키지</b>고, <code>views.py</code>·<code>tests.py</code> 는 트리에 <b>없다</b>. <code>name</code> 도 깊은 점 경로여야 해서 그대로 두면 부팅이 안 된다.<br>
<b>그래서 앱 뼈대는 플러그인이 찍는다.</b> <code>startapp</code> 뒤에 사람이 다섯 개를 손보게 두면 <b><code>label</code> 을 잊는 날이 온다</b> — 그날 django 가 폴더 이름(<code>django_&lt;bounded_context&gt;</code>)을 <code>label</code> 로 삼아 <b>검사 ④가 즉시 위반으로 찍는다</b>. <span class="dim">되돌리는 값은 위 이행 규칙의 셋과 같다 — 못 되돌리는 것은 아니지만 <b>안 겪는 편이 낫다</b>.</span></dd>
<dt>D7 의 «기술 폴더를 만들지 않는다»에 안 걸린다</dt>
<dd><code>api/ninja/</code> 는 <b>분류 축</b>이었고, 값이 하나뿐이라 <em>애초에 축이 아니었다</em>. 이건 축이 아니라 <b>프레임워크 레지스트리가 요구하는 이름 하나</b>다 — 이름을 바꾸면 <em>돌아가지 않는다</em>. 클린이 가장 바깥 링을 «<b>세부사항이 가는 곳</b>»이라 부른 게 이 뜻이다. <b>트리가 프레임워크에 굽히는 자리는 여기 하나뿐이고, 그래서 여기여야 한다.</b></dd>
<dt>규칙 — <b>리프다</b></dt>
<dd><b><code>django_&lt;bounded_context&gt;/</code> 는 django 말고 아무것도 import 하지 않는다.</b> <code>domain_layer</code> 도 안 된다.<br>
<b>전역 제약 ① 은 이걸 안 막는다</b> — <code>driven</code> → <code>domain</code> 은 <em>허용된 방향</em>이다. 그런데도 막는다. <b>모델이 도메인을 만질 수 있으면 누군가 모델을 애그리거트로 만든다</b>(메서드가 붙고 불변식이 붙는다) — 장고에서 가장 흔한 실패다. 재료를 없애면 모델은 <b>필드 선언에 머무를 수밖에 없다</b>. <b>D12</b> 가 «규칙을 문서가 아니라 시그니처가 지킨다»고 한 것과 <b>같은 수법</b>이다.</dd>
<dt>덤 — BC 사이 ForeignKey 가 <b>구조적으로 불가능</b>해진다</dt>
<dd>이 한 줄이면 <code>django_order/</code> 가 <code>django_billing/</code> 를 import 할 수 없다. <b>전역 제약 ③(BC 경계는 관문으로만)이 ORM 층에서도 저절로 지켜진다</b> — 조문을 따로 쓸 필요가 없다. 스키마가 BC 경계를 넘어 묶이는 건 가장 되돌리기 어려운 결합인데, 그게 <b>import 한 줄로</b> 닫힌다.</dd>
<dt>치르는 값 — 정직하게</dt>
<dd><b>enum 값 같은 것이 두 군데 적힌다.</b> 모델의 <code>choices</code> 와 도메인 값 객체가 같은 문자열을 각자 갖는다.<br>다만 이건 낭비만은 아니다 — <b>컬럼 값은 «저장 형식»이고 도메인 enum 은 «도메인 개념»</b>이다. 묶어두면 <em>도메인 이름을 바꿀 때마다 마이그레이션이 된다.</em> 갈라두는 쪽이 맞다.</dd>
<dt><code>migrations/</code> 를 트리에 올리는 이유</dt>
<dd>django 가 이름을 강제하므로 <b>선택의 여지가 없고</b>, 올려두면 트리가 한 가지를 말한다 — <b>스키마는 BC 안에 산다</b>. 중앙 마이그레이션 폴더가 아니다. <span class="dim">그 안(모델을 <code>models.py</code> 한 파일로 두나 패키지로 쪼개나)은 <b>D10</b> 대로 <b>재량</b>이다 — 폴더 단위 규칙은 이미 «리프» 한 줄로 다 걸렸다.</span></dd>
<dt class="ans-dt">결정 ③ <code>repository/</code> — 왜 <code>django_&lt;bounded_context&gt;/</code> 안이 아닌가</dt>
<dd class="ans-dd filled"><b>리프 규칙이 답을 강제한다.</b> 번역자는 <b>양쪽을 다 알아야</b> 한다 — <code>domain_layer/&lt;A&gt;/</code> 의 애그리거트와 <code>django_&lt;bounded_context&gt;/</code> 의 모델을 <b>동시에 import</b> 한다. 안에 두면 리프가 깨진다.</dd>
<dt>계보로도 갈린다 — <b>넘겨받은 걱정이 여기서 닫힌다</b></dt>
<dd>리포지토리 구현은 클린의 <b>Interface Adapters</b>(번역), ORM 모델은 <b>Frameworks &amp; Drivers</b>(세부사항)다. «두 링이 한 칸에 산다»가 이 칸으로 넘어온 걱정이었는데, <b>1계층을 다시 열지 않고 폴더로 갈라서 답한다</b> — 링의 차이가 <b>import 규칙의 차이</b>로 나타난다. 한쪽은 <b>아무것도 모르고</b>(리프), 한쪽은 <b>양쪽을 다 안다</b>(번역자).</dd>
<dt>파일 이름을 <b>선언과 똑같이</b> 쓴다</dt>
<dd><code>domain_layer/order/order_repository.py</code>(선언) ↔ <code>driven_layer/adapter/persistence/repository/order_repository.py</code>(구현).<br><b>1:1 이 이름으로 검사된다</b> — 선언마다 구현이 정확히 하나. 기술은 §4 대로 <b>클래스 이름</b>에 붙인다(<code>DjangoOrderRepository</code>). 경로에 <code>django_</code> 를 또 붙이지 않는 이유는 <b>D7</b> 근거③ 과 같다 — <b><code>driven_layer/</code> 가 이미 그 말을 했다.</b><br>폴더가 아니라 <b>파일</b>인 것도 <b>D12</b> 그대로다 — 애그리거트당 하나다.</dd>
<dt>이 칸에서 검사되는 것 <span class="dim">지금까지</span></dt>
<dd><b>①</b> <code>django_&lt;bounded_context&gt;/**</code> 는 <code>django</code> 와 <b>같은 폴더 안</b> 말고 아무것도 import 하지 않는다 <span class="dim">— 단 <code>admin/**</code> 는 대상에서 뺀다(트리 74행이 «규정 밖 구역»으로 화살표를 규정하지 않았다 · <b>D21</b> · 08-07 · 2차 리뷰 S7)</span><br><b>②</b> <code>domain_layer/&lt;A&gt;/&lt;A&gt;_repository.py</code> 마다 <code>driven_layer/repository/&lt;A&gt;_repository.py</code> 가 <b>정확히 하나</b><br><b>③</b> <code>repository/</code> 밖에서는 아무도 <code>django_&lt;bounded_context&gt;/</code> 를 import 하지 않는다 <span class="dim">— 나머지 어댑터 자리가 정해지면 그쪽까지 넓어진다</span><br><b>④</b> <code>apps.py</code> 가 <code>label</code> 을 <b>명시 선언</b>하고, 그 값이 <b>BC 폴더 이름과 같다</b> <span class="dim">— 폴더는 <code>django_</code> + 그 값 · 08-06 · R9</span></dd>
<dt class="ans-dt">남은 것 — <b>넷 중 둘이 비어 있다</b></dt>
<dd class="ans-dd filled"><b>칸 셋</b> — ⒜ <b>타 BC 출구</b>: <b>D9</b> 가 <code>open_host_service/</code>(입구)의 짝을 <b>Anticorruption Layer</b>(출구)라 했고 <b>D14</b> 가 «타 BC 도 <code>port/</code> 경유»로 정했다 — 그 어댑터가 여기다. ⒝ <b>나머지 포트 어댑터</b>: <code>application_layer/port/</code> 의 UnitOfWork · Clock · 게이트웨이 · 알림 · 조회 포트 구현. ⒞ <b>이벤트 발신</b>: <b>D13</b> 의 «정직한 공백» — 도메인 이벤트를 통합 이벤트로 <b>번역</b>해 내보내는 자리.<br>
<b>08-06 — 셋이 다 닫혔다.</b> 타 BC 출구는 <b>D17</b>, 바깥 시스템은 <b>D18</b>, <b>이벤트 발신은 <b>D34</b> 가 «칸을 안 연다»로 닫았다</b>. 나머지 포트 어댑터(⒝)도 그 사이 <b>D29</b>·<b>D31</b> 이 갈라 앉혔다. 이름은 <b>D16</b>, 화살표와 앎의 범위는 <b>D20</b> 이다.</dd>
</dl>

## D5 · 칸들 사이의 화살표를 어떻게 그리나

**확정 · 08-05** · 자리 — ③ 화살표 &nbsp;·&nbsp; 닫는 문제 <b>P11</b>

<div class="pre-wrap">
<pre><code>presentation_layer → application_layer → (domain_layer + infra_layer)
                                                          ▲
                                    application 이 infra 를 의존한다고 읽힌다</code></pre>
</div>
<dl class="kv">
<dt>실측</dt>
<dd><code>application_layer</code> → <code>driven_layer</code> import <b>0개</b>. 코드는 DIP 를 지키고 <b>틀린 것은 문장 한 줄</b>이다.</dd>
<dt>막고 있던 것이 풀렸다</dt>
<dd>«D2 에서 칸이 늘면 다시 그려야 한다»가 미룬 이유였는데, <b>D2 가 최상위 칸을 만들지 않기로 닫혔다</b>. 칸 수가 안 늘었으므로 그림이 흔들릴 일이 없다.</dd>
<dt>세 칸은 이미 그려졌다</dt>
<dd><code>driving_layer</code> → <code>application_layer</code> <b>만</b>(D11)<br><code>domain_layer</code> → <b>아무것도 안 한다</b>(D13, 나가는 화살표 0)<br><code>application_layer</code> → <code>domain_layer</code> <b>와 자기 <code>port/</code> 만</b>(D14)<br><b>남은 건 <code>driven_layer</code> 하나</b>다 — 그 칸을 열면 D5 가 바로 닫힌다.</dd>
<dt class="ans-dt">결정 — 네 칸이 다 그려졌다</dt>
<dd class="ans-dd filled"><div class="pre-wrap"><pre><code>driving_layer ──▶ application_layer ──▶ domain_layer
                         ▲                    ▲
                         └──── driven_layer ──┘
                              (포트를 구현한다)</code></pre></div>
<b>화살표가 전부 안쪽을 향한다.</b> <code>driven_layer</code> 도 <em>안쪽</em>을 향한다 — <b>실행은 밖에서 일어나지만 아는 방향은 반대</b>다. 그래서 «application 이 infra 를 의존한다»고 읽히던 문장이 없어진다.</dd>
<dt>네 줄로 적으면</dt>
<dd><code>driving_layer</code> → <code>application_layer/&lt;area&gt;/</code> <b>만</b> <span class="dim">D11</span><br>
<code>application_layer</code> → <code>domain_layer</code> + 자기 <code>port/</code> <b>만</b> <span class="dim">D14</span><br>
<code>domain_layer</code> → <b>아무것도</b> <span class="dim">D13</span><br>
<code>driven_layer</code> → <code>domain_layer</code> + <code>application_layer/port/</code> <b>만</b> <span class="dim">D20</span><br>
그리고 <code>composition_root</code> <b>혼자 넷을 다 안다</b> — 그것이 <b>DIP 가 지켜진다는 증거</b>다.</dd>
<dt>D3 이 넘긴 숙제도 여기서 답한다</dt>
<dd><code>*_layer</code> 이름 넷이 Evans 의 «층층이 쌓인» 그림으로 읽힐 위험이 있었다. <b>위 그림이 그 오독을 막는다</b> — 넷은 <em>쌓인 층</em>이 아니라 <b>안팎</b>이고, <code>driving</code> 과 <code>driven</code> 은 <b>같은 바깥에서 방향만 반대</b>다.</dd>
<dt>실측과 어긋나지 않는다</dt>
<dd>정본 121줄이 <code>presentation_layer → application_layer → (domain_layer + infra_layer)</code> 였는데, <b>틀린 것은 문장 한 줄뿐</b>이었다 — 코드의 <code>application → infra</code> import 는 <b>0 건</b>이다.</dd>
</dl>

## D21 · 어드민 — 규정 밖 구역으로 둔다

**확정 · 08-05** · 자리 — ① 칸 · ② 이름 &nbsp;·&nbsp; <code>driven_layer/django_&lt;bounded_context&gt;/admin/</code> &nbsp;·&nbsp; <b>같은 날 오후에 뒤집었다</b>

<p><b>08-05 오전에 「모델만 안다」로 좁혀 닫았다가, 오후에 뒤집었다.</b> 뒤집은 이유는 하나다 — <em>「정말 필요한 기능이라면 admin 에서 개발한다」</em>가 방침으로 정해졌기 때문이다. 좁힌 규칙 아래에서는 그게 <b>전부 위반</b>이 된다.</p>
<dl class="kv">
<dt>실측을 다시 보니 어드민은 이미 «기능»이다</dt>
<dd><code>*_admin.py</code> <b>15개 중 11개</b>가 유스케이스를 부른다. 모델 화면만인 건 4개(<code>accounts</code> 3 · <code>llm_meta</code> 1)다.<span class="dim">08-07 · 3차 리뷰 정정 — 옛 값 「11개 중 8개」는 <code>llm_meta</code> 어드민 4개를 통째로 빠뜨렸다(그중 3개가 유스케이스를 부른다). <b>수가 커졌는데 결론이 안 움직였다는 것 자체가 이 수치가 판정선을 잡고 있지 않다는 방증이다.</b></span>
<div class="pre-wrap"><pre><code>payment_admin.py     save_model 을 막고, get_urls() 로 checkout/ 화면을 붙이고,
                     그 화면에서 build_checkout_payment_command() 를 실행한다
product_admin.py     save_model · delete_model 이 곧 유스케이스 호출
report 4 · managed_copy 2   프롬프트 판 · 관리 문구 저장</code></pre></div>
<b>모델 편집 화면이 아니라 운영 기능이다.</b> 좁힌 규칙을 유지하면 이 8개가 갈 곳이 없다.</dd>
<dt class="ans-dt">결정 — 자리와 이름만 정하고, <b>화살표·앎의 범위는 규정하지 않는다</b></dt>
<dd class="ans-dd filled"><b>① 자리</b> — <code>django_&lt;bounded_context&gt;/admin/</code> · <code>django_&lt;bounded_context&gt;/templates/admin/&lt;bounded_context&gt;/</code>. <em>둘 다 django 가 강제한다.</em><br>
<b>② 이름</b> — <b><code>admin/&lt;entity&gt;/panel.py</code> · <code>form/&lt;form&gt;_form.py</code> · <code>feature/&lt;feature&gt;.py</code></b> · <em>모델 하나 = 폴더 하나</em>. <b>안은 자유.</b><br>
<b>③ 화살표 · ④ 앎의 범위</b> — <b>«리프 규칙» 둘만 면제한다.</b> <b>D22</b> 의 <code>scripts/</code> 와 같은 취급이다.<br>
<span class="dim">→ <b>예외 조항이 아니라 관할 표시</b>다. 예외는 규칙 안에 숨지만, 이건 <b>트리에 「규정하지 않는다」라고 적혀 있다</b>.</span></dd>
<dt>왜 규칙 없이 안전한가 — 실측 셋</dt>
<dd><div class="pre-wrap"><pre><code>다른 BC import        0 / 11
리포지토리 직접 호출   0 / 11
도메인 로직(반복·계산) 0 / 11</code></pre></div>
<b>규칙이 없었는데도 깨끗하다.</b> 그리고 정말 중요한 불변식은 <b>이미 DB 가 지킨다</b> — 프롬프트 판은 <code>trg_…_append_only</code> 트리거가 수정을 거부한다. <em>도메인 규칙이 중요하면 DB 로 강제하는 게 맞고, 그러면 어드민 규칙은 이중 방어다.</em></dd>
<dt>가벼운 안을 두고 완전 예외를 골랐다</dt>
<dd>중간안이 있었다 — <b>「읽기는 자유, 쓰기는 유스케이스를 통한다」</b> 한 줄. 되돌리기 어려운 사고(모델 직접 <code>UPDATE</code> 로 불변식 우회) 하나만 막는 안이다.<br>
<b>완전 예외를 고른 값</b>: 규칙 0 · 화면 쪽 자유 완전 개방 · 지금 11개 그대로 통과. <b>치르는 값</b>: <em>DB 제약을 빠뜨린 애그리거트는 어드민에서 우회될 수 있다.</em> 트리로는 못 막는다.</dd>
<dt>하위 구조 — <b>참고였다가 확정으로 올렸다</b></dt>
<dd>처음엔 평평하게(<code>&lt;entity&gt;_admin.py</code> 하나) 두고 폴더 형태는 <em>참고</em>로만 뒀다. 근거는 <b>「실측 11개 중 10개가 커스텀 기능 0~1개」</b>였다. <b>그 근거가 무너졌다</b> — 운영 유스케이스 9개가 어드민 안으로 들어오면서 <b>11개 중 8개</b>가 기능 코드를 담는다.
<div class="pre-wrap"><pre><code>                                 지금      유스케이스가 들어온 뒤
product_admin                    193줄  →  318줄   (+ create 31 · update 64 · delete 30)
child_targeted_copy_item_admin    72줄  →  155줄   (+ 83)
general_copy_item_admin           63줄  →  133줄   (+ 70)
report × 4                        94줄  →  132줄   (+ 38)</code></pre></div>
<b>파일 하나로는 안 된다.</b>
<div class="pre-wrap"><pre><code>admin/&lt;entity&gt;/
  panel.py                ModelAdmin — 등록 · 목록 · 권한 · django 훅
  form/&lt;form&gt;_form.py    폼 — panel.form · add_form · 인라인 폼
  feature/&lt;feature&gt;.py    운영 기능 하나 = 파일 하나</code></pre></div>
<b>가르는 기준 — panel 은 «등록»하고 feature 는 «한다».</b> <code>get_urls()</code> 는 django 훅이라 <code>panel</code> 에 남고, 그게 가리키는 뷰가 <code>feature/</code> 로 간다. <code>save_model</code> 도 마찬가지 — 훅은 <code>panel</code> 에, 몸통은 <code>feature/</code> 에.<br>
<span class="dim"><b><code>form/</code> 도 폴더다</b> — 한 엔티티에 폼이 여럿이 될 수 있다(<code>panel.form</code> 편집 폼 · <code>add_form</code> 추가 폼 · 인라인 폼). 실측은 아직 어드민당 1개지만 <code>feature/</code> 와 <b>모양을 맞춘다</b>.</span></dd>
<dt><code>feature/</code> 안은 <b>최단거리로 짠다</b></dt>
<dd>유스케이스 «형태»(클래스 + Request DTO + Result DTO)는 <b>D14</b> 가 <code>application_layer</code> 에 건 규칙이다. <b>여기는 그 규칙이 안 걸린다</b> — 함수 하나면 된다.
<div class="pre-wrap"><pre><code>admin/product/feature/create_product.py

def create_product(name, price, ...):
    with unit_of_work() as uow:
        product = Product.create(name=name, price=price, ...)   ← 도메인은 그대로 쓴다
        return uow.products.save(product)</code></pre></div>
<b>DTO 두 개가 없어진다.</b> 다만 <b><code>Product</code> 애그리거트와 리포지토리는 그대로 쓴다</b> — 그건 <code>domain_layer</code> 이고 <b>규정 안</b>이다. 어드민이 그걸 <em>부르는</em> 것은 자유고 <em>우회하는</em> 것은 다른 얘기다.<br>
<span class="dim"><code>feature/</code> 에는 두 종류가 산다 — <b>유스케이스</b>(<code>panel</code> 의 <code>save_model</code> 이 부른다)와 <b>커스텀 뷰</b>(<code>get_urls()</code> 가 가리킨다). 둘 다 「운영 기능 하나」라 같은 폴더다. <code>checkout_payment</code> 처럼 <b>사용자 API 와 공유</b>하는 유스케이스는 <code>application_layer</code> 에 남고 <code>feature/</code> 에는 화면만 온다.</span></dd>
<dt>접미사가 하나 줄었다</dt>
<dd>「접미사는 겹칠 때만」으로 재면 <b>필수인 리프가 둘에서 하나로</b> 준다.
<div class="pre-wrap"><pre><code>models/&lt;entity&gt;_model.py   파일명에 entity 가 있다 · 도메인 &lt;entity&gt;.py 와 겹친다  → 접미사 필요
admin/&lt;entity&gt;/panel.py    파일명은 panel 이다 · 겹칠 게 없다                    → 접미사 불필요</code></pre></div>
<code>&lt;entity&gt;</code> 가 파일 이름에서 <b>폴더 이름으로 옮겨 가면서</b> <code>_admin</code> 이 할 일이 없어졌다. <b><code>models/&lt;entity&gt;_model.py</code> 가 다시 「접미사가 필수인 유일한 리프」가 된다.</b><br>
<span class="dim"><code>__init__.py</code> 는 트리에 안 그린다 — <code>models/</code> 도 하위를 re-export 하지만 안 그렸다. 다만 <code>admin/__init__.py</code> 는 <b>하위 <code>panel</code> 을 import 해야 django 가 등록한다</b>(안 쓰면 어드민이 아예 안 뜬다).</span></dd>
<dt>템플릿 자리 — 트리의 구멍이었다</dt>
<dd>어드민 화면을 만들면 HTML 이 필요한데 <b>정본 트리에 자리가 없었다</b>(실측 3개). 그리고 <b>entity 폴더 아래로 못 내린다</b> — django 는 템플릿을 «경로»가 아니라 <b>«전역 이름»</b>으로 찾는다.
<div class="pre-wrap"><pre><code>ModelAdmin.render_change_form →  "admin/&lt;app_label&gt;/&lt;model_name&gt;/change_form.html"
                                 "admin/&lt;app_label&gt;/change_form.html"
                                 "admin/change_form.html"
get_app_template_dirs         →  Path(app_config.path) / "templates"   ← 앱 루트 밑 한 곳뿐</code></pre></div>
어디에 두든 <b>이름에 app·model 을 다시 적어야</b> 해서, 옮기면 엔티티 이름이 경로에 두 번 나온다. <b>모르면 틀리는 곳 둘</b>: 경로에 오는 이름은 폴더(<code>django_…</code>)가 아니라 <code>apps.py</code> 의 <code>label</code> · 덮어쓰기 경로의 <code>&lt;model&gt;</code> 은 <b>모델 클래스명을 전부 소문자로 붙인 것</b>(<code>FamilyProductAssignmentModel</code> → <code>familyproductassignmentmodel</code>).</dd>
<dt>딸려 나온 것 — <b>운영 유스케이스가 여기 산다</b></dt>
<dd>어드민을 열어두니 <b>운영자 전용 유스케이스가 BC 안에 쌓인다</b>는 걱정이 나왔다. 한때 <code>application_layer/operation/</code> 이라는 칸으로 갈랐다가 <b>접었다</b> — <em>규정 밖 구역이라면 부르는 쪽 안에 두는 것이 일관된다</em>.
<div class="pre-wrap"><pre><code>admin/ 안에 산다                  9개 · 806줄
  create_*_prompt_revision × 4     38줄×4    어드민만 부른다
  create/update/delete_product     31·64·30  scripts/ 가 가져다 쓴다
  save_*_copy_item × 2             70·83     scripts/ 가 가져다 쓴다

application_layer 에 남는다        4개 · 377줄
  배치 4(expire_usage_reservations …)  driving_layer 는 로직 금지(D11) 라 celery 안에 못 넣는다</code></pre></div>
<b>「부르는 쪽에 둔다」가 어디서 멈추나</b> — 어드민은 <b>규정 밖</b>이라 무엇을 담아도 된다. <code>driving_layer/</code> 의 celery 칸은 <b>규정 안</b>이고 <b>D11</b> 이 「로직을 갖지 않는다」를 이미 못 박았다 — 그래서 배치 4개는 못 따라간다. <em>규정 밖과 규정 안의 경계가 그대로 답이 됐다.</em><br>
<b>정직한 값 둘</b> — ① 지금 <code>test/unit/application/</code> 에서 <b>DB 없이</b> 도는 테스트(<code>test_product_commands.py</code>·<code>test_save_copy_item_commands.py</code>)가 <b><code>integration/</code> 으로 내려간다</b> ② <code>scripts/</code> 가 <code>admin/</code> 을 물어 <b>어드민을 마음대로 못 지운다</b>. <span class="dim">둘 다 «규정 밖 구역끼리 얽히는» 값이다 — <b>깨져도 규칙이 안 잡아준다</b>. 사용자 판단: 「스크립트가 깨지는 건 예상한 일이고, 애초에 <code>scripts/</code> 가 많이 쓰이는 게 좋지 않다」.</span></dd>
</dl>

## D22 · 관리 명령 — 칸을 만들지 않는다

**확정 · 08-05** · 자리 — ① 칸 &nbsp;·&nbsp; <code>management/commands/</code> 를 트리에서 <b>뺀다</b>

<p><b>무엇인가</b> — django 의 커스텀 관리 명령이다. <code>&lt;app&gt;/management/commands/&lt;name&gt;.py</code> 를 놓으면 <code>python manage.py &lt;name&gt;</code> 이 생긴다. <b>경로가 하드코딩</b>이라 다른 데 두면 못 찾고, <em>파일 이름이 곧 CLI 명령 이름</em>이다.</p>
<p><b>왜 열렸나</b> — 정본 트리에 없는 자리인데 코드가 산다(8 BC · 11파일). 트리에 없으니 규칙도 없고, <b>성격이 다른 셋이 한 폴더에 섞여</b> 있었다.</p>
<dl class="kv">
<dt>실측을 코드까지 읽으니 분류가 바뀌었다</dt>
<dd><div class="tw"><table class="pairtbl"><thead><tr><th>종류</th><th>수</th><th>누가 부르나 — <b>실측</b></th></tr></thead><tbody>
<tr><td><b>주기 배치</b></td><td class="mono">3</td><td>cron·systemd timer <b>0건</b> → <b>아무도 안 부른다</b></td></tr>
<tr><td><b>시드</b></td><td class="mono">4</td><td>자동화 <b>0건</b> → 사람이 손으로</td></tr>
<tr><td><b>점검·복구</b></td><td class="mono">4</td><td>사람이 손으로</td></tr>
</tbody></table></div>
<b>배치가 4 가 아니라 3 이었다.</b> <code>pairing_replay_approval_notifications</code> 는 항목마다 <code>request_id=… status=… failure=…</code> 를 찍는다 — 나머지 셋은 <code>"Completed 7 …"</code> 한 줄만 찍는다. <b>건별 진단을 사람에게 보여주는 복구 도구</b>이지 주기 배치가 아니다.<br>
그리고 <b>우리 명령을 부르는 자동화가 0건</b>이다 — <code>fabfile.py</code>·<code>Makefile</code> 이 부르는 건 <code>check</code>·<code>migrate</code>·<code>collectstatic</code> 뿐, <b>전부 django 내장</b>이다.</dd>
<dt>celery 가 답을 뒤집었다</dt>
<dd>한때 ⒞ <b>「배치만 인정」</b>이 유력했다 — 배치 4 만 와이어링을 거치고 ORM 을 안 만지는 <em>깨끗한</em> 쪽이었기 때문이다. 그런데 <b>celery 를 쓰면 그 배치가 통째로 빠져나간다</b>: celery 는 파이썬 함수를 직접 부르니 <code>manage.py</code> 를 거칠 이유가 없다. <b>⒞ 는 빈 칸이 된다.</b><br>
<span class="dim">celery 는 <code>autodiscover_tasks(<b>packages=</b>…)</code> 로 <b>경로를 우리가 정할 수 있다</b> — management 명령과 달리 강제가 없어서, 입구를 <code>driving_layer/</code> 에 둘 수 있다. <b>08-07 · R10 ⒞ 정정</b> — 옛 문장은 <code>related_name</code>·<code>imports</code> 라고 썼는데 둘 다 안 된다(<b>D26</b>).</span></dd>
<dt class="ans-dt">결정 — 칸을 만들지 않는다</dt>
<dd class="ans-dd filled"><b><code>application/**/management/commands/</code> 를 만들지 않는다.</b><br>
<b>주기 배치 3</b> → celery task(<code>driving_layer/</code>) · <b>시드 4 · 점검·복구 4</b> → 저장소 루트 <code>scripts/</code>.<br>
<b><code>scripts/</code> 는 규정하지 않는다</b> — 이름도 화살표도 앎의 범위도. <em>임시 · 일회성 · 정말 자주 안 쓰는 것만 둔다.</em><br>
<span class="dim">→ 그리고 <b><code>driven_layer/</code> 안에 주도 입구가 섞이던 모순이 통째로 없어진다</b>.</span></dd>
<dt>왜 <code>scripts/</code> 는 규정 없이 안전한가</dt>
<dd><b><b>P4</b> 「최후 수용소」와 다르다.</b> P4 는 <em>규칙이 있는 트리 «안»</em>에 규칙 없는 칸을 두는 것이고, <code>scripts/</code> 는 <b>트리 «밖»</b>이다 — 예외가 아니라 <b>관할 밖</b>이다.<br>
그리고 <b>작게 유지된다는 전제</b>가 붙었다. 파일 수가 늘면 그 자체가 신호다 — <em>어드민으로 갔어야 할 게 안 간 것</em>. <b>규칙이 아니라 계기판으로 쓴다.</b><br>
<span class="dim">덤 — 시드 4 는 지금 <code>models/</code> 를 직접 만져 <b>D15</b> 리프 규칙에 걸린다. 트리 밖으로 나가면 <b>예외 조항 없이</b> 그 문제가 사라진다.</span></dd>
<dt><code>scripts/</code> 는 어드민을 가져다 쓴다</dt>
<dd>상품·문구 유스케이스는 <b>어드민 안에 산다</b>(<b>D21</b>) — 시드 스크립트는 그걸 import 한다. <b>규정 밖 구역 둘이라 규칙에 안 걸린다.</b><br>
<b>값</b> — 어드민을 고치면 스크립트가 <em>조용히</em> 깨질 수 있고 아무도 안 잡아준다. <span class="dim">받아들인 이유: <b>스크립트는 지워도 되는 자리</b>라 깨지는 게 예상된 일이고, <b><code>scripts/</code> 가 많이 쓰이면 그 자체가 신호</b>다.</span></dd>
<dt>정직한 값 둘</dt>
<dd><b>① django 부팅을 직접 해야 한다</b> — <code>DJANGO_SETTINGS_MODULE</code> + <code>django.setup()</code> 세 줄. <code>settings/__init__.py</code> 가 태워지므로 <code>.env</code> 로딩은 그대로 산다. 공용 부트스트랩 하나로 끝난다.<br>
<b>② BC 밖에서 BC 안을 부른다</b> — <code>scripts/</code> 는 BC 가 아니라 <b>어댑터</b>다(헥사고날에서 주도 어댑터는 육각형 밖, 클린에서 Main 은 가장 바깥). 위험은 <em>한 스크립트가 여러 BC 를 부르기 시작할 때</em>인데, <b>실측 11/11 이 단일 BC</b>다.</dd>
<dt>남은 구멍 — 트리 문제가 아니다</dt>
<dd>배치 셋의 <b>재시도 전략 전체가 「다음 주기가 재시도한다」에 걸려 있는데</b>(코드 주석 6곳), <b>스케줄러가 저장소에 없다</b>. 지금 실패한 리마인더는 영영 안 나간다. <em>운영 구멍이고, 여기서 고칠 것이 아니라 기록해 둔다.</em></dd>
<dt>세 관점</dt>
<dd><b>헥사고날</b> — 배치는 드라이버다. <code>driven</code> 에 있던 게 틀렸고, celery 로 가면 <b>제자리를 찾는다</b>. <b>클린</b> — 파싱 + 와이어링 + 종료 코드는 Main 컴포넌트의 일이라, 그게 <code>scripts/</code> 든 celery task 든 <b>같은 일</b>이다. <b>DDD</b> — 말이 없다.</dd>
</dl>

## D6 · 와이어링 파일 둘 — 자리가 갈렸다

**확정 · 08-06** · 자리 — ① 칸 &nbsp;·&nbsp; <code>&lt;bounded_context&gt;_api_router.py</code> + <code>composition_root/dependency_wiring.py</code> &nbsp;·&nbsp; <b>트리의 마지막 열린 칸이었다</b>

<p>둘 다 <b>와이어링 파일</b>이다 — 하나는 라우트를, 하나는 의존성을 꽂는다. 클린의 <b>Main 컴포넌트</b>이고 DDD·헥사고날은 이 자리에 말이 없다. 처음엔 <b>묶어서 함께</b> 정하려 했는데, <b>실측이 둘을 갈랐다</b>.</p>
<div class="pre-wrap">
<pre><code>&lt;bounded_context&gt;_api_router.py    13파일 · 중앙값 16줄   부르는 쪽 → presentation 22 · django 2
composition_root.py    15파일 · 중앙값 107줄  부르는 쪽 → 67곳 · 얘가 부르는 곳 → 264건</code></pre>
</div>
<dl class="kv">
<dt><code>api_router</code> — 하는 일이 <b><code>api/</code> 하나</b>다</dt>
<dd>파일 전문이 이만큼이다.
<div class="pre-wrap"><pre><code>&quot;&quot;&quot;Products BC 배선 — 단일 NinjaExtraAPI 에 controller 들을 등록한다.&quot;&quot;&quot;
from application.products.presentation_layer.api.product.product_controller import ProductController
from broccoli_server.api import api          ← 프로젝트 전역 객체
api.register_controllers(ProductController)</code></pre></div>
<b><code>api/</code> 안의 컨트롤러를 모아 꽂는 것뿐</b>이고 <code>open_host_service/</code> 와는 무관하다 — 타 BC 는 함수를 <b>직접</b> 부르니 라우팅이 없다. 소비자는 프로젝트 <code>urls.py</code> 하나(<code># noqa: F401 registers controllers</code> — <b>import 자체가 등록</b>이다).</dd>
<dt class="ans-dt">결정 — 자리가 갈린다</dt>
<dd class="ans-dd filled"><b><code>&lt;bounded_context&gt;_api_router.py</code> → <code>driving_layer/api/api_router.py</code>.</b> <span class="dim">(08-06 에 이름과 방식까지 정했다 — 아래)</span><br>
<b><code>composition_root/dependency_wiring.py</code> → BC 루트 그대로.</b> <em>어느 층에도 못 들어간다</em> — 아래 소거법으로 <b>하나만 남는다</b>.</dd>
<dt class="ans-dt">08-06 — <b>이름 <code>api_router.py</code> · 방식은 「전달받은 API 에 함수로」</b></dt>
<dd class="ans-dd filled">플러그인 대조(<b>D27</b>)에서 나왔다. <b>이름만 다른 게 아니라 등록 방식이 달랐다.</b>
<div class="pre-wrap"><pre><code>지금    from broccoli_server.api import api      BC 가 프로젝트를 import
        api.register_controllers(...)            module top-level 에서 «즉시» 실행
        urls.py 가 # noqa: F401 로 부작용 등록

이후    def register_&lt;bc&gt;_api(api):             함수 · api 를 «받는다»
        urls.py 가 register_&lt;bc&gt;_api(api)        «명시» 호출
        @api_controller(..., auto_import=False)  자동 등록을 끈다</code></pre></div>
<b>값 넷</b> — ①<b>화살표가 뒤집힌다</b>: BC 가 프로젝트를 모르게 되어 다른 프로젝트로 옮겨도 안 깨진다. ②<b>테스트가 격리된다</b>: 지금은 모듈을 import 하는 순간 전역 <code>api</code> 가 오염돼 테스트 전용 인스턴스를 못 만든다. ③<b>조용히 사라지지 않는다</b>: <code>urls.py</code> 의 그 11줄은 문법상 「안 쓰는 import」라 정리 도구가 지우면 <b>엔드포인트가 통째로 없어지는데 에러가 안 난다</b>(404 만 난다). 함수 호출은 지울 수 없다. ④<b>등록 순서를 우리가 소유</b>한다(지금은 import 순서에 딸려간다).<br>
<span class="dim">이 모양의 이름이 <b>Configurable Dependency</b> 다 — 구현을 밖에서 <b>«넣지»</b>, 안에서 «찾지» 않는다.
<b>출처는 한 겹이 아니다</b> — 낱말은 <b>Meszaros</b> 에서 왔고 <b>Cockburn 이 「Dependency Injection 보다 나은 이름」으로 밀었으며</b>, 헥사고날 문맥의 정식화는 <b>Garrido de Paz</b> 의 해설에 있다(<em>“a configurable dependency is a dependency of an object on an interface … an argument of the object constructor”</em>).
<b>Cockburn 의 헥사고날 원문 페이지에는 이 낱말이 «없다»</b> — 4차 리뷰가 그걸 짚었다. 안에서 찾는 쪽(서비스 로케이터)은 이 트리에 문이 없다 — <code>composition_root</code> 밖에서 구현을 얻는 자리가 없다.</span><br>
<b>따라온 값 — 위 D11 예외가 없어진다.</b> 프로젝트 <code>api</code> 를 import 하지 않으니 <b>「칸 바로 밑 파일이라 사정거리 밖」이라는 조항이 필요 없다.</b> 예외를 지키는 게 아니라 <b>예외가 생길 이유를 없앤 것</b>이다.<br>
<b>이름</b> — <code>&lt;bounded_context&gt;_</code> 접두를 뗀다. 현행이 <code>accounts_api_router</code> 인 건 <b>BC 루트에 있어서</b>(실측 13파일 전부) 이름으로 구분해야 했기 때문이고, <code>api/</code> 안으로 들어오면 <b>경로가 이미 BC 를 말한다</b>. 남는 <code>api_router.py</code> 는 <code>&lt;use_case&gt;_command.py</code>·<code>schema/schema_in.py</code>·<code>&lt;area&gt;/&lt;area&gt;_controller.py</code> 와 <b>정확히 같은 모양</b>이다(부모 폴더 이름 + 역할).<br>
<em>플러그인은 이 파일을 <code>presentation_layer/registrar.py</code> 로 부른다 — <b>방식은 받고 이름은 트리를 따른다</b>. 구현에 들어갈 때 플러그인 쪽을 맞춘다.</em></dd>

<dt>08-05 재검 — <b>첫 근거가 약했다</b></dt>
<dd>처음엔 「모든 입구가 부르니 어느 칸에도 안 속한다」로 닫았다. <b>약하다</b> — 부르는 쪽을 정확히 세면 <b>67 중 46 이 driving</b> 이라(<code>api/</code> 22 · <code>open_host_service/</code> 22 · <code>authentication.py</code> 2) <em>「그럼 <code>driving_layer/</code> 밑에 두지」</em> 가 바로 나온다. <b>첫 표에 <code>open_host_service</code> 22 가 통째로 빠져 있었다.</b>
<div class="pre-wrap"><pre><code>부르는 쪽 67    api/ 22 · OHS 22 · admin 8 · scripts 8 · acl 3 · apps.py 2 · authentication 2
                └ 규정 안 51 · 규정 밖 16   (「명령 10」은 8 이었다 — 둘은 주석 언급뿐)</code></pre></div>
<b>답은 «누가 부르냐»가 아니라 «얘가 뭘 부르냐»에 있었다.</b>
<div class="pre-wrap"><pre><code>composition_root 가 부르는 곳
  application_layer  135     ← 어느 층 «안»에 넣으면
  driven_layer       102        그 층이 나머지 둘을 부르는 셈이 된다
  domain_layer        27
  driving_layer        0     ← 한 번도 안 부른다</code></pre></div>
<b>세 층을 다 부른다. 층 밖이어야 하는 건 위치 취향이 아니라 성질이다.</b></dd>
<dt>소거법 — 넷이 <b>각각 다른 제약</b>을 깬다</dt>
<dd><div class="pre-wrap"><pre><code>driving_layer/ 밑      driven_layer 를 102번 부른다        → D11 정면 위반
driven_layer/ 밑       driving 46건이 driven 을 import     → 제약 ①. D16 의 「driven 을
                                                          부르는 건 composition_root 뿐」이
                                                          자기 자신 때문에 무너진다
application_layer/ 밑  application → driven 이 0 → 102     → 제약 ② 정면 위반
프로젝트 루트 통합      2,314줄 한 파일. BC 하나 떼면 전역을 손댄다. 지금 타 BC import 0건이 깨진다
BC 루트                아무것도 안 깨진다                  ← 하나만 남는다</code></pre></div>
취향이 아니라 <b>소거</b>다. 세 관점도 같은 답이다 — 클린의 <b>Main 은 가장 바깥 링</b>이고 어떤 링에도 안 들어간다, 헥사고날은 <b>육각형 밖</b>, DDD 는 말이 없다.</dd>
<dt>③ 화살표 — <b>자기 BC 안에서만</b></dt>
<dd><b><code>composition_root/dependency_wiring.py</code> 는 자기 BC 의 <code>composition_root</code> 만 import 한다.</b> 판정은 한 줄이다 — <em>import 경로의 BC 이름 ≠ 자기 BC 이름이면 위반</em>.<br>
실측 — <b>이 파일들 자신은 타 BC 0건으로 깨끗하다.</b> 어기는 건 <b>부르는 쪽 ACL 3건</b>(<code>pairing</code>×2 · <code>parental_controls</code>×1 → <code>accounts.composition_root.build_get_child_query</code>). <code>accounts</code> 는 <code>child_profile_service</code> 라는 <b>관문을 이미 갖고 있는데도</b> 우회한다 — 제약 ③ 위반이자 <b>D9</b> 우회다.</dd>
<dt>선례 — <b>칸 바로 밑 파일은 그 칸 전체에 걸린 것</b></dt>
<dd><code>driven_layer/unit_of_work.py</code> 가 이미 층 바로 밑에 있다. <b>「폴더 밑은 규칙, 칸 바로 밑 파일은 와이어링」</b>이 트리에 이미 쓰이는 모양이다.</dd>
<dt>따라온 값 — <b>D11</b> 의 사정거리를 좁혔다</dt>
<dd><span class="dim">※ 아래는 08-05 시점 서술이다 — 08-06 개정으로 <b>이 예외 자체가 없어졌다</b>.</span> <code>api_router</code> 는 <b>프로젝트 전역 <code>api</code> 객체</b>를 import 한다. D11 문구가 「<code>driving_layer</code> 는 …」이면 <b>이 파일이 위반</b>이 된다.
<div class="pre-wrap"><pre><code>전:  driving_layer 는                            application_layer/&lt;area&gt;/ 아래만 의존한다
후:  api/&lt;area&gt;/ · open_host_service/&lt;service&gt;/ 아래는  ─ 같은 문구 ─</code></pre></div>
<b>예외를 내는 대신 규칙이 닿는 범위를 정확히 적었다.</b> D11 은 08-04 에도 한 번 이렇게 좁힌 적이 있다(<code>port/</code> 구멍 때문에 <code>&lt;area&gt;/</code> 아래로).</dd>
<dt>따라온 값 둘째 — <code>authentication.py</code> 를 <b>여기서 찾다가 <b>D24</b> 로 넘어갔다</b></dt>
<dd>이 카드의 규칙(「하는 일이 <code>api/</code> 하나면 <code>api/</code> 바로 밑」)을 적용하면 <code>ParentAuth</code>·<code>ChildAuth</code> 는 <code>driving_layer/api/</code> 로 간다 — <b>부르는 쪽 27건이 전부 <code>api/</code></b> 였으니까.<br>
<b>그런데 그 27건 중 24건이 «타 BC» 였다.</b> 자리를 BC 안에 두는 한 <b>규칙 위반이 남는다</b>. → <b>D24 에서 인증을 둘로 갈라 풀었다</b>(틀은 <code>framework/</code>, 해석은 관문). <b>BC 안에는 인증 파일이 남지 않는다.</b></dd>
<dt>유스케이스가 조립하면 안 되나 — <b>08-05 재검</b></dt>
<dd><b>「무엇을 쓸지」는 이미 유스케이스가 정한다.</b> 생성자 시그니처가 그 선언이고(협력자 평균 <b>2.6개</b>), <code>composition_root</code> 는 <b>그 목록을 못 바꾼다</b> — 늘리지도 줄이지도 못하고 채우기만 한다. 남는 물음은 <b>「어느 판본이냐」</b> 하나인데, <b>답이 하나가 아니라서</b> 유스케이스가 못 고른다.
<div class="pre-wrap"><pre><code>GetPurchasableProductQuery(repository: ProductRepository, clock: Callable[[], datetime])

프로덕션    DjangoProductRepository()      timezone.now
단위 테스트  Mock(spec=ProductRepository)   Mock(return_value=고정 시각)  ← 판매 경계 5일을 찍는다</code></pre></div>
유스케이스가 스스로 지으면 <b>이 구멍이 사라진다</b> — 실측 unit 테스트가 «인자를 꽂아» 유스케이스를 직접 생성하는 게 <b>656회</b>(파일 100개)다. 시계를 밖에서 받기 때문에 <em>「오늘 = 판매 시작일」</em> 같은 하루를 테스트할 수 있다.<br>
<b>정직한 값</b> — 프로덕션 구현이 둘 이상인 포트는 <b>108 중 5</b> 뿐이다(FCM · SMS · social auth · OTP · turn event). 나머지 103 은 두 번째 판본이 <b>테스트 대역</b> 하나다. 95% 가 낭비로 보이지만, <b>「안쪽은 바깥을 모른다」는 한 줄은 5개가 아니라 108개 전부에 걸린다.</b></dd>
<dt>정직한 값 — <b>Service Locator 모양</b>이다</dt>
<dd>컨트롤러가 <code>build_…()</code> 를 <b>직접</b> 부르는 건 엄밀히는 Service Locator 다. 순수한 Main 이라면 <b>Main 이 컨트롤러를 만들어 주입</b>해야 하는데, <b>Django/Ninja 가 컨트롤러를 만들기 때문에</b> 그럴 수가 없다 — 화살표가 뒤집힌다.<br>
<b>설계 실수가 아니라 Django 를 쓰는 값</b>이다.<br>
<b>08-06 정정(R6) — 「대안이 없다」고 썼는데 과했다.</b> <code>ninja-extra</code> 에 <code>injector</code> 기반 생성자 주입이 있다 —
컨트롤러 <code>__init__</code> 에 유스케이스 타입을 달고 <code>composition_root</code> 는 <b>타입 → 팩토리 바인딩만</b> 등록하면
컨트롤러가 <code>composition_root</code> 를 import 하지 않아도 된다. <b>대안은 있다. 값이 비쌀 뿐이다.</b>
<div class="pre-wrap"><pre><code>DI 컨테이너가 하나 들어온다     전역 지침의 «DI 컨테이너도 필수가 아니다» 선을 넘는다
매요청 계약을 스코프로 지켜야    잘못 걸면 조용히 싱글톤이 된다
                             — 플러그인이 blocker 로 잡는 바로 그것
와이어링이 둘로 쪼개진다            바인딩 등록이 «또 하나의 와이어링»이 된다</code></pre></div>
그래서 팩토리 호출을 택하되 <b>「대안이 없어서」가 아니라 「값을 비교해서」</b>라고 적어 둔다.<br>
<b>Service Locator 의 «해악»은 따라오지 않는다</b> — 진짜 Service Locator 는 <em>무엇이든 꺼내는 범용 컨테이너</em>라
의존이 어디에도 안 드러나는 게 문제인데, <code>build_&lt;use_case&gt;()</code> 는 <b>이름이 무엇을 꺼내는지 말하고</b>,
<b>반환 타입이 정적으로 드러나고</b>, 없는 함수는 <b>import 시점에 터진다</b>(런타임 해석 실패가 없다).
컨트롤러의 의존도 <b>본문에 그대로 보여 AST 로 셀 수 있다</b>. <em>모양은 같지만 해악은 안 따라온다.</em><br>
<b>사정거리는 <b>D11</b> 이 좁혔다</b> — 자기 BC 의 <code>build_</code> 이름만.</dd>
</dl>

## D24 · framework/ — BC 밖 공용 구역, 이름을 세 번 만에 정했다

**확정 · 08-06** · 자리 — ① 칸 · ② 이름 · ③ 재결정 &nbsp;·&nbsp; <code>common/</code> → <s>platform/</s> → <s>foundation/</s> → <code>framework/</code> &nbsp;·&nbsp; <b>트리 밖에 있어 한 번도 안 세어졌던 구역</b>

<p><code>common/</code> 은 저장소 루트에 있고 트리 «밖»이라 <b>화살표를 한 번도 안 셌다</b>. 열어보니 <b>파일 여섯 개</b>인데 <b>성격이 제각각</b>이었다. 여섯을 하나씩 판정하고, <b>이름은 안이 정해진 뒤에 보기로</b> 미뤘다.</p>
<div class="pre-wrap">
<pre><code>파일                                   줄    쓰는 BC   판정
ninja/response/error_out.py            16    15개 + broccoli_server   남는다
ninja/response/validation_error_out.py 22    13개 + broccoli_server   남는다
django/retryable_database_error.py     36     4개                     남는다
ninja/authentication.py                38     3개                     남는다
broccoli/notification_navigation.py   125     2개                     나간다
enum/child_report_topic.py             43     0개 (lessons 테스트만)  나간다</code></pre>
</div>
<dl class="kv">
<dt>가장 큰 발견 — <code>domain_layer</code> 가 <b>밖을 부르고 있었다</b></dt>
<dd><b>D13</b> 은 「<code>domain_layer</code> 는 나가는 화살표 <b>0</b>」이다. 그런데 실측 <b>6건이 나간다</b>. 안 걸린 이유는 하나 — <b>세는 범위가 <code>application/</code> 안이었고 <code>common/</code> 은 트리 밖이었다.</b> <em>트리에 들이자마자 드러났다 — 이 작업의 값이 여기 있다.</em></dd>
<dt><code>shared_kernel/</code> 을 만들려다 <b>접었다</b></dt>
<dd>처음엔 <code>notification_navigation</code>(<code>delivery</code>·<code>notifications</code> 둘이 쓴다)을 Evans 의 <b>Shared Kernel</b> 로 보고 칸을 만들려 했다. <b>경로를 끝까지 따라가니 필요가 없었다.</b>
<div class="pre-wrap"><pre><code>notifications 도메인
   → notifications/…/acl/delivery_notification_dispatch_adapter.py    ← 관문 앞 ACL
   → delivery/…/contract/request/deliver_notification_request.py
   → deliver_notification(request)                                     ← 관문</code></pre></div>
<b>이미 관문을 제대로 통과하고, 계약이 자기 타입을 갖고 있다</b>(<code>NotificationDeliveryNavigationActionV1</code> + 전용 <code>NavigationPage</code> enum). 넘어가는 건 <b>JSON</b> 이다(<code>navigation_action_json()</code>). 게다가 <code>delivery</code> 의 «값 객체»를 열어보니 —
<div class="pre-wrap"><pre><code>from common.broccoli.notification_navigation import NavigationPage
__all__ = ["NavigationPage"]                    ← 파일 전문이 3줄, 재수출 껍데기다</code></pre></div>
즉 <b>「두 BC 가 도메인을 공유해야 해서」가 아니라 「검증 코드를 한 번만 쓰려고」</b>였다. 걷어내도 경계는 멀쩡하다. → <b>125줄을 셋으로 갈라 주인에게 준다</b>: 화면 목록·파라미터 규칙·<code>parse()</code> 는 <code>notifications</code> 도메인 · 경계 형식은 <b>이미 계약에 있음</b> · <code>NavigationLinkFactory</code> 는 <code>delivery</code> 도메인.<br>
<b>칸을 안 여는 이유는 「아직 안 쓰여서」가 아니다</b> — <b>BC 사이의 공유는 언제나 관문 + 번역으로 푼다</b>(전역 제약 ③). Shared Kernel 은 그 관문 없이 <b>모델 자체를 나눠 갖는</b> 패턴이라 이 트리에서는 <b>정의상 자리가 없다</b>. 위 경로가 그 증거다 — 관문을 제대로 통과하고 계약이 자기 타입을 갖고 있어서, 「공유해야 한다」로 보이던 것이 실은 <b>검증 코드 재사용</b>이었다. <b>같은 모양이 또 나와도 답은 같은 자리다.</b><br>
<span class="dim"><b>08-07 · 2차 리뷰 S2</b> — 옛 문장은 <em>「아직 안 쓰이는 자리는 만들지 않는다 — 진짜 Shared Kernel 이 생기면 그때 연다」</em> 였다. R13 이 세운 자(<b>「나중에 그때 연다」로 끝나는 문장은 그 자체가 결함</b>)에 걸려 근거를 갈았다. <b>결론도 트리도 안 바뀐다</b> — 갈아 낀 근거는 이 카드가 아래에서 이미 쓰고 있던 것이다(<em>「Shared Kernel 을 «만들지 않은 것»이 DDD 적 결론이다 — 관문·계약이 이미 일하고 있었다」</em>).</span></dd>
<dt>폴더 여섯 판정 — <b>축이 하나여야 한다</b></dt>
<dd><div class="pre-wrap"><pre><code>broccoli/         나간다   내용이 도메인 · 이름이 «제품명»이라 표준 트리에 못 쓴다 · 축이 다르다
enum/             나간다   축이 다르다(나머지는 「무엇에 딸렸나」, 이것만 「자료형이 뭐냐」)
                           그리고 모든 enum 이 들어올 수 있어 게이트가 안 된다
ninja/response/   나간다   파일이 이미 _out 이라 말하는데 폴더가 같은 말을 반복한다
                           request/ 짝이 없다 — 방향 축인데 값이 하나뿐(D7 과 같은 수)
django/ · ninja/  남는다   「그 라이브러리 타입 없이 말이 되나?」 로 판정된다
test/             남는다   다만 하위가 소스를 미러링했다 → BC 의 test/ 규칙을 그대로 쓴다</code></pre></div></dd>
<dt class="ans-dt">테스트 뼈대 — <b>08-07 · R11 에 판정 축을 고쳤다</b></dt>
<dd class="ans-dd filled"><b>옛 축은 «몇 개 BC 가 쓰나»였고, 그 축이 자기가 지키려던 규칙을 어겼다.</b> 가장 많이 쓰이던 <code>login_session</code>(13개 BC)이 본문에서 <code>/v1/auth/social-login</code> 을 POST 하고 200 을 단언한다 — 올리면 <b>공용 칸이 accounts 엔드포인트 목록을 갖는다</b>. <b>D25</b> 가 이름 붙인 «규칙이 아니라 목록» 병이 <b>공용 칸에서 재발</b>한다.<br>
<b>새 축 — 「BC 하나를 지웠을 때 이 파일이 바뀌나?」</b> <span class="dim">문서의 «55건»은 옛 코퍼스다. 재측정하면 타 BC 의 <code>test/</code> 를 import 하는 게 <b>67문 · 심볼 199회</b>.</span>
<div class="pre-wrap"><pre><code>올라간다    BC 중립  5종  57회   bearer 28 · assert_problem 20 · jpost 6
                                   assert_core_only_problem 2 · authed_post 1   (12개 BC 가 쓴다)
안 올라간다  BC 고유 24종 131회   login_session 40 · bootstrap_family 33
                                   create_child 25 · pair_existing_child_via_qr 12 · …
안 올라간다  factory  8종  11회   ParentModelFactory 3 · ChildModelFactory 2 · LessonModelFactory · …</code></pre></div>
<b>중립 5종은 진짜 공용이다</b> — <code>bearer(token)</code> 은 HTTP 헤더를 만들고 <code>assert_problem(resp, status, type_slug)</code> 은 RFC 9457 형식을 검사한다. <b>이름·시그니처·본문 어디에도 업무 어휘가 없다.</b><br>
<b>131회는 각 BC 가 갖는다 — 중복이 답이다.</b> 실물은 함수 서넛(≈30줄)이고, accounts 가 공개 계약을 바꾸면 13곳이 깨지는데 <b>깨지는 게 맞다</b>. 지금은 헬퍼 한 파일만 고치면 조용히 넘어간다 — 그리고 <b>그 파일이 <code>_acceptance_helpers.py</code> 다. 밑줄로 «사설»을 표시하는데 13개 BC 가 쓴다 — 이름이 거짓말을 하고 있다.</b><br>
<b>관문으로 우회할 수는 없다</b> — accounts 관문 여섯이 <b>전부 조회·구독</b>이다(<code>household_lookup</code>·<code>child_profile</code>·<code>child_access</code>·<code>family_membership</code>·<code>family_purchase_context</code>·<code>lifecycle_subscription</code>). <b>생성이 하나도 없어서</b> 타 BC 가 상태를 만들려면 그 BC 의 <b>공개 API 를 HTTP 로 두드리는 수밖에 없다</b>. 방식은 옳다 — 틀린 건 <b>그 두드리는 코드를 남의 <code>test/</code> 에서 꺼내 쓰는 것</b>이다.<br>
<b>규칙 둘, 그리고 ②가 ①보다 세다</b> — ① <code>framework/test/</code> 는 <b>HTTP 로만 시스템을 구동한다</b>(모델 import 금지 → 팩토리는 <b>정의상</b> 못 들어온다) ② <b>BC 하나를 지웠을 때 이 파일이 바뀌면 올리지 않는다</b>. <code>login_session</code> 은 <b>①을 통과하고 ②에 걸린다</b> — 그래서 ①만으로는 부족했다.<br>
<b>덤 — 문서가 한 번도 안 센 것.</b> 테스트가 타 BC 의 <b>«프로덕션»</b>을 <b>161건</b> import 한다. 관문(<code>open_host_service/</code>)이 <b>115 로 정당</b>하고 <b>46건이 관문을 우회</b>한다(Django 모델 41 · 도메인 타입 5 · <code>ParentModel</code>×12 <code>DeliveryRequestModel</code>×11 …). 표본 하나가 성격을 보여준다 — <code>usage_quota</code> 가 <code>bootstrap_family</code> 의 <b>반환값을 버리고</b> <code>ParentModel.objects.get(…).family_id</code> 로 다시 읽는데 <b>그 값이 이미 응답에 있다</b>. <b>4번 ⓑ 로 넘긴다.</b></dd>
<dt>⚠ 구현할 때 챙길 것 — <b>이 칸은 «만들고 끝»이 아니다</b></dt>
<dd><b>「이 재료의 뜻을 밖이 정하나」를 만들 때 물어야 한다.</b> 예면 <b>그 자리에서</b> <code>framework/test/</code> 에 만든다 — BC 가 하나뿐이어도 그렇다. <b>안 물으면 조용히 복사본이 는다</b> — 아래가 그 결과다.
<span class="dim">08-10 · C2 — 옛 문면은 <em>「두 번째 BC 가 또 만들 때 알아채고 올린다」</em> 였다. 아래 수치는 <b>「둘」의 근거였는데 이제 「미루면 무슨 일이 생기나」의 보기</b>다.</span>
<div class="pre-wrap"><pre><code>jpatch()  7개   parental_controls 안에서만 4개 (08-07 재측정 · 옛 값 「4벌」은 한 파일 기준이었다)
                셋은 본문이 «글자 단위로» 같고, parental_controls 것만 str 분기가 빠져 있다
                                                        ← 복사해 가다 뒤처진 판</code></pre></div>
<b><code>jpatch</code> 는 처음부터 <code>framework/test/</code> 것이었다</b> — JSON Patch 의 뜻을 정하는 것은 RFC 6902 이지 <code>parental_controls</code> 가 아니다. 미루니 넷이 각자 조금씩 다른 판을 가졌다. <b>이건 트리가 대신 막아줄 수 없고 구현자가 챙겨야 한다.</b> 검사는 있다 — <em>「BC 테스트가 다른 BC 의 <code>test</code> 를 import 하면 위반」</em> 이 grep 한 줄이다.</dd>
<dt class="ans-dt">08-07 · R10 — <b>자식이 둘이 됐다. «능력» 칸을 연다</b></dt>
<dd class="ans-dd filled"><b>이 칸의 정의는 「BC 가 하나도 없어도 존재하는 바닥」인데, 자식은 <code>&lt;technology&gt;/</code> 하나였다.</b>
그 폴더의 판정이 <em>「그 라이브러리 타입 없이는 말이 안 되나」</em> 라서, <code>ClockPort.now() -&gt; datetime</code> 처럼 <b>django 없이도 말이 되는 계약</b>은 들어갈 자리가 없었다.
어댑터만 올릴 수도 없다 — 포트를 상속해야 하니 <b>«<code>framework/</code> → <code>application</code> 0건»이 첫 줄에서 깨진다</b>.
<b class="dim">※ 이 논거는 08-08 · T32(<b>D47</b>)가 폐기했다 — 클린 기준으로 «바깥이 안쪽을 아는 것»은 정상이라 그 «깨짐»은 결함이 아니다.
<b>결론(계약과 구현이 한 폴더)은 그대로 서고</b>, 근거가 «링»에서 «공용성»으로 바뀐다.</b><br>
<b><code>&lt;capability&gt;/</code> 를 형제로 세운다</b> — 안에 <b>계약과 구현이 함께</b> 산다(<code>clock/clock.py</code> + <code>clock/django_adapter.py</code>). 그러면 나가는 화살표가 없어 ④ 가 그대로 유지된다.<br>
<b>둘을 가르는 자는 접미사 하나다 — <code>_port</code> 면 계약, <code>_adapter</code> 면 구현.</b> <span class="dim">08-07 · 2차 리뷰 — 이 모양은 처음부터 이랬는데 <b>판정으로 안 적혀 있어서</b> 107행 검사(«<code>composition_root</code> 밖에서는 아무도 구현을 import 하지 않는다»)가 <b>대상을 못 고르는 「판정 불가」</b>로 남아 있었다. 같은 자가 <b>폴더 갈래도 정한다</b> — 폴더 안에 폴더 이름과 같은 파일이 있으면 <code>&lt;capability&gt;/</code>, 없으면 <code>&lt;technology&gt;/</code>. 그래서 <code>&lt;technology&gt;/</code> 안에는 폴더 이름과 같은 모듈을 두지 않는다.</span></dd>

<dt>원전과 참조 구현이 이 모양을 지지한다</dt>
<dd>Evans <b>COHESIVE MECHANISM</b> — <em>「Partition a conceptually cohesive mechanism into a <b>separate lightweight framework</b>. Expose the capabilities of the framework with an <b>INTENTION-REVEALING INTERFACE</b>. … 도메인은 «무엇»에 집중하고 «어떻게»는 프레임워크에 위임한다」</em>.
<div class="pre-wrap"><table class="mini">
<tr><th>참조 구현</th><th>계약</th><th>구현</th></tr>
<tr><td>Grzybek</td><td class="mono">BuildingBlocks/<b>Application</b>/Emails/IEmailSender</td><td class="mono">BuildingBlocks/<b>Infrastructure</b>/Emails/EmailSender</td></tr>
<tr><td>eShopOnContainers</td><td class="mono">BuildingBlocks/EventBus/<b>Abstractions</b>/</td><td class="mono">EventBus<b>RabbitMQ</b>/ · EventBus<b>ServiceBus</b>/</td></tr>
<tr><td>IDDD_Samples</td><td class="mono">iddd_common/domain/model/DomainEventPublisher</td><td class="mono">같은 패키지 <code>port/adapter/</code></td></tr>
</table></div>
<b>공용 패키지가 «계약 + 구현»을 함께 담는 실물이 있다 — 근거 표의 다수는 분리형이라 «표준»이 아니라 «전례»로 적는다.</b> <b>D17</b> 이 <code>adapter/</code> 후보로 든 셋(UnitOfWork · Clock · <b>메일</b>) 중 메일을 Grzybek 이 정확히 이렇게 처리했다.<br>
<b>반례도 하나 있다</b> — Grzybek 의 <code>SystemClock</code> 은 <code>Meetings/Domain/SharedKernel/</code> 과 <code>Payments/Domain/SeedWork/</code> 에 <b>각각 중복된 <code>static class</code></b> 다(테스트용 전역 <code>Set()</code>/<code>Reset()</code> 훅까지). <b>하지 말아야 할 예</b>로 적어 둔다.</dd>

<dt>서랍이 되지 않게 — <b>판정이 이분법이어야 한다</b></dt>
<dd>이 카드가 <code>common/</code> 을 기각한 이유가 <em>「«공통이냐»는 성질이 아니라 정도라 서랍이 된다」</em> 였다. 같은 병에 안 걸리려면 자가 <b>기계로 갈리는 이분법</b>이어야 한다.
<div class="pre-wrap"><pre><code>판정  계약의 «이름에도 시그니처에도» 어느 BC 의 업무 어휘가 한 글자도 안 나오나

  ClockPort.now() -&gt; datetime                    업무 어휘 0     → framework   ✅
  RandomDrawPort.draw(upper_exclusive) -&gt; int    업무 어휘 0     → framework   ✅
  ────────────────────────────────────────────────────────────────────────────
  OtpCodeGenerator            속은 secrets 뿐인데  «OTP»          → BC
  CurriculumCodebookSource…   속은 json+pathlib   «Curriculum»   → BC
  ResumeSlotGate                                  «Resume Slot»  → BC
  TurnExhaustExecutor                             «Turn» + 도메인 타입 셋
  Fcm/Sms/Alimtalk Gateway                        ChannelOutcome → BC
                                                  ─────────────────────────
                                                  16 중 2 만 통과</code></pre></div>
<b>문이 좁다는 것을 실측으로 확인했다.</b> «속에 든 기술»이 아니라 «계약이 무슨 업무를 말하나»가 가르기 때문이다 —
그래서 <code>SecureOtpCodeGenerator</code> 는 앞으로 <code>secrets</code> 를 직접 부르는 대신 <b><code>framework/random</code> 을 «쓰는»</b> BC 어댑터가 된다.</dd>

<dt>왜 지금 여는가 — <b>실측이 아니라 원리가 정했다</b></dt>
<dd>지금 이 자에 걸리는 계약은 <b>2개뿐</b>이고 둘 다 <code>managed_copy</code> 하나에 있다. 「두 번째 BC 가 생기면 그때」로 미룰 뻔했는데, <b>그건 실측을 근거로 쓴 것</b>이라 규율 ① 과 어긋난다 — <em>「원리로 짓고 기존 구현은 다 만든 뒤 대조한다」</em>.<br>
그리고 <b>불일치가 이미 실재한다</b> — 「지금 몇 시인가」를 묻는 방식이 <code>timezone.now()</code> 39회(9 BC) · <code>datetime.now(…)</code> 4회 · <code>date.today()</code> 1회로 <b>세 갈래</b>다. 전역 지침의 예외 조항이 이 경우다 — <em>「불일치 위험이 큰 지식의 중복은 더 일찍 모아도 된다」</em>.</dd>

<dt>③ 화살표 · ④ 앎</dt>
<dd><b>③</b> <code>&lt;technology&gt;/</code> 는 <b>그 기술을 아는 층만</b> 부른다(실측 <code>domain_layer → ninja/</code> <b>0건</b>) · <code>test/</code> 는 <b>BC 의 test 만</b>.<br>
<b>④</b> 이 구역은 <b><code>application/</code> 을 모른다</b> — <b>실측 0건이고 그게 규칙이 된다</b>. 이 한 줄이 여기를 «바닥»으로 만든다.</dd>
<dt>인증이 갈렸다 — <b>실측이 둘로 잘랐다</b></dt>
<dd><em>「인증은 여러 BC 가 공통으로 쓰는 게 좋다」</em>가 방침이 됐고, 실측이 그 말을 둘로 갈랐다.
<div class="pre-wrap"><pre><code>읽는 것  ninja/authentication.py  38줄   request.auth 를 부모/자녀로 정규화   BC 0개  ← 이미 여기 있었다
푸는 것  ParentAuth 30줄 · ChildAuth 44줄  토큰 → DB 에서 사람 찾기          BC 1개

class ParentAuth(HttpBearer):  ... return build_parent_session_token_service().resolve(token)
class ChildAuth(HttpBearer):   ... return build_child_device_token_service().resolve(token)
                                          ← 본문 3줄, 다른 건 resolve 하나뿐이다</code></pre></div>
→ <b>틀을 여기로 올린다</b>(<code>BearerAuthentication(resolve)</code>) · <b>해석은 각 BC 가 <code>open_host_service/</code> 로 공개한다</b>. ④ 가 유지되고, 타 BC 는 <b>관문을 통해</b> 인증을 얻는다.<br>
<b>따라온 값</b> — 13개 BC 가 <code>accounts</code>·<code>pairing</code> 의 <code>authentication</code> 을 직접 부르던 <b>27건이 통째로 사라진다</b>. <b>D16</b> 의 「예외는 둘」을 깨던 세 번째가 없어지고, <b>BC 안에 인증 파일이 남지 않는다</b>.</dd>
<dt class="ans-dt">② 이름 — <b><code>common</code> 을 버리고 <code>framework</code> 으로</b></dt>
<dd class="ans-dd filled"><b><code>common</code> 이 걸린 이유는 판정 기준이 아니어서</b>다. 「공통이면 여기」로는 <b>오늘 걷어낸 둘이 전부 다시 통과</b>한다(<code>shared_kernel</code> 후보 · 한 BC 것) — 실제로 그렇게 들어와 있었다. <b>「공통이냐」는 성질이 아니라 정도</b>라서 서랍이 된다.<br>
판정이 되는 물음은 하나다 — <em>「Django/Ninja 없이 이 파일이 말이 되나?」</em>
<div class="pre-wrap"><pre><code>common/      판정 불가   「공통이냐」는 성질이 아니라 정도다 — 무엇이든 통과한다
support/     판정 불가   같은 병. 「공용이면 전부 support」라 울타리가 없다
shared/·util/ 판정 불가   같은 병
platform/    판정 가능   ← 08-05 에 골랐다가 08-06 에 취소(파이썬 표준 라이브러리 이름) — ③
foundation/  판정 가능   ← 08-06 에 잠깐 골랐다가 취소(내용이 «토대»가 아니다) — ③
framework/   판정 가능   「Django/Ninja 없이 이 파일이 말이 되나?」 = ②의 판정 질문 그대로
                         남는 다섯이 전부 첫 줄에 프레임워크 타입을 갖는다
                         클린의 가장 바깥 링 이름 그대로 — Frameworks &amp; Drivers</code></pre></div>
<b>정직한 값</b> — 이 트리는 표준어를 그대로 써왔는데(<code>open_host_service</code> · <code>anticorruption_layer</code> · <code>composition_root</code>) <b>여기만 관례어</b>다. 클린 계보를 우선하면 <code>framework/</code> 였지만, <b>바깥·안쪽이 같은 말을 하는 값</b>이 더 컸다.<br>
<b>§0-4(도메인 축 1차)와도 충돌하지 않는다</b> — 여기엔 도메인이 <b>아예 없어</b> 1차로 놓을 게 기술밖에 없다. 예외가 아니라 <b>적용 대상이 아닌 것</b>이고, <b>D22</b> 가 <code>scripts/</code> 를 「트리 밖이라 P4 와 다르다」고 한 것과 같은 논리다.<br>
<b>안쪽 뼈대 칸은 이름을 따로 두지 않았다</b> — <code>support/</code> 는 뭐가 와도 통과해 <code>enum/</code> 과 같은 함정이고, <code>acceptance/</code> 는 <code>unit/</code>·<code>integration/</code> 옆에서 <b>테스트 «종류»로 읽힌다</b>. 파일이 둘셋뿐이라 <b>칸 바로 밑 파일</b>로 둔다(선례 <code>driven_layer/unit_of_work.py</code>).</dd>
<dt class="ans-dt">③ <b>08-06 재결정 — <code>platform</code> 은 애초에 쓸 수 없는 이름이었다</b></dt>
<dd class="ans-dd filled"><b>적대적 리뷰가 잡았다.</b> <code>platform</code> 은 <b>파이썬 표준 라이브러리 모듈 이름</b>이고,
저장소 루트는 <code>manage.py</code>(<code>sys.path[0]</code>)와 gunicorn 양쪽에서 <code>sys.path</code> 에 들어간다.
루트에 <code>platform/</code> 패키지를 두면 <b>표준 라이브러리 <code>platform</code> 이 가려진다</b>.<br>
<b>실측 — 이 저장소가 실제로 쓰는 체인이 둘이다.</b>
<div class="pre-wrap"><pre><code>firebase_admin/_utils.py:18      from platform import python_version
    ← delivery/composition_root.py:34 → firebase_fcm_push_gateway.py:9
gunicorn/workers/workertmp.py:7  import platform          ← 워커 로딩 자체

$ python manage.py check
ImportError: cannot import name 'python_version' from 'platform'
(consider renaming '.../platform/__init__.py' since it has the same name
 as the standard library module named 'platform')</code></pre></div>
<b>첫 배포에서 서비스가 뜨지 않는다.</b> 08-05 의 ②는 <code>common</code>·<code>framework</code>·<code>platform</code> 셋을
<b>«판정 가능성»으로만</b> 견줬고 <b>이름이 이미 임자가 있는지</b>는 축으로 세우지 않았다.<br>
<b>먼저 <code>foundation/</code> 으로 갔다가 그것도 취소했다.</b> 방향은 살았지만 <b>내용이 «토대»가 아니다</b> —
이 폴더를 지워도 무너지는 것이 없고, 각 BC 가 작은 파일 다섯을 각자 쓸 뿐이다.
「여러 BC 가 갖다 쓰는 것」이 정확한 성격이다.<br>
<b>그렇다고 <code>util/</code>·<code>support/</code>·<code>shared/</code> 로 갈 수는 없다</b> — ②가 <code>common</code> 을 버린 이유가 그대로 걸린다.
<b>이 저장소는 그 대가를 실제로 치렀다</b>: <code>common/</code> 이라는 이름이 업무 파일 둘을 빨아들였다
(<code>enum/child_report_topic.py</code> · <code>broccoli/notification_navigation.py</code>).<br>
<b>고른 것 — <code>framework/</code></b>. ②가 세운 판정 질문 <em>「Django/Ninja 없이 이 파일이 말이 되나?」</em>가
<b>그대로 폴더 이름이 된다</b>. 남는 다섯이 전부 첫 줄에 프레임워크 타입을 갖는다 —
<code>from ninja import Schema</code> · <code>from django.db import OperationalError</code> ·
<code>from django.http import HttpRequest</code>.
<code>sys.stdlib_module_names</code> 대조 <b>충돌 0</b> · 설치 패키지 대조 <b>충돌 0</b>.<br>
<b>②가 <code>framework/</code> 를 물리쳤던 이유 둘은 다시 재니 서지 않았다.</b>
⒜ 「안쪽 <code>&lt;technology&gt;/</code> 와 같은 말을 한다」 — 이 트리는 그 반복을 이미 좋다고 한다
(<code>&lt;aggregate&gt;/&lt;aggregate&gt;.py</code> · <code>&lt;aggregate&gt;_repository.py</code> · <code>django_&lt;bounded_context&gt;/</code>).
여기서는 <b>정보를 담은 반복</b>이다 — <code>framework/</code> 가 성격을, <code>django/</code> 가 어느 것인지를 말한다.
⒝ 「<code>framework/test/</code> 가 «프레임워크의 테스트»로 읽힌다」 — <b>실측하면 그게 맞는 읽기다</b>.
지금 거기 있는 테스트 셋이 전부 그 다섯 모듈의 테스트이고, 공유 뼈대의 규칙도
「HTTP 로만 구동한다」= ninja·django 테스트 클라이언트다.<br>
<b>치르는 값</b> — 클린의 «Frameworks &amp; Drivers»가 <b>두 자리를 가리키게 된다</b>(여기와 <code>driven_layer/django_&lt;bounded_context&gt;/</code>).
같은 링의 <b>BC 밖 / BC 안</b>이라 어긋나지는 않는다.<br>
<b>규칙이 하나 늘었다</b> — <em>「저장소 루트의 패키지 이름은 파이썬 표준 라이브러리 모듈명과 겹치지 않는다」</em>.
<code>sys.stdlib_module_names</code> 와 대조하는 <b>한 줄 검사</b>다. 같은 함정이
<code>test/</code> · <code>types/</code> · <code>json/</code> · <code>enum/</code> · <code>code/</code> 에도 있고,
이 트리는 <code>test/</code> 를 <b>항상 무언가의 자식</b>으로만 두어 우연히 피해 있었다.</dd>
<dt>세 관점</dt>
<dd><b>클린</b> — 여기 있는 게 <b>프레임워크 세부</b>라 가장 바깥 링이고, 그래서 안쪽이 부르면 안 된다. <b>DDD</b> — Shared Kernel 을 <b>만들지 않은 것</b>이 DDD 적 결론이다(관문·계약이 이미 일하고 있었다). <b>헥사고날</b> — 인증 틀은 <b>주도 어댑터의 부속</b>이라 육각형 밖이다.</dd>
</dl>

## D56 · 페이크가 살 칸 — 트리가 「꽂는다」 적어 놓고 자리를 안 줬다

**확정 · 08-09 · T47** · 자리 — <code>test/fake/&lt;declaration&gt;.py</code> &nbsp;·&nbsp; <b>신설 2행 · 새 규칙 0</b> &nbsp;·&nbsp; <code>test/</code> 자식 넷 → <b>다섯 · 갈래 둘</b>

<dl class="kv">
<dt class="ans-dt">물음 — <b>포트의 가짜 구현이 어디 사나</b></dt>
<dd class="ans-dd filled"><b>트리가 스스로 적어 놓고 자리를 안 줬다.</b>
<div class="pre-wrap"><pre><code>test/unit/  «무엇이 오나»
   「도메인과 응용의 테스트. DB 를 켜지 않는다.
     <b>포트 자리에는 페이크 구현을 꽂고</b>, 애그리거트의 불변식과 유스케이스의 절차만 본다.」

test/
  unit/ integration/ e2e/     ← 테스트다
  factories/                  ← <b>ORM 을 만지는 것이 정의</b>라 unit 이 못 쓴다
                              ← <b>페이크가 갈 칸이 없다</b></code></pre></div>
<b><b>D54</b> ④(폐쇄) 이후로 심각도가 달라졌다</b> —
전에는 「자리가 애매하다」였는데, 지금은 <b>「트리에 없는 모양은 만들 수 없다」가 골격 검사 1순위로 돌고 걸리면 반환</b>이다.
<b>만들면 위반이고, 안 만들면 <code>unit/</code> 이 「DB 를 켜지 않는다」를 지킬 방법이 없다</b> — 트리가 자기 규칙으로 자기를 막고 있었다.</dd>

<dt class="ans-dt">답 — <b><code>test/</code> 자식은 다섯이고 «둘»로 갈린다</b></dt>
<dd class="ans-dd filled"><div class="pre-wrap"><pre><code>test/
  unit/  integration/  e2e/     ← <b>«테스트»</b>  안이 자유 — pytest 가 파일 이름을 소유한다
  factories/  fake/             ← <b>«재료»</b>    이름·상속 규칙이 걸린다</code></pre></div>
<b><code>factories/</code> 가 이미 «테스트가 아닌 것»이었다</b> — 픽스처는 테스트가 아니라 테스트가 쓰는 재료다.
그리고 그것이 <code>integration/</code> 안이 아니라 <b>형제로 올라온 이유</b>를 트리가 적어 놨다:
<em>「안에 숨겨 두면 <code>unit/</code> 이 무심코 가져다 쓰고 <b>«unit 은 DB 를 안 켠다»가 조용히 깨진다</b>」</em>.
<br><b>그 자가 페이크에 «반대 방향»으로 그대로 걸린다</b> — <code>unit/</code> 안에 숨기면 <code>integration/</code>·<code>e2e/</code> 가 가져다 써서
<b>「진짜 DB 를 켠다」가 조용히 깨진다</b>. <b>새 근거를 만들지 않았다.</b></dd>

<dt class="ans-dt"><code>fake/</code> 는 <b>D37</b> 짝의 <b>«세 번째»</b>다 — 새 규칙 0</dt>
<dd class="ans-dd filled"><div class="pre-wrap"><pre><code>port/&lt;capability&gt;/&lt;capability&gt;_port.py                    선언
  driven_layer/adapter/…/&lt;capability&gt;_adapter.py            구현 ①  프로덕션
  test/fake/&lt;capability&gt;_port.py                            구현 ②  테스트   ← 신설</code></pre></div>
<code>adapter/</code> 의 문장을 <b>그대로 두 번째로 건다</b> — <em>「어떤 «선언»의 구현이고 · 파일 이름이 그 선언과 같고 · 그 선언 클래스를 «상속»한다」</em>.
그래서 4차 리뷰 SC-I 의 <em>「D44 의 의도는 «가짜도 상속한다»인데 그 규칙이 어디에도 없다」</em> 가 <b>문장 하나 안 쓰고 닫힌다</b>.
<div class="pre-wrap"><table class="mini">
<tr><th>거는 것</th><th>안 거는 것</th></tr>
<tr><td><b>여기 있는 파일은 반드시 «선언»이 있어야 한다</b> — 한 방향</td>
<td><b>1:1 짝맞춤</b> — 걸면 <b>모든 포트에 페이크가 강제</b>된다. <code>&lt;…&gt;</code> 가 처음 나오는 낱말이라 <b>필요할 때</b> 생긴다</td></tr></table></div>
<b>SC-I 의 지적 하나는 «틀렸다»</b> — <em>「강제 수단이 mypy 뿐이다 — <code>ABC</code> 는 런타임에 덕타이핑을 못 막는다」</em>.
<b>실행해서 확인했다</b>: 상속만 하면 미구현은 <b>인스턴스화에서 <code>TypeError</code></b> 로 터진다.
<div class="pre-wrap"><pre><code>Fake(P) 가 save 를 구현 안 하면  →  TypeError: Can't instantiate abstract class Fake
상속을 «안» 하면 isinstance     →  False</code></pre></div>
<b>그러니 강제할 것은 「상속했나」 하나뿐이고, 그건 <code>adapter/</code> 가 쓰는 «경로가 선언을 유도한다»로 선다.</b></dd>

<dt>기각 — <b>프로덕션 <code>adapter/</code> 아래에 두기</b> <span class="dim">원전이 지지하는 안이라 근거를 남긴다</span></dt>
<dd><b>Cockburn 의 Blue Zone 도해는 Test Double 을 «어댑터의 하나»로 그린다</b> — 같은 포트에 <em>File adapter</em> 와 <em>Test Double</em> 이 나란히 붙고,
<em>“Given a port, there may be an adapter for each desired technology that we want to use.”</em> 라 적는다.
<br><b>그래도 안 둔다.</b> 우리 <code>adapter/</code> 는 <b>「내가 무엇을 구동하나」로 네 갈래</b>인데 <b>페이크는 아무것도 구동하지 않고</b>,
<code>driven_layer/</code> 는 「나가는 화살표는 안쪽뿐」인데 <b>페이크는 나가는 것이 0</b>이다. 무엇보다 <b>프로덕션 배포에 테스트 코드가 실린다</b>.
<br><b>가르는 자는 「테스트에서만 쓰나」 하나다</b> — 인메모리 구현을 <b>로컬 개발·기능 플래그로 프로덕션에서도</b> 켠다면 그건 페이크가 아니라
<b>진짜 어댑터</b>라 <code>adapter/&lt;capability&gt;/</code> 에 산다.</dd>

<dt>이름 — <b><code>fake/</code></b> <span class="dim">기각 둘</span></dt>
<dd><div class="pre-wrap"><table class="mini">
<tr><td><b><code>fake/</code></b></td><td><b>채택</b> — Fowler 축자 <em>“Fake objects actually have <b>working implementations</b>”</em>. 여기 오는 것이 정확히 그것이다</td></tr>
<tr><td><code>double/</code></td><td><b>기각</b> — Meszaros 의 <em>Test Double</em> 은 <b>상위어</b>라 Dummy·Stub·Spy·Mock 이 다 들어와 <b>서랍이 된다</b></td></tr>
<tr><td><code>in_memory/</code></td><td><b>기각</b> — <b>구현 수단</b>이라 고정 시계·빈 발송기를 안 덮는다. 그건 <b>클래스 이름</b>이 진다(<code>InMemoryOrderRepository</code>·<code>FixedClock</code>)</td></tr></table></div>
<span class="dim">Cockburn 은 <em>mock</em> 이라 쓰지만(<em>“The natural test adapter to substitute for a secondary actor such as a database is a <b>mock</b>”</em>) Meszaros 분류에서 <b>mock 은 다른 물건</b>이다 — 우리가 두는 것은 <em>Fake</em> 다.</span></dd>

<dt class="ans-dt">딸려 나온 것 — <b><code>test/</code> 아래 «리프가 0개»였다</b></dt>
<dd class="ans-dd filled"><code>unit/</code>·<code>integration/</code>·<code>e2e/</code>·<code>factories/</code> 넷 모두 <b>파일 행이 하나도 없었다</b>
(<code>framework/test/</code> 에는 <code>&lt;module&gt;.py</code> 가 있는데 BC 쪽에는 없다).
<b><b>D54</b> ④ 를 그대로 적용하면 <code>test/unit/test_order.py</code> 도 매칭이 안 되어 위반</b>이 된다 —
<b>제1원칙을 닫으면서 테스트 코드 전체가 골격 검사에 걸리게 된 것을 아무도 안 봤다</b>.
<br><b>답 — 테스트 셋은 「안이 자유」로 명시한다.</b> <code>admin/</code> 이 이미 <em>「자리와 이름은 정하고 <b>리프 규칙만 면제</b>한다」</em> 로 그 선례이고,
여기는 <b>pytest 가 파일 이름으로 «수집»</b>하므로 <b>기계가 이미 이름을 소유</b>한다 — <code>migrations/</code>·<code>apps.py</code> 와 같은 갈래다.
<br><b>면제는 셋에만 걸린다</b> — <code>factories/</code>·<code>fake/</code> 는 «재료»라 규칙이 그대로 산다.</dd>

<dt>공유 페이크 — <b><code>framework/test/</code></b></dt>
<dd><b>D38</b> 의 자(<b>「뜻을 밖이 정하나」</b>)가 그대로 돈다 — <b>개수는 안 묻는다</b>.
<code>framework/&lt;capability&gt;/</code> 포트의 페이크는 <b>처음부터</b> <code>framework/test/fake/</code> 다 — BC 가 하나뿐일 때도 그렇다.
<span class="dim">08-10 · C2 — 그 <code>fake/</code> 칸을 이번에 열었다. 그전에는 「처음부터 여기」라 적어 놓고 <b>칸이 없어</b> 진짜 계약과 같은 평면에 살았다.</span>
<span class="dim">옛 문면은 <em>「여러 BC 가 갖다 쓰는 뼈대 — HTTP 로만 시스템을 구동한다」</em> 라 <b>뼈대만 말하고 페이크를 안 덮었다</b>. 한 줄 넓혔다.</span></dd>
</dl>

## D57 · 한 포트에 어댑터 여럿 — 「1:1」이 «양방향»으로 읽히고 있었다

**확정 · 08-09 · T48** · 자리 — <code>&lt;technology&gt;_adapter.py</code> 개명 &nbsp;·&nbsp; <code>framework/&lt;capability&gt;/&lt;data&gt;_out|_in.py</code> &nbsp;·&nbsp; <code>framework/broker/&lt;technology&gt;_broker.py</code> &nbsp;·&nbsp; <b>신설 3행 · 개명 1 · 새 규칙 0</b>

<dl class="kv">
<dt class="ans-dt">물음 — <b>한 포트에 어댑터가 «동시에» 여럿일 수 있나</b></dt>
<dd class="ans-dd filled"><b>있다. 그리고 트리는 그걸 «한 자리»에서만 막고 있었다.</b>
<div class="pre-wrap"><pre><code>external_system/toss/payment_adapter.py         폴더=벤더    파일=능력    ✔ stripe/ 와 공존
anticorruption_layer/billing/settle_adapter.py  폴더=상대BC  파일=능력    ✔
persistence/repository/order_repository.py      폴더=종류    파일=애그리거트 ✔
adapter/&lt;capability&gt;/&lt;capability&gt;_adapter.py    폴더=능력    파일=«능력»   ✗ 되풀이라 둘째가 못 온다</code></pre></div>
4차 리뷰 HEX-3 은 <em>「구조적으로는 안 막힌다 — 문면이 반대로 읽히게 써 놨을 뿐」</em> 으로 봤는데,
<b>전수로 재니 한 자리는 실제로 막혀 있었고 그 자리가 리뷰가 지목한 곳이 아니었다</b>.
<br><b>같은 칸 안에서 이름 규칙 둘이 어긋나 있었다</b> — 파일 이름은 <code>&lt;capability&gt;_adapter.py</code> 로 <b>하나로 닫히는데</b>
클래스 이름은 <code>&lt;기술&gt;&lt;Capability&gt;Adapter</code> 로 <b>여럿을 전제</b>한다. <b>클래스는 이미 갈리는데 파일만 안 갈렸다.</b></dd>

<dt class="ans-dt">결정 ① — <b><code>adapter/&lt;capability&gt;/&lt;technology&gt;_adapter.py</code></b></dt>
<dd class="ans-dd filled"><b>가르는 자는 「폴더가 말하지 «않는» 축을 파일이 말한다」</b>이고, 형제 셋에 이미 성립하고 있었다.
<b>여기만 폴더가 «능력»이라 파일이 «기술»을 져야 한다.</b>
<br><b>형제 칸이 이미 답을 갖고 있었다</b> — <code>framework/&lt;capability&gt;/<b>&lt;technology&gt;</b>_adapter.py</code>
(<em>「기술 + <code>_adapter</code> — 능력은 폴더가 이미 말했다」</em>). <b>같은 물건이 승격한 자린데 이름 규칙이 서로 달랐다.</b>
<span class="dim">「그럼 <code>&lt;use_case&gt;/&lt;use_case&gt;_use_case.py</code> 의 되풀이는?」 — 거기는 <b>그 폴더에 하나뿐</b>이라 되풀이 말고 쓸 게 없고 근거도 「편집기 탭이 전부 같은 이름이 된다」이다.
여기는 <b>여럿이 될 수 있는데 되풀이가 그걸 막고</b> 있었고, <code>&lt;technology&gt;</code> 가 탭 문제를 이미 해결한다(<code>bcrypt_adapter.py</code>·<code>argon2_adapter.py</code>).</span></dd>

<dt class="ans-dt">결정 ② — <b>「1:1」을 «방향»으로 다시 쓴다</b></dt>
<dd class="ans-dd filled"><code>adapter/</code> 총론이 <em>「… 파일 이름이 그 선언과 같다 — <b>1:1 이 폴더 하나로 걸린다</b>」</em> 라 적어
<b>앞 절은 단방향인데 뒤 절이 양방향으로 읽혔다</b>.
<div class="pre-wrap"><table class="mini">
<tr><th>방향</th><th>어디에</th></tr>
<tr><td><b>한 방향</b> — 「파일 하나 = 선언 하나」</td><td><b>기본값</b>. <code>adapter/</code> 아래 전부 · <code>test/fake/</code>(T47 에 이미 적었다)</td></tr>
<tr><td><b>양방향</b> — 「선언 하나 = 파일 하나」</td><td><b>셋뿐</b> — <code>repository/</code>·<code>unit_of_work/</code>·<code>domain_bypass_query/</code>.
<b>그 셋이 «하나여야 하는» 것들이라서</b>다(애그리거트당 하나 · 경계당 하나 · 조회당 하나)</td></tr></table></div>
<b>원전이 그림으로 답한다</b> — <em>“Given a port, there may be an adapter for <b>each desired technology</b> that we want to use.”</em>
Blue Zone 도해는 <code>For obtaining rates</code> 포트에 <b>Test Double 과 File adapter 를 동시에</b> 건다.
<b>우리 트리에서 그 셋이 이미 선다</b> — 벤더 둘 · 기술 이행 중 · <b>진짜와 가짜</b>(<code>adapter/</code> ↔ <code>test/fake/</code>, T47 로 어제 갈라졌다).</dd>

<dt class="ans-dt">결정 ③ — <b><code>framework/&lt;capability&gt;/</code> 에 자료 둘</b> · <b><code>broker/</code> 에 구현 하나</b></dt>
<dd class="ans-dd filled"><b>승격하면 자료가 갈 곳을 잃고 있었다.</b>
<div class="pre-wrap"><pre><code>BC        port/&lt;capability&gt;/     _port.py · exception.py · &lt;data&gt;_out.py · &lt;data&gt;_in.py
          adapter/&lt;capability&gt;/  &lt;technology&gt;_adapter.py

framework &lt;capability&gt;/         _port.py · exception.py · <b>&lt;data&gt;_out.py · &lt;data&gt;_in.py</b>  ← 신설
                                 &lt;technology&gt;_adapter.py
          broker/                broker_port.py · <b>&lt;technology&gt;_broker.py</b>              ← 신설</code></pre></div>
<b>파일 이름이 여섯 다 같아진다</b> — 다른 것은 <b>「폴더가 몇 겹이냐」</b>뿐이고 그게 곧 <b>「층이 있느냐」</b>다.
BC 는 <code>port/</code>(응용층)와 <code>adapter/</code>(드리븐층)가 <b>의존 방향</b>을 가르는데 <b><code>framework/</code> 엔 도메인이 없어 그 축 자체가 없다</b>.
가르는 일은 <b>접미사(<code>_port</code> ↔ <code>_adapter</code>)</b>가 한다.
<br><b><code>broker/</code> 는 계약만 있고 구현 칸이 «0» 이었다</b> — <code>broker_port.py</code> 에
<em>「구독 등록은 메모리에만」</em> 이라는 <b>구현 제약</b>을 적어 놓고 그 구현이 살 자리를 안 줬다.
<b>D54</b> ④(폐쇄) 아래에서는 <b>만들면 위반</b>이다.
<b>접미는 <span class='no'>_adapter</span> 가 아니라 <code>_broker</code></b> — 인프로세스 브로커는 <b>번역할 «바깥 상대»가 없고</b>,
<code>*_adapter.py</code> 를 대상으로 도는 검사 넷이 여기 걸리면 안 된다.</dd>

<dt>기각 — <b><code>framework/</code> 에 <code>port/</code>·<code>adapter/</code> 겹을 만들기</b></dt>
<dd><b>사용자 제안으로 한 번 채택했다가 되돌렸다.</b> BC 와 모양을 끝까지 맞추자는 안인데,
<b>BC 의 <code>adapter/</code> 네 갈래 중 둘이 구조적으로 «불가능»하다</b> — <code>persistence/</code> 는 <code>framework/</code> 에 ORM 모델이 없어서,
<code>anticorruption_layer/</code> 는 BC 를 몰라서. <b>부분집합이 되고, 그게 「없는 축을 억지로 만든 것」의 증상이다.</b>
<br><b>BC 의 층은 «의존 방향»을 강제하려고 있다</b> — 도메인이 밖을 모르게. <code>framework/</code> 엔 도메인이 없어 그 축이 없다.
<span class="dim">그리고 「계약이냐 구현이냐」는 접미사가 이미 가른다 — 트리가 그렇게 적어 놨다: <em>「같은 폴더에 구현이 나란히 살아서 <b>둘을 가르는 것이 접미사뿐</b>이다」</em>.</span></dd>

<dt>기각 — <b><code>framework/</code> 에 «구현만» 두기</b></dt>
<dd><b>「framework 엔 실제 구현이 있는 것만 온다」는 맞다 — 다만 그 구현이 «혼자» 오지 못한다.</b>
계약을 BC 에 남기면 구현이 상속할 대상에 <b>닿지 못한다</b>:
<div class="pre-wrap"><pre><code># framework/clock/django_clock.py
from application.bc_a.…port.clock.clock_port import ClockPort   ← 「framework → application import 0」 위반
class DjangoClock(ClockPort): ...                               ← BC 가 둘이면 «어느 쪽»을 상속하나</code></pre></div>
<b>계약을 같이 올리면 그 문제가 통째로 사라진다</b> — 계약과 구현이 <b>같은 폴더 안에서</b> 상속 관계를 맺고 나가는 import 가 0으로 유지된다.
<br><b>그리고 <code>framework/</code> 에는 이미 «구현만 있는» 갈래가 둘 있다</b> — <code>&lt;technology&gt;/</code>·<code>pure/</code>.
<b>가르는 자는 「이걸 갈아 껴야 하나」 하나</b>이고, 그 자는 트리의 갈래 판정에 <b>이미 들어 있다</b>(<em>「폴더에 <code>*_port.py</code> 가 있으면 «능력»」</em>).
<span class="dim">우회안 — framework 구현을 BC 마다 얇은 어댑터로 감싸기. <b>D38</b> 이 없애려던 중복이 <b>계약 N개 + 위임 파일 N개</b>로 되살아난다.</span></dd>
</dl>

## D58 · 타입은 «어떤 상황에서도» 적는다 — 추론은 기계의 사정이고, 규칙이 아끼는 것은 사람의 노동이다

**확정 · 08-10 · T49** · 자리 — <b>전역 제약 옆에 «전제» 신설</b> &nbsp;·&nbsp; 트리 행 인용 정정 1곳 &nbsp;·&nbsp; <b>트리 신설 0 · 리맵 0</b> &nbsp;·&nbsp; 6번 이관 넷

<dl class="kv">
<dt class="ans-dt">물음 — <b>「어노테이션 필수」를 전역 제약으로 올릴까</b>(4차 리뷰 CHK-16)</dt>
<dd class="ans-dd filled"><b>앞부분은 사실이다.</b> 트리 <b>140행 중 아홉 행</b>의 검사가 «타입을 아는 것»에 기대고 있다.
<div class="pre-wrap"><pre><code>published_event/&lt;event&gt;.py                        도메인 타입 0
&lt;use_case&gt;_use_case.py                             무엇이 «애그리거트 리포지토리»인가 · 도메인 객체는 만들고 읽기만
&lt;use_case&gt;_result.py                               애그리거트가 오면 위반
port/&lt;capability&gt;/&lt;data&gt;_in.py                     애그리거트가 오면 위반
port/domain_bypass_query/…/&lt;data&gt;_out.py           애그리거트가 오면 위반
framework/&lt;capability&gt;/&lt;data&gt;_out.py · _in.py      애그리거트 · 업무 어휘 0
framework/&lt;capability&gt;/&lt;technology&gt;_adapter.py     도메인 타입이 한 글자도
anticorruption_layer/…/&lt;capability&gt;_adapter.py     상대의 «기저 예외»를 반드시 잡는다</code></pre></div>
<b>그런데 «승격»은 이미 두 자리에서 기각돼 있었다</b> — 전역 제약 aside 3문단(<em>「여기 «타입을 적어라»가 없는 것은 빠뜨린 것이 아니다」</em>)과
<b>D50</b>(<em>08-09 에 사용자가 「플러그인이 이미 강제할 것」이라 짚어 <b>전역 제약 ④ 신설을 같은 날 철회</b>했다</em>).
<b>「T 표에 올리기 전에 다른 카드·플러그인이 이미 답했는지부터」에 걸리는 다섯 번째</b>다.</dd>

<dt class="ans-dt">★ 조사하다 나온 것 — <b>인용한 강제자가 틀렸다</b></dt>
<dd class="ans-dd filled">트리 행이 <em>「그 전제는 플러그인이 이미 강제한다(시그니처 어노테이션 필수 · <code>check-public-surface-annotation</code>)」</em> 라 적는데,
<b>그 검사기는 시그니처를 «안 본다»</b>.
<div class="pre-wrap"><pre><code>if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
    bound.add(stmt.name)
    continue          # 함수 본문 = 지역 변수, 검사 안 함</code></pre></div>
잡는 것은 <code>MAX_RETRY = 3</code> 같은 <b>모듈·클래스 «직계»의 리터럴 대입</b>뿐이다.
<b>D50</b> 이 필요로 한 <code>def __init__(self, order_repository: OrderRepository)</code> 는 <b>세 겹으로 면제</b>된다 —
함수 본문 스킵 · <code>self.x</code> 는 Attribute 타깃 · RHS 가 이름 참조.
<b>인용된 검사기가 트리가 필요로 하는 전제를 «구조적으로» 못 준다.</b>
<br>시그니처를 실제로 강제하는 것은 <b>mypy strict</b> 이고, houserules §4 는 그것을
<em>「타입 검사가 <b>구성돼 있으면</b>」 · 「구성돼 있지 않아도 … <b>감수자가 점검</b>」</em> 으로 걸어 두었다 — <b>결정적 백스톱이 없다.</b></dd>

<dt class="ans-dt">★ 실증 — <b>타입이 없으면 «계약 대조 자체»가 안 선다</b></dt>
<dd class="ans-dd filled">포트를 상속한 페이크를 두고 mypy strict 를 돌렸다.
<div class="pre-wrap"><pre><code>class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -&gt; None: ...

def save(self, order: int) -&gt; None:   # 타입 O · 계약과 «다른» 타입
  → error: Argument 1 of "save" is incompatible with supertype "OrderRepository"
           note: This violates the Liskov substitution principle

def save(self, order):                # 타입 X · «같은» 위반
  → Success: no issues found</code></pre></div>
<b>같은 잘못인데 타입만 빼면 조용히 지나간다.</b> 페이크가 계약과 어긋난 채 <b>테스트는 초록</b>이고 프로덕션에서 깨진다.
§4 의 <code>tests.*</code> 면제가 <b>D56</b> 이 방금 연 <code>test/fake/</code> 에 그대로 걸린다.</dd>

<dt class="ans-dt">★★★ 사용자 결정 — <b>「타입은 무조건 어떤 상황에서도 적는다」</b></dt>
<dd class="ans-dd filled">나는 <b>지역 변수는 「권장」으로 두자</b>고 선을 그었다 — <em>「이미 추론되고, 트리 검사 아홉 중 지역 변수에 기대는 건 0개다」</em>.
<b>사용자가 뒤집었다</b>: <em>「추론이 가능하지만 <b>추론하는 데는 내 노력이 들어가</b>. 적어면 개발자가 더 편할 거 같아」</em>.
<br><b>축이 다르다 — 나는 «기계가 셀 수 있나»를 셌고 사용자는 «사람이 읽는 노동»을 셌다.</b>
houserules §4.1 의 반대 논거(<em>「추론 자명한 곳까지 강제하면 노이즈만 늘고 타입 안전은 거의 안 오른다」</em>)도 <b>기계 쪽 셈</b>이라 같은 자리에서 갈린다.
<code>order = repo.get(id)</code> 는 <code>get</code> 의 시그니처까지 가 봐야 <code>order</code> 가 무엇인지 알 수 있다.</dd>

<dt class="ans-dt">규칙 — <b>예외 0 · 「못 쓰는 곳」만 빠진다</b></dt>
<dd class="ans-dd filled"><b>모든 이름은 «첫 대입»에 타입을 단다.</b> 시그니처(인자·반환) · 모듈 변수 · 클래스 변수 · <b>함수 지역 변수</b>.
<div class="pre-wrap"><pre><code>✔ 건다      n: int = 3 · order: Order = repo.get(id) · router: Router = Router() · items: list[str] = []
⛔ 문법 없음  for x in xs: · with … as f: · except … as e: · a, b = pair · a = b = 0 · x += 1 · walrus · 컴프리헨션
⛔ 첫 바인딩 아님  재대입</code></pre></div>
<b>「자명하니까 면제」를 안 둔다</b> — 「자명하냐」를 기계가 가르기 시작하면
<b>D54</b> 가 없앤 <b>«조건부»가 돌아온다</b>.
검사기의 <b>리터럴 RHS 필터를 걷으면</b> 규칙이 한 줄로 정리된다.</dd>

<dt class="ans-dt">집행이 지금 <b>«0»</b>이다</dt>
<dd class="ans-dd filled">지역 변수를 잡는 도구가 <b>아무 데도 없다</b>.
<div class="pre-wrap"><pre><code>mypy --strict --disallow-any-expr loc.py   →  Success: no issues found
     ( order = get() · n = 3 이 둘 다 통과 — 지역 변수 어노테이션 옵션이 «존재하지 않는다» )
ruff ANN001-ANN401                         →  함수 인자·반환 전용
check-public-surface-annotation.py         →  함수 본문을 안 본다</code></pre></div>
<b>다만 기존 검사기의 «함수 본문 스킵»과 «리터럴 RHS 필터» 두 줄만 걷으면 면제 판정이 그대로 재사용된다</b> —
문법 없는 자리·재대입·선언적 클래스 면제가 이미 다 들어 있다. <b>6번 이관 넷</b> — 검사기 확장·개명 · §4 개정(지역 변수 필수) ·
<code>tests.*</code> 면제 삭제 · <b>mypy strict 구성 자체를 게이트로</b>(「구성돼 있으면」 조건 삭제).</dd>

<dt>번호를 «④»로 안 준 까닭</dt>
<dd>①②③ 은 어기면 <b>«설계»가 틀린 것</b>이고, 이건 어기면 <b>검사가 아예 안 돈다</b>.
④ 로 묶으면 같은 급으로 읽혀 「내 설계는 맞으니까」로 빠져나갈 여지가 생기는데,
<b>«전제»는 빠져나갈 데가 없다 — 없으면 그냥 안 돈다.</b></dd>

<dt>주류와 갈린다 — 숨기지 않는다</dt>
<dd>PEP 8 · mypy · Google 이 <b>「추론 가능한 지역 변수엔 비권장」</b>이다.
§4.1 이 이미 <em>「주류와 다른 선택임을 숨기지 않는다(출처 정직성)」</em> 라는 입장을 적어 놨으므로,
<b>범위만 «공개 표면»에서 «전부»로 넓히면</b> 문서 안에서 모순이 나지 않는다.
<span class="dim">§4.1 의 실익 문장(<em>「생성 결정성과 계약 가독성」</em>)도 그대로 산다 — 이번 결정은 그 «가독성» 쪽을 지역 변수까지 민 것이다.</span></dd>
</dl>

## D59 · 브로커를 internal / external 로 가르고, 사실은 «애그리거트가 만들고 유스케이스가 꺼내» 커밋 뒤에 나간다

**확정 · 08-10 · T50** · 자리 — <b>트리 137 → 138행</b>(<code>broker/{internal,external}/</code> · 계약도 둘) &nbsp;·&nbsp; 발행 경로 확정 &nbsp;·&nbsp; 2장 «빨간 점선 빈 상자»가 채워졌다

<dl class="kv">
<dt class="ans-dt">물음 ① — <b><code>broker/</code> 아래가 한 겹이라 「언제 바깥 미들웨어를 두나」가 갈 자리가 없다</b></dt>
<dd class="ans-dd filled"><b>트리를 <code>internal/</code> · <code>external/</code> 로 가르고 <b>계약도 둘</b>로 둔다.</b>
<div class="pre-wrap"><pre><code>framework/broker/
  internal/  internal_broker_port.py · internal_broker.py
  external/  external_broker_port.py · external_broker.py   ← 지금은 빈 파일</code></pre></div>
<b>계약을 하나로 두면 안 되는 까닭</b> — 보장이 다르다. 하나로 묶으면 <b>가장 약한 쪽(at-most-once)에 맞춰야</b> 하고,
그러면 바깥 중개자를 두고도 그 강한 보장을 못 쓴다. 반대로 강한 쪽에 맞추면 <code>internal</code> 이 <b>지킬 수 없는 약속</b>을 한다.
<br><b>★ 둘이라 얻는 것</b> — 갈아 끼면 <code>InternalBrokerPort</code> → <code>ExternalBrokerPort</code> 로 <b>시그니처가 바뀌어 mypy 가 모든 소비자를 짚는다</b>.
하나였다면 「소비자는 멱등해야 한다」가 <b>조용히</b> 생긴다.</dd>

<dt class="ans-dt">가르는 자 — <b>내가 «두 번» 틀렸고 사용자가 둘 다 바로잡았다</b></dt>
<dd class="ans-dd filled">
<div class="pre-wrap"><pre><code>내 안 ①  「듣는 쪽이 «다른 프로세스»에 있나」     → 배포 구성이라 코드에 없다
내 안 ②  「이 사실이 «BC 경계»를 넘나」            → 완전히 틀렸다
확정     「듣는 쪽이 «다른 배포 단위»에 있나」</code></pre></div>
<b>② 를 무너뜨린 한 문장</b> — <em>「external, internal <b>모두가 경계는 넘어</b> 그러니깐 broker 를 쓰는 거지」</em>.
<b>브로커를 쓴다는 것 자체가 경계를 넘는 일</b>이라 BC 경계로는 <b>아무것도 안 갈린다</b>.
이 칸이 지는 축은 «무엇을 배달하나»가 아니라 <b>«어떻게 배달하나»</b>다.
<br><b>★ 오답 넷</b> — <b>내구성 · 백프레셔 · 재시도</b>는 «워커»의 일이라 <code>cron_job/</code> 이 이미 받고(D48 ②),
<b>보존·재생</b>은 관할 밖(Event Sourcing)이다. 조사한 여섯 중 <b>넷이 브로커 축이 아니었다</b>.
<span class="dim">원전 정합 — Newman <em>“<b>Independently deployable</b> services…”</em>·<em>“the monolith is <b>not the enemy</b>”</em> ·
Grzybek ADR15 가 in-memory 를 채택하며 계기를 <em>“if we ever want to <b>separate a module to another process</b>”</em> 하나로 적는다 ·
ABP.IO 는 버스를 둘로 두되 <em>“LocalDistributedEventBus is the default implementation … to work as <b>in-process</b>”</em>.</span></dd>

<dt class="ans-dt">물음 ② — <b>브로커 인스턴스가 «몇 개»인지 트리가 답을 안 했다</b></dt>
<dd class="ans-dd filled"><b>오른쪽 119 칸은 「저장소에 브로커는 하나여야 한다」고 적는데, 검사는 「생성이 <code>composition_root</code> 안에서 한 번」이었다.</b>
그런데 <code>composition_root/</code> 는 <b>BC 마다</b> 있다 — 16 BC 면 브로커가 16개가 되고 <b>브로커를 쓰는 이유가 사라진다</b>.
<br><b>결정 — 인스턴스는 <code>internal_broker.py</code> «안»에 하나.</b> 「한 번」은 <b>파이썬 모듈 캐시</b>가 보장한다(AST 로 세는 것보다 세다).
모든 진입점(gunicorn · celery · <code>manage.py</code> · pytest)에서 똑같이 돈다.
<br><b>기각 — <code>&lt;project&gt;/broker.py</code></b>: <code>api.py</code>·<code>celery.py</code> 와 형제로 두는 안인데,
<b>BC 가 <code>&lt;project&gt;</code> 를 import 하게 되어 방향이 뒤집힌다</b>.
<span class="dim"><code>api.py</code> 가 거기 사는 것은 <b>BC 가 그걸 import 하지 «않아서»</b>다(<code>urls.py</code> 가 BC 라우터를 «등록»한다 — 방향이 반대).</span>
<br><b>「모듈 전역이라 나쁘다」는 이 트리가 이미 안 쓰는 논거다</b> — <code>&lt;project&gt;/api.py</code> 의 전역 API 객체가 같은 모양이다.
<b>D40</b> 이 signals 를 반려한 것은 <b>«구독표»가 전역이고 등록이 «임포트 부작용»</b>이라서였고,
여기는 구독표가 인스턴스 속성이고 등록이 <b>명시 호출</b>이다.</dd>

<dt class="ans-dt">물음 ③ — <b>부팅이 <code>ready()</code> 인데 <code>apps.py</code> 칸에 그 낱말이 없었다</b></dt>
<dd class="ans-dd filled"><b>「한 번」을 장고가 보장하지 않는다.</b>
<em>“in some corner cases, particularly in <b>tests which are fiddling with installed applications</b>, <code>ready</code> <b>might be called more than once</b>.
In that case, either write <b>idempotent</b> methods, or put a <b>flag</b> on your AppConfig classes”</em>.
<b>멱등을 고른다</b> — 플래그는 「누가 언제 켰나」를 하나 더 만들고, 테스트가 앱 레지스트리를 새로 지으면 <b>플래그도 새것이라 어차피 안 막는다</b>.
<br><b>★ 그런데 현행 코드가 이미 그 함정에 빠져 있었다.</b> <code>child_evicted_event.py</code> 가 <code>if handler not in _handlers</code> 로 멱등을 걸고
도크스트링에 <em>「두 번 등록된 handler 도 <b>한 번만 발화</b>한다」</em> 라 적는데, 공개 채널이 <b>람다로 감싸서</b> 넘긴다 —
<b>매번 «새 객체»라 <code>not in</code> 이 항상 참</b>이다. 실행하면 구독자가 2개, 호출이 2회다.
<br><b>그래서 검사가 «브로커»가 아니라 «넘기는 쪽»(<code>event_wiring.py</code>)에 선다</b> — 계약이 「같은 짝은 하나」를 지더라도
<b>넘기는 것이 매번 다른 객체면 그 계약이 아무것도 못 한다</b>.
<span class="dim">장고 자신도 함수 아이덴티티가 아니라 <b>별도 키</b>로 푼다 — signals 의 <code>dispatch_uid</code>.
우리는 키를 손으로 짓는 대신 <b>「이름 있는 모듈 함수만」</b>으로 좁혀 함수 객체를 키로 쓴다.</span>
<br><b>딸린 면제 하나</b> — <code>django_&lt;bc&gt;/</code> 의 리프 규칙(django 말고 import 0)에 <b>구멍이 하나 필요하다</b>:
<code>ready()</code> 본문의 <b>자기 BC <code>composition_root/event_wiring.py</code> 한 줄</b>. 폭이 그 한 줄로 닫혀 있다.</dd>

<dt class="ans-dt">물음 ④ — <b>2장 도해의 ⑧ 이 «빨간 점선 빈 상자»였다</b>(「실어 나를 장치는 아직 정하지 않았다」)</dt>
<dd class="ans-dd filled"><b>세 걸음이고 순서가 규칙이다</b> — ① 애그리거트에서 <code>pull_events()</code> ② 저장 ③ 옮겨 담아 <code>uow.after_commit(…)</code>.
<div class="pre-wrap"><pre><code>order.cancel(req.reason)                        # 무슨 일이 일어났나
facts: list[OrderEvent] = order.pull_events()   # ★ 애그리거트가 «사실을 남겼다»
self._orders.save(order)                        # 저장 — 사실은 이미 비었다</code></pre></div>
<b>★ 가운데 줄이 이 배치의 값이다</b> — 「애그리거트가 만들었다」가 <b>주어</b>(<code>order</code>)·<b>행위</b>(<code>pull</code> = 꺼내면 비운다)·<b>타입</b>(<code>list[OrderEvent]</code>) 셋으로 한 줄에 선다.
<span class="dim">사용자가 자를 이렇게 잡았다 — <em>「개발자가 use_case 를 볼 때 <b>aggregate 가 이벤트를 만들었구나</b> 까지 보이면 좋겠다」</em>. 그 자로 재면 후보 셋 중 하나만 남는다.</span>
<br><b>①이 ②보다 «앞»인 것이 요점</b> — 그래야 저장이 <b>「안 꺼낸 사실이 남았나」</b>를 볼 수 있다.
「잊으면 아무 일도 안 일어난다」를 <b>터지게</b> 바꾼 것이고, 이것이 <b>«자동 수거»를 대신한다</b>.
<br><b>★ 「모른다」에 서로 다른 셋이 섞여 있었다</b> —
<b>①무엇이 일어나는가</b>(보여야 한다) · <b>②누가 반응하는가</b>(안 보이는 것이 «사실»의 정의) · <b>③무엇으로 나르는가</b>(전역 제약 ②).
②를 알고 싶으면 <code>event_router.py</code> <b>한 자리</b>에 모여 있고,
<b>「그 뒤가 걱정되면 그건 사실이 아니라 «지시»다」</b>(Fowler 의 passive-aggressive command · D48 ①).</dd>

<dt class="ans-dt">기각 — <b>저장 경계가 «알아서 걷는» 안</b>(참조 구현 넷이 전부 그렇다)</dt>
<dd class="ans-dd filled">
<div class="pre-wrap"><pre><code>Spring Data   리포지토리가 걷는다   save/saveAll/delete… 호출마다
cosmicpython  UoW 가 걷는다        commit() 직후
eShop·Grzybek SaveChanges 가 걷는다  커밋 «직전»</code></pre></div>
<b>안 고른 까닭 셋</b> —
<b>⑴ 그 줄이 사라진다.</b> cosmicpython 이 대가를 자기 입으로 적는다:
<em>“It's <b>not obvious</b> when we call <code>commit</code> that we're also going to go and send email to people”</em> ·
<em>“that <b>hidden</b> event-handling code executes synchronously”</em> ·
<em>“there is <b>no single place</b> in the system where you can understand how a request will be fulfilled”</em>.
<br><b>⑵ 그 근거가 우리가 «금지한 것»에 의존한다</b> — <em>“it knows about all the aggregates currently in play <b>because it provides access to the repository</b>”</em>.
오른쪽 44 칸이 <b>「경계만 연다 — 리포지토리를 노출하지 않는다」</b>로 그것을 막는다.
<br><b>⑶ 장고에는 그 기계가 없다</b> — EF Core 의 ChangeTracker 도, SQLAlchemy 의 Identity Map·dirty tracking 도 없다.
<b>「알아서」의 «알아서»를 우리가 지어야 하고</b>, 그게 곧 ⑵ 를 여는 일이다.
<br><b>딸린 정합 — 시점</b>: eShop·Grzybek 의 «커밋 전»은 근거가 <em>“you want the side effects … <b>included in the same transaction</b>”</em> 인데,
그건 <b>한 트랜잭션이 애그리거트 여럿을 바꾼다는 뜻</b>이라 <b>D43</b> 과 정면으로 부딪힌다.
우리 «커밋 뒤»가 맞고 Khorikov 도 같은 쪽이다(<em>“the <b>‘commit before dispatching’</b> approach using <b>ORM post-commit hooks</b>”</em> = 장고 <code>transaction.on_commit</code>).
<br><b>범위도 일치한다</b> — <em>“Employ them for <b>inter-application communication only</b> … For inner-application communication, <b>get your program flow straight and explicit</b>”</em>.
같은 BC 안 순서는 <b>D42</b>·D48 이 이미 「유스케이스가 직접」으로 정했다.
<br><b>기각 — <code>uow.publish(event)</code></b>: 유스케이스가 브로커를 안 봐도 되지만 <b>「애그리거트가 만들었다」가 안 보이고</b>(지어낸 것처럼 읽힌다),
오른쪽 43 칸의 「계약은 셋」이 넷이 된다.</dd>

<dt class="ans-dt">딸린 것 — <b>«옮겨 담기»는 자동이 될 수 없다</b></dt>
<dd class="ans-dd filled"><b>애그리거트가 든 것과 브로커로 나가는 것이 «다른 타입»이다.</b>
안쪽 <code>event/&lt;event&gt;.py</code> 는 세밀하고 자주 바뀌고, 나가는 <code>published_event/&lt;event&gt;.py</code> 는 성글고 오래 간다.
<b>둘이 1:1 이 아니다</b> — 전부가 공표되지는 않는다.
<br>애그리거트가 «공표 사실»을 직접 들면 <b>도메인이 바깥 계약을 알게 된다</b>. 그래서 트리가 이미 <b>「옮겨 담는 일은 유스케이스가 한다」</b>고 적어 뒀고,
<b>그 문장이 자동 수거의 «상한»</b>이다.
<span class="dim">08-10 · T50 — <code>pull_events()</code> 는 <b>D40</b> 카드 <b>한 자리</b>에만 있고
행·<code>WHAT</code>·<code>NAMES</code> 어디에도 <b>0건</b>이었다. 카드에만 있으면 강제가 0이라 이번에 행으로 내렸다 —
<b>D58</b> 에서 잡은 것과 <b>같은 병</b>이다.</span></dd>
</dl>


---

# 본문에서 걷어낸 정정 이력

정본은 «지금의 결론»만 싣는다. 아래는 그 결론에 이르며 갈아 낀 문장들이다.

## 08-11 · C7′

검사기가 폴더 이름만 보고 있었다. 열 규칙이 같은 재료를 쓴다.

## 08-10 · G-1

옛 문장은 「여섯」이었고 결선을 <code>composition_root/dependency_wiring.py</code> <b>파일 하나</b>로 셌다.
D40 이 결선을 둘로 만들며 폴더가 됐고 <code>published_event/</code> 도 그때 섰는데 이 칸이 안 따라왔다(4차 리뷰 G-1).
아래 패널이 <em>「네 층 어디에도 속하지 않는 것은 <code>composition_root/</code> 와 <code>published_event/</code> 둘」</em> 이라 적고 있어 <b>같은 화면 안에서 어긋나 있었다</b>.

## 08-10 · 5차 리뷰

옛 문장은 「컨트롤러가 <b>Humble Object 여야 한다</b>」였다. 그러면 같은 화면의 규칙(<em>「예외→코드 매핑을 컨트롤러 «안»에 직접 쓴다 — helper 로 옮기지 않는다」</em>)과 <b>서로를 부정한다</b> — 그 규칙은 패턴이 요구하는 «분리 자체»를 금지하는 것이기 때문이다. 이름표를 바로잡았고, <b>매핑을 어디 둘지는 규칙 그대로 둔다</b>(그 교환은 사용자 결정으로 남긴다).

## 08-09 · T51

옛 문장은 여기에 <em>「빈 한 겹만 생긴다」</em> 를 근거로 붙였는데, <b>제1원칙이 「비어도 둔다」로 정해져 그 근거는 이제 못 쓴다</b>. 결론은 앞 절이 지탱한다 — <b>고를 값이 없는 것은 축이 아니다</b>.

## 08-11 · C6

옛 문장은 「늘지 않는다」로 끝나 «누가 늘리나»가 비어 있었다.</b> <code>webhook/</code> 행 note 의 <em>「<code>api/</code> 의 형제가 «는다»」</em> 가 그 빈자리를 <b>「BC 가 늘린다」</b>로 채워, 이 칸의 <b>「자식은 넷뿐」</b>과 정면으로 부딪히고 있었다. 「는다」의 주어는 처음부터 <b>정본 트리</b>였다.

## 08-09 · T44

옛 문장은 축을 «행위자 종류»라 적고 「사람이 부르면 <code>api/</code>」로 예시를 들었다.</b>
행위자와 전송이 여태 1:1 로 붙어 있어 구분이 안 드러났는데, <b>웹훅이 처음으로 둘을 갈랐다</b> — 행위자는 새 종류(외부 시스템)인데 전송은 기존 것(HTTP)이라 <b>옛 축이 답을 못 냈다</b>.
<b>그리고 Cockburn 이 그 구분을 «이 패턴이 고치려는 병»으로 지목한다</b> —
<em>“it becomes impossible to shift from a <b>human-driven use of the system to a batch-run system</b>… difficult or impossible to allow the program to be <b>driven by another program</b>”</em>.
그가 primary/secondary 를 가르는 자도 하나다 — <em>“<b>who triggers or is in charge of the conversation</b>”</em>. <b>«사람이냐»는 어디에도 없다.</b>

## 08-09 · T53

<code>error_out.py</code> 에서 개명했다. 트리에서 <code>_out</code> 은 «쌍의 한쪽»인데 <b>이 파일만 짝이 없어 그 접미사가 아무것도 안 말했다</b>. 클래스도 함께 옮긴다.

## 08-11 · C8

OAuth 콜백이 이 칸의 모순을 드러냈다.</b> 「우리 URL 을 바깥에 등록해 두고 그쪽이 부른다」는 <b>이 칸의 정의 그대로</b>인데, 옛 문면의 귀결 셋(멱등 필수 · ack · 4xx 면 재시도) 중 <b>어느 것도 참이 아니었다</b> — 리다이렉트라 ack 가 아니고, 브라우저가 오는 것이라 재시도가 없고, 멱등은 <b>만들 수 있지만 반드시일 필요는 없다</b>. 셋이 전부 <b>«발신자 스펙»에 달린 것을 우리 규칙으로 적은 것</b>이었다.

## 08-11 · C8

옛 문면은 「ack 를 돌려준다」·「4xx 를 주면 재시도가 안 멈춘다」로 수단을 우리가 닫았다.</b> 이 칸의 정의(계약이 저쪽 것)와 부딪히고, 실제로 발신자마다 기대 응답이 다르다.

## 08-10 · 축 정합

옛 문장은 「사람이 부르면 · 남의 BC 가 부르면 · 시간이 깨우면」으로 «행위자»를 축으로 적었다.
D53 이 1차 축을 «전송»으로 바꾸면서 그 근거를 <em>「행위자와 전송이 1:1 로 붙어 있어 여태 안 드러났다」</em> 로 들었는데, <b>이 칸이 바로 그 낡은 짝이었다</b>.

## 08-10 · C4

옛 문장은 «누가»를 안 적어 <b>한 줄이 둘을 덮었다</b>. 그래서 받는 쪽이 못 견디는 경우까지 ①의 «있다»로 밀렸고,
  거기서는 <b>보내는 쪽이 남의 실패를 져야 해서</b> 어느 칸으로도 못 갔다.

## 08-08 · F6

이 폴더는 <code>port/</code> 의 «형제»였고 이름이 <code>query_repository/</code> 였다.
  형제였던 근거가 <em>「포트는 바깥에 «행위자»가 있어야 하는데 DB 는 행위자가 아니다」</em> 였는데, <b>Cockburn 의 2차 행위자(secondary actor) 표준 예가 바로 DB·시계다</b> — 「행위자가 아니다」부터 원전 오독이라 그 자로는 아무것도 안 갈렸다.
  이름은 「조회냐」로 물어서 <b>애그리거트 리포지토리와 안 갈렸다</b>(그쪽도 <code>find_by_id</code>·<code>count</code> 를 한다).

## 08-10 · A-7

옛 문장은 <em>「여섯 중 넷만 … 빼놓은 <b>Output Boundary</b> 와 <b>Presenter</b>」</em> 라 <b>셈이 어긋나 있었다</b>(뺀 둘 중 하나가 그 여섯에 없으니 남는 것이 다섯이 된다).

## 08-09 · T46

옛 문장은 <em>「이 저장소는 아직 안 뒤집혔다」</em> 였다. <b>실측을 근거로 미룬 형태</b>라 <b>D26·D34 가 이미 두 번 강등한 논법</b>이고, 규율 ① 과 부딪힌다. 결론은 아래 잣대가 지탱하므로 안 바뀐다.

## 08-08 · F6

넷이었다. <code>query_repository/</code> 와 <code>transaction/</code> 이 <code>port/</code> 아래로 들어가면서 둘로 줄었다.

## 08-09 · T53

<code>&lt;use_case&gt;/dto/</code> 겹이 없어지고 <code>dto_in.py</code> 가 이 이름으로 여기 왔다. <code>dto</code> 는 <b>Fowler 의 «프로세스 사이» 패턴 이름</b>인데 우리 것은 같은 프로세스라 <b>낱말이 틀렸었다</b>.

## 08-09 · T53

<code>dto_out.py</code> 에서 개명. <b>Uncle Bob 실물</b>도 <code>…ResponseModel</code> 을 유스케이스 폴더에 <b>평평하게</b> 두고 겹을 안 만든다.

## 08-08 · F6

옛 문면은 「바깥에 «<b>행위자</b>»가 있나」를 판정으로 썼는데, <b>Cockburn 의 2차 행위자 표준 예가 바로 DB·시계다</b> — 「DB 는 행위자가 아니다」부터 원전 오독이었고, 그 자로는 아무것도 안 갈렸다.

## 08-10 · C-8

옛 문장은 「파일 이름은 폴더와 «같고» … <code>email_sender.py</code> 다」였다. D41 이 파일에 «종류» 접미사를 달면서 거짓이 됐는데 이 칸이 안 따라왔다(4차 리뷰 C-8).

## 08-08 · F6

이름이 <code>query_repository</code> 였다. 「조회냐」로 물으면 <b>애그리거트 리포지토리도 조회를 해서</b>(<code>find_by_id</code>·<code>count</code>) 사람을 틀린 데로 민다.
<code>command</code>/<code>query</code> 로 가르는 안도 같은 이유로 접었다 — <b><code>command</code> 는 거짓</b>이 된다.

## 08-08 · T22

옛 이름은 <code>…DomainBypassRepository</code> 였고, 이 칸은 「계보가 한 겹 흐려진다」를 <b>«치르는 값»으로 스스로 적어 두고 있었다</b>. D41 이 그 값을 <b>안 치르기로</b> 했다.

## 08-08 · F6

이름이 <code>transaction</code> 이었다. <b>파일도 클래스도 이미 <code>unit_of_work</code></b> 인데 폴더만 다른 말을 했고,
무엇보다 트리가 <b>「<code>transaction</code> 을 아는 것은 드리븐까지」</b>라고 못박아 두고 응용층 폴더에 그 낱말을 쓰고 있었다.

## 08-09 · T51

옛 문장은 <em>「빈 한 겹이 남는다 · 실측 47폴더 중 46이 비어 있다」</em> 였다. <b>제1원칙 아래서 «빈 것»은 위반이 아니라 정상</b>이라 그대로는 근거가 안 된다 — «비어서 나쁘다»가 아니라 <b>«구조 요소가 아닌 것을 골격에 올리면 안 된다»</b> 가 이유다.

## 08-08 · T28

여기는 원래 파일이었다. 08-07 · 2차 리뷰 S2 가 지운 것은
  「감당이 안 되면 «그때» 폴더가 된다」의 <b>「나중에 그때」라는 조건</b>이었지 폴더 자체가 아니었고,
  <b>D40</b> 이 조건 없이 폴더로 확정했다.

## 08-08 · T28

파일에서 폴더로 뒤집혔다</b>(<b>D40</b>). 08-07 · 2차 리뷰 S2 가 지운 것은
<em>「커져서 한 파일로 감당이 안 되면 «그때» <code>exception/</code> 폴더가 된다」</em> 에서 <b>「나중에 그때」라는 조건</b>이었지 폴더 자체가 아니었다
(⑴ R13 의 자 — 「나중에 그때」로 끝나는 문장은 그 자체가 결함 ⑵ 「감당이 안 되면」은 <b>기계로 못 재는 조건</b>이라 D10 에 걸린다).
<b>D40 은 조건을 없앤 자리에 폴더를 놓았다</b> — 「커지면 그때」가 아니라 «처음부터».

## 08-09 · T38

결론은 그대로고 «근거»를 갈았다.</b> 옛 문장은 <em>「창구 쪽은 남이 묶어서 잡으라고 기저를 주지만, 여기 것은 «타입»으로만 잡히므로 묶을 대상이 없다」</em> 였는데 <b>기저도 «타입»이라 앞 절에서 뒤 절이 안 나온다</b>. 「타입으로만」은 <b>«속성을 안 읽는다»의 근거</b>였고, 「도메인 ↔ 포트를 한 <code>except</code> 에 걸지 않는다」는 <b>둘을 서로 묶지 말라는 것</b>이지 도메인끼리를 막는 말이 아니었다.

## 08-08 · F6

<code>adapter/</code> 는 «폴더»로는 08-08 에 만들었다. D17 이 접었던 근거가
  「이 칸에 있는 것이 <b>전부</b> Adapter 라 선을 못 긋는다」였는데 <b>전부가 아니었다</b> — <code>django_&lt;bounded_context&gt;/</code> 는 어댑터가 아니고, 그 하나가 선을 긋는다.

## 08-07 · 3차 리뷰

옛 문장은 「<b>규정 밖 구역</b>이다 — 화살표·앎의 범위는 규정하지 «않는다»」였는데 <b>집행보다 넓었다</b>(면제는 리프 검사 둘뿐이고 타 BC·SDK 검사는 계속 걸린다).
그리고 「<code>scripts/</code> 와 같은 취급」도 부정확하다 — <code>scripts/</code> 는 트리 «밖»이라 자리도 이름도 0인데, 어드민은 <b>66~87행 여섯 줄로 자리와 이름이 규정된 «트리 안»</b>이다.
반대로 「규정하지 않는다」를 지우고 <b>D11 화살표를 그대로 걸어 보면</b> 42개 중 32개가 위반이고 <b>그중엔 유스케이스 호출이 0인 것도 있다</b> — 자기 BC 의 ORM 모델을 import 했다는 이유만으로다. <b>코드 결함이 아니라 <code>ModelAdmin</code> 계약이다.</b>

## 08-08 · F6

D17 이 <code>adapter/</code> 를 접은 근거는 「이 칸에 있는 것이 <b>전부</b> Adapter 라 아무 선도 긋지 못한다」였는데 <b>전부가 아니었다</b>. 그 하나가 선을 긋는다.

## 08-08 · F6

<code>repository/</code> 아래에 둘을 묶자는 안이 먼저 있었는데, <b>그 겹에는 공통 규칙이 0</b>이었다(도메인 import 필수 ↔ 금지). 셋으로 넓히니 규칙이 하나 생겼다.

## 08-08 · F6

옛 문면이 든 예시 다섯(시계·난수·락·스레드·파일시스템)은 <b>전부 업무 어휘가 0이라 자기 판정에 걸려 <code>framework/</code> 로 간다</b>. 한 건도 안 맞았다.

## 08-07 · 3차 리뷰 정정

트리에 붙어 있던 「실측 16/16」은 <b>«16개 BC 가 이 폴더를 갖고 있다»는 폴더 census</b> 였는데 「전부 지킨다」로 읽혔다.

## 08-09 · T47

4차 리뷰 SC-I 가 <em>「가짜가 살 칸도 없다」</em> 로 지적했다.
같은 지적의 <em>「강제 수단이 mypy 뿐」</em> 은 <b>틀렸다</b> — <code>ABC</code> 는 인스턴스화에서 <code>TypeError</code> 를 낸다(실행으로 확인).

## 08-08 · T32 이 칸 전체를

<b>Frameworks &amp; Drivers</b> 라 부르면서 「BC 의 유스케이스는 이 파일만 import 한다」를 규칙으로 강제했었다.
  <b>가장 안쪽이 가장 바깥을 알도록 «규칙이» 시킨 것</b>이라 Martin 의 <em>“Nothing in an inner circle can know anything at all about something in an outer circle.”</em> 와 정면으로 부딪쳤다.
  구조는 그대로 두고 <b>이름표와 그 위에 쌓은 논거</b>만 걷어냈다.

## 08-07 · 3차 리뷰

옛 문장은 「규칙은 <b>실측 숫자 하나로 굳는다</b> … 실측 0건이고 <b>그 0 을 그대로 규칙으로 삼는다</b>」였다.
  <b>D34</b> 근거②를 강등시킨 논법과 <b>문장 형태가 같아</b> 근거를 정의 쪽으로 옮겼다 — <b>답은 같다</b>(실측도 0건으로 재현된다).

## 08-08 · D41

옛 자는 «폴더 이름과 같은 파일이 있나»였다. <b>폴더 이름이 우연히 같은 것</b>에 기대는 대신 <b>접미사가 직접 «계약»이라고 말하게</b> 바꿨다. 판정 결과는 그대로다.

## 08-07 · 2차 리뷰

「판정 불가 4행」 중 107행이 여기 걸려 있었다. 107행 검사(«<code>composition_root</code> 밖에서는 아무도 import 하지 않는다»)를 돌리려면 <b>어느 파일이 구현인지부터 골라야</b> 하는데, 계약과 구현이 <b>같은 폴더에 나란히</b> 살아서 경로만으로는 못 골랐다. 이 한 줄로 <b>폴더 갈래와 파일 역할이 한꺼번에</b> 선다.

## 08-10 · T50

신설. 전에는 이 겹이 없어 <b>계약 하나에 구현 하나</b>가 <code>broker/</code> 바로 아래 있었고,
<em>「Redis·Celery 로 갈아탈 때 이 칸에 형제가 는다」</em> 가 <b>행 note 의 «산문»으로만</b> 있었다.

## 08-10 · T50

옛 문면은 「<code>composition_root</code> 가 하나 만들어 양쪽에 넘긴다」였다.
「저장소에 브로커는 하나여야 한다」(오른쪽 119 칸)와 <b>정면으로 어긋나 있었다</b>.
<code>&lt;project&gt;/broker.py</code> 로 올리는 안도 있었으나 <b>BC 가 <code>&lt;project&gt;</code> 를 import 하게 되어 방향이 뒤집힌다</b> —
<code>api.py</code> 가 거기 사는 것은 <b>BC 가 그걸 import 하지 «않아서»</b>이고, 브로커는 반대다.

## 08-10 · T50

<b>이 말이 트리에 없었다</b>. 정본 전체에 「싱글톤」도 인스턴스 수명을 말하는 문장도 0이었고,
그러면 <b>D40</b> 이 현행 코드를 반려한 근거 셋 중
<em>「<code>_handlers</code> 가 모듈 레벨 가변 전역」</em> 이 <b>수정안에서 안 고쳐진 채로 남는다</b>.

## 08-10 · T50

신설. 이 목록이 <b>어디에도 없었다</b>. <code>outbox</code> 하나만
<em>「여는 계기(브로커가 네트워크 너머로 나감)」</em> 에 매달려 있었고 나머지 여섯은 이름조차 없었다.

## 08-10 · T50

<code>&lt;technology&gt;_broker.py</code>(형제 여럿)로 두는 안이 있었고
<b>계약이 둘로 갈리면서 접혔다</b> — 계약이 이 폴더 안에 있으면 「같은 폴더의 <code>*_port.py</code> 를 상속」이 서고,
그러면 <b>D57</b> 의 「폴더 이름 되풀이」 문제가 <b>애초에 안 생긴다</b>.

## 08-09 · T48

칸이 없어서 <b>승격하면 자료가 갈 곳을 잃었다</b>.
<code>pure/</code> 로 보내면 <em>「대화 하나의 어휘 셋이 한 자리에 산다」</em> 가 깨지고,
<code>&lt;capability&gt;_port.py</code> 안에 우겨넣으면 <b>BC 쪽과 모양이 달라져 승격이 «파일 이동»이 아니게 된다</b>.

## 08-07 · 2차 리뷰

여기가 「판정 불가」로 남아 있던 자리다. 검사 문장은 있는데 <b>대상을 고르는 자가 없어서</b>, 계약과 구현이 같은 폴더에 나란히 사는 이 칸에서는 검사를 돌릴 수가 없었다. 94·105행에 이미 있던 모양(<em>계약 파일 = 폴더 이름</em>)을 <b>판정으로 적어</b> 닫았다 — 새 규칙이 아니라 쓰고 있던 규칙을 명문화한 것이다.


---

# 버린 안 · 뒤집은 판단

<p><b><code>boundary/</code> 신설안</b>(08-03) — <code>published_service/</code>와 포트 선언을 한 칸에 모으는 안이었다. 전수 검토 결과 닫힘 3 · 부분 5 · 안 닫힘 2 · <b>악화 2</b> · <b>새 문제 6</b>. 가장 큰 실패는 그 칸이 <b>선언과 구현을 함께 담은 것</b>이었고, 원인은 <em>아래 겹을 정하지 않은 채 위 겹을 확정한 것</em>이었다.</p>

<p><b>D14 «<code>&lt;use_case&gt;/</code> 평면» → «<code>&lt;area&gt;/&lt;use_case&gt;/</code>»</b>(08-04 뒤집음) — 클린의 Screaming Architecture 를 따라 평면으로 잡았다가 <b>대칭</b>을 택해 한 겹을 넣었다. 근거는 <code>api/&lt;area&gt;/</code> 와 <b>1:1</b> 이 되어 «바깥 엔드포인트 ↔ 안쪽 유스케이스»를 <em>같은 이름의 폴더</em>에서 찾게 된다는 것. Screaming 은 «최상위가 기술이 아니라 <b>업무</b>를 외쳐야 한다»가 요지이고 <code>&lt;area&gt;/</code> 도 업무 이름이라 어긋나지 않는다.</p>

<p><b>규칙을 그림으로 그려보니 문구의 구멍이 드러났다</b>(08-04) — 「사용자 → 컨트롤러 → 유스케이스 → 애그리거트 · 포트」를 한 장으로 그리고 «어디서 어디로 바로 갈 수 있나»를 따져보니, <b>D11 과 D13 이 각각 한 군데씩 못 막고 있었다</b>(컨트롤러 → <code>port/</code> · 애그리거트 → 자기 리포지토리). 둘 다 칸이나 이름은 그대로고 <b>문구만 한 줄씩 좁혔다</b>. <em>규칙은 글로 쓸 때가 아니라 그림으로 그릴 때 구멍이 보인다.</em></p>

<p><b>D3 «이름 유지»</b>(08-03 → 08-04 뒤집음) — 이름을 유지하기로 했다가 개명으로 바꿨다. 근거는 <b>의미가 바뀌면 이름의 값어치도 바뀐다</b>는 것이다. 이 칸이 «표현»에서 «모든 요청의 입구»가 되면서 이름이 <em>부정확한</em> 것에서 <b>틀린</b> 것이 됐다.</p>

<p><b>도해의 <code>port/&lt;other_bc&gt;_gateway.py</code> → <code>port/&lt;capability&gt;/&lt;capability&gt;.py</code></b>(08-05 정정) — «BC 의 입구는 언제나 <code>driving_layer</code> 아니냐»는 물음을 확인하다 <b>다른 것이 걸렸다</b>. 입구 규칙은 지켜지고 있었는데(옆 BC 상자가 <code>driving_layer/open_host_service/</code> 다), <b>포트 이름에 공급자 BC 가 박혀 있었다</b>. <code>clock_port.py</code>·<code>email_sender_port.py</code> 와 어긋나고, 공급자가 바뀌면 안쪽까지 고치게 된다. <em>도해를 고치려고 들여다보다 규칙의 구멍을 찾은 것이 이번이 두 번째다.</em></p>

<p><b>«<code>infra_layer</code>를 driven 이라 부르면 틀린 이름»</b>(08-04, 철회 → 08-05 개명) — 클린의 링 구분(Interface Adapters / Frameworks &amp; Drivers)을 <b>헥사고날 판정에 잘못 섞었다</b>. 헥사고날 기준으로는 이 칸 <b>전부가 driven</b> 이다(DB 는 secondary actor, ORM 은 그 기술). 철회로 끝내지 않고 <b>실제 개명까지 갔다</b> — <b>D16</b>. 그 사이에 D15 가 두 링을 <b>폴더로 갈라</b> 답하면서 반론이 완전히 없어졌다.</p>

---

# 이 문서가 스스로에게 걸었던 규율 다섯

| 번호 | 규율 | 자 |
|---|---|---|
| ① | **원리로 짓고, 기존 구현은 다 만든 뒤에 대조한다** | 이 물음이 «현행을 수정안에 매핑»하고 있나 |
| ② | **한 칸씩 닫고 넘어간다** — 칸 · 이름 · 화살표 · 앎의 범위 넷이 다 정해져야 다음으로 간다 | 넷 중 하나라도 비었나 |
| ③ | **트리 하나만 쓴다** — 대안 트리를 병렬로 유지하지 않는다 | 같은 칸에 답이 둘 살아 있나 |
| ④ | **약어를 쓰지 않는다** — 원전 패턴 이름은 줄이지 않는다. 다만 일반어가 된 약어(`api`·`dto`)는 둔다 | 정본의 «명명 방침» |
| ⑤ | **아직 안 쓰이는 확장 지점은 만들지 않는다** | **이 칸 자체에 결함이 있나** |

**① 이 금지하는 것은 기존 «구현»을 설계 입력으로 쓰는 것이지 «요구사항»이 아니다** — 「필요한 기능은 어드민에서 개발한다」 같은 방침은 실측이 아니라 주어진 조건이라 ① 에 안 걸린다(08-07 · 3차 리뷰가 어드민 판정에서 가른 선).

**⑤ 의 자는 「지금 실측에 있나?」가 아니라 「이 칸 자체에 결함이 있나?」다**(08-07 · R13). 이 트리의 목표가 «앞으로 생길 상황을 이미 커버한다» 이므로, **「나중에 생기면 그때 연다」로 끝나는 문장은 그 자체가 결함**이다.

---

**실측 대상** — `/Users/hyun/Desktop/broccoli-server` · BC 15개 · **읽기 전용**
**현행 진단서** — `workspace/design/2026-08-03-tree-vocabulary-design.html` (현행 트리 · 문제 P1~P12 · B1~B3 · 실측 부록)
