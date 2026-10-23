# cybergym-incidents-oct

An [OpenEnv](https://github.com/meta-pytorch/OpenEnv) cyber environment for
[OpenEnv Arena: CyberGym](https://openenvarena-cybergym.hf.space): eight more
October-2026 incident classes as synthetic tasks — exposed secrets in a status
artifact, planted SSH key with its use in logs, live API key among logged test
keys, the one binary whose checksum changed across releases, a rogue backup
identity, a PHP eval RCE payload to craft, an npm preinstall exfil hook, and
identifying the last safe release. Deterministic artifacts, server-side answer
hashes, nothing to shortcut inside the sandbox.

- Action schema: `cmd` (shell in the task folder; php-cli and openssl are
  available) and `answer` (final answer; ends the episode).
- Reward 1.0 for the exact answer, 0.0 otherwise.

## Licence

BSD-3-Clause, following OpenEnv.
