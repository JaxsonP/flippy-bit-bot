from audioop import avg
from bisect import bisect_left
from math import dist
from multiprocessing.reduction import duplicate
import time

import cv2
import numpy as np
import pyautogui
import win32gui

def main ():
  print("\n\n\n")

  print("Loading reference images")
  #bit_img = np.uint8(cv2.imread(r"ref_images\bit.png", cv2.IMREAD_GRAYSCALE))
  bit_img = cv2.imread(r"ref_images\bit.png", cv2.IMREAD_COLOR)
  enemy_img = cv2.imread(r"ref_images\enemy.png", cv2.IMREAD_COLOR)
  hex_imgs = [
    cv2.imread(r"ref_images\0.png", cv2.IMREAD_COLOR),
    cv2.imread(r"ref_images\1.png", cv2.IMREAD_COLOR),
    cv2.imread(r"ref_images\2.png", cv2.IMREAD_COLOR),
    cv2.imread(r"ref_images\3.png", cv2.IMREAD_COLOR),
    cv2.imread(r"ref_images\4.png", cv2.IMREAD_COLOR),
    cv2.imread(r"ref_images\5.png", cv2.IMREAD_COLOR),
    cv2.imread(r"ref_images\6.png", cv2.IMREAD_COLOR),
    cv2.imread(r"ref_images\7.png", cv2.IMREAD_COLOR),
    cv2.imread(r"ref_images\8.png", cv2.IMREAD_COLOR),
    cv2.imread(r"ref_images\9.png", cv2.IMREAD_COLOR),
    cv2.imread(r"ref_images\a.png", cv2.IMREAD_COLOR),
    cv2.imread(r"ref_images\b.png", cv2.IMREAD_COLOR),
    cv2.imread(r"ref_images\c.png", cv2.IMREAD_COLOR),
    cv2.imread(r"ref_images\d.png", cv2.IMREAD_COLOR),
    cv2.imread(r"ref_images\e.png", cv2.IMREAD_COLOR),
    cv2.imread(r"ref_images\f.png", cv2.IMREAD_COLOR)
  ]

  print('Finding bluestacks window')
  bluestacks_hwnd = win32gui.FindWindow(None, "BlueStacks App Player")
  bluestacks_rect = win32gui.GetWindowRect(bluestacks_hwnd)
  x = bluestacks_rect[0]
  y = bluestacks_rect[1]
  w = bluestacks_rect[2] - x
  h = bluestacks_rect[3] - y
  #print(x, y, w, h)

  print("Waiting for bluestacks window to focus")
  while win32gui.GetForegroundWindow() != bluestacks_hwnd:
    time.sleep(0.1)
    
  print("Setting up bit flippers")
  screenshot = pyautogui.screenshot(region=(x, y, w, h))
  game_img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

  def templateMatchBits (img):

    # the magic
    bits_map = cv2.matchTemplate(game_img, img, cv2.TM_CCOEFF_NORMED)
    y_loc, x_loc = np.where(bits_map >= 0.7)
    possible_locations = list(zip(x_loc, y_loc))

    # grouping and parsing TM locations
    bit_flippers = []
    for pos in possible_locations:
      duplicate = False
      for flipper in bit_flippers:
        if dist(pos, flipper) < 5:
          duplicate = True
          break
      if not duplicate:
        bit_flippers.append(pos)

    for i in range(len(bit_flippers)):
      flipper = (int(bit_flippers[i][0] + img.shape[1] / 2), int(bit_flippers[i][1] + img.shape[0] / 2))
      #cv2.drawMarker(game_img, (flipper[0], flipper[1]), color=(255, 0, 255), markerType=cv2.MARKER_CROSS, markerSize=30, thickness=2)
      bit_flippers[i] = flipper
    return bit_flippers
    
  size_factor = 1
  bit_flippers = []
  print("Scaling template matching")
  while True:

    dimensions = (int(bit_img.shape[1] * size_factor), int(bit_img.shape[0] * size_factor))
    bit_flippers = templateMatchBits(cv2.resize(bit_img, dimensions, interpolation=cv2.INTER_AREA))
    if len(bit_flippers) == 8:
      print(f"Screen size factor: {round(size_factor, 4)}")
      break
    size_factor *= 0.99

    if size_factor < 0.2:
      print("ERROR couldnt find bit flippers :(")
      return


  # sorting bit flippers
  def sortBitFlippers (flipper):
    return flipper[0]
  bit_flippers.sort(key=sortBitFlippers)
  print("Found bit flippers")
  print("Bit flippers:", bit_flippers)
  
  #cv2.imwrite('game_image.png', game_img)
  game_img = cv2.imread("game_image.png", cv2.IMREAD_COLOR)

  for i in range(len(hex_imgs)):
    hex_img = hex_imgs[i]
    dimensions = (int(hex_img.shape[1] * size_factor), int(hex_img.shape[0] * size_factor))
    cv2.resize(hex_img, dimensions, interpolation=cv2.INTER_AREA)
    letters_map = cv2.matchTemplate(game_img, hex_img, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(letters_map)
    
    print(f"{hex(i)}: {max_val}")
    if max_val >= 0.94:
      print("Found letter!")

    """cv2.imshow("lettermap", letters_map)
    cv2.waitKey()
    cv2.destroyAllWindows()"""

  return




if __name__ == "__main__":
  main()