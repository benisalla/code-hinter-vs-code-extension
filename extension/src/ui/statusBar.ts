import * as vscode from 'vscode';

let item: vscode.StatusBarItem | undefined;

/** "💡 Hint" in the status bar while a student is logged in. */
export function refreshStatusBar(context: vscode.ExtensionContext) {
  if (!item) {
    item = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    item.command = 'ch.hint';
    context.subscriptions.push(item);
  }
  const exerciseId = context.globalState.get<string>('exerciseId');
  if (context.globalState.get<string>('userEmail') && exerciseId) {
    item.text = `$(lightbulb) Hint · ex ${exerciseId}`;
    item.tooltip = 'Code Hinter: get a hint for your exercise (Ctrl+Alt+H). Hints only, never the solution.';
    item.show();
  } else {
    item.hide();
  }
}
