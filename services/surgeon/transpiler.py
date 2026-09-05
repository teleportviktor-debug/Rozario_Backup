"""
Surgeon Transpiler (Agent 2 - Core UI Engineer)
Microservice: v0/JSX/Tailwind -> Google Workspace CardService & A2UICardPayload.

Zero-Trust compliant parser with Ver Sacrum / Klimt Cyber-minimalist aesthetics:
- Obsidian: #0a0a0c
- Neon Cyan: #00f0ff
- Gold: #d4af37
"""

import re
import json
import logging
from typing import Union, Dict, Any, List, Optional
from bs4 import BeautifulSoup, Tag, NavigableString

from services.schemas.card_service import (
    A2UICardPayload,
    CardSection,
    CardWidget,
    WidgetButton,
    GoogleWorkspaceCardMessage,
    CardItemV2,
    Card,
    CardHeader,
    Section,
    Widget,
    TextParagraph,
    DecoratedText,
    ButtonList,
    Button,
    Image,
    Icon,
    OnClick,
    OpenLink,
    Color,
    COLOR_OBSIDIAN,
    COLOR_NEON_CYAN,
    COLOR_KLIMT_GOLD,
    COLOR_MUTED_STEEL,
)

logger = logging.getLogger("SurgeonTranspiler")


class SurgeonTranspiler:
    """
    Transpiles v0 React/Tailwind JSX, HTML or AST into:
    1) A2UICardPayload (intermediate representation)
    2) GoogleWorkspaceCardMessage (Google CardService v2 cardsV2)
    """

    ALLOWED_TAGS = {"b", "i", "u", "font", "a", "br"}

    def __init__(
        self,
        default_theme: str = "OBSIDIAN_CYAN",
        theme_gold: str = COLOR_KLIMT_GOLD,
        theme_cyan: str = COLOR_NEON_CYAN,
    ):
        self.default_theme = default_theme
        self.theme_gold = theme_gold
        self.theme_cyan = theme_cyan

    def transpile_to_payload(
        self,
        input_content: Union[str, Dict[str, Any]],
        card_id: Optional[str] = None
    ) -> A2UICardPayload:
        """
        Parses JSX/HTML or AST into an A2UICardPayload.
        Guarantees fallback resilience (never crashes on malformed input).
        """
        cid = card_id or "genome_card"

        # 1. Direct dict/AST parsing
        if isinstance(input_content, dict):
            try:
                return self._parse_ast_to_payload(input_content, card_id=cid)
            except Exception as e:
                logger.error(f"AST parsing error: {e}")
                return self._build_fallback_payload(cid, f"AST Parsing Error: {str(e)}")

        if not isinstance(input_content, str) or not input_content.strip():
            return self._build_fallback_payload(cid, "Empty or invalid input provided")

        # 2. Stringified JSON detection
        stripped = input_content.strip()
        if stripped.startswith("{") and stripped.endswith("}"):
            try:
                data = json.loads(stripped)
                if isinstance(data, dict):
                    return self._parse_ast_to_payload(data, card_id=cid)
            except json.JSONDecodeError:
                pass

        # 3. JSX / HTML parsing with error recovery
        try:
            return self._parse_jsx_to_payload(input_content, card_id=cid)
        except Exception as e:
            logger.error(f"Transpilation recovery triggered for JSX: {e}")
            return self._build_fallback_payload(cid, f"Transpilation Warning: {str(e)}")

    def transpile(
        self,
        input_content: Union[str, Dict[str, Any], A2UICardPayload],
        card_id: Optional[str] = None
    ) -> GoogleWorkspaceCardMessage:
        """
        Translates input into validated GoogleWorkspaceCardMessage.
        """
        if isinstance(input_content, A2UICardPayload):
            return input_content.to_card_service_message()

        payload = self.transpile_to_payload(input_content, card_id=card_id)
        return payload.to_card_service_message()

    def transpile_to_json(
        self,
        input_content: Union[str, Dict[str, Any], A2UICardPayload],
        indent: int = 2
    ) -> str:
        """Serializes transpiled card into JSON string."""
        msg = self.transpile(input_content)
        return msg.to_json_str(indent=indent)

    def _clean_jsx(self, jsx: str) -> str:
        """Preprocesses JSX, removing React runtime constructs and handling ternaries."""
        text = jsx

        # Remove import statements and exports
        text = re.sub(r"import\s+.*?;\s*", "", text)
        text = re.sub(r"export\s+default\s+function\s+\w+\s*\([^)]*\)\s*\{", "", text)
        text = re.sub(r"return\s*\(\s*", "", text)

        # Remove JSX comments
        text = re.sub(r"\{/\*.*?\*/\}", "", text, flags=re.DOTALL)

        # Resolve JSX ternaries: {condition ? "Truthy" : "Falsy"} -> "Truthy"
        text = re.sub(
            r'\{[^{}]*\?\s*["\']([^"\']+)["\']\s*:\s*["\']([^"\']+)["\']\s*\}',
            r"\1",
            text
        )
        # Resolve JSX conditionals: {condition && "Value"} -> "Value"
        text = re.sub(r'\{[^{}]*&&\s*["\']([^"\']+)["\']\s*\}', r"\1", text)

        # Remove SVG blocks cleanly
        text = re.sub(r"<svg.*?</svg>", "", text, flags=re.DOTALL)

        # Standardize JSX attributes to HTML
        text = re.sub(r"className=", "class=", text)
        text = re.sub(r"htmlFor=", "for=", text)
        # Strip inline style objects style={{...}}
        text = re.sub(r"style=\{\{.*?\}\}", "", text)
        # Strip onClick handlers to adhere to Zero Trust
        text = re.sub(r'onClick=\{.*?\}', "", text)

        return text

    def _parse_jsx_to_payload(self, jsx_str: str, card_id: str) -> A2UICardPayload:
        """Extracts titles, badges, metrics, paragraphs, and buttons into A2UICardPayload."""
        cleaned = self._clean_jsx(jsx_str)
        soup = BeautifulSoup(cleaned, "html.parser")

        # Fallback if soup is empty or invalid
        if not soup.find():
            return self._build_fallback_payload(card_id, "Malformed JSX markup structure")

        title: Optional[str] = None
        subtitle: Optional[str] = None
        widgets: List[CardWidget] = []
        pending_buttons: List[WidgetButton] = []

        # 1. Identify primary title & subtitle
        heading_tags = soup.find_all(["h1", "h2", "h3", "h4"])
        if heading_tags:
            primary_h = heading_tags[0]
            title = primary_h.get_text(separator=" ", strip=True)
            # Check for subtitle
            next_sib = primary_h.find_next_sibling(["p", "span", "h3", "h4", "h5"])
            if next_sib:
                sub_text = next_sib.get_text(separator=" ", strip=True)
                if sub_text and sub_text != title and len(sub_text) < 120:
                    subtitle = sub_text

        if not title:
            title = "Razum Sovereign Intelligence"
        if not subtitle:
            subtitle = "Google Workspace Autonomous Card"

        # 2. Traverse tags
        for el in soup.find_all(True):
            if not isinstance(el, Tag) or el.attrs is None:
                continue

            tag_name = el.name.lower() if el.name else ""
            raw_classes = el.attrs.get("class", [])
            classes = " ".join(raw_classes) if isinstance(raw_classes, list) else str(raw_classes)

            # Skip main heading if already used
            if heading_tags and el == heading_tags[0]:
                continue

            # Process Buttons & Links
            if tag_name in ("button", "a"):
                btn_text = el.get_text(separator=" ", strip=True)
                raw_href = el.attrs.get("href", "")
                if btn_text:
                    # Sanitize URL for Zero Trust
                    safe_url = raw_href if raw_href.startswith(("http://", "https://", "mailto:")) else None
                    pending_buttons.append(
                        WidgetButton(
                            text=btn_text,
                            action_type="OPEN_URL" if safe_url else "CLICK_ACTION",
                            url=safe_url
                        )
                    )

            # Process Key-Value / Metrics (e.g. flex justify-between or grid cells)
            elif ("justify-between" in classes or "flex-between" in classes) and tag_name == "div":
                children = [c for c in el.children if isinstance(c, Tag)]
                if len(children) == 2:
                    top_lbl = children[0].get_text(separator=" ", strip=True)
                    val_text = children[1].get_text(separator=" ", strip=True)
                    if top_lbl and val_text:
                        widgets.append(
                            CardWidget(
                                widget_type="decoratedText",
                                top_label=top_lbl,
                                text=self._sanitize_string(val_text)
                            )
                        )
                        # Decompose so children aren't processed as paragraphs
                        children[0].decompose()
                        children[1].decompose()

            # Process Paragraphs & Notes
            elif tag_name in ("p", "blockquote") and el.parent.name not in ("button", "a"):
                p_text = el.get_text(separator=" ", strip=True)
                if p_text and p_text != subtitle and len(p_text) > 2:
                    sanitized_p = self._sanitize_string(p_text)
                    if sanitized_p:
                        widgets.append(
                            CardWidget(
                                widget_type="textParagraph",
                                text=sanitized_p
                            )
                        )

        # 3. Attach collected buttons
        if pending_buttons:
            widgets.append(
                CardWidget(
                    widget_type="buttonList",
                    buttons=pending_buttons
                )
            )

        # 4. Guarantee at least one widget
        if not widgets:
            widgets.append(
                CardWidget(
                    widget_type="textParagraph",
                    text="Autonomous card payload processed under Zero Trust."
                )
            )

        section = CardSection(header="Overview", collapsible=False, widgets=widgets)
        return A2UICardPayload(
            card_id=card_id,
            title=title,
            subtitle=subtitle,
            style_theme=self.default_theme,
            sections=[section]
        )

    def _parse_ast_to_payload(self, ast_data: Dict[str, Any], card_id: str) -> A2UICardPayload:
        """Maps AST dictionary directly to A2UICardPayload."""
        title = ast_data.get("title") or "Razum Genome Card"
        subtitle = ast_data.get("subtitle") or "Autonomous A2UI Service"
        theme = ast_data.get("style_theme") or self.default_theme

        raw_sections = ast_data.get("sections", [])
        sections: List[CardSection] = []

        if raw_sections:
            for s in raw_sections:
                s_header = s.get("header")
                s_collapsible = bool(s.get("collapsible", False))
                s_widgets: List[CardWidget] = []
                for w in s.get("widgets", []):
                    s_widgets.append(
                        CardWidget(
                            widget_type=w.get("widget_type", "textParagraph"),
                            text=self._sanitize_string(w.get("text", "")),
                            top_label=w.get("top_label"),
                            bottom_label=w.get("bottom_label"),
                            icon_url=w.get("icon_url"),
                            buttons=[WidgetButton(**b) for b in w.get("buttons", [])] if w.get("buttons") else None
                        )
                    )
                if s_widgets:
                    sections.append(CardSection(header=s_header, collapsible=s_collapsible, widgets=s_widgets))
        else:
            # Flat children
            flat_widgets: List[CardWidget] = []
            for item in ast_data.get("elements", []):
                flat_widgets.append(
                    CardWidget(
                        widget_type=item.get("type", "textParagraph"),
                        text=self._sanitize_string(item.get("text", "")),
                        top_label=item.get("topLabel"),
                        bottom_label=item.get("bottomLabel"),
                    )
                )
            if not flat_widgets:
                flat_widgets.append(CardWidget(widget_type="textParagraph", text="System ready."))
            sections.append(CardSection(header="Details", widgets=flat_widgets))

        return A2UICardPayload(
            card_id=card_id,
            title=title,
            subtitle=subtitle,
            style_theme=theme,
            sections=sections
        )

    def _build_fallback_payload(self, card_id: str, reason: str) -> A2UICardPayload:
        """Constructs a valid resilient fallback payload when parsing is obstructed."""
        return A2UICardPayload(
            card_id=card_id,
            title="[Fallback] Parsing Recovery Mode",
            subtitle="Autonomous Zero Trust Sanitizer",
            style_theme="OBSIDIAN_CYAN",
            sections=[
                CardSection(
                    header="Telemetry Status",
                    widgets=[
                        CardWidget(
                            widget_type="decoratedText",
                            top_label="System State",
                            text="FALLBACK_ENGAGED"
                        ),
                        CardWidget(
                            widget_type="textParagraph",
                            text=f"The card was generated via fallback recovery: {reason}"
                        )
                    ]
                )
            ]
        )

    def _sanitize_string(self, text: str) -> str:
        """Sanitizes text, stripping dangerous tags, scripts, and non-printable artifacts."""
        if not text:
            return ""
        # Strip dangerous HTML/scripts
        cleaned = re.sub(r"<(script|iframe|style|object|embed)[^>]*>.*?</\1>", "", text, flags=re.IGNORECASE | re.DOTALL)
        # Strip potential event handlers
        cleaned = re.sub(r"on\w+\s*=\s*['\"][^'\"]*['\"]", "", cleaned, flags=re.IGNORECASE)
        # Strip unprintable control characters
        cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", cleaned)
        return cleaned.strip()
