import * as assert from 'assert';
import sinon from 'sinon';
import * as api from '../../api/flaskApi';
import { stubGlobalFetch } from '../helpers/testUtils';

suite('Tutor API client', () => {
  let fetchStub: sinon.SinonStub;

  teardown(() => {
    fetchStub.restore();
    api.setBaseUrl(undefined);
  });

  test('getHint posts the code, diagnostics and ladder options to /tutor/hint', async () => {
    fetchStub = stubGlobalFetch({ hint: 'What does `=` do?', level: 1, max_level: 4 });
    api.setBaseUrl('http://localhost:5000/api/');
    const hint = await api.getHint('a@b.c', '4', 'if b = 0:', { more: true, diagnostics: [{ line: 1, message: 'invalid syntax', severity: 'error' }] });
    assert.strictEqual(hint.level, 1);
    const [url, init] = fetchStub.getCall(0).args;
    assert.strictEqual(url, 'http://localhost:5000/api/tutor/hint');
    const body = JSON.parse(init.body);
    assert.deepStrictEqual([body.email, body.exercise_id, body.code, body.more], ['a@b.c', '4', 'if b = 0:', true]);
    assert.strictEqual(body.diagnostics[0].line, 1);
  });

  test('query strings are encoded', async () => {
    fetchStub = stubGlobalFetch({ concepts: [] });
    api.setBaseUrl('http://h/api');
    await api.getProgress('first+last@x.com', '3');
    assert.strictEqual(fetchStub.getCall(0).args[0], 'http://h/api/tutor/progress?email=first%2Blast%40x.com&exercise_id=3');
  });

  test('the server error message reaches the student', async () => {
    fetchStub = stubGlobalFetch({ error: 'Quiz not found' }, false);
    await assert.rejects(api.submitQuiz('a@b.c', 'nope', {}), /Quiz not found/);
  });
});
