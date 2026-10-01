#!/usr/bin/env python3
"""
Emite un token firmado para el WebSocket.

Deliberadamente NO es un endpoint HTTP. Un endpoint que reparte tokens sin
autenticación es el mismo agujero que acabamos de cerrar, con otra forma: el
WebSocket pasaría a estar protegido por una puerta que cualquiera puede abrir.
Emitir desde la línea de comandos exige acceso a la máquina y a la clave.

Uso:
  python backend/scripts/issue_ws_token.py
  python backend/scripts/issue_ws_token.py --horas 8
  python backend/scripts/issue_ws_token.py --env        # línea para .env

Requiere HYDRA_SECRET_KEY en el entorno, la misma que use el backend. Si no
está, el programa falla en vez de inventar una clave efímera: un token firmado
con una clave distinta a la del servidor sería rechazado, y el fallo parecería
de red.
"""

from __future__ import annotations

import argparse
import os
import secrets
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main() -> int:
    ap = argparse.ArgumentParser(description="Emite un token para /ws.")
    ap.add_argument("--horas", type=float, default=24.0,
                    help="validez en horas (def. 24). Mantenlo corto: la "
                         "revocación no está implementada.")
    ap.add_argument("--env", action="store_true",
                    help="imprime la línea lista para .env del frontend")
    ap.add_argument("--nueva-clave", action="store_true",
                    help="genera una HYDRA_SECRET_KEY y sale, sin emitir token")
    args = ap.parse_args()

    if args.nueva_clave:
        print(f"HYDRA_SECRET_KEY={secrets.token_hex(32)}")
        print("\nPonla en el entorno del backend (y en el de PM2, para que "
              "todos los workers compartan la misma).", file=sys.stderr)
        return 0

    try:
        from src.security.websocket_auth import WebSocketAuthenticator
    except ImportError as e:
        print(f"no pude importar el autenticador: {e}", file=sys.stderr)
        print("corre esto desde la raíz del repo.", file=sys.stderr)
        return 1

    try:
        auth = WebSocketAuthenticator()
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        print("\nGenera una con: python backend/scripts/issue_ws_token.py "
              "--nueva-clave", file=sys.stderr)
        return 1

    token = auth.generate_token(expires_hours=args.horas)
    if args.env:
        print(f"VITE_WS_TOKEN={token}")
    else:
        print(token)
    print(f"\nválido {args.horas} h. La revocación no está implementada, así "
          f"que la expiración es el único límite.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
