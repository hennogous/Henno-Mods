using System;
using System.Collections.Generic;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Windows.Forms;
using Firaxis.IO;
using Firaxis.Utility;
using Firaxis.Granny;
using NexusBuddy.GrannyWrappers;
using NexusBuddy.GrannyInfos;
class PatchFashionDressUV {
 static byte[] Read(IGrannyMesh mesh,out IntPtr ptr,out int stride,out int offset) {
  var wrapper=new GrannyMeshWrapper(mesh);var info=new GrannyMeshInfo();
  info.setVertexStructInfos((List<GrannyMeshVertexStructInfo>)typeof(GrannyMeshWrapper).GetMethod("getVertexStructInfos",BindingFlags.Instance|BindingFlags.NonPublic).Invoke(wrapper,null));
  var uv=info.getVertexStructInfoByName("TextureCoordinates0");
  if(uv.type!=10 || uv.count<2)throw new Exception("Unexpected UV format");
  stride=info.bytesPerVertex;offset=uv.offset;ptr=Marshal.ReadIntPtr(wrapper.getVerticesPtr());
  byte[] b=new byte[wrapper.getNumVertices()*stride];Marshal.Copy(ptr,b,0,b.Length);return b;
 }
 [STAThread] static void Main(string[] args) {
  Context.Add(new VirtualSpace());var asm=Assembly.LoadFrom("CivNexus6.exe");
  using(var form=(Form)Activator.CreateInstance(asm.GetType("NexusBuddy.CivNexusSixApplicationForm"))) {
   form.ShowInTaskbar=false;form.Opacity=0;
   var file=Context.Get<GrannyContext>().LoadGrannyFile(args[0]);var expected=new Dictionary<string,byte[]>();int changed=0;
   foreach(IGrannyMesh mesh in file.Meshes) {
    IntPtr ptr;int stride,offset;var b=Read(mesh,out ptr,out stride,out offset);
    bool gown=mesh.Name.Contains("Front_Ivory_Gown_Bell"),sleeve=mesh.Name.Contains("Ivory_Rounded_Sleeve");
    if(gown||sleeve) {
     for(int i=0;i<b.Length;i+=stride) {
      float u=BitConverter.ToSingle(b,i+offset),v=BitConverter.ToSingle(b,i+offset+4);
      if(gown && !(u>.874 && u<1 && v>.249 && v<.376))throw new Exception("Gown outside ivory embroidery region");
      if(sleeve && !(u>=0 && u<.126 && v>.374 && v<.501))throw new Exception("Sleeve outside ivory region");
      Array.Copy(BitConverter.GetBytes(u+(gown?-.375f:.75f)),0,b,i+offset,4);
      Array.Copy(BitConverter.GetBytes(v+(gown?.125f:-.125f)),0,b,i+offset+4,4);
     }
     Marshal.Copy(b,0,ptr,b.Length);changed++;
    }
    expected.Add(mesh.Name,b);
   }
   if(changed!=3)throw new Exception("Expected exactly three changed meshes");
   form.GetType().GetMethod("SaveAsAction",BindingFlags.Instance|BindingFlags.Public|BindingFlags.NonPublic).Invoke(form,new object[]{file,args[1],false});
   var saved=Context.Get<GrannyContext>().LoadGrannyFile(args[1]);int verified=0;
   foreach(IGrannyMesh mesh in saved.Meshes) {
    IntPtr ptr;int stride,offset;var b=Read(mesh,out ptr,out stride,out offset);var e=expected[mesh.Name];
    if(b.Length!=e.Length)throw new Exception("Vertex count changed");
    for(int i=0;i<b.Length;i++)if(b[i]!=e[i])throw new Exception("Unexpected vertex data change: "+mesh.Name+" at "+i);
    verified++;
   }
   if(verified!=expected.Count)throw new Exception("Mesh count changed");
   Console.WriteLine("Verified "+verified+" complete native vertex buffers; only gown/sleeve UV0 changed.");
  }
 }
}
