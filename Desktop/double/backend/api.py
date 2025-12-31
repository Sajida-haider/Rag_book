"""Simple Flask API for the RAG system to allow querying book content"""

import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import sys
import os

# Add the backend directory to the path so we can import our modules
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from services.rag_service import RAGService

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize the RAG service
rag_service = RAGService()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'RAG service is running'})

@app.route('/query', methods=['POST'])
def query_endpoint():
    """Query endpoint to ask questions about the book content"""
    try:
        data = request.get_json()

        if not data or 'question' not in data:
            return jsonify({'error': 'Question is required'}), 400

        question = data['question']
        top_k = data.get('top_k', 5)  # Number of results to return
        max_context_length = data.get('max_context_length', 2000)  # Max context length

        logger.info(f"Received query: {question}")

        # Get the RAG response
        if data.get('mode') == 'context':
            # Return just the context that would be used for generation
            context = rag_service.get_context_for_generation(question, max_context_length)
            return jsonify({
                'question': question,
                'context': context,
                'mode': 'context'
            })
        elif data.get('mode') == 'search':
            # Return the raw search results
            results = rag_service.query(question, top_k)
            return jsonify({
                'question': question,
                'results': results,
                'mode': 'search'
            })
        else:
            # Default: return the full answer (context)
            answer = rag_service.answer_question(question, max_context_length)
            return jsonify({
                'question': question,
                'answer': answer,
                'mode': 'answer'
            })

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/search', methods=['POST'])
def search_endpoint():
    """Search endpoint for keyword-based search"""
    try:
        data = request.get_json()

        if not data or 'keywords' not in data:
            return jsonify({'error': 'Keywords are required'}), 400

        keywords = data['keywords']
        top_k = data.get('top_k', 5)

        logger.info(f"Received search: {keywords}")

        results = rag_service.search_by_keywords(keywords, top_k)

        return jsonify({
            'keywords': keywords,
            'results': results
        })

    except Exception as e:
        logger.error(f"Error processing search: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/docs', methods=['GET'])
def get_all_docs():
    """Get all stored documentation content"""
    try:
        docs = rag_service.get_all_documentation()
        return jsonify({
            'total_documents': len(docs),
            'documents': docs
        })
    except Exception as e:
        logger.error(f"Error retrieving documentation: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)