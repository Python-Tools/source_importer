"""定义loader."""
import sys
import hashlib
import shutil
import warnings
from pathlib import Path
import importlib.util
from importlib.abc import Loader
from numpy import f2py


class FortranImportLoader(Loader):
    """fortran code's loader."""

    def __init__(self, source_path):
        self._source_path = source_path
        with open(str(self._source_path), "rb") as f:
            self.source = f.read()
        self.source_hash = hashlib.md5(self.source)
        self.wrap_spec = None

    def _check_source(self):
        with open(str(self._source_path), "rb") as f:
            source = f.read()
        source_hash = hashlib.md5(source)
        if self.source_hash == source_hash:
            return False
        else:
            self.source_hash = source_hash
            self.source = source
            return True

    def _compile(self):
        modulename = self._source_path.stem
        dir_path = str(Path(self._source_path).parent)
        suffix = self._source_path.suffix
        complie_result = f2py.compile(
            self.source,
            modulename=modulename,
            verbose=False,
            extra_args="--quiet",
            extension=suffix
        )
        if complie_result != 0:
            raise ImportError("complie failed")
        else:
            root = Path(dir_path).resolve()
            find_files = [
                i for i in root.iterdir() if i.match(f"{modulename}*.pyd") or i.match(f"{modulename}*.so")
            ]
            if len(find_files) != 1:
                raise ImportError(f"find {len(find_files)} Dynamic Link Library")
            file = find_files[0]
            target_path = self._source_path.with_name(file.name)
            if file != target_path:
                try:
                    shutil.move(str(file), str(target_path))
                except shutil.SameFileError as sfe:
                    pass
                except Exception as e:
                    raise e
            del_target = [i for i in root.iterdir() if i.match(str(file) + ".*")]
            for i in del_target:
                try:
                    i.chmod(0o777)
                    i.unlink()
                except Exception as e:
                    warnings.warn(f'can not delete file {i}:{type(e)}--{e}', UserWarning)
            return target_path

    def create_module(self, spec):
        self._check_source()
        target_path = self._compile()
        self.wrap_spec = importlib.util.spec_from_file_location(
            spec.name,
            str(target_path)
        )
        mod = importlib.util.module_from_spec(self.wrap_spec)
        mod = sys.modules.setdefault(spec.name, mod)
        return mod

    def exec_module(self, module):
        """在_post_import_hooks中查找对应模块中的回调函数并执行."""
        self.wrap_spec.loader.exec_module(module)
