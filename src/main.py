import os
import asyncio
from dotenv import dotenv_values
import openai
from openai import OpenAI

from story_generator import StoryGenerator
from config import SCENARIOS
from utils import select_scenario_with_menu

# Configuration
CONFIG = dotenv_values(".env")
OPEN_AI_KEY = CONFIG.get("KEY") or os.environ.get("OPEN_AI_KEY")
OPEN_AI_ORG = CONFIG.get("ORG") or os.environ.get("OPEN_AI_ORG")
client = OpenAI(api_key=OPEN_AI_KEY)
client.organization = OPEN_AI_ORG

async def main():
    print("🌟 Welcome to the Polar Opposites Story Generator! 🌟")
    print("✨ Let's embark on a creative journey to craft a unique and captivating story together! ✨")
    print("📚 Get ready to explore fascinating scenarios and bring them to life with words and images! 📚")
    
    # Create temporary assistant for scenario selection
    temp_assistant = client.beta.assistants.create(
        name="Scenario Generator",
        instructions="Generate creative polar opposite scenarios for stories.",
        tools=[{"type": "code_interpreter"}],
        model="gpt-4"
    )
    
    try:
        # Select scenario
        scenario = select_scenario_with_menu(temp_assistant)
        print(f"\nPreparing to generate story for: {scenario['setting']}")
        
        # Initialize story generator
        generator = StoryGenerator(client)
        await generator.initialize()
        
        # Create story and illustrator assistants
        generator.story_assistant = await generator.create_assistant(
            "Story Generator",
            f"Generate an engaging story about {scenario['setting']}. "
            f"Theme: {scenario['description']}"
        )
        
        generator.illustrator_assistant = await generator.create_assistant(
            "Illustrator",
            f"Create detailed image prompts for {scenario['setting']} story."
        )
        
        # Generate story
        print("\nGenerating story...")
        story = await generator.generate_story(generator.story_assistant.id)
        
        # Split into chapters
        print("\nSplitting into chapters...")
        chapters = generator.split_into_chapters(story)
        
        # Generate images
        print("\nGenerating images...")
        images = await generator.generate_all_images(chapters)
        
        # Create PDF
        print("\nCreating PDF...")
        references = [
            f"1. Historical documentation about {scenario['setting']}",
            "2. Cultural studies and research",
            "3. Similar creative works"
        ]
        
        pdf_filename = generator.create_pdf(chapters, images, scenario, references)
        print(f"\nStory generated successfully! File saved as: {pdf_filename}")
        
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    
    finally:
        # Cleanup
        if 'temp_assistant' in locals():
            client.beta.assistants.delete(temp_assistant.id)
        if 'generator' in locals():
            await generator.cleanup()

if __name__ == "__main__":
    asyncio.run(main())