"""⑤-2 B MINOR-1 — architecture-api-final s022-5.2/b7 앵커·어휘 in-place(Expression 무신설) + prefLabel R-3467 어휘.
실행: cd /Users/hyun/Desktop/dddjango && .venv/bin/python <this>  → gate → render --apply architecture-api-final → LEDGER → srcmirror → corpus --write → rulepack
"""
import sys
sys.path.insert(0, "/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/d31bf8ef-f45e-4609-badc-3add1039bdb0/scratchpad/fr3/impl")
import ontlib as L
from ontlib import DJR, S, Literal
from rdflib.namespace import SKOS

p, g = L.load("rules/architecture-api-final.ttl")
b7 = S("dddjango/skills/architecture-api/references/final.md/s022-5.2/b7")
L.replace_in(g, b7, "오류 본문의 union 은 각 오류 schema 가 고정 `code` 로 자기 판별되므로 이 요구의 대상이 아니다(§6 에러 프로필)",
             "오류 본문의 union 은 각 오류 schema 가 고정 공개 식별자(code 프로필의 `<Bc>ErrorCode` 값 · RFC 9457 의 `type`)로 자기 판별되므로 이 요구의 대상이 아니다(§5.4 에러 프로필)")
w = DJR["R-3467"]; old = next(g.objects(w, SKOS.prefLabel)); assert "고정 code 로 자기 판별" in str(old)
g.remove((w, SKOS.prefLabel, old)); g.add((w, SKOS.prefLabel, Literal(str(old).replace("고정 code 로 자기 판별", "고정 공개 식별자(ErrorCode 값·RFC 9457 type)로 자기 판별"), lang="ko")))
L.save(p, g); print("architecture-api-final b7 in-place · R-3467 prefLabel")
