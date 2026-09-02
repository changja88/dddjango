# 미니 설계 명세 — 마이그레이션 오배치 (red2 픽스처)

의도된 위반 1건: 마이그레이션 칸을 BC 직계 `application/billing/migrations/` 에 계획한다.
정형 Migration 스텁은 내용상 #593 을 통과하지만(수리 배치 2 ⑤ — «표면 제외»가 아니라 정형 렌더),
오배치 진탐은 **경로 기반** 검사기(#81 트리 밖 칸 · #325 BC 안 오배치)가 내용 불문으로 잡아야 한다 —
귀속 규칙 집합을 러너가 실측 고정한다(검출 집합 단조성 증거).

## 파일 계획

<!-- machine: file-plan -->
```paths
add	application/billing/migrations/0001_initial.py	# 의도 위반 — BC 직계 오배치
```

## 공개 심볼

<!-- machine: symbols -->
```symbols
```
