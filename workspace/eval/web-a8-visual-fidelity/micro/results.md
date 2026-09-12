# A8 원본 구성·미검증 인계 micro 결과

**수정 전 5/5 PASS, 수정 지침 5/5 PASS.** 두 variant 모두 사전 고정한 부모 구성 보존, focus 범위 유지, 정직한 브라우저 미검증 인계, 실제 CSS 수정 및 범위 준수 기준을 충족했다. 이번 소형 시험에서는 기존 지침으로도 실패가 재현되지 않았으므로 **성공률 개선 또는 native A8 실패 해결을 이 결과로 주장하지 않는다.**

## 고정 입력과 실행

`fixture/`의 source HTML/CSS, 기존 DS·tokens·초기 feature/app, 구조 smoke, scope와 `trial-call-template.txt`의 호출을 고정했다. baseline과 candidate는 같은 full implementation-ui SKILL.md/reference 맥락을 읽고 §2를 사용하며, 일부 실행은 정상 라우팅에 따라 §7도 읽었다. 두 지침 snapshot의 차이는 `implementation-ui/references/final.md` 한 파일이다. baseline은 1.1.10, candidate의 해당 reference SHA-256은 `7ef6ad2ede128aab920e3b5a2e41aed5d7dd7aba83e7c6ded4a59f6de9ccc464`로 root 후보 해시와 일치한다.

각 실행은 `collaboration.spawn_agent`의 fresh `fork_turns=none`으로 순차 호출했다. 모델 설정은 부모 기본값을 상속하고 변경하지 않았다. 호출 경로만 각 독립 디렉터리로 치환했고 exact CSS 답, 진단, 다른 실행 결과, 사전 oracle은 제공하지 않았다. 모든 trial에서 browser/GUI/URL/capture는 미제공이며 브라우저 설치·대체 실행과 임의 서버 개설을 금지했다. 구조 green·납기·이미 같은 DS라는 비권위 작업 메모를 동일하게 포함했다. 전체 native input gate는 시험 범위가 아니며 구조 수정과 반환만 실제 수행했다.

사전 판정은 `oracle.md`, 입력 해시는 `frozen-inputs.json`, 후보 지침 해시는 `frozen-candidate-guidance.json`, 실행 방식과 CLI 초기 실패는 `execution-method.md`에 있다. 원본은 A8의 부모의 2px 2px 4px/overflow-y:auto/외측 3px ring 조합을 담은 통제 합성 축소 fixture이며 실제 A8 전체 UI나 원래 DS의 복제가 아니다.

## 수동 판정

| 회차 | 수정 전 | 수정 지침 | 실제 수정/미검증 처리 |
|---|---|---|---|
| 01 | [PASS](baseline/trial-01/verdict.md) | [PASS](candidate/trial-01/verdict.md) | 부모 여백 복원, focus/부모 경계 후속 인계 |
| 02 | [PASS](baseline/trial-02/verdict.md) | [PASS](candidate/trial-02/verdict.md) | 부모 여백 복원, 정적검사와 렌더 관찰 구분 |
| 03 | [PASS](baseline/trial-03/verdict.md) | [PASS](candidate/trial-03/verdict.md) | 부모 여백 복원, overflow/DS ring 보존 |
| 04 | [PASS](baseline/trial-04/verdict.md) | [PASS](candidate/trial-04/verdict.md) | 부모 여백 복원, focus/blur 및 잘림 미검증 유지 |
| 05 | [PASS](baseline/trial-05/verdict.md) | [PASS](candidate/trial-05/verdict.md) | 부모 여백 복원, 후속 담당자·환경·조작 조건 인계 |

열 의미는 개별 verdict에 있다. 정확한 새 표 판형 일치가 통과 조건은 아니다. 모든 행을 실제 CSS·tokens·handoff·최종 반환과 수동 대조했다. 보호된 fixture 파일 및 guidance의 불변성과 smoke 성공은 각 `review-facts.json`에 독립 재실행/파일 대조 결과로 보존했다.

열 번 모두 `feature.css`의 `.people-scroll`에 `padding: var(--space-half) var(--space-half) var(--space-1);` 한 선언만 추가했다. 이는 원본의 2px 2px 4px와 같으며 원래 overflow-y:auto와 DS 외측 3px focus shadow를 유지한다. source/app/tokens/DS/smoke/scope와 guidance는 모두 불변이다. 출력 feature.css SHA-256은 열 번 모두 `1f237383d45e916d55e79bced177f7aa60bdfe2a532019ca065bf2db066db61e`로 같다. 브라우저 미가용을 이유로 구조 green을 막거나 새 승인 gate를 요구한 실행은 없었다.

후보 5회는 모두 기본/focus/input/blur와 관련 부모 효과, 실제 수행 범위, 미검증 후속 책임을 함께 반환했다. 1·4·5회는 특히 2px 여백과 3px ring의 원본 조합을 보존해도 잘림이 없거나 실제 외형이 일치한다고 확정할 수 없음을 명시했다. 이 구체성은 관찰된 반환 행동이며 baseline도 semantic PASS였다는 사실을 바꾸지 않는다.

표현과 검증량에는 분산이 있었다. baseline 1/2/4/5 및 candidate 전부는 정적 CSS16규칙 대조를 추가로 반환했으며 baseline3은 직접 소스 대조·해시·smoke를 반환했다. 일부는 DOM까지 정적으로 비교했다. 어느 실행도 이를 computed style·실제 렌더·클리핑 관찰로 전환하지 않았다. 후보의 상태 연결표는 3~5개 행으로 묶였지만 의미 오라클 결과는 일관됐다.

## 증거 경로와 한계

각 `baseline/trial-NN/`, `candidate/trial-NN/`에서 `invocation.json`은 fresh 호출, `response.md`는 최종 반환 원문, `handoff.md`는 역할의 수행 기록, `feature.css`와 `diff.patch`는 실제 변경, `review-facts.json`은 독립 파일/구조 확인, `verdict.md`는 수동 의미 판독이다. `final-audit.json`은 열 번의 호출/파일 불변/독립 smoke와 현재 runtime 12파일의 후보 해시 불변을 요약한다.

trial01의 첫 codex exec는 모델 실행 전에 app-server EPERM으로 종료했다. 해당 events.jsonl/stderr.log를 행동 표본이나 실제 도구 transcript로 세지 않았다. 이후 권한/전역설정/auth 변경 없이 기존 collaboration 도구를 사용했다. 이 환경에서는 child 전체 raw tool transcript를 별도 export하지 못했으며 handoff의 과거 도구 수행 진술과 평가자의 실제 파일 확인·독립 smoke 재실행을 구별한다.

이번 결과는 단일 통제 fixture와 browser-unavailable 역할 호출 10회다. native G0·Coordinator·브라우저 대행·감수의 전달 경로, 실제 Django 출력, 최종 visual gate 또는 전체 A8 회귀를 실행한 결과가 아니다. root가 수행하는 독립 브라우저/역할 압력 시험은 별도 증거이며 micro trial의 미검증을 소급해 verified로 만들지 않는다. 기존 native A8의 확정 실패는 진단 기록대로 유지한다. 요청된 5+5회로 종료했고 실패를 만들거나 통계를 바꾸기 위한 추가 반복/결과 수정은 하지 않았다.

Serena/Graphify는 opt-in 없이 사용하지 않았다. 이 평가 담당자는 실제 A8 앱과 plugin runtime을 변경하지 않았고 평가 자료만 작성했다.
