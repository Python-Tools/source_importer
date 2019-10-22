import sys
from pathlib import Path
p = Path(__file__)
root = p.parent.parent.parent.parent.absolute()
sys.path.append(str(root))
import source_importer
from sum_of_square import sum_of_square

result = sum_of_square([1,2,3,4])

print(result)