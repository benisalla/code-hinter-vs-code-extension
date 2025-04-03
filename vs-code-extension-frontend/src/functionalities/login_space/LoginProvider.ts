import * as vscode from 'vscode';
import { login } from '../../api/flaskApi';

export function registerLoginProvider(context: vscode.ExtensionContext) {
  const disposable = vscode.commands.registerCommand('ch.login', async () => {
    await handleLogin(context);
  });
  context.subscriptions.push(disposable);
}

async function handleLogin(context: vscode.ExtensionContext) {
  const storedEmail = context.globalState.get<string>('userEmail');
  if (storedEmail) {
    vscode.window.showInformationMessage('You are already logged in.');
    return;
  }

  const email = await vscode.window.showInputBox({
    prompt: "Enter your email",
    placeHolder: "example@domain.com",
  });
  if (!email) {
    vscode.window.showErrorMessage('Email is required.');
    return;
  }

  const password = await vscode.window.showInputBox({
    prompt: "Enter your password",
    password: true,
  });
  if (!password) {
    vscode.window.showErrorMessage('Password is required.');
    return;
  }

  const exerciseId = await vscode.window.showInputBox({
    prompt: "Enter your exercise ID",
    placeHolder: "1234",
  });
  if (!exerciseId) {
    vscode.window.showErrorMessage('Exercise ID is required.');
    return;
  }

  try {
    const data = await login(email, password, exerciseId);
    if (data && data.user) {
      await context.globalState.update('userEmail', email);
      await context.globalState.update('userPassword', password);
      await context.globalState.update('exerciseId', exerciseId);
      await context.globalState.update('hasRunBefore', true);

      vscode.window.showInformationMessage(
        `Login successful. Welcome, ${data.user.name || email}!`
      );
    } else {
      vscode.window.showErrorMessage('Login failed: No user data received.');
    }
  } catch (error: any) {
    vscode.window.showErrorMessage(`Login failed: ${error.message || error}`);
  }
}
