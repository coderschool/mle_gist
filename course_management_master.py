import json
import re
import nbformat as nbf

############################## Get the question list (question,answer, points, type) from solution notebook ##############################
def construct_quest_dict(q_str,q_pts,solution,q_type):
    return {
            'question': q_str,
            'score': q_pts,
            'solution': solution,
            'resultType': q_type
        }
  
def extract_answer(ans):
    start = ans.find('=')+1
    end = ans.find('#@param')
    if end == -1: end= len(ans)
    ans = ans[start:end].strip()

    if ans[0:3] in ("'''",'"""'):
        start=3
        end=len(ans)-3
    else:
        start=1
        end=len(ans)-1
    return ans[start:end].strip()

def generate_question_list(PATH):
    nb_json = json.load(open(PATH,'r'))
    markdown_pattern = r'^#{1,} Question\s(\d{1,})\s\((.*):\s(\d{1,}).*'
    q_list = []
    i = 0
    while i < len(nb_json['cells']):
        cell = nb_json['cells'][i]
        if cell['cell_type'] == 'markdown':
            q_source = re.findall(markdown_pattern,cell['source'][0])
            if not len(q_source): 
                i+=1
                continue

            q_source = q_source[0]
            q_idx, q_pts = map(int,[q_source[0],q_source[2]])
            q_type = q_source[1]
            q_str = ''.join(cell['source'][1:])
            
            i+=1
            cell = nb_json['cells'][i]
            if cell['cell_type'] == 'code':
                solution = ''.join(cell['source'])
                if q_type != 'Function' : solution = extract_answer(solution)

                q_list.append(construct_quest_dict(q_str,q_pts,solution,q_type))
        i+=1
    return q_list


############################## Generate new solution-free client ##############################
def generate_answer_cells(new_cells,q_idx,q_type,func_head = None):
    q_idx = str(q_idx)

    if q_type == 'Value':
        results = []
        results.append('#@title ####Choose your answer from the dropdown list and run this cell {display-mode: "form"}\n')
        results.append('answer_' + q_idx + ' = \'A\' #@param ["A", "B", "C", "D"] {allow-input: true}\n\n')
        results.append(f'idx = {q_idx}\n')
        results.append("verify_answer(idx-1,f'answer_{idx}')")
        new_cells.append(nbf.v4.new_code_cell(''.join(results)))

    if q_type == 'Expression':
        results=[]
        results.append('#@title ####Put your answer here and run this cell {display-mode: "form"}\n')
        results.append('answer_' + q_idx + ' = "" #@param {type:"string"}\n\n')
        results.append(f'idx = {q_idx}\n')
        results.append("verify_answer(idx-1,f'answer_{idx}',df=df)")
        new_cells.append(nbf.v4.new_code_cell(''.join(results)))

    if q_type == 'SQL':
        results=[]
        results.append('answer_' + q_idx + ' = """\n')
        results.append('\n')
        results.append('"""\n')
        results.append(f'pd.read_sql_query(answer_{q_idx}, conn)')
        new_cells.append(nbf.v4.new_code_cell(''.join(results)))
        results=[]
        results.append('#@title ####Run this cell to check your answer {display-mode: "form"}\n')
        results.append(f'idx = {q_idx}\n')
        results.append("verify_answer(idx-1,f'answer_{idx}',connection=conn)")
        new_cells.append(nbf.v4.new_code_cell(''.join(results)))
    
    if q_type=='Function':
        results = []
        if not func_head: return
        results.append(func_head+'\n')
        results.append('\t# YOUR CODE HERE\n')
        new_cells.append(nbf.v4.new_code_cell(''.join(results)))
        results=[]
        results.append('#@title ####Run this cell to check your answer {display-mode: "form"}\n')
        results.append(f'idx = {q_idx}\n')
        results.append("verify_answer(idx-1,f'answer_{idx}',test_cases = test_cases_"+q_idx+")")
        new_cells.append(nbf.v4.new_code_cell(''.join(results)))
        # TODO: handle function's test_cases better. Save it to database

def generate_submit_code(new_cells,assignment_id):
    results = ['#@title Before you start, please login with the same email you have registered for the course {display-mode: "form"}\n',
    '\n',
    '# This code will be hidden when the notebook is loaded.\n',
    'import requests\n',
    'import ipywidgets as widgets\n',
    'from IPython.display import display\n',
    'import urllib.request as request\n',
    'import inspect\n',
    '\n',
    "checker_str = request.urlopen('https://raw.githubusercontent.com/coderschool/mle_gist/master/course_management.py')\n",
    'exec(checker_str.read())\n',
    '\n',
    "assignment_id = '"+assignment_id+"'\n",
    'assignment = Assignment.get_assignment_by_id(db, assignment_id)\n',
    "total_score = sum([q['score'] for q in assignment.questions])\n",
    '\n',
    'submission_data = {\n',
    '    "assignmentId": assignment_id,\n',
    '    "answers": [{\'question\': q[\'_id\'], \'answer\':\'\', \'clientCheck\':0} for q in assignment.questions],\n',
    '    "currentScore": 0\n',
    '}\n',
    '\n',
    'button = widgets.Button( icon=\'fa-paper-plane\', description="Submit", button_style=\'success\', tooltip=\'Submit\')\n',
    'email_field =widgets.Text(\n',
    "    value='',\n",
    "    placeholder='Email..',\n",
    "    description='Your email',\n",
    '    disabled=False\n',
    ')\n',
    'output = widgets.Output()\n',
    '\n',
    'def submit():\n',
    '    button.description = "Submitting..."\n',
    '    button.disabled = True\n',
    '\n',
    '    submission = Submission.create(db, submission_data)\n',
    "    if isinstance(submission,Submission) and getattr(submission, '_id', ''):\n",
    "        if (getattr(submission, 'name', '')):\n",
    "            print(f'Welcome {submission.name}!')\n",
    '        else:\n',
    "            print(f'Welcome {submission.email}')\n",
    '    else:\n',
    "        del submission_data['email']\n",
    '\n',
    '    button.description = "Submit"\n',
    '    button.disabled = False\n',
    '\n',
    'def on_button_clicked(b):\n',
    '    # Display the message within the output widget.\n',
    '    with output:\n',
    '        if (len(email_field.value) == 0):\n',
    '            print("Please enter your email")\n',
    '            return\n',
    "        submission_data['email'] = email_field.value.strip()\n",
    '        submit()\n',
    '\n',
    'button.on_click(on_button_clicked)\n',
    '\n',
    'display(email_field)\n',
    'display(button, output)']
    new_cells.append(nbf.v4.new_code_cell(''.join(results)))


def generate_assignment_notebook(client_path,solution_path,assignment_id):
    new_nb_json = nbf.v4.new_notebook()
    nb_json = json.load(open(solution_path,'r'))
    new_cells = []
    generate_submit_code(new_cells,assignment_id) # "before you start" cell

    markdown_pattern = r'^#{1,} Question\s(\d{1,})\s\((.*):\s(\d{1,}).*'
    i = 0
    while i < len(nb_json['cells']):
        cell = nb_json['cells'][i]
        if cell['cell_type'] == 'markdown':
            new_cells.append(nbf.v4.new_markdown_cell(cell['source'])) # add markdown cell
            
            q_source = re.findall(markdown_pattern,cell['source'][0])
            if not len(q_source): 
                i+=1
                continue

            q_source = q_source[0]
            q_idx, q_pts = map(int,[q_source[0],q_source[2]])
            q_type = q_source[1]
            q_str = ''.join(cell['source'][1:])
            new_cells.append(nbf.v4.new_code_cell("")) # empty code cell

            i+=1
            cell = nb_json['cells'][i]
            func_head = cell['source'][0] if q_type == 'Function' else None # get function header if possible
            generate_answer_cells(new_cells,q_idx,q_type,func_head)

        else:
            new_cells.append(nbf.v4.new_code_cell(cell['source'])) # add code cell
        i+=1

    new_nb_json['cells'] = new_cells
    if '.ipynb' in client_path:
        nbf.write(new_nb_json, client_path)
    else:
        nbf.write(new_nb_json, f'{client_path}.ipynb')
