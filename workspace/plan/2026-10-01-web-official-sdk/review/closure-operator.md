# 닫힘 확인(운영자) — web 2차 리뷰 지적 F1~F7 · 대상 66781e89 (2026-10-01 20시)

Codex 리뷰 창(sdk-review)의 닫힘 확인은 OpenAI 쪽 안전 필터(«Daybreak isn't available for Astra. Some cybersecurity requests may still be limited»)로 응답이 막혔다. 필터 우회는 하지 않고, 운영자가 리뷰어 재현 자료를 수정본에 그대로 다시 돌렸다.

## 방법
- 리뷰어 자료(`$TMPDIR/web-sdk-review.Jk1VlJ/`)의 `probes.py` · `boundary-probes.cjs` · `gateway-urls.json` 을 복사하고, `repo` = `66781e89` 공유 클론.
- `probes.py` 한 줄 보정: 후보 단계가 이제 거절(exit 2)돼 산출 폴더가 없으므로 초안 쓰기 전 `mkdir`(구현자와 같은 보정).

## 결과(수정 전 → 수정 뒤)
| 지적 | 재현 | 전 | 뒤 |
|---|---|---|---|
| F1 restore 밖 파일 덮어씀 | file `../../restore-victim.js` | 덮어씀 True | False · «승인 불요 복원 대상이 아니다(쓰기 0)» |
| F2 첫 채택 gateway 경로 원문 없음 | install | 0 | 1 |
| F3 문서 리다이렉트 http 외부 | candidate · install | 0 · 0 | 2 · 1 |
| F4 gateway 정규형 | Python · JS 각 7표본 | JS 4꼴이 승인 경로로 통과(`v2/user/me` · `..` · 앞 공백 외부 · 역슬래시 외부) | 넷 다 path null · findings 4 · 정상 `/v2/user/me` · `https://kapi.kakao.com/v2/user/me/?x=1` · `/v2/user/%6De` 통과 |
| F5 WV8 우회 5꼴 | backstop `--only wv8` | 0 ×5 | 2 ×5 |
| F6 미등재 하위 링크 | verify · gated | 0 · 0 | 2 · 2 |
| F7 K51 걸음 | 구현자 픽스처 F7a·F7b · 변이 red 확인(구현자 기록) | — | 고정 |

## 추가 우회 시도(WV8 · 운영자)
- 잡힘(exit 2): `document?.write` · `Reflect.apply(document.write, …)` · `globalThis.document.write` · `window['document'].write` · `document.writeln` · `f.contentWindow.document.write` · `f.srcdoc =` · `setAttribute('srcdoc', …)`
- 정상 짝 통과(exit 0): `logger.write` · `stream.write` · `el.textContent =`
- **안 잡힘(exit 0) 2꼴**: 구조 분해 `const {write} = document; write.call(document, payload)` · 이어 붙인 키 `document['wr'+'ite'](payload)`
  - 설계 §5 WV8 은 정적 덫이며 «정적 덫이 못 잡는 몫은 모든 레인에서 discipline-reviewer-web · SDK 레인은 G2 실행 확인»으로 나눈다. 리뷰 F5 회귀가 아니라 기존 정적 한계다 → minor · 기록.

## 판정
닫힘(착지 가능). 남은 것 = 위 정적 한계 2꼴(minor).
