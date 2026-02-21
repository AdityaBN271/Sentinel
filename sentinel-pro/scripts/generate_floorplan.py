from PIL import Image, ImageDraw

def generate_floorplan():
    # Create white canvas
    width, height = 800, 600
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Draw dark gray walls (rectangle)
    margin = 50
    wall_thickness = 10
    draw.rectangle([margin, margin, width - margin, height - margin], outline='black', width=wall_thickness)
    
    # Draw a door gap on the left wall
    door_size = 80
    door_y_start = height // 2 - door_size // 2
    draw.rectangle([margin - 2, door_y_start, margin + wall_thickness + 2, door_y_start + door_size], fill='white', outline='white')
    
    # Draw door swing arc (optional but nice)
    draw.arc([margin - door_size, door_y_start, margin + door_size, door_y_start + door_size * 2], start=270, end=360, fill='black')
    
    # Draw two windows on the right wall
    window_size = 60
    window_padding = 100
    # Window 1
    draw.rectangle([width - margin - wall_thickness - 2, window_padding, width - margin + 2, window_padding + window_size], fill='lightblue', outline='black')
    # Window 2
    draw.rectangle([width - margin - wall_thickness - 2, height - window_padding - window_size, width - margin + 2, height - window_padding], fill='lightblue', outline='black')

    # Save to artifacts directory
    path = r"C:\Users\soura\.gemini\antigravity\brain\cb788982-7cb7-45b6-b03c-9003de12823b\simple_floor_plan.png"
    img.save(path)
    print(f"Floor plan saved to: {path}")

if __name__ == "__main__":
    generate_floorplan()
