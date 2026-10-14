using System;
using System.IO;
using System.Reflection;
using System.Collections;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using System.Windows.Forms;
using System.Runtime.InteropServices;
using System.Web.Script.Serialization;
using NexusBuddy.GrannyWrappers;
using NexusBuddy.GrannyInfos;
using Firaxis.IO;
using Firaxis.Utility;
using Firaxis.Granny;

namespace CSCTools
{
    class CN6ToFGX
    {
        // Firaxis' installed x64 Granny wrappers use packed 44-byte member descriptors.
        // Extend the known skinned template, retaining its bone/material setup.
        // No SDK assets or proprietary template copies need to be distributed.
        static string MakeSkinnedTemplate(string source, string destination, int uvCount, Form form)
        {
            if (IntPtr.Size != 8) throw new PlatformNotSupportedException("The Firaxis bridge must run as x64");
            var file = new GrannyFileLoader().LoadGrannyFile(source);
            var mesh = file.Models[0].MeshBindings[0];
            var wrapper = new GrannyMeshWrapper(mesh);
            var info = new GrannyMeshInfo();
            info.setVertexStructInfos((List<GrannyMeshVertexStructInfo>)typeof(GrannyMeshWrapper)
                .GetMethod("getVertexStructInfos", BindingFlags.Instance | BindingFlags.NonPublic)
                .Invoke(wrapper,null));
            if (info.getVertexStructInfoByName("BoneWeights") == null ||
                info.getVertexStructInfoByName("BoneIndices") == null)
                throw new InvalidDataException("Base template does not contain skinning");
            var uv = info.getVertexStructInfoByName("TextureCoordinates0");
            if (uv == null || uv.type != 10 || uv.count != 3)
                throw new InvalidDataException("Unexpected Firaxis template UV layout");
            IntPtr data = Marshal.ReadIntPtr(wrapper.getPrimaryVertexDataPtr());
            IntPtr oldType = Marshal.ReadIntPtr(data);
            int oldCount = info.vertexStructInfos.Count;
            int newCount = oldCount + uvCount - 1;
            byte[] members = new byte[(newCount + 1) * 44];
            Marshal.Copy(oldType, members, 0, oldCount * 44);
            int uvMember = info.vertexStructInfos.FindIndex(x => x.name == "TextureCoordinates0");
            for (int channel = 1; channel < uvCount; channel++)
                Buffer.BlockCopy(members, uvMember * 44, members, (oldCount + channel - 1) * 44, 44);
            IntPtr newType = Marshal.AllocHGlobal(members.Length);
            Marshal.Copy(members, 0, newType, members.Length);
            for (int channel = 1; channel < uvCount; channel++)
                Marshal.WriteIntPtr(newType, (oldCount + channel - 1) * 44 + 4,
                    Marshal.StringToHGlobalAnsi("TextureCoordinates" + channel));
            int oldStride = info.bytesPerVertex, newStride = oldStride + (uvCount - 1) * 12;
            int count = wrapper.getNumVertices();
            byte[] oldBytes = new byte[count * oldStride], newBytes = new byte[count * newStride];
            Marshal.Copy(Marshal.ReadIntPtr(wrapper.getVerticesPtr()), oldBytes, 0, oldBytes.Length);
            for (int i = 0; i < count; i++)
            {
                Buffer.BlockCopy(oldBytes, i * oldStride, newBytes, i * newStride, oldStride);
                for (int channel = 1; channel < uvCount; channel++)
                    Buffer.BlockCopy(oldBytes, i * oldStride + uv.offset, newBytes,
                        i * newStride + oldStride + (channel - 1) * 12, 12);
            }
            IntPtr vertices = Marshal.AllocHGlobal(newBytes.Length);
            Marshal.Copy(newBytes, 0, vertices, newBytes.Length);
            Marshal.WriteIntPtr(data, newType);
            Marshal.WriteIntPtr(wrapper.getVerticesPtr(), vertices);
            form.GetType().GetMethod("SaveAsAction", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic)
                .Invoke(form, new object[] {file, destination, false});
            return destination;
        }

        static float Compare(float[] expected, float[] actual, int count, string label)
        {
            float max = 0;
            for (int i = 0; i < count; i++)
            {
                if (float.IsNaN(actual[i]) || float.IsInfinity(actual[i]))
                    throw new InvalidDataException("Nonfinite " + label);
                max = Math.Max(max, Math.Abs(expected[i] - actual[i]));
            }
            if (max > 0.0001f) throw new InvalidDataException(label + " differs after FGX save: " + max);
            return max;
        }

        static void ValidateSkinnedData(Assembly asm, string cn6Path, string fgxPath, int uvCount)
        {
            var ops = asm.GetType("NexusBuddy.FileOps.CN6FileOps");
            var flags = BindingFlags.Static | BindingFlags.NonPublic | BindingFlags.Public;
            var models = (IList)ops.GetMethod("loadModelInfos", flags).Invoke(null, new object[] {cn6Path, 0});
            var file = new GrannyFileLoader().LoadGrannyFile(fgxPath);
            var rows = new List<object>();
            if (models.Count != file.Models.Count) throw new InvalidDataException("Model count changed");
            float maxPosition = 0, maxUV = 0;
            for (int modelIndex = 0; modelIndex < models.Count; modelIndex++)
            {
                var model = models[modelIndex];
                ops.GetMethod("doBoneBindings", flags).Invoke(null, new object[] {model});
                var expectedMeshes = (List<GrannyMeshInfo>)model.GetType().GetField("meshBindings").GetValue(model);
                var actualModel = file.Models[modelIndex];
                if (actualModel.MeshBindings.Count != expectedMeshes.Count) throw new InvalidDataException("Mesh bindings changed");
                for (int m = 0; m < expectedMeshes.Count; m++)
                {
                    var expected = expectedMeshes[m];
                    var actual = new GrannyMeshWrapper(actualModel.MeshBindings[m]).getMeshInfo();
                    if (expected.name != actual.name || expected.vertices.Count != actual.vertices.Count ||
                        expected.triangles.Count != actual.triangles.Count)
                        throw new InvalidDataException("Mesh identity/topology counts changed");
                    if (actual.getVertexStructInfoByName("BoneWeights") == null ||
                        actual.getVertexStructInfoByName("BoneIndices") == null)
                        throw new InvalidDataException("Output lost skinning");
                    for (int u = 0; u < uvCount; u++)
                        if (actual.getVertexStructInfoByName("TextureCoordinates" + u) == null)
                            throw new InvalidDataException("Output lost UV channel " + u);
                    for (int i = 0; i < expected.vertices.Count; i++)
                    {
                        var a = expected.vertices[i]; var b = actual.vertices[i];
                        maxPosition = Math.Max(maxPosition, Compare(a.position, b.position, 3, "Position"));
                        Compare(a.normal,b.normal,3,"Normal");
                        maxUV = Math.Max(maxUV, Compare(a.uv,b.uv,2,"UV1"));
                        if (uvCount > 1) maxUV = Math.Max(maxUV, Compare(a.uv2,b.uv2,2,"UV2"));
                        if (uvCount > 2) maxUV = Math.Max(maxUV, Compare(a.uv3,b.uv3,2,"UV3"));
                        int total = 0;
                        for (int j = 0; j < 8; j++)
                        {
                            total += b.boneWeights[j];
                            if (a.boneWeights[j] != b.boneWeights[j] ||
                                (a.boneWeights[j] > 0 && expected.boneBindings[a.boneIndices[j]] != actual.boneBindings[b.boneIndices[j]]))
                                throw new InvalidDataException("Output changed bone weights/bindings");
                        }
                        if (total != 255) throw new InvalidDataException("Weights must sum to 255");
                    }
                    for (int i = 0; i < expected.triangles.Count; i++)
                        for (int j = 0; j < 4; j++)
                            if (expected.triangles[i][j] != actual.triangles[i][j])
                                throw new InvalidDataException("Output changed triangle/material indices");
                    rows.Add(new {name=actual.name, vertices=actual.vertices.Count, uv_maps=uvCount,
                        bound_bones=actual.boneBindings, stride=actual.bytesPerVertex});
                }
            }
            File.WriteAllText(fgxPath + ".validation.json", new JavaScriptSerializer().Serialize(new {
                verified=true, skinning=true, meshes=rows, max_position_error=maxPosition, max_uv_error=maxUV}));
            Console.WriteLine("Verified saved FGX positions, normals, UVs, triangles and skin weights");
        }

        static void ValidateMeshNames(string cn6Path, string fgxPath)
        {
            var expected = new List<string>();
            foreach (string line in File.ReadLines(cn6Path))
            {
                Match match = Regex.Match(line.Trim(), "^mesh:\"([^\"]+)\"");
                if (match.Success) expected.Add(match.Groups[1].Value);
            }
            IGrannyFile file = new GrannyFileLoader().LoadGrannyFile(fgxPath);
            if (file.Meshes.Count != expected.Count)
                throw new InvalidDataException("Converted FGX mesh count differs from CN6");
            for (int i = 0; i < expected.Count; i++)
                if (file.Meshes[i].Name != expected[i])
                    throw new InvalidDataException("Converted FGX mesh name differs from CN6: expected "
                        + expected[i] + ", got " + file.Meshes[i].Name
                        + ". Normalize names consistently in CN6, GEO and AST before conversion.");
            Console.WriteLine("Verified " + expected.Count + " FGX mesh names against CN6");
        }

        [STAThread]
        static int Main(string[] args)
        {
            if (args.Length < 3)
            {
                Console.WriteLine("Usage: CN6ToFGX.exe <input.cn6> <output.fgx> <vertexFormat> [--skinned]");
                Console.WriteLine("  vertexFormat: 0=1UV skinned, 1=2UV static, 2=3UV static; --skinned preserves weights for every UV count");
                return 1;
            }

            string cn6Path = args[0];
            string fgxPath = args[1];
            int vertexFormat = int.Parse(args[2]);
            if (vertexFormat < 0 || vertexFormat > 2 || (args.Length > 3 && args[3] != "--skinned")) return 1;
            bool skinned = vertexFormat == 0 || args.Length > 3;
            int exitCode = 0;
            string scratch = Path.Combine(Path.GetTempPath(), "csc_fgx_" + Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(scratch);

            try
            {
                Context.Add(new VirtualSpace());
                
                Assembly cn6Asm = Assembly.LoadFrom("CivNexus6.exe");
                BindingFlags bf = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static;
                BindingFlags bfi = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance;
                
                // Extract templates
                string[] tNames = { "model_template.fgx", "model_template_2uv.fgx", "model_template_3uv.fgx" };
                string[] templatePaths = new string[3];
                for (int i = 0; i < 3; i++)
                {
                    templatePaths[i] = Path.Combine(scratch, tNames[i]);
                    using (Stream rs = cn6Asm.GetManifestResourceStream("NexusBuddy.GrannyTemplates." + tNames[i]))
                    using (FileStream fs = File.Create(templatePaths[i]))
                        rs.CopyTo(fs);
                }
                
                // Create the ACTUAL CivNexus6 application form (hidden)
                Type formType = cn6Asm.GetType("NexusBuddy.CivNexusSixApplicationForm");
                Form appForm = (Form)Activator.CreateInstance(formType);
                appForm.WindowState = FormWindowState.Minimized;
                appForm.ShowInTaskbar = false;
                appForm.Opacity = 0;
                
                // Set the template filename fields
                formType.GetField("modelTemplateFilename", bfi).SetValue(appForm, templatePaths[0]);
                formType.GetField("modelTemplateFilename2", bfi).SetValue(appForm, templatePaths[1]);
                formType.GetField("modelTemplateFilename3", bfi).SetValue(appForm, templatePaths[2]);
                Console.WriteLine("Form created, templates set");
                
                appForm.Shown += (s, e) =>
                {
                    try
                    {
                        if (skinned && vertexFormat > 0)
                        {
                            string prepared = MakeSkinnedTemplate(templatePaths[0], Path.Combine(scratch,"skinned.fgx"),vertexFormat+1,appForm);
                            formType.GetField(vertexFormat==1 ? "modelTemplateFilename2" : "modelTemplateFilename3",bfi).SetValue(appForm,prepared);
                        }
                        // Now importCN6 can access getTemplateFilename via the form
                        Type cn6Ops = cn6Asm.GetType("NexusBuddy.FileOps.CN6FileOps");
                        GrannyContext gc = new GrannyContext();
                        
                        cn6Ops.GetMethod("importCN6", bf)
                            .Invoke(null, new object[] { cn6Path, fgxPath, gc, vertexFormat });
                        
                        if (File.Exists(fgxPath))
                        {
                            ValidateMeshNames(cn6Path, fgxPath);
                            if (skinned) ValidateSkinnedData(cn6Asm,cn6Path,fgxPath,vertexFormat+1);
                            Console.WriteLine("OK: " + new FileInfo(fgxPath).Length + " bytes");
                        }
                        else
                        {
                            Console.WriteLine("ERROR: Output not created");
                            exitCode = 1;
                        }
                    }
                    catch (TargetInvocationException tex)
                    {
                        Console.WriteLine("ERROR: " + (tex.InnerException ?? tex).Message);
                        Console.WriteLine("STACK: " + (tex.InnerException ?? tex).StackTrace);
                        exitCode = 1;
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine("ERROR: " + ex.ToString());
                        exitCode = 1;
                    }
                    finally { appForm.Close(); }
                };
                
                Application.Run(appForm);
            }
            catch (Exception ex)
            {
                Console.WriteLine("INIT ERROR: " + ex.Message);
                if (ex.InnerException != null)
                    Console.WriteLine("INNER: " + ex.InnerException.Message);
                exitCode = 1;
            }

            return exitCode;
        }
    }
}
