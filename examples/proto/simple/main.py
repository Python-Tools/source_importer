import sys
from pathlib import Path
p = Path(__file__).absolute()
print(p)
root = p.parent.parent.parent.parent.absolute()
print(root)
sys.path.append(str(root))
import source_importer
import tutorial

print(tutorial.Person)