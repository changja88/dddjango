"""Native runtime role harness. Prompts go through stdin; no generated UI is seeded."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

REPO = Path('/Users/hyun/Desktop/dddjango')
ROOT = Path('/tmp/dddjango-web-js-integration-20260905')
PYTHON = Path('/tmp/dddjango-ui-js-20260905/venv/bin/python')

def setup(lane):
    app = ROOT / lane / 'app'
    app.mkdir(parents=True, exist_ok=True)
    files = {
        'manage.py': 'import os\nimport sys\nfrom django.core.management import execute_from_command_line\nos.environ.setdefault("DJANGO_SETTINGS_MODULE", "host.settings")\nexecute_from_command_line(sys.argv)\n',
        'host/__init__.py': '',
        'host/settings.py': 'from pathlib import Path\nBASE_DIR = Path(__file__).resolve().parent.parent\nSECRET_KEY = "isolated-evaluation-only"\nDEBUG = True\nALLOWED_HOSTS = ["127.0.0.1", "localhost", "testserver"]\nINSTALLED_APPS = ["django.contrib.staticfiles", "web.apps.WebConfig"]\nROOT_URLCONF = "host.urls"\nMIDDLEWARE = []\nTEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": [BASE_DIR / "web"], "APP_DIRS": True, "OPTIONS": {"context_processors": []}}]\nSTATIC_URL = "/static/"\nSTATICFILES_DIRS = [("web", BASE_DIR / "web/static"), ("design_system", BASE_DIR / "web/design_system")]\nDATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}\n',
        'host/urls.py': 'from django.http import HttpResponse\nfrom django.urls import include, path\ndef favicon(request):\n    return HttpResponse(status=204)\nurlpatterns = [path("favicon.ico", favicon), path("", include("web.urls"))]\n',
        'web/__init__.py': '',
        'web/apps.py': 'from django.apps import AppConfig\nclass WebConfig(AppConfig):\n    name: str = "web"\n',
        'web/urls.py': 'urlpatterns: list = []\n',
        'web/base/base.html': '{% load static %}\n<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{% block title %}Evaluation{% endblock %}</title><link rel="stylesheet" href="{% static \'design_system/foundation/tokens.css\' %}">{% block styles %}{% endblock %}<script defer src="{% static \'web/htmx/htmx.min.js\' %}"></script>{% block scripts %}{% endblock %}</head><body>{% block content %}{% endblock %}</body></html>\n',
        'web/design_system/foundation/tokens.css': ':root { --space-sm: 0.5rem; --space-md: 1rem; --space-lg: 2rem; --text-color: #202020; --surface-color: #ffffff; --error-color: #9f1239; --preview-size: 10rem; --font-body: system-ui, sans-serif; --line-body: 1.5; }\n',
        'web/design_system/foundation/motion.css': '',
    }
    for name, data in files.items():
        target = app / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(data)
    for name in ['design_system/component', 'static/css', 'static/js', 'static/htmx', 'static/images']:
        target = app / 'web' / name
        target.mkdir(parents=True, exist_ok=True)
        (target / '.gitkeep').touch()
    core = ROOT / 'htmx-2.0.10.min.js'
    assert hashlib.sha256(core.read_bytes()).hexdigest() == '71ea67185bfa8c98c39d31717c6fce5d852370fcdfd129db4543774d3145c0de'
    shutil.copy2(core, app / 'web/static/htmx/htmx.min.js')
    if lane == 'codex':
        shutil.copytree(REPO / 'codex-dddjango-web/skills', app / '.agents/skills', dirs_exist_ok=True)
    for name in ['evaluation-requirements.md', 'evaluation-oracle.md']:
        frozen = json.loads((ROOT / 'evaluation-input-hashes.json').read_text())
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == frozen[name]
        shutil.copy2(ROOT / name, app / name)
    baseline = subprocess.run([str(PYTHON), 'manage.py', 'check'], cwd=app, capture_output=True, text=True)
    (ROOT / lane / 'baseline-check.txt').write_text(baseline.stdout + baseline.stderr)
    assert baseline.returncode == 0
    return app

def run(lane, role, label, task):
    app = ROOT / lane / 'app'
    directory = ROOT / lane
    role_source = (REPO / 'dddjango-web/agents' / (role + '.md')) if lane == 'claude' else app / '.agents/skills' / ('dddjango-web-' + role) / 'SKILL.md'
    common = f'''You are the actual {role} role in a controlled integration evaluation. The Coordinator is this external harness. Use the current distribution role at {role_source}. Do not use an installed stale plugin cache. Read required knowledge from this distribution only. Do not spawn agents; this invocation is one isolated role. User authorizes this bounded evaluation and native role execution; do not ask new gate questions. Do not touch repository sources, global settings/config, Git, user profiles, dependencies or any files outside this app. Do not create production tests. Review roles return report in final output only, do not write files.\nRead evaluation-requirements.md and evaluation-oracle.md. Those were frozen before generation. This is static_only; OpenAPI and server-contract absent by approval, no business API consumption. No design-ref/assets/motion notes: native design authorized using existing design_system tokens. G0 area decision ① new lab area, one ui_lab screen concept. Existing host skeleton is complete and Django manage.py check baseline is zero issues. New lab/ui_lab skeleton generation flag ON. Host already includes web.urls, web app, TEMPLATES DIRS web root, staticfiles, and verified official HTMX2.0.10 at web/static/htmx/htmx.min.js (source https://raw.githubusercontent.com/bigskysoftware/htmx/v2.0.10/dist/htmx.min.js SHA25671ea67185bfa8c98c39d31717c6fce5d852370fcdfd129db4543774d3145c0de). base has generic styles/scripts/content blocks and external classic defer core. No existing screen conventions beyond skeleton. Author code only in web/; architect writes only design.md. Python with Django is on PATH. Independent Coordinator browser harness will execute behavior, so do not claim browser checks you have not run.\n'''
    correction = ROOT / 'host-correction.txt'
    if correction.exists():
        common += correction.read_text() + '\n'
    common += f'Absolute application root: {app.resolve()}. Authoritative design to read/write: {(app / "design.md").resolve()}. Coder implementation write boundary is exactly {(app / "web").resolve()}/. Never write an implementation under the source repository or durable evaluation harness directory. Relative paths in the task refer exclusively to this app. Knowledge-source reads from the specified distribution are authorized.\n'
    prompt = common + task
    if lane == 'codex':
        prompt = '$dddjango-web-' + role + '\n' + prompt
        cmd = ['codex', 'exec', '--ephemeral', '--skip-git-repo-check', '-C', str(app), '--sandbox', 'workspace-write', '-c', 'model_reasoning_effort="medium"', '--json', '--output-last-message', str(directory / (label + '.final.md')), '-']
    else:
        tools = 'Read,Grep,Glob' if 'review' in role else ('Read,Grep,Glob,Edit,Write' if 'architect' in role else 'Read,Grep,Glob,Edit,Write,Bash')
        cmd = ['claude', '-p', '--plugin-dir', str(REPO / 'dddjango-web'), '--agent', 'dddjango-web:' + role, '--model', 'claude-opus-5[1m]', '--effort', 'medium', '--output-format', 'stream-json', '--verbose', '--no-session-persistence', '--strict-mcp-config', '--no-chrome', '--setting-sources', '', '--permission-mode', 'acceptEdits', '--permission-prompts', 'none', '--allowedTools', tools, '--add-dir', str(REPO / 'dddjango-web')]
    (directory / (label + '.prompt.txt')).write_text(prompt)
    (directory / (label + '.command.json')).write_text(json.dumps(cmd, indent=2))
    env = os.environ.copy()
    env['PATH'] = str(PYTHON.parent) + os.pathsep + env['PATH']
    inherited_pwd = env.get('PWD')
    env['PWD'] = str(app.resolve())
    (directory / (label + '.launcher.json')).write_text(json.dumps({'subprocess_cwd':str(app.resolve()),'inherited_pwd':inherited_pwd,'child_pwd':env['PWD'],'role_source':str(role_source)},indent=2))
    started = time.time()
    with (directory / (label + '.trace.jsonl')).open('w') as out, (directory / (label + '.stderr.txt')).open('w') as err:
        result = subprocess.run(cmd, input=prompt, text=True, cwd=app, stdout=out, stderr=err, env=env)
    if lane == 'claude':
        for line in (directory / (label + '.trace.jsonl')).read_text().splitlines():
            try:
                item = json.loads(line)
                if item.get('type') == 'result':
                    (directory / (label + '.final.md')).write_text(item.get('result', json.dumps(item)))
            except json.JSONDecodeError:
                pass
    (directory / (label + '.result.json')).write_text(json.dumps({'exit_code': result.returncode, 'seconds': time.time()-started}, indent=2))
    print(lane, label, result.returncode, flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('lane', choices=['claude', 'codex'])
    parser.add_argument('role')
    parser.add_argument('label')
    parser.add_argument('task_file')
    parser.add_argument('--setup', action='store_true')
    args = parser.parse_args()
    if args.setup:
        setup(args.lane)
    run(args.lane, args.role, args.label, Path(args.task_file).read_text())
