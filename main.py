import sys
from agent.logic import ClinicAgent
from eval.harness import run_evaluation

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "eval":
        run_evaluation()
    else:
        print("🤖 Starting Clinic Virtual Assistant (Interactive Mode)")
        print("Type 'exit' or 'quit' to end the conversation.\n")
        
        agent = ClinicAgent()
        while True:
            try:
                user_input = input("Patient: ")
                if user_input.lower() in ["exit", "quit"]:
                    print("Assistant: Have a great day! Goodbye.")
                    break
                
                reply = agent.chat(user_input)
                print(f"Assistant: {reply}\n")
            except KeyboardInterrupt:
                print("\nExiting...")
                break

if __name__ == "__main__":
    main()