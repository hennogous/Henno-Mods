// Rename rig identities through the installed Firaxis serializer.
using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Windows.Forms;
using Firaxis.IO;
using Firaxis.Utility;
using Firaxis.Granny;
class RenameFgxRig {
 static BindingFlags Flags=BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Instance;
 static List<IntPtr> Strings=new List<IntPtr>();
 static List<object> Names(object value) {
  var result=new List<object>();result.Add(value);
  foreach(string child in new string[]{"Skeleton","Bones","TrackGroups","TransformTracks"}) {
   var property=value.GetType().GetProperty(child,Flags);if(property==null)continue;
   var next=property.GetValue(value,null);if(next==null)continue;
   var list=next as IEnumerable;
   if(list!=null){foreach(var item in list)result.AddRange(Names(item));}
   else result.AddRange(Names(next));
  }
  return result;
 }
 static unsafe void Rename(object value,string oldName,string newName) {
  var property=value.GetType().GetProperty("Name",Flags);
  if(property.CanWrite){property.SetValue(value,newName,null);return;}
  FieldInfo field=null;
  foreach(string name in new string[]{"m_pkBone","m_pkSkeleton","m_pkTransformTrack"})
   if((field=value.GetType().GetField(name,Flags))!=null)break;
  if(field==null)throw new Exception("Unsupported native name field: "+value.GetType());
  // Granny bone, skeleton and transform-track structures start with a name
  // pointer. Validate it before touching a separately allocated loaded file.
  IntPtr address=(IntPtr)Pointer.Unbox(field.GetValue(value));
  if(Marshal.PtrToStringAnsi(Marshal.ReadIntPtr(address))!=oldName)
   throw new Exception("Native name layout mismatch");
  IntPtr text=Marshal.StringToHGlobalAnsi(newName);Strings.Add(text);
  Marshal.WriteIntPtr(address,text);
  if((string)property.GetValue(value,null)!=newName)throw new Exception("Name update failed");
 }
 static void Describe(object value,string label,int depth) {
  if(value==null || depth>3)return;
  Console.WriteLine(label+" TYPE "+value.GetType());
  foreach(var p in value.GetType().GetProperties(Flags)) {
   if(p.GetIndexParameters().Length>0)continue;
   object v;try{v=p.GetValue(value,null);}catch{continue;}
   if(p.PropertyType==typeof(string)) Console.WriteLine(label+"."+p.Name+"="+v+" WRITE="+p.CanWrite);
   if(p.Name=="Name" && (string)v=="CSC_TEST_TAILORS_Delivery_Rig" && !p.CanWrite)
    foreach(var field in value.GetType().GetFields(Flags))Console.WriteLine(" FIELD "+field.Name+" "+field.FieldType);
   if(p.Name=="Skeleton" || p.Name=="Bones" || p.Name=="TrackGroups" || p.Name=="TransformTracks" || p.Name=="BoneBindings") {
    var list=v as IEnumerable;
    if(list!=null){int i=0;foreach(var child in list)Describe(child,label+"."+p.Name+"["+(i++)+"]",depth+1);}
    else Describe(v,label+"."+p.Name,depth+1);
   }
  }
 }
 [STAThread] static int Main(string[] args) {
  try {
   Context.Add(new VirtualSpace());var asm=Assembly.LoadFrom("CivNexus6.exe");
   using(var form=(Form)Activator.CreateInstance(asm.GetType("NexusBuddy.CivNexusSixApplicationForm"))) {
    form.ShowInTaskbar=false;form.Opacity=0;
    var file=Context.Get<GrannyContext>().LoadGrannyFile(args[0]);
    if(args.Length==1) {
     foreach(var model in file.Models)Describe(model,"MODEL",0);
     foreach(var anim in file.Animations)Describe(anim,"ANIMATION",0);
    } else {
     if(args.Length!=4)throw new ArgumentException("input output old new");
     var values=new List<object>();
     foreach(var model in file.Models)values.AddRange(Names(model));
     foreach(var anim in file.Animations)values.AddRange(Names(anim));
     int count=0;
     foreach(var value in values) {
      var prop=value.GetType().GetProperty("Name",Flags);if(prop==null)continue;
      string name=(string)prop.GetValue(value,null);
      if(name==args[3])throw new Exception("Target name already present");
      if(name==args[2]){Rename(value,args[2],args[3]);count++;}
     }
     int expected=file.Models.Count>0?3:2;
     if(count!=expected)throw new Exception("Expected "+expected+" name changes, got "+count);
     form.GetType().GetMethod("SaveAsAction",Flags).Invoke(form,new object[]{file,args[1],false});
     var saved=Context.Get<GrannyContext>().LoadGrannyFile(args[1]);
     values.Clear();foreach(var m in saved.Models)values.AddRange(Names(m));foreach(var a in saved.Animations)values.AddRange(Names(a));
     int verified=0;
     foreach(var value in values) {
      var prop=value.GetType().GetProperty("Name",Flags);if(prop==null)continue;
      string name=(string)prop.GetValue(value,null);
      if(name==args[2])throw new Exception("Old name survived serialization");
      if(name==args[3])verified++;
     }
     if(verified!=expected)throw new Exception("Reloaded name count mismatch");
     Console.WriteLine("RENAMED_AND_RELOADED "+verified+" names");
    }
   }
   return 0;
  }catch(Exception e){Console.Error.WriteLine(e);return 1;}
 }
}
