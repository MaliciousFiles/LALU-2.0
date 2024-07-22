import os
import sys
from time import sleep
import subprocess as SP

inp = None
proc = None

fName = sys.argv[1]
if __name__ == "__main__":
    with open(fName) as f:
        contents = None
        
        while True:
            sleep(1)
            f.seek(0)
            newContents = f.read()
            
            if newContents != contents:
                if (platform := sys.platform) == 'win32':
                    os.system("cls")
                elif platform == 'darwin':
                    os.system("clear")
                else:
                    exit('Unsupported Operating System `' + platform +'`')
                
                print(f"Opening new process.\n\tnew: {hash(newContents)} ({type(newContents)}) != old: {hash(contents)} ({type(contents)})\n")
                contents = newContents
                print('Calling: `'+f'python {fName} {" ".join(sys.argv[2:])}'+'`\n\n')
                if proc != None:
                    proc.kill()
                    print('Killed')
                proc = SP.Popen(f'python {fName} {" ".join(sys.argv[2:])}')
