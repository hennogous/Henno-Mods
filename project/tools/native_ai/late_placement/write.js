'use strict';

// The exact saved-world fixture is configured by the host. The ordinary
// calculation and its read-only receipt finish before the single-cell write.
const LATE_READERS = {
 GetBestDistrict: [0x3e4a50, '48894c24085355564154415541574883ec284c8bea488be9e873be3e00488bb5'],
 PresentValueOf: [0x3e7f40, '4d63d84c8bd2488bc14183fbff750833c9488bc2890ac34d85c9744d8b81d804'],
};

function createLatePlacement(module, io, study) {
 const plan = JSON.parse(JSON.stringify(study.latePlan));
 const { mode, plot, player, city, district, delta } = plan;
 const { mapWidth, mapHeight, districtCount } = study;
 if (!['baseline', 'pulse', 'correction'].includes(mode) || plot !== 1210 || player !== 1 || city !== 65536 ||
     district !== 36 || districtCount !== 38 || mapWidth !== 74 || mapHeight !== 46 ||
     !Number.isInteger(delta) || (mode === 'baseline' ? delta !== 0 :
        (mode === 'pulse' ? delta <= 0 || delta > 200000 : delta >= 0 || delta < -8192))) {
  throw Error('Unreviewed late placement scope');
 }
 const addresses = Object.entries(LATE_READERS).map(([name, [rva, expected]]) => {
  const address = module.base.add(rva);
  const bytes = Array.from(new Uint8Array(address.readByteArray(32)), b => b.toString(16).padStart(2, '0')).join('');
  if (bytes !== expected) throw Error('Late reader fingerprint ' + name);
  return address;
 });
 let enabled = false;
 let writes = 0;
 let active = 0;
 const records = [];
 const errors = [];
 const listeners = [];

 function read(address, offset, type) {
  const result = io.read(address, offset, type);
  if (result.error) throw Error(`${type} at ${offset}: ${result.error}`);
  return result.value;
 }
 function fault(error) {
  enabled = false;
  if (errors.length < 8) errors.push(String(error));
 }
 function record(value) {
  if (records.length >= 128) throw Error('Late trace capacity');
  records.push(value);
 }
 function matches(object) {
  const owner = read(object, 0x90, 'ptr');
  return read(owner, 0xd8, 'i32') === player && read(owner, 0xa8, 'i32') === city;
 }
 function findRow(object, x, y) {
  const count = read(object, 0x4d8, 'u32');
  if (count > 37 || x < 0 || x >= mapWidth || y < 0 || y >= mapHeight) throw Error('District row bounds');
  const rows = read(object, 0x4c8, 'ptr');
  for (let i = 0; i < count; i++) {
   const row = io.add(rows, i * 0x78);
   if (read(row, 8, 'i32') === x && read(row, 12, 'i32') === y) return row;
  }
  throw Error('District row absent');
 }
 function hook(address, enter, leave) {
  listeners.push(Interceptor.attach(address, {
   onEnter(args) {
    this.sample = null;
    if (!enabled) return;
    try {
     const object = args[0].toString();
     if (!matches(object)) return;
     this.sample = enter(object, args);
     if (this.sample) active++;
    } catch (error) { fault(error); }
   },
   onLeave(result) {
    if (!this.sample) return;
    active--;
    if (!enabled) return;
    try { leave(this.sample, result); } catch (error) { fault(error); }
   },
  }));
 }
 hook(addresses[0], (object, args) => ({object, out: args[1].toString()}), (sample, result) => {
  const selected = result.toInt32();
  if (selected === -1) return;
  if (selected < 0 || selected >= districtCount) throw Error('Winner definition bounds');
  const x = read(sample.out, 0, 'i32');
  const y = read(sample.out, 4, 'i32');
  const row = findRow(sample.object, x, y);
  const scores = read(row, 0x20, 'ptr');
  record({kind: 'winner', district: selected, plot: y * mapWidth + x, score: read(scores, selected * 4, 'i32'), writes});
 });
 hook(addresses[1], (object, args) => {
  if (args[2].toInt32() !== district || args[3].isNull()) return null;
  const tile = args[3];
  const span = Process.findRangeByAddress(tile.add(0x28));
  if (!span || !span.protection.includes('r') || tile.add(0x2b).compare(span.base.add(span.size)) >= 0)
   throw Error('Present value plot bounds');
  const x = tile.add(0x28).readS16();
  const y = tile.add(0x2a).readS16();
  return y * mapWidth + x === plot ? {out: args[1].toString()} : null;
 }, (sample, result) => {
  if (result.toString() !== sample.out) throw Error('Present value output pointer changed');
  record({kind: 'presentValue', district, plot, score: read(sample.out, 0, 'i32'), writes});
 });

 function calculated(calculation, object) {
  if (!enabled || calculation.leave.identity.player !== player || calculation.leave.identity.city !== city) return;
  if (calculation.callerRva !== '0x3e2941') throw Error('Unexpected aggregation caller');
  const first = calculation.entry.cache.districtRows.find(row => row.plot === plot);
  const last = calculation.leave.cache.districtRows.find(row => row.plot === plot);
  if (!first || !last || first.row < 1 || first.row !== last.row || !first.rawAliasesMutable || !last.rawAliasesMutable ||
      !first.eligible || !first.owned || !last.eligible || !last.owned || first.rawPointer !== last.rawPointer)
   throw Error('Unqualified district row or matrix alias');
  const row = findRow(object, last.x, last.y);
  if (read(read(row, 0x48, 'ptr'), 0, 'i32') !== -1) throw Error('Candidate has a live reservation');
  const before = first.mutableDistrictValues.find(item => item.district === district).value;
  const native = last.mutableDistrictValues.find(item => item.district === district).value;
  if (before <= 0 || native <= before) throw Error('Positive building uplift not observed');
  if (mode !== 'baseline') {
   if (before !== plan.expectedBefore || native !== plan.expectedNative)
    throw Error('Fresh calculation differs from matched baseline');
   for (const item of plan.expectedBuildings || []) {
    // The raw pointer can alias the prerequisite-chain vector. After the
    // original call, Wind's slot may contain Bakery and Café as well.
    const found = calculation.entry.cache.rawBuildingQ8.find(building => building.index === item.index);
    if (!found || found.value !== item.raw) throw Error('Raw building input differs from calibration');
   }
  }
  if (writes) throw Error('Second target calculation after single-write window');
  const final = native + delta;
  if (final <= 0 || final > 2147483647) throw Error('Late score bounds');
  const cell = ptr(last.rawPointer).add(district * 4);
  if (read(last.rawPointer, district * 4, 'i32') !== native) throw Error('Live score changed since snapshot');
  const region = Process.findRangeByAddress(cell);
  if (!region || !region.protection.includes('w') || cell.add(3).compare(region.base.add(region.size)) >= 0)
   throw Error('Score cell is not writable');
  record({kind: 'calculation', calculationId: calculation.id, district, plot, before, native, final, delta, row: last.row});
  if (delta) {
   cell.writeS32(final);
   writes++;
   if (cell.readS32() !== final) throw Error('Late score readback differs');
  }
 }
 return {
  start() { enabled = true; },
  stop() { enabled = false; },
  calculated(calculation, object) { try { calculated(calculation, object); } catch (error) { fault(error); } },
  snapshot() { return {mode, records, writes, active, errors, hooks: listeners.length}; },
 };
}

installStudyRuntime(createLatePlacement);
