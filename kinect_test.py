import freenect
import cv2
import numpy as np
import sys
import threading

# Gelen çerçeveleri saklamak için global değişkenler
latest_depth_frame = None
latest_video_frame = None
# Kilitler, aynı anda yazma/okuma çakışmalarını önlemek için
depth_lock = threading.Lock()
video_lock = threading.Lock()

# Ana döngünün çalışıp çalışmadığını kontrol etmek için
keep_running = True

def video_callback(dev, video, timestamp):
    """freenect tarafından yeni bir video çerçevesi geldiğinde çağrılır."""
    global latest_video_frame
    with video_lock:
        # Gelen RGB formatını OpenCV'nin kullandığı BGR formatına çevir
        video_bgr = cv2.cvtColor(video, cv2.COLOR_RGB2BGR)
        latest_video_frame = video_bgr.copy()

def depth_callback(dev, depth, timestamp):
    """freenect tarafından yeni bir derinlik çerçevesi geldiğinde çağrılır."""
    global latest_depth_frame
    with depth_lock:
        # 11-bit derinlik verisini görselleştirilebilir hale getir
        np.clip(depth, 0, 2**10 - 1, depth)
        depth >>= 2
        depth = depth.astype(np.uint8)
        # Renklendirerek daha anlaşılır yap
        depth_colored = cv2.applyColorMap(depth, cv2.COLORMAP_JET)
        latest_depth_frame = depth_colored.copy()

def freenect_thread_body(ctx):
    """freenect olaylarını işlemek için ayrı bir thread'de çalışır."""
    while keep_running:
        freenect.proc_events(ctx)

def change_tilt(device, delta):
    """Motorun eğim açısını değiştirir."""
    current_angle = freenect.get_tilt_degs(device)
    new_angle = max(-30, min(30, current_angle + delta))
    print(f"Motor açısı ayarlanıyor: {new_angle} derece")
    freenect.set_tilt_degs(device, new_angle)

def level_motor(device):
    """Motoru ortaya (0 derece) hizalar."""
    print("Motor ortaya hizalanıyor...")
    freenect.set_tilt_degs(device, 0)

if __name__ == "__main__":
    print("Kinect Kontrolü - Asenkron Model")
    print("-" * 30)
    print(" 'w' -> Motor Yukarı | 's' -> Motor Aşağı | 'x' -> Ortala | 'q' -> Çık")
    print("-" * 30)

    # Cihazı başlat
    ctx = freenect.init()
    dev = freenect.open_device(ctx, 0)
    if not dev:
        print("Hata: Kinect cihazı açılamadı!")
        freenect.shutdown(ctx)
        sys.exit(1)

    try:
        # Motoru ortala
        level_motor(dev)
        
        # Callback fonksiyonlarını ayarla
        freenect.set_video_callback(dev, video_callback)
        freenect.set_depth_callback(dev, depth_callback)
        
        # Veri akış modlarını ve formatlarını ayarla
        freenect.set_video_mode(dev, freenect.RESOLUTION_MEDIUM, freenect.VIDEO_RGB)
        freenect.set_depth_mode(dev, freenect.RESOLUTION_MEDIUM, freenect.DEPTH_11BIT)
        
        # Veri akışlarını başlat
        freenect.start_video(dev)
        freenect.start_depth(dev)

        # freenect olaylarını işlemek için thread'i başlat
        f_thread = threading.Thread(target=freenect_thread_body, args=(ctx,))
        f_thread.start()

        # Ana döngü: Görüntüleri göster ve klavyeyi dinle
        while keep_running:
            # En son gelen çerçeveleri al
            with video_lock:
                video_display = latest_video_frame
            with depth_lock:
                depth_display = latest_depth_frame

            # Eğer çerçeveler henüz gelmediyse, boş bir görüntü göster
            if video_display is None:
                video_display = np.zeros((480, 640, 3), dtype=np.uint8)
            if depth_display is None:
                depth_display = np.zeros((480, 640, 3), dtype=np.uint8)

            cv2.imshow('RGB Goruntusu', video_display)
            cv2.imshow('Derinlik Goruntusu (Renkli)', depth_display)

            key = cv2.waitKey(10)
            if key == ord('q'):
                break
            elif key == ord('w'):
                change_tilt(dev, 5)
            elif key == ord('s'):
                change_tilt(dev, -5)
            elif key == ord('x'):
                level_motor(dev)

    finally:
        # Program kapanırken tüm kaynakları temizle
        print("Program sonlandırılıyor...")
        keep_running = False
        f_thread.join() # Thread'in bitmesini bekle
        
        if dev:
            level_motor(dev)
            freenect.stop_video(dev)
            freenect.stop_depth(dev)
            freenect.close_device(dev)
        if ctx:
            freenect.shutdown(ctx)
        cv2.destroyAllWindows()

