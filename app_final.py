from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import base64
from PIL import Image
import io
import traceback
import warnings
warnings.filterwarnings('ignore')

# Import the hybrid search system
from biology_hybrid_search import BiologyHybridSearch, prepare_biology_data
from chonkie import SemanticChunker

app = Flask(__name__)
CORS(app)

# ==========================================
# CONFIGURATION
# ==========================================
QDRANT_URL = "https://6638cf80-266b-4b74-b8cc-aac14899c528.us-east4-0.gcp.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.xA63-tAtaxTSPSPtHU5DywVjpqrn-WhLK-Dn68PN35U"
JSON_PATH = "biology_data_with_images_fixed.json"

# ==========================================
# INITIALIZE SEARCH SYSTEM
# ==========================================
print("🧬 Initializing BioSemantica Hybrid Search System...")
print("=" * 70)

try:
    # Initialize the search system
    search_system = BiologyHybridSearch(QDRANT_URL, QDRANT_API_KEY)
    print("✅ Search system initialized successfully")
    
    # Check if collection exists and has data
    try:
        collections = search_system.client.get_collections()
        collection_exists = any(c.name == "biology_hybrid_search" for c in collections.collections)
        
        if collection_exists:
            info = search_system.client.get_collection("biology_hybrid_search")
            if info.points_count > 0:
                print(f"✅ Collection ready with {info.points_count} indexed documents")
            else:
                print("⚠️  Collection exists but is empty. Run initialize_db.py to index data.")
        else:
            print("⚠️  Collection not found. Run initialize_db.py to create and index data.")
    except Exception as e:
        print(f"⚠️  Could not check collection status: {e}")
        
except Exception as e:
    print(f"❌ Failed to initialize search system: {e}")
    search_system = None

# ==========================================
# API ENDPOINTS
# ==========================================

@app.route("/api/health")
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "BioSemantica API is running",
        "search_ready": search_system is not None
    })

@app.route("/api/collection-info")
def collection_info():
    """Get collection information"""
    if not search_system:
        return jsonify({"error": "Search system not initialized"}), 500
    
    try:
        collections = search_system.client.get_collections()
        collection_exists = any(c.name == "biology_hybrid_search" for c in collections.collections)
        
        if not collection_exists:
            return jsonify({
                "collection": "biology_hybrid_search",
                "status": "not_found",
                "points": 0
            })
        
        info = search_system.client.get_collection("biology_hybrid_search")
        return jsonify({
            "collection": "biology_hybrid_search",
            "status": "ready",
            "points": info.points_count,
            "vectors": ["dense", "sparse", "colbert"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/search", methods=["POST"])
def api_search():
    """Main search endpoint"""
    if not search_system:
        return jsonify({
            "success": False,
            "error": "Search system not initialized"
        }), 500
    
    try:
        # Get request data
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON body provided"
            }), 400
        
        # Extract parameters
        query = data.get("query", "").strip()
        image_data = data.get("image")
        top_k = int(data.get("top_k", 10))
        content_type = data.get("content_type")
        year = data.get("year")
        
        # Convert empty strings to None
        if content_type == "" or content_type == "null":
            content_type = None
        if year == "" or year == "null":
            year = None
        else:
            year = int(year) if year else None
        
        # Debug logging
        print(f"🔍 Search Request:")
        print(f"   Query: '{query}'")
        print(f"   Top K: {top_k}")
        print(f"   Content Type: {content_type}")
        print(f"   Year: {year}")
        print(f"   Has Image: {bool(image_data)}")
        
        # Validate input
        if not query and not image_data:
            return jsonify({
                "success": False,
                "error": "Query or image required"
            }), 400
        
        # Handle image search (for now, use image description as query if provided)
        if image_data and not query:
            query = "biological image microscopy"  # Default query for image search
            print("   Using default query for image search")
        
        # Perform search
        results = search_system.search(
            query=query,
            top_k=top_k,
            content_filter=content_type,
            year=year,
            use_reranking=True,
            min_score=None  # No minimum score filter
        )
        
        print(f"   ✅ Found {len(results)} results")
        
        # Format results for frontend
        formatted_results = []
        for result in results:
            formatted_results.append({
                "content": result["text"],
                "score": float(result["score"]),
                "type": result["source_type"],
                "metadata": result["metadata"]
            })
        
        return jsonify({
            "success": True,
            "count": len(formatted_results),
            "results": formatted_results
        })
        
    except Exception as e:
        print("❌ SEARCH ERROR:")
        print(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/initialize", methods=["POST"])
def api_initialize():
    """Initialize or recreate the database"""
    if not search_system:
        return jsonify({
            "success": False,
            "error": "Search system not initialized"
        }), 500
    
    try:
        print("🔄 Initializing database...")
        
        # Create chunker
        chunker = SemanticChunker(
            chunk_size=1024,
            threshold=0.5
        )
        
        # Prepare data
        print("📄 Preparing biology data...")
        chunks = prepare_biology_data(JSON_PATH, chunker)
        
        # Create collection
        print("🗄️ Creating collection...")
        search_system.create_collection()
        
        # Index chunks
        print("📊 Indexing chunks...")
        search_system.index_chunks(chunks, batch_size=50)
        
        print("✅ Database initialized successfully")
        
        return jsonify({
            "success": True,
            "message": f"Indexed {len(chunks)} chunks successfully"
        })
        
    except Exception as e:
        print("❌ INITIALIZATION ERROR:")
        print(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/")
def home():
    """Serve the main page"""
    return send_from_directory(".", "index.html")

@app.route("/<path:path>")
def static_files(path):
    """Serve static files"""
    return send_from_directory(".", path)

# ==========================================
# MAIN
# ==========================================
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🧬 BioSemantica Hybrid Search API")
    print("=" * 70)
    print("🚀 Starting server on http://localhost:8000")
    print("📚 API Endpoints:")
    print("   - GET  /api/health          - Health check")
    print("   - GET  /api/collection-info - Database info")
    print("   - POST /api/search          - Semantic search")
    print("   - POST /api/initialize      - Initialize database")
    print("=" * 70)
    print()
    
    app.run(host="0.0.0.0", port=8000, debug=False, use_reloader=False)
