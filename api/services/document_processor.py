"""Document processing service for regulatory documents"""
import os
import re
from pathlib import Path
from typing import List, Dict, Any
import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

from ..core.config import Settings
from ..models.schemas import ProcessedDocument, DocumentMetadata

class DocumentProcessor:
    """Process regulatory documents for fraud investigation RAG system"""
    
    def __init__(self, embeddings_model: OpenAIEmbeddings, settings: Settings):
        self.embeddings = embeddings_model
        self.settings = settings
        self.documents = []
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
        )
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file using PyMuPDF"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            
            for page in doc:
                page_text = page.get_text()
                # Clean up the text
                page_text = re.sub(r'\s+', ' ', page_text)  # Normalize whitespace
                page_text = re.sub(r'\n+', '\n', page_text)  # Normalize line breaks
                text += page_text + " "
            
            doc.close()
            
            # Filter out procedural text before returning
            filtered_text = self._filter_procedural_text(text.strip())
            print(f"   📝 Text extracted: {len(text)} chars -> {len(filtered_text)} chars after filtering")
            return filtered_text
            
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return ""
    
    def classify_document_type(self, filename: str, content: str) -> tuple[str, str]:
        """Classify document by type and content category"""
        filename_lower = filename.lower()
        content_lower = content.lower()
        
        # Document type classification
        if 'fincen' in filename_lower:
            source_type = 'fincen'
        elif 'ffiec' in filename_lower:
            source_type = 'ffiec'
        elif 'fdic' in filename_lower:
            source_type = 'fdic'
        elif 'federal_reserve' in filename_lower:
            source_type = 'federal_reserve'
        elif 'irs' in filename_lower:
            source_type = 'irs'
        elif 'interpol' in filename_lower:
            source_type = 'interpol'
        elif 'open_banking' in filename_lower:
            source_type = 'open_banking'
        else:
            source_type = 'regulatory'
        
        # Content category classification
        if any(term in content_lower for term in ['suspicious activity report', 'sar']):
            content_category = 'sar_guidance'
        elif any(term in content_lower for term in ['currency transaction report', 'ctr']):
            content_category = 'ctr_guidance'
        elif any(term in content_lower for term in ['bsa', 'bank secrecy act']):
            content_category = 'bsa_compliance'
        elif any(term in content_lower for term in ['customer due diligence', 'cdd']):
            content_category = 'cdd_requirements'
        elif any(term in content_lower for term in ['anti-money laundering', 'aml']):
            content_category = 'aml_compliance'
        elif any(term in content_lower for term in ['fraud', 'fraudulent']):
            content_category = 'fraud_indicators'
        elif any(term in content_lower for term in ['human trafficking']):
            content_category = 'human_trafficking'
        else:
            content_category = 'general_guidance'
        
        return source_type, content_category
    
    def _filter_procedural_text(self, text: str) -> str:
        """Filter out procedural and administrative text sections before chunking"""
        
        # Define procedural text patterns to remove
        procedural_patterns = [
            # Filing instructions and addresses
            r'send each completed.*?report to:.*?detroit computing center.*?detroit,?\s*mi\s*\d+[-\d]*',
            r'detroit computing center,?\s*p\.?o\.?\s*box\s*\d+,?\s*detroit,?\s*mi\s*\d+[-\d]*',
            
            # Form catalog numbers and administrative codes
            r'catalog\s+no\.?\s*\d+[a-z]*(?:\s*\([^)]*\))?',
            r'form\s+no\.?\s*\d+[a-z]*(?:\s*\([^)]*\))?',
            r'omb\s+no\.?\s*\d+[-\d]*',
            
            # Checkbox and form instructions
            r'check\s+(?:the\s+)?box(?:es)?.*?(?:if|when|to).*?(?:\.|$)',
            r'for\s+items\s+that\s+do\s+not\s+apply.*?leave\s+blank',
            r'if\s+you\s+are\s+correcting.*?previously\s+filed\s+report.*?line\s+\d+',
            r'complete\s+the\s+report\s+in\s+its\s+entirety',
            r'include\s+the\s+corrected\s+information\s+in\s+the\s+applicable\s+boxes',
            r'describe\s+the\s+changes.*?part\s+[ivx]+.*?description\s+of\s+suspicious\s+activity',
            r'do\s+not\s+include\s+any\s+supporting\s+documentation',
            
            # Filing deadlines and procedural requirements (keep substantive content)
            r'this\s+suspicious\s+activity\s+report\s+does\s+not\s+need\s+to\s+be\s+filed\s+for\s+those\s+robberies\s+and\s+burglaries.*?17\s+cfr\s+240\.17f-1',
            
            # Revision and draft markers
            r'\brev\.?\s*\d+/\d+\b',
            r'\bdraft\b.*?(?:\n|$)',
            
            # Page numbers and headers/footers
            r'\bpage\s+\d+\s+of\s+\d+\b',
            
            # Table continuation markers
            r'\bcontinued\s+on\s+next\s+page\b',
            r'\bsee\s+instructions\s+on\s+(?:page|back)\b'
        ]
        
        # Apply filtering
        filtered_text = text
        removed_sections = []
        
        for pattern in procedural_patterns:
            matches = re.finditer(pattern, filtered_text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                removed_sections.append(match.group(0)[:100] + "..." if len(match.group(0)) > 100 else match.group(0))
            
            filtered_text = re.sub(pattern, ' ', filtered_text, flags=re.IGNORECASE | re.DOTALL)
        
        # Clean up multiple spaces and empty lines
        filtered_text = re.sub(r'\s+', ' ', filtered_text)
        filtered_text = re.sub(r'\n\s*\n', '\n', filtered_text)
        
        # Log what was removed for debugging
        if removed_sections:
            print(f"   🧹 Filtered out {len(removed_sections)} procedural sections:")
            for section in removed_sections[:3]:  # Show first 3
                print(f"      - {section}")
            if len(removed_sections) > 3:
                print(f"      - ... and {len(removed_sections) - 3} more")
        
        return filtered_text.strip()
    
    def process_single_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Process a single PDF file into chunks with metadata"""
        filename = os.path.basename(pdf_path)
        print(f"📖 Processing: {filename}")
        
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        
        if not text:
            print(f"   ⚠️ No text extracted from {filename}")
            return []
        
        # Classify document
        source_type, content_category = self.classify_document_type(filename, text)
        
        # Split into chunks
        chunks = self.text_splitter.split_text(text)
        
        # Create document objects with metadata
        documents = []
        for i, chunk in enumerate(chunks):
            doc_metadata = {
                'filename': filename,
                'chunk_id': i,
                'source_type': source_type,
                'content_category': content_category,
                'document_type': 'regulatory_guidance',
                'last_updated': None
            }
            
            documents.append({
                'page_content': chunk,
                'metadata': doc_metadata
            })
        
        print(f"   ✅ {len(documents)} chunks created")
        return documents
    
    def process_all_pdfs(self) -> List[Dict[str, Any]]:
        """Process all PDFs in the data directory"""
        pdf_dir = Path(self.settings.pdf_data_path)
        
        if not pdf_dir.exists():
            print(f"❌ PDF directory not found: {pdf_dir}")
            return []
        
        pdf_files = list(pdf_dir.glob("*.pdf"))
        
        if not pdf_files:
            print(f"❌ No PDF files found in {pdf_dir}")
            return []
        
        print(f"📄 Found {len(pdf_files)} PDF files to process")
        
        all_documents = []
        for pdf_file in pdf_files:
            documents = self.process_single_pdf(str(pdf_file))
            all_documents.extend(documents)
        
        print(f"\n📊 Total processed: {len(all_documents)} document chunks")
        self.documents = all_documents
        return all_documents
    
    def get_langchain_documents(self) -> List[Document]:
        """Convert processed documents to LangChain Document format"""
        return [
            Document(page_content=doc['page_content'], metadata=doc['metadata'])
            for doc in self.documents
        ]