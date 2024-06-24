from typing import List

from dotenv import load_dotenv
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI


class DialogueAgent:
    def __init__(
        self,
        name: str,
        system_message: SystemMessage,
        model: ChatOpenAI,
    ) -> None:
        self.name = name
        self.system_message = system_message
        self.model = model
        self.prefix = f"{self.name}: "
        self.reset()

    def reset(self):
        self.message_history = ["Here is the conversation so far."]

    def send(self) -> str:
        message = self.model.invoke(
            [
                self.system_message,
                HumanMessage(content="\n".join(self.message_history + [self.prefix])),
            ]
        )
        return message.content

    def receive(self, name: str, message: str) -> None:
        self.message_history.append(f"{name}: {message}")


class DialogueSimulator:
    def __init__(self, agents: List[DialogueAgent], selection_function) -> None:
        self.agents = agents
        self._step = 0
        self.select_next_speaker = selection_function

    def reset(self):
        for agent in self.agents:
            agent.reset()

    def inject(self, name: str, message: str):
        for agent in self.agents:
            agent.receive(name, message)
        self._step += 1

    def step(self) -> tuple[str, str]:
        speaker_idx = self.select_next_speaker(self._step, self.agents)
        speaker = self.agents[speaker_idx]
        message = speaker.send()

        for receiver in self.agents:
            receiver.receive(speaker.name, message)

        self._step += 1
        return speaker.name, message


def select_next_speaker(step: int, agents: List[DialogueAgent]) -> int:
    return step % len(agents)


def generate_agent_description(name):
    agent_descriptor_system_message = SystemMessage(
        content="You can add detail to the description of the conversation participant."
    )
    agent_specifier_prompt = [
        agent_descriptor_system_message,
        HumanMessage(
            content=f"""{conversation_description}
            Please reply with a creative description of {name}, in {word_limit} words or less. 
            Speak directly to {name}.
            Give them a point of view.
            Do not add anything else."""
        ),
    ]
    agent_description = ChatOpenAI(temperature=1.0)(agent_specifier_prompt).content
    return agent_description


def generate_system_message(name, description):
    return f"""{conversation_description}
    
Your name is {name}.

Your description is as follows: {description}

Your goal is to persuade your conversation partner of your point of view.

Do not add anything else.

Stop speaking the moment you finish speaking from your perspective.
"""


if __name__ == "__main__":
    load_dotenv()

    names = ["AI accelerationist", "AI alarmist"]
    topic = "The current impact of automation and artificial intelligence on employment"
    word_limit = 50

    conversation_description = f"""Here is the topic of conversation: {topic}
The participants are: {', '.join(names)}"""

    agent_descriptions = {name: generate_agent_description(name) for name in names}

    agent_system_messages = {
        name: generate_system_message(name, description)
        for name, description in agent_descriptions.items()
    }

    agents = [
        DialogueAgent(
            name=name,
            system_message=SystemMessage(content=system_message),
            model=ChatOpenAI(model="gpt-4", temperature=0.2),
        )
        for name, system_message in agent_system_messages.items()
    ]

    topic_specifier_prompt = [
        SystemMessage(content="You can make a topic more specific."),
        HumanMessage(
            content=f"""{topic}
            
            You are the moderator.
            Please make the topic more specific.
            Please reply with the specified quest in {word_limit} words or less. 
            Speak directly to the participants: {*names,}.
            Do not add anything else."""
        ),
    ]
    specified_topic = ChatOpenAI(temperature=1.0)(topic_specifier_prompt).content

    max_iters = 6
    simulator = DialogueSimulator(agents=agents, selection_function=select_next_speaker)
    simulator.reset()
    simulator.inject("Moderator", specified_topic)
    print(f"(Moderator): {specified_topic}\n")

    for _ in range(max_iters):
        name, message = simulator.step()
        print(f"({name}): {message}\n")
