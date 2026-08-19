<!-- ═══════════════════ T0 스냅숏 메타 (B1 — 이 주석 블록은 사본 본문이 아니다) ═══════════════════
스냅숏: rule-owner-map T0 동결 사본 — 이후 원본이 변해도 B암 규칙 팩은 이 스냅숏에서만
구성한다(동결 문면 «T0 시점 스냅숏 고정» · T0 계획 3절 B1 — A/B 이전 배선 재지정 금지의 전제).

원본 경로        : workspace/plan/2026-08-11-rule-owner-map.md
원본 SHA-256     : e5fd04245d8380dd11cefb04fddc2749c9d5aa8e0b24d63d4c678edae525e7d4
사본 SHA-256     : e5fd04245d8380dd11cefb04fddc2749c9d5aa8e0b24d63d4c678edae525e7d4
                   (사본 = 이 주석 블록 종료 행 다음 행부터 파일 끝까지 — 원본과 byte 동일)
생성 시점 git 커밋: 8b212d99ebf02686c59ed35b10fcf3f9a9690179  (git rev-parse HEAD)
spec_lint.py SHA-256: ea48ab9c2d6de5423a0dacd33c77e9f1f97a404dfcc11bcb285d6ed75fd43fae
                   (workspace/tools/spec_lint.py — --emit-owner-map 생성기의 당시 실물)
생성일           : 2026-08-19 (T0 B1)
검증 절차        : 본문 = 메타 종료 행(HTML 주석 닫힘 `-->` 로 끝나는 행)의 다음 행부터 EOF.
                   추출·대조: awk 'f; /-->$/{f=1}' <이 파일> | shasum -a 256  → 위 SHA-256 과 일치해야 함.
                   (2026-08-19 정정 — 구 문면의 sed 패턴은 `$` 앵커가 실제 종료행 `-->` 접미와
                   불일치해 빈 입력 해시를 내던 오기. T2 적대 리뷰 L-M #14. awk 추출로 본문이
                   원본과 byte 동일함을 재실증 — «byte 동일» 등재 주장은 참·절차 문면만 결함).
═══ 스냅숏 메타 끝 ═══-->
# 규칙 → 소유자 매핑표 (Phase 0 산출물)

생성: `python3 workspace/tools/spec_lint.py --emit-owner-map` · 검증: 같은 도구 ⑧

- **ⓐ 정본**(`skills/discipline-houserules/references/final.md`)은 **전 규칙**의 값 소유자라 컬럼에 없다. ⓑ SKILL.md 는 포인터만(값 0).
- 모양: `path`·`ast`→ⓒ 하나 · `ast+`→ⓒ+ⓓ · `human`→ⓓ 하나. `어겼을 때=검사기`인 행의 ⓒ 는 검사기의 검사기(`workspace/tools/checker_lint.py`)다.
- **작업**: `신설`=그 자리에 새로 쓴다(백스톱 실측 0 이라 대부분) · `재작성`=있는 로직을 다시 · `치환`=이름 갈이 · `무변`.
- `#486~#492`(제1원칙)는 다른 모든 검사보다 먼저 도는 **별도 게이트**다(명세 «읽는 법»).

| # | 판정 | ⓒ 검사기 | ⓓ 에이전트 | 작업 | 비고 |
|---|---|---|---|---|---|
| 1 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 2 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 3 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 4 | ast | scripts/check-transaction-boundary.py (신설) | — | 신설 |  |
| 5 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 7 | ast | scripts/check-event-publish.py (신설) | — | 신설 |  |
| 8 | ast | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 9 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 10 | ast | scripts/check-layer-skeleton.py | — | 재작성 |  |
| 11 | ast+ | scripts/check-context-isolation.py | agents/discipline-reviewer.md | 신설 |  |
| 12 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 13 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 14 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 15 | human | — | agents/discipline-reviewer.md | 치환 | 면제 |
| 16 | human | — | agents/discipline-reviewer.md | 치환 | 면제 |
| 17 | ast+ | scripts/check-domain-model.py (신설) | agents/discipline-reviewer.md | 신설 |  |
| 18 | ast+ | scripts/check-domain-model.py (신설) | agents/discipline-reviewer.md | 신설 |  |
| 19 | path | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 20 | path | scripts/check-layer-skeleton.py | — | 재작성 |  |
| 21 | path | scripts/check-layer-skeleton.py | — | 재작성 |  |
| 23 | human | — | agents/discipline-reviewer.md | 치환 | 면제 |
| 24 | human | — | agents/discipline-reviewer.md | 치환 | 면제 |
| 25 | human | — | agents/discipline-reviewer.md | 치환 | 면제 |
| 26 | human | — | agents/discipline-reviewer.md | 치환 | 면제 |
| 27 | human | — | agents/discipline-reviewer.md | 치환 | 면제 |
| 28 | path | scripts/check-naming.py (신설) | — | 신설 |  |
| 30 | path | scripts/check-naming.py (신설) | — | 신설 |  |
| 33 | path | scripts/check-naming.py (신설) | — | 신설 |  |
| 34 | path | scripts/check-naming.py (신설) | — | 신설 |  |
| 35 | path | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 36 | ast+ | scripts/check-naming.py (신설) | agents/discipline-reviewer.md | 신설 |  |
| 39 | ast | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 40 | ast | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 41 | path | scripts/check-naming.py (신설) | — | 신설 |  |
| 42 | path | workspace/tools/checker_lint.py (신설) | — | 신설 |  |
| 43 | ast | scripts/check-naming.py (신설) | — | 신설 |  |
| 44 | path | scripts/check-naming.py (신설) | — | 신설 |  |
| 46 | ast | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 47 | ast | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 48 | path | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 49 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 51 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 52 | ast | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 53 | ast | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 54 | ast+ | workspace/tools/checker_lint.py (신설) | 메타(6번 지침·checker_lint) | 신설 |  |
| 56 | human | — | agents/discipline-reviewer.md | 치환 | 면제 |
| 58 | path | scripts/check-layer-skeleton.py | — | 재작성 |  |
| 59 | ast | scripts/check-api-error-controller-contract.py | — | 신설 |  |
| 62 | ast | scripts/check-api-error-controller-contract.py | — | 신설 |  |
| 63 | ast | scripts/check-openapi-error-declaration.py | — | 신설 |  |
| 64 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 67 | ast | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
| 68 | ast+ | scripts/check-usecase-dto-placement.py | agents/discipline-reviewer.md | 재작성 |  |
| 69 | ast+ | scripts/check-public-surface-annotation.py | agents/discipline-reviewer.md | 재작성 |  |
| 71 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 72 | human | — | 메타(6번 지침·checker_lint) | 치환 | 이행 |
| 73 | ast | workspace/tools/checker_lint.py (신설) | — | 신설 | 이행 |
| 74 | ast | workspace/tools/checker_lint.py (신설) | — | 신설 |  |
| 75 | ast | workspace/tools/checker_lint.py (신설) | — | 신설 |  |
| 76 | ast | scripts/check-naming.py (신설) | — | 신설 | 이행 |
| 77 | ast | workspace/tools/checker_lint.py (신설) | — | 신설 | 이행 |
| 78 | ast | workspace/tools/checker_lint.py (신설) | — | 신설 |  |
| 79 | path | workspace/tools/checker_lint.py (신설) | — | 신설 |  |
| 80 | path | workspace/tools/checker_lint.py (신설) | — | 신설 |  |
| 81 | path | scripts/check-layer-skeleton.py | — | 재작성 |  |
| 82 | ast+ | scripts/check-layer-skeleton.py | agents/discipline-reviewer.md | 재작성 |  |
| 83 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 84 | path | scripts/check-composition-root.py | — | 신설 |  |
| 85 | ast | scripts/check-composition-root.py | — | 신설 |  |
| 86 | ast+ | scripts/check-composition-root.py | agents/discipline-reviewer.md | 신설 |  |
| 87 | ast | scripts/check-naming.py (신설) | — | 신설 |  |
| 88 | path | scripts/check-layer-skeleton.py | — | 재작성 |  |
| 89 | ast | scripts/check-layer-skeleton.py | — | 재작성 |  |
| 90 | path | scripts/check-layer-skeleton.py | — | 재작성 |  |
| 91 | path | scripts/check-layer-skeleton.py | — | 재작성 |  |
| 92 | ast | scripts/check-layer-skeleton.py | — | 재작성 |  |
| 93 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 94 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 95 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 96 | ast | scripts/check-event-publish.py (신설) | — | 신설 |  |
| 97 | ast | scripts/check-naming.py (신설) | — | 신설 |  |
| 98 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 99 | path | workspace/tools/checker_lint.py (신설) | — | 신설 |  |
| 100 | human | — | agents/discipline-reviewer.md | 치환 | 면제 |
| 101 | ast | scripts/check-composition-root.py | — | 신설 |  |
| 102 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 103 | ast+ | scripts/check-usecase-dto-placement.py | agents/discipline-reviewer.md | 재작성 |  |
| 105 | path | scripts/check-composition-root.py | — | 신설 |  |
| 107 | ast | scripts/check-composition-root.py | — | 신설 |  |
| 108 | ast | scripts/check-composition-root.py | — | 신설 |  |
| 109 | ast | scripts/check-composition-root.py | — | 신설 |  |
| 110 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 111 | ast | scripts/check-composition-root.py | — | 신설 |  |
| 112 | path | scripts/check-composition-root.py | — | 신설 |  |
| 113 | path | scripts/check-context-isolation.py | — | 신설 |  |
| 114 | path | scripts/check-error-centralization.py | — | 신설 |  |
| 117 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 118 | path | scripts/check-naming.py (신설) | — | 신설 |  |
| 119 | ast | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 120 | path | scripts/check-api-error-controller-contract.py | — | 신설 |  |
| 121 | path | scripts/check-api-error-controller-contract.py | — | 신설 |  |
| 123 | path | scripts/check-api-error-controller-contract.py | — | 신설 |  |
| 124 | ast | scripts/check-api-error-controller-contract.py | — | 신설 |  |
| 125 | ast+ | scripts/check-api-error-controller-contract.py | agents/discipline-reviewer.md | 신설 |  |
| 126 | ast | scripts/check-api-error-controller-contract.py | — | 신설 |  |
| 127 | human | — | agents/discipline-reviewer.md | 치환 | 면제 |
| 129 | ast | scripts/check-synthetic-infra-exc.py | — | 신설 |  |
| 131 | ast | scripts/check-api-error-controller-contract.py | — | 신설 |  |
| 132 | ast | scripts/check-api-error-controller-contract.py | — | 신설 |  |
| 134 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 135 | path | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
| 136 | path | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
| 137 | human | — | agents/discipline-reviewer.md | 치환 | 면제 |
| 139 | ast | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
| 140 | ast+ | scripts/check-usecase-dto-placement.py | agents/discipline-reviewer.md | 재작성 |  |
| 141 | ast | scripts/check-usecase-dto-placement.py | — | 재작성 | 면제 |
| 142 | ast | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
| 143 | ast | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
| 144 | ast | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
| 145 | human | — | agents/discipline-reviewer.md | 치환 | 면제 |
| 146 | path | scripts/check-context-isolation.py | — | 신설 |  |
| 148 | path | scripts/check-naming.py (신설) | — | 신설 |  |
| 149 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 150 | path | scripts/check-context-isolation.py | — | 신설 |  |
| 151 | ast+ | scripts/check-context-isolation.py | agents/discipline-reviewer.md | 신설 |  |
| 152 | path | scripts/check-context-isolation.py | — | 신설 |  |
| 153 | ast+ | scripts/check-context-isolation.py | agents/discipline-reviewer.md | 신설 |  |
| 154 | path | scripts/check-context-isolation.py | — | 신설 |  |
| 155 | path | scripts/check-context-isolation.py | — | 신설 |  |
| 156 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 157 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 159 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 160 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 162 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 163 | path | scripts/check-context-isolation.py | — | 신설 |  |
| 164 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 166 | path | scripts/check-context-isolation.py | — | 신설 |  |
| 167 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 168 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 169 | path | scripts/check-naming.py (신설) | — | 신설 |  |
| 170 | path | scripts/check-context-isolation.py | — | 신설 |  |
| 171 | ast+ | scripts/check-context-isolation.py | agents/discipline-reviewer.md | 신설 |  |
| 172 | path | scripts/check-missable-entrance.py (신설) | — | 신설 |  |
| 173 | path | scripts/check-missable-entrance.py (신설) | — | 신설 |  |
| 174 | path | scripts/check-missable-entrance.py (신설) | — | 신설 |  |
| 175 | ast | scripts/check-missable-entrance.py (신설) | — | 신설 |  |
| 178 | ast | scripts/check-layer-skeleton.py | — | 재작성 |  |
| 179 | ast | scripts/check-missable-entrance.py (신설) | — | 신설 |  |
| 180 | ast | scripts/check-missable-entrance.py (신설) | — | 신설 |  |
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
| 192 | path | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
| 193 | path | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
| 194 | ast+ | scripts/check-usecase-dto-placement.py | agents/discipline-reviewer.md | 재작성 |  |
| 195 | ast | scripts/check-transaction-boundary.py (신설) | — | 신설 |  |
| 196 | ast | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
| 197 | ast | scripts/check-transaction-boundary.py (신설) | — | 신설 |  |
| 200 | ast | scripts/check-transaction-boundary.py (신설) | — | 신설 |  |
| 201 | path | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
| 202 | ast | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
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
| 214 | path | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 215 | path | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 216 | path | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 218 | path | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 219 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 220 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 221 | path | workspace/tools/checker_lint.py (신설) | — | 신설 |  |
| 225 | path | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 227 | ast+ | scripts/check-port-adapter-pairing.py (신설) | agents/discipline-reviewer.md | 신설 |  |
| 228 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 229 | path | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 231 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 232 | path | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 233 | ast+ | scripts/check-port-adapter-pairing.py (신설) | agents/discipline-reviewer.md | 신설 |  |
| 234 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 235 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 236 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 238 | path | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 239 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 240 | path | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 241 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 242 | path | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 244 | path | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 245 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 246 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 247 | ast | scripts/check-naming.py (신설) | — | 신설 |  |
| 248 | human | — | agents/discipline-reviewer.md | 치환 | 면제 |
| 249 | path | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 251 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 252 | path | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 253 | ast | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 254 | human | — | agents/discipline-reviewer.md | 치환 |  |
| 256 | ast | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 257 | ast+ | scripts/check-domain-model.py (신설) | agents/discipline-reviewer.md | 신설 |  |
| 258 | ast | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 259 | ast+ | scripts/check-domain-model.py (신설) | agents/discipline-reviewer.md | 신설 |  |
| 260 | ast | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 261 | ast | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 262 | path | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 263 | path | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 264 | ast | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 265 | ast | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 266 | ast | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 267 | ast | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 268 | ast+ | scripts/check-domain-model.py (신설) | agents/discipline-reviewer.md | 신설 |  |
| 269 | ast | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 270 | ast | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 271 | ast+ | scripts/check-event-publish.py (신설) | agents/discipline-reviewer.md | 신설 |  |
| 272 | ast | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 275 | ast | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 276 | ast | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 279 | ast | scripts/check-event-publish.py (신설) | — | 신설 |  |
| 280 | ast | scripts/check-event-publish.py (신설) | — | 신설 |  |
| 282 | path | scripts/check-transaction-boundary.py (신설) | — | 신설 |  |
| 283 | ast | scripts/check-transaction-boundary.py (신설) | — | 신설 |  |
| 285 | ast+ | scripts/check-transaction-boundary.py (신설) | agents/discipline-reviewer.md | 신설 |  |
| 287 | ast | scripts/check-transaction-boundary.py (신설) | — | 신설 |  |
| 288 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 289 | path | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 290 | path | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 291 | path | scripts/check-context-isolation.py | — | 신설 |  |
| 292 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 294 | ast | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 295 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 298 | ast | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 299 | path | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 300 | path | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 301 | ast+ | scripts/check-domain-model.py (신설) | agents/discipline-reviewer.md | 신설 |  |
| 302 | ast | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 303 | ast | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 304 | ast | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 305 | ast | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 307 | ast | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 308 | ast | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 309 | path | scripts/check-naming.py (신설) | — | 신설 |  |
| 310 | ast | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 311 | ast+ | scripts/check-domain-model.py (신설) | agents/discipline-reviewer.md | 신설 |  |
| 312 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 313 | path | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 314 | path | scripts/check-layer-skeleton.py | — | 재작성 |  |
| 315 | path | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 316 | human | — | agents/discipline-reviewer.md | 치환 |  |
| 318 | path | scripts/check-db-table.py | — | 신설 |  |
| 319 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 322 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 323 | path | scripts/check-event-publish.py (신설) | — | 신설 | 면제 |
| 324 | path | scripts/check-db-table.py | — | 신설 |  |
| 325 | path | scripts/check-db-table.py | — | 신설 |  |
| 326 | ast | scripts/check-db-table.py | — | 신설 |  |
| 327 | path | workspace/tools/checker_lint.py (신설) | — | 신설 |  |
| 328 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 329 | ast | scripts/check-db-table.py | — | 신설 |  |
| 330 | ast | scripts/check-db-table.py | — | 신설 |  |
| 331 | ast | scripts/check-db-table.py | — | 신설 |  |
| 332 | ast | scripts/check-db-table.py | — | 신설 |  |
| 334 | path | scripts/check-db-table.py | — | 신설 |  |
| 335 | ast | scripts/check-db-table.py | — | 신설 |  |
| 336 | path | scripts/check-mechanism-ownership.py | — | 신설 |  |
| 337 | path | scripts/check-mechanism-ownership.py | — | 신설 |  |
| 338 | ast | scripts/check-mechanism-ownership.py | — | 신설 |  |
| 339 | path | scripts/check-naming.py (신설) | — | 신설 | 면제 |
| 340 | path | scripts/check-naming.py (신설) | — | 신설 |  |
| 341 | path | scripts/check-naming.py (신설) | — | 신설 |  |
| 342 | ast | scripts/check-naming.py (신설) | — | 신설 |  |
| 343 | ast+ | scripts/check-naming.py (신설) | agents/discipline-reviewer.md | 신설 |  |
| 344 | ast | scripts/check-naming.py (신설) | — | 신설 |  |
| 345 | ast | scripts/check-naming.py (신설) | — | 신설 |  |
| 346 | human | — | agents/discipline-reviewer.md | 치환 | 면제 |
| 347 | ast+ | scripts/check-context-isolation.py | agents/discipline-reviewer.md | 신설 |  |
| 348 | ast | scripts/check-naming.py (신설) | — | 신설 |  |
| 349 | path | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 350 | path | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 351 | path | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 352 | path | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 353 | path | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 354 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 355 | ast+ | scripts/check-transaction-boundary.py (신설) | agents/discipline-reviewer.md | 신설 |  |
| 356 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 357 | path | workspace/tools/checker_lint.py (신설) | — | 신설 |  |
| 358 | ast | scripts/check-public-surface-annotation.py | — | 재작성 |  |
| 359 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 361 | path | scripts/check-context-isolation.py | — | 신설 |  |
| 362 | path | scripts/check-context-isolation.py | — | 신설 | 면제 |
| 363 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 364 | path | scripts/check-context-isolation.py | — | 신설 |  |
| 365 | path | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 366 | ast | scripts/check-naming.py (신설) | — | 신설 |  |
| 367 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 368 | ast+ | scripts/check-port-adapter-pairing.py (신설) | agents/discipline-reviewer.md | 신설 |  |
| 369 | path | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 370 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 371 | path | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 372 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 373 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 374 | path | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 375 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 376 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 382 | ast | scripts/check-naming.py (신설) | — | 신설 |  |
| 383 | path | scripts/check-test-config.py | — | 신설 |  |
| 384 | path | scripts/check-test-config.py | — | 신설 |  |
| 385 | path | scripts/check-test-config.py | — | 신설 |  |
| 387 | ast | scripts/check-test-config.py | — | 신설 |  |
| 388 | ast | scripts/check-test-config.py | — | 신설 |  |
| 389 | ast | scripts/check-test-config.py | — | 신설 |  |
| 390 | ast | scripts/check-test-config.py | — | 신설 |  |
| 391 | path | scripts/check-test-config.py | — | 신설 |  |
| 392 | ast | scripts/check-test-config.py | — | 신설 |  |
| 393 | path | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 395 | path | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 396 | path | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 398 | path | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 401 | path | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 402 | path | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 403 | ast | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 404 | ast | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 405 | path | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 406 | ast | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 407 | path | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 408 | ast | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 411 | path | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 412 | path | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 413 | ast | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 414 | path | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 415 | ast | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 416 | ast | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 417 | path | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 420 | path | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 423 | path | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 425 | ast+ | scripts/check-business-vocabulary.py (신설) | agents/discipline-reviewer.md | 신설 |  |
| 426 | ast | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 428 | path | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 429 | path | scripts/check-layer-skeleton.py | — | 재작성 |  |
| 430 | ast | scripts/check-layer-skeleton.py | — | 재작성 |  |
| 431 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 432 | ast | scripts/check-layer-skeleton.py | — | 재작성 |  |
| 433 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 434 | path | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 435 | path | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 436 | path | scripts/check-layer-skeleton.py | — | 재작성 | 면제 |
| 437 | ast | scripts/check-composition-root.py | — | 신설 |  |
| 440 | ast | scripts/check-composition-root.py | — | 신설 |  |
| 441 | ast | scripts/check-composition-root.py | — | 신설 |  |
| 442 | ast | scripts/check-broker-contract.py (신설) | — | 신설 |  |
| 443 | ast | scripts/check-broker-contract.py (신설) | — | 신설 |  |
| 444 | ast | scripts/check-broker-contract.py (신설) | — | 신설 |  |
| 445 | path | scripts/check-test-config.py | — | 신설 |  |
| 446 | path | scripts/check-test-config.py | — | 신설 |  |
| 447 | ast | scripts/check-test-config.py | — | 신설 |  |
| 448 | ast+ | scripts/check-business-vocabulary.py (신설) | agents/discipline-reviewer.md | 신설 |  |
| 449 | human | — | 메타(6번 지침·checker_lint) | 치환 |  |
| 450 | path | scripts/check-context-isolation.py | — | 신설 |  |
| 451 | ast+ | scripts/check-missable-entrance.py (신설) | agents/discipline-reviewer.md | 신설 |  |
| 452 | human | — | 메타(6번 지침·checker_lint) | 치환 |  |
| 453 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 454 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 455 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 456 | ast | scripts/check-public-surface-annotation.py | — | 재작성 |  |
| 457 | path | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 459 | path | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 460 | path | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 462 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 463 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 464 | path | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 465 | path | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 467 | path | scripts/check-db-table.py | — | 신설 |  |
| 470 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 471 | ast | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 472 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 473 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 474 | ast | scripts/check-api-error-controller-contract.py | — | 신설 |  |
| 475 | ast+ | scripts/check-port-adapter-pairing.py (신설) | agents/discipline-reviewer.md | 신설 |  |
| 476 | path | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 477 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 480 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 481 | path | scripts/check-naming.py (신설) | — | 신설 |  |
| 482 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 483 | path | scripts/check-context-isolation.py | — | 신설 |  |
| 484 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 485 | ast+ | scripts/check-port-adapter-pairing.py (신설) | agents/discipline-reviewer.md | 신설 |  |
| 486 | path | scripts/check-layer-skeleton.py | — | 재작성 | 제1원칙 선행 게이트 |
| 487 | path | workspace/tools/checker_lint.py (신설) | — | 신설 | 제1원칙 선행 게이트 |
| 488 | path | scripts/check-layer-skeleton.py | — | 재작성 | 제1원칙 선행 게이트 |
| 489 | path | scripts/check-layer-skeleton.py | — | 재작성 | 제1원칙 선행 게이트 |
| 490 | path | scripts/check-layer-skeleton.py | — | 재작성 | 제1원칙 선행 게이트 |
| 491 | path | scripts/check-layer-skeleton.py | — | 재작성 | 제1원칙 선행 게이트 |
| 492 | ast+ | workspace/tools/spec_lint.py | agents/discipline-reviewer.md | 신설 | 제1원칙 선행 게이트 |
| 493 | ast | scripts/check-public-surface-annotation.py | — | 재작성 |  |
| 494 | human | — | 메타(6번 지침·checker_lint) | 치환 |  |
| 495 | ast | workspace/tools/checker_lint.py (신설) | — | 신설 |  |
| 496 | ast | workspace/tools/checker_lint.py (신설) | — | 신설 |  |
| 497 | path | scripts/check-composition-root.py | — | 신설 |  |
| 498 | ast | scripts/check-composition-root.py | — | 신설 |  |
| 500 | ast | scripts/check-composition-root.py | — | 신설 |  |
| 501 | ast | scripts/check-composition-root.py | — | 신설 |  |
| 502 | path | scripts/check-event-publish.py (신설) | — | 신설 |  |
| 503 | ast | scripts/check-event-publish.py (신설) | — | 신설 |  |
| 504 | ast | scripts/check-event-publish.py (신설) | — | 신설 |  |
| 505 | ast | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 506 | ast | scripts/check-domain-model.py (신설) | — | 신설 |  |
| 507 | ast | scripts/check-event-publish.py (신설) | — | 신설 |  |
| 508 | ast | scripts/check-event-publish.py (신설) | — | 신설 |  |
| 509 | ast | scripts/check-event-publish.py (신설) | — | 신설 |  |
| 511 | ast+ | scripts/check-composition-root.py | agents/discipline-reviewer.md | 신설 |  |
| 512 | ast+ | scripts/check-missable-entrance.py (신설) | agents/discipline-reviewer.md | 신설 |  |
| 514 | ast | scripts/check-missable-entrance.py (신설) | — | 신설 |  |
| 515 | path | scripts/check-missable-entrance.py (신설) | — | 신설 |  |
| 516 | ast | scripts/check-missable-entrance.py (신설) | — | 신설 |  |
| 517 | ast | scripts/check-missable-entrance.py (신설) | — | 신설 |  |
| 518 | ast | scripts/check-broker-contract.py (신설) | — | 신설 |  |
| 520 | ast+ | scripts/check-broker-contract.py (신설) | agents/discipline-reviewer.md | 신설 |  |
| 521 | ast | scripts/check-broker-contract.py (신설) | — | 신설 |  |
| 522 | human | — | agents/discipline-reviewer.md | 치환 | 면제 |
| 523 | ast | scripts/check-broker-contract.py (신설) | — | 신설 |  |
| 524 | ast | scripts/check-broker-contract.py (신설) | — | 신설 |  |
| 525 | ast | scripts/check-broker-contract.py (신설) | — | 신설 |  |
| 526 | human | — | agents/design-architect.md | 치환 |  |
| 527 | ast | scripts/check-broker-contract.py (신설) | — | 신설 |  |
| 528 | ast | scripts/check-broker-contract.py (신설) | — | 신설 |  |
| 529 | ast+ | scripts/check-broker-contract.py (신설) | agents/discipline-reviewer.md | 신설 |  |
| 530 | human | — | agents/design-architect.md | 치환 |  |
| 531 | ast | scripts/check-broker-contract.py (신설) | — | 신설 |  |
| 532 | ast+ | scripts/check-broker-contract.py (신설) | agents/discipline-reviewer.md | 신설 |  |
| 533 | ast | scripts/check-broker-contract.py (신설) | — | 신설 |  |
| 534 | path | scripts/check-broker-contract.py (신설) | — | 신설 |  |
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
| 546 | ast | scripts/check-domain-model.py (신설) | — | 신설 |  |
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
| 557 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
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
| 568 | path | scripts/check-error-centralization.py | — | 신설 |  |
| 569 | ast | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
| 570 | path | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
| 571 | ast | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
| 572 | ast | scripts/check-error-centralization.py | — | 신설 |  |
| 573 | path | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 574 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 575 | path | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 576 | path | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 577 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 578 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 579 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 580 | ast | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 581 | path | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 582 | path | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 583 | path | scripts/check-port-adapter-pairing.py (신설) | — | 신설 |  |
| 584 | ast+ | scripts/check-business-vocabulary.py (신설) | agents/discipline-reviewer.md | 신설 |  |
| 585 | ast | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 587 | ast | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 588 | ast | scripts/check-naming.py (신설) | — | 신설 |  |
| 589 | ast+ | scripts/check-naming.py (신설) | agents/discipline-reviewer.md | 신설 |  |
| 590 | ast+ | scripts/check-naming.py (신설) | agents/discipline-reviewer.md | 신설 |  |
| 591 | ast | workspace/tools/checker_lint.py (신설) | — | 신설 | 이행 |
| 592 | human | — | 메타(6번 지침·checker_lint) | 치환 | 이행 |
| 593 | ast | scripts/check-mechanism-ownership.py | — | 신설 |  |
| 594 | ast+ | scripts/check-port-adapter-pairing.py (신설) | agents/discipline-reviewer.md | 신설 |  |
| 595 | ast+ | scripts/check-port-adapter-pairing.py (신설) | agents/discipline-reviewer.md | 신설 |  |
| 596 | path | scripts/check-test-config.py | — | 신설 | 면제 |
| 597 | ast | scripts/check-transaction-boundary.py (신설) | — | 신설 |  |
| 599 | ast | scripts/check-transaction-boundary.py (신설) | — | 신설 |  |
| 600 | ast | scripts/check-event-publish.py (신설) | — | 신설 |  |
| 601 | ast | scripts/check-event-publish.py (신설) | — | 신설 |  |
| 602 | ast | workspace/tools/checker_lint.py (신설) | — | 신설 |  |
| 603 | ast | scripts/check-broker-contract.py (신설) | — | 신설 |  |
| 604 | ast | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 606 | ast | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 607 | ast+ | scripts/check-business-vocabulary.py (신설) | agents/discipline-reviewer.md | 신설 |  |
| 609 | path | workspace/tools/tree_mirror_check.py | — | 신설 | 이행 |
| 610 | path | scripts/check-naming.py (신설) | — | 신설 | 이행 |
| 611 | path | scripts/check-naming.py (신설) | — | 신설 | 이행 |
| 613 | ast | workspace/tools/checker_lint.py (신설) | — | 신설 |  |
| 614 | path | scripts/check-business-vocabulary.py (신설) | — | 신설 | 이행 |
| 615 | ast | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 616 | ast | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 617 | ast | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 618 | ast+ | scripts/check-business-vocabulary.py (신설) | agents/discipline-reviewer.md | 신설 |  |
| 619 | ast+ | scripts/check-business-vocabulary.py (신설) | agents/discipline-reviewer.md | 신설 |  |
| 620 | path | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 621 | path | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 622 | ast | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 623 | path | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 624 | ast | scripts/check-business-vocabulary.py (신설) | — | 신설 |  |
| 625 | human | — | agents/discipline-reviewer.md | 치환 | 면제 |
| 626 | human | — | agents/design-architect.md | 치환 |  |
| 627 | ast | scripts/check-event-publish.py (신설) | — | 신설 |  |
| 628 | ast | scripts/check-layer-skeleton.py | — | 재작성 |  |
| 629 | ast+ | scripts/check-missable-entrance.py (신설) | agents/discipline-reviewer.md | 신설 |  |
| 630 | ast | scripts/check-db-table.py | — | 신설 |  |
| 631 | ast | scripts/check-db-table.py | — | 신설 |  |
| 632 | ast | scripts/check-db-table.py | — | 신설 |  |
| 633 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 634 | ast | scripts/check-context-isolation.py | — | 신설 |  |
| 635 | ast | scripts/check-usecase-dto-placement.py | — | 재작성 |  |
| 636 | ast | scripts/check-error-centralization.py | — | 신설 |  |
