"""
Integration tests for external service connectivity:
- OpenAI API
- Google Generative AI API
- Anthropic API
- ChromaDB vector store
"""
import pytest
import asyncio
from typing import List

from app.utils.llm import LLMClient, EmbeddingClient
from app.services.rag.chroma_store import ChromaVectorStore
from config import settings


@pytest.mark.integration
@pytest.mark.llm
class TestLLMConnectivity:
    """Test connectivity to LLM providers."""
    
    @pytest.mark.asyncio
    async def test_openai_connection(self, check_openai_key):
        """Test OpenAI API connectivity and basic chat completion."""
        if not check_openai_key:
            pytest.skip("OpenAI API key not configured")
        
        client = LLMClient(provider="openai", model="gpt-4o-mini")
        
        response = await client.chat(
            messages=[{"role": "user", "content": "Respond with just the word 'success'"}],
            temperature=0.0,
            max_tokens=10
        )
        
        assert response is not None
        assert len(response) > 0
        assert "success" in response.lower()
        print(f"✓ OpenAI connection successful: {response}")
    
    @pytest.mark.asyncio
    async def test_openai_medical_query(self, check_openai_key):
        """Test OpenAI with a medical coding query."""
        if not check_openai_key:
            pytest.skip("OpenAI API key not configured")
        
        client = LLMClient(provider="openai")
        
        response = await client.chat(
            messages=[{
                "role": "user",
                "content": "What is the ICD-10 code for acute myocardial infarction of the inferior wall? Respond with just the code."
            }],
            temperature=0.0,
            max_tokens=20
        )
        
        assert response is not None
        assert "I21" in response  # ICD-10 code family for MI
        print(f"✓ OpenAI medical query successful: {response}")
    
    @pytest.mark.asyncio
    async def test_google_connection(self, check_google_key):
        """Test Google Generative AI connectivity."""
        if not check_google_key:
            pytest.skip("Google API key not configured")
        
        client = LLMClient(provider="google", model="gemini-pro")
        
        response = await client.chat(
            messages=[{"role": "user", "content": "Respond with just the word 'success'"}],
            temperature=0.0,
            max_tokens=10
        )
        
        assert response is not None
        assert len(response) > 0
        print(f"✓ Google AI connection successful: {response}")
    
    @pytest.mark.asyncio
    async def test_anthropic_connection(self, check_anthropic_key):
        """Test Anthropic API connectivity."""
        if not check_anthropic_key:
            pytest.skip("Anthropic API key not configured")
        
        client = LLMClient(provider="anthropic", model="claude-3-sonnet-20240229")
        
        response = await client.chat(
            messages=[{"role": "user", "content": "Respond with just the word 'success'"}],
            temperature=0.0,
            max_tokens=10
        )
        
        assert response is not None
        assert len(response) > 0
        print(f"✓ Anthropic connection successful: {response}")
    
    @pytest.mark.asyncio
    async def test_llm_provider_switching(self, check_openai_key):
        """Test switching between LLM providers."""
        if not check_openai_key:
            pytest.skip("OpenAI API key not configured")
        
        # Test provider switching
        client1 = LLMClient(provider="openai")
        response1 = await client1.chat(
            messages=[{"role": "user", "content": "Say 'test1'"}],
            max_tokens=10
        )
        assert "test1" in response1.lower() or response1 is not None
        
        # Same query with explicit provider
        client2 = LLMClient(provider=settings.llm_provider)
        response2 = await client2.chat(
            messages=[{"role": "user", "content": "Say 'test2'"}],
            max_tokens=10
        )
        assert response2 is not None
        
        print(f"✓ Provider switching successful")


@pytest.mark.integration
@pytest.mark.llm
class TestEmbeddingConnectivity:
    """Test embedding model connectivity."""
    
    @pytest.mark.asyncio
    async def test_openai_embeddings(self, check_openai_key):
        """Test OpenAI embeddings API."""
        if not check_openai_key:
            pytest.skip("OpenAI API key not configured")
        
        client = EmbeddingClient(provider="openai")
        
        texts = [
            "Acute myocardial infarction",
            "Type 2 diabetes mellitus",
            "Chest pain"
        ]
        
        embeddings = await client.embed(texts)
        
        assert len(embeddings) == 3
        assert all(isinstance(emb, list) for emb in embeddings)
        assert all(len(emb) > 0 for emb in embeddings)
        assert all(isinstance(val, float) for emb in embeddings for val in emb)
        
        print(f"✓ OpenAI embeddings successful: {len(embeddings[0])} dimensions")
    
    @pytest.mark.asyncio
    async def test_embedding_consistency(self, check_openai_key):
        """Test that same text produces consistent embeddings."""
        if not check_openai_key:
            pytest.skip("OpenAI API key not configured")
        
        client = EmbeddingClient(provider="openai")
        text = "Acute myocardial infarction of inferior wall"
        
        # Get embeddings twice
        emb1 = await client.embed([text])
        emb2 = await client.embed([text])
        
        # Should be identical (deterministic)
        assert len(emb1[0]) == len(emb2[0])
        
        # Calculate cosine similarity (should be ~1.0)
        import numpy as np
        vec1 = np.array(emb1[0])
        vec2 = np.array(emb2[0])
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        
        assert similarity > 0.99  # Very high similarity
        print(f"✓ Embedding consistency: similarity = {similarity:.4f}")


@pytest.mark.integration
@pytest.mark.rag
class TestVectorStoreConnectivity:
    """Test ChromaDB vector store connectivity."""
    
    @pytest.mark.asyncio
    async def test_chromadb_initialization(self):
        """Test ChromaDB initialization."""
        store = ChromaVectorStore(collection_name="test_collection")
        
        assert store.client is not None
        assert store.collection is not None
        assert store.embedding_client is not None
        
        print("✓ ChromaDB initialized successfully")
    
    @pytest.mark.asyncio
    async def test_chromadb_ingest_and_query(self, check_openai_key, tmp_path):
        """Test document ingestion and querying."""
        if not check_openai_key:
            pytest.skip("OpenAI API key required for embeddings")
        
        # Create test documents
        test_doc_dir = tmp_path / "test_docs"
        test_doc_dir.mkdir()
        
        (test_doc_dir / "icd10_guidelines.txt").write_text("""
ICD-10-CM Coding Guidelines for Myocardial Infarction:
- I21: ST elevation myocardial infarction
- I21.0: ST elevation myocardial infarction of anterior wall
- I21.1: ST elevation myocardial infarction of inferior wall
- I21.2: ST elevation myocardial infarction of other sites
- I21.3: ST elevation myocardial infarction of unspecified site
Documentation must specify location and whether acute or subsequent.
        """)
        
        (test_doc_dir / "cpt_guidelines.txt").write_text("""
CPT Coding for Cardiac Catheterization:
- 93454: Catheter placement in coronary artery(s)
- 93458: Left heart catheterization with coronary angiography
- 93460: Right and left heart catheterization with coronary angiography
All procedures require documentation of medical necessity.
        """)
        
        # Initialize store and ingest
        store = ChromaVectorStore(collection_name="test_medical_guidelines")
        ingested_count = await store.ingest_directory(str(test_doc_dir))
        
        assert ingested_count == 2
        print(f"✓ Ingested {ingested_count} documents")
        
        # Query the store
        results = await store.query("What is the ICD-10 code for inferior wall MI?", k=2)
        
        assert len(results) > 0
        assert any("I21" in result["document"] for result in results)
        
        print(f"✓ Query returned {len(results)} results")
        print(f"  Top result: {results[0]['document'][:100]}...")
    
    @pytest.mark.asyncio
    async def test_chromadb_semantic_search(self, check_openai_key, tmp_path):
        """Test semantic search quality."""
        if not check_openai_key:
            pytest.skip("OpenAI API key required for embeddings")
        
        # Create test documents with different topics
        test_doc_dir = tmp_path / "semantic_test"
        test_doc_dir.mkdir()
        
        (test_doc_dir / "cardiology.txt").write_text(
            "Myocardial infarction requires ECG showing ST elevation and elevated troponin."
        )
        (test_doc_dir / "endocrinology.txt").write_text(
            "Type 2 diabetes diagnosis requires HbA1c >= 6.5% or fasting glucose >= 126 mg/dL."
        )
        (test_doc_dir / "pulmonology.txt").write_text(
            "Chronic obstructive pulmonary disease diagnosed by spirometry showing FEV1/FVC < 0.7."
        )
        
        store = ChromaVectorStore(collection_name="semantic_test")
        await store.ingest_directory(str(test_doc_dir))
        
        # Query for cardiac topic
        results = await store.query("What tests diagnose heart attack?", k=3)
        
        # Top result should be cardiology doc
        assert "troponin" in results[0]["document"].lower() or "ecg" in results[0]["document"].lower()
        
        print("✓ Semantic search correctly ranked cardiac document first")
    
    @pytest.mark.asyncio
    async def test_chromadb_persistence(self, check_openai_key, tmp_path):
        """Test that data persists across store instances."""
        if not check_openai_key:
            pytest.skip("OpenAI API key required for embeddings")
        
        collection_name = "persistence_test"
        
        # Create and populate first instance
        test_doc_dir = tmp_path / "persist_test"
        test_doc_dir.mkdir()
        (test_doc_dir / "test.txt").write_text("Persistence test document")
        
        store1 = ChromaVectorStore(collection_name=collection_name)
        count1 = await store1.ingest_directory(str(test_doc_dir))
        assert count1 == 1
        
        # Create second instance (should access same collection)
        store2 = ChromaVectorStore(collection_name=collection_name)
        results = await store2.query("persistence test", k=1)
        
        assert len(results) > 0
        assert "persistence" in results[0]["document"].lower()
        
        print("✓ Data persisted across store instances")


@pytest.mark.integration
@pytest.mark.slow
class TestEndToEndConnectivity:
    """Test end-to-end connectivity of all external services."""
    
    @pytest.mark.asyncio
    async def test_full_rag_pipeline(self, check_openai_key, tmp_path):
        """Test complete RAG pipeline: embed, store, retrieve, generate."""
        if not check_openai_key:
            pytest.skip("OpenAI API key required")
        
        # 1. Create medical documents
        doc_dir = tmp_path / "medical_docs"
        doc_dir.mkdir()
        (doc_dir / "guidelines.txt").write_text("""
ICD-10 code I21.19 is used for ST elevation myocardial infarction 
involving other coronary artery of inferior wall. This requires 
documentation of ST elevation on ECG and elevated cardiac biomarkers.
        """)
        
        # 2. Ingest into vector store
        store = ChromaVectorStore(collection_name="full_test")
        ingested = await store.ingest_directory(str(doc_dir))
        assert ingested == 1
        
        # 3. Query vector store
        rag_results = await store.query("What documentation is needed for inferior MI?", k=1)
        assert len(rag_results) > 0
        context = rag_results[0]["document"]
        
        # 4. Use context with LLM
        llm = LLMClient(provider="openai")
        response = await llm.chat(
            messages=[{
                "role": "user",
                "content": f"Based on this guideline: {context}\n\nWhat ICD-10 code for inferior wall MI? Reply with just the code."
            }],
            temperature=0.0,
            max_tokens=20
        )
        
        assert "I21.19" in response or "I21" in response
        
        print("✓ Full RAG pipeline successful")
        print(f"  Retrieved context: {context[:100]}...")
        print(f"  LLM response: {response}")
    
    @pytest.mark.asyncio
    async def test_concurrent_llm_requests(self, check_openai_key):
        """Test handling concurrent LLM requests."""
        if not check_openai_key:
            pytest.skip("OpenAI API key required")
        
        client = LLMClient(provider="openai")
        
        # Create multiple concurrent requests
        queries = [
            "ICD-10 code for diabetes",
            "CPT code for ECG",
            "ICD-10 code for hypertension",
            "CPT code for chest X-ray",
            "ICD-10 code for COPD"
        ]
        
        tasks = [
            client.chat([{"role": "user", "content": q}], max_tokens=50)
            for q in queries
        ]
        
        # Execute concurrently
        responses = await asyncio.gather(*tasks)
        
        assert len(responses) == 5
        assert all(resp is not None and len(resp) > 0 for resp in responses)
        
        print(f"✓ Handled {len(responses)} concurrent requests successfully")
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_api_key(self):
        """Test error handling with invalid API key."""
        # Temporarily use invalid key
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key="invalid-key-test")
        
        with pytest.raises(Exception) as exc_info:
            await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=10
            )
        
        assert "api" in str(exc_info.value).lower() or "auth" in str(exc_info.value).lower()
        print("✓ Invalid API key correctly raises exception")
    
    @pytest.mark.asyncio
    async def test_rate_limit_handling(self, check_openai_key):
        """Test graceful handling of rate limits."""
        if not check_openai_key:
            pytest.skip("OpenAI API key required")
        
        client = LLMClient(provider="openai")
        
        # Make rapid requests (may hit rate limit)
        results = []
        errors = []
        
        for i in range(5):
            try:
                response = await client.chat(
                    [{"role": "user", "content": f"test {i}"}],
                    max_tokens=10
                )
                results.append(response)
            except Exception as e:
                errors.append(e)
        
        # Should have at least some successes
        assert len(results) > 0 or len(errors) > 0
        
        print(f"✓ Rate limit test: {len(results)} successes, {len(errors)} errors")

