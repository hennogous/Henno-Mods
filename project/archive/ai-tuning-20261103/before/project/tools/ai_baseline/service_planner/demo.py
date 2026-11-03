"""Reproducible policy comparison, not a native game or observed AI result."""
from dataclasses import asdict
import argparse,json
from pathlib import Path
from .policy import Budget,Candidate,Need,Planner


def scenarios():
    budget=Budget(600);planner=Planner()
    common=dict(player=1,city=10,plot=42,quarter='TAILORS',base=2,specialty=0,
                service='dockmaster',venue_ready=True,research_ready=True,ready_in_turns=10,
                confidence=.9,dependencies_owned_or_in_purchase=True,missing_tiles=(42,),purchase_plot=42,
                price=80,revealed=True,material_visible=True,potential_legal=True,native_purchasable=True,
                eligible_ai=True,native_projection_verified=True,customer_plot=100,observed_turn=60)
    out=[]
    for title,changes,needs in (
        ('Strong naval Service',{}, {'naval':Need(.95,.95,'scenario: observed naval production')}),
        ('General Quarter',{'service':None},{}),
        ('Weak agenda evidence',{}, {'naval':Need(.95,.4,'scenario: personality prior only')}),
        ('Culture Service missing Specialty',{'service':'stage_manager'}, {'culture':Need(1,.95,'scenario: culture focus')}),
        ('Owned Base-only naval Service',{'missing_tiles':(),'purchase_plot':None,'price':0,'current_legal':True},{'naval':Need(.95,.95,'scenario: naval production')}),
    ):
        c=Candidate(**(common|changes));d=planner.evaluate(c,needs,budget,60)
        out.append({'scenario':title,'action':d.action,'tier':d.tier,'price':c.price,
                    'max_price':d.max_price,'score':round(d.score,2),'reason':d.reason})
    return {'kind':'offline policy scenarios; not native outcomes','gold':600,'reserve':150,'results':out}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path);args=p.parse_args();result=scenarios()
    if args.output:args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
