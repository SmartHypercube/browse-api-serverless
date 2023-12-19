import json
import pypdfium2
import requests
import tempfile

max_result_length = 6291556
def result_length(r):
    return len(json.dumps(r, ensure_ascii=False).encode())

def pdf(url, log=None):
    if log is None:
        log = {}
    log['url'] = url

    with tempfile.TemporaryDirectory() as tmpdir:
        with requests.get(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            },
            stream=True,
            timeout=30,
        ) as response:
            response.raise_for_status()
            assert response.headers['content-type'].startswith('application/pdf')
            with open(f'{tmpdir}/input.pdf', 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        pdf = pypdfium2.PdfDocument(f'{tmpdir}/input.pdf')
        n_pages = len(pdf)
        pages = []
        for page_id in range(n_pages):
            page = pdf[page_id]
            textpage = page.get_textpage()
            text_all = textpage.get_text_range()
            pages.append(text_all)
        content = '\n'.join(pages).replace('\r', '').replace('￾', '')

    print(json.dumps(log, ensure_ascii=False, indent=2))

    result = {
        'data': {
            'url': url,
            'content': content,
        },
        'truncated': False,
        'template': [
            {'field': 'url', 'name': 'URL', 'type': 'inline'},
            {'field': 'content', 'name': 'Content', 'type': 'block'},
        ],
    }
    if result_length(result) > max_result_length:
        result['truncated'] = True
        result['data']['content'] = ''
        left = 0
        right = len(content)
        while left + 1 < right:
            mid = (left + right) // 2
            result['data']['content'] = content[:mid]
            if result_length(result) > max_result_length:
                right = mid
            else:
                left = mid
        result['data']['content'] = content[:left]
    return result

def handler(event, context):
    return pdf(json.loads(event['body'])['url'], {'event': event, 'context': repr(context)})
