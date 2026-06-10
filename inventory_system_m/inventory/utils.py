def categorize_item(description):
    text = description.lower()
    category_rules = [
        ('Cleaning Supplies', [
            'cleaning agent', 'cleaning tools', 'liquid bleach', 'glass cleaner', 'deodorizer',
            'disinfect', 'sanitiz', 'air freshener', 'trash bag', 'dust pan', 'broom',
            'duster', 'rags', 'fabric conditioner', 'disinfectant wipes', 'soap', 'insect killer',
            'alcohol'
        ]),
        ('Bags & Storage', [
            'trash bag', 'eco bag', 'paper bag', 'bag,', ' bag', 'bundle', 'pack'
        ]),
        ('Safety & PPE', ['glove', 'gloves']),
        ('Ink & Toner', ['ink refill', 'stamp pad ink', 'stamp pad ink', 'ink,', ' ink ']),
        ('Writing Instruments', [
            'ballpen', 'sign pen', 'pen', 'pencil', 'marker', 'highlighter', 'eraser'
        ]),
        ('Paper Products', [
            'paper', 'board', 'notepad', 'record book', 'folder', 'sticker paper', 'vellum', 'bristol'
        ]),
        ('Office Tools', [
            'clip', 'staple', 'scissors', 'stapler', 'tape', 'film', 'organizer', 'desk tray',
            'data folder', 'pressboard', 'clipboard', 'glue', 'battery', 'bottle', 'pad'
        ]),
    ]
    for category_name, keywords in category_rules:
        if any(keyword in text for keyword in keywords):
            return category_name
    return 'Office Supplies'
