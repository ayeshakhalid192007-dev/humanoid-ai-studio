"""Service Registry and Repository Pattern Implementation."""

import asyncio
from typing import Dict, Type, Any, Optional, Protocol
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager

from ..db.neon_client import NeonClient
from .embedder import Embedder
from .rag_pipeline import RAGPipeline
from .chapter_retriever import ChapterRetriever


class Service(ABC):
    """Base interface for all services."""

    async def initialize(self):
        """Initialize the service."""
        pass

    async def shutdown(self):
        """Shutdown and cleanup the service."""
        pass


class Repository(ABC):
    """Base repository interface with common CRUD operations."""

    @abstractmethod
    async def get(self, key: Any) -> Optional[Any]:
        """Get an entity by key."""
        pass

    @abstractmethod
    async def create(self, entity: Any) -> Any:
        """Create a new entity."""
        pass

    @abstractmethod
    async def update(self, key: Any, entity: Any) -> Optional[Any]:
        """Update an existing entity."""
        pass

    @abstractmethod
    async def delete(self, key: Any) -> bool:
        """Delete an entity."""
        pass

    @abstractmethod
    async def list(self, **filters) -> list:
        """List entities with optional filtering."""
        pass


class ServiceRepository(Protocol):
    """Protocol defining service repository contracts."""

    @abstractmethod
    async def get_neon_client(self) -> NeonClient:
        """Get a neon database client."""
        pass


class ServiceRegistry:
    """Centralized registry for service discovery and management."""

    def __init__(self):
        self._services: Dict[str, Service] = {}
        self._repositories: Dict[str, Repository] = {}
        self._initialized = False

    async def initialize(self):
        """Initialize all registered services."""
        if self._initialized:
            return

        for service_name, service in self._services.items():
            await service.initialize()

        # Special initialization for Neon database clients
        if 'neon_client' in self._services:
            neon_client: NeonClient = self._services['neon_client']
            await neon_client.connect()

        self._initialized = True

    async def shutdown(self):
        """Shutdown all registered services."""
        for service_name, service in self._services.items():
            await service.shutdown()

        # Close Neon database connections
        if 'neon_client' in self._services:
            neon_client: NeonClient = self._services['neon_client']
            await neon_client.close()

        self._initialized = False

    def register_service(self, name: str, service: Service):
        """Register a service in the registry."""
        self._services[name] = service

    def get_service(self, name: str) -> Optional[Service]:
        """Get a service by name."""
        return self._services.get(name)

    def get_service_typed(self, name: str, service_type: Type) -> Optional[Service]:
        """Get a service with type checking."""
        service = self._services.get(name)
        if service and isinstance(service, service_type):
            return service
        return None

    def register_repository(self, name: str, repository: Repository):
        """Register a repository in the registry."""
        self._repositories[name] = repository

    def get_repository(self, name: str) -> Optional[Repository]:
        """Get a repository by name."""
        return self._repositories.get(name)

    async def get_neon_client(self) -> Optional[NeonClient]:
        """Helper method to get the neon client if registered."""
        service = self.get_service('neon_client')
        if isinstance(service, NeonClient):
            return service
        return None

    def get_all_services(self) -> Dict[str, Service]:
        """Get all registered services."""
        return self._services.copy()

    def get_all_repositories(self) -> Dict[str, Repository]:
        """Get all registered repositories."""
        return self._repositories.copy()


# Repository implementations
class BaseRepository(Repository):
    """Base implementation of repository pattern."""

    def __init__(self, neon_client: NeonClient):
        self.neon_client = neon_client

    async def get(self, key: Any) -> Optional[Any]:
        # Default implementation - override in subclasses
        return None

    async def create(self, entity: Any) -> Any:
        # Default implementation - override in subclasses
        return entity

    async def update(self, key: Any, entity: Any) -> Optional[Any]:
        # Default implementation - override in subclasses
        return None

    async def delete(self, key: Any) -> bool:
        # Default implementation - override in subclasses
        return False

    async def list(self, **filters) -> list:
        # Default implementation - override in subclasses
        return []


class PersonalizedContentRepository(BaseRepository):
    """Repository for personalized content operations."""

    async def get_personalized_content(self, user_id: str, chapter_slug: str,
                                     content_version: str = None, prompt_version: str = None) -> Optional[Dict]:
        """Get personalized content for a user and chapter."""
        return await self.neon_client.get_personalized_content(
            user_id, chapter_slug, content_version, prompt_version
        )

    async def create_personalized_content(self, user_id: str, chapter_slug: str,
                                        personalized_markdown: str, user_profile_snapshot: dict,
                                        content_version: str, prompt_version: str = "") -> int:
        """Create personalized content record."""
        return await self.neon_client.upsert_personalized_content(
            user_id, chapter_slug, personalized_markdown, user_profile_snapshot,
            content_version, prompt_version
        )

    async def update_personalized_content(self, user_id: str, chapter_slug: str,
                                        personalized_markdown: str, user_profile_snapshot: dict,
                                        content_version: str, prompt_version: str = "") -> int:
        """Update personalized content record (same as create since it's upsert)."""
        return await self.neon_client.upsert_personalized_content(
            user_id, chapter_slug, personalized_markdown, user_profile_snapshot,
            content_version, prompt_version
        )

    async def get(self, key: tuple) -> Optional[Dict]:
        """Get by (user_id, chapter_slug)."""
        user_id, chapter_slug = key
        return await self.get_personalized_content(user_id, chapter_slug)

    async def create(self, entity: Dict) -> Dict:
        """Create personalized content."""
        if not all(k in entity for k in ['user_id', 'chapter_slug', 'personalized_markdown', 'user_profile_snapshot', 'content_version']):
            raise ValueError("Missing required fields for personalized content")

        await self.create_personalized_content(
            entity['user_id'], entity['chapter_slug'],
            entity['personalized_markdown'], entity['user_profile_snapshot'],
            entity['content_version'], entity.get('prompt_version', '')
        )
        return entity

    async def update(self, key: tuple, entity: Dict) -> Optional[Dict]:
        """Update personalized content."""
        user_id, chapter_slug = key
        await self.update_personalized_content(
            user_id, chapter_slug,
            entity.get('personalized_markdown', ''),
            entity.get('user_profile_snapshot', {}),
            entity.get('content_version', ''),
            entity.get('prompt_version', '')
        )
        return entity

    async def delete(self, key: tuple) -> bool:
        """Delete is not supported for this entity (upsert only)."""
        return False  # In current schema, deletion requires custom method

    async def list(self, **filters) -> list:
        """List is not directly supported for this entity without custom implementation."""
        return []


class UrduTranslationRepository(BaseRepository):
    """Repository for Urdu translation operations."""

    async def get_urdu_translation(self, chapter_slug: str,
                                 content_version: str = None, prompt_version: str = None) -> Optional[Dict]:
        """Get Urdu translation for a chapter."""
        return await self.neon_client.get_urdu_translation(
            chapter_slug, content_version, prompt_version
        )

    async def create_urdu_translation(self, chapter_slug: str,
                                    urdu_markdown: str, content_version: str, prompt_version: str = "") -> int:
        """Create Urdu translation record."""
        return await self.neon_client.upsert_urdu_translation(
            chapter_slug, urdu_markdown, content_version, prompt_version
        )

    async def update_urdu_translation(self, chapter_slug: str,
                                    urdu_markdown: str, content_version: str, prompt_version: str = "") -> int:
        """Update Urdu translation record (same as create since it's upsert)."""
        return await self.neon_client.upsert_urdu_translation(
            chapter_slug, urdu_markdown, content_version, prompt_version
        )

    async def get(self, key: str) -> Optional[Dict]:
        """Get by chapter_slug."""
        return await self.get_urdu_translation(key)

    async def create(self, entity: Dict) -> Dict:
        """Create Urdu translation."""
        if not all(k in entity for k in ['chapter_slug', 'urdu_markdown', 'content_version']):
            raise ValueError("Missing required fields for Urdu translation")

        await self.create_urdu_translation(
            entity['chapter_slug'], entity['urdu_markdown'],
            entity['content_version'], entity.get('prompt_version', '')
        )
        return entity

    async def update(self, key: str, entity: Dict) -> Optional[Dict]:
        """Update Urdu translation."""
        await self.update_urdu_translation(
            key,
            entity.get('urdu_markdown', ''),
            entity.get('content_version', ''),
            entity.get('prompt_version', '')
        )
        return entity

    async def delete(self, key: str) -> bool:
        """Delete is not supported for this entity (upsert only)."""
        return False  # In current schema, deletion requires custom method

    async def list(self, **filters) -> list:
        """List is not directly supported for this entity without custom implementation."""
        return []


# Global registry instance
_service_registry: Optional[ServiceRegistry] = None


async def get_service_registry() -> ServiceRegistry:
    """Get the global service registry instance."""
    global _service_registry
    if _service_registry is None:
        _service_registry = ServiceRegistry()
        await _service_registry.initialize()
    return _service_registry


async def initialize_services(neon_client: Optional[NeonClient] = None) -> ServiceRegistry:
    """Initialize and register all services."""
    registry = await get_service_registry()

    # Register the neon client if provided
    if neon_client:
        registry.register_service('neon_client', neon_client)
        # Register repositories that use the neon client
        registry.register_repository('personalized_content', PersonalizedContentRepository(neon_client))
        registry.register_repository('urdu_translation', UrduTranslationRepository(neon_client))

    # Register business services
    registry.register_service('embedder', Embedder())
    registry.register_service('rag_pipeline', RAGPipeline())
    registry.register_service('chapter_retriever', ChapterRetriever())

    return registry