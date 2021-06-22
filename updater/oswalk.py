import os
from pathlib import Path


installdir = Path(__file__).absolute().parent

new_dir = (str(installdir) + "\\new")
old_dir = (str(installdir) + "\\old")

new_file_list = open(str(installdir) + "\\new_list.txt", "a+")

for root, dirs, files in os.walk(new_dir, topdown=False):
    for name in files:
        new_file = (os.path.join(root, name))
        new_listing = new_file.split("\\new\\")
        new_file_list.write(new_listing[1] + "\n")
    for name in dirs:
        new_file = (os.path.join(root, name))
        new_listing = new_file.split("\\new\\")
        new_file_list.write(new_listing[1] + "\n")

new_file_list.close()

old_file_list = open(str(installdir) + "\\old_list.txt", "a+")

for root, dirs, files in os.walk(old_dir, topdown=False):
    for name in files:
        old_file = (os.path.join(root, name))
        old_listing = old_file.split("\\old\\")
        old_file_list.write(old_listing[1] + "\n")
    for name in dirs:
        old_file = (os.path.join(root, name))
        old_listing = old_file.split("\\old\\")
        old_file_list.write(old_listing[1] + "\n")

old_file_list.close()
