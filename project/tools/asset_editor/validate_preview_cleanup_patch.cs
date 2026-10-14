// Offline IL verification. Loads metadata only, never executes Firaxis code.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

class PreviewCleanupValidator {
    static void Check(bool condition, string reason) { if (!condition) throw new Exception(reason); }
    static IEnumerable<TypeDefinition> Types(IEnumerable<TypeDefinition> types) {
        foreach (var t in types) { yield return t; foreach (var n in Types(t.NestedTypes)) yield return n; }
    }
    static string Operand(object o) {
        var target = o as Instruction;
        if(target != null) return target.Offset.ToString("x4");
        var targets = o as Instruction[];
        if(targets != null) return String.Join(",", targets.Select(x => x.Offset.ToString("x4")));
        return o == null ? "" : o.ToString();
    }
    // Interpret the real removal method's IL, substituting explicit dependency/document states.
    // Engine calls are recorded, not executed. Unknown IL/calls fail the test.
    static string Trace(MethodDefinition method, bool surrogate, bool previewable, bool tracked) {
        var stack = new Stack<object>(); var locals = new object[method.Body.Variables.Count];
        var events = new List<string>(); var instructions = method.Body.Instructions;
        int pc=0, steps=0;
        while(pc < instructions.Count) {
            Check(++steps<200,"Unexpected loop"); var i=instructions[pc++];
            switch(i.OpCode.Code) {
                case Code.Nop: break;
                case Code.Ldarg_0: stack.Push("service"); break;
                case Code.Ldarg_2: stack.Push("event"); break;
                case Code.Ldfld: {
                    stack.Pop(); var f=(FieldReference)i.Operand;
                    Check(f.Name=="Item" || f.Name=="PreviewWindows","Unknown field");
                    stack.Push(f.Name=="Item" ? "document" : "dictionary"); break;
                }
                case Code.Ldnull: stack.Push(null); break;
                case Code.Ldc_I4_0: stack.Push(false); break;
                case Code.Ldstr: stack.Push(i.Operand); break;
                case Code.Stloc_0: locals[0]=stack.Pop(); break;
                case Code.Stloc_1: locals[1]=stack.Pop(); break;
                case Code.Stloc_2: locals[2]=stack.Pop(); break;
                case Code.Stloc_3: locals[3]=stack.Pop(); break;
                case Code.Stloc_S: locals[((VariableDefinition)i.Operand).Index]=stack.Pop(); break;
                case Code.Ldloc_0: stack.Push(locals[0]); break;
                case Code.Ldloc_1: stack.Push(locals[1]); break;
                case Code.Ldloc_2: stack.Push(locals[2]); break;
                case Code.Ldloc_3: stack.Push(locals[3]); break;
                case Code.Ldloc_S: stack.Push(locals[((VariableDefinition)i.Operand).Index]); break;
                case Code.Ceq: { var a=stack.Pop(); var b=stack.Pop(); stack.Push(Object.Equals(a,b)); break; }
                case Code.Brfalse_S: if(!(bool)stack.Pop()) pc=instructions.IndexOf((Instruction)i.Operand); break;
                case Code.Br_S: pc=instructions.IndexOf((Instruction)i.Operand); break;
                case Code.Pop: stack.Pop(); break;
                case Code.Call:
                case Code.Callvirt: {
                    var call=(MethodReference)i.Operand;
                    for(int n=0;n<call.Parameters.Count+(call.HasThis ? 1:0);n++) stack.Pop();
                    switch(call.Name) {
                        case "UnbindSurrogatePreviewer": events.Add("Unbind"); stack.Push(surrogate); break;
                        case "As": stack.Push(previewable ? "previewable" : null); break;
                        case "ContainsKey": stack.Push(tracked); break;
                        case "get_Item": stack.Push("window"); break;
                        case "ShutdownDocumentPreviewing": events.Add("Shutdown"); break;
                        case "get_AssetPreviewer": stack.Push("previewer"); break;
                        case "CloseWindow": events.Add("Close"); break;
                        case "Remove": events.Add("Remove"); stack.Push(true); break;
                        case "get_Uri": stack.Push("uri"); break;
                        case "get_LocalPath": stack.Push("path"); break;
                        case "Format": stack.Push("message"); break;
                        case "SilentAssert": events.Add("AssertUntracked"); break;
                        default: throw new Exception("Unknown call: "+call);
                    } break;
                }
                case Code.Ret: Check(stack.Count==0,"Nonempty stack on return"); return String.Join(",",events);
                default: throw new Exception("Unsupported IL: "+i);
            }
        }
        throw new Exception("No return");
    }
    public static int Main(string[] args) {
        try {
            byte[] a=File.ReadAllBytes(args[0]), b=File.ReadAllBytes(args[1]);
            Check(a.Length==b.Length,"Size changed");
            var differences=Enumerable.Range(0,a.Length).Where(x=>a[x]!=b[x]).ToArray();
            Check(differences.Length==1 && a[differences[0]]==0x7a && b[differences[0]]==0,"Expected exactly one branch operand change");
            using(var old=ModuleDefinition.ReadModule(args[0])) using(var patch=ModuleDefinition.ReadModule(args[1])) {
                Check(!old.Assembly.Name.HasPublicKey && !patch.Assembly.Name.HasPublicKey,"Strong-named DLL cannot be patched");
                Check(old.Mvid==patch.Mvid,"Module identity changed");
                Console.WriteLine("Assembly "+old.Assembly.Name+"; unsigned; unchanged MVID "+old.Mvid);
                var oldMethods=Types(old.Types).SelectMany(x=>x.Methods).Where(x=>x.HasBody).ToArray();
                var newMethods=Types(patch.Types).SelectMany(x=>x.Methods).Where(x=>x.HasBody).ToArray();
                Check(oldMethods.Length==newMethods.Length,"Method count changed"); int changes=0;
                MethodDefinition oldTarget=null,newTarget=null;
                for(int n=0;n<oldMethods.Length;n++) {
                    var m=oldMethods[n]; var p=newMethods[n];
                    Check(m.FullName==p.FullName && m.RVA==p.RVA && m.Body.Instructions.Count==p.Body.Instructions.Count,"Method layout changed");
                    for(int k=0;k<m.Body.Instructions.Count;k++) {
                        var oi=m.Body.Instructions[k];var ni=p.Body.Instructions[k];
                        Check(oi.Offset==ni.Offset && oi.OpCode==ni.OpCode,"Instruction changed");
                        if(Operand(oi.Operand)==Operand(ni.Operand)) continue;
                        Check(m.DeclaringType.FullName=="Firaxis.AssetPreviewing.PreviewerDocumentService" && m.Name=="DocumentRegistry_DocumentRemoved" && m.MetadataToken.ToUInt32()==0x060002b8 && m.RVA==0xd7a0 && oi.Offset==0x11 && oi.OpCode==OpCodes.Br_S && Operand(oi.Operand)=="008d" && Operand(ni.Operand)=="0013","Unexpected operand change");
                        changes++; oldTarget=m;newTarget=p;
                    }
                }
                Check(changes==1,"Wrong IL change count");
                Console.WriteLine("Verified all "+oldMethods.Length+" method bodies; only IL_0011 branch target differs.");
                foreach(bool surrogate in new[]{false,true}) foreach(bool previewable in new[]{false,true}) foreach(bool tracked in new[]{false,true}) {
                    string before=Trace(oldTarget,surrogate,previewable,tracked),after=Trace(newTarget,surrogate,previewable,tracked);
                    string expected="Unbind"+(previewable ? (tracked ? ",Shutdown,Close,Remove" : ",AssertUntracked") : "");
                    Check(after==expected,"Incorrect patched path");
                    if(!surrogate || !previewable) Check(before==after,"Unrelated path changed");
                    if(surrogate && previewable) Check(before=="Unbind","Original defect not reproduced");
                    Console.WriteLine("PASS surrogate="+surrogate+" previewable="+previewable+" tracked="+tracked+" old=["+before+"] patched=["+after+"]");
                }
            }
            Console.WriteLine("PASS offline validation; native engine/editor runtime test still required.");return 0;
        } catch(Exception ex) { Console.Error.WriteLine(ex);return 1; }
    }
}
