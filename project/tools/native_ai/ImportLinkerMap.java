// Adds map-supplied names to an isolated, hash-pinned historical program.
// Does not create functions, change bodies, apply prototypes or touch current-build addresses.
// @category CSC.Analysis
import ghidra.app.script.GhidraScript;
import ghidra.app.util.demangler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.io.*;
import java.util.*;

public class ImportLinkerMap extends GhidraScript {
 public void run() throws Exception {
  String[] a=getScriptArgs();
  if(a.length!=4) throw new IllegalArgumentException("symbols.tsv expected-program-sha expected-tsv-sha output-directory");
  if(!a[1].equalsIgnoreCase(currentProgram.getExecutableSHA256())) throw new IllegalStateException("Program SHA mismatch");
  Path input=Paths.get(a[0]);
  String hash=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(input)));
  if(!hash.equalsIgnoreCase(a[2])) throw new IllegalStateException("Symbol index SHA mismatch");
  File out=new File(a[3]);out.mkdirs();
  Map<Long,List<String[]>> groups=new LinkedHashMap<>();
  for(String line:Files.readAllLines(input,StandardCharsets.UTF_8)) {
   String[] p=line.split("\t",-1);
   if(p.length!=6||!p[0].startsWith("0x"))continue;
   // The complete raw index is retained. Ghidra imports code and vtables only,
   // avoiding hundreds of thousands of unwind/compiler data aliases.
   if(!p[1].equals("function")&&!p[3].startsWith("??_7"))continue;
   groups.computeIfAbsent(Long.parseUnsignedLong(p[0].substring(2),16),k->new ArrayList<>()).add(p);
  }
  int labels=0,renamed=0,missing=0,errors=0,demangled=0;
  try(PrintWriter w=new PrintWriter(new File(out,"imported-symbols.tsv"),"UTF-8")) {
   w.println("rva\tkind\tlabel\tdemangled\tobject\tfunction_at_entry\taliases\tstatus");
   for(Map.Entry<Long,List<String[]>> e:groups.entrySet()) {
    monitor.checkCancelled();
    Address ad=currentProgram.getImageBase().add(e.getKey());
    if(!currentProgram.getMemory().contains(ad)){missing+=e.getValue().size();continue;}
    Function fn=getFunctionAt(ad); Set<String> seen=new HashSet<>();
    for(String[] p:e.getValue()) {
     if(!seen.add(p[3]))continue;
     String sig=p[3], name=p[3];
     try {
      DemangledObject d=DemanglerUtil.demangle(currentProgram,p[3]);
      if(d!=null) {sig=d.getSignature();name=d.getNamespaceString();demangled++;}
      name=name.replaceAll("[^A-Za-z0-9_]","_");
      if(name.length()>160)name=name.substring(0,160);
      String suffix=Integer.toUnsignedString(p[3].hashCode(),16);
      name="MAP23_"+name+"_"+Long.toHexString(e.getKey())+"_"+suffix;
      if(currentProgram.getSymbolTable().getSymbol(name,ad,currentProgram.getGlobalNamespace())==null)createLabel(ad,name,false,SourceType.IMPORTED);
      labels++;
      if(fn!=null && e.getValue().size()==1 && fn.getSymbol().getSource()!=SourceType.USER_DEFINED) {
       // A global label of this name can coexist with an analyzed function;
       // give the function a distinct stable spelling to avoid rename conflicts.
       fn.setName(name+"__function",SourceType.IMPORTED);renamed++;
      }
      w.println(p[0]+"\t"+p[1]+"\t"+name+"\t"+sig.replaceAll("[\\t\\r\\n]"," ")+"\t"+p[4]+"\t"+(fn!=null)+"\t"+e.getValue().size()+"\tok");
     } catch(Exception ex) {errors++;w.println(p[0]+"\t"+p[1]+"\t\t\t"+p[4]+"\t"+(fn!=null)+"\t"+e.getValue().size()+"\tERROR "+ex.toString().replaceAll("[\\t\\r\\n]"," "));}
    }
    String comment="Supplied 2023 linker map; layout validated, map/DLL timestamps differ. Names only; no prototypes/bodies applied. Alias rows="+e.getValue().size()+". See imported-symbols.tsv and map-validation.json.\n"+e.getValue().get(0)[3];
    setPlateComment(ad,comment);
   }
  }
  String result="labels="+labels+" renamed_existing_functions="+renamed+" demangled="+demangled+" outside_memory="+missing+" errors="+errors+"\n";
  Files.writeString(new File(out,"import-summary.txt").toPath(),result);
  println(result);
  if(errors>0||missing>0)throw new IllegalStateException("Inspect incomplete import report");
 }
}
