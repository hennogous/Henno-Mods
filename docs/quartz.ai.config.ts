import { QuartzConfig } from "./quartz/cfg"
import * as Plugin from "./quartz/plugins"
import * as Component from "./quartz/components"
import AIReaderNav from "./quartz/components/AIReaderNav"
import AIPageContext from "./quartz/components/AIPageContext"

// Selected only by the handbook builder. The public CSC build keeps its config.
export function aiHandbookConfig(base: QuartzConfig): QuartzConfig {
  const readerLayout = {
    header: [Component.MobileOnly(AIReaderNav())],
    beforeBody: [AIPageContext(), Component.ArticleTitle(), Component.ContentMeta({ showReadingTime: true })],
    left: [Component.PageTitle(), Component.MobileOnly(Component.Spacer()),
      Component.Flex({ components: [{ Component: Component.Search({ enablePreview: false, aiReaderScope: true }), grow: true },
        { Component: Component.Darkmode() }] }), Component.DesktopOnly(AIReaderNav())],
    right: [Component.DesktopOnly(Component.TableOfContents())],
    footer: Component.Footer({ links: {
      "CSC documentation": "https://hennogous.github.io/Henno-Mods/",
      "Source & evidence": "https://github.com/hennogous/Henno-Mods/tree/main/project/docs/civ6-ai",
    } }),
  }
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
      emitters: [Plugin.AliasRedirects(), Plugin.ComponentResources(), Plugin.ContentPage(readerLayout),
        Plugin.FolderPage(readerLayout), Plugin.TagPage(readerLayout),
        Plugin.ContentIndex({ enableSiteMap: false, enableRSS: false }),
        Plugin.Assets(), Plugin.Static(), Plugin.Favicon(), Plugin.NotFoundPage()],
    },
  }
}
