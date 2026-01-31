# 🧬 BioSemantica - Biological Discovery Engine

A powerful semantic search engine for biological research powered by AI vector embeddings and multimodal search capabilities.

## 🌟 Features

- **Semantic Search**: Advanced vector-based search using CLIP embeddings
- **Multimodal Support**: Search with text, images, or DNA/protein sequences
- **Content Types**: 
  - Research papers and abstracts
  - Biological images and microscopy
  - DNA/RNA/Protein sequences
  - Experimental protocols and results
- **Smart Filtering**: Filter by year, content type, and organism
- **Beautiful UI**: Modern, responsive 3D interface with animations
- **Real-time Results**: Fast vector similarity search with Qdrant

## 🏗️ Architecture

### Backend
- **Flask** - Python web framework
- **Qdrant** - Vector database for semantic search
- **CLIP** - OpenAI's vision-language model for embeddings
- **Chonkie** - Smart text chunking

### Frontend
- **Vanilla JavaScript** - No framework dependencies
- **Modern CSS** - 3D effects and animations
- **Responsive Design** - Works on all devices

## 📋 Prerequisites

- Python 3.8 or higher
- Node.js (optional, for serving frontend)
- Modern web browser

## 🚀 Quick Start

### 1. Clone/Download the Project

```bash
# If you have the files already, navigate to the directory
cd biosemantica
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Initialize the Database (First Time Only)

The database is already hosted on Qdrant Cloud, but you need to initialize it with data:

```bash
python initialize_db.py
```

This will:
- Connect to the Qdrant cloud instance
- Create the collection
- Index all biological data
- Verify the setup

### 4. Start the Backend Server

```bash
python app.py
```

The backend will start on `http://localhost:8000`

You should see:
```
🧬 BioSemantica API Server
======================================================================
✅ Collection 'biology_multimodal' is ready
   Total points: XXX
   Content types: {...}

Starting server on http://localhost:8000
======================================================================
```

### 5. Open the Frontend

Simply open `index.html` in your web browser, or use a simple HTTP server:

```bash
# Using Python
python -m http.server 3000

# Or using Node.js
npx serve .
```

Then navigate to `http://localhost:3000`

## 🔍 How to Use

### Basic Text Search
1. Enter your query in the search box (e.g., "CRISPR gene editing")
2. Click "Search" or press Enter
3. View results ranked by semantic similarity

### Image Search
1. Click the "Image" upload button
2. Select a biological image
3. Optionally add text context
4. Click "Search"

### Sequence Search
1. Click the "Sequence" upload button
2. Upload a FASTA or sequence file
3. Search for similar sequences

### Filters
- **Year**: Filter results by publication year
- **Content Type**: Filter by text, image, sequence, or experiment
- **Organism**: Filter by organism type

## 📁 Project Structure

```
biosemantica/
├── app.py                              # Flask backend server
├── initialize_db.py                     # Database initialization script
├── biology_data_with_images_fixed.json # Biology dataset
├── requirements.txt                     # Python dependencies
├── index.html                          # Frontend HTML
├── style.css                           # Frontend styles
├── script.js                           # Frontend JavaScript
└── README.md                           # This file
```

## 🛠️ API Endpoints

### GET `/api/health`
Check if the API is running

### GET `/api/collection-info`
Get information about the database collection

### POST `/api/search`
Perform semantic search

**Request Body:**
```json
{
  "query": "search text",
  "image": "base64_encoded_image",
  "top_k": 10,
  "content_type": "text",
  "year": 2024
}
```

**Response:**
```json
{
  "success": true,
  "results": [...],
  "count": 10
}
```

### POST `/api/initialize`
Initialize or recreate the database collection

## 🎨 Customization

### Modify Search Results
Edit `script.js` and modify the `createResultCard()` function

### Change Styling
Edit `style.css` to customize colors, animations, and layout

### Add More Data
Edit `biology_data_with_images_fixed.json` and re-run `initialize_db.py`

## 🔧 Configuration

### Backend Configuration (app.py)
```python
QDRANT_URL = "your-qdrant-url"
QDRANT_API_KEY = "your-api-key"
COLLECTION_NAME = "biology_multimodal"
```

### Frontend Configuration (script.js)
```javascript
const API_ENDPOINT = 'http://localhost:8000/api/search';
```

## 📊 Database Schema

### Text Documents
- content: Text content
- metadata: {title, authors, year, journal, keywords}
- content_type: "text"

### Images
- description: Image description
- metadata: {title, type, date}
- content_type: "image"

### Sequences
- sequence: DNA/RNA/Protein sequence
- metadata: {gene, organism, function}
- content_type: "sequence"

### Experiments
- conditions: Experimental conditions
- results: Experimental results
- metadata: {title, year, protocol}
- content_type: "experiment"

## 🐛 Troubleshooting

### Backend won't start
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.8+)
- Verify Qdrant credentials are correct

### Frontend can't connect to backend
- Make sure backend is running on port 8000
- Check browser console for CORS errors
- Verify API_ENDPOINT in script.js matches backend URL

### Search returns no results
- Initialize the database: `python initialize_db.py`
- Check collection info: Visit `http://localhost:8000/api/collection-info`
- Verify data file exists: `biology_data_with_images_fixed.json`

### Slow search performance
- Reduce `top_k` value in search requests
- Use content type filters to narrow search
- Check network connection to Qdrant cloud

## 🚀 Deployment

### Deploy Backend
1. Use a platform like Heroku, Railway, or DigitalOcean
2. Set environment variables for Qdrant credentials
3. Install dependencies from requirements.txt
4. Run `python app.py`

### Deploy Frontend
1. Upload files to Netlify, Vercel, or GitHub Pages
2. Update API_ENDPOINT in script.js to your backend URL
3. Deploy!

## 📝 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## 👥 Credits

- Built for the Vector in Orbits Hackathon
- Powered by Qdrant, OpenAI CLIP, and Flask
- Modern UI inspired by biological research tools

## 📧 Contact

For questions or support, please open an issue on the repository.
