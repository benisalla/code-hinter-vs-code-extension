// Runs inside VS Code (npm test, needs a display): checks every command is registered.
import * as assert from 'assert';
import * as vscode from 'vscode';

suite('Extension commands', () => {
  test('all Code Hinter commands are registered', async () => {
    const ext = vscode.extensions.all.find(e => e.packageJSON.name === 'code-hinter');
    assert.ok(ext, 'extension not found');
    await ext!.activate();
    const commands = await vscode.commands.getCommands(true);
    for (const id of ['ch.login', 'ch.logout', 'ch.evaluate', 'ch.submit', 'ch.chexe', 'ch.testapi',
      'ch.hint', 'ch.askTutor', 'ch.explain', 'ch.testMe', 'ch.progress', 'ch.profile', 'ch.askProfessor']) {
      assert.ok(commands.includes(id), `${id} is not registered`);
    }
  });
});
