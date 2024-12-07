import random
import asyncio
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

def create_user_scenario():
    """Get scenario input from user"""
    print("\nCreate your own scenario:")
    print("Example format:")
    print("Setting: Vikings in Ancient China")
    print("Description: Norse warriors learning the ways of silk trading and Confucian philosophy")
    
    setting = input("\nEnter your scenario setting: ")
    description = input("Enter your scenario description: ")
    
    return {"setting": setting, "description": description}

async def generate_dynamic_scenario(client, assistant):
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
        assistant_id=assistant.id
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

async def enhance_user_scenario(client, assistant, user_scenario):
    """Enhance user-provided scenario with AI suggestions"""
    print("\nEnhancing your scenario with AI suggestions...")
    
    prompt = f"""Based on the user's scenario:
    Setting: {user_scenario['setting']}
    Description: {user_scenario['description']}
    
    Please enhance this scenario by:
    1. Adding more specific cultural or thematic elements
    2. Developing potential plot points
    3. Suggesting interesting character dynamics
    
    Return THREE enhanced versions in this format:
    Version 1:
    Setting: [Enhanced title]
    Description: [Enhanced description]
    
    Version 2: ...
    """
    
    thread = client.beta.threads.create()
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt
    )
    
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
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
    
    # Parse the enhanced versions
    versions = []
    current_version = {}
    
    for line in response.split('\n'):
        line = line.strip()
        if line.startswith('Version'):
            if current_version:
                versions.append(current_version)
                current_version = {}
        elif line.startswith('Setting:'):
            current_version['setting'] = line.replace('Setting:', '').strip()
        elif line.startswith('Description:'):
            current_version['description'] = line.replace('Description:', '').strip()
    
    if current_version:
        versions.append(current_version)
    
    return versions

async def handle_user_scenario(client, assistant):
    """Handle user scenario creation and enhancement"""
    user_scenario = create_user_scenario()
    
    print("\nWould you like to:")
    print("1. Use your scenario as is")
    print("2. Get AI-enhanced versions of your scenario")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (1-2): "))
            if choice == 1:
                return user_scenario
            elif choice == 2:
                enhanced_versions = await enhance_user_scenario(client, assistant, user_scenario)
                
                print("\nEnhanced versions of your scenario:")
                for i, version in enumerate(enhanced_versions, 1):
                    print(f"\nVersion {i}:")
                    print(f"Setting: {version['setting']}")
                    print(f"Description: {version['description']}")
                
                print("\n0. Use original scenario")
                print("1-3. Select enhanced version")
                
                while True:
                    try:
                        version_choice = int(input("\nSelect version (0-3): "))
                        if version_choice == 0:
                            return user_scenario
                        elif 1 <= version_choice <= len(enhanced_versions):
                            return enhanced_versions[version_choice - 1]
                        print(f"Please enter a number between 0 and {len(enhanced_versions)}")
                    except ValueError:
                        print("Please enter a valid number")
                
            print("Please enter either 1 or 2")
        except ValueError:
            print("Please enter a valid number")

async def select_scenario_with_menu(client, assistant):
    """Main scenario selection menu"""
    print("\n🌟 How would you like to select your scenario? 🌟")
    print("1. 📜 Choose from predefined scenarios")
    print("2. 🎲 Random selection")
    print("3. 🤖 Generate a brand new AI scenario")
    print("4. ✍️ Create your own scenario")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (1-4): "))
            if choice == 1:
                return select_scenario_user_choice()
            elif choice == 2:
                return select_scenario_random()
            elif choice == 3:
                return await generate_dynamic_scenario(client, assistant)
            elif choice == 4:
                return await handle_user_scenario(client, assistant)
            else:
                print("Please enter a number between 1 and 4")
        except ValueError:
            print("Please enter a valid number")