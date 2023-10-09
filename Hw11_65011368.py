import ZODB
import ZODB.FileStorage
import transaction
import BTrees.OOBTree
import persistent

class Student(persistent.Persistent):
    def __init__(self, ID, name, enrolls):
        self.ID = ID
        self.name = name
        self.enrolls = enrolls  # list of enrollment objects

    def __str__(self) -> str:
        course_list = []
        for enroll in self.enrolls:
            course = enroll.courseObject
            course_info = f"Course: ID: {course.ID}, Name: {course.name}, Credit: {course.credit}, Score: {enroll.score}, Grade: {enroll.calculateGrade()}"
            course_list.append(course_info)

        transcript = f"Transcript\nID: {self.ID}, Name: {self.name}, Enrollments: {len(self.enrolls)}\n"
        transcript += "\n".join(course_list)
        transcript += f"\nGPA: {self.calculateGPA():.2f}"
        return transcript

    def enrollCourse(self, courseObject, score):
        enrollment = Enrollment(courseObject, self, score)
        self.enrolls.append(enrollment)
        return enrollment

    def calculateGPA(self):
        total_credit = 0
        total_score = 0

        for enroll in self.enrolls:
            course = enroll.courseObject
            credit = course.credit
            score = enroll.score
            grade = enroll.calculateGrade()

            if grade:
                total_credit += credit
                total_score += credit * self.gradeToPoint(grade)

        if total_credit == 0:
            return 0.0

        return total_score / total_credit

    def gradeToPoint(self, grade):
        grade_scheme = self.enrolls[0].courseObject.gradeScheme
        for entry in grade_scheme:
            if entry["Grade"] == grade:
                return entry["Point"]
        return 0.0

    def printTranscript(self):
        print(self.__str__())

    def setName(self, name):
        self.name = name


class Course(persistent.Persistent):
    grading = [
        {"Grade": "A", "min": 80, "max": 100, "Point": 4.0},
        {"Grade": "B", "min": 70, "max": 79, "Point": 3.0},
        {"Grade": "C", "min": 60, "max": 69, "Point": 2.0},
        {"Grade": "D", "min": 50, "max": 59, "Point": 1.0},
        {"Grade": "F", "min": 0, "max": 49, "Point": 0.0},
    ]

    def __init__(self, ID, credit, name, gradeScheme=None):
        self.ID = ID
        self.credit = credit
        self.name = name
        self.gradeScheme = gradeScheme if gradeScheme is not None else []

    def __str__(self) -> str:
        return f"ID: {self.ID}, Course: {self.name}, Credit: {self.credit}"

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
        if isinstance(scheme, list) and all(isinstance(grading, dict) and "Grade" in grading and "min" in grading and "max" in grading and "Point" in grading for grading in scheme):
            self.gradeScheme = scheme
            return True
        else:
            return False


class Enrollment(persistent.Persistent):
    def __init__(self, courseObject, studentObject, score):
        self.courseObject = courseObject
        self.studentObject = studentObject
        self.score = score

    def __str__(self) -> str:
        course_info = f"Course: ID: {self.courseObject.ID}, Credit: {self.courseObject.credit}, Name: {self.courseObject.name}"
        student_info = f"Student: ID: {self.studentObject.ID}, Name: {self.studentObject.name}, Enrollments: {len(self.studentObject.enrolls)}"
        return f"Enrollment:\n{course_info}, Score: {self.score}, Grade: {self.calculateGrade()}, {student_info}"

    def getCourse(self):
        return self.courseObject

    def getGrade(self):
        return self.grade

    def getScore(self):
        return self.score

    def calculateGrade(self):
        # Calculate the grade based on the score and course's grading scheme
        grade_scheme = self.courseObject.gradeScheme
        if grade_scheme:
            for entry in grade_scheme:
                min_score = entry["min"]
                max_score = entry["max"]
                if min_score <= self.score <= max_score:
                    return entry["Grade"]
        return None

    def setScore(self, score):
        self.score = score

    def printDetail(self):
        print(self.__str__())

storage = ZODB.FileStorage.FileStorage('mydata2.fs')
db = ZODB.DB(storage)
connection = db.open()
root = connection.root

# Create Course objects
course1 = Course("CSCI101", 3, "Introduction to OOP", [
    {"Grade": "A", "min": 80, "max": 100, "Point": 4.0},
    {"Grade": "B", "min": 70, "max": 79, "Point": 3.0},
    {"Grade": "C", "min": 60, "max": 69, "Point": 2.0},
    {"Grade": "D", "min": 50, "max": 59, "Point": 1.0},
    {"Grade": "F", "min": 0, "max": 49, "Point": 0.0},
])
course2 = Course("54011999", 4, "Calculus", [
    {"Grade": "A", "min": 80, "max": 100, "Point": 4.0},
    {"Grade": "B", "min": 70, "max": 79, "Point": 3.0},
    {"Grade": "C", "min": 60, "max": 69, "Point": 2.0},
    {"Grade": "D", "min": 50, "max": 59, "Point": 1.0},
    {"Grade": "F", "min": 0, "max": 49, "Point": 0.0},
])

# Create Student objects and enroll them in courses
student1 = Student("101", "Alice", [])
student1.enrollCourse(course1, 75)

student2 = Student("201", "Bob", [])
student2.enrollCourse(course1, 50)
student2.enrollCourse(course2, 80)

student3 = Student("301", "Charlie", [])
student3.enrollCourse(course2, 60)

# Store the objects in the database using BTrees
root.courses = BTrees.OOBTree.BTree()
root.students = BTrees.OOBTree.BTree()

root.courses[course1.ID] = course1
root.courses[course2.ID] = course2

root.students[student1.ID] = student1
root.students[student2.ID] = student2
root.students[student3.ID] = student3

# Commit the transaction to save the changes
transaction.commit()

# Reloading the data and displaying it
courses = root.courses
for course_id, course in courses.items():
    course.printDetail()

print()

students = root.students
for student_id, student in students.items():
    student.printTranscript()
    print()
