import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from Config.LLM import LLM

from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool


prompt_template_commits = ChatPromptTemplate.from_template("""
You are a DevOps and root cause analysis expert. Analyze the following commits to identify potential root causes of system issues:

Commits:
{commits}

Root Cause Analysis Tasks:
- Identify commits that introduced breaking changes or system instability
- Look for patterns in code changes that could cause runtime failures
- Detect configuration changes that might impact system behavior
- Identify deployments or changes made around the time of incidents
- Find code patterns that could lead to performance issues or resource leaks

Root Cause Analysis Format:
- Timeline: <when changes occurred>
- Risk Factors: <changes that could cause issues>
- Correlation: <relationship to system problems>
- Technical Impact: <how changes affect system behavior>
""")

@tool("analyze_commits", return_direct=False)
def analyze_commits(commits_file_path: str = None):
    """
    Analyze commits from a JSON file and provide AI-powered insights on code changes, risks, and patterns.
    
    Args:
        commits_file_path (str, optional): Path to the commits JSON file. 
                                         Defaults to data/commit.json
    
    Returns:
        str: Analysis of the commits including risky changes, patterns, and optimization suggestions
    """
    if commits_file_path is None or commits_file_path == "" or commits_file_path == "{}":
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        commits_file_path = os.path.join(project_root, "data", "commit.json")
    
    try:
        with open(commits_file_path, "r", encoding='utf-8') as f:
            commits_content = f.read()
    except FileNotFoundError:
        return f"Error: Commits file not found at {commits_file_path}"
    except Exception as e:
        return f"Error reading commits file: {e}"
    
    if not commits_content.strip():
        return "Error: Commits file is empty or contains no readable content."
    
    try:
        llm_instance = LLM.get_instance()
        llm = llm_instance.get_model("gemini-2.5-flash")
        
        prompt = prompt_template_commits.format_prompt(commits=commits_content)
        
        response = llm.invoke(prompt.to_messages())
        return response.content
    except Exception as e:
        return f"Error during analysis: {e}"

if __name__ == "__main__":
    # Analyze commits from data/commit.json
    # Use invoke method since function is decorated with @tool
    analysis = analyze_commits.invoke({})
    print("Analysis of Commits:")
    print(analysis)
    
    # Alternative: Analyze from specific file path
    # analysis = analyze_commits.invoke({"commits_file_path": "path/to/your/custom/commits.json"})
    # print(analysis)

    