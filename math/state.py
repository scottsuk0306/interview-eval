from random import randint
from utils import extract_json
from src.prompt import (
    EVALUATEE_STATE_EXP_PROMPT_TEMPLATE,
    MODERATOR_STATE_INIT_UNCLARIFYING_PROMPT_TEMPLATE,
    MODERATOR_STATE_INIT_PARAPHRASING_PROMPT_TEMPLATE,
    EVALUATOR_STATE_UNC_PROMPT_TEMPLATE,

)
def state_transition(state,action):
    if state == INIT:
        if action in ["paraphrasing", None]:
            state == EXP
        elif action in ["unclarifying"]:
            state == UNC
    elif state == EXP:
        if action.lower() == "complete":
            state = ACT
    return state

class INIT: #initial
    def action():
        action_set = ['paraphrasing','unclarifying',None]
        action = action[randint(0,3)]
        return action
    def prompt(solution,action):
        if action == 'paraphrasing':
            prompt = MODERATOR_STATE_INIT_PARAPHRASING_PROMPT_TEMPLATE.format( question=solution['initial_question'].replace('{','').replace('}','').replace('"',"'"))
                        
        elif action == 'unclarifying':
            prompt = MODERATOR_STATE_INIT_UNCLARIFYING_PROMPT_TEMPLATE.format( question=solution['initial_question'].replace('{','').replace('}','').replace('"',"'"))
        return prompt

class UNC: #unclarify
    def prompt(solution,session_history, action = None):
        prompt = EVALUATOR_STATE_UNC_PROMPT_TEMPLATE.format(initial_question=solution['initial_question'],
                revised_question=solution['revised_question'],
                deleted_information=solution['deleted_information'],
                Dialogue_History=session_history)
        return prompt
    def extract_message(message):
        message_json = extract_json(message)

        return message_json['answer'], message_json['status']

class EXP: #explore
    def prompt():
        prompt = EVALUATOR_STATE_ACTION_PROMPT_TEMPLATE_STEM_LONG.format(
                    output_example = output_examples, 
                    question=solution['initial_question'],
                    answer = solution['answer'],
                    solution=solution['solution'],
                    model_output=message_history,
                )  
        return str
    def extract_message(message):
        message_json = extract_json(message)
  
        return message_json['feedback'], message_json['status']

class INS : #insight
    def prompt():
        return str
    def extract_message():
        return str
class ACT : #action
    def prompt():
        return str
    def extract_message():
        return str

class FIN : #fin
    def prompt():
        return str
    def extract_message():
        return str

