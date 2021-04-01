import requests
import pandas as pd

class DBService():
    def __init__(self, base_url, access_token=None):
        self.headers = {} if access_token is None else {'Authorization': f'Bearer {access_token}'}
        self.base_url = base_url
        self.current_user = {}

    def __repr__(self):
        return '<DBService>'

    def auth(self, google_access_token):
        response = requests.post(f'{self.base_url}/auth/login/google', {'access_token': google_access_token}).json()
        if ('success' in response):
            self.current_user = response['data']['user']
            access_token = response['data']['accessToken']
            self.headers['Authorization'] = f'Bearer {access_token}'
            print(f"Welcome {self.current_user['email']}!")
        else:
            print(f"ERROR: {response['errors']['message']}")
            
    def login_with_email(self, email, password):
        response = requests.post(f'{self.base_url}/auth/login', {'email': email, 'password':password}).json()
        if ('success' in response):
            self.current_user = response['data']['user']
            access_token = response['data']['accessToken']
            self.headers['Authorization'] = f'Bearer {access_token}'
            print(f"Welcome {self.current_user['email']}!")
        else:
            print(f"ERROR: {response['errors']['message']}")
    
    def get(self, path):
        response = requests.get(self.base_url + path, headers=self.headers).json()
        if ('success' in response):
            return response['data']
        else:
            print(f"ERROR: {response['errors']['message']}")
            return {}

    def post(self, path, data):
        response = requests.post(self.base_url + path, data, headers=self.headers).json()
        if ('success' in response):
            return response['data']
        else:
            print(f"ERROR: {response['errors']['message']}")
            return {}
    
    def delete(self, path):
        response = requests.delete(self.base_url + path, headers=self.headers).json()
        if ('success' in response):
            print('Delete sucessfully')
            return True
        else:
            print(f"ERROR: {response['errors']['message']}")
            return False

class Cohort():
    def __init__(self, cohort_dict):
        self.cohort_id = cohort_dict['_id'] if '_id' in cohort_dict else ''
        self.name = cohort_dict['name'] if 'name' in cohort_dict else ''
        self.students = cohort_dict['students'] if 'students' in cohort_dict else []
        self.created_at = cohort_dict['createdAt'] if 'createdAt' in cohort_dict else '' 
        self.updated_at = cohort_dict['updatedAt'] if 'updatedAt' in cohort_dict else ''
        self.created_by = cohort_dict['createdBy'] if 'createdBy' in cohort_dict else ''
        self.updated_by = cohort_dict['updatedBy'] if 'updatedBy' in cohort_dict else ''

    def __repr__(self):
        return f'Cohort {self.name} - {self.cohort_id}'

    def json(self):
        return {'_id': self.cohort_id, 
                'name': self.name,
                'students': self.students,
                'createdAt': self.created_at,
                'updatedAt': self.updated_at,
                'createdBy': self.created_by,
                'updatedBy': self.updated_by,}
    
    @classmethod
    def get_cohorts(cls, db_service):
        cohorts = db_service.get('/cohorts?page=1&limit=100')['cohorts']
        return pd.DataFrame(cohorts)

    @classmethod
    def get_cohort_by_id(cls, db_service, cohort_id):
        cohort = db_service.get(f'/cohorts/{cohort_id}')
        return Cohort(cohort)

    @classmethod
    def create_cohort_by_name(cls, db_service, cohort_name):
        df = cls.get_cohorts(db_service)
        if (df[df['name'] == cohort_name].size > 0):
            cohort_id = df[df['name'] == cohort_name]['_id'].values[0]
            print(f"Cohort already exists {cohort_id}")
            return None
        else:
            new_cohort = db_service.post('/cohorts', {"name": cohort_name})
            if (new_cohort):
                cohort_id = new_cohort['_id']
                print(f"New Cohort has been created {cohort_id}")
                return Cohort(new_cohort)
            else:
                return None

    @classmethod
    def remove_cohort_by_id(cls, db_service, cohort_id):
        return db_service.delete(f'/cohorts/{cohort_id}')

class Student():
    def __init__(self, student_dict):
        self.student_id = student_dict['_id']
        self.name = student_dict['name']
        self.email = student_dict['email']
        self.cohorts = student_dict['cohorts']
        self.created_at = student_dict['createdAt']
        self.updated_at = student_dict['updatedAt']
        self.created_by = student_dict['createdBy']
        self.updated_by = student_dict['updatedBy']

    def __repr__(self):
        return f'Student {self.name} - {self.email}'

    def json(self):
        return {'_id': self.cohort_id, 
                'name': self.name,
                'email': self.email,
                'cohorts': self.cohorts,
                'createdAt': self.created_at,
                'updatedAt': self.updated_at,
                'createdBy': self.created_by,
                'updatedBy': self.updated_by,}
    
    @classmethod
    def get_students(cls, db_service):
        students = db_service.get('/students?page=1&limit=100')['students']
        return pd.DataFrame(students)

    @classmethod
    def get_student_by_id(cls, db_service, student_id):
        student = db_service.get(f'/students/{student_id}')
        return Student(student)

    @classmethod
    def add_student_to_cohort(cls, db_service, std_name, std_email, cohort_id):
        data = {"name": std_name, "email": std_email, "cohortId": cohort_id}
        new_student = db_service.post('/students', data)
        if (new_student):
            return Student(new_student)
        else:
            return None

    @classmethod
    def remove_student_by_id(cls, db_service, student_id):
        return db_service.delete(f'/students/{student_id}')
    
class User():
    def __init__(self, user_dict):
        self.student_id = user_dict['_id']
        self.name = user_dict['name']
        self.email = user_dict['email']
        

    def __repr__(self):
        return f'Student {self.name} - {self.email}'

    def json(self):
        return {'_id': self.cohort_id, 
                'name': self.name,
                'email': self.email}
    
    @classmethod
    def register(cls, db_service, name, email, password):
        data = {"name":name, "email":email, 'password': password}
        res = db_service.post('/auth/register', data)
        return res