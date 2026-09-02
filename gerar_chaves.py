import base64
import datetime
import hashlib


class LicenseManager:

  SALT = "DEEPMARKET_ENTERPRISE_SECURE_2026_KEY"

  @classmethod
  def generate_license(
      cls, client_id: str, days_valid: int = 365
  ) -> str:
    expiry_date = (
        datetime.date.today() + datetime.timedelta(days=days_valid)
    ).strftime("%Y-%m-%d")
    payload = f"{client_id}|{expiry_date}"
    signature = hashlib.sha256(
        f"{payload}|{cls.SALT}".encode()
    ).hexdigest()[:8]
    token = f"{payload}|{signature}"
    return base64.b64encode(token.encode()).decode()


# Gera 3 chaves de licença prontas para entrega imediata
for i in range(1, 4):
  chave = LicenseManager.generate_license(
      client_id=f"CLIENTE_VIP_00{i}", days_valid=365
  )
  print(f"Licença Cliente {i}: {chave}")