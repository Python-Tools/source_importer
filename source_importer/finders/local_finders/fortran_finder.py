"""在本地文件系统中查找fortain模块."""
import sys
from pathlib import Path
from importlib.abc import MetaPathFinder
from importlib.machinery import ModuleSpec
import numpy
from source_importer.loader import FortranImportLoader

class FortranImportFinder(MetaPathFinder):

    def find_spec(self, fullname, paths=None, target=None):
        relative_path = fullname.replace(".", "/")
        base_path = None
        full_path = None
        for path in sys.path:
            path_dir = Path(path)
            base_path = path_dir.resolve()
            abs_path = base_path.joinpath(relative_path)
            # 如果已经编译,那么跳过
            if path_dir.is_dir():
                find_files = [
                    i for i in path_dir.iterdir() if i.match(f"{relative_path}*.pyd") or i.match(f"{relative_path}*.so")
                ]
                if len(find_files) > 0:
                    return None
            # 判断是否是fortran模块
            if abs_path.with_suffix(".f").exists():
                full_path = abs_path.with_suffix(".f")
                break
            elif abs_path.with_suffix(".f90").exists():
                full_path = abs_path.with_suffix(".f90")
                break
            elif abs_path.with_suffix(".f95").exists():
                full_path = abs_path.with_suffix(".f95")
                break
        else:
            # 都不是就跳过
            return None
        loader = FortranImportLoader(full_path)
        spec = ModuleSpec(fullname, loader, origin=paths)
        return spec
