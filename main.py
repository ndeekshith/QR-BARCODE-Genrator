import streamlit as st
import barcode
from barcode.writer import ImageWriter
import qrcode
from io import BytesIO
from PIL import Image


def generate_barcode(data, barcode_type='code128', scale=2):
    """
    Generates a barcode image in memory.

    Args:
        data: The data to encode in the barcode.
        barcode_type: The type of barcode to generate.
        scale: Scaling factor for the barcode image (smaller = smaller image).

    Returns:
        A PIL Image object if successful, None otherwise.
    """
    try:
        barcode_class = barcode.get_barcode_class(barcode_type)
        barcode_instance = barcode_class(data, writer=ImageWriter())

        # Create a BytesIO buffer to hold the image data
        buffer = BytesIO()
        barcode_instance.write(buffer, options={'module_width': 0.2 * scale, 'module_height': 10 * scale})  # Adjust module_width for size
        buffer.seek(0)  # Reset the buffer's position to the beginning

        # Open the image from the buffer using PIL
        image = Image.open(buffer)
        return image

    except barcode.errors.BarcodeNotFoundError:
        st.error(f"Error: Barcode type '{barcode_type}' is not supported.")
        return None
    except barcode.errors.NumberError as e:
        st.error(f"Error: Invalid data for barcode type '{barcode_type}': {e}")
        return None
    except barcode.errors.IllegalCharacterError as e:
        st.error(f"Error: Invalid characters in data for barcode type '{barcode_type}': {e}")
        return None
    except Exception as e:
        st.error(f"Error creating barcode: {e}")
        return None


def generate_qrcode(data, box_size=3):
    """
    Generates a QR code image in memory.

    Args:
        data: The data to encode in the QR code.
        box_size:  Size of each box in the QR code (smaller = smaller image).

    Returns:
        A PIL Image object if successful, None otherwise.
    """
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=box_size,
            border=2,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        return img

    except Exception as e:
        st.error(f"Error creating QR code: {e}")
        return None


def main():
    st.title("Barcode/QR Code Generator")

    code_type = st.radio("Select code type:", ("Barcode", "QR Code"))  # Radio button to choose

    data = st.text_input("Enter data:", value="")

    if st.button("Generate"):
        if not data:
            st.warning("Please enter data.")
            return

        if code_type == "Barcode":
            barcode_type = st.selectbox("Select barcode type:",
                                        ("code128", "code39", "ean13", "ean8", "upca", "pzn7"))

            # Adjust scale value to decrease the image size more.
            image = generate_barcode(data, barcode_type, scale=1)
            filename = "barcode.png"
        else:  # QR Code
            # Adjust box_size to decrease the image size
            image = generate_qrcode(data, box_size=2)
            filename = "qrcode.png"

        if image:
            # Convert the PIL Image to bytes
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_bytes = buffered.getvalue()

            st.image(img_bytes, caption=f"Generated {code_type}", use_container_width=True)  # Use use_container_width

            # Download button
            buffered = BytesIO()  # Create a *new* buffer
            image.save(buffered, format="PNG")
            img_str = buffered.getvalue()

            st.download_button(
                label=f"Download {code_type} (PNG)",
                data=img_str,
                file_name=filename,
                mime="image/png",
            )
        else:
            st.error("Code generation failed. See error messages above.")


if __name__ == "__main__":
    main()