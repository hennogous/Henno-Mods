// Offline only: inspect preview-control objects in an AE full memory dump.
using System;
using System.Collections.Generic;
using Microsoft.Diagnostics.Runtime;

public class AEKnobDump {
    static ulong Reference(ClrHeap heap, ulong address, string name) {
        var f=heap.GetObjectType(address).GetFieldByName(name);
        return Convert.ToUInt64(f.GetValue(address));
    }
    static string DocumentName(ClrHeap heap, ulong address) {
        var type=heap.GetObjectType(address); var uri=type.GetFieldByName("m_uri");
        if(uri==null) return type.Name;
        ulong u=Convert.ToUInt64(uri.GetValue(address));
        return (string)heap.GetObjectType(u).GetFieldByName("m_String").GetValue(u);
    }
    static void Registry(ClrHeap heap, ulong service) {
        ulong registry=Reference(heap,service,"<DocumentRegistry>k__BackingField");
        ulong collection=Reference(heap,registry,"m_documents");
        ulong list=Reference(heap,collection,"m_list");
        ulong items=Reference(heap,list,"_items");
        int size=Convert.ToInt32(heap.GetObjectType(list).GetFieldByName("_size").GetValue(list));
        var live=new HashSet<ulong>(); var array=heap.GetObjectType(items);
        Console.WriteLine("SERVICE "+service.ToString("X")+" DOCUMENT REGISTRY "+registry.ToString("X")+" COUNT "+size);
        for(int n=0;n<size;n++) {
            ulong doc=Convert.ToUInt64(array.GetArrayElementValue(items,n));live.Add(doc);
            Console.WriteLine("LIVE DOCUMENT "+doc.ToString("X")+" "+DocumentName(heap,doc));
        }
        ulong dictionary=Reference(heap,service,"PreviewWindows");
        ulong entries=Reference(heap,dictionary,"entries");
        var dt=heap.GetObjectType(dictionary); int count=Convert.ToInt32(dt.GetFieldByName("count").GetValue(dictionary));
        int free=Convert.ToInt32(dt.GetFieldByName("freeCount").GetValue(dictionary));
        var et=heap.GetObjectType(entries);var element=et.ComponentType;
        Console.WriteLine("PREVIEW DICTIONARY "+dictionary.ToString("X")+" COUNT "+count+" FREE "+free);
        for(int n=0;n<count;n++) {
            ulong address=et.GetArrayElementAddress(entries,n);
            int hash=Convert.ToInt32(element.GetFieldByName("hashCode").GetValue(address,true));
            if(hash<0) continue;
            ulong doc=Convert.ToUInt64(element.GetFieldByName("key").GetValue(address,true));
            ulong window=Convert.ToUInt64(element.GetFieldByName("value").GetValue(address,true));
            object id=heap.GetObjectType(window).GetFieldByName("m_windowID").GetValue(window);
            Console.WriteLine("PREVIEW document="+doc.ToString("X")+" window="+window.ToString("X")+" id="+id+" orphan="+(!live.Contains(doc))+" "+DocumentName(heap,doc));
        }
    }
    static void Describe(ClrHeap heap, ulong address, int depth, HashSet<ulong> seen) {
        if (address == 0 || !seen.Add(address)) return;
        ClrType type = heap.GetObjectType(address);
        if (type == null) return;
        Console.WriteLine(new string(' ', depth*2) + "OBJECT " + address.ToString("X") + " " + type.Name);
        if (type.IsArray) { Console.WriteLine("ARRAY LENGTH " + type.GetArrayLength(address)); return; }
        foreach (ClrInstanceField field in type.Fields) {
            try {
                object value = field.GetValue(address);
                Console.WriteLine(new string(' ',depth*2) + "  FIELD " + field.Name + " " + field.Type.Name + " = " + value);
                if (depth < 2 && value is ulong && (field.IsObjectReference || field.Type.Name.Contains("Dictionary"))) Describe(heap,(ulong)value,depth+1,seen);
            } catch (Exception e) { Console.WriteLine("FIELD ERROR " + field.Name + " " + e.Message); }
        }
    }
    public static int Main(string[] args) {
        using (DataTarget target=DataTarget.LoadCrashDump(args[0])) {
            ClrRuntime runtime=target.ClrVersions[0].CreateRuntime(args[1],false);
            ClrHeap heap=runtime.Heap;
            if(args.Length>2 && args[2]=="--registry") {
                foreach(ulong obj in heap.EnumerateObjectAddresses()) {
                    var type=heap.GetObjectType(obj);
                    if(type!=null && type.Name=="Firaxis.AssetPreviewing.PreviewerDocumentService") Registry(heap,obj);
                }
                return 0;
            }
            if(args.Length>2 && args[2]=="--threads") {
                foreach(ClrThread thread in runtime.Threads) {
                    Console.WriteLine("THREAD "+thread.OSThreadId.ToString("X"));
                    foreach(ClrStackFrame frame in thread.StackTrace) Console.WriteLine(frame);
                }
                return 0;
            }
            foreach (ClrThread thread in runtime.Threads) {
                if (thread.CurrentException==null) continue;
                Console.WriteLine("THREAD " + thread.OSThreadId.ToString("X"));
                foreach (ClrStackFrame frame in thread.StackTrace)
                    Console.WriteLine("FRAME IP="+frame.InstructionPointer.ToString("X")+" SP="+frame.StackPointer.ToString("X")+" NATIVE="+(frame.Method==null?"":frame.Method.NativeCode.ToString("X"))+" "+frame);
            }
            bool byName=args.Length>2 && args[2].StartsWith("--name=");
            bool documents=args.Length>2 && args[2]=="--documents";
            bool byType=args.Length>2 && args[2].StartsWith("--type=");
            if (args.Length>2 && !byName && !documents && !byType) { Describe(heap,Convert.ToUInt64(args[2],16),0,new HashSet<ulong>()); return 0; }
            Dictionary<string,int> counts=new Dictionary<string,int>();
            foreach (ulong obj in heap.EnumerateObjectAddresses()) {
                ClrType type=heap.GetObjectType(obj);
                if (type==null || type.Name==null) continue;
                if(byType) { if(type.Name==args[2].Substring(7)) Describe(heap,obj,0,new HashSet<ulong>()); continue; }
                if(documents) {
                    if(type.Name=="Firaxis.AssetEditing.AssetDocument") {
                        Console.WriteLine("DOCUMENT " + obj.ToString("X"));
                        foreach(ClrInstanceField field in type.Fields) {
                            if(field.Name=="m_uri" || field.Name.Contains("PreviewWindow")) {
                                ulong address=(ulong)field.GetValue(obj);
                                Describe(heap,address,1,new HashSet<ulong>());
                            }
                        }
                    }
                    continue;
                }
                if (type.Name.IndexOf("Knob",StringComparison.OrdinalIgnoreCase)<0) continue;
                if (byName) {
                    ClrInstanceField name=type.GetFieldByName("m_name");
                    if(name!=null && (string)name.GetValue(obj)==args[2].Substring(7)) Describe(heap,obj,0,new HashSet<ulong>());
                    continue;
                }
                if (!counts.ContainsKey(type.Name)) counts[type.Name]=0;
                counts[type.Name]++;
                if (!type.Name.StartsWith("System.") && counts[type.Name] <= 4) Describe(heap,obj,0,new HashSet<ulong>());
            }
            foreach(var count in counts) Console.WriteLine("COUNT " + count.Value+" "+count.Key);
        }
        return 0;
    }
}
