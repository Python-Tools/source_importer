"""load local finders."""
import sys
import warnings
import subprocess
try:
    import numpy
except ModuleNotFoundError:
    warnings.warn('to import a fortain file you need numpy', UserWarning)
else:
    from .fortran_finder import FortranImportFinder
    finder = FortranImportFinder()
    sys.meta_path.insert(0, finder)
    warnings.warn('now you can import a fortain file', UserWarning)

try:
    import google.protobuf
except ModuleNotFoundError:
    warnings.warn('to import a protobuf file you need protobuf', UserWarning)
else:
    if subprocess.run("protoc -h",shell=True, check=False).returncode == 0:
        from .proto_finder import ProtoImportFinder
        finder = ProtoImportFinder()
        sys.meta_path.insert(0, finder)
        warnings.warn('now you can import a protobuffer file', UserWarning)
    else:
        warnings.warn('to import a protobuffer file you need protoc', UserWarning)