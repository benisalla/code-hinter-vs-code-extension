// import * as assert from 'assert';
// import * as vscode from 'vscode';
// import sinon from 'sinon';

// suite('Evaluate Provider Test', function () {
//   // Increase the timeout to 10 seconds (10000ms)
//   this.timeout(10000);

//   let sandbox: sinon.SinonSandbox;

//   setup(() => {
//     sandbox = sinon.createSandbox();
//   });

//   teardown(() => {
//     sandbox.restore();
//   });

//   test('Should execute evaluateCode command and display a message', async () => {
//     // Stub the message display to capture output.
//     const showInfoStub = sandbox.stub(vscode.window, 'showInformationMessage')
//     .resolves({ title: 'Evaluation result' });

//     // Open a document.
//     const doc = await vscode.workspace.openTextDocument({ language: 'javascript', content: 'function test() {}' });
//     await vscode.window.showTextDocument(doc);

//     // Execute your evaluate command.
//     await vscode.commands.executeCommand('code-hinter.evaluateCode');

//     // Verify that the stub was called.
//     assert.ok(showInfoStub.called, 'No evaluation message was shown');
//     const message = showInfoStub.getCall(0).args[0] as string;
//     assert.ok(message.toLowerCase().includes('evaluation'), 'Unexpected message content');
//   });
// });












import * as assert from 'assert';
import * as vscode from 'vscode';
import sinon from 'sinon';
import * as flaskApi from "../api/flaskApi";

suite('Evaluate Provider Test', function () {
    // Increase timeout if needed
    this.timeout(10000);

    let sandbox: sinon.SinonSandbox;

    setup(() => {
        sandbox = sinon.createSandbox();
        // Stub the API call so it resolves immediately
        sandbox.stub(flaskApi, 'evaluateCode').resolves({ response: 'evaluation result' });
    });

    teardown(() => {
        sandbox.restore();
    });

    test('Should execute evaluateCode command and display a message', async () => {
        // Stub the VS Code message display
        const showInfoStub = sandbox.stub(vscode.window, 'showInformationMessage')
            .resolves({ title: 'Evaluation result' });

        // Open a document to simulate an active editor
        const doc = await vscode.workspace.openTextDocument({ language: 'javascript', content: 'function test() {}' });
        await vscode.window.showTextDocument(doc);

        // Execute the command (make sure the command ID matches your registration)
        await vscode.commands.executeCommand('code-hinter.evaluateCode');

        // Verify that the message was displayed
        assert.ok(showInfoStub.called, 'No evaluation message was shown');
        const message = showInfoStub.getCall(0).args[0] as string;
        assert.ok(message.toLowerCase().includes('evaluation'), 'Unexpected message content');
    });
});
