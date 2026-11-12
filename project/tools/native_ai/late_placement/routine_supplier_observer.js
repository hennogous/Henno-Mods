// Diagnostic only, read-only: connect the native improvement row to the one
// cached resource-purchase candidate and the routine buyer's actual funds.
// Reference XP2 SHA324c51e9, text-matched hotfix092abfbb. No native calls/writes.
// CityBuild::AnalyzeCityPlots3de990 takes CityBuild*; PurchasePlots458530 takes
// Economic*. Field identities come from those bodies and evaluator3e2aa0.
function observeRoutineSupplier({core,scope,read,fingerprint,emit,fail,turnNow,listeners,isFaulted=()=>false}) {
    let localFault=false;
    const originalFail=fail;
    fail=error=>{localFault=true;originalFail(error);};
    const AnalyzeCityPlots=0x3de990, PurchasePlots=0x458530;
    const CityBuildCity=0x90, CityBuildRows=0x4c8, CityBuildRowCount=0x4d8;
    const CityBuildImprovementCount=0x488, CachedPurchaseXY=0x238, RowSize=0x78;
    const CityId=0xa8, CityOwner=0xd8, CityBuild=0x1948;
    const PlayerId=0xd8;
    const EconomicPlayer=0x98, EconomicSavings=0x250;
    const PlayerCities=0x6d0, CitiesHead=0xd0, NodeCity=0, NodeNext=0x10;
    fingerprint(AnalyzeCityPlots,'48895c241848896c2420565741544155');
    fingerprint(PurchasePlots,'48895c242056574154415541574881ec');
    const identity=city=>({player:read(city,CityOwner,'i32'),city:read(city,CityId,'i32')});
    const matches=city=>{const k=identity(city);return k.player===scope.player&&k.city===scope.city;};
    const candidate=build=>({x:read(build,CachedPurchaseXY,'i32'),y:read(build,CachedPurchaseXY+4,'i32')});
    listeners.push(Interceptor.attach(core.base.add(AnalyzeCityPlots),{
        onEnter(args) {
            if(faulted())return;
            try {
                const city=ptr(read(args[0],CityBuildCity,'ptr'));
                if(matches(city))this.supplierBuild=args[0];
            }catch(error){fail(error);}
        },
        onLeave() {
            if(!this.supplierBuild||faulted())return;
            try {
                const build=this.supplierBuild, city=ptr(read(build,CityBuildCity,'ptr'));
                if(!matches(city))throw Error('Supplier analysis city changed');
                const count=read(build,CityBuildRowCount,'u32');
                const improvements=read(build,CityBuildImprovementCount,'u32');
                if(count>256||improvements>1024)throw Error('Supplier row bounds differ');
                const rows=ptr(read(build,CityBuildRows,'ptr')), frontier=[];
                for(let i=0;i<count;i++) {
                    const row=rows.add(i*RowSize), resource=read(row,0,'i32');
                    if(resource<0||read(row,0x57,'u8')===0)continue;
                    const x=read(row,8,'i32'),y=read(row,12,'i32');
                    if(x<0||x>=scope.width||y<0||y>=scope.height)throw Error('Supplier row coordinates differ');
                    const values=ptr(read(row,0x30,'ptr'));
                    let maximum=null,improvement=-1;
                    for(let k=0;k<improvements;k++) {
                        const value=read(values,k*4,'i32');
                        if(maximum===null||value>maximum){maximum=value;improvement=k;}
                    }
                    const plot=y*scope.width+x;
                    const scoresQ8=scope.plots.includes(plot)?
                        Array.from({length:improvements},(_,k)=>read(values,k*4,'i32')):undefined;
                    frontier.push({plot,resource,feature:read(row,4,'i32'),maximumQ8:maximum,improvement,scoresQ8});
                }
                emit({kind:'routine-candidate',turn:turnNow(),...identity(city),cached:candidate(build),frontier});
            }catch(error){fail(error);}
        }
    }));
    listeners.push(Interceptor.attach(core.base.add(PurchasePlots),{
        onEnter(args) {
            if(faulted())return;
            try {
                const player=ptr(read(args[0],EconomicPlayer,'ptr'));
                if(read(player,PlayerId,'i32')!==scope.player)return;
                const manager=ptr(read(player,PlayerCities,'ptr'));
                let node=ptr(read(manager,CitiesHead,'ptr'));const visited=new Set();
                while(!node.isNull()) {
                    const key=node.toString();
                    if(visited.has(key)||visited.size>=256)throw Error('Supplier city-list cycle/bound');
                    visited.add(key);
                    const city=ptr(read(node,NodeCity,'ptr'));
                    if(matches(city)) {
                        const savings=ptr(read(args[0],EconomicSavings,'ptr'));
                        const build=ptr(read(city,CityBuild,'ptr'));
                        // Raw Q8 balances at routine entry, not a fabricated
                        // admission receipt. This route uses strict C<P+S,
                        // floor(C/2)<P; quote and actual debit are separate.
                        emit({kind:'routine-savings',turn:turnNow(),...identity(city),cached:candidate(build),
                            slushQ8:read(savings,0,'i32'),plotFundQ8:read(savings,8,'i32')});
                        break;
                    }
                    node=ptr(read(node,NodeNext,'ptr'));
                }
            }catch(error){fail(error);}
        }
    }));
    // A local latch prevents an observer fault from generating further rows.
    // The enclosing observer still owns the authoritative fault and cleanup.
    function faulted(){return localFault||isFaulted();}
}
