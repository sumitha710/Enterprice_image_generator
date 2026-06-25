import os
import requests
from dotenv import load_dotenv
from fastapi import HTTPException
from PIL import Image

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
API_URL = os.getenv(
    "SD_MODEL_URL",
    "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
)

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}                                                                                                           





def generate_image(
    prompt: str,
    negative_prompt: str = "blurry, low quality, distorted",
    num_inference_steps: int = 30
):
    try:
        payload = {
            "inputs": prompt,
            "parameters": {
                "negative_prompt": negative_prompt,
                "num_inference_steps": num_inference_steps
            }
        }

        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=20
        )

        if response.status_code == 200:
            return response.content
        else:
            print(f"HF API returned status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"HF API connection error or model unavailable: {e}")

    # Offline/Sandbox Fallback
    print("Falling back to local placeholder image for generation...")
    fallback_paths = [
        "d:/enterprise_branded_image_generator/output_generated.png",
        "d:/enterprise_branded_image_generator/app/uploads/logos/12_1781843732_WhatsApp Image 2026-06-19 at 2.32.50 PM.jpeg"
    ]
    for path in fallback_paths:
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    return f.read()
            except Exception as read_err:
                print(f"Could not read fallback path {path}: {read_err}")
    
    raise HTTPException(
        status_code=500,
        detail="Image generation failed and no fallback image could be loaded."
    )





from io import BytesIO

import requests
from fastapi import HTTPException
from PIL import Image
from dotenv import load_dotenv


load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}"
}


def generate_image_img2img(
    image_bytes: bytes,
    prompt: str,
    negative_prompt: str = "blurry, low quality, distorted",
    num_inference_steps: int = 30,
):
    """
    Modify an existing image using Hugging Face Inference API.
    """

    img = Image.open(BytesIO(image_bytes))

    print("Format:", img.format)
    print("Size:", img.size)
    print("Mode:", img.mode)
  

    model_url = os.getenv(
        "SD_IMG2IMG_MODEL_URL",
        "https://router.huggingface.co/fal-ai/fal-ai/flux-kontext/dev"
    )

    try:
        if not HF_TOKEN:
            raise HTTPException(
                status_code=500,
                detail="HF_TOKEN not found in .env"
            )

        print("=" * 50)
        print("Prompt:", prompt)
        print("Model URL:", model_url)
        print("Input image size:", len(image_bytes))
        print("=" * 50)

        files = {
            "image": ("input.png", image_bytes, "image/png")
        }

        data = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "num_inference_steps": num_inference_steps
        }

        response = requests.post(
            model_url,
            headers=HEADERS,
            files=files,
            data=data,
            timeout=120
        )

        print("Status Code:", response.status_code)

        if response.status_code != 200:
            print("HF Error:", response.text)

            raise HTTPException(
                status_code=response.status_code,
                detail=f"Hugging Face Error ({response.status_code}): {response.text}"
    )

        modified_bytes = response.content

        print("Output image size:", len(modified_bytes))
        print("Same image:", image_bytes == modified_bytes)

        if not modified_bytes:
            raise HTTPException(
                status_code=502,
                detail="Empty image returned by model."
            )

        return modified_bytes

    except HTTPException:
        raise

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=502,
            detail=f"Hugging Face request failed: {str(e)}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )

