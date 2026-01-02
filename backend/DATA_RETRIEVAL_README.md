# Data Retrieval and Validation Pipeline

This directory contains the implementation for retrieving data from Qdrant and validating its accuracy, as specified in the feature spec for `006-retrieve-data`.

## Components

### 1. Qdrant Data Retrieval (`retrieve_data.py`)
- Connects to Qdrant vector database
- Retrieves embeddings and metadata
- Handles connection errors gracefully

### 2. Content Verification (`content_verification.py`)
- Compares retrieved chunks with original book text
- Validates text position accuracy
- Generates discrepancy reports

### 3. Metadata Validation (`metadata_validation.py`)
- Validates source URL accessibility
- Cross-references metadata with original documents
- Creates consistency reports

### 4. Pipeline Testing (`pipeline_tests.py`)
- Comprehensive performance testing
- Consistency validation across runs
- Error handling verification
- Generates test reports in Markdown format

### 5. Integration Testing (`integration_test.py`)
- End-to-end pipeline testing
- Validates complete data flow
- Generates comprehensive reports

## Usage

### Running the Data Retrieval
```bash
cd backend
python retrieve_data.py
```

### Running Content Verification
```bash
cd backend
python content_verification.py
```

### Running Metadata Validation
```bash
cd backend
python metadata_validation.py
```

### Running Pipeline Tests
```bash
cd backend
python pipeline_tests.py
```

### Running Integration Tests
```bash
cd backend
python integration_test.py
```

### Running All Tests
```bash
cd backend
python test_retrieve_data.py
```

## Environment Configuration

Create a `.env` file in the backend directory with the following variables:
```
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=documents
```

## Requirements

All required dependencies are listed in `backend/requirements.txt` and include:
- qdrant-client
- requests
- python-dotenv

Install dependencies with:
```bash
pip install -r backend/requirements.txt
```

## Test Reports

Test reports are automatically generated in Markdown format when running pipeline tests. The reports include:
- Performance metrics
- Error rates
- Consistency validation results
- Content verification accuracy
- Metadata validation results

## Architecture

The system follows a modular architecture:
```
retrieve_data.py     → Handles Qdrant connections and data retrieval
content_verification.py → Validates content accuracy against original text
metadata_validation.py → Validates metadata and URL accessibility
pipeline_tests.py    → Runs comprehensive pipeline tests
integration_test.py  → Tests end-to-end functionality
```