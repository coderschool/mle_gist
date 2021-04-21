def test_is_equal_func():
    assert is_equal(1,1.0)==True
    assert is_equal(1.0,1)==True
    assert is_equal(1.001,1)==False
    assert is_equal(1,1.0001)==False
    assert is_equal(1,1.00001)==True
    assert is_equal(1.00002,1.00004)==False
    assert is_equal(1.00002,1.00003)==True

    assert is_equal('a','b')==False
    assert is_equal('abc','abc')==True

    assert is_equal((1,2,3),(1,2,3))==True
    assert is_equal([1,2,3],[1,2,3])==True
    assert is_equal([1.00001,2,3],[1,2,3])==True
    assert is_equal([1.0001,2,3],[1,2,3])==False
    assert is_equal([1.00001,-2.49999,3],[1,-2.5,3])==True
    assert is_equal((1.00001,-2.49999,3),(1,-2.5,3))==True
    assert is_equal(('a','bbb','c'),('a','bbb','c'))==True
    assert is_equal(('a','bbb','c',1,2,3),('a','bbb','c',1,2,3))==True
    assert is_equal([None],[None])==True
    assert is_equal([1,None],[1,None])==True
    assert is_equal([1.,None],[1.,None])==True
    assert is_equal(['a',None],['a',None])==True

    assert is_equal(np.array([1,2,3]),np.array([1,2,3]))==True
    assert is_equal(np.array([1.,2.,3.]),np.array([1,2,3]))==True
    assert is_equal(np.array([1.00001,-2.49999,3]),np.array([1,-2.5,3]))==True
    assert is_equal(np.array(('a','bbb','c')),np.array(('a','bbb','c')))==True
    assert is_equal(np.array([1,2,3]).astype(np.int8),np.array([1.00001,2,3]).astype(np.float16))==True
    assert is_equal(np.array([1,2,3]).astype(np.int16),np.array([1,2,3]).astype(np.uint8))==True


    assert is_equal(pd.Series([1,2,3]),pd.Series([1,2,3]))==True
    assert is_equal(pd.Series([1.,2.,3.]),pd.Series([1,2,3]))==True
    assert is_equal(pd.Series([1.00001,2,3]),pd.Series([1,2,3]))==True
    assert is_equal(pd.Series([1.0001,2,3]),pd.Series([1,2,3]))==False
    assert is_equal(pd.Series([1.00001,-2.49999,3]),pd.Series([1,-2.5,3]))==True
    assert is_equal(pd.Series(('a','bbb','c')),pd.Series(('a','bbb','c')))==True
    assert is_equal(pd.Series([1.00001,-2.49999,3],index=[0,1,2],name='asd'),pd.Series([1,-2.5,3],index=[2,3,4],name='sdf'))==True


    a = pd.DataFrame({'col1':[1.00001,2,3],'col2':['a','b','c'],'col3':[-2.49999,3,np.NaN]})
    b = pd.DataFrame({'col1':[1,2,3],'col2':['a','b','c'],'col3':[-2.5,3,np.NaN]})
    assert is_equal(a,b)==True
    a = pd.DataFrame({'col1':[1.00001,2,3],'col2':['a','b','c'],'col3':[-2.49999,3,np.NaN]})
    b = pd.DataFrame({'col4':[1,2,3],'col5':['a','b','c'],'col6':[-2.5,3,np.NaN]})
    assert is_equal(a,b)==False
    assert is_equal(a,b,same_col_name=True)==False
    assert is_equal(a,b,holaamigo='whatthefuck')==False
    assert is_equal(a,b,same_col_name = False)==True

    a = pd.DataFrame({'col1':[np.NaN]})
    b = pd.DataFrame({'col1':[np.NaN]})
    assert is_equal(a,b)==True
    a = pd.DataFrame({'col1':[np.NaN,1]})
    b = pd.DataFrame({'col1':[np.NaN,1]})
    assert is_equal(a,b)==True
    a = pd.DataFrame({'col1':[np.NaN,'a']})
    b = pd.DataFrame({'col1':[np.NaN,'a']})
    assert is_equal(a,b)==True

def testing(db, clean_up=False):
    print('TESTING COURSE API ------------------------------')
    # Creating a course
    db.post('/auth/drop-db', {'collectionName': 'Course'})
    course_name = 'Test Course 1'
    course = Course.create(db, {'name': course_name})
    print(course.to_json())
    assert course.name == course_name and course._id
    # Update course & get course by ID
    course_name = 'Test Course 0'
    course.name = course_name
    course.save(db)
    assert Course.get_course_by_id(db, course._id).name == course_name
    # Get list of course
    courses = Course.get_courses(db, output='object')
    assert course._id in [c._id for c in courses]
    courses_by_name = Course.get_courses_by_name(db, 'Test', output='object')
    assert [c._id for c in courses].sort() == [c._id for c in courses_by_name].sort()
    # Create the same course
    same_course = Course.create(db, {'name': course_name})
    assert getattr(same_course, '_id', '') == ''
    # Remove the course
    Course.remove_course_by_id(db, course._id)
    assert getattr(Course.get_course_by_id(db, course._id), '_id', '') == ''
    # Create another one
    course_name = 'Test Course 2'
    course = Course.create(db, {'name': course_name})
    print('-------------------------------------------------')
    
    print('TESTING COHORT API ------------------------------')
    db.post('/auth/drop-db', {'collectionName': 'Cohort'})
    # Creating a cohort without courseId
    cohort_name = 'Test Cohort'
    data = {'name': cohort_name}
    cohort = Cohort.create(db, data)
    assert getattr(cohort, '_id', '') == '' 
    # Create a new cohort
    data['courseId'] = course._id
    cohort = Cohort.create(db, data)
    print(cohort.to_json())
    assert cohort.name == cohort_name and cohort._id
    # Update cohort & get cohort by ID
    cohort_name = 'Test Cohort 0'
    cohort.name = cohort_name
    cohort.save(db)
    assert Cohort.get_cohort_by_id(db, cohort._id).name == cohort_name
    # Get list of cohort
    cohorts = Cohort.get_cohorts(db, output='object')
    assert cohort._id in [c._id for c in cohorts]
    cohorts_by_name = Cohort.get_cohorts_by_name(db, 'Test', output='object')
    assert [c._id for c in cohorts].sort() == [c._id for c in cohorts_by_name].sort()
    # Create the same cohort
    data['name'] = cohort_name
    same_cohort = Cohort.create(db, data)
    assert getattr(same_cohort, '_id', '') == ''
    # Remove the cohort
    Cohort.remove_cohort_by_id(db, cohort._id)
    assert getattr(Cohort.get_cohort_by_id(db, cohort._id), '_id', '') == ''
    # Create another one
    data['name'] = 'Test Cohort 2'
    cohort = Cohort.create(db, data)
    assert cohort.name == data['name'] and cohort._id
    print('-------------------------------------------------')
    
    print('TESTING STUDENT API ------------------------------')
    # Creating a student
    db.post('/auth/drop-db', {'collectionName': 'Student'})
    data = {'name': 'Test Student', 'email': 'test@coderschool.vn'}
    student = Student.create(db, data)
    print(student.to_json())
    assert student.email == data['email'] and student._id
    # Update student & get student by ID
    student_name = 'Test Student 0'
    student.name = student_name
    student.save(db)
    assert Student.get_student_by_id(db, student._id).name == student_name
    # Get list of student
    students = Student.get_students(db, output='object')
    assert student._id in [x._id for x in students]
    students_by_name = Student.get_students_by_name(db, 'Test', output='object')
    assert [c._id for c in students].sort() == [c._id for c in students_by_name].sort()
    # Create the same student
    same_student = Student.create(db, data)
    assert getattr(same_student, '_id', '') == ''
    # Remove the student
    Student.remove_student_by_id(db, student._id)
    assert getattr(Student.get_student_by_id(db, student._id), '_id', '') == ''
    # Add bulk
    arr = [{'name': 'Test Student 2', 'email': 'test2@coderschool.vn'},
            {'name': 'Test Student 3', 'email': 'test3@coderschool.vn'},
            {'name': 'Test Student 4', 'email': 'test4@coderschool.vn'}]
    students = Student.add_bulk(db, arr)
    assert len(Student.get_students(db)) == len(arr)
    assert sum([getattr(student, '_id', '') == '' for student in students]) == 0
    # Enroll students to the cohort
    db.post('/auth/drop-db', {'collectionName': 'CohortMember'})
    cohort.enroll_students(db, students)
    cohort_students = cohort.get_student_list(db, output='object')
    assert len(cohort_students) == len(CohortMember.get_cohort_members(db)) and len(cohort_students) == len(arr)
    print('-------------------------------------------------')
    
    print('TESTING COHORT GROUP ------------------------------')
    db.post('/auth/drop-db', {'collectionName': 'CohortGroup'})
    # Creating a cohort_group without cohortId
    cohort_group_name = 'Test CohortGroup'
    data = {'name': cohort_group_name}
    cohort_group = CohortGroup.create(db, data)
    assert getattr(cohort_group, '_id', '') == '' 
    # Create a new cohort_group
    cohort_group = CohortGroup.create(db, {'name': cohort_group_name, 'cohortId':cohort._id})
    print(cohort_group.to_json())
    assert cohort_group.name == cohort_group_name and cohort_group._id and cohort_group.cohort == cohort._id
    # Update cohort_group & get cohort_group by ID
    cohort_group_name = 'Test CohortGroup 0'
    cohort_group.name = cohort_group_name
    cohort_group.save(db)
    assert CohortGroup.get_cohort_group_by_id(db, cohort_group._id).name == cohort_group_name
    # Get list of cohort_group
    cohort_groups = CohortGroup.get_cohort_groups(db, output='object')
    assert cohort_group._id in [c._id for c in cohort_groups]
    cohort_groups_by_name = CohortGroup.get_cohort_groups_by_name(db, 'Test', output='object')
    assert [c._id for c in cohort_groups].sort() == [c._id for c in cohort_groups_by_name].sort()
    # Create the same cohort_group
    data['name'] = cohort_group_name
    same_cohort_group = CohortGroup.create(db, {'name': cohort_group_name, 'cohortId':cohort._id})
    assert getattr(same_cohort_group, '_id', '') == ''
    # Remove the cohort_group
    CohortGroup.remove_cohort_group_by_id(db, cohort_group._id)
    assert getattr(CohortGroup.get_cohort_group_by_id(db, cohort_group._id), '_id', '') == ''
    # Add bulk
    names = ['Group 1', 'Group 2', 'Group 3']
    cohort_groups = CohortGroup.create_groups_by_names(db, names, cohort._id)
    assert [c._id for c in cohort_groups].sort() == [c._id for c in CohortGroup.get_cohort_groups(db, output='object')].sort()
    print('-------------------------------------------------')
    
    print('TESTING COHORT MEMBER ------------------------------')
    # Creating a cohort_member without cohortId
    data = {'memberType': 'User', 'memberId': db.current_user._id}
    cohort_member = CohortMember.create(db, data)
    assert getattr(cohort_member, '_id', '') == '' 
    # Create a new cohort_member
    data['cohortId'] = cohort._id
    cohort_member = CohortMember.create(db, data)
    print(cohort_member.to_json())
    assert cohort_member.cohort == cohort._id and cohort_member._id
    # Update cohort_member & get cohort_member by ID
    cohort_member_status = 'Alumni'
    cohort_member.status = cohort_member_status
    cohort_member.save(db)
    assert CohortMember.get_cohort_member_by_id(db, cohort_member._id).status == cohort_member_status
    # Get list of cohort_member
    cohort_members = CohortMember.get_cohort_members(db, output='object')
    assert cohort_member._id in [c._id for c in cohort_members]
    # Create the same cohort_member
    same_cohort_member = CohortMember.create(db, data)
    assert getattr(same_cohort_member, '_id', '') == ''
    # Remove the cohort_member
    CohortMember.remove_cohort_member_by_id(db, cohort_member._id)
    assert getattr(CohortMember.get_cohort_member_by_id(db, cohort_member._id), '_id', '') == ''
    # Add student member to group
    student_members = CohortMember.get_cohort_members(db, output='object', filter={'cohort': cohort._id, 'memberType':'Student', 'EXACT': True})
    assert [s.member for s in student_members].sort() == [s._id for s in cohort_students].sort()
    added_students = []
    for index, group in enumerate(cohort_groups):
        group.add_members_to_group(db, [student_members[index]])
        added_students += group.get_student_list(db, output='object')
    assert [s._id for s in added_students].sort() == [s._id for s in cohort_students].sort()
    print('-------------------------------------------------')
    
    print('TESTING PROGRESS SCORE ------------------------------')
    db.post('/auth/drop-db', {'collectionName': 'ProgressScore'})
    # Creating a progress score without cohortMemberId
    data = {'activity':'Attendance', 'notes':'On time', 'score': 1}
    progress_score = ProgressScore.create(db, data)
    assert getattr(progress_score, '_id', '') == '' 
    # Create a new progress_score
    data['cohortMemberId'] = student_members[0]._id
    progress_score = ProgressScore.create(db, data)
    print(progress_score.to_json())
    student_members[0] = CohortMember.get_cohort_member_by_id(db, student_members[0]._id)
    assert progress_score.cohort_member == student_members[0]._id and progress_score._id and student_members[0].progress_score == 101
    # Update progress score
    progress_score.score = 2
    progress_score.save(db)
    student_members[0] = CohortMember.get_cohort_member_by_id(db, student_members[0]._id)
    assert progress_score._id and progress_score.score == 2 and student_members[0].progress_score == 102
    # Get progress_score by id
    assert ProgressScore.get_progress_score_by_id(db, progress_score._id).cohort_member == student_members[0]._id
    # Get list of progress_score
    progress_scores = ProgressScore.get_progress_scores(db, output='object')
    assert progress_score._id in [c._id for c in progress_scores]
    # Remove the progress_score
    ProgressScore.remove_progress_score_by_id(db, progress_score._id)
    assert getattr(ProgressScore.get_progress_score_by_id(db, progress_score._id), '_id', '') == ''
    student_members[0] = CohortMember.get_cohort_member_by_id(db, student_members[0]._id)
    assert student_members[0].progress_score == 100
    print('-------------------------------------------------')
    
    print('TESTING ASSIGNMENT API ------------------------------')
    db.post('/auth/drop-db', {'collectionName': 'Assignment'})
    # Creating an assignment without cohortId
    assignment_name = 'Test Assignment'
    data = {
        'name': assignment_name, 
        'questions': [
            {'question': 'Who am I', 'score': 10, 'solution': 'Minh'},
            {'question': 'What is the result of 1 + 1?', 'score': 90, 'solution': '2'}
        ]
    }
    assignment = Assignment.create(db, data)
    assert getattr(assignment, '_id', '') == '' 
    # Create a new assignment
    data['cohortId'] = cohort._id
    assignment = Assignment.create(db, data)
    print(assignment.to_json())
    assert assignment.name == assignment_name and assignment._id
    # Update assignment & get assignment by ID
    assignment_name = 'Test Assignment 0'
    assignment.name = assignment_name
    assignment.questions = [
        {'question': 'Who am I', 'score': 10, 'solution': 'I dont know'},
        {'question': 'What is the result of 2 * 2?', 'score': 10, 'solution': '4'},
        {'question': 'What is the result of 1 + 2?', 'score': 90, 'solution': '3'}
    ]
    assignment.save(db)
    updated_assignment = Assignment.get_assignment_by_id(db, assignment._id)
    assert updated_assignment.name == assignment_name and updated_assignment.questions[2]['solution'] == '3'
    # Get list of assignment
    assignments = Assignment.get_assignments(db, output='object')
    assert assignment._id in [c._id for c in assignments]
    assignments_by_name = Assignment.get_assignments_by_name(db, 'Test', output='object')
    assert [c._id for c in assignments].sort() == [c._id for c in assignments_by_name].sort()
    # Create the same assignment
    data['name'] = assignment_name
    same_assignment = Assignment.create(db, data)
    assert getattr(same_assignment, '_id', '') == ''
    # Remove the assignment
    Assignment.remove_assignment_by_id(db, assignment._id)
    assert getattr(Assignment.get_assignment_by_id(db, assignment._id), '_id', '') == ''
    # Create another one
    data['name'] = 'Test Assignment 2'
    assignment = Assignment.create(db, data)
    assert assignment.name == data['name'] and assignment._id
    print('-------------------------------------------------')
    
    print('TESTING SUBMISSION API ------------------------------')
    db.post('/auth/drop-db', {'collectionName': 'Submission'})
    # # Creating a submission without assignmentId
    data = {'email': students[0].email, 'answers': []}
    submission = Submission.create(db, data)
    assert getattr(submission, '_id', '') == '' 
    # Create a new submission with wrong email
    data['assignmentId'] = assignment._id
    data['email'] = 'unknown@email.com'
    submission = Submission.create(db, data)
    assert getattr(submission, '_id', '') == ''
    # Create a new submission with unenrolled student
    unenrolled_student = Student.create(db, {'name': 'Unenroll Student', 'email': 'unenroll@coderschool.vn'})
    data['email'] = unenrolled_student.email
    submission = Submission.create(db, data)
    assert getattr(submission, '_id', '') == ''
    # Create a new submission with cohortMemberId
    del data['email']
    data['cohortMemberId'] = student_members[1]._id
    submission = Submission.create(db, data)
    print(submission.to_json())
    assert submission.cohort_member == student_members[1]._id and submission._id
    # Create a new submission with enrolled student
    del data['cohortMemberId']
    data['email'] = students[1].email
    submission = Submission.create(db, data)
    print(submission.to_json())
    assert submission.cohort_member == student_members[1]._id and submission._id
    # Get list of submission
    submissions = Submission.get_submissions(db, output='object')
    assert submission._id in [c._id for c in submissions]
    print('-------------------------------------------------')
    
    
    if clean_up:
        print('CLEAN UP TEST DATA ------------------------------')
        db.post('/auth/drop-db', {'collectionName': 'Course'})
        db.post('/auth/drop-db', {'collectionName': 'Cohort'})
        db.post('/auth/drop-db', {'collectionName': 'Student'})
        db.post('/auth/drop-db', {'collectionName': 'CohortMember'})
        db.post('/auth/drop-db', {'collectionName': 'CohortGroup'})
        db.post('/auth/drop-db', {'collectionName': 'ProgressScore'})
        db.post('/auth/drop-db', {'collectionName': 'Assignment'})
        db.post('/auth/drop-db', {'collectionName': 'Submission'})
        print('-------------------------------------------------')
