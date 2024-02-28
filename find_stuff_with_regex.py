import re

raw_text = open('bible/NASB 1995 (01-04-24)/option1.xml-NASB95(bible)(01-04-24).txt').read()

reg = re.compile(r'(\w+)(<M[GH][^>]+>)(([<>\w\s]+?\w+(<M[GH][^>]+>)){2})[<>\w\s]+?(\w+)(\2)')

with open('bible/output/regex_same_tags.txt', 'w') as output_file:

    for match in reg.finditer(raw_text):
        # print(match.groups())
        # input()
        if match.group(1) != match.group(6) and match.group(2) != match.group(5):
            output_file.write(str(match.group()) + '\n')
            # print(match.group())
            # print(match.group(1), match.group(4))
            # input()