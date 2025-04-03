import * as vscode from 'vscode';

export function registerLogoutProvider(context: vscode.ExtensionContext) {
    const disposable = vscode.commands.registerCommand('ch.logout', async () => {

        await context.globalState.update('userEmail', undefined);
        await context.globalState.update('userPassword', undefined);
        await context.globalState.update('exerciseId', undefined);
        await context.globalState.update('hasRunBefore', undefined);

        vscode.window.showInformationMessage('You have been logged out successfully.');
    });

    context.subscriptions.push(disposable);
}
