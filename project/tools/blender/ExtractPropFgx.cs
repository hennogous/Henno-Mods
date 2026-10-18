// Read-only FGX extraction using the installed Firaxis/CivNexus6 libraries.
using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Collections;
using System.Collections.Generic;
using System.Web.Script.Serialization;
using Firaxis.IO;
using Firaxis.Utility;
using Firaxis.Granny;
class ExtractPropFgx {
 static unsafe object Transform(IGrannyTransform t) {
  var scale=new float[]{1,0,0,0,1,0,0,0,1};
  if ((((int)t.Flags)&4)!=0) {
   // The installed managed getter reads +16 (Orientation), not +32.
   // Native granny_transform: flags(4), position(12), quaternion(16), 3x3(36).
   var field=t.GetType().GetField("m_pkTransform",BindingFlags.Instance|BindingFlags.NonPublic);
   if(field==null) throw new InvalidOperationException("Unsupported native transform implementation");
   var pointer=(IntPtr)Pointer.Unbox(field.GetValue(t));
   if(pointer==IntPtr.Zero || Marshal.ReadInt32(pointer)!=(int)t.Flags)
    throw new InvalidOperationException("Native transform flags mismatch");
   var position=new float[3]; Marshal.Copy(IntPtr.Add(pointer,4),position,0,3);
   for(int i=0;i<3;i++) if(Math.Abs(position[i]-t.Position[i])>0.00001f)
    throw new InvalidOperationException("Native transform position mismatch");
   Marshal.Copy(IntPtr.Add(pointer,32),scale,0,9);
   if(scale.Any(v=>float.IsNaN(v)||float.IsInfinity(v)))
    throw new InvalidOperationException("Invalid native transform scale/shear");
  }
  return new {position=t.Position,orientation=t.Orientation,scaleShear=scale,flags=t.Flags.ToString()};
 }
 static object Fields(object o) { var d=new Dictionary<string,object>(); foreach(var f in o.GetType().GetFields()) d[f.Name]=f.GetValue(o); return d; }
 [STAThread] static int Main(string[] args) {
  try {
   Context.Add(new VirtualSpace());
   var asm=Assembly.LoadFrom(Path.Combine(args[0],"CivNexus6.exe"));
   var wt=asm.GetType("NexusBuddy.GrannyWrappers.GrannyMeshWrapper");
   var flags=BindingFlags.Instance|BindingFlags.Public|BindingFlags.NonPublic;
   var file=new GrannyFileLoader().LoadGrannyFile(args[1]);
   var meshes=new List<object>();
   foreach(var mesh in file.Meshes) {
    var wrapper=Activator.CreateInstance(wt,new object[]{mesh});
    var info=wt.GetMethod("getMeshInfo",flags).Invoke(wrapper,null);
    var d=(Dictionary<string,object>)Fields(info);
    var verts=(IEnumerable)d["vertices"]; var vl=new List<object>();
    foreach(var v in verts) vl.Add(Fields(v)); d["vertices"]=vl;
    var groups=new List<object>(); int n=(int)wt.GetMethod("getNumTriangleGroups",flags).Invoke(wrapper,null);
    for(int i=0;i<n;i++) groups.Add(new {material=(int)wt.GetMethod("getGroupMaterialIndexForIndex",flags).Invoke(wrapper,new object[]{i}),first=(int)wt.GetMethod("getGroupTriFirstForIndex",flags).Invoke(wrapper,new object[]{i}),count=(int)wt.GetMethod("getGroupTriCountForIndex",flags).Invoke(wrapper,new object[]{i})});
    d["groups"]=groups; meshes.Add(d);
   }
   var models=new List<object>();
   foreach(var m in file.Models) {
    var bones=new List<object>();
    foreach(var b in m.Skeleton.Bones) {
     var bt=asm.GetType("NexusBuddy.GrannyWrappers.GrannyBoneWrapper");
     var bw=Activator.CreateInstance(bt,new object[]{b});
     bones.Add(new {name=b.Name,parent=b.ParentIndex,local=new {position=b.LocalTransform.Position,orientation=b.LocalTransform.Orientation,scaleShear=bt.GetMethod("getScaleShear",flags).Invoke(bw,null),flags=b.LocalTransform.Flags.ToString()},inverseWorld=b.InverseWorldTransform});
    }
    models.Add(new {name=m.Name,placement=Transform(m.InitialPlacement),bones=bones,meshBindings=m.MeshBindings.Select(x=>x.Name).ToArray()});
   }
   var ser=new JavaScriptSerializer(); ser.MaxJsonLength=int.MaxValue;
   File.WriteAllText(args[2],ser.Serialize(new {meshes=meshes,models=models}));
   Console.WriteLine(Path.GetFileName(args[1])+": "+meshes.Count+" meshes, "+models.Count+" models"); return 0;
  } catch(Exception e) {Console.Error.WriteLine(e);return 1;}
 }
}
