import * as vscode from 'vscode';
import { startQuiz, submitQuiz, Quiz, QuizResult } from '../../api/flaskApi';
import { requireSession } from './session';
import { page, escapeHtml, renderMarkdown, masteryBar, STATUS_LABEL } from '../../ui/webview';

type Scope = 'exercise' | 'course' | 'weak';

const SCOPES: { label: string; description: string; scope: Scope }[] = [
  { label: '$(beaker) This exercise', description: 'every concept of the current exercise', scope: 'exercise' },
  { label: '$(book) Everything my professor taught', description: 'all concepts of all your exercises', scope: 'course' },
  { label: '$(target) My weak concepts', description: 'only what you have not mastered yet', scope: 'weak' },
];

const DIFFICULTY = ['', 'easy', 'medium', 'hard'];

/** "Test me": an adaptive quiz over the professor's concepts, graded by the backend. */
export function registerQuizProvider(context: vscode.ExtensionContext) {
  context.subscriptions.push(vscode.commands.registerCommand('ch.testMe', async (preset?: Scope) => {
    const session = await requireSession(context);
    if (!session) { return; }
    let scope = preset;
    if (!scope) {
      const pick = await vscode.window.showQuickPick(SCOPES, { placeHolder: 'What should the tutor test you on?' });
      if (!pick) { return; }
      scope = pick.scope;
    }
    await runQuiz(context, session.email, session.exerciseId, scope);
  }));
}

async function runQuiz(context: vscode.ExtensionContext, email: string, exerciseId: string, scope: Scope) {
  let quiz: Quiz;
  try {
    quiz = await startQuiz(email, scope, exerciseId);
  } catch (error: any) {
    vscode.window.showErrorMessage(`Code Hinter: ${error.message || error}`);
    return;
  }
  const panel = vscode.window.createWebviewPanel('codeHinterQuiz', 'Test me', vscode.ViewColumn.Active, { enableScripts: true });
  panel.webview.html = page(panel.webview, 'Test me', quizHtml(quiz), QUIZ_SCRIPT);
  panel.webview.onDidReceiveMessage(async (msg: { cmd: string; arg?: string; answers?: Record<string, string> }) => {
    if (msg.cmd === 'submit' && msg.answers) {
      const unanswered = quiz.questions.filter(q => !String(msg.answers![q.qid] ?? '').trim()).length;
      if (unanswered) {
        const go = await vscode.window.showWarningMessage(
          `${unanswered} question(s) are unanswered. Submit anyway?`, { modal: true }, 'Submit');
        if (go !== 'Submit') {
          panel.webview.postMessage({ cmd: 'enable' });
          return;
        }
      }
      try {
        const result = await submitQuiz(email, quiz.id, msg.answers);
        panel.webview.html = page(panel.webview, 'Test me: results', resultHtml(result));
      } catch (error: any) {
        vscode.window.showErrorMessage(`Code Hinter: ${error.message || error}`);
        panel.webview.postMessage({ cmd: 'enable' });
      }
    } else if (msg.cmd === 'retest') {
      panel.dispose();
      await runQuiz(context, email, exerciseId, (msg.arg as Scope) || 'weak');
    } else if (msg.cmd === 'explain') {
      await vscode.commands.executeCommand('ch.explain', msg.arg);
    } else if (msg.cmd === 'progress') {
      await vscode.commands.executeCommand('ch.progress');
    }
  }, null, context.subscriptions);
}

export function quizHtml(quiz: Quiz): string {
  const questions = quiz.questions.map((q, i) => {
    let input: string;
    if (q.type === 'mcq') {
      input = (q.choices || []).map((c, j) =>
        `<label class="choice"><input type="radio" name="${escapeHtml(q.qid)}" value="${j}"> ${renderInline(c)}</label>`).join('');
    } else if (q.type === 'output') {
      input = `<input type="text" data-qid="${escapeHtml(q.qid)}" placeholder="Exactly what is printed">`;
    } else {
      input = `<textarea rows="3" data-qid="${escapeHtml(q.qid)}" placeholder="Answer in your own words"></textarea>`;
    }
    return `<div class="card">
      <div class="muted">Question ${i + 1} of ${quiz.questions.length} · <span class="tag">${escapeHtml(q.concept)}</span>
        <span class="tag">${DIFFICULTY[q.difficulty] || ''}</span></div>
      <p><strong>${renderInline(q.prompt)}</strong></p>
      ${q.code ? `<pre><code>${escapeHtml(q.code)}</code></pre>` : ''}
      ${input}</div>`;
  }).join('');
  return `<h1>🧪 Test me</h1>
    <p class="muted">${quiz.questions.length} questions, chosen for your level and for the concepts you know least.
      No hints here: show what you understand. You will get explanations after submitting.</p>
    ${questions}
    <button id="submit">Submit my answers</button>`;
}

const QUIZ_SCRIPT = `
const submit = document.getElementById('submit');
submit.addEventListener('click', () => {
  const answers = {};
  document.querySelectorAll('input[type=radio]:checked').forEach(r => { answers[r.name] = r.value; });
  document.querySelectorAll('[data-qid]').forEach(el => { answers[el.dataset.qid] = el.value; });
  submit.disabled = true;
  submit.textContent = 'Grading…';
  vscode.postMessage({ cmd: 'submit', answers });
});
window.addEventListener('message', e => {
  if (e.data.cmd === 'enable') { submit.disabled = false; submit.textContent = 'Submit my answers'; }
});`;

function renderInline(text: string): string {
  return escapeHtml(text).replace(/`([^`]+)`/g, '<code>$1</code>');
}

export function resultHtml(r: QuizResult): string {
  const concepts = r.concepts.map(c => `<tr>
      <td>${escapeHtml(c.concept)}</td>
      <td>${Math.round(c.credit * 10) / 10}/${c.questions}</td>
      <td style="width:35%">${masteryBar(c.mastery_after)}</td>
      <td>${Math.round(c.mastery_before * 100)}% → <strong>${Math.round(c.mastery_after * 100)}%</strong>
        <span class="muted">${escapeHtml(STATUS_LABEL[c.status] || c.status)}</span></td>
      <td>${c.mastery_after < 0.5 ? `<button class="secondary" data-cmd="explain" data-arg="${escapeHtml(c.concept)}">Explain</button>` : ''}</td>
    </tr>`).join('');
  const answers = r.results.map((q, i) => `<div class="card">
      <div><span class="${q.correct ? 'ok' : q.credit > 0 ? 'warn' : 'ko'}">${q.correct ? '✔ correct' : q.credit > 0 ? '◐ partly right' : '✘ not yet'}</span>
        · <span class="muted">Q${i + 1} · ${escapeHtml(q.concept)}</span></div>
      <p><strong>${renderInline(q.prompt)}</strong></p>
      ${q.code ? `<pre><code>${escapeHtml(q.code)}</code></pre>` : ''}
      <div>Your answer: <code>${escapeHtml(q.your_answer ?? '(none)')}</code></div>
      ${q.correct ? '' : `<div>Expected: <code>${escapeHtml(q.expected)}</code></div>`}
      <p class="muted">${renderInline(q.explanation)}${q.feedback ? ' ' + escapeHtml(q.feedback) : ''}</p>
      ${q.review ? `<details><summary>Review this idea</summary>${renderMarkdown(q.review)}</details>` : ''}
    </div>`).join('');
  return `<h1>🧪 Your result: ${r.score}%</h1>
    ${r.level_message ? `<div class="card">${escapeHtml(r.level_message)}</div>` : ''}
    <div class="card"><strong>Next step:</strong> ${escapeHtml(r.next_step)}</div>
    <h2>Concepts</h2><table>${concepts}</table>
    <div>
      <button data-cmd="retest" data-arg="weak">Test me again on weak concepts</button>
      <button class="secondary" data-cmd="progress">Open my progress</button>
    </div>
    <h2>Answers</h2>${answers}`;
}
