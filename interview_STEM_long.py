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
    EVALUATOR_STATE_EXP_PROMPT_TEMPLATE,
    EVALUATEE_STATE_EXP_PROMPT_TEMPLATE_STEM_LONG,
    EVALUATOR_STATE_ACTION_PROMPT_TEMPLATE_STEM_LONG
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
            # new_prob = extract_json(message.content)
            
            self.solution['revised_question'] = "I need help understanding a biological concept."
            self.solution['deleted_information'] = "symbiosis"
            self.transition_state("EXP")
            return EVALUATEE_STATE_EXP_PROMPT_TEMPLATE_STEM_LONG.format(initial_question = self.solution['revised_question']) 

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
    topic = "STEM explanation"
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
    solution = {"initial_question":"I need help understanding a biological concept-symbiosis.",
                "answer":"",
                "solution":'''Symbiosis is a close and long-term biological interaction between two different biological organisms, often of different species, called symbionts. This relationship can take several forms:

Mutualism: Both organisms benefit from the relationship. For example, clownfish live among the stinging tentacles of sea anemones. The clownfish gains protection from predators, while the anemone benefits from the nutrients in the clownfish's waste? (Wikipedia)?.

Commensalism: One organism benefits while the other is neither helped nor harmed. An example of this is barnacles attaching to whales. The barnacles get a place to live and access to nutrient-rich waters, while the whale is largely unaffected? (Wikipedia)?.

Parasitism: One organism benefits at the expense of the other. A common example is fleas or ticks that feed on the blood of mammals, harming the host while gaining sustenance for themselves? (Wikipedia)?? (Wikipedia)?.

Symbiotic relationships can also be classified based on the dependency and physical attachment of the organisms involved:

Obligate vs. Facultative: In obligate symbiosis, one or both organisms cannot survive without the other, such as the relationship between certain fungi and algae in lichens. In facultative symbiosis, the organisms can live independently, but benefit from the relationship when it occurs? (Wikipedia)?.

Ectosymbiosis vs. Endosymbiosis: Ectosymbiosis occurs when one organism lives on the surface of another, like lice on humans. Endosymbiosis involves one organism living inside the tissues of another, such as nitrogen-fixing bacteria within the root nodules of legumes? (Wikipedia)?.'''}
    agents = []
    for name, system_message in agent_system_messages.items():
        if name == "Evaluator":
            agent = EvaluatorAgent(
                name=name,
                system_message=SystemMessage(content=system_message),
                model=ChatOpenAI(model="gpt-4o", temperature=0.2),solution = solution
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
