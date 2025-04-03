# Code-Hinter README

Welcome to the README for the "code-hinter" VS Code extension. This extension enhances your coding experience by providing intelligent code hints, improving productivity with automated suggestions, and enabling interaction with a backend for code evaluation.

## Features

- **Intelligent Code Hints:** Suggests context-aware code snippets and completions.
- **Syntax Highlighting:** Customized color schemes for various programming languages.
- **API Interaction:** Evaluate, compare, and submit code directly from your editor.

> Tip: Check out our [demo video](https://youtu.be/IU4lvCVFDRM) on YouTube to see the extension in action!

## Installation and Setup

### Backend

#### 🚀 Setting Up on a Remote Server

##### 1️⃣ **Clone the Project**
```sh
git clone https://github.com/benisalla/vs-code-extension-backend.git
cd vs-code-extension-backend
```

##### 2️⃣ **Create and Activate a Virtual Environment**
```sh
python3 -m venv venv
source venv/bin/activate
```

##### 3️⃣ **Install Dependencies**
```sh
pip install --upgrade pip
pip install -r requirements.txt
```

##### 4️⃣ **Run the Flask API**
```sh
pkill -f "python main.py" || true; nohup python main.py --port 5000 > output.log 2>&1 &
```

*Note: Modify the port as necessary if your application requires a different one.*

##### 5️⃣ **Test the API**
###### 🔹 Check if the API is Running
```sh
curl http://127.0.0.1:5000/api/test/
```
###### 🔹 Evaluate, Compare, and Complete Code
```sh
curl -X POST http://127.0.0.1:5000/api/evaluate_code \
     -H "Content-Type: application/json" \
     -d '{"exercise_id": 1, "student_id": 123, "code": "print([x for x in range(10)])"}'
```

### Frontend

##### Activating Commands

After installation, access the extension's features through the Command Palette:

1. **Test API**
   - **Command:** `Ctrl+Shift+P` then `Code Hinter: Test api's`

2. **Login**
   - **Command:** `Ctrl+Shift+P` then `Code Hinter: Login`

3. **Logout**
   - **Command:** `Ctrl+Shift+P` then `Code Hinter: Logout`

4. **Evaluate Code**
   - **Command:** `Ctrl+Shift+P` then `Code Hinter: Evaluate Code`

5. **Submit Code for Comparison**
   - **Command:** `Ctrl+Shift+P` then `Code Hinter: submit Code for comparison`

6. **Change Exercise**
   - **Command:** `Ctrl+Shift+P` then `Code Hinter: change exercise`

Code suggestions are activated by pressing `Ctrl+Space` within a Python file.

## Extension Settings

This extension contributes the following settings:

- `codeHinter.enable`: Enable/disable this feature.
- `codeHinter.completionTrigger`: Set to `onType` to activate hints as you type.

## Requirements

- Python 3.8+
- Flask
- Other dependencies as listed in `requirements.txt`

---

## Extension Guidelines and Support

- [Extension Guidelines](https://code.visualstudio.com/api/references/extension-guidelines)
- [Visual Studio Code's Markdown Support](http://code.visualstudio.com/docs/languages/markdown)

## Additional Resources

- **Extension Demo:** [Watch on YouTube](https://youtu.be/IU4lvCVFDRM)
- **App Demonstration:** [Watch on YouTube](https://youtu.be/8QEqd-eQrrI)

**Enjoy coding with Code-Hinter!**