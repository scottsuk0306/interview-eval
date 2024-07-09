import json
import re
def extract_json(text):
    # Define the regex pattern to extract the JSON part
    pattern = r'\{[^{}]*\}'
    match = re.findall(pattern, text)
    try :
        output = json.loads(re.sub(r"(?<=\{|\s)'|(?<=\s|:)'|(?<=\d)'(?!:)|'(?=\s|,|}|:)", '"',match[0]))
    except:
        import pdb;pdb.set_trace()
    
    return output