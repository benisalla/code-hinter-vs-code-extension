import * as vscode from 'vscode';

export function registerTestProvider(context: vscode.ExtensionContext) {
  const disposable = vscode.commands.registerCommand(
    'code-hinter.test',
    async () => {
      // Retrieve stored information
      const email = context.globalState.get<string>('userEmail');
      const password = context.globalState.get<string>('userPassword');
      const exerciseId = context.globalState.get<string>('exerciseId');

      if (email || password || exerciseId) {
        vscode.window.showInformationMessage(
          `Email: ${email}\nPassword: ${password}\nExercise ID: ${exerciseId}`
        );
      } else {
        vscode.window.showInformationMessage(
          'No user credentials found. Please sign in first.'
        );
      }
    }
  );

  context.subscriptions.push(disposable);
}

// Optional: Keep this as a standalone function if needed elsewhere
export function showTest(): void {
  vscode.window.showInformationMessage('Hello World from VS Code Extension!');
}
