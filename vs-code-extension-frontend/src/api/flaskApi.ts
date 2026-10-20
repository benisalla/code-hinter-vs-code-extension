// src/api/flaskApi.ts
export const DEFAULT_BASE_URL = 'http://156.18.90.98:5000/api';
let BASE_URL = DEFAULT_BASE_URL;

/** Set from the `codeHinter.serverUrl` setting (see extension.ts). */
export function setBaseUrl(url: string | undefined) {
  BASE_URL = (url || DEFAULT_BASE_URL).replace(/\/+$/, '');
}

export async function callTestEndpoint(): Promise<any> {
  const response = await fetch(`${BASE_URL}/test`, {
    method: 'GET'
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }
  return response.json();
}

export async function evaluateCode(exerciseId: string, email: string, code: string): Promise<EvaluationResult> {
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
  return await response.json() as EvaluationResult;
}

export interface EvaluationResult {
  response: string;
  concepts: { concept: string; key: string; satisfied: boolean }[];
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

// ===================================================================== //
// Tutor API: learner profile, hints, explanations, "Test me", progress
// ===================================================================== //

export type Level = 'beginner' | 'intermediate' | 'advanced';
export type Style = 'examples' | 'analogies' | 'step_by_step' | 'socratic';

export interface LearnerProfile {
  email: string;
  level: Level;
  style: Style;
  goal: string;
  onboarded: boolean;
  effective_level: Level;
}

export interface Diagnostic { line: number; message: string; severity: string }

export interface Hint {
  hint: string;
  level: number;
  level_name: string;
  max_level: number;
  concept: string;
  concept_key: string;
  line: number | null;
  check_question: string;
  escalate: boolean;
  escalate_message: string | null;
  source: 'llm' | 'rules';
}

export interface Explanation { concept: string; topic: string; style: Style; level: Level; explanation: string; source: string }

export interface ConceptView {
  key: string;
  label: string;
  topic: string;
  exercise_id?: number;
  mastery: number;
  status: 'not_started' | 'learning' | 'almost' | 'mastered';
  evidence: number;
  hints: number;
}

export interface QuizQuestion {
  qid: string;
  concept: string;
  concept_key: string;
  topic: string;
  type: 'mcq' | 'output' | 'open';
  difficulty: number;
  prompt: string;
  code: string | null;
  choices?: string[];
}

export interface Quiz { id: string; scope: string; created_at: string; questions: QuizQuestion[] }

export interface QuizResult {
  quiz_id: string;
  score: number;
  results: {
    qid: string; concept: string; type: string; prompt: string; code: string | null; your_answer: string | null;
    credit: number; correct: boolean; expected: string; explanation: string; feedback: string; review: string | null;
  }[];
  concepts: { concept: string; credit: number; questions: number; mastery_before: number; mastery_after: number; status: string }[];
  level_before: Level;
  level_after: Level;
  level_message: string | null;
  next_step: string;
}

export interface Readiness { exercise_id: number; ready: boolean; concepts: ConceptView[]; missing: string[]; message: string }

export interface Progress {
  email: string;
  level: Level;
  effective_level: Level;
  style: Style;
  concepts: ConceptView[];
  counts: Record<string, number>;
  coverage: number;
  quiz_history: { quiz_id: string; scope: string; score: number; at: string; n: number }[];
  hints_used: number;
  recommendations: { concept: string; key: string; action: 'test' | 'explain'; text: string }[];
  readiness: Readiness | null;
}

export interface HelpRequest {
  id: number; exercise_id: number; concept: string | null; message: string; status: string; reply?: string; created_at: string;
}

async function tutorRequest<T>(method: 'GET' | 'POST' | 'PUT', path: string, body?: object): Promise<T> {
  const response = await fetch(`${BASE_URL}/tutor${path}`, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await response.json().catch(() => ({})) as any;
  if (!response.ok) {
    throw new Error(data.error || `API error: ${response.statusText}`);
  }
  return data as T;
}

const qs = (params: Record<string, string | undefined>) =>
  '?' + Object.entries(params).filter(([, v]) => v !== undefined).map(([k, v]) => `${k}=${encodeURIComponent(v as string)}`).join('&');

export const getProfile = (email: string) => tutorRequest<LearnerProfile>('GET', `/profile${qs({ email })}`);

export const updateProfile = (email: string, changes: Partial<Pick<LearnerProfile, 'level' | 'style' | 'goal'>>) =>
  tutorRequest<LearnerProfile>('PUT', '/profile', { email, ...changes });

export const getHint = (email: string, exerciseId: string, code: string,
  opts: { question?: string; diagnostics?: Diagnostic[]; more?: boolean; level?: number } = {}) =>
  tutorRequest<Hint>('POST', '/hint', { email, exercise_id: exerciseId, code, ...opts });

export const explainConcept = (email: string, concept: string, exerciseId?: string) =>
  tutorRequest<Explanation>('POST', '/explain', { email, concept, exercise_id: exerciseId });

export const getConcepts = (email: string, exerciseId?: string) =>
  tutorRequest<ConceptView[]>('GET', `/concepts${qs({ email, exercise_id: exerciseId })}`);

export const startQuiz = (email: string, scope: 'exercise' | 'course' | 'weak', exerciseId?: string) =>
  tutorRequest<Quiz>('POST', '/quiz', { email, scope, exercise_id: exerciseId });

export const submitQuiz = (email: string, quizId: string, answers: Record<string, string | number>) =>
  tutorRequest<QuizResult>('POST', `/quiz/${quizId}/submit`, { email, answers });

export const getProgress = (email: string, exerciseId?: string) =>
  tutorRequest<Progress>('GET', `/progress${qs({ email, exercise_id: exerciseId })}`);

export const getReadiness = (email: string, exerciseId: string) =>
  tutorRequest<Readiness>('GET', `/readiness${qs({ email, exercise_id: exerciseId })}`);

export const askProfessor = (email: string, exerciseId: string, message: string, code: string, concept?: string) =>
  tutorRequest<HelpRequest>('POST', '/help_request', { email, exercise_id: exerciseId, message, code, concept });

export const getMyHelpRequests = (email: string) =>
  tutorRequest<HelpRequest[]>('GET', `/help_requests${qs({ email })}`);

export const getTutorStatus = () =>
  tutorRequest<{ llm_backend: string; llm_available: boolean }>('GET', '/status');
