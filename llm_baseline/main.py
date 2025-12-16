import collections
import sys
import pickle
import pypdf
import networkx as nx
import openai
from openai import OpenAI
from pypdf import PdfReader


def extract_destination_text(reader, name):
    text = ''
    if name in reader.named_destinations:
        v = reader.named_destinations[name]
        text = extract_text_in_rect(
            reader.pages[reader.get_destination_page_number(v)], (v['/Left'], v['/Top'], 10000, 10000))
        if len(text) == 0:
            text = reader.pages[reader.get_destination_page_number(v)].extract_text()
    return text


def extract_destination_pgnum(reader, name):
    if name in reader.named_destinations:
        v = reader.named_destinations[name]
        return reader.get_destination_page_number(v)
    return -1


def extract_pages_in_page(reader, page_number):
    pages = set()

    for page_num in range(page_number[0], page_number[1]+1):
        page = reader.pages[page_num]
        if '/Annots' in page:
            annotations = page['/Annots']
            for annot in annotations:
                obj = annot.get_object()
                if obj.get('/Subtype') == '/Link':
                    uri = None
                    destination = None

                    if '/A' in obj:
                        action = obj['/A']
                        if '/URI' in action:
                            uri = action['/URI']
                        elif action.get('/S') == '/GoTo' and '/D' in action:
                            destination = action['/D']
                    if destination:
                        now = extract_destination_pgnum(reader, destination)
                        pages.add(now)
    return pages


def extract_hyperlinks_and_text(pdf_path='cca.pdf', start_page=8, end_page=15):
    reader = pypdf.PdfReader(pdf_path)

    hyperlinks = []

    sections = set()
    last = 0

    for page_num in range(start_page, end_page):
        page = reader.pages[page_num]

        if '/Annots' in page:
            annotations = page['/Annots']
            print('processing page', page_num, ' # of annotations:', len(annotations))
            for annot in annotations:
                obj = annot.get_object()
                if obj.get('/Subtype') == '/Link':
                    uri = None
                    destination = None

                    if '/A' in obj:
                        action = obj['/A']
                        if '/URI' in action:
                            uri = action['/URI']
                        elif action.get('/S') == '/GoTo' and '/D' in action:
                            destination = action['/D']

                    # rect = obj['/Rect']
                    # print(rect, destination)

                    # # Extract text in the rectangle
                    # text = extract_text_in_rect(page, rect)
                    #
                    # link_info = {
                    #     'page_num': page_num + 1,
                    #     'rect': rect,
                    #     'text': text,
                    # }

                    # if uri:
                    #     link_info['type'] = 'web_link'
                    #     link_info['uri'] = uri
                    # elif destination:
                    #     link_info['type'] = 'internal_link'
                    #     link_info['destination'] = destination
                    if destination:
                        now = extract_destination_pgnum(reader, destination)
                        if now == -1:
                            now = last
                        if last != 0:
                            sections.add((last, now))
                        last = now
                    # print(link_info)
                    # hyperlinks.append(link_info)
    s = list(sections)
    s.sort(key=lambda x: x[0])
    print(s)
    print(len(s))

    return sections


def extract_text_in_rect(page, rect):
    parts = []
    def visitor_body(text, cm, tm, font_dict, font_size):
        (x, y) = (tm[4], tm[5])
        if rect[0] <= x <= rect[2] and rect[1] <= y <= rect[3]:
            parts.append(text)
    # Get text from the whole page
    page.extract_text(visitor_text=visitor_body)
    return ''.join(parts)


def build_graph(pdf_path, sections):
    kvs = {}
    for idx, item in enumerate(sections):
        kvs[item] = idx
    reader = pypdf.PdfReader(pdf_path)
    connections = collections.defaultdict(list)
    for st, ed in sections:
        for i in range(st, ed+1):
            connections[i].append((st, ed))
    G = nx.Graph()
    for item in sections:
        G.add_node(kvs[item])
    ct = 0
    for item in sections:
        pages = extract_pages_in_page(reader, item)
        for page in pages:
            for tar in connections[page]:
                G.add_edge(kvs[item], kvs[tar])
        ct += 1
        print(ct, len(pages), len(sections))
    nx.write_adjlist(G, 'cca.gh')
    with open('cca.kvs', 'wb') as fp:
        pickle.dump(kvs, fp)
    return G, kvs
    # for scc in nx.strongly_connected_components(G):
    #     print(scc)


def merge(intervals):
    """
    :type intervals: List[Interval]
    :rtype: List[Interval]
    """
    intervals.sort(key=lambda l1:(l1[0], l1[1]))
    cur=None
    answer=[]
    for l in intervals:
        if(cur==None):
            cur=l
        else:
            if(l[0]<=cur[1]):
                if(cur[1]<l[1]):
                    cur[1]=l[1]
            else:
                answer.append(cur)
                cur=l
    if(cur!=None):
        answer.append(cur)
    return answer


def prepare_graph(f:str, sections):
    g= nx.read_adjlist(f)
    task = []
    for n in g:
        wl = [list(sections[int(n)])]
        for nei in g[n]:
            wl.append(list(sections[int(nei)]))
        wl = merge(wl)
        ct = 0
        for itm in wl:
            ct += (itm[1] - itm[0]) + 1
        task.append(wl)
    return task


def build_client():
    from openai import OpenAI
    KEY = '<YOUR_API_KEY>'
    client = openai.OpenAI(api_key=KEY, base_url="https://api.deepseek.com") # remove deepseek url to use OpenAI
    return client


def extract_text(reader: PdfReader, wl: list):
    text = ''
    for item in wl:
        st = item[0]
        ed = item[1]
        for num in range(st, ed+1):
            page = reader.pages[num]
            page_text = page.extract_text()
            text += page_text
    return text


def build_request(client: OpenAI, text: str, model: str):
    print('='*20)
    messages = [
            {"role": "user", "content": "You are an expert in ARM CCA and PDF document. I need your help to find contradictions in the long document, usually across tables, sections." +
                                        "Your input will be a long text extracted from pdf document, and you are expected to find **all** the **contradictions** in the long document."
                                        + f"Your input is below:\n```text\n{text}\n```"}
        ]
    print(messages[0]['content'])
    print('-'*20)
    completion = client.chat.completions.create(
        model=model,
        messages= messages,
        max_tokens=8192
    )
    print(completion.choices[0].message.content)
    print('$'*20)
    return (text, completion.choices[0].message.content)



def run_llm(f:str, pdf: str, sections):
    import time
    task = prepare_graph(f, sections)
    reader = pypdf.PdfReader(pdf)
    client = build_client()
    reasoning = []
    print(len(task))
    models = []
    models = ['llama-3.1-70b-instruct-maas', 'o3-mini', 'gemini-2.0-flash-thinking-exp', 'gemini-2.0-flash', 'claude-3-7-sonnet-20250219', 'gpt-4o', 'deepseek-reasoner']

    for model in models:
        tt = 0
        for idx, wl in enumerate(task[20:]):
            text = extract_text(reader, wl)
            # tt+=len(enc.encode(text))
            # print('='*100)
            # print(text)
            ans = build_request(client, text, model)
            # # return
            reasoning.append(ans)
            print(idx, model)
            time.sleep(1)

        with open(f'reasoning_{model}.pkl', 'wb') as fp:
            pickle.dump(reasoning, fp)
        with open(f'output_{model}.txt', 'w') as fp:
            fp.writelines([x[1] for x in reasoning])

        print('done')

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage: python main.py <pdf> <table_of_content_start page> <table_of_content_end page>\nDefault: python3 main.py cca.pdf 8 15')
        file = 'cca.pdf'
        table_of_content_start = 8
        table_of_content_end = 15
    else:
        file = sys.argv[1]
        table_of_content_start = int(sys.argv[2])
        table_of_content_end = int(sys.argv[3])
    sections = extract_hyperlinks_and_text(file, table_of_content_start, table_of_content_end)
    build_graph(file, sections)
    run_llm('cca.gh', 'cca.pdf', sections)