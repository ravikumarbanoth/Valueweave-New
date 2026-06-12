import { getAllArticleSlugs } from "@/lib/mdx";
import ArticleEditor from "../ArticleEditor";

export default function EditArticlePage({ params }) {
  return <ArticleEditor id={params.id} mdxSlugs={getAllArticleSlugs({ includeDrafts: true })} />;
}
