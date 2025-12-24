#!/usr/bin/env python3
"""
Simple script to start the RAG backend server with error handling
"""
import sys
import os
import traceback
import logging

# Add the ragbot_backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ragbot_backend'))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    logger.info("Importing main module...")
    import main
    logger.info("Successfully imported main module")

    logger.info("Starting server...")
    import uvicorn
    uvicorn.run('ragbot_backend.main:app', host='127.0.0.1', port=8001, timeout_graceful_shutdown=5, log_level="info")

except ImportError as e:
    logger.error(f"Import error: {e}")
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    logger.error(f"Server error: {e}")
    traceback.print_exc()
    sys.exit(1)