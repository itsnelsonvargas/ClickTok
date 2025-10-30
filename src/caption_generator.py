"""
Caption and Hashtag Generator
Creates engaging captions and relevant hashtags for TikTok posts
"""
import logging
import random
import json
from typing import Dict, List, Tuple, Optional
import re

logger = logging.getLogger(__name__)


class CaptionGenerator:
    """Generates TikTok captions and hashtags"""

    def __init__(self, ai_config: Dict, hashtag_config: Dict, credentials: Dict):
        self.ai_config = ai_config
        self.hashtag_config = hashtag_config
        self.credentials = credentials
        self.max_caption_length = 2200

        # Initialize AI client if configured
        self.ai_client = self._init_ai_client()

    def _init_ai_client(self):
        """Initialize AI client (OpenAI or Anthropic)"""
        provider = self.ai_config.get('provider', 'local')

        if provider == 'openai':
            try:
                import openai
                api_key = self.credentials.get('openai_api_key')
                if api_key and api_key != 'YOUR_OPENAI_API_KEY_HERE':
                    openai.api_key = api_key
                    logger.info("OpenAI client initialized")
                    return openai
            except ImportError:
                logger.warning("OpenAI package not installed")

        elif provider == 'anthropic':
            try:
                import anthropic
                api_key = self.credentials.get('anthropic_api_key')
                if api_key and api_key != 'YOUR_ANTHROPIC_API_KEY_HERE':
                    client = anthropic.Anthropic(api_key=api_key)
                    logger.info("Anthropic client initialized")
                    return client
            except ImportError:
                logger.warning("Anthropic package not installed")

        logger.info("Using local caption generation")
        return None

    def generate_caption(self, product: Dict) -> str:
        """Generate an engaging caption for the product"""
        if self.ai_client:
            return self._generate_ai_caption(product)
        else:
            return self._generate_template_caption(product)

    def _generate_ai_caption(self, product: Dict) -> str:
        """Generate caption using AI (OpenAI or Claude)"""
        prompt = f"""
Create an engaging TikTok caption for this product:

Product: {product['name']}
Price: ${product['price']}
Category: {product.get('category', 'General')}
Commission: ${product['commission_amount']} ({product['commission_rate']}%)

Requirements:
- Hook viewers in the first line
- Highlight the main benefit
- Create urgency
- Include a clear call-to-action
- Keep it under 150 characters
- Use emojis strategically
- Make it sound natural and exciting

Caption:
"""

        try:
            provider = self.ai_config.get('provider')

            if provider == 'openai':
                response = self.ai_client.ChatCompletion.create(
                    model=self.ai_config.get('model', 'gpt-3.5-turbo'),
                    messages=[
                        {"role": "system", "content": "You are a TikTok marketing expert who creates viral captions."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.ai_config.get('temperature', 0.7),
                    max_tokens=self.ai_config.get('max_tokens', 150)
                )
                caption = response.choices[0].message.content.strip()

            elif provider == 'anthropic':
                response = self.ai_client.messages.create(
                    model=self.ai_config.get('model', 'claude-3-haiku-20240307'),
                    max_tokens=self.ai_config.get('max_tokens', 150),
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                caption = response.content[0].text.strip()

            else:
                return self._generate_template_caption(product)

            logger.info("Generated AI caption")
            return caption

        except Exception as e:
            logger.error(f"Error generating AI caption: {e}")
            return self._generate_template_caption(product)

    def _generate_template_caption(self, product: Dict) -> str:
        """Generate caption using templates"""
        templates = [
            "🔥 OMG! You NEED this {name}! Only ${price}! {cta}",
            "✨ Best {category} product I've found! {name} for just ${price}! {cta}",
            "💸 STEAL ALERT! {name} at ${price}! Limited stock! {cta}",
            "🎯 This {name} changed everything! Only ${price}! {cta}",
            "⚡ Wait for it... {name} is only ${price}! {cta}",
            "🛒 Everyone's getting this {name}! Just ${price}! {cta}",
            "💎 Hidden gem alert! {name} - ${price}! You're welcome! {cta}",
            "🚨 Don't scroll! This {name} is ${price} and AMAZING! {cta}",
        ]

        ctas = [
            "Link in bio! 👆",
            "Tap the link! 🔗",
            "Shop now! 🛍️",
            "Grab yours! ⚡",
            "Click to buy! 💳",
            "Get it now! 🏃",
        ]

        template = random.choice(templates)
        caption = template.format(
            name=product['name'][:40],
            price=product['price'],
            category=product.get('category', 'product'),
            cta=random.choice(ctas)
        )

        return caption

    def generate_hashtags(self, product: Dict, count: int = 5) -> List[str]:
        """Generate relevant hashtags for the product"""
        hashtags = set()

        # Base hashtags from config
        base_tags = self.hashtag_config.get('base_tags', [])
        hashtags.update(base_tags)

        # Category-based hashtags
        category = product.get('category', '').lower()
        if category:
            hashtags.add(f"#{category}")
            hashtags.add(f"#{category}TikTok")

        # Product-specific hashtags
        product_name = product['name'].lower()
        words = re.findall(r'\w+', product_name)

        # Add product keywords as hashtags
        for word in words[:3]:  # First 3 words
            if len(word) > 3:  # Skip short words
                hashtags.add(f"#{word.capitalize()}")

        # Add trending/common hashtags
        trending_tags = self._get_trending_hashtags(category)
        hashtags.update(trending_tags)

        # Price-based hashtags
        if product['price'] < 20:
            hashtags.add("#AffordableFinds")
            hashtags.add("#BudgetFriendly")
        elif product['price'] > 100:
            hashtags.add("#LuxuryFinds")
            hashtags.add("#Premium")

        # Commission-based
        if product['commission_rate'] >= 15:
            hashtags.add("#AffiliateMarketing")

        # Convert to list and limit
        hashtag_list = list(hashtags)[:count]

        logger.info(f"Generated {len(hashtag_list)} hashtags")
        return hashtag_list

    def _get_trending_hashtags(self, category: str) -> List[str]:
        """Get trending hashtags for category"""
        # In production, you'd fetch these from TikTok API or trending database
        trending_by_category = {
            'electronics': ['#TechTikTok', '#GadgetReview', '#TechFinds'],
            'beauty': ['#BeautyTikTok', '#MakeupHaul', '#SkincareRoutine'],
            'fashion': ['#FashionTikTok', '#OOTD', '#StyleInspo'],
            'fitness': ['#FitTok', '#WorkoutMotivation', '#FitnessJourney'],
            'home': ['#HomeTikTok', '#HomeDecor', '#Organization'],
        }

        general_trending = [
            '#Viral',
            '#ForYou',
            '#FYP',
            '#MustHave',
            '#ProductReview'
        ]

        category_tags = trending_by_category.get(category.lower(), [])
        return category_tags + random.sample(general_trending, 2)

    def create_full_post(self, product: Dict) -> Tuple[str, str]:
        """
        Generate complete post with caption and hashtags

        Returns:
            Tuple of (caption, hashtags_string)
        """
        caption = self.generate_caption(product)
        hashtags = self.generate_hashtags(
            product,
            count=self.hashtag_config.get('max_hashtags_per_post', 5)
        )

        # Combine caption and hashtags
        hashtags_str = ' '.join(hashtags)
        full_caption = f"{caption}\n\n{hashtags_str}"

        # Ensure we don't exceed TikTok's limit
        if len(full_caption) > self.max_caption_length:
            # Trim caption if needed
            excess = len(full_caption) - self.max_caption_length
            caption = caption[:-excess-3] + "..."
            full_caption = f"{caption}\n\n{hashtags_str}"

        logger.info("Created full post")
        return caption, hashtags_str

    def create_multiple_variations(self, product: Dict, count: int = 3) -> List[Tuple[str, str]]:
        """Create multiple caption variations for A/B testing"""
        variations = []

        for i in range(count):
            caption, hashtags = self.create_full_post(product)
            variations.append((caption, hashtags))

        logger.info(f"Created {len(variations)} caption variations")
        return variations


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    product = {
        'name': 'Wireless Bluetooth Earbuds Pro',
        'price': 49.99,
        'commission_rate': 15.0,
        'commission_amount': 7.50,
        'category': 'Electronics',
        'rating': 4.8
    }

    ai_config = {
        'provider': 'local',
        'temperature': 0.7,
        'max_tokens': 150
    }

    hashtag_config = {
        'base_tags': ['#TikTokShop', '#TikTokAffiliate'],
        'max_hashtags_per_post': 5
    }

    credentials = {}

    generator = CaptionGenerator(ai_config, hashtag_config, credentials)

    # Generate single post
    caption, hashtags = generator.create_full_post(product)
    print("Caption:", caption)
    print("\nHashtags:", hashtags)

    # Generate variations
    print("\n\nVariations:")
    variations = generator.create_multiple_variations(product, count=3)
    for i, (cap, tags) in enumerate(variations, 1):
        print(f"\n--- Variation {i} ---")
        print(cap)
