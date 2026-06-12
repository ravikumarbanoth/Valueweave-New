import { getAllArticleSlugs } from "@/lib/mdx";
import ArticleEditor from "../ArticleEditor";

export default function NewArticlePage() {
  return <ArticleEditor mdxSlugs={getAllArticleSlugs({ includeDrafts: true })} />;
}
