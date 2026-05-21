# Templates

이 reference는 Django templates, inheritance, base templates, includes/components, template style을 다룬다. 정확한 component 또는 design-system convention은 대상 프로젝트를 따른다.

## Template Role

- Template은 presentation과 presentation-related branching만 담당한다.
- Domain rule, state transition, pricing, permission policy, complex data selection을 template에 두지 않는다.
- 렌더링 전에 view, selector, service, context builder에서 데이터를 준비한다.
- Optional field는 준비된 display value를 렌더링한다. `None`, blank, missing optional data의 domain fallback을 template이 직접 결정하지 않는다.
- Template filter/tag는 작은 presentation transform에만 사용하고 business decision에는 사용하지 않는다.

## Inheritance And Base Templates

- 프로젝트가 inheritance를 쓰면 shared document structure, common blocks, common assets, navigation을 base template에 둔다.
- `{% extends %}`는 첫 번째 비주석 template line에 둔다.
- Block은 명시적으로 이름 붙이고 `{% endblock content %}`처럼 block name으로 닫는다.
- Page-specific template은 page content와 local block에 집중한다.
- Page-specific CSS/JS를 생성하거나 수정하면 프로젝트 static convention에 따라 page template 또는 base-template block에서 include한다. Rendered detail template이 참조하지 않는 `detail.css` 같은 orphan page asset을 남기지 않는다.

## Includes And Components

- 같은 의미의 UI fragment가 반복되고 함께 바뀔 때 includes/components를 사용한다.
- Include context는 명시적으로 유지한다. 작은 변수 집합이면 broad implicit context에 의존하지 않는다.
- 모든 작은 snippet을 include로 만들지 않는다. 재사용이 clarity 또는 consistency를 높일 때만 분리한다.

## Template Style

- `{{ variable }}`와 `{% tag %}` 안에는 한 칸 공백을 둔다.
- 여러 template library를 load하면 알파벳순으로 둔다.
- Template indentation은 프로젝트 관례를 따른다. Django source style은 HTML template에 2칸 들여쓰기를 사용한다.
- Django staticfiles system으로 asset을 렌더링할 때는 `{% load static %}`를 사용한다.
- `|safe`와 `mark_safe()`는 값이 trusted이고 escaping이 의도적으로 처리된 경우에만 사용한다.
