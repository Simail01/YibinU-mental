from scl90_logic import SCL90_QUESTIONS, CATEGORIES

counts = {k: 0 for k in CATEGORIES.keys()}
items = {k: [] for k in CATEGORIES.keys()}

for q in SCL90_QUESTIONS:
    cat = q["category"]
    if cat in counts:
        counts[cat] += 1
        items[cat].append(q["id"])
    else:
        print(f"Unknown category: {cat} for ID {q['id']}")

print("Category Counts:")
for k, v in counts.items():
    print(f"{CATEGORIES[k]} ({k}): {v}")
    print(f"Items: {items[k]}")

print(f"Total items: {len(SCL90_QUESTIONS)}")
