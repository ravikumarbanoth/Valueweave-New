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
// EXPRESSIONS ARE REMOVED, NOT EVALUATED — exactly as in production today.
// next-mdx-remote v6 blocks JavaScript in MDX by default (`blockJS`): before
// compiling it deletes every `{...}` expression, every expression-valued JSX
// attribute and every import/export. So on the live site `Two plus two is
// {2 + 2}.` renders as "Two plus two is ." with the rest of the article intact.
// The two plugins below reproduce those removals (next-mdx-remote's
// removeJavaScriptExpressions and removeImportsExportsPlugin), in the same
// position in the pipeline, so this renderer matches it for such content too.
// Content that is not valid MDX at all (a stray "{") still throws, and
// renderBody falls back to plain markdown as before.

import { unified } from "unified";
import remarkParse from "remark-parse";
import remarkMdx from "remark-mdx";
import remarkGfm from "remark-gfm";
import remarkRehype from "remark-rehype";
import { toJsxRuntime } from "hast-util-to-jsx-runtime";
import { visit, SKIP } from "unist-util-visit";
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
// names (`Callout`). This one INTERPRETS a syntax tree; it never turns a
// string into code. It resolves a bare identifier to the matching component
// (or, for the renamed raw tags, to the plain HTML tag) and a literal to its
// value. Expressions never reach it — they are removed above, as in
// production — and anything else is refused.
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

// next-mdx-remote's removeImportsExportsPlugin: drop import/export statements.
function remarkRemoveEsm() {
  return (tree) => {
    visit(tree, "mdxjsEsm", (node, index, parent) => {
      if (parent && typeof index === "number") {
        parent.children.splice(index, 1);
        return [SKIP, index];
      }
    });
  };
}

// next-mdx-remote's removeJavaScriptExpressions (its default `blockJS`):
// drop `{...}` expressions, expression-valued JSX attributes and spreads.
function remarkRemoveExpressions() {
  return (tree) => {
    visit(tree, (node, index, parent) => {
      if (node.type === "mdxFlowExpression" || node.type === "mdxTextExpression") {
        if (parent && typeof index === "number") {
          parent.children.splice(index, 1);
          return [SKIP, index];
        }
      }
      if ((node.type === "mdxJsxFlowElement" || node.type === "mdxJsxTextElement") && node.attributes) {
        node.attributes = node.attributes.filter((attr) =>
          attr.type === "mdxJsxAttribute"
            ? attr.value === null || typeof attr.value === "string"
              || (attr.value && attr.value.type !== "mdxJsxAttributeValueExpression")
            : attr.type !== "mdxJsxExpressionAttribute"
        );
      }
    });
  };
}

// The same order as compileMDX: MDX's own unravelling first, then the page's
// remark plugins (remark-gfm), then next-mdx-remote's two removals.
const processor = unified()
  .use(remarkParse)
  .use(remarkMdx)
  .use(remarkMdxParity)
  .use(remarkGfm)
  .use(remarkRemoveEsm)
  .use(remarkRemoveExpressions)
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
