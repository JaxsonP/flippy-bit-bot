from audioop import avg
from bisect import bisect_left
from math import dist
from multiprocessing.reduction import duplicate
import time

import cv2
import numpy as np
import pyautogui
import win32gui
from pygetwindow import getWindowsWithTitle

x = 0
y = 0
w = 0
h = 0
last_enemy_pos = (0, 0)


def reset_bits():
  global x, y, w, h
  print(" - resetting bits")

  flipped_bit_img = cv2.imread(r"ref_images\flipped_bit.png", cv2.IMREAD_COLOR)

  # resetting bit flippers
  screenshot = pyautogui.screenshot(region=(x, y, w, h))
  game_img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

  flipped_bits_map = cv2.matchTemplate(game_img, flipped_bit_img, cv2.TM_CCOEFF_NORMED)
  y_loc, x_loc = np.where(flipped_bits_map >= 0.7)
  possible_locations = list(zip(x_loc, y_loc))

  # grouping and parsing TM locations
  flipped_bits = []
  for pos in possible_locations:
    duplicate = False
    for flipper in flipped_bits:
      if dist(pos, flipper) < 30:
        duplicate = True
        break
    if not duplicate:
      flipped_bits.append(pos)
    
  print(f"   - Found {len(flipped_bits)} flipped bits")
  
  for bit in flipped_bits:
    pyautogui.moveTo(int(x + bit[0] + flipped_bit_img.shape[1] / 2), int(y + bit[1] + flipped_bit_img.shape[0] / 2))
    #time.sleep(0.01)
    pyautogui.leftClick()
  
  return len(flipped_bits)



def main ():
  global x, y, w, h, last_enemy_pos
  print("\n\n\n")


  pyautogui.PAUSE = 0.05

  print("Loading reference images")
  bit_img = cv2.imread(r"ref_images\bit.png", cv2.IMREAD_COLOR)
  flipped_bit_img = cv2.imread(r"ref_images\flipped_bit.png", cv2.IMREAD_COLOR)
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

  print("Waiting for bluestacks window to focus")
  while win32gui.GetForegroundWindow() != bluestacks_hwnd:
    time.sleep(0.1)
  
  print("Resizing window")
  win = getWindowsWithTitle('BlueStacks App Player')[0]
  win.size = (593, 1020)
    
  print("Setting up bit flippers")
  screenshot = pyautogui.screenshot(region=(x, y, w, h))
  game_img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

  bits_map = cv2.matchTemplate(game_img, bit_img, cv2.TM_CCOEFF_NORMED)
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
    flipper = (int(bit_flippers[i][0] + bit_img.shape[1] / 2), int(bit_flippers[i][1] + bit_img.shape[0] / 2))
    bit_flippers[i] = flipper

  # sorting bit flippers
  def sortBitFlippers (flipper):
    return flipper[0]
  bit_flippers.sort(key=sortBitFlippers)
  print("Found bit flippers")
  print(bit_flippers)
  while True:

    screenshot = pyautogui.screenshot(region=(x, y, w, h))
    game_img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # finding enemies
    enemy_map = cv2.matchTemplate(game_img, enemy_img, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(enemy_map)

    if max_val > 0.4 and max_loc[1] > 75:

      if dist(max_loc, last_enemy_pos) < 100:
        continue

      last_enemy_pos = max_loc

      print(f"\nFound enemy! {max_loc}")
      enemy_screenshot = pyautogui.screenshot(region=(x + max_loc[0], y + max_loc[1], enemy_img.shape[1], enemy_img.shape[0]))
      read_img = cv2.cvtColor(np.array(enemy_screenshot), cv2.COLOR_RGB2BGR)

      # finding hex letters
      numbers = []
      print(" - Numbers located: ", end="")
      for i in range(len(hex_imgs)):
        hex_img = hex_imgs[i]
        letters_map = cv2.matchTemplate(read_img, hex_img, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(letters_map)
        
        if max_val >= 0.86:
          print(f"{hex(i)[2:]}, ", end="")
          numbers.append((str(bin(i))[2:].rjust(4, '0'), max_loc[0]))
      print()

      if len(numbers) == 1:

        answer = "0000" + numbers[0][0]
        print(f" - answer: {answer}")
        for i in range(len(answer)):
          print(i, end="")
          if answer[i] == "1":
            pyautogui.moveTo(x + bit_flippers[i][0], y + bit_flippers[i][1])
            #time.sleep(1/8)
            pyautogui.leftClick()
        print()
        time.sleep(0.02)

        # for double digits
        if reset_bits() > 0:
          answer = numbers[0][0] + numbers[0][0]
          print(f" - answer: {answer}")
          for i in range(len(answer)):
            print(i, end="")
            if answer[i] == "1":
              pyautogui.moveTo(x + bit_flippers[i][0], y + bit_flippers[i][1])
              #time.sleep(1/8)
              pyautogui.leftClick()
            time.sleep(0.02)
          print()
          reset_bits()



      elif len(numbers) == 2:

        #arranging letters
        def sortHexs (num):
          return num[1]
        numbers.sort(key=sortHexs)
        answer = str(numbers[0][0]) + str(numbers[1][0])

        # executing
        for i in range(len(answer)):
          if answer[i] == "1":
            pyautogui.moveTo(x + bit_flippers[i][0], y + bit_flippers[i][1])
            #time.sleep(1/8)
            pyautogui.leftClick()
        time.sleep(0.02)
        reset_bits()

      elif len(numbers) == 0:

        print("Failed to read characters, retrying")
        continue
      else:
        print("ERROR read 3 chars, retrying")
        continue


    else:
      #print("Didn't find any enemies")
      continue
    
    time.sleep(0.5)


  return




if __name__ == "__main__":
  main()