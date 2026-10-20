import * as vscode from 'vscode';

export interface Session { email: string; exerciseId: string }

/** The logged-in student, or undefined after telling them to log in. */
export async function requireSession(context: vscode.ExtensionContext): Promise<Session | undefined> {
  const email = context.globalState.get<string>('userEmail');
  const exerciseId = context.globalState.get<string>('exerciseId');
  if (email && exerciseId) {
    return { email, exerciseId };
  }
  const choice = await vscode.window.showWarningMessage('Code Hinter: please log in first.', 'Login');
  if (choice === 'Login') {
    await vscode.commands.executeCommand('ch.login');
  }
  return undefined;
}

/** Errors and warnings the editor already reports for this file (1-based lines). */
export function editorDiagnostics(document: vscode.TextDocument) {
  return vscode.languages.getDiagnostics(document.uri)
    .filter(d => d.severity <= vscode.DiagnosticSeverity.Warning)
    .slice(0, 10)
    .map(d => ({
      line: d.range.start.line + 1,
      message: d.message,
      severity: d.severity === vscode.DiagnosticSeverity.Error ? 'error' : 'warning',
    }));
}
