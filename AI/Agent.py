from Tools.CommitsAnalyzer import analyze_commits
from Tools.LogsAnalyzer import analyze_logs
from Tools.MetricsAnalyzer import analyze_metrics

from Config.LLM import LLM

class Agent:
    def __init__(self):
        """Initialize the AI Agent with analysis tools and LLM"""
        self.tools = [analyze_logs, analyze_metrics, analyze_commits]
        
        llm_instance = LLM.get_instance()
        self.llm = llm_instance.get_model("gemini-2.5-flash")
    
    def invoke(self):
        """
        Invoke each tool sequentially and then perform final analysis
        
        Returns:
            dict: Analysis results from the agent
        """
        results = {}
        
        try:
            # Execute each tool exactly once
            print("Step 1: Analyzing logs...")
            logs_result = analyze_logs.invoke({"query": "Analyze system logs for errors and issues"})
            results["logs_analysis"] = logs_result
            
            print("Step 2: Analyzing metrics...")
            metrics_result = analyze_metrics.invoke({"query": "Analyze performance metrics for bottlenecks"})
            results["metrics_analysis"] = metrics_result
            
            print("Step 3: Analyzing commits...")
            commits_result = analyze_commits.invoke({"query": "Analyze recent commits for potential issues"})
            results["commits_analysis"] = commits_result
            
            # Now use LLM for final consolidated analysis
            print("Step 4: Performing root cause analysis...")
            final_analysis_prompt = f"""
            Based on the following analysis results from each tool, provide a comprehensive ROOT CAUSE ANALYSIS:

            LOGS ANALYSIS:
            {logs_result}

            METRICS ANALYSIS:
            {metrics_result}

            COMMITS ANALYSIS:
            {commits_result}

            Provide a consolidated ROOT CAUSE ANALYSIS focusing on:
            1. Primary root cause identification
            2. Contributing factors from each data source
            3. Timeline correlation between commits, metrics, and logs
            4. Evidence-based causality chain

            DO NOT provide suggestions or recommendations. Focus ONLY on identifying and analyzing root causes.
            """
            
            final_result = self.llm.invoke(final_analysis_prompt)
            results["root_cause_analysis"] = final_result.content if hasattr(final_result, 'content') else str(final_result)
            
            return {
                "input": "Root cause analysis completed",
                "output": results["root_cause_analysis"],
                "intermediate_steps": [
                    ("analyze_logs", logs_result),
                    ("analyze_metrics", metrics_result),
                    ("analyze_commits", commits_result)
                ]
            }
            
        except Exception as e:
            print(f"Agent execution error: {e}")
            return {"error": str(e), "partial_results": results}

# Create a global instance for backward compatibility
agent = Agent()

if __name__ == "__main__":
    # Test the Agent class
    agent_instance = Agent()
    result = agent_instance.invoke()
    print("Agent Output:\n", result)