"""
Google Workspace A2UI CardService Pydantic Schemas.
Architecture "Genome" (Phase 1) - Razum Google AI PRO.

Aesthetic Tokens:
- Obsidian: #0a0a0c
- Neon Cyan: #00f0ff
- Gold (Klimt / Ver Sacrum): #d4af37
- Steel Muted: #8a8f98
- Deep Dark Surface: #121216
"""

from typing import List, Optional, Literal, Dict, Any, Union
from pydantic import BaseModel, Field, model_validator, HttpUrl
import json

# Visual Palette Tokens
COLOR_OBSIDIAN = "#0a0a0c"
COLOR_NEON_CYAN = "#00f0ff"
COLOR_KLIMT_GOLD = "#d4af37"
COLOR_MUTED_STEEL = "#8a8f98"
COLOR_DARK_SURFACE = "#121216"


class Color(BaseModel):
    """Google Card Color (RGB normalized 0.0 - 1.0 or hex conversion)."""
    red: float = Field(default=0.0, ge=0.0, le=1.0)
    green: float = Field(default=0.0, ge=0.0, le=1.0)
    blue: float = Field(default=0.0, ge=0.0, le=1.0)
    alpha: float = Field(default=1.0, ge=0.0, le=1.0)

    @classmethod
    def from_hex(cls, hex_str: str) -> "Color":
        h = hex_str.lstrip('#')
        if len(h) == 6:
            r = int(h[0:2], 16) / 255.0
            g = int(h[2:4], 16) / 255.0
            b = int(h[4:6], 16) / 255.0
            return cls(red=round(r, 3), green=round(g, 3), blue=round(b, 3), alpha=1.0)
        return cls(red=0.0, green=0.94, blue=1.0, alpha=1.0)


class Icon(BaseModel):
    """Google Card Icon widget component."""
    knownIcon: Optional[str] = None
    iconUrl: Optional[str] = None
    altText: Optional[str] = None
    imageType: Optional[Literal["SQUARE", "CIRCLE"]] = "SQUARE"


class OpenLink(BaseModel):
    """Link trigger for buttons and interactive elements."""
    url: str
    openAs: Optional[Literal["FULL_SIZE", "OVERLAY"]] = "FULL_SIZE"
    onClose: Optional[Literal["NOTHING", "RELOAD"]] = "NOTHING"


class ActionParameter(BaseModel):
    key: str
    value: str


class CardAction(BaseModel):
    """Google Workspace interactive action hook."""
    actionMethodName: str
    parameters: Optional[List[ActionParameter]] = None


class OnClick(BaseModel):
    openLink: Optional[OpenLink] = None
    action: Optional[CardAction] = None


class Button(BaseModel):
    """Interactive Button component."""
    text: str
    icon: Optional[Icon] = None
    color: Optional[Color] = None
    onClick: Optional[OnClick] = None
    disabled: Optional[bool] = False
    altText: Optional[str] = None


class ButtonList(BaseModel):
    """Container for one or more action buttons."""
    buttons: List[Button] = Field(default_factory=list)


class SwitchControl(BaseModel):
    name: str
    value: Optional[str] = None
    selected: Optional[bool] = False
    onChangeAction: Optional[CardAction] = None
    controlType: Optional[Literal["SWITCH", "CHECK_BOX"]] = "SWITCH"


class TextParagraph(BaseModel):
    """
    Standard text paragraph supporting allowed Google Workspace HTML tags:
    <b>, <i>, <u>, <font color="...">, <a href="...">, <br>
    """
    text: str


class DecoratedText(BaseModel):
    """Rich information row with optional icons, top/bottom labels, and button."""
    topLabel: Optional[str] = None
    text: str
    bottomLabel: Optional[str] = None
    startIcon: Optional[Icon] = None
    endIcon: Optional[Icon] = None
    button: Optional[Button] = None
    switchControl: Optional[SwitchControl] = None
    wrapText: Optional[bool] = True
    onClick: Optional[OnClick] = None


class Image(BaseModel):
    """Image widget for visual media display."""
    imageUrl: str
    altText: Optional[str] = "Visual component"
    onClick: Optional[OnClick] = None


class Divider(BaseModel):
    """Horizontal divider line."""
    dividerType: Optional[str] = "SOLID_DIVIDER"


class Widget(BaseModel):
    """
    Google Workspace Card Widget union.
    Must contain exactly one widget payload.
    """
    textParagraph: Optional[TextParagraph] = None
    decoratedText: Optional[DecoratedText] = None
    buttonList: Optional[ButtonList] = None
    image: Optional[Image] = None
    divider: Optional[Dict[str, Any]] = None

    @model_validator(mode="after")
    def validate_single_widget(self) -> "Widget":
        active_fields = [
            k for k in ["textParagraph", "decoratedText", "buttonList", "image", "divider"]
            if getattr(self, k) is not None
        ]
        if not active_fields:
            raise ValueError("Widget must have at least one active component.")
        return self


class Section(BaseModel):
    """Card Section grouping multiple widgets."""
    header: Optional[str] = None
    widgets: List[Widget] = Field(default_factory=list)
    collapsible: Optional[bool] = False
    uncollapsibleWidgetsCount: Optional[int] = None


class CardHeader(BaseModel):
    """Card Header with title, subtitle, and avatar/icon."""
    title: str
    subtitle: Optional[str] = None
    imageUrl: Optional[str] = None
    imageType: Optional[Literal["SQUARE", "CIRCLE"]] = "CIRCLE"
    imageAltText: Optional[str] = None


class Card(BaseModel):
    """Core Google Workspace Card Model."""
    header: Optional[CardHeader] = None
    sections: List[Section] = Field(default_factory=list)
    cardActions: Optional[List[Dict[str, Any]]] = None
    name: Optional[str] = "GenomeCard"


class CardItemV2(BaseModel):
    """CardV2 wrapper for Google Chat and Workspace Add-ons."""
    cardId: str = "genome_card_v2"
    card: Card


class GoogleWorkspaceCardMessage(BaseModel):
    """Root JSON Envelope for Google Workspace / Chat webhook dispatch."""
    cardsV2: List[CardItemV2] = Field(default_factory=list)
    text: Optional[str] = None

    def to_json_dict(self) -> Dict[str, Any]:
        """Serialize clean dictionary excluding unset nulls for CardService."""
        return self.model_dump(exclude_none=True, by_alias=True)

    def to_json_str(self, indent: int = 2) -> str:
        return json.dumps(self.to_json_dict(), indent=indent, ensure_ascii=False)


# Cyber-Minimalism & Klimt Gold Builders
def make_genome_header(title: str, subtitle: Optional[str] = None, icon_url: Optional[str] = None) -> CardHeader:
    """Creates a stylized header with Neon Cyan / Gold palette hints."""
    klimt_title = f'<font color="{COLOR_KLIMT_GOLD}">✦</font> {title}'
    cyan_subtitle = f'<font color="{COLOR_NEON_CYAN}">{subtitle}</font>' if subtitle else None
    return CardHeader(
        title=klimt_title,
        subtitle=cyan_subtitle,
        imageUrl=icon_url,
        imageType="CIRCLE"
    )


def make_cyber_button(text: str, url: str, is_gold: bool = False) -> Button:
    """Creates a high-contrast action button with Cyber Cyan or Gold accent."""
    color_hex = COLOR_KLIMT_GOLD if is_gold else COLOR_NEON_CYAN
    return Button(
        text=text,
        color=Color.from_hex(color_hex),
        onClick=OnClick(openLink=OpenLink(url=url))
    )


# --- Intermediate Representation (IR) Schemas for A2UI Generation ---

class WidgetButton(BaseModel):
    text: str
    action_type: str = "OPEN_URL"
    url: Optional[str] = None
    on_click_custom_fn: Optional[str] = None


class CardWidget(BaseModel):
    widget_type: str = Field(..., description="textParagraph, decoratedText, buttonList")
    text: Optional[str] = None
    top_label: Optional[str] = None
    bottom_label: Optional[str] = None
    icon_url: Optional[str] = None
    buttons: Optional[List[WidgetButton]] = None


class CardSection(BaseModel):
    header: Optional[str] = None
    collapsible: bool = False
    widgets: List[CardWidget]


class A2UICardPayload(BaseModel):
    card_id: str
    title: str
    subtitle: Optional[str] = None
    style_theme: str = "OBSIDIAN_CYAN"  # Наш корпоративный стиль
    sections: List[CardSection]

    def to_card_service_message(self) -> GoogleWorkspaceCardMessage:
        """
        Converts intermediate A2UICardPayload directly into fully validated
        Google Workspace CardService JSON (cardsV2) with Cyber-minimalist branding.
        """
        is_gold_theme = "GOLD" in self.style_theme.upper()
        primary_color_hex = COLOR_KLIMT_GOLD if is_gold_theme else COLOR_NEON_CYAN

        # Header with branding
        header = make_genome_header(title=self.title, subtitle=self.subtitle)

        gw_sections: List[Section] = []
        for sec in self.sections:
            gw_widgets: List[Widget] = []
            for w in sec.widgets:
                wtype = w.widget_type.lower()
                if wtype in ("textparagraph", "text", "paragraph", "p"):
                    gw_widgets.append(Widget(
                        textParagraph=TextParagraph(text=w.text or "")
                    ))
                elif wtype in ("decoratedtext", "decorated"):
                    start_icon = Icon(iconUrl=w.icon_url) if w.icon_url else None
                    gw_widgets.append(Widget(
                        decoratedText=DecoratedText(
                            topLabel=w.top_label,
                            text=w.text or "",
                            bottomLabel=w.bottom_label,
                            startIcon=start_icon
                        )
                    ))
                elif wtype in ("buttonlist", "buttons"):
                    gw_buttons: List[Button] = []
                    for b in (w.buttons or []):
                        onclick_obj = None
                        if b.action_type == "CUSTOM_FN" and b.on_click_custom_fn:
                            onclick_obj = OnClick(action=CardAction(actionMethodName=b.on_click_custom_fn))
                        else:
                            onclick_obj = OnClick(openLink=OpenLink(url=b.url or "#"))

                        gw_buttons.append(Button(
                            text=b.text,
                            color=Color.from_hex(primary_color_hex),
                            onClick=onclick_obj
                        ))
                    if gw_buttons:
                        gw_widgets.append(Widget(buttonList=ButtonList(buttons=gw_buttons)))

            if gw_widgets:
                gw_sections.append(Section(
                    header=sec.header,
                    collapsible=sec.collapsible,
                    widgets=gw_widgets
                ))

        card = Card(
            name=self.card_id,
            header=header,
            sections=gw_sections
        )

        return GoogleWorkspaceCardMessage(
            cardsV2=[CardItemV2(cardId=self.card_id, card=card)]
        )

