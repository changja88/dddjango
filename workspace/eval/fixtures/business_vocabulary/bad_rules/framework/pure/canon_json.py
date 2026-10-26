"""framework 쪽 동음 낱말(`FRAMEWORK_HOMONYMS` · 2026-08-25 #562 국소 목록에서 옮김) 경계 — 범용 직렬화 용어 `keys` 는 업무 어휘가 아니다.

BC 식별자(`get_successful_transaction_keys`)의 토큰화로 `keys` 가 BC 어휘에 들어와도 framework 쪽 합집합(`all_vocab`)은
이 낱말을 빼므로 pure/ 의 JSON object key 정렬 용어는 #562 · ⓓ#448 어느 쪽에도 서지 않는다(직렬화 정렬 실물 판형).
"""


def canonical_members(mapping: dict) -> list[str]:
    keys: list[str] = [key for key in mapping if isinstance(key, str)]
    keys.sort()
    return [f"{key}:{mapping[key]}" for key in keys]
