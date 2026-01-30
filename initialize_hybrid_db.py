#!/usr/bin/env python3
"""
BioSemantica Hybrid Search Database Initialization
Indexes biological data using advanced hybrid search with Dense, Sparse, and ColBERT embeddings
"""

import json
from biology_hybrid_search import BiologyHybridSearch, prepare_biology_data
from chonkie import SemanticChunker

# Configuration
QDRANT_URL = "https://6638cf80-266b-4b74-b8cc-aac14899c528.us-east4-0.gcp.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.xA63-tAtaxTSPSPtHU5DywVjpqrn-WhLK-Dn68PN35U"
JSON_PATH = "biology_data_with_images_fixed.json"

def main():
    print("=" * 80)
    print("🧬 BioSemantica Hybrid Search - Database Initialization")
    print("=" * 80)
    print()
    
    # Step 1: Initialize the search system
    print("📦 Step 1: Initializing search system...")
    try:
        search_system = BiologyHybridSearch(QDRANT_URL, QDRANT_API_KEY)
        print("✅ Search system initialized")
    except Exception as e:
        print(f"❌ Error initializing search system: {e}")
        return
    
    # Step 2: Check if collection exists
    print("\n🔍 Step 2: Checking existing collection...")
    try:
        collections = search_system.client.get_collections()
        collection_exists = any(c.name == "biology_hybrid_search" for c in collections.collections)
        
        if collection_exists:
            info = search_system.client.get_collection("biology_hybrid_search")
            print(f"⚠️  Collection already exists with {info.points_count} points")
            response = input("Do you want to recreate it? This will delete all data. (yes/no): ")
            if response.lower() != 'yes':
                print("Keeping existing data. Initialization cancelled.")
                return
    except Exception as e:
        print(f"Note: {e}")
    
    # Step 3: Prepare data
    print("\n📄 Step 3: Preparing biology data...")
    try:
        # Create semantic chunker
        chunker = SemanticChunker(
            chunk_size=1024,
            threshold=0.5
        )
        
        # Load and chunk the data
        chunks = prepare_biology_data(JSON_PATH, chunker)
        
        # Count by type
        type_counts = {}
        for chunk in chunks:
            type_counts[chunk.source_type] = type_counts.get(chunk.source_type, 0) + 1
        
        print("\n📊 Chunk breakdown:")
        for source_type, count in sorted(type_counts.items()):
            print(f"   - {source_type}: {count} chunks")
        
    except FileNotFoundError:
        print(f"❌ Error: {JSON_PATH} not found")
        print("   Please ensure the data file is in the same directory")
        return
    except Exception as e:
        print(f"❌ Error preparing data: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 4: Create collection
    print("\n🗄️  Step 4: Creating collection...")
    try:
        search_system.create_collection()
        print("✅ Collection created")
    except Exception as e:
        print(f"❌ Error creating collection: {e}")
        return
    
    # Step 5: Index chunks
    print("\n📊 Step 5: Indexing chunks (this will take several minutes)...")
    print("   This generates Dense, Sparse, and ColBERT embeddings for optimal search")
    try:
        search_system.index_chunks(chunks, batch_size=50)
        print("✅ All chunks indexed successfully")
    except Exception as e:
        print(f"❌ Error indexing chunks: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 6: Verify
    print("\n✅ Step 6: Verifying setup...")
    try:
        info = search_system.client.get_collection("biology_hybrid_search")
        print(f"\n📊 Collection Information:")
        print(f"   Name: biology_hybrid_search")
        print(f"   Status: Ready")
        print(f"   Total Points: {info.points_count}")
        print(f"   Vectors: Dense (384D), Sparse, ColBERT (128D)")
    except Exception as e:
        print(f"❌ Error verifying setup: {e}")
    
    # Step 7: Test search
    print("\n🔍 Step 7: Running test search...")
    try:
        results = search_system.search(
            query="CRISPR gene editing",
            top_k=3,
            use_reranking=True
        )
        
        if results:
            print(f"✅ Test search successful! Found {len(results)} results")
            print(f"\n   Top result:")
            print(f"   - Type: {results[0]['source_type']}")
            print(f"   - Score: {results[0]['score']:.4f}")
            print(f"   - Text: {results[0]['text'][:100]}...")
        else:
            print("⚠️  Test search returned no results")
    except Exception as e:
        print(f"⚠️  Test search failed: {e}")
    
    print("\n" + "=" * 80)
    print("🎉 Initialization Complete!")
    print("=" * 80)
    print("\n📝 Next steps:")
    print("1. Start the backend: python app_final.py")
    print("2. Open index.html in your browser")
    print("3. Start searching with advanced hybrid search!")
    print("\n💡 Features enabled:")
    print("   - Dense vector search (semantic understanding)")
    print("   - Sparse vector search (keyword matching)")
    print("   - ColBERT reranking (best precision)")
    print("   - RRF fusion (optimal result combination)")
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Initialization cancelled by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
