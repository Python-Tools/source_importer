import warnings
import sys
import importlib.abc
from importlib.machinery import ModuleSpec
from html.parser import HTMLParser
from urllib.request import urlopen

from source_importer.loader import UrlModuleLoader, UrlPackageLoader


def _get_links(url):
    """在指定url查找包含的其他url"""
    class LinkParser(HTMLParser):
        """解析html文件,从中获取a标签中的url"""
        def handle_starttag(self, tag, attrs):
            if tag == 'a':
                attrs = dict(attrs)
                links.add(attrs.get('href').rstrip('/'))
    links = set()
    try:
        warnings.warn(f'Getting links from {url}',UserWarning)
        u = urlopen(url)
        parser = LinkParser()
        parser.feed(u.read().decode('utf-8'))
    except Exception as e:
        warnings.warn(f'Could not get links. {e}',UserWarning)
    warnings.warn(f'links: {links}',UserWarning)
    return links

class UrlPathFinder(importlib.abc.PathEntryFinder):
    """查找url及其中a标签中指向的url中的模块."""
    def __init__(self, baseurl):
        self._links = None # 保存一个baseurl中指定的可用url路径
        self._baseurl = baseurl # 

    def find_spec(self, fullname, paths=None, target=None):
        warnings.warn(f'find_loader: {fullname}', UserWarning)
        parts = fullname.split('.')
        basename = parts[-1]
        # 查看links和初始化links
        if self._links is None:
            self._links = [] 
            self._links = _get_links(self._baseurl)
        spec = None

        # 检查links是不是package,判断的标准是有没有.py
        if basename in self._links:
            warnings.warn(f'find_loader: trying package {fullname}', UserWarning)
            fullurl = self._baseurl + '/' + basename
            try:
                loader = UrlPackageLoader(fullurl)
                loader.load_module(fullname)#
                warnings.warn(f'find_loader: package {fullname} loaded', UserWarning)
                spec = ModuleSpec(fullname, loader, origin=paths)
            except ImportError as ie:
                warnings.warn(f'find_loader: {fullname} is a namespace package', UserWarning)
                spec = None
            except Exception as e:
                raise e


        elif (basename + '.py') in self._links:
            # 正常module的处理
            warnings.warn(f'find_loader: module {fullname} found', UserWarning)
            loader = UrlModuleLoader(self._baseurl)
            spec = ModuleSpec(fullname, loader, origin=paths)
        else:
            warnings.warn(f'find_loader: module {fullname} not found', UserWarning)

        return spec

    def invalidate_caches(self):
        warnings.warn("invalidating link cache", UserWarning)
        self._links = None


_url_path_cache = {}
def handle_url(path):
    if path.startswith(('http://', 'https://')):
        warnings.warn(f'Handle path? {path}. [Yes]', UserWarning)
        if path in _url_path_cache:
            finder = _url_path_cache[path]
        else:
            finder = UrlPathFinder(path)
            _url_path_cache[path] = finder
        return finder
    else:
        warnings.warn(f'Handle path? {path}. [No]', UserWarning)

def install_path_hook():
    sys.path_hooks.append(handle_url)
    sys.path_importer_cache.clear()
    warnings.warn('Installing handle_url', UserWarning)

def remove_path_hook():
    sys.path_hooks.remove(handle_url)
    sys.path_importer_cache.clear()
    warnings.warn('Removing handle_url', UserWarning)
