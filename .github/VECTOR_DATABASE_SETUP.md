# Vector Database GitHub Action Setup

This document explains how to set up the GitHub Action that automatically updates the vector database when changes are pushed to the repository.

## 🔧 Required GitHub Secrets

To use the vector database update workflow, you need to configure the following secrets in your GitHub repository:

### Setting Up Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** for each of the following:

### Required Secrets

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `OPENAI_API_KEY` | Your OpenAI API key for embeddings | `sk-proj-...` |
| `QDRANT_URL` | Your Qdrant Cloud cluster URL | `https://your-cluster-id.us-east4-0.gcp.cloud.qdrant.io` |
| `QDRANT_API_KEY` | Your Qdrant Cloud API key (optional for some clusters) | `your-api-key` or leave empty |

## 🚀 How the Workflow Works

The GitHub Action (`update-vector-database.yml`) automatically runs when:

### Automatic Triggers
- **Push to main branch** with changes to:
  - `data/pdf_downloads/**` (new or updated PDF files)
  - `rag/init_vector_database.py` (script updates)
  - `data/configs/**` (configuration changes)
- **Push to deploy branch** with the same path changes

### Manual Trigger
- You can manually trigger the workflow from the **Actions** tab in GitHub
- Click on "Update Vector Database" → "Run workflow"

## 📋 What the Workflow Does

1. **Environment Setup**
   - Sets up Python 3.11
   - Installs UV package manager
   - Installs required dependencies

2. **Validation**
   - Checks that required secrets are configured
   - Verifies PDF files exist in `data/pdf_downloads/`

3. **Vector Database Update**
   - Creates environment configuration
   - Runs the `rag/init_vector_database.py` script
   - Processes all PDF files and uploads to Qdrant Cloud

4. **Logging & Error Handling**
   - Captures detailed logs of the process
   - Uploads logs as artifacts if the workflow fails
   - Provides summary of documents processed

## 📊 Monitoring the Workflow

### Viewing Results
1. Go to the **Actions** tab in your GitHub repository
2. Click on the latest "Update Vector Database" workflow run
3. Expand the steps to see detailed logs

### Success Indicators
- ✅ All steps complete without errors
- 📊 Summary shows number of documents processed
- 🎯 Qdrant collection updated with new embeddings

### Troubleshooting
- If the workflow fails, check the uploaded log artifacts
- Verify all required secrets are properly configured
- Ensure PDF files are valid and readable

## 🔄 Workflow Optimization

### Performance Considerations
- The workflow processes all PDF files each time it runs
- Large PDF collections may take 10-30 minutes to process
- Consider running during off-peak hours for large updates

### Cost Considerations
- Each run uses OpenAI API credits for embeddings
- Monitor your OpenAI usage if you have frequent updates
- The workflow only runs when relevant files change

## 🛠️ Customization

You can modify the workflow by editing `.github/workflows/update-vector-database.yml`:

- **Change trigger paths**: Modify the `paths:` section
- **Adjust chunk settings**: Update environment variables
- **Add notifications**: Include Slack/email notifications
- **Modify Python version**: Change the `python-version` setting

## 📝 Example Workflow Run

```
✅ Required secrets are available
📄 Found PDF files to process:
   PDF count: 15
🚀 Starting vector database initialization...
📊 Processing FATF_Recommendations_2012.pdf: 127 chunks
📊 Processing FinCEN_SAR_Filing_Instructions.pdf: 89 chunks
...
✅ Successfully uploaded 1,247 document chunks to Qdrant Cloud
✅ Vector database update completed successfully!
```

This automated workflow ensures your vector database stays synchronized with your document collection, enabling the RAG system to always have access to the latest regulatory information.
