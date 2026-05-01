using System;
using System.IO;
using System.Reflection;
using System.Windows.Forms;
using Firaxis.IO;
using Firaxis.Utility;
using Firaxis.Granny;

namespace CSCTools
{
    class FGXToCN6
    {
        [STAThread]
        static int Main(string[] args)
        {
            if (args.Length < 2)
            {
                Console.WriteLine("Usage: FGXToCN6.exe <input.fgx> <output.cn6>");
                return 1;
            }

            string fgxPath = args[0];
            string cn6Path = args[1];
            int exitCode = 0;

            try
            {
                Context.Add(new VirtualSpace());
                Assembly cn6Asm = Assembly.LoadFrom("CivNexus6.exe");
                BindingFlags bf = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static;
                BindingFlags bfi = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance;

                // Extract templates (needed by form init)
                string[] tNames = { "model_template.fgx", "model_template_2uv.fgx", "model_template_3uv.fgx" };
                string[] templatePaths = new string[3];
                for (int i = 0; i < 3; i++)
                {
                    templatePaths[i] = Path.Combine(Path.GetTempPath(), "csc_" + tNames[i]);
                    if (!File.Exists(templatePaths[i]))
                    {
                        using (Stream rs = cn6Asm.GetManifestResourceStream("NexusBuddy.GrannyTemplates." + tNames[i]))
                        using (FileStream fs = File.Create(templatePaths[i]))
                            rs.CopyTo(fs);
                    }
                }

                // Create form (hidden)
                Type formType = cn6Asm.GetType("NexusBuddy.CivNexusSixApplicationForm");
                Form appForm = (Form)Activator.CreateInstance(formType);
                appForm.WindowState = FormWindowState.Minimized;
                appForm.ShowInTaskbar = false;
                appForm.Opacity = 0;

                formType.GetField("modelTemplateFilename", bfi).SetValue(appForm, templatePaths[0]);
                formType.GetField("modelTemplateFilename2", bfi).SetValue(appForm, templatePaths[1]);
                formType.GetField("modelTemplateFilename3", bfi).SetValue(appForm, templatePaths[2]);

                appForm.Shown += (s, e) =>
                {
                    try
                    {
                        // Load the FGX via the form's OpenFileAsTempFileCopy
                        // Actually, simpler: load directly and use cn6Export
                        IGrannyFile grannyFile = new GrannyFileLoader().LoadGrannyFile(fgxPath);
                        Console.WriteLine("Loaded: " + grannyFile.Meshes.Count + " meshes");

                        // Get mesh infos using wrapper
                        Type mwType = cn6Asm.GetType("NexusBuddy.GrannyWrappers.GrannyMeshWrapper");

                        // Build CN6 text output manually (same format as Blender addon)
                        using (StreamWriter writer = new StreamWriter(cn6Path))
                        {
                            writer.WriteLine("// CivNexus6 CN6 - Exported from FGX via CSC pipeline");
                            writer.WriteLine("skeleton");

                            // Write world bone
                            string modelName = grannyFile.Models.Count > 0 ? grannyFile.Models[0].Name : "Model";
                            writer.WriteLine(string.Format("0 \"{0}\" -1 0.00000000 0.00000000 0.00000000 0.00000000 0.00000000 0.00000000 1.00000000 1.00000000 0.00000000 0.00000000 0.00000000 0.00000000 1.00000000 0.00000000 0.00000000 0.00000000 0.00000000 1.00000000 0.00000000 0.00000000 0.00000000 0.00000000 1.00000000", modelName));

                            // Write meshes
                            writer.WriteLine("meshes:" + grannyFile.Meshes.Count);

                            for (int mi = 0; mi < grannyFile.Meshes.Count; mi++)
                            {
                                object mw = Activator.CreateInstance(mwType, new object[] { grannyFile.Meshes[mi] });
                                object meshInfo = mwType.GetMethod("getMeshInfo", bfi).Invoke(mw, null);

                                Type miType = meshInfo.GetType();
                                string meshName = (string)miType.GetField("name").GetValue(meshInfo);
                                var vertices = (System.Collections.IList)miType.GetField("vertices").GetValue(meshInfo);
                                var triangles = (System.Collections.IList)miType.GetField("triangles").GetValue(meshInfo);
                                var matBindingNames = (System.Collections.IList)miType.GetField("materialBindingNames").GetValue(meshInfo);

                                writer.WriteLine("mesh:\"" + meshName + "\"");
                                writer.WriteLine("materials");
                                if (matBindingNames != null)
                                    foreach (string mat in matBindingNames)
                                        writer.WriteLine("\"" + mat + "\"");

                                // Write vertices
                                writer.WriteLine("vertices");
                                Type viType = null;
                                foreach (object v in vertices)
                                {
                                    if (viType == null) viType = v.GetType();
                                    float[] pos = (float[])viType.GetField("position").GetValue(v);
                                    float[] norm = (float[])viType.GetField("normal").GetValue(v);
                                    float[] tang = (float[])viType.GetField("tangent").GetValue(v);
                                    float[] bino = (float[])viType.GetField("binormal").GetValue(v);
                                    float[] uv = (float[])viType.GetField("uv").GetValue(v);
                                    float[] uv2 = (float[])viType.GetField("uv2").GetValue(v);
                                    float[] uv3 = (float[])viType.GetField("uv3").GetValue(v);

                                    writer.Write(string.Format("{0:F8} {1:F8} {2:F8} ", pos[0], pos[1], pos[2]));
                                    writer.Write(string.Format("{0:F8} {1:F8} {2:F8} ", norm[0], norm[1], norm[2]));
                                    writer.Write(string.Format("{0:F8} {1:F8} {2:F8} ", tang[0], tang[1], tang[2]));
                                    writer.Write(string.Format("{0:F8} {1:F8} {2:F8} ", bino[0], bino[1], bino[2]));
                                    writer.Write(string.Format("{0:F8} {1:F8} ", uv[0], uv[1]));
                                    writer.Write(string.Format("{0:F8} {1:F8} ", uv2 != null ? uv2[0] : 0, uv2 != null ? uv2[1] : 0));
                                    writer.Write(string.Format("{0:F8} {1:F8} ", uv3 != null ? uv3[0] : 0, uv3 != null ? uv3[1] : 0));
                                    writer.WriteLine("1 1 1 1 1 1 1 1 255 0 0 0 0 0 0 0");
                                }

                                // Write triangles
                                writer.WriteLine("triangles");
                                foreach (object tri in triangles)
                                {
                                    int[] t = (int[])tri;
                                    writer.WriteLine(string.Format("{0} {1} {2} 0", t[0], t[1], t[2]));
                                }
                            }

                            writer.WriteLine("end");
                        }

                        Console.WriteLine("OK: " + cn6Path);
                    }
                    catch (Exception ex)
                    {
                        Exception inner = ex.InnerException ?? ex;
                        Console.WriteLine("ERROR: " + inner.Message);
                        Console.WriteLine("STACK: " + inner.StackTrace);
                        exitCode = 1;
                    }
                    finally { appForm.Close(); }
                };

                Application.Run(appForm);
            }
            catch (Exception ex)
            {
                Console.WriteLine("INIT ERROR: " + ex.Message);
                exitCode = 1;
            }

            return exitCode;
        }
    }
}
