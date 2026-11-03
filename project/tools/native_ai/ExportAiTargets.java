// Exports named RVA targets without inferring types or signatures.
// @category CSC.Analysis
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.nio.file.*;

public class ExportAiTargets extends GhidraScript {
 public void run() throws Exception {
  String[] a=getScriptArgs();
  File out=new File(a[0]);out.mkdirs();
    java.util.Map<String,java.util.List<String[]>> mapped=new java.util.LinkedHashMap<>();
  Path mapping=Paths.get(a[2]);
  for(String row:Files.readAllLines(mapping)) {
   if(row.startsWith("#"))continue;
   String[] q=row.split("\t",5);
   if(q.length!=5||!(q[2].equals("unique")||q[2].equals("unique-reordered")||q[2].equals("resolved")))continue;
   mapped.computeIfAbsent(q[1],k->new java.util.ArrayList<>()).add(q);
  }
  for(java.util.List<String[]> aliases:mapped.values())for(String[] q:aliases) {
   Address ad=currentProgram.getImageBase().add(Long.parseUnsignedLong(q[1].replace("0x",""),16));
   String name=q[4].replaceAll("[^A-Za-z0-9_]","_");
   if(name.length()>180)name=name.substring(0,180);
   name=name+"_RVA_"+q[1].replace("0x","")+"_"+q[2].replace('-','_');
   Function fn=getFunctionAt(ad);
   if(fn!=null&&aliases.size()==1)fn.setName(name,SourceType.USER_DEFINED);
   else createLabel(ad,name,false,SourceType.USER_DEFINED);
   setPlateComment(ad,"Mapped name only; category="+q[2]+"; old RVA="+q[0]+"; full reference name="+q[4]+"; aliases at current RVA="+aliases.size()+". No signature imported.");
  }
  DecompInterface d=new DecompInterface();d.openProgram(currentProgram);
  for(String line:Files.readAllLines(Paths.get(a[1]))) { if(line.trim().isEmpty()||line.startsWith("#"))continue; String[] p=line.trim().split("\\s+"); Address ad=currentProgram.getImageBase().add(Long.parseUnsignedLong(p[0],16)); Function f=getFunctionAt(ad); if(f!=null)f.setName(p[1]+"_RVA_"+p[0],SourceType.USER_DEFINED); }
  PrintWriter status=new PrintWriter(new File(out,"target-status.tsv")); status.println("rva\tname\tmap_categories\tbody\tdecompile_completed\terror");
  for(String line:Files.readAllLines(Paths.get(a[1]))) {
   if(line.trim().isEmpty()||line.startsWith("#"))continue;
   String[] p=line.trim().split("\\s+");
   Address ad=currentProgram.getImageBase().add(Long.parseUnsignedLong(p[0],16));
   Function f=getFunctionAt(ad);
   // Preserve native PE/pdata-derived boundaries; skip missing starts.
   if(f==null){println("NO FUNCTION "+line);status.println(p[0]+"\t"+p[1]+"\t\t\tfalse\tNo function at target RVA");continue;}
   f.setName(p[1]+"_RVA_"+p[0],SourceType.USER_DEFINED);
   try(PrintWriter w=new PrintWriter(new File(out,p[1]+"_"+p[0]+".txt"))) {
    w.println("Program: "+currentProgram.getName()+" Image base: "+currentProgram.getImageBase()+" RVA: "+p[0]);
    w.println("Label only; recovered types/signatures remain decompiler estimates.\n");
    DecompileResults r=d.decompileFunction(f,180,monitor);
    java.util.List<String[]> provenance=mapped.get("0x"+p[0]); String cats=""; if(provenance!=null)for(String[] q:provenance)cats+=q[2]+",";
    status.println(p[0]+"\t"+p[1]+"\t"+cats+"\t"+f.getBody()+"\t"+r.decompileCompleted()+"\t"+r.getErrorMessage().replaceAll("[\\r\\n\\t]"," "));status.flush();
    w.println("=== C ===");w.println(r.decompileCompleted()?r.getDecompiledFunction().getC():r.getErrorMessage());
    w.println("=== ASSEMBLY ===");
    InstructionIterator it=currentProgram.getListing().getInstructions(f.getBody(),true);
    while(it.hasNext()){Instruction ins=it.next();w.println(ins.getAddress()+"  "+ins);}
    w.println("=== REFERENCES TO ENTRY ===");
    for(Reference ref:getReferencesTo(f.getEntryPoint())){Function caller=getFunctionContaining(ref.getFromAddress());w.println(ref.getFromAddress()+" "+ref.getReferenceType()+" "+(caller==null?"":caller.getName()));}
    w.println("=== CALLED FUNCTIONS ===");
    for(Function c:f.getCalledFunctions(monitor))w.println(c.getEntryPoint()+" "+c.getName());
   }
  }
  try(PrintWriter w=new PrintWriter(new File(out,"ai-parameter-string-xrefs.txt"))) {
   for(String needle:new String[]{"AI_CURRENT_TASK_BIAS","AI_DISCOUNT_RATE"}) {
    Address start=currentProgram.getMinAddress();
    while(start!=null) {
     Address hit=currentProgram.getMemory().findBytes(start,needle.getBytes(java.nio.charset.StandardCharsets.US_ASCII),null,true,monitor);
     if(hit==null)break;
     w.println(needle+" STRING "+hit+" RVA "+hit.subtract(currentProgram.getImageBase()));
     for(Reference ref:getReferencesTo(hit)) {
      Function fn=getFunctionContaining(ref.getFromAddress());
      w.println("  "+ref.getFromAddress()+" "+ref.getReferenceType()+" "+(fn==null?"no containing function":fn.getEntryPoint()+" "+fn.getName()));
     }
     start=hit.next();
    }
   }
  }
  status.close();
  d.dispose();
 }
}





