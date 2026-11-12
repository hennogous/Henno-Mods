'use strict';

// DIAGNOSTIC ONLY, not shipping CSC policy or a finished CE API. Given freshly
// observed city->tree->purchase lineage and a measured debit, test whether a
// native acknowledgement releases the waiting construction decorator. This
// neither buys land nor bids for production. The native build path still must
// reserve, nominate, win and place the district after the decorator progresses.
//
// ABI/layout scope: XP2 reference324c51e9, text matching Steam092abfbb. Pure
// lookups52d00/5f090 (pool4c210) match TryReservePlot3ea040's ownership reads.
// UnitRequestContract::DistrictCreated3f8210 demonstrates tracked assignment
// 64a6d0(contract+a0,&int32Seven). That generic FAutoVariable assignment tracks
// archive dirtiness; it is not a semantic CompleteContract routine. Never write
// contract+b0 directly or erase the native handles ourselves.
function createPurchasedContractAcknowledgement({core,scope,read,fingerprint}) {
    if(scope.repairOwnedPurchase!==true||scope.observeLifecycle!==true||
        scope.observeExecution!==true||scope.observeLineage!==true||!Number.isInteger(scope.city))
        throw Error('Acknowledgement requires explicit repair and provenance scope');
    const MapLookupRva=0x52d00,PlotAttributesRva=0x5f090,TrackedAssignmentRva=0x64a6d0;
    fingerprint(MapLookupRva,'448b024181f8f1d8ffff0f8492000000448b4a044181f9f1d8ffff0f8481000000');
    fingerprint(PlotAttributesRva,'0fb7494ee977d1feff');
    fingerprint(0x4c210,'3b0d8252b100488b156b52b10073158bc1488d0c80803cca00488d04ca75054883c008c3488d4208c3');
    fingerprint(TrackedAssignmentRva,'48895c2418574883ec30488b4108');
    // The first two routines only read. Do not substitute EditPlot overloads:
    // those enter archive-edit bookkeeping. Native calls exist only in this
    // explicitly enabled diagnostic, never the default read-only observer.
    const lookupPlot=new NativeFunction(core.base.add(MapLookupRva),'pointer',['pointer','pointer']);
    const attributesOf=new NativeFunction(core.base.add(PlotAttributesRva),'pointer',['pointer']);
    // This leaf assignment calls only native archive/set helpers, never the
    // observed AI boundaries. Keep the JS lock during it; the caller reserves
    // its outcome receipt before the write. See Frida's NativeFunction options:
    // https://frida.re/docs/javascript-api/#nativefunction
    const assignTracked=new NativeFunction(core.base.add(TrackedAssignmentRva),'void',['pointer','pointer'],
        {abi:'win64',scheduling:'exclusive'});
    const coordinates=Memory.alloc(8),complete=Memory.alloc(4);
    complete.writeS32(7); // Frida-owned scratch, not a game object.
    const payments=new Map(),acknowledged=new Set();
    return {
        observeDebit(receipt) {
            if(receipt.player!==scope.player||receipt.city!==scope.city||!scope.plots.includes(receipt.plot)||
                receipt.deltaMatched!==true||receipt.measuredDeltaQ8>=0||
                receipt.measuredDeltaQ8!==receipt.deltaQ8||!Number.isInteger(receipt.contractId)||
                !receipt.contractPointer)return;
            if(payments.size>=36)throw Error('Acknowledgement payment capacity');
            payments.set(receipt.contractId,receipt);
        },
        tryAcknowledge(contract,binding,state,turn,beforeWrite) {
            if(!binding||binding.originCity!==scope.city||!binding.originCityPointer||
                state.contractStatus!==3||acknowledged.has(binding.contractId))return null;
            if(state.contractVtableRva!==0x9fa930||state.executeRva!==0x3f82c0||
                state.updateRva!==0x3fa260||state.eligibilityRva!==0x3fa880)
                throw Error('Acknowledgement contract dispatch differs from verified lifecycle');
            const payment=payments.get(binding.contractId);
            // This bounded experiment accepts only the payment just observed,
            // not a guessed history reconstructed from already-owned land.
            if(!payment||payment.contractPointer!==contract.toString()||
                payment.ownerControl!==binding.ownerControl||payment.rootTreeId!==binding.rootTreeId||
                payment.plot!==binding.plot||turn<payment.turn||turn>payment.turn+2)return null;
            const city=ptr(binding.originCityPointer);
            if(read(city,0xd8,'i32')!==scope.player||read(city,0xa8,'i32')!==binding.originCity)
                throw Error('Acknowledgement originating city identity changed');
            const game=ptr(read(core.base.add(0xb8aa68),0,'ptr'));
            if(game.isNull())return {acknowledged:false,reason:'no-current-game'};
            const map=ptr(read(game,0x248,'ptr'));
            if(map.isNull())return {acknowledged:false,reason:'no-current-map'};
            coordinates.writeS32(binding.x);coordinates.add(4).writeS32(binding.y);
            const plot=lookupPlot(map,coordinates);
            if(plot.isNull())return {acknowledged:false,reason:'no-current-plot'};
            const packed=read(plot,0x28,'i32');
            if(((packed<<16)>>16)!==binding.x||(packed>>16)!==binding.y)
                throw Error('Acknowledgement plot coordinates differ');
            const attributes=attributesOf(plot);
            if(attributes.isNull())return {acknowledged:false,reason:'no-current-attributes'};
            // The shared memory adapter supports u8, not i8. Convert the
            // signed owner explicitly so unowned255 becomes -1.
            const owner=(read(attributes,0x1c,'u8')<<24)>>24;
            const purchaseCity=read(attributes,0xc,'i32');
            if(owner!==scope.player||purchaseCity!==binding.originCity)
                return {acknowledged:false,reason:'ownership-mismatch',owner,purchaseCity};
            // The caller just revalidated the known contract's identity and
            // dispatch. Recheck its state after the pure lookups, before the
            // sole game write, and retain the ordinary decorator/handle path.
            if(read(contract,0xb0,'i32')!==3)throw Error('Acknowledgement state changed before assignment');
            if(typeof beforeWrite!=='function')throw Error('Acknowledgement requires reserved write journal');
            beforeWrite(); // The caller must reserve/log before the sole game write.
            assignTracked(contract.add(0xa0),complete);
            const after=read(contract,0xb0,'i32');
            if(after!==7)throw Error('Native tracked completion assignment did not land');
            acknowledged.add(binding.contractId);
            return {acknowledged:true,writeKind:'native-tracked-assignment',before:3,after,
                owner,purchaseCity,paymentTurn:payment.turn,measuredPaymentQ8:payment.measuredDeltaQ8};
        },
    };
}
