"""AI Orchestrator module - central routing and execution for AI agents."""
import asyncio
import time
from typing import Dict, Any, Optional, AsyncGenerator, List
from datetime import datetime
from .base import BaseAgent, BaseSkill, SkillPhase, SkillContext, AgentRequest, AgentResponse
from .registry import AgentRegistry, SkillRegistry
from .prompts.registry import PromptRegistry
from .envelope import AIEnvelope, GenerationMetadata
from ..db.neon_client import NeonClient


class AIOrchestrator:
    """Singleton. Routes requests to agents, composes skills, logs execution."""

    def __init__(self, agent_registry: AgentRegistry, skill_registry: SkillRegistry,
                 prompt_registry: PromptRegistry, neon_client: NeonClient):
        self.agent_registry = agent_registry
        self.skill_registry = skill_registry
        self.prompt_registry = prompt_registry
        self.neon_client = neon_client

    async def execute(self, request_type: str, payload: Dict[str, Any]) -> AIEnvelope:
        """
        Execute a request through the orchestrator:
        1. Look up agent by request_type
        2. Verify required skills
        3. Run pre-processing skills
        4. Agent.execute()
        5. Run post-processing skills
        6. Log execution
        7. Return envelope
        """
        start_time = time.time()

        # Build AgentRequest from payload
        request = self._build_agent_request(request_type, payload)

        # Get and validate agent
        agent = self.agent_registry.get_agent(request_type)
        if not agent:
            raise ValueError(f"Unknown agent type: {request_type}")

        # Get and validate required skills
        skill_names = agent.get_required_skills()
        skills = [self.skill_registry.get_skill(skill_name) for skill_name in skill_names]
        if any(s is None for s in skills):
            missing = [name for name, s in zip(skill_names, skills) if s is None]
            raise ValueError(f"Missing required skills: {missing}")

        # Load prompt template with version
        template = self.prompt_registry.get_template(agent.get_agent_type())

        # Prepare initial skill context
        context = SkillContext(
            agent_type=agent.get_agent_type(),
            grounding_policy=agent.get_grounding_policy(),
            system_prompt=template.content if template else "",
            user_message=payload.get('content', payload.get('query', '')),
            original_content=payload.get('content', ''),
            original_headings=self._extract_headings(payload.get('content', '')),
            original_code_blocks=self._extract_code_blocks(payload.get('content', ''))
        )

        # Track execution details
        skills_executed = []
        skill_details = []

        # Execute pre-processing skills
        for skill in skills:
            if skill.get_phase() in [SkillPhase.PRE, SkillPhase.BOTH]:
                skill_start = time.time()
                try:
                    context = await skill.pre_process(context)
                    duration = int((time.time() - skill_start) * 1000)
                    skills_executed.append(skill.get_name())
                    skill_details.append({
                        "skill": skill.get_name(),
                        "phase": "pre",
                        "status": "success",
                        "duration_ms": duration
                    })
                except Exception as e:
                    duration = int((time.time() - skill_start) * 1000)
                    skill_details.append({
                        "skill": skill.get_name(),
                        "phase": "pre",
                        "status": "failure",
                        "duration_ms": duration,
                        "details": str(e)
                    })

        # Execute the agent with error handling
        try:
            response = await agent.execute(request)
            # Update context with AI response for post-processing
            context.ai_response = response.content
        except Exception as e:
            # Log the error for debugging
            import traceback
            error_msg = f"Agent execution failed: {str(e)}"
            print(f"ERROR in orchestrator: {error_msg}")
            print(f"Traceback: {traceback.format_exc()}")

            # Create an error response instead of crashing
            response = AgentResponse(
                agent_type=agent.get_agent_type(),
                content=f"Error: The {agent.get_agent_type()} agent encountered an issue: {str(e)}",
                cached=False,
                model="",
                token_count=0,
                latency_ms=0,
                grounding_policy=agent.get_grounding_policy(),
                agent_data={}
            )
            # Set a basic error response in context
            context.ai_response = response.content

        # Execute post-processing skills
        for skill in skills:
            if skill.get_phase() in [SkillPhase.POST, SkillPhase.BOTH]:
                skill_start = time.time()
                try:
                    context = await skill.post_process(context)
                    duration = int((time.time() - skill_start) * 1000)
                    skills_executed.append(skill.get_name())
                    skill_details.append({
                        "skill": skill.get_name(),
                        "phase": "post",
                        "status": "success",
                        "duration_ms": duration
                    })
                except Exception as e:
                    duration = int((time.time() - skill_start) * 1000)
                    skill_details.append({
                        "skill": skill.get_name(),
                        "phase": "post",
                        "status": "failure",
                        "duration_ms": duration,
                        "details": str(e)
                    })

        # Validate final output
        is_valid = agent.validate_output(response)
        if not is_valid:
            # Add a note about validation failure to the skill details
            skill_details.append({
                "skill": "output_validator",
                "phase": "post",
                "status": "failure",
                "duration_ms": 0,
                "details": "Agent output validation failed"
            })

        # Calculate total latency
        total_latency = int((time.time() - start_time) * 1000)

        # Log execution with error handling
        try:
            await self._log_execution(
                agent_type=agent.get_agent_type(),
                grounding_policy=agent.get_grounding_policy(),
                skills_used=skills_executed,
                skills_detail=skill_details,
                token_count=response.token_count,
                model=response.model,
                latency_ms=total_latency,
                cached=response.cached,
                request_payload=payload
            )
        except Exception as log_error:
            print(f"ERROR logging execution: {str(log_error)}")
            # Don't let logging errors break the response

        # Build return envelope
        envelope_data = {**response.agent_data}
        if request_type == 'personalization':
            envelope_data['personalized_markdown'] = response.content
            envelope_data['content_version'] = payload.get('content_version', '')
            envelope_data['prompt_version'] = self.prompt_registry.get_version(agent.get_agent_type())
            if 'user_profile' in payload:
                envelope_data['profile_used'] = payload['user_profile']
        elif request_type == 'translation':
            envelope_data['translated_markdown'] = response.content
            envelope_data['content_version'] = payload.get('content_version', '')
            envelope_data['prompt_version'] = self.prompt_registry.get_version(agent.get_agent_type())
            envelope_data['target_language'] = payload.get('target_language', 'urdu')
            envelope_data['source_language'] = 'english'  # Simplified for now
        else:  # chat or other agents
            envelope_data['content'] = response.content
            envelope_data['query'] = payload.get('query', '')

        return AIEnvelope(
            agent_type=agent.get_agent_type(),
            skills_used=list(set(skills_executed)),  # Remove duplicates
            cached=response.cached,
            grounding_policy=agent.get_grounding_policy(),
            generation_metadata=GenerationMetadata(
                model=response.model,
                token_count=response.token_count,
                latency_ms=response.latency_ms,
                prompt_version=self.prompt_registry.get_version(agent.get_agent_type())
            ),
            data=envelope_data
        )

    async def execute_stream(self, request_type: str, payload: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """
        Execute a streaming request (for chat agents).
        Pre-processing skills run before streaming starts.
        Post-processing skills run after streaming completes.
        """
        start_time = time.time()

        # Build AgentRequest from payload (with stream=True)
        request_dict = dict(payload)
        request_dict['stream'] = True
        request = self._build_agent_request(request_type, request_dict)

        # Get and validate agent
        agent = self.agent_registry.get_agent(request_type)
        if not agent:
            raise ValueError(f"Unknown agent type: {request_type}")

        # Get and validate required skills
        skill_names = agent.get_required_skills()
        skills = [self.skill_registry.get_skill(skill_name) for skill_name in skill_names]
        if any(s is None for s in skills):
            missing = [name for name, s in zip(skill_names, skills) if s is None]
            raise ValueError(f"Missing required skills: {missing}")

        # Load prompt template with version
        template = self.prompt_registry.get_template(agent.get_agent_type())

        # Prepare initial skill context (pre-streaming)
        context = SkillContext(
            agent_type=agent.get_agent_type(),
            grounding_policy=agent.get_grounding_policy(),
            system_prompt=template.content if template else "",
            user_message=payload.get('content', payload.get('query', '')),
            original_content=payload.get('content', ''),
            original_headings=self._extract_headings(payload.get('content', '')),
            original_code_blocks=self._extract_code_blocks(payload.get('content', ''))
        )

        # Execute pre-processing skills
        skills_executed = []
        skill_details = []

        for skill in skills:
            if skill.get_phase() in [SkillPhase.PRE, SkillPhase.BOTH]:
                skill_start = time.time()
                try:
                    context = await skill.pre_process(context)
                    duration = int((time.time() - skill_start) * 1000)
                    skills_executed.append(skill.get_name())
                    skill_details.append({
                        "skill": skill.get_name(),
                        "phase": "pre",
                        "status": "success",
                        "duration_ms": duration
                    })
                except Exception as e:
                    duration = int((time.time() - skill_start) * 1000)
                    skill_details.append({
                        "skill": skill.get_name(),
                        "phase": "pre",
                        "status": "failure",
                        "duration_ms": duration,
                        "details": str(e)
                    })

        # Execute the streaming agent using its execute_stream method
        try:
            async for token in agent.execute_stream(request):
                yield token
        except NotImplementedError:
            # If streaming is not implemented for the agent
            yield "Streaming not implemented for this agent type"
        except Exception as e:
            # Handle any other errors during streaming
            import traceback
            print(f"ERROR in streaming execution: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            yield f"Error during streaming: {str(e)}"

        # Calculate total latency
        total_latency = int((time.time() - start_time) * 1000)

        # Log execution with error handling
        try:
            await self._log_execution(
                agent_type=agent.get_agent_type(),
                grounding_policy=agent.get_grounding_policy(),
                skills_used=skills_executed,
                skills_detail=skill_details,
                token_count=0,  # Not applicable for streaming
                model="",  # Not applicable for streaming
                latency_ms=total_latency,
                cached=False,  # Not applicable for streaming
                request_payload=payload
            )
        except Exception as log_error:
            print(f"ERROR logging streaming execution: {str(log_error)}")
            # Don't let logging errors break the streaming response

    def _build_agent_request(self, request_type: str, payload: Dict[str, Any]) -> AgentRequest:
        """Build an AgentRequest from the payload."""
        return AgentRequest(
            request_type=request_type,
            chapter_slug=payload.get('chapter_slug'),
            content=payload.get('content'),
            query=payload.get('query'),
            user_id=payload.get('user_id'),
            user_profile=payload.get('user_profile'),
            target_language=payload.get('target_language'),
            conversation_history=payload.get('conversation_history'),
            session_id=payload.get('session_id'),
            mode=payload.get('mode'),
            selected_text=payload.get('selected_text'),
            content_version=payload.get('content_version'),
            prompt_version=payload.get('prompt_version'),
            stream=payload.get('stream', False)
        )

    def _extract_headings(self, content: str) -> List[str]:
        """Extract heading hierarchy from markdown content."""
        if not content:
            return []

        headings = []
        for line in content.split('\n'):
            stripped = line.strip()
            if stripped.startswith('#'):
                # Count the number of # symbols to get heading level
                level = 0
                for char in stripped:
                    if char == '#':
                        level += 1
                    else:
                        break
                # Extract the heading text (remove # and leading/trailing spaces)
                heading_text = stripped[level:].strip()
                if heading_text:
                    headings.append(f"{'#' * level} {heading_text}")
        return headings

    def _extract_code_blocks(self, content: str) -> List[str]:
        """Extract code blocks from markdown content."""
        if not content:
            return []

        code_blocks = []
        lines = content.split('\n')
        in_code_block = False
        current_block = []

        for line in lines:
            if line.startswith('```'):
                if in_code_block:
                    # End of code block
                    code_blocks.append('\n'.join(current_block))
                    current_block = []
                    in_code_block = False
                else:
                    # Start of code block
                    in_code_block = True
                    current_block.append(line)
            elif in_code_block:
                current_block.append(line)

        # Handle case where content ends while still in a code block
        if in_code_block and current_block:
            code_blocks.append('\n'.join(current_block))

        return code_blocks

    async def _log_execution(
        self,
        agent_type: str,
        grounding_policy: str,
        skills_used: List[str],
        skills_detail: List[Dict[str, Any]],
        token_count: int,
        model: str,
        latency_ms: int,
        cached: bool,
        request_payload: Dict[str, Any]
    ):
        """Log the execution to the database."""
        # Extract relevant metadata from request payload
        request_metadata = {}

        if 'user_id' in request_payload:
            request_metadata['user_id'] = request_payload['user_id']
        if 'chapter_slug' in request_payload:
            request_metadata['chapter_slug'] = request_payload['chapter_slug']
        if 'request_type' in request_payload:
            request_metadata['request_type'] = request_payload['request_type']

        # Add IP address if available in the payload
        if 'ip_address' in request_payload:
            request_metadata['ip_address'] = request_payload['ip_address']

        # Insert log entry
        try:
            await self.neon_client.insert_agent_execution_log(
                agent_type=agent_type,
                grounding_policy=grounding_policy,
                skills_used=skills_used,
                skills_detail=skills_detail,
                token_count=token_count,
                model=model,
                latency_ms=latency_ms,
                cached=cached,
                request_metadata=request_metadata
            )
        except Exception as e:
            # Log to console if db logging fails, but don't break the main flow
            print(f"Failed to log execution for {agent_type}: {e}")