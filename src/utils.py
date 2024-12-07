import random
import unicodedata
from config import SCENARIOS

def clean_text(text):
    """Clean unicode characters from text"""
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = unicodedata.normalize('NFKD', text)
    return ''.join(char for char in text if ord(char) < 128)

def get_word_count(text):
    """Count words in text"""
    return len(text.split())

def select_scenario_user_choice():
    """Allow user to select from predefined scenarios"""
    print("\nAvailable Scenarios:")
    for i, scenario in enumerate(SCENARIOS, 1):
        print(f"{i}. {scenario['setting']}")
        print(f"   Description: {scenario['description']}\n")
    
    while True:
        try:
            choice = int(input("Select a scenario (1-5): "))
            if 1 <= choice <= len(SCENARIOS):
                return SCENARIOS[choice - 1]
            print(f"Please enter a number between 1 and {len(SCENARIOS)}")
        except ValueError:
            print("Please enter a valid number")

def select_scenario_random():
    """Randomly select a scenario"""
    scenario = random.choice(SCENARIOS)
    print(f"\nRandomly selected scenario: {scenario['setting']}")
    print(f"Description: {scenario['description']}")
    return scenario

async def generate_dynamic_scenario(client, story_assistant):
    """Generate a new AI-created scenario"""
    print("\nGenerating new AI scenario...")
    prompt = """Generate a unique 'polar opposites' scenario for a story. 
    The scenario should combine two completely contrasting elements, cultures, or concepts.
    Return the response in the following format:
    Setting: [Brief title]
    Description: [One sentence explanation]"""
    
    thread = client.beta.threads.create()
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt
    )
    
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=story_assistant.id
    )
    
    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        if run_status.status == 'completed':
            break
        await asyncio.sleep(2)
    
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    response = messages.data[0].content[0].text.value
    
    lines = response.split('\n')
    setting = lines[0].replace('Setting:', '').strip()
    description = lines[1].replace('Description:', '').strip()
    
    return {"setting": setting, "description": description}

def select_scenario_with_menu(story_assistant):
    """Main scenario selection menu"""
    print("\n🌟 How would you like to select your scenario? 🌟")
    print("1. 📜 Choose from predefined scenarios")
    print("2. 🎲 Random selection")
    print("3. 🤖 Generate a brand new AI scenario")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (1-3): "))
            if choice == 1:
                return select_scenario_user_choice()
            elif choice == 2:
                return select_scenario_random()
            elif choice == 3:
                return asyncio.run(generate_dynamic_scenario(story_assistant))
            else:
                print("Please enter a number between 1 and 3")
        except ValueError:
            print("Please enter a valid number")