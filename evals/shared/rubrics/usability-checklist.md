# dddjango Usability Manual Review Checklist

수동 리뷰는 자동 점수로 잡기 어려운 실제 사용성을 5점 척도로 기록한다.
각 항목은 `0`에서 `5`까지 채점하고, 확신이 낮으면 `notes`에 근거를 남긴다.

## Score Fields

| Field | Label | 기준 |
| --- | --- | --- |
| `actionable` | Actionable | 사용자가 바로 적용 가능한 수준인가. 코드, 순서, 명령, 의사결정 기준이 충분한가. |
| `concise` | Concise | 필요한 내용을 유지하면서 불필요한 장황함을 피했는가. 정책 설명이 과하게 반복되지 않는가. |
| `realistic_file_layout` | Realistic Layout | 실행 가능한 Django/Ninja 문법인가. 파일 구조와 import가 현실적인가. migration, transaction, test 고려가 있는가. |
| `korean_quality` | Korean Quality | 한국어 요청에 자연스럽게 답하는가. 코드 식별자와 필수 영어 용어를 제외하고 설명이 한국어 중심인가. |

## Review Checklist

1. 실행 가능한 Django/Ninja 문법인가.
2. 파일 구조와 import가 현실적인가.
3. migration, transaction, test 고려가 있는가.
4. 한국어 요청에 자연스럽게 답하는가.
5. 정책 설명이 과하게 반복되지 않는가.
6. 사용자가 바로 적용 가능한 수준인가.

## Notes Rule

`notes`에는 점수의 근거를 짧게 적는다. 예:

```json
{
  "usability": {
    "actionable": 5,
    "concise": 4,
    "realistic_file_layout": 5,
    "korean_quality": 5,
    "notes": "바로 적용 가능"
  }
}
```
