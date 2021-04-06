import requests
import re
import pandas as pd
import numpy as np

def check(submission, solution, assignment_type, **kargs):
    if (assignment_type == 'SQL'):
        conn = kargs['connection']
        df_sub = pd.read_sql_query(submission, conn)
        df_sol = pd.read_sql_query(solution, conn)
        try:
            assert df_sol.equals(df_sub)
            print('You passed! Good job!')
            return True
        except:
            print('Your solution is not correct, try again')
            return False

    if (assignment_type == 'Function'):
        test_cases = kargs['test_cases']
        
        try:
            score = 0
            exec(submission)
            exec(solution)
            func_name = submission.split('(')[0][4:]
            func_name_sol = solution.split('(')[0][4:]
            for test_case in test_cases:
                result = locals()[func_name_sol](*test_case)
                if (result == locals()[func_name](*test_case)):
                    score += 1
            print(f'You have passed {score}/{len(test_cases)} test cases')
            return score
        except:
            print('Your solution is not correct, try again')
            return 0

    if (assignment_type == "Expression"):
        try:
            result = eval(solution)
            result_sub = eval(submission)
            if (isinstance(result, (int, str, float, bool))):
                assert result == result_sub
            if (isinstance(result, (pd.DataFrame, pd.Series))):
                assert result.equals(result_sub)
            if (isinstance(result, (np.ndarray))):
                assert np.array_equal(result, result_sub)
            print('You passed! Good job!')
            return True
        except:
            print('Your solution is not correct, try again')
            return False

    if (assignment_type == "Value"):
        try:
            if (isinstance(result, (int, str, float, bool))):
                assert result == result_sub
            else:
                return False
            print('You passed! Good job!')
            return True
        except:
            print('Your solution is not correct, try again')
            return False


class User():
    def __init__(self, data):
        self.ATTRIBUTES = ['_id', 'name', 'email', 'password', 'created_by', 'updated_by', 'created_at', 'updated_at']
        for key in data.keys():
            snake_key = Utils.to_snake_case(key)
            if (snake_key in self.ATTRIBUTES):
                setattr(self, snake_key, data[key])

    def __repr__(self):
        name = getattr(self, 'name', '')
        email = getattr(self, 'email', '')
        return f'User {name} - {email}'

    def to_json(self):
        return {Utils.to_camel_case(key):getattr(self, key) for key in self.ATTRIBUTES if getattr(self, key, None)}
    
    @classmethod
    def register(cls, db_service, name, email, password):
        data = {"name":name, "email":email, 'password': password}
        res = db_service.post('/auth/register', data)
        return res
    
    
class DBService():
    def __init__(self, base_url, access_token=None):
        self.headers = {} if access_token is None else {'Authorization': f'Bearer {access_token}'}
        self.base_url = base_url
        self.current_user = {}

    def __repr__(self):
        return '<DBService>'

    def auth(self, google_access_token='', user=None):
        if ((google_access_token) and (type(google_access_token) is str)):
            response = requests.post(f'{self.base_url}/auth/login/google', {'access_token': google_access_token}).json()
        elif ((user) and (type(user) is User)):
            response = requests.post(f'{self.base_url}/auth/login', 
                                     {'email': getattr(user, 'email', ''), 
                                      'password': getattr(user, 'password', '')}
                                    ).json()
        else:
            print('ERROR: Credential Information required')
            return
        
        if ('success' in response):
            self.current_user = User(response['data']['user'])
            access_token = response['data']['accessToken']
            self.headers['Authorization'] = f'Bearer {access_token}'
            print(f"Welcome {self.current_user.email}!")
        else:
            print(f"ERROR: {response['errors']['message']}")
    
    def get(self, path):
        response = requests.get(self.base_url + path, headers=self.headers).json()
        if ('success' in response):
            return response['data']
        else:
            print(f"ERROR: {response['errors']['message']}")
            return None

    def post(self, path, data):
        response = requests.post(self.base_url + path, json=data, headers=self.headers).json()
        if ('success' in response):
            print(response['message'])
            return response['data']
        else:
            print(f"ERROR: {response['errors']['message']}")
            return None

    def put(self, path, data):
        response = requests.put(self.base_url + path, json=data, headers=self.headers).json()
        if ('success' in response):
            print(response['message'])
            return response['data']
        else:
            print(f"ERROR: {response['errors']['message']}")
            return None
    
    def delete(self, path):
        response = requests.delete(self.base_url + path, headers=self.headers).json()
        if ('success' in response):
            print(response['message'])
        else:
            print(f"ERROR: {response['errors']['message']}")

            
class Utils():
    @classmethod
    def to_camel_case(cls, snake_str):
        if (snake_str == '_id'): return snake_str
        components = snake_str.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])

    @classmethod
    def to_snake_case(cls, camel_str):
        if (camel_str == '_id'): return camel_str
        return re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()
    
    @classmethod
    def output_form(cls, class_, data_list, output):
        if (not data_list): 
            return []
        if (output == 'DataFrame'):
            return pd.DataFrame(data_list) 
        else:
            return [class_(instance) for instance in data_list]
    
    @classmethod
    def build_filter_params(cls, filter, pre_character='&'):
        if (not filter): return ''
        result = pre_character
        if 'EXACT' in filter:
            del filter['EXACT']
            for key in filter:
                result += f'{key}={filter[key]}&'
        else:
            for key in filter:
                result += f'{key}[$regex]={filter[key]}&{key}[$options]=i&'
        return result[:-1]
    
class Course():
    def __init__(self, data):
        self.ATTRIBUTES = ['_id', 'name', 'slug', 'duration', 'is_published', 'is_enrollable', 
                           'created_by', 'updated_by', 'created_at', 'updated_at']
        self.set_attributes(data)
                
    def set_attributes(self, data):
        if (not data):
            return
        for key in data.keys():
            snake_key = Utils.to_snake_case(key)
            if (snake_key in self.ATTRIBUTES):
                setattr(self, snake_key, data[key])

    def __repr__(self):
        name = getattr(self, 'name', '')
        _id = getattr(self, '_id', '')
        return f'Course {name} - {_id}'

    def to_json(self):
        return {Utils.to_camel_case(key):getattr(self, key) for key in self.ATTRIBUTES if getattr(self, key, None)}
    
    def save(self, db_service):
        if (not getattr(self, '_id', '')):
            new_course = db_service.post('/courses', self.to_json())
            if (new_course and '_id' in new_course):
                self.set_attributes(new_course)
        else:
            updated_course = db_service.put(f'/courses/{self._id}', self.to_json())

    @classmethod
    def create(cls, db_service, data):
        new_course = cls(data)
        new_course.save(db_service)
        return new_course

    @classmethod
    def get_courses(cls, db_service, output='DataFrame', filter={}):
        filter_params = Utils.build_filter_params(filter)
        courses = db_service.get(f'/courses?page=1&limit=1000{filter_params}')['courses']
        return Utils.output_form(cls, courses, output)

    @classmethod
    def get_courses_by_name(cls, db_service, course_name, output='DataFrame'):
        return cls.get_courses(db_service, output, {'name': course_name})

    @classmethod
    def get_course_by_id(cls, db_service, course_id):
        course = db_service.get(f'/courses/{course_id}')
        return Course(course)

    @classmethod
    def remove_course_by_id(cls, db_service, course_id):
        return db_service.delete(f'/courses/{course_id}')

    
class Cohort():
    def __init__(self, data):
        self.ATTRIBUTES = ['_id', 'course', 'course_id', 'name', 'slug', 'contact_list_sheet_url', 'support_email', 'prework_url', 'start_date', 'demo_day_date', 
                           'created_by', 'updated_by', 'created_at', 'updated_at']
        self.set_attributes(data)
                
    def set_attributes(self, data):
        if (not data):
            return
        for key in data.keys():
            snake_key = Utils.to_snake_case(key)
            if (snake_key in self.ATTRIBUTES):
                setattr(self, snake_key, data[key])

    def __repr__(self):
        name = getattr(self, 'name', '')
        _id = getattr(self, '_id', '')
        return f'Cohort {name} - {_id}'

    def to_json(self):
        return {Utils.to_camel_case(key):getattr(self, key) for key in self.ATTRIBUTES if getattr(self, key, None)}
    
    def save(self, db_service):
        if (not getattr(self, '_id', '')):
            new_cohort = db_service.post('/cohorts', self.to_json())
            if (new_cohort and '_id' in new_cohort):
                self.set_attributes(new_cohort)
        else:
            updated_cohort = db_service.put(f'/cohorts/{self._id}', self.to_json())
                
    def enroll_single_student(self, db_service, student, status='participant'):
        if (type(student) is not Student):
            print('ERROR: Data must be instance of Student')
            return
        if (not getattr(self, '_id', '')):
            print('ERROR: Cohort undefined')
            return
        if (not getattr(student, '_id', '')):
            print('ERROR: Student undefined')
            return
                
        data = {'cohortId': self._id, 'memberType':'Student', 'memberId':student._id, 'status': status}
        db_service.post('/cohort-members', data)
        
    def enroll_students(self, db_service, students, status='participant'):
        for student in students:
            self.enroll_single_student(db_service, student, status)
            
    def get_student_list(self, db_service, output='DataFrame'):
        if (not getattr(self, '_id', '')):
            print('ERROR: Cohort undefined')
            return
        students = db_service.get(f'/cohorts/{self._id}/students?page=1&limit=1000')['students']
        return Utils.output_form(Student, students, output)


    @classmethod
    def create(cls, db_service, data):
        new_cohort = cls(data)
        new_cohort.save(db_service)
        return new_cohort
    
    @classmethod
    def get_cohorts(cls, db_service, output='DataFrame', filter={}):
        filter_params = Utils.build_filter_params(filter)
        cohorts = db_service.get(f'/cohorts?page=1&limit=1000{filter_params}')['cohorts']
        return Utils.output_form(cls, cohorts, output)

    @classmethod
    def get_cohorts_by_name(cls, db_service, cohort_name, output='DataFrame'):
        return cls.get_cohorts(db_service, output, {'name': cohort_name})

    @classmethod
    def get_cohort_by_id(cls, db_service, cohort_id):
        cohort = db_service.get(f'/cohorts/{cohort_id}')
        return Cohort(cohort)

    @classmethod
    def remove_cohort_by_id(cls, db_service, cohort_id):
        return db_service.delete(f'/cohorts/{cohort_id}')

    
class Student():
    def __init__(self, data):
        self.ATTRIBUTES = ['_id', 'name', 'email', 'sub_emails', 'first_name', 'last_name', 'gender', 'phone_number', 'linked_in_url', 'current_employment_status',
                           'current_company', 'engineering_experience', 'personal_website', 'github_profile', 'address', 'city', 'country',
                           'progress_score', 'status', 'cohort_group_name', 'cohort_member_id',
                           'created_by', 'updated_by', 'created_at', 'updated_at']
        self.set_attributes(data)
                
    def set_attributes(self, data):
        if (not data):
            return
        for key in data.keys():
            snake_key = Utils.to_snake_case(key)
            if (snake_key in self.ATTRIBUTES):
                setattr(self, snake_key, data[key])

    def __repr__(self):
        name = getattr(self, 'name', '')
        email = getattr(self, 'email', '')
        return f'Student {name} - {email}'

    def to_json(self):
        return {Utils.to_camel_case(key):getattr(self, key) for key in self.ATTRIBUTES if getattr(self, key, None)}
    
    def save(self, db_service):
        if (not getattr(self, '_id', '')):
            new_student = db_service.post('/students', self.to_json())
            if (new_student and '_id' in new_student):
                self.set_attributes(new_student)
        else:
            updated_student = db_service.put(f'/students/{self._id}', self.to_json())

    @classmethod
    def create(cls, db_service, data):
        new_student = cls(data)
        new_student.save(db_service)
        return new_student
    
    @classmethod
    def add_bulk(cls, db_service, std_list):
        return [cls.create(db_service, std) for std in std_list]
    
    @classmethod
    def get_students(cls, db_service, output='DataFrame', filter={}):
        filter_params = Utils.build_filter_params(filter)
        students = db_service.get(f'/students?page=1&limit=1000{filter_params}')['students']
        return Utils.output_form(cls, students, output)

    @classmethod
    def get_students_by_name(cls, db_service, student_name, output='DataFrame'):
        return cls.get_students(db_service, output, {'name': student_name})

    @classmethod
    def get_student_by_id(cls, db_service, student_id):
        student = db_service.get(f'/students/{student_id}')
        return Student(student)
    
    @classmethod
    def remove_student_by_id(cls, db_service, student_id):
        return db_service.delete(f'/students/{student_id}')


class CohortMember():
    def __init__(self, data):
        self.ATTRIBUTES = ['_id', 'cohort', 'cohort_id', 'member_type', 'member', 'member_id', 'status', 'withdrawn_at', 'progress_score',
                           'cohort_group', 'cohort_group_id',
                           'created_by', 'updated_by', 'created_at', 'updated_at']
        self.set_attributes(data)
                
    def set_attributes(self, data):
        if (not data):
            return
        for key in data.keys():
            snake_key = Utils.to_snake_case(key)
            if (snake_key in self.ATTRIBUTES):
                setattr(self, snake_key, data[key])

    def __repr__(self):
        cohort = getattr(self, 'cohort', '')
        member = getattr(self, 'member', '')
        member_type = getattr(self, 'member_type', '')
        return f'Cohort Member: Cohort {cohort} - Member {member} - Member Type {member_type}'

    def to_json(self):
        return {Utils.to_camel_case(key):getattr(self, key) for key in self.ATTRIBUTES if getattr(self, key, None)}
    
    def save(self, db_service):
        if (not getattr(self, '_id', '')):
            new_cohort_member = db_service.post('/cohort-members', self.to_json())
            if (new_cohort_member and '_id' in new_cohort_member):
                self.set_attributes(new_cohort_member)
        else:
            updated_cohort_member = db_service.put(f'/cohort-members/{self._id}', self.to_json())

    @classmethod
    def create(cls, db_service, data):
        new_cohort_member = cls(data)
        new_cohort_member.save(db_service)
        return new_cohort_member
    
    @classmethod
    def get_cohort_members(cls, db_service, output='DataFrame', filter={}):
        filter_params = Utils.build_filter_params(filter)
        cohort_members = db_service.get(f'/cohort-members?page=1&limit=1000{filter_params}')['cohortMembers']
        return Utils.output_form(cls, cohort_members, output)

    @classmethod
    def get_cohort_member_by_id(cls, db_service, cohort_member_id):
        cohort_member = db_service.get(f'/cohort-members/{cohort_member_id}')
        return CohortMember(cohort_member)

    @classmethod
    def remove_cohort_member_by_id(cls, db_service, cohort_member_id):
        return db_service.delete(f'/cohort-members/{cohort_member_id}')


class CohortGroup():
    def __init__(self, data):
        self.ATTRIBUTES = ['_id', 'cohort', 'cohort_id', 'name', 
                           'created_by', 'updated_by', 'created_at', 'updated_at']
        self.set_attributes(data)
                
    def set_attributes(self, data):
        if (not data):
            return
        for key in data.keys():
            snake_key = Utils.to_snake_case(key)
            if (snake_key in self.ATTRIBUTES):
                setattr(self, snake_key, data[key])

    def __repr__(self):
        cohort = getattr(self, 'cohort', '')
        name = getattr(self, 'name', '')
        return f'Cohort Group: Cohort {cohort} - Name {name}'

    def to_json(self):
        return {Utils.to_camel_case(key):getattr(self, key) for key in self.ATTRIBUTES if getattr(self, key, None)}
    
    def save(self, db_service):
        if (not getattr(self, '_id', '')):
            new_cohort_group = db_service.post('/cohort-groups', self.to_json())
            if (new_cohort_group and '_id' in new_cohort_group):
                self.set_attributes(new_cohort_group)
        else:
            updated_cohort_group = db_service.put(f'/cohort-groups/{self._id}', self.to_json())
            
    def add_single_member(self, db_service, member, status='participant'):
        if (type(member) is not CohortMember):
            print('ERROR: Data must be instance of Cohort Member')
            return
        if (not getattr(self, '_id', '')):
            print('ERROR: Cohort Group undefined')
            return
        if (not getattr(member, '_id', '')):
            print('ERROR: Cohort Member undefined')
            return
                
        member.cohort_group_id = self._id
        member.save(db_service)
            
    def add_members_to_group(self, db_service, members):
        for member in members:
            self.add_single_member(db_service, member)
            
    def get_student_list(self, db_service, output='DataFrame'):
        if (not getattr(self, '_id', '')):
            print('ERROR: Cohort Group undefined')
            return
        students = db_service.get(f'/cohort-groups/{self._id}/students?page=1&limit=1000')['students']
        return Utils.output_form(Student, students, output)
        
    @classmethod
    def create(cls, db_service, data):
        new_cohort_group = cls(data)
        new_cohort_group.save(db_service)
        return new_cohort_group
    
    @classmethod
    def create_groups_by_names(cls, db_service, names, cohort_id):
        return [cls.create(db_service, {'name': name, 'cohortId': cohort_id}) for name in names]
    
    @classmethod
    def get_cohort_groups(cls, db_service, output='DataFrame', filter={}):
        filter_params = Utils.build_filter_params(filter)
        cohort_groups = db_service.get(f'/cohort-groups?page=1&limit=1000{filter_params}')['cohortGroups']
        return Utils.output_form(cls, cohort_groups, output)

    @classmethod
    def get_cohort_groups_by_name(cls, db_service, cohort_group_name, output='DataFrame'):
        return cls.get_cohort_groups(db_service, output, {'name': cohort_group_name})

    @classmethod
    def get_cohort_group_by_id(cls, db_service, cohort_group_id):
        cohort_group = db_service.get(f'/cohort-groups/{cohort_group_id}')
        return Student(cohort_group)

    @classmethod
    def remove_cohort_group_by_id(cls, db_service, cohort_group_id):
        return db_service.delete(f'/cohort-groups/{cohort_group_id}')


class ProgressScore():
    def __init__(self, data):
        self.ATTRIBUTES = ['_id', 'cohort_member', 'cohort_member_id', 'activity', 'notes', 'score',
                           'created_by', 'updated_by', 'created_at', 'updated_at']
        self.set_attributes(data)
                
    def set_attributes(self, data):
        if (not data):
            return
        for key in data.keys():
            snake_key = Utils.to_snake_case(key)
            if (snake_key in self.ATTRIBUTES):
                setattr(self, snake_key, data[key])

    def __repr__(self):
        cohort_member = getattr(self, 'cohort_member', '')
        activity = getattr(self, 'activity', '')
        score = getattr(self, 'score', '')
        return f'Progress Score: Member {cohort_member} - Activity {name} - Score {score}'

    def to_json(self):
        return {Utils.to_camel_case(key):getattr(self, key) for key in self.ATTRIBUTES if getattr(self, key, None)}
    
    def save(self, db_service):
        if (not getattr(self, '_id', '')):
            new_progress_score = db_service.post('/progress-scores', self.to_json())
            if (new_progress_score and '_id' in new_progress_score):
                self.set_attributes(new_progress_score)
        else:
            updated_progress_score = db_service.put(f'/progress-scores/{self._id}', self.to_json())

    @classmethod
    def create(cls, db_service, data):
        new_progress_score = cls(data)
        new_progress_score.save(db_service)
        return new_progress_score
    
    @classmethod
    def get_progress_scores(cls, db_service, output='DataFrame', filter={}):
        filter_params = Utils.build_filter_params(filter)
        progress_scores = db_service.get(f'/progress-scores?page=1&limit=1000{filter_params}')['progressScores']
        return Utils.output_form(cls, progress_scores, output)

    @classmethod
    def get_progress_score_by_id(cls, db_service, progress_score_id):
        progress_score = db_service.get(f'/progress-scores/{progress_score_id}')
        return ProgressScore(progress_score)

    @classmethod
    def remove_progress_score_by_id(cls, db_service, progress_score_id):
        return db_service.delete(f'/progress-scores/{progress_score_id}')


class Assignment():
    def __init__(self, data):
        self.ATTRIBUTES = ['_id', 'name', 'slug', 'cohort','cohort_id', 'assignment_type', 'questions', 'assignment_url', 
                           'max_progress_score', 'member_only',
                           'created_by', 'updated_by', 'created_at', 'updated_at']
        self.set_attributes(data)
                
    def set_attributes(self, data):
        if (not data):
            return
        for key in data.keys():
            snake_key = Utils.to_snake_case(key)
            if (snake_key in self.ATTRIBUTES):
                setattr(self, snake_key, data[key])

    def __repr__(self):
        name = getattr(self, 'name', '')
        _id = getattr(self, '_id', '')
        return f'Assignment {name} - {_id}'

    def to_json(self):
        return {Utils.to_camel_case(key):getattr(self, key) for key in self.ATTRIBUTES if getattr(self, key, None)}
    
    def save(self, db_service):
        if (not getattr(self, '_id', '')):
            new_assignment = db_service.post('/assignments', self.to_json())
            if (new_assignment and '_id' in new_assignment):
                self.set_attributes(new_assignment)
        else:
            updated_assignment = db_service.put(f'/assignments/{self._id}', self.to_json())

    @classmethod
    def create(cls, db_service, data):
        new_assignment = cls(data)
        new_assignment.save(db_service)
        return new_assignment
    
    @classmethod
    def get_assignments(cls, db_service, output='DataFrame', filter={}):
        filter_params = Utils.build_filter_params(filter)
        assignments = db_service.get(f'/assignments?page=1&limit=1000{filter_params}')['assignments']
        return Utils.output_form(cls, assignments, output)

    @classmethod
    def get_assignments_by_name(cls, db_service, assignment_name, output='DataFrame'):
        return cls.get_assignments(db_service, output, {'name': assignment_name})

    @classmethod
    def get_assignment_by_id(cls, db_service, assignment_id):
        assignment = db_service.get(f'/assignments/{assignment_id}')
        return Assignment(assignment)

    @classmethod
    def remove_assignment_by_id(cls, db_service, assignment_id):
        return db_service.delete(f'/assignments/{assignment_id}')


class Attendance():
    def __init__(self, data):
        self.ATTRIBUTES = ['_id', 'cohort_member', 'cohort_member_id', 'session', 'status', 'notes', 
                           'created_by', 'updated_by', 'created_at', 'updated_at']
        self.set_attributes(data)
                
    def set_attributes(self, data):
        if (not data):
            return
        for key in data.keys():
            snake_key = Utils.to_snake_case(key)
            if (snake_key in self.ATTRIBUTES):
                setattr(self, snake_key, data[key])

    def __repr__(self):
        cohort_member = getattr(self, 'cohort_member', '')
        session = getattr(self, 'session', '')
        status = getattr(self, 'status', '')
        return f'Attendance: Cohort Member {cohort_member} - Session {session} - Status {status}'

    def to_json(self):
        return {Utils.to_camel_case(key):getattr(self, key) for key in self.ATTRIBUTES if getattr(self, key, None)}
    
    def save(self, db_service):
        if (not getattr(self, '_id', '')):
            new_attendance = db_service.post('/attendances', self.to_json())
            if (new_attendance and '_id' in new_attendance):
                self.set_attributes(new_attendance)
        else:
            updated_attendance = db_service.put(f'/attendances/{self._id}', self.to_json())

    @classmethod
    def create(cls, db_service, data):
        new_attendance = cls(data)
        new_attendance.save(db_service)
        return new_attendance

    @classmethod
    def get_attendances(cls, db_service, output='DataFrame', filter={}):
        filter_params = Utils.build_filter_params(filter)
        attendances = db_service.get(f'/attendances?page=1&limit=1000{filter_params}')['attendances']
        return Utils.output_form(cls, attendances, output)

    @classmethod
    def get_attendance_by_id(cls, db_service, attendance_id):
        attendance = db_service.get(f'/attendances/{attendance_id}')
        return Attendance(attendance)

    @classmethod
    def remove_attendance_by_id(cls, db_service, attendance_id):
        return db_service.delete(f'/attendances/{attendance_id}')


class Submission():
    def __init__(self, data):
        self.ATTRIBUTES = ['_id', 'cohort_member', 'cohort_member_id', 'assignment', 'assignment_id', 'submission_url', 
                           'email', 'name', 'answers', 'entries',
                           'created_by', 'updated_by', 'created_at', 'updated_at']
        self.set_attributes(data)
                
    def set_attributes(self, data):
        if (not data):
            return
        for key in data.keys():
            snake_key = Utils.to_snake_case(key)
            if (snake_key in self.ATTRIBUTES):
                setattr(self, snake_key, data[key])

    def __repr__(self):
        name = getattr(self, 'name', '')
        _id = getattr(self, '_id', '')
        return f'Submission {name} - {_id}'

    def to_json(self):
        return {Utils.to_camel_case(key):getattr(self, key) for key in self.ATTRIBUTES if getattr(self, key, None)}
    
    def save(self, db_service):
        if (not getattr(self, '_id', '')):
            new_submission = db_service.post('/submissions', self.to_json())
            if (new_submission and '_id' in new_submission):
                self.set_attributes(new_submission)
        else:
            updated_submission = db_service.put(f'/submissions/{self._id}', self.to_json())

    @classmethod
    def create(cls, db_service, data):
        new_submission = cls(data)
        new_submission.save(db_service)
        return new_submission

    @classmethod
    def get_submissions(cls, db_service, output='DataFrame', filter={}):
        filter_params = Utils.build_filter_params(filter)
        submissions = db_service.get(f'/submissions?page=1&limit=1000{filter_params}')['submissions']
        return Utils.output_form(cls, submissions, output)

    @classmethod
    def get_submission_by_id(cls, db_service, submission_id):
        submission = db_service.get(f'/submissions/{submission_id}')
        return Submission(submission)

    @classmethod
    def remove_submission_by_id(cls, db_service, submission_id):
        return db_service.delete(f'/submissions/{attendance_id}')


class SubmissionGrade():
    def __init__(self, data):
        self.ATTRIBUTES = ['_id', 'submission', 'submission_id', 'grader', 'grader_id', 'notes', 'total_score', 'status',
                           'created_by', 'updated_by', 'created_at', 'updated_at']
        self.set_attributes(data)
                
    def set_attributes(self, data):
        if (not data):
            return
        for key in data.keys():
            snake_key = Utils.to_snake_case(key)
            if (snake_key in self.ATTRIBUTES):
                setattr(self, snake_key, data[key])

    def __repr__(self):
        name = getattr(self, 'name', '')
        _id = getattr(self, '_id', '')
        return f'Submission Grade {name} - {_id}'

    def to_json(self):
        return {Utils.to_camel_case(key):getattr(self, key) for key in self.ATTRIBUTES if getattr(self, key, None)}
    
    def save(self, db_service):
        if (not getattr(self, '_id', '')):
            new_submission_grade = db_service.post('/submission-grades', self.to_json())
            if (new_submission_grade and '_id' in new_submission_grade):
                self.set_attributes(new_submission_grade)
        else:
            updated_submission_grade = db_service.put(f'/submission-grades/{self._id}', self.to_json())

    @classmethod
    def create(cls, db_service, data):
        new_submission_grade = cls(data)
        new_submission_grade.save(db_service)
        return new_submission_grade

    @classmethod
    def get_submission_grades(cls, db_service, output='DataFrame', filter={}):
        filter_params = Utils.build_filter_params(filter)
        submission_grades = db_service.get(f'/submission-grades?page=1&limit=1000{filter_params}')['submissionGrades']
        return Utils.output_form(cls, submission_grades, output)

    @classmethod
    def get_submission_grade_by_id(cls, db_service, submission_grade_id):
        submission_grade = db_service.get(f'/submission-grades/{submission_grade_id}')
        return SubmissionGrade(submission_grade)

    @classmethod
    def remove_submission_grade_by_id(cls, db_service, submission_grade_id):
        return db_service.delete(f'/submission-grades/{attendance_id}')

API_URL = 'https://cs-platform-306304.et.r.appspot.com/api'
db = DBService(API_URL)