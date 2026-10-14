// Offline x64 .NET Framework dump reader using Microsoft ClrMD 1.1 (net45).
// Compile with csc /platform:x64 /reference:Microsoft.Diagnostics.Runtime.dll.
using System;
using Microsoft.Diagnostics.Runtime;

public class AEManagedDump {
    public static int Main(string[] args) {
        if (args.Length < 1) { Console.Error.WriteLine("Usage: inspect_ae_managed_dump.exe dump [matching-mscordacwks.dll]"); return 2; }
        using (DataTarget target = DataTarget.LoadCrashDump(args[0])) {
            foreach (ClrInfo info in target.ClrVersions) {
                Console.WriteLine("CLR " + info.Version);
                ClrRuntime runtime = args.Length > 1 ? info.CreateRuntime(args[1], false) : info.CreateRuntime();
                foreach (ClrThread thread in runtime.Threads) {
                    ClrException exception = thread.CurrentException;
                    if (exception == null) continue;
                    Console.WriteLine("THREAD " + thread.OSThreadId.ToString("X") + " Last thrown exception (can be stale):");
                    for (ClrException current = exception; current != null; current = current.Inner) {
                        Console.WriteLine("EXCEPTION " + current.Type.Name + " at " + current.Address.ToString("X") + " HRESULT=" + current.HResult.ToString("X"));
                        Console.WriteLine("MESSAGE " + current.Message);
                        Console.WriteLine("EXCEPTION STACK");
                        foreach (ClrStackFrame frame in current.StackTrace) Console.WriteLine(frame.ToString());
                    }
                    Console.WriteLine("THREAD STACK");
                    foreach (ClrStackFrame frame in thread.StackTrace) Console.WriteLine(frame.ToString());
                }
            }
        }
        return 0;
    }
}
