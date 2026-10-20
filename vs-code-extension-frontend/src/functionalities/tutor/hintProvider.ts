import * as vscode from 'vscode';
import { getHint, explainConcept, getConcepts, askProfessor, Hint, Explanation } from '../../api/flaskApi';
import { requireSession, editorDiagnostics } from './session';
import { page, escapeHtml, renderMarkdown } from './webview';

/**
 * The tutor panel: hints (never solutions), concept explanations, and the
 * "Ask my professor" escape hatch once the hint ladder is exhausted.
 */
let panel: vscode.WebviewPanel | undefined;
let lastDocument: vscode.Uri | undefined;

function tutorPanel(context: vscode.ExtensionContext): vscode.WebviewPanel {
  if (panel) {
    panel.reveal(vscode.ViewColumn.Beside, true);
    return panel;
  }
  panel = vscode.window.createWebviewPanel('codeHinterTutor', 'Code Hinter Tutor',
    { viewColumn: vscode.ViewColumn.Beside, preserveFocus: true }, { enableScripts: true });
  panel.onDidDispose(() => { panel = undefined; }, null, context.subscriptions);
  panel.webview.onDidReceiveMessage(async (msg: { cmd: string; arg?: string }) => {
    switch (msg.cmd) {
      case 'more': return requestHint(context, { more: true });
      case 'explain': return showExplanation(context, msg.arg);
      case 'testExercise': return vscode.commands.executeCommand('ch.testMe', 'exercise');
      case 'askProf': return vscode.commands.executeCommand('ch.askProfessor', msg.arg);
      case 'gotoLine': return gotoLine(Number(msg.arg));
    }
  }, null, context.subscriptions);
  return panel;
}

async function gotoLine(line: number) {
  if (!lastDocument || !line) { return; }
  const editor = await vscode.window.showTextDocument(lastDocument, { viewColumn: vscode.ViewColumn.One });
  const pos = new vscode.Position(line - 1, 0);
  editor.selection = new vscode.Selection(pos, editor.document.lineAt(line - 1).range.end);
  editor.revealRange(new vscode.Range(pos, pos), vscode.TextEditorRevealType.InCenter);
}

function codeDocument(): vscode.TextDocument | undefined {
  const editor = vscode.window.activeTextEditor;
  if (editor) {
    lastDocument = editor.document.uri;
    return editor.document;
  }
  return lastDocument ? vscode.workspace.textDocuments.find(d => d.uri.toString() === lastDocument!.toString()) : undefined;
}

async function requestHint(context: vscode.ExtensionContext, opts: { question?: string; more?: boolean } = {}) {
  const session = await requireSession(context);
  const document = codeDocument();
  if (!session) { return; }
  if (!document) {
    vscode.window.showErrorMessage('Open your exercise file first.');
    return;
  }
  try {
    const hint = await vscode.window.withProgress(
      { location: vscode.ProgressLocation.Window, title: 'Code Hinter: thinking of a hint…' },
      () => getHint(session.email, session.exerciseId, document.getText(),
        { ...opts, diagnostics: editorDiagnostics(document) }));
    const p = tutorPanel(context);
    p.webview.html = page(p.webview, 'Hint', hintHtml(hint, opts.question));
  } catch (error: any) {
    vscode.window.showErrorMessage(`Code Hinter: could not get a hint: ${error.message || error}`);
  }
}

export function hintHtml(h: Hint, question?: string): string {
  const ladder = Array.from({ length: h.max_level }, (_, i) => `<span class="${i < h.level ? 'on' : ''}"></span>`).join('');
  return `
    <h1>💡 Hint</h1>
    <div class="muted">Concept: <strong>${escapeHtml(h.concept)}</strong></div>
    <div class="ladder" title="Hint ${h.level} of ${h.max_level}: ${escapeHtml(h.level_name)}">${ladder}
      <span class="label muted">step ${h.level}/${h.max_level} · ${escapeHtml(h.level_name)}</span></div>
    ${question ? `<p class="muted">You asked: “${escapeHtml(question)}”</p>` : ''}
    <div class="card">${renderMarkdown(h.hint)}</div>
    ${h.line ? `<button class="secondary" data-cmd="gotoLine" data-arg="${h.line}">Show me line ${h.line}</button>` : ''}
    <div class="card"><strong>Think about it:</strong> ${escapeHtml(h.check_question)}</div>
    ${h.escalate ? `<div class="card warn">${escapeHtml(h.escalate_message)}</div>` : ''}
    <div>
      ${h.level < h.max_level ? '<button data-cmd="more">I need more help</button>' : ''}
      <button class="secondary" data-cmd="explain" data-arg="${escapeHtml(h.concept)}">Explain this concept</button>
      <button class="secondary" data-cmd="testExercise">Test me on this exercise</button>
      ${h.escalate ? `<button data-cmd="askProf" data-arg="${escapeHtml(h.concept)}">Ask my professor</button>` : ''}
    </div>
    <p class="muted">The tutor gives hints, never the solution. Try something, run it, then ask again if you are stuck.</p>`;
}

export async function showExplanation(context: vscode.ExtensionContext, concept?: string) {
  const session = await requireSession(context);
  if (!session) { return; }
  try {
    if (!concept) {
      const concepts = await getConcepts(session.email, session.exerciseId);
      const pick = await vscode.window.showQuickPick(
        concepts.map(c => ({ label: c.label, description: `${Math.round(c.mastery * 100)}% · ${c.status.replace('_', ' ')}` })),
        { placeHolder: 'Which concept should the tutor explain?' });
      if (!pick) { return; }
      concept = pick.label;
    }
    const exp: Explanation = await vscode.window.withProgress(
      { location: vscode.ProgressLocation.Window, title: 'Code Hinter: preparing an explanation…' },
      () => explainConcept(session.email, concept!, session.exerciseId));
    const p = tutorPanel(context);
    p.webview.html = page(p.webview, 'Explanation', `
      <h1>📘 ${escapeHtml(exp.concept)}</h1>
      <div><span class="tag">${escapeHtml(exp.level)}</span><span class="tag">${escapeHtml(exp.style.replace(/_/g, ' '))}</span></div>
      <div class="card">${renderMarkdown(exp.explanation)}</div>
      <button data-cmd="testExercise">Test me now</button>
      <p class="muted">Change how the tutor explains things with “Code Hinter: Set up my learning profile”.</p>`);
  } catch (error: any) {
    vscode.window.showErrorMessage(`Code Hinter: ${error.message || error}`);
  }
}

export function registerHintProvider(context: vscode.ExtensionContext) {
  context.subscriptions.push(
    vscode.commands.registerCommand('ch.hint', () => requestHint(context)),
    vscode.commands.registerCommand('ch.askTutor', async () => {
      const question = await vscode.window.showInputBox({
        prompt: 'What are you stuck on? (the tutor answers with a hint, not the solution)',
        placeHolder: 'e.g. why does my loop stop too early?',
      });
      if (question) { await requestHint(context, { question }); }
    }),
    vscode.commands.registerCommand('ch.explain', (concept?: string) => showExplanation(context, concept)),
    vscode.commands.registerCommand('ch.askProfessor', async (concept?: string) => {
      const session = await requireSession(context);
      if (!session) { return; }
      const message = await vscode.window.showInputBox({
        prompt: 'Message for your professor: what have you tried, and where are you blocked?',
        placeHolder: 'I tried … but …',
      });
      if (!message) { return; }
      const document = codeDocument();
      try {
        await askProfessor(session.email, session.exerciseId, message, document?.getText() || '', concept);
        vscode.window.showInformationMessage('Your professor has been notified, with your code and the hints you already used.');
      } catch (error: any) {
        vscode.window.showErrorMessage(`Code Hinter: ${error.message || error}`);
      }
    }),
  );
}
