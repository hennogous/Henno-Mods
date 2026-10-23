"""Recording cadence is independent of planner actions and economic receipts."""
from dataclasses import dataclass
from .boundary_bundle import capture

@dataclass(frozen=True)
class CaptureSchedule:
    mode: str='light'
    interval: int=25
    endpoint: int=250
    def __post_init__(self):
        assert self.mode in ('light','deep')and self.interval>0
    def due(self,turn):
        return self.mode=='deep' or turn==1 or turn==self.endpoint or turn%self.interval==0

def evaluate_boundary(adapter,experiment,turn,root,write,*,schedule=CaptureSchedule(),capture_bundle=capture):
    # Live Quarter facts and delta/treasury checks are planner inputs, not optional
    # telemetry. Purchase and foundation methods retain all exact receipts.
    adapter.collect(turn)
    if turn<schedule.endpoint:experiment.cycle(adapter,turn)
    if not schedule.due(turn):return None
    # One post-action census only; no full before/after export on purchase turns.
    bundle=capture_bundle(adapter.r,root,write,turn)
    adapter.record_chain_metrics(turn,value=bundle['chain'])
    return bundle
