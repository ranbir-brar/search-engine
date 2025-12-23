"""
MIT OpenCourseWare Collector for Atlas Academic Search Engine.
Scrapes lecture notes and slides from MIT OCW.
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from urllib.parse import urljoin
from .base import BaseCollector


class OCWCollector(BaseCollector):
    """
    Collector for MIT OpenCourseWare materials.
    
    Scrapes course pages for lecture notes, slides, and syllabi.
    """
    
    BASE_URL = "https://ocw.mit.edu"
    
    # Popular CS/Math courses for students
    COURSE_URLS = [
        "/courses/6-006-introduction-to-algorithms-spring-2020/",
        "/courses/6-042j-mathematics-for-computer-science-fall-2010/",
        "/courses/6-034-artificial-intelligence-fall-2010/",
        "/courses/6-046j-design-and-analysis-of-algorithms-spring-2015/",
        "/courses/18-06-linear-algebra-spring-2010/",
        "/courses/6-001-structure-and-interpretation-of-computer-programs-spring-2005/",
    ]
    
    # File extensions we're interested in
    VALID_EXTENSIONS = ['.pdf', '.ppt', '.pptx']
    
    def __init__(self, course_urls: List[str] = None):
        super().__init__(name="MIT OCW")
        self.course_urls = course_urls or self.COURSE_URLS
        self.headers = {
            "User-Agent": "Atlas Academic Search (Student Project) - https://github.com/student/atlas"
        }
    
    def _determine_resource_type(self, text: str, url: str) -> str:
        """Determine resource type based on context."""
        text_lower = text.lower()
        url_lower = url.lower()
        
        if 'syllabus' in text_lower or 'syllabus' in url_lower:
            return "Syllabus"
        elif 'slide' in text_lower or '.ppt' in url_lower:
            return "Lecture Slides"
        elif 'lecture' in text_lower or 'note' in text_lower:
            return "Course Notes"
        else:
            return "Course Notes"  # Default
    
    def _scrape_course(self, course_path: str) -> List[Dict[str, Any]]:
        """Scrape a single course page for resources."""
        payloads = []
        course_url = urljoin(self.BASE_URL, course_path)
        
        try:
            # Get course main page
            response = requests.get(course_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get course title
            title_elem = soup.find('h1')
            course_title = title_elem.get_text(strip=True) if title_elem else "Unknown Course"
            
            # Find all links to resources
            for link in soup.find_all('a', href=True):
                href = link['href']
                link_text = link.get_text(strip=True)
                
                # Check if it's a resource we want
                if any(href.lower().endswith(ext) for ext in self.VALID_EXTENSIONS):
                    full_url = urljoin(self.BASE_URL, href)
                    
                    if not self.is_new(full_url):
                        continue
                    
                    resource_type = self._determine_resource_type(link_text, href)
                    
                    payload = self.create_payload(
                        title=link_text or f"{course_title} - Resource",
                        summary=f"Part of MIT OpenCourseWare: {course_title}",
                        authors=["MIT Faculty"],
                        url=full_url,
                        source="MIT OpenCourseWare",
                        resource_type=resource_type
                    )
                    
                    payloads.append(payload)
                    print(f"[MIT OCW] Collected: {link_text[:50]}...")
                    
        except Exception as e:
            print(f"[MIT OCW] Error scraping {course_path}: {e}")
        
        return payloads
    
    def collect(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Scrape MIT OCW for course materials.
        
        Args:
            limit: Maximum number of resources to collect
            
        Returns:
            List of resource payloads
        """
        payloads = []
        
        for course_path in self.course_urls:
            if len(payloads) >= limit:
                break
            
            course_resources = self._scrape_course(course_path)
            payloads.extend(course_resources)
        
        return payloads[:limit]
