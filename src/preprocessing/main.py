"""run preprocessing."""
from src.preprocessing.file_download import FileDownloader
from src.preprocessing.file_list_collect import FileListCollecter

fc = FileListCollecter()
fc.run()
urls_dict_path = fc.result_path
fd = FileDownloader(urls_dict_path=urls_dict_path)
fd.run()
