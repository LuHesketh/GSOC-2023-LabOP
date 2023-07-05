# Instructions
- Setup virtual environment:
  ```bash
  python -m venv .venv
  source .venv/bin/activate
  ```
- Install correct labop version:
  ```bash
  pip install -e git+https://github.com/Bioprotocols/labop.git@ecl#egg=labop
  ```
- To run:
  ```bash
  python protocols/simple_transfer/labop/hello_world_protocol_LABOP.py
  ```