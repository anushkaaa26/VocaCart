import sqlite3
import random
from datetime import datetime

DB_NAME = "store.db"

random.seed(42)


# ============================================================
# PRODUCT DATA
# ============================================================

PRODUCTS = [

    # --------------------------------------------------------
    # DAIRY
    # --------------------------------------------------------

    ("Amul Taaza Milk", "dairy", 68, "Fresh toned milk 1 litre", 0, "Amul", "1 L", "milk"),
    ("Amul Gold Milk", "dairy", 72, "Full cream milk", 0, "Amul", "1 L", "milk"),
    ("Amul Lactose Free Milk", "dairy", 75, "Lactose free milk", 0, "Amul", "1 L", "milk"),
    ("Mother Dairy Toned Milk", "dairy", 66, "Fresh toned milk", 0, "Mother Dairy", "1 L", "milk"),
    ("Mother Dairy Full Cream Milk", "dairy", 72, "Full cream milk", 0, "Mother Dairy", "1 L", "milk"),
    ("Amul Butter", "dairy", 58, "Salted table butter", 0, "Amul", "100 g", "butter"),
    ("Amul Cheese Slices", "dairy", 145, "Processed cheese slices", 0, "Amul", "200 g", "cheese"),
    ("Amul Cheese Cubes", "dairy", 130, "Processed cheese cubes", 0, "Amul", "200 g", "cheese"),
    ("Amul Fresh Cream", "dairy", 65, "Fresh cream", 0, "Amul", "250 ml", "cream"),
    ("Mother Dairy Curd", "dairy", 55, "Fresh plain curd", 0, "Mother Dairy", "400 g", "curd"),
    ("Epigamia Greek Yogurt", "dairy", 75, "Greek yogurt", 0, "Epigamia", "90 g", "yogurt"),
    ("Epigamia Mango Yogurt", "dairy", 55, "Mango yogurt", 0, "Epigamia", "90 g", "yogurt"),

    # --------------------------------------------------------
    # DAIRY ALTERNATIVES
    # --------------------------------------------------------

    ("Almond Breeze Almond Milk", "dairy-alt", 299, "Unsweetened almond milk", 0, "Almond Breeze", "1 L", "almond milk"),
    ("So Good Almond Milk", "dairy-alt", 240, "Plant based almond milk", 0, "So Good", "1 L", "almond milk"),
    ("So Good Oat Milk", "dairy-alt", 280, "Creamy oat milk", 0, "So Good", "1 L", "oat milk"),
    ("Epigamia Coconut Milk", "dairy-alt", 180, "Coconut based milk", 0, "Epigamia", "1 L", "coconut milk"),
    ("Urban Platter Soy Milk", "dairy-alt", 220, "Unsweetened soy milk", 0, "Urban Platter", "1 L", "soy milk"),

    # --------------------------------------------------------
    # FRUITS
    # --------------------------------------------------------

    ("Fresh Red Apples", "produce", 180, "Crisp red apples", 0, "Farm Fresh", "1 kg", "apples"),
    ("Organic Red Apples", "produce", 240, "Organic red apples", 1, "Organic Farm", "1 kg", "organic apples"),
    ("Green Apples", "produce", 190, "Fresh green apples", 0, "Farm Fresh", "1 kg", "green apples"),
    ("Bananas", "produce", 60, "Fresh ripe bananas", 0, "Farm Fresh", "1 kg", "bananas"),
    ("Organic Bananas", "produce", 90, "Organic bananas", 1, "Organic Farm", "1 kg", "organic bananas"),
    ("Alphonso Mangoes", "produce", 250, "Premium Alphonso mangoes", 0, "Farm Fresh", "1 kg", "mangoes"),
    ("Fresh Oranges", "produce", 100, "Juicy oranges", 0, "Farm Fresh", "1 kg", "oranges"),
    ("Pomegranate", "produce", 180, "Fresh pomegranate", 0, "Farm Fresh", "1 kg", "pomegranate"),
    ("Papaya", "produce", 70, "Fresh papaya", 0, "Farm Fresh", "1 kg", "papaya"),
    ("Watermelon", "produce", 55, "Fresh watermelon", 0, "Farm Fresh", "1 kg", "watermelon"),
    ("Kiwi", "produce", 220, "Fresh green kiwi", 0, "Farm Fresh", "500 g", "kiwi"),
    ("Grapes", "produce", 110, "Fresh seedless grapes", 0, "Farm Fresh", "500 g", "grapes"),

    # --------------------------------------------------------
    # VEGETABLES
    # --------------------------------------------------------

    ("Potatoes", "vegetables", 45, "Fresh potatoes", 0, "Farm Fresh", "1 kg", "potatoes"),
    ("Onions", "vegetables", 50, "Fresh onions", 0, "Farm Fresh", "1 kg", "onions"),
    ("Tomatoes", "vegetables", 55, "Fresh tomatoes", 0, "Farm Fresh", "1 kg", "tomatoes"),
    ("Organic Tomatoes", "vegetables", 85, "Organic tomatoes", 1, "Organic Farm", "1 kg", "organic tomatoes"),
    ("Carrots", "vegetables", 65, "Fresh carrots", 0, "Farm Fresh", "1 kg", "carrots"),
    ("Capsicum", "vegetables", 90, "Fresh green capsicum", 0, "Farm Fresh", "500 g", "capsicum"),
    ("Broccoli", "vegetables", 110, "Fresh broccoli", 0, "Farm Fresh", "500 g", "broccoli"),
    ("Spinach", "vegetables", 40, "Fresh spinach leaves", 0, "Farm Fresh", "250 g", "spinach"),
    ("Cucumber", "vegetables", 50, "Fresh cucumber", 0, "Farm Fresh", "1 kg", "cucumber"),
    ("Green Peas", "vegetables", 100, "Fresh green peas", 0, "Farm Fresh", "500 g", "peas"),

    # --------------------------------------------------------
    # STAPLES / GRAINS
    # --------------------------------------------------------

    ("India Gate Basmati Rice", "grains", 180, "Premium basmati rice", 0, "India Gate", "1 kg", "rice"),
    ("India Gate Classic Basmati Rice", "grains", 240, "Classic basmati rice", 0, "India Gate", "1 kg", "basmati rice"),
    ("Organic Brown Rice", "grains", 190, "Organic whole grain brown rice", 1, "Organic Tattva", "1 kg", "brown rice"),
    ("Quinoa", "grains", 320, "Premium white quinoa", 0, "True Elements", "500 g", "quinoa"),
    ("Organic Quinoa", "grains", 390, "Organic quinoa", 1, "Organic Tattva", "500 g", "organic quinoa"),
    ("Whole Wheat Atta", "grains", 65, "Whole wheat flour", 0, "Aashirvaad", "1 kg", "atta"),
    ("Aashirvaad Multigrain Atta", "grains", 95, "Multigrain wheat flour", 0, "Aashirvaad", "1 kg", "multigrain atta"),
    ("Organic Whole Wheat Atta", "grains", 130, "Organic wheat flour", 1, "Organic Tattva", "1 kg", "organic atta"),
    ("Rolled Oats", "grains", 180, "Whole rolled oats", 0, "Saffola", "1 kg", "oats"),
    ("Organic Rolled Oats", "grains", 240, "Organic rolled oats", 1, "True Elements", "1 kg", "organic oats"),
    ("Poha", "grains", 75, "Flattened rice", 0, "Fortune", "1 kg", "poha"),
    ("Sooji", "grains", 65, "Fine semolina", 0, "Fortune", "500 g", "sooji"),
    ("Besan", "grains", 90, "Gram flour", 0, "Fortune", "500 g", "besan"),

    # --------------------------------------------------------
    # BAKERY
    # --------------------------------------------------------

    ("Harvest Gold White Bread", "bakery", 45, "Soft white bread", 0, "Harvest Gold", "400 g", "bread"),
    ("Britannia Brown Bread", "bakery", 50, "Whole wheat brown bread", 0, "Britannia", "400 g", "brown bread"),
    ("Modern Multigrain Bread", "bakery", 55, "Multigrain bread", 0, "Modern", "400 g", "multigrain bread"),
    ("Organic Whole Wheat Bread", "bakery", 95, "Organic wheat bread", 1, "Nature's Basket", "400 g", "organic bread"),
    ("Burger Buns", "bakery", 45, "Soft burger buns", 0, "Harvest Gold", "4 pcs", "burger buns"),
    ("Croissants", "bakery", 160, "Butter croissants", 0, "Theobroma", "4 pcs", "croissants"),

    # --------------------------------------------------------
    # EGGS / PROTEIN
    # --------------------------------------------------------

    ("Farm Fresh Eggs", "eggs", 90, "Farm fresh eggs", 0, "Farm Fresh", "6 pcs", "eggs"),
    ("Organic Free Range Eggs", "eggs", 150, "Organic free range eggs", 1, "Organic Farm", "6 pcs", "organic eggs"),
    ("Brown Eggs", "eggs", 110, "Fresh brown eggs", 0, "Farm Fresh", "6 pcs", "brown eggs"),
    ("High Protein Eggs", "eggs", 130, "Protein rich eggs", 0, "Healthy Farm", "6 pcs", "protein eggs"),
    ("Chicken Breast", "protein", 320, "Fresh boneless chicken breast", 0, "Fresh Meat", "500 g", "chicken"),
    ("Chicken Curry Cut", "protein", 280, "Fresh curry cut chicken", 0, "Fresh Meat", "500 g", "chicken"),

    # --------------------------------------------------------
    # SNACKS
    # --------------------------------------------------------

    ("Lays Classic Salted", "snacks", 20, "Classic salted potato chips", 0, "Lays", "50 g", "chips"),
    ("Lays Magic Masala", "snacks", 20, "Masala potato chips", 0, "Lays", "50 g", "chips"),
    ("Kurkure Masala Munch", "snacks", 20, "Spicy corn snack", 0, "Kurkure", "90 g", "kurkure"),
    ("Too Yumm Multigrain Chips", "snacks", 50, "Multigrain baked chips", 0, "Too Yumm", "75 g", "healthy chips"),
    ("Organic Oats Granola", "snacks", 280, "Organic granola with oats", 1, "True Elements", "400 g", "granola"),
    ("Protein Granola", "snacks", 350, "High protein granola", 0, "The Whole Truth", "400 g", "protein granola"),
    ("Roasted Almonds", "snacks", 220, "Dry roasted almonds", 0, "Farmley", "200 g", "almonds"),
    ("Salted Cashews", "snacks", 260, "Roasted salted cashews", 0, "Farmley", "200 g", "cashews"),
    ("Trail Mix", "snacks", 300, "Nuts and dried fruit mix", 0, "Farmley", "250 g", "trail mix"),
    ("Makhana", "snacks", 180, "Roasted fox nuts", 0, "Farmley", "100 g", "makhana"),
    ("Roasted Makhana", "snacks", 220, "Healthy roasted fox nuts", 0, "Too Yumm", "100 g", "roasted makhana"),

    # --------------------------------------------------------
    # BISCUITS
    # --------------------------------------------------------

    ("Parle-G Biscuits", "biscuits", 30, "Classic glucose biscuits", 0, "Parle", "800 g", "biscuits"),
    ("Britannia Good Day", "biscuits", 40, "Butter cookies", 0, "Britannia", "200 g", "biscuits"),
    ("Britannia Marie Gold", "biscuits", 35, "Marie biscuits", 0, "Britannia", "250 g", "biscuits"),
    ("Oreo Original", "biscuits", 40, "Chocolate sandwich cookies", 0, "Oreo", "120 g", "oreo"),
    ("Dark Fantasy", "biscuits", 55, "Chocolate filled cookies", 0, "Sunfeast", "150 g", "cookies"),
    ("NutriChoice Digestive", "biscuits", 55, "Digestive biscuits", 0, "Britannia", "250 g", "digestive biscuits"),

    # --------------------------------------------------------
    # NOODLES / PACKAGED FOOD
    # --------------------------------------------------------

    ("Maggi 2 Minute Noodles", "packaged-food", 14, "Instant masala noodles", 0, "Maggi", "70 g", "maggi"),
    ("Maggi Family Pack", "packaged-food", 65, "Instant noodles family pack", 0, "Maggi", "420 g", "maggi"),
    ("Yippee Magic Masala", "packaged-food", 15, "Instant masala noodles", 0, "Sunfeast", "70 g", "noodles"),
    ("Yippee Wow Masala", "packaged-food", 20, "Instant noodles", 0, "Sunfeast", "70 g", "noodles"),
    ("Pasta Penne", "packaged-food", 95, "Durum wheat penne pasta", 0, "Del Monte", "500 g", "pasta"),
    ("Pasta Fusilli", "packaged-food", 110, "Fusilli pasta", 0, "Del Monte", "500 g", "pasta"),
    ("Tomato Pasta Sauce", "packaged-food", 130, "Italian tomato sauce", 0, "Del Monte", "500 g", "pasta sauce"),
    ("Peanut Butter", "spreads", 210, "Creamy peanut butter", 0, "Pintola", "350 g", "peanut butter"),
    ("Crunchy Peanut Butter", "spreads", 220, "Crunchy peanut butter", 0, "Pintola", "350 g", "peanut butter"),
    ("Organic Peanut Butter", "spreads", 290, "Organic peanut butter", 1, "Alpino", "350 g", "organic peanut butter"),

    # --------------------------------------------------------
    # CHOCOLATES
    # --------------------------------------------------------

    ("Cadbury Dairy Milk", "chocolates", 50, "Milk chocolate", 0, "Cadbury", "110 g", "chocolate"),
    ("Cadbury 5 Star", "chocolates", 40, "Chocolate bar", 0, "Cadbury", "100 g", "chocolate"),
    ("KitKat", "chocolates", 50, "Crispy wafer chocolate", 0, "Nestle", "100 g", "kitkat"),
    ("Ferrero Rocher", "chocolates", 450, "Premium hazelnut chocolates", 0, "Ferrero", "200 g", "premium chocolate"),
    ("Dark Chocolate 70%", "chocolates", 180, "70 percent dark chocolate", 0, "Amul", "150 g", "dark chocolate"),
    ("Organic Dark Chocolate", "chocolates", 250, "Organic dark chocolate", 1, "Mason & Co", "100 g", "organic chocolate"),

    # --------------------------------------------------------
    # TEA / COFFEE
    # --------------------------------------------------------

    ("Tata Tea Gold", "tea-coffee", 220, "Premium tea", 0, "Tata", "500 g", "tea"),
    ("Tata Tea Premium", "tea-coffee", 190, "Everyday tea", 0, "Tata", "500 g", "tea"),
    ("Organic Green Tea", "tea-coffee", 220, "Organic green tea", 1, "Organic India", "25 bags", "green tea"),
    ("Chamomile Tea", "tea-coffee", 250, "Relaxing chamomile tea", 0, "Organic India", "25 bags", "chamomile tea"),
    ("Nescafe Classic", "tea-coffee", 310, "Instant coffee", 0, "Nescafe", "100 g", "coffee"),
    ("Nescafe Gold", "tea-coffee", 450, "Premium instant coffee", 0, "Nescafe", "100 g", "coffee"),
    ("Bru Instant Coffee", "tea-coffee", 280, "Instant coffee", 0, "Bru", "100 g", "coffee"),
    ("Ethiopian Whole Bean Coffee", "tea-coffee", 650, "Single origin coffee beans", 0, "Blue Tokai", "250 g", "coffee beans"),
    ("Cold Brew Coffee", "beverages", 180, "Ready to drink cold brew", 0, "Sleepy Owl", "200 ml", "cold coffee"),

    # --------------------------------------------------------
    # BEVERAGES
    # --------------------------------------------------------

    ("Bisleri Water", "beverages", 20, "Packaged drinking water", 0, "Bisleri", "1 L", "water"),
    ("Kinley Water", "beverages", 20, "Packaged drinking water", 0, "Kinley", "1 L", "water"),
    ("Paper Boat Aam Panna", "beverages", 40, "Traditional Indian drink", 0, "Paper Boat", "250 ml", "juice"),
    ("Real Fruit Juice Orange", "beverages", 120, "Orange fruit juice", 0, "Real", "1 L", "orange juice"),
    ("Real Mixed Fruit Juice", "beverages", 130, "Mixed fruit juice", 0, "Real", "1 L", "fruit juice"),
    ("Coconut Water", "beverages", 60, "Natural coconut water", 0, "Raw Pressery", "200 ml", "coconut water"),
    ("Electrolyte Drink", "beverages", 50, "Electrolyte hydration drink", 0, "Fast&Up", "200 ml", "electrolyte"),

    # --------------------------------------------------------
    # SPICES
    # --------------------------------------------------------

    ("Everest Chilli Powder", "spices", 65, "Red chilli powder", 0, "Everest", "100 g", "chilli powder"),
    ("Everest Turmeric Powder", "spices", 55, "Turmeric powder", 0, "Everest", "100 g", "turmeric"),
    ("Everest Garam Masala", "spices", 70, "Garam masala", 0, "Everest", "100 g", "garam masala"),
    ("MDH Chana Masala", "spices", 75, "Chana masala spice mix", 0, "MDH", "100 g", "chana masala"),
    ("Organic Turmeric", "spices", 160, "Organic turmeric powder", 1, "Organic India", "100 g", "organic turmeric"),
    ("Black Pepper", "spices", 140, "Whole black pepper", 0, "Catch", "100 g", "pepper"),
    ("Cumin Seeds", "spices", 90, "Whole cumin seeds", 0, "Catch", "100 g", "cumin"),

    # --------------------------------------------------------
    # OIL
    # --------------------------------------------------------

    ("Fortune Sunflower Oil", "oil", 140, "Refined sunflower oil", 0, "Fortune", "1 L", "cooking oil"),
    ("Fortune Rice Bran Oil", "oil", 160, "Rice bran cooking oil", 0, "Fortune", "1 L", "cooking oil"),
    ("Extra Virgin Olive Oil", "oil", 550, "Extra virgin olive oil", 0, "Figaro", "500 ml", "olive oil"),
    ("Organic Extra Virgin Olive Oil", "oil", 750, "Organic extra virgin olive oil", 1, "Borges", "500 ml", "organic olive oil"),
    ("Cold Pressed Coconut Oil", "oil", 350, "Cold pressed coconut oil", 0, "Max Care", "500 ml", "coconut oil"),

    # --------------------------------------------------------
    # HONEY / CONDIMENTS
    # --------------------------------------------------------

    ("Dabur Honey", "condiments", 180, "Natural honey", 0, "Dabur", "500 g", "honey"),
    ("Organic Raw Honey", "condiments", 350, "Raw organic honey", 1, "Nature's Nectar", "500 g", "organic honey"),
    ("Wildflower Honey", "condiments", 300, "Natural wildflower honey", 0, "Under The Mango Tree", "250 g", "honey"),
    ("Premium Manuka Honey", "condiments", 1200, "Premium manuka honey", 0, "Manuka Health", "250 g", "manuka honey"),
    ("Kissan Tomato Ketchup", "condiments", 130, "Tomato ketchup", 0, "Kissan", "500 g", "ketchup"),
    ("Hellmann's Mayonnaise", "condiments", 180, "Creamy mayonnaise", 0, "Hellmann's", "400 g", "mayonnaise"),

    # --------------------------------------------------------
    # PERSONAL CARE
    # --------------------------------------------------------

    ("Colgate Strong Teeth Toothpaste", "personal-care", 95, "Daily fluoride toothpaste", 0, "Colgate", "200 g", "toothpaste"),
    ("Colgate Herbal Toothpaste", "personal-care", 110, "Herbal toothpaste", 0, "Colgate", "200 g", "toothpaste"),
    ("Sensodyne Repair Toothpaste", "personal-care", 180, "Sensitive teeth toothpaste", 0, "Sensodyne", "70 g", "toothpaste"),
    ("Dabur Red Toothpaste", "personal-care", 110, "Ayurvedic toothpaste", 0, "Dabur", "200 g", "toothpaste"),
    ("Himalaya Neem Face Wash", "personal-care", 150, "Neem face wash", 0, "Himalaya", "150 ml", "face wash"),
    ("Cetaphil Gentle Cleanser", "personal-care", 399, "Gentle facial cleanser", 0, "Cetaphil", "125 ml", "face wash"),
    ("Nivea Body Lotion", "personal-care", 220, "Moisturizing body lotion", 0, "Nivea", "400 ml", "body lotion"),
    ("Dove Shampoo", "personal-care", 240, "Daily care shampoo", 0, "Dove", "650 ml", "shampoo"),
    ("Head & Shoulders Shampoo", "personal-care", 280, "Anti dandruff shampoo", 0, "Head & Shoulders", "650 ml", "shampoo"),
    ("Mamaearth Onion Shampoo", "personal-care", 399, "Onion hair shampoo", 0, "Mamaearth", "250 ml", "shampoo"),
    ("Dove Soap", "personal-care", 180, "Moisturizing bathing soap", 0, "Dove", "4 x 100 g", "soap"),
    ("Nivea Deodorant", "personal-care", 220, "Fresh deodorant", 0, "Nivea", "150 ml", "deodorant"),

    # --------------------------------------------------------
    # HOUSEHOLD CLEANING
    # --------------------------------------------------------

    ("Surf Excel Matic", "household", 520, "Liquid detergent", 0, "Surf Excel", "2 L", "detergent"),
    ("Surf Excel Easy Wash", "household", 240, "Laundry detergent", 0, "Surf Excel", "2 kg", "detergent"),
    ("Ariel Matic Liquid", "household", 480, "Liquid laundry detergent", 0, "Ariel", "2 L", "detergent"),
    ("Tide Naturals", "household", 210, "Laundry detergent", 0, "Tide", "2 kg", "detergent"),
    ("Vim Dishwash Liquid", "household", 120, "Dishwashing liquid", 0, "Vim", "750 ml", "dishwash"),
    ("Vim Dishwasher Gel", "household", 220, "Dishwasher cleaning gel", 0, "Vim", "500 ml", "dishwasher"),
    ("Harpic Toilet Cleaner", "household", 190, "Toilet cleaning liquid", 0, "Harpic", "1 L", "toilet cleaner"),
    ("Lizol Floor Cleaner", "household", 220, "Floor cleaning liquid", 0, "Lizol", "2 L", "floor cleaner"),
    ("Colin Glass Cleaner", "household", 110, "Glass and surface cleaner", 0, "Colin", "500 ml", "glass cleaner"),
    ("Dettol Disinfectant", "household", 180, "Surface disinfectant", 0, "Dettol", "500 ml", "disinfectant"),
    ("Scotch Brite Scrub Pads", "household", 90, "Kitchen scrub pads", 0, "Scotch Brite", "3 pcs", "scrub pad"),
    ("Garbage Bags", "household", 120, "Large garbage bags", 0, "Solimo", "30 pcs", "garbage bags"),

    # --------------------------------------------------------
    # PAPER / ESSENTIALS
    # --------------------------------------------------------

    ("Origami Toilet Paper", "household-essentials", 280, "Soft toilet paper rolls", 0, "Origami", "6 rolls", "toilet paper"),
    ("Kitchen Paper Towels", "household-essentials", 180, "Absorbent paper towels", 0, "Origami", "2 rolls", "paper towels"),
    ("Aluminium Foil", "household-essentials", 180, "Kitchen aluminium foil", 0, "Freshwrapp", "9 m", "foil"),
    ("Cling Film", "household-essentials", 150, "Food wrapping cling film", 0, "Freshwrapp", "30 m", "cling film"),
    ("Zip Lock Bags", "household-essentials", 180, "Reusable food storage bags", 0, "Solimo", "20 pcs", "zip bags"),

    # --------------------------------------------------------
    # BABY
    # --------------------------------------------------------

    ("Pampers Baby Dry", "baby-care", 650, "Baby diapers", 0, "Pampers", "42 pcs", "diapers"),
    ("Huggies Wonder Pants", "baby-care", 620, "Baby diapers", 0, "Huggies", "42 pcs", "diapers"),
    ("Johnson's Baby Shampoo", "baby-care", 220, "Gentle baby shampoo", 0, "Johnson's", "200 ml", "baby shampoo"),
    ("Johnson's Baby Lotion", "baby-care", 240, "Baby moisturizing lotion", 0, "Johnson's", "200 ml", "baby lotion"),

    # --------------------------------------------------------
    # PET
    # --------------------------------------------------------

    ("Pedigree Adult Dog Food", "pet-care", 450, "Adult dog food", 0, "Pedigree", "1.2 kg", "dog food"),
    ("Whiskas Adult Cat Food", "pet-care", 420, "Adult cat food", 0, "Whiskas", "1.2 kg", "cat food"),
    ("Dog Treats", "pet-care", 250, "Crunchy dog treats", 0, "Pedigree", "400 g", "dog treats"),
    ("Cat Treats", "pet-care", 220, "Cat treats", 0, "Whiskas", "100 g", "cat treats"),
]


# ============================================================
# EXTRA VARIATIONS
# ============================================================

# These add realistic product variants without manually
# writing hundreds of rows.

VARIATIONS = [
    ("Small", 0.70),
    ("Large", 1.35),
    ("Family Pack", 1.60),
]


def build_products():
    products = []

    for product in PRODUCTS:
        products.append(product)

        name, category, price, description, organic, brand, size, keyword = product

        # Add selected pack-size variations for common products.
        if category in {
            "snacks",
            "biscuits",
            "grains",
            "packaged-food",
            "household",
        }:

            for suffix, multiplier in random.sample(
                VARIATIONS,
                k=min(2, len(VARIATIONS))
            ):
                variant_name = f"{name} {suffix}"

                variant_price = round(price * multiplier)

                products.append(
                    (
                        variant_name,
                        category,
                        variant_price,
                        f"{description} - {suffix.lower()}",
                        organic,
                        brand,
                        size,
                        keyword,
                    )
                )

    return products


# ============================================================
# DATABASE
# ============================================================

def setup_database():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    # --------------------------------------------------------
    # PRODUCTS
    # --------------------------------------------------------

    cursor.execute("""
        DROP TABLE IF EXISTS products
    """)

    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL,
            description TEXT,
            is_organic INTEGER DEFAULT 0,
            brand TEXT,
            size TEXT,
            keywords TEXT,
            stock INTEGER DEFAULT 100,
            rating REAL DEFAULT 4.0
        )
    """)

    # --------------------------------------------------------
    # REVIEWS
    # --------------------------------------------------------

    cursor.execute("""
        DROP TABLE IF EXISTS reviews
    """)

    cursor.execute("""
        CREATE TABLE reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            rating REAL,
            reviewer_name TEXT,
            review_text TEXT,
            FOREIGN KEY(product_id)
                REFERENCES products(id)
        )
    """)

    # --------------------------------------------------------
    # ORDERS
    # --------------------------------------------------------

    cursor.execute("""
        DROP TABLE IF EXISTS orders
    """)

    cursor.execute("""
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            price REAL NOT NULL,
            ordered_at TEXT NOT NULL
                DEFAULT (datetime('now')),
            FOREIGN KEY(product_id)
                REFERENCES products(id)
        )
    """)

    # --------------------------------------------------------
    # INSERT PRODUCTS
    # --------------------------------------------------------

    products = build_products()

    cursor.executemany(
        """
        INSERT INTO products
        (
            name,
            category,
            price,
            description,
            is_organic,
            brand,
            size,
            keywords,
            stock,
            rating
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                name,
                category,
                price,
                description,
                organic,
                brand,
                size,
                keyword,
                random.randint(20, 150),
                round(random.uniform(3.8, 4.9), 2),
            )
            for (
                name,
                category,
                price,
                description,
                organic,
                brand,
                size,
                keyword,
            ) in products
        ],
    )

    # --------------------------------------------------------
    # REVIEWS
    # --------------------------------------------------------

    names = [
        "Ananya",
        "Rahul",
        "Priya",
        "Arjun",
        "Neha",
        "Rohan",
        "Aarav",
        "Ishita",
        "Karan",
        "Meera",
    ]

    review_texts = [
        "Good quality product.",
        "Worth the price.",
        "Very good purchase.",
        "Would buy again.",
        "Good quality and packaging.",
        "Works exactly as expected.",
        "Great value for money.",
        "Fresh and good quality.",
    ]

    cursor.execute(
        "SELECT id FROM products"
    )

    product_ids = [
        row[0]
        for row in cursor.fetchall()
    ]

    reviews = []

    for product_id in product_ids:

        review_count = random.randint(2, 6)

        for _ in range(review_count):

            reviews.append(
                (
                    product_id,
                    round(random.uniform(3.5, 5.0), 1),
                    random.choice(names),
                    random.choice(review_texts),
                )
            )

    cursor.executemany(
        """
        INSERT INTO reviews
        (
            product_id,
            rating,
            reviewer_name,
            review_text
        )
        VALUES (?, ?, ?, ?)
        """,
        reviews,
    )

    # --------------------------------------------------------
    # SEARCH INDEXES
    # --------------------------------------------------------

    cursor.execute("""
        CREATE INDEX idx_products_name
        ON products(name)
    """)

    cursor.execute("""
        CREATE INDEX idx_products_category
        ON products(category)
    """)

    cursor.execute("""
        CREATE INDEX idx_products_brand
        ON products(brand)
    """)

    cursor.execute("""
        CREATE INDEX idx_products_price
        ON products(price)
    """)

    cursor.execute("""
        CREATE INDEX idx_products_keywords
        ON products(keywords)
    """)

    conn.commit()

    # --------------------------------------------------------
    # STATS
    # --------------------------------------------------------

    cursor.execute(
        "SELECT COUNT(*) FROM products"
    )

    product_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM reviews"
    )

    review_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(DISTINCT category) FROM products"
    )

    category_count = cursor.fetchone()[0]

    conn.close()

    print("\n" + "=" * 55)
    print("🛒 VocaCart Database Ready")
    print("=" * 55)

    print(f"Products   : {product_count}")
    print(f"Categories : {category_count}")
    print(f"Reviews    : {review_count}")

    print("\nDatabase:")
    print(f"  {DB_NAME}")

    print("\nExamples you can search:")
    print("  • milk")
    print("  • toothpaste")
    print("  • shampoo")
    print("  • detergent")
    print("  • organic apples")
    print("  • coffee under ₹500")
    print("  • Maggi")
    print("  • almond milk")
    print("  • protein snacks")
    print("  • bread")
    print("  • honey")

    print("=" * 55 + "\n")


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    setup_database()