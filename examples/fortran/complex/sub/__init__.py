import sys
from pathlib import Path
p = Path(__file__)
root = p.parent.parent.parent.parent.absolute()
print(root)
sys.path.append(str(root))
import fortran_importer
from sub.sum_of_square import sum_of_square
