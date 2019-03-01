
import json

f = json.loads(open("../input/data_legitimate_36400.json", "r").read())
fn = open("dl_36400.txt", "w")
for line in f:
    fn.write(line+"\n")