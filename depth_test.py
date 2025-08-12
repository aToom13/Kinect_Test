import freenect
import cv2
import numpy as np

def get_depth():
    """
    Kinect'in derinlik sensöründen bir çerçeve alır.
    Bu versiyon, veri formatını belirterek ve normalizasyonu daha doğru yaparak
    daha kararlı çalışmayı hedefler.
    """
    # Veriyi FREENECT_DEPTH_11BIT formatında istiyoruz.
    # Bu, freenect'in en temel ham derinlik formatıdır.
    depth, _ = freenect.sync_get_depth(format=freenect.DEPTH_11BIT)

    # Derinlik verisi 0-2047 arasında (11-bit).
    # Bunu 0-255 (8-bit) aralığına ölçekleyerek görselleştirebiliriz.
    # Geçersiz pikselleri (2047) siyaha çevirelim.
    depth[depth == 2047] = 0
    
    # Kalan pikselleri 0-255 arasına yayalım.
    depth = (depth / 1024.0 * 255).astype(np.uint8)

    return depth

if __name__ == "__main__":
    print("Geliştirilmiş derinlik testi başlatılıyor...")
    print("Bir pencere açılmazsa veya program donarsa, USB portunuzu değiştirmeyi deneyin.")
    print("Çıkmak için 'q' tuşuna basın.")
    
    while 1:
        try:
            depth_frame = get_depth()

            # Görüntüyü daha iyi seçebilmek için bir renk haritası uygulayalım (isteğe bağlı)
            depth_colormap = cv2.applyColorMap(depth_frame, cv2.COLORMAP_JET)

            # Hem ham (siyah-beyaz) hem de renklendirilmiş görüntüyü gösterelim
        #cv2.imshow('Derinlik (Siyah-Beyaz)', depth_frame)
            cv2.imshow('Derinlik (Renkli)', depth_colormap)

            if cv2.waitKey(10) == ord('q'):
                break
        
        except TypeError:
            # Bazen ilk birkaç çerçeve boş gelebilir, bu hatayı görmezden gel.
            print("İlk çerçeve alınamadı, tekrar deneniyor...")
            continue

    cv2.destroyAllWindows()
    freenect.sync_stop()
    print("Program sonlandırıldı.")
