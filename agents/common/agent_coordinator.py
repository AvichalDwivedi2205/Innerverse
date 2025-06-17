"""Agent Coordinator for managing multi-agent workflows.

This module provides coordination capabilities for managing interactions between
different agents in the Innerverse system, replacing Firebase-based triggers
with direct agent communication.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from .tool_results import CoordinationResult


class AgentCoordinator:
    """Coordinates interactions between multiple agents."""
    
    def __init__(self):
        self.agent_registry: Dict[str, Agent] = {}
        self.workflow_definitions: Dict[str, List[Dict[str, Any]]] = {}
        self._setup_workflows()
    
    def _setup_workflows(self):
        """Define standard workflows for agent coordination."""
        self.workflow_definitions = {
            "journal_to_mindmap": [
                {
                    "agent": "journaling_agent",
                    "action": "process_journal_entry",
                    "required_data": ["raw_text", "user_id"]
                },
                {
                    "agent": "mental_orchestrator_agent", 
                    "action": "update_mind_map",
                    "required_data": ["journal_id", "user_id"]
                }
            ],
            "therapy_to_mindmap": [
                {
                    "agent": "therapy_agent",
                    "action": "process_therapy_session",
                    "required_data": ["transcript", "user_id"]
                },
                {
                    "agent": "mental_orchestrator_agent",
                    "action": "update_mind_map", 
                    "required_data": ["session_id", "user_id"]
                }
            ],
            "comprehensive_analysis": [
                {
                    "agent": "mental_orchestrator_agent",
                    "action": "retrieve_embeddings",
                    "required_data": ["user_id"]
                },
                {
                    "agent": "mental_orchestrator_agent",
                    "action": "cluster_patterns",
                    "required_data": ["user_id"]
                },
                {
                    "agent": "mental_orchestrator_agent",
                    "action": "generate_insights",
                    "required_data": ["user_id"]
                }
            ]
        }
    
    def register_agent(self, name: str, agent: Agent):
        """Register an agent for coordination."""
        self.agent_registry[name] = agent
    
    async def coordinate_workflow(
        self, 
        workflow_name: str, 
        initial_data: Dict[str, Any],
        callback_context: CallbackContext
    ) -> CoordinationResult:
        """Execute a coordinated workflow across multiple agents.
        
        Args:
            workflow_name: Name of the workflow to execute
            initial_data: Initial data to pass to the workflow
            callback_context: Shared callback context for state management
            
        Returns:
            CoordinationResult with workflow execution results
        """
        try:
            if workflow_name not in self.workflow_definitions:
                return CoordinationResult(
                    success=False,
                    coordinated_agents=[],
                    results={},
                    message=f"Unknown workflow: {workflow_name}",
                    errors=[f"Workflow '{workflow_name}' not found"]
                )
            
            workflow_steps = self.workflow_definitions[workflow_name]
            results = {}
            coordinated_agents = []
            
            # Execute workflow steps sequentially
            current_data = initial_data.copy()
            
            for step in workflow_steps:
                agent_name = step["agent"]
                action = step["action"]
                required_data = step["required_data"]
                
                # Check if required data is available
                missing_data = [key for key in required_data if key not in current_data]
                if missing_data:
                    return CoordinationResult(
                        success=False,
                        coordinated_agents=coordinated_agents,
                        results=results,
                        message=f"Missing required data: {missing_data}",
                        errors=[f"Missing data for step {action}: {missing_data}"]
                    )
                
                # Execute step
                step_result = await self._execute_agent_action(
                    agent_name, 
                    action, 
                    current_data,
                    callback_context
                )
                
                # Store results and update data for next step
                step_key = f"{agent_name}_{action}"
                results[step_key] = step_result
                coordinated_agents.append(agent_name)
                
                # Update current_data with results for next step
                if isinstance(step_result, dict) and "data" in step_result:
                    current_data.update(step_result["data"])
            
            return CoordinationResult(
                success=True,
                coordinated_agents=list(set(coordinated_agents)),
                results=results,
                message=f"Workflow '{workflow_name}' completed successfully"
            )
            
        except Exception as e:
            return CoordinationResult(
                success=False,
                coordinated_agents=coordinated_agents,
                results=results,
                message=f"Workflow execution failed: {str(e)}",
                errors=[str(e)]
            )
    
    async def _execute_agent_action(
        self, 
        agent_name: str, 
        action: str, 
        data: Dict[str, Any],
        callback_context: CallbackContext
    ) -> Dict[str, Any]:
        """Execute a specific action on an agent.
        
        This is a simplified implementation that would need to be expanded
        based on your specific agent action patterns.
        """
        # Update callback context with current data
        callback_context.state.update(data)
        
        # For this implementation, we'll return a mock result
        # In a real implementation, you would call the specific agent method
        return {
            "agent": agent_name,
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "data": {"result": f"Executed {action} on {agent_name}"},
            "success": True
        }
    
    async def trigger_mindmap_update(
        self,
        user_id: str,
        source_type: str,
        source_id: str,
        callback_context: CallbackContext
    ) -> CoordinationResult:
        """Trigger mind map update directly instead of using Firebase triggers.
        
        Args:
            user_id: User identifier
            source_type: Type of source (journal, therapy)
            source_id: ID of the source document
            callback_context: Shared callback context
            
        Returns:
            CoordinationResult with update results
        """
        try:
            # Determine workflow based on source type
            workflow_map = {
                "journal": "journal_to_mindmap",
                "therapy": "therapy_to_mindmap"
            }
            
            workflow_name = workflow_map.get(source_type)
            if not workflow_name:
                return CoordinationResult(
                    success=False,
                    coordinated_agents=[],
                    results={},
                    message=f"No workflow defined for source type: {source_type}",
                    errors=[f"Unknown source type: {source_type}"]
                )
            
            # Prepare data for workflow
            workflow_data = {
                "user_id": user_id,
                "source_type": source_type,
                "source_id": source_id,
                f"{source_type}_id": source_id
            }
            
            # Execute workflow
            result = await self.coordinate_workflow(
                workflow_name,
                workflow_data,
                callback_context
            )
            
            return result
            
        except Exception as e:
            return CoordinationResult(
                success=False,
                coordinated_agents=[],
                results={},
                message=f"Mind map update failed: {str(e)}",
                errors=[str(e)]
            )


# Global coordinator instance
coordinator = AgentCoordinator() 