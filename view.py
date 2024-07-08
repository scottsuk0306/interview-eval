import os
import random
from src.data_loader import MTBench101DataLoader

def display_formatted_conversation(index):
    loader = MTBench101DataLoader()

    # Load the data
    loader.load_data()

    # Check if the index is valid
    if index < 0 or index >= len(loader):
        print(f"Error: Invalid index. Please choose an index between 0 and {len(loader) - 1}")
        return

    # Get the conversation data
    entry = loader[index]

    # Format and print the conversation
    print(f"Task: {entry['task']}")
    print(f"ID: {entry['id']}")
    print()

    for turn in entry['history']:
        print(f"User: {turn['user']}")
        print(f"Bot: {turn['bot']}")
        print()

if __name__ == "__main__":
    # You can change this index to display different conversations
    conversation_index = random.randint(0, 100)
    display_formatted_conversation(conversation_index)