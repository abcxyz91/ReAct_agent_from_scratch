# =========================
# Imports
# =========================

import os, re
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from typing import Dict, List
from tools import known_actions
from system_prompt import prompt_template

# =========================
# Environment & Client
# =========================

_ = load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# =========================
# Define Agent class
# =========================

"""
Step by step explanation of the Agent class:
1. agent = Agent(...) runs __init__ → stores the system message.
2. agent(<user_message>) runs __call__ → adds user message → calls execute.
3. execute() sends everything to the GPT model → gets response.
4. That response is stored and returned.
5. run() manages the ReAct loop, executing actions and feeding observations back to the agent.
6. It continues until a final answer is produced or max_turns is reached.
"""

# Define a type alias for message dictionaries
Message = Dict[str, str]

class Agent:
    def __init__(self, system: str ="", model: str ="gpt-5-mini", temperature: float = 1.0) -> None:
        """
        Initializes the agent with a system prompt and model settings.
        
        Args:
            system: The system prompt to guide the agent's behavior.
            model: The identifier for the OpenAI model (e.g., "gpt-5-mini").
            temperature: The sampling temperature for the model (0.0 for deterministic).
        """
        self.system = system
        self.model = model
        self.temperature = temperature

        self.messages: List[Message] = []
        if self.system:
            self.messages.append({"role": "system", "content": system})


    def __call__(self, message: str) -> str:
        """
        Allows the agent instance to be called like a function.
        Adds the user message, executes one step, and returns the result.
        
        Args:
            message: The user's input message.
            
        Returns:
            The assistant's response (which could be a Thought, Action, or Answer).
        """
        self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result


    def execute(self) -> str:
        """Execute method sends the accumulated messages to the OpenAI API and retrieves the assistant's response"""
        try:
            completion = client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=self.messages
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Error during API call: {e}"


    def run(self, prompt: str, max_turns: int = 5) -> str:
        """
        Run the agent in a loop until it produces a final answer or reaches max_turns.
        It looks for "Action: <action>: <input>" patterns in the agent's responses,
        executes the corresponding action, and feeds the observation back into the agent.
        Finally, it returns the agent's last response when no more actions are found.
        
        Args:
            prompt: The initial user query.
            max_turns: The maximum number of tool-use cycles before stopping.
            
        Returns:
            The final "Answer:" from the agent.
        """
        i = 0
        next_prompt = prompt

        # Regular expression to match lines with the pattern "Action: <tool_name>: <input_string>"
        action_re = re.compile(r'^Action: (\w+): (.*)$')

        while i < max_turns:
            i += 1
            # 1. Get the agent's response (Thought, Action, or Answer)
            result = self(next_prompt)
            print(result)

            # 2. Find and execute actions
            # Split the result into lines, look for action patterns, extract into a list
            actions = [
                action_re.match(a) for a in result.splitlines() if action_re.match(a)
            ]

            if actions:
                action, action_input = actions[0].groups() # Get the first action's name and input
                if action not in known_actions:
                    raise ValueError(f"Unknown action: {action}")
                else:
                    try:
                        # 3. Run the tool and get the observation
                        print(f" -- Running {action}: {action_input}")
                        observation = known_actions[action](action_input) # Execute the action if found
                    except Exception as e:
                        observation = f"Error executing action {action}: {e}"

                print(f" -- Observation: {observation}")
                
                # 4. Feed the observation back
                next_prompt = (
                    f"Observation: {observation}\n\n"
                    f"Given the original user question: \"{prompt}\", do ONE of the following:\n"
                    "- If the observation already contains the answer or enough data to compute it, respond immediately with `Answer: ...`.\n"
                    "- Otherwise, continue the ReAct loop with Thought → Action → PAUSE → Observation, and produce exactly ONE next Action.\n"
                )
            else:
                return result
            
        return "Agent reached maximum turns without a final answer."

# =========================
# Run the agent pipeline
# =========================

if __name__ == "__main__":
    # 1. Format the ReAct system prompt
    system_prompt = prompt_template.format(
        current_date=datetime.now().strftime("%Y-%m-%d")
    )
    
    # 2. Create the agent instance
    agent = Agent(system=system_prompt)
    
    # 3. Run the agent
    print("Welcome to the ReAct Agent. Type 'exit' to quit.")
    while True:
        user_query = input("\nEnter your question: ")
        if user_query.lower() == 'exit':
            break
        final_response = agent.run(user_query)
        print(f"\n\nFinal Response:\n{final_response}")

