"""
Task agent - Eisenhower matrix and scheduling
Q2 (important not urgent) is where the magic happens
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv
import vertexai
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

load_dotenv()

vertexai.init(
    project=os.getenv('GOOGLE_CLOUD_PROJECT'),
    location=os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
)

import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from tools.task_management_tools import (
    categorize_task_eisenhower,
    calculate_deadline_urgency,
    check_task_dependencies,
    suggest_task_schedule,
    batch_process_tasks
)


def create_task_management_agent():
    """Setup task agent with Eisenhower matrix"""
    
    agent = LlmAgent(
        model=Gemini(model="gemini-2.5-flash-lite"),
        name="task_management_agent",
        description="Task prioritization using Eisenhower Matrix",
        instruction="""
        Manage tasks for busy executives. Use Eisenhower Matrix to prioritize.
        
        Process:
        1. Categorize (use categorize_task_eisenhower)
           - Q1: Urgent + Important -> Do now
           - Q2: Important not urgent -> Schedule (this is gold)
           - Q3: Urgent not important -> Delegate
           - Q4: Neither -> Drop it
        
        2. Score urgency (use calculate_deadline_urgency)
           - 10: Today/overdue
           - 8-9: Tomorrow
           - 6-7: This week
           - 3-5: Next week
           - 0-2: Later
        
        3. Check dependencies (use check_task_dependencies)
           - What's blocked?
           - What blocks others?
        
        4. Schedule smart (use suggest_task_schedule)
           - Q1: Next available slot
           - Q2: Protected time blocks
           - Q3: Batch with similar tasks
           - Q4: Never
        
        5. Batch process (use batch_process_tasks for multiple)
        
        Output format:
        Task: [name]
        Quadrant: [Q1/Q2/Q3/Q4]
        Priority: [score/10]
        Deadline: [date or none]
        Dependencies: [list or none]
        Schedule: [when to do it]
        Reasoning: [1 line why]
        
        Rules:
        - Protect Q2 time (strategic work)
        - Don't let Q3 hijack the day
        - Be ruthless about Q4
        - If everything is Q1, nothing is
        """,
        tools=[
            categorize_task_eisenhower,
            calculate_deadline_urgency,
            check_task_dependencies,
            suggest_task_schedule,
            batch_process_tasks
        ]
    )
    
    return agent


def prioritize_tasks(task_list: List[Dict], calendar_context: Optional[Dict] = None) -> Dict:
    """
    Prioritize a list of tasks
    
    Args:
        task_list: List of tasks with name, deadline, description
        calendar_context: Optional calendar info for scheduling
        
    Returns:
        Prioritized task list with quadrants and schedule
    """
    
    agent = create_task_management_agent()
    
    # format tasks
    task_summary = f"Prioritize {len(task_list)} tasks:\n\n"
    for i, task in enumerate(task_list, 1):
        task_summary += f"{i}. {task.get('name', 'Unnamed')}\n"
        if task.get('deadline'):
            task_summary += f"   Deadline: {task['deadline']}\n"
        if task.get('description'):
            task_summary += f"   Details: {task['description']}\n"
        task_summary += "\n"
    
    query = f"""{task_summary}
    
    Analyze each task:
    1. Categorize into Eisenhower quadrant
    2. Calculate urgency score
    3. Check dependencies
    4. Suggest optimal schedule
    
    Use batch_process_tasks for efficiency.
    
    Return prioritized list with clear actions.
    """
    
    if calendar_context:
        query += f"\n\nCalendar context: {calendar_context}"
    
    # let agent work
    response = agent.invoke(query)
    
    return {
        "prioritized_tasks": response,
        "task_count": len(task_list),
        "analysis_timestamp": datetime.now().isoformat()
    }


def process_email_tasks(email_action_items: List[Dict]) -> Dict:
    """
    Process action items from email agent
    
    Quick triage for email-extracted tasks
    """
    
    agent = create_task_management_agent()
    
    # quick format
    task_summary = "Tasks from email:\n"
    for item in email_action_items:
        task_summary += f"- {item.get('task', 'Unknown')}"
        if item.get('deadline'):
            task_summary += f" (due: {item['deadline']})"
        task_summary += "\n"
    
    query = f"""{task_summary}
    
    Quick prioritization:
    1. Batch process all tasks
    2. Focus on Q1 and Q2 only
    3. Suggest immediate actions
    """
    
    response = agent.invoke(query)
    
    return {
        "processed_tasks": response,
        "email_task_count": len(email_action_items),
        "processing_time": datetime.now().isoformat()
    }


def get_daily_priorities(all_tasks: List[Dict], max_tasks: int = 5) -> Dict:
    """
    Get top priorities for today
    
    Returns max 5 tasks to focus on
    """
    
    agent = create_task_management_agent()
    
    query = f"""From these {len(all_tasks)} tasks, identify the TOP {max_tasks} for today.
    
    Selection criteria:
    1. All Q1 tasks (urgent + important)
    2. High-value Q2 tasks if time allows
    3. Nothing from Q3/Q4 unless critical
    
    Tasks: {all_tasks}
    
    Return:
    - Top {max_tasks} tasks with timing
    - Brief reasoning
    - Suggested order
    """
    
    response = agent.invoke(query)
    
    return {
        "daily_priorities": response,
        "total_tasks": len(all_tasks),
        "selected_count": max_tasks,
        "date": datetime.now().strftime("%Y-%m-%d")
    }


def analyze_task_load(tasks: List[Dict]) -> Dict:
    """
    Analyze overall task load and health
    
    Are we in firefighting mode or strategic?
    """
    
    # quick analysis without agent
    q1_count = 0
    q2_count = 0
    q3_count = 0
    q4_count = 0
    
    # rough categorization
    for task in tasks:
        desc = str(task).lower()
        if "urgent" in desc and "important" in desc:
            q1_count += 1
        elif "important" in desc and "urgent" not in desc:
            q2_count += 1
        elif "urgent" in desc:
            q3_count += 1
        else:
            q4_count += 1
    
    total = len(tasks)
    
    # health check
    if q1_count > total * 0.5:
        health = "CRISIS MODE - Too many urgent/important tasks"
        recommendation = "Block time to reduce Q1 backlog"
    elif q2_count > total * 0.3:
        health = "HEALTHY - Good focus on strategic work"
        recommendation = "Maintain Q2 focus"
    elif q3_count > total * 0.4:
        health = "REACTIVE - Too many urgent but unimportant"
        recommendation = "Delegate or batch Q3 tasks"
    else:
        health = "UNFOCUSED - Mixed priorities"
        recommendation = "Reassess task importance"
    
    return {
        "task_distribution": {
            "Q1_urgent_important": q1_count,
            "Q2_important_not_urgent": q2_count,
            "Q3_urgent_not_important": q3_count,
            "Q4_neither": q4_count
        },
        "total_tasks": total,
        "health_status": health,
        "recommendation": recommendation,
        "q2_percentage": round((q2_count / total * 100) if total > 0 else 0, 1)
    }


if __name__ == "__main__":
    print("Task Management Agent Test")
    print("-" * 40)
    
    # test tasks
    test_tasks = [
        {
            "name": "Finish Q4 budget presentation",
            "deadline": "today",
            "description": "Board meeting tomorrow"
        },
        {
            "name": "Review team performance",
            "deadline": "next week",
            "description": "Quarterly reviews"
        },
        {
            "name": "Reply to client escalation",
            "deadline": "today",
            "description": "Angry about delays"
        },
        {
            "name": "Plan 2025 strategy",
            "deadline": "next month",
            "description": "Strategic planning"
        },
        {
            "name": "Attend optional webinar",
            "deadline": "tomorrow",
            "description": "Industry trends"
        }
    ]
    
    print(f"Testing with {len(test_tasks)} tasks\n")
    
    # quick analysis
    analysis = analyze_task_load(test_tasks)
    print(f"Task health: {analysis['health_status']}")
    print(f"Q2 focus: {analysis['q2_percentage']}%")
    print(f"Recommendation: {analysis['recommendation']}\n")
    
    # prioritize
    try:
        agent = create_task_management_agent()
        print("Agent ready")
        
        result = prioritize_tasks(test_tasks)
        print("\nPrioritized tasks:")
        print(result['prioritized_tasks'])
        
    except Exception as e:
        print(f"Error: {e}")
        print("Using fallback analysis")
