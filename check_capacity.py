#!/usr/bin/env python3
"""Oracle Cloud Always Free A1 kapasite AVCISI — GitHub Actions'ta bulutta koşar.
Her çalışmada: (1) zaten A1 instance var mı bak -> varsa sessiz çık.
(2) yoksa A1 launch dene -> BAŞARILIYSA Telegram'a 'YAKALANDI' bildir.
(3) kapasite yok / throttle -> SESSIZ (spam yok). (4) config hatası -> Telegram'a uyar.

PC-bağımsız: GitHub sunucusunda çalışır, ev PC'si kapalı/uykuda olsa da sürer.
Gizli: yalnızca OCI private key + Telegram token GitHub Secrets'tan gelir.
"""
import os
import sys
import base64
import json
import urllib.parse
import urllib.request

import oci

# --- Hesaba özgü (gizli olmayan) tanımlayıcılar — private repo ---
REGION  = "ap-singapore-1"
USER    = "ocid1.user.oc1..aaaaaaaaozb3ny6m75qaalo7volfnvnuxvtdtirv2bvgoyfcqknizt2ien6a"
FINGER  = "92:2b:34:29:97:b0:03:22:4b:64:d8:94:26:73:4c:7e"
TENANCY = "ocid1.tenancy.oc1..aaaaaaaadtqny7jv7f76foydwj74t727rapjehlujpu4kyvb7dojtbzj4bha"
AD      = "vhBU:AP-SINGAPORE-1-AD-1"
IMAGE   = "ocid1.image.oc1.ap-singapore-1.aaaaaaaamynzciw3t7fypsdqahuupzsvbv5ewlubquu3ksfqugxchksgxm4q"
SUBNET  = "ocid1.subnet.oc1.ap-singapore-1.aaaaaaaaiorkinj5x5wpqprnhzwwy3dkxdw6syzfh6bzw4rayit7netbvkvq"
SSH_PUB = ("ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC5W38wnRCOBLq5nh1kIV/OMyBsfBjQ9WVhD6UAQS3D/"
           "VZUJUfpLJl49l9pvnKvPSy3h8B/feG1wIQ4ibcZaty+EqAKRyOGi3Rcj8msN7UvPYqlkMCS5owTsbNzijFpffah12l"
           "DZXfVPhaeTGxoNg5GAOnLP+v6qSc/VEMvMxlB8HSnUz6EHLCOilgoGi3EuqYlbZb0YnEYmxmihggUM6tgrG1PQ1QXC"
           "ca8zHNjlb3fOOZ29NkO/GUK+vL6OSfYsUswIidtpGWLftVcOhB9Am/MlhIxrvxlYcNBUt1fbB+uClzie+SyCc1Hbd5"
           "4U4JSdixT2X/KUJgmGM8JGpzIg/73 oracle-bot1")
OCPUS   = 2       # yeni Always Free limiti (2026-06): 2 OCPU / 12 GB
MEM_GBS = 12
BOOT_GB = 200


def tg(msg):
    try:
        tok = os.environ["TELEGRAM_BOT_TOKEN"]
        chat = os.environ["TELEGRAM_CHAT_ID"]
        data = urllib.parse.urlencode({"chat_id": chat, "text": msg}).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{tok}/sendMessage", data=data)
        urllib.request.urlopen(req, timeout=20).read()
    except Exception as e:
        print("telegram hata:", e)


def main():
    key_pem = base64.b64decode(os.environ["OCI_KEY_B64"]).decode()
    cfg = {"user": USER, "fingerprint": FINGER, "tenancy": TENANCY,
           "region": REGION, "key_content": key_pem}
    oci.config.validate_config(cfg)
    compute = oci.core.ComputeClient(cfg)

    # 1) zaten A1 instance var mi? (tekrar launch etme, LimitExceeded dongusune girme)
    insts = oci.pagination.list_call_get_all_results(
        compute.list_instances, TENANCY).data
    alive = [i for i in insts if i.shape == "VM.Standard.A1.Flex"
             and i.lifecycle_state in ("RUNNING", "PROVISIONING", "STARTING")]
    if alive:
        print("zaten A1 var, atlaniyor:", alive[0].id)
        return 0

    # 2) launch dene
    details = oci.core.models.LaunchInstanceDetails(
        compartment_id=TENANCY, availability_domain=AD, display_name="bot1-vps",
        shape="VM.Standard.A1.Flex",
        shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(
            ocpus=OCPUS, memory_in_gbs=MEM_GBS),
        source_details=oci.core.models.InstanceSourceViaImageDetails(
            image_id=IMAGE, boot_volume_size_in_gbs=BOOT_GB),
        create_vnic_details=oci.core.models.CreateVnicDetails(
            subnet_id=SUBNET, assign_public_ip=True),
        metadata={"ssh_authorized_keys": SSH_PUB},
    )
    try:
        inst = compute.launch_instance(details).data
        tg(f"ORACLE A1 YAKALANDI!\nInstance: {inst.id}\nBolge: {REGION}\n"
           f"Shape: A1 {OCPUS} OCPU / {MEM_GBS} GB / {BOOT_GB} GB disk\n"
           f"Ubuntu 24.04 ARM. Kuruluma gecebilirsin.")
        print("BASARILI:", inst.id)
        return 0
    except oci.exceptions.ServiceError as e:
        m = (e.message or "").lower()
        code = e.code or ""
        if e.status == 500 or "capacity" in m or code in ("InternalError", "OutOfHostCapacity"):
            print("kapasite yok (sessiz)")        # spam onleme: bildirim yok
            return 0
        if e.status == 429:
            print("429 throttle (sessiz)")
            return 0
        # beklenmedik/config hatasi -> bildir (nadir, kullanici bir kez duzeltir)
        tg(f"Oracle A1 tracker HATA: {e.status} {code}: {e.message}")
        print("KRITIK:", e.status, code, e.message)
        return 1


if __name__ == "__main__":
    sys.exit(main())
