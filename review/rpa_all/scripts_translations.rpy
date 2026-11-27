init -200 python:
    import json
    
    class Languages(python_dict):
        @property
        def current(self):
            if _preferences.language in self:
                return self[_preferences.language]
            return self[None]


    class LanguageData:
        def __init__(self, name, font, what_prefix='"', what_suffix='"'):
            self.name = name
            self.font = font
            self.what_prefix = what_prefix
            self.what_suffix = what_suffix


    def LoadTranslations():
        ## Create English language information
        rv = Languages()
        rv[None] = LanguageData(
            name="English",
            font=""
        )

        ## Load other languages from folders
        tl_path = os.path.join(renpy.config.gamedir, "tl") 
        if not os.path.exists(tl_path):
            return rv
        
        lang_codes = os.listdir(tl_path)

        for lang_code in lang_codes:
            path = os.path.join(tl_path, lang_code)
            details_path = os.path.join(path, "details.json")
            if not os.path.exists(details_path):
                print("details.json not found for language '{}'".format(lang_code))
                continue
            
            with open(details_path, 'rb') as file:
                details = json.loads(file.read().decode('utf8'))
            
            rv[lang_code] = LanguageData(**details)
        
        return rv
    
    store.languages = LoadTranslations()