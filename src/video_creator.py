"""
Video Creator Module
Generates TikTok-ready videos with product images, text overlays, and music
"""
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import random
import requests

# Fix for PIL.Image.ANTIALIAS deprecation in newer Pillow versions
# This must be done BEFORE importing MoviePy, as MoviePy uses ANTIALIAS internally
from PIL import Image
try:
    # Try to use the new Resampling enum (Pillow 10.0.0+)
    if hasattr(Image, 'Resampling'):
        Image.ANTIALIAS = Image.Resampling.LANCZOS
    elif not hasattr(Image, 'ANTIALIAS'):
        # Fallback for older Pillow versions
        Image.ANTIALIAS = Image.LANCZOS
except:
    # If Resampling doesn't exist, use LANCZOS directly
    if not hasattr(Image, 'ANTIALIAS'):
        Image.ANTIALIAS = Image.LANCZOS

# MoviePy imports (after fixing ANTIALIAS)
from moviepy.editor import (
    ImageClip, TextClip, CompositeVideoClip, AudioFileClip,
    VideoFileClip, concatenate_videoclips, ColorClip, CompositeAudioClip
)
from moviepy.video.fx.all import fadein, fadeout, resize
from moviepy.video.tools.subtitles import SubtitlesClip
from PIL import ImageDraw, ImageFont, ImageFilter
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
        
        # Ensure products directory exists
        products_dir = self.assets_dir.parent / "data" / "products"
        products_dir.mkdir(parents=True, exist_ok=True)

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

    def download_product_image(self, product: Dict) -> bool:
        """
        Download product image for a product (public method)
        
        Args:
            product: Product dictionary with 'product_id' and 'image_url'
            
        Returns:
            True if download successful or already exists, False otherwise
        """
        product_image_path = self.assets_dir.parent / "data" / "products" / f"{product['product_id']}.jpg"
        
        # If image already exists, return True
        if product_image_path.exists():
            logger.debug(f"Image already exists: {product_image_path}")
            return True
        
        # Try to download
        image_url = product.get('image_url', '')
        if image_url and image_url.startswith('http'):
            return self._download_product_image(image_url, product_image_path)
        else:
            logger.warning(f"No valid image URL for product {product.get('name', 'Unknown')}")
            return False
    
    def _download_product_image(self, image_url: str, save_path: Path) -> bool:
        """
        Download product image from URL (internal method)
        
        Args:
            image_url: URL of the product image
            save_path: Path where to save the image
            
        Returns:
            True if download successful, False otherwise
        """
        if not image_url or not image_url.startswith('http'):
            logger.warning(f"Invalid image URL: {image_url}")
            return False
            
        try:
            logger.info(f"Downloading product image from {image_url}")
            response = requests.get(image_url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            # Save image
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Successfully downloaded image to {save_path}")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to download image from {image_url}: {e}")
            return False

    def _create_product_clip(self, product: Dict, template: str) -> ImageClip:
        """
        Create the main product visual clip
        Downloads or uses cached product image
        """
        product_image_path = self.assets_dir.parent / "data" / "products" / f"{product['product_id']}.jpg"

        if product_image_path.exists():
            # Load actual product image
            logger.debug(f"Using cached image: {product_image_path}")
            img = Image.open(product_image_path)
        else:
            # Try to download the image
            image_url = product.get('image_url', '')
            if image_url and image_url.startswith('http'):
                logger.info(f"Image not cached, downloading from {image_url}")
                if self._download_product_image(image_url, product_image_path):
                    # Successfully downloaded, load it
                    img = Image.open(product_image_path)
                else:
                    # Download failed, create placeholder
                    logger.warning(f"Download failed, creating placeholder for {product.get('name', 'Unknown')}")
                    img = self._create_placeholder_image(product)
                    img.save(product_image_path)
            else:
                # No valid image URL, create placeholder
                logger.info(f"No valid image URL, creating placeholder for {product.get('name', 'Unknown')}")
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

    def _create_text_overlays(self, product: Dict, template: str) -> List[ImageClip]:
        """Create animated text overlays using PIL (no ImageMagick required)"""
        text_clips = []
        
        # Title text (product name)
        title_text = product['name'][:40]
        title_img = self._create_text_image(title_text, fontsize=70, color='white', 
                                           stroke_color='black', bg_color=None,
                                           width=self.resolution[0] - 100)
        title = ImageClip(title_img)
        title = title.set_position(('center', 100))
        title = title.set_duration(self.duration)
        text_clips.append(title)
        
        # Price text
        price_text = f"${product['price']}"
        price_img = self._create_text_image(price_text, fontsize=90, color='yellow',
                                          stroke_color='black', bg_color=None, width=400)
        price = ImageClip(price_img)
        price = price.set_position(('center', self.resolution[1] - 400))
        price = price.set_duration(self.duration)
        # Pulse effect
        price = price.resize(lambda t: 1 + 0.1 * np.sin(2 * np.pi * t))
        text_clips.append(price)
        
        # Commission text
        commission_text = f"Earn ${product['commission_amount']:.2f}!"
        commission_img = self._create_text_image(commission_text, fontsize=50, 
                                                 color='lightgreen', stroke_color='black',
                                                 bg_color=None, width=500)
        commission = ImageClip(commission_img)
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
        cta_img = self._create_text_image(cta_text, fontsize=60, color='white',
                                          stroke_color='black', bg_color='red', width=400)
        cta = ImageClip(cta_img)
        cta = cta.set_position(('center', self.resolution[1] - 200))
        cta = cta.set_start(self.duration - 4)  # Last 4 seconds
        cta = cta.set_duration(4)
        text_clips.append(cta)
        
        return text_clips
    
    def _create_text_image(self, text: str, fontsize: int, color: str, 
                          stroke_color: str, bg_color: Optional[str] = None,
                          width: int = 500) -> np.ndarray:
        """Create a text image using PIL (no ImageMagick required)"""
        # Estimate height based on font size
        height = int(fontsize * 1.5)
        
        # Create image with background color or transparent
        if bg_color:
            # Convert color name to RGB
            color_map = {
                'red': (255, 0, 0, 255),
                'blue': (0, 0, 255, 255),
                'green': (0, 255, 0, 255),
                'yellow': (255, 255, 0, 255),
                'white': (255, 255, 255, 255),
                'black': (0, 0, 0, 255)
            }
            bg_rgba = color_map.get(bg_color.lower(), (255, 0, 0, 255))
            img = Image.new('RGBA', (width, height), bg_rgba)
        else:
            img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        
        draw = ImageDraw.Draw(img)
        
        # Try to load a font
        try:
            font_paths = [
                "arial.ttf",
                "Arial.ttf",
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/Arial.ttf",
            ]
            font = None
            for font_path in font_paths:
                try:
                    font = ImageFont.truetype(font_path, fontsize)
                    break
                except:
                    continue
            if font is None:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # Convert color names to RGB
        color_map = {
            'white': (255, 255, 255, 255),
            'black': (0, 0, 0, 255),
            'yellow': (255, 255, 0, 255),
            'lightgreen': (144, 238, 144, 255),
            'red': (255, 0, 0, 255)
        }
        text_rgba = color_map.get(color.lower(), (255, 255, 255, 255))
        stroke_rgba = color_map.get(stroke_color.lower(), (0, 0, 0, 255))
        
        # Wrap text if needed
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= width - 40:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw each line
        line_height = int(fontsize * 1.2)
        start_y = (height - (len(lines) * line_height)) // 2
        
        for i, line in enumerate(lines):
            y_pos = start_y + (i * line_height)
            x_pos = width // 2
            
            # Draw stroke (outline) first
            stroke_width = 3 if fontsize >= 70 else 2
            for adj in range(-stroke_width, stroke_width + 1):
                for adj2 in range(-stroke_width, stroke_width + 1):
                    if adj != 0 or adj2 != 0:
                        draw.text((x_pos + adj, y_pos + adj2), line, 
                                 font=font, fill=stroke_rgba, anchor='mm')
            
            # Draw main text
            draw.text((x_pos, y_pos), line, font=font, fill=text_rgba, anchor='mm')
        
        # Convert PIL image to numpy array for MoviePy
        return np.array(img)

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

    def _add_background_music(self, video: CompositeVideoClip, volume: float = 0.3) -> CompositeVideoClip:
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
            audio = audio.volumex(volume)  # Adjustable volume

            # If video already has audio (narration), composite it
            if video.audio:
                video = video.set_audio(CompositeAudioClip([video.audio, audio]))
            else:
                video = video.set_audio(audio)
            
            logger.info(f"Added background music: {music_path.name}")

        except Exception as e:
            logger.warning(f"Could not add music: {e}")

        return video

    def create_product_video_with_script(
        self,
        product: Dict,
        script: str,
        output_path: Path,
        narration_audio_path: Optional[Path] = None,
        duration: int = 15,
        template: str = "modern"
    ) -> bool:
        """
        Create a video with script narration and subtitles
        
        Args:
            product: Product data dictionary
            script: Script text to narrate and display as subtitles
            output_path: Where to save the video
            narration_audio_path: Path to narration audio file (if using ElevenLabs)
            duration: Video duration in seconds
            template: Video style template
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Creating video with script for: {product['name']}")
            self.duration = duration  # Update duration
            
            # Step 1: Create background
            background = self._create_background(template)
            
            # Step 2: Add product image/visuals
            product_clip = self._create_product_clip(product, template)
            
            # Step 3: Create script-based subtitles
            subtitle_clips = self._create_script_subtitles(script, template)
            
            # Step 4: Add logo/watermark
            logo_clip = self._add_watermark()
            
            # Step 5: Combine all visual elements
            all_clips = [background, product_clip] + subtitle_clips
            if logo_clip:
                all_clips.append(logo_clip)
            
            video = CompositeVideoClip(all_clips, size=self.resolution)
            video = video.set_duration(duration)
            
            # Step 6: Add narration audio (if available) or background music
            if narration_audio_path and narration_audio_path.exists():
                try:
                    narration_audio = AudioFileClip(str(narration_audio_path))
                    narration_audio = narration_audio.subclip(0, min(narration_audio.duration, duration))
                    # Set narration volume higher than background music
                    narration_audio = narration_audio.volumex(0.9)
                    video = video.set_audio(narration_audio)
                    logger.info("Added narration audio")
                except Exception as e:
                    logger.warning(f"Could not add narration audio: {e}")
                    # Fallback to background music
                    video = self._add_background_music(video, volume=0.2)  # Lower volume with narration
            else:
                # Add background music
                video = self._add_background_music(video)
            
            # Step 7: Add transitions
            video = fadein(video, duration=0.5)
            video = fadeout(video, duration=0.5)
            
            # Step 8: Export
            logger.info(f"Rendering video with script to {output_path}")
            video.write_videofile(
                str(output_path),
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                logger=None
            )
            
            video.close()
            logger.info("Video with script created successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Error creating video with script: {e}", exc_info=True)
            return False
    
    def _create_script_subtitles(self, script: str, template: str) -> List[ImageClip]:
        """Create animated subtitle clips from script text using PIL (no ImageMagick required)"""
        subtitle_clips = []
        
        # Split script into sentences or phrases for display
        import re
        sentences = re.split(r'[.!?]\s+', script)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # If script is short, display as single subtitle
        if len(script) < 100:
            sentences = [script]
        
        # Calculate timing for each subtitle
        words_per_second = 2.5  # Average speaking rate
        total_words = len(script.split())
        total_duration = min(total_words / words_per_second, self.duration)
        
        if len(sentences) == 1:
            # Single subtitle - display throughout most of video
            start_time = 0.5
            end_time = self.duration - 0.5
            subtitle_img = self._create_subtitle_image(script[:100], template)
            subtitle = ImageClip(subtitle_img)
            subtitle = subtitle.set_position(('center', self.resolution[1] - 300))
            subtitle = subtitle.set_start(start_time).set_duration(end_time - start_time)
            subtitle_clips.append(subtitle)
        else:
            # Multiple subtitles - display sequentially
            time_per_sentence = total_duration / len(sentences)
            current_time = 0.5
            
            for i, sentence in enumerate(sentences[:10]):  # Limit to 10 subtitles
                if current_time >= self.duration - 1:
                    break
                    
                # Create subtitle image using PIL
                subtitle_img = self._create_subtitle_image(sentence[:80], template)
                subtitle = ImageClip(subtitle_img)
                subtitle = subtitle.set_position(('center', self.resolution[1] - 250))
                
                # Duration with fade
                duration = min(time_per_sentence, self.duration - current_time - 0.5)
                subtitle = subtitle.set_start(current_time).set_duration(duration)
                
                # Add fade effect
                subtitle = subtitle.crossfadein(0.3).crossfadeout(0.3)
                
                subtitle_clips.append(subtitle)
                current_time += time_per_sentence
        
        return subtitle_clips
    
    def _create_subtitle_image(self, text: str, template: str) -> np.ndarray:
        """Create a subtitle image using PIL (no ImageMagick required)"""
        # Create a transparent background image
        img_width = self.resolution[0] - 120
        img_height = 150
        
        # Create RGBA image with transparent background
        img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Try to load a font
        try:
            # Try different font paths
            font_paths = [
                "arial.ttf",
                "Arial.ttf",
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/Arial.ttf",
            ]
            font = None
            for font_path in font_paths:
                try:
                    font = ImageFont.truetype(font_path, 55)
                    break
                except:
                    continue
            if font is None:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # Text color based on template
        if template == "minimal":
            text_color = (50, 50, 50, 255)  # Dark gray
            stroke_color = (255, 255, 255, 255)  # White stroke
        else:
            text_color = (255, 255, 255, 255)  # White
            stroke_color = (0, 0, 0, 255)  # Black stroke
        
        # Wrap text to fit width
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= img_width - 40:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw each line
        line_height = 60
        start_y = (img_height - (len(lines) * line_height)) // 2
        
        for i, line in enumerate(lines):
            y_pos = start_y + (i * line_height)
            
            # Draw stroke (outline) first
            for adj in range(-2, 3):
                for adj2 in range(-2, 3):
                    if adj != 0 or adj2 != 0:
                        draw.text((img_width//2 + adj, y_pos + adj2), line, 
                                 font=font, fill=stroke_color, anchor='mm')
            
            # Draw main text
            draw.text((img_width//2, y_pos), line, font=font, 
                     fill=text_color, anchor='mm')
        
        # Convert PIL image to numpy array for MoviePy
        return np.array(img)
    
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
