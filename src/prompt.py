# prompt.py
from utils import extract_json
AGENT_DESCRIPTOR_SYSTEM_MESSAGE = "You can add detail to the description of the conversation participant."

AGENT_SPECIFIER_PROMPT_TEMPLATE = """{conversation_description}
Please reply with a creative description of {name}, in {word_limit} words or less. 
Speak directly to {name}.
Give them a point of view.
Do not add anything else."""

SYSTEM_MESSAGE_TEMPLATE = """{conversation_description}

Your name is {name}.

Your description is as follows: {description}

Your goal is to persuade your conversation partner of your point of view.

Do not add anything else.

Stop speaking the moment you finish speaking from your perspective.
"""

TOPIC_SPECIFIER_SYSTEM_MESSAGE = "You can make a topic more specific."

TOPIC_SPECIFIER_PROMPT_TEMPLATE = """{topic}

You are the moderator.
Please make the topic more specific.
Please reply with the specified quest in {word_limit} words or less. 
Speak directly to the participants: {names}.
Do not add anything else."""

EVALUATOR_STATE_ACTION_PROMPT_TEMPLATE = """You are an expert tasked with evaluating and providing feedback on an assistant's performance.
--- 
Your response should contain the correctness as "status", whether it is correct or wrong with [True/False] and the feedback.  Rather than giving away the solution, details about the answer, or telling which step is incorrect, Encourage them to solve once more. When you give the feedback, refer the solution. The models' output must be same with the answer. 
---
Here are examples. Please follow the format as the following expert acts.
{output_example}
---
Now provide your feedback.
Question : 
{question}
Answer : 
{answer}
Correct solution (please DO NOT disclose the correct solution to the assistant):
{solution}
Model output : 
{model_output}
Expert feedback:"""

EVALUATOR_STATE_UNCLARIFYING_PROMPT_TEMPLATE ='''Delete some important information from the following question, so that the agent should seek for the additional information
---
Here are examples. Please follow the format as the following expert acts. Your output must be a json format.
initial question : cell-phone recharges at the rate of 1 percentage-point of charge per 3 minutes. Now, the phone is at 60% charged. How long will it take to fully charge, in hours? Solution output format: an integer.
output : {output_example}
---
initial question : {question}
output : '''
EVALUATOR_STATE_EXP_PROMPT_TEMPLATE ='''There's initial question and revised question. Some of information from initial question are deleted to revised question. For the given intial question, revised question and deleted information, You are an Evalautor that answer the evaluatee's questions. The evaluatee's role is to find deleted information. If the evaluatee asks for information that corresponds to the deleted information, provide that information. If the evaluatee asks for information not included in the deleted information, respond that this information is not needed. If the evaluatee tries to solve the problem without asking anything, inform them that the information is needed. If the evaluatee has asked for and found all the information in the deleted information, respond the "Status" with  "complete.". Else, respond the "Status" with "incomplete".
---
Here are examples. Please follow the format as the following expert acts. Your output must be a json format.
{output_example}
---
initial_question : {initial_question}
revised_question : {revised_question}
deleted_information : {deleted_information}
Dialogue_History : {Dialogue_History}
Evalautor : '''
EVALUATOR_STATE_INDEPTH_QUESTION_PROMPT_TEMPLATE ='''There's initial question and revised question. Some of information from initial question are deleted to revised question. For the given intial question, revised question and deleted information, You are an Evalautor that answer the evaluatee's questions. The evaluatee's role is to find deleted information. If the evaluatee asks for information that corresponds to the deleted information, provide that information. If the evaluatee asks for information not included in the deleted information, respond that this information is not needed. If the evaluatee tries to solve the problem without asking anything, inform them that the information is needed. If the evaluatee has asked for and found all the information in the deleted information, respond the "Status" with  "complete.". Else, respond the "Status" with "incomplete".
---
Here are examples. Please follow the format as the following expert acts. Your output must be a json format.
{output_example}
---
Reference Material : {initial_question}
Dialogue_History : {Dialogue_History}
Evalautor : '''

EVALUATOR_STATE_ACTION_PROMPT_TEMPLATE_STEM_LONG = """You are an expert tasked with evaluating and providing feedback on an assistant's performance.
--- 
current status is "False".
Your response should contain feedback if there's something wrong with the given reference solution. Rather than giving away the solution, tell which step is incorrect and encourage them to solve it once more. If there are missing facts compared with the reference solution, ask in-depth questions about the facts that are in the solution. If you ask for all of the missing facts and give all of the feedback, return the status as "True." 
Be sure to include only one piece of feedback at a time. If the evaluatee does not answer your question directly, rephrase your question to be more specific and guide them towards providing a direct response.
---
Output Format
{{"feedback":, "status":}}
---
Now provide your feedback.
Question : 
{question}
Reference Answer (please DO NOT disclose the correct solution to the assistant):
{solution}
Model output : 
{model_output}
Evaluator : 
"""

EVALUATOR_STATE_UNCLARIFYING_PROMPT_STEM_LONG ='''Delete some important information from the following question, so that the agent should seek for the additional information
---
Here are examples. Please follow the format as the following expert acts. Your output must be a json format.
initial question : cell-phone recharges at the rate of 1 percentage-point of charge per 3 minutes. Now, the phone is at 60% charged. How long will it take to fully charge, in hours? Solution output format: an integer.
output : {output_example}
---
initial question : {question}
output : '''
EVALUATOR_STATE_EXP_PROMPT_TEMPLATE_STEM_LONG ='''There's initial question and revised question. Some of information from initial question are deleted to revised question. For the given intial question, revised question and deleted information, You are an Evalautor that answer the evaluatee's questions. The evaluatee's role is to find deleted information. If the evaluatee asks for information that corresponds to the deleted information, provide that information. If the evaluatee asks for information not included in the deleted information, respond that this information is not needed. If the evaluatee tries to solve the problem without asking anything, inform them that the information is needed. If the evaluatee has asked for and found all the information in the deleted information, respond the "Status" with  "complete.". Else, respond the "Status" with "incomplete".
---
Here are examples. Please follow the format as the following expert acts. Your output must be a json format.
{output_example}
---
initial_question : {initial_question}
revised_question : {revised_question}
deleted_information : {deleted_information}
Dialogue_History : {Dialogue_History}
Evalautor : '''


EVALUATEE_STATE_EXP_PROMPT_TEMPLATE = '''You are a helpful assistant assigned with the task of problem-solving.  To achieve this, you can proactively ask user to give additional information. At each turn, you should first provide your step-by-step thinking for solving the task. Your thought process should be enclosed using \"<thought>\" tag, for example: <thought> I need to print \"Hello World!\" </thought>.You have chances to interact with the environment or propose a solution. You can only propose a solution 1 times.

Question: {initial_question}''' 

EVALUATEE_STATE_EXP_PROMPT_TEMPLATE_STEM_LONG = '''You are a helpful assistant assigned with the task of problem-solving. Answer to the Question.
Question: {initial_question}''' 

def PromptGenerator(state,solution,message_history):
    if state == 'UNC':
        output_examples = '''{"revised_question" : "The cell-phone recharges at a certain rate. Now, the phone is at 60% charged. How long will it take to fully charge, in hours? Solution output format: an integer.","deleted_information" : "cell-phone recharges at the rate of 1 percentage-point of charge per 3 minutes."}'''
        prompt = EVALUATOR_STATE_UNCLARIFYING_PROMPT_TEMPLATE.format( output_example = output_examples, question=solution['initial_question'])
             
    elif state == 'EXP':
        output_examples = '''initial_question : cell-phone recharges at the rate of 1 percentage-point of charge per 3 minutes. Now, the phone is at 60% charged. How long will it take to fully charge, in hours? Solution output format: an integer.
revised_question : The cell-phone recharges at a certain rate. Now, the phone is at 60% charged. How long will it take to fully charge, in hours? Solution output format: an integer.,
deleted_information : ["cell-phone recharges at the rate of 1 percentage-point of charge per 3 minutes."]
Dialogue_History : ["Evalautee : What is cell-phone recharging rate ?"]
Evalautor : {"answer" : "The recharging rate is 1 percentage-point of charge per 3 minutes",
"status" : "Complete"}'''
        prompt =     EVALUATOR_STATE_EXP_PROMPT_TEMPLATE.format(  output_example = output_examples, initial_question=solution['initial_question'],
            revised_question=solution['revised_question'],
            deleted_information=solution['deleted_information'],
            Dialogue_History=message_history)
    elif state == "INS":
        output_examples = '''{"status" : "True",
"feedback" : "This is GOOD. You have got the solution!"}
{"status" : "False",
"feedback" : "Your answer is incorrect. Think step by step and retry"}
{"status" : "False",
"feedback" : "Your approach is good, but you should get the final number as a output."}'''
        prompt =     EVALUATOR_STATE_ACTION_PROMPT_TEMPLATE_STEM_LONG.format(
            output_example = output_examples, 
            question=solution['initial_question'],
            answer = solution['answer'],
            solution=solution['solution'],
            model_output=message_history,
        )    
    elif state == "ACT":
        output_examples = '''Expert feedback: {"status" : True,
"feedback" : This is GOOD. You have got the solution!}
{"status" : False,
"feedback" : Your answer is incorrect. Think step by step and retry}'''
        prompt =     EVALUATOR_STATE_ACTION_PROMPT_TEMPLATE_STEM_LONG.format(
            output_example = output_examples, 
            question=solution['initial_question'],
            solution=solution['solution'],
            model_output=message_history,
        )
    return prompt
