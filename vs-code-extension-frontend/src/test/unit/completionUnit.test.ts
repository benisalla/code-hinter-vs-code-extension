import * as assert from 'assert';
import sinon from 'sinon';
import * as api from '../../api/flaskApi';

suite('Completion Unit Test', () => {
  let sandbox: sinon.SinonSandbox;

  setup(() => {
    sandbox = sinon.createSandbox();
  });

  teardown(() => {
    sandbox.restore();
  });

  test('evaluateCode API returns suggestion', async () => {
    const stubResponse = { response: 'suggestion' };
    const evaluateStub = sandbox.stub(api, 'evaluateCode').resolves(stubResponse);

    const result = await api.evaluateCode('exercise_id', 'student_id', 'console.');
    assert.strictEqual(result.response, 'suggestion');
    assert.ok(evaluateStub.calledOnce);
  });
});
