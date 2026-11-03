import { QuartzConfig } from "./quartz/cfg"
import * as Plugin from "./quartz/plugins"

// Selected only by the handbook builder. The public CSC build keeps its config.
export function aiHandbookConfig(base: QuartzConfig): QuartzConfig {
  return {
    ...base,
    configuration: {
      ...base.configuration,
      pageTitle: "Civilization VI AI",
      baseUrl: process.env.CSC_AI_BASE_URL || "localhost:8091",
      theme: {
        ...base.configuration.theme,
        fontOrigin: "local",
        typography: {
          header: "Segoe UI",
          body: "Segoe UI",
          code: "Consolas",
        },
      },
    },
    plugins: {
      ...base.plugins,
      transformers: [
        Plugin.FrontMatter(),
        Plugin.CreatedModifiedDate({ priority: ["frontmatter", "filesystem"] }),
        Plugin.SyntaxHighlighting({ keepBackground: false }),
        Plugin.ObsidianFlavoredMarkdown({ enableInHtmlEmbed: false }),
        Plugin.GitHubFlavoredMarkdown(),
        Plugin.TableOfContents(),
        Plugin.CrawlLinks({ markdownLinkResolution: "relative" }),
        Plugin.Description(),
      ],
      // No generated social images, remote fonts, RSS or sitemap for this research build.
      emitters: [Plugin.AliasRedirects(), Plugin.ComponentResources(), Plugin.ContentPage(),
        Plugin.FolderPage(), Plugin.TagPage(),
        Plugin.ContentIndex({ enableSiteMap: false, enableRSS: false }),
        Plugin.Assets(), Plugin.Static(), Plugin.Favicon(), Plugin.NotFoundPage()],
    },
  }
}
