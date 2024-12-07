import os
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.units import inch

from config import MIN_WORDS, MAX_WORDS, MIN_IMAGES, TOTAL_CHUNKS, PDF_STYLES
from utils import clean_text, get_word_count

class StoryGenerator:
    def __init__(self, client):
        self.client = client
        self.story_assistant = None
        self.illustrator_assistant = None
        self.session = None
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.chunk_semaphore = asyncio.Semaphore(5)
        self.image_semaphore = asyncio.Semaphore(3)

    async def initialize(self):
        """Initialize async session"""
        self.session = aiohttp.ClientSession()

    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
        if self.executor:
            self.executor.shutdown()
        # Cleanup assistants
        for assistant in [self.story_assistant, self.illustrator_assistant]:
            if assistant:
                await self.delete_assistant(assistant.id)

    async def create_assistant(self, name, instructions):
        """Create an OpenAI assistant"""
        return self.client.beta.assistants.create(
            name=name,
            instructions=instructions,
            tools=[{"type": "code_interpreter"}],
            model="gpt-4"
        )

    async def delete_assistant(self, assistant_id):
        """Delete an OpenAI assistant"""
        try:
            self.client.beta.assistants.delete(assistant_id)
        except Exception as e:
            print(f"Error deleting assistant: {e}")

    async def generate_story_chunk(self, assistant_id, chunk_number, total_chunks, previous_chunk=""):
        """Generate a single story chunk with rate limiting"""
        async with self.chunk_semaphore:
            try:
                thread = self.client.beta.threads.create()
                target_words = MIN_WORDS // TOTAL_CHUNKS
                
                context = f"""Previous content: {previous_chunk[-500:] if previous_chunk else 'Story beginning'}
                Write chunk {chunk_number}/{total_chunks}.
                Target length: {target_words} words.
                
                Requirements:
                - Natural continuation
                - Rich descriptions and dialogue
                - Cultural interactions
                - Hook for next section"""
                
                message = self.client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=context
                )
                
                run = self.client.beta.threads.runs.create(
                    thread_id=thread.id,
                    assistant_id=assistant_id,
                )
                
                while True:
                    run_status = self.client.beta.threads.runs.retrieve(
                        thread_id=thread.id,
                        run_id=run.id
                    )
                    if run_status.status == 'completed':
                        break
                    await asyncio.sleep(2)
                
                messages = self.client.beta.threads.messages.list(thread_id=thread.id)
                chunk = clean_text(messages.data[0].content[0].text.value)
                print(f"Generated chunk {chunk_number}/{total_chunks} with {get_word_count(chunk)} words")
                return chunk
                
            except Exception as e:
                print(f"Error generating chunk {chunk_number}: {e}")
                return ""

    async def generate_story(self, assistant_id):
        """Generate story chunks concurrently"""
        print(f"\nGenerating story in {TOTAL_CHUNKS} chunks...")
        chunks = [""] * TOTAL_CHUNKS
        tasks = []
        
        for i in range(TOTAL_CHUNKS):
            previous_chunk = chunks[i-1] if i > 0 else ""
            task = asyncio.create_task(
                self.generate_story_chunk(
                    assistant_id,
                    i+1,
                    TOTAL_CHUNKS,
                    previous_chunk
                )
            )
            tasks.append((i, task))
        
        total_words = 0
        for i, task in tasks:
            try:
                chunk = await task
                chunks[i] = chunk
                chunk_words = get_word_count(chunk)
                total_words += chunk_words
                print(f"Chunk {i+1} complete. Total words so far: {total_words}")
            except Exception as e:
                print(f"Error in chunk {i+1}: {e}")
        
        return "\n\n".join(chunks)

    async def get_image_prompt(self, assistant_id, chapter_content):
        """Generate image prompt for a chapter"""
        thread = self.client.beta.threads.create()
        
        message = self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"Create a single, concise image prompt (max 100 words) for this chapter:\n\n{chapter_content[:1000]}"
        )
        
        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id
        )
        
        while True:
            run_status = self.client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run_status.status == 'completed':
                break
            await asyncio.sleep(2)
        
        messages = self.client.beta.threads.messages.list(thread_id=thread.id)
        return clean_text(messages.data[0].content[0].text.value)

    async def generate_image(self, prompt, filename):
        """Generate image from prompt with retries"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size="1024x1024",
                    quality="hd",
                    n=1
                )
                
                image_url = response.data[0].url
                async with self.session.get(image_url) as resp:
                    if resp.status == 200:
                        image_data = await resp.read()
                        with open(filename, 'wb') as f:
                            f.write(image_data)
                        return filename
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Failed to generate image after {max_retries} attempts: {e}")
                    return None
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        return None

    async def generate_all_images(self, chapters):
        """Generate all images concurrently with rate limiting"""
        images = {}
        
        async def generate_single_image(chapter_title, chapter_content, index):
            async with self.image_semaphore:
                prompt = await self.get_image_prompt(self.illustrator_assistant.id, chapter_content)
                filename = f'chapter_{index}.png'
                result = await self.generate_image(prompt, filename)
                if result:
                    images[chapter_title] = result
                    print(f"Generated image {index}/{len(chapters)}")
        
        tasks = [
            generate_single_image(title, content, i)
            for i, (title, content) in enumerate(chapters.items(), 1)
        ]
        
        await asyncio.gather(*tasks)
        return images

    def split_into_chapters(self, story):
        """Split story into chapters"""
        paragraphs = story.split('\n\n')
        paragraphs_per_chapter = max(1, len(paragraphs) // MIN_IMAGES)
        chapters = {}
        
        for i in range(MIN_IMAGES):
            start_idx = i * paragraphs_per_chapter
            end_idx = start_idx + paragraphs_per_chapter if i < MIN_IMAGES - 1 else len(paragraphs)
            chapter_content = '\n\n'.join(paragraphs[start_idx:end_idx])
            chapters[f"Chapter {i + 1}"] = chapter_content
        
        return chapters

    def create_pdf(self, chapters, images, scenario, references):
        """Create PDF with enhanced styling"""
        filename = f"polar_opposites_{scenario['setting'].lower().replace(' ', '_')}.pdf"
        doc = SimpleDocTemplate(
            filename,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Create custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=PDF_STYLES['title']['fontSize'],
            spaceAfter=PDF_STYLES['title']['spaceAfter'],
            alignment=PDF_STYLES['title']['alignment']
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=PDF_STYLES['subtitle']['fontSize'],
            spaceAfter=PDF_STYLES['subtitle']['spaceAfter'],
            alignment=PDF_STYLES['subtitle']['alignment']
        )
        
        chapter_style = ParagraphStyle(
            'ChapterTitle',
            parent=styles['Heading1'],
            fontSize=PDF_STYLES['chapter']['fontSize'],
            spaceAfter=PDF_STYLES['chapter']['spaceAfter'],
            alignment=PDF_STYLES['chapter']['alignment']
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=PDF_STYLES['body']['fontSize'],
            leading=PDF_STYLES['body']['leading'],
            spaceBefore=PDF_STYLES['body']['spaceBefore'],
            spaceAfter=PDF_STYLES['body']['spaceAfter']
        )
        
        # Title page
        story.append(Paragraph(f"Polar Opposites:", title_style))
        story.append(Paragraph(scenario['setting'], title_style))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(scenario['description'], subtitle_style))
        story.append(Spacer(1, 2*inch))
        story.append(PageBreak())
        
        # Table of Contents
        story.append(Paragraph("Table of Contents", chapter_style))
        for chapter_title in chapters.keys():
            story.append(Paragraph(chapter_title, body_style))
        story.append(PageBreak())
        
        # Chapters with images
        for chapter_title, chapter_content in chapters.items():
            story.append(Paragraph(chapter_title, chapter_style))
            
            image_path = images.get(chapter_title)
            if image_path and os.path.exists(image_path):
                img = Image(image_path, width=6*inch, height=6*inch)
                img.hAlign = 'CENTER'
                story.append(img)
                story.append(Spacer(1, 0.5*inch))
            
            paragraphs = chapter_content.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para, body_style))
            
            story.append(PageBreak())
        
        # References section
        if references:
            story.append(Paragraph("References", chapter_style))
            for ref in references:
                story.append(Paragraph(ref, body_style))
        
        # Build PDF
        doc.build(story)
        return filename