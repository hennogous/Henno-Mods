using System;
using System.Reflection;
using System.Collections;
using System.Windows.Forms;
using Firaxis.IO;
using Firaxis.Utility;
using Firaxis.Granny;
class InspectFgxLayout {
 [STAThread] static void Main(string[] args) {
  Context.Add(new VirtualSpace());
  var asm=Assembly.LoadFrom("CivNexus6.exe");
  var form=(Form)Activator.CreateInstance(asm.GetType("NexusBuddy.CivNexusSixApplicationForm"));
  form.ShowInTaskbar=false;form.Opacity=0;
  foreach(var path in args) {
   var file=Context.Get<GrannyContext>().LoadGrannyFile(path);
   Console.WriteLine("FILE "+path);
   foreach(IGrannyMesh mesh in file.Meshes) {
    Console.WriteLine("MESH "+mesh.Name);
    var wrapper=Activator.CreateInstance(asm.GetType("NexusBuddy.GrannyWrappers.GrannyMeshWrapper"),new object[]{mesh});
    var infos=(IEnumerable)wrapper.GetType().GetMethod("getVertexStructInfos",BindingFlags.Instance|BindingFlags.Public|BindingFlags.NonPublic).Invoke(wrapper,null);
    foreach(var info in infos) {
     var t=info.GetType();
     Console.WriteLine(t.GetField("name").GetValue(info)+" type="+t.GetField("type").GetValue(info)+" count="+t.GetField("count").GetValue(info));
    }
    break;
   }
  }
  form.Dispose();
 }
}
