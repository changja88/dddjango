"""dddjango 표준 파일트리 — 정본의 기계 가독 사본 (데이터 모듈 · 게이트 아님).

정본은 저장소의 `docs/file_tree.html`(트리 140행)이고, 이 파일은 검사기 19종이
import 하는 유일한 트리 데이터다. **손으로 고치지 않는다** — 정본이 개정되면
`workspace/tools/tree_mirror_check.py --write` 가 이 파일을 다시 쓰고,
`--check` 가 «정본 ≡ 이 파일 ≡ houserules final.md 트리 블록» 삼중 동기를 지킨다.

칸의 유형은 셋뿐이다(제1원칙 · 명세 #491):
  fixed        고정 이름 — 부모가 있으면 반드시 있다(#488)
  placeholder  `<>` 첫 등장 — 그 개념이 실제로 생길 때 0개 이상(#489)
  reappear     `<>` 재등장 — 조상이 이미 연 낱말이라 값이 채워져 fixed 와 같다(#491)

swappable=True 는 «동명 폴더 승격» 허용 표기다(#490 교체형 실현 — 파일 칸이
`<이름>.py` ⇄ `<이름>/`(본체+`__init__.py`) 두 실현을 갖는다). 칸 유형이 아니라
실현 형태의 직교 속성이며, 값의 정본은 docs/file_tree.html 의 data-sw 다.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

SOURCE: str = "docs/file_tree.html"
SOURCE_SHA: str = "e0585441b2e6939d"  # 생성 시점 정본 sha256[:16] — 출처 표시(동기 판정은 행 비교로 한다)

Kind = Literal["fixed", "placeholder", "reappear"]


@dataclass(frozen=True)
class Row:
    r: int          # 정본의 data-r (파트 순서 — 명세 «자리»의 「트리 N행」이 이 번호다)
    depth: int
    name: str       # 리프 이름 — admin·templates 처럼 하위 경로를 품은 이름도 있다
    kind: Kind
    swappable: bool = False  # 동명 폴더 승격 허용 표기(#490 교체형 — 정본은 data-sw)


ROWS: tuple[Row, ...] = (
    Row(1, 0, 'application/<bounded_context>/', 'placeholder'),
    Row(2, 1, 'composition_root/', 'fixed'),
    Row(3, 2, 'dependency_wiring.py', 'fixed'),
    Row(4, 2, 'event_wiring.py', 'fixed'),
    Row(5, 1, 'published_event/', 'fixed'),
    Row(6, 2, '<event>.py', 'placeholder'),
    Row(7, 1, 'driving_layer/', 'fixed'),
    Row(8, 2, 'api/', 'fixed'),
    Row(9, 3, 'api_router.py', 'fixed'),
    Row(10, 3, 'bc_error_schema.py', 'fixed'),
    Row(11, 3, '<area>/', 'placeholder'),
    Row(12, 4, '<area>_controller.py', 'reappear', swappable=True),
    Row(13, 4, 'schema/', 'fixed'),
    Row(14, 5, 'schema_in.py', 'fixed', swappable=True),
    Row(15, 5, 'schema_out.py', 'fixed', swappable=True),
    Row(16, 3, 'webhook/', 'fixed'),
    Row(17, 4, '<provider>/', 'placeholder'),
    Row(18, 5, '<provider>_controller.py', 'reappear', swappable=True),
    Row(19, 5, 'schema/', 'fixed'),
    Row(20, 6, 'schema_in.py', 'fixed', swappable=True),
    Row(21, 6, 'schema_out.py', 'fixed', swappable=True),
    Row(22, 2, 'open_host_service/', 'fixed'),
    Row(23, 3, '<service>/', 'placeholder'),
    Row(24, 4, '<service>_service.py', 'reappear', swappable=True),
    Row(25, 4, 'contract/', 'fixed'),
    Row(26, 5, 'request/', 'fixed'),
    Row(27, 6, '<request>_request.py', 'placeholder'),
    Row(28, 5, 'response/', 'fixed'),
    Row(29, 6, '<response>_response.py', 'placeholder'),
    Row(30, 5, 'exception/', 'fixed'),
    Row(31, 6, '<service>_published_error.py', 'reappear'),
    Row(32, 6, '<exception>_exception.py', 'placeholder'),
    Row(33, 2, 'cron_job/', 'fixed'),
    Row(34, 3, '<job>_cron_job.py', 'placeholder'),
    Row(35, 2, 'event_subscription/', 'fixed'),
    Row(36, 3, 'event_router.py', 'fixed'),
    Row(37, 3, '<event>_subscription.py', 'placeholder'),
    Row(38, 1, 'application_layer/', 'fixed'),
    Row(39, 2, '<area>/', 'placeholder'),
    Row(40, 3, '<use_case>/', 'placeholder'),
    Row(41, 4, '<use_case>_use_case.py', 'reappear', swappable=True),
    Row(42, 4, '<use_case>_command.py', 'reappear'),
    Row(43, 4, '<use_case>_query.py', 'reappear'),
    Row(44, 4, '<use_case>_result.py', 'reappear'),
    Row(45, 2, 'port/', 'fixed'),
    Row(46, 3, '<capability>/', 'placeholder'),
    Row(47, 4, '<capability>_port.py', 'reappear'),
    Row(48, 4, 'exception.py', 'fixed'),
    Row(49, 4, '<data>_out.py', 'placeholder'),
    Row(50, 4, '<data>_in.py', 'placeholder'),
    Row(51, 3, 'domain_bypass_query/', 'fixed'),
    Row(52, 4, '<capability>/', 'placeholder'),
    Row(53, 5, '<capability>_query.py', 'reappear'),
    Row(54, 5, '<data>_out.py', 'placeholder'),
    Row(55, 5, '<data>_in.py', 'placeholder'),
    Row(56, 5, 'exception.py', 'fixed'),
    Row(57, 3, 'unit_of_work/', 'fixed'),
    Row(58, 4, '<boundary>_unit_of_work.py', 'placeholder'),
    Row(59, 1, 'domain_layer/', 'fixed'),
    Row(60, 2, '<aggregate>/', 'placeholder'),
    Row(61, 3, '<aggregate>.py', 'reappear', swappable=True),
    Row(62, 3, 'entity/', 'fixed'),
    Row(63, 4, '<entity>.py', 'placeholder'),
    Row(64, 3, 'value_object/', 'fixed'),
    Row(65, 4, '<value_object>.py', 'placeholder'),
    Row(66, 3, 'event/', 'fixed'),
    Row(67, 4, '<event>.py', 'placeholder'),
    Row(68, 3, '<aggregate>_repository.py', 'reappear'),
    Row(69, 3, 'exception/', 'fixed'),
    Row(70, 4, '<exception>.py', 'placeholder'),
    Row(71, 2, 'shared_value_object/', 'fixed'),
    Row(72, 3, '<value_object>.py', 'placeholder'),
    Row(73, 2, 'domain_service/', 'fixed'),
    Row(74, 3, '<domain_service>.py', 'placeholder', swappable=True),
    Row(75, 1, 'driven_layer/', 'fixed'),
    Row(76, 2, 'django_<bounded_context>/', 'reappear'),
    Row(77, 3, 'apps.py', 'fixed'),
    Row(78, 3, 'models/', 'fixed'),
    Row(79, 4, '<entity>_model.py', 'placeholder'),
    Row(80, 3, 'migrations/', 'fixed'),
    Row(81, 4, '<migration>.py', 'placeholder'),
    Row(82, 3, 'admin/', 'fixed'),
    Row(83, 4, '<entity>/', 'placeholder'),
    Row(84, 5, 'panel.py', 'fixed'),
    Row(85, 5, 'form/<form>_form.py', 'placeholder'),
    Row(86, 5, 'feature/<feature>.py', 'placeholder'),
    Row(87, 3, 'templates/admin/<bounded_context>/<page>.html', 'placeholder'),
    Row(88, 3, 'templates/<bounded_context>/<capability>/<template>.html', 'placeholder'),
    Row(89, 2, 'adapter/', 'fixed'),
    Row(90, 3, 'persistence/', 'fixed'),
    Row(91, 4, 'repository/', 'fixed'),
    Row(92, 5, '<aggregate>_repository.py', 'placeholder', swappable=True),
    Row(93, 4, 'domain_bypass_query/', 'fixed'),
    Row(94, 5, '<capability>_query.py', 'placeholder', swappable=True),
    Row(95, 4, 'unit_of_work/', 'fixed'),
    Row(96, 5, '<boundary>_unit_of_work.py', 'placeholder', swappable=True),
    Row(97, 3, 'anticorruption_layer/', 'fixed'),
    Row(98, 4, '<other_bounded_context>/', 'placeholder'),
    Row(99, 5, '<capability>_adapter.py', 'placeholder', swappable=True),
    Row(100, 3, 'external_system/', 'fixed'),
    Row(101, 4, '<system>/', 'placeholder'),
    Row(102, 5, '<capability>_adapter.py', 'placeholder', swappable=True),
    Row(103, 3, '<capability>/', 'placeholder'),
    Row(104, 4, '<technology>_adapter.py', 'placeholder', swappable=True),
    Row(105, 1, 'test/', 'fixed'),
    Row(106, 2, 'unit/', 'fixed'),
    Row(107, 2, 'integration/', 'fixed'),
    Row(108, 2, 'e2e/', 'fixed'),
    Row(109, 2, 'factories/', 'fixed'),
    Row(110, 2, 'fake/', 'fixed'),
    Row(111, 3, '<declaration>.py', 'placeholder'),
    Row(112, 0, 'framework/', 'fixed'),
    Row(113, 1, 'broker/', 'fixed'),
    Row(114, 2, 'internal/', 'fixed'),
    Row(115, 3, 'internal_broker_port.py', 'fixed'),
    Row(116, 3, 'internal_broker.py', 'fixed'),
    Row(117, 2, 'external/', 'fixed'),
    Row(118, 3, 'external_broker_port.py', 'fixed'),
    Row(119, 3, 'external_broker.py', 'fixed'),
    Row(120, 1, '<capability>/', 'placeholder'),
    Row(121, 2, '<capability>_port.py', 'reappear'),
    Row(122, 2, 'exception.py', 'fixed'),
    Row(123, 2, '<data>_out.py', 'placeholder'),
    Row(124, 2, '<data>_in.py', 'placeholder'),
    Row(125, 2, '<technology>_adapter.py', 'placeholder'),
    Row(126, 1, '<technology>/', 'placeholder'),
    Row(127, 2, '<module>.py', 'placeholder'),
    Row(128, 1, 'pure/', 'fixed'),
    Row(129, 2, '<module>.py', 'placeholder'),
    Row(130, 1, 'test/', 'fixed'),
    Row(131, 2, '<module>.py', 'placeholder'),
    Row(132, 2, 'fake/', 'fixed'),
    Row(133, 3, '<declaration>.py', 'placeholder'),
    Row(134, 2, 'unit/', 'fixed'),
    Row(135, 0, '<project>/', 'placeholder'),
    Row(136, 1, 'api.py', 'fixed'),
    Row(137, 1, 'urls.py', 'fixed'),
    Row(138, 1, 'celery.py', 'fixed'),
    Row(139, 1, 'settings/', 'fixed'),
    Row(140, 2, '<environment>.py', 'placeholder'),
)


def children(parent: Row | None) -> tuple[Row, ...]:
    """parent 의 직계 자식 행. parent=None 이면 최상위 셋(BC·framework·<project>)."""
    if parent is None:
        return tuple(r for r in ROWS if r.depth == 0)
    idx = ROWS.index(parent)
    out: list[Row] = []
    for row in ROWS[idx + 1 :]:
        if row.depth <= parent.depth:
            break
        if row.depth == parent.depth + 1:
            out.append(row)
    return tuple(out)


def bc_root() -> Row:
    """`application/<bounded_context>/` — BC 서브트리의 뿌리(트리 1행)."""
    return ROWS[0]


def required_children(parent: Row) -> tuple[Row, ...]:
    """부모 인스턴스가 있으면 반드시 있어야 하는 자식(#488) — fixed·reappear."""
    return tuple(c for c in children(parent) if c.kind in ("fixed", "reappear"))


def is_dir(row: Row) -> bool:
    return row.name.endswith("/")


def concrete_name(row: Row, bindings: dict[str, str]) -> str:
    """`<토큰>` 을 채운 실제 이름 — 재등장 칸의 기대 이름을 만든다."""
    name = row.name
    for token, value in bindings.items():
        name = name.replace(f"<{token}>", value)
    return name
