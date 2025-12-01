"""
Task Management Tools for ProFlow
Author: Atul Thapliyal
Created: Nov 17, 2024

Tools for Eisenhower Matrix, deadline tracking, dependencies, and smart scheduling.
These tools support the Task Management Agent.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json


def categorize_task_eisenhower(
    task_description: str,
    urgency_score: int,
    importance_score: int,
    deadline: Optional[str] = None,
    sender_context: Optional[str] = None
) -> Dict:
    """
    Categorize task into Eisenhower Matrix quadrant.
    
    Eisenhower Matrix:
    - Q1 (Urgent + Important): DO FIRST - crises, deadlines
    - Q2 (Not Urgent + Important): SCHEDULE - strategic work, planning
    - Q3 (Urgent + Not Important): DELEGATE - interruptions, busywork
    - Q4 (Not Urgent + Not Important): ELIMINATE - time wasters
    
    Args:
        task_description: What needs to be done
        urgency_score: 0-10, how time-sensitive (deadlines, crisis)
        importance_score: 0-10, long-term impact and value
        deadline: ISO format or relative (e.g., "today", "Friday")
        sender_context: Who requested it (affects importance)
    
    Returns:
        Dict with quadrant, reasoning, and recommendation
        
    Examples:
        >>> categorize_task_eisenhower(
        ...     "Prepare board presentation",
        ...     urgency_score=8,
        ...     importance_score=10,
        ...     deadline="tomorrow 9am"
        ... )
        {'quadrant': 'Q1', 'action': 'DO FIRST', ...}
    """
    
    # Adjust scores based on context
    if deadline:
        deadline_urgency = _calculate_deadline_urgency_boost(deadline)
        urgency_score = min(10, urgency_score + deadline_urgency)
    
    if sender_context:
        importance_boost = _calculate_sender_importance(sender_context)
        importance_score = min(10, importance_score + importance_boost)
    
    # Determine quadrant (using 5 as threshold for high/low)
    is_urgent = urgency_score >= 5
    is_important = importance_score >= 5
    
    if is_urgent and is_important:
        quadrant = "Q1"
        action = "DO FIRST"
        recommendation = "Schedule immediately or within next 4 hours"
        priority_level = "CRITICAL"
        
    elif not is_urgent and is_important:
        quadrant = "Q2"
        action = "SCHEDULE"
        recommendation = "Block dedicated time on calendar - this creates long-term value"
        priority_level = "HIGH"
        
    elif is_urgent and not is_important:
        quadrant = "Q3"
        action = "DELEGATE"
        recommendation = "Delegate if possible, or batch with similar tasks"
        priority_level = "MEDIUM"
        
    else:  # not urgent and not important
        quadrant = "Q4"
        action = "ELIMINATE"
        recommendation = "Consider if this is necessary - defer or eliminate"
        priority_level = "LOW"
    
    return {
        'quadrant': quadrant,
        'action': action,
        'priority_level': priority_level,
        'urgency_score': urgency_score,
        'importance_score': importance_score,
        'recommendation': recommendation,
        'reasoning': _explain_quadrant_placement(
            quadrant, urgency_score, importance_score, deadline, sender_context
        )
    }


def calculate_deadline_urgency(
    deadline: str,
    task_type: str = "general",
    consequences: Optional[str] = None
) -> Dict:
    """
    Calculate urgency score (0-10) based on deadline proximity.
    
    Scoring:
    - 10: Overdue or due today
    - 8-9: Tomorrow
    - 6-7: This week (2-5 days)
    - 4-5: Next week (6-10 days)
    - 2-3: This month (11-20 days)
    - 0-1: More than 3 weeks
    
    Args:
        deadline: ISO format, relative ("today", "Friday"), or descriptive
        task_type: "hard_deadline", "soft_deadline", "milestone", "general"
        consequences: What happens if missed (increases urgency)
    
    Returns:
        Dict with urgency score, deadline info, and warnings
        
    Examples:
        >>> calculate_deadline_urgency("2024-11-18 17:00", task_type="hard_deadline")
        {'urgency_score': 9, 'hours_until_deadline': 25, ...}
    """
    
    # Parse deadline
    deadline_dt, is_relative = _parse_deadline(deadline)
    
    if not deadline_dt:
        return {
            'urgency_score': 3,  # Default moderate urgency without deadline
            'warning': 'No clear deadline specified',
            'recommendation': 'Set a specific deadline to properly prioritize'
        }
    
    # Calculate time until deadline
    now = datetime.now()
    time_until = deadline_dt - now
    hours_until = time_until.total_seconds() / 3600
    days_until = time_until.days
    
    # Base urgency score
    if hours_until <= 0:
        base_score = 10  # Overdue!
        status = "OVERDUE"
    elif hours_until <= 4:
        base_score = 10  # Today, very soon
        status = "URGENT - TODAY"
    elif hours_until <= 24:
        base_score = 9  # Rest of today or early tomorrow
        status = "URGENT - TOMORROW"
    elif days_until <= 2:
        base_score = 8  # Day after tomorrow
        status = "THIS WEEK"
    elif days_until <= 5:
        base_score = 7  # This week
        status = "THIS WEEK"
    elif days_until <= 10:
        base_score = 5  # Next week
        status = "NEXT WEEK"
    elif days_until <= 20:
        base_score = 3  # This month
        status = "THIS MONTH"
    else:
        base_score = 1  # Far out
        status = "FUTURE"
    
    # Adjust for task type
    if task_type == "hard_deadline":
        # Hard deadlines (regulatory, client commitments) = +2
        base_score = min(10, base_score + 2)
    elif task_type == "soft_deadline":
        # Soft deadlines (internal targets) = -1
        base_score = max(0, base_score - 1)
    
    # Adjust for consequences
    if consequences:
        consequences_lower = consequences.lower()
        if any(word in consequences_lower for word in ['revenue', 'client', 'legal', 'regulatory']):
            base_score = min(10, base_score + 2)
        elif any(word in consequences_lower for word in ['blocked', 'critical path', 'dependency']):
            base_score = min(10, base_score + 1)
    
    # Build response
    result = {
        'urgency_score': base_score,
        'status': status,
        'deadline': deadline_dt.isoformat(),
        'hours_until_deadline': round(hours_until, 1),
        'days_until_deadline': days_until,
        'is_overdue': hours_until <= 0,
        'task_type': task_type
    }
    
    # Add warnings
    if hours_until <= 0:
        result['warning'] = "⚠️ OVERDUE - immediate action required"
    elif hours_until <= 4:
        result['warning'] = "🔴 Due within 4 hours - drop everything else"
    elif hours_until <= 24:
        result['warning'] = "🟠 Due tomorrow - prioritize today"
    elif days_until <= 2:
        result['warning'] = "🟡 Due in 2 days - schedule time today"
    
    return result


def check_task_dependencies(
    task_id: str,
    task_title: str,
    all_tasks: List[Dict],
    dependency_map: Optional[Dict] = None
) -> Dict:
    """
    Check task dependencies, blockers, and critical path.
    
    Args:
        task_id: Unique identifier for this task
        task_title: Task description
        all_tasks: List of all tasks to check against
        dependency_map: Optional explicit dependencies {task_id: [dependency_ids]}
    
    Returns:
        Dict with blockers, dependents, critical path status
        
    Example:
        >>> check_task_dependencies(
        ...     "task_123",
        ...     "Deploy to production",
        ...     all_tasks=[{"id": "task_122", "title": "QA testing", ...}],
        ...     dependency_map={"task_123": ["task_122"]}
        ... )
    """
    
    blockers = []  # Tasks that must complete before this one
    blocks = []    # Tasks that need this one to complete
    critical_path = False
    
    # Check explicit dependencies
    if dependency_map and task_id in dependency_map:
        blocker_ids = dependency_map[task_id]
        blockers = [
            task for task in all_tasks 
            if task.get('id') in blocker_ids and not task.get('completed', False)
        ]
    
    # Find tasks this one blocks
    if dependency_map:
        for dependent_id, deps in dependency_map.items():
            if task_id in deps:
                dependent_task = next(
                    (t for t in all_tasks if t.get('id') == dependent_id),
                    None
                )
                if dependent_task:
                    blocks.append(dependent_task)
    
    # Detect critical path (heuristic: many dependencies or hard deadline)
    if len(blocks) >= 3:  # Blocks 3+ other tasks
        critical_path = True
    
    # Check for dependency keywords in task title
    dependency_keywords = {
        'blockers': ['after', 'once', 'requires', 'needs', 'depends on', 'waiting for'],
        'critical': ['launch', 'release', 'deploy', 'deadline', 'critical']
    }
    
    title_lower = task_title.lower()
    for keyword in dependency_keywords['critical']:
        if keyword in title_lower:
            critical_path = True
            break
    
    return {
        'has_blockers': len(blockers) > 0,
        'blocker_count': len(blockers),
        'blockers': [
            {'id': t.get('id'), 'title': t.get('title'), 'status': t.get('status')}
            for t in blockers
        ],
        'blocks_count': len(blocks),
        'blocks': [
            {'id': t.get('id'), 'title': t.get('title')}
            for t in blocks
        ],
        'on_critical_path': critical_path,
        'is_blocked': len(blockers) > 0,
        'recommendation': _generate_dependency_recommendation(
            blockers, blocks, critical_path
        )
    }


def suggest_task_schedule(
    task: Dict,
    available_slots: List[Dict],
    work_preferences: Optional[Dict] = None
) -> Dict:
    """
    Suggest optimal calendar slot for a task based on requirements and energy.
    
    Task Requirements:
    - Q1: Immediate, any available time
    - Q2: Deep work, needs 90+ min focused blocks, morning preferred
    - Q3: Quick tasks, can use buffers between meetings
    - Q4: Low priority, flexible timing
    
    Args:
        task: Dict with quadrant, estimated_duration, focus_level
        available_slots: List of free calendar blocks
        work_preferences: Optional preferences (focus_hours, break_times)
    
    Returns:
        Dict with recommended slot, reasoning, alternatives
        
    Example:
        >>> suggest_task_schedule(
        ...     {"quadrant": "Q2", "estimated_duration": 120, "title": "Strategic planning"},
        ...     [{"start": "09:00", "end": "11:00", "duration": 120}]
        ... )
    """
    
    if not work_preferences:
        work_preferences = {
            'focus_hours': ['09:00-12:00'],  # Morning for deep work
            'admin_hours': ['14:00-17:00'],  # Afternoon for lightweight tasks
            'no_deep_work_after': '16:00'    # Energy drops
        }
    
    quadrant = task.get('quadrant', 'Q3')
    duration = task.get('estimated_duration', 30)
    focus_level = task.get('focus_level', 'medium')  # low, medium, high
    
    # Filter slots by duration
    viable_slots = [s for s in available_slots if s['duration'] >= duration]
    
    if not viable_slots:
        return {
            'recommended_slot': None,
            'issue': 'No slots available with sufficient duration',
            'needed_duration': duration,
            'recommendation': 'Need to reschedule existing meetings or split task'
        }
    
    # Score each slot
    scored_slots = []
    for slot in viable_slots:
        score = _score_slot_for_task(slot, task, work_preferences)
        scored_slots.append({**slot, 'score': score})
    
    # Sort by score (highest first)
    scored_slots.sort(key=lambda x: x['score'], reverse=True)
    
    best_slot = scored_slots[0]
    alternatives = scored_slots[1:3] if len(scored_slots) > 1 else []
    
    return {
        'recommended_slot': {
            'start': best_slot['start'],
            'end': best_slot['end'],
            'duration': best_slot['duration']
        },
        'fit_score': best_slot['score'],
        'reasoning': _explain_slot_choice(best_slot, task, work_preferences),
        'alternatives': [
            {'start': s['start'], 'end': s['end'], 'score': s['score']}
            for s in alternatives
        ],
        'task_quadrant': quadrant,
        'estimated_duration': duration
    }


def batch_process_tasks(
    tasks: List[Dict],
    categorization_hints: Optional[Dict] = None
) -> Dict:
    """
    Efficiently process multiple tasks at once.
    
    Batch processing benefits:
    - Faster than processing one by one
    - Can identify patterns (all Q1 = crisis mode!)
    - Group similar tasks for context switching reduction
    - Calculate aggregate metrics
    
    Args:
        tasks: List of tasks with title, description, deadline, etc.
        categorization_hints: Optional scoring adjustments
    
    Returns:
        Dict with categorized tasks, summary stats, and recommendations
        
    Example:
        >>> batch_process_tasks([
        ...     {"title": "Review doc", "urgency": 3, "importance": 5},
        ...     {"title": "Client call", "urgency": 8, "importance": 9}
        ... ])
    """
    
    categorized = {
        'Q1': [],  # DO FIRST
        'Q2': [],  # SCHEDULE
        'Q3': [],  # DELEGATE
        'Q4': []   # ELIMINATE
    }
    
    total_time_needed = 0
    overdue_count = 0
    blocked_count = 0
    
    for task in tasks:
        # Categorize each task
        urgency = task.get('urgency_score', 5)
        importance = task.get('importance_score', 5)
        
        result = categorize_task_eisenhower(
            task_description=task.get('title', ''),
            urgency_score=urgency,
            importance_score=importance,
            deadline=task.get('deadline'),
            sender_context=task.get('sender')
        )
        
        quadrant = result['quadrant']
        categorized[quadrant].append({
            **task,
            'quadrant': quadrant,
            'priority_level': result['priority_level']
        })
        
        # Aggregate stats
        if task.get('estimated_duration'):
            total_time_needed += task['estimated_duration']
        
        if task.get('is_overdue'):
            overdue_count += 1
        
        if task.get('has_blockers'):
            blocked_count += 1
    
    # Calculate summary statistics
    total_tasks = len(tasks)
    quadrant_counts = {q: len(tasks) for q, tasks in categorized.items()}
    
    # Generate insights
    insights = []
    
    if quadrant_counts['Q1'] > total_tasks * 0.5:
        insights.append("⚠️ Crisis mode: Over 50% of tasks are urgent+important. Need better planning.")
    
    if quadrant_counts['Q2'] == 0:
        insights.append("🚨 No strategic work scheduled! You're being purely reactive.")
    elif quadrant_counts['Q2'] < total_tasks * 0.2:
        insights.append("⚠️ Very little strategic work (Q2). Make time for important but not urgent tasks.")
    
    if quadrant_counts['Q3'] > total_tasks * 0.3:
        insights.append(f"👥 {quadrant_counts['Q3']} tasks could be delegated. Consider team expansion.")
    
    if quadrant_counts['Q4'] > 0:
        insights.append(f"🗑️ {quadrant_counts['Q4']} tasks are low value. Consider eliminating.")
    
    if overdue_count > 0:
        insights.append(f"🔴 {overdue_count} tasks are overdue - immediate action needed!")
    
    if blocked_count > 0:
        insights.append(f"⛔ {blocked_count} tasks are blocked - resolve dependencies first.")
    
    # Recommend execution order
    execution_order = (
        categorized['Q1'] +  # Urgent+Important first
        categorized['Q2'][:2] +  # Squeeze in some strategic work
        categorized['Q3']  # Then delegate items
    )
    
    return {
        'summary': {
            'total_tasks': total_tasks,
            'by_quadrant': quadrant_counts,
            'total_time_estimated': total_time_needed,
            'overdue_tasks': overdue_count,
            'blocked_tasks': blocked_count
        },
        'categorized_tasks': categorized,
        'insights': insights,
        'recommended_order': execution_order[:10],  # Top 10 to tackle
        'quick_wins': [t for t in tasks if t.get('estimated_duration', 999) <= 15],
        'delegation_candidates': categorized['Q3'],
        'elimination_candidates': categorized['Q4']
    }


# Helper functions

def _calculate_deadline_urgency_boost(deadline: str) -> int:
    """Calculate how much deadline adds to urgency (0-3 boost)."""
    deadline_dt, _ = _parse_deadline(deadline)
    if not deadline_dt:
        return 0
    
    hours_until = (deadline_dt - datetime.now()).total_seconds() / 3600
    
    if hours_until <= 4:
        return 3  # Very soon
    elif hours_until <= 24:
        return 2  # Tomorrow
    elif hours_until <= 48:
        return 1  # Day after
    else:
        return 0


def _calculate_sender_importance(sender_context: str) -> int:
    """Calculate importance boost from sender (0-2)."""
    sender_lower = sender_context.lower()
    
    # VIP senders
    if any(title in sender_lower for title in ['ceo', 'board', 'executive', 'vp']):
        return 2
    elif any(title in sender_lower for title in ['director', 'manager', 'lead']):
        return 1
    else:
        return 0


def _parse_deadline(deadline: str) -> Tuple[Optional[datetime], bool]:
    """Parse various deadline formats. Returns (datetime, is_relative)."""
    deadline_lower = deadline.lower() if deadline else ''
    
    # Handle relative deadlines
    now = datetime.now()
    
    if 'today' in deadline_lower or 'eod' in deadline_lower:
        return now.replace(hour=17, minute=0, second=0), True
    elif 'tomorrow' in deadline_lower:
        return now + timedelta(days=1), True
    elif 'this week' in deadline_lower:
        return now + timedelta(days=5), True
    elif 'next week' in deadline_lower:
        return now + timedelta(days=7), True
    
    # Try ISO format
    try:
        return datetime.fromisoformat(deadline), False
    except:
        pass
    
    # Try common formats
    for fmt in ['%Y-%m-%d %H:%M', '%Y-%m-%d', '%m/%d/%Y']:
        try:
            return datetime.strptime(deadline, fmt), False
        except:
            continue
    
    return None, False


def _explain_quadrant_placement(
    quadrant: str,
    urgency: int,
    importance: int,
    deadline: Optional[str],
    sender: Optional[str]
) -> str:
    """Generate human-readable explanation of quadrant placement."""
    reasons = []
    
    if urgency >= 8:
        reasons.append("high urgency")
    elif urgency <= 3:
        reasons.append("low urgency")
    
    if importance >= 8:
        reasons.append("high importance")
    elif importance <= 3:
        reasons.append("low importance")
    
    if deadline:
        reasons.append(f"deadline: {deadline}")
    
    if sender:
        reasons.append(f"from: {sender}")
    
    quadrant_names = {
        'Q1': 'Urgent + Important',
        'Q2': 'Not Urgent + Important',
        'Q3': 'Urgent + Not Important',
        'Q4': 'Not Urgent + Not Important'
    }
    
    return f"{quadrant_names[quadrant]} ({', '.join(reasons)})"


def _generate_dependency_recommendation(
    blockers: List[Dict],
    blocks: List[Dict],
    critical_path: bool
) -> str:
    """Generate recommendation based on dependencies."""
    if len(blockers) > 0:
        blocker_titles = ', '.join([b['title'] for b in blockers[:2]])
        return f"⛔ Blocked by: {blocker_titles}. Resolve these first."
    
    if critical_path:
        if len(blocks) > 0:
            return f"🎯 On critical path, blocks {len(blocks)} other tasks. High priority."
        else:
            return "🎯 On critical path. Delays will cascade."
    
    if len(blocks) > 0:
        return f"Blocks {len(blocks)} downstream tasks. Complete soon to unblock team."
    
    return "No blocking dependencies. Can schedule flexibly."


def _score_slot_for_task(
    slot: Dict,
    task: Dict,
    preferences: Dict
) -> int:
    """Score a calendar slot for a task (0-100)."""
    score = 50  # Base score
    
    slot_start = slot['start']
    quadrant = task.get('quadrant', 'Q3')
    focus_level = task.get('focus_level', 'medium')
    
    # Q2 (strategic) tasks need morning focus time
    if quadrant == 'Q2' or focus_level == 'high':
        if '09:' in slot_start or '10:' in slot_start:
            score += 30  # Perfect morning slot
        elif '11:' in slot_start:
            score += 20  # Good morning slot
        elif '08:' in slot_start:
            score += 10  # Early but okay
        elif any(h in slot_start for h in ['14:', '15:', '16:']):
            score -= 20  # Afternoon, not ideal for deep work
    
    # Q3 tasks can go anywhere
    elif quadrant == 'Q3':
        if any(h in slot_start for h in ['14:', '15:']):
            score += 10  # Good for admin tasks
    
    # Longer slots are better for deep work
    if slot['duration'] >= 90 and focus_level == 'high':
        score += 20
    
    # Penalize very late slots
    if '17:' in slot_start or '18:' in slot_start:
        score -= 30
    
    return max(0, min(100, score))


def _explain_slot_choice(slot: Dict, task: Dict, preferences: Dict) -> str:
    """Explain why this slot was recommended."""
    reasons = []
    
    quadrant = task.get('quadrant')
    if quadrant == 'Q2' and ('09:' in slot['start'] or '10:' in slot['start']):
        reasons.append("morning focus time for strategic work")
    
    if slot['duration'] >= 90:
        reasons.append("long uninterrupted block")
    
    if task.get('focus_level') == 'high':
        reasons.append("high-energy time for complex task")
    
    if not reasons:
        reasons.append("fits duration requirement")
    
    return "Best slot: " + ", ".join(reasons)


# Test the tools
if __name__ == "__main__":
    print("=" * 70)
    print("Task Management Tools - Test Suite")
    print("=" * 70)
    
    # Test 1: Eisenhower categorization
    print("\n1. Testing Eisenhower Matrix Categorization")
    print("-" * 70)
    
    test_task = categorize_task_eisenhower(
        task_description="Prepare board presentation",
        urgency_score=8,
        importance_score=10,
        deadline="tomorrow 9am",
        sender_context="CEO request"
    )
    
    print(f"Task: Prepare board presentation")
    print(f"Quadrant: {test_task['quadrant']} - {test_task['action']}")
    print(f"Priority: {test_task['priority_level']}")
    print(f"Scores: Urgency={test_task['urgency_score']}, Importance={test_task['importance_score']}")
    print(f"Recommendation: {test_task['recommendation']}")
    
    # Test 2: Deadline urgency
    print("\n2. Testing Deadline Urgency Calculation")
    print("-" * 70)
    
    urgency = calculate_deadline_urgency(
        deadline="2024-11-18 17:00",
        task_type="hard_deadline",
        consequences="client deliverable, revenue impact"
    )
    
    print(f"Deadline: 2024-11-18 17:00")
    print(f"Urgency Score: {urgency['urgency_score']}/10")
    print(f"Status: {urgency['status']}")
    print(f"Time Until: {urgency.get('hours_until_deadline', 'N/A')} hours")
    if 'warning' in urgency:
        print(f"Warning: {urgency['warning']}")
    
    # Test 3: Batch processing
    print("\n3. Testing Batch Task Processing")
    print("-" * 70)
    
    sample_tasks = [
        {"title": "Review contract", "urgency_score": 8, "importance_score": 9, "estimated_duration": 60},
        {"title": "Strategic planning", "urgency_score": 4, "importance_score": 10, "estimated_duration": 120},
        {"title": "Approve expenses", "urgency_score": 7, "importance_score": 3, "estimated_duration": 15},
        {"title": "Read industry report", "urgency_score": 2, "importance_score": 2, "estimated_duration": 30}
    ]
    
    batch_result = batch_process_tasks(sample_tasks)
    
    print(f"Total Tasks: {batch_result['summary']['total_tasks']}")
    print(f"By Quadrant: {batch_result['summary']['by_quadrant']}")
    print(f"Total Time: {batch_result['summary']['total_time_estimated']} minutes")
    print(f"\nInsights:")
    for insight in batch_result['insights']:
        print(f"  {insight}")
    
    print("\n" + "=" * 70)
    print("✅ All tools working! Ready for integration with Task Management Agent")
    print("=" * 70)
