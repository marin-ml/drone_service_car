import cv2
import json
import sys
print(cv2.__version__)

fn_json = 'dataset\ROIs.json'
fn_cascade_src = 'dataset\cars.xml'

init_width = 853
init_height = 480

camera_ids = []
roads_rects = []


def get_road_rect(cam_id):

    for i in camera_ids:
        if i == cam_id:
            rect = roads_rects[i.index]
            return rect

    return None


def isPinRectangle(r, P):
    """
        r: A list of four points, each has a x- and a y- coordinate
        P: A point
    """

    areaRectangle = 0.5*abs(
        # y_A      y_C      x_D      x_B    #   y_B     y_D       x_A     x_C
        (r[0][1]-r[2][1])*(r[3][0]-r[1][0]) + (r[1][1]-r[3][1])*(r[0][0]-r[2][0])
                    )

    ABP = 0.5*abs(
              r[0][0]*(r[1][1]-P[1]) + r[1][0]*(P[1]-r[0][1]) + P[0]*(r[0][1]-r[1][1])
          )
    BCP = 0.5*abs(
             r[1][0]*(r[2][1]-P[1]) + r[2][0]*(P[1]-r[1][1]) + P[0]*(r[1][1]-r[2][1])
          )
    CDP = 0.5*abs(
              r[2][0]*(r[3][1]-P[1]) + r[3][0]*(P[1]-r[2][1]) + P[0]*(r[2][1]-r[3][1])
          )
    DAP = 0.5*abs(
              r[3][0]*(r[0][1]-P[1]) + r[0][0]*(P[1]-r[3][1]) + P[0]*(r[3][1]-r[0][1])
    )
    return areaRectangle == (ABP+BCP+CDP+DAP)


def main(argv):

    # Make the file name from the webcam number
    fn_image_src = argv[1] + ".jpg"

    # Read the camera feed as a image
    img = cv2.imread(fn_image_src)

    if img is None:
        print "can't read image"
        return

    # Extract the camera id from imag file name
    camera_id = int(filter(str.isdigit, fn_image_src))

    # Define the car detector in Haar cascade model
    car_cascade = cv2.CascadeClassifier(fn_cascade_src)

    # Read the YAML data (Road space ploygons)

    with open(fn_json, 'rb') as fp:
        for line in fp:
            data = json.loads(line)
            camera_ids.append(data['id'])

            rect = [data['points'][0], data['points'][1], data['points'][2], data['points'][3]]
            roads_rects.append(rect)

    # Detecting the vehicles and Counting the number of them from images
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # gray = cv2.resize(gray, (init_height, init_width))

    scaleFactor = 1.01
    minNeighbors = 1

    cars = car_cascade.detectMultiScale(gray, scaleFactor, minNeighbors)

    rect = roads_rects[camera_ids.index(camera_id)]
    cv2.line(img, (rect[0][0], rect[0][1]), (rect[1][0], rect[1][1]), (0, 255, 0), 2)
    cv2.line(img, (rect[2][0], rect[2][1]), (rect[3][0], rect[3][1]), (0, 255, 0), 2)

    cnt = 0
    for (x, y, w, h) in cars:
        center_x = x + w/2
        center_y = y + h/2

        cv2.rectangle(img, (x, y), (x + w - 10, y + h - 10), (0, 255, 0), 1)

        if isPinRectangle(rect, P=(center_x, center_y)):
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 1)
            cnt += 1

    cv2.imshow("Result", img)
    cv2.waitKey(delay=0)

    return cnt

if __name__ == '__main__':

    if len(sys.argv) == 1:
        print "Please Select the Nubmer of webcam as a parmeter."
    else:
        print main(sys.argv)


