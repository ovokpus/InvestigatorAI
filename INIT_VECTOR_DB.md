# 🚀 Ad-hoc Vector Database Initialization

This guide explains how to initialize your InvestigatorAI vector database on-demand.

## 📋 Prerequisites

1. **Environment Configuration**: Ensure your `.env` file contains:
   ```bash
   QDRANT_URL=https://qdrant-production-1cff.up.railway.app
   OPENAI_API_KEY=your_openai_api_key_here
   ```

2. **PDF Documents**: Place regulatory documents in `data/pdf_downloads/`

## 🏃‍♂️ Quick Start

### Option 1: Simple Wrapper (Recommended)
```bash
python init_vector_db.py
```

### Option 2: Direct Script Execution
```bash
python scripts/init_vector_database_railway.py
```

## 📊 What Happens During Initialization

1. **🔍 Environment Loading**: Reads configuration from `.env` file
2. **🔗 Qdrant Connection**: Connects to your vector database
3. **📚 Document Processing**: Processes all PDF files in `data/pdf_downloads/`
4. **🧠 Embedding Generation**: Creates embeddings using OpenAI's `text-embedding-3-large`
5. **📤 Upload**: Uploads document chunks to Qdrant collection `regulatory_documents`

## ⏱️ Expected Runtime

- **Small dataset** (5-10 PDFs): 2-5 minutes
- **Medium dataset** (10-20 PDFs): 5-10 minutes  
- **Large dataset** (20+ PDFs): 10+ minutes

## 🔧 Configuration Options

You can override settings via environment variables:

```bash
# Vector database settings
QDRANT_URL=https://your-qdrant-instance.com
VECTOR_COLLECTION_NAME=regulatory_documents

# Document processing settings
PDF_DATA_PATH=data/pdf_downloads
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# OpenAI settings
OPENAI_API_KEY=your_key_here
EMBEDDING_MODEL=text-embedding-3-large
```

## 🚨 Troubleshooting

### Common Issues:

1. **Missing OPENAI_API_KEY**:
   ```
   ValueError: OPENAI_API_KEY environment variable is required
   ```
   **Solution**: Add your OpenAI API key to `.env` file

2. **Qdrant Connection Failed**:
   ```
   Connection refused to qdrant-production-xxxx.up.railway.app
   ```
   **Solution**: Verify `QDRANT_URL` in `.env` file is correct

3. **No PDF Files Found**:
   ```
   No PDF files found in data/pdf_downloads
   ```
   **Solution**: Add PDF documents to the `data/pdf_downloads/` directory

## 📈 Monitoring Progress

The script provides detailed logging:
- ✅ **Green checkmarks**: Successful operations
- 📄 **Document icons**: File processing status
- 📦 **Package icons**: Batch upload progress
- 🎉 **Party icon**: Completion

## 🔄 Re-running Initialization

- **Safe to re-run**: The script will recreate the collection
- **Overwrites existing data**: Previous embeddings will be replaced
- **Use for updates**: Run after adding new documents

## 🎯 Next Steps

After successful initialization:
1. **Test your API**: Make investigation requests
2. **Verify collection**: Check Qdrant dashboard for document count
3. **Frontend testing**: Ensure UI can query the vector database

---

**Need help?** Check the logs for detailed error messages and troubleshooting steps.
