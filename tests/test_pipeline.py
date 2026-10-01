"""Synthetic fixtures only: temporary files are removed after every test."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from xml.sax.saxutils import escape

spec = importlib.util.spec_from_file_location('vod', Path(__file__).resolve().parents[1] / 'value_of_data.py')
v = importlib.util.module_from_spec(spec); spec.loader.exec_module(v)


def docx(path, paragraphs, extras=None):
    path.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(path,'w') as z:
        z.writestr('word/document.xml','<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'+''.join('<w:p><w:r><w:t xml:space="preserve">'+escape(x)+'</w:t></w:r></w:p>' for x in paragraphs)+'</w:body></w:document>')
        for name,text in (extras or {}).items():z.writestr(name,text)


class Pipeline(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.source=self.root/'notes';self.source.mkdir();self.run=self.root/'run'
        self.text='Synthetic note: scientific value matters because it enables research.\nA second line with æ, ø and å.'
        questions=v.read(v.HOME/'framework/questions.json')
        docx(self.source/'a.docx',[questions['Q8'],self.text])
        docx(self.source/'nested'/'b.docx',[questions['Q8'],'Synthetic note: the category needs a narrower definition.'])
        docx(self.source/'empty.dotx',[questions['Q8']])
        self.hashes={str(p):v.digest(p) for p in self.source.rglob('*') if p.is_file()}
        v.prepare(self.source,self.run)
        v.write(self.run/'inference-log.json',{'sessions':[{'id':'test','kind':'human','provider':None,'model':None,'temperature':None,'top_p':None,'seed':None,'date_utc':'2000-01-01T00:00:00Z','notes':'Synthetic fixture, not a real coding session'}]})
        for d in v.read(self.run/'manifest.json')['documents']:
            p=self.run/'coding'/(d['doc_id']+'.json');c=v.read(p);e=v.read(self.run/'extracted'/(d['doc_id']+'.json'))
            c.update(status='complete',case_reason='Synthetic test decision',source_review='Synthetic plain paragraphs reviewed',case_decision='empty' if d['filename']=='empty.dotx' else 'include',case_id='empty' if d['filename']=='empty.dotx' else 'case-one')
            for disp in c['dispositions']:
                disp.update(kind='heading' if disp['heading_suggestion'] else 'coded',reason='Question heading' if disp['heading_suggestion'] else '')
            if c['case_decision']=='include':
                p2=e['paragraphs'][1];stance='SUP' if d['filename']=='a.docx' else 'QUAL'
                u={'unit_id':'U0001','spans':[{'paragraph':p2['id'],'start':0,'end':len(p2['text'])}],
                   'meaning':'Synthetic interpretation','assignments':[{'target':'T2','stance':stance,'strength':'strong'}],
                   'provenance':'reported','confidence':'high','framework_fit':'in_framework','suggestion':'none',
                   'rationale':'Synthetic testing rationale','author_session':'test','review_status':'unreviewed'}
                c['units']=[u]
            v.write(p,c)
        refs=[d['doc_id']+'/U0001' for d in v.read(self.run/'manifest.json')['documents'] if d['filename']!='empty.dotx']
        v.write(self.run/'synthesis.json',{'status':'complete','author_session':'test','findings':[{'text':'Synthetic mixed evidence','evidence':refs}],'recommendations':[],'limitations':['Synthetic test only']})

    def tearDown(self):self.temp.cleanup()
    def coding(self):return self.run/'coding/D0001.json'
    def change(self,fn):
        p=self.coding();c=v.read(p);fn(c);v.write(p,c)
    def invalid(self,pattern):
        with self.assertRaisesRegex(ValueError,pattern):v.validate(self.run)

    def test_end_to_end_and_case_deduplication(self):
        v.build(self.run);out=self.run/'outputs/build-0001';v.verify(self.run,out)
        s=next(x for x in v.read(out/'support-summary.json') if x['target']=='T2')
        self.assertEqual((s['cases'],s['SUP'],s['QUAL'],s['evaluating_cases']),(1,1,1,1))
        row=next(r for r in v.read(out/'case-matrix.json') if r['target']=='T2');self.assertEqual(row['status'],'mixed')
        self.assertEqual(v.read(out/'statements.json')[0]['full text of statement'],self.text)
        self.assertEqual({str(p):v.digest(p) for p in self.source.rglob('*') if p.is_file()},self.hashes)
        old=v.digest(out/'statements.json');v.build(self.run)
        self.assertTrue((self.run/'outputs/build-0002/verify.json').exists());self.assertEqual(old,v.digest(out/'statements.json'))
    def test_preparation_refuses_existing_run(self):
        with self.assertRaisesRegex(ValueError,'already exists'):v.prepare(self.source,self.run)
    def test_source_tampering(self):
        (self.source/'a.docx').write_bytes(b'changed');self.invalid('source missing or changed')
    def test_added_source_requires_new_run(self):
        docx(self.source/'new.docx',['Synthetic late addition']);self.invalid('Source collection changed')
    def test_extraction_tampering(self):
        p=self.run/'extracted/D0001.json';x=v.read(p);x['paragraphs'][1]['text']='changed';v.write(p,x);self.invalid('extracted text changed')
    def test_incomplete_coding(self):
        self.change(lambda c:c.update(status='pending'));self.invalid('status must be complete')
    def test_gap(self):
        self.change(lambda c:c['units'][0]['spans'][0].update(start=1));self.invalid('uncovered characters')
    def test_overlap(self):
        def change(c):
            u=copy.deepcopy(c['units'][0]);u['unit_id']='U0002';c['units'].append(u)
        self.change(change);self.invalid('overlap')
    def test_invalid_strength(self):
        self.change(lambda c:c['units'][0]['assignments'][0].update(stance='ILL'));self.invalid('invalid strength')
    def test_unmapped_question(self):
        self.change(lambda c:c['dispositions'][1].update(question='Q0'));self.invalid('map substantive answers')
    def test_missing_disposition(self):
        self.change(lambda c:c['dispositions'].pop());self.invalid('exactly one disposition')
    def test_valid_split_preserves_all_characters(self):
        def change(c):
            first=c['units'][0];second=copy.deepcopy(first);second['unit_id']='U0002'
            first['spans'][0]['end']=20;second['spans'][0]['start']=20;c['units'].append(second)
        self.change(change)
        _,_,rows,_,_,_=v.validate(self.run)
        self.assertEqual(''.join(r['full text of statement'] for r in rows if r['doc_id']=='D0001'),self.text)
    def test_same_paragraph_multiple_spans_rejected(self):
        def change(c):
            span=c['units'][0]['spans'][0];second=copy.deepcopy(span)
            span['end']=20;second['start']=20;c['units'][0]['spans'].append(second)
        self.change(change);self.invalid('one span per paragraph')
    def test_local_nonrelevance_is_separate(self):
        self.change(lambda c:c['units'][0]['assignments'][0].update(stance='NR'))
        _,cb,rows,cases,_,_=v.validate(self.run);_,summary=v.tabulate(rows,cases,cb['targets'])
        s=next(s for s in summary if s['target']=='T2')
        self.assertEqual((s['NR'],s['OPP'],s['SUP']),(1,0,0))
    def test_ambiguous_sensitivity(self):
        self.change(lambda c:c['units'][0].update(provenance='ambiguous'))
        _,cb,rows,cases,_,_=v.validate(self.run)
        _,primary=v.tabulate(rows,cases,cb['targets'])
        _,alternative=v.tabulate(rows,cases,cb['targets'],'include_ambiguous')
        self.assertEqual(next(s for s in primary if s['target']=='T2')['SUP'],0)
        self.assertEqual(next(s for s in alternative if s['target']=='T2')['SUP'],1)
    def test_multiple_independent_cases_dynamic_denominator(self):
        self.change(lambda c:c.update(case_id='case-two'))
        _,cb,rows,cases,_,_=v.validate(self.run);_,summary=v.tabulate(rows,cases,cb['targets'])
        s=next(s for s in summary if s['target']=='T2')
        self.assertEqual(s['cases'],2);self.assertEqual(s['support_all_cases'],0.5)
    def test_unknown_target(self):
        self.change(lambda c:c['units'][0]['assignments'][0].update(target='MISSING'));self.invalid('unknown target')
    def test_missing_session(self):
        self.change(lambda c:c['units'][0].update(author_session='absent'));self.invalid('author_session')
    def test_human_review_needs_reviewer(self):
        self.change(lambda c:c['units'][0].update(review_status='reviewed'));self.invalid('reviewer required')
    def test_invalid_evidence_reference(self):
        p=self.run/'synthesis.json';s=v.read(p);s['findings'][0]['evidence']=['D9999/U0001'];v.write(p,s);self.invalid('valid doc_id/unit_id')
    def test_draft_requires_explicit_flag(self):
        p=self.run/'synthesis.json';s=v.read(p);s['status']='pending';v.write(p,s)
        with self.assertRaisesRegex(ValueError,'Synthesis is pending'):v.build(self.run)
        v.build(self.run,True);self.assertIn('DRAFT',(self.run/'outputs/build-0001/findings.md').read_text())
    def test_zero_denominators(self):
        matrix,summary=v.tabulate([],{}, {'T2':'Scientific value'})
        self.assertEqual(matrix,[]);self.assertIsNone(summary[0]['support_all_cases']);self.assertIsNone(summary[0]['support_evaluating_cases'])
    def test_illustration_is_not_support(self):
        self.change(lambda c:c['units'][0]['assignments'][0].update(stance='ILL',strength='n/a'))
        _,cb,rows,cases,_,_=v.validate(self.run);_,summary=v.tabulate(rows,cases,cb['targets'])
        s=next(s for s in summary if s['target']=='T2');self.assertEqual(s['SUP'],0);self.assertEqual(s['ILL'],1)
    def test_sensitivity_preserves_or_changes_denominator(self):
        self.change(lambda c:(c.update(sensitivity_exclude=True),c['units'][0].update(provenance='mixed')))
        _,cb,rows,cases,_,_=v.validate(self.run)
        _,reported=v.tabulate(rows,cases,cb['targets'],'reported_only')
        self.assertEqual(next(s for s in reported if s['target']=='T2')['SUP'],0)
        self.assertEqual(reported[0]['cases'],1)
        _,excluded=v.tabulate(rows,cases,cb['targets'],'exclude_flagged_cases');self.assertEqual(excluded[0]['cases'],0)
    def test_snapshot_edit_detected(self):
        v.build(self.run);out=self.run/'outputs/build-0001';(out/'findings.md').write_text('changed')
        with self.assertRaisesRegex(ValueError,'Output changed'):v.verify(self.run,out)
    def test_changed_coding_needs_new_build(self):
        v.build(self.run);self.change(lambda c:c['units'][0].update(meaning='Changed synthetic interpretation'))
        with self.assertRaisesRegex(ValueError,'Run inputs differ'):v.verify(self.run,self.run/'outputs/build-0001')
    def test_tracked_changes_and_auxiliary(self):
        path=self.root/'special.docx'
        with zipfile.ZipFile(path,'w') as z:
            z.writestr('word/document.xml','<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:del><w:r><w:delText>removed</w:delText></w:r></w:del><w:ins><w:r><w:t>inserted</w:t></w:r></w:ins><w:r><w:tab/><w:t>text</w:t><w:br/></w:r></w:p></w:body></w:document>')
            z.writestr('word/comments.xml','<w:comments xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:comment><w:p><w:r><w:t>Synthetic comment</w:t></w:r></w:p></w:comment></w:comments>')
        e=v.extract(path);self.assertEqual(e['paragraphs'][0]['text'],'inserted\ttext\n');self.assertEqual(len(e['warnings']),3)


if __name__=='__main__':unittest.main()
