// Deterministic material masks for the inspected generated atlas layout.
import sharp from '../../project/tools/blender/node_modules/sharp/lib/index.js';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const out=path.join(path.dirname(fileURLToPath(import.meta.url)),'Textures');
const stem=path.join(out,'CSC_BLACKSMITH_Workshop');
const {data,info}=await sharp(stem+'_B.png').ensureAlpha().raw().toBuffer({resolveWithObject:true});
const G=Buffer.alloc(data.length),M=Buffer.alloc(data.length),E=Buffer.alloc(data.length);
for(let y=0;y<info.height;y++)for(let x=0;x<info.width;x++){
 const u=x/info.width,v=y/info.height,i=(y*info.width+x)*4;
 let gloss=v<.5?(u<.5?.22:.13):(u<.5?.22:.10),metal=0,emissive=false;
 if(u>=.5&&v>=.683){
   const col=Math.min(3,Math.floor((u-.5)*8));
   if(v<.816){
     gloss=[.46,.18,.09,.08][col];metal=col===0?.88:0;emissive=col===3;
   }else{gloss=[.06,.78,.22,.52][col];metal=col===3?.92:0;}
 }
 const lum=(data[i]*.2126+data[i+1]*.7152+data[i+2]*.0722)/255;
 const g=Math.round(Math.max(0,Math.min(1,gloss+(lum-.5)*.025))*255);
 for(let c=0;c<3;c++){G[i+c]=g;M[i+c]=Math.round(metal*255);E[i+c]=emissive?data[i+c]:0;}
 G[i+3]=M[i+3]=E[i+3]=255;
}
for(const [suffix,buf] of [['G',G],['M',M],['E',E]]){
 await sharp(buf,{raw:{width:info.width,height:info.height,channels:4}}).png().toFile(stem+'_'+suffix+'.png');
}
console.log('Wrote pixel-aligned gloss, metalness, and coal emissive masks; base color unchanged.');
