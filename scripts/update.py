import os
import sys
import json
import time

to_update = ['version', 'submission_type']
to_update_install = []

mappings = {
    'submission_type': 'type',
    'copy_file': 'files',
    'copy_folder': 'folders',
    'load_chrome': 'uclChromeTarget',
    'load_content': 'uclContentTarget',
    'thumbnail': 'image'
}

with open('/home/runner/issue-parser-result.json', 'r') as file:
    data = json.load(file)

if data['description']:
    to_update.append('description')

if data['copy_file']:
    if data['copy_file'] == '!erase':
        data['copy_file'] = []
    else:
        data['copy_file'] = data['copy_file'].split('\n')
    to_update_install.append('copy_file')

if data['copy_folder']:
    if data['copy_folder'] == '!erase':
        data['copy_folder'] = []
    else:
        data['copy_folder'] = data['copy_folder'].split('\n')
    to_update_install.append('copy_folder')

if data['load_chrome']:
    if data['load_chrome'] == '!erase':
        data['load_chrome'] = []
    else:
        data['load_chrome'] = data['load_chrome'].split('\n')
    to_update_install.append('load_chrome')

if data['load_content']:
    if data['load_content'] == '!erase':
        data['load_content'] = []
    else:
        data['load_content'] = data['load_content'].split('\n')
    to_update_install.append('load_content')

if data['domains']:
    if data['domains'] == '!erase':
        data['domains'] = []
    else:
        data['domains'] = data['domains'].split('\n')
    to_update.append('domains')

theme_type = 0
data['submission_type'] = 0

if data['load_chrome'] and not data['load_content']:
    theme_type = 1
    data['submission_type'] = 1

if data['load_content'] and not data['load_chrome']:
    theme_type = 2
    data['submission_type'] = 2

# Update themes.json entry
with open('themes.json', 'r') as file:
    themes = json.load(file)

if not data['id'] in themes:
    print('ERROR: Theme not found.')
    print('Please provide a valid theme ID.')
    sys.exit(1)

for key in to_update:
    mapped = mappings.get(key, key)
    themes[data['id']][mapped] = data[key]

themes[data['id']]['updatedAt'] = round(time.time())

with open('themes.json', 'w+') as file:
    # noinspection PyTypeChecker
    json.dump(themes, file, indent=4)

gh_username = themes[data["id"]]["homepage"].replace('https://github.com/', '', 1).split('/')[0]
if not gh_username.lower() == sys.argv[1].lower():
    print('ERROR: Repository owner mismatch.')
    print('You don\'t own this repository.')
    sys.exit(1)

os.system(f'git clone {themes[data["id"]]["homepage"]} theme-repo')
theme_dir = f'themes/{data["id"]}'

with open(f'{theme_dir}/theme.json', 'r') as file:
    install_data = json.load(file)

for key in to_update_install:
    mapped = mappings.get(key, key)
    install_data[mapped] = data[key]

with open(f'{theme_dir}/theme.json', 'w+') as file:
    # noinspection PyTypeChecker
    json.dump(install_data, file, indent=4)

for file in install_data['files']:
    os.system(f'cp theme-repo/{file} {theme_dir}')

for folder in install_data['folders']:
    os.system(f'cp -r theme-repo/{folder} {theme_dir}')

os.system(f'cp theme-repo/.custom-store/README.md {theme_dir}')
os.system(f'cp theme-repo/.custom-store/image.png {theme_dir}')

os.system(f'rm -rf theme-repo')

if not install_data['files'] and not install_data['folders']:
    print('ERROR: No files to copy.')
    print('Please provide a file or folder to copy.')
    sys.exit(1)

if not install_data['uclChromeTarget'] and not install_data['uclContentTarget']:
    print('ERROR: No load points.')
    print('Please provide a load point for either userChrome or userContent.')
    sys.exit(1)

if install_data['uclChromeTarget']:
    for load_point in install_data['uclChromeTarget']:
        if not os.path.isfile(theme_dir + '/' + load_point):
            print(f'ERROR: Invalid userChrome load point {load_point}.')
            print('Please provide a valid file path.')
            sys.exit(1)

if install_data['uclContentTarget']:
    for load_point in install_data['uclContentTarget']:
        if not os.path.isfile(theme_dir + '/' + load_point):
            print(f'ERROR: Invalid userContent load point {load_point}.')
            print('Please provide a valid file path.')
            sys.exit(1)

with open('/home/runner/theme_name', 'w+') as file:
    file.write(themes[data["id"]]["name"])

print('SUCCESS: Files have been written to folder.')
