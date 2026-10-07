clinic-agent/
│
├── agent/
│   ├── __init__.py
│   ├── prompt.py      # System prompts, tone, safety guardrails
│   ├── tools.py       # Mock clinic tools (availability, booking, cancel)
│   └── logic.py       # Core agent loop (e.g., using LangGraph or standard chat loop)
│
├── eval/
│   ├── __init__.py
│   ├── scenarios.json # Test cases (happy path + hard edge cases)
│   └── harness.py     # Evaluation runner & scoring logic
│
├── improvements/      # Where we store prompt patches or code adjustments after failures
│
├── main.py            # CLI entry point to run a live chat or run the eval suite
└── README.md          # Clear instructions on how to run everything