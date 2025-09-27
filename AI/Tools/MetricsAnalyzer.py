import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from Config.LLM import LLM

from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool


prompt_template = ChatPromptTemplate.from_template("""
You are a DevOps root cause analysis expert specializing in performance metrics. Analyze system metrics to identify root causes of performance issues:

Metrics:
{metrics}

Root Cause Analysis Tasks:
- Identify performance degradations that correlate with system incidents
- Detect resource exhaustion patterns (CPU, memory, disk, network)
- Find anomalous spikes or drops that indicate system stress or failures
- Identify capacity limits being reached that could cause system instability
- Detect gradual resource leaks or performance degradation trends
- Look for correlations between different metrics that suggest underlying issues

Root Cause Analysis Format:
- Performance Anomalies: <unusual patterns that indicate problems>
- Resource Constraints: <limits being reached that could cause failures>
- Trend Analysis: <performance degradation over time>
- Correlation Indicators: <relationships between metrics suggesting root causes>
""")

@tool("analyze_metrics", return_direct=False)
def analyze_metrics(metrics_file_path: str = None):
    """
    Analyze system performance metrics and provide AI-powered insights on performance trends and issues.
    
    Args:
        metrics_file_path (str, optional): Path to the metrics file. 
                                         Defaults to data/metrics.txt
    
    Returns:
        str: Analysis of the metrics including performance trends, anomalies, and optimization recommendations
    """
    # Handle None, empty string, or "{}" cases
    if metrics_file_path is None or metrics_file_path == "" or metrics_file_path == "{}":
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        metrics_file_path = os.path.join(project_root, "data", "metrics.txt")
    
    try:
        with open(metrics_file_path, "r", encoding='utf-8') as f:
            metrics_content = f.read()
    except FileNotFoundError:
        return f"Error: Metrics file not found at {metrics_file_path}"
    except Exception as e:
        return f"Error reading metrics file: {e}"
    
    if not metrics_content.strip():
        return "Error: Metrics file is empty or contains no readable content."
    
    llm_instance = LLM.get_instance()
    llm = llm_instance.get_model("gemini-2.5-flash")
    
    prompt = prompt_template.format_prompt(metrics=metrics_content)
    
    try:
        response = llm.invoke(prompt.to_messages())
        return response.content
    except Exception as e:
        return f"Error during analysis: {e}"
    
    
if __name__ == "__main__":
    # Analyze metrics from data/metrics.txt
    # Use invoke method since function is decorated with @tool
    analysis = analyze_metrics.invoke({})
    print("Analysis of Metrics:")
    print(analysis)
    
    # Alternative: Analyze from specific file path
    # analysis = analyze_metrics.invoke({"metrics_file_path": "path/to/your/custom/metrics.txt"})
    # print(analysis)
