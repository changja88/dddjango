"""#562 국소 stoplist(2026-08-25) 경계 — 범용 직렬화 용어 `keys` 는 업무 어휘가 아니다.

BC 식별자(`get_successful_transaction_keys`)의 토큰화로 `keys` 가 어휘 합집합에 들어와도
pure/ 의 JSON object key 정렬 용어와의 동음 충돌은 위반이 아니다(kkebi jcs.py 실물 판형).
"""


def canonical_members(mapping: dict) -> list[str]:
    keys: list[str] = [key for key in mapping if isinstance(key, str)]
    keys.sort()
    return [f"{key}:{mapping[key]}" for key in keys]
