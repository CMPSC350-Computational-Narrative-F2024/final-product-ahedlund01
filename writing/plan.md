# CMPSC 350: Project Plan

## Summary

This project aims to extend an existing children's story generation application to create a narrative that explores themes of "polar opposites," such as Vikings living in Asia or sumo wrestlers ice skating. The project will use OpenAI's API for both text generation (via GPT models) and image generation (via DALL-E) to create stories that defy traditional expectations by placing characters or events in unusual and contrasting settings. The final product will consist of 30,000 to 49,999 words and 30 to 50 images, bundled into a professionally formatted PDF that includes a title page, Table of Contents, and references to similar creative works or inspirations. This project aligns with our semester's exploration of prompt engineering and creative uses of Large Language Models (LLMs).

## Peer works

1. **Radford, A., Wu, J., Amodei, D., Clark, J., Brundage, M., & Sutskever, I. (2019). *"Language Models are Unsupervised Multitask Learners."* OpenAI.**
   - This foundational paper introduces the GPT-2 language model and explores its capacity for generating coherent, contextually accurate text in a variety of tasks. It provides insights into prompt engineering and the versatility of LLMs, which is critical for understanding how to structure prompts for different narrative styles and constraints, like in children’s storytelling.

2. **Brown, T. B., Mann, B., Ryder, N., Subbiah, M., Kaplan, J., Dhariwal, P., ... & Amodei, D. (2020). *"Language Models are Few-Shot Learners."* Advances in Neural Information Processing Systems, 33.**
   - This paper presents GPT-3 and emphasizes few-shot learning, where minimal examples are needed to prompt the model. The concept of few-shot learning can be applied to develop nuanced prompts that guide the model effectively, particularly when generating polar-opposite story themes and maintaining consistency in long-form narratives.

3. **Peng, H., Huang, Z., Xie, X., & Liang, X. (2022). *"Characterizing the Diversity of Large Language Models in Generative Tasks."* Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics.**
   - This study examines how LLMs like GPT-3 vary in generating creative content and explores ways to manage narrative diversity and coherence. The findings could be useful for designing prompt sequences to ensure diverse but contextually appropriate story elements, especially in producing novel, unexpected scenarios that still align with narrative goals.

4. **Holtzman, A., Buys, J., Du, L., Forbes, M., & Choi, Y. (2020). *"The Curious Case of Neural Text Degeneration."* International Conference on Learning Representations (ICLR).**
   - This paper discusses issues with text degeneration in generative models, where output becomes repetitive or nonsensical over time, especially in longer texts. Techniques like nucleus sampling and controlling for model verbosity are highlighted, which could help in managing quality control over a story that spans thousands of words.

5. **Ziegler, D., Stiennon, N., Wu, J., Brown, T., Radford, A., Amodei, D., ... & Christiano, P. (2019). *"Fine-tuning Language Models from Human Preferences."* arXiv preprint arXiv:1909.08593.**
   - This work explores the fine-tuning of LLMs using human feedback to align outputs with specific user goals. It provides practical insights into controlling narrative tone and age-appropriateness—essential aspects for a children’s story generation application focused on interesting but context-sensitive themes.


## Challenges

1. **Generating a Large Volume of Content:** Writing a story of up to 49,999 words will require extensive prompt engineering to maintain consistency and coherence across all sections. Ensuring continuity of plot elements, character development, and thematic consistency in such a long narrative may be challenging.

2. **Consistency Between Text and Images:** Generating images that accurately match the narrative description and the "polar opposite" theme can be difficult, as it may require multiple prompt refinements in DALL-E to achieve the intended style and context without repetitive elements. Addressing image variation while maintaining the theme across all images will be crucial.

3. **Technical Constraints and Costs:** API usage for such a large-scale project could be costly, especially with the word count and number of images required. Additionally, handling API rate limits, ensuring stable internet connectivity, and managing long-running operations to create a seamless workflow for generating and assembling the PDF could be complex.
