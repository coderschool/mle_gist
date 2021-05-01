import json
import re

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
