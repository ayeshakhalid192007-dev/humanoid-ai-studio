"""
Initialize Qdrant collection for curriculum embeddings.

Run once during deployment setup with:
    python backend/scripts/init_qdrant.py

Requirements:
- QDRANT_URL and QDRANT_API_KEY environment variables must be set
- qdrant-client package installed (pip install qdrant-client)

Collection created:
- Name: curriculum
- Vector dimension: 1536 (OpenAI text-embedding-3-small)
- Distance metric: Cosine similarity
- Index: HNSW (Hierarchical Navigable Small World)

Author: Physical AI Platform Team
Date: 2026-02-09
"""
import os
import sys
from typing import Optional

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, HnswConfigDiff


def init_qdrant_collection() -> bool:
    """
    Initialize Qdrant collection with proper configuration.

    Returns:
        bool: True if successful, False otherwise
    """
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")

    if not qdrant_url or not qdrant_api_key:
        print("❌ Error: QDRANT_URL or QDRANT_API_KEY environment variable not set")
        print("   Please set them in .env file or environment")
        return False

    client: Optional[QdrantClient] = None

    try:
        print("🔌 Connecting to Qdrant Cloud...")
        client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        print("✅ Connected successfully")

        collection_name = "curriculum"

        # Check if collection already exists
        print(f"\n🔍 Checking if collection '{collection_name}' exists...")
        collections = client.get_collections()
        existing_names = [col.name for col in collections.collections]

        if collection_name in existing_names:
            print(f"⚠️  Collection '{collection_name}' already exists")
            print("   Skipping creation (collection is already configured)")
            return True

        # Create collection with HNSW index
        print(f"\n📋 Creating collection '{collection_name}'...")
        print("   Configuration:")
        print("     - Vector dimension: 1536 (OpenAI text-embedding-3-small)")
        print("     - Distance metric: Cosine similarity")
        print("     - Index type: HNSW (Hierarchical Navigable Small World)")
        print("     - HNSW parameters:")
        print("       * m: 16 (connections per layer, balanced speed/accuracy)")
        print("       * ef_construct: 100 (construction accuracy)")

        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=1536,  # OpenAI text-embedding-3-small dimension
                distance=Distance.COSINE,  # Cosine similarity for text embeddings
            ),
            hnsw_config=HnswConfigDiff(
                m=16,  # Number of connections per layer
                ef_construct=100,  # Accuracy during index construction
            ),
        )
        print(f"✅ Collection '{collection_name}' created successfully")

        # Verify collection info
        print("\n🔍 Verifying collection configuration...")
        collection_info = client.get_collection(collection_name=collection_name)
        print(f"   Collection name: {collection_info.config.params.vectors.size}")
        print(f"   Vector dimension: {collection_info.config.params.vectors.size}")
        print(f"   Distance metric: {collection_info.config.params.vectors.distance}")
        print(f"   Points count: {collection_info.points_count}")

        print("\n✅ Qdrant collection initialized successfully")
        print("\nNext steps:")
        print("  1. Run backend/scripts/embed_curriculum.py to populate with curriculum chunks")
        print("  2. Verify retrieval with test queries")
        print("\nPerformance expectations:")
        print("  - Vector search: <100ms for 500-800 chunks")
        print("  - Cosine similarity threshold: >0.7 for relevant results")
        print("  - Storage capacity: ~3.6MB for 500 chunks (well within 1GB free tier)")

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"   Type: {type(e).__name__}")
        return False

    finally:
        if client:
            print("\n🔌 Qdrant connection closed")


def main():
    """Main entry point for script execution."""
    print("=" * 70)
    print("Qdrant Collection Initialization")
    print("Physical AI & Humanoid Robotics Platform - RAG Chatbot")
    print("=" * 70)

    success = init_qdrant_collection()

    if success:
        print("\n🎉 Setup complete! Qdrant collection ready for curriculum embeddings.")
        sys.exit(0)
    else:
        print("\n❌ Setup failed. Please check error messages above.")
        print("\nTroubleshooting:")
        print("  1. Verify QDRANT_URL is set correctly (e.g., https://xyz.cloud.qdrant.io)")
        print("  2. Verify QDRANT_API_KEY is valid")
        print("  3. Check network connectivity to Qdrant Cloud")
        print("  4. Ensure Qdrant cluster is active (free tier may suspend)")
        sys.exit(1)


if __name__ == "__main__":
    main()
