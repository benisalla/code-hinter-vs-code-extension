import * as assert from 'assert';
import sinon from 'sinon';
import * as api from '../../api/flaskApi';

suite('Comparison Unit Test', () => {
  let sandbox: sinon.SinonSandbox;

  setup(() => {
    sandbox = sinon.createSandbox();
  });

  teardown(() => {
    sandbox.restore();
  });

  test('compareCode API returns comparison result', async () => {
    const stubResponse = { response: 'comparison result' };
    const compareStub = sandbox.stub(api, 'compareCode').resolves(stubResponse);

    const result = await api.compareCode('exercise_id', 'student_id', 'some code');
    assert.strictEqual(result.response, 'comparison result');
    assert.ok(compareStub.calledOnce);
  });
});
