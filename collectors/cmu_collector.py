"""
CMU Open Learning Initiative (OLI) Collector for Atlas Course Materials Search Engine.
Collects free course materials from CMU's OLI platform.
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base import BaseCollector


class CMUCollector(BaseCollector):
    """
    Collector for Carnegie Mellon University Open Learning Initiative.
    Focuses on free courses with actual content.
    """
    
    BASE_URL = "https://oli.cmu.edu"
    
    # Free OLI courses with open content
    FREE_COURSES = [
        {
            "title": "Introduction to Statistics",
            "url": "https://oli.cmu.edu/courses/introduction-to-statistics/",
            "subject": "Statistics",
            "description": "Learn statistical concepts including data analysis, probability, and inference.",
        },
        {
            "title": "Principles of Computing",
            "url": "https://oli.cmu.edu/courses/principles-of-computing/",
            "subject": "Computer Science",
            "description": "Introduction to computational thinking and programming fundamentals.",
        },
        {
            "title": "Logic & Proofs",
            "url": "https://oli.cmu.edu/courses/logic-proofs/",
            "subject": "Mathematics",
            "description": "Formal logic, proof techniques, and mathematical reasoning.",
        },
        {
            "title": "Engineering Statics",
            "url": "https://oli.cmu.edu/courses/engineering-statics/",
            "subject": "Engineering",
            "description": "Forces, moments, equilibrium, and structural analysis.",
        },
        {
            "title": "General Chemistry I",
            "url": "https://oli.cmu.edu/courses/general-chemistry-i/",
            "subject": "Chemistry",
            "description": "Atomic structure, bonding, stoichiometry, and thermodynamics.",
        },
        {
            "title": "General Chemistry II",
            "url": "https://oli.cmu.edu/courses/general-chemistry-ii/",
            "subject": "Chemistry",
            "description": "Kinetics, equilibrium, electrochemistry, and organic chemistry basics.",
        },
        {
            "title": "Modern Biology",
            "url": "https://oli.cmu.edu/courses/modern-biology/",
            "subject": "Biology",
            "description": "Cell biology, genetics, evolution, and molecular biology.",
        },
        {
            "title": "Biochemistry",
            "url": "https://oli.cmu.edu/courses/biochemistry/",
            "subject": "Biology",
            "description": "Proteins, enzymes, metabolism, and molecular pathways.",
        },
        {
            "title": "Introduction to Psychology",
            "url": "https://oli.cmu.edu/courses/introduction-to-psychology/",
            "subject": "Psychology",
            "description": "Cognitive, developmental, and social psychology concepts.",
        },
        {
            "title": "Probability & Statistics",
            "url": "https://oli.cmu.edu/courses/probability-statistics/",
            "subject": "Statistics",
            "description": "Probability theory, distributions, hypothesis testing.",
        },
        {
            "title": "Anatomy & Physiology",
            "url": "https://oli.cmu.edu/courses/anatomy-physiology/",
            "subject": "Biology",
            "description": "Human body systems, structure, and function.",
        },
        {
            "title": "Media Programming",
            "url": "https://oli.cmu.edu/courses/media-programming/",
            "subject": "Computer Science",
            "description": "Programming with multimedia: images, sound, and video processing.",
        },
    ]
    
    def __init__(self):
        super().__init__(name="CMU OLI")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/537.36"
        })
    
    def _scrape_course_modules(self, course_url: str, course_title: str) -> List[Dict[str, Any]]:
        """Attempt to scrape module content from a course page."""
        payloads = []
        
        try:
            resp = self.session.get(course_url, timeout=15)
            if resp.status_code != 200:
                return payloads
            
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Look for module/unit links
            module_links = soup.find_all("a", href=True)
            for link in module_links:
                href = link.get("href", "")
                text = link.get_text(strip=True)
                
                # Filter for educational content
                if any(kw in text.lower() for kw in ["module", "unit", "chapter", "lesson", "lecture"]):
                    if not self.is_new(href):
                        continue
                    
                    payload = self.create_payload(
                        title=f"{course_title}: {text}",
                        summary=f"CMU OLI course module from {course_title}. {text}",
                        authors=["CMU OLI"],
                        url=href if href.startswith("http") else f"{self.BASE_URL}{href}",
                        source="CMU OLI",
                        resource_type="Course Notes"
                    )
                    payloads.append(payload)
                    print(f"[CMU OLI] Found module: {text[:50]}...")
                    
        except Exception as e:
            print(f"[CMU OLI] Error scraping {course_url}: {e}")
        
        return payloads
    
    def collect(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Collect course materials from CMU OLI."""
        payloads = []
        
        for course in self.FREE_COURSES:
            if len(payloads) >= limit:
                break
            
            # Add the course itself
            if self.is_new(course["url"]):
                payload = self.create_payload(
                    title=course["title"],
                    summary=f"CMU Open Learning Initiative: {course['description']} Subject: {course['subject']}.",
                    authors=["CMU OLI"],
                    url=course["url"],
                    source="CMU OLI",
                    resource_type="Course Notes"
                )
                payloads.append(payload)
                print(f"[CMU OLI] Collected: {course['title']}")
            
            # Try to get modules
            if len(payloads) < limit:
                modules = self._scrape_course_modules(course["url"], course["title"])
                payloads.extend(modules[:limit - len(payloads)])
        
        return payloads[:limit]
