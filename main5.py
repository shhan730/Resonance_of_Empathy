import cv2
from deepface import DeepFace
import pygame
import numpy as np
import qrcode
import webbrowser

# pygame 초기화
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Resonance of Empathy")

# 화면 크기 가져오기
screen_width, screen_height = pygame.display.get_surface().get_size()

# 웹캠에서 비디오 캡처 시작
cap = cv2.VideoCapture(0)

# 감정 색상 및 관련 링크 매핑
emotion_data = {
    "angry": {"color": (255, 0, 0), "link": "https://www.canva.com/colors/color-meanings/red/"},
    "disgust": {"color": (0, 255, 0), "link": "https://www.canva.com/colors/color-meanings/green/"},
    "fear": {"color": (0, 0, 255), "link": "https://www.canva.com/colors/color-meanings/blue/"},
    "happy": {"color": (255, 255, 0), "link": "https://www.canva.com/colors/color-meanings/yellow/"},
    "sad": {"color": (0, 255, 255), "link": "https://www.canva.com/colors/color-meanings/cyan/"},
    "surprise": {"color": (255, 0, 255), "link": "https://www.canva.com/colors/color-meanings/magenta/"},
    "neutral": {"color": (255, 255, 255), "link": "https://www.canva.com/colors/color-meanings/white/"}
}

# 감정 누적을 위한 변수
emotion_counts = {emotion: 0 for emotion in emotion_data}

# 감정 감지 주기 설정 (프레임 수)
emotion_detection_interval = 10
circle_drawing_interval = 20
frame_count = 0
running = True  # 상태 변수 추가

# 초기 감정 설정
dominant_emotion = "neutral"
emotion_color = emotion_data[dominant_emotion]["color"]

def draw_soft_particles(screen, color):
    for _ in range(30):  # 파티클 수 조정
        x, y = np.random.randint(0, screen_width), np.random.randint(0, screen_height)
        size = np.random.randint(100, 200)  # 동그라미 크기 증가
        transparency = np.random.randint(50, 150)
        s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color, transparency), (size, size), size)
        screen.blit(s, (x, y))

def draw_button(screen, text, position, size=(200, 50)):
    font = pygame.font.Font(None, 36)
    button_surface = pygame.Surface(size)
    button_surface.fill((100, 100, 100))
    pygame.draw.rect(button_surface, (255, 255, 255), button_surface.get_rect(), 2)
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(size[0] // 2, size[1] // 2))
    button_surface.blit(text_surface, text_rect)
    screen.blit(button_surface, position)
    return button_surface.get_rect(topleft=position)

while True:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                cap.release()
                cv2.destroyAllWindows()
                pygame.quit()
                exit()
            elif event.key == pygame.K_SPACE:
                # QR 코드 스캔 시 해당 감정 관련 링크 열기
                webbrowser.open(emotion_data[dominant_emotion]["link"])
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                running = not running

    if running:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        frame_count += 1

        if frame_count % emotion_detection_interval == 0:
            # 얼굴 감정 인식
            try:
                emotion = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
                dominant_emotion = emotion[0]['dominant_emotion']
                emotion_color = emotion_data[dominant_emotion]["color"]
                if dominant_emotion != "neutral":
                    emotion_counts[dominant_emotion] += 1
            except:
                dominant_emotion = "neutral"
                emotion_color = emotion_data[dominant_emotion]["color"]
        
        # 인식된 감정을 바탕으로 인터랙티브한 시각 효과 생성
        if frame_count % circle_drawing_interval == 0:
            screen.fill((0, 0, 0))  # 화면 초기화
        
            # 감정에 따른 부드러운 파티클 효과
            draw_soft_particles(screen, emotion_color)
        
            # 감정 누적 시각화 (중립 감정 제외)
            filtered_emotion_counts = {k: v for k, v in emotion_counts.items() if k != "neutral"}
            total_emotions = sum(filtered_emotion_counts.values())
            if total_emotions > 0:
                center_x, center_y = screen_width // 2, screen_height // 2
                arc_radius = 200
                start_angle = 0
                for emotion, count in filtered_emotion_counts.items():
                    angle = count / total_emotions * 360
                    if angle > 0:
                        pygame.draw.arc(screen, emotion_data[emotion]["color"], (center_x - arc_radius, center_y - arc_radius, arc_radius * 2, arc_radius * 2), start_angle, start_angle + np.radians(angle), 100)
                        start_angle += np.radians(angle)
            
                # QR 코드 생성
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(emotion_data[dominant_emotion]["link"])
                qr.make(fit=True)
                qr_img = qr.make_image(fill_color="black", back_color="white")
                qr_img = qr_img.resize((150, 150))
                qr_img = qr_img.convert('RGB')
                qr_surface = pygame.image.fromstring(qr_img.tobytes(), qr_img.size, 'RGB')
                screen.blit(qr_surface, (center_x - 75, center_y + arc_radius + 20))
        
        # 감정 텍스트 표시
        # font = pygame.font.Font(None, 36)
        # text = font.render(f"Current Emotion: {dominant_emotion}", True, (255, 255, 255))
        # screen.blit(text, (10, 10))
    
    # 시작/일시정지 버튼 그리기
    if running:
        button_text = "Pause"
    else:
        button_text = "Start"
    button_rect = draw_button(screen, button_text, (screen_width - 220, 10))

    pygame.display.flip()
