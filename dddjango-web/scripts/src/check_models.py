# MD — 모델 선언 형태 2종. 게이트: added 모델 파일.
#
# *왜 결정적 백스톱인가*: 엔티티·VO·애그리거트 루트·State의 선언 형태
# (`@dataclass(frozen=True, slots=True, kw_only=True)` + 직파싱 `from_json` 클래스메서드 하나)는
# architecture-ddd §3·architecture-state §3가 *필수 형태*로 규정한다 — 수기 가변 클래스·
# 조용한 기본값(`.get`)·try/except 복구·수기 타입 리더는 그 계약 위반이며 "형태"로 결정 판별된다.
# 누락·타입 불일치는 그대로 예외로 올라가 safe_api_call 이 정규화한다.
#
# 거짓양성 차단: added 한정(레거시 면책) + enum/exception.py 제외 + 모델 스코프 파일만.
# 형태 판별은 표준 `ast`(주석·문자열 자동 배제) — 구문 오류 파일은 py_compile 기준선의 몫이라 건너뛴다.
# 허용(architecture-ddd §3): enum 의 `Enum(값)` 매핑 · VO 의 `from_api(...)` 커스텀 변환과 그 안의 parse-raise ·
# 도메인 `*Exception`.
# (판형: dddart check_models.dart)

from __future__ import annotations

import ast
from typing import List, Optional, Tuple

from .common import BackstopContext, Finding, base_name_of, ext_of, has_seg, parent_dir_of, segs_of

_RULE_DDD: str = '제1 규약 §9-2·architecture-ddd §3 직파싱(필수 형태)'
_RULE_STATE: str = 'architecture-state §3 — 항상 frozen dataclass State'
_FLAGS: Tuple[str, ...] = ('frozen', 'slots', 'kw_only')
_ALT_NAMES = {'from_dict', 'fromJson', 'from_response', 'parse_json'}  # from_api(커스텀 변환)는 허용


def _is_entity_or_vo(f: str) -> bool:
    return has_seg(f, 'domain_layer') and parent_dir_of(f) in ('entity', 'value_object')


def _is_aggregate_root(f: str) -> bool:
    s: List[str] = segs_of(f)
    if 'domain_layer' not in s or s.index('domain_layer') != len(s) - 3:
        return False
    return base_name_of(f) == '%s.py' % s[-2]


def _is_state_file(f: str) -> bool:
    return has_seg(f, 'application_layer') and parent_dir_of(f) == 'state'


def _is_excluded(f: str) -> bool:
    return has_seg(f, 'enum') or base_name_of(f) in ('exception.py', '__init__.py')


def _dataclass_missing(cls: ast.ClassDef) -> Optional[List[str]]:
    """frozen dataclass 형태에서 빠진 것 — None 이면 형태 충족."""
    for d in cls.decorator_list:
        func = d.func if isinstance(d, ast.Call) else d
        name: str = func.id if isinstance(func, ast.Name) else (func.attr if isinstance(func, ast.Attribute) else '')
        if name != 'dataclass':
            continue
        kws = {k.arg: k.value for k in d.keywords} if isinstance(d, ast.Call) else {}
        missing: List[str] = [k for k in _FLAGS
                              if not (isinstance(kws.get(k), ast.Constant) and kws[k].value is True)]
        return missing or None
    return ['@dataclass']


def run_models(ctx: BackstopContext) -> List[Finding]:
    out: List[Finding] = []
    for f in ctx.files:
        if not ctx.is_added(f) or ext_of(f) != '.py' or _is_excluded(f):
            continue
        is_ent_vo: bool = _is_entity_or_vo(f)
        is_root: bool = _is_aggregate_root(f)
        is_state: bool = _is_state_file(f)
        if not (is_ent_vo or is_root or is_state):
            continue
        try:
            tree = ast.parse((ctx.web / f).read_text(encoding='utf-8', errors='replace'))
        except SyntaxError:
            continue
        classes: List[ast.ClassDef] = [n for n in tree.body if isinstance(n, ast.ClassDef)]
        if not classes:
            continue  # 클래스 선언 없음(별칭·상수만) → 비대상

        # ---- MD1: frozen dataclass 형태 (entity/VO/root/state 공통 — 합 타입 파일은 클래스마다)
        for cls in classes:
            missing: Optional[List[str]] = _dataclass_missing(cls)
            if missing:
                out.append(Finding('MD1', f, cls.lineno,
                    '모델 클래스 `%s` — `@dataclass(frozen=True, slots=True, kw_only=True)` 형태 아님(누락: %s) — '
                    '엔티티·VO·State는 불변 dataclass로 선언한다(수기 가변 클래스 금지)' % (cls.name, ', '.join(missing)),
                    _RULE_STATE if is_state else _RULE_DDD,
                    '`@dataclass(frozen=True, slots=True, kw_only=True)` 로 선언하고 변경은 `dataclasses.replace`, '
                    '합 타입은 클래스 여럿 + 파일명과 같은 별칭 `<Name> = A | B` 로 둔다(enum은 enum/ 의 Enum).'))

        # ---- MD2: 수기·관대 직렬화 (entity/VO/root만 — State는 from_json 없음)
        if is_state:
            continue
        signals: List[Tuple[int, str]] = []
        for node in ast.walk(tree):  # 수기 타입 리더는 파일 어디서든
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith('_read'):
                signals.append((node.lineno, '수기 타입 리더 `%s`' % node.name))
        for cls in classes:
            for item in cls.body:
                if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if item.name in _ALT_NAMES:
                    signals.append((item.lineno, '직렬화 진입 이름 `%s`(from_json 하나)' % item.name))
                if item.name != 'from_json':
                    continue
                if not any(isinstance(d, ast.Name) and d.id == 'classmethod' for d in item.decorator_list):
                    signals.append((item.lineno, '`from_json` 이 @classmethod 아님'))
                for node in ast.walk(item):  # from_json 안의 복구·기본값
                    if isinstance(node, ast.Try):
                        signals.append((node.lineno, 'from_json 안 try/except 복구'))
                    elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'get':
                        signals.append((node.lineno, 'from_json 안 `.get(` 조용한 기본값'))
        if signals:
            signals.sort()
            kinds: List[str] = []
            for _, k in signals:
                if k not in kinds:
                    kinds.append(k)
            out.append(Finding('MD2', f, signals[0][0],
                '수기·관대 직렬화 — %s — 직파싱은 `from_json(cls, data) -> Self` 클래스메서드 하나, '
                '누락·타입 불일치는 그대로 예외' % '·'.join(kinds),
                _RULE_DDD,
                '`data["key"]` 직접 접근으로 읽고 try/except·`.get` 기본값·`_read*` 리더를 제거한다'
                '(파싱 실패 정규화는 safe_api_call 의 몫).'))
    return out
