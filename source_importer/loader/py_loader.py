# Module Loader for a URL
import sys
import imp
import warnings
import importlib.abc

from urllib.request import urlopen
from urllib.error import HTTPError, URLError


class UrlModuleLoader(importlib.abc.SourceLoader):
    def __init__(self, baseurl):
        self._baseurl = baseurl
        self._source_cache = {}

    def create_module(self,spec):
        """这边只要调用父类的实现即可."""
        mod = sys.modules.setdefault(spec.name, imp.new_module(spec.name))
        mod.__file__ = self.get_filename(spec.name)
        mod.__loader__ = self
        mod.__package__ = spec.name.rpartition('.')[0]
        return mod


    def exec_module (self, module):
        """在_post_import_hooks中查找对应模块中的回调函数并执行."""
        code = self.get_code(module.__name__)
        exec(code, module.__dict__)

    # Optional extensions
    def get_code(self, fullname):
        src = self.get_source(fullname)
        return compile(src, self.get_filename(fullname), 'exec')

    def get_data(self, path):
        pass

    def get_filename(self, fullname):
        return self._baseurl + '/' + fullname.split('.')[-1] + '.py'

    def get_source(self, fullname):
        filename = self.get_filename(fullname)
        warnings.warn(f'loader: reading {filename}', UserWarning)
        if filename in self._source_cache:
            warnings.warn(f'loader: cached {fullname} not found', UserWarning)
            return self._source_cache[filename]
        try:
            u = urlopen(filename)
            source = u.read().decode('utf-8')
            warnings.warn(f'loader: {filename} loaded', UserWarning)
            self._source_cache[filename] = source
            return source
        except (HTTPError, URLError) as e:
            warnings.warn(f'loader: {filename} failed. {e}', UserWarning)
            raise ImportError("Can't load %s" % filename)

    def is_package(self, fullname):
        return False

# Package loader for a URL
class UrlPackageLoader(UrlModuleLoader):
    def create_module(self, spec):
        mod = super().create_module(spec)
        mod.__path__ = [ self._baseurl ]
        mod.__package__ = spec.name
        return mod

    def get_filename(self, fullname):
        return self._baseurl + '/' + '__init__.py'

    def is_package(self, fullname):
        return True

