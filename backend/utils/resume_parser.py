import PyPDF2
from docx import Document
import re
import os

def parse_resume(file):
    """
    Parse resume file and extract key information
    Supports PDF, DOCX, and TXT files
    """
    filename = file.filename.lower()
    
    if filename.endswith('.pdf'):
        return parse_pdf(file)
    elif filename.endswith('.docx'):
        return parse_docx(file)
    elif filename.endswith('.txt'):
        return parse_txt(file)
    else:
        # Try to parse as text if format not recognized
        try:
            return parse_txt(file)
        except:
            raise ValueError("Unsupported file format. Please use PDF, DOCX, or TXT.")

def parse_pdf(file):
    """Parse PDF resume"""
    try:
        file.seek(0)  # Reset file pointer
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return extract_key_info(text)
    except Exception as e:
        raise Exception(f"Error parsing PDF: {str(e)}")

def parse_docx(file):
    """Parse DOCX resume"""
    try:
        file.seek(0)  # Reset file pointer
        doc = Document(file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return extract_key_info(text)
    except Exception as e:
        raise Exception(f"Error parsing DOCX: {str(e)}")

def parse_txt(file):
    """Parse TXT resume"""
    try:
        file.seek(0)  # Reset file pointer
        text = file.read().decode('utf-8')
        return extract_key_info(text)
    except Exception as e:
        raise Exception(f"Error parsing TXT: {str(e)}")

def extract_key_info(text):
    """
    Extract key information from resume text
    """
    # Clean the text
    text = re.sub(r'\s+', ' ', text)
    
    info = {
        'skills': extract_skills(text),
        'experience': extract_experience(text),
        'education': extract_education(text),
        'projects': extract_projects(text),
        'summary': extract_summary(text),
        'raw_text': text[:1000]  # First 1000 chars for context
    }
    
    return info

def extract_skills(text):
    """Extract technical and professional skills"""
    # Common skills database
    technical_skills = [
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust',
        'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring', 'express',
        'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'ci/cd',
        'machine learning', 'ai', 'data analysis', 'tableau', 'power bi', 'excel',
        'photoshop', 'figma', 'sketch', 'adobe xd', 'ui/ux design',
        'salesforce', 'hubspot', 'seo', 'sem', 'google analytics', 'wordpress'
    ]
    
    professional_skills = [
        'project management', 'agile', 'scrum', 'kanban', 'leadership', 'team management',
        'communication', 'problem solving', 'critical thinking', 'public speaking',
        'client relations', 'negotiation', 'strategic planning', 'budget management'
    ]
    
    all_skills = technical_skills + professional_skills
    found_skills = []
    
    for skill in all_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', text.lower()):
            found_skills.append(skill.title())
    
    return list(set(found_skills))[:15]  # Remove duplicates and limit

def extract_experience(text):
    """Extract work experience information"""
    # Look for experience patterns
    experience_patterns = [
        r'(\d+[\+\+]?\s*(?:years?|yrs?))',
        r'experience.*?(\d+[\+\+]?\s*(?:years?|yrs?))',
        r'(\d+[\+\+]?\s*(?:years?|yrs?)).*?experience'
    ]
    
    for pattern in experience_patterns:
        matches = re.findall(pattern, text.lower())
        if matches:
            return matches[0].title()
    
    # Look for job titles and companies
    job_titles = [
        'developer', 'engineer', 'analyst', 'manager', 'director', 'specialist',
        'consultant', 'architect', 'designer', 'scientist'
    ]
    
    found_titles = []
    for title in job_titles:
        if re.search(r'\b' + title + r'\b', text.lower()):
            found_titles.append(title.title())
    
    return found_titles[:3] if found_titles else "Experience details found"

def extract_education(text):
    """Extract education information"""
    # FIXED: Use raw strings for regex patterns
    education_keywords = [
        'university', 'college', 'institute', 'school',
        'bachelor', r'b\.?s\.?', r'b\.?a\.?',
        'master', r'm\.?s\.?', r'm\.?a\.?', 'mba',
        'phd', r'ph\.?d\.?', 'doctorate',
        'associate', 'diploma', 'certificate'
    ]
    
    # Look for education section
    lines = text.split('\n')
    education_lines = []
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(re.search(keyword, line_lower) for keyword in education_keywords if '.' in keyword):
            education_line = line.strip()
            if i + 1 < len(lines) and len(lines[i + 1].strip()) > 10:
                education_line += " | " + lines[i + 1].strip()
            education_lines.append(education_line)
        elif any(keyword in line_lower for keyword in education_keywords if '.' not in keyword):
            education_line = line.strip()
            if i + 1 < len(lines) and len(lines[i + 1].strip()) > 10:
                education_line += " | " + lines[i + 1].strip()
            education_lines.append(education_line)
    
    return education_lines[:3] if education_lines else ["Education information found"]

def extract_projects(text):
    """Extract project information"""
    # Look for project sections
    project_sections = re.findall(
        r'projects?:(.*?)(?:\n\s*\n|\n[A-Z]|$)',
        text, 
        re.IGNORECASE | re.DOTALL
    )
    
    if project_sections:
        projects = []
        for section in project_sections:
            # Split by likely project separators
            project_items = re.split(r'\n\s*[•\-*]\s*|\n\s*\d+\.\s*', section)
            for item in project_items:
                item = item.strip()
                if len(item) > 20:  # Meaningful project description
                    projects.append(item[:200])  # Limit length
        return projects[:5]
    
    return ["Project experience detailed in resume"]

def extract_summary(text):
    """Extract summary or objective section"""
    # Look for summary/objective sections
    summary_patterns = [
        r'summary[:\s]*(.*?)(?:\n\s*\n|\n[A-Z]|$)',
        r'objective[:\s]*(.*?)(?:\n\s*\n|\n[A-Z]|$)',
        r'profile[:\s]*(.*?)(?:\n\s*\n|\n[A-Z]|$)'
    ]
    
    for pattern in summary_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
        if matches:
            summary = matches[0].strip()
            if len(summary) > 10:
                return summary[:300]  # Limit length
    
    # Fallback: first few lines that seem like a summary
    lines = text.split('\n')
    for line in lines[:5]:
        if len(line.strip()) > 20 and not any(keyword in line.lower() for keyword in ['name', 'address', 'phone', 'email']):
            return line.strip()[:200]
    
    return "Professional summary available in resume"

# Test function
if __name__ == '__main__':
    # Test with sample text
    sample_resume = """
    John Doe
    Software Engineer
    Experience: 5+ years in web development
    Skills: Python, JavaScript, React, AWS, Docker
    Education: BS Computer Science, University of Tech
    Projects: E-commerce platform, Mobile app development
    """
    
    result = extract_key_info(sample_resume)
    print("Resume Parse Test:")
    for key, value in result.items():
        if key != 'raw_text':
            print(f"{key}: {value}")