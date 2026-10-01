#!/usr/bin/env python3
"""Value of Data: source-preserving preparation, validation and reporting. Python 3.10+.

Released under the MIT License. See the LICENSE file in the project root.
"""
import argparse
import csv
import hashlib
import html
import json
import platform
import re
import shutil
import sys
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

HOME = Path(__file__).resolve().parent
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
STANCES = ['SUP', 'OPP', 'QUAL', 'NR', 'ILL', 'PRO', 'UNC', 'CTX']
PROVENANCES = ['reported', 'mixed', 'researcher', 'background', 'supplementary', 'ambiguous']
FIELDS = ['S-number', 'filename', 'Q-number', 'meaning of statement', 'code', 'weak/strong', 'full text of statement']
VERSION = '2.0.0'


def fail(message):
    raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def runtime():
    return {'tool_version': VERSION, 'python': sys.version, 'executable': sys.executable,
            'platform': platform.platform(), 'script_sha256': digest(__file__), 'time_utc': now(),
            'third_party_python_dependencies': [], 'javascript_used': False,
            'llm_called_by_script': False}


def norm(s):
    return ' '.join(s.lower().split()).strip(' .?:')


def paragraph_text(element):
    if element.tag == W + 'del':
        return ''
    if element.tag == W + 't':
        return element.text or ''
    if element.tag == W + 'tab':
        return '\t'
    if element.tag in (W + 'br', W + 'cr'):
        return '\n'
    return ''.join(paragraph_text(child) for child in element)


def extract(path):
    with zipfile.ZipFile(path) as z:
        tree = ET.fromstring(z.read('word/document.xml'))
        body = tree.find(W + 'body')
        if body is None:
            fail(f'No document body in {path}')
        paragraphs = []
        for n, p in enumerate(body.iter(W + 'p'), 1):
            text = paragraph_text(p)
            if text.strip():
                style = p.find('./' + W + 'pPr/' + W + 'pStyle')
                paragraphs.append({'id': f'P{n:04d}', 'text': text,
                                   'style': style.get(W + 'val') if style is not None else None})
        auxiliary = {}
        for name in z.namelist():
            if re.match(r'word/(comments|footnotes|endnotes|header\d*|footer\d*)\.xml$', name):
                aux = ET.fromstring(z.read(name))
                auxiliary[name] = [paragraph_text(p) for p in aux.iter(W + 'p') if paragraph_text(p).strip()]
        warnings = []
        for tag, label in [('ins','tracked insertions (included)'), ('del','tracked deletions (excluded)'),
                           ('drawing','drawings/images (not interpreted)'), ('txbxContent','text boxes (reading order needs review)')]:
            count = sum(1 for _ in tree.iter(W + tag))
            if count:
                warnings.append(f'{count} {label}')
        if auxiliary:
            warnings.append('Auxiliary text exists: inspect it; it is outside the automatic statement inventory')
        return {'paragraphs': paragraphs, 'auxiliary_text': auxiliary, 'warnings': warnings}


def prepare(source, run):
    source, run = Path(source).resolve(), Path(run).resolve()
    if not source.is_dir():
        fail('Input must be a folder of DOCX/DOTX files')
    if run.exists():
        fail('Run folder already exists. Choose a new folder; preparation never overwrites a run.')
    if source == run or source in run.parents:
        fail('Place the run outside the input folder')
    files = sorted((p for p in source.rglob('*') if p.suffix.lower() in ('.docx', '.dotx') and not p.name.startswith('~$')), key=lambda p: p.relative_to(source).as_posix())
    if not files:
        fail('No DOCX/DOTX files found; legacy .doc needs conversion in a separate folder')
    # Read all sources before creating the run; do not leave partial output on malformed XML.
    documents = [(p, digest(p), extract(p)) for p in files]
    run.mkdir(parents=True)
    for d in ['extracted', 'coding', 'config']:
        (run / d).mkdir()
    for p in (HOME / 'framework').iterdir():
        if p.is_file():
            shutil.copy2(p, run / 'config' / p.name)
    questions = read(run / 'config/questions.json')
    manifest = {'version': VERSION, 'source_root': str(source), 'created': runtime(), 'documents': []}
    for n, (path, sha, extracted) in enumerate(documents, 1):
        doc_id = f'D{n:04d}'
        filename = path.relative_to(source).as_posix()
        extracted.update({'doc_id': doc_id, 'filename': filename, 'source_sha256': sha})
        write(run / 'extracted' / (doc_id + '.json'), extracted)
        current_q = 'Q0'
        dispositions = []
        for p in extracted['paragraphs']:
            match = next((q for q, heading in questions.items() if q not in ['Q0','QX','Q10a','Q7–Q8'] and norm(p['text']).lstrip('0123456789. )') == norm(heading)), None)
            if match:
                current_q = match
            dispositions.append({'paragraph': p['id'], 'question': current_q, 'kind': 'pending',
                                 'reason': '', 'heading_suggestion': bool(match)})
        coding = {'doc_id': doc_id, 'status': 'pending', 'case_id': doc_id, 'case_decision': 'pending',
                  'case_reason': '', 'sensitivity_exclude': False, 'source_review': '',
                  'dispositions': dispositions, 'units': [], 'review_log': []}
        write(run / 'coding' / (doc_id + '.json'), coding)
        manifest['documents'].append({'doc_id': doc_id, 'filename': filename, 'sha256': sha,
                                     'extraction_sha256': digest(run / 'extracted' / (doc_id + '.json'))})
    write(run / 'manifest.json', manifest)
    write(run / 'inference-log.json', {'sessions': []})
    write(run / 'synthesis.json', {'status': 'pending', 'author_session': None,
                                  'findings': [], 'recommendations': [], 'limitations': []})
    (run / 'README.md').write_text('# Analysis run\n\nSources are read-only. Read the toolkit README and prompts/analyse.md.\n'
        'Complete coding/*.json, inference-log.json and synthesis.json; never edit extracted/ or manifest.json.\n'
        'Every non-empty paragraph needs a disposition. Review question suggestions, attribution and auxiliary text.\n'
        'Validate and build from the toolkit command line. Builds create new numbered snapshots.\n', encoding='utf-8')
    print(f'Prepared {len(documents)} documents in {run}; qualitative coding is pending.')


def validate(run):
    run = Path(run).resolve()
    manifest = read(run / 'manifest.json')
    source_root = Path(manifest['source_root'])
    actual_files = {p.relative_to(source_root).as_posix() for p in source_root.rglob('*')
                    if p.suffix.lower() in ('.docx', '.dotx') and not p.name.startswith('~$')}
    expected_files = {d['filename'] for d in manifest['documents']}
    if actual_files != expected_files:
        fail('Source collection changed: files added or removed; prepare a new run')
    codebook = read(run / 'config/codebook.json')
    questions = read(run / 'config/questions.json')
    sessions = read(run / 'inference-log.json')['sessions']
    session_ids = set()
    for s in sessions:
        if not s.get('id') or s['id'] in session_ids or s.get('kind') not in ['llm', 'human']:
            fail('Inference log: unique id and kind llm/human required')
        for key in ['model','provider','temperature','top_p','seed','date_utc','notes']:
            if key not in s:
                fail(f'Inference log {s["id"]}: include {key}; use null if unknown')
        if not s['date_utc'] or not s['notes']:
            fail('Inference log needs a date and notes about what was done')
        session_ids.add(s['id'])
    rows, cases, decisions, source_checks = [], {}, {}, []
    references = set()
    for doc in manifest['documents']:
        did = doc['doc_id']
        source = Path(manifest['source_root']) / doc['filename']
        if not source.is_file() or digest(source) != doc['sha256']:
            fail(f'{did}: source missing or changed; restore source or prepare a new run')
        ep = run / 'extracted' / (did + '.json')
        if digest(ep) != doc['extraction_sha256']:
            fail(f'{did}: extracted text changed; do not edit extracted files')
        ext, c = read(ep), read(run / 'coding' / (did + '.json'))
        if c['doc_id'] != did or c['status'] != 'complete':
            fail(f'{did}: coding status must be complete')
        case = c['case_id']
        if not isinstance(case, str) or not case.strip():
            fail(f'{did}: non-empty case_id required')
        decision = c['case_decision']
        if decision not in ['include','exclude','empty'] or not c.get('case_reason'):
            fail(f'{did}: explicit case decision and reason required')
        if not isinstance(c.get('sensitivity_exclude'), bool):
            fail(f'{did}: sensitivity_exclude must be boolean')
        if not c.get('source_review'):
            fail(f'{did}: source_review must document headings, attribution and extraction review')
        if case in decisions and decisions[case] != decision:
            fail(f'{case}: conflicting document inclusion decisions; give excluded duplicates separate case IDs')
        decisions[case] = decision
        if decision == 'include':
            cases[case] = cases.get(case, False) or c['sensitivity_exclude']
        paras = {p['id']: p['text'] for p in ext['paragraphs']}
        ds = c['dispositions']
        if len(ds) != len(paras) or {d['paragraph'] for d in ds} != set(paras):
            fail(f'{did}: every paragraph must have exactly one disposition')
        disposition = {d['paragraph']: d for d in ds}
        for d in ds:
            if d['question'] not in questions or d['kind'] not in ['coded','heading','front_matter','scaffold','cross_reference','excluded']:
                fail(f'{did}/{d["paragraph"]}: invalid question or pending/invalid disposition')
            if d['kind'] != 'coded' and not d.get('reason'):
                fail(f'{did}/{d["paragraph"]}: uncoded text needs a reason')
        coverage = defaultdict(list)
        if decision == 'empty' and c['units']:
            fail(f'{did}: empty record cannot contain units')
        if decision == 'include' and not c['units']:
            fail(f'{did}: included case needs at least one recorded unit')
        for u in c['units']:
            uid = u.get('unit_id', '')
            ref = did + '/' + uid
            if not re.fullmatch(r'U[0-9]+', uid) or ref in references:
                fail(f'{did}: unique unit_id U<number> required')
            references.add(ref)
            if u.get('author_session') not in session_ids:
                fail(f'{ref}: author_session missing from inference-log')
            if not u.get('meaning') or not u.get('rationale'):
                fail(f'{ref}: meaning and rationale required')
            if u.get('confidence') not in ['high','medium','low'] or u.get('provenance') not in PROVENANCES:
                fail(f'{ref}: invalid confidence or provenance')
            if u.get('suggestion') not in codebook['suggestions']:
                fail(f'{ref}: invalid suggestion')
            if u.get('framework_fit') not in ['in_framework','partial_extension','outside_framework','context_only']:
                fail(f'{ref}: invalid framework_fit')
            if u.get('review_status') not in ['unreviewed','reviewed','adjudicated']:
                fail(f'{ref}: review_status required')
            if u['review_status'] != 'unreviewed' and not u.get('reviewer'):
                fail(f'{ref}: reviewer required for reviewed/adjudicated coding')
            parts, locators, qs, ordering = [], [], set(), []
            for span in u.get('spans', []):
                p = span['paragraph']
                if p not in paras or disposition[p]['kind'] != 'coded':
                    fail(f'{ref}: span must reference a coded paragraph')
                a, b = span['start'], span['end']
                if type(a) is not int or type(b) is not int or not 0 <= a < b <= len(paras[p]):
                    fail(f'{ref}: invalid Unicode character offsets')
                parts.append(paras[p][a:b]); locators.append(f'{p}[{a}:{b}]')
                qs.add(disposition[p]['question']); ordering.append((list(paras).index(p), a))
                coverage[p].append((a,b))
            if not parts or ordering != sorted(ordering) or len(qs) != 1:
                fail(f'{ref}: ordered spans within one question required')
            # Do not silently join distant source passages into one apparent continuous quotation.
            for i, (left, right) in enumerate(zip(ordering, ordering[1:])):
                if right[0] != left[0] + 1:
                    fail(f'{ref}: use one span per paragraph and only adjacent paragraphs')
                prev, following = u['spans'][i], u['spans'][i+1]
                if prev['end'] != len(paras[prev['paragraph']]) or following['start'] != 0:
                    fail(f'{ref}: multi-paragraph excerpts must be continuous across paragraph boundaries')
            question = next(iter(qs))
            if question == 'Q0' and u['provenance'] in ['reported','mixed']:
                fail(f'{ref}: map substantive answers to a question before inclusion')
            codes = u.get('assignments', [])
            if not codes or len({(a['target'], a['stance']) for a in codes}) != len(codes):
                fail(f'{ref}: non-empty unique target/stance assignments required')
            for a in codes:
                if a['target'] not in codebook['targets'] or a['stance'] not in STANCES:
                    fail(f'{ref}: unknown target or stance')
                allowed = ['n/a'] if a['stance'] in ['ILL','UNC','CTX'] else ['weak','strong']
                if a['strength'] not in allowed:
                    fail(f'{ref}: invalid strength for {a["stance"]}')
            full = '\n'.join(parts)
            if 'full_text_check' in u and u['full_text_check'] != full:
                fail(f'{ref}: supplied excerpt does not match source spans')
            rows.append({'S-number': '', 'filename': doc['filename'], 'Q-number': question,
                         'meaning of statement': u['meaning'], 'code': '; '.join(a['target']+':'+a['stance'] for a in codes),
                         'weak/strong': '; '.join(a['target']+':'+a['stance']+'='+a['strength'] for a in codes),
                         'full text of statement': full, 'doc_id': did, 'case_id': case,
                         'unit_ref': ref, 'source_locator': '; '.join(locators), 'assignments': codes,
                         'primary_included': decision == 'include' and question not in ['Q0','QX'] and u['provenance'] in ['reported','mixed'],
                         'case_included': decision == 'include',
                         **{k:u[k] for k in ['provenance','confidence','rationale','framework_fit','suggestion','author_session','review_status']},
                         'reviewer': u.get('reviewer'), '_order': (did, ordering[0])})
        for p, d in disposition.items():
            intervals = sorted(coverage[p])
            if d['kind'] == 'coded':
                cursor = 0
                for a,b in intervals:
                    if a != cursor:
                        fail(f'{did}/{p}: overlap or uncovered characters at {cursor}')
                    cursor = b
                if cursor != len(paras[p]):
                    fail(f'{did}/{p}: incomplete character coverage')
            elif intervals:
                fail(f'{did}/{p}: excluded paragraph has coded spans')
        source_checks.append({'doc_id': did, 'case_id': case, 'decision': decision,
                              'reason': c['case_reason'], 'source_review': c['source_review'],
                              'warnings': ext['warnings'], 'paragraphs': len(paras)})
    rows.sort(key=lambda r:r['_order'])
    for i,r in enumerate(rows,1):
        r.pop('_order'); r['S-number'] = f'S{i:05d}'
    synthesis = read(run / 'synthesis.json')
    if synthesis.get('status') not in ['pending','complete']:
        fail('Synthesis status must be pending or complete')
    if synthesis['status'] == 'complete':
        if synthesis.get('author_session') not in session_ids:
            fail('Completed synthesis needs an author_session in inference-log')
        if not synthesis.get('limitations'):
            fail('Completed synthesis needs explicit limitations')
        for item in synthesis['findings'] + synthesis['recommendations']:
            if not item.get('text') or not item.get('evidence') or not set(item['evidence']) <= references:
                fail('Each synthesis finding/recommendation needs text and valid doc_id/unit_id evidence references')
    return manifest, codebook, rows, cases, source_checks, synthesis


def tabulate(rows, cases, targets, mode='primary'):
    eligible_cases = {c for c in cases if mode != 'exclude_flagged_cases' or not cases[c]}
    selected = []
    for r in rows:
        include = r['primary_included']
        if mode == 'reported_only':
            include = include and r['provenance'] == 'reported'
        elif mode == 'include_ambiguous':
            include = include or (r['case_included'] and r['provenance'] == 'ambiguous' and r['Q-number'] not in ['Q0','QX'])
        if include and r['case_id'] in eligible_cases:
            selected.append(r)
    index = defaultdict(list)
    for r in selected:
        for a in r['assignments']:
            index[(r['case_id'], a['target'])].append(a)
    matrix, summary = [], []
    for target, label in targets.items():
        counts = {s:0 for s in STANCES}; covered = evaluated = strong = 0
        for case in sorted(eligible_cases):
            aa = index[(case,target)]; flags = {a['stance'] for a in aa}
            counts = {s:counts[s]+int(s in flags) for s in STANCES}
            ev = bool(flags & {'SUP','OPP','QUAL','NR'}); evaluated += ev; covered += bool(aa)
            strong += any(a['stance']=='SUP' and a['strength']=='strong' for a in aa)
            challenged = bool(flags & {'OPP','QUAL'})
            status = 'mixed' if 'SUP' in flags and challenged else 'support_only' if 'SUP' in flags else 'challenged_only' if challenged else 'local_nonrelevance' if 'NR' in flags else 'no_explicit_evaluation'
            matrix.append({'case_id':case, 'target':target, **{s:int(s in flags) for s in STANCES},
                           'evaluated':int(ev), 'covered':int(bool(aa)), 'status':status})
        summary.append({'target':target,'label':label,'cases':len(eligible_cases),'covered_cases':covered,
                        'evaluating_cases':evaluated,**counts,'strong_SUP':strong,
                        'support_all_cases': counts['SUP']/len(eligible_cases) if eligible_cases else None,
                        'support_evaluating_cases': counts['SUP']/evaluated if evaluated else None})
    return matrix, summary


def tsv(path, rows, fields=None):
    fields = fields or (list(rows[0]) if rows else [])
    with Path(path).open('w',encoding='utf-8',newline='') as f:
        w = csv.DictWriter(f,fieldnames=fields,delimiter='\t',extrasaction='ignore'); w.writeheader()
        for row in rows:
            w.writerow({k: json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in row.items()})


def escaped(text):
    return str(text).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('|','\\|').replace('\n','<br>')


def table(rows, fields):
    return '| '+' | '.join(fields)+' |\n| '+' | '.join(['---']*len(fields))+' |\n' + '\n'.join('| '+' | '.join(escaped(r.get(k,'')) for k in fields)+' |' for r in rows)+'\n'


def inputs_hashes(run):
    paths = [run/'manifest.json',run/'inference-log.json',run/'synthesis.json']
    for folder in ['coding','config','extracted']:
        paths.extend(p for p in (run/folder).rglob('*') if p.is_file())
    return {p.relative_to(run).as_posix():digest(p) for p in sorted(paths)}


def build(run, draft=False):
    run = Path(run).resolve()
    before = inputs_hashes(run)
    manifest, cb, rows, cases, checks, synthesis = validate(run)
    if synthesis['status'] != 'complete' and not draft:
        fail('Synthesis is pending. Complete the qualitative synthesis or explicitly use --draft.')
    output_root = run/'outputs'; output_root.mkdir(exist_ok=True)
    n = 1
    while (output_root/f'build-{n:04d}').exists():
        n += 1
    output = output_root/f'build-{n:04d}'; output.mkdir()
    matrix, summary = tabulate(rows,cases,cb['targets'])
    sensitivities = {m:tabulate(rows,cases,cb['targets'],m)[1] for m in ['reported_only','exclude_flagged_cases','include_ambiguous']}
    write(output/'statements.json',rows); tsv(output/'statements.tsv', rows, FIELDS+['doc_id','case_id','unit_ref','source_locator','primary_included','provenance','framework_fit','suggestion','confidence','rationale','review_status','reviewer','author_session'])
    write(output/'case-matrix.json',matrix); tsv(output/'case-matrix.tsv',matrix)
    write(output/'support-summary.json',summary); tsv(output/'support-summary.tsv',summary)
    write(output/'sensitivity.json',sensitivities); write(output/'source-review.json',checks)
    write(output/'revision-register.json',[r for r in rows if r['suggestion']!='none'])
    review = [r for r in rows if r['review_status']=='unreviewed' or r['confidence']!='high' or r['suggestion']!='none' or any(a['stance'] in ['OPP','QUAL','UNC'] for a in r['assignments'])]
    tsv(output/'review-queue.tsv',review,FIELDS+['unit_ref','provenance','confidence','rationale','review_status'])
    write(output/'codebook.json',cb)
    docs = output/'statements'; docs.mkdir()
    for doc in manifest['documents']:
        rr = [r for r in rows if r['doc_id']==doc['doc_id']]
        chunks = ['# Statement register: '+doc['doc_id'], '\nExtracts reproduce written notes, not verified verbatim participant speech.\n']
        for r in rr:
            chunks.extend([f'## {r["S-number"]} · {r["unit_ref"]}',
                           table([r],FIELDS[:-1]),
                           '**Full text of statement**\n', '<pre>'+html.escape(r['full text of statement'])+'</pre>\n',
                           f'Location: {r["source_locator"]}. Provenance: {r["provenance"]}. Confidence: {r["confidence"]}. Review: {r["review_status"]}.\n',
                           'Rationale: '+escaped(r['rationale'])+'\n'])
        (docs/(doc['doc_id']+'.md')).write_text('\n\n'.join(chunks),encoding='utf-8')
    mapping = {r['unit_ref']:r for r in rows}
    narrative = ['# Findings\n',f'{len(cases)} included cases; {len(manifest["documents"])} source documents; {len(rows)} recorded meaning units.\n',
                 'Counts describe this collection of interview notes. They do not estimate population approval or establish theoretical validity.\n']
    if synthesis['status'] != 'complete':
        narrative.append('**DRAFT: qualitative synthesis is pending.**\n')
    for key in ['findings','recommendations']:
        narrative.append('## '+key.title()+'\n')
        for item in synthesis[key] if synthesis['status']=='complete' else []:
            links=[]
            for ref in item['evidence']:
                r=mapping[ref]; links.append(f'[{ref}](statements/{r["doc_id"]}.md)')
            narrative.append(escaped(item['text'])+' Evidence: '+', '.join(links)+'.\n')
    narrative.append('## Limitations\n')
    narrative.extend('- '+escaped(x) for x in synthesis['limitations'])
    narrative.extend(['\n## Support by target\n','Stances overlap within a case; columns must not be added as independent votes. Strong support is a subset of SUP. Evaluating cases = cases with SUP, OPP, QUAL or NR. Empty denominators remain null in JSON.\n',table(summary,['target','label','cases','evaluating_cases','SUP','strong_SUP','OPP','QUAL','NR','covered_cases'])])
    (output/'findings.md').write_text('\n'.join(narrative),encoding='utf-8')
    (output/'revision-register.md').write_text('# Revision register\n\nProposals are candidates, not accepted additions. Review attribution before using them to revise the framework.\n\n'+table([r for r in rows if r['suggestion']!='none'],['S-number','unit_ref','suggestion','meaning of statement','code','provenance','primary_included']),encoding='utf-8')
    (output/'README.md').write_text('# Value of Data analysis\n\nStart with [findings](findings.md). Inspect the [revision register](revision-register.md), [statement register](statements.tsv), [case matrix](case-matrix.tsv) and [support summary](support-summary.tsv).\n\n'
        'review-queue.tsv prioritises uncoded-review status, uncertainty, challenge and suggestions; it is a view, not the authoritative coding file. Edit run/coding/*.json and log review decisions, then build a new snapshot.\n\n'
        'sensitivity.json contains reported-only, flagged-case-excluded and ambiguous-included alternatives. source-review.json records inclusion and extraction review. provenance.json records inputs and runtime. verify.json reports technical checks, not semantic validation.\n\n'
        'These outputs can contain identifiable and sensitive notes. Review disclosure and quotations before sharing beyond the research group.\n',encoding='utf-8')
    if inputs_hashes(run) != before:
        fail('Run inputs changed during build; discard this output snapshot and rerun')
    provenance = {'runtime':runtime(),'input_hashes':before,'source_hashes':{d['filename']:d['sha256'] for d in manifest['documents']},
                  'inference_log':read(run/'inference-log.json'),'synthesis_status':synthesis['status'],
                  'human_reviewed_units':sum(r['review_status']!='unreviewed' for r in rows),
                  'output_hashes':{p.relative_to(output).as_posix():digest(p) for p in output.rglob('*') if p.is_file()}}
    write(output/'provenance.json',provenance)
    verify(run,output)
    print(f'Created {output}')


def verify(run,output):
    run, output = Path(run).resolve(), Path(output).resolve()
    _,cb,rows,cases,_,_ = validate(run)
    prov = read(output/'provenance.json')
    if prov['input_hashes'] != inputs_hashes(run):
        fail('Run inputs differ from this snapshot; build a new version after edits')
    for name,sha in prov['output_hashes'].items():
        if digest(output/name) != sha:
            fail(f'Output changed: {name}')
    if read(output/'statements.json') != rows:
        fail('Statement JSON does not match current coding and exact source spans')
    with (output/'statements.tsv').open(encoding='utf-8',newline='') as f:
        trows = list(csv.DictReader(f,delimiter='\t'))
    if len(trows) != len(rows) or any(any(t[k]!=r[k] for k in FIELDS) for t,r in zip(trows,rows)):
        fail('TSV does not preserve the seven required fields')
    # Independent set-based support computation, separate from tabulate().
    for s in read(output/'support-summary.json'):
        sets = {stance:{r['case_id'] for r in rows if r['primary_included'] and any(a['target']==s['target'] and a['stance']==stance for a in r['assignments'])} for stance in STANCES}
        if any(s[st] != len(v) for st,v in sets.items()) or s['cases'] != len(cases) or s['evaluating_cases'] != len(set().union(*(sets[st] for st in ['SUP','OPP','QUAL','NR']))):
            fail('Independent support recount failed')
    result = {'status':'passed','time_utc':now(),'documents':len(read(run/'manifest.json')['documents']),
              'cases':len(cases),'statements':len(rows),'checks':['source hashes','extraction hashes','complete paragraph/span coverage','valid coding schema and evidence references','input and output hashes','exact JSON/TSV excerpts','independent primary support recount'],
              'semantic_validation':False,'note':'No automatic check establishes that a qualitative interpretation is correct.'}
    # Verification itself does not alter an existing snapshot.
    if not (output/'verify.json').exists():
        write(output/'verify.json',result)
    print(json.dumps(result,ensure_ascii=False))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('prepare',help='Read Word notes and create an empty coding run');p.add_argument('--input',required=True);p.add_argument('--run',required=True)
    p=sub.add_parser('validate',help='Check coding completeness, source spans and references');p.add_argument('--run',required=True)
    p=sub.add_parser('build',help='Create a new numbered report snapshot');p.add_argument('--run',required=True);p.add_argument('--draft',action='store_true',help='Allow pending qualitative synthesis; coding still must be complete')
    p=sub.add_parser('verify',help='Recheck sources and a generated snapshot');p.add_argument('--run',required=True);p.add_argument('--output',required=True)
    args=parser.parse_args()
    try:
        if args.command=='prepare':prepare(args.input,args.run)
        elif args.command=='validate':
            _,_,r,c,_,s=validate(args.run);print(f'Valid coding: {len(r)} units, {len(c)} included cases; synthesis {s["status"]}')
        elif args.command=='build':build(args.run,args.draft)
        else:verify(args.run,args.output)
    except (ValueError,KeyError,TypeError,OSError,zipfile.BadZipFile,ET.ParseError) as e:
        print(f'ERROR: {e}',file=sys.stderr);return 1
    return 0


if __name__=='__main__':
    sys.exit(main())
