import freenect
import cv2
import numpy as np

# Kinect'ten RGB görüntü çerçevesi almak için bir fonksiyon
def get_video():
    """
    Kinect'in RGB kamerasından bir çerçeve alır.
    Veriyi freenect'in ham formatından OpenCV'nin BGR formatına dönüştürür.
    """
    array, _ = freenect.sync_get_video()
    # Gelen RGB formatını OpenCV'nin kullandığı BGR formatına çevir
    array = cv2.cvtColor(array, cv2.COLOR_RGB2BGR)
    return array

if __name__ == "__main__":
    while 1:
        # Kinect'ten bir çerçeve al
        frame = get_video()

        # Çerçeveyi 'RGB Goruntusu' adlı bir pencerede göster
        cv2.imshow('RGB Goruntusu', frame)

        # 10 milisaniye bekle ve bir tuşa basılıp basılmadığını kontrol et
        # 'q' tuşuna basılırsa döngüden çık
        if cv2.waitKey(10) == ord('q'):
            break

    # Tüm OpenCV pencerelerini kapat
    cv2.destroyAllWindows()
    # freenect context'ini güvenli bir şekilde kapat (bazı sistemlerde gerekli)
    # freenect.sync_stop() # Bu satır bazen hataya neden olabilir, gerekirse açın.
