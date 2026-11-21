'use strict';

// Read a repair's cached value and admission in a bounded checkpoint replay.
// The observer never changes a score, reservation, worker or native order.
// Windows Steam XP2 26595377. The host also verifies the loaded module hash.
const TERRAIN = 0x3de500;
const PROPOSAL = 0x3e0a10;
const LOCATION = 0x3e5010;
const FIND_RESERVATION = 0x4019d0;
const TERRAIN_RESERVATION_RETURN = 0x3de710;
const PROPOSAL_LOCATION_RETURN = 0x3e0a65;
const GAME_INSTANCE_SLOT = 0xb8aa68;
const GAME_TURN = 0xc0;
const CORE_SHA = '4de40abf7c739f53c1f3f825863ace84dc220e5a42d87620e56fceaf3fbd4dc8';
const LAYOUT = {
    city: 0x90, owner: 0xd8, id: 0xa8, preferredImprovement: 0x250,
    improvementTree: 0x430, treeId: 0xc, rows: 0x4c8, count: 0x4d8, stride: 0x78,
    x: 8, y: 12, scores: 0x30, reservation: 0x48, selectable: 0x54, owned: 0x5a,
    plotCoordinates: 0x28,
};
const memory = createStudyMemoryIO({ptr, findRangeByAddress: p => Process.findRangeByAddress(p)});
const records = [];
let armed = false;
let installed = false;
let outstanding = 0;
let fault = null;

function read(p, offset, type) {
    const result = memory.read(p.toString(), offset, type);
    if (result.error) throw Error(result.error);
    return result.value;
}

function add(record) {
    if (records.length >= 256) throw Error('Repair admission observation exceeded its budget');
    records.push(record);
}

function init(spec, scope) {
    const normalize = path => path.replace(/\\/g, '/').toLowerCase();
    const core = Process.enumerateModules().find(module => normalize(module.path) === normalize(spec.path));
    if (installed || Process.platform !== 'windows' || Process.arch !== 'x64' ||
        !core || core.size !== spec.image_size || spec.sha256 !== CORE_SHA ||
        ![scope.player, scope.city, scope.x, scope.y, scope.improvement].every(n => Number.isInteger(n) && n >= 0) ||
        scope.player < 1 || scope.player >= 64 || scope.improvement >= 256)
        throw Error('Expected a verified Windows repair replay scope');
    const address = rva => core.base.add(rva);
    for (const [rva, expected] of [
        [TERRAIN, '48894c2408535657415541574883ec70488b8190000000488bd98b88d8000000'],
        [PROPOSAL, '4c8bdc574881ec10010000488b8130040000488bf983780cff0f85f301000048'],
        [LOCATION, '44884c242048894c2408415541574883ec684c63ea458bf84183fdff750b33c0'],
        [TERRAIN_RESERVATION_RETURN, '4885c00f85ee0000'],
    ]) {
        const actual = Array.from(new Uint8Array(address(rva).readByteArray(expected.length / 2)),
            byte => byte.toString(16).padStart(2, '0')).join('');
        if (actual !== expected) throw Error(`Repair observer fingerprint at ${rva.toString(16)}`);
    }
    for (const [returnRva, callee] of [[PROPOSAL_LOCATION_RETURN, LOCATION], [TERRAIN_RESERVATION_RETURN, FIND_RESERVATION]]) {
        const pc = address(returnRva);
        if (pc.sub(5).readU8() !== 0xe8 || !pc.add(pc.sub(4).readS32()).equals(address(callee)))
            throw Error(`Repair observer call at ${returnRva.toString(16)}`);
    }

    const l = LAYOUT;
    const turn = () => read(read(address(GAME_INSTANCE_SLOT), 0, 'ptr'), GAME_TURN, 'i32');
    if (turn() !== scope.turn) throw Error('Repair observer clock differs from the checkpoint');
    const matches = build => {
        const city = read(build, l.city, 'ptr');
        return read(city, l.owner, 'i32') === scope.player && read(city, l.id, 'i32') === scope.city;
    };
    const coordinates = row => [read(row, l.x, 'i32'), read(row, l.y, 'i32')];
    const findRow = (build, x, y) => {
        const count = read(build, l.count, 'u32');
        if (count > 37) throw Error(`Unexpected repair plot count ${count}`);
        const rows = ptr(read(build, l.rows, 'ptr'));
        for (let i = 0; i < count; i++) {
            const row = rows.add(i * l.stride);
            const [rx, ry] = coordinates(row);
            if (rx === x && ry === y) return row;
        }
        return null;
    };
    const score = (row, type) => row && read(read(row, l.scores, 'ptr'), type * 4, 'i32');
    const slot = build => read(read(build, l.improvementTree, 'ptr'), l.treeId, 'i32');
    const site = build => {
        const row = findRow(build, scope.x, scope.y);
        return row && {q8: score(row, scope.improvement), selectable: !!read(row, l.selectable, 'u8'),
            owned: !!read(row, l.owned, 'u8'), reservation: read(read(row, l.reservation, 'ptr'), 0, 'i32')};
    };
    const terrainFrames = new Map();
    function watch(rva, enter, leave) {
        Interceptor.attach(address(rva), {
            onEnter(args) {
                if (!armed) return;
                try { this.frame = enter(args[0], this, args); if (this.frame) outstanding++; }
                catch (error) { fault = String(error); armed = false; }
            },
            onLeave(result) {
                if (!this.frame) return;
                outstanding--;
                try { leave(this.frame, result); }
                catch (error) { fault = String(error); armed = false; }
            },
        });
    }
    watch(TERRAIN, (build, invocation) => {
        if (!matches(build)) return;
        const frame = {build, thread: invocation.threadId, reservationResolved: null};
        terrainFrames.set(frame.thread, frame);
        return frame;
    }, frame => {
        terrainFrames.delete(frame.thread);
        add({kind: 'terrain', turn: turn(), preferred: read(frame.build, l.preferredImprovement, 'i32'),
            site: site(frame.build), reservationResolved: frame.reservationResolved});
    });
    Interceptor.attach(address(TERRAIN_RESERVATION_RETURN), function () {
        const frame = terrainFrames.get(this.threadId);
        if (!armed || !frame) return;
        try {
            const [x, y] = coordinates(this.context.r15);
            if (x === scope.x && y === scope.y) frame.reservationResolved = !this.context.rax.isNull();
        } catch (error) { fault = String(error); armed = false; }
    });
    watch(PROPOSAL, build => matches(build) && {build, before: slot(build), site: site(build)}, frame => {
        add({kind: 'proposal', turn: turn(), before: frame.before, after: slot(frame.build), site: frame.site});
    });
    watch(LOCATION, (build, invocation, args) => {
        if (!invocation.returnAddress.equals(address(PROPOSAL_LOCATION_RETURN)) || !matches(build)) return;
        return {build, type: args[1].toInt32()};
    }, ({build, type}, result) => {
        let plot = null;
        if (!result.isNull()) {
            const span = memory.readBytes(result.toString(), l.plotCoordinates, 4);
            if (span.error) throw Error(span.error);
            const bytes = new DataView(Uint8Array.from(span.value).buffer);
            plot = [bytes.getInt16(0, true), bytes.getInt16(2, true)];
        }
        add({kind: 'location', turn: turn(), type, plot, q8: plot && score(findRow(build, ...plot), type)});
    });
    Interceptor.flush();
    installed = true;
    return true;
}

rpc.exports = {
    init,
    begin() { armed = installed && fault === null; },
    finish() { armed = false; return {records, outstanding, fault}; },
};
