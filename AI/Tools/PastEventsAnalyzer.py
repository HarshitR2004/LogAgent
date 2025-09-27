import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from Config.VectorStore import VectorStore
from Config.LLM import LLM

from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool


prompt_template = ChatPromptTemplate.from_template(
    "You are a DevOps root cause analysis expert specializing in historical incident analysis. "
    "Use past incidents to identify root causes and patterns for current system issues.\n\n"
    "Your task is to perform root cause analysis based on historical data:\n\n"
    "Root Cause Analysis Tasks:\n"
    "1. Identify recurring root causes across similar past incidents\n"
    "2. Find patterns in how incidents escalated and what initially triggered them\n"
    "3. Extract proven root causes from past incident resolutions\n"
    "4. Identify system weaknesses that repeatedly cause problems\n"
    "5. Look for environmental or configuration factors that led to past failures\n\n"
    "Historical Incidents Summary:\n{events}\n\n"
    "Root Cause Analysis Format:\n"
    "- Historical Root Causes: <proven causes from past incidents>\n"
    "- Recurring Patterns: <systemic issues that keep occurring>\n"
    "- Trigger Conditions: <what initially caused past incidents>\n"
    "- System Vulnerabilities: <weak points identified from history>\n"
)

@tool("analyze_events", return_direct=False)
def analyze_past_events(event: str):
    """
    Analyze past events using RAG (Retrieval-Augmented Generation) to find similar incidents and solutions.
    
    Args:
        event (str): Description of the current event to analyze
    
    Returns:
        str: Analysis including similar past events, root causes, and recommended solutions
    """
    # Use default values for collection_name and model_name
    collection_name = "devops_incidents_demo"
    model_name = "all-MiniLM-L6-v2"
    
    vector_store = VectorStore.get_instance().get_collection(collection_name, model_name)
    llm_instance = LLM.get_instance()
    llm = llm_instance.get_model("gemini-2.5-flash")
    
    relevant_docs = vector_store.similarity_search(event, k=3)
    
    context = "\n".join([doc.page_content for doc in relevant_docs])
    
    print(f"Context for analysis:\n{context}\n")
    if not context:
        return "No relevant past events found for analysis."
    
    prompt = prompt_template.format_prompt(events=context)
    
    try : 
        response = llm.invoke(prompt.to_messages())
        return response.content
    except Exception as e:
        return f"Error during analysis: {e}"




if __name__ == "__main__":
    test_event = "Frequent database connection timeouts during peak hours affecting user transactions."
    analysis = analyze_past_events.invoke({"event": test_event})
    print("Analysis of Past Events:")
    print(analysis)