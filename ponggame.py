import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import os

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Path folder script
basePath = os.path.dirname(os.path.abspath(__file__))

# Importing all images
imgBackground = cv2.imread(os.path.join(basePath, "Background.png"))
imgGameOver = cv2.imread(os.path.join(basePath, "GameOver1.png"))
imgBall = cv2.imread(os.path.join(basePath, "Ball.png"), cv2.IMREAD_UNCHANGED)
# Theme-specific ball images
imgBall1 = cv2.imread(os.path.join(basePath, "Ball1.png"), cv2.IMREAD_UNCHANGED)
imgBall2 = cv2.imread(os.path.join(basePath, "Ball2.png"), cv2.IMREAD_UNCHANGED)
imgBall3 = cv2.imread(os.path.join(basePath, "Ball3.png"), cv2.IMREAD_UNCHANGED)
imgBat1 = cv2.imread(os.path.join(basePath, "bat1.png"), cv2.IMREAD_UNCHANGED)
imgBat2 = cv2.imread(os.path.join(basePath, "bat2.png"), cv2.IMREAD_UNCHANGED)
# Menu assets
imgMenu = cv2.imread(os.path.join(basePath, "menuawal.png"))
imgPlay = cv2.imread(os.path.join(basePath, "playbutton.png"), cv2.IMREAD_UNCHANGED)
imgExit = cv2.imread(os.path.join(basePath, "exitbutton.png"), cv2.IMREAD_UNCHANGED)

# Hand Detector
detector = HandDetector(detectionCon=0.8, maxHands=2)

# Variables
ballPos = [100, 100]
speedX = 15
speedY = 15
gameOver = False
score = [0, 0]
# Game mode: default to pvp until set
gameMode = 'pvp'

# AI opponent state (for pvcom)
ai_y = 250
ai_speed = 8  # pixels per frame max

# Menu and selection state
inMenu = True
inSelect = False
inConfirm = False
# Menu button positions (adjust as needed)
playPos = (438, 370)
exitPos = (436, 490)

# Confirmation popup assets
imgConfirm = cv2.imread(os.path.join(basePath, "konfirmasikeluar.png"), cv2.IMREAD_UNCHANGED)
imgYes = cv2.imread(os.path.join(basePath, "YA.png"), cv2.IMREAD_UNCHANGED)
imgNo = cv2.imread(os.path.join(basePath, "TIDAK.png"), cv2.IMREAD_UNCHANGED)

# Selection screen image
imgSelect = cv2.imread(os.path.join(basePath, "menupilih.png"))
selectedTheme = -1  # -1 means not chosen yet; 0..2 valid themes
selectedMode = None  # 'pvp' or 'pvcom' (None until chosen)

# Back button for selection screen
imgBack = cv2.imread(os.path.join(basePath, "backbutton.png"), cv2.IMREAD_UNCHANGED)
imgBack = cv2.resize(imgBack, (125, 120))
backPos = (-5, -5)

# Theme images for selection screen
imgTema1 = cv2.imread(os.path.join(basePath, "tema1.png"), cv2.IMREAD_UNCHANGED)
imgTema2 = cv2.imread(os.path.join(basePath, "tema2.png"), cv2.IMREAD_UNCHANGED)
imgTema3 = cv2.imread(os.path.join(basePath, "tema3.png"), cv2.IMREAD_UNCHANGED)
temaImages = [imgTema1, imgTema2, imgTema3]

# Mode and play button assets for selection screen
imgP1vP2 = cv2.imread(os.path.join(basePath, "p1vsp2.png"), cv2.IMREAD_UNCHANGED)
imgP1vCom = cv2.imread(os.path.join(basePath, "p1vscom.png"), cv2.IMREAD_UNCHANGED)
imgPlayGame = cv2.imread(os.path.join(basePath, "playgame.png"), cv2.IMREAD_UNCHANGED)

# Layout for selection clickable regions (for 1280x720 layout)
WIDTH, HEIGHT = 1280, 720
card_w, card_h = 340, 200
card_gap = 40
start_x = (WIDTH - (card_w * 3 + card_gap * 2)) // 2

theme_positions = [
(112, 110),
(470, 110),
(825, 110)
]

theme_image_positions = [
(100, 100),
(460, 100),
(815, 100)
]

mode_w, mode_h = 350, 130

mode_highlight_positions = [
(265, 461),
(650, 461)
]

mode_positions = [
(255, 441),
(635, 449)
]
selectPlayPos = (402, 605)
selectPlaySize = (300, 80)

# Click detection
prev_index_y = None
click_cooldown = 0  # frames
CLICK_COOLDOWN_FRAMES = 15
CLICK_DY_THRESHOLD = 20

while True:
    success, img = cap.read()

    if not success:
        break

    img = cv2.flip(img, 1)
    imgRaw = img.copy()

    # Find hands
    hands, img = detector.findHands(img, flipType=False)

    if inMenu:
        # Show menu background (if available)
        if imgMenu is not None:
            img = cv2.addWeighted(img, 0.2, imgMenu, 0.8, 0)

        # Overlay buttons
        if imgPlay is not None:
            img = cvzone.overlayPNG(img, imgPlay, playPos)
            ph, pw = imgPlay.shape[:2]
        else:
            ph = pw = 0
        if imgExit is not None:
            img = cvzone.overlayPNG(img, imgExit, exitPos)
            eh, ew = imgExit.shape[:2]
        else:
            eh = ew = 0

        # Detect 'click' using index fingertip downward motion
        if hands:
            # Use first detected hand
            hand = hands[0]
            lmList = hand.get('lmList', [])
            if lmList:
                ix, iy = lmList[8][0], lmList[8][1]

                # Draw small circle on fingertip for feedback
                cv2.circle(img, (ix, iy), 8, (0, 255, 0), cv2.FILLED)

                if prev_index_y is not None:
                    dy = iy - prev_index_y
                else:
                    dy = 0

                # Check play button click -> open selection menu
                if click_cooldown == 0 and pw > 0 and playPos[0] < ix < playPos[0] + pw and playPos[1] < iy < playPos[1] + ph:
                    if dy > CLICK_DY_THRESHOLD:
                        inMenu = False
                        inSelect = True
                        click_cooldown = CLICK_COOLDOWN_FRAMES

                # Check exit button click -> open confirmation popup
                if click_cooldown == 0 and ew > 0 and exitPos[0] < ix < exitPos[0] + ew and exitPos[1] < iy < exitPos[1] + eh:
                    if dy > CLICK_DY_THRESHOLD:
                        inConfirm = True
                        inMenu = False
                        click_cooldown = CLICK_COOLDOWN_FRAMES

                prev_index_y = iy
        else:
            prev_index_y = None

        if click_cooldown > 0:
            click_cooldown -= 1

    elif inSelect:
        # Show selection screen
        if imgSelect is not None:
            img = cv2.addWeighted(img, 0.2, imgSelect, 0.8, 0)

        # Overlay back button
        if imgBack is not None:
            img = cvzone.overlayPNG(img, imgBack, backPos)
            back_h, back_w = imgBack.shape[:2]
        else:
            back_w = back_h = 0

        # Overlay theme images
        for i, temaImg in enumerate(temaImages):
            if temaImg is not None:
                pos = theme_image_positions[i]
                img = cvzone.overlayPNG(img, temaImg, pos)

        # Highlight selected theme (if any)
        if selectedTheme is not None and selectedTheme >= 0:
            tx, ty = theme_positions[selectedTheme]
            cv2.rectangle(img, (tx - 4, ty - 4), (tx + card_w + 4, ty + card_h + 4), (0, 0, 255), 6)

        # Draw mode buttons (p1vsp2 / p1vscom)
        for i, modeImg in enumerate([imgP1vP2, imgP1vCom]):
            mx, my = mode_positions[i]
            if modeImg is not None:
                mh, mw = modeImg.shape[:2]
                posx = mx + max((mode_w - mw) // 2, 0)
                posy = my + max((mode_h - mh) // 2, 0)
                img = cvzone.overlayPNG(img, modeImg, (posx, posy))

        if selectedMode is not None:
            sel_idx = 0 if selectedMode == 'pvp' else 1
            mx, my = mode_highlight_positions[sel_idx]

            cv2.rectangle(
                img,
                (mx - 4, my - 4),
                (mx + mode_w + 4, my + mode_h + 4),
                (0, 0, 255),
                6
            )

        # Play button area
        sx, sy = selectPlayPos
        sw, sh = selectPlaySize
        if imgPlayGame is not None:
            img = cvzone.overlayPNG(img, imgPlayGame, (sx, sy))
        else:
            cv2.rectangle(img, (sx, sy), (sx + sw, sy + sh), (200, 200, 200), 2)

        # Detect selection clicks
        if hands:
            hand = hands[0]
            lmList = hand.get('lmList', [])
            if lmList:
                ix, iy = lmList[8][0], lmList[8][1]
                cv2.circle(img, (ix, iy), 8, (0, 255, 0), cv2.FILLED)

                if prev_index_y is not None:
                    dy = iy - prev_index_y
                else:
                    dy = 0

                if click_cooldown == 0 and dy > CLICK_DY_THRESHOLD:
                    # Back button
                    if back_w > 0 and backPos[0] < ix < backPos[0] + back_w and backPos[1] < iy < backPos[1] + back_h:
                        inSelect = False
                        inMenu = True
                        click_cooldown = CLICK_COOLDOWN_FRAMES

                    # Theme cards
                    for i, (tx, ty) in enumerate(theme_positions):
                        if tx < ix < tx + card_w and ty < iy < ty + card_h:
                            selectedTheme = i
                            click_cooldown = CLICK_COOLDOWN_FRAMES

                    # Mode buttons (only active after a theme is selected)
                    for i, (mx, my) in enumerate(mode_positions):
                        if mx < ix < mx + mode_w and my < iy < my + mode_h:
                            if selectedTheme is not None and selectedTheme >= 0:
                                selectedMode = 'pvp' if i == 0 else 'pvcom'
                                click_cooldown = CLICK_COOLDOWN_FRAMES

                    # Start game: only start if theme and mode chosen
                    if sx < ix < sx + sw and sy < iy < sy + sh:
                        if selectedTheme is not None and selectedTheme >= 0 and selectedMode is not None:
                            inSelect = False
                            # apply theme assets if available
                            try:
                                bg_file = ["Background1.png", "Background2.png", "Background3.png"][selectedTheme]
                                b1 = ["bat1tema1.png", "bat1tema2.png", "bat1tema3.png"][selectedTheme]
                                b2 = ["bat2tema1.png", "bat2tema2.png", "bat2tema3.png"][selectedTheme]
                                tmp = cv2.imread(os.path.join(basePath, bg_file))
                                if tmp is not None:
                                    imgBackground = tmp
                                t1 = cv2.imread(os.path.join(basePath, b1), cv2.IMREAD_UNCHANGED)
                                t2 = cv2.imread(os.path.join(basePath, b2), cv2.IMREAD_UNCHANGED)
                                if t1 is not None:
                                    imgBat1 = t1
                                if t2 is not None:
                                    imgBat2 = t2
                                # Apply ball image according to selected theme
                                try:
                                    ball_files = ["Ball1.png", "Ball2.png", "Ball3.png"]
                                    bball = ball_files[selectedTheme]
                                    bb = cv2.imread(os.path.join(basePath, bball), cv2.IMREAD_UNCHANGED)
                                    if bb is not None:
                                        imgBall = bb
                                except Exception:
                                    pass
                            except Exception:
                                pass

                            # set game mode variable for gameplay
                            gameMode = selectedMode
                            click_cooldown = CLICK_COOLDOWN_FRAMES

                prev_index_y = iy
        else:
            prev_index_y = None

        if click_cooldown > 0:
            click_cooldown -= 1

    elif inConfirm:
        # Show menu background behind popup
        if imgMenu is not None:
            img = cv2.addWeighted(img, 0.2, imgMenu, 0.8, 0)

        # Overlay confirmation popup centered
        if imgConfirm is not None:
            ch, cw = imgConfirm.shape[:2]
            cx = (WIDTH - cw) // 2
            cy = (HEIGHT - ch) // 2
            img = cvzone.overlayPNG(img, imgConfirm, (cx, cy))
        else:
            cx = (WIDTH - 400) // 2
            cy = (HEIGHT - 200) // 2
            cw = 400
            ch = 200

        # Overlay Yes/No buttons if available
        yes_w = yes_h = no_w = no_h = 0
        if imgYes is not None:
            yes_h, yes_w = imgYes.shape[:2]
            yesPos = (cx + 400, cy + 281)
            img = cvzone.overlayPNG(img, imgYes, yesPos)
        if imgNo is not None:
            no_h, no_w = imgNo.shape[:2]
            noPos = (cx + 667, cy + 282)
            img = cvzone.overlayPNG(img, imgNo, noPos)

        # Detect clicks on Yes/No
        if hands:
            hand = hands[0]
            lmList = hand.get('lmList', [])
            if lmList:
                ix, iy = lmList[8][0], lmList[8][1]
                cv2.circle(img, (ix, iy), 8, (0, 255, 0), cv2.FILLED)

                if prev_index_y is not None:
                    dy = iy - prev_index_y
                else:
                    dy = 0

                if click_cooldown == 0 and dy > CLICK_DY_THRESHOLD:
                    # Yes
                    if imgYes is not None and yesPos[0] < ix < yesPos[0] + yes_w and yesPos[1] < iy < yesPos[1] + yes_h:
                        break
                    # No -> back to main menu
                    if imgNo is not None and noPos[0] < ix < noPos[0] + no_w and noPos[1] < iy < noPos[1] + no_h:
                        inConfirm = False
                        inMenu = True
                        click_cooldown = CLICK_COOLDOWN_FRAMES

                prev_index_y = iy
        else:
            prev_index_y = None

        if click_cooldown > 0:
            click_cooldown -= 1

    else:
        # Overlay background
        img = cv2.addWeighted(img, 0.2, imgBackground, 0.8, 0)

        # Check paddles: either both hands (pvp) or left = AI and right = player (pvcom)
        h1, w1, _ = imgBat1.shape
        # AI-controlled left paddle
        if gameMode == 'pvcom':
            # Move AI paddle towards ball with limited speed
            target_y = int(ballPos[1] - h1 // 2)
            delta = target_y - ai_y
            if abs(delta) > ai_speed:
                ai_y += int(np.sign(delta) * ai_speed)
            else:
                ai_y = target_y
            ai_y = int(np.clip(ai_y, 20, 415))
            img = cvzone.overlayPNG(img, imgBat1, (59, ai_y))
            # Collision left
            if 59 < ballPos[0] < 59 + w1 and ai_y < ballPos[1] < ai_y + h1:
                speedX = -speedX
                ballPos[0] += 30
                score[0] += 1

            # Player controls right paddle via right hand if available
            if hands:
                for hand in hands:
                    if hand['type'] == 'Right':
                        x, y, w, h = hand['bbox']
                        y1 = y - h1 // 2
                        y1 = int(np.clip(y1, 20, 415))
                        img = cvzone.overlayPNG(img, imgBat2, (1195, y1))
                        if 1195 - 50 < ballPos[0] < 1195 and y1 < ballPos[1] < y1 + h1:
                            speedX = -speedX
                            ballPos[0] -= 30
                            score[1] += 1

        else:
            # PvP: both paddles controlled by detected hands
            if hands:
                for hand in hands:
                    x, y, w, h = hand['bbox']
                    y1 = y - h1 // 2
                    y1 = int(np.clip(y1, 20, 415))

                    # Left hand
                    if hand['type'] == "Left":
                        img = cvzone.overlayPNG(img, imgBat1, (59, y1))
                        if 59 < ballPos[0] < 59 + w1 and y1 < ballPos[1] < y1 + h1:
                            speedX = -speedX
                            ballPos[0] += 30
                            score[0] += 1

                    # Right hand
                    if hand['type'] == "Right":
                        img = cvzone.overlayPNG(img, imgBat2, (1195, y1))
                        if 1195 - 50 < ballPos[0] < 1195 and y1 < ballPos[1] < y1 + h1:
                            speedX = -speedX
                            ballPos[0] -= 30
                            score[1] += 1

        # Game logic
        if ballPos[0] < 40 or ballPos[0] > 1200:
            gameOver = True

        if gameOver:
            img = imgGameOver
            cv2.putText(img, str(score[1] + score[0]).zfill(2), (585, 360), cv2.FONT_HERSHEY_COMPLEX, 2.5, (0, 0, 0), 5)
        else:
            if ballPos[1] >= 500 or ballPos[1] <= 10:
                speedY = -speedY

            ballPos[0] += speedX
            ballPos[1] += speedY

            img = cvzone.overlayPNG(img, imgBall, ballPos)

            cv2.putText(img, str(score[0]), (300, 650), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)
            cv2.putText(img, str(score[1]), (900, 650), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)

    # Small webcam preview
    img[580:700, 20:233] = cv2.resize(imgRaw, (213, 120))

    cv2.imshow("Image", img)

    key = cv2.waitKey(1)

    if key == ord('r'):
        ballPos = [100, 100]
        speedX = 15
        speedY = 15
        gameOver = False
        score = [0, 0]
        imgGameOver = cv2.imread(os.path.join(basePath, "GameOver1.png"))
    # Return to main menu when pressing 'm' or 'M'
    if key == ord('m') or key == ord('M'):
        inMenu = True
        inSelect = False
        inConfirm = False
        gameOver = False
        # Reset game state
        ballPos = [100, 100]
        speedX = 15
        speedY = 15
        score = [0, 0]
        imgBackground = cv2.imread(os.path.join(basePath, "Background.png"))
        # Reload GameOver image to clear any drawn text so it doesn't accumulate
        imgGameOver = cv2.imread(os.path.join(basePath, "GameOver1.png"))
        prev_index_y = None
        click_cooldown = 0

# Cleanup
cap.release()
cv2.destroyAllWindows()