from pathlib import Path
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound
from django.template import engines
from django.urls import path
from django.core.management import execute_from_command_line

ROOT = Path(__file__).resolve().parent
settings.configure(DEBUG=False, SECRET_KEY='temporary-evaluation-only', ALLOWED_HOSTS=['127.0.0.1'], ROOT_URLCONF=__name__, TEMPLATES=[{'BACKEND': 'django.template.backends.django.DjangoTemplates', 'OPTIONS': {'libraries': {'static': 'django.templatetags.static'}}}], STATIC_URL='/static/')
import django
django.setup()

def section(name):
    return f'''<section id="preview-{name}" data-file-preview><label>사진 <input type="file" accept="image/*" data-preview-input></label><img data-preview-image hidden alt="선택한 이미지 미리보기"><output data-preview-name></output><button type="button" data-preview-clear>선택 지우기</button></section>'''

PAGE = '''{% load static %}<!doctype html><html lang="ko"><meta charset="utf-8"><title>UI lifecycle evaluation</title><script src="{% static 'instrument.js' %}"></script><script defer src="{% static 'htmx.min.js' %}"></script><script defer src="{% static script %}"></script><main><div id="preview-list">{{ sections|safe }}</div><button id="replace-parent" hx-get="/fragment/parent" hx-target="#preview-list" hx-swap="innerHTML">Replace parent contents</button><button id="replace-root" hx-get="/fragment/root" hx-target="#preview-a" hx-swap="outerHTML">Replace root</button><button id="delete-root" hx-get="/fragment/delete" hx-target="#preview-a" hx-swap="delete">Delete root</button></main></html>'''

def index(request, mode):
    if mode == 'example':
        markup = (ROOT/'password.html').read_text()
        sections = markup.replace('<div ', '<div id="password-a" ', 1) + markup.replace('<div ', '<div id="password-b" ', 1)
        body = engines['django'].from_string(PAGE).render({'script':'password_visibility.js','sections':sections})
        return HttpResponse(body)
    if mode == 'holdout':
        sections = ''.join(f'<section id="copy-{n}" data-copy-feedback><input data-copy-text value="{n}"><button type="button" data-copy-button>복사</button><output data-copy-status role="status"></output></section>' for n in ('a','b'))
        body = engines['django'].from_string(PAGE).render({'script':'holdout/copy_feedback.js','sections':sections})
        return HttpResponse(body)
    if mode not in ('baseline', 'with-skill'): return HttpResponseNotFound()
    body = engines['django'].from_string(PAGE).render({'script': f'{mode}/file_preview.js', 'sections': section('a') + section('b')})
    return HttpResponse(body)

def fragment(request, kind):
    bodies = {'parent': section('a') + section('c'), 'root': section('a'), 'delete': '', 'note': ''}
    bodies.update({'password-root': (ROOT/'password.html').read_text().replace('<div ', '<div id="password-a" ', 1), 'password-button':'<button type="button" data-password-toggle aria-pressed="false" hidden>비밀번호 표시</button>', 'password-input':'<input type="password" autocomplete="current-password" data-password-input>', 'copy-root':'<section id="copy-a" data-copy-feedback><input data-copy-text value="new"><button type="button" data-copy-button>복사</button><output data-copy-status role="status"></output></section>', 'copy-input':'<input data-copy-text value="new-input">', 'copy-output':'<output data-copy-status role="status"></output>'})
    return HttpResponse(bodies.get(kind, ''))

def static(request, asset):
    file = (ROOT / asset).resolve()
    if not file.is_relative_to(ROOT) or not file.is_file(): return HttpResponseNotFound()
    return HttpResponse(file.read_bytes(), content_type='application/javascript')

urlpatterns = [path('<str:mode>/', index), path('fragment/<str:kind>', fragment), path('static/<path:asset>', static)]
if __name__ == '__main__': execute_from_command_line(['eval', 'runserver', '127.0.0.1:8771', '--noreload'])
