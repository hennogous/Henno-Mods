// Patch only UV0 bytes, preserving native skeletons, placements and vertex layout.
using System;
using System.IO;
using System.Collections.Generic;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Windows.Forms;
using System.Web.Script.Serialization;
using Firaxis.IO;
using Firaxis.Utility;
using Firaxis.Granny;
using NexusBuddy.GrannyWrappers;
using NexusBuddy.GrannyInfos;
class PatchAtlasUV {
 static byte[] Read(IGrannyMesh mesh,out IntPtr ptr,out int stride,out int offset) {
  var w=new GrannyMeshWrapper(mesh);var info=new GrannyMeshInfo();
  info.setVertexStructInfos((List<GrannyMeshVertexStructInfo>)typeof(GrannyMeshWrapper).GetMethod("getVertexStructInfos",BindingFlags.Instance|BindingFlags.NonPublic).Invoke(w,null));
  var uv=info.getVertexStructInfoByName("TextureCoordinates0");
  if(uv.type!=10 || uv.count<2)throw new Exception("Unexpected UV format");
  stride=info.bytesPerVertex;offset=uv.offset;ptr=Marshal.ReadIntPtr(w.getVerticesPtr());
  byte[] b=new byte[w.getNumVertices()*stride];Marshal.Copy(ptr,b,0,b.Length);return b;
 }
 [STAThread] static void Main(string[] args) {
  Context.Add(new VirtualSpace());var asm=Assembly.LoadFrom("CivNexus6.exe");
  var edits=new JavaScriptSerializer().Deserialize<Dictionary<string,Dictionary<string,float[]>>>(File.ReadAllText(args[2]));
  using(var form=(Form)Activator.CreateInstance(asm.GetType("NexusBuddy.CivNexusSixApplicationForm"))) {
   form.ShowInTaskbar=false;form.Opacity=0;
   var file=Context.Get<GrannyContext>().LoadGrannyFile(args[0]);var expected=new Dictionary<string,byte[]>();int changed=0;
   foreach(IGrannyMesh mesh in file.Meshes) {
    IntPtr ptr;int stride,offset;var b=Read(mesh,out ptr,out stride,out offset);
    if(edits.ContainsKey(mesh.Name))foreach(var e in edits[mesh.Name]) {
     int pos=int.Parse(e.Key)*stride+offset;
     if(Math.Abs(BitConverter.ToSingle(b,pos)-e.Value[0])>0.000001 || Math.Abs(BitConverter.ToSingle(b,pos+4)-e.Value[1])>0.000001)throw new Exception("Stale source UV");
     Array.Copy(BitConverter.GetBytes(e.Value[2]),0,b,pos,4);Array.Copy(BitConverter.GetBytes(e.Value[3]),0,b,pos+4,4);changed++;
    }
    Marshal.Copy(b,0,ptr,b.Length);expected.Add(mesh.Name,b);
   }
   if(changed==0)throw new Exception("No changes requested");
   form.GetType().GetMethod("SaveAsAction",BindingFlags.Instance|BindingFlags.Public|BindingFlags.NonPublic).Invoke(form,new object[]{file,args[1],false});
   var saved=Context.Get<GrannyContext>().LoadGrannyFile(args[1]);int verified=0;
   foreach(IGrannyMesh mesh in saved.Meshes) {
    IntPtr ptr;int stride,offset;var b=Read(mesh,out ptr,out stride,out offset);var e=expected[mesh.Name];
    if(b.Length!=e.Length)throw new Exception("Vertex count changed");
    for(int i=0;i<b.Length;i++)if(b[i]!=e[i])throw new Exception("Unexpected vertex data change: "+mesh.Name+" at "+i);
    verified++;
   }
   if(verified!=expected.Count)throw new Exception("Mesh count changed");
   Console.WriteLine("Verified "+verified+" complete native buffers; moved "+changed+" UV0 coordinates.");
  }
 }
}
