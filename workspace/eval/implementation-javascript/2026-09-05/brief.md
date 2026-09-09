# 독립 UI 구현 과제

이 임시 평가 앱에서는 UI JavaScript 사용이 승인되어 있다. dddjango-web 플러그인 통합 작업이 아니다.
페이지에는 아래 마크업의 파일 미리보기 두 개가 있다. 각 input의 선택한 이미지를 같은 root의 img로 미리 보여주고, clear 버튼으로 해당 input·이미지·파일명 표시를 비운다. 파일명은 그대로 텍스트로 표시한다. 폼 제출이나 서버 업로드 처리는 하지 않는다. 이미지가 아닌 선택은 미리보기를 비우고 안내한다.

```html
<section data-file-preview>
  <label>사진 <input type="file" accept="image/*" data-preview-input></label>
  <img data-preview-image hidden alt="선택한 이미지 미리보기">
  <output data-preview-name></output>
  <button type="button" data-preview-clear>선택 지우기</button>
</section>
```

오래 열어 사용하는 Django/HTMX 화면이다. HTMX 2.0.8이 로드되어 있다. 전체 페이지 첫 진입과 HTMX 부분 교체에서 기능이 동작해야 한다. 초기에는 두 개, 나중에는 더 추가될 수 있다. 부모 innerHTML 교체, 위 section 자체 outerHTML 교체, 삭제가 일어날 수 있다. DOM·임시 브라우저 자원의 수명도 고려한다. 스크립트는 페이지에서 외부 파일로 한 번 로드한다. 로딩 방식은 선택해 보고한다. 네트워크 호출·서버 계약 변경·일반 JS 프레임워크는 필요 없다.

산출: 지정된 출력 폴더의 file_preview.js 하나(기능당 파일 하나), report.md(로딩 방식·구현 판단·실제 수행한 확인만). 프로젝트나 다른 평가 결과를 읽지 말고 이 요구만 사용한다. 평가자와 추가 대화 없이 완료한다.
