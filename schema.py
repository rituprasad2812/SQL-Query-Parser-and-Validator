SCHEMA = {

    'courses' : {
        'course_id' : 'INT',
        'course_name' : 'VARCHAR',
        'credits' : 'INT'
    },

    'students' : {
        'student_id' : 'INT',
        'name' : 'VARCHAR',
        'age' : 'INT',
        'department' : 'VARCHAR'
    },

    'enrollments' : {
        'enrollment_id' : 'INT',
        'student_id' : 'INT',
        'course_id' : 'INT'
    }
}