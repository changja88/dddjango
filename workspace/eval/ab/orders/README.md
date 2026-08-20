# A/B 실런 발주 봉인 (T2-0b · 실런 전 동결)

> 이 폴더의 세 파일은 **실런 전에 동결**되고 `T2-0b-manifest.json` 의 `orders` 그룹으로 해시
> 봉인된다. 봉인 후 한 글자라도 바뀌면 이미 돈 런은 전부 무효다(t2-plan §2 T2-0b).

## 왜 발주를 문서로 봉인하는가

세 암의 차이는 **환경 스위치 둘**뿐이어야 한다(`DJR_LOOP_ENABLED`·`DJR_LOOP_SELECTOR`).
발주문이 암마다 조금씩 달라지면 그 순간 비교가 성립하지 않는데, 발주문이 사람의 기억이나
세션 히스토리에 있으면 «조금씩 다름»은 반드시 일어난다. 그래서 발주문·게이트 답·허용
도구를 파일로 못 박고, 실런은 이 파일을 **그대로 읽어** 투입한다.

## 인수 테스트의 경계 — 채점과 겹치지 않게

발주마다 **인수 테스트**(arm-independent 블랙박스)를 둔다. 인수는 «이 런이 채점 대상인가»만
가른다. 통과 못 한 런은 채점하지 않고 **판정 실패**로 기록한다(t2-plan §2 L-M #7).

인수에 **품질 판정을 넣지 않는다**. 예컨대 O-7 의 옛 합격 기준 (B)(역사적 결함 부재 grep —
빈혈 도메인·ORM 오명명 따위)은 인수에 넣지 않는다. 그건 처치가 개선하려는 바로 그 대상이고,
인수에 넣으면 처치가 잘 먹은 런만 채점되어 선택 편향이 된다. 인수는 **기능적 완성**만 본다:

| 인수가 보는 것 | 인수가 보지 않는 것(= 채점기 몫) |
|---|---|
| 기동하는가(`check`·migrate) | 구조·명명·계층 규율 |
| 요구한 동작을 하는가(테스트 green) | 결정적 검사기 위반 수(판정 스칼라) |
| 공개 표면이 약속대로인가(shape) | 루브릭 34차원·Q 차원 |

## 세 발주와 층

| 발주 | 층 | 왜 이 층인가 | 규모 |
|---|---|---|---|
| [O-7](O-7.md) | **밀착** | 409 거절+재고 차감 판정 = ddd §3.2 + ninja §6.2 직격 | 합성·판형 동결 |
| [O-4](O-4.md) | **혼합** | HTTP 표면은 있으나 파일럿 클러스터가 주 시험 대상이 아니다 | 705 LOC |
| [O-5](O-5.md) | **비밀착** | HTTP 표면 없음 — ninja 절 비적용, 클러스터가 주변부 | 3,848 LOC |

층 셋을 모두 두는 이유는 «파일럿 클러스터를 건드리는 발주에서만 효과가 난다»와 «어디서나
난다»를 가르기 위해서다. 비밀착 층은 통제군 역할을 한다 — 여기서도 효과가 크게 나오면 그건
클러스터 처치의 효과가 아니라 다른 무언가다.

## 런 시작 체크리스트 (세 암 공통 — 실행자 소유)

순서대로. 하나라도 빠지면 그 런은 **기술 실패**다.

```bash
# 1) 타깃 리셋 — 발주별 §리셋 앵커의 봉인 명령 그대로. 그 뒤 미추적 잔여 확인.
python3 workspace/tools/manifest_seal.py --tree-hash <타깃>     # 추적 해시 + 미추적 목록

# 2) 앞 런 산출물 제거 — .dddjango/ 는 미추적이라 git 리셋에 살아남는다
rm -rf <타깃>/.dddjango

# 3) 메모리 대피 확인 — 18런 전에 한 번 대피하고, 매 런 부재를 확인한다(삭제 아님)
ls ~/.claude/projects/<타깃 키>/memory 2>/dev/null && echo "대피 안 됨 — 중단"

# 4) 봉인 대조 — 이 런이 봉인된 그 구현으로 도는가
python3 workspace/tools/manifest_seal.py --check

# 5) 암 영수증 — A암도 반드시 남긴다
DJR_LOOP_ENABLED=<off|on> DJR_LOOP_SELECTOR=<snapshot|sparql> \
DJR_EXPERIMENT_RUN_ID=t2ab-R<NN> \
  python3 <설치본 scripts>/regen_core.py --arm-receipt <산출물 폴더>/arm.json
```

**왜 영수증이 필요한가**: A암은 루프를 안 돌려 `injection.jsonl` 이 아예 생기지 않는다. 그러면
산출물만으로는 ⓐ A로 돌았다 ⓑ B인데 게이트가 green 이라 발화가 없었다 ⓒ B인데 조율자가
step 6′ 를 건너뛰었다 — 셋이 구별되지 않는다. 판정 의미는 각각 **정상·노출 0·프로토콜 위반**
으로 전혀 다르다.

**`--selector` 는 명시 인자다**. 기본값이 없으므로 환경변수도 플래그도 없으면 `exit 1` 로
중단한다 — 기본값을 두면 selector 가 안 잡힌 C암 런이 조용히 B 처치를 받고 정상 종료한다.

## 채점 (런 종료 후 — arm-blind)

```bash
python3 workspace/tools/ab_score.py <타깃> --anchor <라운드 앵커> \
  --run t2ab-R<NN> [--legacy-debt-file <봉인 빚>] --scripts <설치본 scripts> \
  --out <산출물 폴더>/score.json
python3 workspace/tools/collect_violations.py --from <타깃>/.dddjango/violations --run t2ab-R<NN>
```

채점기는 `--arm`·`--selector` 류 인자를 **거절**한다. 계수 규약은
`T2-0a-preregistration.md` §1.1 이 정본이다.

## 봉인 대상과 외부 의존

세 파일의 **문면**은 여기서 봉인된다. 다음 값은 **타깃 저장소 접근**이 있어야 측정되고,
`T2-0b-manifest.json` 의 `external_annex` 에 들어간다. 그 값들이 `PENDING` 인 동안
`manifest_seal.py --check` 는 red 이며 그것이 곧 **실런 금지**다.

- 타깃 저장소 경로·baseline commit
- 앵커 상태의 baseline 테스트 실측(green/red 수) — 인수의 «신규 red 0» 이 그 수를 기준으로 한다
- O-5 클린룸 리셋 앵커 실증 1회(리셋 명령·리셋 후 트리 해시)

측정 명령: `python3 workspace/tools/manifest_seal.py --measure-annex --targets <json>`
