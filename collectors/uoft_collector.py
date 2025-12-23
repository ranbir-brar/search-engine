"""
University of Toronto Collector for Atlas Course Materials Search Engine.
Collects course materials from UofT Computer Science department.
"""
import requests
from typing import List, Dict, Any
from .base import BaseCollector


class UofTCollector(BaseCollector):
    """
    Collector for University of Toronto course materials.
    Focuses on CS course notes publicly available.
    """
    
    # Known public course materials
    COURSES = [
        # Intro CS
        {
            "code": "CSC108",
            "name": "Introduction to Computer Programming",
            "url": "https://www.teach.cs.toronto.edu/~csc108h/",
            "instructor": "CS Faculty",
        },
        {
            "code": "CSC148",
            "name": "Introduction to Computer Science",
            "url": "https://www.teach.cs.toronto.edu/~csc148h/",
            "instructor": "CS Faculty",
        },
        {
            "code": "CSC165",
            "name": "Mathematical Expression and Reasoning for CS",
            "url": "https://www.teach.cs.toronto.edu/~csc165h/",
            "instructor": "CS Faculty",
        },
        # Core CS
        {
            "code": "CSC207",
            "name": "Software Design",
            "url": "https://www.teach.cs.toronto.edu/~csc207h/",
            "instructor": "CS Faculty",
        },
        {
            "code": "CSC209",
            "name": "Software Tools and Systems Programming",
            "url": "https://www.teach.cs.toronto.edu/~csc209h/",
            "instructor": "CS Faculty",
        },
        {
            "code": "CSC236",
            "name": "Introduction to the Theory of Computation",
            "url": "https://www.teach.cs.toronto.edu/~csc236h/",
            "instructor": "CS Faculty",
        },
        {
            "code": "CSC258",
            "name": "Computer Organization",
            "url": "https://www.teach.cs.toronto.edu/~csc258h/",
            "instructor": "CS Faculty",
        },
        {
            "code": "CSC263",
            "name": "Data Structures and Analysis",
            "url": "https://www.teach.cs.toronto.edu/~csc263h/",
            "instructor": "CS Faculty",
        },
        # Upper year
        {
            "code": "CSC343",
            "name": "Introduction to Databases",
            "url": "https://www.teach.cs.toronto.edu/~csc343h/",
            "instructor": "CS Faculty",
        },
        {
            "code": "CSC369",
            "name": "Operating Systems",
            "url": "https://www.teach.cs.toronto.edu/~csc369h/",
            "instructor": "CS Faculty",
        },
        {
            "code": "CSC373",
            "name": "Algorithm Design, Analysis & Complexity",
            "url": "https://www.teach.cs.toronto.edu/~csc373h/",
            "instructor": "CS Faculty",
        },
        {
            "code": "CSC384",
            "name": "Introduction to Artificial Intelligence",
            "url": "https://www.teach.cs.toronto.edu/~csc384h/",
            "instructor": "CS Faculty",
        },
        {
            "code": "CSC401",
            "name": "Natural Language Computing",
            "url": "https://www.teach.cs.toronto.edu/~csc401h/",
            "instructor": "CS Faculty",
        },
        {
            "code": "CSC411",
            "name": "Machine Learning and Data Mining",
            "url": "https://www.teach.cs.toronto.edu/~csc411h/",
            "instructor": "CS Faculty",
        },
        # Math courses
        {
            "code": "MAT137",
            "name": "Calculus with Proofs",
            "url": "https://www.math.toronto.edu/courses/mat137y1/",
            "instructor": "Math Faculty",
        },
        {
            "code": "MAT223",
            "name": "Linear Algebra I",
            "url": "https://www.math.toronto.edu/courses/mat223h1/",
            "instructor": "Math Faculty",
        },
        {
            "code": "MAT224",
            "name": "Linear Algebra II",
            "url": "https://www.math.toronto.edu/courses/mat224h1/",
            "instructor": "Math Faculty",
        },
        {
            "code": "STA247",
            "name": "Probability with Computer Applications",
            "url": "https://www.math.toronto.edu/courses/sta247h1/",
            "instructor": "Stats Faculty",
        },
    ]
    
    def __init__(self):
        super().__init__(name="UofT")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/537.36"
        })
    
    def _create_course_entry(self, course: Dict[str, str]) -> Dict[str, Any]:
        """Create a payload for a course."""
        title = f"{course['code']}: {course['name']}"
        summary = (
            f"University of Toronto course: {course['name']} ({course['code']}). "
            f"UofT's Computer Science program is consistently ranked among the top in Canada and globally, "
            f"with strong research in AI, systems, and theory."
        )
        
        return self.create_payload(
            title=title,
            summary=summary,
            authors=[course["instructor"]],
            url=course["url"],
            source="UofT",
            resource_type="Course Notes"
        )
    
    def collect(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Collect course materials from UofT."""
        payloads = []
        
        for course in self.COURSES:
            if len(payloads) >= limit:
                break
            
            if not self.is_new(course["url"]):
                continue
            
            try:
                payload = self._create_course_entry(course)
                payloads.append(payload)
                print(f"[UofT] Collected: {course['code']}")
            except Exception as e:
                print(f"[UofT] Error with {course['code']}: {e}")
        
        return payloads[:limit]
