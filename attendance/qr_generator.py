"""
QR Code generator for attendance sessions.
"""
from io import BytesIO
from django.core.files.base import ContentFile

# Try to import qrcode, but don't fail if not installed
QRCODE_AVAILABLE = False
try:
    import qrcode
    from qrcode.image.styledpil import StyledPilImage
    from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
    from qrcode.image.styles.colormasks import RadialGradiantColorMask
    QRCODE_AVAILABLE = True
except ImportError:
    print("⚠ qrcode not installed. Run: pip install qrcode[pil] Pillow")


def generate_session_qr(session, base_url: str) -> ContentFile:
    """
    Generate a styled QR code for an attendance session.
    
    Args:
        session: AttendanceSession model instance
        base_url: The base URL of the application
    
    Returns:
        ContentFile containing the QR code image
    """
    # Create the URL that the QR code will point to
    attendance_url = f"{base_url}/attend/{session.id}/"
    
    if not QRCODE_AVAILABLE:
        # Return a placeholder image if qrcode is not available
        # Create a simple 1x1 pixel PNG as placeholder
        placeholder = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        filename = f"qr_{session.id}.png"
        return ContentFile(placeholder, name=filename)
    
    # Create QR code with high error correction
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    
    qr.add_data(attendance_url)
    qr.make(fit=True)
    
    # Try styled image, fallback to simple if it fails
    try:
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer(),
            color_mask=RadialGradiantColorMask(
                back_color=(255, 255, 255),
                center_color=(0, 255, 200),  # Cyan center
                edge_color=(75, 0, 130),     # Indigo edge
            )
        )
    except Exception:
        # Fallback to simple QR code
        img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to bytes
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Return as Django ContentFile
    filename = f"qr_{session.id}.png"
    return ContentFile(buffer.getvalue(), name=filename)


def generate_simple_qr(data: str) -> bytes:
    """Generate a simple QR code and return as bytes."""
    if not QRCODE_AVAILABLE:
        return b''
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()
