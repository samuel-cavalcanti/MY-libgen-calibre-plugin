import zipfile
import os


def compress_files():

    name_file = "libgen.zip"

    print("zipping!")
    if os.path.isfile(name_file):
        os.remove(name_file)
    zf = zipfile.ZipFile(name_file, "w", zipfile.ZIP_DEFLATED)

    zf.write("libgen.py")
    zf.write("__init__.py")

    print("Done")

if __name__ == "__main__":
    compress_files()
