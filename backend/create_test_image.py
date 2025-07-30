from PIL import Image, ImageDraw, ImageFont
import os

def create_test_image():
    """Create a simple test PNG image"""
    
    # Create a 200x200 image with a white background
    img = Image.new('RGB', (200, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw a simple pattern
    draw.rectangle([50, 50, 150, 150], outline='blue', width=3)
    draw.text((60, 80), "Test", fill='black')
    draw.text((60, 100), "Image", fill='black')
    
    # Save as PNG
    test_image_path = "uploads/test_image.png"
    img.save(test_image_path, "PNG")
    
    print(f"✅ Created test image: {test_image_path}")
    print(f"📁 File size: {os.path.getsize(test_image_path)} bytes")
    
    return test_image_path

if __name__ == "__main__":
    try:
        from PIL import Image, ImageDraw
        create_test_image()
    except ImportError:
        print("❌ PIL/Pillow not installed. Creating a simple text file instead.")
        # Fallback: create a simple text file
        test_content = "This is a test file for gallery upload testing.\n" * 10
        with open("uploads/test_image.txt", "w") as f:
            f.write(test_content)
        print("✅ Created test file: uploads/test_image.txt") 