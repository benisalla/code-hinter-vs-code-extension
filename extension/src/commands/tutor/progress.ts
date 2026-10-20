import * as vscode from 'vscode';
import { getProgress, getMyHelpRequests, Progress, HelpRequest } from '../../api/flaskApi';
import { requireSession } from './session';
import { page, escapeHtml, masteryBar, STATUS_LABEL } from '../../ui/webview';

/** "My learning progress": every concept the professor taught, and how well the student knows it. */
export function registerProgressProvider(context: vscode.ExtensionContext) {
  context.subscriptions.push(vscode.commands.registerCommand('ch.progress', async () => {
    const session = await requireSession(context);
    if (!session) { return; }
    let progress: Progress;
    let requests: HelpRequest[] = [];
    try {
      [progress, requests] = await Promise.all([
        getProgress(session.email, session.exerciseId),
        getMyHelpRequests(session.email).catch(() => []),
      ]);
    } catch (error: any) {
      vscode.window.showErrorMessage(`Code Hinter: ${error.message || error}`);
      return;
    }
    const panel = vscode.window.createWebviewPanel('codeHinterProgress', 'My learning progress', vscode.ViewColumn.Active, { enableScripts: true });
    panel.webview.html = page(panel.webview, 'My learning progress', progressHtml(progress, requests));
    panel.webview.onDidReceiveMessage((msg: { cmd: string; arg?: string }) => {
      switch (msg.cmd) {
        case 'explain': return vscode.commands.executeCommand('ch.explain', msg.arg);
        case 'test': return vscode.commands.executeCommand('ch.testMe', msg.arg);
        case 'profile': return vscode.commands.executeCommand('ch.profile');
      }
    }, null, context.subscriptions);
  }));
}

export function progressHtml(p: Progress, requests: HelpRequest[]): string {
  const levelNote = p.effective_level !== p.level
    ? `<span class="muted">(you said ${escapeHtml(p.level)}; your results show ${escapeHtml(p.effective_level)})</span>` : '';
  const rows = p.concepts.map(c => `<tr>
      <td>${escapeHtml(c.label)}<div class="muted">exercise ${escapeHtml(c.exercise_id)}</div></td>
      <td style="width:30%">${masteryBar(c.mastery)}</td>
      <td>${c.status === 'not_started' ? '<span class="muted">not tested yet</span>' : `${Math.round(c.mastery * 100)}% · ${escapeHtml(STATUS_LABEL[c.status])}`}</td>
      <td class="muted nowrap">${c.hints} hint${c.hints === 1 ? '' : 's'}</td>
      <td><button class="secondary" data-cmd="explain" data-arg="${escapeHtml(c.label)}">Explain</button></td>
    </tr>`).join('');
  const recs = p.recommendations.map(r => `<li>${escapeHtml(r.text)}
      <button class="secondary" data-cmd="${r.action === 'test' ? 'test' : 'explain'}" data-arg="${r.action === 'test' ? 'weak' : escapeHtml(r.concept)}">
      ${r.action === 'test' ? 'Test me' : 'Explain'}</button></li>`).join('');
  const ready = p.readiness ? `<div class="card ${p.readiness.ready ? 'ok' : 'warn'}">
      <strong>Current exercise:</strong> ${escapeHtml(p.readiness.message)}</div>` : '';
  const quizzes = p.quiz_history.slice().reverse().map(q =>
    `<tr><td>${escapeHtml(new Date(q.at).toLocaleString())}</td><td>${escapeHtml(q.scope)}</td><td>${q.n} questions</td><td><strong>${q.score}%</strong></td></tr>`).join('');
  const replies = requests.slice().reverse().map(r => `<div class="card">
      <span class="tag">${escapeHtml(r.status)}</span> exercise ${escapeHtml(r.exercise_id)} · ${escapeHtml(r.message)}
      ${r.reply ? `<p><strong>Professor:</strong> ${escapeHtml(r.reply)}</p>` : '<p class="muted">Waiting for your professor.</p>'}</div>`).join('');
  return `<h1>📈 My learning progress</h1>
    <div><span class="tag">level: ${escapeHtml(p.effective_level)}</span> ${levelNote}
      <span class="tag">learns with: ${escapeHtml(p.style.replace(/_/g, ' '))}</span>
      <button class="secondary" data-cmd="profile">Change</button></div>
    <div class="card"><strong>${p.coverage}%</strong> of the concepts your professor taught are mastered ·
      ${p.counts.mastered} mastered · ${p.counts.almost} almost · ${p.counts.learning} learning · ${p.counts.not_started} not tested ·
      ${p.hints_used} hints used</div>
    ${ready}
    ${recs ? `<h2>What to do next</h2><ul>${recs}</ul>` : ''}
    <div><button data-cmd="test" data-arg="course">Test me on everything</button>
      <button class="secondary" data-cmd="test" data-arg="weak">Test me on my weak concepts</button></div>
    <h2>Concepts</h2><table>${rows}</table>
    ${quizzes ? `<h2>Recent tests</h2><table>${quizzes}</table>` : ''}
    ${replies ? `<h2>Questions to my professor</h2>${replies}` : ''}`;
}
