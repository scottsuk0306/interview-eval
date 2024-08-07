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
from src.temp_data import (
    MATH_GEO_HARD,MATH_GEO_LOW,MATH_GEO_MIDDLE
)

class EvaluatorAgent:
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
        self.state = "UNC"  # Initial state, [UNC, EXP,INS,ACT]
        self.prev_state = "UNC"
        self.ins_cnt = 0
    def reset(self):
        self.message_history = ["Here is the conversation so far."]

    def send(self) -> str:
        state_prompt = f"Current state: {self.state}\n"
        try:
            prompt = PromptGenerator(self.state,self.solution,self.message_history)
           # print('**prompt**\n',prompt)
        except:
            import pdb;pdb.set_trace()

        if self.state == "UNC":
            message = self.model.invoke(
                [
                    self.system_message,
                    HumanMessage(content=prompt),
                ]
            )
            new_prob = extract_json(message.content)
            
            self.solution['revised_question'] = new_prob['revised_question'] 
            self.solution['deleted_information'] = new_prob['deleted_information']
            self.transition_state("EXP")
            return EVALUATEE_STATE_EXP_PROMPT_TEMPLATE.format(initial_question = self.solution['revised_question']) 

        elif self.state == "EXP":
            message = self.model.invoke(
                [
                    self.system_message,
                    HumanMessage(content=prompt + "\n".join(self.message_history + [self.prefix])),
                ]
            )
            message = extract_json(message.content)
            if message['status'].lower() == "complete":
                self.transition_state("INS")
            return message['answer']

        elif self.state == "INS":
            message = self.model.invoke(
                [
                    self.system_message,
                    HumanMessage(content=prompt + "\n".join(self.message_history + [self.prefix])),
                ]
            )
            if self.ins_cnt == 5:
                self.transition_state("FIN")
                self.status = False
                self.ins_cnt = 0
                return "I think the question is difficult to you. Let's change the question"
            self.ins_cnt += 1
            message = extract_json(message.content)
            if message['status'].lower() == "true":
                self.status = True
                self.transition_state("FIN")
                self.ins_cnt = 0
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
#     solution = {"initial_question":'''A triangle with sides $3a-1$, $a^2 + 1$ and $a^2 + 2$ has a perimeter of 16 units. What is the number of square units in the area of the triangle?''',
#                 "answer":"12",
#                 "solution":'''"Sum $3a-1$, $a^2+1$, and $a^2+2$ to find $2a^2+3a+2=16$.  Subtract 16 from both sides and factor the left-hand side to find $(2a+7)(a-2)=0\\implies a=-7/2$ or $a=2$.  Discarding the negative solution, we substitute $a=2$ into $3a-1$, $a^2+1$, and $a^2+2$ to find that the side lengths of the triangle are 5, 5, and 6 units.  Draw a perpendicular from the 6-unit side to the opposite vertex to divide the triangle into two congruent right triangles (see figure).  The height of the triangle is $\\sqrt{5^2-3^2}=4$ units, so the area of the triangle is $\\frac{1}{2}(6)(4)=\\boxed{12\\text{ square units}}$.\n\n[asy]\nimport olympiad;\nsize(150);\ndefaultpen(linewidth(0.8)+fontsize(10));\npair A=(0,0), B=(6,0), C=(3,4);\ndraw(A--B--C--cycle);\ndraw(C--(A+B)/2,linetype(\"2 3\"));\nlabel(\"5\",(A+C)/2,unit((-4,3)));\nlabel(\"3\",B/4,S);\ndraw(\"6\",shift((0,-0.6))*(A--B),Bars(5));\ndraw(rightanglemark(A,(A+B)/2,C));[/asy]"
# '''}
    agents = []
    for name, system_message in agent_system_messages.items():
        if name == "Evaluator":
            agent = EvaluatorAgent(
                name=name,
                system_message=SystemMessage(content=system_message),
                model=ChatOpenAI(model="gpt-4", temperature=0.2)
            )
        else:
            agent = DialogueAgent(
                name=name,
                system_message=SystemMessage(content=system_message),
                model=ChatOpenAI(model="gpt-4", temperature=0.2),
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
    simulator = DalogueSimulator(agents=agents, selection_function=select_next_speaker)
    simulator.reset()
    # simulator.inject("Moderator", specified_topic)
    # print(f"(Moderator): {specified_topic}\n")
    state_all = None
    i = 1
    prob = [MATH_GEO_LOW,MATH_GEO_MIDDLE,MATH_GEO_HARD]
    while state_all != "FIN":
        simulator.agents[0].solution = prob[i]
        simulator.agents[0].state = 'UNC'
        simulator.agents[0].prev_state = "UNC"
        for _ in range(max_iters):
            name, message = simulator.step()
            print(f"({name}): {message}\n")
            if isinstance(simulator.agents[0], EvaluatorAgent):
                if simulator.agents[0].state == "FIN":
                    if i == len(prob):
                        state_all = "FIN"
                        break
                    elif i == 0 :
                        state_all = "FIN"
                        break
                    else : 
                        if  simulator.agents[0].status == True:
                            i+= 1
                            print("\n\n**New Session (Hard Problem) **\n\n")
                            break
                        else:

                            i = i-1
                            print("\n\n**New Session (Easy Problem) **\n\n")
                            break



