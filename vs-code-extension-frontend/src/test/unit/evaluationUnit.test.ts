import * as assert from 'assert';
import sinon from 'sinon';
import * as api from '../../api/flaskApi';

suite('Evaluation Unit Test', () => {
  let sandbox: sinon.SinonSandbox;

  setup(() => {
    sandbox = sinon.createSandbox();
  });

  teardown(() => {
    sandbox.restore();
  });

  test('evaluateCode API returns evaluation result', async () => {
    const stubResponse = { response: 'evaluation result' };
    const evaluateStub = sandbox.stub(api, 'evaluateCode').resolves(stubResponse);

    const result = await api.evaluateCode('exercise_id', 'student_id', 'some code');
    assert.strictEqual(result.response, 'evaluation result');
    assert.ok(evaluateStub.calledOnce);
  });
});
