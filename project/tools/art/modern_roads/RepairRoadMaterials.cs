using System;
using System.IO;
using System.Reflection;
using System.Collections;
using System.Collections.Generic;
using System.Windows.Forms;
using Firaxis.IO;
using Firaxis.Utility;
using Firaxis.Granny;
using NexusBuddy.GrannyWrappers;
class RepairRoadMaterials {
 [STAThread] static void Main(string[] args) {
  Context.Add(new VirtualSpace());var asm=Assembly.LoadFrom("CivNexus6.exe");
  using(var form=(Form)Activator.CreateInstance(asm.GetType("NexusBuddy.CivNexusSixApplicationForm"))) {
   form.ShowInTaskbar=false;form.Opacity=0;
   var file=Context.Get<GrannyContext>().LoadGrannyFile(args[0]);
   if(args.Length==1) {foreach(var m in file.GetType().GetMembers(BindingFlags.Instance|BindingFlags.Public|BindingFlags.NonPublic))if(m.Name.ToLower().Contains("mat"))Console.WriteLine(m);return;}
   var prior=Context.Get<GrannyContext>().LoadGrannyFile(args[1]);
   foreach(var mat in prior.Materials)if(!file.AddMaterialReference(mat))throw new Exception("File material registration failed");
   var originals=new Dictionary<string,IGrannyMesh>();foreach(var m in prior.Meshes)originals.Add(m.Name,m);
   foreach(var mesh in file.Meshes) {
    var old=originals[mesh.Name];if(old.MaterialBindings.Count!=1)throw new Exception("Expected one material per road mesh");
    foreach(var mat in new List<IGrannyMaterial>(mesh.MaterialBindings))if(!mesh.RemoveMaterialBinding(mat))throw new Exception("Remove failed");
    if(!mesh.AddMaterialBinding(old.MaterialBindings[0]))throw new Exception("Add failed");
   }
   form.GetType().GetMethod("SaveAsAction",BindingFlags.Instance|BindingFlags.Public|BindingFlags.NonPublic).Invoke(form,new object[]{file,args[2],false});
   Console.WriteLine("Restored exact existing material bindings for "+file.Meshes.Count+" meshes");
  }
 }
}
