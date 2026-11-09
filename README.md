# oracle-a1-tracker

Oracle Cloud **Always Free A1** kapasite avcısı — **GitHub Actions'ta bulutta** koşar
(PC'den bağımsız; ev bilgisayarı kapalı/uykuda olsa da sürer). Kapasite açılırsa A1 instance'ı
yakalar ve **Telegram'a bildirir**.

## Nasıl çalışır
- `.github/workflows/check.yml` → her 10 dakikada bir (+ elle `workflow_dispatch`).
- `check_capacity.py`:
  1. Zaten A1 instance varsa sessiz çıkar (tekrar denemez).
  2. Yoksa A1 launch dener (2 OCPU / 12 GB — 2026 yeni free limiti).
  3. **Başarılı → Telegram'a "YAKALANDI + Instance OCID".**
  4. Kapasite yok / throttle → sessiz (spam yok). Config hatası → Telegram uyarısı.

## Gizlilik
- Private repo. Hesap tanımlayıcıları (OCID) kod içinde; **gerçek sır yalnızca OCI private key.**
- Key **GitHub Secrets**'ta (`OCI_KEY_B64` = private key PEM'in base64'ü), kodda değil.

## Gerekli Secrets (repo → Settings → Secrets and variables → Actions)
| Secret | Değer |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token |
| `TELEGRAM_CHAT_ID` | Telegram chat id |
| `OCI_KEY_B64` | `E:\AI\Keys\oci_api_key.pem` dosyasının base64'ü (tek satır) |

## Kota
Private repo GitHub Actions: 2000 dk/ay ücretsiz. 10 dk cron ≈ ayda ~1500 dk altı.
Daha agresif (her 5 dk) istenirse repo'yu **public** yap → Actions dakikası sınırsız
(key yine secret olduğu için güvenli).

## Not
Yerel PC avcısı (`E:\AI\bot1-hunter`) ile birlikte çalışabilir: ikisi de launch öncesi
"zaten A1 var mı?" kontrol eder, çift instance oluşmaz. Bu bulut avcısı çalışınca yerel
avcıya gerek kalmayabilir (PC-bağımsız).
