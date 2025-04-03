import * as assert from 'assert';
import * as vscode from 'vscode';

suite('Completion Provider Test', () => {
  test('Should return completion items on trigger', async () => {
    // Open a new JavaScript document with initial content.
    const doc = await vscode.workspace.openTextDocument({ language: 'javascript', content: 'console.' });
    const position = new vscode.Position(0, 'console.'.length);
    
    // Execute the built-in VS Code command to get completion items.
    const completionList = await vscode.commands.executeCommand<vscode.CompletionList>(
      'vscode.executeCompletionItemProvider',
      doc.uri,
      position,
      '.' // trigger character
    );
    
    assert.ok(completionList, 'No completion list returned');
    assert.ok(completionList!.items.length > 0, 'No completion items were provided');
  });
});
