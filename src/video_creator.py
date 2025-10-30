"""
Video Creator Module
Generates TikTok-ready videos with product images, text overlays, and music
"""
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import random

# MoviePy imports
from moviepy.editor import (
    ImageClip, TextClip, CompositeVideoClip, AudioFileClip,
    VideoFileClip, concatenate_videoclips, ColorClip
)
from moviepy.video.fx.all import fadein, fadeout, resize
from moviepy.video.tools.subtitles import SubtitlesClip
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

logger = logging.getLogger(__name__)


class VideoCreator:
    """Creates engaging TikTok videos for affiliate products"""

    def __init__(self, config: Dict, assets_dir: Path):
        self.config = config
        self.assets_dir = assets_dir
        self.resolution = config.get('resolution', (1080, 1920))  # width x height (9:16)
        self.fps = config.get('fps', 30)
        self.duration = config.get('duration', 15)

    def create_product_video(
        self,
        product: Dict,
        output_path: Path,
        template: str = "modern"
    ) -> bool:
        """
        Create a complete product video

        Args:
            product: Product data dictionary
            output_path: Where to save the video
            template: Video style template ('modern', 'minimal', 'energetic')

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Creating video for: {product['name']}")

            # Step 1: Create background
            background = self._create_background(template)

            # Step 2: Add product image/visuals
            product_clip = self._create_product_clip(product, template)

            # Step 3: Create text overlays
            text_clips = self._create_text_overlays(product, template)

            # Step 4: Add logo/watermark
            logo_clip = self._add_watermark()

            # Step 5: Combine all elements
            all_clips = [background, product_clip] + text_clips
            if logo_clip:
                all_clips.append(logo_clip)

            video = CompositeVideoClip(all_clips, size=self.resolution)
            video = video.set_duration(self.duration)

            # Step 6: Add background music
            video = self._add_background_music(video)

            # Step 7: Add transitions
            video = fadein(video, duration=0.5)
            video = fadeout(video, duration=0.5)

            # Step 8: Export
            logger.info(f"Rendering video to {output_path}")
            video.write_videofile(
                str(output_path),
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                logger=None  # Suppress moviepy's verbose output
            )

            video.close()
            logger.info("Video created successfully!")
            return True

        except Exception as e:
            logger.error(f"Error creating video: {e}", exc_info=True)
            return False

    def _create_background(self, template: str) -> ColorClip:
        """Create background layer"""
        if template == "modern":
            # Gradient background (simplified - use PIL for real gradient)
            color = (20, 20, 40)  # Dark blue
        elif template == "minimal":
            color = (255, 255, 255)  # White
        else:  # energetic
            color = (255, 50, 100)  # Vibrant pink

        bg = ColorClip(size=self.resolution, color=color)
        bg = bg.set_duration(self.duration)
        return bg

    def _create_product_clip(self, product: Dict, template: str) -> ImageClip:
        """
        Create the main product visual clip
        Downloads or uses cached product image
        """
        # In real implementation, download and cache the image
        # For now, create a placeholder
        product_image_path = self.assets_dir.parent / "data" / "products" / f"{product['product_id']}.jpg"

        if product_image_path.exists():
            # Load actual product image
            img = Image.open(product_image_path)
        else:
            # Create placeholder
            img = self._create_placeholder_image(product)
            img.save(product_image_path)

        # Resize to fit in center of frame
        img = self._prepare_product_image(img, template)
        temp_path = product_image_path.parent / f"{product['product_id']}_processed.png"
        img.save(temp_path)

        # Create clip from image
        clip = ImageClip(str(temp_path))
        clip = clip.set_duration(self.duration)

        # Position in center
        clip = clip.set_position(('center', 'center'))

        # Add zoom effect
        clip = clip.resize(lambda t: 1 + 0.05 * t / self.duration)  # Slow zoom

        return clip

    def _create_placeholder_image(self, product: Dict) -> Image.Image:
        """Create a placeholder image with product name"""
        img = Image.new('RGB', (800, 800), color=(200, 200, 200))
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()

        # Draw product name
        text = product['name'][:30]
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((800 - text_width) / 2, (800 - text_height) / 2)

        draw.text(position, text, fill=(50, 50, 50), font=font)

        return img

    def _prepare_product_image(self, img: Image.Image, template: str) -> Image.Image:
        """Prepare product image with effects"""
        # Resize to fit
        max_size = (int(self.resolution[0] * 0.8), int(self.resolution[1] * 0.6))
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Add shadow/glow effect
        if template == "modern":
            # Add subtle shadow
            shadow = Image.new('RGBA', (img.width + 20, img.height + 20), (0, 0, 0, 0))
            shadow.paste((0, 0, 0, 100), (10, 10, img.width + 10, img.height + 10))
            shadow = shadow.filter(ImageFilter.GaussianBlur(10))
            shadow.paste(img, (10, 10), img if img.mode == 'RGBA' else None)
            img = shadow

        return img

    def _create_text_overlays(self, product: Dict, template: str) -> List[TextClip]:
        """Create animated text overlays"""
        text_clips = []

        # Title text (product name)
        title_text = product['name'][:40]
        title = TextClip(
            title_text,
            fontsize=70,
            color='white',
            font='Arial-Bold',
            stroke_color='black',
            stroke_width=3,
            method='caption',
            size=(self.resolution[0] - 100, None)
        )
        title = title.set_position(('center', 100))
        title = title.set_duration(self.duration)
        text_clips.append(title)

        # Price text
        price_text = f"${product['price']}"
        price = TextClip(
            price_text,
            fontsize=90,
            color='yellow',
            font='Arial-Bold',
            stroke_color='black',
            stroke_width=4
        )
        price = price.set_position(('center', self.resolution[1] - 400))
        price = price.set_duration(self.duration)
        # Pulse effect
        price = price.resize(lambda t: 1 + 0.1 * np.sin(2 * np.pi * t))
        text_clips.append(price)

        # Commission text
        commission_text = f"Earn ${product['commission_amount']:.2f}!"
        commission = TextClip(
            commission_text,
            fontsize=50,
            color='lightgreen',
            font='Arial-Bold',
            stroke_color='black',
            stroke_width=2
        )
        commission = commission.set_position(('center', self.resolution[1] - 300))
        commission = commission.set_duration(self.duration)
        text_clips.append(commission)

        # Call to action
        cta_texts = [
            "Shop Now! 🛒",
            "Limited Stock! ⚡",
            "Click Link! 👆",
            "Tap to Buy! 💸"
        ]
        cta_text = random.choice(cta_texts)
        cta = TextClip(
            cta_text,
            fontsize=60,
            color='white',
            font='Arial-Bold',
            bg_color='red',
            method='caption',
            size=(400, None)
        )
        cta = cta.set_position(('center', self.resolution[1] - 200))
        cta = cta.set_start(self.duration - 4)  # Last 4 seconds
        cta = cta.set_duration(4)
        text_clips.append(cta)

        return text_clips

    def _add_watermark(self) -> Optional[ImageClip]:
        """Add logo watermark"""
        logo_path = self.assets_dir / "logo.png"

        if not logo_path.exists():
            logger.warning("Logo not found, skipping watermark")
            return None

        try:
            logo = ImageClip(str(logo_path))
            logo = logo.resize(height=80)  # Small logo
            logo = logo.set_duration(self.duration)
            logo = logo.set_position((20, 20))  # Top-left corner
            logo = logo.set_opacity(0.7)
            return logo
        except Exception as e:
            logger.warning(f"Could not add logo: {e}")
            return None

    def _add_background_music(self, video: CompositeVideoClip) -> CompositeVideoClip:
        """Add background music to video"""
        music_dir = self.assets_dir / "music"

        if not music_dir.exists() or not list(music_dir.glob("*.mp3")):
            logger.warning("No background music found")
            return video

        try:
            # Pick random music file
            music_files = list(music_dir.glob("*.mp3"))
            music_path = random.choice(music_files)

            audio = AudioFileClip(str(music_path))
            audio = audio.subclip(0, min(audio.duration, self.duration))
            audio = audio.volumex(0.3)  # Lower volume

            video = video.set_audio(audio)
            logger.info(f"Added background music: {music_path.name}")

        except Exception as e:
            logger.warning(f"Could not add music: {e}")

        return video

    def create_batch_videos(
        self,
        products: List[Dict],
        output_dir: Path,
        template: str = "modern"
    ) -> List[Path]:
        """Create videos for multiple products"""
        created_videos = []

        for i, product in enumerate(products, 1):
            logger.info(f"Creating video {i}/{len(products)}")
            output_path = output_dir / f"{product['product_id']}_video.mp4"

            if self.create_product_video(product, output_path, template):
                created_videos.append(output_path)

        logger.info(f"Created {len(created_videos)} videos successfully")
        return created_videos


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    from config.settings import VIDEO_CONFIG, ASSETS_DIR, VIDEOS_DIR

    # Demo product
    product = {
        'product_id': 'DEMO_0001',
        'name': 'Wireless Bluetooth Earbuds Pro',
        'price': 49.99,
        'commission_rate': 15.0,
        'commission_amount': 7.50,
        'rating': 4.8
    }

    creator = VideoCreator(VIDEO_CONFIG, ASSETS_DIR)
    output_path = VIDEOS_DIR / "demo_video.mp4"

    creator.create_product_video(product, output_path, template="modern")
    print(f"Video created: {output_path}")
