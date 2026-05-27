import os
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

if __name__ == "__main__":

    content = "New Delhi serves as the capital city of India for several historical, political, and strategic reasons:\n\n1. **Historical Context**: The decision to establish New Delhi as the capital was made during the British colonial period. In 1911, the British government announced the move of the capital from Calcutta (now Kolkata) to Delhi, partly to symbolize their power and to have a more centrally located capital in the northern part of India.\n\n2. **Geographical Advantage**: Delhi's location is strategically advantageous as it is situated in the northern part of India, making it accessible from various regions of the country. This central location facilitates better governance and administration across the diverse states of India.\n\n3. **Architectural Planning**: New Delhi was designed by British architects Edwin Lutyens and Herbert Baker, who envisioned a grand city that would reflect the power of the British Empire. The city features wide boulevards, impressive government buildings, and green spaces, which contribute to its status as the capital.\n\n4. **Political Significance**: After India gained independence in 1947, New Delhi continued to serve as the capital. It houses important government institutions, including the President's residence (Rashtrapati Bhavan), Parliament House, and the Supreme Court, making it the political hub of the country.\n\n5. **Symbol of Unity**: As the capital, New Delhi represents the unity and diversity of India. It is a melting pot of cultures, languages, and traditions, reflecting the country's pluralistic society.\n\nOverall, New Delhi's historical significance, strategic location, and role in governance have solidified its status as the capital of India."
    try:
        msgs = [
            SystemMessage(content="You are summarisation assistant. Summarise the input in 1 sentence"),
            HumanMessage(content=content),
        ]
        test_llm = ChatGroq(
            model="llama-3.1-8b-instant", 
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        print("Groq Test Success:", test_llm.invoke(msgs).content)
    except Exception as e:
        print("Groq Test Failed Error details:", e)
