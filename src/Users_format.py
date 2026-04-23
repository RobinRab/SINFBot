import os
import re
import json
from settings import DATA_DIR
from utils import INPUT_DATA

#-------- /!| this method assumes only one occurence of the keyword 'users' is used within the datasinf.json --------#

os.rename(f"{DATA_DIR}/datasinf.json", f"{DATA_DIR}/datasinf_save.json")

with open(f"{DATA_DIR}/datasinf_save.json") as f:
    data = json.load(f)
    f.seek(0)
    l = f.readlines()

start_format_index = l.index('        "users": {\n')

user_id_discord = re.compile('"\\d{18}": {')

with open(f"{DATA_DIR}/datasinf.json", "w+") as f:
    for i in range(start_format_index + 1):
        f.write(l[i])
    
    #We start searching for users after to lines containing each one '{'
    right_crly_brket_count = 2
    previous_match = start_format_index + 1

    for i in range(start_format_index + 2, len(l)):
        if r'{' in l[i]:
            right_crly_brket_count += 1
        if r'}' in l[i]:
            right_crly_brket_count -= 1
        if right_crly_brket_count == 0:
            right_crly_brket_count = i
            f.write(l[previous_match][:-2])
            json.dump(INPUT_DATA, f, indent=4)
            f.write("\n")
            break
        if user_id_discord.search(l[i]):
            f.write(l[previous_match][:-2])
            previous_match = i
            json.dump(INPUT_DATA, f, indent=4)
            f.write(",\n")

    for i in range(right_crly_brket_count, len(l)):
        f.write(l[i])

    f.seek(0)
    new_data = json.load(f)    

#Update new created json with still relevant old data
for user in new_data["games"]["users"].items():
    for key in user[1]:
        try:
            user[1][key]=data["games"]["users"][user[0]][key]
        except:
            continue
        
with open(f"{DATA_DIR}/datasinf.json", "w") as f:
    json.dump(new_data, f, indent=4)