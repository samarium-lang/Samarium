// @ts-check
const codeBlocks = document.querySelectorAll("pre.sm");

fetch("https://raw.githubusercontent.com/samarium-lang/vscode-samarium/master/syntaxes/samarium.tmLanguage.json")
  .then((data) => data.json())
  .then((grammar) => ({
    id: "samarium",
    scopeName: "source.samarium",
    grammar,
  }))
  .then(async (sm) => shiki.getHighlighter({ theme: "github-dark", langs: [sm] }))
  .then((h) => {
    [...codeBlocks].forEach((block) => {
      block.innerHTML = highlight(h, block.innerText);
    });
  });

function highlight(h, code) {
  return h.codeToHtml(code, { lang: "samarium" });
}
