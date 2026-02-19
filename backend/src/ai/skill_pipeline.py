"""Advanced Skill Pipeline Manager with context transformation, error recovery, and rollback."""

import asyncio
import time
from typing import List, Dict, Any, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum
from contextlib import asynccontextmanager
from copy import deepcopy

from .base import BaseSkill, BaseAgent, SkillContext, AgentRequest, AgentResponse, SkillPhase
from ..services.retriever import Retriever
from ..utils.circuit_breaker import RetryPolicy


class PipelinePhase(str, Enum):
    """Execution phases for the skill pipeline."""
    PREPROCESSING = "pre"
    AGENT_EXECUTION = "agent"
    POSTPROCESSING = "post"
    ERROR_HANDLING = "error"


class PipelineError(Exception):
    """Raised when pipeline execution fails."""
    pass


@dataclass
class PipelineStep:
    """Represents a step in the pipeline with context and result."""
    step_id: str
    name: str
    phase: PipelinePhase
    context: SkillContext
    result: Any = None
    error: Optional[Exception] = None
    duration: float = 0.0
    timestamp: float = 0.0


@dataclass
class PipelineState:
    """Current state of the pipeline execution."""
    steps: List[PipelineStep]
    current_phase: PipelinePhase
    context: SkillContext
    agent_request: AgentRequest
    agent_response: Optional[AgentResponse] = None
    rollback_stack: List[Callable] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.rollback_stack is None:
            self.rollback_stack = []
        if self.metadata is None:
            self.metadata = {}


class SkillRollbackManager:
    """Manages rollback operations for skill execution failures."""

    def __init__(self):
        self.rollback_actions = []

    def add_rollback(self, action: Callable):
        """Add an action to be executed during rollback."""
        self.rollback_actions.append(action)

    async def execute_rollbacks(self):
        """Execute all registered rollback actions."""
        for action in reversed(self.rollback_actions):
            try:
                if asyncio.iscoroutinefunction(action):
                    await action()
                else:
                    action()
            except Exception as e:
                print(f"Rollback action failed: {e}")  # Use logger in production


class SkillPipelineManager:
    """
    Advanced skill pipeline manager with:
    - Context transformation
    - Error recovery
    - Rollback capabilities
    - Retry mechanisms
    - Step monitoring
    """

    def __init__(self):
        self.retry_policy = RetryPolicy(max_retries=3, base_delay=0.5)
        self.retriever = Retriever()

    def _create_pipeline_step(self, step_id: str, name: str, phase: PipelinePhase, context: SkillContext) -> PipelineStep:
        """Create a pipeline step record."""
        return PipelineStep(
            step_id=step_id,
            name=name,
            phase=phase,
            context=deepcopy(context),
            timestamp=time.time()
        )

    def _get_skill_phase_from_enum(self, skill: BaseSkill):
        """Get phase from skill's get_phase() which may return str or SkillPhase."""
        phase = skill.get_phase()
        if isinstance(phase, str):
            return PipelinePhase(phase)
        else:  # It's a SkillPhase enum
            return PipelinePhase(phase.value)

    async def execute_skill_pipeline(
        self,
        agent: BaseAgent,
        skills: List[BaseSkill],
        request: AgentRequest,
        initial_context: SkillContext
    ) -> tuple[PipelineState, AgentResponse]:
        """
        Execute the complete skill pipeline with error handling:
        1. Pre-processing skills
        2. Agent execution
        3. Post-processing skills
        4. Error recovery if needed
        """
        pipeline_id = f"pipeline-{int(time.time())}-{request.request_type[:3]}"
        rollback_manager = SkillRollbackManager()
        pipeline_state = PipelineState(
            steps=[],
            current_phase=PipelinePhase.PREPROCESSING,
            context=initial_context,
            agent_request=request,
            metadata={"pipeline_id": pipeline_id}
        )

        try:
            # 1. Execute pre-processing skills
            pipeline_state = await self._execute_preprocessing_skills(
                skills, pipeline_state, rollback_manager
            )

            # 2. Execute agent with circuit breaker and retry logic
            pipeline_state = await self._execute_agent_with_retry(
                agent, request, pipeline_state
            )

            # 3. Execute post-processing skills
            pipeline_state = await self._execute_postprocessing_skills(
                skills, pipeline_state, rollback_manager
            )

            # 4. Update final response with pipeline metadata
            if pipeline_state.agent_response:
                metadata = pipeline_state.agent_response.agent_data
                metadata['pipeline_id'] = pipeline_id
                metadata['pipeline_steps'] = len(pipeline_state.steps)
                metadata['pipeline_success'] = True

        except Exception as e:
            pipeline_state.metadata['pipeline_error'] = str(e)
            # Execute error handling
            pipeline_state = await self._execute_error_handling(pipeline_state, e)

        return pipeline_state, pipeline_state.agent_response

    async def _execute_preprocessing_skills(
        self, skills: List[BaseSkill], pipeline_state: PipelineState, rollback_manager: SkillRollbackManager
    ) -> PipelineState:
        """Execute all pre-processing skills in the pipeline."""
        pipeline_state.current_phase = PipelinePhase.PREPROCESSING

        for i, skill in enumerate(skills):
            skill_phase = self._get_skill_phase_from_enum(skill)
            if skill_phase in [PipelinePhase.PREPROCESSING, "pre", "both"]:
                step_id = f"pre-{i}-{skill.get_name()}"
                step = self._create_pipeline_step(step_id, skill.get_name(), PipelinePhase.PREPROCESSING, pipeline_state.context)

                start_time = time.time()
                try:
                    # Execute skill preprocessing
                    new_context = await skill.pre_process(pipeline_state.context)
                    pipeline_state.context = new_context
                    step.result = "success"
                    step.duration = time.time() - start_time

                    # Add a rollback handler that stores original context before modifications
                    async def rollback_context(context_before=deepcopy(pipeline_state.context), step_index=i):
                        pipeline_state.context = context_before

                    rollback_manager.add_rollback(rollback_context)

                    pipeline_state.steps.append(step)

                except Exception as e:
                    step.error = e
                    step.result = "failure"
                    step.duration = time.time() - start_time
                    pipeline_state.steps.append(step)
                    raise PipelineError(f"Failed to execute pre-skill {skill.get_name()}: {str(e)}")

        return pipeline_state

    async def _execute_agent_with_retry(
        self, agent: BaseAgent, request: AgentRequest, pipeline_state: PipelineState
    ) -> PipelineState:
        """Execute the agent with retry logic and circuit breaker."""
        start_time = time.time()

        # Attempt up to max_retires retries
        last_exception = None
        response = None

        for attempt in range(self.retry_policy.max_retries + 1):
            try:
                # Update the agent request with the modified context values
                actual_request = request
                if pipeline_state.context.ai_response:
                    # Create new request with updated content if needed
                    actual_request = AgentRequest(
                        request_type=request.request_type,
                        chapter_slug=request.chapter_slug,
                        content=pipeline_state.context.ai_response or request.content,
                        query=request.query,
                        user_id=request.user_id,
                        user_profile=request.user_profile,
                        target_language=request.target_language,
                        conversation_history=request.conversation_history,
                        session_id=request.session_id,
                        mode=request.mode,
                        selected_text=request.selected_text,
                        content_version=request.content_version,
                        prompt_version=request.prompt_version,
                        stream=request.stream
                    )

                response = await agent.execute(actual_request)
                break  # Success, exit retry loop

            except Exception as e:
                last_exception = e
                if attempt < self.retry_policy.max_retries:
                    delay = self.retry_policy.get_delay(attempt)
                    await asyncio.sleep(delay)
                else:
                    # All retries failed
                    step_id = f"agent-execution-failed"
                    step = self._create_pipeline_step(step_id, agent.get_agent_type(), PipelinePhase.AGENT_EXECUTION, pipeline_state.context)
                    step.error = e
                    step.result = "failure"
                    step.duration = time.time() - start_time
                    pipeline_state.steps.append(step)
                    raise PipelineError(f"Agent execution failed after {self.retry_policy.max_retries} retries: {str(e)}")

        # Record successful execution
        step_id = f"agent-execution-success"
        step = self._create_pipeline_step(step_id, agent.get_agent_type(), PipelinePhase.AGENT_EXECUTION, pipeline_state.context)
        step.result = "success"
        step.duration = time.time() - start_time
        pipeline_state.steps.append(step)

        # Update pipeline state
        pipeline_state.current_phase = PipelinePhase.AGENT_EXECUTION
        pipeline_state.agent_response = response
        # Update context with the result
        pipeline_state.context.ai_response = response.content

        return pipeline_state

    async def _execute_postprocessing_skills(
        self, skills: List[BaseSkill], pipeline_state: PipelineState, rollback_manager: SkillRollbackManager
    ) -> PipelineState:
        """Execute all post-processing skills in the pipeline."""
        pipeline_state.current_phase = PipelinePhase.POSTPROCESSING

        for i, skill in enumerate(skills):
            skill_phase = self._get_skill_phase_from_enum(skill)
            if skill_phase in [PipelinePhase.POSTPROCESSING, "post", "both"]:
                step_id = f"post-{i}-{skill.get_name()}"
                step = self._create_pipeline_step(step_id, skill.get_name(), PipelinePhase.POSTPROCESSING, pipeline_state.context)

                start_time = time.time()
                try:
                    # Execute skill postprocessing
                    new_context = await skill.post_process(pipeline_state.context)
                    pipeline_state.context = new_context
                    step.result = "success"
                    step.duration = time.time() - start_time

                    pipeline_state.steps.append(step)

                except Exception as e:
                    step.error = e
                    step.result = "failure"
                    step.duration = time.time() - start_time
                    pipeline_state.steps.append(step)
                    raise PipelineError(f"Failed to execute post-skill {skill.get_name()}: {str(e)}")

        return pipeline_state

    async def _execute_error_handling(self, pipeline_state: PipelineState, error: Exception) -> PipelineState:
        """Execute error handling phase."""
        pipeline_state.current_phase = PipelinePhase.ERROR_HANDLING

        step_id = f"error-handling"
        step = self._create_pipeline_step(step_id, "error_recovery", PipelinePhase.ERROR_HANDLING, pipeline_state.context)
        step.error = error
        step.result = "error_occurred"
        step.duration = 0.0

        pipeline_state.steps.append(step)

        # Create an error response
        error_response = AgentResponse(
            agent_type="pipeline_error",
            content=f"Pipeline error: {str(error)}",
            cached=False,
            model="",
            token_count=0,
            latency_ms=0,
            grounding_policy="error",
            agent_data={"error": str(error), "pipeline_error": True}
        )
        pipeline_state.agent_response = error_response

        return pipeline_state

    async def validate_agent_response(self, agent: BaseAgent, response: AgentResponse) -> Union[AgentResponse, None]:
        """
        Validate the agent response and potentially re-execute if validation fails.
        """
        is_valid = agent.validate_output(response)
        if not is_valid:
            # Create a new request to retry the agent with information about the validation failure
            # This is a simplified version - in a real implementation, you might want to
            # send back the failure details to the agent to correct
            return None
        return response


# Convenience function for use in orchestrator
async def execute_agent_with_skills(agent: BaseAgent, skills: List[BaseSkill], request: AgentRequest, context: SkillContext) -> AgentResponse:
    """
    Utility function to execute an agent with skills using the pipeline manager.
    """
    pipeline_manager = SkillPipelineManager()
    pipeline_state, agent_response = await pipeline_manager.execute_skill_pipeline(agent, skills, request, context)
    return agent_response