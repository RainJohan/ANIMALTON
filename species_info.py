"""
ANIMALTON — per-species info
--------------------------------
Individual description + danger/friendliness rating for specific species,
since lumping all dogs (or all birds) together hides real differences.

NOTE on dog breed ratings: temperament depends heavily on individual
upbringing, training and socialization — these ratings describe general
tendencies relevant to a casual encounter, not a claim that any breed is
inherently dangerous or universally friendly.

Species not listed here fall back to their category's general info.
"""

SPECIES_INFO = {
    # --- Dog breeds ---
    "pomeranian": {
        "description": "A tiny, fluffy toy breed with a fox-like face, bred down from larger Arctic sled dogs. Known for a big, confident personality in a small body.",
        "danger": "Very Low", "friendliness": "Very High"},
    "golden retriever": {
        "description": "A large, friendly sporting breed originally bred to retrieve game for hunters. Famous for being gentle with children and easy to train.",
        "danger": "Very Low", "friendliness": "Very High"},
    "labrador retriever": {
        "description": "One of the most popular family dogs worldwide — energetic, food-motivated, and typically very sociable.",
        "danger": "Very Low", "friendliness": "Very High"},
    "siberian husky": {
        "description": "A medium-large working breed built for pulling sleds across long distances. High energy and vocal, generally friendly but strong-willed.",
        "danger": "Low", "friendliness": "High"},
    "german shepherd": {
        "description": "A highly intelligent working breed used in police, military and guide-dog roles. Loyal and protective, benefits from early socialization.",
        "danger": "Medium", "friendliness": "Medium"},
    "rottweiler": {
        "description": "A large, powerful breed originally used for herding and guarding livestock. A well-socialized Rottweiler is affectionate with its family, but its size and guarding instincts warrant caution around strangers.",
        "danger": "Medium", "friendliness": "Medium"},
    "chihuahua": {
        "description": "The smallest dog breed, originating in Mexico. Bold and alert despite its size, sometimes wary of strangers.",
        "danger": "Very Low", "friendliness": "Medium"},
    "shih-tzu": {
        "description": "A small companion breed developed in Tibet, bred purely for affection rather than work. Generally calm and gentle.",
        "danger": "Very Low", "friendliness": "Very High"},
    "pug": {
        "description": "A small, wrinkly-faced companion breed known for its playful, laid-back temperament.",
        "danger": "Very Low", "friendliness": "Very High"},
    "dalmatian": {
        "description": "A distinctively spotted breed historically used as a carriage/firehouse dog. Energetic and needs plenty of exercise.",
        "danger": "Low", "friendliness": "High"},
    "doberman": {
        "description": "A sleek, athletic breed originally bred for personal protection. Intelligent and loyal, with strong guarding instincts.",
        "danger": "Medium", "friendliness": "Medium"},
    "great dane": {
        "description": "One of the tallest dog breeds — despite its imposing size, typically gentle and affectionate, sometimes called a 'gentle giant.'",
        "danger": "Low", "friendliness": "High"},
    "border collie": {
        "description": "A highly intelligent herding breed, widely considered one of the smartest dog breeds. Extremely energetic, needs a job to stay content.",
        "danger": "Very Low", "friendliness": "High"},
    "dingo": {
        "description": "A wild or semi-wild canine native to Australia — unlike domesticated dogs, dingoes behave more like wild animals.",
        "danger": "Medium", "friendliness": "Low"},

    # --- Cats ---
    "tabby": {
        "description": "Not a breed but a common coat pattern — striped or swirled markings seen across many domestic cat breeds.",
        "danger": "Very Low", "friendliness": "Medium"},
    "siamese cat": {
        "description": "A vocal, social breed originating in Thailand, known for its striking blue eyes and pointed coat coloring.",
        "danger": "Very Low", "friendliness": "High"},
    "persian cat": {
        "description": "A long-haired breed known for its calm, laid-back temperament and flat face.",
        "danger": "Very Low", "friendliness": "High"},
    "egyptian cat": {
        "description": "A short-haired breed with a spotted coat pattern, among the oldest domesticated cat breeds.",
        "danger": "Very Low", "friendliness": "Medium"},

    # --- Big cats ---
    "lion": {
        "description": "The only cat species that lives in social groups (prides). An apex predator capable of taking down large game.",
        "danger": "Very High", "friendliness": "Very Low"},
    "tiger": {
        "description": "The largest cat species, a solitary and powerful ambush predator found across parts of Asia.",
        "danger": "Very High", "friendliness": "Very Low"},
    "leopard": {
        "description": "A stealthy, solitary big cat known for dragging prey into trees to keep it from other predators.",
        "danger": "High", "friendliness": "Very Low"},
    "cheetah": {
        "description": "The fastest land animal, built for short explosive sprints rather than raw strength. Generally more avoidant of humans than other big cats.",
        "danger": "Medium", "friendliness": "Low"},

    # --- Wild mammals ---
    "gray wolf": {
        "description": "A highly social pack-hunting canine, ancestor of the domestic dog. Naturally wary of humans in the wild.",
        "danger": "Medium", "friendliness": "Low"},
    "brown bear": {
        "description": "A large, powerful omnivore found across the Northern Hemisphere. Generally avoids humans but can be dangerous if surprised or provoked.",
        "danger": "High", "friendliness": "Very Low"},
    "giant panda": {
        "description": "A bear species that feeds almost exclusively on bamboo. Solitary and generally non-aggressive.",
        "danger": "Medium", "friendliness": "Low"},
    "red fox": {
        "description": "A small, adaptable wild canine found across much of the world, including urban areas. Generally shy around humans.",
        "danger": "Low", "friendliness": "Low"},

    # --- Primates ---
    "gorilla": {
        "description": "The largest living primate, a gentle herbivore despite its immense strength. Lives in family groups led by a dominant male.",
        "danger": "Medium", "friendliness": "Low"},
    "chimpanzee": {
        "description": "One of humans' closest living relatives, highly intelligent and social, capable of tool use.",
        "danger": "Medium", "friendliness": "Low"},
    "orangutan": {
        "description": "A solitary, tree-dwelling great ape native to Indonesia and Malaysia, known for exceptional problem-solving intelligence.",
        "danger": "Low", "friendliness": "Low"},

    # --- Birds ---
    "bald eagle": {
        "description": "A large bird of prey and the national bird of the United States. A powerful hunter with excellent eyesight.",
        "danger": "Low", "friendliness": "Low"},
    "peacock": {
        "description": "Known for the male's iridescent tail display used to attract mates. Generally calm around humans in captivity.",
        "danger": "Very Low", "friendliness": "Medium"},
    "great grey owl": {
        "description": "One of the largest owl species by length, a silent nocturnal hunter of small mammals.",
        "danger": "Low", "friendliness": "Low"},

    # --- Reptiles ---
    "komodo dragon": {
        "description": "The largest living lizard species, an apex predator on its native Indonesian islands with a venomous bite.",
        "danger": "High", "friendliness": "Very Low"},
    "american alligator": {
        "description": "A large aquatic reptile native to the southeastern United States. Generally avoids humans but can be dangerous if approached.",
        "danger": "High", "friendliness": "Very Low"},
    "indian cobra": {
        "description": "A venomous snake species found across the Indian subcontinent, capable of a defensive hood display.",
        "danger": "High", "friendliness": "Very Low"},

    # --- Sharks ---
    "great white shark": {
        "description": "One of the ocean's largest predatory fish, an apex predator with a powerful bite. Attacks on humans are rare and often cases of mistaken identity.",
        "danger": "High", "friendliness": "Very Low"},
    "hammerhead": {
        "description": "Named for its distinctively shaped head, which improves vision and prey detection. Generally not considered a major threat to humans.",
        "danger": "Medium", "friendliness": "Very Low"},
    "tiger shark": {
        "description": "A large, opportunistic predator known for eating almost anything, including inedible objects. One of the species involved in more shark-human encounters.",
        "danger": "High", "friendliness": "Very Low"},
}


def get_species_info(label, category_fallback):
    """
    Returns {"description", "danger", "friendliness"} for a specific
    species label, falling back to the broader category's info if this
    exact species isn't individually covered.
    """
    key = label.lower().strip()
    if key in SPECIES_INFO:
        return SPECIES_INFO[key]
    return {
        "description": category_fallback["description"],
        "danger": category_fallback["danger"],
        "friendliness": category_fallback["friendliness"],
    }