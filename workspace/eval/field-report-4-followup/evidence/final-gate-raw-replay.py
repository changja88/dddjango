from pathlib import Path
import ast,collections,hashlib,io,json,os,subprocess,sys,tarfile,tempfile
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'workspace/tools'))
import findings_count_matrix as fm
BASE=Path(__file__).parent
# Freeze the oracle so this diagnostic remains reproducible after the golden repair.
old_matrix=ast.parse((BASE/'final-gate-fix-before/workspace/tools/findings_count_matrix.py').read_text())
FROZEN_EXPECTED=ast.literal_eval(next(n.value for n in old_matrix.body if isinstance(n,ast.AnnAssign) and isinstance(n.target,ast.Name) and n.target.id=='EXPECTED'))
CHECKERS=['check-context-isolation.py','check-domain-model.py','check-port-adapter-pairing.py','check-public-surface-annotation.py','check-usecase-dto-placement.py','check-layer-skeleton.py']
VOLATILE={'run_id','record_id','ts'}
def stable(row):return {k:v for k,v in row.items() if k not in VOLATILE}
def counter(rows):return collections.Counter(json.dumps(stable(r),ensure_ascii=False,sort_keys=True) for r in rows)
results={}
with tempfile.TemporaryDirectory(prefix='final-gate-record-replay-') as td:
 scratch=Path(td);os.environ['DJR_VIOLATIONS_DIR']=str(scratch/'violations');os.environ['PYTHONDONTWRITEBYTECODE']='1'
 fixtures=[str(Path('workspace/eval/fixtures')/fm._LANE[s][0]) for s in CHECKERS]
 blob=subprocess.check_output(['git','archive','HEAD','dddjango/scripts',*fixtures],cwd=ROOT)
 with tarfile.open(fileobj=io.BytesIO(blob)) as archive:archive.extractall(scratch,filter='data')
 for script in CHECKERS:
  rel=Path('workspace/eval/fixtures')/fm._LANE[script][0]
  def inventory(root):return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
  assert inventory(scratch/rel)==inventory(ROOT/rel),('fixture changed',rel)
  row={}
  for label,scripts in [('HEAD',scratch/'dddjango/scripts'),('final',ROOT/'dddjango/scripts')]:
   code,stdout,records,issues=fm._measure_one(script,False,ROOT/rel,fm.DEFAULT_LANE,scripts)
   assert not issues,(script,label,issues)
   assert not fm._record_oracle(script,records),(script,label,'record oracle')
   result={'exit':code,'stdout':stdout,'records':records,'expected':[*fm._summarize(code,records),fm._fingerprint(records)]}
   (BASE/f'final-gate-{script}-{label}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
   row[label]=result
  assert tuple(row['HEAD']['expected'])==FROZEN_EXPECTED[script],(script,'HEAD mismatches stored expectation',row['HEAD']['expected'])
  removed=counter(row['HEAD']['records'])-counter(row['final']['records']);added=counter(row['final']['records'])-counter(row['HEAD']['records'])
  row['delta']={'removed':[json.loads(x) for x in removed.elements()],'added':[json.loads(x) for x in added.elements()]}
  results[script]={'HEAD':row['HEAD']['expected'],'final':row['final']['expected'],'delta':row['delta'],'fixture_unchanged':True}
  print(script, 'changed=',len(removed),len(added));print(json.dumps(row['delta'],ensure_ascii=False,indent=2))
(BASE/'final-gate-raw-delta.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print('Replay complete: 6 HEAD/current checker pairs; all fixture bytes identical; all HEAD rows match old goldens')
