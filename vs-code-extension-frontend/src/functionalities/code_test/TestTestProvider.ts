import * as vscode from 'vscode';
import { getTutorStatus } from '../../api/flaskApi';

export function registerTestTestProvider(context: vscode.ExtensionContext) {
    const disposable = vscode.commands.registerCommand('ch.testapi', async () => {
        try {
            const status = await getTutorStatus();
            vscode.window.showInformationMessage(
                `Code Hinter backend is up. LLM: ${status.llm_available ? status.llm_backend : 'offline (rule-based tutor)'}`
            );
        } catch (error: any) {
            vscode.window.showErrorMessage(`Error testing API: ${error.message}`);
        }
    });

    context.subscriptions.push(disposable);
}
