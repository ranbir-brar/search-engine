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
    
    # Comprehensive course list across MIT departments
    COURSE_URLS = [
        # Mathematics (10)
        "/courses/18-01sc-single-variable-calculus-fall-2010/",
        "/courses/18-02sc-multivariable-calculus-fall-2010/",
        "/courses/18-03sc-differential-equations-fall-2011/",
        "/courses/18-05-introduction-to-probability-and-statistics-spring-2022/",
        "/courses/18-06sc-linear-algebra-fall-2011/",
        "/courses/18-065-matrix-methods-in-data-analysis-signal-processing-and-machine-learning-spring-2018/",
        "/courses/18-100a-real-analysis-fall-2020/",
        "/courses/18-404j-theory-of-computation-fall-2020/",
        "/courses/18-650-statistics-for-applications-fall-2016/",
        "/courses/18-s096-topics-in-mathematics-with-applications-in-finance-fall-2013/",
        # Computer Science (12)
        "/courses/6-006-introduction-to-algorithms-spring-2020/",
        "/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/",
        "/courses/6-0002-introduction-to-computational-thinking-and-data-science-fall-2016/",
        "/courses/6-004-computation-structures-spring-2017/",
        "/courses/6-005-software-construction-spring-2016/",
        "/courses/6-033-computer-system-engineering-spring-2018/",
        "/courses/6-034-artificial-intelligence-fall-2010/",
        "/courses/6-036-introduction-to-machine-learning-fall-2020/",
        "/courses/6-042j-mathematics-for-computer-science-fall-2010/",
        "/courses/6-046j-design-and-analysis-of-algorithms-spring-2015/",
        "/courses/6-801-machine-vision-fall-2020/",
        "/courses/6-824-distributed-computer-systems-engineering-spring-2006/",
        # Physics (8)
        "/courses/8-01sc-classical-mechanics-fall-2016/",
        "/courses/8-02-physics-ii-electricity-and-magnetism-spring-2019/",
        "/courses/8-03sc-physics-iii-vibrations-and-waves-fall-2016/",
        "/courses/8-04-quantum-physics-i-spring-2016/",
        "/courses/8-05-quantum-physics-ii-fall-2013/",
        "/courses/8-06-quantum-physics-iii-spring-2018/",
        "/courses/8-333-statistical-mechanics-i-statistical-mechanics-of-particles-fall-2013/",
        "/courses/8-962-general-relativity-spring-2020/",
        # Chemistry (6)
        "/courses/5-111sc-principles-of-chemical-science-fall-2014/",
        "/courses/5-12-organic-chemistry-i-spring-2005/",
        "/courses/5-13-organic-chemistry-ii-fall-2006/",
        "/courses/5-60-thermodynamics-kinetics-spring-2008/",
        "/courses/5-61-physical-chemistry-fall-2017/",
        "/courses/5-07sc-biological-chemistry-i-fall-2013/",
        # Biology (6)
        "/courses/7-01sc-fundamentals-of-biology-fall-2011/",
        "/courses/7-012-introduction-to-biology-fall-2004/",
        "/courses/7-013-introductory-biology-spring-2018/",
        "/courses/7-016-introductory-biology-fall-2018/",
        "/courses/7-06-cell-biology-spring-2007/",
        "/courses/7-28-molecular-biology-spring-2005/",
        # Economics (6)
        "/courses/14-01sc-principles-of-microeconomics-fall-2011/",
        "/courses/14-02-principles-of-macroeconomics-spring-2023/",
        "/courses/14-30-introduction-to-statistical-methods-in-economics-spring-2009/",
        "/courses/14-41-public-finance-and-public-policy-spring-2016/",
        "/courses/14-73-the-challenge-of-world-poverty-spring-2011/",
        "/courses/15-401-finance-theory-i-fall-2008/",
        # Electrical Engineering (4)
        "/courses/6-002-circuits-and-electronics-spring-2007/",
        "/courses/6-003-signals-and-systems-fall-2011/",
        "/courses/6-011-signals-systems-and-inference-spring-2018/",
        "/courses/6-041sc-probabilistic-systems-analysis-and-applied-probability-fall-2013/",
    ]
    
    # Subpages with actual content (including exams and problem sets)
    CONTENT_PAGES = [
        "pages/lecture-notes/",
        "pages/syllabus/",
        "pages/readings/",
        "pages/exams/",
        "pages/assignments/",
        "pages/problem-sets/",
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
        text_lower = text.lower()
        
        # Determine type based on keywords
        if any(kw in text_lower for kw in ['exam', 'midterm', 'final', 'quiz', 'test']):
            resource_type = "Exam"
        elif any(kw in text_lower for kw in ['problem set', 'pset', 'assignment', 'homework']):
            resource_type = "Problem Set"
        elif 'solution' in text_lower:
            resource_type = "Solutions"
        elif 'recitation' in text_lower:
            resource_type = "Course Notes"
        elif 'slide' in text_lower:
            resource_type = "Lecture Slides"
        elif 'syllabus' in text_lower:
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
