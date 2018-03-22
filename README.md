# PC Chair Kit


This is a kit to make PC chairs lifes less painful.

They can be used for the following tasks:
* Conflict of interest management.
* Paper assignments.
* Various nagging tasks (prepare to nag a lot to your PCs about missed dealines and ignored guidelines).
* Managing ranking information (disclosing it to reviewers, ranking papers using PC ranks, etc)
* Meeting management (if for some reason you can't use HotCRP's awesome meeting tracker).
* Conflict of interest management for TOT awards.

## Conflict of interest (COI) management
EXPLAIN WHY WE USE DBLP

The workflow for checking/flagging COIs between papers and PC members is the following:
1. Generate a `.csv` with a list of the PC members, with their first and last names. This list have to be manually generated and it has the following format:
```
id, first_name, last_name
1, PCFirstName1, PCLastName1
```

2. Use the first list as an input to DBLP crawler. To do so, run:
```bash
python3 dblp_crawler.py author-keys --author-list AUTHOR_LIST_FILE --author-keys AUTHOR_KEYS_FILE
```
This command will generate another CSV file in `AUTHOR_KEYS_FILE` which has all the DBLP keys that matched the author names. Your job now is to go through that file and filter out all the bad entries (i.e. homonyms). You can do that by removing the `x` in the `valid` column of `AUTHOR_KEYS_FILE`.

3. Generate the paper list from the author-keys file. To do so, run:
```bash
python3 dblp_crawler.py paper-list --author-keys AUTHOR_KEYS_FILE --paper-list PAPER_LIST_FILE
```
This command will generate another CSV file in `PAPER_LIST_FILE` with all the papers authored by each PC member. Your job now is to go through that file and filter out all the bad entries (i.e. papers that do not constitute COI with co-authors), the same way you filtered out the author keys.

4. Generate the co-author list from the paper list. To do so, run:
```bash
python3 dblp_crawler.py list-co-authors --paper-list PAPER_LIST_FILE
```
This command will warm up the paper cache so that every time you read from this list, you won't have to query it from DBLP. As you might notice, querying DBLP takes a long time.

5. Download and clean paper information from HotCRP. Go to HotCRP and download all the paper info. Search for all submitted papers, and, on the bottom of the page, click `select all`, and, in the drop down list, select `JSON`, and click go. You will get a JSON file. In that file you need to clean up all the information. For every paper, make sure that the COI list (collaborators) is in the following form:
```
Institution1 \n
AuthorFirstName AuthorLastName, Instutution2 \n
```
The scripts will interpret everything that does not have a `,` or a `(` before the end of the line as an institution name, and everything else as an author name. Make sure there are no line with multiple institutions/authors. The scripts will ignore authors institutions, therefore, it is enough to end author names with a `,` to make sure the script will recognize them. Keep an eye on names that are common and short, as the cause lots of trouble when matching strings. For the author list, make sure that, for authors with multiple affiliations, you list all the affiliations in the `collaborators` field, as the scripts won't be able to recognize multiple affiliations.

Cleaning up submission data is a time consuming and error prone task, therefore, make sure you have the time to do it. Do not create any deadlines shortly after the submission deadline, as you might find yourself spending days parsing through bad author data. To aid in this task you can use the `collab_format_checker.py` script, that looks for suspicious entries in the collaborator fields. Look at the script for more details.

6. Download and clean PC data. Go to HotCRP `User` page and select the PC. On the bottom of the page, click on `select all` and download `PC info`.

7. Cross check all conflicts. You can do so by running:
```bash
python3 cross_reference_conflcits.py INSTITUTIONS_CSV PAPER_DATA PC_INFO PC_PAPERS OUT_PROPER_CONFLICTS PAPER_COLLABS_FIELD_CONFLICTS PC_COLLABS_FIELD_CONFLICTS DBLP_COLLABS_FIELD_CONFLICTS SUSPICIOUS_CONFLICTS
```

This scripts takes the following inputs:
* **INSTITUTIONS_CSV** CSV file with list of institutions and their aliases. We added ours to this repo, in `data/institutions.csv`, and you can add institutions to that file as you see fit.
* **PAPER_DATA** The `.json` file you donwloaded and cleaned with the paper info.
* **PC_INFO** The `.csv` file you you downloaded and cleaned with the PC info
* **PC_PAPERS** The `.csv` file you generated and filtered with the list of PC papers.
* **OUT_PROPER_CONFLICTS** The output file with the proper conflicts (the conflicts flagged by authors in the submission form.
* **OUT_PAPER_COLLABS_FIELD_CONFLICTS** The output file with conflicts that are detected by checking the paper collabs field of the submission
* **OUT_PC_COLLABS_FIELD_CONFLICTS** The output file with conflicts that are detected by checking the paper collabs field of the PCs
* **OUT_DBLP_COLLABS_FIELD_CONFLICTS** The output file with conflicts that are detected through DBLP
* **OUT_SUSPICIOUS_CONFLICTS** The output file with conflicts that are flagged by authors but can't be checked elsewhere


## Paper assignments

## Nagging your PC members

## Managing the PC meeting

## COIs for TOT Award.
