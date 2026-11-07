'use strict';

// Diagnostic only. The contract's native Update reads the building forecast
// and uses its own archived value setter. Change that one input so the game
// still validates and ranks the offer, then chooses and executes production.
const REPAIR_BUILDING_PRESENT_VALUE = 0x3e7e50;
const REPAIR_CONTRACT_VALUE_RETURN = 0x3fa635;
const REPAIR_BUILDING_VALUE_ENTRY = '48895c240848896c2410488974241857';
const MAX_REPAIR_TEST_FLOOR = 1 << 23;

function installMillRepairBid(api, bid) {
    const {address, observe, read, caller, target, cityOf, contract, add, scope, currentBoundary, queuePass} = api;
    if (!Number.isInteger(bid.id) || bid.id <= 0 ||
        !Number.isInteger(bid.boundary) || bid.boundary <= 0 ||
        !Number.isInteger(bid.expectedQ8) || bid.expectedQ8 <= 0 ||
        !Number.isInteger(bid.floorQ8) || bid.floorQ8 <= bid.expectedQ8 || bid.floorQ8 > MAX_REPAIR_TEST_FLOOR)
        throw Error('Expected one bounded, identified repair test');

    const entry = address(REPAIR_BUILDING_PRESENT_VALUE);
    const prefix = Array.from(new Uint8Array(entry.readByteArray(REPAIR_BUILDING_VALUE_ENTRY.length / 2)),
        value => value.toString(16).padStart(2, '0')).join('');
    const end = address(REPAIR_CONTRACT_VALUE_RETURN);
    if (prefix !== REPAIR_BUILDING_VALUE_ENTRY || end.sub(5).readU8() !== 0xe8 ||
        !end.add(end.sub(4).readS32()).equals(entry))
        throw Error('Building contract forecast fingerprint changed');

    let written = false;
    observe(REPAIR_BUILDING_PRESENT_VALUE, (args, invocation) => {
        if (written || currentBoundary() !== bid.boundary || caller(invocation) !== REPAIR_CONTRACT_VALUE_RETURN ||
            args[2].toInt32() !== scope.mill || !target(cityOf(args[0]))) return;
        const pass = queuePass.get(invocation.threadId);
        if (pass === undefined) return;
        // The verified Update caller preserves its contract object in RDI
        // while invoking the four-argument building PresentValueOf overload.
        const offer = contract(invocation.context.rdi);
        if (offer.id !== bid.id || offer.status !== 3 || offer.building !== scope.mill ||
            offer.unit !== -1 || offer.district !== -1) return;
        return {out: args[1], offer, pass};
    }, ({out, offer, pass}, result) => {
        if (!result.equals(out)) throw Error('Unexpected building forecast output');
        const before = read(result, 0, 'i32');
        if (Math.max(before, offer.q8) !== bid.expectedQ8)
            throw Error('Repair forecast differs from the matched control');
        const range = Process.findRangeByAddress(out);
        if (!range || !range.protection.includes('w') ||
            out.add(3).compare(range.base.add(range.size)) >= 0)
            throw Error('Unwritable building forecast output');
        out.writeS32(bid.floorQ8);
        if (read(out, 0, 'i32') !== bid.floorQ8) throw Error('Building forecast floor did not stick');
        written = true;
        add({kind: 'repair-bid', pass, offer, before, after: bid.floorQ8});
    });
}
