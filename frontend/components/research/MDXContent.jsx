// Renders MDX article content server-side via next-mdx-remote/rsc.
// Must be used from a Server Component (the rendered tree can then be
// passed into client components as a prop/children).

import { MDXRemote } from "next-mdx-remote/rsc";
import remarkGfm from "remark-gfm";

export const mdxComponents = {
  h2: (props) => (
    <h2 className="font-display font-extrabold tracking-tight text-2xl text-ink mt-10 mb-4 scroll-mt-24" {...props} />
  ),
  h3: (props) => (
    <h3 className="font-display font-bold text-xl text-ink mt-7 mb-3" {...props} />
  ),
  p: (props) => <p className="text-stone-600 leading-relaxed mb-4" {...props} />,
  ul: (props) => <ul className="list-disc list-inside space-y-1.5 text-stone-600 mb-4" {...props} />,
  ol: (props) => <ol className="list-decimal list-inside space-y-1.5 text-stone-600 mb-4" {...props} />,
  li: (props) => <li className="text-stone-600" {...props} />,
  a: (props) => <a className="text-amber-700 font-semibold hover:underline" {...props} />,
  strong: (props) => <strong className="font-bold text-ink" {...props} />,
  blockquote: (props) => (
    <blockquote className="border-l-4 border-amber-400 pl-4 py-1 my-4 text-stone-600 italic bg-amber-50 rounded-r-lg" {...props} />
  ),
  table: (props) => (
    <div className="overflow-x-auto my-6">
      <table className="w-full text-sm border-collapse" {...props} />
    </div>
  ),
  th: (props) => (
    <th className="text-left px-4 py-3 bg-amber-50 text-amber-800 font-display font-bold border border-stone-200" {...props} />
  ),
  td: (props) => <td className="px-4 py-3 border border-stone-200 text-stone-600" {...props} />,
  hr: () => <hr className="my-8 border-stone-200" />,
  // Callout shortcode: <Callout type="tip">…</Callout>
  Callout: ({ type = "tip", children }) => {
    const styles = {
      tip: "bg-teal-50 border-teal-300 text-teal-800",
      warning: "bg-amber-50 border-amber-300 text-amber-800",
      info: "bg-stone-50 border-stone-300 text-stone-700",
    };
    const icons = { tip: "✅", warning: "⚠️", info: "ℹ️" };
    return (
      <div className={`border-l-4 rounded-r-xl px-5 py-4 my-5 ${styles[type] ?? styles.info}`}>
        <p className="font-display font-bold mb-1">
          {icons[type] ?? icons.info} {type.charAt(0).toUpperCase() + type.slice(1)}
        </p>
        <div className="text-sm leading-relaxed">{children}</div>
      </div>
    );
  },
};

export function MDXContent({ source }) {
  return (
    <MDXRemote
      source={source}
      components={mdxComponents}
      options={{ mdxOptions: { remarkPlugins: [remarkGfm] } }}
    />
  );
}
