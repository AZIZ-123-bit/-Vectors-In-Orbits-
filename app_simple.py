from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import random

app = Flask(__name__)
CORS(app)

print("🧬 Loading BioSemantica Simple Backend...")

# Load the biology data
try:
    with open('biology_data_with_images_fixed.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create a searchable list from all content
    SEARCH_DATA = []
    
    # Add texts
    if 'texts' in data:
        for item in data['texts']:
            SEARCH_DATA.append({
                'content': item.get('content', ''),
                'type': 'text',
                'metadata': item.get('metadata', {})
            })
    
    # Add sequences
    if 'sequences' in data:
        for item in data['sequences']:
            content = f"{item.get('metadata', {}).get('gene', 'Unknown gene')} - {item.get('metadata', {}).get('function', 'Function unknown')}"
            SEARCH_DATA.append({
                'content': content,
                'type': 'sequence',
                'metadata': item.get('metadata', {})
            })
    
    # Add images
    if 'images' in data:
        for item in data['images']:
            SEARCH_DATA.append({
                'content': item.get('image_description', ''),
                'type': 'image',
                'metadata': item.get('metadata', {})
            })
    
    # Add experiments
    if 'experiments' in data:
        for item in data['experiments']:
            SEARCH_DATA.append({
                'content': item.get('description', ''),
                'type': 'experiment',
                'metadata': item.get('metadata', {})
            })
    
    print(f"✅ Loaded {len(SEARCH_DATA)} items from database")
    
except Exception as e:
    print(f"❌ Error loading data: {e}")
    SEARCH_DATA = []

@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "message": "BioSemantica Simple Backend",
        "search_ready": len(SEARCH_DATA) > 0,
        "total_items": len(SEARCH_DATA)
    })

@app.route("/api/collection-info")
def collection_info():
    return jsonify({
        "collection": "biology_simple",
        "status": "ready",
        "points": len(SEARCH_DATA)
    })

@app.route("/api/search", methods=["POST"])
def search():
    try:
        data = request.get_json()
        query = data.get('query', '').lower().strip()
        top_k = int(data.get('top_k', 10))
        content_type = data.get('content_type')
        year = data.get('year')
        
        print(f"🔍 Search: query='{query}', top_k={top_k}, type={content_type}, year={year}")
        
        if not query:
            return jsonify({"success": False, "error": "Query required"}), 400
        
        results = []
        
        for item in SEARCH_DATA:
            # Skip if content type filter doesn't match
            if content_type and item['type'] != content_type:
                continue
            
            # Skip if year filter doesn't match
            if year:
                item_year = item['metadata'].get('year')
                if item_year != int(year):
                    continue
            
            # Simple keyword matching
            content_lower = item['content'].lower()
            score = 0.0
            
            # Check if query words are in content
            query_words = query.split()
            for word in query_words:
                if word in content_lower:
                    score += 0.3
            
            # Bonus for exact phrase match
            if query in content_lower:
                score += 0.5
            
            # Add some randomness for variety
            if score > 0:
                score = min(0.99, score + random.random() * 0.1)
                
                results.append({
                    'content': item['content'][:500],  # Limit content length
                    'score': score,
                    'type': item['type'],
                    'metadata': item['metadata']
                })
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Limit to top_k
        results = results[:top_k]
        
        print(f"   ✅ Found {len(results)} results")
        
        return jsonify({
            "success": True,
            "count": len(results),
            "results": results
        })
        
    except Exception as e:
        print(f"❌ Search error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(".", path)

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🧬 BioSemantica Simple Backend")
    print("=" * 70)
    print(f"📊 {len(SEARCH_DATA)} items ready for search")
    print("🚀 Starting server on http://localhost:8000")
    print("=" * 70)
    print()
    
    app.run(host="0.0.0.0", port=8000, debug=True)