import * as vscode from 'vscode';
import { evaluateCode } from '../../api/flaskApi';

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
      const evaluation_text = await evaluateCode(exerciseId, email, code);

      // Create and display a new webview panel for the result
      const panel = vscode.window.createWebviewPanel(
        'evaluationResult',
        'Code Evaluation Result',
        vscode.ViewColumn.One,
        {}
      );

      // Set the HTML content for the panel
      panel.webview.html = getWebviewContent(evaluation_text);
    } catch (error) {
      vscode.window.showErrorMessage(`Error evaluating code: ${error}`);
    }
  });
  context.subscriptions.push(disposable);
}

function getWebviewContent(text: any): string {
  return `
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Code Evaluation Result</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          margin: 0;
          padding: 0;
          line-height: 1.6;
          background-color: #f2f2f2;
          color: #333;
        }
        .container {
          background-color: #ffffff;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
          max-width: 800px;
          margin: 40px auto;
        }
        h1 {
          margin-top: 0;
          text-align: center;
          color: #444;
        }
        pre {
          background-color: #e8e8e8;
          color: #333;
          padding: 15px;
          border-radius: 4px;
          overflow-x: auto;
          white-space: pre-wrap;
          word-wrap: break-word;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <h1>Evaluation Result</h1>
        <pre>${text}</pre>
      </div>
    </body>
    </html>
  `;
}
