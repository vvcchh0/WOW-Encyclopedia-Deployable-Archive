"""Root review of the data-bound prefix04 driver; never sends requests."""
import ast,hashlib,importlib.util,json,sys
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[3];B=R/'research/continuous-recovery-20261016';D=B/'network/gallery-prefix04';old=B/'network/gallery-prefix03/gallery_prefix_driver_v4.py';new=D/'gallery_prefix_driver_v4.py'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(old)=='3ae5d0655a0f8459107c059e2593737dde13effe2877ada99a41fa0a7f6e9ba2'
assert sha(new)=='22f45b6776944df8cdc36bab5231edc1f8eee9faf627dcb07b1af6523929af38'
def funcs(p):return {x.name:x for x in ast.parse(p.read_text()).body if isinstance(x,ast.FunctionDef)}
a,b=funcs(old),funcs(new);assert a.keys()==b.keys()
unchanged=[n for n in a if ast.dump(a[n])==ast.dump(b[n])];assert len(unchanged)==20
assert ast.dump(ast.parse(ast.unparse(a['request']).replace('GALLERYPREFIX03','GALLERYPREFIX04')))==ast.dump(ast.parse(ast.unparse(b['request'])))
oldloops=[x for x in a['execute'].body if isinstance(x,ast.For)];newloops=[x for x in b['execute'].body if isinstance(x,ast.For)];assert ast.dump(ast.Module(body=oldloops,type_ignores=[]))==ast.dump(ast.Module(body=newloops,type_ignores=[]))
s=importlib.util.spec_from_file_location('root_prefix04_review',new);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
plan,candidates,bindings=m.validate_inputs();f=m.fixture();assert f['all_passed'] and f['passed']==f['total']==15
assert len(candidates)==20 and m.MAX_ATTEMPTS==40 and m.WINDOW_SECONDS==900
assert m.MAX_ENTITY_BODY_BYTES==8*1024**2 and m.MAX_TOTAL_BODY_BYTES==64*1024**2
assert m.MIN_DISPATCH_SECONDS==5.25 and m.MIN_REQUEST_START_SECONDS==5 and m.DISK_FLOOR_BYTES==11005853696
receipt={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'network_requests':0,'driver_sha256':sha(new),'plan_sha256':sha(D/'plan.json'),'input_bindings_sha256':sha(D/'input-bindings.json'),'candidate_count':20,'starting_failure_tail':0,'historical_prefix03_failure_tail':5,'independently_executed_fixtures':15,'unchanged_functions':unchanged,'request_core_unchanged_except_raw_file_stem':True,'execute_candidate_loop_ast_unchanged':True,'index_only':True,'no_payload_replay':True}
out=B/'publication/root-prefix04-plan-acceptance.json';assert not out.exists();out.write_bytes((json.dumps(receipt,indent=2)+'\n').encode());print(json.dumps(receipt))
