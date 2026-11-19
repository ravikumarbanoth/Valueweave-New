// Render research-article MDX to React elements WITHOUT evaluating code.
//
// WHY THIS EXISTS
// ---------------
// Articles were rendered with next-mdx-remote's compileMDX, which compiles the
// MDX to JavaScript and then runs that JavaScript with `new Function`.
// Cloudflare Workers forbid generating code from strings, so on Workers that
// call throws "Code generation from strings disallowed for this context". The
// page's existing catch then falls back to plain `marked` HTML — silently, so
// every article would lose its Callouts and its themed headings, lists and
// tables while still "working".
//
// This renders the same source through the same parser MDX itself uses
// (unified + remark-parse + remark-mdx + remark-gfm + remark-rehype, the exact
// versions @mdx-js/mdx depends on), then turns the tree into React elements
// with hast-util-to-jsx-runtime against the same `components` object. Nothing
// is compiled to JavaScript and nothing is evaluated, so it behaves the same on
// Node (Vercel) and on Workers. tests/test_research_registry.py renders every
// article both ways on Node and requires byte-identical HTML.
//
// WHAT IT DOES NOT DO: MDX expressions (`{...}`), expression attributes and
// import/export need real evaluation. They throw here, and renderBody's
// existing fallback renders the article as plain markdown — the path a stray
// "{" in admin-typed content already takes today. No current article uses any
// of them.

import { unified } from "unified";
import remarkParse from "remark-parse";
import remarkMdx from "remark-mdx";
import remarkGfm from "remark-gfm";
import remarkRehype from "remark-rehype";
import { toJsxRuntime } from "hast-util-to-jsx-runtime";
import { visit } from "unist-util-visit";
import { Fragment, jsx, jsxs } from "react/jsx-runtime";

// MDX node types remark-rehype hands through untouched, as @mdx-js/mdx does.
const MDX_NODE_TYPES = [
  "mdxFlowExpression",
  "mdxJsxFlowElement",
  "mdxJsxTextElement",
  "mdxTextExpression",
  "mdxjsEsm",
];

// Explicitly written lowercase JSX (`<a href>` typed as JSX rather than made
// by markdown) is renamed to this prefix so the components map is NOT applied
// to it — MDX's own rule: components replace markdown-produced elements, and
// a literal `<a>` in the source stays a plain <a>.
const RAW = "__vwRaw_";

/**
 * The two MDX-specific steps @mdx-js/mdx performs between parsing and HTML
 * (its internal remark-mark-and-unravel plugin, reproduced here):
 *   1. a paragraph holding only JSX elements/expressions and whitespace is
 *      replaced by those elements, so a one-line <Callout>…</Callout> is a
 *      block, not a block inside <p>;
 *   2. explicitly written JSX is remembered as explicit (here: lowercase names
 *      are renamed so the components map leaves them alone).
 */
function remarkMdxParity() {
  return (tree) => {
    visit(tree, (node, index, parent) => {
      if (parent && typeof index === "number" && node.type === "paragraph") {
        let all = true;
        let oneOrMore = false;
        for (const child of node.children) {
          if (child.type === "mdxJsxTextElement" || child.type === "mdxTextExpression") oneOrMore = true;
          else if (!(child.type === "text" && /^[\t\n\f\r ]*$/.test(child.value))) { all = false; break; }
        }
        if (all && oneOrMore) {
          const next = [];
          for (const child of node.children) {
            if (child.type === "mdxJsxTextElement") child.type = "mdxJsxFlowElement";
            if (child.type === "mdxTextExpression") child.type = "mdxFlowExpression";
            if (!(child.type === "text" && /^[\t\r\n ]+$/.test(String(child.value)))) next.push(child);
          }
          parent.children.splice(index, 1, ...next);
          return index;
        }
      }
      if ((node.type === "mdxJsxFlowElement" || node.type === "mdxJsxTextElement")
          && typeof node.name === "string" && /^[a-z]/.test(node.name) && !node.name.includes(".")) {
        node.name = RAW + node.name;
      }
    });
  };
}

// hast-util-to-jsx-runtime asks an "evaluater" to resolve capitalised JSX
// names (`Callout`) and any expression. This one INTERPRETS a syntax tree; it
// never turns a string into code. It resolves a bare identifier to the
// matching component (or, for the renamed raw tags, to the plain HTML tag) and
// a literal to its value. Anything else — a function call, an object, a
// variable — is refused, which lands on renderBody's markdown fallback.
function createEvaluater(components) {
  const refuse = () => {
    throw new Error("MDX expression requires evaluation, which is not available here");
  };
  return () => ({
    evaluateExpression(node) {
      if (node.type === "Identifier") {
        if (node.name.startsWith(RAW)) return node.name.slice(RAW.length);
        if (Object.prototype.hasOwnProperty.call(components, node.name)) return components[node.name];
        // compileMDX throws for an undefined component too; same outcome.
        throw new Error(`Expected component \`${node.name}\` to be defined`);
      }
      if (node.type === "Literal") return node.value;
      return refuse();
    },
    evaluateProgram: refuse,
  });
}

const processor = unified()
  .use(remarkParse)
  .use(remarkMdx)
  .use(remarkGfm)
  .use(remarkMdxParity)
  .use(remarkRehype, { allowDangerousHtml: true, passThrough: MDX_NODE_TYPES });

/**
 * MDX source → React element tree. Throws on content that cannot be rendered
 * without evaluation or that is not valid MDX; callers keep their existing
 * fallback for that case.
 */
export function renderMdx(source, components = {}) {
  const tree = processor.runSync(processor.parse(String(source ?? "")));
  return toJsxRuntime(tree, {
    Fragment,
    jsx,
    jsxs,
    components,
    createEvaluater: createEvaluater(components),
    elementAttributeNameCase: "react",
    stylePropertyNameCase: "dom",
  });
}
