import { getAllArticleSlugs } from "@/lib/mdx";
import ArticleEditor from "../ArticleEditor";

export default async function EditArticlePage(props) {
  const params = await props.params;
  return <ArticleEditor id={params.id} mdxSlugs={getAllArticleSlugs({ includeDrafts: true })} />;
}
