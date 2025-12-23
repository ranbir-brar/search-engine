"""
MIT OpenCourseWare Collector for Atlas Academic Search Engine.
Navigates through course structure to find lecture materials.
"""
import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urljoin
from .base import BaseCollector


class OCWCollector(BaseCollector):
    """
    Collector for MIT OpenCourseWare materials.
    Handles MIT's multi-level page structure.
    """
    
    BASE_URL = "https://ocw.mit.edu"
    
    COURSE_URLS = [
        "/courses/6-006-introduction-to-algorithms-spring-2020/",
        "/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/",
        "/courses/18-06sc-linear-algebra-fall-2011/",
        "/courses/6-0002-introduction-to-computational-thinking-and-data-science-fall-2016/",
    ]
    
    # Subpages with actual content
    CONTENT_PAGES = [
        "pages/lecture-notes/",
        "pages/syllabus/",
        "pages/readings/",
    ]
    
    def __init__(self, course_urls: List[str] = None):
        super().__init__(name="MIT OCW")
        self.course_urls = course_urls or self.COURSE_URLS
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/537.36"
        })
        self.session.max_redirects = 10
    
    def _safe_get(self, url: str) -> Optional[requests.Response]:
        """Safely fetch a URL with error handling."""
        try:
            resp = self.session.get(url, timeout=15, allow_redirects=True)
            if resp.status_code == 200:
                return resp
        except Exception as e:
            print(f"[MIT OCW] Request failed for {url}: {e}")
        return None
    
    def _extract_lecture_info(self, link_text: str) -> Tuple[str, str]:
        """
        Extract title and type from link text.
        e.g., "Lecture 1: Introduction notes (PDF)" -> ("Lecture 1: Introduction", "Course Notes")
        """
        # Remove (PDF) suffix
        text = re.sub(r'\s*\(PDF\)\s*$', '', link_text, flags=re.IGNORECASE).strip()
        
        # Determine type
        if 'recitation' in text.lower():
            resource_type = "Course Notes"
        elif 'slide' in text.lower():
            resource_type = "Lecture Slides"
        elif 'syllabus' in text.lower():
            resource_type = "Syllabus"
        else:
            resource_type = "Course Notes"
        
        # Clean up "notes" suffix
        text = re.sub(r'\s+notes?\s*$', '', text, flags=re.IGNORECASE).strip()
        
        return text, resource_type
    
    def _get_pdf_from_resource_page(self, resource_url: str) -> Optional[str]:
        """Fetch the actual PDF link from a resource page."""
        resp = self._safe_get(resource_url)
        if not resp:
            return None
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Look for download links
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '.pdf' in href.lower():
                return urljoin(self.BASE_URL, href)
        
        return None
    
    def _scrape_content_page(self, page_url: str, course_title: str) -> List[Dict[str, Any]]:
        """Scrape a content page (like lecture-notes) for resources."""
        payloads = []
        
        resp = self._safe_get(page_url)
        if not resp:
            return []
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Find links to resource pages (they contain "/resources/")
        for link in soup.find_all('a', href=True):
            href = link['href']
            link_text = link.get_text(strip=True)
            
            # Skip non-resource links
            if '/resources/' not in href and '.pdf' not in href.lower():
                continue
            
            # Skip if already seen
            full_url = urljoin(self.BASE_URL, href)
            if not self.is_new(full_url):
                continue
            
            # Get title and type from link text
            if not link_text or len(link_text) < 5:
                continue
            
            title, resource_type = self._extract_lecture_info(link_text)
            
            # For resource pages, get the actual PDF
            if '/resources/' in href:
                pdf_url = self._get_pdf_from_resource_page(full_url)
                if pdf_url:
                    full_url = pdf_url
            
            # Build full title with course context
            full_title = f"{course_title}: {title}"
            
            summary = f"Lecture material from MIT OpenCourseWare course: {course_title}. " \
                      f"This {resource_type.lower()} covers fundamental concepts taught at MIT."
            
            payload = self.create_payload(
                title=full_title,
                summary=summary,
                authors=["MIT Faculty"],
                url=full_url,
                source="MIT OpenCourseWare",
                resource_type=resource_type
            )
            
            payloads.append(payload)
            print(f"[MIT OCW] Collected: {full_title[:60]}...")
            
            # Limit per page to avoid overloading
            if len(payloads) >= 30:
                break
        
        return payloads
    
    def _scrape_course(self, course_path: str) -> List[Dict[str, Any]]:
        """Scrape a course for lecture materials."""
        payloads = []
        course_url = urljoin(self.BASE_URL, course_path)
        
        resp = self._safe_get(course_url)
        if not resp:
            print(f"[MIT OCW] Could not access {course_path}")
            return []
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Get course title
        title_elem = soup.find('h1')
        course_title = title_elem.get_text(strip=True) if title_elem else "MIT Course"
        course_title = re.sub(r'\s*,\s*(Spring|Fall)\s+\d{4}$', '', course_title)
        
        print(f"[MIT OCW] Scraping: {course_title}")
        
        # Scrape each content page
        for content_page in self.CONTENT_PAGES:
            page_url = urljoin(course_url, content_page)
            payloads.extend(self._scrape_content_page(page_url, course_title))
        
        return payloads
    
    def collect(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Collect course materials from MIT OCW."""
        payloads = []
        
        for course_path in self.course_urls:
            if len(payloads) >= limit:
                break
            payloads.extend(self._scrape_course(course_path))
        
        return payloads[:limit]
