from typing import List

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
        message = message.content
        self.receive(self.name,message)
        return message

    def receive(self, name: str, message: str) -> None:
        self.last_message = message
        self.message_history.append(f"{name}: {message}")

class EvaluateAgent:
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

    def send(self) -> str:
        message = self.model.invoke(
            [
                self.system_message,
                HumanMessage(content="\n".join(self.last_message)),
            ]
        )
        return message.content

    def receive(self, message: str) -> None:
        self.last_message = message

class Moderator:
    def __init__(
        self,
        system_message: SystemMessage,
        model: ChatOpenAI,
        agents_name : list,
        queries : dict,
        references : dict,
        store_session : bool
    ) -> None:

        self.system_message = system_message

        self.model = model
        self.agents_name = agents_name

        self.queries = queries
        self.reference = references

        self.global_state_flow = {}
        self.session_state_flow = []

        self.global_message_history = {}
        self.session_history = []
        self.query_flow = {}

        self.session_num = 0
        self.store_session = True if store_session != None else store_session

    def reset(self) -> None:
        if not self.session_num == 0:
            self.global_state_flow[self.session_num] = self.session_state_flow
            self.global_message_history[self.session_num] = self.session_history
            if self.store_session:
                self.summarize_session()      
        self.state = INIT
        self.session_state_flow = []
        self.session_history = []
        self.session_num += 1
    def send_query(self):
        current_query = self._select_queries()

        action = self.state.action()
        current_query = self._gen_queries(current_query,action)
        self.declare_state(self.state,action) #INIT -> UNC/EXP
        return self.speaker, self.state.prompt(current_query)
    
    def _select_queries(self) -> dict: #select_query_function: need to define
        current_query = self.select_query_function(query = self.current_query, state = self.state )
        return current_query

    def _gen_queries(self,current_query,action) -> dict: #select_query_function: need to define
        if action != None:
            query_generatin_prompt = self.state.prompt(action)
            new_prob = self.model.invoke(
                    [
                        self.system_message,
                        HumanMessage(content=query_generatin_prompt),
                    ]
                )        
            new_prob= extract_json(new_prob)
            current_query['revised_question'] = new_prob['revised_question'] 
            current_query['deleted_information'] = new_prob['deleted_information']
        return current_query

    def receive_and_send(self, message: str) -> tuple[str,str]:
        self.message_history.append(f"{self.speaker}: {message}")
        if self.speaker == self.agents_name[0]: #evaluatee
            message = self.state.prompt(self.solution,self.session_history)
            self.speaker = self.agents_name[1]
        elif self.speaker == self.agents_name[1]: #evaluator
            message, action =  self.state.extract_message(message)
            self.declare_state(self.state,action) 
            self.speaker = self.agents_name[0]

        return self.speaker, message
    def declare_state(self,state,action):
        self.prev_state = self.state
        self.state = state_transition(state,action)
        self.session_state_flow.append(state)
        
        print(f"**STATE TRANSITION**\nSTATE {self.prev_state}--> STATE {self.state}\n")
        


    def summarize_session(self) -> None:
        summary = self._summarize(self.session_history)
        self.global_message_history[self.session_num] = summary

    def _summarize(self,session_history):
        message = self.model.invoke(
                [
                    self.system_message,
                    HumanMessage(content=SESSION_SUMMARIZE_PROMPT + "\n".join(session_history)),
                ]
            )
        return message
        
class DialogueSimulator:
    def __init__(self, agents: List[DialogueAgent], moderator,selection_function) -> None:
        self.agents = agents
        self.moderator = moderator
        self._step = 0
        self.message_history = []
        self.session_history = []
        self.select_next_speaker = selection_function

    def reset(self):
        for agent in self.agents:
            agent.reset()
        #send initial queries
        self.next_speaker, message = self.moderator.send_query()
        for receiver in self.agents:
            receiver.receive('', message)     

    def history_reset(self):
        self.message_history = ["Here is the conversation so far."]

    def inject(self, name: str, message: str):
        for agent in self.agents:
            agent.receive(name, message)
        self._step += 1

    def step(self) -> tuple[str, str]:
        speaker_idx = self.next_speaker       
        speaker = self.agents[speaker_idx]
        
        agent_message = speaker.send()
        self.next_speaker, message = self.moderator.receive_and_send(agent_message)

        self.agents[self.next_speaker].receive(message)
        self._step += 1
        return speaker_idx, agent_message

def select_next_speaker(step: int, agents: List[DialogueAgent]) -> int:
    return step % len(agents)
