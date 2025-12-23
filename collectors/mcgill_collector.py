"""
McGill University Collector for Atlas Course Materials Search Engine.
Collects course materials from McGill CS and Math departments.
"""
import requests
from typing import List, Dict, Any
from .base import BaseCollector


class McGillCollector(BaseCollector):
    """
    Collector for McGill University course materials.
    Focuses on CS and Math course notes publicly available.
    """
    
    # Known public course materials
    COURSES = [
        # Intro CS
        {
            "code": "COMP 202",
            "name": "Foundations of Programming",
            "url": "https://www.cs.mcgill.ca/~cs202/",
            "instructor": "CS Faculty",
        },
        {
            "code": "COMP 206",
            "name": "Introduction to Software Systems",
            "url": "https://www.cs.mcgill.ca/~cs206/",
            "instructor": "CS Faculty",
        },
        {
            "code": "COMP 250",
            "name": "Introduction to Computer Science",
            "url": "https://www.cs.mcgill.ca/~cs250/",
            "instructor": "CS Faculty",
        },
        {
            "code": "COMP 251",
            "name": "Algorithms and Data Structures",
            "url": "https://www.cs.mcgill.ca/~cs251/",
            "instructor": "CS Faculty",
        },
        {
            "code": "COMP 273",
            "name": "Introduction to Computer Systems",
            "url": "https://www.cs.mcgill.ca/~cs273/",
            "instructor": "CS Faculty",
        },
        # Core CS
        {
            "code": "COMP 302",
            "name": "Programming Languages and Paradigms",
            "url": "https://www.cs.mcgill.ca/~cs302/",
            "instructor": "CS Faculty",
        },
        {
            "code": "COMP 303",
            "name": "Software Design",
            "url": "https://www.cs.mcgill.ca/~cs303/",
            "instructor": "CS Faculty",
        },
        {
            "code": "COMP 310",
            "name": "Operating Systems",
            "url": "https://www.cs.mcgill.ca/~cs310/",
            "instructor": "CS Faculty",
        },
        {
            "code": "COMP 330",
            "name": "Theory of Computation",
            "url": "https://www.cs.mcgill.ca/~cs330/",
            "instructor": "CS Faculty",
        },
        {
            "code": "COMP 360",
            "name": "Algorithm Design",
            "url": "https://www.cs.mcgill.ca/~cs360/",
            "instructor": "CS Faculty",
        },
        # Upper year
        {
            "code": "COMP 421",
            "name": "Database Systems",
            "url": "https://www.cs.mcgill.ca/~cs421/",
            "instructor": "CS Faculty",
        },
        {
            "code": "COMP 424",
            "name": "Artificial Intelligence",
            "url": "https://www.cs.mcgill.ca/~cs424/",
            "instructor": "CS Faculty",
        },
        {
            "code": "COMP 451",
            "name": "Machine Learning",
            "url": "https://www.cs.mcgill.ca/~cs451/",
            "instructor": "CS Faculty",
        },
        {
            "code": "COMP 512",
            "name": "Distributed Systems",
            "url": "https://www.cs.mcgill.ca/~cs512/",
            "instructor": "CS Faculty",
        },
        # Math courses
        {
            "code": "MATH 140",
            "name": "Calculus 1",
            "url": "https://www.math.mcgill.ca/courses/math140/",
            "instructor": "Math Faculty",
        },
        {
            "code": "MATH 141",
            "name": "Calculus 2",
            "url": "https://www.math.mcgill.ca/courses/math141/",
            "instructor": "Math Faculty",
        },
        {
            "code": "MATH 133",
            "name": "Linear Algebra and Geometry",
            "url": "https://www.math.mcgill.ca/courses/math133/",
            "instructor": "Math Faculty",
        },
        {
            "code": "MATH 222",
            "name": "Calculus 3",
            "url": "https://www.math.mcgill.ca/courses/math222/",
            "instructor": "Math Faculty",
        },
        {
            "code": "MATH 323",
            "name": "Probability",
            "url": "https://www.math.mcgill.ca/courses/math323/",
            "instructor": "Math Faculty",
        },
    ]
    
    def __init__(self):
        super().__init__(name="McGill")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/537.36"
        })
    
    def _create_course_entry(self, course: Dict[str, str]) -> Dict[str, Any]:
        """Create a payload for a course."""
        title = f"{course['code']}: {course['name']}"
        summary = (
            f"McGill University course: {course['name']} ({course['code']}). "
            f"McGill is one of Canada's top research universities, known for strong programs "
            f"in computer science, mathematics, and AI research at Mila."
        )
        
        return self.create_payload(
            title=title,
            summary=summary,
            authors=[course["instructor"]],
            url=course["url"],
            source="McGill",
            resource_type="Course Notes"
        )
    
    def collect(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Collect course materials from McGill."""
        payloads = []
        
        for course in self.COURSES:
            if len(payloads) >= limit:
                break
            
            if not self.is_new(course["url"]):
                continue
            
            try:
                payload = self._create_course_entry(course)
                payloads.append(payload)
                print(f"[McGill] Collected: {course['code']}")
            except Exception as e:
                print(f"[McGill] Error with {course['code']}: {e}")
        
        return payloads[:limit]
