# VS Code Extension LLM Backend

## 🚀 Installation and Setup on Remote Server

### 1️⃣ **Clone the project**

```sh
git clone https://github.com/benisalla/code-hinter-vs-code-extension.git
cd code-hinter-vs-code-extension/backend
```

### 2️⃣ **Create and activate a virtual environment**

```sh
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ **Install dependencies**

```sh
pip install --upgrade pip
pip install -r requirements.txt
```

### 4️⃣ **Run the Flask API**

You can clear any existing instance and start a new one on port 5000 with a single command:

```sh
pkill -f "python main.py" || true; nohup python main.py --port 5000 > output.log 2>&1 &
```

Add `--offline` to run the rule-based tutor without loading any LLM (no torch needed). The model can be
changed with `CH_MODEL` (default `HuggingFaceTB/SmolLM2-1.7B-Instruct`) and `CH_TORCH_DTYPE=bfloat16`
halves its memory on CPU.

### 5️⃣ **Test the API**

#### 🔹 Check if the API is running

```sh
curl http://127.0.0.1:5000/api/test/
```

#### 🔹 Evaluate code

```sh
curl -X POST http://127.0.0.1:5000/api/evaluate_code \
     -H "Content-Type: application/json" \
     -d '{"exercise_id": 1, "student_id": 123, "code": "print([x for x in range(10)])"}'
```

#### 🔹 Compare code

```sh
curl -X POST http://127.0.0.1:5000/api/compare_code \
     -H "Content-Type: application/json" \
     -d '{"exercise_id": 1, "student_id": 123, "code": "print([i for i in range(10)])"}'
```

#### 🔹 Complete code (HTTP API)

```sh
curl -X POST http://127.0.0.1:5000/api/complete_code \
     -H "Content-Type: application/json" \
     -d '{"code": "for i in range(10):"}'
```

#### 🔹 The tutor (hints, Test me, progress)

```sh
curl http://127.0.0.1:5000/api/tutor/status
curl -X POST http://127.0.0.1:5000/api/tutor/hint -H "Content-Type: application/json" \
     -d '{"email": "benalla@example.com", "exercise_id": 2, "code": "class Animal:\n    def (self): pass"}'
curl -X POST http://127.0.0.1:5000/api/tutor/quiz -H "Content-Type: application/json" \
     -d '{"email": "benalla@example.com", "scope": "exercise", "exercise_id": 1}'
```

All tutor endpoints are listed in the [main README](../README.md#api) and the design is explained in
[docs/how-the-tutor-works.md](../docs/how-the-tutor-works.md).

### 6️⃣ **Examples and tests**

```sh
python examples/02_hint_ladder.py      # 01 … 06, no server and no LLM needed
pip install pytest && python -m pytest -q tests
```

Learner profiles, quizzes and help requests are written to `data/learners.json`, `data/quizzes.json` and
`data/help_requests.json` (git-ignored).

👨‍💻 **Author:** Ben Alla Ismail