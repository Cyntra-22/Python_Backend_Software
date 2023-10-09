import ZODB
import ZODB.FileStorage
import transaction
import BTrees.OOBTree
import persistent


class Student(persistent.Persistent):
    def __init__(self, ID, name, enrolls):
        self.ID = ID
        self.name = name
        self.enrolls = enrolls # list of enrollment objects

    def __str__(self) -> str:
        course_list = "\n".join([f"     Course: ID: {enroll.courseObject.ID}, Name: {enroll.courseObject.name}, Credit: {enroll.courseObject.credit}, Grade: {enroll.grade}" for enroll in self.enrolls])
        return f"Transcript \nID: {self.ID}, Name: {self.name}, Enrollments: {len(self.enrolls)}\n{course_list}"
  
    def enrollCourse(self, courseObject, Grade):
        
        enrollment = Enrollment(courseObject, Grade, self)

        
        self.enrolls.append(enrollment)

        # Return the created Enrollment object
        return enrollment
    
    def getEnrollment(self, courseObject):
        for enrollment in self.enrolls:
            if enrollment.courseObject == courseObject:
                return enrollment
        return None  # Return None if the enrollment is not found

    def printTranscript(self):
        print(self.__str__())

    def setName(self, name):
        self.name = name


class Course(persistent.Persistent):

    grading = [
        {"Grade": "A", "min": 80, "max": 100},
        {"Grade": "B", "min": 70, "max": 79},
        {"Grade": "C", "min": 60, "max": 69},
        {"Grade": "D", "min": 50, "max": 59},
        {"Grade": "F", "min": 0, "max": 49},
    ]

    def __init__(self, ID, credit, name,gradeScheme=None):
        self.ID = ID
        self.credit = credit
        self.name = name
        self.gradeScheme = gradeScheme if gradeScheme is not None else []

    def __str__(self) -> str:
        return f"ID:    {self.ID}, Course: {self.name}, Credit {self.credit}"

    def getCredit(self):
        return self.credit

    def setName(self, name):
        self.name = name

    def printDetail(self):
        print(self.__str__())

    def scoreGrading(self, score):
       
        for grading in Course.grading:
            min_score = grading["min"]
            max_score = grading["max"]
            if min_score <= score <= max_score:
                return grading["Grade"]
        return None
    
    def setGradeScheme(self, scheme):
        
        if isinstance(scheme, list) and all(isinstance(grading, dict) and "Grade" in grading and "min" in grading and "max" in grading for grading in scheme):     
            self.gradeScheme = scheme
            return True  
        else:
            return False 


class Enrollment(persistent.Persistent):
    def __init__(self, courseObject, grade, studentObject):
        self.courseObject = courseObject
        self.studentObject = studentObject
        self.grade = grade

    def __str__(self) -> str:
        course_info = f"Course: ID: {self.courseObject.ID}, Credit: {self.courseObject.credit}, Name: {self.courseObject.name}"
        student_info = f"Student: ID: {self.studentObject.ID}, Name: {self.studentObject.name}, Enrollments: {len(self.studentObject.enrolls)}"
        return f"Enrollment:\n{course_info}, Grade: {self.grade}, {student_info}"

    def getCourse(self):
        return self.courseObject

    def getGrade(self):
        return self.grade

    def printDetail(self):
        print(self.__str__())


