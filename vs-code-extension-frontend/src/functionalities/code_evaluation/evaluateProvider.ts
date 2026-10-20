import * as vscode from 'vscode';
import { evaluateCode, EvaluationResult } from '../../api/flaskApi';
import { page, escapeHtml } from '../tutor/webview';

export function registerEvaluateProvider(
  context: vscode.ExtensionContext,
) {
  const disposable = vscode.commands.registerCommand('ch.evaluate', async () => {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      vscode.window.showErrorMessage('No active editor found.');
      return;
    }

    // Retrieve the entire content of the current document
    const code = editor.document.getText();

    // Retrieve email and exerciseId from globalState
    const email = context.globalState.get<string>('userEmail');
    const exerciseId = context.globalState.get<string>('exerciseId');

    if (!email || !exerciseId) {
      vscode.window.showErrorMessage('Missing user email or exercise id in global state.');
      return;
    }

    try {
      // Call the evaluateCode API with the proper parameters
      const evaluation = await vscode.window.withProgress(
        { location: vscode.ProgressLocation.Window, title: 'Code Hinter: checking your code against the concepts…' },
        () => evaluateCode(exerciseId, email, code));

      // Create and display a new webview panel for the result
      const panel = vscode.window.createWebviewPanel(
        'evaluationResult',
        'Code Evaluation Result',
        vscode.ViewColumn.Beside,
        { enableScripts: true }
      );
      panel.webview.html = page(panel.webview, 'Code Evaluation Result', getEvaluationHtml(evaluation));
      panel.webview.onDidReceiveMessage((msg: { cmd: string; arg?: string }) => {
        if (msg.cmd === 'hint') { vscode.commands.executeCommand('ch.hint'); }
        if (msg.cmd === 'explain') { vscode.commands.executeCommand('ch.explain', msg.arg); }
      }, null, context.subscriptions);
    } catch (error) {
      vscode.window.showErrorMessage(`Error evaluating code: ${error}`);
    }
  });
  context.subscriptions.push(disposable);
}

function getEvaluationHtml(evaluation: EvaluationResult): string {
  const rows = (evaluation.concepts || []).map(c => `<tr>
      <td class="${c.satisfied ? 'ok' : 'ko'}">${c.satisfied ? '✔' : '✘'}</td>
      <td>${escapeHtml(c.concept)}</td>
      <td>${c.satisfied ? '' : `<button class="secondary" data-cmd="explain" data-arg="${escapeHtml(c.concept)}">Explain</button>`}</td>
    </tr>`).join('');
  const missing = (evaluation.concepts || []).filter(c => !c.satisfied).length;
  return `
    <h1>Evaluation Result</h1>
    ${rows ? `<table>${rows}</table>` : ''}
    <h2>Details</h2>
    <pre>${escapeHtml(evaluation.response)}</pre>
    ${missing ? `<p>${missing} concept(s) are not there yet. Want a nudge in the right direction?</p>
      <button data-cmd="hint">Give me a hint</button>` : '<p class="ok">Every concept is satisfied. Nice work!</p>'}`;
}
