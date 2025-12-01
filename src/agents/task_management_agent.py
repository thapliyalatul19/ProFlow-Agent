"""
Task Management Agent for ProFlow
Author: Atul Thapliyal
Created: Nov 17, 2024

Manages tasks with priority matrix (Eisenhower), deadline tracking, dependency 
management, and integration with email/calendar agents.

Features:
- Eisenhower Matrix (Urgent/Important quadrants)
- Deadline proximity scoring
- Task dependencies and blocking
- Integration with email action items
- Calendar-aware scheduling
- Executive focus optimization
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
    """
    Create Task Management Agent with Eisenhower Matrix and smart scheduling.
    
    Core Capabilities:
    - Eisenhower Matrix categorization (4 quadrants)
    - Deadline urgency scoring (0-10 scale)
    - Dependency tracking and blocking detection
    - Calendar-aware task scheduling
    - Batch processing for email-extracted tasks
    
    Integration Points:
    - Receives action items from Email Agent
    - Requests calendar slots from Calendar Agent
    - Provides task status to Orchestrator
    """
    
    agent = LlmAgent(
        model=Gemini(model="gemini-2.5-flash-lite"),
        name="task_management_agent",
        description="Executive task prioritization using Eisenhower Matrix and deadline tracking",
        instruction="""
        You manage tasks for busy executives using the Eisenhower Matrix framework.
        Be strategic, data-driven, and respect executive time.
        
        TASK ANALYSIS PROCESS:
        
        1. EISENHOWER CATEGORIZATION (use categorize_task_eisenhower tool)
           Assess both urgency and importance to place tasks in quadrants:
           
           Q1 (DO FIRST): Urgent + Important
           - Crises, deadlines, emergencies
           - Action: Schedule immediately
           
           Q2 (SCHEDULE): Not Urgent + Important  
           - Strategic work, planning, development
           - Action: Block calendar time
           - NOTE: This is where executives create value!
           
           Q3 (DELEGATE): Urgent + Not Important
           - Interruptions, some emails/calls
           - Action: Delegate or minimize
           
           Q4 (ELIMINATE): Not Urgent + Not Important
           - Busywork, time wasters
           - Action: Defer or eliminate
        
        2. DEADLINE URGENCY (use calculate_deadline_urgency tool)
           Score 0-10 based on deadline proximity:
           - 10: Today/overdue
           - 8-9: Tomorrow
           - 6-7: This week
           - 3-5: Next week
           - 0-2: 2+ weeks away
           
           Factor in: deadline type (hard vs soft), consequences, dependencies
        
        3. DEPENDENCIES (use check_task_dependencies tool)
           - Identify blockers and prerequisites
           - Map task chains (A → B → C)
           - Flag critical path items
           - Warn about bottlenecks
        
        4. SCHEDULING (use suggest_task_schedule tool)
           - Match task requirements to calendar availability
           - Deep work → morning focus blocks
           - Quick tasks → meeting buffers
           - Meetings → afternoon slots
           - Consider energy levels and context switching
        
        5. BATCH PROCESSING (use batch_process_tasks tool)
           - Process multiple tasks from emails efficiently
           - Group similar tasks together
           - Identify quick wins vs. major projects
        
        TASK PRIORITIZATION LOGIC:
        
        Priority Score = (Importance × 2) + Urgency + (Deadline Score) + (Dependency Multiplier)
        
        Decision Framework:
        - Q1 tasks: Do immediately or within 4 hours
        - Q2 tasks: Schedule specific blocks (don't let Q1 crowd these out!)
        - Q3 tasks: Delegate with clear handoff
        - Q4 tasks: Be honest - eliminate or defer indefinitely
        
        RESPONSE FORMAT:
        
        Task: [title]
        Quadrant: [Q1/Q2/Q3/Q4] - [DO FIRST/SCHEDULE/DELEGATE/ELIMINATE]
        Priority Score: [0-100]
        Urgency: [X/10]
        Importance: [X/10]
        Deadline: [date/time] (in X days)
        
        Dependencies:
        - Blocked by: [task(s)]
        - Blocks: [task(s)]
        - On critical path: [Yes/No]
        
        Recommendation:
        [Specific action - when to do it, how long it needs, any delegation]
        
        Scheduling Suggestion:
        - Best time: [morning/afternoon/specific slot]
        - Duration needed: [X min]
        - Calendar block: [suggested time]
        
        Rationale:
        [Brief explanation of priority and timing]
        
        SPECIAL RULES:
        
        1. PROTECT Q2 TIME:
           - Q2 is where executives build the future
           - If calendar has no Q2 blocks, FLAG THIS
           - Suggest specific times for strategic work
        
        2. DELEGATION CLARITY:
           - For Q3, name specific team members if known
           - Provide clear success criteria
           - Set follow-up checkpoints
        
        3. DEADLINE REALISM:
           - If deadline seems impossible, say so
           - Suggest renegotiation or resource addition
           - Don't just accept unrealistic timelines
        
        4. BATCH SIMILAR TASKS:
           - Group emails, calls, approvals
           - Reduce context switching
           - Suggest specific batching times
        
        5. ENERGY MANAGEMENT:
           - Deep work (Q2) → high energy times
           - Administrative (Q3/Q4) → low energy times
           - Don't schedule hard thinking after 4pm
        
        6. INTEGRATION WITH OTHER AGENTS:
           - Email agent provides action items → you prioritize
           - Calendar agent provides slots → you recommend scheduling
           - You provide status → orchestrator coordinates
        
        COMMUNICATION STYLE:
        - Direct and actionable
        - Use data (scores, timelines)
        - Be honest about what's realistic
        - Push back on poor prioritization
        - Protect the executive's strategic time
        
        When you detect tasks that are:
        - All Q1 (crisis mode) → Flag "Need better planning"
        - No Q2 (reactive mode) → Flag "Not building future value"
        - Lots of Q3 (delegation needed) → Suggest team expansion
        - Any Q4 taking time → Challenge necessity
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


def quick_prioritize_task(
    task_title: str,
    task_description: str,
    deadline: Optional[str] = None,
    importance_hints: Optional[List[str]] = None
) -> Dict:
    """
    Quick task prioritization for single task analysis.
    
    Args:
        task_title: Short task name
        task_description: Detailed description
        deadline: ISO format date/time or relative (e.g., "tomorrow")
        importance_hints: Factors indicating importance (e.g., ["CEO request", "revenue impact"])
    
    Returns:
        Dict with quadrant, priority score, and recommendations
    """
    agent = create_task_management_agent()
    
    query = f"""
    Analyze this task:
    
    Title: {task_title}
    Description: {task_description}
    Deadline: {deadline if deadline else "Not specified"}
    Importance Signals: {', '.join(importance_hints) if importance_hints else "None provided"}
    
    Provide:
    1. Eisenhower quadrant
    2. Priority score
    3. Scheduling recommendation
    4. Any dependencies to watch for
    """
    
    response = agent.generate_content(query)
    return response


def process_email_action_items(action_items: List[Dict]) -> List[Dict]:
    """
    Batch process action items extracted from emails.
    
    Args:
        action_items: List of tasks from email agent with format:
            {
                'task': str,
                'deadline': str,
                'source_email': str,
                'sender': str,
                'urgency_signals': List[str]
            }
    
    Returns:
        List of prioritized tasks with quadrants and scheduling
    """
    agent = create_task_management_agent()
    
    # Format tasks for batch processing
    tasks_summary = f"Processing {len(action_items)} action items from emails:\n\n"
    for idx, item in enumerate(action_items, 1):
        tasks_summary += f"{idx}. {item['task']}\n"
        tasks_summary += f"   Deadline: {item.get('deadline', 'None')}\n"
        tasks_summary += f"   From: {item['sender']}\n"
        if item.get('urgency_signals'):
            tasks_summary += f"   Signals: {', '.join(item['urgency_signals'])}\n"
        tasks_summary += "\n"
    
    query = f"""{tasks_summary}
    
    Use batch_process_tasks to efficiently categorize all of these.
    
    For each task, provide:
    - Quadrant (Q1/Q2/Q3/Q4)
    - Priority score
    - When to tackle it
    - Quick wins vs. time-intensive work
    
    Then give an executive summary:
    - How many in each quadrant
    - Recommended order of execution
    - Any items to delegate immediately
    - Total estimated time needed
    """
    
    response = agent.generate_content(query)
    return response


def check_calendar_task_fit(
    tasks: List[Dict],
    available_calendar_slots: List[Dict]
) -> Dict:
    """
    Match tasks to calendar availability using smart scheduling.
    
    Args:
        tasks: List of prioritized tasks with time estimates
        available_calendar_slots: Free time blocks from calendar agent
    
    Returns:
        Scheduling plan with task-to-slot mapping
    """
    agent = create_task_management_agent()
    
    tasks_summary = "\n".join([
        f"- {t['title']} (Q{t['quadrant']}, {t['estimated_duration']}min)"
        for t in tasks
    ])
    
    slots_summary = "\n".join([
        f"- {s['start']} to {s['end']} ({s['duration']}min)"
        for s in available_calendar_slots
    ])
    
    query = f"""
    Tasks to schedule:
    {tasks_summary}
    
    Available calendar slots:
    {slots_summary}
    
    Use suggest_task_schedule to create optimal task-to-calendar mapping.
    
    Consider:
    - Q1 tasks need immediate slots
    - Q2 deep work needs 90+ min blocks
    - Morning slots for high-focus work
    - Afternoon for lighter tasks
    - Buffer time between different task types
    
    Provide a specific scheduling plan.
    """
    
    response = agent.generate_content(query)
    return response


# Test and demonstration
if __name__ == "__main__":
    print("=" * 70)
    print("Task Management Agent - Eisenhower Matrix + Smart Scheduling")
    print("=" * 70)
    
    agent = create_task_management_agent()
    
    print("\n✅ Agent initialized with capabilities:")
    print("   - Eisenhower Matrix categorization")
    print("   - Deadline urgency scoring (0-10)")
    print("   - Dependency tracking")
    print("   - Calendar-aware scheduling")
    print("   - Batch email task processing")
    print(f"\n   Tools loaded: {len(agent.tools)}")
    print("   Model: gemini-2.5-flash-lite")
    
    # Demo: Single task analysis
    print("\n" + "=" * 70)
    print("DEMO: Analyzing a single task")
    print("=" * 70)
    
    demo_task = {
        'title': 'Prepare Q4 Board Presentation',
        'description': 'Create comprehensive slide deck covering financials, strategy, and team updates for board meeting',
        'deadline': '2024-11-25 09:00',
        'importance_hints': ['CEO request', 'board meeting', 'strategic decision']
    }
    
    print(f"\nTask: {demo_task['title']}")
    print(f"Deadline: {demo_task['deadline']}")
    print(f"Importance: {', '.join(demo_task['importance_hints'])}")
    print("\nAnalyzing...")
    
    # Note: Actual execution would call the agent
    print("\n[Would analyze and categorize into Eisenhower quadrant]")
    print("[Would calculate priority score and scheduling recommendation]")
    
    print("\n" + "=" * 70)
    print("Ready for integration with Email and Calendar agents! 🚀")
    print("=" * 70)
