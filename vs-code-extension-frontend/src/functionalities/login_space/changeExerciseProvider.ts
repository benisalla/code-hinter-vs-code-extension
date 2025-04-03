import * as vscode from 'vscode';
import { checkExerciseExistence } from '../../api/flaskApi';

export function registerChangeExerciseProvider(context: vscode.ExtensionContext) {
  const disposable = vscode.commands.registerCommand('ch.chexe', async () => {
    await handleChangeExercise(context);
  });
  context.subscriptions.push(disposable);
}

async function handleChangeExercise(context: vscode.ExtensionContext) {
  // Prompt the user to enter a new exercise ID
  const newExerciseId = await vscode.window.showInputBox({
    prompt: "Enter new exercise ID",
    placeHolder: "e.g., 1234",
  });

  if (!newExerciseId) {
    vscode.window.showErrorMessage('Exercise ID is required.');
    return;
  }

  try {
    // Check if the exercise exists using the provided API
    const result = await checkExerciseExistence(newExerciseId);
    
    if (!result.exists) {
      vscode.window.showErrorMessage(
        `Cannot switch to exercise with ID ${newExerciseId}. Please verify the ID and try again.`
      );
      return;
    }

    // If the exercise exists, update the global state with the new exercise ID
    await context.globalState.update('exerciseId', newExerciseId);
    vscode.window.showInformationMessage(`Exercise ID updated successfully to ${newExerciseId}.`);
    
  } catch (error: any) {
    vscode.window.showErrorMessage(`Failed to update exercise ID: ${error.message || error}`);
  }
}
