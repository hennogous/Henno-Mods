// Rename one FGX mesh through Firaxis serialization, without rebuilding geometry.
using System;
using System.Reflection;
using System.Windows.Forms;
using Firaxis.IO;
using Firaxis.Utility;
using Firaxis.Granny;
class RenameFgxMesh {
 [STAThread] static int Main(string[] args) {
  try {
   if(args.Length!=4) throw new ArgumentException("input.fgx output.fgx old_name new_name");
   Context.Add(new VirtualSpace());
   var asm=Assembly.LoadFrom("CivNexus6.exe");
   using(var form=(Form)Activator.CreateInstance(asm.GetType("NexusBuddy.CivNexusSixApplicationForm"))) {
    form.ShowInTaskbar=false;form.Opacity=0;
    var file=Context.Get<GrannyContext>().LoadGrannyFile(args[0]);
    int count=0;
    foreach(IGrannyMesh mesh in file.Meshes) {
     if(mesh.Name==args[3]) throw new Exception("Target name already exists");
     if(mesh.Name==args[2]) {mesh.Name=args[3];count++;}
    }
    if(count!=1) throw new Exception("Expected exactly one matching mesh, got "+count);
    form.GetType().GetMethod("SaveAsAction",BindingFlags.Instance|BindingFlags.Public|BindingFlags.NonPublic)
      .Invoke(form,new object[]{file,args[1],false});
    var saved=Context.Get<GrannyContext>().LoadGrannyFile(args[1]);
    count=0;
    foreach(IGrannyMesh mesh in saved.Meshes) {
     if(mesh.Name==args[2]) throw new Exception("Old name remains after save");
     if(mesh.Name==args[3]) count++;
    }
    if(count!=1) throw new Exception("Renamed mesh not found after save");
    Console.WriteLine("RENAMED_AND_RELOADED "+args[2]+" -> "+args[3]);
   }
   return 0;
  } catch(Exception e) {Console.Error.WriteLine(e);return 1;}
 }
}
