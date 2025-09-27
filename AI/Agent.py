from langchain.agents import initialize_agent, AgentType

from Tools.CommitsAnalyzer import analyze_commits
from Tools.LogsAnalyzer import analyze_logs
from Tools.MetricsAnalyzer import analyze_metrics
from Tools.PastEventsAnalyzer import analyze_past_events

from Config.LLM import LLM

class Agent:
    def __init__(self):
        """Initialize the AI Agent with analysis tools and LLM"""
        self.tools = [analyze_logs, analyze_metrics, analyze_commits, analyze_past_events]
        
        llm_instance = LLM.get_instance()
        self.llm = llm_instance.get_model("gemini-2.5-flash")
        
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            max_iterations=15,
            early_stopping_method="generate"
        )
        
        self.task = """
        You MUST perform comprehensive root cause analysis by using ALL 4 available analysis tools in sequence:

        1. MANDATORY: Use analyze_logs tool to identify error patterns and system issues
        2. MANDATORY: Use analyze_metrics tool to identify performance bottlenecks and resource issues  
        3. MANDATORY: Use analyze_commits tool to identify code changes that may have caused issues
        4. MANDATORY: Use analyze_past_events tool with "root cause analysis" as input to find similar historical incidents

        After using ALL 4 tools, provide a consolidated ROOT CAUSE ANALYSIS focusing on:
        1. Primary root cause identification
        2. Contributing factors from each data source
        3. Timeline correlation between commits, metrics, and logs
        4. Evidence-based causality chain

        DO NOT provide suggestions or recommendations. Focus ONLY on identifying and analyzing root causes.
        DO NOT STOP until you have used all 4 tools and provided the root cause analysis.
        """
    
    def invoke(self, custom_task=None):
        """
        Invoke the AI Agent to perform analysis
        
        Args:
            custom_task (str, optional): Custom task to override default task
        
        Returns:
            dict: Analysis results from the agent
        """
        task_to_run = custom_task if custom_task else self.task
        return self.agent.invoke({"input": task_to_run})

# Create a global instance for backward compatibility
agent = Agent()

if __name__ == "__main__":
    # Test the Agent class
    agent_instance = Agent()
    result = agent_instance.invoke()
    print("Agent Output:\n", result)