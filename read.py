import json
import pickle

from numpy import diag_indices

with open('./data/mydata_new_baidu_.pkl', 'rb') as f:
    my_data = pickle.load(f)
with open('./data/mydata_url2secs_new_baidu.pkl', 'rb') as f:
    url2secs = pickle.load(f)

print(len(url2secs))

dataset = json.load(open('./dataset_new_3.json', 'r', encoding='utf-8'))
url_set = set()
key_set = set()
corpus = {}
d_id = 1
q_id = 1
query_pos = {}
query_neg = {}
querys = {}

for data in dataset:
    for sec_data in data['contents']:
        for ann_data in sec_data['tooltips']:
            key = ann_data['origin']
            if key not in query_pos:
                query_pos[key] = []
                query_neg[key] = []
            anno = ann_data['translation']
            urls = []
            rsecs = []
            rpo_secs = []
            for ref_data in ann_data['sources']:
                url = ref_data['link']
                url_set.add(url)
                ref = ref_data['reference']
                if url in url2secs:
                    sec = ''
                    for s in url2secs[url]:
                        sec+=s
                        
                    ref_sts = ref.split('。')
                    sec_sts = sec.split('。')
                    for sec_st in sec_sts:
                        if sec_st not in corpus and len(sec_st)>1:
                            corpus[sec_st] = d_id
                            d_id += 1


for data in dataset:
    for sec_data in data['contents']:
        for ann_data in sec_data['tooltips']:
            key = ann_data['origin']
            anno = ann_data['translation']
            urls = []
            rsecs = []
            rpo_secs = []
            for ref_data in ann_data['sources']:
                url = ref_data['link']
                url_set.add(url)
                ref = ref_data['reference']
                if url in url2secs:

                    sec = ''
                    for s in url2secs[url]:
                        sec+=s
                        
                    ref_sts = ref.split('。')
                    sec_sts = sec.split('。')
                    for ref_st in ref_sts:
                        if ref_st in corpus:
                            p = corpus[ref_st]
                            if p not in query_pos[key]:
                                query_pos[key].append(p)
                    
                    for sec_st in sec_sts:
                        if sec_st in corpus:
                            p = corpus[sec_st]
                            if p not in query_neg[key] and p not in query_pos[key]:
                                query_neg[key].append(p)
                    
                    if key not in key_set:
                        querys[q_id] = key
                        q_id += 1
                        key_set.add(key)
                    
                    # if len(ref_sts)>1:
                        # print(url)
                        # print('-'*40)
                        # print(ref)
                        # print('-'*40)
                        # print(sec)
                        # print('*'*40)
                        # print()

                                

print('|C|:{}'.format(len(corpus)))
corpus_tot_len = 0
for d in corpus:
    corpus_tot_len += len(d)
print('corpus_tot_len:{}'.format(corpus_tot_len))
print('L(C):{}'.format(corpus_tot_len/len(corpus)))
print()

print('|q|:{}'.format(len(query_pos)))
query_tot_len = 0
for q in query_pos:
    query_tot_len += len(q)

print('query_tot_len:{}'.format(query_tot_len))
print('L(q):{}'.format(query_tot_len/len(query_pos)))
print()

tot_judge = 0
for q in query_pos:
    tot_judge += len(query_pos[q])

print('|J|:{}'.format(tot_judge))
print('|J|/q:{}'.format(tot_judge/len(query_pos)))

q_train_ids, q_dev_ids, q_eval_ids = [], [], []

for i in range(len(querys)):
    if i <= len(querys)//10*8:
        q_train_ids.append(i+1)
    elif i <= len(querys)//10*9:
        q_dev_ids.append(i+1)
    else:
        q_eval_ids.append(i+1)

print('train:dev:eval={}:{}:{}'.format(len(q_train_ids), len(q_dev_ids), len(q_eval_ids)))


with open('./data/ir/collection.tsv','w', encoding='utf-8') as f:
    for passage in corpus:
        pid = corpus[passage]
        p = passage.replace('\t',' ').replace('\r',' ').replace('\n',' ').strip()
        f.write('{}\t{}\n'.format(pid, p))


with open('./data/ir/queries.train.tsv','w', encoding='utf-8') as f:
    for qid in q_train_ids:
        query = querys[qid].replace('\t',' ').replace('\r',' ').replace('\n',' ').strip()
        f.write('{}\t{}\n'.format(qid, query))

with open('./data/ir/queries.dev.tsv','w', encoding='utf-8') as f:
    for qid in q_dev_ids:
        query = querys[qid].replace('\t',' ').replace('\r',' ').replace('\n',' ').strip()
        f.write('{}\t{}\n'.format(qid, query))

with open('./data/ir/queries.eval.tsv','w', encoding='utf-8') as f:
    for qid in q_eval_ids:
        query = querys[qid].replace('\t',' ').replace('\r',' ').replace('\n',' ').strip()
        f.write('{}\t{}\n'.format(qid, query))

with open('./data/ir/queries.dev.small.tsv','w', encoding='utf-8') as f:
    for qid in q_dev_ids[:100]:
        query = querys[qid].replace('\t',' ').replace('\r',' ').replace('\n',' ').strip()
        f.write('{}\t{}\n'.format(qid, query))

with open('./data/ir/queries.eval.small.tsv','w', encoding='utf-8') as f:
    for qid in q_eval_ids[:100]:
        query = querys[qid].replace('\t',' ').replace('\r',' ').replace('\n',' ').strip()
        f.write('{}\t{}\n'.format(qid, query))

with open('./data/ir/qidpidtriples.train.small.tsv','w', encoding='utf-8') as f:
    for qid in q_train_ids:
        query = querys[qid].replace('\t',' ').replace('\r',' ').replace('\n',' ').strip()
        for pos_id in query_pos[querys[qid]]:
            for neg_id in query_neg[querys[qid]]:
                f.write('{}\t{}\t{}\n'.format(qid, pos_id, neg_id))

with open('./data/ir/qrels.train.tsv','w', encoding='utf-8') as f:
    for qid in q_train_ids:
        query = querys[qid].replace('\t',' ').replace('\r',' ').replace('\n',' ').strip()
        for pos_id in query_pos[querys[qid]]:
            f.write('{}\t{}\t{}\t{}\n'.format(qid, 0, pos_id, 1))

with open('./data/ir/qrels.dev.small.tsv','w', encoding='utf-8') as f:
    for qid in q_dev_ids:
        query = querys[qid].replace('\t',' ').replace('\r',' ').replace('\n',' ').strip()
        for pos_id in query_pos[querys[qid]]:
            f.write('{}\t{}\t{}\t{}\n'.format(qid, 0, pos_id, 1))
