

import json
import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from qdrant_client import QdrantClient, models
from fastembed import TextEmbedding, SparseTextEmbedding, LateInteractionTextEmbedding
from chonkie import SemanticChunker

@dataclass
class Chunk:
    """Représente un morceau de texte avec ses métadonnées"""
    text: str
    source_id: int
    chunk_id: int
    metadata: Dict[str, Any]
    source_type: str  # 'text', 'sequence', 'image', 'experiment'


def prepare_biology_data(json_path: str, chunker: SemanticChunker) -> List[Chunk]:
 
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    all_chunks = []
    source_id = 0
    
    # 1. Traiter les TEXTES (abstracts, protocols)
    if 'texts' in data:
        for text_item in data['texts']:
            content = text_item.get('content', '')
            metadata = text_item.get('metadata', {})
            metadata['source'] = text_item.get('source', 'unknown')
            
            # Utiliser chonkie pour chunker
            chonkie_chunks = chunker.chunk(content)
            
            # Convertir en objets Chunk personnalisés
            chunks = []
            for chunk_id, chonkie_chunk in enumerate(chonkie_chunks):
                chunks.append(Chunk(
                    text=chonkie_chunk.text,
                    source_id=source_id,
                    chunk_id=chunk_id,
                    metadata=metadata,
                    source_type='text'
                ))
            
            all_chunks.extend(chunks)
            source_id += 1
    
    # 2. Traiter les SEQUENCES (ADN, protéines)
    if 'sequences' in data:
        for seq_item in data['sequences']:
            sequence = seq_item.get('sequence', '')
            metadata = seq_item.get('metadata', {})
            metadata['sequence_type'] = seq_item.get('type', 'unknown')
            
            # Créer une description textuelle de la séquence
            gene_name = metadata.get('gene', metadata.get('protein_name', 'Unknown'))
            function = metadata.get('function', 'Unknown function')
            seq_length = len(sequence)
            
            description = f"Gene/Protein: {gene_name}. Function: {function}. "
            description += f"Sequence length: {seq_length} bp/aa. "
            description += f"Type: {metadata['sequence_type']}. "
            
            # Ajouter des informations supplémentaires si disponibles
            if 'organism' in metadata:
                description += f"Organism: {metadata['organism']}. "
            if 'expression_level' in metadata:
                description += f"Expression level: {metadata['expression_level']}. "
            if 'applications' in metadata:
                description += f"Applications: {', '.join(metadata['applications'])}. "
            
            # Stocker aussi la séquence complète dans les métadonnées
            metadata['full_sequence'] = sequence
            
            # Utiliser chonkie pour chunker la description
            chonkie_chunks = chunker.chunk(description)
            
            chunks = []
            for chunk_id, chonkie_chunk in enumerate(chonkie_chunks):
                chunks.append(Chunk(
                    text=chonkie_chunk.text,
                    source_id=source_id,
                    chunk_id=chunk_id,
                    metadata=metadata,
                    source_type='sequence'
                ))
            
            all_chunks.extend(chunks)
            source_id += 1
    
    # 3. Traiter les IMAGES
    if 'images' in data:
        for img_item in data['images']:
            description = img_item.get('image_description', '')
            metadata = img_item.get('metadata', {})
            metadata['image_path'] = img_item.get('image_path', '')
            
            # Utiliser chonkie pour chunker
            chonkie_chunks = chunker.chunk(description)
            
            chunks = []
            for chunk_id, chonkie_chunk in enumerate(chonkie_chunks):
                chunks.append(Chunk(
                    text=chonkie_chunk.text,
                    source_id=source_id,
                    chunk_id=chunk_id,
                    metadata=metadata,
                    source_type='image'
                ))
            
            all_chunks.extend(chunks)
            source_id += 1
    
    # 4. Traiter les EXPÉRIENCES
    if 'experiments' in data:
        for exp_item in data['experiments']:
            description = exp_item.get('description', '')
            conditions = exp_item.get('conditions', {})
            results = exp_item.get('results', {})
            metadata = exp_item.get('metadata', {})
            
            # Enrichir la description avec les conditions et résultats
            full_text = f"Experiment: {description}\n\n"
            full_text += f"Conditions: {json.dumps(conditions, indent=2)}\n\n"
            full_text += f"Results: {json.dumps(results, indent=2)}"
            
            metadata['experiment_success'] = results.get('success', False)
            
            # Utiliser chonkie pour chunker
            chonkie_chunks = chunker.chunk(full_text)
            
            chunks = []
            for chunk_id, chonkie_chunk in enumerate(chonkie_chunks):
                chunks.append(Chunk(
                    text=chonkie_chunk.text,
                    source_id=source_id,
                    chunk_id=chunk_id,
                    metadata=metadata,
                    source_type='experiment'
                ))
            
            all_chunks.extend(chunks)
            source_id += 1
    
    print(f"✓ Préparé {len(all_chunks)} chunks à partir de {source_id} sources")
    return all_chunks


# ============================================================================
# SYSTÈME DE RECHERCHE HYBRIDE
# ============================================================================

class BiologyHybridSearch:

    def __init__(self, qdrant_url: str, api_key: str):
        # Configuration Qdrant
        self.client = QdrantClient(url=qdrant_url, api_key=api_key)
        self.collection_name = "biology_hybrid_search"
        
        # Modèles d'embedding
        self.dense_model = TextEmbedding("sentence-transformers/all-MiniLM-L6-v2")
        self.sparse_model = SparseTextEmbedding("prithivida/Splade_PP_en_v1")
        self.colbert_model = LateInteractionTextEmbedding("colbert-ir/colbertv2.0")
        
        print("✓ Modèles d'embedding chargés")
    
    def create_collection(self):
        # Supprimer l'ancienne collection si elle existe
        if self.client.collection_exists(collection_name=self.collection_name):
            self.client.delete_collection(collection_name=self.collection_name)
            print("✓ Ancienne collection supprimée")
        
        # Créer nouvelle collection
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config={
                "dense": models.VectorParams(
                    size=384,
                    distance=models.Distance.COSINE
                ),
                "colbert": models.VectorParams(
                    size=128,
                    distance=models.Distance.COSINE,
                    multivector_config=models.MultiVectorConfig(
                        comparator=models.MultiVectorComparator.MAX_SIM
                    ),
                    hnsw_config=models.HnswConfigDiff(m=0)
                ),
            },
            sparse_vectors_config={
                "sparse": models.SparseVectorParams(
                    index=models.SparseIndexParams(on_disk=False)
                )
            },
        )
        
        # Créer des index pour la recherche
        indexes = [
            ("source_type", "keyword"),
            ("title", "keyword"),
            ("gene", "keyword"),
            ("protein_name", "keyword"),
            ("authors", "text"),
            ("keywords", "keyword"),
        ]
        
        for field_name, field_schema in indexes:
            try:
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name=field_name,
                    field_schema=field_schema,
                )
            except:
                pass  # Index peut déjà exister
        
        print("✓ Collection créée avec succès")
    
    def index_chunks(self, chunks: List[Chunk], batch_size: int = 50):
 
        print(f"\nIndexation de {len(chunks)} chunks...")
        
        # Extraire les textes
        texts = [chunk.text for chunk in chunks]
        
        # Générer les embeddings pour tous les chunks
        print("  - Génération des embeddings dense...")
        dense_embeds = list(self.dense_model.embed(texts, parallel=0))
        
        print("  - Génération des embeddings sparse...")
        sparse_embeds = list(self.sparse_model.embed(texts, parallel=0))
        
        print("  - Génération des embeddings ColBERT...")
        colbert_embeds = list(self.colbert_model.embed(texts, parallel=0))
        
        # Créer les points pour Qdrant
        points = []
        for i, chunk in enumerate(chunks):
            # Préparer le payload
            payload = {
                "text": chunk.text,
                "source_id": chunk.source_id,
                "chunk_id": chunk.chunk_id,
                "source_type": chunk.source_type,
                **chunk.metadata
            }
            
            # Créer le point
            point = models.PointStruct(
                id=i,
                vector={
                    "dense": dense_embeds[i],
                    "sparse": sparse_embeds[i].as_object(),
                    "colbert": colbert_embeds[i],
                },
                payload=payload
            )
            points.append(point)
        
        # Upload par batch
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upload_points(
                collection_name=self.collection_name,
                points=batch
            )
            print(f"  - Uploadé {min(i + batch_size, len(points))}/{len(points)} chunks")
        
        print(f"✓ Indexation terminée : {len(points)} chunks indexés")
    
    def search(
        self,
        query: str,
        top_k: int = 10,
        content_filter: Optional[str] = None,
        year: Optional[int] = None,
        use_reranking: bool = True,
        min_score: Optional[float] = None,
        filters: Optional[Dict[str, Any]] = None,
        prefetch_limit: int = 100
    ) -> List[Dict[str, Any]]:

        # Générer les embeddings de la requête
        query_dense = next(self.dense_model.query_embed(query))
        query_sparse = next(self.sparse_model.query_embed(query)).as_object()
        query_colbert = next(self.colbert_model.query_embed(query))
        
        # Construire les filtres à partir des paramètres
        filter_dict = filters.copy() if filters else {}
        
        if content_filter:
            filter_dict['source_type'] = content_filter
        if year:
            filter_dict['year'] = year
        
        # Construire les filtres Qdrant
        query_filter = None
        if filter_dict:
            conditions = []
            for key, value in filter_dict.items():
                if isinstance(value, list):
                    conditions.append(
                        models.FieldCondition(
                            key=key,
                            match=models.MatchAny(any=value)
                        )
                    )
                else:
                    conditions.append(
                        models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=value)
                        )
                    )
            
            if conditions:
                query_filter = models.Filter(must=conditions)
        
        # Étape 1: Prefetch avec Dense et Sparse
        hybrid_prefetch = [
            models.Prefetch(
                query=query_dense,
                using="dense",
                limit=prefetch_limit
            ),
            models.Prefetch(
                query=query_sparse,
                using="sparse",
                limit=prefetch_limit
            ),
        ]
        
        # Étape 2: Fusion RRF
        fusion_prefetch = models.Prefetch(
            prefetch=hybrid_prefetch,
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            limit=prefetch_limit,
        )
        
        # Étape 3: Reranking final avec ColBERT
        try:
            response = self.client.query_points(
                collection_name=self.collection_name,
                prefetch=fusion_prefetch,
                query=query_colbert,
                using="colbert",
                query_filter=query_filter,
                limit=top_k,
                with_payload=True,
            )
            
            results = response.points if response.points else []
            
            if not results:
                print("❌ Aucun résultat trouvé")
                return []
            
            print(f"✓ {len(results)} résultats trouvés")
            
            # Formater les résultats
            formatted_results = []
            for hit in results:
                result = {
                    "score": hit.score,
                    "text": hit.payload.get("text", ""),
                    "source_type": hit.payload.get("source_type", "unknown"),
                    "metadata": {k: v for k, v in hit.payload.items() 
                               if k not in ["text", "source_id", "chunk_id", "source_type"]}
                }
                formatted_results.append(result)
            
            # Appliquer le filtre de score minimum si spécifié
            if min_score is not None:
                original_count = len(formatted_results)
                formatted_results = [r for r in formatted_results if r['score'] >= min_score]
                if len(formatted_results) < original_count:
                    print(f"⚠️  Filtré {original_count - len(formatted_results)} résultats avec score < {min_score}")
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ Erreur lors de la recherche: {str(e)}")
            return []



    
    

