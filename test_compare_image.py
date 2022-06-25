import cv2 as cv
from cv2 import waitKey

from Reddit_API import html_to_img

img_1_url = "https://i.redd.it/03izpr7rtvq81.png"
img_2_url = "https://i.redd.it/wk7vsho2lvq81.jpg"

img_test_url = "https://i.redd.it/2hw0rjgeljq81.jpg"

img_1 = html_to_img(img_1_url)
img_2 = html_to_img(img_2_url)

img_test = html_to_img(img_test_url)

[h_t, w_t] = [img_test.shape[0], img_test.shape[1]]

# difference = cv.subtract(img_1, img_2)
# b, g, r = cv.split(difference)
# total_difference = cv.countNonZero(b) + cv.countNonZero(g) + cv.countNonZero(r)

# cv.imshow("why", difference)

print(f"h: {h_t}; w: {w_t}")

result = False

if [h_t, w_t] == [60, 130]:
    result = True
else:
    result = False

print(f"Result: {result}")

cv.imshow("test", img_test)

waitKey(0)
