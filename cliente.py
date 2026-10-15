import requests

# Configuracion del servidor
URL = "http://localhost:5000"


def pedir_credenciales():
    usuario = input("Usuario: ").strip()
    contrasena = input("Contraseña: ").strip()
    return {"usuario": usuario, "contraseña": contrasena}


def main():
    # La sesion conserva la cookie del login entre peticiones
    sesion = requests.Session()

    try:
        while True:
            print("\n1. Registrarse\n2. Iniciar sesion\n3. Ver tareas\n4. Salir")
            opcion = input("Opcion: ").strip()

            if opcion == "1":
                r = sesion.post(f"{URL}/registro", json=pedir_credenciales())
            elif opcion == "2":
                r = sesion.post(f"{URL}/login", json=pedir_credenciales())
            elif opcion == "3":
                r = sesion.get(f"{URL}/tareas")
            elif opcion == "4":
                break
            else:
                continue

            print(f"Respuesta del servidor ({r.status_code}): {r.text}")

    except requests.exceptions.ConnectionError:
        print("Error: No se pudo conectar al servidor. Asegurate de que este iniciado.")
    except KeyboardInterrupt:
        print("\nCliente finalizado por el usuario.")


if __name__ == '__main__':
    main()
