"""
Surgeon Transpiler (Микросервис «Хирург»)
Architecture "Genome" (Phase 1) - Razum Google AI PRO.

Transpiles v0 / React / Tailwind JSX or AST JSON into strictly validated
Google Workspace CardService JSON (cardsV2) compliant with Zero Trust standards.
"""

import re
import json
import html
from typing import Union, Dict, Any, List, Optional
from bs4 import BeautifulSoup, Tag, NavigableString

from services.schemas.card_service import (
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
    A2UICardPayload,
    COLOR_OBSIDIAN,
    COLOR_NEON_CYAN,
    COLOR_KLIMT_GOLD,
    COLOR_MUTED_STEEL,
)


class SurgeonTranspiler:
    """
    Core transpilation engine that ingests React/Tailwind/JSX markup or AST representations
    and outputs validated Google Workspace CardService JSON.
    """

    ALLOWED_TAGS = {"b", "i", "u", "font", "a", "br"}

    def __init__(
        self,
        default_title: str = "Razum Genome UI",
        default_subtitle: str = "Google Workspace Autonomous Intelligence",
        theme_gold: str = COLOR_KLIMT_GOLD,
        theme_cyan: str = COLOR_NEON_CYAN,
    ):
        self.default_title = default_title
        self.default_subtitle = default_subtitle
        self.theme_gold = theme_gold
        self.theme_cyan = theme_cyan

    def transpile(self, input_content: Union[str, Dict[str, Any], A2UICardPayload]) -> GoogleWorkspaceCardMessage:
        """
        Main entry point. Detects if input is A2UICardPayload, AST dict, JSON string, or raw JSX/Tailwind.
        """
        if isinstance(input_content, A2UICardPayload):
            return input_content.to_card_service_message()

        if isinstance(input_content, dict):
            return self.transpile_ast(input_content)

        if isinstance(input_content, str):
            stripped = input_content.strip()
            if stripped.startswith("{") and stripped.endswith("}"):
                try:
                    data = json.loads(stripped)
                    if isinstance(data, dict):
                        return self.transpile_ast(data)
                except json.JSONDecodeError:
                    pass
            return self.transpile_jsx(input_content)

        raise ValueError(f"Unsupported input type for SurgeonTranspiler: {type(input_content)}")

    def transpile_to_json(self, input_content: Union[str, Dict[str, Any]], indent: int = 2) -> str:
        """Convenience method returning sanitized and formatted JSON string."""
        card_msg = self.transpile(input_content)
        return card_msg.to_json_str(indent=indent)

    def transpile_ast(self, ast_data: Dict[str, Any]) -> GoogleWorkspaceCardMessage:
        """
        Transpiles an AST dictionary into a GoogleWorkspaceCardMessage.
        """
        # Extract or construct header
        title = ast_data.get("title") or self.default_title
        subtitle = ast_data.get("subtitle") or self.default_subtitle
        icon_url = ast_data.get("iconUrl") or ast_data.get("avatarUrl")

        header = CardHeader(
            title=f'<font color="{self.theme_gold}">✦</font> {title}',
            subtitle=f'<font color="{self.theme_cyan}">{subtitle}</font>' if subtitle else None,
            imageUrl=icon_url,
            imageType="CIRCLE" if icon_url else None
        )

        sections: List[Section] = []
        raw_sections = ast_data.get("sections")

        if raw_sections and isinstance(raw_sections, list):
            for s_idx, sec_data in enumerate(raw_sections):
                sec_header = sec_data.get("header")
                sec_widgets: List[Widget] = []
                for w in sec_data.get("widgets", []):
                    widget = self._parse_ast_widget(w)
                    if widget:
                        sec_widgets.append(widget)
                if sec_widgets:
                    sections.append(Section(header=sec_header, widgets=sec_widgets))
        else:
            # Flat widget list in AST root
            elements = ast_data.get("elements") or ast_data.get("children") or []
            widgets: List[Widget] = []
            for el in elements:
                widget = self._parse_ast_widget(el)
                if widget:
                    widgets.append(widget)
            if not widgets:
                # Fallback paragraph
                widgets.append(Widget(
                    textParagraph=TextParagraph(
                        text=f'<font color="{self.theme_cyan}">[Genome Active]</font> System initialized.'
                    )
                ))
            sections.append(Section(header=None, widgets=widgets))

        card = Card(
            header=header,
            sections=sections,
            name=ast_data.get("cardId", "GenomeCard")
        )

        return GoogleWorkspaceCardMessage(
            cardsV2=[CardItemV2(cardId="genome_card_v2", card=card)]
        )

    def _parse_ast_widget(self, el: Dict[str, Any]) -> Optional[Widget]:
        """Maps single AST node to a CardService Widget."""
        w_type = el.get("type", "").lower()

        if w_type in ("text", "textparagraph", "paragraph", "p"):
            raw_text = el.get("text") or el.get("content", "")
            return Widget(textParagraph=TextParagraph(text=self._sanitize_html(raw_text)))

        if w_type in ("decoratedtext", "decorated", "stat", "metric"):
            top_label = el.get("topLabel") or el.get("label")
            text = el.get("text") or el.get("value", "")
            bottom_label = el.get("bottomLabel")
            icon_url = el.get("iconUrl")
            start_icon = Icon(iconUrl=icon_url) if icon_url else None

            button_data = el.get("button")
            btn = None
            if button_data:
                btn = Button(
                    text=button_data.get("text", "Open"),
                    color=Color.from_hex(self.theme_cyan),
                    onClick=OnClick(openLink=OpenLink(url=button_data.get("url", "#")))
                )

            return Widget(
                decoratedText=DecoratedText(
                    topLabel=top_label,
                    text=self._sanitize_html(text),
                    bottomLabel=bottom_label,
                    startIcon=start_icon,
                    button=btn
                )
            )

        if w_type in ("buttonlist", "buttons"):
            buttons: List[Button] = []
            for b in el.get("buttons", []):
                btn_color = Color.from_hex(self.theme_gold if b.get("isGold") else self.theme_cyan)
                buttons.append(
                    Button(
                        text=b.get("text", "Execute"),
                        color=btn_color,
                        onClick=OnClick(openLink=OpenLink(url=b.get("url", "#")))
                    )
                )
            if buttons:
                return Widget(buttonList=ButtonList(buttons=buttons))

        if w_type in ("button", "action"):
            btn_color = Color.from_hex(self.theme_gold if el.get("isGold") else self.theme_cyan)
            return Widget(
                buttonList=ButtonList(
                    buttons=[
                        Button(
                            text=el.get("text", "Execute"),
                            color=btn_color,
                            onClick=OnClick(openLink=OpenLink(url=el.get("url", "#")))
                        )
                    ]
                )
            )

        if w_type in ("image", "img"):
            url = el.get("imageUrl") or el.get("url") or el.get("src", "")
            alt = el.get("alt") or el.get("altText", "Visual")
            return Widget(image=Image(imageUrl=url, altText=alt))

        if w_type in ("divider", "separator", "hr"):
            return Widget(divider={"dividerType": "SOLID_DIVIDER"})

        return None

    def transpile_jsx(self, jsx_code: str) -> GoogleWorkspaceCardMessage:
        """
        Parses raw React/JSX code with Tailwind classes and synthesizes a valid CardService schema.
        """
        cleaned_jsx = self._preprocess_jsx(jsx_code)
        soup = BeautifulSoup(cleaned_jsx, "html.parser")

        header_title: Optional[str] = None
        header_subtitle: Optional[str] = None
        header_avatar: Optional[str] = None

        widgets: List[Widget] = []
        pending_buttons: List[Button] = []

        # 1. Search for title candidates (h1, h2, h3)
        heading_tags = soup.find_all(["h1", "h2", "h3"])
        if heading_tags:
            first_h = heading_tags[0]
            header_title = first_h.get_text(strip=True)
            # Look for subtitle immediately following or in close proximity
            sub_candidate = first_h.find_next_sibling(["p", "span", "h4"])
            if sub_candidate:
                header_subtitle = sub_candidate.get_text(strip=True)

        # 2. Search for header avatar/image
        avatar_img = soup.find("img")
        if avatar_img and avatar_img.get("src"):
            header_avatar = avatar_img["src"]

        # If still no title, use fallback
        if not header_title:
            header_title = self.default_title
        if not header_subtitle:
            header_subtitle = self.default_subtitle

        header = CardHeader(
            title=f'<font color="{self.theme_gold}">✦</font> {header_title}',
            subtitle=f'<font color="{self.theme_cyan}">{header_subtitle}</font>' if header_subtitle else None,
            imageUrl=header_avatar,
            imageType="CIRCLE" if header_avatar else None
        )

        # 3. Process structural blocks
        for element in soup.find_all(True):
            if not isinstance(element, Tag) or element.attrs is None:
                continue

            tag_name = element.name.lower() if element.name else ""
            raw_classes = element.attrs.get("class", []) if element.attrs else []
            classes = " ".join(raw_classes) if isinstance(raw_classes, list) else str(raw_classes)

            # Skip header tags already absorbed
            if heading_tags and element in heading_tags[:1]:
                continue

            # Process Images
            if tag_name == "img":
                src = element.get("src", "")
                if src and src != header_avatar:  # Don't duplicate header avatar
                    widgets.append(Widget(
                        image=Image(
                            imageUrl=src,
                            altText=element.get("alt", "Media asset")
                        )
                    ))

            # Process Buttons & Links
            elif tag_name in ("button", "a") and element.get_text(strip=True):
                btn_text = element.get_text(strip=True)
                btn_href = element.get("href", "#")
                is_gold = "gold" in classes or "#d4af37" in classes or "amber" in classes
                btn = Button(
                    text=btn_text,
                    color=Color.from_hex(self.theme_gold if is_gold else self.theme_cyan),
                    onClick=OnClick(openLink=OpenLink(url=btn_href))
                )
                pending_buttons.append(btn)

            # Process Key-Value / Stat rows (e.g. flex justify-between or dl/dt/dd)
            elif ("justify-between" in classes or "flex-between" in classes) and tag_name == "div":
                children = [c for c in element.children if isinstance(c, Tag)]
                if len(children) == 2:
                    top_lbl = children[0].get_text(strip=True)
                    val_text = children[1].get_text(strip=True)
                    # Check if val_text has styling
                    if "cyan" in " ".join(children[1].get("class", [])) or "#00f0ff" in " ".join(children[1].get("class", [])):
                        val_text = f'<font color="{self.theme_cyan}"><b>{val_text}</b></font>'
                    elif "emerald" in " ".join(children[1].get("class", [])):
                        val_text = f'<font color="#00ff88"><b>{val_text}</b></font>'
                    elif "gold" in " ".join(children[1].get("class", [])) or "#d4af37" in " ".join(children[1].get("class", [])):
                        val_text = f'<font color="{self.theme_gold}"><b>{val_text}</b></font>'
                    else:
                        val_text = f'<b>{val_text}</b>'

                    widgets.append(Widget(
                        decoratedText=DecoratedText(
                            topLabel=top_lbl,
                            text=val_text
                        )
                    ))
                    # Clear children so they aren't parsed again
                    children[0].decompose()
                    children[1].decompose()

            # Process Paragraphs & Descriptions
            elif tag_name in ("p", "span", "blockquote") and element.parent.name not in ("button", "a", "h1", "h2"):
                # Avoid re-processing text from decorated rows or buttons
                inner_text = element.get_text(strip=True)
                if inner_text and len(inner_text) > 4:
                    formatted_snippet = self._html_to_cardservice_text(element)
                    if formatted_snippet:
                        widgets.append(Widget(
                            textParagraph=TextParagraph(text=formatted_snippet)
                        ))

            # Process Dividers
            elif tag_name == "hr" or ("border-b" in classes and not element.get_text(strip=True)):
                widgets.append(Widget(divider={"dividerType": "SOLID_DIVIDER"}))

        # Flush any collected buttons into a single ButtonList widget
        if pending_buttons:
            widgets.append(Widget(buttonList=ButtonList(buttons=pending_buttons)))

        # Ensure at least one widget exists in the card
        if not widgets:
            widgets.append(Widget(
                textParagraph=TextParagraph(
                    text=f'<font color="{self.theme_cyan}">[Genome Transpiler]</font> Card content generated.'
                )
            ))

        section = Section(header="Overview", widgets=widgets)
        card = Card(header=header, sections=[section], name="TranspiledGenomeCard")

        return GoogleWorkspaceCardMessage(cardsV2=[CardItemV2(cardId="genome_card_v2", card=card)])

    def _preprocess_jsx(self, jsx_code: str) -> str:
        """Strips React boilerplate, imports, exports, and cleans self-closing tags."""
        code = jsx_code
        # Remove imports
        code = re.sub(r"import\s+.*?;\s*", "", code)
        # Remove export default function ... { return ( ... ) }
        code = re.sub(r"export\s+default\s+function\s+\w+\s*\([^)]*\)\s*\{", "", code)
        code = re.sub(r"return\s*\(\s*", "", code)
        # Replace JSX className="..." with class="..."
        code = re.sub(r"className=", "class=", code)
        # Replace JSX style={{...}} with empty string
        code = re.sub(r"style=\{\{.*?\}\}", "", code)
        return code

    def _html_to_cardservice_text(self, tag: Tag) -> str:
        """Converts an HTML tag into sanitized CardService HTML string with cyber styling."""
        raw_html = str(tag)
        # Replace Tailwind text color hints
        raw_html = re.sub(r'class="[^"]*text-cyan-[^"]*"', f'color="{self.theme_cyan}"', raw_html)
        raw_html = re.sub(r'class="[^"]*text-\[#00f0ff\][^"]*"', f'color="{self.theme_cyan}"', raw_html)
        raw_html = re.sub(r'class="[^"]*text-amber-[^"]*"', f'color="{self.theme_gold}"', raw_html)
        raw_html = re.sub(r'class="[^"]*text-\[#d4af37\][^"]*"', f'color="{self.theme_gold}"', raw_html)
        return self._sanitize_html(raw_html)

    def _sanitize_html(self, text_content: str) -> str:
        """
        Sanitizes text ensuring ONLY allowed Google CardService tags remain:
        <b>, <i>, <u>, <font color="...">, <a href="...">, <br>
        All other tags are stripped while preserving interior text.
        """
        if not text_content:
            return ""

        # Use beautifulsoup to parse and filter
        soup = BeautifulSoup(text_content, "html.parser")

        for el in soup.find_all(True):
            if not isinstance(el, Tag) or el.attrs is None:
                continue
            name = el.name.lower() if el.name else ""
            if name in ("strong", "h1", "h2", "h3", "h4", "h5", "h6"):
                el.name = "b"
            elif name in ("em",):
                el.name = "i"
            elif name in ("p", "div", "span", "blockquote"):
                el.unwrap()
            elif name in ("font", "b", "i", "u", "a", "br"):
                # Clean attributes, keep only allowed ones
                if name == "font":
                    allowed_attrs = {}
                    if "color" in el.attrs:
                        allowed_attrs["color"] = el.attrs["color"]
                    el.attrs = allowed_attrs
                elif name == "a":
                    allowed_attrs = {}
                    if "href" in el.attrs:
                        allowed_attrs["href"] = el.attrs["href"]
                    el.attrs = allowed_attrs
                else:
                    el.attrs = {}
            else:
                el.unwrap()

        result = str(soup).strip()
        # Clean extra whitespace
        result = re.sub(r"\s+", " ", result)
        return result
