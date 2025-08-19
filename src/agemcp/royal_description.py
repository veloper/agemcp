import random, secrets

from typing import ClassVar, List


class RoyalDescription:
    """
    Provides canonical adjective order arrays for English noun phrase construction.

    This class encapsulates the canonical ordering of English adjectives for noun phrase generation,
    using class-level lists for each adjective category (quantity, quality, size, age, shape, color,
    origin, material, purpose, and noun). These lists are typed with `ClassVar[List[str]]` for clarity
    and type safety, but the class does not use generics or TypeVar. All adjective categories are
    fixed and idiomatic for English usage.

    Methods in this class allow for random selection and generation of noun phrases following
    canonical adjective order, including reversed order for stylistic variation.

    Instance Methods:
        choose(index: int): Selects a random adjective from the reversed canonical order at the given index.

    Class Methods:
        canonical_order_adjectives(): Returns the canonical order of adjective categories.
        reversed_canonical_order_adjectives(): Returns the reversed canonical order of adjective categories.
        generate(words=10, delimiter=' '): Generates a random noun phrase using the canonical adjective order.

    Attributes:
        quantity (ClassVar[List[str]]): Adjectives describing quantity.
        quality (ClassVar[List[str]]): Adjectives describing quality.
        size (ClassVar[List[str]]): Adjectives describing size.
        age (ClassVar[List[str]]): Adjectives describing age.
        shape (ClassVar[List[str]]): Adjectives describing shape.
        color (ClassVar[List[str]]): Adjectives describing color.
        origin (ClassVar[List[str]]): Adjectives describing origin.
        material (ClassVar[List[str]]): Adjectives describing material.
        purpose (ClassVar[List[str]]): Adjectives describing purpose.
        noun (ClassVar[List[str]]): Nouns for phrase construction.

    Example:
        >>> RoyalDescription.generate(words=5)
        'ancient blue french silk ox'
    """

    quantity : ClassVar[List[str]] = [ "one", "two", "several", "many", "few", "hundred", "dozen", "all", "some", "no" ]
    quality  : ClassVar[List[str]] = [ "lovely", "horrible", "delightful", "awful", "magnificent", "mediocre", "splendid", "terrible", "charming", "dreadful" ]
    size     : ClassVar[List[str]] = [ "tiny", "small", "medium", "large", "huge", "gigantic", "minuscule", "massive", "petite", "enormous" ]
    age      : ClassVar[List[str]] = [ "young", "old", "ancient", "modern", "new", "antique", "recent", "medieval", "vintage", "prehistoric" ]
    shape    : ClassVar[List[str]] = [ "round", "square", "rectangular", "triangular", "flat", "bulky", "slender", "curved", "pointed", "oval" ]
    color    : ClassVar[List[str]] = [ "red", "green", "blue", "yellow", "black", "white", "purple", "orange", "pink", "gray" ]
    origin   : ClassVar[List[str]] = [
        "french", "american", "chinese", "egyptian", "greek", "roman", "japanese", "german", "russian", "brazilian",
        "italian", "spanish", "british", "scottish", "irish", "welsh", "swiss", "swedish", "norwegian", "danish",
        "finnish", "icelandic", "polish", "czech", "slovak", "hungarian", "austrian", "belgian", "dutch", "portuguese",
        "turkish", "persian", "arabic", "hebrew", "syrian", "lebanese", "iraqi", "iranian", "pakistani", "indian",
        "bangladeshi", "sri_lankan", "nepali", "tibetan", "mongolian", "korean", "thai", "vietnamese", "filipino", "malaysian",
        "indonesian", "australian", "new_zealander", "canadian", "mexican", "argentinian", "chilean", "colombian", "peruvian", "venezuelan",
        "ecuadorian", "bolivian", "paraguayan", "uruguayan", "panamanian", "cuban", "jamaican", "haitian", "dominican", "puerto_rican",
        "nigerian", "ethiopian", "kenyan", "tanzanian", "ugandan", "ghanaian", "ivorian", "senegalese", "algerian", "moroccan",
        "tunisian", "libyan", "sudanese", "somali", "south_african", "zimbabwean", "zambian", "botswanan", "namibian", "angolan",
        "mozambican", "madagascan", "cameroonian", "congolese", "rwandan", "burundian", "malian", "nigerien", "chadian", "central_african",
        "gabonese", "guinean", "sierra_leonean", "liberian", "beninese", "togolese", "burkinabe", "mauritanian", "gambian"
    ]
    material : ClassVar[List[str]] = [ "tin", "wax", "fur", "ice", "gem", "oil", "tar", "net", "ash", "mud", "cot", "mat", "silk", "wool", "rub", "tin", "oak", "elm", "ivy", "pea", "cot", "den", "fib", "gum", "hay", "jet", "lid", "mat", "oak", "pad", "rag", "sap", "tan", "urn", "vat", "web", "yam", "zip", "clay", "sand" ]
    purpose  : ClassVar[List[str]] = [ "baking", "camping", "climbing", "cooking", "cutting", "diving", "drying", "eating", "fishing", "gardening", "grating", "growing", "hiking", "hunting", "icing", "jogging", "knitting", "marinating", "measuring", "mixing", "nursing", "opening", "painting", "piping", "pouring", "quilting", "racing", "reading", "riding", "rowing", "running", "sailing", "serving", "sewing", "shopping", "sleeping", "sowing", "stirring", "studying", "swimming", "teaching", "timing", "training", "traveling", "typing", "voting", "walking", "washing", "watering", "wiring" ]
    noun     : ClassVar[List[str]] = [ "ox", "id", "ax", "boy", "toy", "ant", "bee", "pig", "hen", "owl", "fox", "cow", "yak", "ram", "kid", "mob", "cop", "dad", "mom", "nun", "son", "pal", "gal", "guy", "lad", "kin", "doc", "don", "dan", "sir", "spy", "vet", "sub", "bud", "cub", "con", "cam", "cab", "bin", "bob", "bun", "bug", "bear", "bull", "deer", "duck", "goat", "king", "lady", "lion", "lord", "maid", "monk", "pope", "stag", "wolf", "hero", "guru", "jury", "pawn", "knob", "sage", "seer", "twin", "wife", "yogi", "yarn", "yawn" ]
    
    
    def choose(self, index: int) -> str:
        if not (0 <= index <= 8):
            raise ValueError("Index must be between 0 and 8.")
        adjectives = self.reversed_canonical_order_adjectives()[index]
        return secrets.choice(adjectives)

    @classmethod
    def canonical_order_adjectives(cls) -> List[List[str]]:
        return [ cls.quantity, cls.quality, cls.size, cls.age, cls.shape, cls.color, cls.origin, cls.material, cls.purpose ]
    
    @classmethod
    def reversed_canonical_order_adjectives(cls) -> List[List[str]]:
        return list(reversed(cls.canonical_order_adjectives()))

    @classmethod
    def generate(cls, words=10, delimiter=' ') -> str:
        if not (1 <= words <= 10):
            raise ValueError("Number of words must be between 1 and 10.")
        parts = [random.choice(cls.noun)]
        for i in range(words - 1):
            adjectives = cls.reversed_canonical_order_adjectives()[i]
            adjective = random.choice(adjectives)
            parts.insert(0, adjective)
        return delimiter.join(parts)
