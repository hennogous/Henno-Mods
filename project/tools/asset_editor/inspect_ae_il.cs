// Static metadata/IL reader. Does not load or execute inspected AE code.
using System;
using Mono.Cecil;
using Mono.Cecil.Cil;
public class AEIL {
    static bool listOnly;
    static bool callers;
    static void Dump(TypeDefinition type, string filter) {
        bool match = type.FullName.IndexOf(filter,StringComparison.OrdinalIgnoreCase)>=0;
        foreach (MethodDefinition method in type.Methods) {
            bool selected=match || method.FullName.IndexOf(filter,StringComparison.OrdinalIgnoreCase)>=0;
            if (method.HasBody) foreach(Instruction i in method.Body.Instructions)
                if ((i.OpCode==OpCodes.Ldstr || callers) && i.Operand!=null && i.Operand.ToString().IndexOf(filter,StringComparison.OrdinalIgnoreCase)>=0) selected=true;
            if (!selected) continue;
            Console.WriteLine("METHOD " + method.FullName + " RVA=" + method.RVA.ToString("X") + " TOKEN=" + method.MetadataToken);
            if(method.HasBody && !listOnly) foreach(Instruction i in method.Body.Instructions) Console.WriteLine(i);
        }
        if(match) foreach(FieldDefinition f in type.Fields) Console.WriteLine("FIELD " + f.FullName);
        foreach(TypeDefinition child in type.NestedTypes) Dump(child,filter);
    }
    public static int Main(string[] args) {
        listOnly=Array.IndexOf(args,"--list")>=0;
        callers=Array.IndexOf(args,"--calls")>=0;
        using(ModuleDefinition module=ModuleDefinition.ReadModule(args[0]))
            foreach(TypeDefinition type in module.Types) Dump(type,args[1]);
        return 0;
    }
}
