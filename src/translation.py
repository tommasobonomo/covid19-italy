import yaml
from cachetools import cached, TTLCache
cache = TTLCache(maxsize=10, ttl=86400)

@cached(cache)
class Languages:
  lang_mapping = {}
  def __init__(self):
    with open("translations/lang_mapping.yml", 'r') as yml_mapping_file:
      self.lang_mapping = yaml.safe_load(yml_mapping_file)

  def __dict__(self):
    return self.lang_mapping

  def locale(self, attr: str):
    return self.lang_mapping[attr]

  def get_array(self):
    return [*self.lang_mapping.keys()]

@cached(cache)
class Translate:
  strings = {}
  def __init__(self, language: str = "English"):
    lang = Languages()
    loc = lang.locale(language)
    try:
      with open("translations/%s.yml" % loc, 'r') as yml_file:
        self.strings = yaml.safe_load(yml_file)
    except IOError:
      with open("translations/it.yml", 'r') as yml_file:
        self.strings = yaml.safe_load(yml_file)

  def __getattr__(self, string: str):
    if string == "loc":
      return self.loc
    if string == "lang":
      return self.lang
    return self.strings.get(string, f"{string}")

  def get(self, string: str):
    return self.strings.get(string, f"{string}")