import flet as ft
import asyncio
import json
import threading
import time
from pathlib import Path
from datetime import datetime
from logic import genera_quiz
from i18n_manager import i18n

# ── PALETTE ───────────────────────────────────────────────────────────────────
BG      = "#090C14"
SURFACE = "#0F1420"
CARD    = "#131928"
BORDER  = "#1E2840"
ACCENT  = "#00C8FF"
ACCENT2 = "#7B4FFF"
GOLD    = "#F5C842"
TEXT    = "#E8EAF6"
DIM     = "#5A6380"
SUCCESS = "#00E676"
ERROR   = "#FF5252"
WHITE   = "#FFFFFF"
WARN    = "#FF9800"
LETTERE = ["A", "B", "C", "D"]
COLORI  = {"A": "#00C8FF", "B": "#7B4FFF", "C": "#F5C842", "D": "#00E676"}

CRONOLOGIA_FILE = Path(__file__).parent / "cronologia.json"

# ── CRONOLOGIA HELPERS ────────────────────────────────────────────────────────
def load_cronologia():
    if CRONOLOGIA_FILE.exists():
        with CRONOLOGIA_FILE.open(encoding="utf-8") as f:
            return json.load(f)
    return []

def save_to_cronologia(entry: dict):
    storia = load_cronologia()
    storia.insert(0, entry)
    with CRONOLOGIA_FILE.open("w", encoding="utf-8") as f:
        json.dump(storia, f, ensure_ascii=False, indent=2)

def clear_cronologia():
    if CRONOLOGIA_FILE.exists():
        CRONOLOGIA_FILE.unlink()

# ── WIDGET HELPERS ─────────────────────────────────────────────────────────────

def filled_btn(text, color_bg, color_text, on_click, width=None):
    b = ft.FilledButton(
        content=ft.Text(text, size=14, weight=ft.FontWeight.BOLD, color=color_text),
        style=ft.ButtonStyle(
            bgcolor={ft.ControlState.DEFAULT: color_bg},
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=ft.Padding.symmetric(horizontal=24, vertical=14),
        ),
        on_click=on_click,
        height=48,
    )
    if width: b.width = width
    return b

def card(content, border_color=None, padding=20):
    return ft.Container(
        content=content,
        bgcolor=CARD,
        border=ft.Border.all(1, border_color or BORDER),
        border_radius=12,
        padding=padding,
        margin=ft.Margin(0, 8, 0, 8),
    )

def lbl(txt, size=11, color=None, bold=False):
    return ft.Text(txt, size=size, color=color or DIM,
                   weight=ft.FontWeight.BOLD if bold else ft.FontWeight.NORMAL)

def tok_badge(label_txt, value, color):
    return ft.Container(
        ft.Column([
            lbl(label_txt, bold=True, color=DIM),
            ft.Text(value, size=20, color=color, weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2, tight=True),
        bgcolor=SURFACE, border=ft.Border.all(1, color), border_radius=10,
        padding=ft.Padding.symmetric(vertical=10, horizontal=16),
    )

def make_field(hint, value="", width=None, expand=False):
    f = ft.TextField(
        hint_text=hint,
        hint_style=ft.TextStyle(color=DIM, size=13),
        text_style=ft.TextStyle(color=WHITE, size=14),
        border_color=BORDER,
        focused_border_color=ACCENT,
        cursor_color=ACCENT,
        bgcolor=SURFACE,
        border_radius=10,
        content_padding=ft.Padding.symmetric(horizontal=16, vertical=14),
        value=value,
        expand=expand,
    )
    if width: f.width = width
    return f

def lang_switcher(on_change):
    return ft.Dropdown(
        value=i18n.current_locale,
        options=[
            ft.dropdown.Option("it", i18n.t("lang_it")),
            ft.dropdown.Option("en", i18n.t("lang_en")),
        ],
        width=180,
        bgcolor=SURFACE,
        color=TEXT,
        border_color=BORDER,
        focused_border_color=ACCENT,
        border_radius=8,
        on_select=lambda e: on_change(e.control.value),
    )


# ══════════════════════════════════════════════════════════════════════════════
def main(page: ft.Page):
    page.title         = i18n.t("app_title")
    page.bgcolor       = BG
    page.padding       = 30
    page.scroll        = ft.ScrollMode.AUTO
    page.window.width  = 820
    page.window.height = 750
    page.window.resizable = True

    state = {
        "domande": [], "risposte": {}, "corrente": 0,
        "modalita": None, "tokens": None,
        "timer_sec": 0, "_timer_task": None,
    }

    main_col = ft.Column(spacing=0, expand=True)

    # ── Timer helpers ────────────────────────────────────────────────────────
    def stop_timer():
        task = state.get("_timer_task")
        if task is not None:
            task.cancel()
        state["_timer_task"] = None

    def render(controls):
        stop_timer()
        main_col.controls = controls
        page.update()

    # ── Cambio lingua globale ────────────────────────────────────────────────
    def on_lang_change(locale: str):
        i18n.set_locale(locale)
        page.title = i18n.t("app_title")
        show_home()

    # ══════════════════════════════════════════════════════════════════════════
    # SCHERMATA 0 — HOME
    # ══════════════════════════════════════════════════════════════════════════
    def show_home():
        render([
            # Header
            ft.Container(
                ft.Row([
                    ft.Text("◈", size=26, color=ACCENT),
                    ft.Column([
                        ft.Text(i18n.t("app_title"), size=24, color=WHITE, weight=ft.FontWeight.BOLD),
                        lbl(i18n.t("app_subtitle"), size=12),
                        
                    ], spacing=2, tight=True),
                    ft.Container(expand=True),
                    lang_switcher(on_lang_change),
                ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.Padding.symmetric(horizontal=0, vertical=4),
                border=ft.Border(bottom=ft.BorderSide(1, BORDER)),
                margin=ft.Margin(0, 0, 0, 40),
            ),
            # Hero
            ft.Container(
                ft.Column([
                    ft.Text("🧠", size=72, text_align=ft.TextAlign.CENTER),
                    ft.Container(height=12),
                    ft.Text(i18n.t("home_welcome"), size=30, color=WHITE,
                            weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    ft.Container(height=8),
                    lbl(i18n.t("home_sub"), size=14, color=DIM),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                alignment=ft.Alignment(0, 0),
                margin=ft.Margin(0, 0, 0, 40),
            ),
            # Bottoni
            ft.Container(
                ft.Column([
                    filled_btn(i18n.t("home_btn_quiz"),        ACCENT,  BG,   lambda e: show_form(),       width=300),
                    ft.Container(height=12),
                    filled_btn(i18n.t("home_btn_cronologia"),  SURFACE, TEXT, lambda e: show_cronologia(), width=300),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                alignment=ft.Alignment(0, 0),
            ),
            ft.Container(
                ft.Column([
                    ft.Container(height=50),
                    ft.Text(i18n.t("avviso_ai"), size=12, color=DIM, text_align=ft.TextAlign.CENTER),
                ])
            )
        ])

    # ══════════════════════════════════════════════════════════════════════════
    # SCHERMATA 1 — FORM
    # ══════════════════════════════════════════════════════════════════════════
    inp_argomento  = make_field(i18n.t("hint_argomento"), expand=True)
    inp_difficolta = make_field(i18n.t("hint_difficolta"), width=180)
    inp_numero     = make_field(i18n.t("hint_numero"),     value="5",  width=100)
    inp_timer      = make_field(i18n.t("timer_hint"),      value="0",  width=100)
    status_lbl     = ft.Text("", size=12, color=DIM, text_align=ft.TextAlign.CENTER)
    spinner        = ft.ProgressRing(color=ACCENT, stroke_width=3, width=26, height=26, visible=False)
    btn_genera     = filled_btn(i18n.t("btn_genera"), ACCENT, BG, None)

    def on_genera(e):
        argomento  = inp_argomento.value.strip()
        difficolta = inp_difficolta.value.strip() or "Medio"
        try:    n = max(1, min(10, int(inp_numero.value.strip())))
        except: n = 5
        try:    timer_sec = max(0, int(inp_timer.value.strip()))
        except: timer_sec = 0

        if not argomento:
            status_lbl.value = i18n.t("err_argomento")
            status_lbl.color = ERROR
            page.update(); return

        btn_genera.disabled = True
        spinner.visible     = True
        status_lbl.value    = i18n.t("genera_loading")
        status_lbl.color    = DIM
        page.update()

        try:
            data = genera_quiz(argomento, difficolta, n, lingua=i18n.current_locale)
            state.update({
                "domande":    data["domande"],
                "risposte":   {},
                "corrente":   0,
                "tokens":     data.get("tokens"),
                "argomento":  argomento,
                "difficolta": difficolta,
                "timer_sec":  timer_sec,
            })
            show_modalita()
        except Exception as ex:
            status_lbl.value = f"✗  {ex}"
            status_lbl.color = ERROR
        finally:
            btn_genera.disabled = False
            spinner.visible     = False
            page.update()

    btn_genera.on_click = on_genera

    def show_form():
        inp_argomento.hint_text  = i18n.t("hint_argomento")
        inp_difficolta.hint_text = i18n.t("hint_difficolta")
        inp_numero.hint_text     = i18n.t("hint_numero")
        inp_timer.hint_text      = i18n.t("timer_hint")
        btn_genera.content       = ft.Text(i18n.t("btn_genera"), size=14,
                                           weight=ft.FontWeight.BOLD, color=BG)
        render([
            ft.Container(
                ft.Row([
                    ft.Text("◈", size=26, color=ACCENT),
                    ft.Column([
                        ft.Text(i18n.t("app_title"), size=24, color=WHITE, weight=ft.FontWeight.BOLD),
                        lbl(i18n.t("app_subtitle"), size=12),
                    ], spacing=2, tight=True),
                    ft.Container(expand=True),
                    lang_switcher(on_lang_change),
                ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.Padding.symmetric(horizontal=0, vertical=4),
                border=ft.Border(bottom=ft.BorderSide(1, BORDER)),
                margin=ft.Margin(0, 0, 0, 20),
            ),
            ft.Row([
                ft.TextButton(i18n.t("btn_indietro"), on_click=lambda e: show_home(),
                              style=ft.ButtonStyle(color={ft.ControlState.DEFAULT: DIM})),
            ]),
            card(ft.Column([
                lbl(i18n.t("form_title"), bold=True),
                ft.Container(height=12),
                lbl(i18n.t("label_argomento"), size=12),
                ft.Container(height=4),
                inp_argomento,
                ft.Container(height=12),
                ft.Row([
                    ft.Column([lbl(i18n.t("label_difficolta"),  size=12), ft.Container(height=4), inp_difficolta], spacing=0),
                    ft.Column([lbl(i18n.t("label_num_domande"), size=12), ft.Container(height=4), inp_numero],    spacing=0),
                    ft.Column([lbl(i18n.t("label_timer"),       size=12), ft.Container(height=4), inp_timer],     spacing=0),
                ], spacing=16),
                ft.Container(height=20),
                ft.Row([spinner, btn_genera],
                       alignment=ft.MainAxisAlignment.CENTER,
                       vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                ft.Container(height=4),
                status_lbl,
            ], spacing=0), padding=24),
        ])

    # ══════════════════════════════════════════════════════════════════════════
    # SCHERMATA 2 — MODALITÀ
    # ══════════════════════════════════════════════════════════════════════════
    def show_modalita():
        n    = len(state["domande"])
        arg  = state.get("argomento", "")
        diff = state.get("difficolta", "")

        def scegli(m):
            state["modalita"] = m
            state["risposte"] = {}
            state["corrente"] = 0
            show_quiz()

        render([
            ft.Row([
                ft.TextButton(i18n.t("btn_indietro"), on_click=lambda e: show_form(),
                              style=ft.ButtonStyle(color={ft.ControlState.DEFAULT: DIM})),
                ft.Container(expand=True),
                lang_switcher(on_lang_change),
            ]),
            ft.Container(height=10),
            ft.Text("Quiz Pronto! 🎉", size=26, color=WHITE, weight=ft.FontWeight.BOLD),
            ft.Text(i18n.t("modal_subtitle", n=n, arg=arg, diff=diff), size=13, color=DIM),
            ft.Container(height=24),
            lbl(i18n.t("modal_title"), bold=True),
            ft.Container(height=12),

            card(ft.Column([
                ft.Row([
                    ft.Text("🎮", size=32),
                    ft.Column([
                        ft.Text(i18n.t("modal_interattiva"), size=16, color=WHITE, weight=ft.FontWeight.BOLD),
                        lbl(i18n.t("modal_interattiva_sub"), size=12),
                    ], spacing=4, expand=True),
                ], spacing=16, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(height=14),
                filled_btn("Gioca!" if i18n.current_locale == "it" else "Play!", ACCENT, BG, lambda e: scegli("interattiva")),
            ], spacing=0), border_color=ACCENT),

            ft.Container(height=8),

            card(ft.Column([
                ft.Row([
                    ft.Text("📖", size=32),
                    ft.Column([
                        ft.Text(i18n.t("modal_visualizza"), size=16, color=WHITE, weight=ft.FontWeight.BOLD),
                        lbl(i18n.t("modal_visualizza_sub"), size=12),
                    ], spacing=4, expand=True),
                ], spacing=16, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(height=14),
                filled_btn(
                    "Visualizza" if i18n.current_locale == "it" else "Browse",
                    ACCENT2, WHITE, lambda e: scegli("visualizza")
                ),
            ], spacing=0), border_color=ACCENT2),
        ])

    # ══════════════════════════════════════════════════════════════════════════
    # SCHERMATA 3 — QUIZ
    # ══════════════════════════════════════════════════════════════════════════
    def show_quiz():
        if state["modalita"] == "interattiva":
            show_interattiva()
        else:
            show_visualizza()

    def show_interattiva():
        stop_timer()

        domande   = state["domande"]
        idx       = state["corrente"]
        d         = domande[idx]
        n_tot     = len(domande)
        sel       = state["risposte"].get(idx)
        confirmed = sel is not None
        timer_sec = state["timer_sec"]

        timer_ref = ft.Ref[ft.Text]()

        opzioni = []
        for lettera in LETTERE:
            testo = d["opzioni"].get(lettera, "")
            if not testo: continue

            is_sel      = sel == lettera
            is_corretta = lettera == d["corretta"]

            if confirmed:
                if is_corretta:  border_c, bg_c = SUCCESS, "#0A2A14"
                elif is_sel:     border_c, bg_c = ERROR,   "#2A0A0A"
                else:            border_c, bg_c = BORDER,  CARD
            else:
                border_c = COLORI[lettera] if is_sel else BORDER
                bg_c     = "#0A1828"       if is_sel else CARD

            icona = ("  ✓" if is_corretta else "  ✗") if (confirmed and (is_sel or is_corretta)) else ""

            opzioni.append(ft.Container(
                ft.Row([
                    ft.Container(
                        ft.Text(lettera, size=12, color=BG, weight=ft.FontWeight.BOLD),
                        bgcolor=COLORI[lettera], border_radius=6,
                        width=26, height=26, alignment=ft.Alignment(0, 0),
                    ),
                    ft.Text(testo + icona, size=14, color=WHITE if is_sel else TEXT, expand=True),
                ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=bg_c,
                border=ft.Border.all(2 if is_sel else 1, border_c),
                border_radius=10, padding=14,
                on_click=(None if confirmed else (lambda e, l=lettera: _seleziona(l))),
                ink=not confirmed,
                margin=ft.Margin(0, 4, 0, 4),
            ))

        spiegazione = []
        if confirmed:
            ok = sel == d["corretta"]
            risposta_label = (
                f"✓ {i18n.t('ris_corretta')}!" if ok
                else f"✗ {i18n.t('ris_tua_risposta')}: {sel}) {d['opzioni'].get(sel, '')}"
            )
            spiegazione = [ft.Container(
                ft.Column([
                    ft.Text(risposta_label, size=14,
                            color=SUCCESS if ok else ERROR, weight=ft.FontWeight.BOLD),
                    ft.Container(height=4),
                    ft.Text(f"{i18n.t('ris_corretta')}: {d['corretta']}) {d['opzioni'][d['corretta']]}",
                            size=13, color=GOLD),
                    ft.Container(height=6),
                    ft.Text(d["spiegazione"], size=13, color=TEXT),
                ], spacing=2),
                bgcolor="#0A1A0A" if ok else "#1A0A0A",
                border=ft.Border.all(1, SUCCESS if ok else ERROR),
                border_radius=10, padding=14,
                margin=ft.Margin(0, 8, 0, 0),
            )]

        nav = []
        if idx > 0:
            nav.append(filled_btn(i18n.t("quiz_precedente"), SURFACE, TEXT, lambda e: _vai(idx - 1)))
        nav.append(ft.Container(expand=True))
        if idx < n_tot - 1:
            nav.append(filled_btn(i18n.t("quiz_successivo"), ACCENT, BG, lambda e: _vai(idx + 1)))
        else:
            nav.append(filled_btn(f"{i18n.t('quiz_risultati')} 🏆", GOLD, BG, lambda e: show_risultati()))

        # Timer widget (visibile solo se attivo e domanda non ancora risposta)
        timer_widget = ft.Container(height=0)
        if timer_sec > 0 and not confirmed:
            timer_widget = ft.Container(
                ft.Row([
                    ft.Container(expand=True),
                    ft.Text(f"⏱  {timer_sec}s", size=20, color=ACCENT,
                            weight=ft.FontWeight.BOLD, ref=timer_ref),
                    ft.Container(expand=True),
                ]),
                margin=ft.Margin(0, 0, 0, 8),
            )

        # Costruiamo i controlli e aggiorniamo la pagina
        main_col.controls = [
            ft.Container(
                ft.Column([
                    ft.Row([
                        ft.TextButton(i18n.t("btn_indietro"), on_click=lambda e: show_modalita(),
                                      style=ft.ButtonStyle(color={ft.ControlState.DEFAULT: DIM})),
                        ft.Container(expand=True),
                        lbl(f"{len(state['risposte'])}/{n_tot} {i18n.t('quiz_risultati').lower()}", size=12, color=ACCENT),
                    ]),
                    ft.Container(height=6),
                    ft.ProgressBar(value=(idx + 1) / n_tot, bgcolor=BORDER, color=ACCENT,
                                   border_radius=4, height=6),
                    ft.Container(height=4),
                    lbl(i18n.t("quiz_domanda", corrente=idx + 1, totale=n_tot), size=12),
                ], spacing=0),
                border=ft.Border(bottom=ft.BorderSide(1, BORDER)),
                margin=ft.Margin(0, 0, 0, 16),
                padding=ft.Padding.symmetric(vertical=10),
            ),
            timer_widget,
            card(ft.Text(f"{idx + 1}. {d['testo']}", size=16, color=WHITE, weight=ft.FontWeight.BOLD)),
            ft.Column(opzioni, spacing=0),
            *spiegazione,
            ft.Container(height=16),
            ft.Row(nav, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ]
        page.update()

        # Avvia il timer asincrono se necessario
        if timer_sec > 0 and not confirmed:
            async def run_timer(sec, q_idx):
                try:
                    for remaining in range(sec, -1, -1):
                        if timer_ref.current:
                            timer_ref.current.value = f"⏱  {remaining}s"
                            timer_ref.current.color = ERROR if remaining <= 5 else ACCENT
                            page.update()
                        if remaining == 0:
                            break
                        await asyncio.sleep(1)
                    # Tempo scaduto
                    if state["corrente"] == q_idx:
                        if q_idx < len(state["domande"]) - 1:
                            state["corrente"] = q_idx + 1
                            show_interattiva()
                        else:
                            show_risultati()
                except asyncio.CancelledError:
                    pass

            state["_timer_task"] = page.run_task(run_timer, timer_sec, idx)

    def _seleziona(lettera):
        stop_timer()
        state["risposte"][state["corrente"]] = lettera
        show_interattiva()

    def _vai(idx):
        state["corrente"] = idx
        show_interattiva()

    def show_visualizza():
        domande = state["domande"]
        items = [
            ft.Row([
                ft.TextButton(i18n.t("btn_indietro"), on_click=lambda e: show_modalita(),
                              style=ft.ButtonStyle(color={ft.ControlState.DEFAULT: DIM})),
                ft.Container(expand=True),
                lbl(i18n.t("quiz_num_domande", n=len(domande)), size=12, color=ACCENT),
            ]),
            ft.Container(height=8),
            ft.Text(i18n.t("quiz_tutte"), size=22, color=WHITE, weight=ft.FontWeight.BOLD),
            ft.Container(height=16),
        ]

        for i, d in enumerate(domande):
            risposta_ref = ft.Ref[ft.Container]()
            btn_ref      = ft.Ref[ft.FilledButton]()

            def toggle(e, rr=risposta_ref, br=btn_ref):
                rr.current.visible = not rr.current.visible
                br.current.content = ft.Text(
                    i18n.t("btn_nascondi") if rr.current.visible else i18n.t("btn_rivela"),
                    size=12, color=BG if rr.current.visible else ACCENT,
                )
                br.current.style.bgcolor = {
                    ft.ControlState.DEFAULT: ACCENT if rr.current.visible else SURFACE,
                }
                page.update()

            opz = ft.Column([
                ft.Row([
                    ft.Container(
                        ft.Text(l, size=11, color=BG, weight=ft.FontWeight.BOLD),
                        bgcolor=COLORI[l], border_radius=5,
                        width=24, height=24, alignment=ft.Alignment(0, 0),
                    ),
                    ft.Text(d["opzioni"].get(l, ""), size=13, color=TEXT, expand=True),
                ], spacing=10)
                for l in LETTERE if d["opzioni"].get(l)
            ], spacing=6)

            risposta_box = ft.Container(
                ft.Column([
                    ft.Text(f"✓ {d['corretta']}) {d['opzioni'][d['corretta']]}",
                            size=13, color=SUCCESS, weight=ft.FontWeight.BOLD),
                    ft.Container(height=4),
                    ft.Text(d["spiegazione"], size=12, color=TEXT),
                ], spacing=2),
                bgcolor="#0A1A0A", border=ft.Border.all(1, SUCCESS),
                border_radius=8, padding=12,
                visible=False, ref=risposta_ref,
                margin=ft.Margin(0, 8, 0, 0),
            )

            items.append(card(ft.Column([
                ft.Text(f"{i + 1}. {d['testo']}", size=15, color=WHITE, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                opz,
                ft.Container(height=10),
                ft.FilledButton(
                    content=ft.Text(i18n.t("btn_rivela"), size=12, color=ACCENT),
                    style=ft.ButtonStyle(
                        bgcolor={ft.ControlState.DEFAULT: SURFACE},
                        shape=ft.RoundedRectangleBorder(radius=7),
                        side={ft.ControlState.DEFAULT: ft.BorderSide(1, ACCENT)},
                        padding=ft.Padding.symmetric(horizontal=16, vertical=8),
                    ),
                    on_click=toggle, ref=btn_ref,
                ),
                risposta_box,
            ], spacing=0)))

        render(items)

    # ══════════════════════════════════════════════════════════════════════════
    # SCHERMATA 4 — RISULTATI
    # ══════════════════════════════════════════════════════════════════════════
    def show_risultati():
        stop_timer()
        domande  = state["domande"]
        risposte = state["risposte"]
        tokens   = state["tokens"]
        n_tot    = len(domande)
        corrette    = sum(1 for i, d in enumerate(domande) if risposte.get(i) == d["corretta"])
        non_risp    = sum(1 for i in range(n_tot) if i not in risposte)
        sbagliate_n = n_tot - corrette - non_risp
        pct         = int(corrette / n_tot * 100) if n_tot else 0

        if pct == 100:  emoji, msg_key, col = "🏆", "ris_perfetto", GOLD
        elif pct >= 70: emoji, msg_key, col = "🎉", "ris_ottimo",   SUCCESS
        elif pct >= 50: emoji, msg_key, col = "📚", "ris_quasi",    ACCENT
        else:           emoji, msg_key, col = "💪", "ris_allenati", WARN

        # Salva in cronologia
        save_to_cronologia({
            "data":       datetime.now().strftime("%d/%m/%Y %H:%M"),
            "argomento":  state.get("argomento", ""),
            "difficolta": state.get("difficolta", ""),
            "n_domande":  n_tot,
            "corrette":   corrette,
            "pct":        pct,
        })

        sbagliate = [(i, d) for i, d in enumerate(domande)
                     if risposte.get(i) != d["corretta"]]

        # ── Grafico a barre ──────────────────────────────────────────────────
        def barra(valore, totale, colore, etichetta):
            pct_bar = valore / totale if totale > 0 else 0
            return ft.Column([
                ft.Text(str(valore), size=18, color=colore,
                        weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Container(
                    ft.Container(bgcolor=colore, border_radius=6,
                                 width=60 * pct_bar + 4, height=12),
                    bgcolor=SURFACE, border_radius=6,
                    width=64, height=12, padding=0,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                ),
                lbl(etichetta, size=11, color=TEXT),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6)

        grafico = ft.Row([
            barra(corrette,    n_tot, SUCCESS, i18n.t("grafico_corrette")),
            ft.Container(width=1, height=60, bgcolor=BORDER),
            barra(sbagliate_n, n_tot, ERROR,   i18n.t("grafico_sbagliate")),
            ft.Container(width=1, height=60, bgcolor=BORDER),
            barra(non_risp,    n_tot, DIM,     i18n.t("grafico_non_risp")),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=24,
           vertical_alignment=ft.CrossAxisAlignment.CENTER)



        items = [
            ft.Row([
                ft.TextButton(i18n.t("btn_rigioca"), on_click=lambda e: _rigioca(),
                              style=ft.ButtonStyle(color={ft.ControlState.DEFAULT: DIM})),
                ft.Container(expand=True),
                filled_btn(i18n.t("btn_nuovo_quiz"), ACCENT, BG, lambda e: show_home()),
            ]),
            ft.Container(height=10),

            card(ft.Column([
                ft.Text(emoji, size=48, text_align=ft.TextAlign.CENTER),
                ft.Text(i18n.t(msg_key), size=22, color=col,
                        weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Container(height=8),
                ft.Text(i18n.t("ris_corrette", corrette=corrette, totale=n_tot),
                        size=16, color=WHITE, text_align=ft.TextAlign.CENTER),
                ft.Container(height=12),
                ft.ProgressBar(value=pct / 100, bgcolor=BORDER, color=col,
                               border_radius=6, height=10),
                ft.Text(f"{pct}%", size=14, color=col, text_align=ft.TextAlign.CENTER),
                ft.Container(height=20),
                lbl(i18n.t("grafico_title"), bold=True, size=12),
                ft.Container(height=10),
                grafico,
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
            border_color=col),

            *([] if not tokens else [
                ft.Container(height=8),
                lbl(i18n.t("tok_title"), bold=True),
                ft.Container(height=8),
                ft.Row([
                    tok_badge(i18n.t("tok_prompt"),   str(tokens["prompt"]),   ACCENT),
                    tok_badge(i18n.t("tok_risposta"), str(tokens["risposta"]), ACCENT2),
                    tok_badge(i18n.t("tok_totale"),   str(tokens["totale"]),   GOLD),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=12),
            ]),

            ft.Container(height=16),
        ]

        if sbagliate:
            items.append(lbl(i18n.t("ris_sbagliate"), bold=True))
            for i, d in sbagliate:
                scelta = risposte.get(i)
                items.append(card(ft.Column([
                    ft.Text(f"{i + 1}. {d['testo']}", size=14, color=WHITE,
                            weight=ft.FontWeight.BOLD),
                    ft.Container(height=8),
                    ft.Row([
                        ft.Container(
                            lbl(i18n.t("ris_tua_risposta"), color=ERROR, bold=True),
                            bgcolor="#2A0A0A", border=ft.Border.all(1, ERROR),
                            border_radius=6, padding=ft.Padding.symmetric(),
                        ),
                        ft.Text(
                            f"{scelta}) {d['opzioni'].get(scelta, '—')}" if scelta
                            else i18n.t("ris_non_risposto"),
                            size=13, color=ERROR,
                        ),
                    ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Row([
                        ft.Container(
                            lbl(i18n.t("ris_corretta"), color=SUCCESS, bold=True),
                            bgcolor="#0A2A14", border=ft.Border.all(1, SUCCESS),
                            border_radius=6, padding=ft.Padding.symmetric(),
                        ),
                        ft.Text(f"{d['corretta']}) {d['opzioni'][d['corretta']]}",
                                size=13, color=SUCCESS),
                    ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Container(height=8),
                    ft.Container(height=1, bgcolor=BORDER),
                    ft.Container(height=8),
                    ft.Text("💡  " + d["spiegazione"], size=13, color=TEXT),
                ], spacing=4)))
        else:
            items.append(ft.Text(i18n.t("ris_tutte_ok"), size=14, color=SUCCESS))

        items.append(ft.Container(height=40))
        render(items)

    def _rigioca():
        state["risposte"] = {}
        state["corrente"] = 0
        show_interattiva()

    # ══════════════════════════════════════════════════════════════════════════
    # SCHERMATA 5 — CRONOLOGIA
    # ══════════════════════════════════════════════════════════════════════════
    def show_cronologia():
        storia = load_cronologia()

        def on_clear(e):
            clear_cronologia()
            show_cronologia()

        items = [
            ft.Row([
                ft.TextButton(i18n.t("btn_indietro"), on_click=lambda e: show_home(),
                              style=ft.ButtonStyle(color={ft.ControlState.DEFAULT: DIM})),
                ft.Container(expand=True),
                *([] if not storia else [
                    ft.TextButton(i18n.t("cronologia_clear"), on_click=on_clear,
                                  style=ft.ButtonStyle(color={ft.ControlState.DEFAULT: ERROR})),
                ]),
            ]),
            ft.Container(height=10),
            ft.Text(i18n.t("cronologia_title"), size=24, color=WHITE, weight=ft.FontWeight.BOLD),
            ft.Container(height=16),
        ]

        if not storia:
            items.append(card(ft.Column([
                ft.Text("📭", size=48, text_align=ft.TextAlign.CENTER),
                ft.Container(height=8),
                lbl(i18n.t("cronologia_vuota"), size=14, color=DIM),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0)))
        else:
            for entry in storia:
                pct = entry.get("pct", 0)
                col = GOLD if pct == 100 else SUCCESS if pct >= 70 else ACCENT if pct >= 50 else WARN
                n_dom = entry.get("n_domande", 0)
                items.append(card(ft.Column([
                    ft.Row([
                        ft.Column([
                            ft.Text(entry.get("argomento", ""), size=15, color=WHITE,
                                    weight=ft.FontWeight.BOLD),
                            lbl(f"{entry.get('difficolta', '')}  ·  {n_dom} {i18n.t('label_domande')}  ·  {entry.get('data', '')}", size=11),
                        ], spacing=2, expand=True),
                        ft.Container(
                            ft.Text(f"{pct}%", size=18, color=col,
                                    weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                            bgcolor=SURFACE, border=ft.Border.all(1, col),
                            border_radius=8, padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                        ),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Container(height=8),
                    ft.ProgressBar(value=pct / 100, bgcolor=BORDER, color=col,
                                   border_radius=4, height=6),
                    ft.Container(height=4),
                    lbl(i18n.t("ris_corrette",
                               corrette=entry.get("corrette", 0),
                               totale=n_dom), size=11),
                ], spacing=0)))

        render(items)

    page.add(main_col)
    show_home()


ft.app(main)