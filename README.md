# Espresso - Sistem Monitörü

Espresso, GTK4 kullanarak geliştirilmiş, Python tabanlı gerçek zamanlı bir sistem monitörüdür. Bu uygulama, sisteminizin CPU, RAM, GPU ve disk kullanımını görselleştirmenizi sağlar.

## Özellikler

- CPU kullanımı ve sıcaklık izleme
- RAM ve swap kullanımı görselleştirme
- NVIDIA ve AMD GPU desteği
- Disk kullanımı ve dizin tarama
- Modern ve kullanıcı dostu arayüz

## Kurulum

```bash
# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Uygulamayı çalıştırın
python -m espresso
```

## Komut Satırı Argümanları

- `--interval`: Veri güncelleme aralığı (saniye)
- `--theme`: Uygulama teması (light/dark)
- `--scan-home`: Home dizinini otomatik tara

## Geliştirme

Bu proje MVC mimarisi kullanılarak geliştirilmiştir. Katkıda bulunmak için lütfen bir pull request açın.
