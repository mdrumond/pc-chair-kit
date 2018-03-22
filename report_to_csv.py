from util import iterate_csv
import sys

def main():
    report = sys.argv[1]
    output_csv = sys.argv[2]

    output_lines = ['paper,assignment,email']
    for r in iterate_csv(report):
        valid, paper, email, reasons = r

        if valid=='x':
            output_lines.append("%s,conflict,%s" %(paper, email))

    with open(output_csv,'w') as f:
        f.write('\n'.join(output_lines))
        f.write('\n')

if __name__ == '__main__':
    main()
