import re
from langchain_core.documents import Document

def parse_law_text(text, filename):
    """
    Parses a law text file where articles start with 'Статья' or 'СТАТЬЯ'.
    Returns a list of Document objects.
    """
    documents = []
    # Split by lines and clean
    lines = [line.strip() for line in text.split('\n')]
    
    current_title = "Преамбула"
    current_article_id = ""
    current_content = []
    
    # Pattern to match "Статья 1", "Статья 1-1", "СТАТЬЯ 104"
    article_pattern = re.compile(r'^(Статья|СТАТЬЯ)\s+([0-9]+(-[0-9]+)?)([^\n]*)', re.IGNORECASE)
    
    for line in lines:
        if not line:
            continue
            
        match = article_pattern.match(line)
        if match:
            # Save previous article
            if current_content or current_title != "Преамбула":
                documents.append(_create_doc(current_title, current_article_id, current_content, filename))
                current_content = []
            
            current_title = line
            current_article_id = f"st{match.group(2)}"
        else:
            current_content.append(line)
            
    # Save last article
    if current_content or current_title != "Преамбула":
        documents.append(_create_doc(current_title, current_article_id, current_content, filename))
        
    return documents

def _create_doc(title, article_id, content_list, filename):
    content = "\n".join(content_list)
    return Document(
        page_content=f"{title}\n{content}",
        metadata={
            "source": filename,
            "title": title,
            "article_id": article_id,
            "link": f"{filename}#{article_id}" if article_id else filename
        }
    )
