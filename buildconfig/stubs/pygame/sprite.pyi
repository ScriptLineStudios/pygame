"""
pygame module with basic game object classes

This module contains several simple classes to be used within games. There
are the main Sprite class and several Group classes that contain Sprites.
The use of these classes is entirely optional when using Pygame. The classes
are fairly lightweight and only provide a starting place for the code
that is common to most games.

The Sprite class is intended to be used as a base class for the different
types of objects in the game. There is also a base Group class that simply
stores sprites. A game could create new types of Group classes that operate
on specially customized Sprite instances they contain.

The basic Sprite class can draw the Sprites it contains to a Surface. The
Group.draw() method requires that each Sprite have a Surface.image attribute
and a Surface.rect. The Group.clear() method requires these same attributes
and can be used to erase all the Sprites with background. There are also
more advanced Groups: pygame.sprite.RenderUpdates() and
pygame.sprite.OrderedUpdates().

Lastly, this module contains several collision functions. These help find
sprites inside multiple groups that have intersecting bounding rectangles.
To find the collisions, the Sprites are required to have a Surface.rect
attribute assigned.

The groups are designed for high efficiency in removing and adding Sprites
to them. They also allow cheap testing to see if a Sprite already exists in
a Group. A given Sprite can exist in any number of groups. A game could use
some groups to control object rendering, and a completely separate set of
groups to control interaction or player movement. Instead of adding type
attributes or bools to a derived Sprite class, consider keeping the
Sprites inside organized Groups. This will allow for easier lookup later
in the game.

Sprites and Groups manage their relationships with the add() and remove()
methods. These methods can accept a single or multiple group arguments for
membership.  The default initializers for these classes also take a
single group or list of groups as arguments for initial membership. It is safe
to repeatedly add and remove the same Sprite from a Group.

While it is possible to design sprite and group classes that don't derive
from the Sprite and AbstractGroup classes below, it is strongly recommended
that you extend those when you create a new Sprite or Group class.

Sprites are not thread safe, so lock them yourself if using threads.

"""

from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    SupportsFloat,
    Tuple,
    Union,
)

from pygame.rect import Rect
from pygame.surface import Surface

from ._common import RectValue

class Sprite:
    image: Optional[Surface] = None
    rect: Optional[Rect] = None
    @property
    def layer(self) -> int: ...
    @layer.setter
    def layer(self, value: int) -> None: ...
    def __init__(self, *groups: AbstractGroup) -> None: ...
    def add_internal(self, group: AbstractGroup) -> None: ...
    def remove_internal(self, group: AbstractGroup) -> None: ...
    def update(self, *args: Any, **kwargs: Any) -> None: ...
    def add(self, *groups: AbstractGroup) -> None: ...
    def remove(self, *groups: AbstractGroup) -> None: ...
    def kill(self) -> None: ...
    def alive(self) -> bool: ...
    def groups(self) -> List[AbstractGroup]: ...

class DirtySprite(Sprite):
    dirty: int
    blendmode: int
    source_rect: Rect
    visible: int
    _layer: int
    def _set_visible(self, val: int) -> None: ...
    def _get_visible(self) -> int: ...

class AbstractGroup:
    spritedict: Dict[Sprite, Rect]
    lostsprites: List[int]  # I think
    def __init__(self) -> None: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[Sprite]: ...
    def __nonzero__(self) -> bool: ...
    __bool__ = __nonzero__
    def __contains__(self, item: Any) -> bool: ...
    def add_internal(self, sprite: Sprite, layer: None = None) -> None: ...
    def remove_internal(self, sprite: Sprite) -> None: ...
    def has_internal(self, sprite: Sprite) -> bool: ...
    def copy(self) -> AbstractGroup: ...
    def sprites(self) -> List[Sprite]: ...
    def add(
        self,
        *sprites: Union[Sprite, AbstractGroup, Iterable[Union[Sprite, AbstractGroup]]]
    ) -> None: ...
    def remove(self, *sprites: Sprite) -> None: ...
    def has(self, *sprites: Sprite) -> bool: ...
    def update(self, *args: Any, **kwargs: Any) -> None: ...
    def draw(self, surface: Surface) -> List[Rect]: ...
    def clear(self, surface: Surface, bgd: Surface) -> None: ...
    def empty(self) -> None: ...

class Group(AbstractGroup):
    def __init__(self, *sprites: Union[Sprite, Sequence[Sprite]]) -> None: ...
    def copy(self) -> Group: ...

class RenderPlain(Group):
    def copy(self) -> RenderPlain: ...

class RenderClear(Group):
    def copy(self) -> RenderClear: ...

class RenderUpdates(Group):
    def copy(self) -> RenderUpdates: ...
    def draw(self, surface: Surface) -> List[Rect]: ...

class OrderedUpdates(RenderUpdates):
    def copy(self) -> OrderedUpdates: ...

class LayeredUpdates(AbstractGroup):
    def __init__(self, *sprites: Sprite, **kwargs: Any) -> None: ...
    def copy(self) -> LayeredUpdates: ...
    def add(
        self,
        *sprites: Union[Sprite, AbstractGroup, Iterable[Union[Sprite, AbstractGroup]]],
        **kwargs: Any
    ) -> None: ...
    def draw(self, surface: Surface) -> List[Rect]: ...
    def get_sprites_at(
        self, pos: Union[Tuple[int, int], List[int]]
    ) -> List[Sprite]: ...
    def get_sprite(self, idx: int) -> Sprite: ...
    def remove_sprites_of_layer(self, layer_nr: int) -> List[Sprite]: ...
    def layers(self) -> List[int]: ...
    def change_layer(self, sprite: Sprite, new_layer: int) -> None: ...
    def get_layer_of_sprite(self, sprite: Sprite) -> int: ...
    def get_top_layer(self) -> int: ...
    def get_bottom_layer(self) -> int: ...
    def move_to_front(self, sprite: Sprite) -> None: ...
    def move_to_back(self, sprite: Sprite) -> None: ...
    def get_top_sprite(self) -> Sprite: ...
    def get_sprites_from_layer(self, layer: int) -> List[Sprite]: ...
    def switch_layer(self, layer1_nr: int, layer2_nr: int) -> None: ...

class LayeredDirty(LayeredUpdates):
    def __init__(self, *sprites: DirtySprite, **kwargs: Any) -> None: ...
    def copy(self) -> LayeredDirty: ...
    def draw(self, surface: Surface, bgd: Optional[Surface] = None) -> List[Rect]: ...
    def clear(self, surface: Surface, bgd: Surface) -> None: ...
    def repaint_rect(self, screen_rect: RectValue) -> None: ...
    def set_clip(self, screen_rect: Optional[RectValue] = None) -> None: ...
    def get_clip(self) -> Rect: ...
    def set_timing_treshold(
        self, time_ms: SupportsFloat
    ) -> None: ...  # This actually accept any value
    def set_timing_threshold(
        self, time_ms: SupportsFloat
    ) -> None: ...  # This actually accept any value

class GroupSingle(AbstractGroup):
    sprite: Sprite
    def __init__(self, sprite: Optional[Sprite] = None) -> None: ...
    def copy(self) -> GroupSingle: ...

def spritecollide(
    sprite: Sprite,
    group: AbstractGroup,
    dokill: bool,
    collided: Optional[Callable[[Sprite, Sprite], bool]] = None,
) -> List[Sprite]: ...
def collide_rect(left: Sprite, right: Sprite) -> bool: ...

class collide_rect_ratio:
    ratio: float
    def __init__(self, ratio: float) -> None: ...
    def __call__(self, left: Sprite, right: Sprite) -> bool: ...

def collide_circle(left: Sprite, right: Sprite) -> bool: ...

class collide_circle_ratio:
    ratio: float
    def __init__(self, ratio: float) -> None: ...
    def __call__(self, left: Sprite, right: Sprite) -> bool: ...

def collide_mask(left: Sprite, right: Sprite) -> Tuple[int, int]: ...
def groupcollide(
    groupa: AbstractGroup,
    groupb: AbstractGroup,
    dokilla: bool,
    dokillb: bool,
    collided: Optional[Callable[[Sprite, Sprite], bool]] = None,
) -> Dict[Sprite, Sprite]: ...
def spritecollideany(
    sprite: Sprite,
    group: AbstractGroup,
    collided: Optional[Callable[[Sprite, Sprite], bool]] = None,
) -> Sprite: ...