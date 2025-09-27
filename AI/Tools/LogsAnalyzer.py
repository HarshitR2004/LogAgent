import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from Config.LLM import LLM

from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool



prompt_template_logs = ChatPromptTemplate.from_template("""
You are a DevOps root cause analysis expert specializing in log analysis. Analyze system logs to identify root causes of system issues:

Logs:
{logs}

Root Cause Analysis Tasks:
- Identify critical errors that could be causing system failures
- Trace error sequences and cascading failures in chronological order  
- Find patterns that indicate underlying system problems (not just symptoms)
- Detect resource exhaustion, timeout, or connectivity issues
- Identify configuration errors or missing dependencies
- Look for security-related failures or access issues

Root Cause Analysis Format:
- Error Timeline: <chronological sequence of critical errors>
- Root Cause Indicators: <underlying causes not just symptoms>
- System Impact: <how errors affect overall system health>
- Failure Patterns: <recurring issues that suggest systemic problems>
""")

@tool("analyze_logs", return_direct=False)
def analyze_logs(logs_file_path: str = None):
    """
    Analyze system logs and provide AI-powered insights on errors, warnings, and anomalies.
    
    Args:
        logs_file_path (str, optional): Path to the logs file. 
                                      Defaults to data/filteredLogs.txt
    
    Returns:
        str: Analysis of the logs including error patterns, root causes, and recommended fixes
    """
    # Handle None, empty string, or "{}" cases
    if logs_file_path is None or logs_file_path == "" or logs_file_path == "{}":
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        logs_file_path = os.path.join(project_root, "data", "filteredLogs.txt")
    
    try:
        with open(logs_file_path, "r", encoding='utf-8') as f:
            logs_content = f.read()
    except FileNotFoundError:
        return f"Error: Logs file not found at {logs_file_path}"
    except Exception as e:
        return f"Error reading logs file: {e}"
    
    if not logs_content.strip():
        return "Error: Logs file is empty or contains no readable content."
    
    try:
        llm_instance = LLM.get_instance()
        llm = llm_instance.get_model("gemini-2.5-flash")
        
        prompt = prompt_template_logs.format_prompt(logs=logs_content)
        
        response = llm.invoke(prompt.to_messages())
        return response.content
    except Exception as e:
        return f"Error during analysis: {e}"

if __name__ == "__main__":
    # Analyze logs from data/filteredLogs.txt
    # Use invoke method since function is decorated with @tool
    analysis = analyze_logs.invoke({})
    print("Analysis of Filtered Logs:")
    print(analysis)
    
    # Alternative: Analyze from specific file path
    # analysis = analyze_logs.invoke({"logs_file_path": "path/to/your/custom/logs.txt"})
    # print(analysis)
    