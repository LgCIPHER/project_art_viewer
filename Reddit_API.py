from praw import Reddit
import os.path
from pathlib import Path
import pickle
import requests
import cv2 as cv
import numpy as np


def create_folder(folder_path):  # Create directory if it doesn't exist to save images
    CHECK_FOLDER = os.path.isdir(folder_path)
    # If folder doesn't exist, then create it.
    if not CHECK_FOLDER:
        os.makedirs(folder_path)


def create_token():  # Create token file
    client_id = "vxCV2waXGarClfnBNI8jZw"
    secret = "Zd7IZVZRmkjKPuJCIUEgnl_dYmhXZg"
    creds = {}

    creds["client_id"] = client_id
    creds["client_secret"] = secret
    creds["user_agent"] = input("user_agent: ")
    creds["username"] = input("username: ")
    creds["password"] = input("password: ")

    return creds


def read_token(dir_path):  # Read token file
    # Token file directory
    FilePath = os.path.join(dir_path, "token.pickle")

    file = Path(FilePath)

    if file.is_file():
        with open(FilePath, 'rb') as token:
            creds = pickle.load(token)
    else:
        creds = create_token()
        pickle_out = open("token.pickle", "wb")
        pickle.dump(creds, pickle_out)

    return creds


def name_progress(url_str, sub_path, sub):
    url_name_lst = url_str.split("/")
    pic_name = url_name_lst[3]
    pic_name_lst = pic_name.split(".")
    pic_id = pic_name_lst[0]
    pic_type = pic_name_lst[1]

    img_name = f"{sub_path}{sub}-{pic_id}.{pic_type}"
    img_path = os.path.join(sub_path, img_name)


def html_to_img(url_str, resize=False):
    # Getting image from HTML page
    resp = requests.get(url_str, stream=True).raw
    image = np.asarray(
        bytearray(resp.read()), dtype="uint8")
    image = cv.imdecode(image, cv.IMREAD_COLOR)

    if resize == True:
        # Could do transforms on images like resize!
        image = cv.resize(image, (352, 627))

    return image


def check_deleted_img(url_str):
    deleted_flag = False

    img = html_to_img(url_str)
    [h, w] = [img.shape[0], img.shape[1]]

    if [h, w] != [60, 130]:
        pass
    else:
        deleted_flag = True

    return deleted_flag


def compare_img(url_str, url_list):
    ignore_flag = False

    img_1 = html_to_img(url_str)
    [h_1, w_1] = [img_1.shape[0], img_1.shape[1]]

    print(f"Start comparing--{url_str}")

    for url_done in url_list:
        img_2 = html_to_img(url_done)
        [h_2, w_2] = [img_2.shape[0], img_2.shape[1]]

        if [h_1, w_1] == [h_2, w_2]:
            print(f"--Comparing with--{url_done}")
            difference = cv.subtract(img_1, img_2)
            b, g, r = cv.split(difference)
            total_difference = cv.countNonZero(
                b) + cv.countNonZero(g) + cv.countNonZero(r)
            if total_difference == 0:
                ignore_flag = True

    return ignore_flag


def past_list(lst_img_dir):
    past_list = []

    with open(lst_img_dir, mode="r", encoding="utf-8-sig") as f_past_result:
        for line in f_past_result:
            url = line.strip()
            past_list.append(url)

    return past_list


def check_available(url_str, already_done):
    exist_flag = False

    for url_done in already_done:
        if url_str == url_done:
            exist_flag = True

    return exist_flag


def Reddit_API():
    sub = "Pixiv"   # Search for images in this Subreddit

    POST_SEARCH_AMOUNT = 50

    # Path of this file
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print(dir_path)

    creds = read_token(dir_path)

    reddit = Reddit(client_id=creds['client_id'],
                    client_secret=creds['client_secret'],
                    user_agent=creds['user_agent'],
                    username=creds['username'],
                    password=creds['password'])

    past_result = []
    already_done = []
    last_sub_url_list = []

    lst_sub_name = "sub_list.csv"
    lst_sub_dir = os.path.join(dir_path, lst_sub_name)

    lst_img_name = "img_list.csv"
    lst_img_dir = os.path.join(dir_path, lst_img_name)

    past_result = past_list(lst_img_dir)
    for url in past_result:
        already_done.append(url)

    with open(lst_sub_dir, mode="r", encoding="utf-8-sig") as f_source:
        for line in f_source:
            sub = line.strip()
            subreddit = reddit.subreddit(sub)

            count = 0

            print(f"Starting {sub} subreddit!\n")

            # Searching for Hot post
            for submission in subreddit.hot(limit=POST_SEARCH_AMOUNT):
                # Get image URL
                url_str = str(submission.url.lower())

                if "jpg" in url_str or "png" in url_str:
                    exist_flag = False

                    exist_flag = check_available(url_str, already_done)

                    if exist_flag == False:
                        if url_str not in already_done:
                            domain_name = submission.domain

                            if domain_name != "i.imgur.com":
                                try:
                                    deleted_flag = False

                                    deleted_flag = check_deleted_img(
                                        url_str)

                                    if not deleted_flag:
                                        ignore_flag = False

                                        ignore_flag = compare_img(
                                            url_str, last_sub_url_list)

                                        if not ignore_flag:
                                            already_done.append(url_str)
                                            count += 1
                                            print(
                                                f"Add--successfully--{url_str}")
                                    else:
                                        print("Deleted img")

                                except Exception as e:
                                    print(
                                        f"Image failed. {url_str}")
                                    print(e)

                            else:
                                print("Can't deal with Imgur link yet!")
                    else:
                        print(f"--Pass--{url_str}")

            for url_done in already_done:
                last_sub_url_list.append(url_done)

            print(f"{count} new picture has been added!\n")

    print("Finish scraping!")

    print("Start writing into csv file")

    with open(lst_img_dir, mode="w", encoding="utf-8-sig") as f_result:
        for url_done in already_done:
            img_path_str = str(url_done) + "\n"
            f_result.write(img_path_str)

    print("Finish running!")


def scan_csv():
    # Path of this file
    dir_path = os.path.dirname(os.path.realpath(__file__))

    past_result = -1
    count = 0
    already_done = []
    last_sub_url_list = []

    lst_img_name = "img_list.csv"
    lst_img_dir = os.path.join(dir_path, lst_img_name)

    past_result = past_list(lst_img_dir)
    for url in past_result:
        already_done.append(url)

    for line in already_done:
        url_str = line.strip()
        try:
            deleted_flag = False

            deleted_flag = check_deleted_img(url_str)

            if not deleted_flag:
                print(f"Keep--{url_str}")
            else:
                already_done.remove(line)
                count += 1
                print(f"Remove--{url_str}")
        except Exception as e:
            print(f"Image failed. {url_str}")
            print(e)

    print("\nFinish scanning!")

    print(f"{count} picture has been removed!\n")

    print("Start writing into csv file")

    with open(lst_img_dir, mode="w", encoding="utf-8-sig") as f_result:
        for url_done in already_done:
            img_path_str = str(url_done) + "\n"
            f_result.write(img_path_str)

    print("Finish running!")


def main():
    Reddit_API()
    scan_csv()


if __name__ == "__main__":
    main()
