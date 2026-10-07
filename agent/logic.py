import os
import json
from groq import Groq
from dotenv import load_dotenv
from agent.prompt import CLINIC_SYSTEM_PROMPT
from agent.tools import check_availability, book_appointment, cancel_appointment

# Load environment variables from .env
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Map tool names to actual Python functions
AVAILABLE_TOOLS = {
    "check_availability": check_availability,
    "book_appointment": book_appointment,
    "cancel_appointment": cancel_appointment
}

# Define tool schemas for the Groq API
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Check available time slots for a specific doctor on a given date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doctor_name": {"type": "string", "description": "Name of the doctor (e.g., Dr. Sarah Smith)"},
                    "date": {"type": "string", "description": "Date in YYYY-MM-DD format"}
                },
                "required": ["doctor_name", "date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book an appointment for a patient with a doctor at a specific time slot.",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_name": {"type": "string", "description": "Full name of the patient"},
                    "doctor_name": {"type": "string", "description": "Name of the doctor"},
                    "time_slot": {"type": "string", "description": "Selected time slot (e.g., 09:00 AM)"},
                    "reason": {"type": "string", "description": "Reason for the visit or symptoms"}
                },
                "required": ["patient_name", "doctor_name", "time_slot", "reason"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_appointment",
            "description": "Cancel an existing appointment by its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_id": {"type": "string", "description": "The unique appointment ID (e.g., APT-12345678)"}
                },
                "required": ["appointment_id"]
            }
        }
    }
]

class ClinicAgent:
    def __init__(self, system_prompt: str = CLINIC_SYSTEM_PROMPT):
        self.system_prompt = system_prompt
        self.messages = [
            {"role": "system", "content": self.system_prompt}
        ]

    def reset_conversation(self):
        """Clears chat history while maintaining the system prompt."""
        self.messages = [{"role": "system", "content": self.system_prompt}]

    def update_system_prompt(self, new_prompt: str):
        """Allows updating the system prompt dynamically (used for our self-correction loop!)."""
        self.system_prompt = new_prompt
        self.messages[0] = {"role": "system", "content": self.system_prompt}

    def chat(self, user_message: str) -> str:
        """Processes a user message, handles tool calls, and returns the final response."""
        self.messages.append({"role": "user", "content": user_message})

        # Call Groq API with gpt-oss-120b
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=self.messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
            temperature=0.3
        )

        response_message = response.choices[0].message
        
        # Check if the model wants to call a tool
        if response_message.tool_calls:
            # Append assistant's request to call tools into the history
            self.messages.append(response_message)

            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                # Execute the corresponding local python tool function
                if function_name in AVAILABLE_TOOLS:
                    tool_function = AVAILABLE_TOOLS[function_name]
                    tool_output = tool_function(**function_args)

                    # Append tool response back into conversation history
                    self.messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": tool_output
                    })

            # Make a second follow-up call to the LLM so it can interpret the tool output for the patient
            second_response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=self.messages,
                temperature=0.3
            )
            
            final_reply = second_response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": final_reply})
            return final_reply

        else:
            # Standard conversational response without tools
            final_reply = response_message.content
            self.messages.append({"role": "assistant", "content": final_reply})
            return final_reply