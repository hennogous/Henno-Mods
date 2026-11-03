"""One read-only Gameplay transaction for metrics and durable observer prefixes.

Scheduled first-activation snapshots stay in CSCBASE.checkpoints. The separately
labelled current primary shares the exact capture used for current chain metrics.
No observers or checkpoint tables are reset at a same-process source handoff.
"""
from pathlib import Path
from .native_adapter import parse

def capture(r, root, write, turn):
    here=Path(__file__).parent
    chain=(here/'native_chain_metrics.lua').read_text(encoding='utf-8')
    # The maintained script's local s is the full, freshly captured census.
    assert 'local s=CSCBASE.capture()'in chain
    chain+='\nprint("CSC_CURRENT_PRIMARY="..json(s))\n'
    code='do\n'+(here/'native_quarter_sites.lua').read_text(encoding='utf-8')+'\nend\ndo\n'+chain+'\nend\nCSC_SERIES_RESEARCH.Export();CSC_BUILDERS.Export('+str(turn)+');'
    raw=r.cmd(code,'CSC_AdjacencyGameplay','boundary-bundle-'+str(turn))
    result={key:parse(raw,marker)for key,marker in (
        ('quarters','CSC_QUARTER_SITES'),('chain','CSC_CHAIN_METRICS'),
        ('primary','CSC_CURRENT_PRIMARY'),('research','CSC_SERIES_RESEARCH'),
        ('builders','CSC_BUILDERS_SNAPSHOT'))}
    for key in ('quarters','chain','primary','research'):
        assert result[key]['turn']==turn,('Boundary bundle clock mismatch',key)
    assert not result['chain']['errors']and not result['research']['errors']
    root=Path(root)
    for key,name in [('primary','failure-preserved-primary-current.json'),('research','failure-preserved-research.json'),('builders','failure-preserved-builders-current.json')]:write(root/name,result[key])
    write(root/'research-latest.json',result['research'])
    return result
