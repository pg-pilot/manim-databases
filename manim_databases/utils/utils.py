from __future__ import annotations

from manim import (
    RED,
    UP,
    Create,
    FadeOut,
    ManimColor,
    Text,
    VMobject,
    override_animate,
)
from manim.typing import Vector3D


def set_text(old_manim_text: Text, new_text: str) -> Text:
    """Replace the content of a Manim Text object while preserving its style.

    Manim's :meth:`Text.set_text` does not always rerender correctly. This
    helper builds a new Text with the same font, size, weight, color, and
    position as the original.

    Parameters
    ----------
    old_manim_text : Text
        The original Text object whose content is being replaced.
    new_text : str
        The new text content.

    Returns
    -------
    Text
        A new Text object with updated content matching the original style.
    """
    NewText = type(old_manim_text)
    return (
        NewText(
            str(new_text),
            font=old_manim_text.font,
            font_size=old_manim_text.font_size,
            weight=old_manim_text.weight,
        )
        .match_style(old_manim_text)
        .move_to(old_manim_text)
    )


class Labelable:
    """Mixin that adds an optional label to a mobject.

    Attributes
    ----------
    label : Text or None
        The label associated with the object, or ``None`` if no label is set.
    """

    def __init__(self):
        super().__init__()
        self.label = None

    def add_label(
        self,
        text: Text,
        direction: Vector3D = UP,
        buff: float = 0.5,
        **kwargs,
    ) -> Labelable:
        """Add a label positioned relative to the object.

        Parameters
        ----------
        text : Text
            The label text.
        direction : Vector3D, optional
            Direction to place the label relative to the object. Default ``UP``.
        buff : float, optional
            Distance between the object and the label. Default ``0.5``.
        """
        self.label = text
        self.label.next_to(self, direction, buff, **kwargs)
        return self

    def has_label(self) -> bool:
        """Return ``True`` if the object has a label."""
        return self.label is not None


class Highlightable:
    """Mixin that adds highlight/unhighlight behavior to a mobject.

    A highlight is a transparent overlay stroke around a target VMobject. The
    target is supplied via :meth:`_add_highlight`.

    Attributes
    ----------
    highlighting : VMobject or None
        The highlight overlay, or ``None`` if highlighting is not initialized.
    """

    def __init__(self):
        super().__init__()
        self.__target = None
        self.highlighting = None

    def _add_highlight(self, target: VMobject):
        """Initialize the highlight overlay for a target VMobject."""
        self.__target = target
        self.highlighting = (
            target.copy().set_fill(opacity=0).set_z_index(self.__target.z_index + 1)
        )
        self.set_highlight()

    def highlight(
        self,
        stroke_color: ManimColor = RED,
        stroke_width: float = 8,
    ) -> Highlightable:
        """Apply a highlight stroke to the target."""
        self.set_highlight(stroke_color, stroke_width)
        self.highlighting.width = self.__target.width
        self.highlighting.height = self.__target.height
        self.highlighting.move_to(self.__target)
        self += self.highlighting
        return self

    @override_animate(highlight)
    def _highlight_animation(
        self,
        stroke_color: ManimColor = RED,
        stroke_width: float = 8,
        anim_args: dict = None,
    ) -> Create:
        if anim_args is None:
            anim_args = {}
        self.highlight(stroke_color, stroke_width)
        return Create(self.highlighting, **anim_args)

    def set_highlight(
        self,
        stroke_color: ManimColor = RED,
        stroke_width: float = 8,
    ):
        """Configure the highlight stroke color and width."""
        self.highlighting.set_stroke(stroke_color, stroke_width)

    def unhighlight(self) -> Highlightable:
        """Remove the highlight overlay."""
        self -= self.highlighting
        return self

    @override_animate(unhighlight)
    def _unhighlight_animation(self, anim_args: dict = None) -> FadeOut:
        if anim_args is None:
            anim_args = {}
        self.unhighlight()
        return FadeOut(self.highlighting, **anim_args)
