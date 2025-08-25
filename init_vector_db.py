#!/usr/bin/env python3
"""
Ad-hoc Vector Database Initialization Script

Simple wrapper to initialize the vector database with documents.
Automatically loads configuration from .env file.

Usage:
    python init_vector_db.py

The script will:
1. Load environment variables from .env file
2. Connect to Qdrant (Railway or local)
3. Process all PDF documents in data/pdf_downloads/
4. Create embeddings and upload to vector database
"""

import sys
from pathlib import Path

# Add the scripts directory to Python path
scripts_dir = Path(__file__).parent / "scripts"
sys.path.insert(0, str(scripts_dir))

# Import and run the Railway initialization script
try:
    from init_vector_database_railway import main
    
    if __name__ == "__main__":
        print("🚀 Starting ad-hoc vector database initialization...")
        print("📋 This will load configuration from .env file")
        print("📚 Processing all PDF documents in data/pdf_downloads/")
        print("⏳ This may take several minutes depending on document count...")
        print()
        
        main()
        
        print()
        print("🎉 Vector database initialization complete!")
        print("✅ Your InvestigatorAI is ready to use!")
        
except ImportError as e:
    print(f"❌ Error importing initialization script: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error during initialization: {e}")
    sys.exit(1)
