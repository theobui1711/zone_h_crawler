import json
import re
import warnings
import os
import sys
import logging
import pkgutil
import pkg_resources

import requests
import urllib3

urllib3.disable_warnings()

from bs4 import BeautifulSoup

from cybot.helper.settings import WAPPALYZER_DATA

logger = logging.getLogger(name=__name__)


class WappalyzerError(Exception):
    """
    Raised for fatal Wappalyzer errors.
    """
    pass


class WebPage(object):
    """
    Simple representation of a web page, decoupled
    from any particular HTTP library's API.
    """

    def __init__(self, url, timeout=None):
        """
        Initialize a new WebPage object.

        Parameters
        ----------

        url : str
            The web page URL.
        html : str
            The web page content (HTML)
        headers : dict
            The HTTP response headers
        """
        self.url = url
        self.response = requests.get(url, verify=False, timeout=timeout)
        self.responses = self.response.history + [self.response]
        self._parse_htmls()

    def _parse_htmls(self):
        """
        Parse the HTML with BeautifulSoup to find <script> and <meta> tags.
        """
        self.scripts = set()
        self.meta = []
        for r in self.responses:
            if r.text:
                try:
                    soup = BeautifulSoup(r.text, 'html.parser')
                except:
                    soup = BeautifulSoup(r.text.encode("utf-8").decode('ascii', 'ignore'), 'html.parser')
                self.scripts.update([script['src'] for script in soup.findAll('script', src=True)])
                self.meta.extend([{
                    meta['name'].lower(): meta['content']
                } for meta in soup.findAll('meta', attrs=dict(name=True, content=True))])


class Wappalyzer(object):
    """
    Python Wappalyzer driver.
    """

    def __init__(self, resource=None):
        if resource:
            with open(resource, 'r') as fd:
                obj = json.load(fd)
        else:
            with open(WAPPALYZER_DATA) as wd:
                obj = json.loads(wd.read())
        self.categories = obj['categories']
        self.apps = obj['apps']

        for name, app in self.apps.items():
            self._prepare_app(app)

    def _prepare_app(self, app):
        """
        Normalize app data, preparing it for the detection phase.
        """
        # Ensure these keys' values are lists
        for key in ['url', 'html', 'script', 'implies']:
            try:
                value = app[key]
            except KeyError:
                app[key] = []
            else:
                if not isinstance(value, list):
                    app[key] = [value]

        # Ensure these keys exist
        for key in ['headers', 'meta', 'cookies']:
            try:
                value = app[key]
            except KeyError:
                app[key] = {}

        # Ensure the 'meta' key is a dict
        obj = app['meta']
        if not isinstance(obj, dict):
            app['meta'] = {'generator': obj}

        # Ensure keys are lowercase
        for key in ['headers', 'meta']:
            obj = app[key]
            app[key] = {k.lower(): v for k, v in obj.items()}

        # Prepare regular expression patterns
        for key in ['url', 'html', 'script']:
            app[key] = [self._prepare_pattern(pattern) for pattern in app[key]]

        for key in ['headers', 'meta']:
            obj = app[key]
            for name, pattern in obj.items():
                obj[name] = self._prepare_pattern(obj[name])

    def _prepare_pattern(self, pattern):
        """
        Strip out key:value pairs from the pattern and compile the regular
        expression.
        """
        regex, _, sub_pattern = pattern.partition('\\;')
        try:
            r = re.compile(regex, re.I)
        except re.error as e:
            warnings.warn(
                "Caught '{error}' compiling regex: {regex}"
                    .format(error=e, regex=regex)
            )
            # regex that never matches:
            # http://stackoverflow.com/a/1845097/413622
            r = re.compile(r'(?!x)x'), version_pattern
        version_pattern = None
        for v in sub_pattern.split("\\;"):
            if "version:" in v:
                version_pattern = v.split(":")[1]
        return r, version_pattern

    def _has_app(self, app, webpage):
        """
        Determine whether the web page matches the app signature.
        """

        # Search the easiest things first and save the full-text search of the
        # HTML for last
        def get_version(search_pattern, version_pattern, content):
            if not version_pattern:
                return None
            if not search_pattern.startswith("^"):
                search_pattern = ".*?%s" % (search_pattern)
            if not search_pattern.endswith("$"):
                search_pattern = "%s.*" % (search_pattern)
            # print >> sys.stderr, search_pattern, version_pattern, content 
            try:
                return re.sub(search_pattern, version_pattern, content, flags=re.I)
            except:
                return None

        responses = webpage.response.history + [webpage.response]
        version = False
        # for regex, version_pattern in app['url']:
        #     match = regex.search(webpage.url)
        #     if match:
        #         version = get_version(regex.pattern, version_pattern, match.group(0))

        for r in responses:
            for name, (regex, version_pattern) in app['headers'].items():
                if name in r.headers:
                    content = r.headers[name]
                    match = regex.search(content)
                    if match:
                        version = version or get_version(regex.pattern, version_pattern, match.group(0))
            for c in app['cookies'].keys():
                if c in r.cookies.keys():
                    version = version or None
            for regex, version_pattern in app['html']:
                match = regex.search(r.text)
                if match:
                    version = version or get_version(regex.pattern, version_pattern, match.group(0))

        for regex, version_pattern in app['script']:
            for script in webpage.scripts:
                match = regex.search(script)
                if match:
                    version = version or get_version(regex.pattern, version_pattern, match.group(0))

        for name, (regex, version_pattern) in app['meta'].items():
            for m in webpage.meta:
                if name in m:
                    content = m[name]
                    match = regex.search(content)
                    if match:
                        version = version or get_version(regex.pattern, version_pattern, match.group(0))
        return version

    def _get_implied_apps(self, detected_apps):
        """
        Get the set of apps implied by `detected_apps`.
        """

        def __get_implied_apps(apps):
            _implied_apps = set()
            for app in apps:
                try:
                    _implied_apps.update(self.apps[app]['implies'])
                except KeyError:
                    pass
            return _implied_apps

        implied_apps = __get_implied_apps(detected_apps)
        all_implied_apps = set()

        # Descend recursively until we've found all implied apps
        while not all_implied_apps.issuperset(implied_apps):
            all_implied_apps.update(implied_apps)
            implied_apps = __get_implied_apps(all_implied_apps)

        return all_implied_apps

    def get_categories(self, app_name):
        """
        Returns a list of the categories for an app name.
        """
        cat_nums = self.apps.get(app_name, {}).get("cats", [])
        cat_names = [self.categories.get("%s" % cat_num, "")["cname"]
                     for cat_num in cat_nums]

        return cat_names

    def analyze(self, webpage):
        """
        Return a list of applications that can be detected on the web page.
        """
        detected_apps = {}

        for app_name, app in self.apps.items():
            cat_names = self.get_categories(app_name)
            result = self._has_app(app, webpage)
            if result is not False:
                detected_apps[app_name] = result
                for a in self._get_implied_apps([app_name]):
                    if a not in detected_apps:
                        detected_apps[a] = None
        return detected_apps

    def analyze_with_categories(self, webpage):
        detected_apps = self.analyze(webpage)
        categorised_apps = {}

        for app_name, version in detected_apps.items():
            cat_names = self.get_categories(app_name)
            for c in cat_names:
                if c not in categorised_apps:
                    categorised_apps[c] = []
                categorised_apps[c].append({"name": app_name, "version": version})
        return categorised_apps


# wappalyzer = Wappalyzer()
#
# def get_tech(url):
#     data = dict()
#     try:
#         p = WebPage(url=url, timeout=20)
#     except Exception as e:
#         tech = {"error": str(e)}
#     else:
#         tech = wappalyzer.analyze_with_categories(p)
#     data["tech"] = tech
#     data["address"] = url
#     return data

# WAPPALYZER_DATA_URL = 'https://raw.githubusercontent.com/AliasIO/Wappalyzer/master/src/apps.json'

# r = requests.get(WAPPALYZER_DATA_URL).json()
# for i in r['categories']:
#     r['categories'][i]['cname'] = (r['categories'][i]['name'].lower().replace(' ', '_'))
#
# with open(WAPPALYZER_DATA, 'w') as f:
#     f.write(json.dumps(r))
