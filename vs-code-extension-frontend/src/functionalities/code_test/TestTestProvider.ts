import * as vscode from 'vscode';
import { callTestEndpoint, evaluateCode, compareCode, completeCode } from '../../api/flaskApi';

export function registerTestTestProvider(context: vscode.ExtensionContext) {
    const disposable = vscode.commands.registerCommand('code-hinter.testapi', async () => {
        try {
            // Test the GET endpoint
            const testResponse = await callTestEndpoint();
            vscode.window.showInformationMessage(`Test Endpoint Response: ${JSON.stringify(testResponse)}`);

            // Use dummy data for evaluation and comparison
            // const exerciseId = '1';
            // const studentId = '1';
            // const sampleCode = 'print("Hello, world!")';

            // // Test evaluateCode endpoint
            // const evalResponse = await evaluateCode(exerciseId, studentId, sampleCode);
            // vscode.window.showInformationMessage(`Evaluate Code Response: ${JSON.stringify(evalResponse)}`);

            // // Test compareCode endpoint
            // const compareResponse = await compareCode(exerciseId, studentId, sampleCode);
            // vscode.window.showInformationMessage(`Compare Code Response: ${JSON.stringify(compareResponse)}`);
            
            // Test completeCode endpoint
            const codeToComplete = 'for i in range(10):';
            const completeResponse = await completeCode(codeToComplete);
            vscode.window.showInformationMessage(`Complete Code Response: ${JSON.stringify(completeResponse)}`);
        } catch (error: any) {
            vscode.window.showErrorMessage(`Error testing API: ${error.message}`);
        }
    });

    context.subscriptions.push(disposable);
}
