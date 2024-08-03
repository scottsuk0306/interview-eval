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
    EVALUATEE_STATE_EXP_PROMPT_TEMPLATE
)
from src.dialogue import DialogueAgent, DialogueSimulator, select_next_speaker
from utils import extract_json
from src.prompt import PromptGenerator

class EvaluatorAgent:
    def __init__(
        self,
        name: str,
        system_message: SystemMessage,
        model: ChatOpenAI,
        solution : dict
    ) -> None:
        self.name = name
        self.system_message = system_message
        self.model = model
        self.prefix = f"{self.name}: "
        self.reset()
        self.state = "UNC"  # Initial state, [UNC, EXP,INS,ACT]
        self.prev_state = "UNC"
        self.solution = solution
    def reset(self):
        self.message_history = ["Here is the conversation so far."]

    def send(self) -> str:
        state_prompt = f"Current state: {self.state}\n"
        prompt = PromptGenerator(self.state,self.solution,self.message_history)
        message = self.model.invoke(
            [
                self.system_message,
                HumanMessage(content=prompt + "\n".join(self.message_history + [self.prefix])),
            ]
        )
        if self.state == "UNC":
            new_prob = extract_json(message.content)
            
            self.solution['revised_question'] = new_prob['revised_question'] 
            self.solution['deleted_information'] = new_prob['deleted_information']
            self.transition_state("EXP")
            return EVALUATEE_STATE_EXP_PROMPT_TEMPLATE.format(initial_question = self.solution['revised_question']) 

        elif self.state == "EXP":
            message = extract_json(message.content)
            if message['status'].lower() == "complete":
                self.transition_state("INS")
            return message['answer']

        elif self.state == "INS":
            message = extract_json(message.content)
            if message['status'].lower() == "true":
                self.transition_state("FIN")
            return message['feedback']

    def receive(self, name: str, message: str) -> None:
        self.message_history.append(f"{name}: {message}")


    def transition_state(self,next_state):
        self.prev_state = self.state
        self.state = next_state
        print(f"**STATE TRANSITION**\nSTATE {self.prev_state}--> STATE {self.state}\n")
        


def generate_agent_description(name, conversation_description, word_limit):
    if name == "Evaluator":
        # role_description = "a user seeking travel planning assistance"
        role_description = ""
    else:
        # role_description = "an AI assistant helping with travel planning"
        role_description = ""
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
    topic = "Math problem solving"
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
    solution = {"initial_question":'''cell-phone recharges at the rate of 1 percentage-point of charge per 3 minutes. Now, the phone is at 60% charged. How long will it take to fully charge, in hours? Solution output format: an integer.''',
                "answer":"2",
                "solution":'''To determine how long it will take for the cell phone to fully charge, we start by noting the given conditions: The phone recharges at a rate of 1 percentage point every 3 minutes. The current charge level is 60%. First, we calculate the remaining charge needed to reach 100%: 100 % − 60 % = 40 % 100%−60%=40% Next, we determine the time required to recharge this 40% at the given rate of 1% per 3 minutes: Time required = 40 × 3 minutes Time required=40×3 minutes Time required = 120 minutes Time required=120 minutes Now, we convert this time from minutes to hours. Since there are 60 minutes in an hour, we perform the conversion: Time in hours = 120 minutes 60 minutes per hour = 2 hours Time in hours= 60 minutes per hour 120 minutes ​ =2 hours Thus, the time required to fully charge the phone is: 2 hours'''}
    agents = []
    for name, system_message in agent_system_messages.items():
        if name == "Evaluator":
            agent = EvaluatorAgent(
                name=name,
                system_message=SystemMessage(content=system_message),
                model=ChatOpenAI(model="gpt-4", temperature=0.2),solution = solution
            )
        else:
            agent = DialogueAgent(
                name=name,
                system_message=SystemMessage(content=system_message),
                model=ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2),
            )
        agents.append(agent)

    # topic_specifier_prompt = [
    #     SystemMessage(content=TOPIC_SPECIFIER_SYSTEM_MESSAGE),
    #     HumanMessage(
    #         content=TOPIC_SPECIFIER_PROMPT_TEMPLATE.format(topic=topic, word_limit=word_limit, names=", ".join(names))
    #     ),
    # ]
    # specified_topic = ChatOpenAI(temperature=1.0).invoke(topic_specifier_prompt).content

    max_iters = 20
    simulator = DialogueSimulator(agents=agents, selection_function=select_next_speaker)
    simulator.reset()
    # simulator.inject("Moderator", specified_topic)
    # print(f"(Moderator): {specified_topic}\n")
    for _ in range(max_iters):
        name, message = simulator.step()
        print(f"({name}): {message}\n")
        if isinstance(simulator.agents[0], EvaluatorAgent):
           if simulator.agents[0].state == "FIN":
                break
