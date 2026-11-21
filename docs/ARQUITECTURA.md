# Especificación de Arquitectura de Software — AutoSen (Django)

> **Issues asociados:**
> - `[DOC-02] Actualizar el Documento de Especificación de Arquitectura (#2)`
> - `[DOC-08] Rehacer los diagramas de clases, paquetes, componentes y despliegue (#8)`

---

## 1. Visión General de la Arquitectura

**AutoSen** es una plataforma web y de telemetría automotriz construida sobre **Python 3.12+**, **Django 6.1+** y **PostgreSQL 18**. La solución implementa una arquitectura modular por capas basada en el patrón arquitectónico **MVT (Model-View-Template)** complementada con patrones de diseño orientados a objetos **GoF (Gang of Four)**.

El sistema se compone de dos frentes principales:
1. **Portal Web Responsivo:** Para clientes, técnicos de soporte y administradores del sistema.
2. **API REST / OBD2:** Servicio JSON sin estado (stateless) para comunicación bidireccional con escáneres ELM327 Bluetooth y la aplicación cliente Android.

```mermaid
graph TD
    A["Escáner ELM327 (OBD2 Bluetooth)"] -->|Bluetooth SPP| B["App Móvil Android AutoSen"]
    B -->|HTTP JSON REST /api/| C["Módulo API Django"]
    D["Navegador Web (Cliente / Admin)"] -->|HTTPS / HTML5| E["Módulo Web & Panel Django"]
    C --> F["Capa de Negocio y Patrones GoF"]
    E --> F
    F --> G["Capa de Persistencia ORM (Django)"]
    G --> H["Base de Datos PostgreSQL 18"]
    F --> I["Despachador Multicanal (WhatsApp / Email / Telegram / WebPush)"]
```

---

## 2. Diagrama de Paquetes y Módulos

El proyecto se estructura en 5 aplicaciones Django desacopladas bajo la raíz `autosen/`:

```mermaid
graph LR
    subgraph Core ["core (Núcleo)"]
        M[Modelos ORM]
        P[Patrones GoF]
        N[Notificaciones]
        A[Auditoría]
        V[Validaciones]
    end
    subgraph Apps ["Módulos de Aplicación"]
        WEB[web: Portal Clientes]
        PANEL[panel: Dashboard Admin / Soporte]
        API[api: Telemetría OBD2]
        REP[reportes: Exportación PDF / Excel]
    end
    WEB --> Core
    PANEL --> Core
    API --> Core
    REP --> Core
```

* **`core/`**: Modelos de base de datos (`Cliente`, `Vehiculo`, `Sensor`, `Alerta`, `RegistroAuditoria`, `NotificacionEnviada`, `Usuario`), patrones GoF, autenticación personalizada y utilidades de normalización.
* **`api/`**: Endpoints para sincronización de telemetría OBD2, lectura de códigos DTC y simulación de desgaste.
* **`panel/`**: Vistas administrativas con control de acceso por roles (`SUPERADMIN`, `ADMIN`, `SOPORTE`), calibración técnica y auditoría.
* **`web/`**: Portal del cliente para registro (con correo y WhatsApp), gestión vehicular y monitoreo personal.
* **`reportes/`**: Generador de reportes con filtros dinámicos y exportación en PDF, CSV y Excel.

---

## 3. Patrones de Diseño GoF Implementados

| Patrón GoF | Tipo | Aplicación en AutoSen | Ubicación en el Código |
| :--- | :--- | :--- | :--- |
| **Strategy (Estrategia)** | Comportamiento | Cálculo dinámico del nivel de desgaste y estado de sensores OBD2 (ECT, MAP, RPM, TPS, O2, Combustible). | `core/patrones/estrategia/` |
| **Observer (Observador)** | Comportamiento | Despacho reactivo de notificaciones multicanal (Email, WhatsApp, Telegram, Web Push) cuando se detecta una alerta crítica. | `core/patrones/observador/` y `core/notificaciones.py` |
| **Factory Method (Fábrica)** | Creacional | Creación parametrizada de sensores automotrices con umbrales, nombres y unidades predeterminadas. | `core/patrones/fabrica/` y `core/sensores_defecto.py` |
| **Singleton** | Creacional | Instancia única compartida del importador de datos y configuración del sistema. | `core/patrones/singleton/` |

---

## 4. Diagrama de Clases del Dominio Principal

```mermaid
classDiagram
    class Cliente {
        +int id_cliente
        +string nombre_cliente
        +string apellido_cliente
        +string correo
        +string telefono
        +string contrasena
        +string estado
    }
    class Vehiculo {
        +int id_vehiculo
        +string nombre_vehiculo
        +string marca
        +string modelo
        +string placa
        +string color
        +string tipo_placa
        +string elm_mac
    }
    class Sensor {
        +int id_sensor
        +string nombre_sensor
        +string tipo_sensor
        +float valor
        +int nivel
        +string tipo_dano
    }
    class Alerta {
        +int id_alerta
        +int id_vehiculo
        +string nombre_sensor
        +string tipo_sensor
        +int nivel
        +string mensaje
        +datetime fecha_alerta
    }
    class RegistroAuditoria {
        +int id_auditoria
        +string accion
        +string entidad
        +int entidad_id
        +string descripcion
        +string usuario_correo
        +datetime fecha
    }
    class NotificacionEnviada {
        +int id_notificacion
        +string canal
        +string destinatario
        +string asunto
        +string mensaje
        +string estado
        +datetime fecha_envio
    }

    Cliente "1" -- "0..*" Vehiculo : es propietario de
    Vehiculo "1" -- "0..*" Sensor : posee
    Vehiculo "1" -- "0..*" Alerta : genera
    Alerta "1" -- "0..*" NotificacionEnviada : despacha
```

---

## 5. Diagrama de Despliegue Físico

```mermaid
graph TD
    subgraph Cliente ["Capa Cliente"]
        Browser["Navegador Web (Chrome/Firefox/Edge)"]
        Mobile["App Android / Dispositivo Móvil"]
        OBD2["Escáner ELM327 OBD2 (Bluetooth)"]
    end

    subgraph Servidor ["Servidor de Aplicación (Host / Docker / VPS)"]
        Nginx["Servidor Web Inverso Nginx"]
        Gunicorn["Servidor WSGI Gunicorn (Python 3.12+)"]
        DjangoApp["AutoSen Django Core (Puerto 8080)"]
    end

    subgraph Datos ["Capa de Almacenamiento"]
        Postgres[("PostgreSQL 18 - Base: vehiculos")]
    end

    subgraph Externos ["Servicios de Notificación"]
        WA["WhatsApp Web / Cloud API"]
        SMTP["Servidor SMTP (Email)"]
        TG["Telegram Bot API"]
    end

    OBD2 -->|Bluetooth SPP| Mobile
    Mobile -->|HTTPS REST| Nginx
    Browser -->|HTTPS Web| Nginx
    Nginx -->|Proxy Pass| Gunicorn
    Gunicorn --> DjangoApp
    DjangoApp -->|TCP 5432| Postgres
    DjangoApp -->|HTTPS REST| WA
    DjangoApp -->|SMTP 587| SMTP
    DjangoApp -->|HTTPS REST| TG
```
