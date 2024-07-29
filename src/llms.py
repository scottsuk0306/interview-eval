# Support different llms including ChatOpenAI

from langchain_community.llms import VLLM


def vllm_example():
    # local VLLM
    # ref: https://python.langchain.com/v0.1/docs/integrations/llms/vllm/
    llm = VLLM(
        model="mosaicml/mpt-7b",
        trust_remote_code=True,  # mandatory for hf models
        max_new_tokens=128,
        top_k=10,
        top_p=0.95,
        temperature=0.8,
    )

    print(llm.invoke("What is the capital of France ?"))


def vllm_serve_example():
    # VLLM served with OpenAI
    # ref: https://python.langchain.com/v0.1/docs/integrations/chat/vllm/
    pass


def litellm_example():
    # other proprietary llms
    # ref: https://python.langchain.com/v0.1/docs/integrations/chat/litellm_router/
    pass
