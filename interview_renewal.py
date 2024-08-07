from typing import List
from random import randint
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
from src.state import (INIT,UNC,INS,ACT,FIN, state_transition)
from src.dialogue import DialogueAgent,EvaluateAgent,Moderator,DialogueSimulator, select_next_speaker
from utils import extract_json
from src.prompt import PromptGenerator
from src.temp_data import (
    MATH_GEO_HARD,MATH_GEO_LOW,MATH_GEO_MIDDLE
)


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
    #Interview Settings
    topic = "Math problem solving"
    Seed_Questions = [MATH_GEO_LOW,MATH_GEO_MIDDLE,MATH_GEO_HARD]
    #Seed_Questions = load_seed_questions(args.input_path)
    word_limit = 50
    names = ["Evaluatee","Evaluator"] # reveal evaluatee that it is getting evaluated? or names = ["System","User"] 
    conversation_description = f"""Here is the scenario: {topic}
The participants are: {', '.join(names)}"""

    #Moderator Setting
    moderator = Moderator()
    #Agents Setting
    agent_descriptions = {
        name: generate_agent_description(name, conversation_description, word_limit) for name in names
    }

    agent_system_messages = {
        name: generate_system_message(name, description, conversation_description)
        for name, description in agent_descriptions.items()
    }
    agents = {}
    agents_model = {'evaluator':'gpt-4', 'evaluatee':'gpt-3.5-turbo'}
    # agents_model = {'evaluator':args.evaluator_model, 'evaluatee':args.evaluatee_model}
    for name, system_message in agent_system_messages.items():
        agent = DialogueAgent(
            name=name,
            system_message=SystemMessage(content=system_message),
            model=ChatOpenAI(model=agents_model[name], temperature=0.2),
        )
        #agents.append(agent)
        agents[name] = agent

    # topic_specifier_prompt = [
    #     SystemMessage(content=TOPIC_SPECIFIER_SYSTEM_MESSAGE),
    #     HumanMessage(
    #         content=TOPIC_SPECIFIER_PROMPT_TEMPLATE.format(topic=topic, word_limit=word_limit, names=", ".join(names))
    #     ),
    # ]
    # specified_topic = ChatOpenAI(temperature=1.0).invoke(topic_specifier_prompt).content

    max_iters = 20
    simulator = DialogueSimulator(agents=agents, moderator = moderator,selection_function=select_next_speaker)

    simulator.reset()
    # simulator.inject("Moderator", specified_topic)
    # print(f"(Moderator): {specified_topic}\n")
    state_all = None
    i = 1
    
    while state_all != "FIN":
        simulator.agents[0].solution = prob[i]
        simulator.agents[0].state = 'UNC'
        simulator.agents[0].prev_state = "UNC"
        for _ in range(max_iters):
            name, message = simulator.step()
            print(f"({name}): {message}\n")
            

