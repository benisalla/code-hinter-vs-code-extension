import * as assert from 'assert';
import { escapeHtml, renderMarkdown, masteryBar } from '../../functionalities/tutor/webview';

suite('Tutor webview rendering', () => {
  test('escapeHtml neutralises markup coming from the backend or the LLM', () => {
    assert.strictEqual(escapeHtml('<img src=x onerror="alert(1)">'), '&lt;img src=x onerror=&quot;alert(1)&quot;&gt;');
    assert.strictEqual(escapeHtml(undefined), '');
  });

  test('renderMarkdown renders code, bold and lists but never raw HTML', () => {
    const html = renderMarkdown('Focus on **loops**.\n\n```python\nfor i in range(3):\n    print(i < 2)\n```\n\n1. first\n2. `second`\n\n<script>x</script>');
    assert.ok(html.includes('<strong>loops</strong>'));
    assert.ok(html.includes('<pre><code>for i in range(3):\n    print(i &lt; 2)</code></pre>'));
    assert.ok(html.includes('<ol><li>first</li><li><code>second</code></li></ol>'));
    assert.ok(!html.includes('<script>'));
  });

  test('masteryBar width follows mastery', () => {
    assert.ok(masteryBar(0.42).includes('width:42%'));
  });
});
