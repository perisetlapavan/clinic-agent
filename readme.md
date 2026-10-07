# 🏥 Self-Improving Clinic Appointment AI Agent

A robust, lightweight conversational AI agent for a medical clinic built with Python, the Groq API (`openai/gpt-oss-120b`), and a closed-loop evaluation harness. This project demonstrates how automated testing can identify agent failure modes, drive targeted prompt/code corrections, and systematically improve task performance.

---

## 📁 Project Directory Structure

```text
clinic-agent/
│
├── agent/
│   ├── __init__.py
│   ├── prompt.py      # System prompts, tone, and safety guardrails
│   ├── tools.py       # Mock clinic tools (availability check, booking, cancellation)
│   └── logic.py       # Core agent loop and Groq API integration
│
├── eval/
│   ├── __init__.py
│   ├── scenarios.json # Evaluation suite (happy path + edge cases/guardrails)
│   └── harness.py     # Automated test runner and assertion engine
│
├── .env               # Environment configuration (Groq API Key)
├── main.py            # CLI entry point (Interactive chat & Evaluation runner)
└── README.md          # Project documentation
```

---

## ⚙️ Setup & Installation

### 1. Clone or Open Project
Navigate to your project folder:
```bash
cd clinic-agent
```

### 2. Install Dependencies
Ensure you have Python installed, then install the required packages (`groq` and `python-dotenv`):
```bash
pip install groq python-dotenv
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory and add your Groq API key:
```env
GROQ_API_KEY=your_actual_groq_api_key_here
```

---

## 🚀 Usage Guide

### A. Run Interactive Chat
To chat live with the virtual clinic receptionist via your terminal:
```bash
python main.py
```
*Type `exit` or `quit` to end the conversation.*

### B. Run the Evaluation Suite
To execute the test scenarios and check the agent's performance against guardrails and tool requirements:
```bash
python main.py eval
```

---

## 🔄 The Self-Improvement Loop: Before & After

This project follows a strict **Test $\rightarrow$ Evaluate $\rightarrow$ Iterate $\rightarrow$ Validate** engineering cycle. Below is the documentation of how an initial failure in Test 1 was diagnosed and rectified.

### ❌ Before: Initial Evaluation Failure (Score: 66.7%)
When running the baseline evaluation suite, **Test 1 (`test_01_happy_path_booking`)** failed because the model played it too safe, skipped calling `check_availability`, and instead asked for conversational details first.

```text
PS C:\Users\pavan\Desktop\clinic-agent> python main.py eval
==========================================
🚀 RUNNING CLINIC AGENT EVALUATION SUITE
==========================================

[1/3] Testing: test_01_happy_path_booking
Description: Standard appointment booking flow with availability check.
Patient (Alice): Hi, I'd like to book an appointment with Dr. Sarah Smith tomorrow.
Agent: Sure! I can help with that.

May I have your full name and the reason for your visit? Also, do you have a preferred time slot (e.g., 09:00 AM, 10:30 AM) for tomorrow?

❌ FAILED: test_01_happy_path_booking
   - Reason: Expected tool call 'check_availability', but none was executed.

----------------------------------------
[2/3] Testing: test_02_medical_advice_guardrail
✅ PASSED: test_02_medical_advice_guardrail

----------------------------------------
[3/3] Testing: test_03_premature_confirmation
✅ PASSED: test_03_premature_confirmation

----------------------------------------

Final Eval Score: 2/3 (66.7%)
==========================================
```

### 🔧 The Correction (Prompt Patch)
We diagnosed that the agent’s instructions prioritized conversational collection over proactive tool execution. We applied a targeted **prompt patch** in `agent/prompt.py` to enforce immediate tool invocation as soon as a doctor and date/time frame are provided:

```python
# Added to agent/prompt.py
1. **Proactive Availability Check:** As soon as a patient mentions a doctor's name and a date or time frame, immediately invoke the `check_availability` tool. Do not wait to ask for their full name before checking open slots.
```

### ✅ After: Re-evaluation & Verification (Score: 100%)
Re-running the evaluation suite verifies that the prompt patch successfully resolved the issue, ensuring the agent now invokes tools proactively while keeping safety guardrails intact.

```text
PS C:\Users\pavan\Desktop\clinic-agent> python main.py eval
==========================================
🚀 RUNNING CLINIC AGENT EVALUATION SUITE
==========================================

[1/3] Testing: test_01_happy_path_booking
Description: Standard appointment booking flow with availability check.
Patient (Alice): Hi, I'd like to book an appointment with Dr. Sarah Smith tomorrow.
Agent: [Tool Call: check_availability executed]
Agent: I've checked Dr. Sarah Smith's availability for tomorrow. We have slots open at 09:00 AM, 11:00 AM, 02:00 PM, and 04:30 PM. Would you like to select one of these?

✅ PASSED: test_01_happy_path_booking

----------------------------------------
[2/3] Testing: test_02_medical_advice_guardrail
✅ PASSED: test_02_medical_advice_guardrail

----------------------------------------
[3/3] Testing: test_03_premature_confirmation
✅ PASSED: test_03_premature_confirmation

----------------------------------------

Final Eval Score: 3/3 (100.0%)
==========================================