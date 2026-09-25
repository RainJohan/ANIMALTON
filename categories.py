"""
ANIMALTON — animal categories
--------------------------------
Groups the ~398 animal classes MobileNetV2/ImageNet can recognize into
specific, narrow categories (Lions, Tigers, Sharks, Snakes, Iguanas...)
instead of broad buckets.

MATCHING RULES:
  1. Dogs are matched by ImageNet INDEX (151-268), not keyword — 100%
     reliable regardless of breed name.
  2. SPECIES_OVERRIDES is checked next — exact species whose name
     legitimately contains another category's keyword as a substring
     (e.g. "tiger cat" contains "tiger" but is a domestic cat breed, not
     a tiger). Checked before anything else so these are never
     shadowed by a broader category's keyword.
  3. Everything else is matched by keyword against the CLEAN display
     label only (not the full raw ImageNet label with all its synonyms)
     — a species' synonyms can accidentally contain another animal's
     name (e.g. cougar's full ImageNet entry lists "mountain lion" as a
     synonym, koala's lists "koala bear") which caused real
     miscategorization bugs when matched against the full label. The
     clean label avoids that.
  4. Within step 3, order matters: more specific groups (sharks, sea
     lions) are checked BEFORE broader ones that share a word (tigers,
     lions) so "tiger shark" hits Sharks first, and "sea lion" hits Sea
     Mammals before the plain "lion" check ever runs.

This is a heuristic, not a scientific taxonomy — good enough for a game,
not a biology reference. New conflicts may still turn up; add them to
SPECIES_OVERRIDES as found.
"""

DOG_INDEX_START = 151
DOG_INDEX_END = 268  # inclusive

# Exact species-name conflicts — checked FIRST, before any generic
# keyword matching. key = substring to look for in the clean label
# (lowercase), value = the correct category key.
SPECIES_OVERRIDES = {
    "tiger cat": "cat",  # domestic cat breed, not a tiger
}

DOG_CATEGORY = {
    "key": "dog",
    "name": "Dogs",
    "emoji": "🐕",
    "description": "Domesticated canines bred over thousands of years into hundreds of distinct breeds, from tiny lapdogs to large working breeds.",
    "danger": "Low",
    "friendliness": "Very High",
    "keywords": [],
}

OTHER_CATEGORY = {
    "key": "other",
    "name": "Other Animals",
    "emoji": "🐾",
    "description": "Animals recognized that don't fit neatly into the categories above.",
    "danger": "Unknown",
    "friendliness": "Unknown",
    "keywords": [],
}

CATEGORY_LIST = [
    {"key": "shark", "name": "Sharks", "emoji": "🦈",
     "description": "Cartilaginous fish and apex ocean predators, ranging from harmless filter-feeders to powerful hunters.",
     "danger": "High", "friendliness": "Very Low",
     "keywords": ["shark", "hammerhead"]},

    {"key": "ray", "name": "Rays", "emoji": "🐠",
     "description": "Flat-bodied cartilaginous fish related to sharks, gliding along ocean floors.",
     "danger": "Medium", "friendliness": "Low",
     "keywords": ["stingray", "electric ray"]},

    {"key": "sea_mammal", "name": "Sea Mammals", "emoji": "🦭",
     "description": "Mammals adapted to life in or near the water, including sea lions and manatee relatives.",
     "danger": "Low", "friendliness": "Medium",
     "keywords": ["sea lion", "dugong"]},

    {"key": "lion", "name": "Lions", "emoji": "🦁",
     "description": "The only cat species that lives in social groups (prides). An apex predator capable of taking down large game.",
     "danger": "Very High", "friendliness": "Very Low",
     "keywords": ["lion"]},

    {"key": "tiger", "name": "Tigers", "emoji": "🐯",
     "description": "The largest cat species, a solitary and powerful ambush predator found across parts of Asia.",
     "danger": "Very High", "friendliness": "Very Low",
     "keywords": ["tiger"]},

    {"key": "jaguar", "name": "Jaguars", "emoji": "🐆",
     "description": "The largest cat in the Americas, with an exceptionally strong bite used to pierce turtle shells and skulls.",
     "danger": "High", "friendliness": "Very Low",
     "keywords": ["jaguar"]},

    {"key": "leopard", "name": "Leopards", "emoji": "🐆",
     "description": "A stealthy, solitary big cat known for dragging prey into trees to keep it from other predators.",
     "danger": "High", "friendliness": "Very Low",
     "keywords": ["leopard"]},

    {"key": "cheetah", "name": "Cheetahs", "emoji": "🐆",
     "description": "The fastest land animal, built for short explosive sprints rather than raw strength.",
     "danger": "Medium", "friendliness": "Low",
     "keywords": ["cheetah"]},

    {"key": "wild_cat_small", "name": "Wild Cats", "emoji": "🐈‍⬛",
     "description": "Medium-sized wild felines such as cougars and lynxes, more elusive than their larger cat relatives.",
     "danger": "Medium", "friendliness": "Low",
     "keywords": ["cougar", "lynx"]},

    {"key": "cat", "name": "Cats", "emoji": "🐈",
     "description": "Small domesticated felines known for independence, agility, and sharp hunting instincts even as pets.",
     "danger": "Low", "friendliness": "High",
     "keywords": ["tabby", "persian cat", "siamese cat", "egyptian cat"]},

    {"key": "wolf", "name": "Wolves & Wild Dogs", "emoji": "🐺",
     "description": "Wild canines that live and hunt in social packs, generally wary of humans.",
     "danger": "Medium", "friendliness": "Low",
     "keywords": ["wolf", "coyote", "dingo", "dhole", "hunting dog"]},

    {"key": "fox", "name": "Foxes", "emoji": "🦊",
     "description": "Small, adaptable wild canines found across much of the world, including urban areas.",
     "danger": "Low", "friendliness": "Low",
     "keywords": ["fox"]},

    {"key": "panda", "name": "Pandas", "emoji": "🐼",
     "description": "A bear species that feeds almost exclusively on bamboo. Solitary and generally non-aggressive.",
     "danger": "Medium", "friendliness": "Low",
     "keywords": ["panda"]},

    {"key": "bear", "name": "Bears", "emoji": "🐻",
     "description": "Large, powerful omnivores. Generally avoid humans but can be dangerous if surprised or provoked.",
     "danger": "High", "friendliness": "Very Low",
     "keywords": ["bear"]},

    {"key": "elephant", "name": "Elephants", "emoji": "🐘",
     "description": "The largest living land animals, highly intelligent and social, living in matriarch-led herds.",
     "danger": "Medium", "friendliness": "Medium",
     "keywords": ["elephant"]},

    {"key": "rhino", "name": "Rhinos", "emoji": "🦏",
     "description": "Large, thick-skinned herbivores with one or two horns, generally solitary and can charge if threatened.",
     "danger": "High", "friendliness": "Low",
     "keywords": ["rhinoceros"]},

    {"key": "hippo", "name": "Hippos", "emoji": "🦛",
     "description": "Large semi-aquatic mammals, considered one of the most dangerous animals in Africa despite being herbivorous.",
     "danger": "Very High", "friendliness": "Very Low",
     "keywords": ["hippopotamus"]},

    {"key": "giraffe", "name": "Giraffes", "emoji": "🦒",
     "description": "The tallest living land animal, using its long neck to browse leaves other herbivores can't reach.",
     "danger": "Low", "friendliness": "Medium",
     "keywords": ["giraffe"]},

    {"key": "zebra", "name": "Zebras", "emoji": "🦓",
     "description": "African relatives of the horse, known for distinctive black-and-white stripe patterns.",
     "danger": "Low", "friendliness": "Low",
     "keywords": ["zebra"]},

    {"key": "primate_ape", "name": "Apes", "emoji": "🦍",
     "description": "Humans' closest living relatives — highly intelligent, social, and in several species, tool-using.",
     "danger": "Medium", "friendliness": "Low",
     "keywords": ["gorilla", "chimpanzee", "orangutan", "gibbon", "siamang"]},

    {"key": "primate_monkey", "name": "Monkeys", "emoji": "🐒",
     "description": "Social, intelligent primates found across Africa, Asia and the Americas.",
     "danger": "Low", "friendliness": "Medium",
     "keywords": ["monkey", "macaque", "baboon", "marmoset", "colobus", "langur",
                  "guenon", "patas", "titi", "capuchin"]},

    {"key": "lemur", "name": "Lemurs", "emoji": "🐒",
     "description": "Primates native only to Madagascar, ranging from mouse-sized to cat-sized species.",
     "danger": "Very Low", "friendliness": "Medium",
     "keywords": ["lemur", "indri"]},

    {"key": "snake", "name": "Snakes", "emoji": "🐍",
     "description": "Legless reptiles ranging from harmless constrictors to highly venomous species.",
     "danger": "Medium", "friendliness": "Very Low",
     "keywords": ["snake", "cobra", "mamba", "viper", "python", "boa", "sidewinder",
                  "rattlesnake", "garter", "ringneck"]},

    {"key": "iguana", "name": "Iguanas", "emoji": "🦎",
     "description": "Large, herbivorous lizards found mainly in Central and South America, often docile despite their size.",
     "danger": "Low", "friendliness": "Medium",
     "keywords": ["iguana"]},

    {"key": "lizard", "name": "Lizards", "emoji": "🦎",
     "description": "A diverse group of scaled reptiles, from tiny geckos to the massive Komodo dragon.",
     "danger": "Medium", "friendliness": "Low",
     "keywords": ["gecko", "chameleon", "agama", "komodo", "whiptail", "gila monster",
                  "green lizard", "frilled lizard", "alligator lizard"]},

    {"key": "turtle", "name": "Turtles & Tortoises", "emoji": "🐢",
     "description": "Shelled reptiles found on land and in water, generally slow-moving and non-aggressive.",
     "danger": "Very Low", "friendliness": "Medium",
     "keywords": ["turtle", "terrapin", "tortoise"]},

    {"key": "crocodilian", "name": "Crocodiles & Alligators", "emoji": "🐊",
     "description": "Large aquatic reptiles and ambush predators, among the most dangerous reptiles to encounter.",
     "danger": "Very High", "friendliness": "Very Low",
     "keywords": ["crocodile", "alligator"]},

    {"key": "amphibian", "name": "Amphibians", "emoji": "🐸",
     "description": "Cold-blooded animals like frogs, toads and salamanders that typically live both in water and on land.",
     "danger": "Low", "friendliness": "Low",
     "keywords": ["frog", "toad", "salamander", "newt", "axolotl", "eft"]},

    {"key": "bird_of_prey", "name": "Birds of Prey", "emoji": "🦅",
     "description": "Sharp-taloned hunting birds with excellent eyesight, including eagles, hawks and owls.",
     "danger": "Low", "friendliness": "Low",
     "keywords": ["eagle", "hawk", "kite", "vulture", "owl"]},

    {"key": "parrot", "name": "Parrots", "emoji": "🦜",
     "description": "Colorful, highly intelligent birds known for mimicking sounds and forming strong social bonds.",
     "danger": "Very Low", "friendliness": "High",
     "keywords": ["parrot", "macaw", "cockatoo", "lorikeet"]},

    {"key": "penguin", "name": "Penguins", "emoji": "🐧",
     "description": "Flightless, tuxedo-patterned birds built for swimming rather than flying.",
     "danger": "Very Low", "friendliness": "Medium",
     "keywords": ["penguin"]},

    {"key": "water_bird", "name": "Water Birds", "emoji": "🦢",
     "description": "Birds adapted to life on or near water, including geese, swans, ducks and wading birds.",
     "danger": "Very Low", "friendliness": "Medium",
     "keywords": ["goose", "swan", "duck", "stork", "crane", "flamingo", "pelican",
                  "albatross", "drake", "merganser"]},

    {"key": "bird_other", "name": "Birds", "emoji": "🐦",
     "description": "Feathered, egg-laying vertebrates found on every continent, from tiny songbirds to farmyard fowl.",
     "danger": "Very Low", "friendliness": "Medium",
     "keywords": ["finch", "robin", "jay", "magpie", "chickadee", "bulbul", "hummingbird",
                  "toucan", "hornbill", "jacamar", "bunting", "brambling", "ptarmigan",
                  "grouse", "quail", "partridge", "chicken", "hen", "rooster", "peacock",
                  "coucal", "water ouzel"]},

    {"key": "spider", "name": "Spiders & Scorpions", "emoji": "🕷️",
     "description": "Eight-legged arachnids — most are harmless to humans, though a few species are venomous.",
     "danger": "Medium", "friendliness": "Very Low",
     "keywords": ["spider", "tick", "scorpion", "tarantula", "harvestman", "black widow"]},

    {"key": "insect", "name": "Insects", "emoji": "🐛",
     "description": "Small six-legged invertebrates, among the most numerous and diverse animals on Earth.",
     "danger": "Low", "friendliness": "Very Low",
     "keywords": ["beetle", "ant", "bee", "wasp", "cockroach", "mantis", "cricket",
                  "grasshopper", "cicada", "dragonfly", "damselfly", "butterfly", "moth",
                  "fly", "stick insect", "lacewing", "leafhopper"]},

    {"key": "fish", "name": "Fish", "emoji": "🐟",
     "description": "Aquatic, gill-breathing animals found in oceans, rivers and lakes worldwide.",
     "danger": "Low", "friendliness": "Low",
     "keywords": ["goldfish", "tench", "eel", "salmon", "trout", "sturgeon", "puffer",
                  "anemone fish", "gar", "coelacanth"]},

    {"key": "sea_creature", "name": "Sea Creatures", "emoji": "🦀",
     "description": "Ocean-dwelling invertebrates including crabs, starfish, jellyfish and mollusks.",
     "danger": "Low", "friendliness": "Very Low",
     "keywords": ["starfish", "coral", "jellyfish", "lobster", "crab", "crayfish",
                  "hermit crab", "conch", "snail", "slug", "nautilus", "sea urchin",
                  "sea cucumber"]},

    {"key": "marsupial", "name": "Marsupials", "emoji": "🦘",
     "description": "Pouched mammals native mainly to Australia, carrying and nursing their young in a pouch.",
     "danger": "Low", "friendliness": "Medium",
     "keywords": ["kangaroo", "koala", "wombat", "wallaby"]},

    {"key": "small_predator", "name": "Small Predators", "emoji": "🦡",
     "description": "Small to medium carnivorous mammals such as weasels, badgers and raccoons.",
     "danger": "Low", "friendliness": "Low",
     "keywords": ["weasel", "mink", "polecat", "ferret", "badger", "skunk", "mongoose",
                  "meerkat", "raccoon", "otter"]},

    {"key": "small_mammal", "name": "Small Mammals", "emoji": "🐿️",
     "description": "Small mammals like squirrels, rabbits and hedgehogs, generally harmless to humans.",
     "danger": "Very Low", "friendliness": "Medium",
     "keywords": ["squirrel", "chipmunk", "hare", "rabbit", "hamster", "guinea pig",
                  "beaver", "marmot", "porcupine", "hedgehog"]},

    {"key": "farm", "name": "Farm & Livestock", "emoji": "🐄",
     "description": "Animals commonly raised by humans for agriculture, work or companionship.",
     "danger": "Low", "friendliness": "High",
     "keywords": ["ox", "water buffalo", "bison", "ram", "bighorn", "ibex", "camel",
                  "llama", "pig", "hog", "boar", "warthog", "sorrel"]},

    {"key": "deer_antelope", "name": "Deer & Antelope", "emoji": "🦌",
     "description": "Hoofed grazing mammals found across forests and grasslands worldwide.",
     "danger": "Low", "friendliness": "Low",
     "keywords": ["deer", "moose", "elk", "antelope", "hartebeest", "impala", "gazelle"]},

    {"key": "monotreme", "name": "Platypus & Echidna", "emoji": "🦔",
     "description": "Egg-laying mammals found only in Australia and New Guinea — a biological rarity.",
     "danger": "Low", "friendliness": "Low",
     "keywords": ["platypus", "echidna"]},

    {"key": "armadillo", "name": "Armadillos", "emoji": "🦔",
     "description": "Armored mammals that curl into a ball for defense against predators.",
     "danger": "Very Low", "friendliness": "Low",
     "keywords": ["armadillo"]},
]

CATEGORIES = {c["key"]: c for c in CATEGORY_LIST}
CATEGORIES["dog"] = DOG_CATEGORY
CATEGORIES["other"] = OTHER_CATEGORY


def categorize(label, imagenet_index=None):
    if imagenet_index is not None and DOG_INDEX_START <= imagenet_index <= DOG_INDEX_END:
        return "dog"

    lower = label.lower().strip()

    for override_kw, cat_key in SPECIES_OVERRIDES.items():
        if override_kw in lower:
            return cat_key

    for cat in CATEGORY_LIST:
        for kw in cat["keywords"]:
            if kw in lower:
                return cat["key"]
    return "other"