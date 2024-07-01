from typing import List

from dotenv import load_dotenv
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.prompt import (
    AGENT_DESCRIPTOR_SYSTEM_MESSAGE,
    AGENT_SPECIFIER_PROMPT_TEMPLATE,
    SYSTEM_MESSAGE_TEMPLATE,
    TOPIC_SPECIFIER_PROMPT_TEMPLATE,
    TOPIC_SPECIFIER_SYSTEM_MESSAGE,
)
from src.dialogue import DialogueAgent, DialogueSimulator, select_next_speaker


class EvaluatorAgent(DialogueAgent):
    def __init__(self, name: str, system_message: SystemMessage, model: ChatOpenAI) -> None:
        super().__init__(name, system_message, model)
        self.state = "Exploration"  # Initial state

    def send(self) -> str:
        state_prompt = f"Current state: {self.state}\n"
        message = self.model.invoke(
            [
                self.system_message,
                HumanMessage(content=state_prompt + "\n".join(self.message_history + [self.prefix])),
            ]
        )
        return message.content

    def transition_state(self):
        if self.state == "Exploration":
            self.state = "Comforting"
        elif self.state == "Comforting":
            self.state = "Action"
        else:
            self.state = "Exploration"


def generate_agent_description(name, conversation_description, word_limit):
    if name == "Evaluator":
        role_description = "a user seeking travel planning assistance"
    else:
        role_description = "an AI assistant helping with travel planning"

    agent_specifier_prompt = [
        SystemMessage(content=AGENT_DESCRIPTOR_SYSTEM_MESSAGE),
        HumanMessage(
            content=AGENT_SPECIFIER_PROMPT_TEMPLATE.format(
                conversation_description=conversation_description,
                name=name,
                role_description=role_description,
                word_limit=word_limit,
            )
        ),
    ]
    agent_description = ChatOpenAI(temperature=1.0).invoke(agent_specifier_prompt).content
    return agent_description


def generate_system_message(name, description, conversation_description):
    return SYSTEM_MESSAGE_TEMPLATE.format(
        conversation_description=conversation_description,
        name=name,
        description=description,
    )


if __name__ == "__main__":
    load_dotenv()

    names = ["Evaluator", "Evaluatee"]
    topic = "Travel planning assistance"
    word_limit = 50

    conversation_description = f"""Here is the scenario: {topic}
The participants are: {', '.join(names)}"""

    agent_descriptions = {
        name: generate_agent_description(name, conversation_description, word_limit) for name in names
    }

    agent_system_messages = {
        name: generate_system_message(name, description, conversation_description)
        for name, description in agent_descriptions.items()
    }

    agents = []
    for name, system_message in agent_system_messages.items():
        if name == "Evaluator":
            agent = EvaluatorAgent(
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

    topic_specifier_prompt = [
        SystemMessage(content=TOPIC_SPECIFIER_SYSTEM_MESSAGE),
        HumanMessage(
            content=TOPIC_SPECIFIER_PROMPT_TEMPLATE.format(topic=topic, word_limit=word_limit, names=", ".join(names))
        ),
    ]
    specified_topic = ChatOpenAI(temperature=1.0).invoke(topic_specifier_prompt).content

    max_iters = 10
    simulator = DialogueSimulator(agents=agents, selection_function=select_next_speaker)
    simulator.reset()
    simulator.inject("Moderator", specified_topic)
    print(f"(Moderator): {specified_topic}\n")

    for _ in range(max_iters):
        name, message = simulator.step()
        print(f"({name}): {message}\n")
        if isinstance(simulator.agents[0], EvaluatorAgent):
            print(f"Evaluator state: {simulator.agents[0].state}\n")
