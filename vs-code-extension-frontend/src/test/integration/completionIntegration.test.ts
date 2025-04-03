import * as assert from 'assert';
import * as vscode from 'vscode';

suite('Completion Integration Test', () => {
  test('Should provide at least one completion item', async () => {
    const document = await vscode.workspace.openTextDocument({ language: 'javascript', content: 'console.' });
    const position = new vscode.Position(0, 'console.'.length);
    const completionList = await vscode.commands.executeCommand<vscode.CompletionList>(
      'vscode.executeCompletionItemProvider', document.uri, position, '.'
    );

    assert.ok(completionList, 'No completion list returned');
    assert.ok(completionList!.items.length > 0, 'No completion items provided');
  });
});
