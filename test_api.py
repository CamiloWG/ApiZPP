"""
Script de prueba para demostración de la API
Simula el flujo completo de entrada, salida y facturación
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000"


def print_response(titulo, response):
    """Imprime la respuesta de manera formateada"""
    print(f"\n{'='*60}")
    print(f"📋 {titulo}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(response.text)
    print()


def test_flujo_completo():
    """Prueba el flujo completo del sistema"""
    
    print("\n🚗 INICIANDO PRUEBA DEL SISTEMA DE PARQUEO")
    print("="*60)
    
    # 1. Verificar que la API está activa
    print("\n1️⃣ Verificando estado de la API...")
    response = requests.get(f"{BASE_URL}/health")
    print_response("Health Check", response)
    
    # 2. Registrar entrada de vehículo
    print("\n2️⃣ Registrando entrada de vehículo ABC123...")
    response = requests.post(
        f"{BASE_URL}/eventos/",
        json={"placa": "ABC123", "tipo": "entrada"}
    )
    print_response("Registro de Entrada", response)
    
    # 3. Verificar estadías activas
    print("\n3️⃣ Consultando estadías activas...")
    response = requests.get(f"{BASE_URL}/estadias/activas")
    print_response("Estadías Activas", response)
    
    # 4. Simular tiempo de permanencia
    print("\n4️⃣ Simulando permanencia de 5 segundos (en producción serían minutos)...")
    time.sleep(5)
    
    # 5. Registrar salida de vehículo
    print("\n5️⃣ Registrando salida de vehículo ABC123...")
    response = requests.post(
        f"{BASE_URL}/eventos/",
        json={"placa": "ABC123", "tipo": "salida"}
    )
    print_response("Registro de Salida", response)
    
    # 6. Verificar estadías completadas
    print("\n6️⃣ Consultando estadías completadas...")
    response = requests.get(f"{BASE_URL}/estadias/completadas")
    print_response("Estadías Completadas", response)
    
    # 7. Generar factura
    print("\n7️⃣ Generando factura para ABC123...")
    response = requests.post(f"{BASE_URL}/facturas/ABC123")
    print_response("Factura Generada", response)
    
    # 8. Consultar todas las facturas
    print("\n8️⃣ Consultando todas las facturas...")
    response = requests.get(f"{BASE_URL}/facturas/")
    print_response("Todas las Facturas", response)
    
    # 9. Registrar otro vehículo
    print("\n9️⃣ Registrando entrada de otro vehículo XYZ789...")
    response = requests.post(
        f"{BASE_URL}/eventos/",
        json={"placa": "XYZ789", "tipo": "entrada"}
    )
    print_response("Registro de Entrada - Segundo Vehículo", response)
    
    # 10. Ver todos los eventos
    print("\n🔟 Consultando todos los eventos...")
    response = requests.get(f"{BASE_URL}/eventos/")
    print_response("Todos los Eventos", response)
    
    print("\n✅ PRUEBA COMPLETADA EXITOSAMENTE")
    print("="*60)


def test_validaciones():
    """Prueba las validaciones del sistema"""
    
    print("\n🔍 PROBANDO VALIDACIONES DEL SISTEMA")
    print("="*60)
    
    # 1. Intentar registrar salida sin entrada previa
    print("\n1️⃣ Intentando registrar salida sin entrada previa (debe fallar)...")
    response = requests.post(
        f"{BASE_URL}/eventos/",
        json={"placa": "TEST999", "tipo": "salida"}
    )
    print_response("Validación: Salida sin Entrada", response)
    
    # 2. Registrar entrada
    print("\n2️⃣ Registrando entrada de TEST999...")
    response = requests.post(
        f"{BASE_URL}/eventos/",
        json={"placa": "TEST999", "tipo": "entrada"}
    )
    print_response("Registro de Entrada", response)
    
    # 3. Intentar registrar otra entrada (debe fallar)
    print("\n3️⃣ Intentando registrar otra entrada sin salir primero (debe fallar)...")
    response = requests.post(
        f"{BASE_URL}/eventos/",
        json={"placa": "TEST999", "tipo": "entrada"}
    )
    print_response("Validación: Doble Entrada", response)
    
    # 4. Intentar generar factura sin salida (debe fallar)
    print("\n4️⃣ Intentando generar factura sin registrar salida (debe fallar)...")
    response = requests.post(f"{BASE_URL}/facturas/TEST999")
    print_response("Validación: Factura sin Salida", response)
    
    print("\n✅ VALIDACIONES COMPLETADAS")
    print("="*60)


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║   SCRIPT DE PRUEBA - API ZONAS DE PARQUEO PAGO         ║
    ╚══════════════════════════════════════════════════════════╝
    
    Asegúrate de que la API esté ejecutándose en http://localhost:8000
    Para iniciar la API, ejecuta: python main.py
    """)
    
    input("Presiona ENTER para iniciar las pruebas...")
    
    try:
        # Ejecutar prueba del flujo completo
        test_flujo_completo()
        
        input("\nPresiona ENTER para ejecutar pruebas de validación...")
        
        # Ejecutar pruebas de validación
        test_validaciones()
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: No se pudo conectar a la API")
        print("Asegúrate de que la API esté ejecutándose en http://localhost:8000")
        print("Ejecuta: python main.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
