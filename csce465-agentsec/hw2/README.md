# CSCE 465 Homework 2

Protect agent messages with classic cryptography: AES-CTR, HMAC-SHA-256,
finite-field Diffie-Hellman, and RSA-PSS.

Tested on Ubuntu 24.04 with Python 3.12 and OpenSSL 3.0.13.

## Setup

```bash
cd "$HOME/csce465-agentsec"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install cryptography==49.0.0 pytest==9.1.1
```

The Diffie-Hellman group file `ffdhe3072.pem` is included. To regenerate it:

```bash
cd "$HOME/csce465-agentsec/hw2"
openssl genpkey -genparam -algorithm DH -pkeyopt group:ffdhe3072 -out ffdhe3072.pem
```

## Run

Activate the virtual environment and run everything from the `hw2` folder.

```bash
source "$HOME/csce465-agentsec/.venv/bin/activate"
cd "$HOME/csce465-agentsec/hw2"

python baseline_ctr.py     # Task 1: CTR bit-flip and replay
python handshake.py        # Task 2: authenticated Diffie-Hellman handshake
python secure_record.py    # Task 3: encrypt-then-MAC record layer
python -m pytest tests/ -v # Task 4: adversarial tests
```

Use `python -m pytest`, not plain `pytest`, so the tests can import the modules
in `hw2`.

## Files

| File | Purpose |
|---|---|
| `report.pdf` | Report |
| `baseline_ctr.py` | Task 1 |
| `handshake.py` | Task 2 |
| `secure_record.py` | Task 3 |
| `tests/` | Task 4 |
| `ffdhe3072.pem` | ffdhe3072 group parameters |
| `AI_USAGE.md` | AI usage description and logs |