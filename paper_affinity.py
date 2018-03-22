"""
    This script is used to calculate the affinity between an reviewer and a
    paper
    The affinity depends on 3 parameters
        - # of citations a paper makes to the reviewer
        - matches between the paper topics and our own expertise db
        - matches between the paper topics and the reviewer preference
"""
import argparse
import re
import csv
from util import (iterate_csv, get_dict_json)
from tqdm import tqdm
from os import listdir
from os.path import join
from subprocess import Popen, PIPE


def get_citation_count(submission_csv, citation_dict):
    number = re.search(".*paper(\d+).csv", submission_csv)
    if not number:
        raise ValueError("Couldn't get paper number in string: " +
                         submission_csv)
    N = int(number.group(1))

    citation_dict[N] = {}
    for r in iterate_csv(submission_csv):
        email, citcount = r
        citation_dict[N][email] = int(citcount)


def read_expertise_db(expertise_csv, exp_list):
    db = {}
    for r in iterate_csv(expertise_csv):
        db[r[2]] = {}
        if len(exp_list) != len(r[3:]):
            print(exp_list)
            print(r[3:])
            raise ValueError("Exp list and expertise db topics do not match "
                             "%d vs. %d" % (len(exp_list), len(r[3:])))
        db[r[2]]['expertises'] = [l for l, v in zip(exp_list, r[3:])
                                  if v.strip()]
    return db


def read_expertise_to_topics(topics_to_expertise_csv):
    exp_list = []
    topic_list = set()
    t_to_e = {}
    e_to_t = {}
    for r in iterate_csv(topics_to_expertise_csv):
        e = r[0]
        exp_list.append(e)
        ts = [t for t in r[1:] if t]
        e_to_t[e] = ts
        for t in ts:
            topic_list.add(t)
            if t not in t_to_e:
                t_to_e[t] = []
            t_to_e[t].append(e)

    return e_to_t, t_to_e, exp_list, topic_list


def write_dict_of_lists(filename, toWrite, schema):
    with open(filename, 'w') as fh:
        writer = csv.DictWriter(fh, fieldnames=schema)
        writer.writeheader()
        for k, v in toWrite.items():
            if v is not None:
                writer.writerow(v)


def pdf_to_text(filename):
    process = Popen(["pdftotext", filename], stdout=PIPE)
    (output, err) = process.communicate()
    exit_code = process.wait()
    if exit_code:
        print("WARNING: couldn't parse %s" % filename)


def match_author(rolling_word_list, pc_members):
    pass


def parse_txt(filename, pc_members):
    txt = ""
    pc_matches = {pc: 0 for pc in pc_members}
    ackset = False
    parsing_references = False
    rolling_word_list = ['', '', '']
    with open(filename, 'r') as f:
        txt = f.read()

    if not txt:
        return None

    words = txt.split()
    for w in words:
        if parsing_references:
            rolling_word_list = rolling_word_list[1:] + [w]
            match_author(rolling_word_list, pc_matches, pc_members)

        if w.lower == 'references':
            parsing_references = True
        elif w.lower == 'acknowledgement':
            ackset = True

        print(w)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--expertise-db",
                        help="list of authors expertises")
    parser.add_argument("--paper-json",
                        help='json with submitted papers and topics')
    parser.add_argument("--pc-csv",
                        help='csv from hotcrp with pc list')
    parser.add_argument("--expertise-to-topics",
                        help="File that maps expertises in the expertise db "
                        "to the topics used in HotCRP")
    parser.add_argument("--submissions",
                        help="Folder where the submissions are")
    parser.add_argument("--out-pc-topics",
                        help="PC topics reports")
    parser.add_argument("--out-pc-citations",
                        help="PC citations reports")
    parser.add_argument("--out-affinity",
                        help="Global affinity citations")
    args = parser.parse_args()
    topics_csv = args.out_pc_topics
    citations_csv = args.out_pc_citations
    hotcrp_csv = args.out_affinity

    (e_to_t, t_to_e,
     exp_list, topic_list) = read_expertise_to_topics(args.expertise_to_topics)
    expertise_db = read_expertise_db(args.expertise_db, exp_list)

    submissionList = get_dict_json(args.paper_json)

    allFiles = listdir(args.submissions)
    justcsvs = list(filter(lambda x: x.endswith(".csv"), allFiles))
    refCounts = list(map(lambda x: join(args.submissions, x), justcsvs))

    citationsList = {}
    for ref in refCounts:
        get_citation_count(ref, citationsList)

    sub_prefs_exp = {}
    sub_prefs_cit = {}
    sub_topics = {}
    for submission in tqdm(submissionList):
        pid = submission['pid']
        paper_topics = (submission['topics']
                        if 'topics' in submission else [])
        sub_topics[pid] = (submission['topics']
                           if 'topics' in submission else [])

        pc_citations = (citationsList[pid]
                        if pid in citationsList else {})

        sub_prefs_exp[pid] = {}
        sub_prefs_cit[pid] = {}
        for email, rev in expertise_db.items():
            score_expertise = 0
            score_citation = 0

            exps = rev['expertises']
            if email in pc_citations:
                score_citation = pc_citations[email]

            for topic in paper_topics:
                for x in t_to_e[topic]:
                    if x in exps:
                        score_expertise += 1

            sub_prefs_exp[pid][email] = score_expertise
            sub_prefs_cit[pid][email] = score_citation

    emails = sorted([k for k, v in expertise_db.items()])
    pids = sorted([int(s['pid']) for s in submissionList])

    headers = 'pid,topics,' + ','.join(emails) + ',total' + '\n'

    def write_report(report_name, scores):
        with open(report_name, 'w') as f:
            f.write(headers)
            for pid in pids:
                topics = (';'.join(sub_topics[pid])).replace(',', '-')
                s = '%d,%s,' % (pid, topics)
                s += ','.join([str(scores[pid][e]) for e in emails])
                s += ',%d\n' % sum([scores[pid][e] for e in emails])

                f.write(s)

    write_report(topics_csv, sub_prefs_exp)
    write_report(citations_csv, sub_prefs_cit)

    # Print csv for hotcrp upload
    schema = "paper,email,assignment,preference\n"
    with open(hotcrp_csv, 'w') as f:
        f.write(schema)
        for pid in pids:
            for email in emails:
                score = sub_prefs_exp[pid][email] + sub_prefs_cit[pid][email]
                s = "%s,%s,preference,%d\n" % (pid, email, score)
                f.write(s)


if __name__ == '__main__':
    main()
