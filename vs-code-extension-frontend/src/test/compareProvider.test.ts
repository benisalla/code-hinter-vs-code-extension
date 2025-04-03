// import * as assert from 'assert';
// import * as vscode from 'vscode';
// import sinon from 'sinon';

// suite('Compare Provider Test', function () {
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
//     // Stub showInformationMessage to capture the output.
//     const showInfoStub = sandbox.stub(vscode.window, 'showInformationMessage')
//     .resolves({ title: 'Comparison result' });

//     // Open a document.
//     const doc = await vscode.workspace.openTextDocument({ language: 'javascript', content: 'const a = 1;' });
//     await vscode.window.showTextDocument(doc);

//     // Execute your compare command.
//     await vscode.commands.executeCommand('code-hinter.compareCode');

//     // Verify that the message was shown.
//     assert.ok(showInfoStub.called, 'No comparison message was shown');
//     const message = showInfoStub.getCall(0).args[0] as string;
//     assert.ok(message.toLowerCase().includes('comparison'), 'Unexpected message content');
//   });
// });






import * as assert from 'assert';
import * as vscode from 'vscode';
import sinon from 'sinon';
import * as flaskApi from "../api/flaskApi";

suite('Compare Provider Test', function () {
    this.timeout(10000);

    let sandbox: sinon.SinonSandbox;

    setup(() => {
        sandbox = sinon.createSandbox();
        // Stub the compareCode API call so it resolves immediately
        sandbox.stub(flaskApi, 'compareCode').resolves({ response: 'comparison result' });
    });

    teardown(() => {
        sandbox.restore();
    });

    test('Should execute compareCode command and display a message', async () => {
        // Stub the message display function
        const showInfoStub = sandbox.stub(vscode.window, 'showInformationMessage')
            .resolves({ title: 'Comparison result' });

        // Open a document with sample content
        const doc = await vscode.workspace.openTextDocument({ language: 'javascript', content: 'const a = 1;' });
        await vscode.window.showTextDocument(doc);

        // Execute the compare command
        await vscode.commands.executeCommand('code-hinter.compareCode');

        // Verify the message was shown
        assert.ok(showInfoStub.called, 'No comparison message was shown');
        const message = showInfoStub.getCall(0).args[0] as string;
        assert.ok(message.toLowerCase().includes('comparison'), 'Unexpected message content');
    });
});
