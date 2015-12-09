import os
import sys

absolute_path = os.path.dirname(os.path.realpath(sys.argv[0])) + '/static/'

with open(absolute_path + 'log.txt', 'w') as g:
    for f in os.listdir(absolute_path):
        g.write(f + '\n')
        os.remove(absolute_path + f)
