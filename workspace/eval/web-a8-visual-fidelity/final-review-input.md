# 최종 독립 적대 구현 리뷰 패킷

작업 루트 `/Users/hyun/.cache/dddjango-web-a8-20260913`, 기준 HEAD `3e786dce64eee3da81d98e1dc2dcad598ab5d026`. 아직 커밋하지 않은 전체 변경을 읽기 전용으로 검토한다. 구현 작성자의 문맥을 상속하지 않은 fresh 리뷰다. 사용자 요청은 특별한 결정이 없으면 배포까지 진행이며, 리뷰어는 수정·커밋·배포를 하지 않는다.

기준:
- `docs/DEVELOPMENT.md`, `workspace/plan/2026-09-13-web-a8-visual-fidelity.md`
- `workspace/eval/web-a8-visual-fidelity/diagnosis.md`의 A8-V1~V3와 판정 경계
- `dddjango-web/` 정본 6파일, `codex-dddjango-web/` 대응 6파일의 전체 diff. 정본 커맨드·4역할·implementation-ui reference이며 reference는 byte 미러, 역할은 플랫폼 형식을 유지한 의미 미러다.
- 기존 backend 2.18.2→2.18.3 봉인 재발행으로 `workspace/eval/ab/T2-0b-manifest.json`, `workspace/design/2026-08-20-ontology-t2-0b-design.md`의 기계 사실도 바뀌었다. 실제 backend runtime 변경은 없다.

실행 근거(위 eval 폴더 기준): README.md, candidate-hashes.json, verification/result.json 및 final-verify.log, micro/results.md와 final-audit.json 및 필요한 개별 verdict, role-g0-return.md, role-coordinator-decision.md/role-dispatch.md, role-browser-app/handoff.md와 verification.json/capture-comparisons.json, role-review/report.md 및 독립 관찰. 실행 중 초기 실패와 안전한 도구 전환은 execution-notes.md에 있다. 계획 체크박스의 최종 상태/진단의 현재 상태는 리뷰 후 실제 완료 사실로 정리할 예정이다.

검토할 것:
1. 기존 강한 지침을 무의미하게 반복한 것이 아니라 실제 필수 반환·인계·상위 case 수용으로 연결됐는가. 미검증/matches 모순과 누락 focus가 통과할 구멍이 남았는가.
2. 원본의 관련 부모/자식 효과를 보존하면서 전 조상·속성·pseudo-state 의무나 불필요한 새 case/JSON을 강제하지 않는가. 등가 CSS·이미지 시안·정당한 미검증/위임·구조 green 경로가 유지되는가.
3. Claude/Codex 의미 정합, reference byte 일치, 역할 소유와 시안 정본을 훼손하지 않는가. graph-owned 직접 편집이나 불필요한 backend 변경이 없는가.
4. 실제 실행 근거가 주장과 맞는가. 기존 5/5와 후보 5/5를 개선율 증명으로 과장하지 않는가. 역할 checkpoint를 전체 native 성공으로, 2px 원본 복사를 3px 링 완전 정상화로 부풀리지 않는가.
5. 전체 변경 파일 목록을 확인하되 동일한 trial fixture/지침 복제는 hash 근거로 묶어 검토할 수 있다. 실제 민감 정보나 승인 범위 밖 파일 변경, 검증 로그/판정의 모순이 있는가.

중요한 미해결 발견만 Critical/Important로 구분해 근거 위치와 최소 수정 권고를 제시하고, Spec/Quality/ReadyToRelease를 판정한다. 사소한 표현 취향이나 인접 개선은 별도 선택사항으로 두고 범위를 늘리지 않는다. 이미 검증한 도구를 반복 실행할 필요는 없으며 새로운 우려가 있으면 필요한 최소 read-only 확인만 한다.

산출은 이 eval 폴더의 `final-review.md` 하나만 허용한다. 소스·계획·기존 증거는 수정하지 않는다. 새 CLI·권한 확장·자동 승인 옵션·전역 설정 변경은 사용하지 않는다. 기존 제한 도구만 사용하며 Serena/Graphify는 opt-in 부재로 사용하지 않는다. 독립 감수 report가 아직 기록 중이면 그 사실을 보고하고 원문이 제공된 뒤 최종 판정을 확정한다.
