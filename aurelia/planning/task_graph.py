"""
Aurelia Cognitive OS V3 - Phase 5: Task Graph
===========================================
Manages tasks and their dependencies using a graph structure.

Task graphs handle the complex web of dependencies between
different tasks in a plan.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Any
from enum import Enum
from datetime import datetime


class TaskStatus(Enum):
    """Status of a task."""
    PENDING = "pending"
    READY = "ready"  # Dependencies satisfied
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


class TaskType(Enum):
    """Types of tasks."""
    ANALYSIS = "analysis"
    PLANNING = "planning"
    EXECUTION = "execution"
    REVIEW = "review"
    LEARNING = "learning"
    DATA_COLLECTION = "data_collection"


@dataclass
class Task:
    """
    A task in the task graph.
    
    Tasks are atomic units of work that can be executed.
    """
    id: str
    title: str
    description: str
    task_type: TaskType
    status: TaskStatus
    estimated_duration_hours: Optional[float] = None
    actual_duration_hours: Optional[float] = None
    dependencies: List[str] = field(default_factory=list)  # Task IDs this depends on
    dependents: List[str] = field(default_factory=list)  # Task IDs that depend on this
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    associated_goal_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class TaskGraph:
    """
    Manages tasks and their dependencies using a graph structure.
    
    The task graph handles:
    - Task creation and dependency management
    - Dependency resolution (determining which tasks are ready)
    - Critical path analysis
    - Cycle detection
    """
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.task_counter = 0
    
    def create_task(
        self,
        title: str,
        description: str,
        task_type: TaskType,
        dependencies: Optional[List[str]] = None,
        estimated_duration_hours: Optional[float] = None,
        associated_goal_id: Optional[str] = None
    ) -> Task:
        """Create a new task."""
        task_id = f"task_{self.task_counter}"
        
        task = Task(
            id=task_id,
            title=title,
            description=description,
            task_type=task_type,
            status=TaskStatus.PENDING,
            dependencies=dependencies or [],
            estimated_duration_hours=estimated_duration_hours,
            associated_goal_id=associated_goal_id
        )
        
        self.tasks[task_id] = task
        self.task_counter += 1
        
        # Update dependents for each dependency
        for dep_id in task.dependencies:
            if dep_id in self.tasks:
                self.tasks[dep_id].dependents.append(task_id)
        
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self.tasks.get(task_id)
    
    def update_task_status(self, task_id: str, status: TaskStatus):
        """Update the status of a task."""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = status
            
            if status == TaskStatus.IN_PROGRESS and task.started_at is None:
                task.started_at = datetime.now()
            elif status == TaskStatus.COMPLETED and task.completed_at is None:
                task.completed_at = datetime.now()
                
                # Calculate actual duration
                if task.started_at:
                    duration = (task.completed_at - task.started_at).total_seconds() / 3600
                    task.actual_duration_hours = duration
    
    def get_ready_tasks(self) -> List[Task]:
        """
        Get tasks that are ready to execute.
        
        A task is ready if all its dependencies are completed.
        """
        ready_tasks = []
        
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING:
                # Check if all dependencies are completed
                dependencies_completed = all(
                    self.get_task(dep_id).status == TaskStatus.COMPLETED
                    for dep_id in task.dependencies
                    if dep_id in self.tasks
                )
                
                if dependencies_completed:
                    ready_tasks.append(task)
        
        return ready_tasks
    
    def get_blocked_tasks(self) -> List[Task]:
        """Get tasks that are blocked by incomplete dependencies."""
        blocked_tasks = []
        
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING:
                # Check if any dependency is not completed
                has_incomplete_deps = any(
                    self.get_task(dep_id).status != TaskStatus.COMPLETED
                    for dep_id in task.dependencies
                    if dep_id in self.tasks
                )
                
                if has_incomplete_deps:
                    blocked_tasks.append(task)
        
        return blocked_tasks
    
    def detect_cycles(self) -> List[List[str]]:
        """
        Detect cycles in the task dependency graph.
        
        Returns a list of cycles (each cycle is a list of task IDs).
        """
        cycles = []
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(task_id: str):
            if task_id in rec_stack:
                # Found a cycle
                cycle_start = path.index(task_id)
                cycles.append(path[cycle_start:] + [task_id])
                return
            
            if task_id in visited:
                return
            
            visited.add(task_id)
            rec_stack.add(task_id)
            path.append(task_id)
            
            task = self.get_task(task_id)
            if task:
                for dep_id in task.dependencies:
                    if dep_id in self.tasks:
                        dfs(dep_id)
            
            path.pop()
            rec_stack.remove(task_id)
        
        for task_id in self.tasks:
            if task_id not in visited:
                dfs(task_id)
        
        return cycles
    
    def has_cycles(self) -> bool:
        """Check if the task graph has cycles."""
        return len(self.detect_cycles()) > 0
    
    def get_critical_path(self) -> List[Task]:
        """
        Calculate the critical path (longest path through the graph).
        
        The critical path determines the minimum time needed to complete
        all tasks.
        """
        # Simple implementation: find the longest path from start to end
        # This is a simplification - full critical path would need proper DAG analysis
        
        if self.has_cycles():
            return []  # Cannot calculate critical path with cycles
        
        max_path = []
        max_duration = 0
        
        def dfs_longest_path(task_id: str, current_path: List[Task], current_duration: float):
            nonlocal max_path, max_duration
            
            task = self.get_task(task_id)
            if not task:
                return
            
            current_path.append(task)
            current_duration += task.estimated_duration_hours or 0
            
            # Check if this is a leaf node (no dependents)
            if not task.dependents:
                if current_duration > max_duration:
                    max_duration = current_duration
                    max_path = current_path.copy()
            else:
                for dep_id in task.dependents:
                    if dep_id in self.tasks:
                        dfs_longest_path(dep_id, current_path, current_duration)
            
            current_path.pop()
        
        # Start from tasks with no dependencies
        for task in self.tasks.values():
            if not task.dependencies:
                dfs_longest_path(task.id, [], 0)
        
        return max_path
    
    def get_tasks_by_type(self, task_type: TaskType) -> List[Task]:
        """Get all tasks of a specific type."""
        return [t for t in self.tasks.values() if t.task_type == task_type]
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get all tasks with a specific status."""
        return [t for t in self.tasks.values() if t.status == status]
    
    def get_tasks_for_goal(self, goal_id: str) -> List[Task]:
        """Get all tasks associated with a specific goal."""
        return [t for t in self.tasks.values() if t.associated_goal_id == goal_id]
    
    def get_task_dependency_graph(self) -> Dict[str, List[str]]:
        """
        Get the dependency graph as a dictionary.
        
        Returns: {task_id: [dependency_ids]}
        """
        return {
            task_id: task.dependencies
            for task_id, task in self.tasks.items()
        }
    
    def calculate_progress(self) -> float:
        """Calculate overall progress (percentage of completed tasks)."""
        if not self.tasks:
            return 0.0
        
        completed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED)
        return completed / len(self.tasks)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the task graph state."""
        return {
            "total_tasks": len(self.tasks),
            "by_status": {status.value: len(self.get_tasks_by_status(status)) for status in TaskStatus},
            "by_type": {ttype.value: len(self.get_tasks_by_type(ttype)) for ttype in TaskType},
            "ready_tasks": len(self.get_ready_tasks()),
            "blocked_tasks": len(self.get_blocked_tasks()),
            "has_cycles": self.has_cycles(),
            "progress": self.calculate_progress()
        }