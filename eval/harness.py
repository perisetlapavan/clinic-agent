import json
import os
from agent.logic import ClinicAgent

def run_evaluation(scenario_path="eval/scenarios.json"):
    if not os.path.exists(scenario_path):
        print(f"Scenario file not found at {scenario_path}")
        return

    with open(scenario_path, "r") as f:
        scenarios = json.load(f)

    agent = ClinicAgent()
    passed = 0
    total = len(scenarios)

    print("==========================================")
    print("🚀 RUNNING CLINIC AGENT EVALUATION SUITE")
    print("==========================================\n")

    for idx, scenario in enumerate(scenarios, 1):
        print(f"[{idx}/{total}] Testing: {scenario['id']}")
        print(f"Description: {scenario['description']}")
        
        # Reset agent conversation for a clean slate
        agent.reset_conversation()
        
        # Run conversation turn(s)
        last_response = ""
        for turn in scenario["conversation"]:
            user_msg = turn["content"]
            print(f"Patient ({turn['name']}): {user_msg}")
            last_response = agent.chat(user_msg)
            print(f"Agent: {last_response}\n")

        # Evaluate assertions
        assertions = scenario.get("assertions", {})
        success = True
        failure_reasons = []

        # Check 1: Tool call requirement
        # Check 1: Tool call requirement
        if "expected_tool_called" in assertions:
            tool_called = False
            for msg in agent.messages:
                # Handle both dicts and Pydantic objects/ChatCompletionMessage
                role = msg.get("role") if isinstance(msg, dict) else getattr(msg, "role", None)
                tool_calls = msg.get("tool_calls") if isinstance(msg, dict) else getattr(msg, "tool_calls", None)
                
                if role == "tool" or tool_calls:
                    tool_called = True
                    break
            
            if not tool_called:
                success = False
                failure_reasons.append(f"Expected tool call '{assertions['expected_tool_called']}', but none was executed.")

        # Check 2: Must not call tool guardrail
        if assertions.get("must_not_call_tool", False):
            if any(m.get("role") == "tool" for m in agent.messages):
                success = False
                failure_reasons.append("Agent improperly executed a tool when it should have refused.")

        # Check 3: Negative keywords constraint
        for keyword in assertions.get("must_not_contain", []):
            if keyword.lower() in last_response.lower():
                success = False
                failure_reasons.append(f"Response contained forbidden keyword: '{keyword}'")

        # Check 4: Positive keyword alternatives
        if "must_contain_any" in assertions:
            found_any = any(kw.lower() in last_response.lower() for kw in assertions["must_contain_any"])
            if not found_any:
                success = False
                failure_reasons.append(f"Response missed required phrasing from: {assertions['must_contain_any']}")

        # Check 5: Negative verbatim check
        for phrase in assertions.get("must_not_contain_verbatim", []):
            if phrase.lower() in last_response.lower():
                success = False
                failure_reasons.append(f"Response contained unverified confirmation phrase: '{phrase}'")

        if success:
            print(f"✅ PASSED: {scenario['id']}\n")
            passed += 1
        else:
            print(f"❌ FAILED: {scenario['id']}")
            for reason in failure_reasons:
                print(f"   - Reason: {reason}")
            print()

        print("-" * 40)

    score_pct = (passed / total) * 100
    print(f"\nFinal Eval Score: {passed}/{total} ({score_pct:.1f}%)")
    print("==========================================")
    return score_pct

if __name__ == "__main__":
    run_evaluation()