import os
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

if __name__ == "__main__":

    content = "New Delhi serves as the capital city of India for several historical, political, and strategic reasons:\n\n1. **Historical Context**: The decision to establish New Delhi as the capital was made during the British colonial period. In 1911, the British government announced the move of the capital from Calcutta (now Kolkata) to Delhi, partly to symbolize their power and to have a more centrally located capital in the northern part of India.\n\n2. **Geographical Advantage**: Delhi's location is strategically advantageous as it is situated in the northern part of India, making it accessible from various regions of the country. This central location facilitates better governance and administration across the diverse states of India.\n\n3. **Architectural Planning**: New Delhi was designed by British architects Edwin Lutyens and Herbert Baker, who envisioned a grand city that would reflect the power of the British Empire. The city features wide boulevards, impressive government buildings, and green spaces, which contribute to its status as the capital.\n\n4. **Political Significance**: After India gained independence in 1947, New Delhi continued to serve as the capital. It houses important government institutions, including the President's residence (Rashtrapati Bhavan), Parliament House, and the Supreme Court, making it the political hub of the country.\n\n5. **Symbol of Unity**: As the capital, New Delhi represents the unity and diversity of India. It is a melting pot of cultures, languages, and traditions, reflecting the country's pluralistic society.\n\nOverall, New Delhi's historical significance, strategic location, and role in governance have solidified its status as the capital of India."
    try:
        msgs = [
            AIMessage(content='LLM stands for "Large Language Model" in the context of artificial intelligence. These models are designed to understand and generate human language by training on vast amounts of text data. LLMs use deep learning techniques, particularly neural networks, to process and generate text, allowing them to perform a variety of tasks such as translation, summarization, question answering, and conversational agents.\n\nSome well-known examples of LLMs include OpenAI\'s GPT (Generative Pre-trained Transformer) models, Google\'s BERT (Bidirectional Encoder Representations from Transformers), and others. These models are characterized by their large size (hence "large" in LLM), which typically refers to the number of parameters they contain, enabling them to capture complex patterns in language.'),
            HumanMessage(content="You are summarisation assistant. Please summarise the above text in one sentence."),
            # HumanMessage(content='Please summarise the conversation text in one sentence: '),
        ]
        
        test_llm = ChatGroq(
            model="llama-3.1-8b-instant", 
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        print("Groq Test Success:", test_llm.invoke(msgs).content)
    except Exception as e:
        print("Groq Test Failed Error details:", e)
