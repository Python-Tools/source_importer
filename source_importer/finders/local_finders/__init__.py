"""load local finders."""
import sys
import warnings
try:
    import numpy
except ModuleNotFoundError:
    warnings.warn('to import a fortain file you need numpy', UserWarning)
else:
    from .fortran_finder import FortranImportFinder
    finder = FortranImportFinder()
    sys.meta_path.insert(0, finder)
    warnings.warn('now you can import a fortain file', UserWarning)