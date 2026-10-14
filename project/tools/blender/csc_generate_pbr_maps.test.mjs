import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import sharp from 'sharp';

const tool=fileURLToPath(new URL('./csc_generate_pbr_maps.mjs',import.meta.url));
async function fixture(t,size=32) {
  const dir=await fs.mkdtemp(path.join(os.tmpdir(),'csc-pbr-'));
  t.after(()=>fs.rm(dir,{recursive:true,force:true}));
  const base=path.join(dir,'Test_B.png'), height=path.join(dir,'height.png');
  const rgb=Buffer.alloc(size*size*3);
  for(let y=0;y<size;y++)for(let x=0;x<size;x++) {
    const i=(y*size+x)*3;rgb[i]=x<size/2?240:20;rgb[i+1]=60;rgb[i+2]=20;
  }
  await sharp(rgb,{raw:{width:size,height:size,channels:3}}).png().toFile(base);
  const writeHeight=async f=>{
    const data=Buffer.alloc(size*size);
    for(let y=0;y<size;y++)for(let x=0;x<size;x++)data[y*size+x]=f(x,y);
    await sharp(data,{raw:{width:size,height:size,channels:1}}).png().toFile(height);
  };
  await writeHeight(()=>128);
  const run=(...args)=>spawnSync(process.execPath,[tool,'--base',base,'--height',height,'--overwrite',...args],{encoding:'utf8'});
  const read=async suffix=>sharp(path.join(dir,`Test_${suffix}.png`)).removeAlpha().raw().toBuffer();
  return {dir,base,height,size,writeHeight,run,read};
}

test('flat authored height ignores painted color and clamps material boundaries',async t=>{
  const f=await fixture(t);
  await f.writeHeight(x=>x<16?60:200);
  const regions=path.join(f.dir,'regions.json');
  await fs.writeFile(regions,JSON.stringify([
    {bounds:[0,0,.5,1],normal:1,gloss:.1,metalness:0},
    {bounds:[.5,0,1,1],normal:2,gloss:.7,metalness:1},
  ]));
  const result=f.run('--regions',regions);
  assert.equal(result.status,0,result.stderr);
  const n=await f.read('N'),g=await f.read('G'),m=await f.read('M');
  for(let i=0;i<n.length;i+=3)assert.deepEqual([...n.subarray(i,i+3)],[128,128,255]);
  assert.equal(g[0],26);assert.equal(g[31*3],179);
  assert.equal(m[0],0);assert.equal(m[31*3],255);
});

test('height ramps produce correct tangent signs and selectable green convention',async t=>{
  const f=await fixture(t);
  await f.writeHeight((x,y)=>40+x*2+y*2);
  assert.equal(f.run('--normal-y','opengl').status,0);
  const gl=await f.read('N');const i=(16*32+16)*3;
  assert.ok(gl[i]<128 && gl[i+1]>128 && gl[i+2]>240);
  assert.equal(f.run('--normal-y','directx').status,0);
  const dx=await f.read('N');
  assert.equal(dx[i],gl[i]);assert.ok(Math.abs(dx[i+1]+gl[i+1]-255)<=1);
});

test('reference resolution keeps relief stable through output resizing',async t=>{
  const f=await fixture(t,64);
  await f.writeHeight(x=>x*3);
  assert.equal(f.run('--reference-size','64','--normal-strength','8').status,0);
  const full=await f.read('N');const expected=full[(32*64+32)*3];
  assert.equal(f.run('--reference-size','64','--normal-strength','8','--size','32').status,0);
  const half=await f.read('N');
  assert.ok(Math.abs(half[(16*32+16)*3]-expected)<=2);
});

test('invalid height, region coverage and obsolete AO fail before writing maps',async t=>{
  const f=await fixture(t);
  assert.match(f.run('--ao').stderr,/baked from geometry/);
  const regions=path.join(f.dir,'regions.json');
  await fs.writeFile(regions,JSON.stringify([{bounds:[0,0,.5,1]}]));
  assert.match(f.run('--regions',regions).stderr,/cover the entire/);
  await sharp({create:{width:16,height:16,channels:3,background:'#888888'}}).png().toFile(f.height);
  assert.match(f.run().stderr,/dimensions must match/);
  await assert.rejects(fs.access(path.join(f.dir,'Test_N.png')));
});

test('physical relief matches analytic slopes on rectangular surfaces and survives resizing',async t=>{
  const f=await fixture(t,64);
  const regions=path.join(f.dir,'regions.json');
  await fs.writeFile(regions,JSON.stringify([{bounds:[0,0,1,1],normal:1}]));
  await f.writeHeight((x,y)=>20+x*2+y);
  const args=['--regions',regions,'--normal-strength','1','--normal-y','opengl',
    '--height-scale','1','--surface-size','2,1'];
  assert.equal(f.run(...args).status,0);
  const full=await f.read('N');const i=(32*64+32)*3;
  const slope=64/255, length=Math.sqrt(1+2*slope*slope);
  const expected=[-slope/length,slope/length,1/length].map(v=>Math.round((v*.5+.5)*255));
  assert.deepEqual([...full.subarray(i,i+3)],expected);
  assert.equal(f.run(...args,'--size','32').status,0);
  const half=await f.read('N');const j=(16*32+16)*3;
  for(let c=0;c<3;c++)assert.ok(Math.abs(half[j+c]-expected[c])<=2);
});

test('painted scalar maps override regions without treating dark paint as metal',async t=>{
  const f=await fixture(t);
  const g=path.join(f.dir,'gloss.png'),m=path.join(f.dir,'metal.png');
  const rgb=Buffer.alloc(32*32*3);
  for(let y=0;y<32;y++)for(let x=0;x<32;x++) {
    const i=(y*32+x)*3;rgb[i]=x<16?40:190;rgb[i+1]=255;rgb[i+2]=0;
  }
  await sharp(rgb,{raw:{width:32,height:32,channels:3}}).png().toFile(g);
  const metal=Buffer.alloc(32*32);
  for(let y=10;y<20;y++)for(let x=10;x<20;x++)metal[y*32+x]=220;
  await sharp(metal,{raw:{width:32,height:32,channels:1}}).png().toFile(m);
  assert.equal(f.run('--gloss-map',g,'--metalness-map',m,'--gloss-bias','.1').status,0);
  const gm=await f.read('G'),mm=await f.read('M');
  assert.equal(gm[0],66);assert.equal(gm[31*3],216);
  assert.equal(mm[(15*32+15)*3],220);assert.equal(mm[31*3],0);
});

test('physical parameters and scalar-map alignment fail before writing',async t=>{
  const f=await fixture(t);
  for(const args of [ ['--height-scale','1'], ['--surface-size','1,1'],
    ['--height-scale','1','--surface-size','0,1'],
    ['--height-scale','1','--surface-size','1,1','--reference-size','32'] ]) {
    assert.notEqual(f.run(...args).status,0);
  }
  const g=path.join(f.dir,'bad.png');
  await sharp({create:{width:16,height:16,channels:3,background:'#888'}}).png().toFile(g);
  assert.match(f.run('--gloss-map',g).stderr,/Gloss map dimensions must match/);
  assert.match(f.run('--metalness-map',g).stderr,/Metalness map dimensions must match/);
  await assert.rejects(fs.access(path.join(f.dir,'Test_N.png')));
});
