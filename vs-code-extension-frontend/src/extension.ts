import * as vscode from 'vscode';
import { setBaseUrl } from './api/flaskApi';
import { registerTestProvider } from './functionalities/code_test/testProvider';
import { registerLoginProvider } from './functionalities/login_space/LoginProvider';
import { registerLogoutProvider } from './functionalities/login_space/LogoutProvider';
import { registerTestTestProvider } from './functionalities/code_test/TestTestProvider';
import { registerEvaluateProvider } from './functionalities/code_evaluation/evaluateProvider';
import { registerSubmitProvider } from './functionalities/code_comparaison/compareProvider';
import { registerChangeExerciseProvider } from './functionalities/login_space/changeExerciseProvider';
import { registerHintProvider } from './functionalities/tutor/hintProvider';
import { registerQuizProvider } from './functionalities/tutor/quizProvider';
import { registerProgressProvider } from './functionalities/tutor/progressProvider';
import { registerProfileProvider } from './functionalities/tutor/profileProvider';
import { refreshStatusBar } from './functionalities/tutor/statusBar';

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
  registerTestProvider(context);
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
