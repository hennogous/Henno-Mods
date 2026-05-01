using System;
using System.IO;
using System.Reflection;
using System.Collections;
using System.Windows.Forms;
using Firaxis.IO;
using Firaxis.Utility;
using Firaxis.Granny;

namespace CSCTools
{
    class CN6ToFGX
    {
        [STAThread]
        static int Main(string[] args)
        {
            if (args.Length < 3)
            {
                Console.WriteLine("Usage: CN6ToFGX.exe <input.cn6> <output.fgx> <vertexFormat>");
                Console.WriteLine("  vertexFormat: 0=1UV, 1=2UV, 2=3UV (No Bone Bindings)");
                return 1;
            }

            string cn6Path = args[0];
            string fgxPath = args[1];
            int vertexFormat = int.Parse(args[2]);
            int exitCode = 0;

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
                    templatePaths[i] = Path.Combine(Path.GetTempPath(), "csc_" + tNames[i]);
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
                        // Now importCN6 can access getTemplateFilename via the form
                        Type cn6Ops = cn6Asm.GetType("NexusBuddy.FileOps.CN6FileOps");
                        GrannyContext gc = new GrannyContext();
                        
                        cn6Ops.GetMethod("importCN6", bf)
                            .Invoke(null, new object[] { cn6Path, fgxPath, gc, vertexFormat });
                        
                        if (File.Exists(fgxPath))
                            Console.WriteLine("OK: " + new FileInfo(fgxPath).Length + " bytes");
                        else
                            Console.WriteLine("ERROR: Output not created");
                    }
                    catch (TargetInvocationException tex)
                    {
                        Console.WriteLine("ERROR: " + (tex.InnerException ?? tex).Message);
                        Console.WriteLine("STACK: " + (tex.InnerException ?? tex).StackTrace);
                        exitCode = 1;
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine("ERROR: " + ex.Message);
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
