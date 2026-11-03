"""One existing-save, zero-turn, one-city shadow geometry capture and cleanup."""
import json
import re
from pathlib import Path
from native_session_probe import parser, run
from full_game_controller.probe import write_json
from shadow_geometry import review


def preserve_candidate_stage(raw, out, label):
    partial = re.findall(r'CSC_SHADOW_CANDIDATES=([^\r\n]+)', raw)
    if len(partial) == 1:
        write_json(out/(label+'-candidate-stage.json'), json.loads(partial[0]))


def capture_raw(r, reader, out, label):
    try:
        raw = r.cmd(reader.read_text(encoding='utf-8'), 'PlotInfo', label, wait=30)
    except Exception as failure:
        preserve_candidate_stage(getattr(failure, 'text', ''), out, label)
        raise
    preserve_candidate_stage(raw, out, label)
    return raw


def main():
    p = parser()
    p.add_argument('--shadow-reader', type=Path, required=True)
    a = p.parse_args()
    previous = None

    def capture(r, out, label):
        nonlocal previous
        raw = capture_raw(r, a.shadow_reader, out, label)
        rows = re.findall(r'CSC_SHADOW_GEOMETRY=([^\r\n]+)', raw)
        if len(rows) != 1:
            raise RuntimeError('Missing/ambiguous native shadow marker; no extension')
        value = json.loads(rows[0])
        write_json(out/(label+'.json'), value)
        evidence = review(value, str(out/(label+'.json')))
        write_json(out/(label+'-review.json'), evidence)
        if previous is not None and value != previous:
            raise RuntimeError('Zero-turn shadow facts changed; preserve partial evidence')
        previous = value

    run(a, capture=capture, extra_pins=(a.shadow_reader, Path(__file__), Path(__file__).with_name('shadow_geometry.py')))
    evidence = json.loads((a.output/'shadow-final-review.json').read_text(encoding='utf-8'))
    write_json(a.output/'shadow-result.json', {k: evidence[k] for k in
        ('status', 'opportunity_count', 'native_accessor_positive', 'comparative_geometry_observed',
         'action_authorization', 'execution_readiness', 'limitations')})


if __name__ == '__main__':
    main()
