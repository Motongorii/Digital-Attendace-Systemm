import subprocess
import sys

packages = [
    'firebase-admin>=6.2.0',
    'Django>=4.2,<5.0',
    'qrcode[pil]>=7.4.2',
    'Pillow>=10.0.0',
    'python-dotenv>=1.0.0',
    'gunicorn>=21.2.0'
]

for package in packages:
    print(f"Installing {package}...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

print("\n✓ All packages installed successfully!")
