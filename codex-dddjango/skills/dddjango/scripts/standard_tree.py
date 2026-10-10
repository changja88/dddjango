"""dddjango 표준 파일트리 — 정본의 기계 가독 사본 (데이터 모듈 · 게이트 아님).

정본은 저장소의 `docs/file_tree.html`(트리 171행)이고, 이 파일은 검사기 19종이
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
SOURCE_SHA: str = "b10137679cc22962"  # 생성 시점 정본 sha256[:16] — 출처 표시(동기 판정은 행 비교로 한다)

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
    Row(5, 2, 'wiring_material.py', 'fixed'),
    Row(6, 1, 'published_event/', 'fixed'),
    Row(7, 2, '<event>.py', 'placeholder'),
    Row(8, 1, 'driving_layer/', 'fixed'),
    Row(9, 2, 'api/', 'fixed'),
    Row(10, 3, 'api_router.py', 'fixed'),
    Row(11, 3, 'bc_error_schema.py', 'fixed'),
    Row(12, 3, '<area>/', 'placeholder'),
    Row(13, 4, '<area>_controller.py', 'reappear', swappable=True),
    Row(14, 4, 'schema/', 'fixed'),
    Row(15, 5, 'schema_in.py', 'fixed', swappable=True),
    Row(16, 5, 'schema_out.py', 'fixed', swappable=True),
    Row(17, 3, 'webhook/', 'fixed'),
    Row(18, 4, '<provider>/', 'placeholder'),
    Row(19, 5, '<provider>_controller.py', 'reappear', swappable=True),
    Row(20, 5, 'schema/', 'fixed'),
    Row(21, 6, 'schema_in.py', 'fixed', swappable=True),
    Row(22, 6, 'schema_out.py', 'fixed', swappable=True),
    Row(23, 2, 'open_host_service/', 'fixed'),
    Row(24, 3, '<service>/', 'placeholder'),
    Row(25, 4, '<service>_service.py', 'reappear', swappable=True),
    Row(26, 4, 'contract/', 'fixed'),
    Row(27, 5, 'request/', 'fixed'),
    Row(28, 6, '<request>_request.py', 'placeholder'),
    Row(29, 5, 'response/', 'fixed'),
    Row(30, 6, '<response>_response.py', 'placeholder'),
    Row(31, 5, 'exception/', 'fixed'),
    Row(32, 6, '<service>_published_error.py', 'reappear'),
    Row(33, 6, '<exception>_exception.py', 'placeholder'),
    Row(34, 2, 'cron_job/', 'fixed'),
    Row(35, 3, '<job>_cron_job.py', 'placeholder'),
    Row(36, 2, 'event_subscription/', 'fixed'),
    Row(37, 3, 'event_router.py', 'fixed'),
    Row(38, 3, '<event>_subscription.py', 'placeholder'),
    Row(39, 1, 'application_layer/', 'fixed'),
    Row(40, 2, '<area>/', 'placeholder'),
    Row(41, 3, '<use_case>/', 'placeholder'),
    Row(42, 4, '<use_case>_use_case.py', 'reappear', swappable=True),
    Row(43, 4, '<use_case>_command.py', 'reappear'),
    Row(44, 4, '<use_case>_query.py', 'reappear'),
    Row(45, 4, '<use_case>_result.py', 'reappear'),
    Row(46, 2, 'port/', 'fixed'),
    Row(47, 3, '<capability>/', 'placeholder'),
    Row(48, 4, '<capability>_port.py', 'reappear'),
    Row(49, 4, 'exception.py', 'fixed'),
    Row(50, 4, '<data>_out.py', 'placeholder'),
    Row(51, 4, '<data>_in.py', 'placeholder'),
    Row(52, 3, 'domain_bypass_query/', 'fixed'),
    Row(53, 4, '<capability>/', 'placeholder'),
    Row(54, 5, '<capability>_query.py', 'reappear'),
    Row(55, 5, '<data>_out.py', 'placeholder'),
    Row(56, 5, '<data>_in.py', 'placeholder'),
    Row(57, 5, 'exception.py', 'fixed'),
    Row(58, 3, 'unit_of_work/', 'fixed'),
    Row(59, 4, '<boundary>_unit_of_work.py', 'placeholder'),
    Row(60, 1, 'domain_layer/', 'fixed'),
    Row(61, 2, '<aggregate>/', 'placeholder'),
    Row(62, 3, '<aggregate>.py', 'reappear', swappable=True),
    Row(63, 3, 'entity/', 'fixed'),
    Row(64, 4, '<entity>.py', 'placeholder'),
    Row(65, 3, 'value_object/', 'fixed'),
    Row(66, 4, '<value_object>.py', 'placeholder'),
    Row(67, 3, 'event/', 'fixed'),
    Row(68, 4, '<event>.py', 'placeholder'),
    Row(69, 3, '<aggregate>_repository.py', 'reappear'),
    Row(70, 3, 'exception/', 'fixed'),
    Row(71, 4, '<exception>.py', 'placeholder'),
    Row(72, 2, 'shared_value_object/', 'fixed'),
    Row(73, 3, '<value_object>.py', 'placeholder'),
    Row(74, 2, 'domain_service/', 'fixed'),
    Row(75, 3, '<domain_service>.py', 'placeholder', swappable=True),
    Row(76, 1, 'driven_layer/', 'fixed'),
    Row(77, 2, 'django_<bounded_context>/', 'reappear'),
    Row(78, 3, 'apps.py', 'fixed'),
    Row(79, 3, 'models/', 'fixed'),
    Row(80, 4, '<entity>_model.py', 'placeholder'),
    Row(81, 3, 'migrations/', 'fixed'),
    Row(82, 4, '<migration>.py', 'placeholder'),
    Row(83, 3, 'admin/', 'fixed'),
    Row(84, 4, '<entity>/', 'placeholder'),
    Row(85, 5, 'panel.py', 'fixed'),
    Row(86, 5, 'form/<form>_form.py', 'placeholder'),
    Row(87, 5, 'feature/<feature>.py', 'placeholder'),
    Row(88, 3, 'templates/admin/<bounded_context>/<page>.html', 'placeholder'),
    Row(89, 3, 'templates/<bounded_context>/<capability>/<template>.html', 'placeholder'),
    Row(90, 2, 'adapter/', 'fixed'),
    Row(91, 3, 'persistence/', 'fixed'),
    Row(92, 4, 'repository/', 'fixed'),
    Row(93, 5, '<aggregate>_repository.py', 'placeholder', swappable=True),
    Row(94, 4, 'domain_bypass_query/', 'fixed'),
    Row(95, 5, '<capability>_query.py', 'placeholder', swappable=True),
    Row(96, 4, 'unit_of_work/', 'fixed'),
    Row(97, 5, '<boundary>_unit_of_work.py', 'placeholder', swappable=True),
    Row(98, 3, 'anticorruption_layer/', 'fixed'),
    Row(99, 4, '<other_bounded_context>/', 'placeholder'),
    Row(100, 5, '<capability>_adapter/', 'placeholder'),
    Row(101, 6, 'adapter/', 'fixed'),
    Row(102, 7, '<implementation>_adapter.py', 'placeholder'),
    Row(103, 6, 'command/', 'fixed'),
    Row(104, 7, '<command>.py', 'placeholder'),
    Row(105, 6, 'constant/', 'fixed'),
    Row(106, 7, '<constant>.py', 'placeholder'),
    Row(107, 6, 'contract/', 'fixed'),
    Row(108, 7, '<contract>.py', 'placeholder'),
    Row(109, 6, 'schema/', 'fixed'),
    Row(110, 7, '<schema>.py', 'placeholder'),
    Row(111, 3, 'external_system/', 'fixed'),
    Row(112, 4, '<system>/', 'placeholder'),
    Row(113, 5, '<capability>_adapter/', 'placeholder'),
    Row(114, 6, 'adapter/', 'fixed'),
    Row(115, 7, '<implementation>_adapter.py', 'placeholder'),
    Row(116, 6, 'command/', 'fixed'),
    Row(117, 7, '<command>.py', 'placeholder'),
    Row(118, 6, 'constant/', 'fixed'),
    Row(119, 7, '<constant>.py', 'placeholder'),
    Row(120, 6, 'contract/', 'fixed'),
    Row(121, 7, '<contract>.py', 'placeholder'),
    Row(122, 6, 'schema/', 'fixed'),
    Row(123, 7, '<schema>.py', 'placeholder'),
    Row(124, 3, '<capability>/', 'placeholder'),
    Row(125, 4, '<technology>_adapter/', 'placeholder'),
    Row(126, 5, 'adapter/', 'fixed'),
    Row(127, 6, '<implementation>_adapter.py', 'placeholder'),
    Row(128, 5, 'command/', 'fixed'),
    Row(129, 6, '<command>.py', 'placeholder'),
    Row(130, 5, 'constant/', 'fixed'),
    Row(131, 6, '<constant>.py', 'placeholder'),
    Row(132, 5, 'contract/', 'fixed'),
    Row(133, 6, '<contract>.py', 'placeholder'),
    Row(134, 5, 'schema/', 'fixed'),
    Row(135, 6, '<schema>.py', 'placeholder'),
    Row(136, 1, 'test/', 'fixed'),
    Row(137, 2, 'unit/', 'fixed'),
    Row(138, 2, 'integration/', 'fixed'),
    Row(139, 2, 'e2e/', 'fixed'),
    Row(140, 2, 'factories/', 'fixed'),
    Row(141, 2, 'fake/', 'fixed'),
    Row(142, 3, '<declaration>.py', 'placeholder'),
    Row(143, 0, 'framework/', 'fixed'),
    Row(144, 1, 'broker/', 'fixed'),
    Row(145, 2, 'internal/', 'fixed'),
    Row(146, 3, 'internal_broker_port.py', 'fixed'),
    Row(147, 3, 'internal_broker.py', 'fixed'),
    Row(148, 2, 'external/', 'fixed'),
    Row(149, 3, 'external_broker_port.py', 'fixed'),
    Row(150, 3, 'external_broker.py', 'fixed'),
    Row(151, 1, '<capability>/', 'placeholder'),
    Row(152, 2, '<capability>_port.py', 'reappear'),
    Row(153, 2, 'exception.py', 'fixed'),
    Row(154, 2, '<data>_out.py', 'placeholder'),
    Row(155, 2, '<data>_in.py', 'placeholder'),
    Row(156, 2, '<technology>_adapter.py', 'placeholder'),
    Row(157, 1, '<technology>/', 'placeholder'),
    Row(158, 2, '<module>.py', 'placeholder'),
    Row(159, 1, 'pure/', 'fixed'),
    Row(160, 2, '<module>.py', 'placeholder'),
    Row(161, 1, 'test/', 'fixed'),
    Row(162, 2, '<module>.py', 'placeholder'),
    Row(163, 2, 'fake/', 'fixed'),
    Row(164, 3, '<declaration>.py', 'placeholder'),
    Row(165, 2, 'unit/', 'fixed'),
    Row(166, 0, '<project>/', 'placeholder'),
    Row(167, 1, 'api.py', 'fixed'),
    Row(168, 1, 'urls.py', 'fixed'),
    Row(169, 1, 'celery.py', 'fixed'),
    Row(170, 1, 'settings/', 'fixed'),
    Row(171, 2, '<environment>.py', 'placeholder'),
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
