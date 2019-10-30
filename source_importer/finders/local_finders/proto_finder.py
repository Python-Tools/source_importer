"""在本地文件系统中查找fortain模块."""
import sys
from pathlib import Path
from importlib.abc import MetaPathFinder
from importlib.machinery import ModuleSpec
import numpy
from source_importer.loader import ProtoBufferImportLoader, PyProtoBufferImportLoader


class ProtoImportFinder(MetaPathFinder):

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
                    i for i in path_dir.iterdir() if i.match(f"{relative_path}_pb2.py")
                ]
                if len(find_files) > 0:
                    full_path = str(find_files[0])
                    loader = PyProtoBufferImportLoader(full_path)
                    spec = ModuleSpec(fullname, loader, origin=paths)
                    return spec
            # 判断是否是proto模块
            if abs_path.with_suffix(".proto").exists():
                full_path = abs_path.with_suffix(".proto")
                loader = ProtoBufferImportLoader(full_path)
                spec = ModuleSpec(fullname, loader, origin=paths)
                return spec
        else:
            # 都不是就跳过
            return None
