import json
import re
def extract_json(text):
    # Define the regex pattern to extract the JSON part
    text=text.replace('\n','')
    pattern = r'\{[^{}]*\}'
    match = re.findall(pattern, text)
    try : 
        output = eval(text)
        return output
    except:
        pass
    
    try :
        output = json.loads(re.sub(r"(?<=\{|\s)'|(?<=\s|:)'|(?<=\d)'(?!:)|'(?=\s|,|}|:)", '"',match[0]))
    except:
        import pdb;pdb.set_trace()
    
    return output