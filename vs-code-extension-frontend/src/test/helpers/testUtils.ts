import * as sinon from 'sinon';

/**
 * Stub the global fetch function.
 * @param response The JSON response to return.
 * @param ok Whether the response is OK (default: true).
 */
export function stubGlobalFetch(response: any, ok = true) {
    return sinon.stub(global, 'fetch').callsFake(async (input: string | URL | Request, init?: RequestInit): Promise<Response> => {
        return Promise.resolve({
            ok,
            status: ok ? 200 : 500,
            statusText: ok ? 'OK' : 'Error',
            json: async () => response,
            text: async () => JSON.stringify(response),
        } as Response);
    });
}
