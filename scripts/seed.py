"""
Seed the database with hundreds of categories and tens of thousands of products.

Usage:
    .venv/bin/python scripts/seed.py [--categories 300] [--products 50000] [--batch 500]
"""

import argparse
import asyncio
import random
import sys
import time
from pathlib import Path

# Ensure project root is on the path and .env is loaded from there
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

from sqlalchemy import text

from app.database.session import async_session_maker
from app.models.category import Category
from app.models.product import Product

# ---------------------------------------------------------------------------
# Word pools for realistic-looking data
# ---------------------------------------------------------------------------

MATERIALS = [
    "Leather", "Canvas", "Nylon", "Polyester", "Cotton", "Suede", "Velvet",
    "Denim", "Mesh", "Waxed", "Recycled", "Organic", "Waterproof", "Hemp",
]
ADJECTIVES = [
    "Classic", "Modern", "Slim", "Vintage", "Compact", "Oversized", "Casual",
    "Formal", "Urban", "Outdoor", "Travel", "Sport", "Luxury", "Minimalist",
    "Rugged", "Foldable", "Expandable", "Lightweight", "Heavy-Duty", "Premium",
]
PRODUCT_TYPES = [
    "Backpack", "Tote Bag", "Shoulder Bag", "Crossbody Bag", "Clutch",
    "Wallet", "Card Holder", "Duffel Bag", "Messenger Bag", "Belt Bag",
    "Satchel", "Handbag", "Weekender", "Laptop Bag", "Gym Bag",
    "Bucket Bag", "Drawstring Bag", "Pouch", "Briefcase", "Commuter Bag",
]
COLORS = [
    "Black", "Brown", "Tan", "Navy", "Grey", "Olive", "Burgundy", "Camel",
    "White", "Red", "Blue", "Green", "Yellow", "Pink", "Purple", "Orange",
]

TOP_CATEGORIES = [
    "Backpacks", "Wallets", "Handbags", "Travel Bags", "Laptop Bags",
    "Sports Bags", "Kids Bags", "Men's Bags", "Women's Bags", "Eco Bags",
]
SUB_CATEGORY_SUFFIXES = [
    "Under $50", "Premium", "Sale", "New Arrivals", "Best Sellers",
    "Compact", "Large", "Colourful", "Minimalist", "Limited Edition",
    "Seasonal", "Clearance", "Trending", "Staff Picks", "Bundles",
    "Waterproof", "Vegan", "Handmade", "Vintage", "Collaborations",
]

DESCRIPTION_TEMPLATES = [
    "A {adj} {material} {ptype} designed for everyday use. Features multiple compartments and durable stitching.",
    "This {color} {material} {ptype} combines style with functionality. Perfect for work, travel, or casual outings.",
    "Crafted from high-quality {material}, this {adj} {ptype} offers ample storage and a timeless design.",
    "The {adj} {ptype} in {color} is built to last. {material} construction with reinforced seams.",
    "Introducing the {color} {adj} {ptype} — lightweight yet spacious, ideal for the modern commuter.",
]


def make_title(rng: random.Random) -> str:
    return f"{rng.choice(COLORS)} {rng.choice(ADJECTIVES)} {rng.choice(MATERIALS)} {rng.choice(PRODUCT_TYPES)}"


def make_description(rng: random.Random) -> str:
    tpl = rng.choice(DESCRIPTION_TEMPLATES)
    return tpl.format(
        adj=rng.choice(ADJECTIVES).lower(),
        material=rng.choice(MATERIALS).lower(),
        ptype=rng.choice(PRODUCT_TYPES).lower(),
        color=rng.choice(COLORS).lower(),
    )


# ---------------------------------------------------------------------------
# Seeding logic
# ---------------------------------------------------------------------------

async def seed(num_categories: int, num_products: int, batch_size: int) -> None:
    async with async_session_maker() as session:
        # ------------------------------------------------------------------
        # Wipe existing seed data (leave user data outside SKU prefix alone)
        # ------------------------------------------------------------------
        print("Clearing existing seed data...")
        await session.execute(text("DELETE FROM products WHERE sku LIKE 'SEED-%'"))
        # Delete sub-categories (have parent_id) before top-level ones to satisfy FK constraint
        await session.execute(text("DELETE FROM categories WHERE name LIKE '[SEED]%' AND parent_id IS NOT NULL"))
        await session.execute(text("DELETE FROM categories WHERE name LIKE '[SEED]%'"))
        await session.commit()

        # ------------------------------------------------------------------
        # Categories  (top-level + sub-categories)
        # ------------------------------------------------------------------
        print(f"Inserting {num_categories} categories...")
        rng = random.Random(42)

        # First pass: top-level categories
        top_cats: list[Category] = []
        for name in TOP_CATEGORIES:
            cat = Category(name=f"[SEED] {name}")
            session.add(cat)
            top_cats.append(cat)
        await session.flush()  # get IDs

        # Second pass: sub-categories to reach num_categories total
        sub_cats: list[Category] = []
        remaining = num_categories - len(TOP_CATEGORIES)
        for i in range(remaining):
            parent = rng.choice(top_cats)
            suffix = SUB_CATEGORY_SUFFIXES[i % len(SUB_CATEGORY_SUFFIXES)]
            cat = Category(name=f"[SEED] {parent.name[7:]} – {suffix}", parent_id=parent.id)
            session.add(cat)
            sub_cats.append(cat)

        await session.commit()

        all_cat_ids = [c.id for c in top_cats] + [c.id for c in sub_cats]
        print(f"  Created {len(all_cat_ids)} categories.")

        # ------------------------------------------------------------------
        # Products  (inserted in batches for speed)
        # ------------------------------------------------------------------
        print(f"Inserting {num_products} products in batches of {batch_size}...")
        t0 = time.monotonic()
        inserted = 0

        for batch_start in range(0, num_products, batch_size):
            batch_end = min(batch_start + batch_size, num_products)
            objects = []
            for i in range(batch_start, batch_end):
                sku = f"SEED-{i+1:07d}"
                price = round(rng.uniform(5.0, 500.0), 2)
                cat_id = rng.choice(all_cat_ids)
                objects.append(Product(
                    title=make_title(rng),
                    description=make_description(rng),
                    image="media/products/placeholder.jpg",
                    sku=sku,
                    price=price,
                    category_id=cat_id,
                ))
            session.add_all(objects)
            await session.commit()
            inserted += len(objects)
            elapsed = time.monotonic() - t0
            rate = inserted / elapsed if elapsed > 0 else 0
            print(f"  {inserted}/{num_products} products inserted  ({rate:.0f}/s)")

        elapsed = time.monotonic() - t0
        print(f"\nDone! {len(all_cat_ids)} categories and {inserted} products in {elapsed:.1f}s.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed the e-bag database with test data.")
    parser.add_argument("--categories", type=int, default=300,
                        help="Total number of categories to create (default: 300)")
    parser.add_argument("--products", type=int, default=50_000,
                        help="Total number of products to create (default: 50000)")
    parser.add_argument("--batch", type=int, default=500,
                        help="Insert batch size (default: 500)")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(seed(args.categories, args.products, args.batch))
