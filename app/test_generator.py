from app.generator import generate_answer

test_passages = [
    {
        "text": "DocMind is an agentic RAG research assistant that answers questions using uploaded documents.",
        "source": "test_document.txt",
        "page": 1,
    }
]

question = "What is DocMind?"

print("Testing NVIDIA Nemotron through OpenRouter...")

answer = generate_answer(question, test_passages)

print("\nGenerated answer:")
print(answer)
