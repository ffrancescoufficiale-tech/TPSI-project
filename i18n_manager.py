"""
i18n_manager.py — Gestione traduzioni (singleton).
Metti questo file nella stessa cartella di main.py.
La cartella locales/ deve stare accanto a questo file.
"""
import json
from pathlib import Path

LOCALES_DIR      = Path(__file__).parent / "locales"
DEFAULT_LOCALE   = "it"
SUPPORTED_LOCALES = ["it", "en"]


class I18nManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._locale  = DEFAULT_LOCALE
            cls._instance._strings = {}
        return cls._instance

    def set_locale(self, locale: str) -> None:
        if locale not in SUPPORTED_LOCALES:
            raise ValueError(f"Locale '{locale}' non supportato.")
        self._locale = locale
        path = LOCALES_DIR / f"{locale}.json"
        with path.open(encoding="utf-8") as f:
            self._strings = json.load(f)

    def t(self, key: str, **kwargs) -> str:
        """Traduce una chiave con interpolazione opzionale: t('ris_corrette', corrette=3, totale=5)"""
        if not self._strings:
            self.set_locale(self._locale)
        template = self._strings.get(key, f"[{key}]")
        return template.format(**kwargs) if kwargs else template

    @property
    def current_locale(self) -> str:
        return self._locale


# Istanza globale — importa questa nei tuoi file
i18n = I18nManager()
i18n.set_locale(DEFAULT_LOCALE)