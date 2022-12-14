from dataclasses import dataclass
from dataclasses import field
from functools import cache


@dataclass
class Lang:
    # locale id = 1024 * sub_language id  +  primary language id. en_US -> sub lang _ prim lang
    locale_id: int
    description: str
    letter_code: str
    charset: str  # must be same len as english chars_en in model.keyboard to work
    aliases: list[str] | None = None
    sub_lang_id: int = field(init=False)
    primary_lang_id: int = field(init=False)

    def __post_init__(self) -> None:
        self.sub_lang_id = self.locale_id % 1024
        self.primary_lang_id = self.locale_id // 1024


"""
Look up the language, if it has emtpy string as last argument - it isn't implemented yet.
It's very easy to contribute a language, read the docs.
"""
languages: list[Lang] = [
    Lang(1025, "Arabic - Saudi Arabia", "ar-SA", ""),
    Lang(1026, "Bulgarian", "bg-BG", ""),
    Lang(1027, "Catalan", "ca-ES", ""),
    Lang(1028, "Chinese - Taiwan", "zh-TW", ""),
    Lang(1029, "Czech", "cs-CZ", ""),
    Lang(1030, "Danish", "da-DK", ""),
    Lang(1031, "German - Germany", "de-DE", ""),
    Lang(1032, "Greek", "el-GR", ""),
    Lang(
        1033,
        "English - United States",
        "en-US",
        "`1234567890-=qwertyuiop[]\\asdfghjkl;'zxcvbnm,./~!@#$%^&*()_+QWERTYUIOP{}|ASDFGHJKL:\"ZXCVBNM<>?",
        ["en"],
    ),
    Lang(
        1034,
        "Spanish - Spain (Traditional Sort)",
        "es-ES",
        "ñ1234567890-+qwertyuiop'¡ºasdfghjkl`´zxcvbnm,.çÑ!\"·$%&/()=_*QWERTYUIOP?¿ªASDFGHJKL^¨ZXCVBNM;:Ç",
        ["es"],
    ),
    Lang(1035, "Finnish", "fi-FI", ""),
    Lang(1036, "French - France", "fr-FR", ""),
    Lang(1037, "Hebrew", "he-IL", ""),
    Lang(1038, "Hungarian", "hu-HU", ""),
    Lang(1039, "Icelandic", "is-IS", ""),
    Lang(1040, "Italian - Italy", "it-IT", ""),
    Lang(1041, "Japanese", "ja-JP", ""),
    Lang(1042, "Korean", "ko-KR", ""),
    Lang(1043, "Dutch - Netherlands", "nl-NL", ""),
    Lang(1044, "Norwegian (Bokmål)", "nb-NO", ""),
    Lang(1045, "Polish", "pl-PL", ""),
    Lang(
        1046,
        "Portuguese - Brazil",
        "pt-BR",
        "'1234567890-=qwertyuiop´[]asdfghjklç~zxcvbnm,.;\"!@#$%¨&*()_+QWERTYUIOP`{}ASDFGHJKLÇ^ZXCVBNM<>:",
    ),
    Lang(1047, "Rhaeto-Romanic", "rm-CH", ""),
    Lang(1048, "Romanian", "ro-RO", ""),
    Lang(
        1049,
        "Russian",
        "ru-RU",
        'ё1234567890-=йцукенгшщзхъ\\фывапролджэячсмитьбю.Ё!"№;%:?*()_+ЙЦУКЕНГШЩЗХЪ/ФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,',
        ["ru"],
    ),
    Lang(1050, "Croatian", "hr-HR", ""),
    Lang(1051, "Slovak", "sk-SK", ""),
    Lang(1052, "Albanian - Albania", "sq-AL", ""),
    Lang(1053, "Swedish", "sv-SE", ""),
    Lang(1054, "Thai", "th-TH", ""),
    Lang(1055, "Turkish", "tr-TR", ""),
    Lang(1056, "Urdu - Pakistan", "ur-PK", ""),
    Lang(1057, "Indonesian", "id-ID", ""),
    Lang(
        1058,
        "Ukrainian",
        "uk-UA",
        "'1234567890-=йцукенгшщзхї\\фівапролджєячсмитьбю.₴!\"№;%:?*()_+ЙЦУКЕНГШЩЗХЇ/ФІВАПРОЛДЖЄЯЧСМИТЬБЮ,",
        ["ua"],
    ),
    Lang(1059, "Belarusian", "be-BY", ""),
    Lang(1060, "Slovenian", "sl-SI", ""),
    Lang(1061, "Estonian", "et-EE", ""),
    Lang(1062, "Latvian", "lv-LV", ""),
    Lang(1063, "Lithuanian", "lt-LT", ""),
    Lang(1064, "Tajik", "tg-Cyrl-TJ", ""),
    Lang(1065, "Persian", "fa-IR", ""),
    Lang(1066, "Vietnamese", "vi-VN", ""),
    Lang(1067, "Armenian - Armenia", "hy-AM", ""),
    Lang(1068, "Azeri (Latin)", "az-Latn-AZ", ""),
    Lang(1069, "Basque", "eu-ES", ""),
    Lang(1070, "Sorbian", "wen-DE", ""),
    Lang(1071, "F.Y.R.O. Macedonian", "mk-MK", ""),
    Lang(1072, "Sutu", "st-ZA", ""),
    Lang(1073, "Tsonga", "ts-ZA", ""),
    Lang(1074, "Tswana", "tn-ZA", ""),
    Lang(1075, "Venda", "ven-ZA", ""),
    Lang(1076, "Xhosa", "xh-ZA", ""),
    Lang(1077, "Zulu", "zu-ZA", ""),
    Lang(1078, "Afrikaans - South Africa", "af-ZA", ""),
    Lang(1079, "Georgian", "ka-GE", ""),
    Lang(1080, "Faroese", "fo-FO", ""),
    Lang(1081, "Hindi", "hi-IN", ""),
    Lang(1082, "Maltese", "mt-MT", ""),
    Lang(1083, "Sami", "se-NO", ""),
    Lang(1084, "Gaelic (Scotland)", "gd-GB", ""),
    Lang(1085, "Yiddish", "yi", ""),
    Lang(1086, "Malay - Malaysia", "ms-MY", ""),
    Lang(1087, "Kazakh", "kk-KZ", ""),
    Lang(1088, "Kyrgyz (Cyrillic)", "ky-KG", ""),
    Lang(1089, "Swahili", "sw-KE", ""),
    Lang(1090, "Turkmen", "tk-TM", ""),
    Lang(1091, "Uzbek (Latin)", "uz-Latn-UZ", ""),
    Lang(1092, "Tatar", "tt-RU", ""),
    Lang(1093, "Bengali (India)", "bn-IN", ""),
    Lang(1094, "Punjabi", "pa-IN", ""),
    Lang(1095, "Gujarati", "gu-IN", ""),
    Lang(1096, "Oriya", "or-IN", ""),
    Lang(1097, "Tamil", "ta-IN", ""),
    Lang(1098, "Telugu", "te-IN", ""),
    Lang(1099, "Kannada", "kn-IN", ""),
    Lang(1100, "Malayalam", "ml-IN", ""),
    Lang(1101, "Assamese", "as-IN", ""),
    Lang(1102, "Marathi", "mr-IN", ""),
    Lang(1103, "Sanskrit", "sa-IN", ""),
    Lang(1104, "Mongolian (Cyrillic)", "mn-MN", ""),
    Lang(1105, "Tibetan - People's Republic of China", "bo-CN", ""),
    Lang(1106, "Welsh", "cy-GB", ""),
    Lang(1107, "Khmer", "km-KH", ""),
    Lang(1108, "Lao", "lo-LA", ""),
    Lang(1109, "Burmese", "my-MM", ""),
    Lang(1110, "Galician", "gl-ES", ""),
    Lang(1111, "Konkani", "kok-IN", ""),
    Lang(1112, "Manipuri", "mni", ""),
    Lang(1113, "Sindhi - India", "sd-IN", ""),
    Lang(1114, "Syriac", "syr-SY", ""),
    Lang(1115, "Sinhalese - Sri Lanka", "si-LK", ""),
    Lang(1116, "Cherokee - United States", "chr-US", ""),
    Lang(1117, "Inuktitut", "iu-Cans-CA", ""),
    Lang(1118, "Amharic - Ethiopia", "am-ET", ""),
    Lang(1119, "Tamazight (Arabic)", "tmz", ""),
    Lang(1120, "Kashmiri (Arabic)", "ks-Arab-IN", ""),
    Lang(1121, "Nepali", "ne-NP", ""),
    Lang(1122, "Frisian - Netherlands", "fy-NL", ""),
    Lang(1123, "Pashto", "ps-AF", ""),
    Lang(1124, "Filipino", "fil-PH", ""),
    Lang(1125, "Divehi", "dv-MV", ""),
    Lang(1126, "Edo", "bin-NG", ""),
    Lang(1127, "Fulfulde - Nigeria", "fuv-NG", ""),
    Lang(1128, "Hausa - Nigeria", "ha-Latn-NG", ""),
    Lang(1129, "Ibibio - Nigeria", "ibb-NG", ""),
    Lang(1130, "Yoruba", "yo-NG", ""),
    Lang(1131, "Quecha - Bolivia", "quz-BO", ""),
    Lang(1132, "Sepedi", "nso-ZA", ""),
    Lang(1136, "Igbo - Nigeria", "ig-NG", ""),
    Lang(1137, "Kanuri - Nigeria", "kr-NG", ""),
    Lang(1138, "Oromo", "gaz-ET", ""),
    Lang(1139, "Tigrigna - Ethiopia", "ti-ER", ""),
    Lang(1140, "Guarani - Paraguay", "gn-PY", ""),
    Lang(1141, "Hawaiian - United States", "haw-US", ""),
    Lang(1142, "Latin", "la", ""),
    Lang(1143, "Somali", "so-SO", ""),
    Lang(1144, "Yi", "ii-CN", ""),
    Lang(1145, "Papiamentu", "pap-AN", ""),
    Lang(1152, "Uighur - China", "ug-Arab-CN", ""),
    Lang(1153, "Maori - New Zealand", "mi-NZ", ""),
    Lang(2049, "Arabic - Iraq", "ar-IQ", ""),
    Lang(2052, "Chinese - People's Republic of China", "zh-CN", ""),
    Lang(2055, "German - Switzerland", "de-CH", ""),
    Lang(2057, "English - United Kingdom", "en-GB", ""),
    Lang(2058, "Spanish - Mexico", "es-MX", ""),
    Lang(2060, "French - Belgium", "fr-BE", ""),
    Lang(2064, "Italian - Switzerland", "it-CH", ""),
    Lang(2067, "Dutch - Belgium", "nl-BE", ""),
    Lang(2068, "Norwegian (Nynorsk)", "nn-NO", ""),
    Lang(2070, "Portuguese - Portugal", "pt-PT", ""),
    Lang(2072, "Romanian - Moldava", "ro-MD", ""),
    Lang(2073, "Russian - Moldava", "ru-MD", ""),
    Lang(2074, "Serbian (Latin)", "sr-Latn-CS", ""),
    Lang(2077, "Swedish - Finland", "sv-FI", ""),
    Lang(2080, "Urdu - India", "ur-IN", ""),
    Lang(2092, "Azeri (Cyrillic)", "az-Cyrl-AZ", ""),
    Lang(2108, "Gaelic (Ireland)", "ga-IE", ""),
    Lang(2110, "Malay - Brunei Darussalam", "ms-BN", ""),
    Lang(2115, "Uzbek (Cyrillic)", "uz-Cyrl-UZ", ""),
    Lang(2117, "Bengali (Bangladesh)", "bn-BD", ""),
    Lang(2118, "Punjabi (Pakistan)", "pa-PK", ""),
    Lang(2128, "Mongolian (Mongolian)", "mn-Mong-CN", ""),
    Lang(2129, "Tibetan - Bhutan", "bo-BT", ""),
    Lang(2137, "Sindhi - Pakistan", "sd-PK", ""),
    Lang(2143, "Tamazight (Latin)", "tzm-Latn-DZ", ""),
    Lang(2144, "Kashmiri (Devanagari)", "ks-Deva-IN", ""),
    Lang(2145, "Nepali - India", "ne-IN", ""),
    Lang(2155, "Quecha - Ecuador", "quz-EC", ""),
    Lang(2163, "Tigrigna - Eritrea", "ti-ET", ""),
    Lang(3073, "Arabic - Egypt", "ar-EG", ""),
    Lang(3076, "Chinese - Hong Kong SAR", "zh-HK", ""),
    Lang(3079, "German - Austria", "de-AT", ""),
    Lang(3081, "English - Australia", "en-AU", ""),
    Lang(3082, "Spanish - Spain (Modern Sort)", "es-ESM", ""),
    Lang(3084, "French - Canada", "fr-CA", ""),
    Lang(3098, "Serbian (Cyrillic)", "sr-Cyrl-CS", ""),
    Lang(3179, "Quecha - Peru", "quz-PE", ""),
    Lang(4097, "Arabic - Libya", "ar-LY", ""),
    Lang(4100, "Chinese - Singapore", "zh-SG", ""),
    Lang(4103, "German - Luxembourg", "de-LU", ""),
    Lang(4105, "English - Canada", "en-CA", ""),
    Lang(4106, "Spanish - Guatemala", "es-GT", ""),
    Lang(4108, "French - Switzerland", "fr-CH", ""),
    Lang(4122, "Croatian (Bosnia/Herzegovina)", "hr-BA", ""),
    Lang(5121, "Arabic - Algeria", "ar-DZ", ""),
    Lang(5124, "Chinese - Macao SAR", "zh-MO", ""),
    Lang(5127, "German - Liechtenstein", "de-LI", ""),
    Lang(5129, "English - New Zealand", "en-NZ", ""),
    Lang(5130, "Spanish - Costa Rica", "es-CR", ""),
    Lang(5132, "French - Luxembourg", "fr-LU", ""),
    Lang(5146, "Bosnian (Bosnia/Herzegovina)", "bs-Latn-BA", ""),
    Lang(6145, "Arabic - Morocco", "ar-MO", ""),
    Lang(6153, "English - Ireland", "en-IE", ""),
    Lang(6154, "Spanish - Panama", "es-PA", ""),
    Lang(6156, "French - Monaco", "fr-MC", ""),
    Lang(7169, "Arabic - Tunisia", "ar-TN", ""),
    Lang(7177, "English - South Africa", "en-ZA", ""),
    Lang(7178, "Spanish - Dominican Republic", "es-DO", ""),
    Lang(7180, "French - West Indies", "fr-029", ""),
    Lang(8193, "Arabic - Oman", "ar-OM", ""),
    Lang(8201, "English - Jamaica", "en-JM", ""),
    Lang(8202, "Spanish - Venezuela", "es-VE", ""),
    Lang(8204, "French - Reunion", "fr-RE", ""),
    Lang(9217, "Arabic - Yemen", "ar-YE", ""),
    Lang(9225, "English - Caribbean", "en-029", ""),
    Lang(9226, "Spanish - Colombia", "es-CO", ""),
    Lang(9228, "French - Democratic Rep. of Congo", "fr-CG", ""),
    Lang(10241, "Arabic - Syria", "ar-SY", ""),
    Lang(10249, "English - Belize", "en-BZ", ""),
    Lang(10250, "Spanish - Peru", "es-PE", ""),
    Lang(10252, "French - Senegal", "fr-SN", ""),
    Lang(11265, "Arabic - Jordan", "ar-JO", ""),
    Lang(11273, "English - Trinidad", "en-TT", ""),
    Lang(11274, "Spanish - Argentina", "es-AR", ""),
    Lang(11276, "French - Cameroon", "fr-CM", ""),
    Lang(12289, "Arabic - Lebanon", "ar-LB", ""),
    Lang(12297, "English - Zimbabwe", "en-ZW", ""),
    Lang(12298, "Spanish - Ecuador", "es-EC", ""),
    Lang(12300, "French - Cote d'Ivoire", "fr-CI", ""),
    Lang(13313, "Arabic - Kuwait", "ar-KW", ""),
    Lang(13321, "English - Philippines", "en-PH", ""),
    Lang(13322, "Spanish - Chile", "es-CL", ""),
    Lang(13324, "French - Mali", "fr-ML", ""),
    Lang(14337, "Arabic - U.A.E.", "ar-AE", ""),
    Lang(14345, "English - Indonesia", "en-ID", ""),
    Lang(14346, "Spanish - Uruguay", "es-UY", ""),
    Lang(14348, "French - Morocco", "fr-MA", ""),
    Lang(15361, "Arabic - Bahrain", "ar-BH", ""),
    Lang(15369, "English - Hong Kong SAR", "en-HK", ""),
    Lang(15370, "Spanish - Paraguay", "es-PY", ""),
    Lang(15372, "French - Haiti", "fr-HT", ""),
    Lang(16385, "Arabic - Qatar", "ar-QA", ""),
    Lang(16393, "English - India", "en-IN", ""),
    Lang(16394, "Spanish - Bolivia", "es-BO", ""),
    Lang(17417, "English - Malaysia", "en-MY", ""),
    Lang(17418, "Spanish - El Salvador", "es-SV", ""),
    Lang(18441, "English - Singapore", "en-SG", ""),
    Lang(18442, "Spanish - Honduras", "es-HN", ""),
    Lang(19466, "Spanish - Nicaragua", "es-NI", ""),
    Lang(20490, "Spanish - Puerto Rico", "es-PR", ""),
    Lang(21514, "Spanish - United States", "es-US", ""),
    Lang(58378, "Spanish - Latin America", "es-419", ""),
    Lang(58380, "French - North Africa", "fr-015", ""),
]

languages_by_letter_code: dict[str, Lang] = {}
for lang in languages:
    if not lang.charset:
        continue
    languages_by_letter_code[lang.letter_code] = lang
    if lang.aliases:
        for alias in lang.aliases:
            languages_by_letter_code[alias] = lang

languages_by_locale = {lang.locale_id: lang for lang in languages if lang.charset}


@cache
def get(lang_in: str | int | Lang) -> Lang:
    if isinstance(lang_in, Lang):
        return lang_in
    elif isinstance(lang_in, str):
        try:
            return languages_by_letter_code[lang_in]
        except KeyError:
            for ln in languages:
                if lang_in.casefold() in ln.description.partition(" - ")[0].casefold():
                    return ln
            raise KeyError(
                f"Language not found: {lang_in}. "
                f"Support for it may be not implemented, or typo. See tapper.model.languages"
            )
    elif isinstance(lang_in, int):
        return languages_by_locale[lang_in]
    else:
        raise TypeError
