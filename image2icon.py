import argparse
import os
from PIL import Image, ImageDraw


def image_to_ico(image_path, icon_path, remove_alpha):
    source_image = Image.open(image_path)

    icon_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (256, 256)]
    image_data_blocks = []

    for size in icon_sizes:
        resized = source_image.resize(size, Image.LANCZOS)
        format = "PNG" if size == (256, 256) else "BMP"
        ext = "png" if size == (256, 256) else "bmp"

        with open(f"temp.{ext}", "wb") as f:
            if resized.mode == "P":
                resized = resized.convert("RGBA")
            resized.save(f, format)
        with open(f"temp.{ext}", "rb") as f:
            data = f.read()
            if format == "BMP":
                # Adjust the height in BMP's DIB header
                height_bytes = (size[1] * 2).to_bytes(
                    4, byteorder="little", signed=True
                )
                data = data[:22] + height_bytes + data[26:]
                data = data[14:]  # Strip BMP header

            image_data_blocks.append(data)
        os.remove(f"temp.{ext}")

    # Create ICO header
    num_images = len(icon_sizes)
    ico_header = bytearray([0, 0, 1, 0, num_images & 0xFF, (num_images >> 8) & 0xFF])

    offset = 6 + num_images * 16
    directory_entries = bytearray()

    for i, size in enumerate(icon_sizes):
        (width, height) = size
        size_of_data = len(image_data_blocks[i])
        bpp = 32

        # Create ICONDIRENTRY
        entry = bytearray(
            [
                width & 0xFF,
                height & 0xFF,
                0,
                0,
                1,
                0,
                bpp,
                0,
                size_of_data & 0xFF,
                (size_of_data >> 8) & 0xFF,
                (size_of_data >> 16) & 0xFF,
                (size_of_data >> 24) & 0xFF,
                offset & 0xFF,
                (offset >> 8) & 0xFF,
                (offset >> 16) & 0xFF,
                (offset >> 24) & 0xFF,
            ]
        )
        directory_entries.extend(entry)

        offset += size_of_data

    # Combine all parts
    ico_data = ico_header + directory_entries
    for block in image_data_blocks:
        ico_data += block

    with open(icon_path, "wb") as f:
        f.write(ico_data)


def main():
    parser = argparse.ArgumentParser(description="PNG画像ファイルをアイコンファイルに変換する")
    parser.add_argument("source", help="変換する画像ファイル(png, bmp)パスを指定")
    parser.add_argument(
        "-o", "--output", default="out.ico", help="出力されるアイコンのファイルパスを指定 (初期値: out.ico)"
    )
    parser.add_argument("--remove-alpha", action="store_false", help="等価チャンネルを削除")

    args = parser.parse_args()
    image_to_ico(args.source, args.output, args.remove_alpha)


if __name__ == "__main__":
    main()
