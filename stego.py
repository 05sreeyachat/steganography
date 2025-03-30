from PIL import Image
import numpy as np
import os

class Steganography:
    def __init__(self):
        self.delimiter = "$$END$$"

    def text_to_binary(self, text):
        binary = ''.join(format(ord(char), '08b') for char in text)
        return binary + ''.join(format(ord(char), '08b') for char in self.delimiter)

    def binary_to_text(self, binary):
        text = ''
        for i in range(0, len(binary), 8):
            byte = binary[i:i+8]
            text += chr(int(byte, 2))
            if text.endswith(self.delimiter):
                return text[:-len(self.delimiter)]
        return text

    def encode(self, image_path, message, output_path):
        try:
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            pixels = np.array(img, dtype=np.uint8)
            
            binary_message = self.text_to_binary(message)
            print(f"Debug: Message length in bits: {len(binary_message)}")  # Debug info
            
            if len(binary_message) > pixels.size // 3:
                raise ValueError("Message too large for this image")

            flat_pixels = pixels.reshape(-1, 3)
            
            # Store the message length at the start
            message_length = len(binary_message)
            length_binary = format(message_length, '032b')  # 32 bits for length
            
            # First store the length
            for i in range(32):
                channel_index = i % 3
                pixel_index = i // 3
                pixel_value = int(flat_pixels[pixel_index][channel_index])
                new_value = (pixel_value & ~1) | int(length_binary[i])
                flat_pixels[pixel_index][channel_index] = np.uint8(new_value)
            
            # Then store the message
            for i in range(len(binary_message)):
                channel_index = (i + 32) % 3  # Offset by length storage
                pixel_index = (i + 32) // 3
                pixel_value = int(flat_pixels[pixel_index][channel_index])
                new_value = (pixel_value & ~1) | int(binary_message[i])
                flat_pixels[pixel_index][channel_index] = np.uint8(new_value)
            
            modified_pixels = flat_pixels.reshape(pixels.shape)
            modified_image = Image.fromarray(modified_pixels)
            modified_image.save(output_path, 'PNG')
            print(f"Message hidden successfully in {output_path}")
            
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            raise e

    def decode(self, image_path):
        try:
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            pixels = np.array(img, dtype=np.uint8)
            
            flat_pixels = pixels.reshape(-1, 3)
            
            # First read the message length
            length_binary = ''
            for i in range(32):
                channel_index = i % 3
                pixel_index = i // 3
                length_binary += str(flat_pixels[pixel_index][channel_index] & 1)
            
            message_length = int(length_binary, 2)
            print(f"Debug: Expected message length: {message_length} bits")  # Debug info
            
            # Then read the message
            binary_message = ''
            for i in range(message_length):
                channel_index = (i + 32) % 3
                pixel_index = (i + 32) // 3
                binary_message += str(flat_pixels[pixel_index][channel_index] & 1)
            
            text = self.binary_to_text(binary_message)
            return text
            
        except Exception as e:
            print(f"Decoding error: {e}")
            return None

# Example usage
if __name__ == "__main__":
    stego = Steganography()
    
    print("\n=== Steganography Tool ===")
    print("1. Hide a message")
    print("2. Reveal a message")
    choice = input("Choose an option (1/2): ")
    
    if choice == "1":
        message = input("\nEnter the secret message to hide: ")
        try:
            stego.encode("input.png", message, "output.png")
            print("\nOriginal message:", message)
            print("Image with hidden message saved as 'output.png'")
            print("\nVerifying message...")
            decoded = stego.decode("output.png")
            if decoded == message:
                print("✓ Message verified successfully!")
            else:
                print("⚠ Warning: Message verification failed")
        except Exception as e:
            print(f"Error: {e}")
            
    elif choice == "2":
        try:
            filename = input("\nEnter image filename to check (e.g., output.png): ")
            message = stego.decode(filename)
            if message:
                print("\nFound hidden message:", message)
            else:
                print("\nNo message found in this image")
        except Exception as e:
            print(f"Error: {e}")
    
    else:
        print("Invalid choice!")