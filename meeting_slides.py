import math


def print_conflicts(cs):
    if cs:
        str_out = ''
        for c in cs:
            str_out += '%s\n\n' % c
        return str_out
    else:
        return ''


def get_coi(tags):
    if tags is None:
        return ''
    if '#conflict_with_chair' in tags:
        return 'Alternate chair 1'
    elif '#double_conflict' in tags:
        return 'Alternate chair 2'
    else:
        return 'PC Chair'


def gen_presentation(conflicts, tags):
    """Generates a presentation that lists the conflicts for each
    paper, with the next conflict listed.
    Both arguments are lists, and this lists should be alread ordered
    in the desired discussion order. We porpusefully omitted paper 
    identification in the conflict slides, but it can be easilly 
    added.

    Arguments:
        conflicts {list[list[str]]} -- List with one list
            of conflict names for each paper. This list should have the
            names already formatted in the way they should be shown.

        tags {list[list[str]]} -- List with one list tags for each paper.
            Tags are used to identify  when a paper have a different chair.
            See 'get_coi' to see how this is used.

    Returns:
        [str] -- str with the latex contents. This str can be dumped on a
            file and compiled with any latex compiler.
    """
    str_out = '\\documentclass[10pt,t,serif]{beamer}\n'
    str_out += '\\newcommand\\Fontsmall{\\fontsize{7}{7}\\selectfont}\n'
    str_out += '\\begin{document}\n'

    cs = [(i, j) for i, j in zip(conflicts, conflicts[1:] + [[]])]
    tags = [(i, j) for i, j in zip(tags, tags[1:] + [None])]
    for i, ((c1, c2), (t1, t2)) in enumerate(zip(cs, tags), 1):
        str_out += '\\begin{frame}[t]{Discussion order: %d}\n' % i
        # if len(c1) > 24 or len(c2) > 24:
        # str_out += '\\Fontsmall\n'
        c1 = sorted(c1)
        c2 = sorted(c2)
        coi1 = get_coi(t1)
        coi2 = get_coi(t2)

        str_out += '\\begin{columns}[t]\n'
        str_out += '\\column{.4\\textwidth}\n'

        str_out += 'Current paper \n\n'
        str_out += '\\textbf{Chair}: %s\n\n' % coi1
        str_out += 'Conflicts:\n\n'
        str_out += '\\vspace{10pt}\n\n'
        str_out += '\\column{.1\\textwidth}\n'
        str_out += '\\column{.4\\textwidth}\n'
        str_out += '\\column{.1\\textwidth}\n'
        str_out += '\\end{columns}\n'

        half = int(math.ceil(len(c1)/2))
        quarter = int(math.ceil(half/2))

        str_out += '\\begin{columns}[t]\n'
        str_out += '\\column{.25\\textwidth}\n'
        str_out += print_conflicts(c1[:quarter])
        str_out += '\\column{.25\\textwidth}\n'
        str_out += print_conflicts(c1[quarter:half])
        str_out += '\\column{.25\\textwidth}\n'
        str_out += print_conflicts(c1[half:half+quarter])
        str_out += '\\column{.25\\textwidth}\n'
        str_out += print_conflicts(c1[half+quarter:])
        str_out += '\\end{columns}\n'
        str_out += '\\vspace{15pt}\n\\hrule\n\\vspace{15pt}\n'

        str_out += '\\begin{columns}[t]\n'
        str_out += '\\column{.4\\textwidth}\n'

        str_out += '\n\n Next paper\n\n'
        if t2 is not None:
            str_out += '\\textbf{Chair}: %s\n\n' % coi2
        else:
            str_out += '\\textbf{Chair}: --\n\n'
        str_out += 'Conflicts:\n\n'
        str_out += '\\vspace{10pt}\n\n'
        str_out += '\\column{.1\\textwidth}\n'
        str_out += '\\column{.4\\textwidth}\n'
        str_out += '\\column{.1\\textwidth}\n'
        str_out += '\\end{columns}\n'

        half = int(math.ceil(len(c2)/2))
        quarter = int(math.ceil(half/2))

        str_out += '\\begin{columns}[t]\n'
        str_out += '\\column{.25\\textwidth}\n'
        str_out += print_conflicts(c2[:quarter])
        str_out += '\\column{.25\\textwidth}\n'
        str_out += print_conflicts(c2[quarter:half])
        str_out += '\\column{.25\\textwidth}\n'
        str_out += print_conflicts(c2[half:half+quarter])
        str_out += '\\column{.25\\textwidth}\n'
        str_out += print_conflicts(c2[half+quarter:])
        str_out += '\\end{columns}\n'

        str_out += '\\end{frame}\n'

    str_out += '\\end{document}\n'
    return str_out
