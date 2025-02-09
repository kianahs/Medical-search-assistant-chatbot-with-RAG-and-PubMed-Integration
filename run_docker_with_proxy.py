import os
import subprocess

# Proxy
os.environ["HTTP_PROXY"] = "http://127.0.0.1:10809"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:10809"

print("HTTP_PROXY:", os.environ.get("HTTP_PROXY"))
print("HTTPS_PROXY:", os.environ.get("HTTPS_PROXY"))

# build
# subprocess.run(["docker-compose", "build"], check=True)

docker_username = "kianahs"
frontend_image_name = "medical-assistant-app-frontend"  # Your repo name
backend_image_name = "medical-assistant-app-backend"
tag = "first" 

# Tag built images
frontend_tagged = f"{docker_username}/{frontend_image_name}:{tag}"
backend_tagged = f"{docker_username}/{backend_image_name}:{tag}"

# Tag 
try:
    subprocess.run(["docker", "tag", "rag-frontend", frontend_tagged], check=True)  
    subprocess.run(["docker", "tag", "rag-backend", backend_tagged], check=True)  
    print(f"Successfully tagged images: {frontend_tagged} and {backend_tagged}")
except subprocess.CalledProcessError as e:
    print(f"Error tagging images: {e}")
    exit(1)

# Push images 
try:
    subprocess.run(["docker", "push", frontend_tagged], check=True)
    subprocess.run(["docker", "push", backend_tagged], check=True)
    print(f"Successfully pushed images: {frontend_tagged} and {backend_tagged}")
except subprocess.CalledProcessError as e:
    print(f"Error pushing images: {e}")
    exit(1)
