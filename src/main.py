import os
import asyncio
from dotenv import dotenv_values
import openai
from openai import OpenAI

from story_generator import StoryGenerator
from config import MIN_WORDS, SCENARIOS
from utils import select_scenario_with_menu

# Configuration
CONFIG = dotenv_values(".env")
OPEN_AI_KEY = CONFIG.get("KEY") or os.environ.get("OPEN_AI_KEY")
OPEN_AI_ORG = CONFIG.get("ORG") or os.environ.get("OPEN_AI_ORG")

# Initialize OpenAI client
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
        scenario = await select_scenario_with_menu(client, temp_assistant)
        print(f"\nPreparing to generate story for: {scenario['setting']}")
        
        # Initialize story generator
        generator = StoryGenerator(client)
        await generator.initialize()
        
        # Create story and illustrator assistants
        generator.story_assistant = await generator.create_assistant(
            "Story Generator",
            f"""Generate an engaging {MIN_WORDS} word story about {scenario['setting']}.
            Theme: {scenario['description']}
            
            Requirements:
            - Rich character development
            - Detailed world-building
            - Cultural interactions and details
            - Natural dialogue
            - Engaging plot progression"""
        )
        
        generator.illustrator_assistant = await generator.create_assistant(
            "Illustrator",
            f"""Create detailed image prompts for {scenario['setting']} story.
            
            Requirements:
            - Focus on key visual elements
            - Blend contrasting cultural elements
            - No text in images
            - Maintain consistent character appearances
            - Appropriate for general audiences"""
        )
        
        # Generate story
        print("\nGenerating story...")
        try:
            story = await generator.generate_story(generator.story_assistant.id)
            print("\nStory generation complete!")
        except Exception as e:
            print(f"Error generating story: {e}")
            return
        
        # Split into chapters
        print("\nSplitting into chapters...")
        try:
            chapters = generator.split_into_chapters(story)
            print(f"Created {len(chapters)} chapters")
        except Exception as e:
            print(f"Error splitting chapters: {e}")
            return
        
        # Generate images
        print("\nGenerating images...")
        try:
            images = await generator.generate_all_images(chapters)
            print(f"Generated {len(images)} images")
        except Exception as e:
            print(f"Error generating images: {e}")
            return
        
        # Create PDF
        print("\nCreating PDF...")
        try:
            references = [
                f"1. Historical documentation about {scenario['setting']}",
                "2. Cultural studies and research",
                "3. Similar creative works"
            ]
            
            pdf_filename = generator.create_pdf(chapters, images, scenario, references)
            print(f"\n✨ Story generated successfully! ✨")
            print(f"📚 File saved as: {pdf_filename}")
            
        except Exception as e:
            print(f"Error creating PDF: {e}")
            return
        
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    
    finally:
        print("\nCleaning up resources...")
        # Cleanup assistants
        if 'temp_assistant' in locals():
            try:
                client.beta.assistants.delete(temp_assistant.id)
            except Exception as e:
                print(f"Error cleaning up temporary assistant: {e}")
        
        if 'generator' in locals():
            try:
                await generator.cleanup()
            except Exception as e:
                print(f"Error cleaning up generator: {e}")
        
        print("Clean up complete.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Cleaning up...")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    finally:
        print("\nProgram ended.")