import asyncio
import aiohttp
from random import randint
from PIL import Image
import os
from time import sleep
from dotenv import get_key

API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
API_KEY = get_key('.env', 'Hugging_FaceAPIKey')

if not API_KEY:
    raise ValueError("Hugging Face API Key not found! Check your .env file.")

HEADERS = {"Authorization": f"Bearer {API_KEY}"}
SEMAPHORE = asyncio.Semaphore(4)  
IMAGE_DIR = "Data"
FILE_PATH = "Frontend/Files/ImageGeneration.data"


async def show_image(image_path):
    """Opens an image file asynchronously."""
    try:
        img = Image.open(image_path)
        print(f"Opening: {image_path}")
        img.show()
    except IOError:
        print(f"Error opening: {image_path}")


async def query(session, payload):
    """Sends a request to the Hugging Face API and returns image bytes."""
    async with SEMAPHORE:
        for _ in range(3):  
            try:
                async with session.post(API_URL, headers=HEADERS, json=payload, timeout=30) as response:
                    if response.status == 200:
                        return await response.read()
                    print(f"API Error {response.status}: {await response.text()}")
            except Exception as e:
                print(f"Request failed: {e}")
            await asyncio.sleep(2)  
    return None


async def generate_images(prompt):
    """Generates images asynchronously using aiohttp and saves them immediately."""
    os.makedirs(IMAGE_DIR, exist_ok=True)

    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(4):
            payload = {
                "inputs": f"{prompt}, ultra high quality, detailed, high resolution",
                "parameters": {"seed": randint(0, 1000000)}
            }
            task = asyncio.create_task(generate_and_save_image(session, payload, prompt, i + 1))
            tasks.append(task)

        await asyncio.gather(*tasks)


async def generate_and_save_image(session, payload, prompt, index):
    """Handles individual image generation and saving."""
    image_bytes = await query(session, payload)
    if image_bytes:
        image_path = os.path.join(IMAGE_DIR, f"{prompt.replace(' ', '_')}{index}.jpg")
        await asyncio.to_thread(save_image, image_path, image_bytes)


def save_image(image_path, image_bytes):
    """Saves an image file."""
    with open(image_path, "wb") as f:
        f.write(image_bytes)
    print(f"✅ Saved: {image_path}")


async def open_images(prompt):
    """Opens generated images asynchronously."""
    tasks = []
    for i in range(1, 5):
        image_path = os.path.join(IMAGE_DIR, f"{prompt.replace(' ', '_')}{i}.jpg")
        if os.path.exists(image_path):
            tasks.append(asyncio.to_thread(show_image, image_path))

    await asyncio.gather(*tasks)


async def monitor_request_file():
    """Monitors the request file and triggers image generation when needed."""
    while True:
        try:
            if not os.path.exists(FILE_PATH):
                print("Waiting for request file...")
                await asyncio.sleep(1)
                continue

            with open(FILE_PATH, "r") as f:
                data = f.read().strip()

            if not data:
                await asyncio.sleep(1)
                continue

            try:
                prompt, status = data.split(",")
            except ValueError:
                print("Invalid file format. Resetting file.")
                with open(FILE_PATH, "w") as f:
                    f.write("False,False")
                await asyncio.sleep(1)
                continue

            if status.strip().lower() == "true":
                print("Generating Images...")
                await generate_images(prompt.strip())
                await open_images(prompt.strip())

                with open(FILE_PATH, "w") as f:
                    f.write("False,False")

                break  
            else:
                await asyncio.sleep(1)

        except Exception as e:
            print(f"Unexpected error: {e}")
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(monitor_request_file())
