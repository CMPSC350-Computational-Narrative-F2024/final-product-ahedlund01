import os
from openai import OpenAI
from dotenv import dotenv_values
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from urllib.request import urlopen
from PIL import Image
import time

# Set up OpenAI client
CONFIG = dotenv_values(".env")
OPEN_AI_KEY = CONFIG.get("KEY") or os.environ.get("OPEN_AI_KEY")
OPEN_AI_ORG = CONFIG.get("ORG") or os.environ.get("OPEN_AI_ORG")

client = OpenAI(
    api_key=OPEN_AI_KEY,
    organization=OPEN_AI_ORG
)

# Load prompts from external files
def load_file(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

# Create a story writing assistant
assistant = client.beta.assistants.create(
    name="Children's Story Writer",
    instructions="You are a creative assistant that writes children's stories. You specialize in creating engaging, age-appropriate content for children ages 5-7.",
    tools=[{"type": "code_interpreter"}],
    model="gpt-4"
)

# Function to generate text using Assistant API
def generate_text_prompt(chapter_title, content_description):
    # Create a new thread for this chapter
    thread = client.beta.threads.create()
    
    # Create the message
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"Write a {chapter_title} for a children's story called 'The Day the Colors Disappeared.' The story should be around 100-150 words and should be written for children ages 5-7. {content_description}"
    )
    
    # Create and start the run
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
    
    # Poll for completion
    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        if run_status.status == 'completed':
            break
        elif run_status.status == 'failed':
            raise Exception("Assistant run failed")
        time.sleep(1)
    
    # Get the response
    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )
    return messages.data[0].content[0].text.value

# Function to generate image using DALL-E
def generate_image_prompt(description):
    response = client.images.generate(
        model="dall-e-3",
        prompt=description,
        n=1
    )
    return response.data[0].url

# Load chapters and image descriptions from individual files
chapter_files = [
    "prompts/chapter1text.txt",
    "prompts/chapter2text.txt",
    "prompts/chapter3text.txt",
    "prompts/chapter4text.txt",
    "prompts/chapter5text.txt"
]

image_files = [
    "prompts/chap1img.txt",
    "prompts/chap2img.txt",
    "prompts/chap3img.txt",
    "prompts/chap4img.txt",
    "prompts/chap5img.txt"
]

try:
    # Generate text for each chapter
    generated_texts = []
    for chapter_file in chapter_files:
        chapter_text = load_file(chapter_file)
        chapter_title = chapter_file.split("/")[-1].replace("text.txt", "").capitalize()
        text = generate_text_prompt(chapter_title, chapter_text)
        generated_texts.append(text)

    # Generate images for each description
    generated_images = []
    for image_file in image_files:
        image_desc = load_file(image_file)
        image_url = generate_image_prompt(image_desc)
        generated_images.append(image_url)

    # Function to create a PDF file combining text and images
    def create_pdf(texts, images, filename="storybook.pdf"):
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        
        # Add title page
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width/2, height - 100, "The Day the Colors Disappeared")
        c.setFont("Helvetica", 18)
        c.drawCentredString(width/2, height - 130, "A story about the adventure to bring colors back to the world")
        c.showPage()

        # Add each chapter with its image as background
        for i, text in enumerate(texts):
            # Download and prepare the image
            if i < len(images):
                image_file = urlopen(images[i])
                img = Image.open(image_file)
                img = img.convert('RGBA')
                
                # Adjust image opacity for better text readability
                alpha = 0.3  # 30% opacity
                img.putalpha(int(255 * alpha))
                
                # Save temporary image
                img_path = f"temp_img_{i}.png"
                img.save(img_path)
                
                # Draw the image as background
                c.drawImage(img_path, 0, 0, width=width, height=height)
                os.remove(img_path)

            # Add semi-transparent white rectangle for better text readability
            c.setFillColorRGB(1, 1, 1, 0.7)
            c.rect(50, 50, width-100, height-100, fill=True)
            
            # Add chapter title
            c.setFillColorRGB(0, 0, 0, 1)  # Black color for text
            c.setFont("Helvetica-Bold", 18)
            c.drawString(70, height - 100, f"Chapter {i+1}:")
            
            # Add story text with word wrapping
            c.setFont("Helvetica", 14)
            text_object = c.beginText()
            text_object.setTextOrigin(70, height - 140)
            
            # Word wrap implementation
            words = text.split()
            lines = []
            current_line = []
            current_width = 0
            max_width = width - 140  # Margins on both sides
            
            for word in words:
                word_width = c.stringWidth(word + " ", "Helvetica", 14)
                if current_width + word_width <= max_width:
                    current_line.append(word)
                    current_width += word_width
                else:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                    current_width = word_width
            
            if current_line:
                lines.append(" ".join(current_line))
            
            # Add lines to text object with proper spacing
            line_height = 20
            for line in lines:
                text_object.textLine(line)
                text_object.moveCursor(0, line_height)
            
            c.drawText(text_object)
            c.showPage()
        
        c.save()
        
    # Create the final storybook PDF
    create_pdf(generated_texts, generated_images)

    print("Storybook has been successfully created as 'storybook.pdf'.")

finally:
    # Clean up - delete the assistant
    client.beta.assistants.delete(assistant.id)