import base64
import json
import re
import requests

max_result_length = 6291556
def result_length(r):
    return len(json.dumps(r, ensure_ascii=False).encode())

def github(url, log=None):
    if log is None:
        log = {}
    log['url'] = url

    owner, name = re.fullmatch(r'https://github\.com/([^/]+)/([^/]+)', url).group(1, 2)

    response = requests.get(
        f'https://api.github.com/repos/{owner}/{name}',
        headers={
            'Accept': 'application/vnd.github.v3+json',
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    response = requests.get(
        f'https://api.github.com/repos/{owner}/{name}/contents',
        headers={
            'Accept': 'application/vnd.github.v3+json',
        },
        timeout=30,
    )
    response.raise_for_status()
    contents = []
    for i in response.json():
        if i['type'] == 'dir':
            contents.append(i['path'] + '/')
        else:
            contents.append(i['path'])
    contents = '\n'.join(contents)

    try:
        response = requests.get(
            f'https://api.github.com/repos/{owner}/{name}/readme',
            headers={
                'Accept': 'application/vnd.github.v3+json',
            },
            timeout=30,
        )
        response.raise_for_status()
        readme = response.json()
        assert readme['encoding'] == 'base64'
        readme_filename = readme['name']
        readme = base64.b64decode(readme['content']).decode('utf-8')
    except Exception:
        readme_filename = None
        readme = None

    result = {
        'data': {
            'url': url,
            'owner': owner,
            'name': name,
            'stars': str(data['stargazers_count']),
            'contents': contents,
        },
        'truncated': False,
        'template': [
            {'field': 'url', 'name': 'URL', 'type': 'inline'},
            {'field': 'owner', 'name': 'Owner', 'type': 'inline'},
            {'field': 'name', 'name': 'Name', 'type': 'inline'},
            {'field': 'description', 'name': 'Description', 'type': 'inline'},
            {'field': 'stars', 'name': 'Stars', 'type': 'inline'},
            {'field': 'contents', 'name': 'Contents', 'type': 'block'},
        ],
    }
    if data['description']:
        result['data']['description'] = data['description']
    if readme is not None:
        result['data']['readme'] = readme
        result['template'].append({'field': 'readme', 'name': readme_filename, 'type': 'block'})
        if result_length(result) > max_result_length:
            result['truncated'] = True
            result['data']['readme'] = ''
            left = 0
            right = len(readme)
            while left + 1 < right:
                mid = (left + right) // 2
                result['data']['readme'] = readme[:mid]
                if result_length(result) > max_result_length:
                    right = mid
                else:
                    left = mid
            result['data']['readme'] = readme[:left]
    return result

def handler(event, context):
    return github(json.loads(event['body'])['url'], {'event': event, 'context': repr(context)})
