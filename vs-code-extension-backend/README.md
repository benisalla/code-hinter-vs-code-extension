# VS Code Extension LLM Backend

## 🚀 Installation and Setup on Remote Server

### 1️⃣ **Clone the project**

```sh
git clone https://github.com/benisalla/vs-code-extension-backend.git
cd vs-code-extension-backend
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

*Note: Ensure your application accepts the `--port` argument; if not, remove it or adjust the command accordingly.*

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

👨‍💻 **Author:** Ben Alla Ismail