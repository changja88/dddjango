"""Verify durable apps from a new isolated root, reusing the recorded dependencies."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ARTIFACTS=Path(__file__).resolve().parent
ROOT=Path('/tmp/dddjango-web-js-integration-20260905/isolated-replay')
PYTHON='/tmp/dddjango-ui-js-20260905/venv/bin/python'

def run(lane):
    destination=ROOT/lane
    destination.mkdir(parents=True)
    shutil.copytree(ARTIFACTS/lane/'app',destination/'app')
    selectors=ARTIFACTS/lane/'browser-selectors.json'
    if selectors.exists():shutil.copy2(selectors,destination/selectors.name)
    actual={str(p.relative_to(destination/'app')):hashlib.sha256(p.read_bytes()).hexdigest() for p in (destination/'app').rglob('*') if p.is_file()}
    expected=json.loads((ARTIFACTS/lane/'generated-source-hashes.json').read_text());assert actual==expected
    env=os.environ.copy();env.update(DDDJANGO_WEB_EVAL_ROOT=str(ROOT),DDDJANGO_WEB_EVAL_PYTHON=PYTHON,DDDJANGO_WEB_EVAL_REPO='/Users/hyun/Desktop/dddjango',PYTHONDONTWRITEBYTECODE='1')
    browser=[PYTHON,str(ARTIFACTS/('browser_harness.py' if lane=='codex' else 'browser_harness_claude.py'))]
    if lane=='codex':browser.append(lane)
    browser.append('replay-browser')
    backstop=[PYTHON,str(ARTIFACTS/'backstop_harness.py'),lane,'replay-backstop']
    records=[]
    for name,cmd in [('browser',browser),('backstop',backstop)]:
        result=subprocess.run(cmd,env=env,capture_output=True,text=True)
        (destination/(name+'.stdout.txt')).write_text(result.stdout);(destination/(name+'.stderr.txt')).write_text(result.stderr)
        records.append({'name':name,'command':cmd,'exit_code':result.returncode})
        assert result.returncode==0,(name,result.stderr)
    report={'lane':lane,'status':'PASS','source_copy_matches_durable_hashes':True,'file_count':len(actual),'replay_root':str(ROOT),'environment':{k:env[k] for k in ['DDDJANGO_WEB_EVAL_ROOT','DDDJANGO_WEB_EVAL_PYTHON','DDDJANGO_WEB_EVAL_REPO']},'commands':records}
    (destination/'replay-result.json').write_text(json.dumps(report,indent=2))
    target=ARTIFACTS/lane/'replay';target.mkdir(exist_ok=True)
    for path in destination.iterdir():
        if path.is_file():shutil.copy2(path,target/path.name)
    print(lane,'preserved-source replay PASS',len(actual),'files')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('lane',choices=['claude','codex']);run(parser.parse_args().lane)
