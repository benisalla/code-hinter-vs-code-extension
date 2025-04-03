import * as vscode from 'vscode';
import { completeCode } from '../../api/flaskApi';

export function registerCompletionProvider(context: vscode.ExtensionContext) {
  let lastApiCallTime = 0;
  const debounceTime = 500;

  const provider = vscode.languages.registerCompletionItemProvider(
    { scheme: 'file', language: 'python' },
    {
      async provideCompletionItems(document, position) {
        console.log('provideCompletionItems called');

        const now = Date.now();
        if (now - lastApiCallTime < debounceTime) {
          return [];
        }
        lastApiCallTime = now;

        const textSoFar = document.getText(new vscode.Range(new vscode.Position(0, 0), position));

        try {
          const newCode = await completeCode(textSoFar);

          const completionItem = new vscode.CompletionItem(
            "Replace file with AI code",
            vscode.CompletionItemKind.Snippet
          );
          completionItem.detail = "Replace entire file content with AI generated code";

          completionItem.command = {
            command: 'extension.replaceEntireFile',
            title: 'Replace Entire File',
            arguments: [newCode]
          };

          completionItem.insertText = '';

          return [completionItem];
        } catch (error) {
          console.error('Error in completion provider:', error);
          return [];
        }
      }
    },
    '\n'
  );

  context.subscriptions.push(provider);

  context.subscriptions.push(
    vscode.commands.registerCommand('extension.replaceEntireFile', async (newCode: string) => {
      const editor = vscode.window.activeTextEditor;
      if (editor) {
        const document = editor.document;
        const start = new vscode.Position(0, 0);
        const lastLine = document.lineCount - 1;
        const lastLineRange = document.lineAt(lastLine).range;
        const end = new vscode.Position(lastLine, lastLineRange.end.character);
        const fullRange = new vscode.Range(start, end);

        await editor.edit(editBuilder => {
          editBuilder.replace(fullRange, newCode);
        });
      }
    })
  );
}
