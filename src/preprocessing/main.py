"""run preprocessing."""
from pathlib import Path

from file_download import FileDownloader
from file_list_collect import FileListCollecter


def main():
    fc = FileListCollecter()
    fc.run()
    urls_dict_path = fc.result_path
    fd = FileDownloader(urls_dict_path=urls_dict_path)
    fd.run()


if __name__ == "__main__":
    main()
