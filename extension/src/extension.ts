import * as vscode from 'vscode';
import { setBaseUrl } from './api/flaskApi';
import { registerLoginProvider } from './commands/auth/login';
import { registerLogoutProvider } from './commands/auth/logout';
import { registerTestTestProvider } from './commands/healthCheck';
import { registerEvaluateProvider } from './commands/grading/evaluate';
import { registerSubmitProvider } from './commands/grading/submit';
import { registerChangeExerciseProvider } from './commands/auth/changeExercise';
import { registerHintProvider } from './commands/tutor/hint';
import { registerQuizProvider } from './commands/tutor/testMe';
import { registerProgressProvider } from './commands/tutor/progress';
import { registerProfileProvider } from './commands/tutor/profile';
import { refreshStatusBar } from './ui/statusBar';

export function activate(context: vscode.ExtensionContext) {
  console.log('🚀 Welcome to Code-Hinter! Happy coding! ✨');

  const applyServerUrl = () => setBaseUrl(vscode.workspace.getConfiguration('codeHinter').get<string>('serverUrl'));
  applyServerUrl();
  context.subscriptions.push(vscode.workspace.onDidChangeConfiguration(e => {
    if (e.affectsConfiguration('codeHinter.serverUrl')) { applyServerUrl(); }
  }));

  registerLoginProvider(context);
  registerLogoutProvider(context);
  registerTestTestProvider(context);
  registerEvaluateProvider(context);
  registerSubmitProvider(context);
  registerChangeExerciseProvider(context);

  // The tutor: hints only, adapted to the student, plus "Test me" and progress tracking.
  registerHintProvider(context);
  registerQuizProvider(context);
  registerProgressProvider(context);
  registerProfileProvider(context);
  refreshStatusBar(context);
}

export function deactivate() { }
