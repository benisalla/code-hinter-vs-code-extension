// src/test/runTest.ts
// Force using the local VS Code installation (update the path if needed)
process.env.VSCODE_TEST_PATH = 'C:\\Program Files\\Microsoft VS Code\\Code.exe';

import * as path from 'path';
import { runTests } from 'vscode-test';

async function main() {
  try {
    // The folder containing your extension's package.json.
    const extensionDevelopmentPath = path.resolve(__dirname, '../../');
    // The path to your tests (this folder).
    const extensionTestsPath = path.resolve(__dirname, './');
    
    // Run the tests.
    await runTests({ extensionDevelopmentPath, extensionTestsPath });
  } catch (err) {
    console.error('Failed to run tests', err);
    process.exit(1);
  }
}

main();
