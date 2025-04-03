import * as vscode from 'vscode';
import { registerTestProvider } from './functionalities/code_test/testProvider';
import { registerLoginProvider } from './functionalities/login_space/LoginProvider';
import { registerLogoutProvider } from './functionalities/login_space/LogoutProvider';
import { registerTestTestProvider } from './functionalities/code_test/TestTestProvider';
import { registerCompletionProvider } from './functionalities/code_completion/completionProvider';
import { registerEvaluateProvider } from './functionalities/code_evaluation/evaluateProvider';
import { registerSubmitProvider } from './functionalities/code_comparaison/compareProvider';
import { registerChangeExerciseProvider } from './functionalities/login_space/changeExerciseProvider';

export function activate(context: vscode.ExtensionContext) {
  console.log('🚀 Welcome to Code-Hinter! Happy coding! ✨');

  registerLoginProvider(context);
  registerLogoutProvider(context);
  registerTestTestProvider(context);
  registerTestProvider(context);
  registerCompletionProvider(context);
  registerEvaluateProvider(context);
  registerSubmitProvider(context);
  registerChangeExerciseProvider(context);
}

export function deactivate() { }
