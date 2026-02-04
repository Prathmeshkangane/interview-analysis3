"""
Document Parser Module
Extracts text from PDF and DOCX files for resume and job description processing
"""

import PyPDF2
import docx
import os
from typing import Optional


class DocumentParser:
    """Parse and extract text from various document formats"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.txt']
    
    def parse_document(self, file_path: str) -> Optional[str]:
        """
        Parse document and extract text content
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Extracted text or None if parsing fails
        """
        if not os.path.exists(file_path):
            print(f"Error: File not found - {file_path}")
            return None
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext not in self.supported_formats:
            print(f"Error: Unsupported file format - {file_ext}")
            return None
        
        try:
            if file_ext == '.pdf':
                return self._parse_pdf(file_path)
            elif file_ext == '.docx':
                return self._parse_docx(file_path)
            elif file_ext == '.txt':
                return self._parse_txt(file_path)
        except Exception as e:
            print(f"Error parsing document: {e}")
            return None
    
    def _parse_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error reading PDF: {e}")
            raise
        return text.strip()
    
    def _parse_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            print(f"Error reading DOCX: {e}")
            raise
        return text.strip()
    
    def _parse_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
        except Exception as e:
            print(f"Error reading TXT: {e}")
            raise
        return text.strip()
    
    def extract_key_information(self, text: str, doc_type: str) -> dict:
        """
        Extract key information from document text
        
        Args:
            text: Document text
            doc_type: 'resume' or 'job_description'
            
        Returns:
            Dictionary with extracted information
        """
        info = {
            'full_text': text,
            'word_count': len(text.split()),
            'char_count': len(text)
        }
        
        # Basic keyword extraction (can be enhanced with NLP)
        if doc_type == 'resume':
            info['type'] = 'resume'
            # Look for common resume sections
            info['has_experience'] = any(keyword in text.lower() for keyword in 
                                        ['experience', 'work history', 'employment'])
            info['has_education'] = any(keyword in text.lower() for keyword in 
                                       ['education', 'degree', 'university'])
            info['has_skills'] = 'skills' in text.lower()
            
        elif doc_type == 'job_description':
            info['type'] = 'job_description'
            # Look for common JD sections
            info['has_requirements'] = any(keyword in text.lower() for keyword in 
                                          ['requirements', 'qualifications', 'required'])
            info['has_responsibilities'] = any(keyword in text.lower() for keyword in 
                                              ['responsibilities', 'duties', 'role'])
        
        return info


if __name__ == "__main__":
    # Test the document parser
    parser = DocumentParser()
    
    print("Document Parser Module - Test Mode")
    print("=" * 50)
    print("\nSupported formats:", parser.supported_formats)
    
    # Example usage
    test_text = """
    Senior Software Engineer
    
    Experience:
    - 5 years in Python development
    - Machine Learning expertise
    - Full-stack development
    
    Education:
    - BS Computer Science
    
    Skills:
    - Python, TensorFlow, React
    """
    
    info = parser.extract_key_information(test_text, 'resume')
    print("\nExtracted Information:")
    for key, value in info.items():
        if key != 'full_text':
            print(f"  {key}: {value}")