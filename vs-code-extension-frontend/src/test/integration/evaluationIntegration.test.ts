// import * as assert from 'assert';
// import * as vscode from 'vscode';
// import sinon from 'sinon';

// suite('Evaluation Integration Test', function () {
//     // Increase the timeout to 10 seconds
//     this.timeout(10000);

//     let sandbox: sinon.SinonSandbox;

//     setup(() => {
//         sandbox = sinon.createSandbox();
//     });

//     teardown(() => {
//         sandbox.restore();
//     });

//     test('Should execute evaluateCode command and display a message', async () => {
//         // Stub the message display.
//         const showInfoStub = sandbox.stub(vscode.window, 'showInformationMessage')
//             .resolves({ title: 'Evaluation result' });

//         // Open a document.
//         const doc = await vscode.workspace.openTextDocument({ language: 'javascript', content: 'function test() {}' });
//         await vscode.window.showTextDocument(doc);

//         // Execute the evaluation command.
//         await vscode.commands.executeCommand('code-hinter.evaluateCode');

//         // Verify that the stub was called.
//         assert.ok(showInfoStub.called, 'No evaluation message displayed');
//         const message = showInfoStub.getCall(0).args[0] as string;
//         assert.ok(message.toLowerCase().includes('evaluation'), 'Message does not contain expected text');
//     });
// });







import * as assert from 'assert';
import * as vscode from 'vscode';
import sinon from 'sinon';
import * as flaskApi from '../../api/flaskApi';

suite('Evaluation Integration Test', function () {
    this.timeout(10000);

    let sandbox: sinon.SinonSandbox;

    setup(() => {
        sandbox = sinon.createSandbox();
        // Stub the API call for evaluation
        sandbox.stub(flaskApi, 'evaluateCode').resolves({ response: 'evaluation result' });
    });

    teardown(() => {
        sandbox.restore();
    });

    test('Should execute evaluateCode command and display a message', async () => {
        const showInfoStub = sandbox.stub(vscode.window, 'showInformationMessage')
            .resolves({ title: 'Evaluation result' });

        const doc = await vscode.workspace.openTextDocument({ language: 'javascript', content: 'function test() {}' });
        await vscode.window.showTextDocument(doc);

        await vscode.commands.executeCommand('code-hinter.evaluateCode');

        assert.ok(showInfoStub.called, 'No evaluation message displayed');
        const message = showInfoStub.getCall(0).args[0] as string;
        assert.ok(message.toLowerCase().includes('evaluation'), 'Message does not contain expected text');
    });
});
