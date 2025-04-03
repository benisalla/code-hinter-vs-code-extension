// src/api/flaskApi.ts
const BASE_URL = 'http://156.18.90.98:5000/api';

export async function callTestEndpoint(): Promise<any> {
  const response = await fetch(`${BASE_URL}/test`, {
    method: 'GET'
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }
  return response.json();
}

export async function evaluateCode(exerciseId: string, email: string, code: string): Promise<any> {
  const response = await fetch(`${BASE_URL}/evaluate_code`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      exercise_id: exerciseId,
      email: email,
      code: code
    })
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }
  const data = await response.json() as { response: any };
  return data.response;
}

// export async function compareCode(exerciseId: string, email: string, code: string): Promise<any> {
//   const response = await fetch(`${BASE_URL}/compare_code`, {
//     method: 'POST',
//     headers: { 'Content-Type': 'application/json' },
//     body: JSON.stringify({
//       exercise_id: exerciseId,
//       email: email,
//       code: code
//     })
//   });
//   if (!response.ok) {
//     throw new Error(`API error: ${response.statusText}`);
//   }
//   const data = await response.json() as { response: any };
//   return data.response;
// }


export async function compareCode(exerciseId: string, email: string, code: string): Promise<any> {
  const response = await fetch(`${BASE_URL}/compare_code`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      exercise_id: exerciseId,
      email: email,
      code: code
    })
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }
  const data = await response.json();
  return data;
}


export async function completeCode(code: string): Promise<any> {
  const response = await fetch(`${BASE_URL}/complete_code`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  const data = await response.json() as { response: any };
  return data.response;
}

export async function login(email: string, password: string, exerciseId: string): Promise<{ message: string, user: { role: string, email: string, id: string, name: string } }> {
  const response = await fetch(`${BASE_URL}/signin`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: email,
      password: password,
      exercise_id: exerciseId,
    })
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }
  
  const data = await response.json() as { message: string, user: { role: string, email: string, id: string, name: string} };

  return {
    message: data.message,
    user: data.user
  };
}

export async function checkExerciseExistence(exerciseId: string): Promise<{ exists: boolean, error?: string }> {
  const response = await fetch(`${BASE_URL}/exercise`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      exercise_id: exerciseId
    })
  });

  const data = await response.json() as { error?: string };
  
  if (!response.ok) {
    if (response.status === 404) {
      return { exists: false, error: data.error };
    }
    throw new Error(`API error: ${data.error || response.statusText}`);
  }

  return { exists: true };
}