"""
University of British Columbia Collector for Atlas Course Materials Search Engine.
Collects course materials from UBC Computer Science department.
"""
import requests
from typing import List, Dict, Any
from .base import BaseCollector


class UBCCollector(BaseCollector):
    """
    Collector for University of British Columbia course materials.
    Focuses on CS course notes publicly available.
    """
    
    # Known public course materials
    COURSES = [
        # Intro CS
        {
            "code": "CPSC 110",
            "name": "Computation, Programs, and Programming",
            "url": "https://www.cs.ubc.ca/~gregor/teaching/cpsc110/",
            "instructor": "Gregor Kiczales",
        },
        {
            "code": "CPSC 121",
            "name": "Models of Computation",
            "url": "https://www.cs.ubc.ca/~ramesh/cpsc121/",
            "instructor": "CS Faculty",
        },
        {
            "code": "CPSC 210",
            "name": "Software Construction",
            "url": "https://www.cs.ubc.ca/~cs210/",
            "instructor": "CS Faculty",
        },
        {
            "code": "CPSC 213",
            "name": "Introduction to Computer Systems",
            "url": "https://www.cs.ubc.ca/~cs213/",
            "instructor": "CS Faculty",
        },
        {
            "code": "CPSC 221",
            "name": "Basic Algorithms and Data Structures",
            "url": "https://www.cs.ubc.ca/~cs221/",
            "instructor": "CS Faculty",
        },
        # Core CS
        {
            "code": "CPSC 304",
            "name": "Introduction to Relational Databases",
            "url": "https://www.cs.ubc.ca/~cs304/",
            "instructor": "CS Faculty",
        },
        {
            "code": "CPSC 310",
            "name": "Introduction to Software Engineering",
            "url": "https://www.cs.ubc.ca/~cs310/",
            "instructor": "CS Faculty",
        },
        {
            "code": "CPSC 313",
            "name": "Computer Hardware and Operating Systems",
            "url": "https://www.cs.ubc.ca/~cs313/",
            "instructor": "CS Faculty",
        },
        {
            "code": "CPSC 320",
            "name": "Intermediate Algorithm Design and Analysis",
            "url": "https://www.cs.ubc.ca/~cs320/",
            "instructor": "CS Faculty",
        },
        {
            "code": "CPSC 322",
            "name": "Introduction to Artificial Intelligence",
            "url": "https://www.cs.ubc.ca/~cs322/",
            "instructor": "CS Faculty",
        },
        # Upper year
        {
            "code": "CPSC 340",
            "name": "Machine Learning and Data Mining",
            "url": "https://www.cs.ubc.ca/~schmidtm/Courses/340-F19/",
            "instructor": "Mark Schmidt",
        },
        {
            "code": "CPSC 416",
            "name": "Distributed Systems",
            "url": "https://www.cs.ubc.ca/~cs416/",
            "instructor": "CS Faculty",
        },
        {
            "code": "CPSC 420",
            "name": "Advanced Algorithms Design and Analysis",
            "url": "https://www.cs.ubc.ca/~cs420/",
            "instructor": "CS Faculty",
        },
        # Math courses
        {
            "code": "MATH 100",
            "name": "Differential Calculus with Applications",
            "url": "https://www.math.ubc.ca/~courses/math100/",
            "instructor": "Math Faculty",
        },
        {
            "code": "MATH 101",
            "name": "Integral Calculus with Applications",
            "url": "https://www.math.ubc.ca/~courses/math101/",
            "instructor": "Math Faculty",
        },
        {
            "code": "MATH 221",
            "name": "Matrix Algebra",
            "url": "https://www.math.ubc.ca/~courses/math221/",
            "instructor": "Math Faculty",
        },
        {
            "code": "STAT 200",
            "name": "Elementary Statistics for Applications",
            "url": "https://www.stat.ubc.ca/~stat200/",
            "instructor": "Stats Faculty",
        },
    ]
    
    def __init__(self):
        super().__init__(name="UBC")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/537.36"
        })
    
    def _create_course_entry(self, course: Dict[str, str]) -> Dict[str, Any]:
        """Create a payload for a course."""
        title = f"{course['code']}: {course['name']}"
        summary = (
            f"University of British Columbia course: {course['name']} ({course['code']}). "
            f"UBC's CS program is known for excellence in machine learning, systems, "
            f"and human-computer interaction research."
        )
        
        return self.create_payload(
            title=title,
            summary=summary,
            authors=[course["instructor"]],
            url=course["url"],
            source="UBC",
            resource_type="Course Notes"
        )
    
    def collect(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Collect course materials from UBC."""
        payloads = []
        
        for course in self.COURSES:
            if len(payloads) >= limit:
                break
            
            if not self.is_new(course["url"]):
                continue
            
            try:
                payload = self._create_course_entry(course)
                payloads.append(payload)
                print(f"[UBC] Collected: {course['code']}")
            except Exception as e:
                print(f"[UBC] Error with {course['code']}: {e}")
        
        return payloads[:limit]
