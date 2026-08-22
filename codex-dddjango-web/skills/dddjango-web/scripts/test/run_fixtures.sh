#!/usr/bin/env bash
# dddjango-web 스크립트 자기 회귀 픽스처 러너 — fixtures_*.sh 글롭 전부 실행.
# (fixtures_backstop.sh 외에 fixtures_extract.sh·fixtures_contract.sh 등이 추가되면
#  존재하는 것만 자동으로 실행한다.)
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
FAILED=0
RAN=0

for fx in "$HERE"/fixtures_*.sh; do
  [ -e "$fx" ] || continue  # 글롭 미매치(픽스처 0개) 방어
  RAN=$((RAN+1))
  echo "== $(basename "$fx")"
  if ! bash "$fx"; then
    FAILED=$((FAILED+1))
  fi
  echo
done

if [ "$RAN" = 0 ]; then
  echo "run_fixtures: 실행할 fixtures_*.sh 없음"
  exit 1
fi
echo "run_fixtures: 픽스처 파일 ${RAN}개 실행, 실패 ${FAILED}개"
[ "$FAILED" = 0 ]
