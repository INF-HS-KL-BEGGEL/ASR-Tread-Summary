PROMPT_SYSTEM = "You are a summarization engine."

PROMPT_SUMMARY_OF_POST_CHUNKS = """You are tasked with summarizing chunks of posts from a forum discussion. 

Please ensure your summary adheres to the following detailed requirements:

Factual Accuracy: The summary must be factually correct. Do not include any imagined information or assumptions. Only include details that are explicitly mentioned in the forum posts.

No Repetitions: Avoid repeating the same information. Each piece of information should be unique and add value to the summary.

Contextual Information Only: Use only the information provided in the context of the forum posts. Do not incorporate any external knowledge or data that is not part of the forum discussion.

Reader Engagement: Structure the summary in a way that enables the reader to easily understand and participate in the ongoing discussion. The reader should be able to follow the main points and contribute meaningfully to the conversation.

Balance of Opinions: Clearly indicate where the balance of opinions landed both during and after the discussion. Highlight the consensus or predominant viewpoints that emerged as well as any significant minority opinions.

Topic-Focused: Focus on summarizing the content of the discussion rather than listing the topics that were mentioned. Provide insights into what was actually discussed about each topic.

Avoiding the Discussion Path: Do not describe the sequence or path of the discussion. Instead, focus on the key points and conclusions reached.

Paragraph Structure: Write one paragraph per topic discussed. Each paragraph should clearly cover a distinct topic or aspect of the discussion, providing a concise yet comprehensive overview.

Please apply this approach to the forum posts provided, ensuring that your summary is clear, concise, and meets all the specified requirements.

$chunk_content  
"""


PROMPT_SUMMARY_REFINE = """Your job is to produce a final summary.
We have provided an existing detailed summary up to a certain point:  $refined_summary

We have the opportunity to add additional information to the existing summary to get a prolonged summary (only if needed and relevant) with some more context below.\n
------------
$chunk_summary
------------
Given the new context, extend the original summary if necessary and if it relates to the overall topic below.
------
$initial_summary
------
If the context isn't useful or does not add valuable points to the overall topic, return the original summary. Never remove details, only add more from the given context. 

Please ensure your summary adheres to the following detailed requirements:

Factual Accuracy: The summary must be factually correct. Do not include any imagined information or assumptions. Only include details that are explicitly mentioned in the forum posts.

No Repetitions: Avoid repeating the same information. Each piece of information should be unique and add value to the summary.

Contextual Information Only: Use only the information provided in the context of the forum posts. Do not incorporate any external knowledge or data that is not part of the forum discussion.

Reader Engagement: Structure the summary in a way that enables the reader to easily understand and participate in the ongoing discussion. The reader should be able to follow the main points and contribute meaningfully to the conversation.

Balance of Opinions: Clearly indicate where the balance of opinions landed both during and after the discussion. Highlight the consensus or predominant viewpoints that emerged as well as any significant minority opinions.

Topic-Focused: Focus on summarizing the content of the discussion rather than listing the topics that were mentioned. Provide insights into what was actually discussed about each topic.

Avoiding the Discussion Path: Do not describe the sequence or path of the discussion. Instead, focus on the key points and conclusions reached.

Paragraph Structure: Write one paragraph per topic discussed. Each paragraph should clearly cover a distinct topic or aspect of the discussion, providing a concise yet comprehensive overview.

Please apply this approach to the existing summaries provided, ensuring that your summary is clear, concise, and meets all the specified requirements."""

