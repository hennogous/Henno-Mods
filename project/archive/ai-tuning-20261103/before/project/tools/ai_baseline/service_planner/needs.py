"""Conservative demand adapter: record observed signals rather than invent strategy flags."""
from .policy import Need


def from_observations(*, naval_unit_in_production=False, naval_war_need=0.0,
                      housing_shortfall=0.0, food_surplus=None, population=None,
                      culture_emphasis=None, religion_emphasis=None,
                      observed_native_priorities=None):
    needs={}
    if naval_unit_in_production:
        needs['naval']=Need(.95,.95,'observed naval unit currently in production')
    elif naval_war_need>0:
        needs['naval']=Need(min(1,naval_war_need),.8,'inferred coastal/naval war demand')
    if housing_shortfall>0:
        needs['housing']=Need(min(1,.7+.1*housing_shortfall),.95,'observed population/housing shortfall')
    if food_surplus is not None and population is not None and food_surplus>0 and population<=6:
        needs['growth']=Need(.85,.8,'inferred growth opportunity: low population and positive food surplus')
    if culture_emphasis is not None:
        needs['culture']=Need(culture_emphasis,.8,'inferred culture emphasis from observed investment')
    if religion_emphasis is not None:
        needs['religion']=Need(religion_emphasis,.8,'inferred religious emphasis from observed investment')
    for key,strength in (observed_native_priorities or {}).items():
        # Caller must have a verified observation; this module does not assert
        # that a generic active-strategy getter exists on the vanilla interface.
        if key not in {'naval','growth','housing','culture','religion'}:raise ValueError(key)
        needs[key]=Need(strength,1,'verified native priority supplied by driver')
    return needs
