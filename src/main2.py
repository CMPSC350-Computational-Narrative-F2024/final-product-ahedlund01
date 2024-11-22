import os
import json
import requests
from dotenv import dotenv_values
import openai
from openai import OpenAI
from fpdf import FPDF
import unicodedata
import time

# Set up OpenAI credentials
CONFIG = dotenv_values(".env")
OPEN_AI_KEY = CONFIG["KEY"] or os.environ["OPEN_AI_KEY"]
OPEN_AI_ORG = CONFIG["ORG"] or os.environ["OPEN_AI_ORG"]
client = OpenAI(api_key=OPEN_AI_KEY)
client.organization = OPEN_AI_ORG

def clean_text(text):
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = unicodedata.normalize('NFKD', text)
    return ''.join(char for char in text if ord(char) < 128)


def create_story_assistant():
    assistant = client.beta.assistants.create(
        name="Children's Book Author",
        instructions="""You are a creative children's book author specializing in stories for children ages 5-7. 
        Write a children's story of 900-1000 words, divided into 10 chapters. 
        The setting is a magical botanical garden full of bright and colorful plants.
        The story should focus on three animal friends going on a journey through the botanical garden.
        The three main characters are: a butterfly, a fluffy white rabbit, and a wise owl. Maintain these specific descriptions throughout the story.
        During their adventure, they encounter a problem and must work together to find a solution.
        Include elements of friendship, teamwork, problem-solving, and excitement.
        Make it engaging, fun, and appropriate for children ages 5-7.
        Don't include any human characters in the story.
        Keep the different characters' identities and descriptions consistent throughout the story.
        The specific details of the journey, the problem they face, and how they solve it should be generated by the code.
        Example opening:
        `In a magical botanical garden, where flowers sang and trees danced, lived three unlikely friends: Bella the butterfly with iridescent wings, Rudy the fluffy white rabbit with long ears, and Owen the wise brown owl with large golden eyes. One sunny morning, they decided to go on an adventure through the garden's winding paths...`""",
        tools=[{"type": "code_interpreter"}],
        model="gpt-4",
    )
    return assistant

def create_illustrator_assistant():
    assistant = client.beta.assistants.create(
        name="Children's Book Illustrator",
        instructions="""You are a creative, imaginative, and fun children's book illustrator specializing in creating prompts 
        for whimsical and magical illustrations with a focus on their journey. Generate appropriate image descriptions 
        in two sentences or less for children's book illustrations that will be created using DALL-E.
        Focus on illustrating scenes from a magical botanical garden with three animal friends on an adventure.
        For example; a butterfly with incredible wings, a fluffy white rabbit, and a wise owl with large golden eyes.
        Ensure that the illustrations capture the vibrant colors of the garden.  
        Incoporate key moments from their journey, including the problem they face and how they work together to solve it.
        Keep the characters' appearances consistent in every illustration.
        Include elements that showcase friendship, teamwork, and the magical nature of the garden.
        Do not introduce any new characters beyond these three main characters.
        IMPORTANT: A constraint of no text in the images generated.""",
        tools=[{"type": "code_interpreter"}],
        model="gpt-4",
    )
    return assistant

def generate_story(assistant_id):
    thread = client.beta.threads.create()
    
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="Write a children's story following your instructions. Make it a engaging and magical journey."
    )
    
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )
    
    while run.status != 'completed':
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    story = clean_text(messages.data[0].content[0].text.value)
    return story

def get_image_prompt(assistant_id, chapter_content):
    thread = client.beta.threads.create()
    
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"Create a detailed image prompt for the following chapter:\n\n{chapter_content}"
    )
    
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )
    
    while run.status != 'completed':
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    prompt = clean_text(messages.data[0].content[0].text.value)
    return prompt

def generate_image(prompt_text, image_filename):
    response = client.images.generate(
        model='dall-e-3',
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

def split_into_chapters(story):
    chapters = {}
    lines = story.split('\n')
    current_chapter = ""
    current_content = ""
    for line in lines:
        if line.strip().startswith("Chapter"):
            if current_chapter:
                chapters[current_chapter] = current_content.strip()
                current_content = ""
            current_chapter = line.strip()
        else:
            current_content += line + '\n'
    if current_chapter:
        chapters[current_chapter] = current_content.strip()
    return chapters

def create_pdf(chapters, images):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    if not chapters:
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt="No chapters were generated. Please try again.")
        pdf_filename = "error_magical_botanical_garden_storybook.pdf"
        pdf.output(pdf_filename)
        print(f"Error PDF generated and saved as {pdf_filename}")
        return

    # Add a title page
    pdf.add_page()

    # Add the book title first
    pdf.set_font("Arial", 'B', size=24)
    pdf.cell(0, 10, txt="The Magical Botanical Garden", ln=True, align='C')
    pdf.ln(10)

    # Process first chapter
    first_chapter_title, first_chapter_content = next(iter(chapters.items()))

    # Add first chapter title
    pdf.set_font("Arial", 'B', size=18)
    pdf.cell(0, 10, txt=clean_text(first_chapter_title), ln=True)
    pdf.ln(5)

    # Add image for the first chapter
    image_filename = images.get(first_chapter_title)
    if image_filename and os.path.exists(image_filename):
        img_width = 160  # Adjust this value as needed
        img_height = img_width  # Assuming square images
        x = (210 - img_width) / 2  # Center image horizontally
        pdf.image(image_filename, x=x, y=pdf.get_y(), w=img_width)
        pdf.ln(img_height + 10)  # Move cursor below the image

    # Add first chapter content
    pdf.set_font("Arial", size=12)
    
    # Split the content and remove the first line if it's a title
    content_lines = first_chapter_content.split('\n')
    if content_lines[0].startswith('Title:'):
        content_lines = content_lines[1:]
    
    pdf.multi_cell(0, 10, txt=clean_text('\n'.join(content_lines)))

    # Process remaining chapters
    for chapter_title, chapter_content in list(chapters.items())[1:]:
        pdf.add_page()
        
        # Add image
        image_filename = images.get(chapter_title)
        if image_filename and os.path.exists(image_filename):
            img_width = 160  # Adjust this value as needed
            img_height = img_width  # Assuming square images
            x = (210 - img_width) / 2  # Center image horizontally
            pdf.image(image_filename, x=x, y=20, w=img_width)
            
            # Move cursor below the image
            pdf.set_y(20 + img_height + 10)  # 10 is for spacing
        
        # Add chapter title
        pdf.set_font("Arial", 'B', size=16)
        pdf.cell(0, 10, txt=clean_text(chapter_title), ln=True)
        pdf.ln(5)
        
        # Add chapter content
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=clean_text(chapter_content))
        pdf.ln(5)

    pdf_filename = "magical_botanical_garden_storybook2.pdf"
    pdf.output(pdf_filename)
    print(f"PDF generated and saved as {pdf_filename}")

def main():
    # Create assistants
    story_assistant = create_story_assistant()
    illustrator_assistant = create_illustrator_assistant()

    # Generate the story
    story = generate_story(story_assistant.id)
    print("Generated Story:\n")
    print(story)
    print("\n" + "="*50 + "\n")

    # Split the story into chapters
    chapters = split_into_chapters(story)

    # Process each chapter
    images = {}
    for i, (chapter_title, chapter_content) in enumerate(chapters.items(), start=1):
        print(f"{chapter_title}\n{chapter_content}\n")

        # Get image prompt
        image_prompt = get_image_prompt(illustrator_assistant.id, chapter_content)
        
        print(f"Image Prompt for {chapter_title}:")
        print(image_prompt)
        print("\n" + "-"*50 + "\n")

        # Generate the image
        image_filename = f'chapter_{i}.png'
        generate_image(image_prompt, image_filename)
        images[chapter_title] = image_filename
        print(f"Generated image saved as {image_filename}\n")
        print("-" * 50 + "\n")

    # Create the PDF with the story and images
    create_pdf(chapters, images)

    # Clean up assistants
    client.beta.assistants.delete(story_assistant.id)
    client.beta.assistants.delete(illustrator_assistant.id)

if __name__ == "__main__":
    main()
