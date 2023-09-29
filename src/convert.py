# https://sites.google.com/view/geomatics-and-computer-vision/home/datasets

import glob
import os
import shutil
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlparse

import numpy as np
import supervisely as sly
from dataset_tools.convert import unpack_if_archive
from dotenv import load_dotenv
from supervisely.io.fs import (
    file_exists,
    get_file_ext,
    get_file_name,
    get_file_name_with_ext,
    get_file_size,
)
from tqdm import tqdm

import src.settings as s


def download_dataset(teamfiles_dir: str) -> str:
    """Use it for large datasets to convert them on the instance"""
    api = sly.Api.from_env()
    team_id = sly.env.team_id()
    storage_dir = sly.app.get_data_dir()

    if isinstance(s.DOWNLOAD_ORIGINAL_URL, str):
        parsed_url = urlparse(s.DOWNLOAD_ORIGINAL_URL)
        file_name_with_ext = os.path.basename(parsed_url.path)
        file_name_with_ext = unquote(file_name_with_ext)

        sly.logger.info(f"Start unpacking archive '{file_name_with_ext}'...")
        local_path = os.path.join(storage_dir, file_name_with_ext)
        teamfiles_path = os.path.join(teamfiles_dir, file_name_with_ext)

        fsize = api.file.get_directory_size(team_id, teamfiles_dir)
        with tqdm(
            desc=f"Downloading '{file_name_with_ext}' to buffer...",
            total=fsize,
            unit="B",
            unit_scale=True,
        ) as pbar:
            api.file.download(team_id, teamfiles_path, local_path, progress_cb=pbar)
        dataset_path = unpack_if_archive(local_path)

    if isinstance(s.DOWNLOAD_ORIGINAL_URL, dict):
        for file_name_with_ext, url in s.DOWNLOAD_ORIGINAL_URL.items():
            local_path = os.path.join(storage_dir, file_name_with_ext)
            teamfiles_path = os.path.join(teamfiles_dir, file_name_with_ext)

            if not os.path.exists(get_file_name(local_path)):
                fsize = api.file.get_directory_size(team_id, teamfiles_dir)
                with tqdm(
                    desc=f"Downloading '{file_name_with_ext}' to buffer...",
                    total=fsize,
                    unit="B",
                    unit_scale=True,
                ) as pbar:
                    api.file.download(team_id, teamfiles_path, local_path, progress_cb=pbar)

                sly.logger.info(f"Start unpacking archive '{file_name_with_ext}'...")
                unpack_if_archive(local_path)
            else:
                sly.logger.info(
                    f"Archive '{file_name_with_ext}' was already unpacked to '{os.path.join(storage_dir, get_file_name(file_name_with_ext))}'. Skipping..."
                )

        dataset_path = storage_dir
    return dataset_path


def count_files(path, extension):
    count = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(extension):
                count += 1
    return count


def convert_and_upload_supervisely_project(
    api: sly.Api, workspace_id: int, project_name: str
) -> sly.ProjectInfo:
    # project_name = "Tree species detection"
    dataset_path = "/mnt/c/Users/grokh/Downloads/Cumbaru"
    batch_size = 5
    images_ext = ".jpg"
    ann_ext = ".xml"

    def create_ann(image_path):
        labels = []

        curr_bboxes_path = image_path[: -len(get_file_name_with_ext(image_path))]

        ann_path = os.path.join(curr_bboxes_path, get_file_name(image_path) + ".xml")

        tree = ET.parse(ann_path)
        root = tree.getroot()
        img_height = int(root.find(".//height").text)
        img_width = int(root.find(".//width").text)
        objects_content = root.findall(".//object")
        for obj_data in objects_content:
            bndbox = obj_data.find(".//bndbox")
            top = int(bndbox.find(".//ymin").text)
            left = int(bndbox.find(".//xmin").text)
            bottom = int(bndbox.find(".//ymax").text)
            right = int(bndbox.find(".//xmax").text)

            rectangle = sly.Rectangle(top=top, left=left, bottom=bottom, right=right)
            label = sly.Label(rectangle, obj_class)
            labels.append(label)

        # tag_name = image_path.split("/")[-3]  # for example
        # tags = [sly.Tag(tag_meta) for tag_meta in tag_metas if tag_meta.name == tag_name]

        return sly.Annotation(img_size=(img_height, img_width), labels=labels)

    obj_class = sly.ObjClass("cumbaru", sly.Rectangle)

    project = api.project.create(workspace_id, project_name, change_name_if_conflict=True)

    # tag_names = ["folder_0", "folder_1", "folder_2", "folder_3", "folder_4"]
    # tag_metas = [sly.TagMeta(name, sly.TagValueType.NONE) for name in tag_names]

    meta = sly.ProjectMeta(obj_classes=[obj_class])
    api.project.update_meta(project.id, meta.to_json())

    for ds_name in ["train", "val", "test"]:
        dataset = api.dataset.create(project.id, ds_name, change_name_if_conflict=True)

        unique_pathes = []
        unique_images_names = []

        images_pathes = glob.glob(dataset_path + f"/*/{ds_name}/*.JPG")

        for curr_path in images_pathes:
            im_name = get_file_name_with_ext(curr_path)
            if im_name not in unique_images_names:
                unique_images_names.append(im_name)
                unique_pathes.append(curr_path)

        progress = sly.Progress("Create dataset {}".format(ds_name), len(unique_pathes))

        for img_pathes_batch in sly.batched(unique_pathes, batch_size=batch_size):
            images_names_batch = [
                get_file_name_with_ext(image_path) for image_path in img_pathes_batch
            ]

            img_infos = api.image.upload_paths(dataset.id, images_names_batch, img_pathes_batch)
            img_ids = [im_info.id for im_info in img_infos]

            anns = [create_ann(image_path) for image_path in img_pathes_batch]
            api.annotation.upload_anns(img_ids, anns)

            progress.iters_done_report(len(images_names_batch))
    return project
