# CMPSC 350: Final Reflection

## Final title

Interactive Polar Opposite Story Generator

## Summary

The project is an AI-powered story generator that creates unique narratives by combining contrasting cultural elements, complete with AI-generated illustrations. This generator emphasizes the intersection of human creativity and machine assistance by allowing users to either select from predefined scenarios, generate new ones, or create and enhance their own scenarios through AI collaboration.

## Reference works

The project's approach to generating coherent long-form narratives directly relates to Holtzman et al.'s "The Curious Case of Neural Text Degeneration," particularly in addressing the challenge of maintaining narrative consistency over thousands of words. This is reflected in our chunked generation approach, where the story is broken into manageable segments with contextual threading, preventing the text degeneration issues Holtzman describes. The project's "polar opposites" theme implementation draws from Brown et al.'s work on few-shot learning in "Language Models are Few-Shot Learners," particularly in how we structure prompts to maintain thematic consistency while generating creative cultural combinations. Additionally, Peng et al.'s research on LLM diversity in generative tasks informed our implementation of scenario enhancement, where users can choose between multiple AI-generated variations of their ideas, demonstrating the balance between creative diversity and narrative coherence.

## Describe your single largest success.

The project's most significant achievement is its successful implementation of a hybrid human-AI creative process. The system not only generates stories but also allows users to actively participate in the creative process by providing their own scenarios and choosing whether to enhance them with AI suggestions. This creates a genuine collaboration between human creativity and machine capabilities.

## Describe your single largest challenge or failure.

The biggest challenge was optimizing the performance and managing asynchronous operations effectively. The initial implementation faced issues with sequential processing that made the program slow and unresponsive. This was addressed by implementing concurrent processing for story chunks and image generation, along with proper error handling and resource management, though it required significant refactoring and careful consideration of API rate limits.

## The role of feedback

Peer feedback significantly shaped the project's development in two crucial ways. First, Audrey's feedback about the program's ability to maintain consistent syntax throughout the document validated our chunked generation approach while suggesting the exploration of different LLMs for potentially better results. This led to improvements in our prompt engineering to better handle token and word limit requirements. Second, the peer questions about theme selection and narrative coherence prompted us to implement the user scenario enhancement feature, allowing users to either use their scenarios as-is or receive AI-enhanced versions, thereby addressing concerns about both theme selection and narrative consistency. Additionally, feedback about the generation time and API token limitations led to the implementation of concurrent processing and better resource management in our code.

## Contextualizing

This work exemplifies how language technology can serve as a bridge between human creativity and computational capabilities. The program demonstrates how technology can be used not just to generate content, but to augment and enhance human creative expression. The key takeaway is that effective human-AI collaboration in creative work requires carefully designed interfaces and interactions that preserve human agency while leveraging computational power. This is reflected in how the program allows users to maintain control over their creative choices while offering AI assistance when desired.