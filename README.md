# Interview Eval

## Description

This project implements an AI-driven dialogue evaluation system, focusing on simulating conversations between an Evaluator (acting as a user) and an Evaluatee (acting as an AI assistant). The current implementation is centered around a travel planning scenario, but the system is designed to be flexible and adaptable to various interview situations.

The system uses LangChain and OpenAI's GPT models to generate dynamic, context-aware responses for both the Evaluator and Evaluatee. The Evaluator operates in different states (Exploration, Comforting, and Action) to simulate various user behaviors and needs.

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/scottsuk0306/interview-eval.git
   cd interview-eval
   ```

2. Install Poetry (if not already installed):
   ```
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. Install project dependencies:
   ```
   poetry install
   ```

4. Activate the virtual environment:
   ```
   poetry shell
   ```

5. Set up your OpenAI API key:
   - Create a `.env` file in the project root
   - Add your OpenAI API key: `OPENAI_API_KEY=your-api-key-here`


## Usage

To run the default travel planning evaluation scenario:

```
python main.py
```

This will initiate a conversation between the Evaluator and Evaluatee, simulating a travel planning assistance scenario.

## Customizing the Interview Situation

To create a custom interview situation, follow these steps:

1. Create a new file for your custom agent, e.g., `custom_agent.py`:

```python
from core import DialogueAgent
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

class CustomAgent(DialogueAgent):
    def __init__(self, name: str, system_message: SystemMessage, model: ChatOpenAI) -> None:
        super().__init__(name, system_message, model)
        # Add any custom attributes here
        
    def send(self) -> str:
        # Customize the send method if needed
        return super().send()
    
    # Add any additional methods specific to your custom agent
```

2. Update the `custom_prompt.py` file to include prompts and templates for your custom scenario.

3. Modify the `main.py` file to use your custom agent and prompts:

```python
from custom_agent import CustomAgent

# Update agent creation logic
agents = []
for name, system_message in agent_system_messages.items():
    if name == "CustomAgent":
        agent = CustomAgent(
            name=name,
            system_message=SystemMessage(content=system_message),
            model=ChatOpenAI(model="gpt-4", temperature=0.2),
        )
    else:
        agent = DialogueAgent(
            name=name,
            system_message=SystemMessage(content=system_message),
            model=ChatOpenAI(model="gpt-4", temperature=0.2),
        )
    agents.append(agent)

# Update the conversation topic and other relevant parts of the script
```


4. Run your custom scenario:

```
python main.py
```

## Project Structure

- `main.py`: The main script that sets up and runs the dialogue simulation.
- `core.py`: Contains the base `DialogueAgent` and `DialogueSimulator` classes.
- `evaluator_agent.py`: Implements the `EvaluatorAgent` class with state-based behavior.
- `eval_prompt.py`: Contains prompts and templates for the evaluation scenario.
- `requirements.txt`: List of Python package dependencies.

## Contributing

Contributions to improve the project are welcome. Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Make your changes and commit (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature-branch`)
5. Create a new Pull Request