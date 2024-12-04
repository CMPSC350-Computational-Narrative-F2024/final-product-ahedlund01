import os
import json
import requests
from dotenv import dotenv_values
import openai
from openai import OpenAI
from fpdf import FPDF
import unicodedata
import time
import random
import math
import itertools

# Configuration
CONFIG = dotenv_values(".env")
OPEN_AI_KEY = CONFIG["KEY"] or os.environ["OPEN_AI_KEY"]
OPEN_AI_ORG = CONFIG["ORG"] or os.environ["OPEN_AI_ORG"]
client = OpenAI(api_key=OPEN_AI_KEY)
client.organization = OPEN_AI_ORG

MIN_WORDS = 30000
MAX_WORDS = 49999
MIN_IMAGES = 30
MAX_IMAGES = 50
TOTAL_CHUNKS = 20  # Manually set number of chunks

SCENARIOS = [
    {"setting": "Vikings in Ancient China", "description": "Norse warriors learning the ways of silk trading and Confucian philosophy"},
    {"setting": "Sumo Wrestlers at the Winter Olympics", "description": "Japanese sumo champions training for figure skating competitions"},
    {"setting": "Desert Penguins", "description": "Antarctic penguins starting a colony in the Sahara Desert"},
    {"setting": "Space Pirates in the Deep Sea", "description": "Intergalactic privateers exploring ocean trenches"},
    {"setting": "Medieval Knights in Silicon Valley", "description": "Arthurian knights starting a tech startup"}
]

def clean_text(text):
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = unicodedata.normalize('NFKD', text)
    return ''.join(char for char in text if ord(char) < 128)

def get_word_count(text):
    return len(text.split())

def count_tokens(text):
    return int(len(text.split()) * 1.3)

def estimate_tokens_from_words(word_count):
    return int(word_count * 1.3)

def select_scenario_user_choice():
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
    scenario = random.choice(SCENARIOS)
    print(f"\nRandomly selected scenario: {scenario['setting']}")
    print(f"Description: {scenario['description']}")
    return scenario

def generate_dynamic_scenario(story_assistant):
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
        time.sleep(2)
    
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    response = messages.data[0].content[0].text.value
    lines = response.split('\n')
    setting = lines[0].replace('Setting:', '').strip()
    description = lines[1].replace('Description:', '').strip()
    
    return {"setting": setting, "description": description}

def select_scenario_with_menu(story_assistant):
    print("\n🌟 How would you like to select your scenario? 🌟")
    print("1. 📜 Choose from predefined scenarios, will take you to a new menu")
    print("2. 🎲 Random selection of the predefined scenarios")
    print("3. 🤖 Generate a brand new AI scenario")
    while True:
        try:
            choice = int(input("\nEnter your choice (1-3): "))
            if choice == 1:
                return select_scenario_user_choice()
            elif choice == 2:
                return select_scenario_random()
            elif choice == 3:
                return generate_dynamic_scenario(story_assistant)
            else:
                print("Please enter a number between 1 and 3")
        except ValueError:
            print("Please enter a valid number")

def create_story_assistant(scenario):
    assistant = client.beta.assistants.create(
        name="Polar Opposites Storyteller",
        instructions=f"""You are a creative author writing a {MIN_WORDS}-{MAX_WORDS} word story about {scenario['setting']}.
        Theme: {scenario['description']}
        
        The story will be written in {TOTAL_CHUNKS} chunks.
        Each chunk should be approximately {MIN_WORDS // TOTAL_CHUNKS} words.
        
        Requirements:
        - Consistent narrative flow between chunks
        - Rich character development and dialogue
        - Cultural details and descriptions
        - Each chunk should end with a hook to the next section""",
        tools=[{"type": "code_interpreter"}],
        model="gpt-4",
    )
    return assistant

def create_illustrator_assistant(scenario):
    assistant = client.beta.assistants.create(
        name="Polar Opposites Illustrator",
        instructions=f"""Create concise image prompts (max 100 words) for DALL-E 3.
        Theme: {scenario['setting']}
        
        Requirements:
        - Focus on key visual elements
        - Blend contrasting cultural elements
        - No text in images
        - Maintain consistent character appearances
        - Appropriate for general audiences""",
        tools=[{"type": "code_interpreter"}],
        model="gpt-4",
    )
    return assistant

def generate_story_chunk(assistant_id, chunk_number, total_chunks, previous_chunk=""):
    target_words = MIN_WORDS // TOTAL_CHUNKS
    thread = client.beta.threads.create()
    
    context = f"""Previous content: {previous_chunk[-500:] if previous_chunk else 'Story beginning'}
    
    Write chunk {chunk_number}/{total_chunks}.
    Target length: {target_words} words.
    
    Focus on:
    - Continuing the story naturally
    - Rich descriptions and dialogue
    - Cultural interactions and details
    - Leading to the next chunk"""
    
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=context
    )
    
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )
    
    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        if run_status.status == 'completed':
            break
        time.sleep(5)
    
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    chunk = clean_text(messages.data[0].content[0].text.value)
    return chunk

def generate_story(assistant_id):
    print(f"\nGenerating story in {TOTAL_CHUNKS} chunks...")
    full_story = []
    total_words = 0
    
    for i in range(TOTAL_CHUNKS):
        print(f"\nGenerating chunk {i+1} of {TOTAL_CHUNKS}...")
        chunk = generate_story_chunk(
            assistant_id,
            i+1,
            TOTAL_CHUNKS,
            previous_chunk=full_story[-1] if full_story else ""
        )
        
        chunk_words = get_word_count(chunk)
        total_words += chunk_words
        print(f"Chunk {i+1} word count: {chunk_words}")
        print(f"Total word count so far: {total_words}")
        
        full_story.append(chunk)
            
    return "\n\n".join(full_story)

def split_into_chapters(story):
    paragraphs = story.split('\n\n')
    paragraphs_per_chapter = max(1, len(paragraphs) // MIN_IMAGES)
    chapters = {}
    
    for i in range(MIN_IMAGES):
        start_idx = i * paragraphs_per_chapter
        end_idx = start_idx + paragraphs_per_chapter if i < MIN_IMAGES - 1 else len(paragraphs)
        chapter_content = '\n\n'.join(paragraphs[start_idx:end_idx])
        chapters[f"Chapter {i + 1}"] = chapter_content
    
    return chapters

def get_image_prompt(assistant_id, chapter_content):
    thread = client.beta.threads.create()
    
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"Create a single, concise image prompt (max 100 words) for this chapter:\n\n{chapter_content[:1000]}"
    )
    
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )
    
    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        if run_status.status == 'completed':
            break
        time.sleep(5)
    
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    prompt = clean_text(messages.data[0].content[0].text.value)
    return prompt[:1000]

def generate_image(prompt_text, image_filename):
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt_text,
            size="1024x1024",
            quality="hd",
            n=1
        )
        
        image_url = response.data[0].url
        image_data = requests.get(image_url).content
        
        with open(image_filename, 'wb') as f:
            f.write(image_data)
        
        return image_filename
    except Exception as e:
        print(f"Error generating image: {e}")
        return None

def create_pdf(chapters, images, scenario, references):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Title Page
    pdf.add_page()
    pdf.set_font("Arial", 'B', size=24)
    title = f"Polar Opposites: {scenario['setting']}"
    pdf.cell(0, 10, txt=title, ln=True, align='C')
    pdf.ln(20)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=scenario['description'])
    
    # Chapters
    for chapter_title, chapter_content in chapters.items():
        pdf.add_page()
        
        image_filename = images.get(chapter_title)
        if image_filename and os.path.exists(image_filename):
            img_width = 160
            img_height = img_width
            x = (210 - img_width) / 2
            pdf.image(image_filename, x=x, y=20, w=img_width)
            pdf.set_y(20 + img_height + 10)
        
        pdf.set_font("Arial", 'B', size=16)
        pdf.cell(0, 10, txt=clean_text(chapter_title), ln=True)
        pdf.ln(5)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=clean_text(chapter_content))

    pdf_filename = f"polar_opposites_{scenario['setting'].lower().replace(' ', '_')}.pdf"
    pdf.output(pdf_filename)
    return pdf_filename

def main():
    print("🌟 Welcome to the Polar Opposites Story Generator! 🌟")
    print("✨ Let's embark on a creative journey to craft a unique and captivating story together! ✨")
    print("📚 Get ready to explore fascinating scenarios and bring them to life with words and images! 📚")
    
    temp_story_assistant = client.beta.assistants.create(
        name="Scenario Generator",
        instructions="Generate creative polar opposite scenarios for stories.",
        tools=[{"type": "code_interpreter"}],
        model="gpt-4",
    )
    
    try:
        scenario = select_scenario_with_menu(temp_story_assistant)
        print(f"\nPreparing to generate story for: {scenario['setting']}")
        
        story_assistant = create_story_assistant(scenario)
        illustrator_assistant = create_illustrator_assistant(scenario)

        story = generate_story(story_assistant.id)
        word_count = get_word_count(story)
        print(f"\nCompleted story generation with {word_count} words")
        
        chapters = split_into_chapters(story)
        
        images = {}
        print(f"\nGenerating {MIN_IMAGES} images...")
        
        for i, (chapter_title, chapter_content) in enumerate(chapters.items(), start=1):
            print(f"Generating image {i} of {MIN_IMAGES}...")
            image_prompt = get_image_prompt(illustrator_assistant.id, chapter_content)
            image_filename = f'chapter_{i}.png'
            generate_image(image_prompt, image_filename)
            images[chapter_title] = image_filename
            time.sleep(2)

        references = [
            f"1. Historical documentation about {scenario['setting']}",
            "2. Cultural studies and research",
            "3. Similar creative works"
        ]

        pdf_filename = create_pdf(chapters, images, scenario, references)
        print(f"\nStory generated and saved as {pdf_filename}")

    except Exception as e:
        print(f"\nAn error occurred: {e}")
    
    finally:
        print("\nCleaning up resources...")
        for assistant in [temp_story_assistant, story_assistant, illustrator_assistant]:
            if 'assistant' in locals():
                client.beta.assistants.delete(assistant.id)
        print("Clean up complete.")

if __name__ == "__main__":
    main()