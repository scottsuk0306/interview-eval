from datasets import load_dataset
import pandas as pd
from langchain_community.document_loaders import DataFrameLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain.globals import set_debug

set_debug(True)

EXAMPLE_QUERY = '''
Given the question below, please come up with 10 in-depth questions that can be used to test the model. The difficulty level should be similar to the original question.

### Question
If Jim has 3 hats, 5 shirts, and 4 pairs of pants, and he wears a shirt with a pair of pants to school, how many different outfits can he put together?
'''.strip()


def retrieve_test():
    load_dotenv()
    # Load the dataset
    ds = load_dataset("openai/gsm8k", "main")

    # Step 1: Change ds into dataframe
    df = pd.DataFrame(ds['train'])

    # Step 2: Create 'text' column by concatenating 'question' and 'answer'
    df['text'] = df['question'] + '\n---\n' + df['answer']

    # Step 3: Use LangChain to make a VectorStoreIndex and ask a query on it
    loader = DataFrameLoader(df, page_content_column="text")
    index = VectorstoreIndexCreator(embedding=HuggingFaceEmbeddings()).from_loaders([loader])

    # Example query
    query = EXAMPLE_QUERY
    result = index.query(query, llm=ChatOpenAI(temperature=0))

    print("Retriever Test: ", result)


def test():
    query = EXAMPLE_QUERY
    llm = ChatOpenAI(temperature=0)
    
    messages = [
        ("human", EXAMPLE_QUERY),
    ]
    
    result = llm.invoke(messages)
    print("Test: ", result)


if __name__ == "__main__":
    retrieve_test()
    test()