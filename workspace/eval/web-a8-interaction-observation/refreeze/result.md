# 재동결(K4) 실측 — A8 «관계인» build 사본 (Task 11 Step 2)

- 실행일: 2026-09-14 · 실행 위치: scratch 사본 `scratchpad/task11/project/.dddjango-web/20260912-1640-web-related-persons/`(A8 원본 `~/.herdr/worktrees/spring_dream_server/a8/.dddjango-web/20260912-1640-web-related-persons/`은 무수정 — 실행 후 `diff -rq` 동일, 원본에 `_staging-*`·`refreeze-diff.json` 없음 확인).
- 도구: `dddjango-web/scripts/archive_design.py` sha256 `cc993cd0…`(작업 트리, Task 9·10 반영본).
- 기준 manifest = `design-input.json` `manifests[0]` = `source-manifest.json` sha256 `bddc54ec19c5…`(22파일 · entrypoint `관계인.dc.html` sha `cf2fe3486ca8…` · closure ok 13 · 밖 8 = json 2·PNG 4·readme 1·`설정.dc.html` 1).
- A8에는 `_raw-export`가 없다(manifest `source_root`가 부재 경로를 가리킴) — staging은 `design-ref` 사본으로 만들었다.

## run A — staging(BUILD 밖) + PNG 4 `--carried` → exit 4

```
cp -R BUILD/design-ref scratch/staging-a
python3 dddjango-web/scripts/archive_design.py scratch/staging-a/관계인.dc.html \
  --source-root scratch/staging-a \
  --out BUILD/_staging-20260914-194814/design-ref \
  --manifest BUILD/_staging-20260914-194814/source-manifest.json \
  --compare-build BUILD --compare-out BUILD/refreeze-diff.json \
  --carried _ds/…/assets/currency/wonbo.png --carried _ds/…/assets/logo.png \
  --carried _ds/…/assets/ornaments/gold-blossom.png --carried _ds/…/assets/saju/wood/00-element.png
```

- stdout: `[design-archive] 22 files preserved; 0 missing local dependencies; source_ready=false; original browser observations required`
- stderr: `[design-archive] compare: {'same': 18, 'changed': 0, 'added': 0, 'removed': 0, 'carried': 4}; exit=4`
- **exit 4**. `run-a-carried-png.json` = 그때의 `refreeze-diff.json`(base_manifest_sha256 `bddc54ec…`, carried 4행 모두 `carried_from` = 기준 manifest sha). staging manifest sha `6093d526…`, `carried_from` 행 4.

## run B — `_ds_bundle.js` 1바이트 변형 → exit 3

```
cp -R scratch/staging-a scratch/staging-b
printf ' ' >> scratch/staging-b/_ds/…/_ds_bundle.js     # 115341 → 115342 bytes, sha 3d86061b… → b76c390e…
python3 dddjango-web/scripts/archive_design.py scratch/staging-b/관계인.dc.html \
  --source-root scratch/staging-b \
  --out BUILD/_staging-20260914-194826/design-ref \
  --manifest BUILD/_staging-20260914-194826/source-manifest.json \
  --compare-build BUILD --compare-out BUILD/refreeze-diff.json \
  --carried <PNG 4 — run A와 동일>
```

- stderr: `[design-archive] compare: {'same': 17, 'changed': 1, 'added': 0, 'removed': 0, 'carried': 4}; exit=3`
- **exit 3**. changed 1행 = `_ds_bundle.js`(size 115342 · sha12 `b76c390e7d98`). `run-b-bundle-1byte.json`.

## run C — 이전 `design-ref`를 `BUILD/_staging-old/`에 두고 그 경로를 source로 → 자동 carried → exit 4

```
mkdir BUILD/_staging-old && cp -R BUILD/design-ref BUILD/_staging-old/design-ref
python3 dddjango-web/scripts/archive_design.py BUILD/_staging-old/design-ref/관계인.dc.html \
  --source-root BUILD/_staging-old/design-ref \
  --out BUILD/_staging-20260914-194837/design-ref \
  --manifest BUILD/_staging-20260914-194837/source-manifest.json \
  --compare-build BUILD --compare-out BUILD/refreeze-diff.json
```

- stderr: `[design-archive] compare: {'same': 0, 'changed': 0, 'added': 0, 'removed': 0, 'carried': 22}; exit=4`
- **exit 4**. `--carried` 없이 22행 전부 `carried`(source가 다른 `BUILD/_staging-*` 아래 → 자동 carried), `carried_from` = `bddc54ec…`. staging manifest `carried_from` 행 22. `run-c-staging-old-auto.json`.

## 판정

| run | 기대 | 실측 | 일치 |
|---|---|---|---|
| A 동일 바이트 + PNG 4 명시 carried | exit 4 (same 18 · carried 4) | exit 4 (same 18 · carried 4) | ○ |
| B `_ds_bundle.js` 1바이트 | exit 3 (changed 1) | exit 3 (same 17 · changed 1 · carried 4) | ○ |
| C `BUILD/_staging-old` source | exit 4 (자동 carried) | exit 4 (carried 22) | ○ |

- 같은 바이트라도 «기준과 대조하지 않은» 파일은 same이 아니라 carried로 세고(run C), carried가 하나라도 있으면 exit 0이 아니다 — «재동결 = 원본 재획득»이 아니라는 사실이 exit로 드러난다.
- 세 run 모두 `_staging-<ts>` 새 폴더에 보관했고 BUILD의 `design-ref`·`source-manifest.json`·`design-input.json`은 건드리지 않았다(`refreeze-diff.json`만 run마다 덮어씀 — 각 run의 사본을 `run-*.json`으로 보존).
