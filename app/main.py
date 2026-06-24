from app.graph.graph import app

def ask(question):

    result = app.invoke({
        "question": question
    })

    return result.get("final_answer", "No answer generated")


while True:
    q = input("\nAsk your question (type 'exit'): ")

    if q.lower() == "exit":
        break

    print("\n", ask(q))