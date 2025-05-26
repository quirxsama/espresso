# Katkıda Bulunma Rehberi

Espresso projesine katkıda bulunmak istediğiniz için teşekkür ederiz! Bu belge, projeye nasıl katkıda bulunabileceğinizi açıklar.

## Geliştirme Ortamı Kurulumu

1. Projeyi klonlayın:
```bash
git clone https://github.com/quirxsama/espresso.git
cd espresso
```

2. Bağımlılıkları yükleyin:
```bash
# Sistem bağımlılıkları (Ubuntu/Debian için)
sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1 lm-sensors

# Python bağımlılıkları
pip install -r requirements.txt
```

3. Geliştirme modunda kurulum yapın:
```bash
pip install -e .
```

## Kod Standartları

- Kod PEP 8 standartlarına uygun olmalıdır
- Tüm yeni özellikler için birim testleri eklenmelidir
- Tüm değişiklikler için belgelendirme güncellenmelidir
- Modüler, bileşen tabanlı ve okunabilir kod yazılmalıdır

## Pull Request Süreci

1. Yeni bir branch oluşturun:
```bash
git checkout -b ozellik/yeni-ozellik
```

2. Değişikliklerinizi yapın ve commit edin:
```bash
git commit -m "Yeni özellik: Özellik açıklaması"
```

3. Branch'inizi GitHub'a push edin:
```bash
git push origin ozellik/yeni-ozellik
```

4. GitHub üzerinden bir Pull Request oluşturun

## Hata Raporlama

Hata raporları için lütfen GitHub Issues kullanın. Hata raporlarınızda şu bilgileri belirtin:

- Hatanın açıklaması
- Hatayı yeniden oluşturma adımları
- Beklenen davranış
- Gerçekleşen davranış
- Sistem bilgileri (İşletim sistemi, Python sürümü, vb.)

## Yeni Özellik Önerileri

Yeni özellik önerileri için GitHub Issues kullanabilirsiniz. Önerilerinizde şu bilgileri belirtin:

- Özelliğin açıklaması
- Neden bu özelliğe ihtiyaç duyulduğu
- Mümkünse, özelliğin nasıl uygulanabileceğine dair fikirler

## İletişim

Sorularınız için GitHub Issues kullanabilir veya proje yöneticisiyle iletişime geçebilirsiniz.

---

Katkılarınız için şimdiden teşekkür ederim!
