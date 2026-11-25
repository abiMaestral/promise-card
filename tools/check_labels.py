"""Check every hand-label quote against the saved source text for its offer.
Reports quotes that are not found, so source text or label can be fixed before the model runs."""
import csv, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from promise_card.quote_check import quote_in
F=['total_cost','payment_timing','promise','conditions','terms_can_change','if_not_placed','refuse_offer','terms_elsewhere']
lab={r['offer_id']:r for r in csv.DictReader(open('data/labels.csv',encoding='utf-8'))}
tot=okt=0
gaps=[]
for oid,r in lab.items():
    if r.get('in_eval','yes').strip().lower()!='yes': print(f'{oid}: excluded'); continue
    docs=[d.strip() for d in r['doc_ids'].replace('+',' ').split()]
    texts=[Path(f'data/sources/{d}.txt') for d in docs]
    if not any(t.exists() for t in texts): print(f'{oid}: NO SOURCE TEXT ({", ".join(docs)})'); continue
    t='\n'.join(p.read_text(encoding='utf-8') for p in texts if p.exists())
    ok=miss=0; bad=[]
    for f in F:
        for q in [x.strip() for x in (r[f+'_quote'] or '').split('||') if x.strip()]:
            if quote_in(q,t): ok+=1
            else:
                miss+=1; bad.append(f'    {f}: {q[:100]}')
                if (oid,f) not in gaps: gaps.append((oid,f))
    tot+=ok+miss; okt+=ok
    print(f'{oid}: {ok}/{ok+miss} quotes found'); print('\n'.join(bad)) if bad else None
print(f'TOTAL {okt}/{tot}')
import json
Path('data/evidence_gaps.json').write_text(json.dumps([f'{o}.{f}' for o,f in gaps],indent=1))
print('fields with a label quote missing from saved evidence:',len(gaps))
