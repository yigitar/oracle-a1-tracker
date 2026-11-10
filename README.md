# oracle-a1-tracker

Oracle Cloud **Always Free A1** kapasite avcısı — **GitHub Actions'ta bulutta** koşar
(PC'den bağımsız; ev bilgisayarı kapalı/uykuda olsa da sürer). Kapasite açılırsa A1 instance'ı
yakalar ve **Telegram'a bildirir**.

## Nasıl çalışır
- `.github/workflows/check.yml` → her 5 dakikada bir (+ elle `workflow_dispatch`).
- `check_capacity.py`:
  1. Zaten A1 instance varsa sessiz çıkar (tekrar denemez, LimitExceeded döngüsüne girmez).
  2. Yoksa A1 launch dener (2 OCPU / 12 GB — 2026 yeni free limiti).
  3. **Başarılı → Telegram'a "YAKALANDI + Instance OCID".**
  4. Kapasite yok / throttle → sessiz (spam yok). Config hatası → Telegram uyarısı.

## Güvenli public
Repo **public** (Actions dakikası sınırsız → her 5 dk kontrol). Güvenlik:
- **Kodda hiçbir sır ve hesap tanımlayıcısı yok** — hepsi GitHub Secrets'ta.
- GitHub Secrets public repo'da da **şifreli**; fork/PR'lar erişemez, loglara yazılmaz.
- Kodda yalnızca gizli-olmayan sabitler var: bölge/AD (herkese açık), genel Oracle image OCID
  (hesaba özel değil), public SSH anahtarı.

## Gerekli Secrets (repo → Settings → Secrets and variables → Actions)
| Secret | Değer |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token |
| `TELEGRAM_CHAT_ID` | Telegram chat id |
| `OCI_KEY_B64` | OCI API private key PEM'in base64'ü (tek satır) |
| `OCI_USER` | OCI user OCID |
| `OCI_TENANCY` | OCI tenancy OCID |
| `OCI_FINGERPRINT` | OCI API key fingerprint |
| `OCI_SUBNET` | Hedef public subnet OCID |

## Kota
Public repo → GitHub Actions dakikası **sınırsız** (ücretsiz). 5 dk cron rahatça çalışır.

## Not
Yerel PC avcısı (`E:\AI\bot1-hunter`) ile birlikte çalışabilir: ikisi de launch öncesi
"zaten A1 var mı?" kontrol eder → çift instance oluşmaz. Bu bulut avcısı PC-bağımsız olduğu
için yerel avcıya artık gerek kalmayabilir.
