"""Preserve replayable generated source and concise native load evidence, no raw thinking."""
import hashlib
import json
from pathlib import Path
import re
import shutil

ROOT=Path('/tmp/dddjango-web-js-integration-20260905')
DEST=Path(__file__).resolve().parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def collect(lane):
    source=ROOT/lane
    target=DEST/lane
    target.mkdir(exist_ok=True)
    app=target/'app'
    app.mkdir(exist_ok=True)
    for name in ['web','host']:
        shutil.copytree(source/'app'/name,app/name,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    for name in ['manage.py','design.md','evaluation-requirements.md','evaluation-oracle.md']:
        shutil.copy2(source/'app'/name,app/name)
    records=[]
    for trace in sorted(source.glob('*.trace.jsonl')):
        label=trace.name.removesuffix('.trace.jsonl')
        record={'label':label,'trace_path':str(trace),'trace_sha256':digest(trace),'init':[],'reads':[],'writes':[]}
        for line in trace.read_text().splitlines():
            try: event=json.loads(line)
            except json.JSONDecodeError: continue
            if event.get('subtype')=='init':
                record['init'].append({key:event.get(key) for key in ['cwd','model','tools','permissionMode','plugins']})
            if event.get('type')=='assistant':
                for content in event.get('message',{}).get('content',[]):
                    if content.get('type')!='tool_use': continue
                    name=content.get('name');args=content.get('input',{})
                    if name=='Read': record['reads'].append({'tool':name,'path':args.get('file_path')})
                    if name in ['Write','Edit']: record['writes'].append({'tool':name,'path':args.get('file_path')})
            item=event.get('item',{})
            if event.get('type')=='item.completed' and item.get('type')=='command_execution':
                command=item.get('command','')
                if 'implementation-javascript' in command or ('SKILL.md' in command and ('cat ' in command or 'sed ' in command)):
                    record['reads'].append({'tool':'command_execution','command':command,'exit_code':item.get('exit_code')})
            if event.get('type')=='item.completed' and item.get('type')=='file_change':
                record['writes'].extend(item.get('changes',[]))
        for suffix in ['.command.json','.prompt.txt','.result.json','.final.md','.launcher.json','.stderr.txt']:
            artifact=source/(label+suffix)
            if artifact.exists(): shutil.copy2(artifact,target/artifact.name)
        records.append(record)
    (target/'native-load-evidence.json').write_text(json.dumps(records,indent=2,ensure_ascii=False))
    for artifact in source.iterdir():
        if artifact.is_file() and (artifact.name.startswith(('browser-','backstop-','host-','baseline-','architect-1-timeout','architect-output-path','design-review-1-source-proof')) or artifact.name=='browser-selectors.json'):
            shutil.copy2(artifact,target/artifact.name)
    manifest={str(p.relative_to(app)):digest(p) for p in sorted(app.rglob('*')) if p.is_file()}
    (target/'generated-source-hashes.json').write_text(json.dumps(manifest,indent=2))
    print(lane,'preserved',len(manifest),'source files and',len(records),'native invocation records')

if __name__=='__main__':
    import sys
    collect(sys.argv[1])
