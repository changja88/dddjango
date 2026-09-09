"""Run canonical checks on a byte-identical all-new temporary validation copy."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT=Path(os.environ.get('DDDJANGO_WEB_EVAL_ROOT','/tmp/dddjango-web-js-integration-20260905'))
REPO=Path(os.environ.get('DDDJANGO_WEB_EVAL_REPO','/Users/hyun/Desktop/dddjango'))

def hashes(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((root/'web').rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}

def run(lane,label):
    source=ROOT/lane/'app'
    target=ROOT/lane/(label+'-validation-copy')
    target.mkdir()
    shutil.copytree(source/'web',target/'web',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    assert hashes(source)==hashes(target)
    subprocess.run(['git','-c','core.hooksPath=/dev/null','init','--quiet',str(target)],check=True,capture_output=True)
    # A real empty tree object marks every copied source as new; no legacy baseline or commit.
    tree=subprocess.run(['git','hash-object','-w','-t','tree','--stdin'],input='',text=True,cwd=target,capture_output=True,check=True).stdout.strip()
    cmd=[os.environ.get('DDDJANGO_WEB_EVAL_PYTHON','/tmp/dddjango-ui-js-20260905/venv/bin/python'),str(REPO/'dddjango-web/scripts/backstop.py'),str(target),'--all','--diff-base',tree]
    result=subprocess.run(cmd,capture_output=True,text=True)
    (ROOT/lane/(label+'.txt')).write_text(result.stdout+result.stderr)
    (ROOT/lane/(label+'.result.json')).write_text(json.dumps({'command':cmd,'exit_code':result.returncode,'baseline':'real empty Git tree; all generated web files treated as new; no commit','empty_tree':tree,'source_hashes':hashes(source),'copy_hashes':hashes(target)},indent=2))
    print(result.stdout+result.stderr)
    assert result.returncode==0
    assert '생략' not in result.stdout+result.stderr

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('lane');parser.add_argument('label');args=parser.parse_args();run(args.lane,args.label)
