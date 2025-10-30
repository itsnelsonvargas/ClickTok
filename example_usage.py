"""
Example Usage of ClickTok Components

This script demonstrates how to use ClickTok programmatically
without the GUI.
"""
import json
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.database import Database
from src.product_fetcher import ProductFetcher
from src.video_creator import VideoCreator
from src.caption_generator import CaptionGenerator
from config.settings import *


def example_1_fetch_products():
    """Example: Fetch and save products"""
    print("=" * 60)
    print("Example 1: Fetching Products")
    print("=" * 60)

    # Load credentials
    with open(BASE_DIR / "config" / "credentials.json") as f:
        credentials = json.load(f)

    # Initialize components
    db = Database(DATABASE_PATH)
    fetcher = ProductFetcher(credentials, PRODUCT_FILTERS)

    # Fetch products
    print("\nFetching trending products...")
    products = fetcher.fetch_trending_products(limit=5)

    # Save to database
    print(f"\nSaving {len(products)} products to database...")
    for product in products:
        db.add_product(product)
        print(f"  ✓ {product['name']} - ${product['price']}")

    print("\n✅ Done! Products saved to database.\n")


def example_2_create_single_video():
    """Example: Create a video for one product"""
    print("=" * 60)
    print("Example 2: Creating a Single Video")
    print("=" * 60)

    # Define a product (normally you'd get this from database)
    product = {
        'product_id': 'EXAMPLE_001',
        'name': 'Wireless Bluetooth Earbuds Pro',
        'description': 'High-quality wireless earbuds with noise cancellation',
        'price': 49.99,
        'commission_rate': 15.0,
        'commission_amount': 7.50,
        'category': 'Electronics',
        'rating': 4.8
    }

    # Initialize video creator
    creator = VideoCreator(VIDEO_CONFIG, ASSETS_DIR)

    # Create video
    output_path = VIDEOS_DIR / "example_video.mp4"
    print(f"\nCreating video for: {product['name']}")
    print(f"Output: {output_path}")

    success = creator.create_product_video(product, output_path, template="modern")

    if success:
        print(f"\n✅ Video created successfully!")
        print(f"Location: {output_path}")
    else:
        print("\n❌ Video creation failed. Check logs.")


def example_3_generate_captions():
    """Example: Generate multiple caption variations"""
    print("=" * 60)
    print("Example 3: Generating Captions")
    print("=" * 60)

    # Load credentials
    with open(BASE_DIR / "config" / "credentials.json") as f:
        credentials = json.load(f)

    product = {
        'name': 'Smart Fitness Watch',
        'price': 79.99,
        'commission_rate': 20.0,
        'commission_amount': 16.00,
        'category': 'Fitness',
        'rating': 4.7
    }

    # Initialize caption generator
    generator = CaptionGenerator(AI_CONFIG, HASHTAG_CONFIG, credentials)

    # Generate variations
    print(f"\nGenerating 3 caption variations for: {product['name']}")
    variations = generator.create_multiple_variations(product, count=3)

    for i, (caption, hashtags) in enumerate(variations, 1):
        print(f"\n--- Variation {i} ---")
        print(f"Caption: {caption}")
        print(f"Hashtags: {hashtags}")

    print("\n✅ Done!\n")


def example_4_complete_workflow():
    """Example: Complete workflow from fetch to video creation"""
    print("=" * 60)
    print("Example 4: Complete Workflow")
    print("=" * 60)

    # Load credentials
    with open(BASE_DIR / "config" / "credentials.json") as f:
        credentials = json.load(f)

    # Initialize all components
    db = Database(DATABASE_PATH)
    fetcher = ProductFetcher(credentials, PRODUCT_FILTERS)
    creator = VideoCreator(VIDEO_CONFIG, ASSETS_DIR)
    caption_gen = CaptionGenerator(AI_CONFIG, HASHTAG_CONFIG, credentials)

    # Step 1: Fetch products
    print("\n[Step 1] Fetching products...")
    products = fetcher.fetch_trending_products(limit=3)
    print(f"  Found {len(products)} products")

    # Step 2: Save to database
    print("\n[Step 2] Saving to database...")
    for product in products:
        product_id = db.add_product(product)
        if product_id > 0:
            print(f"  ✓ Saved: {product['name']}")

    # Step 3: Select first product for video
    print("\n[Step 3] Selecting product for video creation...")
    selected_product = products[0]
    db.update_product_status(selected_product['product_id'], 'selected')
    print(f"  Selected: {selected_product['name']}")

    # Step 4: Generate caption
    print("\n[Step 4] Generating caption and hashtags...")
    caption, hashtags = caption_gen.create_full_post(selected_product)
    print(f"  Caption: {caption[:50]}...")
    print(f"  Hashtags: {hashtags}")

    # Step 5: Create video
    print("\n[Step 5] Creating video...")
    video_path = VIDEOS_DIR / f"{selected_product['product_id']}_video.mp4"
    success = creator.create_product_video(selected_product, video_path)

    if success:
        # Step 6: Save video record
        print("\n[Step 6] Saving video record...")
        db.add_video({
            'product_id': selected_product['product_id'],
            'video_path': str(video_path),
            'caption': caption,
            'hashtags': hashtags,
            'status': 'created'
        })
        print(f"  ✓ Video saved to database")

        print("\n✅ Complete workflow finished!")
        print(f"\nNext step: Review video at {video_path}")
        print("Then use the GUI or uploader to post to TikTok")
    else:
        print("\n❌ Video creation failed")


def example_5_database_queries():
    """Example: Query database for statistics"""
    print("=" * 60)
    print("Example 5: Database Queries")
    print("=" * 60)

    db = Database(DATABASE_PATH)

    # Get statistics
    print("\n[Statistics]")
    stats = db.get_stats()
    print(f"  Total Products: {stats['total_products']}")
    print(f"  Total Videos: {stats['total_videos']}")
    print(f"  Posted Videos: {stats['posted_videos']}")
    print(f"  Total Views: {stats['total_views']}")
    print(f"  Total Likes: {stats['total_likes']}")

    # Get recent products
    print("\n[Recent Products]")
    products = db.get_products()[:5]
    for p in products:
        print(f"  • {p['name']} | ${p['price']} | {p['commission_rate']}% | {p['status']}")

    # Get recent videos
    print("\n[Recent Videos]")
    videos = db.get_videos()[:5]
    for v in videos:
        print(f"  • {v['product_id']} | {v['status']} | {v['date_created']}")

    print("\n✅ Done!\n")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print(" ClickTok - Example Usage Script")
    print("=" * 60)
    print("\nChoose an example to run:")
    print("1. Fetch Products")
    print("2. Create Single Video")
    print("3. Generate Captions")
    print("4. Complete Workflow")
    print("5. Database Queries")
    print("6. Run All Examples")
    print("0. Exit")

    choice = input("\nEnter choice (0-6): ").strip()

    examples = {
        '1': example_1_fetch_products,
        '2': example_2_create_single_video,
        '3': example_3_generate_captions,
        '4': example_4_complete_workflow,
        '5': example_5_database_queries,
    }

    if choice == '0':
        print("\nGoodbye!")
        return
    elif choice == '6':
        print("\nRunning all examples...\n")
        for func in examples.values():
            func()
            input("\nPress Enter to continue to next example...")
    elif choice in examples:
        examples[choice]()
    else:
        print("\nInvalid choice!")


if __name__ == "__main__":
    main()
