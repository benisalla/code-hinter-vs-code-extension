import * as vscode from 'vscode';
import { getProfile, updateProfile, Level, Style } from '../../api/flaskApi';
import { requireSession } from './session';

const LEVELS: { label: string; description: string; level: Level }[] = [
  { label: 'Beginner', description: 'I am new to programming or to these concepts', level: 'beginner' },
  { label: 'Intermediate', description: 'I know the basics but still make mistakes', level: 'intermediate' },
  { label: 'Advanced', description: 'I am comfortable and want deeper explanations', level: 'advanced' },
];

const STYLES: { label: string; description: string; style: Style }[] = [
  { label: '$(code) Show me examples', description: 'small concrete code examples', style: 'examples' },
  { label: '$(lightbulb) Use analogies', description: 'real-life comparisons', style: 'analogies' },
  { label: '$(list-ordered) Step by step', description: 'short numbered steps', style: 'step_by_step' },
  { label: '$(question) Ask me questions', description: 'guide me with questions so I find it myself', style: 'socratic' },
];

/** Asks the student how they learn; the tutor uses it for every hint, explanation and quiz. */
export async function setUpProfile(context: vscode.ExtensionContext, firstTime = false) {
  const session = await requireSession(context);
  if (!session) { return; }
  try {
    const current = await getProfile(session.email);
    const level = await vscode.window.showQuickPick(
      LEVELS.map(l => ({ ...l, picked: l.level === current.level })),
      { placeHolder: firstTime ? 'Welcome! How would you describe your level? (the tutor will adapt as it learns about you)' : `Your level (currently ${current.level}, your results show ${current.effective_level})` });
    if (!level) { return; }
    const style = await vscode.window.showQuickPick(
      STYLES.map(s => ({ ...s, picked: s.style === current.style })),
      { placeHolder: 'How do you understand things best?' });
    if (!style) { return; }
    await updateProfile(session.email, { level: level.level, style: style.style });
    const next = await vscode.window.showInformationMessage(
      `Got it: ${level.label.toLowerCase()} level, ${style.description}. Want a quick test so the tutor knows where you stand?`,
      'Test me now', 'Later');
    if (next === 'Test me now') {
      await vscode.commands.executeCommand('ch.testMe', 'exercise');
    }
  } catch (error: any) {
    vscode.window.showErrorMessage(`Code Hinter: ${error.message || error}`);
  }
}

export function registerProfileProvider(context: vscode.ExtensionContext) {
  context.subscriptions.push(vscode.commands.registerCommand('ch.profile', () => setUpProfile(context)));
}
