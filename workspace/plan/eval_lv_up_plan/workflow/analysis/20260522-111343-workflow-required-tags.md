수정 대상: evaluator
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

# workflow required coverage tags P4 분석

## 배경

workflow eval goal은 P4 기준으로 consent gate, actual subagent use, critical-path restraint, parallel ownership, responsibility assignment, direct-answer/meta-tail restraint, validation sharing, actual-subagent trace, cache sync report를 요구한다. 그러나 bucket pack validator의 workflow required tag set은 일부 이전 축만 필수로 본다.

## 원인

원인 분류는 `evaluator`다. Case와 answer가 P4 tag를 가지고 있어도 validator required set에 빠져 있으면 해당 case가 삭제되거나 tag가 사라져도 pack validator가 통과할 수 있다.

## 수정 판단

`REQUIRED_COVERAGE_TAGS["workflow"]`에 P4 목적을 대표하는 누락 tag를 추가한다. 이는 case 내용을 새로 확대하지 않고, 이미 존재하거나 이번 P4에서 추가한 case coverage를 validator가 요구하도록 만드는 변경이다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket workflow`
- `.venv/bin/python -B workspace/scripts/test_validate_eval_bucket_pack.py`
