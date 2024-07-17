from datasets import load_dataset
import pandas as pd

if __name__ == "__main__":
    dataset = load_dataset("osunlp/TravelPlanner", "test")
    
    df = pd.DataFrame(dataset['test'])
    
    queries = df['query'].tolist()
    
    for query in queries[:100]:
        print(query) 