// import * as vscode from 'vscode';
// import { compareCode } from '../../api/flaskApi';

// export function registerSubmitProvider(context: vscode.ExtensionContext) {
//   const disposable = vscode.commands.registerCommand('ch.submit', async () => {
//     const editor = vscode.window.activeTextEditor;
//     if (!editor) {
//       vscode.window.showErrorMessage('No active editor found.');
//       return;
//     }

//     // Retrieve the entire content of the current document
//     const code = editor.document.getText();

//     // Retrieve email and exerciseId from globalState
//     const email = context.globalState.get<string>('userEmail');
//     const exerciseId = context.globalState.get<string>('exerciseId');

//     if (!email || !exerciseId) {
//       vscode.window.showErrorMessage('Missing user email or exercise id in global state.');
//       return;
//     }

//     // Inform the student this is their last submission and ask for confirmation
//     const confirmation = await vscode.window.showWarningMessage(
//       'This is your final submission and you will not be able to submit again. Are you sure you want to submit your code?',
//       { modal: true },
//       'Yes'
//     );
//     if (confirmation !== 'Yes') {
//       // User cancelled the submission.
//       return;
//     }

//     try {
//       // Call the compareCode API with the proper parameters and await the score
//       const score = await compareCode(exerciseId, email, code);

//       // Create and display a new webview panel for the result
//       const panel = vscode.window.createWebviewPanel(
//         'submissionResult',
//         'Submission Result',
//         vscode.ViewColumn.One,
//         {}
//       );

//       // Set the HTML content for the panel using a nice style
//       panel.webview.html = getSubmissionWebviewContent(score);
//     } catch (error) {
//       vscode.window.showErrorMessage(`Error submitting code: ${error}`);
//     }
//   });
//   context.subscriptions.push(disposable);
// }

// function getSubmissionWebviewContent(score: any): string {
//   return `
//     <!DOCTYPE html>
//     <html lang="en">
//     <head>
//       <meta charset="UTF-8">
//       <title>Submission Result</title>
//       <style>
//         body {
//           font-family: Arial, sans-serif;
//           background-color: #f8f8f8;
//           margin: 0;
//           padding: 0;
//         }
//         .container {
//           max-width: 800px;
//           margin: 50px auto;
//           background-color: #fff;
//           border-radius: 8px;
//           box-shadow: 0 2px 4px rgba(0,0,0,0.1);
//           padding: 30px;
//           text-align: center;
//         }
//         h1 {
//           color: #444;
//           margin-bottom: 20px;
//         }
//         .score {
//           font-size: 2em;
//           color: #2c3e50;
//           margin-top: 20px;
//         }
//         .message {
//           font-size: 1.2em;
//           color: #555;
//           margin-top: 10px;
//         }
//       </style>
//     </head>
//     <body>
//       <div class="container">
//         <h1>Submission Result</h1>
//         <p class="message">Your code has been evaluated and scored as follows:</p>
//         <div class="score">${score}</div>
//         <p class="message">Thank you for your submission. This was your final attempt.</p>
//       </div>
//     </body>
//     </html>
//   `;
// }





















import * as vscode from 'vscode';
import { compareCode } from '../../api/flaskApi';

export function registerSubmitProvider(context: vscode.ExtensionContext) {
  const disposable = vscode.commands.registerCommand('ch.submit', async () => {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      vscode.window.showErrorMessage('No active editor found.');
      return;
    }

    // Retrieve the entire content of the current document
    const code = editor.document.getText();

    // Retrieve email and exerciseId from globalState
    const email = context.globalState.get<string>('userEmail');
    const exerciseId = context.globalState.get<string>('exerciseId');

    if (!email || !exerciseId) {
      vscode.window.showErrorMessage('Missing user email or exercise id in global state.');
      return;
    }

    // Inform the student this is their last submission and ask for confirmation
    const confirmation = await vscode.window.showWarningMessage(
      'This is your final submission and you will not be able to submit again. Are you sure you want to submit your code?',
      { modal: true },
      'Yes'
    );
    if (confirmation !== 'Yes') {
      // User cancelled the submission.
      return;
    }

    try {
      // Call the compareCode API with the proper parameters and await the result
      const result = await compareCode(exerciseId, email, code);
      
      // Check if an association already exists
      if (result.association_exists) {
        vscode.window.showInformationMessage(result.message || 'You have already completed this exercise.');
        return;
      }
      
      // If no prior submission exists, extract the score
      const score = result.response;

      // Create and display a new webview panel for the result
      const panel = vscode.window.createWebviewPanel(
        'submissionResult',
        'Submission Result',
        vscode.ViewColumn.One,
        {}
      );

      // Set the HTML content for the panel using a nice style
      panel.webview.html = getSubmissionWebviewContent(score);
    } catch (error) {
      vscode.window.showErrorMessage(`Error submitting code: ${error}`);
    }
  });
  context.subscriptions.push(disposable);
}

function getSubmissionWebviewContent(score: any): string {
  return `
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Submission Result</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          background-color: #f8f8f8;
          margin: 0;
          padding: 0;
        }
        .container {
          max-width: 800px;
          margin: 50px auto;
          background-color: #fff;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
          padding: 30px;
          text-align: center;
        }
        h1 {
          color: #444;
          margin-bottom: 20px;
        }
        .score {
          font-size: 2em;
          color: #2c3e50;
          margin-top: 20px;
        }
        .message {
          font-size: 1.2em;
          color: #555;
          margin-top: 10px;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <h1>Submission Result</h1>
        <p class="message">Your code has been evaluated and scored as follows:</p>
        <div class="score">${score}</div>
        <p class="message">Thank you for your submission. This was your final attempt.</p>
      </div>
    </body>
    </html>
  `;
}
