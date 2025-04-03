// import * as assert from 'assert';
// import * as vscode from 'vscode';
// import sinon from 'sinon';

// suite('Comparison Integration Test', function () {
//   // Increase the timeout to 10 seconds
//   this.timeout(10000);
  
//   let sandbox: sinon.SinonSandbox;

//   setup(() => {
//     sandbox = sinon.createSandbox();
//   });

//   teardown(() => {
//     sandbox.restore();
//   });

//   test('Should execute compareCode command and display a message', async () => {
//     // Stub the message display.
//     const showInfoStub = sandbox.stub(vscode.window, 'showInformationMessage')
//     .resolves({ title: 'Comparison result' });

//     // Open a document.
//     const document = await vscode.workspace.openTextDocument({ language: 'javascript', content: 'const a = 1;' });
//     await vscode.window.showTextDocument(document);

//     // Execute the compare command.
//     await vscode.commands.executeCommand('code-hinter.compareCode');

//     // Verify that the stub was called.
//     assert.ok(showInfoStub.called, 'No message displayed');
//     const message = showInfoStub.getCall(0).args[0] as string;
//     assert.ok(message.toLowerCase().includes('comparison'), 'Message does not contain expected text');
//   });
// });



















import * as assert from 'assert';
import * as vscode from 'vscode';
import sinon from 'sinon';
import * as flaskApi from '../../api/flaskApi';

suite('Comparison Integration Test', function () {
  this.timeout(10000);
  
  let sandbox: sinon.SinonSandbox;

  setup(() => {
    sandbox = sinon.createSandbox();
    // Stub the API call for comparison
    sandbox.stub(flaskApi, 'compareCode').resolves({ response: 'comparison result' });
  });

  teardown(() => {
    sandbox.restore();
  });

  test('Should execute compareCode command and display a message', async () => {
    const showInfoStub = sandbox.stub(vscode.window, 'showInformationMessage')
    .resolves({ title: 'Comparison result' });

    const document = await vscode.workspace.openTextDocument({ language: 'javascript', content: 'const a = 1;' });
    await vscode.window.showTextDocument(document);

    await vscode.commands.executeCommand('code-hinter.compareCode');

    assert.ok(showInfoStub.called, 'No comparison message displayed');
    const message = showInfoStub.getCall(0).args[0] as string;
    assert.ok(message.toLowerCase().includes('comparison'), 'Message does not contain expected text');
  });
});
