import * as vscode from 'vscode';

export function escapeHtml(text: unknown): string {
  return String(text ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

/** Tiny, safe markdown: ```code```, `inline`, **bold**, "- " / "1. " lists, paragraphs. */
export function renderMarkdown(text: string): string {
  const blocks: string[] = [];
  let src = escapeHtml(text).replace(/```[a-zA-Z0-9_+-]*\n?([\s\S]*?)```/g, (_m, code) => {
    blocks.push(`<pre><code>${code.replace(/\n$/, '')}</code></pre>`);
    return `\u0000${blocks.length - 1}\u0000`;
  });
  src = src
    .replace(/`([^`\n]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*\n]+)\*\*/g, '<strong>$1</strong>');
  const html = src.split(/\n{2,}/).map(par => {
    const lines = par.split('\n');
    if (lines.every(l => /^\s*(-|\d+\.)\s+/.test(l))) {
      const ordered = /^\s*\d+\./.test(lines[0]);
      const items = lines.map(l => `<li>${l.replace(/^\s*(-|\d+\.)\s+/, '')}</li>`).join('');
      return ordered ? `<ol>${items}</ol>` : `<ul>${items}</ul>`;
    }
    return /^\u0000\d+\u0000$/.test(par.trim()) ? par : `<p>${lines.join('<br>')}</p>`;
  }).join('');
  return html.replace(/\u0000(\d+)\u0000/g, (_m, i) => blocks[Number(i)]);
}

function nonce(): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  return Array.from({ length: 32 }, () => chars.charAt(Math.floor(Math.random() * chars.length))).join('');
}

/** A page that follows the VS Code theme; `script` runs with acquireVsCodeApi() available as `vscode`. */
export function page(webview: vscode.Webview, title: string, body: string, script = ''): string {
  const n = nonce();
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'nonce-${n}';">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${escapeHtml(title)}</title>
<style>
  body { font-family: var(--vscode-font-family); font-size: var(--vscode-font-size); color: var(--vscode-foreground);
         background: var(--vscode-editor-background); padding: 0 20px 40px; line-height: 1.55; max-width: 860px; margin: 0 auto; }
  h1 { font-size: 1.5em; margin: 18px 0 4px; } h2 { font-size: 1.15em; margin: 22px 0 8px; }
  .muted { color: var(--vscode-descriptionForeground); }
  .card { border: 1px solid var(--vscode-panel-border, rgba(128,128,128,.35)); border-radius: 6px; padding: 12px 16px; margin: 12px 0;
          background: var(--vscode-sideBar-background, transparent); }
  .tag { display: inline-block; padding: 1px 8px; border-radius: 10px; font-size: .85em; margin-right: 6px;
         background: var(--vscode-badge-background); color: var(--vscode-badge-foreground); }
  pre { background: var(--vscode-textCodeBlock-background); padding: 10px 12px; border-radius: 4px; overflow-x: auto; }
  code { font-family: var(--vscode-editor-font-family); }
  p code, li code { background: var(--vscode-textCodeBlock-background); padding: 0 4px; border-radius: 3px; }
  button { background: var(--vscode-button-background); color: var(--vscode-button-foreground); border: none; border-radius: 3px;
           padding: 6px 12px; margin: 4px 6px 4px 0; cursor: pointer; font: inherit; }
  button:hover { background: var(--vscode-button-hoverBackground); }
  button.secondary { background: var(--vscode-button-secondaryBackground); color: var(--vscode-button-secondaryForeground); }
  button:disabled { opacity: .5; cursor: default; }
  textarea, input[type=text] { width: 100%; box-sizing: border-box; font: inherit; color: var(--vscode-input-foreground);
           background: var(--vscode-input-background); border: 1px solid var(--vscode-input-border, transparent); padding: 6px; border-radius: 3px; }
  label.choice { display: block; padding: 4px 0; cursor: pointer; }
  .bar { height: 8px; border-radius: 4px; background: rgba(128,128,128,.25); position: relative; min-width: 80px; }
  .bar > span { position: absolute; left: 0; top: 0; bottom: 0; border-radius: 4px; background: var(--vscode-progressBar-background); }
  .ok { color: var(--vscode-testing-iconPassed, #3fb950); } .ko { color: var(--vscode-testing-iconFailed, #f85149); }
  .warn { color: var(--vscode-editorWarning-foreground, #d29922); }
  .ladder span { display: inline-block; width: 22px; height: 6px; margin-right: 4px; border-radius: 3px; background: rgba(128,128,128,.3); }
  .ladder span.on { background: var(--vscode-button-background); }
  .ladder span.label { width: auto; height: auto; background: none; }
  td.nowrap { white-space: nowrap; }
  table { border-collapse: collapse; width: 100%; } td, th { text-align: left; padding: 6px 8px; border-bottom: 1px solid var(--vscode-panel-border, rgba(128,128,128,.25)); }
</style>
</head>
<body>
${body}
<script nonce="${n}">
const vscode = acquireVsCodeApi();
document.addEventListener('click', e => {
  const el = e.target.closest('[data-cmd]');
  if (el) { vscode.postMessage({ cmd: el.dataset.cmd, arg: el.dataset.arg }); }
});
${script}
</script>
</body>
</html>`;
}

export const STATUS_LABEL: Record<string, string> = {
  not_started: 'not tested yet', learning: 'learning', almost: 'almost there', mastered: 'mastered',
};

export function masteryBar(mastery: number): string {
  return `<div class="bar"><span style="width:${Math.round(mastery * 100)}%"></span></div>`;
}
