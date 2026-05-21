# Static Assets

이 reference는 Django static file organization, CSS/JS placement, collectstatic/manifest concern, asset verification을 다룬다. 기존 asset pipeline이 있으면 그 convention을 따른다.

## Organization

- 프로젝트가 `app/static/app_name/...` 구조를 쓰면 app-specific asset을 app 가까이에 둔다.
- Shared design-system 또는 global asset은 프로젝트의 established shared static location에 둔다.
- CSS/JS file name은 지원하는 page 또는 component가 드러나게 짓는다.
- 프로젝트 pipeline이 기대하지 않는 generated build artifact를 source directory에 두지 않는다.

## Loading Assets

- Hardcoded static URL 대신 `{% load static %}`와 `{% static 'path/to/file.css' %}`를 사용한다.
- Page가 opt in해야 하는 CSS/JS include는 base-template block에 둔다.
- Page-specific CSS/JS를 생성하거나 수정하면 같은 변경에서 rendered template에 연결한다. Page가 asset을 필요로 하지 않으면 만들거나 수정하지 않는다.
- Inline script는 external file보다 더 명확할 정도로 작고 template-local일 때만 사용한다.
- Template에 embedded JavaScript를 넣더라도 domain data transformation을 섞지 않는다.

## Production Concerns

- `STATIC_URL`, `STATIC_ROOT`, `STATICFILES_DIRS`, storage backend, deployment pipeline을 존중한다.
- 프로젝트가 manifest/static hashing을 사용하면 asset reference가 Django static resolution을 거치게 한다.
- WhiteNoise, bundler, 다른 asset pipeline이 있으면 새 convention을 만들지 말고 기존 convention을 따른다.
- `collectstatic`은 deployment 또는 asset resolution과 관련 있을 때만 실행하거나 권장한다. 실행 여부는 완료 보고에 명시한다.

## Verification

- 참조한 static path가 존재하는지 확인한다.
- Page template이 필요한 CSS/JS를 duplicate 또는 stale reference 없이 load하는지 확인한다.
- 변경한 page-specific CSS/JS가 rendered page에서 참조되는지 확인한다. 참조되지 않는 변경 asset은 harmless extra가 아니라 unfinished work로 본다.
- Visible UI 변경은 가능한 경우 render test, screenshot, browser check 중 사용할 수 있는 증거로 확인한다.
- Render/browser check를 실행하지 않았으면 미실행으로 적는다.
