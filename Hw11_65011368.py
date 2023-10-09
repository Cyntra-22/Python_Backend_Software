import ZODB
import ZODB.FileStorage
import transaction
import BTrees.OOBTree
import persistent

# Define the Course class
class Course(persistent.Persistent):
    def __init__(self, ID, credit, name):
        self.ID = ID
        self.credit = credit
        self.name = name

    def __str__(self) -> str:
        return f"ID:    {self.ID}, Course: {self.name}, Credit {self.credit}"

    def getCredit(self):
        return self.credit

    def setName(self, name):
        self.name = name

    def printDetail(self):
        print(self.__str__())

# Define the Student class
class Student(persistent.Persistent):
    def __init__(self, ID, name, enrolls):
        self.ID = ID
        self.name = name
        self.enrolls = enrolls  # List of enrollment objects

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

# Define the Enrollment class
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

import ZODB
import ZODB.FileStorage
import transaction
import BTrees.OOBTree


storage = ZODB.FileStorage.FileStorage('mydata2.fs')
db = ZODB.DB(storage)
connection = db.open()
root = connection.root

# Create Course objects
course1 = Course("CSCI101", 3, "Introduction to OOP")
course2 = Course("54011999", 4, "Calculus")

# Create Student objects and enroll them in courses
student1 = Student("101", "Alice",[])
student1.enrollCourse(course1, "C")

student2 = Student("201", "Bob",[])
student2.enrollCourse(course1, "A")
student2.enrollCourse(course2, "B")

student3 = Student("101", "Alice",[])
student3.enrollCourse(course2, "C")

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
